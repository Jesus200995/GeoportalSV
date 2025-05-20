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

// Unificar definición de emisiones - combinar 'save-success' y 'logout'
const emit = defineEmits(['save-success', 'logout']);

// Estado reactivo
const sidebarOpen = ref(true);
const map = ref(null);
const loading = ref(true); // Para mostrar animación de carga
const activeTab = ref('principal'); // Para controlar pestañas de grupos de capas
const activeToolPanel = ref(''); // layers, measure, draw, search
const layerOpacity = ref({}); // Para almacenar opacidad de capas
const searchQuery = ref('');
const searchResults = ref([]);

// Capas organizadas en grupos
const layerGroups = ref({
  principal: [
    {
      id: 1,
      name: 'Territorios 28',
      visible: true,
      type: 'wms',
      url: 'http://localhost:8089/geoserver/sembrandodatos/wms',
      params: {
        'LAYERS': 'territorios_28',
        'FORMAT': 'image/png',
        'TRANSPARENT': 'true'
      },
      description: 'Capa principal de territorios'
    }
  ],
  extras: [
    {
      id: 2,
      name: 'Calles',
      visible: false,
      type: 'wms',
      url: 'http://localhost:8089/geoserver/sembrandodatos/wms',
      params: {
        'LAYERS': 'territorios_28',
        'FORMAT': 'image/png',
        'TRANSPARENT': 'true'
      },
      description: 'Calles y vías principales'
    },
    {
      id: 3,
      name: 'Límites',
      visible: false,
      type: 'wms',
      url: 'http://localhost:8089/geoserver/sembrandodatos/wms',
      params: {
        'LAYERS': 'territorios_28',
        'FORMAT': 'image/png',
        'TRANSPARENT': 'true'
      },
      description: 'Límites de zonas administrativas'
    },
    {
      id: 4,
      name: 'Satélite',
      visible: false,
      type: 'wms',
      url: 'http://localhost:8089/geoserver/sembrandodatos/wms',
      params: {
        'LAYERS': 'territorios_28',
        'FORMAT': 'image/png',
        'TRANSPARENT': 'true'
      },
      description: 'Imagen satelital de la zona'
    }
  ]
});

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
  layer.visible = !layer.visible;
  
  // Buscar la capa correspondiente en el mapa y actualizar visibilidad
  if (map.value) {
    const mapLayers = map.value.getLayers().getArray();
    const olLayer = mapLayers.find(l => 
      l.get('name') === layer.name
    );
    
    if (olLayer) {
      olLayer.setVisible(layer.visible);
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
    const geoserverUrl = 'http://localhost:8089/geoserver'; // Definir explícitamente
    const response = await fetch(`${geoserverUrl}/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=sembrandodatos:territorios_28&outputFormat=application/json&CQL_FILTER=nombre_territorio ILIKE '%${searchQuery.value}%'`);
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
onMounted(() => {
  // Simular tiempo de carga para mostrar la animación
  setTimeout(() => {
    loading.value = false;
  }, 1000);

  // Crear capas base (OpenStreetMap)
  const osmLayer = new TileLayer({
    source: new OSM(),
    visible: true
  });
  
  // Crear capas WMS
  const wmsLayers = getAllLayers().map(layer => {
    return new TileLayer({
      source: new TileWMS({
        url: layer.url,
        params: layer.params,
        serverType: 'geoserver',
      }),
      visible: layer.visible,
      name: layer.name
    });
  });
  
  // Crear mapa
  map.value = new Map({
    target: mapElement.value,
    layers: [osmLayer, ...wmsLayers],
    view: new View({
      center: fromLonLat([-98.9, 21.5]), // [lon, lat]
      zoom: 10
    })
  });

  // Manejar cambios de tamaño
  const handleResize = () => {
    if (map.value) {
      setTimeout(() => map.value.updateSize(), 200);
    }
  };

  window.addEventListener('resize', handleResize);

  // Limpiar el listener cuando se desmonte
  onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize);
  });
});

// Limpiar recursos cuando el componente se desmonte
onBeforeUnmount(() => {
  if (map.value) {
    map.value.setTarget(undefined);
    map.value = null;
  }
});

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
  <div class="h-screen w-screen overflow-hidden relative bg-gray-50">
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
          
          <!-- Botón de inicio -->
          <button 
            @click="handleGoHome"
            class="px-3 py-1.5 bg-white text-green-700 rounded-lg hover:bg-green-50 transition-all duration-300 flex items-center space-x-1 shadow-sm hover:shadow focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <span>🏠</span>
            <span class="hidden sm:inline text-sm">Inicio</span>
          </button>

          <!-- Botón de guardar -->
          <button 
            @click="showSaveDialog = true"
            class="px-3 py-1.5 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-all duration-300 flex items-center space-x-1 shadow-sm hover:shadow focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <span>💾</span>
            <span class="hidden sm:inline text-sm">Guardar</span>
          </button>
          
          <!-- Botón del menú -->
          <button 
            @click="toggleSidebar" 
            class="p-2 rounded-full hover:bg-green-100 transition-colors duration-200 text-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </header>
    
    <!-- Barra lateral flotante plegable -->
    <aside 
      :class="`absolute top-14 sm:top-16 bottom-0 z-20 transition-all duration-500 ease-in-out 
              ${sidebarOpen ? 'left-0' : '-left-80 sm:-left-96'}`"
    >
      <div class="h-full w-80 sm:w-96 bg-white shadow-lg rounded-r-lg overflow-hidden flex flex-col">
        <!-- Pestañas de grupos de capas -->
        <div class="flex border-b border-gray-200">
          <button 
            @click="changeTab('principal')" 
            class="px-4 py-3 text-sm font-medium transition-colors duration-200 flex-1 border-b-2"
            :class="activeTab === 'principal' ? 'border-green-500 text-green-700' : 'border-transparent hover:text-green-600 text-gray-600'"
          >
            Capas Principales
          </button>
          <button 
            @click="changeTab('extras')" 
            class="px-4 py-3 text-sm font-medium transition-colors duration-200 flex-1 border-b-2"
            :class="activeTab === 'extras' ? 'border-green-500 text-green-700' : 'border-transparent hover:text-green-600 text-gray-600'"
          >
            Extras
          </button>
        </div>
        
        <!-- Contenido de pestañas -->
        <div class="p-4 flex-1 overflow-y-auto">
          <!-- Lista de capas principales -->
          <div v-if="activeTab === 'principal'" class="space-y-4 animate-fade-in">
            <h2 class="text-lg font-semibold text-green-800 mb-4">Capas Principales</h2>
            
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
          
          <!-- Lista de capas extras -->
          <div v-if="activeTab === 'extras'" class="space-y-4 animate-fade-in">
            <h2 class="text-lg font-semibold text-green-800 mb-4">Overlays y Extras</h2>
            
            <!-- Nueva sección de herramientas del mapa -->
            <div class="border-b border-gray-200 pb-6 mb-6">
              <h3 class="text-base font-medium text-green-700 mb-3 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                Herramientas del mapa
              </h3>
              
              <!-- Herramientas con iconos SVG modernos -->
              <div class="grid grid-cols-2 gap-3 mt-4">
                <button 
                  v-for="tool in mapTools" 
                  :key="tool.id"
                  @click="activeToolPanel = activeToolPanel === tool.id ? '' : tool.id"
                  class="tool-button relative flex flex-col items-center justify-center p-3 rounded-xl transition-all duration-300"
                  :class=" [
                    activeToolPanel === tool.id 
                      ? 'bg-green-100 text-green-700 shadow-md ring-2 ring-green-400 ring-opacity-50' 
                      : 'bg-white hover:bg-gray-50 text-gray-700 hover:text-green-600 shadow-sm hover:shadow'
                  ]"
                >
                  <!-- Capa de efecto hover -->
                  <span class="absolute inset-0 bg-gradient-to-tr from-green-50 to-transparent rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></span>
                  
                  <!-- Iconos SVG basados en la herramienta -->
                  <div class="relative z-10 mb-1">
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
                  
                  <!-- Indicador de activo -->
                  <span v-if="activeToolPanel === tool.id" class="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                </button>
              </div>
              
              <!-- Descripción de la herramienta seleccionada -->
              <div v-if="activeToolPanel" class="mt-3 px-4 py-2 bg-green-50 text-green-800 text-xs rounded-lg">
                <p class="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ mapTools.find(t => t.id === activeToolPanel)?.description }}
                </p>
              </div>
            </div>
            
            <ul class="space-y-3">
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
        
        <!-- Pie de la barra lateral -->
        <div class="bg-green-50 p-3 text-xs text-green-700 border-t border-green-100">
          <p>Seleccione las capas para visualizar en el mapa</p>
        </div>
      </div>
      
      <!-- Pestaña flotante para abrir cuando está cerrado en móviles -->
      <div 
        v-if="!sidebarOpen" 
        class="absolute top-1/2 -translate-y-1/2 -right-10 bg-white rounded-r-lg shadow-lg p-2 cursor-pointer"
        @click="toggleSidebar"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
        </svg>
      </div>
    </aside>
    
    <!-- Panel lateral de herramientas - Ahora aparecerá a la izquierda y solo cuando esté en la pestaña extras -->
    <div 
      v-if="activeToolPanel && activeTab === 'extras' && sidebarOpen"
      class="absolute top-20 left-96 z-10 bg-white rounded-lg shadow-lg w-72 transition-all duration-300 animate-slide-in-right"
    >
      <!-- Contenido según herramienta activa -->
      <div v-if="activeToolPanel === 'measure'">
        <MeasurementTool :map="map" />
      </div>
      
      <!-- Panel de búsqueda -->
      <div v-if="activeToolPanel === 'search'" class="p-4">
        <div class="flex space-x-2">
          <input 
            v-model="searchQuery"
            type="text"
            placeholder="Buscar lugares..."
            class="flex-1 px-3 py-2 border rounded-lg"
            @keyup.enter="searchFeatures"
          />
          <button 
            @click="searchFeatures"
            class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
            </svg>
          </button>
        </div>
        
        <!-- Resultados de búsqueda -->
        <div v-if="searchResults.length" class="mt-4 max-h-96 overflow-y-auto">
          <div 
            v-for="result in searchResults" 
            :key="result.id"
            class="p-2 hover:bg-green-50 cursor-pointer rounded-lg"
            @click="zoomToFeature(result)"
          >
            {{ result.properties.nombre_territorio }}
          </div>
        </div>
      </div>
      
      <!-- Panel de dibujo -->
      <div v-if="activeToolPanel === 'draw'" class="p-4">
        <div class="text-center py-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-green-600 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.042 21.672L13.684 16.6m0 0l-2.51 2.225.569-9.47 5.227 7.917-3.286-.672zm-7.518-.267A8.25 8.25 0 1120.25 10.5M8.288 14.212A5.25 5.25 0 1117.25 10.5" />
          </svg>
          <p class="text-gray-600 text-sm">Herramienta de dibujo próximamente</p>
        </div>
      </div>
      
      <!-- Panel de capas -->
      <div v-if="activeToolPanel === 'layers'" class="p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-3">Gestión de capas</h3>
        
        <div class="space-y-3 max-h-96 overflow-y-auto">
          <div v-for="layer in getAllLayers()" :key="layer.id" 
               class="p-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <div class="flex items-center justify-between">
              <div>
                <div class="flex items-center">
                  <input 
                    type="checkbox" 
                    :checked="layer.visible"
                    @change="toggleLayerVisibility(layer)" 
                    class="mr-2"
                  />
                  <span class="text-sm">{{ layer.name }}</span>
                </div>
              </div>
              
              <div class="flex items-center space-x-2">
                <button @click="moveLayer(layer, 'up')" class="text-gray-500 hover:text-green-600">↑</button>
                <button @click="moveLayer(layer, 'down')" class="text-gray-500 hover:text-green-600">↓</button>
              </div>
            </div>
            
            <div class="mt-2" v-if="layer.visible">
              <label :for="`opacity-${layer.id}`" class="text-xs text-gray-500 mb-1 block">Opacidad: {{ Math.round((layerOpacity[layer.id] || 1) * 100) }}%</label>
              <input 
                type="range" 
                :id="`opacity-${layer.id}`"
                min="0" 
                max="1" 
                step="0.1"
                :value="layerOpacity[layer.id] || 1"
                @input="updateLayerOpacity(layer, parseFloat($event.target.value))"
                class="w-full"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Botón flotante para herramientas en móviles cuando la sidebar está cerrada -->
    <button 
      v-if="!sidebarOpen"
      @click="toggleToolsPanel"
      class="fixed bottom-24 left-4 z-30 bg-green-500 text-white rounded-full p-3 shadow-lg hover:bg-green-600 transition-all duration-300 hover:scale-110 md:hidden"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    </button>
    
    <!-- Panel de herramientas para móviles cuando la barra lateral está cerrada -->
    <div 
      v-if="!sidebarOpen && showToolsPanel"
      class="fixed bottom-36 left-4 z-30 bg-white rounded-lg shadow-lg p-2 animate-slide-in-up md:hidden"
    >
      <div class="grid grid-cols-2 gap-2 p-1">
        <button 
          v-for="tool in mapTools" 
          :key="tool.id"
          @click="activeToolPanel = activeToolPanel === tool.id ? '' : tool.id; showToolsPanel = false; sidebarOpen = true; changeTab('extras');"
          class="p-2 rounded-lg bg-gray-50 flex flex-col items-center justify-center hover:bg-green-50 transition-colors"
        >
          <!-- Iconos SVG basados en la herramienta -->
          <div class="mb-1">
            <!-- Icono para capas -->
            <svg v-if="tool.id === 'layers'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 00-3.7-3.7 48.678 48.678 0 00-7.324 0 4.006 4.006 0 00-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3l-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 003.7 3.7 48.656 48.656 0 007.324 0 4.006 4.006 0 003.7-3.7c.017-.22.032-.441.046-.662M4.5 12l3 3m-3-3l-3 3" />
            </svg>
            
            <!-- Icono para medición -->
            <svg v-if="tool.id === 'measure'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            
            <!-- Icono para dibujo -->
            <svg v-if="tool.id === 'draw'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.042 21.672L13.684 16.6m0 0l-2.51 2.225.569-9.47 5.227 7.917-3.286-.672zm-7.518-.267A8.25 8.25 0 1120.25 10.5M8.288 14.212A5.25 5.25 0 1117.25 10.5" />
            </svg>
            
            <!-- Icono para búsqueda -->
            <svg v-if="tool.id === 'search'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
            </svg>
          </div>
          <span class="text-xs">{{ tool.name }}</span>
        </button>
      </div>
    </div>

    <!-- Atribución en la parte inferior -->
    <div class="absolute left-0 right-0 bottom-0 bg-white bg-opacity-90 text-xs py-1 px-3 text-gray-600 text-center z-10">
      <p>© 2023 Sembrando Datos - Geoportal de visualización territorial</p>
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
                    scale-100 opacity-100 shadow-xl">
          <div class="text-center">
            <div class="mb-4 transform transition-all duration-500 hover:rotate-12">
              <span class="text-5xl">🏠</span>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-4">
              ¿Volver al inicio?
            </h3>
            <p class="text-gray-600 mb-8">
              ¿Estás seguro de que deseas salir del mapa currente? Los cambios no guardados se perderán.
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
                       rounded-lg transition-colors duration-300 flex items-center space-x-2"
              >
                <span>Volver al inicio</span>
                <span class="text-xl">→</span>
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
</style>
