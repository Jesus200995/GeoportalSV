from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import uuid
import zipfile
import shutil
from app.utils import process_shapefile_zip

app = Flask(__name__)

# Configurar CORS correctamente para permitir solicitudes desde cualquier origen
CORS(app, resources={r"/*": {
    "origins": "*", 
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
}})

# Directorio para almacenar archivos subidos
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
SHAPEFILE_FOLDER = os.path.join(os.getcwd(), 'shapefiles')

# Crear directorios si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SHAPEFILE_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return jsonify({"message": "Backend del Geoportal funcionando correctamente"})

# Ruta principal para subir shapefile - asegurar que sea accesible desde /api/upload-shapefile con el método POST
@app.route('/api/upload-shapefile', methods=['POST', 'OPTIONS'])
def upload_shapefile():
    # Manejar solicitudes OPTIONS para CORS
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        response.headers.add('Access-Control-Max-Age', '86400')
        return response, 200

    # Verificar si hay un archivo en la solicitud
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo', 'success': False}), 400

    # Obtener el archivo y verificar validez
    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'error': 'Archivo no válido', 'success': False}), 400
    
    # Verificar que es un archivo ZIP
    if not file.filename.lower().endswith('.zip'):
        return jsonify({'error': 'El archivo debe ser un ZIP que contenga los archivos shapefile', 'success': False}), 400

    try:
        # Crear un nombre único para el archivo
        unique_filename = str(uuid.uuid4()) + ".zip"
        zip_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Guardar el archivo ZIP
        file.save(zip_path)
        
        # Crear directorio para extraer el shapefile
        extract_dir = os.path.join(SHAPEFILE_FOLDER, str(uuid.uuid4()))
        os.makedirs(extract_dir, exist_ok=True)
        
        # Extraer el archivo ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Verificar que contiene archivos shapefile (.shp)
        has_shapefile = False
        for root, _, files in os.walk(extract_dir):
            for file in files:
                if file.lower().endswith('.shp'):
                    has_shapefile = True
                    break
            if has_shapefile:
                break
        
        if not has_shapefile:
            # Limpieza si no hay shapefiles
            shutil.rmtree(extract_dir, ignore_errors=True)
            os.remove(zip_path)
            return jsonify({'error': 'El archivo ZIP no contiene ningún shapefile (.shp)', 'success': False}), 400
        
        # Procesar el shapefile y publicar en GeoServer
        result = process_shapefile_zip(extract_dir)
        
        # Limpiar archivo ZIP original
        os.remove(zip_path)
        
        if result['success']:
            response_data = {
                'success': True,
                'message': result['message'],
                'table_name': result.get('table_name', '')
            }
            
            # Solo incluir la ruta si el directorio no se eliminó
            if not result.get('cleaned_directory', False):
                response_data['filepath'] = extract_dir
            
            # Agregar información de GeoServer si está disponible
            if 'geoserver_urls' in result:
                response_data['geoserver'] = result['geoserver_urls']
                
            return jsonify(response_data)
        else:
            return jsonify({'error': result['error'], 'success': False}), 500
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# Mantener la misma función para la ruta alternativa
@app.route('/api/process-shapefile', methods=['POST', 'OPTIONS'])
def process_shapefile_route():
    return upload_shapefile()

# También crear una versión sin el prefijo /api para mayor compatibilidad
@app.route('/upload-shapefile', methods=['POST', 'OPTIONS'])
def upload_shapefile_no_prefix():
    return upload_shapefile()

# Interceptor global para añadir headers CORS a todas las respuestas
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
