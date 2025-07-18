/**
 * Configuración para servicios de GeoServer con proxy
 */

// URL del backend local que actuará como proxy
export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000';

// Configuración del proxy para GeoServer
export const GEOSERVER_PROXY_CONFIG = {
  // URL del proxy local
  PROXY_BASE_URL: `${BACKEND_URL}/api/proxy/geoserver`,
  
  // Workspace por defecto
  WORKSPACE: 'sembrando',
  
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
  
  // Configuración original del GeoServer (para referencia)
  ORIGINAL_GEOSERVER_URL: 'https://geoportal.sembrandodatos.com/geoserver',
  
  // Timeout para solicitudes
  REQUEST_TIMEOUT: 30000
};

export default GEOSERVER_PROXY_CONFIG;
