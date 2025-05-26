"""
Utilidades para la aplicación GeoportalSV.
Este módulo contiene funciones auxiliares para el procesamiento de datos
y otras operaciones comunes utilizadas en la aplicación.
"""

import geopandas as gpd
import psycopg2
import os
from config import DB_CONFIG

def format_response(data, success=True, message=""):
    """
    Formatea una respuesta API estándar.
    
    Args:
        data: Los datos a devolver
        success: Indica si la operación fue exitosa
        message: Mensaje descriptivo opcional
        
    Returns:
        dict: Respuesta formateada
    """
    return {
        "success": success,
        "message": message,
        "data": data
    }

def save_and_import_file(filepath):
    try:
        gdf = gpd.read_file(filepath)
        table_name = os.path.splitext(os.path.basename(filepath))[0].lower()

        conn = psycopg2.connect(**DB_CONFIG)
        gdf.to_postgis(table_name, conn, if_exists='replace', index=False)
        conn.close()

        return {'success': True, 'message': f'Capa {table_name} importada con éxito'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
