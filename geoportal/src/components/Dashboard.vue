<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import TileWMS from 'ol/source/TileWMS';
import { fromLonLat } from 'ol/proj';
import { watchEffect } from 'vue';
import MeasurementTool from './map-tools/MeasurementTool.vue';

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
    const response = await fetch(`${geoserverUrl}/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=sembrandodatos:territorios_28&outputFormat=application/json&CQL_FILTER=nombre_territorio ILIKE '%${searchQuery.value}%'`);
    const data = await response.json();
    searchResults.value = data.features;
  } catch (error) {
    console.error('Error en la búsqueda:', error);
  }
};

// Función para guardar el estado del mapa
const saveMapState = () => {
  const mapState = {
    id: Date.now(),
    name: 'Nuevo mapa',  // Permitir al usuario personalizar
    lastModified: new Date().toLocaleString(),
    center: map.value.getView().getCenter(),
    zoom: map.value.getView().getZoom(),
    layers: getAllLayers().map(layer => ({
      ...layer,
      visible: layer.visible,
      opacity: layerOpacity.value[layer.id] || 1
    }))
  };

  // Obtener mapas existentes
  let savedMaps = JSON.parse(localStorage.getItem('savedMaps') || '[]');
  savedMaps.push(mapState);
  localStorage.setItem('savedMaps', JSON.stringify(savedMaps));

  // Mostrar notificación
  alert('Mapa guardado exitosamente');
};

// Botón para guardar en la interfaz
const showSaveDialog = ref(false);
const newMapName = ref('');

const saveMap = () => {
  if (!newMapName.value.trim()) {
    alert('Por favor ingrese un nombre para el mapa');
    return;
  }
  
  saveMapState();
  showSaveDialog.value = false;
  newMapName.value = '';
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

// Función para obtener el icono de cada herramienta
const getToolIcon = (tool) => {
  const icons = {
    layers: '📑',  // Capas
    measure: '📏', // Medición
    draw: '✏️',    // Dibujo
    search: '🔍'   // Búsqueda
  };
  return icons[tool] || '❔';
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
    
    <!-- Header flotante con título -->
    <header class="absolute top-0 left-0 right-0 bg-white bg-opacity-95 shadow-md z-10 transition-all duration-300">
      <div class="container mx-auto px-4 py-2 sm:py-3 flex justify-between items-center">
        <div class="flex items-center space-x-3">
          <img 
            src="@/components/images/logotipo.png" 
            alt="Logotipo SembrandoDatos" 
            class="h-10 sm:h-12 w-auto object-contain"
          />
          <h1 class="text-xl sm:text-2xl md:text-3xl font-serif font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-600 to-teal-500">
            Geoportal SembrandoDatos
          </h1>
        </div>
        <button @click="toggleSidebar" 
                class="p-2 rounded-full hover:bg-green-100 transition-colors duration-200 text-green-700 focus:outline-none focus:ring-2 focus:ring-green-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
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
    
    <!-- Panel de herramientas -->
    <div class="absolute top-20 right-4 z-20 bg-white rounded-lg shadow-lg">
      <div class="tool-buttons flex flex-col space-y-2 p-2">
        <button 
          v-for="tool in ['layers', 'measure', 'draw', 'search']" 
          :key="tool"
          @click="activeToolPanel = activeToolPanel === tool ? '' : tool"
          :class="['tool-btn', { 'active': activeToolPanel === tool }]"
          class="p-2 rounded-lg hover:bg-green-50 transition-colors text-xl"
        >
          {{ getToolIcon(tool) }}
        </button>
      </div>
    </div>

    <!-- Panel lateral de herramientas -->
    <div 
      v-if="activeToolPanel"
      class="absolute top-20 right-16 z-10 bg-white rounded-lg shadow-lg w-72 transition-all duration-300"
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
            class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
          >
            🔍
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
    </div>

    <!-- Controles del mapa -->
    <div class="absolute right-4 bottom-20 flex flex-col space-y-2 z-10 animate-slide-in-right">
      <button @click="zoomIn" class="p-3 bg-white rounded-full shadow-md text-green-700 hover:bg-green-100 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
      </button>
      <button @click="zoomOut" class="p-3 bg-white rounded-full shadow-md text-green-700 hover:bg-green-100 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M5 10a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>

    <!-- Atribución en la parte inferior -->
    <div class="absolute left-0 right-0 bottom-0 bg-white bg-opacity-90 text-xs py-1 px-3 text-gray-600 text-center z-10">
      <p>© 2023 SembrandoDatos - Geoportal de visualización territorial</p>
    </div>

    <!-- Agregar botón de guardar en la barra de herramientas -->
    <button 
      @click="showSaveDialog = true"
      class="absolute top-20 right-4 mt-2 bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors shadow-md"
    >
      💾 Guardar Mapa
    </button>

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
  </div>
</template>

<style scoped>
/* ...existing styles... */

.tool-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tool-btn.active {
  @apply bg-green-500 text-white;
}
</style>
