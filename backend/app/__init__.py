"""
Inicialización de la aplicación Flask para GeoportalSV
"""
from flask import Flask
from flask_cors import CORS

def create_app():
    """
    Crea y configura la aplicación Flask
    
    Returns:
        Flask app: Aplicación Flask configurada
    """
    app = Flask(__name__)
    CORS(app)  # Habilitar CORS para todas las rutas
    
    # Importar y registrar el blueprint
    from .routes import main
    app.register_blueprint(main)
    
    # Configuraciones adicionales
    app.config['JSON_AS_ASCII'] = False
    app.config['JSON_SORT_KEYS'] = False
    
    return app
