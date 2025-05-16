<script setup>
import { ref, onMounted, watch } from 'vue';
import Draw from 'ol/interaction/Draw';
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';
import { Vector as VectorSource } from 'ol/source';
import { Vector as VectorLayer } from 'ol/layer';
import { getArea, getLength } from 'ol/sphere';
import Overlay from 'ol/Overlay';

const props = defineProps(['map']);
const active = ref(false);
const measureType = ref(''); // 'line' o 'area'
const draw = ref(null);
const vectorLayer = ref(null);
const measureTooltip = ref(null);

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
          color: '#00ff00',
          width: 2,
        }),
        image: new CircleStyle({
          radius: 7,
          fill: new Fill({
            color: '#00ff00',
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
        color: 'rgba(255, 255, 255, 0.2)',
      }),
      stroke: new Stroke({
        color: 'rgba(0, 255, 0, 0.5)',
        lineDash: [10, 10],
        width: 2,
      }),
      image: new CircleStyle({
        radius: 5,
        stroke: new Stroke({
          color: 'rgba(0, 255, 0, 0.7)',
        }),
        fill: new Fill({
          color: 'rgba(255, 255, 255, 0.2)',
        }),
      }),
    }),
  });

  props.map.addInteraction(draw.value);

  let listener;
  draw.value.on('drawstart', (evt) => {
    let tooltipCoord = evt.coordinate;

    listener = evt.feature.getGeometry().on('change', (e) => {
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
    measureTooltip.value.getElement().className = 'ol-tooltip ol-tooltip-static';
    measureTooltip.value = null;
    createMeasureTooltip();
    if (listener) {
      ol.Observable.unByKey(listener);
    }
  });
};

const stopMeasuring = () => {
  active.value = false;
  if (draw.value) {
    props.map.removeInteraction(draw.value);
    draw.value = null;
  }
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
};

watch(active, (newValue) => {
  if (!newValue) {
    stopMeasuring();
  }
});

onMounted(() => {
  // Inicialización si es necesaria
});
</script>

<template>
  <div class="measurement-tools p-4">
    <div class="flex flex-col space-y-2">
      <button 
        @click="startMeasuring('line')" 
        :class="['btn', { 'active': active && measureType === 'line' }]"
        class="px-4 py-2 rounded-lg bg-white shadow-md hover:bg-green-50 transition-colors"
      >
        📏 Medir Distancia
      </button>
      <button 
        @click="startMeasuring('area')" 
        :class="['btn', { 'active': active && measureType === 'area' }]"
        class="px-4 py-2 rounded-lg bg-white shadow-md hover:bg-green-50 transition-colors"
      >
        📐 Medir Área
      </button>
      <button 
        @click="clearMeasurements"
        class="px-4 py-2 rounded-lg bg-white shadow-md hover:bg-red-50 text-red-600 transition-colors"
      >
        🗑️ Limpiar Mediciones
      </button>
    </div>
  </div>
</template>

<style scoped>
.btn.active {
  @apply bg-green-500 text-white;
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
</style>
