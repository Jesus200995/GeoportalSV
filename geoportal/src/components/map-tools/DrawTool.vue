<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import Draw from 'ol/interaction/Draw';
import Modify from 'ol/interaction/Modify';
import Snap from 'ol/interaction/Snap';
import { Vector as VectorSource } from 'ol/source';
import { Vector as VectorLayer } from 'ol/layer';
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';
import { createBox } from 'ol/interaction/Draw';
import { unByKey } from 'ol/Observable';

const props = defineProps(['map']);
const drawType = ref('Point');
const drawing = ref(false);
const vectorSource = ref(null);
const vectorLayer = ref(null);
const draw = ref(null);
const snap = ref(null);
const modify = ref(null);
const freehandMode = ref(false);

// Estilos para los diferentes tipos de geometrías
const drawStyles = ref({
  Point: {
    color: '#10B981',
    size: 8
  },
  LineString: {
    color: '#10B981',
    width: 3
  },
  Polygon: {
    color: '#10B981',
    fill: 'rgba(16, 185, 129, 0.2)'
  },
  Circle: {
    color: '#10B981',
    fill: 'rgba(16, 185, 129, 0.2)'
  },
  Box: {
    color: '#10B981',
    fill: 'rgba(16, 185, 129, 0.2)'
  }
});

// Definir las herramientas de dibujo disponibles
const drawTools = [
  { id: 'Point', name: 'Punto', icon: '●' },
  { id: 'LineString', name: 'Línea', icon: '━' },
  { id: 'Polygon', name: 'Polígono', icon: '▲' },
  { id: 'Circle', name: 'Círculo', icon: '○' },
  { id: 'Box', name: 'Rectángulo', icon: '□' }
];

// Inicializar capa vectorial
onMounted(() => {
  vectorSource.value = new VectorSource();
  vectorLayer.value = new VectorLayer({
    source: vectorSource.value,
    style: createStyle,
    zIndex: 1000
  });
  props.map.addLayer(vectorLayer.value);
});

// Crear estilo para las geometrías
const createStyle = (feature) => {
  const geometryType = feature ? feature.getGeometry().getType() : drawType.value;
  let actualType = geometryType;
  
  // Manejar el tipo Box que en realidad es Circle con función geometryFunction
  if (geometryType === 'Circle' && feature) {
    // Intentar determinar si era un Box basado en propiedades
    const isBox = feature.get('isBox');
    if (isBox) actualType = 'Box';
  } else if (drawType.value === 'Box' && !feature) {
    actualType = 'Box';
  }
  
  const style = drawStyles.value[actualType] || drawStyles.value['Polygon'];

  return new Style({
    image: new CircleStyle({
      radius: style.size || 8,
      fill: new Fill({
        color: style.color
      }),
      stroke: new Stroke({
        color: '#ffffff',
        width: 2
      })
    }),
    stroke: new Stroke({
      color: style.color || '#10B981',
      width: style.width || 3,
      lineDash: drawing.value ? [10, 10] : null
    }),
    fill: new Fill({
      color: style.fill || 'rgba(16, 185, 129, 0.2)'
    })
  });
};

// Iniciar dibujo
const startDrawing = () => {
  stopDrawing();
  drawing.value = true;

  // Configurar geometryFunction para rectángulos
  let geometryFunction;
  let type = drawType.value;
  
  if (drawType.value === 'Box') {
    geometryFunction = createBox();
    type = 'Circle'; // OpenLayers usa Circle con geometryFunction para crear cajas
  }

  draw.value = new Draw({
    source: vectorSource.value,
    type: type,
    geometryFunction: geometryFunction,
    style: createStyle,
    freehand: freehandMode.value && drawType.value !== 'Point'
  });

  // Agregar markado para los rectángulos
  if (drawType.value === 'Box') {
    draw.value.on('drawend', (event) => {
      event.feature.set('isBox', true);
    });
  }

  modify.value = new Modify({ 
    source: vectorSource.value,
    style: createStyle
  });
  
  snap.value = new Snap({ source: vectorSource.value });

  props.map.addInteraction(draw.value);
  props.map.addInteraction(modify.value);
  props.map.addInteraction(snap.value);

  // Eventos
  draw.value.on('drawstart', () => {
    drawing.value = true;
  });

  draw.value.on('drawend', () => {
    drawing.value = false;
  });
};

// Detener dibujo
const stopDrawing = () => {
  drawing.value = false;
  
  if (draw.value) {
    props.map.removeInteraction(draw.value);
    draw.value = null;
  }
  
  if (modify.value) {
    props.map.removeInteraction(modify.value);
    modify.value = null;
  }
  
  if (snap.value) {
    props.map.removeInteraction(snap.value);
    snap.value = null;
  }
};

// Limpiar dibujos
const clearDrawings = () => {
  if (vectorSource.value) {
    vectorSource.value.clear();
  }
};

// Cambiar tipo de dibujo
const changeDrawType = (type) => {
  drawType.value = type;
  if (drawing.value) {
    startDrawing();
  }
};

// Toggle modo mano alzada
const toggleFreehand = () => {
  freehandMode.value = !freehandMode.value;
  if (drawing.value) {
    startDrawing();
  }
};

// Función para actualizar estilo
const updateStyle = () => {
  // Forzar actualización del estilo
  vectorLayer.value.changed();
  if (drawing.value) {
    // Reiniciar el dibujo para que tome el nuevo estilo
    startDrawing();
  }
};

// Limpiar al desmontar
onBeforeUnmount(() => {
  stopDrawing();
  if (vectorLayer.value && props.map) {
    props.map.removeLayer(vectorLayer.value);
  }
});
</script>

<template>
  <div class="draw-tools p-4 space-y-4">
    <!-- Tipos de geometrías -->
    <div class="grid grid-cols-3 gap-2">
      <button
        v-for="tool in drawTools"
        :key="tool.id"
        @click="changeDrawType(tool.id)"
        :class="[
          'p-3 rounded-xl transition-all text-center',
          drawType === tool.id
            ? 'bg-green-100 text-green-700 ring-2 ring-green-400 ring-opacity-50'
            : 'bg-white hover:bg-gray-50 text-gray-600 hover:text-green-600'
        ]"
      >
        <span class="block text-xl mb-1">{{ tool.icon }}</span>
        <span class="text-xs font-medium">{{ tool.name }}</span>
      </button>
    </div>

    <!-- Controles de dibujo -->
    <div class="space-y-4">
      <!-- Modo mano alzada -->
      <div class="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
        <div class="flex items-center space-x-3">
          <svg class="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
          <span class="text-sm text-gray-700">Modo mano alzada</span>
        </div>
        <button
          @click="toggleFreehand"
          :class="[
            'px-3 py-1 rounded-full text-sm transition-colors',
            freehandMode
              ? 'bg-green-100 text-green-700'
              : 'bg-gray-200 text-gray-600'
          ]"
        >
          {{ freehandMode ? 'Activado' : 'Desactivado' }}
        </button>
      </div>

      <!-- Botones de acción -->
      <div class="grid grid-cols-2 gap-3">
        <button
          @click="drawing ? stopDrawing() : startDrawing()"
          :class="[
            'px-4 py-2 rounded-lg text-white transition-colors flex items-center justify-center space-x-2',
            drawing
              ? 'bg-yellow-500 hover:bg-yellow-600'
              : 'bg-green-500 hover:bg-green-600'
          ]"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path v-if="!drawing" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M6 18L18 6M6 6l12 12" />
          </svg>
          <span>{{ drawing ? 'Detener' : 'Dibujar' }}</span>
        </button>

        <button
          @click="clearDrawings"
          class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg
                 transition-colors flex items-center justify-center space-x-2"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          <span>Limpiar</span>
        </button>
      </div>
    </div>

    <!-- Personalización de estilo -->
    <div class="p-4 bg-gray-50 rounded-xl space-y-4">
      <h4 class="text-sm font-medium text-gray-700 mb-3">Estilo del dibujo</h4>
      
      <div v-if="drawType === 'Point'" class="space-y-3">
        <div>
          <label class="block text-xs text-gray-500 mb-1">Color del punto</label>
          <input
            type="color"
            v-model="drawStyles.Point.color"
            class="w-full h-8 rounded cursor-pointer"
            @change="updateStyle"
          />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">
            Tamaño: {{ drawStyles.Point.size }}px
          </label>
          <input
            type="range"
            v-model.number="drawStyles.Point.size"
            min="4"
            max="20"
            class="w-full"
            @change="updateStyle"
          />
        </div>
      </div>

      <div v-else class="space-y-3">
        <div>
          <label class="block text-xs text-gray-500 mb-1">Color de línea</label>
          <input
            type="color"
            v-model="drawStyles[drawType].color"
            class="w-full h-8 rounded cursor-pointer"
            @change="updateStyle"
          />
        </div>
        <div v-if="drawType !== 'LineString'">
          <label class="block text-xs text-gray-500 mb-1">Color de relleno</label>
          <input
            type="color"
            v-model="drawStyles[drawType].fill"
            class="w-full h-8 rounded cursor-pointer"
            @change="updateStyle"
          />
        </div>
        <div v-if="drawType === 'LineString'">
          <label class="block text-xs text-gray-500 mb-1">
            Grosor de línea: {{ drawStyles.LineString.width }}px
          </label>
          <input
            type="range"
            v-model.number="drawStyles.LineString.width"
            min="1"
            max="10"
            class="w-full"
            @change="updateStyle"
          />
        </div>
      </div>
    </div>
    
    <!-- Instrucciones de uso -->
    <div class="p-3 bg-blue-50 rounded-lg text-xs text-blue-700">
      <p class="font-medium mb-2">Instrucciones:</p>
      <ul class="list-disc pl-5 space-y-1">
        <li>Seleccione un tipo de geometría</li>
        <li>Haga clic en "Dibujar" para iniciar</li>
        <li>Haga clic en el mapa para dibujar</li>
        <li>Para polígonos, haga doble clic para terminar</li>
        <li>Puede modificar las formas después de dibujarlas</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
input[type="color"] {
  -webkit-appearance: none;
  padding: 0;
  border: none;
  border-radius: 4px;
  overflow: hidden;
}

input[type="color"]::-webkit-color-swatch-wrapper {
  padding: 0;
}

input[type="color"]::-webkit-color-swatch {
  border: none;
}

input[type="range"] {
  -webkit-appearance: none;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  outline: none;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #10B981;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
}

input[type="range"]::-webkit-slider-thumb:hover {
  transform: scale(1.1);
}

/* Animación de entrada */
.draw-tools {
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
