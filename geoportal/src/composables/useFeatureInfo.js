import { ref, computed } from 'vue';
import { getFeatureInfo, getFeatureInfoFromAllLayers } from '../services/featureInfoService';

export function useFeatureInfo() {
  // Estado
  const featureInfo = ref(null);
  const selectedFeature = ref(null);
  const loading = ref(false);
  const error = ref(null);
  const showPanel = ref(false);
  const clickCoordinate = ref(null);
  const activeLayer = ref(null);

  // Computed
  const hasFeatureInfo = computed(() => {
    return featureInfo.value && 
           featureInfo.value.features && 
           featureInfo.value.features.length > 0;
  });

  const featureProperties = computed(() => {
    if (!selectedFeature.value) return {};
    
    return selectedFeature.value.properties || {};
  });

  // Métodos
  const fetchFeatureInfo = async (map, coordinate, layer = null) => {
    if (!map || !coordinate) {
      error.value = 'Mapa o coordenadas no proporcionados';
      return;
    }

    // Configurar el listener de visibilidad si no se ha hecho antes
    // Usar un flag para evitar múltiples configuraciones
    if (!map.get('featureInfoListenerSet')) {
      setupLayerVisibilityListener(map);
      map.set('featureInfoListenerSet', true);
    }

    loading.value = true;
    error.value = null;
    clickCoordinate.value = coordinate;

    try {
      let result;

      if (layer) {
        // Consultar una capa específica
        activeLayer.value = layer;
        result = await getFeatureInfo(map, coordinate, layer);
      } else {
        // Consultar todas las capas visibles
        result = await getFeatureInfoFromAllLayers(map, coordinate);
        if (result.success && result.layerId) {
          // Actualizar la capa activa con la que devolvió resultados
          activeLayer.value = map.getLayers().getArray().find(l => 
            l.get('id') === result.layerId
          );
        }
      }

      featureInfo.value = result;
      
      if (result.success && result.features && result.features.length > 0) {
        selectedFeature.value = result.features[0];
        showPanel.value = true;
      } else {
        if (result.error) {
          error.value = result.error;
          // Modificado: No mostrar el panel si hay un error como "No hay capas visibles"
          if (result.error.includes("No hay capas visibles") || 
              result.error.includes("No se encontraron características")) {
            showPanel.value = false;
          } else {
            // Solo mantener el panel abierto para otros errores que sean informativos
            showPanel.value = true;
          }
        } else {
          error.value = 'No hay información disponible en esta ubicación';
          // Modificado: No mostrar el panel cuando no hay información
          showPanel.value = false;
        }
      }
    } catch (err) {
      console.error('Error al obtener información:', err);
      error.value = 'Error al consultar la información';
      featureInfo.value = null;
      selectedFeature.value = null;
      // Modificado: No mostrar el panel si hay un error crítico
      showPanel.value = false;
    } finally {
      loading.value = false;
    }
  };

  const closePanel = () => {
    showPanel.value = false;
    // Opcional: limpiar los datos al cerrar
    // featureInfo.value = null;
    // selectedFeature.value = null;
  };

  const selectFeature = (feature) => {
    if (feature) {
      selectedFeature.value = feature;
    }
  };

  // Añadir un watcher para detectar cambios en las capas del mapa
  const setupLayerVisibilityListener = (map) => {
    if (!map) return;

    // Función para verificar si hay alguna capa WMS visible
    const checkVisibleLayers = () => {
      const hasVisibleWmsLayers = map.getLayers().getArray().some(layer => {
        return layer.getVisible() && 
               layer.getSource() && 
               typeof layer.getSource().getFeatureInfoUrl === 'function';
      });

      // Si no hay capas visibles, cerrar el panel
      if (!hasVisibleWmsLayers) {
        showPanel.value = false;
        selectedFeature.value = null;
        featureInfo.value = null;
      }
    };

    // Observar cambios en la visibilidad de las capas
    map.getLayers().forEach(layer => {
      layer.on('change:visible', checkVisibleLayers);
    });

    // Observar cuando se añaden o eliminan capas
    map.getLayers().on('add', (event) => {
      const layer = event.element;
      layer.on('change:visible', checkVisibleLayers);
    });

    map.getLayers().on('remove', checkVisibleLayers);

    // Verificar estado inicial
    checkVisibleLayers();
  };

  return {
    // Estado
    featureInfo,
    selectedFeature,
    loading,
    error,
    showPanel,
    clickCoordinate,
    activeLayer,
    
    // Computed
    hasFeatureInfo,
    featureProperties,
    
    // Métodos
    fetchFeatureInfo,
    closePanel,
    selectFeature
  };
}
