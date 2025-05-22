import { ref } from 'vue';

// Configuración de grupos de capas 
export function useLayers() {
  const geoserverUrl = 'http://31.97.8.51:8082/geoserver';

  const layerGroups = ref({
    principal: [
      {
        id: 0,
        name: 'Territorios',
        description: 'Capa de territorios sembrando datos',
        visible: true,
        type: 'wms',
        url: geoserverUrl + '/wms',
        params: {
          'LAYERS': 'sembrando:territorios_28',
          'TILED': true
        }
      },
      {
        id: 1,
        name: 'Unidades de riego',
        description: 'Unidades de riego en México',
        visible: false,
        type: 'wms',
        url: geoserverUrl + '/wms',
        params: {
          'LAYERS': 'sembrando:unidades_riego',
          'TILED': true
        }
      },
    ],
    extras: [
      {
        id: 2,
        name: 'Municipios',
        description: 'Límites municipales',
        visible: false,
        type: 'wms',
        url: geoserverUrl + '/wms',
        params: {
          'LAYERS': 'sembrando:municipios_hidalgo',
          'TILED': true
        }
      },
      {
        id: 3,
        name: 'Ríos',
        description: 'Red hidrológica principal',
        visible: false,
        type: 'wms',
        url: geoserverUrl + '/wms',
        params: {
          'LAYERS': 'sembrando:rios',
          'TILED': true
        }
      },
    ],
    // Nuevo grupo para capas dinámicas añadidas desde el explorador de capas
    dinamicas: []
  });

  return {
    layerGroups
  };
}
