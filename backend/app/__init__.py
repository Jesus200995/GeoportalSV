"""
Inicialización de la aplicación Flask para GeoportalSV
"""
from flask import Flask
from flask_cors import CORS
import os
from .routes.upload import upload_bp
from .routes.layers import layers_bp  # Importamos el nuevo blueprint

def create_app():
    """
    Crea y configura la aplicación Flask
    
    Returns:
        Flask app: Aplicación Flask configurada
    """
    app = Flask(__name__)
    
    # Configuración mejorada de CORS
    CORS(app, supports_credentials=True, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Configurar límite de tamaño de archivo subido (100MB)
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
    
    # Registrar blueprints
    app.register_blueprint(upload_bp, url_prefix='/upload-shapefile')
    app.register_blueprint(layers_bp, url_prefix='/layers')  # Registrar el nuevo blueprint
    
    @app.route('/')
    def hello():
        return {"message": "API Backend para GeoportalSV"}
    
    # Configuraciones adicionales
    app.config['JSON_AS_ASCII'] = False
    app.config['JSON_SORT_KEYS'] = False
    
    return app
