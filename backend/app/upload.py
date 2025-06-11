from flask import request, jsonify
from app import app

@app.route('/api/upload-shapefile', methods=['POST', 'OPTIONS'])
def upload_shapefile():
    # Manejar preflight OPTIONS
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        headers = response.headers

        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Authorization,Content-Type'
        headers['Access-Control-Max-Age'] = '3600'

        return response, 204

    # Manejar POST
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename.endswith('.zip'):
        return jsonify({'error': 'El archivo debe ser un ZIP que contenga los archivos shapefile'}), 400

    return jsonify({'message': f'Archivo {file.filename} recibido correctamente'}), 200
