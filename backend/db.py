import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG  # Reutilizar la configuración existente

def get_data_from_db(query):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print("Error en consulta DB:", e)
        return None
