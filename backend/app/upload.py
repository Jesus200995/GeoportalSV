from flask import Blueprint, request, jsonify

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/api/upload-shapefile', methods=['POST', 'OPTIONS'])
def upload_shapefile():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.status_code = 204
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Authorization,Content-Type')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename.endswith('.zip'):
        return jsonify({'error': 'El archivo debe ser un ZIP que contenga los archivos shapefile'}), 400

    return jsonify({'success': f'Archivo recibido: {file.filename}'})
