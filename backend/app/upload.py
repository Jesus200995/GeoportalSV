from flask import Blueprint, request, jsonify
import os
import uuid
import zipfile
import shutil
import subprocess
import requests
import glob
import tempfile
from app.config import DB_CONFIG, GEOSERVER_CONFIG

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/api/upload-shapefile', methods=['POST', 'OPTIONS'])
def upload_shapefile():
    """
    Endpoint para subir archivos shapefile (ZIP), procesarlos y publicarlos automáticamente.
    1. Recibe un archivo ZIP
    2. Lo descomprime para acceder a los archivos .shp, .shx, .dbf, .prj
    3. Sube el shapefile a PostgreSQL/PostGIS usando ogr2ogr
    4. Publica la capa en GeoServer usando su API REST
    5. Devuelve información de éxito o error
    """
    # Manejar preflight OPTIONS
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response, 204

    # Verificar si hay un archivo en la solicitud
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No se recibió ningún archivo'}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'success': False, 'error': 'Archivo no válido'}), 400

    # Verificar que es un archivo ZIP
    if not file.filename.lower().endswith('.zip'):
        return jsonify({'success': False, 'error': 'El archivo debe ser un ZIP que contenga los archivos shapefile'}), 400

    try:
        # Crear directorios temporales para el procesamiento
        temp_dir = tempfile.mkdtemp(prefix="geoportal_")
        zip_path = os.path.join(temp_dir, "uploaded.zip")
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        print(f"Directorio temporal creado: {temp_dir}")
        print(f"Guardando archivo ZIP en: {zip_path}")
        
        # Guardar el archivo ZIP
        file.save(zip_path)
        
        # Descomprimir el ZIP
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            print(f"Archivo ZIP descomprimido en: {extract_dir}")
        except zipfile.BadZipFile:
            return jsonify({'success': False, 'error': 'El archivo ZIP es inválido o está corrupto'}), 400
        
        # Buscar archivos shapefile en el directorio extraído
        shapefile_paths = glob.glob(os.path.join(extract_dir, "**/*.shp"), recursive=True)
        if not shapefile_paths:
            return jsonify({'success': False, 'error': 'No se encontraron archivos shapefile (.shp) en el ZIP'}), 400
        
        # Tomar el primer shapefile encontrado
        shapefile_path = shapefile_paths[0]
        shapefile_name = os.path.splitext(os.path.basename(shapefile_path))[0]
        table_name = shapefile_name.lower()  # Nombre de la tabla en PostgreSQL
        
        print(f"Shapefile encontrado: {shapefile_path}")
        print(f"Nombre de tabla a crear: {table_name}")
        
        # Subir a PostgreSQL/PostGIS usando ogr2ogr
        try:
            # Construir la cadena de conexión PostgreSQL
            pg_conn_string = f"PG:host={DB_CONFIG['host']} port={DB_CONFIG['port']} dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} password={DB_CONFIG['password']}"
            
            # Comando ogr2ogr para importar a PostGIS
            ogr_cmd = [
                'ogr2ogr',
                '-f', 'PostgreSQL',
                '-overwrite',  # Sobrescribir si ya existe
                '-lco', 'GEOMETRY_NAME=geom',  # Nombre de la columna de geometría
                '-lco', 'FID=gid',  # Nombre de la columna de ID
                '-a_srs', 'EPSG:4326',  # Asignar SRS si no está definido
                '-nlt', 'PROMOTE_TO_MULTI',  # Promover a geometrías multi para consistencia
                pg_conn_string,
                shapefile_path
            ]
            
            print(f"Ejecutando ogr2ogr: {' '.join(ogr_cmd)}")
            result = subprocess.run(ogr_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error en ogr2ogr: {result.stderr}")
                return jsonify({
                    'success': False, 
                    'error': f'Error al importar a PostGIS: {result.stderr}'
                }), 500
                
            print("Shapefile importado correctamente a PostGIS")
            
        except Exception as e:
            print(f"Error al ejecutar ogr2ogr: {str(e)}")
            return jsonify({'success': False, 'error': f'Error al importar a PostGIS: {str(e)}'}), 500
        
        # Publicar en GeoServer
        try:
            # 1. Verificar si el workspace existe
            workspace_url = f"{GEOSERVER_CONFIG['url']}/rest/workspaces/{GEOSERVER_CONFIG['workspace']}"
            auth = (GEOSERVER_CONFIG['user'], GEOSERVER_CONFIG['password'])
            headers = {'Content-Type': 'application/json'}
            
            workspace_response = requests.get(workspace_url, auth=auth)
            
            if workspace_response.status_code != 200:
                # Crear workspace si no existe
                print(f"Workspace {GEOSERVER_CONFIG['workspace']} no existe. Creándolo...")
                workspace_data = {
                    "workspace": {
                        "name": GEOSERVER_CONFIG['workspace']
                    }
                }
                requests.post(
                    f"{GEOSERVER_CONFIG['url']}/rest/workspaces",
                    json=workspace_data,
                    headers=headers,
                    auth=auth
                )
            
            # 2. Verificar/crear datastore
            datastore_url = f"{workspace_url}/datastores/postgis_store"
            datastore_response = requests.get(datastore_url, auth=auth)
            
            if datastore_response.status_code != 200:
                # Crear datastore PostGIS si no existe
                print("Datastore 'postgis_store' no existe. Creándolo...")
                datastore_data = {
                    "dataStore": {
                        "name": "postgis_store",
                        "connectionParameters": {
                            "entry": [
                                {"@key": "host", "$": DB_CONFIG['host']},
                                {"@key": "port", "$": str(DB_CONFIG['port'])},
                                {"@key": "database", "$": DB_CONFIG['dbname']},
                                {"@key": "user", "$": DB_CONFIG['user']},
                                {"@key": "passwd", "$": DB_CONFIG['password']},
                                {"@key": "dbtype", "$": "postgis"},
                                {"@key": "schema", "$": "public"}
                            ]
                        }
                    }
                }
                
                create_ds_response = requests.post(
                    f"{workspace_url}/datastores",
                    json=datastore_data,
                    headers=headers,
                    auth=auth
                )
                
                if create_ds_response.status_code not in [201, 200]:
                    print(f"Error al crear datastore: {create_ds_response.text}")
                    return jsonify({
                        'success': False, 
                        'error': f'Error al crear datastore en GeoServer: {create_ds_response.text}'
                    }), 500
            
            # 3. Publicar la capa como feature type
            print(f"Publicando capa {table_name} en GeoServer...")
            featuretype_url = f"{datastore_url}/featuretypes"
            
            # Primero verificar si ya existe
            check_layer = requests.get(
                f"{featuretype_url}/{table_name}",
                auth=auth
            )
            
            if check_layer.status_code == 200:
                print(f"La capa {table_name} ya existe en GeoServer")
            else:
                # Crear la capa
                layer_data = {
                    "featureType": {
                        "name": table_name,
                        "nativeName": table_name,
                        "title": table_name.replace("_", " ").title(),
                        "srs": "EPSG:4326",
                        "enabled": True
                    }
                }
                
                publish_response = requests.post(
                    featuretype_url,
                    json=layer_data,
                    headers=headers,
                    auth=auth
                )
                
                if publish_response.status_code not in [201, 200]:
                    print(f"Error al publicar capa: {publish_response.text}")
                    return jsonify({
                        'success': False, 
                        'error': f'Error al publicar capa en GeoServer: {publish_response.text}'
                    }), 500
                
                print(f"Capa {table_name} publicada correctamente en GeoServer")
                
            # URLs para acceder a la capa
            wms_url = f"{GEOSERVER_CONFIG['url']}/{GEOSERVER_CONFIG['workspace']}/wms?service=WMS&version=1.1.1&request=GetMap&layers={GEOSERVER_CONFIG['workspace']}:{table_name}"
            wfs_url = f"{GEOSERVER_CONFIG['url']}/{GEOSERVER_CONFIG['workspace']}/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName={GEOSERVER_CONFIG['workspace']}:{table_name}"
            preview_url = f"{GEOSERVER_CONFIG['url']}/{GEOSERVER_CONFIG['workspace']}/wms?service=WMS&version=1.1.1&request=GetMap&layers={GEOSERVER_CONFIG['workspace']}:{table_name}&width=800&height=600&srs=EPSG:4326&bbox=-180,-90,180,90&format=application/openlayers"
            
            # Devolver respuesta exitosa
            response_data = {
                'success': True,
                'message': f'Archivo {file.filename} procesado correctamente. Capa {table_name} publicada.',
                'layer_name': table_name,
                'workspace': GEOSERVER_CONFIG['workspace'],
                'full_layer_name': f"{GEOSERVER_CONFIG['workspace']}:{table_name}",
                'urls': {
                    'wms': wms_url,
                    'wfs': wfs_url,
                    'preview': preview_url
                }
            }
            
            # Limpiar archivos temporales
            try:
                shutil.rmtree(temp_dir)
                print(f"Directorio temporal eliminado: {temp_dir}")
            except Exception as e:
                print(f"Advertencia: No se pudo eliminar el directorio temporal: {str(e)}")
                
            return jsonify(response_data), 200
            
        except Exception as e:
            print(f"Error al publicar en GeoServer: {str(e)}")
            return jsonify({'success': False, 'error': f'Error al publicar en GeoServer: {str(e)}'}), 500
            
    except Exception as e:
        print(f"Error general en el procesamiento: {str(e)}")
        return jsonify({'success': False, 'error': f'Error en el procesamiento: {str(e)}'}), 500
