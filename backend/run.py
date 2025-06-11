#!/usr/bin/env python
"""
Script para ejecutar la aplicación Flask del GeoportalSV
"""
from app import create_app
from cors_middleware import cors_middleware

# Crear la aplicación Flask
app = create_app()

# Aplicar middleware CORS personalizado
app = cors_middleware(app)

if __name__ == '__main__':
    print("Iniciando servidor Flask en http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
