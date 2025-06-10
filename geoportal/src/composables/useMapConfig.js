import { ref } from 'vue';
import { fromLonLat } from 'ol/proj';

export function useMapConfig() {
  // Configuración de servidor GeoServer
  const geoServerConfig = ref({
    baseUrl: 'http://31.97.8.51:8082/geoserver',
    workspace: 'sembrando',
    wmsUrl: 'http://31.97.8.51:8082/geoserver/sembrando/wms',
    wfsUrl: 'http://31.97.8.51:8082/geoserver/ows'
  });
  
  // Configuración inicial del mapa
  const initialMapConfig = ref({
    center: fromLonLat([-98.9, 20.1]), // Hidalgo, México
    zoom: 9,
    minZoom: 5,
    maxZoom: 19,
    projection: 'EPSG:3857' // Web Mercator - estándar para visualización web
  });
  
  // Opciones de interacción
  const mapInteractions = ref({
    doubleClickZoom: true,
    dragPan: true,
    mouseWheelZoom: true,
    keyboard: true
  });
  
  // Configuración de controles del mapa
  const mapControls = ref({
    showZoom: true,
    showFullscreen: true,
    showRotation: false,
    showAttribution: true,
    showScaleLine: true
  });

  return {
    geoServerConfig,
    initialMapConfig,
    mapInteractions,
    mapControls
  };
}
