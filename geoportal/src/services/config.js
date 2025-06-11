/**
 * Configuración centralizada para servicios de API
 */

// Obtener URL base de la API desde variables de entorno o usar un valor por defecto
export const API_URL = import.meta.env.VITE_API_URL || 'https://geoportal.sembrandodatos.com/api';

// Rutas específicas de API - todas en minúsculas para evitar problemas
export const API_ROUTES = {
  // Asegurarse que todas las rutas estén en minúsculas
  UPLOAD_SHAPEFILE: `${API_URL}/upload-shapefile`,
  LAYERS: `${API_URL}/layers`,
  PROCESS_SHAPEFILE: `${API_URL}/process-shapefile`,
};

// Configuración para solicitudes
export const API_CONFIG = {
  DEFAULT_TIMEOUT: 600000,
  WITH_CREDENTIALS: false,  // Cambiado a false para evitar problemas de CORS
  // Añadir configuración CORS explícita para axios
  HEADERS: {
    'Content-Type': 'multipart/form-data',
    'Accept': 'application/json'
  }
};
