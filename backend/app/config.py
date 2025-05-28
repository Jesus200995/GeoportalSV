# Configuraciones para la aplicación

# Configuración de la base de datos PostgreSQL/PostGIS
DB_CONFIG = {
    'host': '31.97.8.51',        # IP pública del servidor
    'port': 5432,                # Puerto de PostgreSQL
    'dbname': 'sembrandodatos',  # Nombre de la base de datos
    'user': 'jesus',             # Usuario correcto
    'password': '2025'           # Contraseña correcta
}

# Configuración de GeoServer
GEOSERVER_CONFIG = {
    'url': 'http://31.97.8.51:8082/geoserver',
    'user': 'admin',
    'password': 'geoserver',
    'workspace': 'sembrando'
}
