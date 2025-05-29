<script setup>
import { ref, onMounted } from 'vue';
import TileLayer from 'ol/layer/Tile';
import XYZ from 'ol/source/XYZ';

const props = defineProps({
  map: {
    type: Object,
    required: true
  }
});

const osmVisible = ref(true);
const satelliteVisible = ref(false);
const baseLayerOpacity = ref(100);
const osmLayer = ref(null);
const satelliteLayer = ref(null);

onMounted(() => {
  // Obtener la capa OSM
  osmLayer.value = props.map.getLayers().getArray().find(layer => 
    layer.get('name') === 'OpenStreetMap'
  );

  // Crear y añadir capa satelital si no existe
  if (!props.map.getLayers().getArray().find(layer => layer.get('name') === 'Satellite')) {
    satelliteLayer.value = new TileLayer({
      source: new XYZ({
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        maxZoom: 19
      }),
      visible: false,
      properties: {
        name: 'Satellite'
      },
      zIndex: 0
    });
    props.map.addLayer(satelliteLayer.value);
  } else {
    satelliteLayer.value = props.map.getLayers().getArray().find(layer => 
      layer.get('name') === 'Satellite'
    );
  }

  // Sincronizar estados iniciales
  if (osmLayer.value) {
    osmVisible.value = osmLayer.value.getVisible();
    baseLayerOpacity.value = Math.round(osmLayer.value.getOpacity() * 100);
  }
  if (satelliteLayer.value) {
    satelliteVisible.value = satelliteLayer.value.getVisible();
  }
});

const toggleOSM = () => {
  if (osmLayer.value) {
    osmVisible.value = !osmVisible.value;
    osmLayer.value.setVisible(osmVisible.value);
    if (osmVisible.value && satelliteLayer.value) {
      satelliteVisible.value = false;
      satelliteLayer.value.setVisible(false);
    }
  }
};

const toggleSatellite = () => {
  if (satelliteLayer.value) {
    satelliteVisible.value = !satelliteVisible.value;
    satelliteLayer.value.setVisible(satelliteVisible.value);
    if (satelliteVisible.value && osmLayer.value) {
      osmVisible.value = false;
      osmLayer.value.setVisible(false);
    }
  }
};

const updateOpacity = (event) => {
  const opacity = parseInt(event.target.value) / 100;
  const activeLayer = osmVisible.value ? osmLayer.value : satelliteLayer.value;
  if (activeLayer) {
    activeLayer.setOpacity(opacity);
    baseLayerOpacity.value = event.target.value;
  }
};
</script>

<template>
  <div class="p-4 space-y-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-medium text-gray-900">Capas base</h3>
    </div>

    <!-- Tarjetas de mapas base -->
    <div class="space-y-4">
      <!-- OpenStreetMap -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              <div>
                <h4 class="text-sm font-medium text-gray-900">OpenStreetMap</h4>
                <p class="text-xs text-gray-500">Mapa base estándar</p>
              </div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox"
                :checked="osmVisible"
                @change="toggleOSM"
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
            </label>
          </div>
        </div>
      </div>

      <!-- Mapa Satelital -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
              </svg>
              <div>
                <h4 class="text-sm font-medium text-gray-900">Satelital</h4>
                <p class="text-xs text-gray-500">Vista satelital ESRI</p>
              </div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox"
                :checked="satelliteVisible"
                @change="toggleSatellite"
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
            </label>
          </div>
        </div>
      </div>

      <!-- Control de opacidad -->
      <div v-if="osmVisible || satelliteVisible" class="bg-gray-50 rounded-lg p-4">
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <label class="text-xs text-gray-500">Opacidad</label>
            <span class="text-xs font-medium text-gray-700">{{ baseLayerOpacity }}%</span>
          </div>
          <input 
            type="range"
            min="0"
            max="100"
            :value="baseLayerOpacity"
            @input="updateOpacity"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-green-600"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Estilos para el slider de opacidad */
input[type="range"] {
  -webkit-appearance: none;
  height: 4px;
  background: #E5E7EB;
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
  box-shadow: 0 0 0 8px rgba(16, 185, 129, 0.1);
}

input[type="range"]::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #10B981;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
}

input[type="range"]::-moz-range-thumb:hover {
  transform: scale(1.1);
}

/* Estilos para el toggle switch */
.toggle-label {
  position: relative;
  width: 2.5rem;
  transition: background-color 0.3s ease;
}

.toggle-label::after {
  content: '';
  position: absolute;
  top: 0.25rem;
  left: 0.25rem;
  width: 1rem;
  height: 1rem;
  background-color: white;
  border-radius: 50%;
  transition: transform 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.toggle-label.active {
  background-color: #10B981;
}

.toggle-label.active::after {
  transform: translateX(1.5rem);
}
</style>
