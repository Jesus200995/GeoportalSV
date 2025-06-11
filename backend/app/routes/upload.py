from flask import Blueprint, request, jsonify, make_response
import os
import uuid
import zipfile
import shutil
from ..utils import process_shapefile_zip

# Crear el blueprint
upload_bp = Blueprint('upload', __name__)

# Directorio para almacenar archivos subidos
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
SHAPEFILE_FOLDER = os.path.join(os.getcwd(), 'shapefiles')

# Crear directorios si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SHAPEFILE_FOLDER, exist_ok=True)

@upload_bp.route('/upload-shapefile', methods=['POST', 'OPTIONS'])
def upload_shapefile():
    """
    Endpoint principal para la subida de archivos shapefile.
    Acepta POST para la subida y OPTIONS para preflight CORS.
    """
    # Manejar solicitudes OPTIONS para CORS
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        return response, 200
    
    # Verificar si hay un archivo en la solicitud
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'error': 'Archivo no válido'}), 400

    # Verificar que es un archivo ZIP
    if not file.filename.lower().endswith('.zip'):
        return jsonify({'error': 'El archivo debe ser un ZIP que contenga los archivos shapefile'}), 400
    
    # Guardar el archivo temporalmente
    unique_filename = str(uuid.uuid4()) + ".zip"
    zip_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(zip_path)
    
    # Aquí puedes procesar el archivo ZIP si es necesario
    # ...

    # Generar respuesta exitosa con headers CORS explícitos
    response = jsonify({
        'success': True,
        'message': f'Archivo {file.filename} recibido correctamente',
        'filename': file.filename
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200

# Ruta alternativa con 'F' mayúscula (para mayor compatibilidad)
@upload_bp.route('/upload-shapeFile', methods=['POST', 'OPTIONS'])
def upload_shapefile_alt():
    """Alias para el endpoint principal con 'F' mayúscula"""
    return upload_shapefile()
