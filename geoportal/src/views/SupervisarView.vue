<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Estado para controlar animaciones y UI
const mapInitialized = ref(false);
const loading = ref(true);
const showMessage = ref(false);
const userLocation = ref(null);
const errorMessage = ref('');

// Simulación de geolocalización para la demo
const simulateGeolocation = () => {
  loading.value = true;
  setTimeout(() => {
    // Coordenadas simuladas en algún lugar de México (CDMX)
    userLocation.value = {
      latitude: 19.4326,
      longitude: -99.1332,
      accuracy: 15,
      timestamp: new Date().toISOString()
    };
    loading.value = false;
    showMessage.value = true;
  }, 2000);
};

// Funcionalidad para volver al inicio
const goToHome = () => {
  router.push('/');
};

// Inicializar la vista cuando se monte el componente
onMounted(() => {
  // Placeholder para la inicialización del mapa
  setTimeout(() => {
    mapInitialized.value = true;
    loading.value = false;
  }, 1500);
});

onBeforeUnmount(() => {
  // Limpiar recursos si es necesario
});
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- Encabezado -->
    <header class="bg-white shadow-md">
      <div class="container mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button @click="goToHome" class="flex items-center text-green-600 hover:text-green-700 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span class="ml-2 font-medium">Volver al inicio</span>
          </button>
          <h1 class="text-xl sm:text-2xl font-bold text-gray-800">Supervisión de Personal</h1>
        </div>
      </div>
    </header>

    <!-- Contenido principal -->
    <main class="flex-1 container mx-auto px-4 py-8">
      <div class="max-w-6xl mx-auto">
        <!-- Panel de información -->
        <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 shadow-md mb-8">
          <h2 class="text-xl font-semibold text-green-800 mb-3">
            Módulo de Supervisión
          </h2>
          <p class="text-gray-600">
            Esta funcionalidad permitirá monitorear la ubicación del personal en campo. Los trabajadores podrán confirmar su ubicación a través de una aplicación PWA.
          </p>
          <div class="mt-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-yellow-700">
                  Módulo en desarrollo. Próximamente disponible.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Demo visual de la funcionalidad -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Panel del mapa -->
          <div class="lg:col-span-2 bg-white rounded-xl shadow-md overflow-hidden h-96 relative">
            <!-- Overlay de carga -->
            <div v-if="loading" class="absolute inset-0 bg-white bg-opacity-80 flex items-center justify-center z-10">
              <div class="w-16 h-16 border-4 border-t-green-500 border-green-200 rounded-full animate-spin"></div>
            </div>

            <!-- Mapa placeholder -->
            <div class="h-full w-full bg-gray-200 flex items-center justify-center">
              <div v-if="!mapInitialized" class="text-gray-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-20 w-20 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
                <p>Cargando mapa...</p>
              </div>
              <div v-else class="w-full h-full p-4 flex items-center justify-center">
                <p class="text-center text-lg text-gray-500">
                  Aquí se mostrará el mapa con la ubicación del personal.
                  <br>
                  <span class="text-sm">(Funcionalidad en desarrollo)</span>
                </p>
              </div>
            </div>
          </div>

          <!-- Panel de información y controles -->
          <div class="bg-white rounded-xl shadow-md p-6 flex flex-col">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">Ubicación de Personal</h3>

            <!-- Controles de demostración -->
            <button 
              @click="simulateGeolocation" 
              class="mb-4 py-3 px-4 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors flex items-center justify-center space-x-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>Simular Ubicación</span>
            </button>

            <!-- Información de ubicación -->
            <div v-if="userLocation" class="mt-4 bg-green-50 rounded-lg p-4 transition-opacity duration-500" :class="{ 'opacity-100': showMessage, 'opacity-0': !showMessage }">
              <h4 class="font-medium text-green-800 mb-2">Ubicación detectada:</h4>
              <div class="space-y-2 text-sm">
                <p class="flex justify-between">
                  <span class="text-gray-600">Latitud:</span>
                  <span class="font-medium">{{ userLocation.latitude }}</span>
                </p>
                <p class="flex justify-between">
                  <span class="text-gray-600">Longitud:</span>
                  <span class="font-medium">{{ userLocation.longitude }}</span>
                </p>
                <p class="flex justify-between">
                  <span class="text-gray-600">Precisión:</span>
                  <span class="font-medium">{{ userLocation.accuracy }} metros</span>
                </p>
                <p class="flex justify-between">
                  <span class="text-gray-600">Fecha y hora:</span>
                  <span class="font-medium">{{ new Date(userLocation.timestamp).toLocaleString() }}</span>
                </p>
              </div>
              <div class="mt-4 pt-4 border-t border-green-100">
                <p class="text-green-700 text-sm">
                  Ubicación compartida exitosamente.
                </p>
              </div>
            </div>

            <div v-if="errorMessage" class="mt-4 bg-red-50 rounded-lg p-4">
              <p class="text-red-700">{{ errorMessage }}</p>
            </div>

            <!-- Espacio de relleno con información -->
            <div class="mt-auto pt-6 text-sm text-gray-500 border-t border-gray-100">
              <p class="mb-2"><strong>¿Cómo funciona?</strong></p>
              <p>Los trabajadores pueden confirmar su ubicación usando la aplicación móvil. Los supervisores podrán ver la última ubicación reportada y recibir notificaciones.</p>
            </div>
          </div>
        </div>

        <!-- Tabla de registros de ejemplo -->
        <div class="mt-8 bg-white rounded-xl shadow-md overflow-hidden">
          <div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <h3 class="text-lg font-semibold text-gray-800">Historial de ubicaciones</h3>
          </div>
          <div class="p-6">
            <p class="text-gray-500 italic text-center">
              El historial de ubicaciones se mostrará aquí cuando la funcionalidad esté disponible.
            </p>
          </div>
        </div>
      </div>
    </main>

    <!-- Pie de página simple -->
    <footer class="bg-white border-t border-gray-200 py-4">
      <div class="container mx-auto px-4 text-center">
        <p class="text-gray-600 text-xs">© 2025 Geoportal Sembrando Datos. Todos los derechos reservados.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Animaciones y estilos específicos para esta vista */
.fade-enter-active, 
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter-from, 
.fade-leave-to {
  opacity: 0;
}
</style>
