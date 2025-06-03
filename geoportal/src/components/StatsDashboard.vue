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
    <!-- Header mejorado con logo y navegación - Reducido en altura -->
    <header class="bg-white shadow-md sticky top-0 z-30">
      <div class="container mx-auto px-4 py-2 flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <img 
            src="@/components/images/logotipo.png" 
            alt="Logotipo Sembrando Datos" 
            class="h-8 sm:h-10 w-auto object-contain"
          />
          <h1 class="text-lg sm:text-xl font-serif font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-500">
            Panel de Estadísticas
          </h1>
        </div>

        <div class="flex items-center">
          <!-- Botón de volver al inicio con diseño más compacto -->
          <a 
            href="/"
            class="px-3 py-1.5 mr-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg transition-all duration-300 flex items-center space-x-2 shadow-md hover:shadow-lg focus:outline-none transform hover:-translate-y-0.5 active:translate-y-0 font-semibold no-underline text-sm"
            aria-label="Volver a la página de inicio"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span class="hidden sm:inline">Inicio</span>
          </a>
          
          <!-- Componente de perfil de usuario -->
          <UserProfile />
        </div>
      </div>
    </header>

    <!-- Contenido principal con layout responsive - Ajustado el padding superior -->
    <div class="container mx-auto px-4 pt-6 pb-4">
      <!-- Título integrado dentro del contenido principal -->
      <div class="text-center mb-6" :class="{ 'animate-fade-in': fadeIn }">
        <h2 class="text-xl font-semibold text-gray-800 mb-1">Análisis Estadístico de Datos</h2>
        <p class="text-gray-600 text-sm">Seleccione una capa para visualizar sus estadísticas y gráficos</p>
      </div>

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

      <!-- Layout de dos columnas para el contenido principal -->
      <div v-else class="flex flex-col lg:flex-row gap-6">
        <!-- Panel izquierdo: Selección de capas (más estrecho en pantallas grandes) -->
        <div class="w-full lg:w-1/3 animate-fade-in">
          <!-- Buscador y selector mejorados -->
          <div class="bg-blue-50 p-5 rounded-xl shadow-sm border border-blue-100 sticky-panel" :class="{ 'animate-slide-up': fadeIn }">
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
                  class="w-full pl-10 pr-4 py-2 border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white shadow-sm transition-all duration-200"
                />
                <svg class="w-5 h-5 text-blue-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
              </div>
            </div>

            <!-- Selector de capas -->
            <div class="mb-4">
              <label for="layer-select" class="block text-sm font-medium text-blue-700 mb-2">
                Seleccione una capa para analizar
              </label>
              <div class="relative">
                <select
                  id="layer-select"
                  v-model="selectedLayer"
                  @change="handleLayerSelect(selectedLayer)"
                  class="w-full p-2 bg-white border border-blue-200 rounded-lg appearance-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm transition-all duration-200"
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
            
            <!-- Panel de información de la capa seleccionada -->
            <div v-if="selectedLayer" class="bg-white rounded-lg p-3 shadow-sm border border-blue-50 mb-4">
              <h3 class="text-sm font-medium text-blue-800 mb-2 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Información de la capa
              </h3>
              <div class="space-y-1 text-sm">
                <p class="flex justify-between">
                  <span class="text-gray-500">Nombre:</span>
                  <span class="font-medium text-gray-800">{{ selectedLayer.title || selectedLayer.name }}</span>
                </p>
                <p class="flex justify-between" v-if="layerData">
                  <span class="text-gray-500">Registros:</span>
                  <span class="font-medium text-gray-800">{{ layerData.length }}</span>
                </p>
              </div>
            </div>
            
            <!-- Información de ayuda - Versión más compacta -->
            <div class="bg-white/70 backdrop-blur-sm p-3 rounded-lg border border-blue-100">
              <div class="flex items-center space-x-2 text-blue-700 mb-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h4 class="font-medium text-sm">¿Cómo funciona?</h4>
              </div>
              <ol class="text-xs text-gray-600 space-y-0.5 list-decimal pl-5">
                <li>Seleccione una capa de datos del menú desplegable</li>
                <li>Visualice automáticamente gráficos estadísticos</li>
                <li>Interactúe con los gráficos para obtener más detalles</li>
                <li>Compare diferentes variables de los datos</li>
              </ol>
            </div>
          </div>
        </div>
        
        <!-- Panel derecho: Visualización de gráficos (más ancho en pantallas grandes) -->
        <div class="w-full lg:w-2/3 animate-fade-in">
          <!-- Contenedor de gráficas mejorado -->
          <div v-if="selectedLayer && layerData" 
               class="bg-white rounded-xl p-5 shadow-lg border border-gray-200">
            <div class="mb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center">
              <div>
                <h3 class="text-lg font-bold text-gray-800 mb-1">
                  {{ selectedLayer.title || selectedLayer.name }}
                </h3>
                <p class="text-gray-500 text-sm">{{ layerData.length }} registros encontrados</p>
              </div>
              <div class="bg-blue-50 rounded-lg px-3 py-1.5 flex items-center mt-2 sm:mt-0">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-500 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-xs text-blue-700">Análisis estadístico</span>
              </div>
            </div>
            
            <!-- Contenedor para los gráficos -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
              <ChartRenderer 
                :data="layerData" 
                :layer="selectedLayer"
              />
            </div>
          </div>

          <!-- Mensaje cuando no hay capa seleccionada -->
          <div v-else class="text-center py-12 bg-white rounded-xl p-6 shadow-sm border border-blue-100">
            <div class="mb-5 transform transition-transform hover:scale-105 duration-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 class="text-lg font-bold text-gray-900 mb-2">Visualización de Estadísticas</h3>
            <p class="text-gray-600 mb-4 max-w-md mx-auto text-sm">
              Seleccione una capa del panel izquierdo para generar análisis estadísticos 
              y visualizar los datos en gráficas interactivas.
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Footer mejorado - Reducido en altura -->
    <footer class="bg-white border-t border-gray-200 py-4 mt-auto">
      <div class="container mx-auto px-4 text-center">
        <p class="text-gray-600 text-xs">© 2023 Geoportal Sembrando Datos. Todos los derechos reservados.</p>
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

/* Para mantener el panel izquierdo siempre visible en pantallas grandes */
@media (min-width: 1024px) {
  .sticky-panel {
    position: sticky;
    top: 60px; /* Ajustado para el header más pequeño */
    max-height: calc(100vh - 80px);
    overflow-y: auto;
  }
}

/* Mejoras de responsividad */
@media (max-width: 640px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
