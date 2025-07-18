"""
Inicialización de la aplicación Flask para GeoportalSV
"""
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
from app.upload import upload_bp  # Importar el blueprint de upload
from app.routes.layers import layers_bp  # Mantener importación de layers
from app.routes.geoserver import geoserver_bp  # Importar el blueprint de proxy geoserver

def create_app():
    """
    Crea y configura la aplicación Flask
    
    Returns:
        Flask app: Aplicación Flask configurada
    """
    app = Flask(__name__)
    
    # Configuración de CORS simplificada
    CORS(app, 
         origins=["*"], 
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=False,
         max_age=86400)
    
    # Configurar límite de tamaño de archivo subido (100MB)
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
    
    # Registrar blueprints - upload_bp sin prefijo ya que ya define la ruta completa
    app.register_blueprint(upload_bp)  # Sin url_prefix, el blueprint ya usa /api/upload-shapefile
    app.register_blueprint(layers_bp, url_prefix='/api/layers')
    app.register_blueprint(geoserver_bp, url_prefix='/api')  # Proxy para GeoServer
    
    # Endpoint para verificar CORS
    @app.route('/api/cors-test', methods=['GET', 'OPTIONS'])
    def cors_test():
        return jsonify({"message": "CORS está configurado correctamente"}), 200
    
    @app.route('/')
    def hello():
        return {"message": "API Backend para GeoportalSV"}
    
    # Configuraciones adicionales
    app.config['JSON_AS_ASCII'] = False
    app.config['JSON_SORT_KEYS'] = False
    
    return app
