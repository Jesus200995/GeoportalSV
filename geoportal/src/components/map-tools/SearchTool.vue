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
const showInstructions = ref(true); // Para mostrar instrucciones cuando no hay búsqueda

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

// Función de búsqueda con debounce - modificada para priorizar lugares globales
const performSearch = async () => {
  if (!searchQuery.value.trim() || searchQuery.value.trim().length < 3) {
    searchResults.value = [];
    showInstructions.value = true;
    return;
  }

  showInstructions.value = false;
  loading.value = true;
  errorMessage.value = '';
  vectorSource.value.clear();

  try {
    // Primero buscamos en OpenStreetMap (Nominatim) para lugares de todo el mundo
    let nominatimResults = [];
    try {
      // Usamos parámetros que favorecen lugares específicos, no direcciones
      const nominatimResponse = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery.value)}&limit=8&addressdetails=1`
      );
      
      if (nominatimResponse.ok) {
        const nominatimData = await nominatimResponse.json();
        nominatimResults = nominatimData.map(place => ({
          id: `osm-${place.place_id}`,
          name: place.display_name,
          type: 'location',
          category: place.type || place.class,
          countryCode: place.address?.country_code,
          countryName: place.address?.country,
          city: place.address?.city || place.address?.town || place.address?.village,
          coordinates: [parseFloat(place.lon), parseFloat(place.lat)],
          importance: place.importance || 0.5,
          bbox: place.boundingbox ? [
            parseFloat(place.boundingbox[2]), 
            parseFloat(place.boundingbox[0]), 
            parseFloat(place.boundingbox[3]), 
            parseFloat(place.boundingbox[1])
          ] : null
        }));
          
        // Ordenar por importancia para mostrar primero los lugares más relevantes
        nominatimResults.sort((a, b) => b.importance - a.importance);      }
    } catch (error) {
      console.log('Error en búsqueda OpenStreetMap:', error);
      // No mostrar error ya que intentaremos con GeoServer
    }
    
    // Luego buscamos en GeoServer para entidades territoriales locales
    let geoserverResults = [];
    try {
      const geoserverUrl = import.meta.env.VITE_GEOSERVER_URL || 'https://geoportal.sembrandodatos.com/geoserver';
      const geoserverResponse = await fetch(
        `${geoserverUrl}/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=sembrando:territorios_28&outputFormat=application/json&CQL_FILTER=nombre_territorio ILIKE '%${searchQuery.value}%'`
      );

      if (geoserverResponse.ok) {
        const geoserverData = await geoserverResponse.json();
        const features = new GeoJSON().readFeatures(geoserverData, {
          featureProjection: 'EPSG:3857'
        });

        // Añadir características al mapa
        vectorSource.value.addFeatures(features);
        
        geoserverResults = features.map(feature => ({
          id: feature.getId() || `geoserver-${Math.random().toString(36)}`,
          name: feature.get('nombre_territorio') || 'Territorio sin nombre',
          type: 'territory',
          feature: feature,
          importance: 0.7 // Darles buena prioridad pero no más que países/ciudades grandes
        }));
      }
    } catch (error) {
      console.error('Error en búsqueda GeoServer:', error);
      // Continuar con los resultados de Nominatim si GeoServer falla
    }
    
    // Combinamos los resultados - primero lugares globales, luego territorios locales
    searchResults.value = [...nominatimResults, ...geoserverResults];

  } catch (error) {
    console.error('Error general en búsqueda:', error);
    errorMessage.value = 'Error al realizar la búsqueda. Intente nuevamente.';
  } finally {
    loading.value = false;
  }
};

// Implementación del debounce - reducido a 200ms para sentirse más en tiempo real
let timeoutId = null;
const debouncedSearch = () => {
  clearTimeout(timeoutId);
  timeoutId = setTimeout(() => {
    performSearch();
  }, 200); // Tiempo reducido para mejor respuesta
};

// Función para hacer zoom al resultado - mejorada para ir a la ubicación exacta
const zoomToResult = (result) => {
  selectedFeature.value = result;
  vectorSource.value.clear();

  let coordinates;
  let extent;
  let zoomLevel = 15; // Zoom predeterminado

  if (result.type === 'territory' && result.feature) {
    // Para características de GeoServer
    extent = result.feature.getGeometry().getExtent();
    coordinates = getCenter(extent);
    vectorSource.value.addFeature(result.feature);
  } else if (result.type === 'location' && result.coordinates) {
    // Para resultados de Nominatim (lugares del mundo)
    coordinates = fromLonLat(result.coordinates);
    
    // Crear un punto para marcar la ubicación
    const pointGeom = new Point(coordinates);
    const feature = new Feature({
      geometry: pointGeom,
      name: result.name
    });
    vectorSource.value.addFeature(feature);
    
    // Ajustar zoom según el tipo de lugar
    if (result.category === 'country') {
      zoomLevel = 6; // Zoom para países
    } else if (result.category === 'state' || result.category === 'region') {
      zoomLevel = 8; // Zoom para estados/regiones
    } else if (result.category === 'city' || result.category === 'administrative') {
      zoomLevel = 12; // Zoom para ciudades
    } else if (result.category === 'town' || result.category === 'village') {
      zoomLevel = 14; // Zoom para pueblos
    }
    
    // Si hay un bounding box disponible, úsalo para un mejor encuadre
    if (result.bbox) {
      try {
        const transformedBBox = [
          fromLonLat([result.bbox[0], result.bbox[1]]),
          fromLonLat([result.bbox[2], result.bbox[3]])
        ].flat();
        
        // Calcular extent desde el bbox transformado
        extent = [
          transformedBBox[0], transformedBBox[1],
          transformedBBox[2], transformedBBox[3]
        ];
      } catch (error) {
        console.error('Error al transformar bbox:', error);
        // En caso de error, usar las coordenadas del punto
      }
    }
  }

  if (coordinates) {
    if (extent && extent[0] !== extent[2] && extent[1] !== extent[3]) {
      // Si tenemos un extent válido, hacer zoom al extent con padding
      props.map.getView().fit(extent, {
        padding: [50, 50, 50, 50],
        duration: 1000
      });
    } else {
      // Si solo tenemos un punto, hacer zoom a las coordenadas
      props.map.getView().animate({
        center: coordinates,
        zoom: zoomLevel,
        duration: 1000
      });
    }
  }
};

// Limpiar búsqueda
const clearSearch = () => {
  searchQuery.value = '';
  searchResults.value = [];
  vectorSource.value.clear();
  errorMessage.value = '';
  showInstructions.value = true;
};

// Limpiar recursos cuando se desmonte
onBeforeUnmount(() => {
  if (vectorLayer.value && props.map) {
    props.map.removeLayer(vectorLayer.value);
  }
});

// Observar cambios en la consulta - se ejecuta en tiempo real
watch(searchQuery, () => {
  if (searchQuery.value.length >= 3) {
    debouncedSearch();
  } else if (searchQuery.value.length === 0) {
    clearSearch();
  } else {
    // Mostrar instrucciones cuando hay menos de 3 caracteres
    searchResults.value = [];
    showInstructions.value = true;
  }
});

// Obtener el icono según el tipo de lugar
const getLocationIcon = (result) => {
  if (result.type === 'territory') {
    return 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7';
  }
  
  if (result.category === 'country') {
    return 'M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9';
  }
  
  if (result.category === 'city' || result.category === 'town' || result.category === 'administrative') {
    return 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4';
  }
  
  if (result.category === 'natural' || result.category === 'leisure') {
    return 'M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25';
  }
  
  return 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z';
};

// Obtener descripción más detallada del resultado
const getLocationDescription = (result) => {
  if (result.type === 'territory') {
    return 'Territorio local';
  }
  
  let description = result.category ? result.category.charAt(0).toUpperCase() + result.category.slice(1) : 'Lugar';
  
  if (result.city && result.countryName) {
    return `${description} en ${result.city}, ${result.countryName}`;
  } else if (result.countryName) {
    return `${description} en ${result.countryName}`;
  }
  
  return description;
};
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

    <!-- Instrucciones de búsqueda -->
    <div v-if="showInstructions" class="bg-blue-50 p-4 rounded-xl text-sm text-blue-700">
      <h3 class="font-medium mb-2">Instrucciones de búsqueda:</h3>
      <ul class="space-y-2 ml-5 list-disc">
        <li>Escriba al menos 3 caracteres para buscar</li>
        <li>Puede buscar lugares de todo el mundo</li>
        <li>Los resultados aparecen en tiempo real</li>
        <li>Haga clic en un resultado para ir a esa ubicación exacta</li>
      </ul>
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
      <div v-for="(result, index) in searchResults" 
           :key="result.id"
           @click="zoomToResult(result)"
           :style="`--i: ${index}`"
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
            result.type === 'territory' ? 'bg-green-100' : 
            result.category === 'country' ? 'bg-purple-100' : 
            result.category === 'city' || result.category === 'administrative' ? 'bg-blue-100' : 
            'bg-amber-100'
          ]">
            <svg class="w-4 h-4" 
                 :class="result.type === 'territory' ? 'text-green-600' : 
                         result.category === 'country' ? 'text-purple-600' : 
                         result.category === 'city' || result.category === 'administrative' ? 'text-blue-600' : 
                         'text-amber-600'"
                 viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    :d="getLocationIcon(result)" />
            </svg>
          </div>
          
          <!-- Información del resultado -->
          <div class="flex-1">
            <div class="text-sm font-medium text-gray-900">{{ result.name }}</div>
            <div class="text-xs text-gray-500">
              {{ getLocationDescription(result) }}
            </div>
          </div>
          
          <!-- Indicador de resultado seleccionado -->
          <svg v-if="selectedFeature?.id === result.id" 
               class="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M5 13l4 4L19 7" />
          </svg>
        </div>
      </div>
    </div>
    
    <!-- Mensaje de no resultados -->
    <div v-if="searchQuery.length >= 3 && !loading && searchResults.length === 0" 
         class="py-8 text-center text-gray-500">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p>No se encontraron resultados para "{{ searchQuery }}"</p>
      <p class="text-sm mt-2">Intente con otro término de búsqueda</p>
    </div>
  </div>
</template>

<style scoped>
/* Estilizar scrollbar */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: #10B981 #E5E7EB;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #E5E7EB;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: #10B981;
  border-radius: 3px;
}

/* Animación para los resultados */
div[v-for] {
  animation: fadeIn 0.3s ease-out forwards;
  opacity: 0;
  animation-delay: calc(var(--i, 0) * 0.05s);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Estilos para las instrucciones */
.bg-blue-50 {
  animation: slideDown 0.3s ease-out forwards;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Animación de pulsación para el resultado seleccionado */
[class*="bg-green-50"] {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.2);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(16, 185, 129, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
  }
}

/* Efecto hover mejorado */
div[v-for]:hover {
  transform: translateY(-2px);
  transition: transform 0.2s ease;
}
</style>
