"""
Utilidades para la aplicación GeoportalSV.
Este módulo contiene funciones auxiliares para el procesamiento de datos
y otras operaciones comunes utilizadas en la aplicación.
"""

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
