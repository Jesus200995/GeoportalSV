<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { Vector as VectorLayer } from 'ol/layer';
import { Vector as VectorSource } from 'ol/source';
import { Style, Fill, Stroke, Circle as CircleStyle } from 'ol/style';
import { fromLonLat, transform } from 'ol/proj';
import GeoJSON from 'ol/format/GeoJSON';
import { getCenter } from 'ol/extent';
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';

const props = defineProps(['map']);
const searchQuery = ref('');
const searchResults = ref([]);
const loading = ref(false);
const errorMessage = ref('');
const vectorSource = ref(null);
const vectorLayer = ref(null);
const selectedFeature = ref(null);

// Inicializar capa vectorial para resultados
onMounted(() => {
  vectorSource.value = new VectorSource();
  vectorLayer.value = new VectorLayer({
    source: vectorSource.value,
    style: new Style({
      image: new CircleStyle({
        radius: 8,
        fill: new Fill({ color: '#10B981' }),
        stroke: new Stroke({ color: '#047857', width: 2 })
      }),
      stroke: new Stroke({
        color: '#10B981',
        width: 3
      }),
      fill: new Fill({
        color: 'rgba(16, 185, 129, 0.2)'
      })
    }),
    zIndex: 999
  });
  props.map.addLayer(vectorLayer.value);
});

// Función de búsqueda con debounce
const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    searchResults.value = [];
    return;
  }

  loading.value = true;
  errorMessage.value = '';
  vectorSource.value.clear();

  try {
    // Búsqueda en GeoServer
    const geoserverUrl = 'http://31.97.8.51:8082/geoserver';
    const geoserverResponse = await fetch(
      `${geoserverUrl}/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=sembrando:territorios_28&outputFormat=application/json&CQL_FILTER=nombre_territorio ILIKE '%${searchQuery.value}%'`
    );

    if (!geoserverResponse.ok) {
      throw new Error('Error en la conexión con GeoServer');
    }
    
    const geoserverData = await geoserverResponse.json();
    const features = new GeoJSON().readFeatures(geoserverData, {
      featureProjection: 'EPSG:3857'
    });

    vectorSource.value.addFeatures(features);
    
    const geoserverResults = features.map(feature => ({
      id: feature.getId() || `geoserver-${Math.random().toString(36)}`,
      name: feature.get('nombre_territorio') || 'Territorio sin nombre',
      type: 'territory',
      feature: feature
    }));

    // Búsqueda en Nominatim (OpenStreetMap) como respaldo
    let nominatimResults = [];
    try {
      const nominatimResponse = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery.value)}&limit=5`
      );
      
      if (nominatimResponse.ok) {
        const nominatimData = await nominatimResponse.json();
        nominatimResults = nominatimData.map(place => ({
          id: `osm-${place.place_id}`,
          name: place.display_name,
          type: 'location',
          coordinates: [parseFloat(place.lon), parseFloat(place.lat)]
        }));
      }
    } catch (error) {
      console.log('Error en búsqueda OpenStreetMap:', error);
      // No mostrar error ya que es un respaldo
    }
    
    searchResults.value = [...geoserverResults, ...nominatimResults];

  } catch (error) {
    console.error('Error en búsqueda:', error);
    errorMessage.value = 'Error al realizar la búsqueda. Intente nuevamente.';
  } finally {
    loading.value = false;
  }
};

// Implementación del debounce manualmente
let timeoutId = null;
const debouncedSearch = () => {
  clearTimeout(timeoutId);
  timeoutId = setTimeout(() => {
    performSearch();
  }, 300);
};

// Función para hacer zoom al resultado
const zoomToResult = (result) => {
  selectedFeature.value = result;
  vectorSource.value.clear();

  let coordinates;
  let extent;

  if (result.type === 'territory' && result.feature) {
    // Para características de GeoServer
    extent = result.feature.getGeometry().getExtent();
    coordinates = getCenter(extent);
    vectorSource.value.addFeature(result.feature);
  } else if (result.type === 'location' && result.coordinates) {
    // Para resultados de Nominatim
    coordinates = fromLonLat(result.coordinates);
    const pointGeom = new Point(coordinates);
    const feature = new Feature({
      geometry: pointGeom,
      name: result.name
    });
    vectorSource.value.addFeature(feature);
  }

  if (coordinates) {
    props.map.getView().animate({
      center: coordinates,
      zoom: 15,
      duration: 1000
    });
  }
};

// Limpiar búsqueda
const clearSearch = () => {
  searchQuery.value = '';
  searchResults.value = [];
  vectorSource.value.clear();
  errorMessage.value = '';
};

// Limpiar recursos cuando se desmonte
onBeforeUnmount(() => {
  if (vectorLayer.value && props.map) {
    props.map.removeLayer(vectorLayer.value);
  }
});

// Observar cambios en la consulta
watch(searchQuery, () => {
  if (searchQuery.value.length >= 3) {
    debouncedSearch();
  } else if (searchQuery.value.length === 0) {
    clearSearch();
  }
});
</script>

<template>
  <div class="search-tool p-4 space-y-4">
    <!-- Barra de búsqueda -->
    <div class="relative">
      <input 
        v-model="searchQuery"
        type="text"
        placeholder="Buscar lugares, territorios..."
        class="w-full pl-10 pr-12 py-3 bg-white border border-gray-200 rounded-xl
               focus:ring-2 focus:ring-green-500 focus:border-transparent
               shadow-sm transition-all"
      />
      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </span>
      <button 
        v-if="searchQuery"
        @click="clearSearch"
        class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400
               hover:text-gray-600 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Estado de carga -->
    <div v-if="loading" class="flex justify-center py-4">
      <div class="animate-spin rounded-full h-6 w-6 border-2 border-green-500 border-t-transparent"></div>
    </div>

    <!-- Mensaje de error -->
    <div v-if="errorMessage" class="p-3 bg-red-50 text-red-600 rounded-lg text-sm">
      {{ errorMessage }}
    </div>

    <!-- Resultados -->
    <div v-if="searchResults.length && !loading" 
         class="space-y-2 max-h-[calc(100vh-300px)] overflow-y-auto rounded-lg">
      <div v-for="result in searchResults" 
           :key="result.id"
           @click="zoomToResult(result)"
           :class=" [
             'p-3 rounded-lg cursor-pointer transition-all',
             selectedFeature?.id === result.id 
               ? 'bg-green-50 ring-1 ring-green-500'
               : 'hover:bg-gray-50'
           ]"
      >
        <div class="flex items-center space-x-3">
          <!-- Icono según tipo -->
          <div :class=" [
            'p-2 rounded-full',
            result.type === 'territory' ? 'bg-green-100' : 'bg-blue-100'
          ]">
            <svg v-if="result.type === 'territory'" class="w-4 h-4 text-green-600" 
                 viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
            <svg v-else class="w-4 h-4 text-blue-600" viewBox="0 0 24 24"
                 fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          
          <div class="flex-1">
            <h4 class="text-sm font-medium text-gray-900">{{ result.name }}</h4>
            <p class="text-xs text-gray-500">
              {{ result.type === 'territory' ? 'Territorio' : 'Ubicación' }}
            </p>
          </div>
          
          <button 
            class="p-1 text-gray-400 hover:text-green-600 rounded-full hover:bg-green-50 transition-all"
            @click.stop="zoomToResult(result)"
            title="Ir a ubicación"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Sin resultados -->
    <div v-else-if="searchQuery && !loading && !searchResults.length" 
         class="text-center py-8 text-gray-500">
      <svg class="w-12 h-12 mx-auto text-gray-400 mb-3" fill="none" 
           viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p>No se encontraron resultados</p>
    </div>
    
    <!-- Instrucciones de búsqueda -->
    <div v-if="!searchQuery && !searchResults.length" class="text-center py-6">
      <div class="bg-blue-50 rounded-lg p-4 text-blue-800 text-sm">
        <p class="mb-2">Instrucciones de búsqueda:</p>
        <ul class="text-xs text-left list-disc pl-5 space-y-1">
          <li>Escriba al menos 3 caracteres para buscar</li>
          <li>Puede buscar por nombres de territorios</li>
          <li>También se mostrarán resultados de OpenStreetMap</li>
          <li>Haga clic en un resultado para ver su ubicación en el mapa</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Estilos para el scrollbar */
.max-h-\[calc\(100vh-300px\)\] {
  scrollbar-width: thin;
  scrollbar-color: #10B981 #E5E7EB;
}

.max-h-\[calc\(100vh-300px\)\]::-webkit-scrollbar {
  width: 6px;
}

.max-h-\[calc\(100vh-300px\)\]::-webkit-scrollbar-track {
  background: #E5E7EB;
  border-radius: 3px;
}

.max-h-\[calc\(100vh-300px\)\]::-webkit-scrollbar-thumb {
  background-color: #10B981;
  border-radius: 3px;
}

/* Animaciones */
.search-tool {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
