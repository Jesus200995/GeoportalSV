<script setup>
import { ref, onMounted } from 'vue';
import Dashboard from '../components/Dashboard.vue';
import ToastNotification from '../components/notifications/ToastNotification.vue';
import UserProfile from '../components/UserProfile.vue';

const showWelcome = ref(true);

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

// Agregar estados para el carrusel de fondo
const backgroundImages = [
  'https://images.unsplash.com/photo-1501854140801-50d01698950b?q=80&w=1920&auto=format&fit=crop', // Bosque verde
  'https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1920&auto=format&fit=crop', // Campo de cultivo
  'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=1920&auto=format&fit=crop'  // Bosque con luz
];

const currentImageIndex = ref(0);

// Función para cambiar la imagen de fondo
const changeBackgroundImage = () => {
  currentImageIndex.value = (currentImageIndex.value + 1) % backgroundImages.length;
};

// Función para abrir el visor de mapa
const openVisor = () => {
  showWelcome.value = false;
};

// Iniciar el carrusel de fondo
onMounted(() => {
  setInterval(changeBackgroundImage, 5000);
});
</script>

<template>
  <div>
    <!-- Vista de bienvenida -->
    <div v-if="showWelcome" class="min-h-screen flex flex-col">
      <!-- Fondo con imágenes en carrusel -->
      <div class="fixed inset-0 bg-black">
        <transition name="fade" mode="out-in">
          <div 
            :key="currentImageIndex"
            :style="{
              backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.7)), url(${backgroundImages[currentImageIndex]})`
            }"
            class="absolute inset-0 bg-cover bg-center transition-opacity duration-1000"
          ></div>
        </transition>
        <!-- Superposición con patrón de puntos -->
        <div class="absolute inset-0 bg-pattern opacity-20"></div>
      </div>

      <!-- Contenido -->
      <div class="relative z-10 flex-1 flex flex-col">
        <!-- Encabezado -->
        <header class="py-6 px-4">
          <div class="container mx-auto flex justify-between items-center">
            <div class="flex items-center space-x-3">
              <img src="@/components/images/logotipo.png" alt="Logo" class="h-12 w-12" />
              <h1 class="text-white text-2xl md:text-3xl lg:text-4xl font-serif font-bold">
                Geoportal <span class="text-green-400">Sembrando Datos</span>
              </h1>
            </div>
            
            <!-- Componente de perfil de usuario -->
            <UserProfile />
          </div>
        </header>

        <!-- Contenido principal centrado -->
        <main class="flex-1 flex items-center justify-center px-4 py-8">
          <div class="max-w-7xl mx-auto text-center">
            <!-- Círculo grande para el visor -->
            <div class="flex flex-col items-center justify-center mt-12">
              <div class="relative group">
                <!-- Círculo exterior con animación de luz verde -->
                <div class="absolute -inset-1 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full blur-lg opacity-70 group-hover:opacity-90 animate-spin-slow"></div>
                
                <!-- Botón del visor -->
                <button 
                  @click="openVisor"
                  class="relative bg-white bg-opacity-10 backdrop-blur-sm hover:bg-opacity-20 text-white rounded-full p-8 w-64 h-64 flex flex-col items-center justify-center transform transition-all duration-500 hover:scale-105 group-hover:shadow-xl shadow-green-500/20 border border-white/10"
                >
                  <img src="@/components/images/vizual2.png" alt="Mapa" class="w-32 h-32 object-cover rounded-full mb-4 shadow-lg" />
                  <span class="text-2xl font-bold tracking-wide">VISOR</span>
                  <span class="text-sm text-green-300 mt-2">Haga clic para explorar</span>
                  
                  <!-- Efecto de brillo al hacer hover -->
                  <div class="absolute inset-0 rounded-full overflow-hidden">
                    <div class="absolute inset-0 bg-gradient-to-br from-green-300/30 to-transparent opacity-0 group-hover:opacity-60 transition-opacity duration-700"></div>
                  </div>
                </button>
              </div>
              
              <!-- Texto descriptivo debajo del botón -->
              <div class="mt-12 max-w-2xl text-white">
                <h2 class="text-2xl mb-4 font-medium text-green-300">Visualizador Geográfico Integral</h2>
                <p class="text-lg text-gray-300">
                  Explore datos territoriales, agrícolas y ambientales a través de nuestro visor interactivo. 
                  Descubra información detallada sobre cultivos, condiciones del suelo, y más.
                </p>
              </div>
            </div>
          </div>
        </main>

        <!-- Pie de página -->
        <footer class="py-6 px-4 text-center text-white/70 text-sm">
          <div class="container mx-auto">
            <p>© 2023 Geoportal Sembrando Datos. Todos los derechos reservados.</p>
          </div>
        </footer>
      </div>
    </div>

    <!-- Vista del dashboard (mapa) -->
    <Dashboard v-else 
               @show-welcome="showWelcome = true"
               @save-success="showNotification('Mapa guardado exitosamente', 'success')"
               @logout="showWelcome = true" />
    
    <!-- Notificación Toast -->
    <ToastNotification 
      :show="notification.show"
      :message="notification.message"
      :type="notification.type"
    />
  </div>
</template>

<style scoped>
.bg-pattern {
  background-image: url("data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.1' fill-rule='evenodd'%3E%3Ccircle cx='3' cy='3' r='1'/%3E%3Ccircle cx='13' cy='13' r='1'/%3E%3C/g%3E%3C/svg%3E");
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 1s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Animación de rotación lenta para el borde iluminado */
@keyframes spin-slow {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.animate-spin-slow {
  animation: spin-slow 10s linear infinite;
}

/* Estilo para partículas flotantes */
.particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation: moveUp 15s linear infinite;
}

@keyframes moveUp {
  0% {
    transform: translateY(100vh) translateX(0);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-20vh) translateX(20px);
    opacity: 0;
  }
}

/* Añadir posiciones aleatorias para las partículas */
.particle:nth-child(1) { left: 10%; animation-delay: 0s; }
.particle:nth-child(2) { left: 20%; animation-delay: 2s; }
.particle:nth-child(3) { left: 30%; animation-delay: 4s; }
.particle:nth-child(4) { left: 40%; animation-delay: 6s; }
.particle:nth-child(5) { left: 50%; animation-delay: 8s; }
.particle:nth-child(6) { left: 60%; animation-delay: 10s; }
.particle:nth-child(7) { left: 70%; animation-delay: 12s; }
.particle:nth-child(8) { left: 80%; animation-delay: 14s; }
.particle:nth-child(9) { left: 90%; animation-delay: 16s; }
</style>
