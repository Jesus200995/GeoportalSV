/**
 * Configuración centralizada para servicios de API
 */

// Obtener URL base de la API desde variables de entorno o usar un valor por defecto
export const API_URL = import.meta.env.VITE_API_URL || 'https://geoportal.sembrandodatos.com/api';

// Rutas específicas de API - todas en minúsculas para evitar problemas
export const API_ROUTES = {
  // Usamos la ruta en minúsculas para que coincida con el backend
  UPLOAD_SHAPEFILE: `${API_URL}/upload-shapefile`,
  LAYERS: `${API_URL}/layers`,
  PROCESS_SHAPEFILE: `${API_URL}/process-shapefile`,
};

// Configuración para solicitudes
export const API_CONFIG = {
  DEFAULT_TIMEOUT: 600000,
  WITH_CREDENTIALS: true,
};
