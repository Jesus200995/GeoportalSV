<script setup>
import { ref, watch } from 'vue';
import { Group as LayerGroup } from 'ol/layer';

const props = defineProps(['map', 'layers']);
const layerOpacity = ref({});
const groupedLayers = ref({});

// Organizar capas por grupos
const organizeLayers = () => {
  const groups = {};
  props.map.getLayers().forEach(layer => {
    const group = layer.get('group') || 'default';
    if (!groups[group]) groups[group] = [];
    groups[group].push(layer);
  });
  groupedLayers.value = groups;
};

// Controlar visibilidad
const toggleLayerVisibility = (layer) => {
  layer.setVisible(!layer.getVisible());
};

// Controlar opacidad
const updateOpacity = (layer, event) => {
  const opacity = parseFloat(event.target.value);
  layer.setOpacity(opacity);
  layerOpacity.value[layer.get('name')] = opacity;
};

// Mover capa arriba/abajo
const moveLayer = (layer, direction) => {
  const layers = props.map.getLayers();
  const index = layers.getArray().indexOf(layer);
  const newIndex = direction === 'up' ? index + 1 : index - 1;
  
  if (newIndex >= 0 && newIndex < layers.getLength()) {
    const layerArray = layers.getArray();
    layers.removeAt(index);
    layers.insertAt(newIndex, layer);
  }
};

// Inicializar cuando el componente se monta
onMounted(() => {
  organizeLayers();
  // Inicializar opacidades
  props.map.getLayers().forEach(layer => {
    layerOpacity.value[layer.get('name')] = layer.getOpacity();
  });
});
</script>

<template>
  <div class="layers-tool p-4 bg-white rounded-lg">
    <div v-for="(layers, groupName) in groupedLayers" :key="groupName" class="mb-6">
      <h3 class="text-sm font-medium text-gray-700 mb-3">{{ groupName }}</h3>
      
      <div class="space-y-3">
        <div v-for="layer in layers" 
             :key="layer.get('name')"
             class="bg-gray-50 rounded-lg p-3 hover:bg-gray-100 transition-colors">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <input 
                type="checkbox"
                :checked="layer.getVisible()"
                @change="toggleLayerVisibility(layer)"
                class="rounded text-green-500 focus:ring-green-400"
              />
              <span class="text-sm">{{ layer.get('name') }}</span>
            </div>
            
            <div class="flex items-center space-x-2">
              <button @click="moveLayer(layer, 'up')"
                      class="p-1 text-gray-500 hover:text-green-600">
                ↑
              </button>
              <button @click="moveLayer(layer, 'down')"
                      class="p-1 text-gray-500 hover:text-green-600">
                ↓
              </button>
            </div>
          </div>
          
          <!-- Control de opacidad -->
          <div v-if="layer.getVisible()" class="mt-2">
            <label class="text-xs text-gray-500 block mb-1">
              Opacidad: {{ Math.round(layerOpacity[layer.get('name')] * 100) }}%
            </label>
            <input 
              type="range"
              min="0"
              max="1"
              step="0.1"
              :value="layerOpacity[layer.get('name')]"
              @input="updateOpacity(layer, $event)"
              class="w-full"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Estilos para el control deslizante de opacidad */
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
</style>
