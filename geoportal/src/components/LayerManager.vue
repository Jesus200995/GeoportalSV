<script setup>
import { ref, onMounted, watch, computed, onBeforeUnmount } from 'vue';
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

// Referencias para el manejo del scroll
const layersScrollWrapper = ref(null);
const layersList = ref(null);

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
  
  // Configurar manejo del scroll después de que se monte el componente
  setTimeout(() => {
    if (layersList.value) {
      updateScrollIndicators();
      layersList.value.addEventListener('scroll', updateScrollIndicators);
    }
  }, 300);
  
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
  
  // Actualizar indicadores de scroll después de refrescar
  setTimeout(() => {
    updateScrollIndicators();
  }, 300);
};

// Función para actualizar indicadores visuales de scroll
const updateScrollIndicators = () => {
  if (!layersList.value || !layersScrollWrapper.value) return;
  
  const { scrollTop, scrollHeight, clientHeight } = layersList.value;
  const canScrollUp = scrollTop > 5;
  const canScrollDown = scrollTop < (scrollHeight - clientHeight - 5);
  
  if (canScrollUp) {
    layersScrollWrapper.value.classList.add('can-scroll-up');
  } else {
    layersScrollWrapper.value.classList.remove('can-scroll-up');
  }
  
  if (canScrollDown) {
    layersScrollWrapper.value.classList.add('can-scroll-down');
  } else {
    layersScrollWrapper.value.classList.remove('can-scroll-down');
  }
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
  <div class="layer-manager rounded-xl bg-white shadow-lg p-5 border border-gray-100 max-w-md mx-auto md:mx-0 w-full">
    <!-- Encabezado con efecto de gradiente -->
    <div class="flex items-center justify-between mb-5 pb-3 border-b border-gray-100">
      <div class="flex items-center space-x-2">
        <div class="w-7 h-7 bg-gradient-to-tr from-green-600 to-emerald-400 rounded-lg flex items-center justify-center shadow-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-800">Capas disponibles</h3>
      </div>
      <div class="flex items-center space-x-2">
        <span class="text-xs text-gray-400 hidden sm:inline">{{ activeLayers.length }} activa(s)</span>
        <button 
          @click="refreshLayers" 
          class="refresh-button"
          :class="{'animate-spin-slow': loadingLayers}"
          :disabled="loadingLayers"
          title="Refrescar capas"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>
    
    <!-- Buscador de capas con diseño mejorado -->
    <div class="relative mb-4">
      <div class="search-container">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar capas..."
          class="search-input"
        />
        <svg class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </div>
    </div>
    
    <!-- Estado de carga con animación mejorada -->
    <div v-if="loadingLayers" class="flex justify-center items-center py-10">
      <div class="loader">
        <div class="loader-circle"></div>
        <div class="loader-line-mask">
          <div class="loader-line"></div>
        </div>
        <span class="text-xs text-green-500 mt-3 block text-center">Cargando capas...</span>
      </div>
    </div>
    
    <!-- Mensaje de error con mejor estilo -->
    <div v-else-if="error" class="p-4 bg-red-50 text-red-600 rounded-xl border border-red-100 text-sm mb-4 animate-fade-in">
      <div class="flex items-start space-x-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <p class="font-medium mb-1">No se pudieron cargar las capas</p>
          <p>{{ error }}</p>
          <button @click="fetchLayers" class="mt-2 text-red-700 hover:text-red-800 font-medium flex items-center space-x-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Reintentar</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Contenedor principal de la lista de capas con scroll mejorado -->
    <div v-else class="layers-scroll-container">
      <!-- Estado vacío mejorado -->
      <div v-if="filteredLayers.length === 0" class="empty-state">
        <div class="empty-icon-container">
          <svg xmlns="http://www.w3.org/2000/svg" class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
        </div>
        <p class="text-gray-600 font-medium">No hay capas disponibles</p>
        <p class="text-gray-400 text-sm mt-2">
          {{ searchQuery ? 'No se encontraron capas que coincidan con la búsqueda.' : 'No hay capas disponibles en el servidor. Sube una nueva capa para comenzar.' }}
        </p>
        <button 
          @click="refreshLayers" 
          class="empty-state-button"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Actualizar</span>
        </button>
      </div>
      
      <!-- Lista con scroll para las capas -->
      <div v-else ref="layersScrollWrapper" class="layers-scroll-wrapper">
        <div ref="layersList" class="layer-list">
          <!-- Listado de capas con diseño mejorado -->
          <div v-for="(layer, index) in filteredLayers" 
              :key="layer.name"
              class="layer-item"
              :style="{'--index': index}"
              :class="{'active-layer': isLayerActive(layer.name)}">
            <!-- Contenedor principal de la capa -->
            <div class="layer-header">
              <div class="flex items-center space-x-3">
                <!-- Switch para activar/desactivar capa -->
                <div class="toggle-container">
                  <input 
                    type="checkbox" 
                    :id="`layer-${layer.name}`" 
                    :checked="isLayerActive(layer.name)"
                    @change="toggleLayer(layer)" 
                    class="toggle-input"
                  />
                  <label 
                    :for="`layer-${layer.name}`" 
                    class="toggle-label"
                    :class="{'active': isLayerActive(layer.name)}"
                  ></label>
                </div>
                
                <!-- Información de la capa -->
                <div class="layer-info">
                  <h4 class="layer-title">{{ layer.title || layer.name }}</h4>
                  <p v-if="layer.abstract" class="layer-description">{{ layer.abstract }}</p>
                </div>
              </div>
            </div>
            
            <!-- Control de opacidad - Solo visible cuando la capa está activa -->
            <div v-if="isLayerActive(layer.name)" 
                class="opacity-control">
              <div class="flex items-center space-x-3">
                <div class="opacity-badge">
                  {{ Math.round((layerOpacities[layer.name] || 1) * 100) }}%
                </div>
                <input 
                  type="range"
                  :id="`opacity-${layer.name}`"
                  :value="layerOpacities[layer.name] || 1"
                  @input="updateOpacity(layer, $event.target.value)"
                  min="0"
                  max="1"
                  step="0.05"
                  class="opacity-slider"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pie de panel con información mejorada -->
    <div v-if="Object.keys(olLayers).length > 0" class="footer-info">
      <div class="active-layers-badge">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ activeLayers.length }} capa(s) activa(s)</span>
      </div>
      <div class="layers-list-footer">
        {{ Object.keys(olLayers).join(', ') }}
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Estilos base para el componente */
.layer-manager {
  transition: all 0.3s ease;
  animation: fade-in 0.5s ease-out;
}

/* Diseño para el botón de actualizar */
.refresh-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: #f3f4f6;
  color: #4b5563;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
}

.refresh-button:hover {
  background-color: #d1fae5;
  color: #10b981;
  transform: rotate(15deg);
}

.refresh-button:active {
  transform: scale(0.9) rotate(15deg);
}

.animate-spin-slow {
  animation: spin 1.5s linear infinite;
}

/* Estilos para el campo de búsqueda */
.search-container {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem 0.5rem 2.5rem;
  font-size: 0.875rem;
  color: #374151;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.search-input:focus {
  outline: none;
  border-color: #10b981;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15);
}

.search-icon {
  position: absolute;
  width: 1.25rem;
  height: 1.25rem;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  pointer-events: none;
}

/* Estilos para el loader animado */
.loader {
  display: inline-block;
  width: 48px;
  height: 48px;
  position: relative;
}

.loader-circle {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid #e2e8f0;
}

.loader-line-mask {
  position: absolute;
  width: 50%;
  height: 100%;
  top: 0;
  right: 0;
  overflow: hidden;
}

.loader-line {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border-width: 2px;
  border-style: solid;
  border-color: transparent;
  border-top-color: #10b981;
  border-right-color: #10b981;
  animation: loader-spin 1s ease-in-out infinite;
  transform-origin: 0% 50%;
}

@keyframes loader-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Estilos para el estado vacío */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  text-align: center;
}

.empty-icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background-color: #f3f4f6;
  border-radius: 50%;
  margin-bottom: 1rem;
}

.empty-icon {
  width: 32px;
  height: 32px;
  color: #9ca3af;
}

.empty-state-button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #ecfdf5;
  color: #047857;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.empty-state-button:hover {
  background-color: #d1fae5;
}

/* Estilos para el contenedor con scroll de capas */
.layers-scroll-container {
  margin-bottom: 1rem;
  position: relative;
}

.layers-scroll-wrapper {
  background-color: #f0fdf4; /* Fondo verde suave para el área de scroll */
  border-radius: 0.75rem;
  padding: 0.75rem;
  border: 1px solid #dcfce7;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.03);
}

.layer-list {
  max-height:400px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #10b981 #e5e7eb;
  padding-right: 0.5rem;
  padding-left: 0.25rem;
  margin-right: -0.25rem;
}

.layer-list::-webkit-scrollbar {
  width: 6px;
}

.layer-list::-webkit-scrollbar-track {
  background: #e5e7eb;
  border-radius: 3px;
}

.layer-list::-webkit-scrollbar-thumb {
  background-color: #10b981;
  border-radius: 3px;
}

/* Indicadores de scroll superior e inferior */
.layers-scroll-wrapper::before,
.layers-scroll-wrapper::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  height: 12px;
  pointer-events: none;
  z-index: 1;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.layers-scroll-wrapper::before {
  top: 0.75rem;
  background: linear-gradient(to bottom, rgba(240, 253, 244, 1), rgba(240, 253, 244, 0));
}

.layers-scroll-wrapper::after {
  bottom: 0.75rem;
  background: linear-gradient(to top, rgba(240, 253, 244, 1), rgba(240, 253, 244, 0));
}

.layers-scroll-wrapper.can-scroll-up::before,
.layers-scroll-wrapper.can-scroll-down::after {
  opacity: 1;
}

/* Estilos para cada elemento de capa */
.layer-item {
  margin-bottom: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  background-color: #ffffff;
  overflow: hidden;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.layer-item:last-child {
  margin-bottom: 0;
}

.layer-item:hover {
  border-color: #86efac; /* Borde verde claro al pasar el cursor */
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.15);
  transform: translateY(-1px);
}

.active-layer {
  border-left: 3px solid #10b981;
  background-color: #f0fdf4; /* Fondo verdecito suave para capas activas */
}

.layer-header {
  padding: 0.75rem;
  position: relative;
}

/* Marcador visual para capas activas */
.active-layer .layer-header::before {
  content: '';
  position: absolute;
  top: 50%;
  right: 0.75rem;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #10b981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

/* Estilos para información de la capa */
.layer-info {
  flex: 1;
}

.layer-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #166534; /* Color verde más oscuro para los títulos */
  margin-bottom: 0.125rem;
}

.layer-description {
  font-size: 0.75rem;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

/* Estilos para toggle switch mejorado */
.toggle-container {
  position: relative;
  display: inline-block;
  width: 40px;
  margin-right: 0.5rem;
  vertical-align: middle;
}

.toggle-input {
  opacity: 0;
  width: 0;
  height: 0;
  position: absolute;
}

.toggle-label {
  position: relative;
  display: block;
  width: 36px;
  height: 18px;
  border-radius: 9999px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  background-color: #d1d5db;
}

.toggle-label.active {
  background-color: #10b981;
}

.toggle-label::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  background-color: white;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease-in-out;
}

.toggle-label.active::after {
  transform: translateX(18px);
}

/* Estilos para el control de opacidad */
.opacity-control {
  padding: 0.75rem;
  border-top: 1px solid #dcfce7; /* Borde verde claro */
  background-color: #ecfdf5; /* Fondo verde muy suave */
  animation: fade-in 0.2s ease-out forwards;
  border-bottom-left-radius: 0.5rem;
  border-bottom-right-radius: 0.5rem;
}

.opacity-badge {
  display: inline-flex;
  min-width: 45px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #15803d; /* Verde oscuro para texto */
  background-color: #dcfce7; /* Verde muy claro para fondo */
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  text-align: center;
  justify-content: center;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.opacity-slider {
  flex: 1;
  height: 4px;
  background-color: #d1d5db;
  border-radius: 9999px;
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
  outline: none;
  background-image: linear-gradient(to right, #10b981 0%, #10b981 50%, #d1d5db 50%, #d1d5db 100%);
  background-size: 200% 100%;
  background-position: right;
}

.opacity-slider::-webkit-slider-thumb {
  appearance: none;
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background-color: #ffffff;
  border: 2px solid #10b981;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.opacity-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background-color: #ffffff;
  border: 2px solid #10b981;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.opacity-slider:hover::-webkit-slider-thumb {
  transform: scale(1.25);
  background-color: #10b981;
  border-color: #10b981;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
}

.opacity-slider:hover::-moz-range-thumb {
  transform: scale(1.25);
  background-color: #10b981;
  border-color: #10b981;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
}

/* Footer info */
.footer-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  background-color: #f0fdf4; /* Fondo verde suave */
  font-size: 0.75rem;
  color: #15803d; /* Texto verde más oscuro */
  margin-top: 0.75rem;
  border: 1px dashed #a7f3d0; /* Borde punteado verde claro */
}

.active-layers-badge {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  color: #047857; /* Verde más intenso */
  font-weight: 600;
}

.layers-list-footer {
  font-family: monospace;
  padding: 0.375rem 0.5rem;
  background-color: #ffffff;
  border-radius: 0.25rem;
  overflow-x: auto;
  white-space: nowrap;
  border-left: 3px solid #10b981;
  color: #4b5563;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* Animaciones */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Media queries para responsividad */
@media (max-width: 640px) {
  .layer-manager {
    padding: 1rem;
  }
  
  .layer-list {
    max-height: 300px;
  }
  
  .layer-header {
    padding: 0.5rem;
  }
  
  .opacity-control {
    padding: 0.5rem;
  }
}

/* Animación para entrada deslizante */
@keyframes slide-in {
  from {
    transform: translateX(20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.layer-item {
  animation: slide-in 0.3s ease-out forwards;
  animation-delay: calc(var(--index, 0) * 0.05s);
}

/* Efecto de iluminación al activar */
.active-layer {
  box-shadow: 0 0 0 1px rgba(16, 185, 129, 0.4);
  background-color: #f0fdf4;
}
</style>
