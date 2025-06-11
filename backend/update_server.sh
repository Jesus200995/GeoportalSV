#!/bin/bash

# Detener el servicio
sudo systemctl stop geoportal.service

# Copia los archivos actualizados
echo "Copiando archivos actualizados..."
cp cors_middleware.py /var/www/GeoportalSV/backend/
cp run.py /var/www/GeoportalSV/backend/
cp app.py /var/www/GeoportalSV/backend/
cp -r app /var/www/GeoportalSV/backend/

# Crear el archivo upload.py específicamente
echo "Creando el archivo upload.py..."
cat > /var/www/GeoportalSV/backend/app/upload.py << 'EOF'
from flask import request, jsonify
from app import app

@app.route('/api/upload-shapefile', methods=['POST', 'OPTIONS'])
def upload_shapefile():
    # Manejar preflight OPTIONS
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        headers = response.headers

        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Authorization,Content-Type'
        headers['Access-Control-Max-Age'] = '3600'

        return response, 204

    # Manejar POST
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename.endswith('.zip'):
        return jsonify({'error': 'El archivo debe ser un ZIP que contenga los archivos shapefile'}), 400

    return jsonify({'message': f'Archivo {file.filename} recibido correctamente'}), 200
EOF

# Actualizar la configuración NGINX si la hay
if [ -f "nginx.conf" ]; then
    echo "Actualizando configuración NGINX..."
    sudo cp nginx.conf /etc/nginx/sites-available/geoportal
    sudo nginx -t
    if [ $? -eq 0 ]; then
        sudo systemctl reload nginx
        echo "Configuración de NGINX actualizada y recargada."
    else
        echo "Error en la configuración de NGINX, no se ha recargado."
    fi
fi

# Reiniciar el servicio
echo "Reiniciando el servicio geoportal..."
sudo systemctl start geoportal.service
sudo systemctl status geoportal.service

echo "Actualizaciones aplicadas."
