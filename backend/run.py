#!/usr/bin/env python
"""
Script para ejecutar la aplicación Flask del GeoportalSV
"""
from main import app  # Importar la aplicación desde main.py

if __name__ == '__main__':
    print("Iniciando servidor Flask en http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
