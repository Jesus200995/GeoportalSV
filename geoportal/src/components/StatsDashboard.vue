<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { getAvailableLayers } from '../services/geoserver';
import { getLayerData } from '../services/postgresql';
import ChartRenderer from './ChartRenderer.vue';

// Estado del componente
const availableLayers = ref([]);
const selectedLayer = ref(null);
const layerData = ref(null);
const searchQuery = ref('');
const loading = ref(false);
const error = ref(null);

// Filtrar capas basado en la búsqueda
const filteredLayers = computed(() => {
  if (!searchQuery.value) return availableLayers.value;
  const query = searchQuery.value.toLowerCase();
  return availableLayers.value.filter(layer => 
    layer.title?.toLowerCase().includes(query) || 
    layer.name?.toLowerCase().includes(query)
  );
});

// Cargar capas disponibles
const loadLayers = async () => {
  try {
    loading.value = true;
    error.value = null;
    const layers = await getAvailableLayers();
    
    // Asegurar que tenemos un array de capas válido
    if (!layers || !Array.isArray(layers) || layers.length === 0) {
      throw new Error('No se encontraron capas disponibles');
    }
    
    console.log("Capas cargadas:", layers.length);
    availableLayers.value = layers.map(layer => ({
      ...layer,
      title: layer.title || layer.name || `Capa ${layer.id || 'sin nombre'}`
    }));
    
  } catch (err) {
    console.error('Error al cargar capas:', err);
    error.value = `No se pudieron cargar las capas disponibles: ${err.message || 'Error desconocido'}`;
    availableLayers.value = [];
  } finally {
    loading.value = false;
  }
};

// Cargar datos cuando se selecciona una capa
const handleLayerSelect = async (layer) => {
  if (!layer || (typeof layer === 'object' && !layer.name)) {
    console.log("Selección de capa inválida:", layer);
    return;
  }
  
  try {
    loading.value = true;
    error.value = null;
    
    // Si recibimos un objeto del evento de select, extraemos solo la capa
    const selectedLayerObj = typeof layer === 'object' ? layer : 
                       availableLayers.value.find(l => l.name === layer);
    
    if (!selectedLayerObj) {
      throw new Error('Capa no encontrada');
    }
    
    selectedLayer.value = selectedLayerObj;
    console.log("Cargando datos para:", selectedLayerObj.name);
    
    const data = await getLayerData(selectedLayerObj.name);
    console.log("Datos recibidos:", data);
    
    if (!data || data.length === 0) {
      throw new Error('No hay datos disponibles para esta capa');
    }
    
    layerData.value = data;
  } catch (err) {
    console.error('Error al cargar datos de la capa:', err);
    error.value = `No se pudieron cargar los datos de la capa: ${err.message || 'Error desconocido'}`;
    layerData.value = null;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadLayers();
});
</script>

<template>
  <div class="stats-dashboard min-h-screen bg-gray-50">
    <!-- Panel de selección de capas -->
    <div class="sticky top-0 z-10 bg-white border-b border-gray-200 shadow-sm">
      <div class="container mx-auto px-4 py-4">
        <div class="max-w-3xl mx-auto space-y-4">
          <!-- Título y buscador -->
          <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
            <h2 class="text-xl font-semibold text-gray-800 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Análisis Estadístico
            </h2>
            
            <!-- Buscador -->
            <div class="relative w-full sm:w-64">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Buscar capas..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
            </div>
          </div>

          <!-- Selector de capas -->
          <div class="relative">
            <select
              v-model="selectedLayer"
              @change="handleLayerSelect(selectedLayer)"
              class="w-full p-3 bg-white border border-gray-300 rounded-lg appearance-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              :disabled="loading"
            >
              <option :value="null">Selecciona una capa para analizar</option>
              <option v-for="layer in filteredLayers" 
                      :key="layer.name" 
                      :value="layer"
              >
                {{ layer.title || layer.name }}
              </option>
            </select>
            <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
              <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contenido principal -->
    <div class="container mx-auto px-4 py-8">
      <!-- Estado de carga -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
      </div>

      <!-- Mensaje de error -->
      <div v-else-if="error" class="max-w-3xl mx-auto p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
        {{ error }}
      </div>

      <!-- Contenedor de gráficas -->
      <div v-else-if="selectedLayer && layerData" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ChartRenderer 
          :data="layerData" 
          :layer="selectedLayer"
        />
      </div>

      <!-- Mensaje inicial -->
      <div v-else class="text-center py-12">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Selecciona una capa para comenzar</h3>
        <p class="text-gray-500">Elige una capa del menú superior para visualizar sus estadísticas</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-dashboard {
  /* Estilos generales para el dashboard */
}

/* Estilos para el panel de selección de capas */
.sticky {
  top: 0;
  z-index: 10;
}

/* Estilos para el buscador */
.relative {
  position: relative;
}

/* Estilos para el selector de capas */
select {
  appearance: none;
}

/* Estilos para el contenedor de gráficas */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

/* Animaciones y transiciones */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
