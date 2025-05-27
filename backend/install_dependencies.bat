@echo off
echo Instalando dependencias para GeoportalSV backend...

REM Actualizar pip
python -m pip install --upgrade pip

REM Instalar wheel primero para asegurarnos de tener soporte para wheels
pip install wheel

REM Instalar Shapely con binary only para evitar compilaciones
pip install shapely --only-binary shapely

REM Instalar GeoPandas con binary only
pip install geopandas --only-binary geopandas

REM Instalar el resto de las dependencias
pip install Flask==2.0.1 Flask-Cors==3.0.10 psycopg2-binary==2.9.3 requests==2.27.1 python-dotenv==0.19.2

echo Instalacion completa!
