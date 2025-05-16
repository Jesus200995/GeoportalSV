<script setup>
import { ref, onMounted } from 'vue';
import Dashboard from '../components/Dashboard.vue';

const showWelcome = ref(true);
const savedMaps = ref([]);

// Cargar mapas guardados
const loadSavedMaps = () => {
  const maps = localStorage.getItem('savedMaps');
  if (maps) {
    savedMaps.value = JSON.parse(maps);
  }
};

// Abrir mapa
const openMap = (map) => {
  showWelcome.value = false;
  // Implementar lógica para cargar el mapa seleccionado
};

// Eliminar mapa
const deleteMap = (mapId) => {
  savedMaps.value = savedMaps.value.filter(m => m.id !== mapId);
  localStorage.setItem('savedMaps', JSON.stringify(savedMaps.value));
};

onMounted(() => {
  loadSavedMaps();
});
</script>

<template>
  <main class="min-h-screen bg-gradient-to-br from-green-50 to-teal-50">
    <!-- Página de bienvenida -->
    <div v-if="showWelcome" class="p-6 md:p-8 lg:p-12">
      <header class="text-center mb-12">
        <h1 class="text-4xl md:text-5xl font-serif font-bold text-green-800 mb-4">
          Geoportal SembrandoDatos
        </h1>
        <p class="text-green-600 text-lg">Visualización y análisis territorial</p>
      </header>

      <!-- Grid de mapas guardados -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <!-- Tarjeta para nuevo mapa -->
        <div 
          @click="showWelcome = false"
          class="bg-white rounded-xl shadow-lg p-6 cursor-pointer transform transition-all duration-300 hover:scale-105 hover:shadow-xl"
        >
          <div class="bg-green-100 rounded-lg p-8 mb-4 flex items-center justify-center">
            <svg class="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-green-800 mb-2">Nuevo Mapa</h3>
          <p class="text-green-600 text-sm">Crear una nueva visualización</p>
        </div>

        <!-- Mapas guardados -->
        <div 
          v-for="map in savedMaps" 
          :key="map.id"
          class="bg-white rounded-xl shadow-lg overflow-hidden group"
        >
          <div class="relative">
            <img :src="map.thumbnail" :alt="map.name" class="w-full h-48 object-cover">
            <div class="absolute inset-0 bg-black bg-opacity-40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center space-x-4">
              <button 
                @click="openMap(map)"
                class="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors"
              >
                Abrir
              </button>
              <button 
                @click="deleteMap(map.id)"
                class="bg-red-500 text-white p-2 rounded-lg hover:bg-red-600 transition-colors"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="p-4">
            <h3 class="text-lg font-semibold text-green-800 mb-2">{{ map.name }}</h3>
            <p class="text-sm text-gray-600">Última modificación: {{ map.lastModified }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Componente del mapa -->
    <Dashboard v-else />
  </main>
</template>
