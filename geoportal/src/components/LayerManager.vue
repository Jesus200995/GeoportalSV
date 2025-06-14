<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { getAvailableLayers } from '../services/geoserver';
import TileLayer from 'ol/layer/Tile';
import TileWMS from 'ol/source/TileWMS';

const props = defineProps({
  map: {
    type: Object,
    required: true
  }
});

// Estado para almacenar las capas
const layers = ref([]);
const activeLayers = ref([]);
const loadingLayers = ref(true);
const error = ref(null);
const searchQuery = ref('');

// Estado para guardar referencias a las capas de OpenLayers
const olLayers = ref({});

// Añadir ref para almacenar opacidades
const layerOpacities = ref({});

// Obtener las capas de GeoServer al montar el componente
onMounted(async () => {
  // Cargar opacidades guardadas
  const savedOpacities = JSON.parse(localStorage.getItem('layerOpacities') || '{}');
  layerOpacities.value = { ...savedOpacities };
  
  await fetchLayers();
  
  // Cargamos estado guardado de localStorage si existe
  const savedActiveLayers = localStorage.getItem('activeLayers');
  if (savedActiveLayers) {
    try {
      const parsed = JSON.parse(savedActiveLayers);
      activeLayers.value = Array.isArray(parsed) ? parsed : [];
      
      // Activar las capas guardadas sólo si existen
      activeLayers.value.forEach(layerName => {
        const layer = layers.value.find(l => l.name === layerName);
        if (layer) {
          addLayerToMap(layer);
        }
      });
      
      // Limpiar activeLayers para que solo contenga capas que realmente existen
      activeLayers.value = activeLayers.value.filter(layerName => 
        layers.value.some(l => l.name === layerName)
      );
      
      // Guardar el estado actualizado
      localStorage.setItem('activeLayers', JSON.stringify(activeLayers.value));
    } catch (e) {
      console.error('Error al cargar capas guardadas:', e);
    }
  }
});

// Filtrar capas por búsqueda
const filteredLayers = computed(() => {
  if (!searchQuery.value) {
    return layers.value;
  }
  
  const query = searchQuery.value.toLowerCase();
  return layers.value.filter(layer => 
    layer.name.toLowerCase().includes(query) || 
    layer.title?.toLowerCase().includes(query)
  );
});

// Función para obtener las capas desde GeoServer
const fetchLayers = async () => {
  loadingLayers.value = true;
  error.value = null;
  
  try {
    const availableLayers = await getAvailableLayers();
    console.log('Capas obtenidas de GeoServer:', availableLayers);
    
    // Si no hay capas disponibles, mostrar un mensaje claro
    if (availableLayers.length === 0) {
      console.log('No se encontraron capas disponibles en GeoServer');
    }
    
    layers.value = availableLayers;
    
    // Actualizar referencias de capas en el mapa
    updateMapLayers();
  } catch (err) {
    console.error('Error al obtener capas:', err);
    error.value = 'No se pudieron cargar las capas de GeoServer. Verifique que el servidor esté disponible.';
  } finally {
    loadingLayers.value = false;
  }
};

// Actualiza las capas en el mapa cuando cambia la lista de capas disponibles
const updateMapLayers = () => {
  if (!props.map) return;
  
  // Obtener nombre de todas las capas disponibles
  const availableLayerNames = new Set(layers.value.map(l => l.name));
  
  // Eliminar capas del mapa que ya no existen en el servidor
  const layersToRemove = [];
  props.map.getLayers().forEach(layer => {
    const layerName = layer.get('name');
    if (layerName && !availableLayerNames.has(layerName) && layer.get('type') === 'wms') {
      layersToRemove.push(layer);
      
      // Eliminar de activeLayers
      activeLayers.value = activeLayers.value.filter(name => name !== layerName);
    }
  });
  
  // Remover las capas obsoletas
  layersToRemove.forEach(layer => {
    props.map.removeLayer(layer);
    const name = layer.get('name');
    if (name && olLayers.value[name]) {
      delete olLayers.value[name];
    }
  });
  
  if (layersToRemove.length > 0) {
    console.log(`Se eliminaron ${layersToRemove.length} capas obsoletas del mapa`);
    // Guardar estado actualizado
    localStorage.setItem('activeLayers', JSON.stringify(activeLayers.value));
  }
};

// Función para verificar si una capa está activa
const isLayerActive = (layerName) => {
  return activeLayers.value.includes(layerName);
};

// Función para alternar el estado de una capa
const toggleLayer = (layer) => {
  const isActive = isLayerActive(layer.name);
  
  if (isActive) {
    // Desactivar la capa
    activeLayers.value = activeLayers.value.filter(name => name !== layer.name);
    removeLayerFromMap(layer);
  } else {
    // Activar la capa
    activeLayers.value.push(layer.name);
    addLayerToMap(layer);
  }
  
  // Guardar estado en localStorage
  localStorage.setItem('activeLayers', JSON.stringify(activeLayers.value));
};

// Función modificada para actualizar la opacidad
const updateOpacity = (layer, opacity) => {
  if (!props.map) return;
  
  // Convertir a número si viene como string
  const opacityValue = parseFloat(opacity);
  
  // Validar que sea un número válido entre 0 y 1
  if (isNaN(opacityValue) || opacityValue < 0 || opacityValue > 1) {
    console.error('Valor de opacidad inválido:', opacity);
    return;
  }
  
  // Actualizar el estado local
  layerOpacities.value[layer.name] = opacityValue;
  
  // Actualizar la opacidad en el mapa
  const olLayer = olLayers.value[layer.name];
  if (olLayer) {
    olLayer.setOpacity(opacityValue);
    
    // Forzar actualización del mapa
    props.map.render();
  }
  
  // Guardar estado en localStorage para persistencia
  const opacityState = JSON.parse(localStorage.getItem('layerOpacities') || '{}');
  opacityState[layer.name] = opacityValue;
  localStorage.setItem('layerOpacities', JSON.stringify(opacityState));
};

// Añadir la capa al mapa
const addLayerToMap = (layer) => {
  if (!props.map || !layer) {
    console.error('No se puede añadir capa: Mapa o capa no definidos');
    return;
  }
  
  // Establecer opacidad inicial si no existe
  if (!(layer.name in layerOpacities.value)) {
    layerOpacities.value[layer.name] = 1;
  }
  
  // Si la capa ya existe en el mapa, solo hacerla visible
  if (olLayers.value[layer.name]) {
    console.log(`Haciendo visible la capa existente: ${layer.name}`);
    olLayers.value[layer.name].setVisible(true);
    return;
  }
  
  console.log(`Añadiendo nueva capa al mapa: ${layer.name}`, layer);
  
  // Crear la fuente WMS
  const wmsSource = new TileWMS({
    url: layer.wmsUrl || 'https://geoportal.sembrandodatos.com/geoserver/sembrando/wms',
    params: {
      'LAYERS': layer.fullName || `sembrando:${layer.name}`,
      'TILED': true,
      'FORMAT': 'image/png',
      'TRANSPARENT': true,
      'VERSION': '1.1.1'
    },
    serverType: 'geoserver',
    transition: 250,
    crossOrigin: 'anonymous'
  });
  
  // Crear la capa OpenLayers
  const wmsLayer = new TileLayer({
    source: wmsSource,
    properties: {
      title: layer.title || layer.name,
      name: layer.name,
      id: layer.name,
      type: 'wms',
      group: 'dynamic'
    },
    visible: true,
    zIndex: 10 // Asegurar que aparezca sobre la capa base pero debajo de otros elementos
  });
  
  // Añadir la capa al mapa
  props.map.addLayer(wmsLayer);
  
  // Guardar referencia a la capa
  olLayers.value[layer.name] = wmsLayer;
  
  // Cargar opacidad guardada o usar valor por defecto
  const savedOpacities = JSON.parse(localStorage.getItem('layerOpacities') || '{}');
  if (!(layer.name in layerOpacities.value)) {
    layerOpacities.value[layer.name] = savedOpacities[layer.name] || 1;
  }
  
  // Asignar opacidad al crear la capa
  wmsLayer.setOpacity(layerOpacities.value[layer.name]);
  
  console.log(`Capa ${layer.name} añadida al mapa correctamente`);
};

// Remover la capa del mapa (o hacerla invisible)
const removeLayerFromMap = (layer) => {
  if (!props.map || !layer) {
    console.error('No se puede remover capa: Mapa o capa no definidos');
    return;
  }
  
  if (olLayers.value[layer.name]) {
    console.log(`Removiendo capa del mapa: ${layer.name}`);
    
    // Remover completamente la capa del mapa
    props.map.removeLayer(olLayers.value[layer.name]);
    delete olLayers.value[layer.name];
  } else {
    console.warn(`Intento de remover capa no existente: ${layer.name}`);
  }
};

// Refrescar las capas
const refreshLayers = async () => {
  await fetchLayers();
};

// Observar cambios en el mapa - si el mapa cambia, actualizar las capas
watch(() => props.map, (newMap) => {
  if (newMap) {
    console.log('El mapa cambió, actualizando capas...');
    // Limpiar las capas existentes
    Object.values(olLayers.value).forEach(layer => {
      newMap.removeLayer(layer);
    });
    olLayers.value = {};
    
    // Volver a añadir las capas activas
    activeLayers.value.forEach(layerName => {
      const layer = layers.value.find(l => l.name === layerName);
      if (layer) {
        addLayerToMap(layer);
      }
    });
  }
}, { immediate: true });
</script>

<template>
  <div class="layer-manager space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-medium text-gray-800">Capas disponibles</h3>
      <button 
        @click="refreshLayers" 
        class="p-1 text-gray-500 hover:text-green-600 rounded-full hover:bg-gray-100"
        :class="{'animate-spin': loadingLayers}"
        :disabled="loadingLayers"
        title="Refrescar capas"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </div>
    
    <!-- Buscador de capas -->
    <div class="relative">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Buscar capas..."
        class="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg
               focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
      />
      <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" 
           fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
      </svg>
    </div>
    
    <!-- Estado de carga -->
    <div v-if="loadingLayers" class="flex justify-center py-4">
      <div class="animate-spin rounded-full h-6 w-6 border-2 border-green-500 border-t-transparent"></div>
    </div>
    
    <!-- Mensaje de error -->
    <div v-else-if="error" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">
      {{ error }}
      <button @click="fetchLayers" class="ml-2 underline">Reintentar</button>
    </div>
    
    <!-- Lista de capas modificada -->
    <div v-else class="space-y-3 max-h-[400px] overflow-y-auto scrollbar-thin">
      <div v-if="filteredLayers.length === 0" class="text-center py-8">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
        <p class="text-gray-500 font-medium">No hay capas disponibles</p>
        <p class="text-gray-400 text-sm mt-2">
          {{ searchQuery ? 'No se encontraron capas que coincidan con la búsqueda.' : 'No hay capas disponibles en el servidor. Sube una nueva capa para comenzar.' }}
        </p>
        <button 
          @click="refreshLayers" 
          class="mt-4 px-4 py-2 bg-green-100 hover:bg-green-200 text-green-700 rounded-lg transition-colors flex items-center space-x-2 mx-auto"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Actualizar</span>
        </button>
      </div>
      
      <div v-for="layer in filteredLayers" 
           :key="layer.name"
           class="bg-white border border-gray-100 rounded-lg hover:bg-gray-50 transition-all">
        <!-- Contenedor principal de la capa -->
        <div class="p-3">
          <div class="flex items-center space-x-3">
            <!-- Switch para activar/desactivar capa -->
            <div class="relative inline-block w-10 mr-2 align-middle select-none">
              <input 
                type="checkbox" 
                :id="`layer-${layer.name}`" 
                :checked="isLayerActive(layer.name)"
                @change="toggleLayer(layer)" 
                class="opacity-0 absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
              />
              <label 
                :for="`layer-${layer.name}`" 
                class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"
                :class="{'active': isLayerActive(layer.name)}"
              ></label>
            </div>
            
            <!-- Información de la capa -->
            <div class="flex-1">
              <h4 class="text-sm font-medium text-gray-800">{{ layer.title || layer.name }}</h4>
              <p v-if="layer.abstract" class="text-xs text-gray-500 truncate">{{ layer.abstract }}</p>
            </div>
          </div>
        </div>
        
        <!-- Control de opacidad - Solo visible cuando la capa está activa -->
        <div v-if="isLayerActive(layer.name)" 
             class="px-3 pb-3 pt-1 border-t border-gray-100 animate-fade-in">
          <div class="flex items-center space-x-3">
            <label :for="`opacity-${layer.name}`" class="text-xs text-gray-500 w-16 select-none">
              {{ Math.round((layerOpacities[layer.name] || 1) * 100) }}%
            </label>
            <input 
              type="range"
              :id="`opacity-${layer.name}`"
              :value="layerOpacities[layer.name] || 1"
              @input="updateOpacity(layer, $event.target.value)"
              min="0"
              max="1"
              step="0.1"
              class="flex-1 h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-green-500 hover:accent-green-600"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Información de debug -->
    <div class="mt-4 p-3 text-xs text-gray-500 bg-gray-50 rounded-lg">
      <p>{{ activeLayers.length }} capa(s) activa(s)</p>
      <p v-if="Object.keys(olLayers).length > 0">
        Capas en el mapa: {{ Object.keys(olLayers).join(', ') }}
      </p>
    </div>
  </div>
</template>

<style scoped>
/* Estilos para el toggle switch */
.toggle-label {
  position: relative;
  display: block;
  width: 3rem;
  height: 1.5rem;
  border-radius: 9999px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  background-color: #D1D5DB;
}

.toggle-label.active {
  background-color: #10B981;
}

.toggle-label::after {
  content: '';
  position: absolute;
  top: 0.25rem;
  left: 0.25rem;
  background-color: white;
  width: 1rem;
  height: 1rem;
  border-radius: 9999px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease-in-out;
}

.toggle-label.active::after {
  transform: translateX(1.5rem);
}

/* Estilos para el scrollbar */
.scrollbar-thin {
  scrollbar-width: thin;
  scrollbar-color: #10B981 #E5E7EB;
}

.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: #E5E7EB;
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: #10B981;
  border-radius: 3px;
}

/* Animación para el botón de refrescar */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Estilos para el control de opacidad */
input[type="range"] {
  -webkit-appearance: none;
  @apply bg-gray-200 h-1.5 rounded-lg;
  background-image: linear-gradient(to right, #10B981, #10B981);
  background-size: calc(var(--value, 0) * 100%) 100%;
  background-repeat: no-repeat;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  @apply w-3 h-3 bg-green-500 rounded-full cursor-pointer transition-all;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

input[type="range"]:hover::-webkit-slider-thumb {
  @apply transform scale-125 bg-green-600;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
}

/* Ajustar animación de aparición */
.animate-fade-in {
  animation: fadeIn 0.2s ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
