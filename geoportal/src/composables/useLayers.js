import { ref } from 'vue';

export function useLayers() {
  // Configuración centralizada de capas
  const layerGroups = ref({
    principal: [
      {
        id: 1,
        name: 'Territorios',
        visible: true,
        type: 'wms',
        url: 'http://31.97.8.51:8082/geoserver/sembrando/wms', // URL actualizada
        params: {
          'LAYERS': 'sembrando:territorios_28', // Nombre de capa actualizado
          'TILED': true,
          'FORMAT': 'image/png',
          'TRANSPARENT': true,
          'VERSION': '1.1.1',
        },
        description: 'Capa base de territorios'
      }
    ],
    extras: [
      {
        id: 2,
        name: 'OpenStreetMap',
        visible: true,
        type: 'osm',
        description: 'Mapa base de OpenStreetMap'
      },
      {
        id: 3,
        name: 'Límites Administrativos',
        visible: false,
        type: 'wms',
        url: 'http://31.97.8.51:8082/geoserver/sembrando/wms', // URL actualizada
        params: {
          'LAYERS': 'sembrando:limites', // Ajustar según la capa disponible
          'TILED': true,
          'FORMAT': 'image/png',
          'TRANSPARENT': true,
          'VERSION': '1.1.1',
        },
        description: 'Límites administrativos del territorio'
      }
    ]
  });

  // Función para añadir una nueva capa al grupo específico
  const addLayer = (layer, group = 'extras') => {
    if (layerGroups.value[group]) {
      // Asignar un ID único a la nueva capa
      const newId = Math.max(...layerGroups.value[group].map(l => l.id), 0) + 1;
      layer.id = newId;
      layerGroups.value[group].push(layer);
      return true;
    }
    return false;
  };

  // Función para eliminar una capa por ID
  const removeLayer = (layerId, group) => {
    if (!group) {
      // Buscar en todos los grupos
      for (const groupName in layerGroups.value) {
        const index = layerGroups.value[groupName].findIndex(l => l.id === layerId);
        if (index !== -1) {
          layerGroups.value[groupName].splice(index, 1);
          return true;
        }
      }
    } else if (layerGroups.value[group]) {
      // Buscar en el grupo especificado
      const index = layerGroups.value[group].findIndex(l => l.id === layerId);
      if (index !== -1) {
        layerGroups.value[group].splice(index, 1);
        return true;
      }
    }
    return false;
  };

  // Función para actualizar una capa existente
  const updateLayer = (layerId, updates, group) => {
    if (!group) {
      // Buscar en todos los grupos
      for (const groupName in layerGroups.value) {
        const index = layerGroups.value[groupName].findIndex(l => l.id === layerId);
        if (index !== -1) {
          layerGroups.value[groupName][index] = {
            ...layerGroups.value[groupName][index],
            ...updates
          };
          return true;
        }
      }
    } else if (layerGroups.value[group]) {
      // Buscar en el grupo especificado
      const index = layerGroups.value[group].findIndex(l => l.id === layerId);
      if (index !== -1) {
        layerGroups.value[group][index] = {
          ...layerGroups.value[group][index],
          ...updates
        };
        return true;
      }
    }
    return false;
  };

  return {
    layerGroups,
    addLayer,
    removeLayer,
    updateLayer
  };
}
