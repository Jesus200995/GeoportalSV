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

// Agregar estado para el carrusel
const backgroundImages = [
  'https://images.unsplash.com/photo-1501854140801-50d01698950b?q=80&w=1920&auto=format&fit=crop', // Bosque verde
  'https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1920&auto=format&fit=crop', // Campo de cultivo
  'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=1920&auto=format&fit=crop'  // Bosque con luz
];

const currentImageIndex = ref(0);

// Función para cambiar la imagen
const changeBackgroundImage = () => {
  currentImageIndex.value = (currentImageIndex.value + 1) % backgroundImages.length;
};

// Iniciar el carrusel cuando el componente se monta
onMounted(() => {
  loadSavedMaps();
  // Cambiar imagen cada 5 segundos
  setInterval(changeBackgroundImage, 5000);
});
</script>

<template>
  <main class="min-h-screen w-full bg-gradient-to-br from-green-50 to-teal-50">
    <!-- Página de bienvenida -->
    <div v-if="showWelcome" class="min-h-screen w-full flex flex-col py-8">
      <!-- Header con carrusel de imágenes -->
      <header class="relative py-16 overflow-hidden">
        <!-- Carrusel de imágenes de fondo -->
        <div class="absolute inset-0">
          <template v-for="(image, index) in backgroundImages" :key="index">
            <div
              class="absolute inset-0 bg-cover bg-center bg-no-repeat transition-opacity duration-1000"
              :style="{
                backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.3)), url('${image}')`,
                opacity: currentImageIndex === index ? 1 : 0
              }"
            ></div>
          </template>
        </div>

        <!-- Contenido del header -->
        <div class="container mx-auto px-4 text-center relative z-10">
          <!-- Contenedor del logo y título -->
          <div class="flex flex-col items-center justify-center space-y-4">
            <img 
              src="@/components/images/logotipo.png" 
              alt="Logotipo SembrandoDatos" 
              class="h-20 md:h-24 w-auto object-contain animate-fade-in drop-shadow-lg"
            />
            <div>
              <h1 class="text-2xl md:text-4xl font-serif font-bold text-white mb-2 animate-fade-in drop-shadow-lg">
                Geoportal SembrandoDatos
              </h1>
              <p class="text-base md:text-lg text-gray-100 max-w-xl mx-auto drop-shadow">
                Visualización y análisis territorial
              </p>
            </div>
          </div>
        </div>
      </header>

      <!-- Contenido principal centrado -->
      <div class="flex-1 container mx-auto px-4 py-8">
        <!-- Grid de mapas guardados -->
        <div class="max-w-6xl mx-auto">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <!-- Tarjeta para nuevo mapa -->
            <div 
              @click="showWelcome = false"
              class="bg-white rounded-lg shadow-md p-4 cursor-pointer transform transition-all duration-300 hover:scale-105 hover:shadow-lg"
            >
              <div class="bg-green-50 rounded-lg p-6 mb-3 flex items-center justify-center">
                <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                </svg>
              </div>
              <h3 class="text-base font-semibold text-green-800 mb-1">Nuevo Mapa</h3>
              <p class="text-sm text-green-600">Crear una nueva visualización</p>
            </div>

            <!-- Mapas guardados -->
            <div 
              v-for="map in savedMaps" 
              :key="map.id"
              class="bg-white rounded-lg shadow-md overflow-hidden group hover:shadow-lg transition-all duration-300"
            >
              <div class="relative">
                <div class="h-32 bg-green-50 flex items-center justify-center">
                  <img 
                    :src="map.thumbnail || '/default-map.png'" 
                    :alt="map.name" 
                    class="w-full h-full object-cover"
                  >
                </div>
                <div class="absolute inset-0 bg-black bg-opacity-40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center space-x-2">
                  <button 
                    @click="openMap(map)"
                    class="bg-green-500 text-white px-2 py-1 rounded-md hover:bg-green-600 transition-colors text-sm"
                    title="Abrir mapa"
                  >
                    🗺️ Abrir
                  </button>
                  <button 
                    @click="renameMap(map)"
                    class="bg-blue-500 text-white p-1 rounded-md hover:bg-blue-600 transition-colors"
                    title="Renombrar mapa"
                  >
                    ✏️
                  </button>
                  <button 
                    @click="confirmDelete(map)"
                    class="bg-red-500 text-white p-1 rounded-md hover:bg-red-600 transition-colors"
                    title="Eliminar mapa"
                  >
                    🗑️
                  </button>
                </div>
              </div>
              <div class="p-3">
                <h3 class="text-base font-semibold text-green-800 mb-1">{{ map.name }}</h3>
                <p class="text-xs text-gray-600">Última modificación: {{ map.lastModified }}</p>
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

/* Añadir estilo para mejorar la transición de la imagen de fondo */
header {
  min-height: 280px;
  transition: all 0.3s ease;
  background-attachment: fixed;
}

/* Mejorar legibilidad del texto sobre la imagen */
.drop-shadow-lg {
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.5));
}

/* Añadir estilos para el carrusel */
.bg-cover {
  background-size: cover;
}

/* Mejorar animación de las imágenes */
.transition-opacity {
  transition: opacity 1s ease-in-out;
}
</style>
