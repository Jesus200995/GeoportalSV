<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import { getAvailableLayers } from '../services/geoserver';
import { getLayerData } from '../services/postgresql';
import ChartRenderer from './ChartRenderer.vue';
import UserProfile from './UserProfile.vue';

// Agregar router para la navegación
const router = useRouter();

// Estado del componente
const availableLayers = ref([]);
const selectedLayer = ref(null);
const layerData = ref(null);
const searchQuery = ref('');
const loading = ref(false);
const error = ref(null);

// Estado para animaciones
const fadeIn = ref(false);

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

// Función para volver al inicio - versión con navegación directa
const goToHome = () => {
  // Usar window.location.href para navegación directa y confiable
  window.location.href = '/';
};

onMounted(() => {
  loadLayers();
  
  // Activar animaciones
  setTimeout(() => {
    fadeIn.value = true;
  }, 100);
});
</script>

<template>
  <div class="stats-dashboard min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
    <!-- Header mejorado con logo y navegación -->
    <header class="bg-white shadow-md sticky top-0 z-30">
      <div class="container mx-auto px-4 py-3 flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <img 
            src="@/components/images/logotipo.png" 
            alt="Logotipo Sembrando Datos" 
            class="h-10 sm:h-12 w-auto object-contain"
          />
          <h1 class="text-xl sm:text-2xl font-serif font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-500">
            Panel de Estadísticas
          </h1>
        </div>

        <div class="flex items-center">
          <!-- Reemplazar el botón con un componente dual botón/enlace para garantizar la navegación -->
          <a 
            href="/"
            class="px-4 py-2 mr-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg transition-all duration-300 flex items-center space-x-2 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50 transform hover:-translate-y-0.5 active:translate-y-0 font-semibold no-underline"
            aria-label="Volver a la página de inicio"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span class="hidden sm:inline">Volver al inicio</span>
          </a>
          
          <!-- Componente de perfil de usuario -->
          <UserProfile />
        </div>
      </div>
    </header>

    <!-- Panel de selección de capas mejorado -->
    <div class="bg-white border-b border-gray-200 shadow-sm">
      <div class="container mx-auto px-4 py-6">
        <div class="max-w-4xl mx-auto space-y-6">
          <!-- Título principal con animación -->
          <div class="text-center mb-6" :class="{ 'animate-fade-in': fadeIn }">
            <h2 class="text-2xl font-semibold text-gray-800 mb-2">Análisis Estadístico de Datos</h2>
            <p class="text-gray-600">Seleccione una capa para visualizar sus estadísticas y gráficos</p>
          </div>

          <!-- Buscador y selector mejorados -->
          <div class="bg-blue-50 p-6 rounded-xl shadow-sm border border-blue-100" :class="{ 'animate-slide-up': fadeIn }">
            <!-- Buscador -->
            <div class="relative w-full mb-4">
              <label for="search-layers" class="block text-sm font-medium text-blue-700 mb-2">
                Buscar capas por nombre
              </label>
              <div class="relative">
                <input
                  id="search-layers"
                  v-model="searchQuery"
                  type="text"
                  placeholder="Buscar capas..."
                  class="w-full pl-10 pr-4 py-3 border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white shadow-sm transition-all duration-200"
                />
                <svg class="w-5 h-5 text-blue-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
              </div>
            </div>

            <!-- Selector de capas -->
            <div>
              <label for="layer-select" class="block text-sm font-medium text-blue-700 mb-2">
                Seleccione una capa para analizar
              </label>
              <div class="relative">
                <select
                  id="layer-select"
                  v-model="selectedLayer"
                  @change="handleLayerSelect(selectedLayer)"
                  class="w-full p-3 bg-white border border-blue-200 rounded-lg appearance-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm transition-all duration-200"
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
                  <svg class="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contenido principal con animaciones -->
    <div class="container mx-auto px-4 py-8">
      <!-- Estado de carga mejorado -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="flex flex-col items-center">
          <div class="animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent shadow-lg"></div>
          <p class="mt-4 text-blue-600 font-medium">Cargando datos estadísticos...</p>
        </div>
      </div>

      <!-- Mensaje de error mejorado -->
      <div v-else-if="error" class="max-w-3xl mx-auto p-6 bg-red-50 border border-red-200 rounded-xl text-red-700 shadow-sm">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-lg font-medium mb-2">Error al cargar datos</h3>
            <p>{{ error }}</p>
            <button 
              @click="loadLayers"
              class="mt-3 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-colors"
            >
              Intentar nuevamente
            </button>
          </div>
        </div>
      </div>

      <!-- Contenedor de gráficas mejorado -->
      <div v-else-if="selectedLayer && layerData" 
           class="bg-white rounded-xl p-6 shadow-lg border border-gray-200 animate-fade-in">
        <div class="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center">
          <div>
            <h3 class="text-xl font-bold text-gray-800 mb-1">
              {{ selectedLayer.title || selectedLayer.name }}
            </h3>
            <p class="text-gray-500">{{ layerData.length }} registros encontrados</p>
          </div>
          <div class="bg-blue-50 rounded-lg px-3 py-2 flex items-center mt-3 sm:mt-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-sm text-blue-700">Análisis estadístico</span>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ChartRenderer 
            :data="layerData" 
            :layer="selectedLayer"
          />
        </div>
      </div>

      <!-- Mensaje inicial mejorado -->
      <div v-else class="text-center py-16 max-w-3xl mx-auto" :class="{ 'animate-fade-in': fadeIn }">
        <div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 shadow-sm border border-blue-100">
          <div class="mb-6 transform transition-transform hover:scale-105 duration-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-20 w-20 mx-auto text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3">Visualización de Estadísticas</h3>
          <p class="text-gray-600 mb-6 max-w-md mx-auto">
            Seleccione una capa del menú superior para generar análisis estadísticos 
            y visualizar los datos en gráficas interactivas.
          </p>
          
          <div class="bg-white p-4 rounded-lg shadow-sm mx-auto max-w-sm">
            <div class="text-left">
              <h4 class="font-medium text-blue-700 mb-2 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                ¿Cómo funciona?
              </h4>
              <ol class="text-sm text-gray-600 space-y-2 list-decimal pl-5">
                <li>Seleccione una capa de datos del menú desplegable</li>
                <li>Visualice automáticamente gráficos estadísticos</li>
                <li>Interactúe con los gráficos para obtener más detalles</li>
                <li>Compare diferentes variables de los datos</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Footer mejorado -->
    <footer class="bg-white border-t border-gray-200 py-6 mt-auto">
      <div class="container mx-auto px-4 text-center">
        <p class="text-gray-600 text-sm">© 2023 Geoportal Sembrando Datos. Todos los derechos reservados.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.stats-dashboard {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Animación de entrada con fade */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.animate-fade-in {
  animation: fadeIn 0.8s ease-out forwards;
}

/* Animación de deslizamiento hacia arriba */
@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-up {
  animation: slideUp 0.6s ease-out forwards;
  animation-delay: 0.2s;
  opacity: 0;
}

/* Estilos para el selector de capas */
select {
  appearance: none;
}

/* Estilos para el contenedor de gráficas */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* Transiciones suaves */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* Animaciones y transiciones */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Efecto de hover para botones */
button:hover {
  filter: brightness(1.05);
}

button:active {
  transform: scale(0.98);
}

/* Asegurar que el enlace no tenga subrayado */
.no-underline {
  text-decoration: none !important;
}
</style>
