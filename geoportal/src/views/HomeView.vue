<script setup>
import { ref, onMounted } from 'vue';
import Dashboard from '../components/Dashboard.vue';
import ToastNotification from '../components/notifications/ToastNotification.vue';

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

// Estado para notificaciones
const notification = ref({
  show: false,
  message: '',
  type: 'success'
});

// Función para mostrar notificaciones
const showNotification = (message, type = 'success') => {
  notification.value = {
    show: true,
    message,
    type
  };
  setTimeout(() => {
    notification.value.show = false;
  }, 3000);
};

// Función para eliminar mapa con confirmación
const confirmDelete = (map) => {
  if (confirm('¿Estás seguro de que deseas eliminar este mapa?')) {
    deleteMap(map.id);
    showNotification('Mapa eliminado correctamente');
  }
};

// Función para renombrar mapa
const renameMap = (map) => {
  const newName = prompt('Ingrese el nuevo nombre para el mapa:', map.name);
  if (newName && newName.trim()) {
    const maps = savedMaps.value;
    const mapIndex = maps.findIndex(m => m.id === map.id);
    if (mapIndex !== -1) {
      maps[mapIndex].name = newName.trim();
      localStorage.setItem('savedMaps', JSON.stringify(maps));
      showNotification('Mapa renombrado correctamente');
    }
  }
};

onMounted(() => {
  loadSavedMaps();
});
</script>

<template>
  <main class="min-h-screen w-full bg-gradient-to-br from-green-50 to-teal-50">
    <!-- Página de bienvenida -->
    <div v-if="showWelcome" class="min-h-screen w-full flex flex-col">
      <!-- Header con logo y título -->
      <header class="relative py-16 bg-green-800/10 backdrop-blur-sm">
        <div class="container mx-auto px-4 text-center relative z-10">
          <!-- Contenedor del logo y título -->
          <div class="flex flex-col items-center justify-center space-y-6">
            <img 
              src="@/components/images/logotipo.png" 
              alt="Logotipo SembrandoDatos" 
              class="h-32 md:h-40 w-auto object-contain animate-fade-in"
            />
            <div>
              <h1 class="text-4xl md:text-6xl font-serif font-bold text-green-800 mb-4 animate-fade-in">
                Geoportal SembrandoDatos
              </h1>
              <p class="text-lg md:text-xl text-green-600 max-w-2xl mx-auto">
                Visualización y análisis territorial
              </p>
            </div>
          </div>
        </div>
      </header>

      <!-- Contenido principal centrado -->
      <div class="flex-1 container mx-auto px-4 py-12">
        <!-- Grid de mapas guardados -->
        <div class="max-w-7xl mx-auto">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
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
              class="bg-white rounded-xl shadow-lg overflow-hidden group hover:shadow-xl transition-all duration-300"
            >
              <div class="relative">
                <div class="h-48 bg-green-100 flex items-center justify-center">
                  <img 
                    :src="map.thumbnail || '/default-map.png'" 
                    :alt="map.name" 
                    class="w-full h-full object-cover"
                  >
                </div>
                <div class="absolute inset-0 bg-black bg-opacity-40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center space-x-3">
                  <button 
                    @click="openMap(map)"
                    class="bg-green-500 text-white px-3 py-2 rounded-lg hover:bg-green-600 transition-colors"
                    title="Abrir mapa"
                  >
                    🗺️ Abrir
                  </button>
                  <button 
                    @click="renameMap(map)"
                    class="bg-blue-500 text-white p-2 rounded-lg hover:bg-blue-600 transition-colors"
                    title="Renombrar mapa"
                  >
                    ✏️
                  </button>
                  <button 
                    @click="confirmDelete(map)"
                    class="bg-red-500 text-white p-2 rounded-lg hover:bg-red-600 transition-colors"
                    title="Eliminar mapa"
                  >
                    🗑️
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
      </div>
    </div>

    <!-- Componente del mapa -->
    <Dashboard v-else @save-success="showNotification('Mapa guardado correctamente')" />

    <!-- Componente de notificaciones -->
    <ToastNotification v-bind="notification" />
  </main>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.8s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Añadir efecto de hover suave al logo */
img {
  transition: transform 0.3s ease;
}

img:hover {
  transform: scale(1.05);
}
</style>
