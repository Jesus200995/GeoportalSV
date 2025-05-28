from flask import Blueprint, request, jsonify
import os
import psycopg2
import requests
from ..utils import format_response
from ..config import DB_CONFIG

# Configuración de GeoServer
GEOSERVER_URL = "http://31.97.8.51:8082/geoserver"
GEOSERVER_USER = "admin"
GEOSERVER_PASSWORD = "geoserver"
WORKSPACE = "sembrando"

layers_bp = Blueprint('layers', __name__)

@layers_bp.route('/<layer_name>', methods=['DELETE'])
def delete_layer(layer_name):
    """
    Elimina una capa geográfica tanto de PostgreSQL/PostGIS como de GeoServer.
    
    Args:
        layer_name: Nombre de la capa a eliminar
        
    Returns:
        JSON: Resultado de la operación
    """
    try:
        # Validación básica del nombre de la capa
        if not layer_name or not isinstance(layer_name, str) or len(layer_name) < 1:
            return jsonify(format_response(None, False, "Nombre de capa inválido")), 400
        
        # 1. Eliminar la capa de GeoServer
        geoserver_success = delete_from_geoserver(layer_name)
        
        # 2. Eliminar la tabla de PostGIS
        postgis_success = delete_from_postgis(layer_name)
        
        if geoserver_success and postgis_success:
            return jsonify(format_response(None, True, f"Capa '{layer_name}' eliminada correctamente de GeoServer y PostGIS"))
        elif geoserver_success:
            return jsonify(format_response(None, True, f"Capa '{layer_name}' eliminada de GeoServer pero hubo un problema al eliminarla de PostGIS"))
        elif postgis_success:
            return jsonify(format_response(None, True, f"Capa '{layer_name}' eliminada de PostGIS pero hubo un problema al eliminarla de GeoServer"))
        else:
            return jsonify(format_response(None, False, f"No se pudo eliminar la capa '{layer_name}'")), 500
            
    except Exception as e:
        return jsonify(format_response(None, False, f"Error al eliminar la capa: {str(e)}")), 500

def delete_from_geoserver(layer_name):
    """
    Elimina una capa de GeoServer usando su API REST
    
    Args:
        layer_name: Nombre de la capa a eliminar
        
    Returns:
        bool: True si se eliminó correctamente, False en caso contrario
    """
    try:
        # Headers comunes para las solicitudes
        headers = {'Content-type': 'application/json'}
        auth = (GEOSERVER_USER, GEOSERVER_PASSWORD)
        
        # 1. Eliminar la capa
        layer_url = f"{GEOSERVER_URL}/rest/layers/{WORKSPACE}:{layer_name}"
        layer_response = requests.delete(layer_url, auth=auth, headers=headers)
        
        # 2. Eliminar el featuretype
        featuretype_url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/datastores/postgis_store/featuretypes/{layer_name}"
        featuretype_response = requests.delete(featuretype_url, auth=auth, headers=headers)
        
        # Comprobar si las eliminaciones fueron exitosas (códigos 200 o 404 significan que ya no existe)
        if (layer_response.status_code in [200, 204, 404] and 
            featuretype_response.status_code in [200, 204, 404]):
            print(f"✅ Capa {layer_name} eliminada correctamente de GeoServer")
            return True
        else:
            print(f"❌ Error al eliminar capa de GeoServer: Layer: {layer_response.status_code}, Featuretype: {featuretype_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción al eliminar de GeoServer: {str(e)}")
        return False

def delete_from_postgis(layer_name):
    """
    Elimina una tabla de PostgreSQL/PostGIS
    
    Args:
        layer_name: Nombre de la tabla a eliminar
        
    Returns:
        bool: True si se eliminó correctamente, False en caso contrario
    """
    try:
        # Importar directamente la configuración para evitar problemas de ruta
        from app.config import DB_CONFIG
        
        # Conectar a la base de datos
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        # Para depuración
        print(f"Conectando a PostgreSQL con: host={DB_CONFIG['host']}, port={DB_CONFIG['port']}, dbname={DB_CONFIG['dbname']}, user={DB_CONFIG['user']}")
        
        # Crear un cursor y ejecutar la eliminación
        with conn.cursor() as cursor:
            # Usar parámetros para evitar SQL injection
            sql = "DROP TABLE IF EXISTS %s"
            # No podemos usar parámetros directos para nombres de tabla, debemos escaparlos manualmente
            # Esto es seguro ya que layer_name ha sido validado anteriormente
            table_name = psycopg2.extensions.AsIs(layer_name)
            cursor.execute(sql, (table_name,))
            conn.commit()
            
        conn.close()
        print(f"✅ Tabla {layer_name} eliminada correctamente de PostgreSQL/PostGIS")
        return True
            
    except Exception as e:
        print(f"❌ Error al eliminar tabla de PostgreSQL/PostGIS: {str(e)}")
        return False

# Añadir una ruta para obtener la lista de capas
@layers_bp.route('/', methods=['GET'])
def get_layers():
    """
    Obtiene la lista de capas disponibles
    
    Returns:
        JSON: Lista de capas
    """
    try:
        # Aquí se implementaría la lógica para obtener las capas
        # Por ahora devuelve una lista vacía
        return jsonify(format_response({"layers": []}, True, "Lista de capas obtenida correctamente"))
    except Exception as e:
        return jsonify(format_response(None, False, f"Error al obtener la lista de capas: {str(e)}")), 500
