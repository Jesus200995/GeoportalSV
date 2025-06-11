from flask import Blueprint, request, jsonify

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload-shapefile', methods=['POST', 'OPTIONS'])
def upload_shapefile():
    # Manejar preflight OPTIONS
    if request.method == 'OPTIONS':
        return '', 204
    
    # Manejar POST
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename.endswith('.zip'):
        return jsonify({'error': 'El archivo debe ser un ZIP que contenga los archivos shapefile'}), 400

    return jsonify({'message': f'Archivo {file.filename} recibido correctamente'}), 200
