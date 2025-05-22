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
        visible: false, // Por defecto apagado para que se controle desde el gestor de capas
        type: 'wms',
        url: geoserverUrl + '/sembrando/wms',
        params: {
          'LAYERS': 'sembrando:territorios_28',
          'TILED': true,
          'FORMAT': 'image/png',
          'TRANSPARENT': true,
          'VERSION': '1.1.1'
        }
      },
      {
        id: 1,
        name: 'Unidades de riego',
        description: 'Unidades de riego en México',
        visible: false,
        type: 'wms',
        url: geoserverUrl + '/sembrando/wms',
        params: {
          'LAYERS': 'sembrando:unidades_riego',
          'TILED': true,
          'FORMAT': 'image/png',
          'TRANSPARENT': true,
          'VERSION': '1.1.1'
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
        url: geoserverUrl + '/sembrando/wms',
        params: {
          'LAYERS': 'sembrando:municipios_hidalgo',
          'TILED': true,
          'FORMAT': 'image/png',
          'TRANSPARENT': true,
          'VERSION': '1.1.1'
        }
      },
      {
        id: 3,
        name: 'Ríos',
        description: 'Red hidrológica principal',
        visible: false,
        type: 'wms',
        url: geoserverUrl + '/sembrando/wms',
        params: {
          'LAYERS': 'sembrando:rios',
          'TILED': true,
          'FORMAT': 'image/png',
          'TRANSPARENT': true,
          'VERSION': '1.1.1'
        }
      },
    ],
    // Grupo para capas dinámicas añadidas desde el explorador de capas
    dinamicas: []
  });

  // Función para añadir una capa dinámica basada en datos de GeoServer
  const addDynamicLayer = (layer) => {
    // Evitar duplicados
    if (layerGroups.value.dinamicas.some(l => l.name === layer.name)) {
      return;
    }
    
    const newLayer = {
      id: `dynamic-${Date.now()}`,
      name: layer.name,
      title: layer.title || layer.name,
      description: layer.abstract || 'Capa dinámica de GeoServer',
      visible: true,
      type: 'wms',
      url: layer.wmsUrl || `${geoserverUrl}/sembrando/wms`,
      params: {
        'LAYERS': layer.fullName || `sembrando:${layer.name}`,
        'TILED': true,
        'FORMAT': 'image/png', 
        'TRANSPARENT': true,
        'VERSION': '1.1.1'
      },
      legendUrl: layer.legendUrl
    };
    
    layerGroups.value.dinamicas.push(newLayer);
    return newLayer;
  };

  // Función para eliminar una capa dinámica
  const removeDynamicLayer = (layerName) => {
    layerGroups.value.dinamicas = layerGroups.value.dinamicas.filter(
      layer => layer.name !== layerName
    );
  };

  return {
    layerGroups,
    addDynamicLayer,
    removeDynamicLayer
  };
}
