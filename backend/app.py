"""
Archivo principal para inicializar la aplicación Flask
"""
from app import create_app

# Crear la aplicación Flask usando la función factory
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
