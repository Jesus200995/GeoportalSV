<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router'; 
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import TileWMS from 'ol/source/TileWMS';
import { fromLonLat } from 'ol/proj';
import { watchEffect } from 'vue';
import MeasurementTool from './map-tools/MeasurementTool.vue';
import UserProfile from './UserProfile.vue';
import LayersTool from './map-tools/LayersTool.vue';
import DrawTool from './map-tools/DrawTool.vue';
import SearchTool from './map-tools/SearchTool.vue';
import { useLayers } from '../composables/useLayers';

// Unificar definición de emisiones - combinar 'save-success', 'logout' y 'show-welcome'
const emit = defineEmits(['save-success', 'logout', 'show-welcome']);

// Estado reactivo
const sidebarOpen = ref(true);
const map = ref(null);
const loading = ref(true); // Para mostrar animación de carga
const activeTab = ref('principal'); // Para controlar pestañas de grupos de capas
const activeToolPanel = ref(''); // layers, measure, draw, search
const layerOpacity = ref({}); // Para almacenar opacidad de capas
const searchQuery = ref('');
const searchResults = ref([]); // Corregido: faltaba el corchete de cierre

// Importar configuración de capas desde el composable
const { layerGroups } = useLayers();

// Referencias a elementos DOM
const mapElement = ref(null);

// Funciones
const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value;
};

const changeTab = (tab) => {
  activeTab.value = tab;
};

// Obtener todas las capas para el mapa
const getAllLayers = () => {
  return [...layerGroups.value.principal, ...layerGroups.value.extras];
};

const toggleLayerVisibility = (layer) => {
  if (map.value) {
    const mapLayer = map.value.getLayers().getArray()
      .find(l => l.get('name') === layer.name);
    if (mapLayer) {
      const currentVisibility = mapLayer.getVisible();
      mapLayer.setVisible(!currentVisibility);
      // Actualizar el estado en layerGroups
      const groupKey = layer.id <= 1 ? 'principal' : 'extras';
      const layerIndex = layerGroups.value[groupKey].findIndex(l => l.name === layer.name);
      if (layerIndex !== -1) {
        layerGroups.value[groupKey][layerIndex].visible = !currentVisibility;
      }
    }
  }
};

// Función para cambiar opacidad de capa
const updateLayerOpacity = (layer, opacity) => {
  if (map.value) {
    const mapLayers = map.value.getLayers().getArray();
    const olLayer = mapLayers.find(l => l.get('name') === layer.name);
    if (olLayer) {
      olLayer.setOpacity(opacity);
      layerOpacity.value[layer.id] = opacity;
    }
  }
};

// Función para mover capa arriba/abajo
const moveLayer = (layer, direction) => {
  if (map.value) {
    const mapLayers = map.value.getLayers().getArray();
    const index = mapLayers.findIndex(l => l.get('name') === layer.name);
    if (index !== -1) {
      const newIndex = direction === 'up' ? index + 1 : index - 1;
      if (newIndex >= 0 && newIndex < mapLayers.length) {
        const layerToMove = mapLayers[index];
        mapLayers.splice(index, 1);
        mapLayers.splice(newIndex, 0, layerToMove);
        map.value.render();
      }
    }
  }
};

// Función para búsqueda
const searchFeatures = async () => {
  if (!searchQuery.value) return;
  
  // Implementar búsqueda WFS aquí
  try {
    const geoserverUrl = 'http://31.97.8.51:8082/geoserver'; // URL actualizada
    const response = await fetch(`${geoserverUrl}/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=sembrando:territorios_28&outputFormat=application/json&CQL_FILTER=nombre_territorio ILIKE '%${searchQuery.value}%'`);
    const data = await response.json();
    searchResults.value = data.features;
  } catch (error) {
    console.error('Error en la búsqueda:', error);
  }
};

// Función mejorada para guardar mapa
const saveMapState = async () => {
  if (!newMapName.value.trim()) {
    alert('Por favor ingrese un nombre para el mapa');
    return;
  }

  const mapState = {
    id: Date.now(),
    name: newMapName.value.trim(),
    lastModified: new Date().toLocaleString(),
    thumbnail: '/src/components/images/vizual2.png', // Usar ruta absoluta
    center: map.value.getView().getCenter(),
    zoom: map.value.getView().getZoom(),
    layers: getAllLayers().map(layer => ({
      ...layer,
      visible: layer.visible,
      opacity: layerOpacity.value[layer.id] || 1
    }))
  };
  
  // Guardar en localStorage
  const savedMaps = JSON.parse(localStorage.getItem('savedMaps') || '[]');
  savedMaps.push(mapState);
  localStorage.setItem('savedMaps', JSON.stringify(savedMaps));
  
  emit('save-success');
  showSaveDialog.value = false;
  newMapName.value = '';
};

// Botón para guardar en la interfaz
const showSaveDialog = ref(false);
const newMapName = ref('');

const saveMap = () => {
  if (!newMapName.value.trim()) {
    alert('Por favor ingrese un nombre para el mapa');
    return;
  }
  
  // Crear captura de pantalla del mapa (o usar imagen predeterminada)
  const mapState = {
    id: Date.now(),
    name: newMapName.value.trim(),
    lastModified: new Date().toLocaleString(),
    thumbnail: '/src/components/images/vizual2.png', // Usar ruta absoluta
    center: map.value.getView().getCenter(),
    zoom: map.value.getView().getZoom(),
    layers: getAllLayers().map(layer => ({
      ...layer,
      visible: layer.visible,
      opacity: layerOpacity.value[layer.id] || 1
    }))
  };
  
  // Guardar en localStorage
  const savedMaps = JSON.parse(localStorage.getItem('savedMaps') || '[]');
  savedMaps.push(mapState);
  localStorage.setItem('savedMaps', JSON.stringify(savedMaps));
  
  emit('save-success');
  showSaveDialog.value = false;
  newMapName.value = '';
};

// Función para hacer zoom a un resultado de búsqueda
const zoomToFeature = (feature) => {
  if (feature && feature.geometry && map.value) {
    // Lógica para hacer zoom a la geometría
    console.log("Zoom a característica", feature);
  }
};

// Inicializar mapa cuando el componente se monte
const initializeMap = () => {
  // Crear capa base OSM
  const osmLayer = new TileLayer({
    source: new OSM(),
    visible: layerGroups.value.extras.find(l => l.type === 'osm')?.visible || false,
    properties: {
      name: 'OpenStreetMap',
      group: 'extras'
    }
  });

  // Crear capas WMS
  const wmsLayers = [...layerGroups.value.principal, ...layerGroups.value.extras]
    .filter(layer => layer.type === 'wms')
    .map(layer => new TileLayer({
      source: new TileWMS({
        url: layer.url,
        params: layer.params,
        serverType: 'geoserver',
      }),
      visible: layer.visible,
      properties: {
        name: layer.name,
        group: layerGroups.value.principal.includes(layer) ? 'principal' : 'extras'
      }
    }));

  // Crear mapa con todas las capas
  map.value = new Map({
    target: mapElement.value,
    layers: [osmLayer, ...wmsLayers],
    view: new View({
      center: fromLonLat([-98.9, 20.1]), // Centrado en Hidalgo, México
      zoom: 9
    })
  });

  // Inicializar opacidades
  map.value.getLayers().forEach(layer => {
    const name = layer.get('name');
    layerOpacity.value[name] = layer.getOpacity();
  });
};

onMounted(() => {
  // Simular tiempo de carga
  loading.value = true;
  setTimeout(() => {
    initializeMap();
    loading.value = false;
  }, 1000);
  
  // Añadir el event listener para cambios de tamaño
  window.addEventListener('resize', updateWindowWidth);
  
  // Asegurarnos de tener el ancho correcto al inicio
  updateWindowWidth();
});

// Limpiar recursos cuando el componente se desmonte
onBeforeUnmount(() => {
  if (map.value) {
    map.value.setTarget(undefined);
    map.value = null;
  }
  
  // Eliminar el event listener
  window.removeEventListener('resize', updateWindowWidth);
});

// Añadir referencia reactiva para el ancho de la ventana
const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 0);

// Función para actualizar el ancho de la ventana
const updateWindowWidth = () => {
  windowWidth.value = window.innerWidth;
};

// Agregar funcionalidad de zoom
const zoomIn = () => {
  if (map.value) {
    const view = map.value.getView();
    const zoom = view.getZoom();
    view.animate({
      zoom: zoom + 1,
      duration: 250
    });
  }
};

const zoomOut = () => {
  if (map.value) {
    const view = map.value.getView();
    const zoom = view.getZoom();
    view.animate({
      zoom: zoom - 1,
      duration: 250
    });
  }
};

// Función para obtener el icono de cada herramienta - Reemplazar con iconos SVG modernos
const getToolIcon = (tool) => {
  // Ya no necesitamos esta función con los nuevos iconos SVG
  return '';
};

// Herramientas para el mapa con etiquetas más descriptivas
const mapTools = ref([
  { id: 'layers', name: 'Capas', description: 'Gestionar capas del mapa' },
  { id: 'measure', name: 'Medir', description: 'Herramientas de medición' },
  { id: 'draw', name: 'Dibujar', description: 'Dibujar en el mapa' },
  { id: 'search', name: 'Buscar', description: 'Buscar elementos en el mapa' }
]);

// Agregar estado para controlar visibilidad del panel de herramientas en móviles
const showToolsPanel = ref(false);

// Toggle para el panel de herramientas en móviles
const toggleToolsPanel = () => {
  showToolsPanel.value = !showToolsPanel.value;
};

// Agregar router para la navegación
const router = useRouter();

// Estado para el modal de confirmación de salida
const showExitModal = ref(false);

// Función para manejar el clic en el botón de inicio
const handleGoHome = () => {
  // Verificar si hay cambios no guardados (puedes personalizar esta lógica)
  const hasUnsavedChanges = false; // Ejemplo: establecer en true si hay cambios sin guardar
  
  if (hasUnsavedChanges) {
    // Mostrar modal de confirmación si hay cambios no guardados
    showExitModal.value = true;
  } else {
    // Navegar directamente a la página de inicio si no hay cambios sin guardar
    navigateToHome();
  }
};

// Función para confirmar la salida y navegar a la página de inicio
const confirmExit = () => {
  navigateToHome();
  showExitModal.value = false;
};

// Función de navegación a la página de inicio
const navigateToHome = () => {
  // Aplicar una animación de transición antes de navegar
  document.body.classList.add('page-transitioning');
  
  // Emitir evento para mostrar la vista de bienvenida
  emit('show-welcome');
  
  // Pequeño retraso para permitir que la animación comience
  setTimeout(() => {
    document.body.classList.remove('page-transitioning');
  }, 500);
};

// Función para cerrar sesión
const logout = () => {
  // Mostrar modal de confirmación
  logoutModal.value = true;
};

// Función para confirmar cierre de sesión
const confirmLogout = () => {
  localStorage.removeItem('authenticated');
  localStorage.removeItem('user');
  logoutModal.value = false;
  // Usar el emit definido arriba en lugar de un nuevo emitLogout
  emit('logout');
  router.push('/login');
};
</script>

<template>
  <!-- Contenedor principal a pantalla completa -->
  <div class="h-screen w-screen overflow-hidden relative bg-gray-50 flex">
    <!-- Nueva barra lateral fija -->
    <aside 
      class="h-full bg-white border-r border-gray-200 flex flex-col transition-all duration-500 ease-in-out z-20"
      :class="sidebarOpen ? 'w-80 sm:w-96' : 'w-16'"
    >
      <!-- Encabezado de la barra lateral -->
      <div class="h-14 sm:h-16 flex items-center justify-between px-4 border-b border-gray-100 bg-gradient-to-r from-green-50 to-emerald-50">
        <div class="flex items-center space-x-3 overflow-hidden">
          <img 
            src="@/components/images/logotipo.png" 
            alt="Logo" 
            class="h-8 w-8 object-contain flex-shrink-0"
          />
          <h2 class="font-medium text-green-800 truncate transition-opacity duration-300"
              :class="sidebarOpen ? 'opacity-100' : 'opacity-0'">
            Herramientas
          </h2>
        </div>
        <!-- Botón para colapsar/expandir la barra lateral -->
        <button 
          @click="toggleSidebar" 
          class="p-1.5 rounded-lg hover:bg-green-100 text-green-700 transition-all duration-300 transform"
          :class="sidebarOpen ? '' : 'rotate-180'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      </div>

      <!-- Contenido de la barra lateral -->
      <div class="flex-1 overflow-hidden flex flex-col">
        <!-- Pestañas de navegación -->
        <div class="flex border-b border-gray-200">
          <button 
            @click="changeTab('principal')" 
            class="px-3 py-3 text-sm font-medium transition-colors duration-200 flex-1 border-b-2 flex items-center justify-center space-x-1"
            :class="activeTab === 'principal' ? 'border-green-500 text-green-700' : 'border-transparent hover:text-green-600 text-gray-600'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <span v-if="sidebarOpen" class="truncate">Capas Principales</span>
          </button>
          <button 
            @click="changeTab('extras')" 
            class="px-3 py-3 text-sm font-medium transition-colors duration-200 flex-1 border-b-2 flex items-center justify-center space-x-1"
            :class="activeTab === 'extras' ? 'border-green-500 text-green-700' : 'border-transparent hover:text-green-600 text-gray-600'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            <span v-if="sidebarOpen" class="truncate">Extras</span>
          </button>
        </div>

        <!-- Contenido según la pestaña activa -->
        <div class="flex-1 overflow-y-auto scrollbar-thin scrollbar-track-gray-100 scrollbar-thumb-green-500">
          <transition name="fade" mode="out-in">
            <!-- Contenido de la pestaña Principal -->
            <div v-if="activeTab === 'principal' && sidebarOpen" class="p-4 space-y-4 animate-fade-in">
              <h2 class="text-lg font-semibold text-green-800 flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
                <span>Capas Principales</span>
              </h2>
              
              <ul class="space-y-3">
                <li v-for="layer in layerGroups.principal" :key="layer.id" 
                    class="transform transition-all duration-300 hover:translate-x-1">
                  <div class="flex items-center p-2 rounded-lg hover:bg-green-50 transition-colors">
                    <div class="relative inline-block w-10 mr-2 align-middle select-none">
                      <input 
                        type="checkbox" 
                        :id="`layer-${layer.id}`" 
                        :checked="layer.visible"
                        @change="toggleLayerVisibility(layer)" 
                        class="opacity-0 absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
                      />
                      <label 
                        :for="`layer-${layer.id}`" 
                        class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"
                        :class="{'active': layer.visible}"
                      ></label>
                    </div>
                    <div>
                      <label :for="`layer-${layer.id}`" class="text-sm font-medium text-gray-700 cursor-pointer">
                        {{ layer.name }}
                      </label>
                      <p class="text-xs text-gray-500">{{ layer.description }}</p>
                    </div>
                  </div>
                </li>
              </ul>
            </div>

            <!-- Contenido de la pestaña Extras con iconos solo en modo colapsado -->
            <div v-else-if="activeTab === 'extras'" class="animate-fade-in">
              <!-- Contenido detallado cuando la sidebar está expandida -->
              <div v-if="sidebarOpen" class="p-4 space-y-4">
                <h2 class="text-lg font-semibold text-green-800 flex items-center space-x-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                  </svg>
                  <span>Herramientas</span>
                </h2>
                
                <!-- Herramientas del mapa mejoradas -->
                <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 shadow-sm">
                  <h3 class="text-base font-medium text-green-700 mb-4 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    Herramientas del mapa
                  </h3>
                  
                  <!-- Herramientas con iconos y efectos mejorados -->
                  <div class="grid grid-cols-2 gap-3">
                    <button 
                      v-for="tool in mapTools" 
                      :key="tool.id"
                      @click="activeToolPanel = activeToolPanel === tool.id ? '' : tool.id"
                      class="tool-button relative flex flex-col items-center justify-center p-3 rounded-xl transition-all duration-300 overflow-hidden group"
                      :class=" [
                        activeToolPanel === tool.id 
                          ? 'bg-green-100 text-green-700 shadow-md ring-2 ring-green-400 ring-opacity-50' 
                          : 'bg-white hover:bg-gray-50 text-gray-700 hover:text-green-600 shadow-sm hover:shadow'
                      ]"
                    >
                      <!-- Efecto de onda al hacer clic -->
                      <span class="absolute inset-0 bg-green-100 opacity-0 group-active:animate-ripple-effect"></span>
                      
                      <!-- Gradiente de fondo con efecto hover -->
                      <span class="absolute inset-0 bg-gradient-to-br from-green-50 to-emerald-50 opacity-0 group-hover:opacity-100 transition-all duration-500"></span>
                      
                      <!-- Iconos SVG para cada herramienta -->
                      <div class="relative z-10 mb-1 transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                        <!-- Icono para capas -->
                        <svg v-if="tool.id === 'layers'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 00-3.7-3.7 48.678 48.678 0 00-7.324 0 4.006 4.006 0 00-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3l-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 003.7 3.7 48.656 48.656 0 007.324 0 4.006 4.006 0 003.7-3.7c.017-.22.032-.441.046-.662M4.5 12l3 3m-3-3l-3 3" />
                        </svg>
                        
                        <!-- Icono para medición -->
                        <svg v-if="tool.id === 'measure'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                        </svg>
                        
                        <!-- Icono para dibujo -->
                        <svg v-if="tool.id === 'draw'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M15.042 21.672L13.684 16.6m0 0l-2.51 2.225.569-9.47 5.227 7.917-3.286-.672zm-7.518-.267A8.25 8.25 0 1120.25 10.5M8.288 14.212A5.25 5.25 0 1117.25 10.5" />
                        </svg>
                        
                        <!-- Icono para búsqueda -->
                        <svg v-if="tool.id === 'search'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                        </svg>
                      </div>
                      
                      <!-- Nombre de la herramienta -->
                      <span class="text-xs font-medium mt-1">{{ tool.name }}</span>
                      
                      <!-- Indicador de herramienta activa -->
                      <span v-if="activeToolPanel === tool.id" class="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                    </button>
                  </div>
                  
                  <!-- Descripción de la herramienta seleccionada -->
                  <div v-if="activeToolPanel" class="mt-3 px-4 py-2 bg-white/80 backdrop-blur-sm text-green-800 text-xs rounded-lg shadow-inner animate-fade-in">
                    <p class="flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {{ mapTools.find(t => t.id === activeToolPanel)?.description }}
                    </p>
                  </div>
                </div>
                
                <!-- Lista de capas adicionales -->
                <div class="mt-6">
                  <h3 class="text-sm font-medium text-gray-700 mb-3">Capas adicionales</h3>
                  <ul class="space-y-2">
                    <li v-for="layer in layerGroups.extras" :key="layer.id" 
                        class="transform transition-all duration-300 hover:translate-x-1">
                      <div class="flex items-center p-2 rounded-lg hover:bg-green-50 transition-colors">
                        <div class="relative inline-block w-10 mr-2 align-middle select-none">
                          <input 
                            type="checkbox" 
                            :id="`layer-${layer.id}`" 
                            :checked="layer.visible"
                            @change="toggleLayerVisibility(layer)" 
                            class="opacity-0 absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
                          />
                          <label 
                            :for="`layer-${layer.id}`" 
                            class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"
                            :class="{'active': layer.visible}"
                          ></label>
                        </div>
                        <div>
                          <label :for="`layer-${layer.id}`" class="text-sm font-medium text-gray-700 cursor-pointer">
                            {{ layer.name }}
                          </label>
                          <p class="text-xs text-gray-500">{{ layer.description }}</p>
                        </div>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Contenido minimalista cuando la sidebar está colapsada -->
              <div v-else class="py-4">
                <div class="flex flex-col items-center space-y-8">
                  <button v-for="tool in mapTools" 
                          :key="tool.id"
                          @click="activeToolPanel = activeToolPanel === tool.id ? '' : tool.id; sidebarOpen = true;"
                          class="p-2 rounded-lg hover:bg-green-50 transition-all duration-300 relative group"
                          :class="{'bg-green-100': activeToolPanel === tool.id}">
                    <!-- Tooltip para mostrar el nombre de la herramienta -->
                    <div class="absolute left-full ml-2 px-2 py-1 bg-gray-800 text-white text-xs rounded whitespace-nowrap opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
                      {{ tool.name }}
                      <div class="absolute top-1/2 -left-1 transform -translate-y-1/2 rotate-45 w-2 h-2 bg-gray-800"></div>
                    </div>

                    <!-- Icono para capas -->
                    <svg v-if="tool.id === 'layers'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 00-3.7-3.7 48.678 48.678 0 00-7.324 0 4.006 4.006 0 00-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3l-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 003.7 3.7 48.656 48.656 0 007.324 0 4.006 4.006 0 003.7-3.7c.017-.22.032-.441.046-.662M4.5 12l3 3m-3-3l-3 3" />
                    </svg>
                    
                    <!-- Icono para medición -->
                    <svg v-if="tool.id === 'measure'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                    
                    <!-- Icono para dibujo -->
                    <svg v-if="tool.id === 'draw'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15.042 21.672L13.684 16.6m0 0l-2.51 2.225.569-9.47 5.227 7.917-3.286-.672zm-7.518-.267A8.25 8.25 0 1120.25 10.5M8.288 14.212A5.25 5.25 0 1117.25 10.5" />
                    </svg>
                    
                    <!-- Icono para búsqueda -->
                    <svg v-if="tool.id === 'search'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                    </svg>
                    
                    <!-- Indicador de herramienta activa -->
                    <span v-if="activeToolPanel === tool.id" class="absolute -right-1 top-1/2 transform -translate-y-1/2 w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                  </button>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- Pie de la barra lateral -->
      <div class="p-3 bg-gradient-to-r from-green-50 to-emerald-50 border-t border-green-100 flex items-center justify-center">
        <p v-if="sidebarOpen" class="text-xs text-green-700">Geoportal Sembrando Datos</p>
        <span v-else class="text-green-700">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </span>
      </div>
    </aside>

    <!-- Contenido principal que se ajusta al espacio restante -->
    <div class="flex-1 relative">
      <!-- Overlay de carga con animación -->
      <div v-if="loading" 
           class="fixed inset-0 bg-white bg-opacity-90 z-50 flex flex-col items-center justify-center transition-opacity duration-500"
           :class="loading ? 'opacity-100' : 'opacity-0 pointer-events-none'">
        <div class="w-16 h-16 border-4 border-t-green-500 border-green-200 rounded-full animate-spin mb-4"></div>
        <p class="text-green-700 font-medium">Cargando geoportal...</p>
      </div>

      <!-- Mapa a pantalla completa -->
      <div ref="mapElement" class="absolute inset-0 z-0"></div>
      
      <!-- Header flotante con título y botones de acción -->
      <header class="absolute top-0 left-0 right-0 bg-white bg-opacity-95 shadow-md z-10 transition-all duration-300">
        <div class="container mx-auto px-4 py-2 sm:py-3 flex justify-between items-center">
          <!-- Logo y título -->
          <div class="flex items-center space-x-3">
            <img 
              src="@/components/images/logotipo.png" 
              alt="Logotipo Sembrando Datos" 
              class="h-10 sm:h-12 w-auto object-contain"
            />
            <h1 class="text-xl sm:text-2xl md:text-3xl font-serif font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-600 to-teal-500">
              Geoportal Sembrando Datos
            </h1>
          </div>

          <!-- Botones de acción -->
          <div class="flex items-center space-x-2 sm:space-x-4">
            <!-- Componente de perfil de usuario -->
            <UserProfile />
            
            <!-- Botón de inicio rediseñado -->
            <button 
              @click="handleGoHome"
              class="home-button px-4 py-2 bg-gradient-to-r from-emerald-500 to-green-500 text-white rounded-lg transition-all duration-300 flex items-center space-x-2 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50 transform hover:-translate-y-0.5 active:translate-y-0"
              aria-label="Volver a la página de inicio"
            >
              <span class="home-icon">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7m-7-7v14" />
                </svg>
              </span>
              <span class="hidden sm:inline font-medium">Inicio</span>
              <span class="absolute inset-0 w-full h-full bg-white rounded-lg transition-all duration-300 opacity-0 hover:opacity-20"></span>
            </button>

            <!-- Botón de guardar -->
            <button 
              @click="showSaveDialog = true"
              class="px-3 py-1.5 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-all duration-300 flex items-center space-x-1 shadow-sm hover:shadow focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <span>💾</span>
              <span class="hidden sm:inline text-sm">Guardar</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Panel lateral de herramientas - Ajustado para estar casi pegado a la barra lateral -->
      <div 
        v-if="activeToolPanel && sidebarOpen"
        class="absolute top-20 z-10 bg-white rounded-lg shadow-lg w-72 transition-all duration-500 ease-in-out animate-slide-in-right"
        :style="{ left: sidebarOpen ? (windowWidth >= 640 ? '5px' : '65px') : '0' }"
      >
        <!-- Contenido según herramienta activa -->
        <div v-if="activeToolPanel === 'measure'">
          <MeasurementTool :map="map" />
        </div>
        
        <!-- Panel de búsqueda -->
        <div v-if="activeToolPanel === 'search'">
          <SearchTool :map="map" />
        </div>
        
        <!-- Panel de dibujo -->
        <div v-if="activeToolPanel === 'draw'">
          <DrawTool :map="map" />
        </div>
        
        <!-- Panel de capas -->
        <div v-if="activeToolPanel === 'layers'">
          <LayersTool :map="map" :layers="getAllLayers()" />
        </div>
      </div>

      <!-- Atribución en la parte inferior -->
      <div class="absolute left-0 right-0 bottom-0 bg-white bg-opacity-90 text-xs py-1 px-3 text-gray-600 text-center z-10">
        <p>© 2023 Sembrando Datos - Geoportal de visualización territorial</p>
      </div>
    </div>

    <!-- Modal para guardar mapa -->
    <div v-if="showSaveDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-semibold text-green-800 mb-4">Guardar Mapa</h3>
        <input 
          v-model="newMapName"
          type="text"
          placeholder="Nombre del mapa"
          class="w-full px-3 py-2 border rounded-lg mb-4"
        />
        <div class="flex justify-end space-x-3">
          <button 
            @click="showSaveDialog = false"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Cancelar
          </button>
          <button 
            @click="saveMap"
            class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
          >
            Guardar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal elegante para confirmar salida -->
    <Transition name="modal-fade">
      <div v-if="showExitModal" 
           class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
           @click.self="showExitModal = false">
        <div class="bg-white rounded-2xl p-6 w-[90%] max-w-md transform transition-all duration-300
                    scale-100 opacity-100 shadow-xl animate-modal-in">
          <div class="text-center">
            <div class="mb-4 transform transition-all duration-500 hover:rotate-12">
              <span class="text-5xl">🏠</span>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-4">
              ¿Volver al inicio?
            </h3>
            <p class="text-gray-600 mb-8">
              ¿Estás seguro de que deseas salir del mapa actual? Los cambios no guardados se perderán.
            </p>
            <div class="flex space-x-3 justify-center">
              <button 
                @click="showExitModal = false"
                class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 
                       rounded-lg transition-colors duration-300"
              >
                Cancelar
              </button>
              <button 
                @click="confirmExit"
                class="px-4 py-2 bg-green-500 hover:bg-green-600 text-white 
                       rounded-lg transition-colors duration-300 flex items-center space-x-2
                       transform hover:scale-105 active:scale-100"
              >
                <span>Volver al inicio</span>
                <span class="text-xl transition-transform transform group-hover:translate-x-1">→</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal de cierre de sesión -->
    <Transition name="modal-fade">
      <div v-if="logoutModal" 
           class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
           @click.self="logoutModal = false">
        <div class="bg-white rounded-2xl p-6 w-[90%] max-w-md transform transition-all duration-300
                    scale-100 opacity-100 shadow-xl">
          <div class="text-center">
            <div class="mb-4 transform transition-all duration-500 hover:rotate-12">
              <span class="text-5xl">🚪</span>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-4">
              Cerrar sesión
            </h3>
            <p class="text-gray-600 mb-8">
              ¿Estás seguro de que deseas cerrar sesión? Los cambios no guardados se perderán.
            </p>
            <div class="flex space-x-3 justify-center">
              <button 
                @click="logoutModal = false"
                class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 
                       rounded-lg transition-colors duration-300"
              >
                Cancelar
              </button>
              <button 
                @click="confirmLogout"
                class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white 
                       rounded-lg transition-colors duration-300 flex items-center space-x-2"
              >
                <span>Cerrar sesión</span>
                <span class="text-xl">→</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* Corregir los selectores que usan @apply */
.tool-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tool-btn.active {
  background-color: #10B981;
  color: white;
}

/* Mejorar estilos de botones de acción */
button {
  font-weight: 500;
  font-size: 0.875rem;
}

button:active {
  transform: translateY(1px);
}

/* Animación suave para los botones */
.flex.items-center.space-x-4 button {
  position: relative;
  overflow: hidden;
}

.flex.items-center.space-x-4 button::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 60%);
  transform: translate(-50%, -50%) scale(0);
  transition: transform 0.5s;
  pointer-events: none;
}

.flex.items-center.space-x-4 button:hover::after {
  transform: translate(-50%, -50%) scale(2);
}

/* Estilos para tooltips de medición */
:global(.ol-tooltip) {
  position: relative;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 4px;
  color: white;
  padding: 4px 8px;
  font-size: 12px;
  white-space: nowrap;
  font-weight: bold;
}

:global(.ol-tooltip-measure) {
  opacity: 1;
  font-weight: bold;
}

:global(.ol-tooltip-static) {
  background-color: rgba(0, 128, 0, 0.7);
}

/* Estilos para botones de herramientas */
.tool-btn {
  width: 48px;
  height: 48px;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4B5563;
  transition: all 0.3s ease;
  transform: scale(1);
  animation: slideIn 0.5s ease-out forwards;
  animation-delay: var(--delay);
  opacity: 0;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.tool-btn:hover {
  color: #059669;
  transform: scale(1.05);
}

.tool-btn.active {
  background-color: #10B981;
  color: white;
  transform: scale(1.05);
}

.tool-background {
  position: absolute;
  inset: 0;
  background-color: #D1FAE5;
  opacity: 0;
  transition: all 0.3s ease;
  transform: scale(0);
  border-radius: inherit;
}

.tool-btn:hover .tool-background {
  transform: scale(1);
  opacity: 0.2;
}

.tool-label {
  position: absolute;
  left: 100%;
  margin-left: 0.5rem;
  padding: 0.25rem 0.5rem;
  background-color: #1F2937;
  color: white;
  font-size: 0.75rem;
  border-radius: 0.375rem;
  opacity: 0;
  transform: translateX(0.5rem);
  pointer-events: none;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.tool-btn:hover .tool-label {
  opacity: 1;
  transform: translateX(0);
}

/* Estilos para los switches */
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

input:checked + .toggle-label {
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

input:checked + .toggle-label::after {
  transform: translateX(1.5rem);
}

/* Animaciones para el modal */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .bg-white,
.modal-fade-leave-to .bg-white {
  transform: scale(0.9);
  opacity: 0;
}

/* Animación para elementos deslizados desde la derecha */
@keyframes slide-in-right {
  from {
    transform: translateX(20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.animate-slide-in-right {
  animation: slide-in-right 0.5s ease-out forwards;
}

/* Animación de fade-in para elementos */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.5s ease-out forwards;
}

/* Nuevos estilos para los botones de herramientas */
.tool-button {
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(229, 231, 235, 1);
}

.tool-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.tool-button:active {
  transform: translateY(0);
}

/* Animación para entrada deslizante desde abajo */
@keyframes slide-in-up {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.animate-slide-in-up {
  animation: slide-in-up 0.3s ease-out forwards;
}

/* Añadir estilos específicos para las capas */
.toggle-label.active {
  background-color: #10B981;
}

.toggle-label.active::after {
  transform: translateX(1.5rem);
}

/* Estilos para el botón de inicio */
.home-button {
  position: relative;
  overflow: hidden;
}

/* Animación del ícono del botón de inicio */
.home-icon {
  display: inline-flex;
  transition: transform 0.3s ease;
}

.home-button:hover .home-icon {
  animation: bounce 0.6s ease infinite alternate;
}

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-3px);
  }
}

/* Efecto de onda al hacer clic */
.home-button::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 5px;
  height: 5px;
  background: rgba(255, 255, 255, 0.5);
  opacity: 0;
  border-radius: 100%;
  transform: scale(1, 1) translate(-50%, -50%);
  transform-origin: 50% 50%;
}

.home-button:active::after {
  animation: ripple 0.6s ease-out;
}

@keyframes ripple {
  0% {
    transform: scale(0, 0) translate(-50%, -50%);
    opacity: 0.5;
  }
  100% {
    transform: scale(20, 20) translate(-50%, -50%);
    opacity: 0;
  }
}

/* Animación de entrada del modal */
@keyframes modal-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-modal-in {
  animation: modal-in 0.3s forwards;
}

/* Añadir efecto de onda para los botones */
@keyframes ripple-effect {
  0% {
    transform: scale(0);
    opacity: 1;
  }
  100% {
    transform: scale(4);
    opacity: 0;
  }
}

.group-active\:animate-ripple-effect {
  animation: ripple-effect 1s ease-out;
}

/* Añadir transición para la barra lateral */
.scrollbar-thin {
  scrollbar-width: thin;
}

.scrollbar-track-gray-100::-webkit-scrollbar-track {
  background-color: #f3f4f6;
}

.scrollbar-thumb-green-500::-webkit-scrollbar-thumb {
  background-color: #10b981;
}
</style>
