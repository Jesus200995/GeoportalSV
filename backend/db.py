import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG  # Reutilizar la configuración existente

def get_data_from_db(query, params=None):
    """
    Ejecuta una consulta en la base de datos y devuelve los resultados
    
    Args:
        query: Consulta SQL a ejecutar
        params: Parámetros para la consulta (opcional)
        
    Returns:
        list: Resultados de la consulta o None si hay error
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print("Error en consulta DB:", e)
        return None
