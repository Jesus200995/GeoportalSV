"""
Archivo principal para inicializar la aplicación Flask
"""
from flask import Flask

# Crear la aplicación Flask global
app = Flask(__name__)

# Configurar límite de tamaño de archivo subido (100MB)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Importar rutas
from app import upload

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
