"""
Inicialización de la aplicación Flask para GeoportalSV
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from .routes.upload import upload_bp
from .routes.layers import layers_bp

def create_app():
    """
    Crea y configura la aplicación Flask
    
    Returns:
        Flask app: Aplicación Flask configurada
    """
    app = Flask(__name__)
    
    # Configuración mejorada de CORS - asegurarse que sea aplicada correctamente
    CORS(app, supports_credentials=True, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "expose_headers": ["Content-Type", "Content-Length"],
            "max_age": 86400
        }
    })
    
    # Configurar límite de tamaño de archivo subido (100MB)
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
    
    # Registrar blueprints con el prefijo /api apropiado
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(layers_bp, url_prefix='/api/layers')
    
    # Rutas directas en la aplicación principal para mayor compatibilidad
    @app.route('/api/upload-shapefile', methods=['POST', 'OPTIONS'])
    def upload_shapefile_root():
        if request.method == 'OPTIONS':
            # Respuesta CORS completa para preflight
            response = jsonify({})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
            return response, 200

        if 'file' not in request.files:
            return jsonify({'error': 'No se encontró el archivo'}), 400

        file = request.files['file']
        filename = file.filename
        return jsonify({'message': f'Archivo {filename} recibido correctamente'}), 200
    
    # Ruta alternativa con 'F' mayúscula
    @app.route('/api/upload-shapeFile', methods=['POST', 'OPTIONS'])
    def upload_shapefile_alt_root():
        return upload_shapefile_root()
    
    # Endpoint para verificar CORS
    @app.route('/api/cors-test', methods=['GET', 'OPTIONS'])
    def cors_test():
        if request.method == 'OPTIONS':
            response = jsonify({})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            return response, 200
            
        return jsonify({"message": "CORS está configurado correctamente"}), 200
    
    @app.route('/')
    def hello():
        return {"message": "API Backend para GeoportalSV"}
    
    # Añadir un interceptor para todas las respuestas
    @app.after_request
    def add_cors_headers(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        response.headers.add('Access-Control-Max-Age', '86400')
        return response
    
    # Configuraciones adicionales
    app.config['JSON_AS_ASCII'] = False
    app.config['JSON_SORT_KEYS'] = False
    
    return app
