from flask import Blueprint, request, jsonify
import os
from .utils import save_and_import_file
from db import get_data_from_db  # Importamos la nueva función

main = Blueprint('main', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

@main.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "GeoportalSV API está funcionando correctamente"})

@main.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    result = save_and_import_file(filepath)
    return jsonify(result)

@main.route('/get-layer-data', methods=['POST'])
def get_layer_data():
    data = request.json
    layer_name = data.get('layer_name')
    
    if not layer_name:
        return jsonify({'error': 'Falta el nombre de la capa', 'success': False})
    
    # Consulta básica para traer datos de la capa (puedes adaptar después)
    query = f"SELECT * FROM {layer_name} LIMIT 10;"
    
    results = get_data_from_db(query)
    if results is None:
        return jsonify({'error': 'Error al consultar la base de datos', 'success': False})
    
    return jsonify({'data': results, 'success': True})
