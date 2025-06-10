from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import uuid
import zipfile
import shutil
from app.utils import process_shapefile_zip

app = Flask(__name__)

# Configurar CORS correctamente
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

# Definir la ruta correctamente con methods=['POST', 'OPTIONS']
@app.route('/api/upload-shapefile', methods=['POST', 'OPTIONS'])
def upload_shapefile():
    # Manejar solicitudes OPTIONS para CORS explícitamente
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        return response, 200

    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400

    file = request.files['file']
    filename = file.filename

    response = jsonify({'message': f'Archivo {filename} recibido correctamente'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200

# Añadir una ruta alternativa con 'F' mayúscula para mayor compatibilidad
@app.route('/api/upload-shapeFile', methods=['POST', 'OPTIONS'])
def upload_shapefile_alt():
    return upload_shapefile()  # Reutilizar la misma función

# Mantener la ruta de procesamiento avanzado con otro nombre
@app.route('/api/process-shapefile', methods=['POST'])
def process_shapefile():
    try:
        # Verificar que se ha enviado un archivo
        if 'file' not in request.files:
            return jsonify({'error': 'No se ha enviado ningún archivo'}), 400
        
        file = request.files['file']
        
        # Verificar que el archivo tiene nombre
        if file.filename == '':
            return jsonify({'error': 'Archivo sin nombre'}), 400
        
        # Verificar que es un archivo ZIP
        if not file.filename.lower().endswith('.zip'):
            return jsonify({'error': 'El archivo debe ser un ZIP que contenga los archivos shapefile'}), 400
        
        # Crear un nombre único para el archivo
        unique_filename = str(uuid.uuid4()) + ".zip"
        zip_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Guardar el archivo ZIP
        file.save(zip_path)
        
        # Crear directorio para extraer el shapefile
        extract_dir = os.path.join(SHAPEFILE_FOLDER, str(uuid.uuid4()))
        os.makedirs(extract_dir, exist_ok=True)
        
        # Extraer el archivo ZIP
        try:
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
                return jsonify({'error': 'El archivo ZIP no contiene ningún shapefile (.shp)'}), 400
            
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
                return jsonify({'error': result['error']}), 500
            
        except zipfile.BadZipFile:
            # Limpieza si el archivo ZIP es inválido
            os.remove(zip_path)
            return jsonify({'error': 'El archivo ZIP es inválido o está corrupto'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Interceptor para añadir headers CORS a todas las respuestas
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
