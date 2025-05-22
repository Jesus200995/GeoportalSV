<script setup>
import { ref, onMounted, watch } from 'vue';
import { getWMSCapabilities, getWMSLayerParams, getGeoServerUrl } from '../../services/geoserver';
import TileLayer from 'ol/layer/Tile';
import TileWMS from 'ol/source/TileWMS';
import { Group as LayerGroup } from 'ol/layer';

const props = defineProps({
  map: Object,
  expanded: {
    type: Boolean,
    default: true
  }
});

// Estado local del componente
const availableLayers = ref([]);
const loading = ref(false);
const error = ref(null);
const showLegend = ref({});
const addedLayerIds = ref(new Set());
const searchQuery = ref('');
const isExpanded = ref(true);

// Cargar las capas disponibles cuando se monte el componente
onMounted(async () => {
  await fetchAvailableLayers();
});

// Cargar las capas desde GeoServer
async function fetchAvailableLayers() {
  loading.value = true;
  error.value = null;
  
  try {
    availableLayers.value = await getWMSCapabilities();
    
    // Verificar las capas que ya están añadidas al mapa
    updateAddedLayersState();
  } catch (err) {
    console.error('Error al cargar capas disponibles:', err);
    error.value = 'No se pudieron cargar las capas. Intente nuevamente.';
  } finally {
    loading.value = false;
  }
}

// Actualiza el estado de las capas ya añadidas
function updateAddedLayersState() {
  addedLayerIds.value.clear();
  
  if (props.map) {
    props.map.getLayers().forEach(layer => {
      const source = layer.getSource();
      if (source instanceof TileWMS) {
        const params = source.getParams();
        if (params && params.LAYERS) {
          // Extraer el ID de la capa a partir del nombre completo (workspace:nombre)
          const layerName = params.LAYERS;
          const layerId = layerName.split(':')[1]; // Quitar el prefijo del workspace
          if (layerId) {
            addedLayerIds.value.add(layerId);
          }
        }
      }
    });
  }
}

// Agregar una capa al mapa
function addLayer(layer) {
  if (!props.map || !layer) return;
  
  // Crear la fuente WMS para la capa
  const wmsSource = new TileWMS({
    url: getGeoServerUrl() + '/wms',
    params: getWMSLayerParams(layer.name),
    serverType: 'geoserver',
    transition: 250,
  });
  
  // Crear la capa OpenLayers
  const wmsLayer = new TileLayer({
    source: wmsSource,
    properties: {
      name: layer.title,
      id: layer.id,
      group: 'dinamicas', // Grupo para capas añadidas dinámicamente
      type: 'wms',
      sourceLayer: layer  // Almacenar la información original de la capa
    }
  });
  
  // Añadir la capa al mapa
  props.map.addLayer(wmsLayer);
  
  // Actualizar el estado de las capas añadidas
  addedLayerIds.value.add(layer.id);
}

// Remover una capa del mapa
function removeLayer(layer) {
  if (!props.map) return;
  
  const layers = props.map.getLayers().getArray();
  const layerToRemove = layers.find(l => {
    return l.get('id') === layer.id;
  });
  
  if (layerToRemove) {
    props.map.removeLayer(layerToRemove);
    addedLayerIds.value.delete(layer.id);
  }
}

// Mostrar/ocultar leyenda
function toggleLegend(layerId) {
  showLegend.value = {
    ...showLegend.value,
    [layerId]: !showLegend.value[layerId]
  };
}

// Actualizar el estado de capas añadidas cuando cambie el mapa
watch(() => props.map, () => {
  if (props.map) {
    updateAddedLayersState();
    
    // Escuchar eventos de adición/eliminación de capas
    props.map.getLayers().on('add', updateAddedLayersState);
    props.map.getLayers().on('remove', updateAddedLayersState);
  }
});

// Filtrar capas según la búsqueda
const filteredLayers = computed(() => {
  if (!searchQuery.value) {
    return availableLayers.value;
  }
  
  const query = searchQuery.value.toLowerCase();
  return availableLayers.value.filter(layer => 
    layer.title.toLowerCase().includes(query) || 
    layer.description.toLowerCase().includes(query)
  );
});

// Alternar la expansión del panel
function toggleExpand() {
  isExpanded.value = !isExpanded.value;
}
</script>

<template>
  <div class="available-layers p-4">
    <div class="mb-4 flex items-center justify-between">
      <h3 class="text-base font-medium text-gray-700 flex items-center space-x-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
        <span>Capas disponibles</span>
      </h3>
      <button @click="toggleExpand" class="p-1.5 rounded-full text-gray-500 hover:bg-gray-100">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" :class="{'rotate-180': !isExpanded}">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
    </div>
    
    <div v-if="isExpanded" class="space-y-4">
      <!-- Buscador -->
      <div class="relative">
        <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" 
             fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar capas..."
          class="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg
                 focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
        />
      </div>
      
      <!-- Estado de carga -->
      <div v-if="loading" class="flex justify-center py-4">
        <div class="animate-spin rounded-full h-6 w-6 border-2 border-green-500 border-t-transparent"></div>
      </div>
      
      <!-- Mensaje de error -->
      <div v-if="error" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">
        {{ error }}
        <button @click="fetchAvailableLayers" class="ml-2 underline">Reintentar</button>
      </div>
      
      <!-- Lista de capas disponibles -->
      <div v-if="!loading && !error" class="space-y-3 max-h-[350px] overflow-y-auto pr-1">
        <div v-for="layer in filteredLayers" :key="layer.id"
             class="border border-gray-100 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow bg-white">
          <div class="p-3">
            <!-- Cabecera de la capa -->
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <h4 class="text-sm font-medium text-gray-800">{{ layer.title }}</h4>
                <p v-if="layer.description" class="text-xs text-gray-500 truncate">{{ layer.description }}</p>
              </div>
              
              <!-- Botón para añadir/remover capa -->
              <button v-if="!addedLayerIds.has(layer.id)" 
                      @click="addLayer(layer)"
                      class="p-1.5 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                      title="Agregar capa">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </button>
              
              <button v-else 
                      @click="removeLayer(layer)"
                      class="p-1.5 text-green-600 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                      title="Quitar capa">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <!-- Enlaces a leyenda e información -->
            <div class="mt-2 flex space-x-2 text-xs">
              <button @click="toggleLegend(layer.id)" 
                      class="text-blue-600 hover:text-blue-800 hover:underline flex items-center">
                <span>{{ showLegend[layer.id] ? 'Ocultar' : 'Ver' }} leyenda</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 ml-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5 4v3H4a2 2 0 00-2 2v3a2 2 0 002 2h1v2a2 2 0 002 2h6a2 2 0 002-2v-2h1a2 2 0 002-2V9a2 2 0 00-2-2h-1V4a2 2 0 00-2-2H7a2 2 0 00-2 2zm8 0v3H7V4h6z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
          
          <!-- Leyenda expandible -->
          <div v-if="showLegend[layer.id]" class="bg-gray-50 p-3 border-t border-gray-100">
            <img :src="layer.legendUrl" :alt="`Leyenda ${layer.title}`" 
                 class="mx-auto" 
                 @error="$event.target.src = 'data:image/svg+xml;charset=utf-8,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'24\' height=\'24\' viewBox=\'0 0 24 24\'%3E%3Cpath fill=\'%23CCC\' d=\'M21.9,21.9l-8.9-8.9l-9,9H3v-1l9-9L3,3V2h1l9,9l8.9-8.9L21.9,21.9z M21.9,2H21l-9,9L3,2H2v1l9,9l-9,9v1h1l9-9l9,9h1L21.9,2z\'/%3E%3C/svg%3E';" />
          </div>
        </div>
      </div>
      
      <!-- Mensaje si no hay resultados -->
      <div v-if="!loading && !error && filteredLayers.length === 0" class="text-center py-4">
        <p class="text-gray-500">No se encontraron capas disponibles</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Estilos para el scrollbar */
.max-h-\[350px\] {
  scrollbar-width: thin;
  scrollbar-color: #10B981 #E5E7EB;
}

.max-h-\[350px\]::-webkit-scrollbar {
  width: 6px;
}

.max-h-\[350px\]::-webkit-scrollbar-track {
  background: #E5E7EB;
  border-radius: 3px;
}

.max-h-\[350px\]::-webkit-scrollbar-thumb {
  background-color: #10B981;
  border-radius: 3px;
}

/* Animación para leyendas */
[v-if="showLegend[layer.id]"] {
  animation: expandIn 0.3s ease-out;
}

@keyframes expandIn {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 200px;
  }
}
</style>
