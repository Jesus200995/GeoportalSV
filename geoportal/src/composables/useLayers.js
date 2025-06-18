import { ref, onMounted } from 'vue';
import { getAvailableLayers } from '../services/geoserver';

// Configuración de grupos de capas 
export function useLayers() {
  const geoserverUrl = import.meta.env.VITE_GEOSERVER_URL || 'https://geoportal.sembrandodatos.com/geoserver';
  
  // Lista de capas predefinidas que queremos mostrar si existen
  const predefinedLayerNames = {
    principal: ['territorios_28', 'unidades_riego'],
    extras: ['municipios_hidalgo', 'rios']
  };

  // Estado reactivo para las capas que realmente están disponibles
  const layerGroups = ref({
    principal: [],
    extras: [],
    dinamicas: []
  });
  
  // Estado de carga
  const isLoadingLayers = ref(false);
  const loadError = ref(null);
  const lastUpdated = ref(null);

  // Función para cargar y verificar capas disponibles
  const loadAvailableLayers = async () => {
    isLoadingLayers.value = true;
    loadError.value = null;
    
    try {
      // Obtener capas disponibles desde GeoServer
      const availableLayers = await getAvailableLayers();
      console.log('Capas obtenidas de GeoServer:', availableLayers);
      
      // Crear un mapa de capas disponibles para búsqueda rápida
      const availableLayersMap = new Map();
      availableLayers.forEach(layer => {
        // Extraer el nombre de la capa sin el prefijo del workspace
        const layerName = layer.name.includes(':') 
          ? layer.name.split(':')[1] 
          : layer.name;
        availableLayersMap.set(layerName.toLowerCase(), layer);
      });
      
      // Actualizar capas principales
      layerGroups.value.principal = [];
      predefinedLayerNames.principal.forEach((layerName, index) => {
        const availableLayer = availableLayersMap.get(layerName.toLowerCase());
        if (availableLayer) {
          layerGroups.value.principal.push({
            id: index,
            name: layerName,
            description: availableLayer.abstract || `Capa ${layerName}`,
            visible: false,
            type: 'wms',
            url: `${geoserverUrl}/sembrando/wms`,
            params: {
              'LAYERS': `sembrando:${layerName}`,
              'TILED': true,
              'FORMAT': 'image/png',
              'TRANSPARENT': true,
              'VERSION': '1.1.1'
            }
          });
        }
      });
      
      // Actualizar capas extras
      layerGroups.value.extras = [];
      predefinedLayerNames.extras.forEach((layerName, index) => {
        const availableLayer = availableLayersMap.get(layerName.toLowerCase());
        if (availableLayer) {
          layerGroups.value.extras.push({
            id: index + 2, // Continuar con la secuencia de IDs
            name: layerName,
            description: availableLayer.abstract || `Capa ${layerName}`,
            visible: false,
            type: 'wms',
            url: `${geoserverUrl}/sembrando/wms`,
            params: {
              'LAYERS': `sembrando:${layerName}`,
              'TILED': true,
              'FORMAT': 'image/png',
              'TRANSPARENT': true,
              'VERSION': '1.1.1'
            }
          });
        }
      });
      
      // Añadir cualquier otra capa disponible como dinámica
      availableLayers.forEach(layer => {
        const layerName = layer.name.includes(':') ? layer.name.split(':')[1] : layer.name;
        
        // Solo agregar si no está ya en principal o extras
        if (!predefinedLayerNames.principal.includes(layerName) && 
            !predefinedLayerNames.extras.includes(layerName)) {
          // Verificar si ya existe en capas dinámicas
          const exists = layerGroups.value.dinamicas.some(l => l.name === layerName);
          if (!exists) {
            addDynamicLayer(layer);
          }
        }
      });
      
      lastUpdated.value = new Date();
    } catch (error) {
      console.error('Error al cargar capas desde GeoServer:', error);
      loadError.value = 'No se pudieron cargar las capas de GeoServer';
    } finally {
      isLoadingLayers.value = false;
    }
  };

  // Función para añadir una capa dinámica basada en datos de GeoServer
  const addDynamicLayer = (layer) => {
    // Evitar duplicados
    if (layerGroups.value.dinamicas.some(l => l.name === layer.name)) {
      return;
    }
    
    const layerName = layer.name.includes(':') ? layer.name.split(':')[1] : layer.name;
    
    const newLayer = {
      id: `dynamic-${Date.now()}`,
      name: layerName,
      title: layer.title || layerName,
      description: layer.abstract || 'Capa dinámica de GeoServer',
      visible: true,
      type: 'wms',
      url: layer.wmsUrl || `${geoserverUrl}/sembrando/wms`,
      params: {
        'LAYERS': layer.fullName || `sembrando:${layerName}`,
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

  // Cargar capas al inicializar
  onMounted(() => {
    loadAvailableLayers();
  });

  return {
    layerGroups,
    addDynamicLayer,
    removeDynamicLayer,
    loadAvailableLayers,
    isLoadingLayers,
    loadError,
    lastUpdated
  };
}
