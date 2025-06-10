"""
Middleware personalizado para manejar CORS en la aplicación Flask
"""

class CORSMiddleware:
    """
    Middleware para añadir encabezados CORS a todas las respuestas
    """
    
    def __init__(self, app):
        """
        Inicializar el middleware
        
        Args:
            app: Aplicación Flask
        """
        self.app = app
        
    def __call__(self, environ, start_response):
        """
        Procesar la solicitud y añadir encabezados CORS
        
        Args:
            environ: Entorno WSGI
            start_response: Función para iniciar respuesta
            
        Returns:
            Respuesta WSGI
        """
        def add_cors_headers(status, headers, exc_info=None):
            """
            Añadir encabezados CORS a la respuesta
            
            Args:
                status: Estado HTTP
                headers: Encabezados HTTP
                exc_info: Información de excepción
                
            Returns:
                Respuesta con encabezados CORS
            """
            headers_list = list(headers)
            headers_list.append(('Access-Control-Allow-Origin', '*'))
            headers_list.append(('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'))
            headers_list.append(('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With'))
            
            return start_response(status, headers_list, exc_info)
        
        # Manejar solicitudes OPTIONS
        if environ['REQUEST_METHOD'] == 'OPTIONS':
            add_cors_headers('200 OK', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', '0'),
            ])
            return [b'']
            
        return self.app(environ, add_cors_headers)

def setup_cors_middleware(app):
    """
    Configurar middleware CORS en aplicación Flask
    
    Args:
        app: Aplicación Flask
        
    Returns:
        Aplicación con middleware CORS configurado
    """
    app.wsgi_app = CORSMiddleware(app.wsgi_app)
    return app
