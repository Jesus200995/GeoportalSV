<script setup>
import { ref, onMounted } from 'vue';
import Dashboard from '../components/Dashboard.vue';
import ToastNotification from '../components/notifications/ToastNotification.vue';
import UserProfile from '../components/UserProfile.vue';

const showWelcome = ref(true);
const isTransitioning = ref(false);

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

// Función para abrir el visor de mapa con animación de transición
const openVisor = () => {
  isTransitioning.value = true;
  
  // Esperar a que termine la animación antes de mostrar el dashboard
  setTimeout(() => {
    showWelcome.value = false;
    
    // Reiniciar el estado de transición después de un breve retraso
    setTimeout(() => {
      isTransitioning.value = false;
    }, 100);
  }, 1200); // Duración total de la animación
};

// Iniciar el carrusel de fondo
onMounted(() => {
  setInterval(changeBackgroundImage, 5000);
});
</script>

<template>
  <div>
    <!-- Animación de transición al hacer clic -->
    <div v-if="isTransitioning" class="transition-overlay">
      <div class="transition-wave"></div>
    </div>
    
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
            <!-- Círculo grande para el visor - REDISEÑADO -->
            <div class="flex flex-col items-center justify-center mt-12">
              <div class="relative group">
                <!-- Círculo exterior con animación de luz verde - Mejorado con blur más intenso -->
                <div class="absolute -inset-3 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full blur-xl opacity-70 group-hover:opacity-90 animate-spin-slow"></div>
                
                <!-- Botón del visor con nueva clase para efecto de clic -->
                <button 
                  @click="openVisor"
                  class="visor-button relative bg-black/40 backdrop-blur-lg hover:bg-black/50 text-white rounded-full p-10 w-80 h-80 flex flex-col items-center justify-center transform transition-all duration-500 hover:scale-105 group-hover:shadow-xl shadow-green-500/20 border border-white/20 overflow-hidden"
                >
                  <!-- Fondo animado tipo plasma -->
                  <div class="absolute inset-0 w-full h-full overflow-hidden">
                    <!-- Capas de gradientes animados para efecto plasma -->
                    <div class="plasma-bg absolute inset-0 opacity-90"></div>
                    <div class="plasma-layer1 absolute inset-0"></div>
                    <div class="plasma-layer2 absolute inset-0"></div>
                    
                    <!-- Overlay con gradiente para mejorar la legibilidad del texto -->
                    <div class="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-black/50"></div>
                  </div>
                  
                  <!-- Icono de globo terráqueo/mapa -->
                  <div class="relative z-10 mb-1 group-hover:scale-110 transition-transform duration-700">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-24 w-24 text-white drop-shadow-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M20.893 13.393l-1.135-1.135a2.252 2.252 0 01-.421-.585l-1.08-2.16a.414.414 0 00-.663-.107.827.827 0 01-.812.21l-1.273-.363a.89.89 0 00-.738 1.595l.587.39c.59.395.674 1.23.172 1.732l-.2.2c-.212.212-.33.498-.33.796v.41c0 .409-.11.809-.32 1.158l-1.315 2.191a2.11 2.11 0 01-1.81 1.025 1.055 1.055 0 01-1.055-1.055v-1.172c0-.92-.56-1.747-1.414-2.089l-.655-.261a2.25 2.25 0 01-1.383-2.46l.007-.042a2.25 2.25 0 01.29-.787l.09-.15a2.25 2.25 0 012.37-1.048l1.178.236a1.125 1.125 0 001.302-.795l.208-.73a1.125 1.125 0 00-.578-1.315l-.665-.332-.091.091a2.25 2.25 0 01-1.591.659h-.18c-.249 0-.487.1-.662.274a.931.931 0 01-1.458-1.137l1.411-2.353a2.25 2.25 0 00.286-.76m11.928 9.869A9 9 0 008.965 3.525m11.928 9.868A9 9 0 118.965 3.525" />
                    </svg>
                  </div>
                  
                  <!-- Texto VISOR mejorado -->
                  <div class="relative z-10 flex flex-col items-center">
                    <span class="text-4xl font-bold tracking-widest text-white drop-shadow-lg">VISOR</span>
                    <span class="text-sm text-green-300 mt-2 font-medium bg-black/30 px-4 py-1 rounded-full">EXPLORAR TERRITORIOS</span>
                  </div>
                  
                  <!-- Efecto de brillo al hacer hover mejorado -->
                  <div class="absolute inset-0 rounded-full overflow-hidden">
                    <div class="absolute inset-0 bg-gradient-to-br from-green-300/30 to-transparent opacity-0 group-hover:opacity-60 transition-opacity duration-700"></div>
                  </div>
                  
                  <!-- Anillo exterior adicional -->
                  <div class="absolute -inset-1.5 rounded-full border border-green-400/30 opacity-50 group-hover:opacity-80 transition-opacity"></div>
                  
                  <!-- Indicador pulsante para llamar la atención -->
                  <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full rounded-full border-4 border-green-400/50 animate-ping-slow opacity-0 group-hover:opacity-100"></div>
                </button>
              </div>
              
              <!-- Texto descriptivo debajo del botón -->
              <div class="mt-16 max-w-2xl text-white">
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
  animation: spin-slow 20s linear infinite;
}

/* Animación pulsante más lenta para el indicador */
@keyframes ping-slow {
  0% {
    transform: translate(-50%, -50%) scale(0.9);
    opacity: 0.6;
  }
  50% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.3;
  }
  100% {
    transform: translate(-50%, -50%) scale(0.9);
    opacity: 0.6;
  }
}

.animate-ping-slow {
  animation: ping-slow 3s ease-in-out infinite;
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

/* Nuevos estilos para la animación de plasma */
.plasma-bg {
  background: linear-gradient(125deg, #064e3b, #065f46, #047857, #059669);
  background-size: 400% 400%;
  animation: plasma-shift 15s ease infinite;
}

.plasma-layer1 {
  background: radial-gradient(circle at 30% 50%, rgba(5, 150, 105, 0.8) 0%, rgba(5, 150, 105, 0) 50%),
              radial-gradient(circle at 80% 80%, rgba(6, 182, 212, 0.8) 0%, rgba(6, 182, 212, 0) 50%);
  background-size: 200% 200%;
  mix-blend-mode: screen;
  animation: plasma-pulse 10s ease infinite alternate;
  opacity: 0.7;
}

.plasma-layer2 {
  background: radial-gradient(circle at 70% 30%, rgba(16, 185, 129, 0.8) 0%, rgba(16, 185, 129, 0) 50%),
              radial-gradient(circle at 20% 70%, rgba(14, 165, 233, 0.8) 0%, rgba(14, 165, 233, 0) 50%);
  background-size: 150% 150%;
  mix-blend-mode: screen;
  animation: plasma-move 8s ease-in-out infinite alternate-reverse;
  opacity: 0.7;
}

@keyframes plasma-shift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

@keyframes plasma-pulse {
  0% {
    background-position: 0% 0%;
    transform: scale(1);
  }
  100% {
    background-position: 100% 100%;
    transform: scale(1.2);
  }
}

@keyframes plasma-move {
  0% {
    background-position: 0% 0%;
    transform: rotate(0deg);
  }
  100% {
    background-position: 100% 100%;
    transform: rotate(10deg);
  }
}

/* Animación de transición al hacer clic en el visor */
.transition-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: transparent;
  z-index: 100;
  pointer-events: none;
  overflow: hidden;
}

.transition-wave {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100vh;
  height: 100vh;
  border-radius: 50%;
  transform: translate(-50%, -50%) scale(0);
  background: radial-gradient(
    circle,
    rgba(255, 255, 255, 0.95) 0%,
    rgba(209, 250, 229, 0.9) 30%,
    rgba(147, 197, 253, 0.85) 70%,
    rgba(37, 99, 235, 0.8) 100%
  );
  animation: wave-expand 1.2s ease-out forwards;
  opacity: 0.98;
  box-shadow: 0 0 50px rgba(255, 255, 255, 0.8);
}

@keyframes wave-expand {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 0.4;
  }
  40% {
    opacity: 0.95;
  }
  100% {
    transform: translate(-50%, -50%) scale(4);
    opacity: 1;
  }
}

/* Animación para el botón al hacer clic */
.visor-button:active::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 10px;
  height: 10px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  transform: translate(-50%, -50%) scale(1);
  opacity: 0.8;
  animation: button-ripple 0.6s ease-out;
  z-index: 5;
}

@keyframes button-ripple {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.8;
  }
  100% {
    transform: translate(-50%, -50%) scale(50);
    opacity: 0;
  }
}
</style>
