/**
 * Configuración para servicios de GeoServer que funciona en desarrollo y producción
 */

// Detectar si estamos en desarrollo o producción
const isDevelopment = import.meta.env.MODE === 'development' || window.location.hostname === 'localhost';

// URL del backend local que actuará como proxy (solo para desarrollo)
export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000';

// Configuración del GeoServer original
export const GEOSERVER_CONFIG = {
  // URL del GeoServer real
  GEOSERVER_URL: 'https://geoportal.sembrandodatos.com/geoserver',
  
  // Workspace por defecto
  WORKSPACE: 'sembrando',
  
  // Credenciales (solo para desarrollo local)
  AUTH: {
    username: 'admin',
    password: 'geoserver'
  }
};

// Configuración del proxy para desarrollo
export const GEOSERVER_PROXY_CONFIG = {
  // URL del proxy local
  PROXY_BASE_URL: `${BACKEND_URL}/api/proxy/geoserver`,
  
  // Workspace por defecto
  WORKSPACE: GEOSERVER_CONFIG.WORKSPACE,
  
  // URLs específicas del proxy
  FEATURETYPES_URL: function(workspace = this.WORKSPACE) {
    return `${this.PROXY_BASE_URL}/rest/workspaces/${workspace}/featuretypes.json`;
  },
  
  WMS_URL: function(workspace = this.WORKSPACE) {
    return `${this.PROXY_BASE_URL}/${workspace}/wms`;
  },
  
  WFS_URL: function(workspace = this.WORKSPACE) {
    return `${this.PROXY_BASE_URL}/${workspace}/wfs`;
  },
  
  // Timeout para solicitudes
  REQUEST_TIMEOUT: 30000
};

// Configuración unificada que cambia según el entorno
export const ACTIVE_GEOSERVER_CONFIG = {
  // URLs que cambian según el entorno
  FEATURETYPES_URL: function(workspace = GEOSERVER_CONFIG.WORKSPACE) {
    if (isDevelopment) {
      return GEOSERVER_PROXY_CONFIG.FEATURETYPES_URL(workspace);
    } else {
      return `${GEOSERVER_CONFIG.GEOSERVER_URL}/rest/workspaces/${workspace}/featuretypes.json`;
    }
  },
  
  WMS_URL: function(workspace = GEOSERVER_CONFIG.WORKSPACE) {
    if (isDevelopment) {
      return GEOSERVER_PROXY_CONFIG.WMS_URL(workspace);
    } else {
      return `${GEOSERVER_CONFIG.GEOSERVER_URL}/${workspace}/wms`;
    }
  },
  
  WFS_URL: function(workspace = GEOSERVER_CONFIG.WORKSPACE) {
    if (isDevelopment) {
      return GEOSERVER_PROXY_CONFIG.WFS_URL(workspace);
    } else {
      return `${GEOSERVER_CONFIG.GEOSERVER_URL}/${workspace}/wfs`;
    }
  },
  
  // Método para obtener headers de autenticación (solo para desarrollo)
  getAuthHeaders: function() {
    if (isDevelopment) {
      // En desarrollo, el proxy maneja la autenticación
      return {};
    } else {
      // En producción, usar autenticación básica si es necesario
      return {
        'Authorization': 'Basic ' + btoa(`${GEOSERVER_CONFIG.AUTH.username}:${GEOSERVER_CONFIG.AUTH.password}`)
      };
    }
  },
  
  // Propiedades comunes
  WORKSPACE: GEOSERVER_CONFIG.WORKSPACE,
  IS_DEVELOPMENT: isDevelopment,
  REQUEST_TIMEOUT: 30000
};

export default ACTIVE_GEOSERVER_CONFIG;
