<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue';
import Draw from 'ol/interaction/Draw';
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';
import { Vector as VectorSource } from 'ol/source';
import { Vector as VectorLayer } from 'ol/layer';
import { getArea, getLength } from 'ol/sphere';
import Overlay from 'ol/Overlay';
import { unByKey } from 'ol/Observable';

const props = defineProps(['map']);
const active = ref(false);
const measureType = ref(''); // 'line' o 'area'
const draw = ref(null);
const vectorLayer = ref(null);
const measureTooltip = ref(null);
const drawListener = ref(null);
const listener = ref(null);

const createMeasureTooltip = () => {
  if (measureTooltip.value) {
    props.map.removeOverlay(measureTooltip.value);
  }
  const element = document.createElement('div');
  element.className = 'ol-tooltip ol-tooltip-measure';
  measureTooltip.value = new Overlay({
    element: element,
    offset: [0, -15],
    positioning: 'bottom-center',
    stopEvent: false,
  });
  props.map.addOverlay(measureTooltip.value);
};

const formatLength = (line) => {
  const length = getLength(line);
  let output;
  if (length > 100) {
    output = Math.round((length / 1000) * 100) / 100 + ' km';
  } else {
    output = Math.round(length * 100) / 100 + ' m';
  }
  return output;
};

const formatArea = (polygon) => {
  const area = getArea(polygon);
  let output;
  if (area > 10000) {
    output = Math.round((area / 1000000) * 100) / 100 + ' km²';
  } else {
    output = Math.round(area * 100) / 100 + ' m²';
  }
  return output;
};

const startMeasuring = (type) => {
  // Detener cualquier medición activa antes de comenzar una nueva
  stopMeasuring();
  
  measureType.value = type;
  active.value = true;
  
  // Crear capa vectorial si no existe
  if (!vectorLayer.value) {
    const source = new VectorSource();
    vectorLayer.value = new VectorLayer({
      source: source,
      style: new Style({
        fill: new Fill({
          color: 'rgba(255, 255, 255, 0.2)',
        }),
        stroke: new Stroke({
          color: '#10B981', // Color verde moderno
          width: 2,
        }),
        image: new CircleStyle({
          radius: 7,
          fill: new Fill({
            color: '#10B981', // Color verde moderno
          }),
        }),
      }),
    });
    props.map.addLayer(vectorLayer.value);
  }

  createMeasureTooltip();

  // Configurar interacción de dibujo
  draw.value = new Draw({
    source: vectorLayer.value.getSource(),
    type: type === 'area' ? 'Polygon' : 'LineString',
    style: new Style({
      fill: new Fill({
        color: 'rgba(16, 185, 129, 0.2)', // Color verde moderno semitransparente
      }),
      stroke: new Stroke({
        color: 'rgba(16, 185, 129, 0.7)', // Color verde moderno
        lineDash: [10, 10],
        width: 2,
      }),
      image: new CircleStyle({
        radius: 5,
        stroke: new Stroke({
          color: 'rgba(16, 185, 129, 0.7)', // Color verde moderno
        }),
        fill: new Fill({
          color: 'rgba(255, 255, 255, 0.5)', // Blanco semitransparente
        }),
      }),
    }),
    // Añadir freehand: true para permitir dibujo a mano alzada
    freehand: false,
  });

  props.map.addInteraction(draw.value);

  drawListener.value = draw.value.on('drawstart', (evt) => {
    let tooltipCoord = evt.coordinate;

    listener.value = evt.feature.getGeometry().on('change', (e) => {
      const geom = e.target;
      let output;
      if (type === 'area') {
        output = formatArea(geom);
        tooltipCoord = geom.getInteriorPoint().getCoordinates();
      } else {
        output = formatLength(geom);
        tooltipCoord = geom.getLastCoordinate();
      }
      measureTooltip.value.getElement().innerHTML = output;
      measureTooltip.value.setPosition(tooltipCoord);
    });
  });

  draw.value.on('drawend', () => {
    if (measureTooltip.value && measureTooltip.value.getElement()) {
      measureTooltip.value.getElement().className = 'ol-tooltip ol-tooltip-static';
      measureTooltip.value = null;
      createMeasureTooltip();
    }
    if (listener.value) {
      unByKey(listener.value);
      listener.value = null;
    }
  });

  // Agregar evento de tecla para cancelar medición
  document.addEventListener('keydown', handleKeyDown);
};

const handleKeyDown = (e) => {
  // Cancelar la medición con la tecla Escape
  if (e.key === 'Escape' && active.value) {
    stopMeasuring();
  }
};

const stopMeasuring = () => {
  active.value = false;
  if (draw.value) {
    props.map.removeInteraction(draw.value);
    draw.value = null;
  }

  if (drawListener.value) {
    unByKey(drawListener.value);
    drawListener.value = null;
  }

  if (listener.value) {
    unByKey(listener.value);
    listener.value = null;
  }

  document.removeEventListener('keydown', handleKeyDown);
};

// Limpiar mediciones
const clearMeasurements = () => {
  if (vectorLayer.value) {
    vectorLayer.value.getSource().clear();
  }
  if (measureTooltip.value) {
    props.map.removeOverlay(measureTooltip.value);
    measureTooltip.value = null;
  }
  stopMeasuring();
};

// Toggles para los modos de medición
const toggleLineMode = () => {
  if (active.value && measureType.value === 'line') {
    stopMeasuring();
  } else {
    startMeasuring('line');
  }
};

const toggleAreaMode = () => {
  if (active.value && measureType.value === 'area') {
    stopMeasuring();
  } else {
    startMeasuring('area');
  }
};

// Configurar medición a mano alzada
const freehandMode = ref(false);

const toggleFreehandMode = () => {
  freehandMode.value = !freehandMode.value;
  if (active.value) {
    // Reiniciar la medición para aplicar el cambio de modo
    const currentType = measureType.value;
    stopMeasuring();
    startMeasuring(currentType);
    
    if (draw.value) {
      draw.value.setFreehand(freehandMode.value);
    }
  }
};

watch(active, (newValue) => {
  if (!newValue) {
    stopMeasuring();
  }
});

onMounted(() => {
  // Inicialización si es necesaria
});

onBeforeUnmount(() => {
  stopMeasuring();
  if (vectorLayer.value && props.map) {
    props.map.removeLayer(vectorLayer.value);
  }
});
</script>

<template>
  <div class="measurement-tools p-4 bg-white rounded-lg">
    <div class="flex flex-col space-y-3">
      <h3 class="text-base font-medium text-gray-700 mb-1 flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
        Herramientas de Medición
      </h3>
      
      <p class="text-xs text-gray-500 mb-2">Seleccione una herramienta para comenzar a medir. Presione ESC para detener la medición.</p>
      
      <!-- Botón para medir distancia -->
      <button 
        @click="toggleLineMode" 
        :class="['btn-measure flex items-center justify-between p-3 rounded-lg transition-all duration-300', active && measureType === 'line' ? 'bg-green-100 text-green-700 shadow-md ring-2 ring-green-400 ring-opacity-50' : 'bg-white hover:bg-gray-50 text-gray-700 hover:text-green-600 shadow-sm hover:shadow border border-gray-200']"
      >
        <div class="flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2 12h20M2 12l10 10m-10 -10l10 -10" />
          </svg>
          <span class="font-medium">Medir Distancia</span>
        </div>
        <span v-if="active && measureType === 'line'" class="text-xs bg-green-200 text-green-800 px-2 py-1 rounded-full">Activo</span>
      </button>
      
      <!-- Botón para medir área -->
      <button 
        @click="toggleAreaMode" 
        :class="['btn-measure flex items-center justify-between p-3 rounded-lg transition-all duration-300', active && measureType === 'area' ? 'bg-green-100 text-green-700 shadow-md ring-2 ring-green-400 ring-opacity-50' : 'bg-white hover:bg-gray-50 text-gray-700 hover:text-green-600 shadow-sm hover:shadow border border-gray-200']"
      >
        <div class="flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5Zm10 0a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1V5ZM4 15a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-4Zm10 0a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1v-4Z" />
          </svg>
          <span class="font-medium">Medir Área</span>
        </div>
        <span v-if="active && measureType === 'area'" class="text-xs bg-green-200 text-green-800 px-2 py-1 rounded-full">Activo</span>
      </button>
      
      <!-- Opción para dibujo a mano alzada -->
      <div class="p-3 bg-gray-50 rounded-lg border border-gray-200 mt-2">
        <div class="flex items-center justify-between">
          <label class="flex items-center text-sm text-gray-700 cursor-pointer">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125" />
            </svg>
            Modo a mano alzada
          </label>
          <div class="relative inline-block w-10 align-middle select-none">
            <input 
              type="checkbox" 
              id="toggle-freehand" 
              :checked="freehandMode"
              @change="toggleFreehandMode" 
              class="opacity-0 absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
            />
            <label 
              for="toggle-freehand" 
              class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"
              :class="{'active': freehandMode}"
            ></label>
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">Activa este modo para dibujar libremente con el mouse.</p>
      </div>
      
      <!-- Botones de control adicionales -->
      <div class="flex space-x-3 mt-2">
        <!-- Botón para detener medición actual -->
        <button 
          @click="stopMeasuring"
          :disabled="!active"
          class="flex-1 px-4 py-2 rounded-lg bg-yellow-500 text-white hover:bg-yellow-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
          </svg>
          Detener
        </button>
        
        <!-- Botón para limpiar todas las mediciones -->
        <button 
          @click="clearMeasurements"
          class="flex-1 px-4 py-2 rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors flex items-center justify-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
          </svg>
          Limpiar todo
        </button>
      </div>
    </div>
    
    <!-- Instrucciones adicionales -->
    <div class="mt-4 p-3 bg-blue-50 rounded-lg text-blue-800 text-xs">
      <div class="flex items-start">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 mt-0.5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <p class="font-medium mb-1">Instrucciones:</p>
          <ul class="list-disc list-inside pl-2 space-y-1">
            <li>Haga clic para iniciar y continuar la medición</li>
            <li>Doble clic para finalizar la medición</li>
            <li>Presione ESC para cancelar la medición actual</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Estilos para los botones de medición */
.btn-measure {
  position: relative;
  overflow: hidden;
}

.btn-measure:hover {
  transform: translateY(-2px);
}

.btn-measure:active {
  transform: translateY(0);
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

/* Estilos para tooltips de medición - estos son globales pero los redefino aquí */
:global(.ol-tooltip) {
  position: relative;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 4px;
  color: white;
  padding: 4px 8px;
  font-size: 12px;
  white-space: nowrap;
  font-weight: bold;
  pointer-events: none;
}

:global(.ol-tooltip-measure) {
  opacity: 1;
  font-weight: bold;
}

:global(.ol-tooltip-static) {
  background-color: rgba(16, 185, 129, 0.7);
  border: 1px solid white;
}

/* Mejorar la lista de instrucciones */
ul.list-inside li {
  text-indent: -1rem;
  padding-left: 1rem;
}
</style>
