<script setup>
import { ref, onMounted } from 'vue';

const props = defineProps({
  map: {
    type: Object,
    required: true
  }
});

const baseLayerVisible = ref(true);
const baseLayerOpacity = ref(100);
const osmLayer = ref(null);

onMounted(() => {
  // Obtener la capa base OSM del mapa
  osmLayer.value = props.map.getLayers().getArray().find(layer => 
    layer.get('name') === 'OpenStreetMap'
  );
  
  if (osmLayer.value) {
    // Sincronizar estado inicial
    baseLayerVisible.value = osmLayer.value.getVisible();
    baseLayerOpacity.value = Math.round(osmLayer.value.getOpacity() * 100);
  }
});

const toggleBaseLayer = () => {
  if (osmLayer.value) {
    baseLayerVisible.value = !baseLayerVisible.value;
    osmLayer.value.setVisible(baseLayerVisible.value);
  }
};

const updateOpacity = (event) => {
  const opacity = parseInt(event.target.value) / 100;
  if (osmLayer.value) {
    osmLayer.value.setOpacity(opacity);
    baseLayerOpacity.value = event.target.value;
  }
};
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- Título de la sección -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-medium text-gray-900">Capas base</h3>
    </div>

    <!-- Tarjeta de OpenStreetMap -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
      <div class="space-y-4">
        <!-- Cabecera con título y switch -->
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <!-- Alternativa usando una URL externa -->
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Openstreetmap_logo.svg/256px-Openstreetmap_logo.svg.png" alt="OSM" class="w-8 h-8 rounded"/>
            <div>
              <h4 class="text-sm font-medium text-gray-900">OpenStreetMap</h4>
              <p class="text-xs text-gray-500">Mapa base estándar</p>
            </div>
          </div>

          <!-- Switch mejorado -->
          <label class="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox"
              :checked="baseLayerVisible"
              @change="toggleBaseLayer"
              class="sr-only peer"
            />
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
          </label>
        </div>

        <!-- Control de opacidad mejorado -->
        <div v-if="baseLayerVisible" class="space-y-2">
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

    <!-- Información adicional -->
    <div class="bg-blue-50 rounded-lg p-3 text-xs text-blue-700">
      <p class="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Ajusta la visibilidad y opacidad del mapa base
      </p>
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
