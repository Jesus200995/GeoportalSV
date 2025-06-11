"""
Middleware personalizado para CORS con soporte específico para la ruta de subida de archivos
"""

def setup_cors_middleware(app):
    """
    Aplica encabezados CORS a todas las respuestas de la aplicación
    con énfasis especial en la ruta de subida de archivos
    
    Args:
        app: Aplicación Flask
        
    Returns:
        Aplicación Flask con middleware CORS aplicado
    """
    @app.after_request
    def apply_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Requested-With"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Max-Age"] = "3600"
        return response

    # Manejar OPTIONS globalmente para todas las rutas
    @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options_handler(path):
        response = app.make_default_options_response()
        apply_cors_headers(response)
        return response
    
    # Rutas específicas para manejar la subida de archivos
    # Estas rutas son adicionales a las definidas en blueprints para asegurar que se manejen correctamente
    @app.route('/api/upload-shapefile', methods=['OPTIONS'])
    @app.route('/api/upload-shapeFile', methods=['OPTIONS'])  # Variante con F mayúscula
    @app.route('/upload-shapefile', methods=['OPTIONS'])      # Por si se accede sin /api
    @app.route('/upload-shapeFile', methods=['OPTIONS'])      # Por si se accede sin /api, con F mayúscula
    def upload_options():
        response = app.make_default_options_response()
        apply_cors_headers(response)
        return response
    
    return app
