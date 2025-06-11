#!/bin/bash

# Detener el servicio
sudo systemctl stop geoportal.service

# Copia los archivos actualizados
echo "Copiando archivos actualizados..."
cp cors_middleware.py /var/www/GeoportalSV/backend/
cp run.py /var/www/GeoportalSV/backend/

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
