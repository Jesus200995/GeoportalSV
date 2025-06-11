#!/bin/bash

# Detener el servicio actual
sudo systemctl stop geoportal

# Aplicar los cambios
cd /var/www/GeoportalSV/backend
source venv/bin/activate
pip install flask flask-cors

# Reiniciar el servicio
sudo systemctl start geoportal
sudo systemctl status geoportal
