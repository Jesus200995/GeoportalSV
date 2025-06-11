"""
Middleware personalizado para CORS
"""

def cors_middleware(app):
    """
    Aplica encabezados CORS a todas las respuestas de la aplicación
    
    Args:
        app: Aplicación Flask
        
    Returns:
        Aplicación Flask con middleware CORS aplicado
    """
    @app.after_request
    def apply_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Authorization,Content-Type,X-Requested-With"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response

    # Manejar OPTIONS globalmente
    @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options_handler(path):
        return '', 200

    return app
