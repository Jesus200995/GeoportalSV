"""
Utilidades para la aplicación GeoportalSV.
Este módulo contiene funciones auxiliares para el procesamiento de datos
y otras operaciones comunes utilizadas en la aplicación.
"""

import geopandas as gpd
import psycopg2
import os
import requests
import glob
from app.config import DB_CONFIG
from packaging import version
import shapely
from sqlalchemy import create_engine
import traceback
from app.config import GEOSERVER_CONFIG

# Configuración de GeoServer
GEOSERVER_URL = GEOSERVER_CONFIG['url']
GEOSERVER_USER = GEOSERVER_CONFIG['user']
GEOSERVER_PASSWORD = GEOSERVER_CONFIG['password']
WORKSPACE = GEOSERVER_CONFIG['workspace']

# Crear engine SQLAlchemy para GeoPandas
def get_sqlalchemy_engine():
    """
    Crea y devuelve un engine SQLAlchemy para conexión a PostgreSQL/PostGIS
    
    Returns:
        sqlalchemy.engine.Engine: Engine de conexión
    """
    # Asegurarnos que el puerto sea string para la URL de conexión
    port = str(DB_CONFIG['port'])
    db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{port}/{DB_CONFIG['dbname']}"
    return create_engine(db_url)

# Verificar la versión de Shapely e importar adecuadamente
# Si se usa alguna función específica de Shapely que haya cambiado entre versiones
if version.parse(shapely.__version__) >= version.parse("2.0.0"):
    # Ajustes para Shapely 2.0+ si son necesarios
    pass
else:
    # Comportamiento para versiones anteriores
    pass

def format_response(data, success=True, message=""):
    """
    Formatea una respuesta API estándar.
    
    Args:
        data: Los datos a devolver
        success: Indica si la operación fue exitosa
        message: Mensaje descriptivo opcional
        
    Returns:
        dict: Respuesta formateada
    """
    return {
        "success": success,
        "message": message,
        "data": data
    }

def save_and_import_file(filepath):
    """
    Importa un archivo shapefile y lo guarda en PostGIS
    
    Args:
        filepath: Ruta del archivo a importar
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        print(f"Leyendo archivo shapefile: {filepath}")
        # Leer shapefile usando geopandas - NO intentar decodificar como texto
        gdf = gpd.read_file(filepath)
        
        # Obtener el nombre de la tabla a partir del nombre del archivo
        table_name = os.path.splitext(os.path.basename(filepath))[0].lower()
        print(f"Nombre de tabla extraído: {table_name}")

        # Usar SQLAlchemy engine en lugar de conexión psycopg2 directa
        print("Creando conexión a base de datos...")
        engine = get_sqlalchemy_engine()
        
        print(f"Importando a PostGIS como tabla: {table_name}")
        # Guardar el GeoDataFrame en PostGIS - IMPORTANTE: if_exists='replace'
        gdf.to_postgis(
            table_name, 
            engine, 
            if_exists='replace',  # Reemplazar si ya existe
            index=False,          # No incluir el índice
            schema='public'       # Esquema público
        )
        print("Datos importados correctamente a PostGIS")
        
        # Publicar automáticamente en GeoServer
        publish_success = publish_layer_to_geoserver(table_name)
        
        if publish_success:
            return {
                'success': True, 
                'message': f'Capa {table_name} importada y publicada con éxito en GeoServer',
                'table_name': table_name
            }
        else:
            return {
                'success': True, 
                'message': f'Capa {table_name} importada con éxito. Advertencia: No se pudo publicar en GeoServer',
                'table_name': table_name
            }
    except Exception as e:
        print(f"❌ Error al importar shapefile: {str(e)}")
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def extract_shapefile_name(extract_dir):
    """
    Extrae el nombre del primer shapefile encontrado en un directorio
    
    Args:
        extract_dir: Directorio donde buscar archivos .shp
        
    Returns:
        str: Nombre del archivo shapefile sin extensión o None si no se encuentra
    """
    # Buscar todos los archivos .shp en el directorio y subdirectorios
    shapefile_paths = glob.glob(os.path.join(extract_dir, "**/*.shp"), recursive=True)
    
    if not shapefile_paths:
        return None
    
    # Tomar el primer shapefile encontrado y extraer solo el nombre sin extensión
    shapefile_name = os.path.splitext(os.path.basename(shapefile_paths[0]))[0].lower()
    return shapefile_name

def process_shapefile_zip(extract_dir):
    """
    Procesa un directorio con archivos shapefile extraídos de un ZIP
    
    Args:
        extract_dir: Directorio con los archivos extraídos
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        print(f"Procesando directorio con shapefile: {extract_dir}")
        # Buscar el primer archivo .shp en el directorio
        shapefile_name = extract_shapefile_name(extract_dir)
        
        if not shapefile_name:
            print("❌ No se encontró ningún archivo shapefile (.shp) en el ZIP")
            return {'success': False, 'error': 'No se encontró ningún archivo shapefile (.shp) en el ZIP'}
        
        print(f"Shapefile encontrado: {shapefile_name}")
        
        # Buscar la ruta completa del shapefile
        shapefile_paths = glob.glob(os.path.join(extract_dir, "**/*.shp"), recursive=True)
        if not shapefile_paths:
            return {'success': False, 'error': 'No se pudo encontrar la ruta del shapefile'}
            
        shapefile_path = shapefile_paths[0]
        print(f"Ruta del shapefile: {shapefile_path}")
        
        # Leer el shapefile y guardarlo en PostGIS
        print(f"Leyendo shapefile con GeoPandas...")
        gdf = gpd.read_file(shapefile_path)
        table_name = shapefile_name  # Usar el nombre del shapefile como nombre de tabla
        
        print(f"GeoDataFrame creado con {len(gdf)} registros. Importando a PostGIS como tabla: {table_name}")
        
        # Usar SQLAlchemy engine en lugar de conexión psycopg2 directa
        engine = get_sqlalchemy_engine()
        
        # Asegurarnos que la tabla se crea correctamente
        try:
            # Si estamos teniendo problemas con to_postgis(), podemos intentar primero con to_file para GeoJSON y luego cargar
            print(f"Importando directamente a PostGIS...")
            gdf.to_postgis(
                table_name, 
                engine, 
                if_exists='replace', 
                index=False, 
                schema='public',
                dtype=None  # Dejar que GeoPandas infiera los tipos
            )
        except Exception as postgis_error:
            print(f"❌ Error al importar directamente a PostGIS: {str(postgis_error)}")
            # Método alternativo: guardar como GeoJSON y luego cargar
            print("⚠️ Intentando método alternativo via GeoJSON...")
            geojson_path = os.path.join(extract_dir, f"{shapefile_name}.geojson")
            gdf.to_file(geojson_path, driver="GeoJSON")
            
            # Ahora cargar el GeoJSON
            gdf_reloaded = gpd.read_file(geojson_path)
            gdf_reloaded.to_postgis(table_name, engine, if_exists='replace', index=False)
            print("✅ Importación via GeoJSON completada")
        
        print("✅ Datos importados correctamente a PostGIS")
        
        # Publicar automáticamente en GeoServer
        publish_success = publish_layer_to_geoserver(table_name)
        
        result = {
            'success': True, 
            'table_name': table_name
        }
        
        if publish_success:
            # Añadir URLs para acceder a la capa en GeoServer
            result['message'] = f'Capa {table_name} importada y publicada con éxito en GeoServer'
            result['geoserver_urls'] = {
                'wms': f"{GEOSERVER_URL}/{WORKSPACE}/wms?service=WMS&version=1.1.1&request=GetMap&layers={WORKSPACE}:{table_name}",
                'wfs': f"{GEOSERVER_URL}/{WORKSPACE}/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName={WORKSPACE}:{table_name}",
                'preview': f"{GEOSERVER_URL}/{WORKSPACE}/wms?service=WMS&version=1.1.1&request=GetMap&layers={WORKSPACE}:{table_name}&width=800&height=600&srs=EPSG:4326&bbox=-180,-90,180,90&format=application/openlayers"
            }
        else:
            result['message'] = f'Capa {table_name} importada con éxito. Advertencia: No se pudo publicar en GeoServer'
        
        # Eliminar el directorio del shapefile después de una importación exitosa
        try:
            import shutil
            shutil.rmtree(extract_dir)
            print(f"🧹 Directorio temporal de shapefile eliminado: {extract_dir}")
            result['cleaned_directory'] = True
        except Exception as cleanup_error:
            print(f"⚠️ No se pudo eliminar el directorio temporal: {str(cleanup_error)}")
            result['cleaned_directory'] = False
            
        return result
            
    except Exception as e:
        print(f"❌ Error al procesar shapefile ZIP: {str(e)}")
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def publish_layer_to_geoserver(table_name):
    """
    Publica una capa de PostGIS en GeoServer
    
    Args:
        table_name: Nombre de la tabla en PostGIS
        
    Returns:
        bool: True si la publicación fue exitosa, False en caso contrario
    """
    try:
        print(f"🔄 Iniciando publicación de capa {table_name} en GeoServer...")
        
        # 1. Crear el DataStore si no existe (una sola vez)
        datastore_payload = {
            "dataStore": {
                "name": "postgis_store",  # Usar un store fijo para todas las capas
                "connectionParameters": {
                    "entry": [
                        {"@key": "host", "$": DB_CONFIG['host']},
                        {"@key": "port", "$": str(DB_CONFIG['port'])},  # Asegurar que sea string
                        {"@key": "database", "$": DB_CONFIG['dbname']},
                        {"@key": "user", "$": DB_CONFIG['user']},
                        {"@key": "passwd", "$": DB_CONFIG['password']},
                        {"@key": "dbtype", "$": "postgis"},
                        {"@key": "schema", "$": "public"},
                        {"@key": "Expose primary keys", "$": "true"}
                    ]
                }
            }
        }

        headers = {"Content-Type": "application/json"}

        datastore_url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/datastores"
        
        # Verificar si el datastore ya existe
        print(f"👉 Verificando si existe el datastore 'postgis_store'...")
        check_ds = requests.get(
            f"{datastore_url}/postgis_store",
            auth=(GEOSERVER_USER, GEOSERVER_PASSWORD)
        )
        
        # Si no existe, crearlo
        if check_ds.status_code != 200:
            print(f"🆕 El datastore no existe. Creando nuevo datastore...")
            ds_response = requests.post(
                datastore_url,
                auth=(GEOSERVER_USER, GEOSERVER_PASSWORD),
                headers=headers,
                json=datastore_payload
            )

            if ds_response.status_code not in [200, 201]:
                print(f"❌ Error al crear DataStore: {ds_response.status_code} - {ds_response.text}")
                return False
            else:
                print(f"✅ DataStore creado correctamente")
        else:
            print(f"✅ DataStore existente encontrado")
        
        # 2. Publicar la capa
        layer_url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/datastores/postgis_store/featuretypes"

        # Verificar si la capa ya existe
        print(f"👉 Verificando si la capa '{table_name}' ya existe...")
        check_layer = requests.get(
            f"{layer_url}/{table_name}",
            auth=(GEOSERVER_USER, GEOSERVER_PASSWORD)
        )
        
        # Si la capa existe, podemos actualizar o saltar
        if check_layer.status_code == 200:
            print(f"⚠️ La capa {table_name} ya existe en GeoServer. Se mantendrá la configuración actual.")
            return True

        print(f"👉 Publicando capa '{table_name}'...")
        publish_payload = {
            "featureType": {
                "name": table_name,
                "nativeName": table_name,
                "title": table_name.replace("_", " ").title(),
                "srs": "EPSG:4326",
                "enabled": True
            }
        }

        publish_response = requests.post(
            layer_url,
            auth=(GEOSERVER_USER, GEOSERVER_PASSWORD),
            headers=headers,
            json=publish_payload
        )

        if publish_response.status_code in [200, 201]:
            print(f"✅ Capa {table_name} publicada en GeoServer correctamente.")
            
            # Añadir información sobre cómo acceder a la capa
            wms_url = f"{GEOSERVER_URL}/{WORKSPACE}/wms?service=WMS&version=1.1.1&request=GetMap&layers={WORKSPACE}:{table_name}"
            wfs_url = f"{GEOSERVER_URL}/{WORKSPACE}/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName={WORKSPACE}:{table_name}"
            print(f"📍 URL de acceso WMS: {wms_url}")
            print(f"📍 URL de acceso WFS: {wfs_url}")
            
            return True
        else:
            print(f"❌ Error al publicar la capa {table_name}: {publish_response.status_code} - {publish_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la publicación en GeoServer: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
