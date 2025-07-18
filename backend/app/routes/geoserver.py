"""
Rutas para hacer proxy a GeoServer y evitar problemas de CORS
"""
from flask import Blueprint, jsonify, request, Response
import requests
import base64
import json

geoserver_bp = Blueprint('geoserver', __name__)

# Configuración del GeoServer
GEOSERVER_URL = "https://geoportal.sembrandodatos.com/geoserver"
WORKSPACE = "sembrando"
GEOSERVER_AUTH = {
    'username': 'admin',
    'password': 'geoserver'
}

@geoserver_bp.route('/proxy/geoserver/rest/workspaces/<workspace>/featuretypes.json', methods=['GET'])
def proxy_geoserver_featuretypes(workspace):
    """
    Proxy para obtener los featuretypes de un workspace desde GeoServer
    """
    try:
        # Construir la URL del GeoServer
        url = f"{GEOSERVER_URL}/rest/workspaces/{workspace}/featuretypes.json"
        
        # Preparar la autenticación
        auth_string = f"{GEOSERVER_AUTH['username']}:{GEOSERVER_AUTH['password']}"
        auth_bytes = auth_string.encode('ascii')
        auth_base64 = base64.b64encode(auth_bytes).decode('ascii')
        
        # Hacer la solicitud al GeoServer
        headers = {
            'Authorization': f'Basic {auth_base64}',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Retornar los datos directamente como JSON
            return jsonify(response.json())
        else:
            return jsonify({
                'error': f'Error al obtener datos del GeoServer: {response.status_code}',
                'details': response.text
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Error de conexión con GeoServer',
            'details': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@geoserver_bp.route('/proxy/geoserver/wms', methods=['GET', 'OPTIONS'])
def proxy_geoserver_wms():
    """
    Proxy para solicitudes WMS a GeoServer
    """
    # Manejar solicitudes OPTIONS para CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response
        
    try:
        # Construir la URL del GeoServer WMS
        url = f"{GEOSERVER_URL}/wms"
        
        # Pasar todos los parámetros de consulta
        params = request.args.to_dict()
        
        # Configurar headers para la solicitud
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Hacer la solicitud al GeoServer con timeout aumentado
        response = requests.get(url, params=params, headers=headers, timeout=60, stream=True)
        
        # Crear la respuesta con streaming para imágenes grandes
        def generate_response():
            for chunk in response.iter_content(chunk_size=8192):
                yield chunk
        
        # Configurar headers de respuesta
        response_headers = {}
        if 'Content-Type' in response.headers:
            response_headers['Content-Type'] = response.headers['Content-Type']
        if 'Content-Length' in response.headers:
            response_headers['Content-Length'] = response.headers['Content-Length']
            
        # Añadir headers CORS explícitos
        response_headers['Access-Control-Allow-Origin'] = '*'
        response_headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response_headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        # Retornar la respuesta con streaming
        return Response(
            generate_response(),
            status=response.status_code,
            headers=response_headers
        )
        
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'Timeout al conectar con GeoServer WMS',
            'details': 'La solicitud tardó demasiado tiempo'
        }), 504
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': 'Error de conexión con GeoServer WMS',
            'details': 'No se pudo conectar al servidor GeoServer'
        }), 502
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Error de conexión con GeoServer WMS',
            'details': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@geoserver_bp.route('/proxy/geoserver/<workspace>/wms', methods=['GET', 'OPTIONS'])
def proxy_geoserver_workspace_wms(workspace):
    """
    Proxy para solicitudes WMS a un workspace específico de GeoServer
    """
    # Manejar solicitudes OPTIONS para CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response
        
    try:
        # Construir la URL del GeoServer WMS para el workspace
        url = f"{GEOSERVER_URL}/{workspace}/wms"
        
        # Pasar todos los parámetros de consulta
        params = request.args.to_dict()
        
        # Configurar headers para la solicitud
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Hacer la solicitud al GeoServer con timeout aumentado
        response = requests.get(url, params=params, headers=headers, timeout=60, stream=True)
        
        # Crear la respuesta con streaming para imágenes grandes
        def generate_response():
            for chunk in response.iter_content(chunk_size=8192):
                yield chunk
        
        # Configurar headers de respuesta
        response_headers = {}
        if 'Content-Type' in response.headers:
            response_headers['Content-Type'] = response.headers['Content-Type']
        if 'Content-Length' in response.headers:
            response_headers['Content-Length'] = response.headers['Content-Length']
        
        # Añadir headers CORS explícitos
        response_headers['Access-Control-Allow-Origin'] = '*'
        response_headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response_headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        # Retornar la respuesta con streaming
        return Response(
            generate_response(),
            status=response.status_code,
            headers=response_headers
        )
        
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'Timeout al conectar con GeoServer WMS',
            'details': 'La solicitud tardó demasiado tiempo'
        }), 504
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': 'Error de conexión con GeoServer WMS',
            'details': 'No se pudo conectar al servidor GeoServer'
        }), 502
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Error de conexión con GeoServer WMS',
            'details': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500

@geoserver_bp.route('/proxy/geoserver/<workspace>/wfs', methods=['GET', 'POST'])
def proxy_geoserver_workspace_wfs(workspace):
    """
    Proxy para solicitudes WFS a un workspace específico de GeoServer
    """
    try:
        # Construir la URL del GeoServer WFS para el workspace
        url = f"{GEOSERVER_URL}/{workspace}/wfs"
        
        if request.method == 'GET':
            # Pasar todos los parámetros de consulta
            params = request.args.to_dict()
            response = requests.get(url, params=params, timeout=30)
        else:
            # Para POST, pasar el cuerpo de la solicitud
            headers = {'Content-Type': request.content_type}
            response = requests.post(url, data=request.data, headers=headers, timeout=30)
        
        # Retornar la respuesta tal como viene del GeoServer
        return Response(
            response.content,
            status=response.status_code,
            headers=dict(response.headers)
        )
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Error de conexión con GeoServer WFS',
            'details': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500
