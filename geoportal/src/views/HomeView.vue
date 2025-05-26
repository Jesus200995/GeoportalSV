<script setup>
import { ref, onMounted } from 'vue';
import Dashboard from '../components/Dashboard.vue';
import ToastNotification from '../components/notifications/ToastNotification.vue';
import UserProfile from '../components/UserProfile.vue';
import StatsDashboard from '../components/StatsDashboard.vue';

const showWelcome = ref(true);
const isTransitioning = ref(false);
const transitionTarget = ref(''); // Para determinar a qué componente hacer la transición

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
  transitionTarget.value = 'map';
  
  // Esperar a que termine la animación antes de mostrar el dashboard
  setTimeout(() => {
    showWelcome.value = false;
    
    // Reiniciar el estado de transición después de un breve retraso
    setTimeout(() => {
      isTransitioning.value = false;
    }, 100);
  }, 1200); // Duración total de la animación
};

// Función para abrir el dashboard de estadísticas con animación
const openStats = () => {
  isTransitioning.value = true;
  transitionTarget.value = 'stats';
  
  // Esperar a que termine la animación antes de mostrar el dashboard de estadísticas
  setTimeout(() => {
    showWelcome.value = false;
    
    // Reiniciar el estado de transición después de un breve retraso
    setTimeout(() => {
      isTransitioning.value = false;
    }, 100);
  }, 1200);
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
      <!-- Eliminar la clase que crea el efecto de onda con colores verde y morado -->
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
              <!-- Aumentamos el tamaño del logo -->
              <img src="@/components/images/logotipo.png" alt="Logo" class="h-16 w-16 animate-logo-pulse" />
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
            <!-- Contenedor para los círculos en fila - Posición ajustada más arriba -->
            <div class="flex flex-col items-center justify-center mt-[-40px]">
              <!-- Texto mejorado con mejor tipografía y animación más elegante -->
              <h2 class="text-3xl font-semibold text-white mb-10 tracking-wider elegant-text">
                <span class="elegant-animation" data-text="Seleccione una herramienta">Seleccione una herramienta</span>
              </h2>
              
              <div class="flex flex-wrap justify-center gap-8 sm:gap-12 md:gap-16">
                <!-- Círculo 1: Visor de Mapa -->
                <div class="relative group mb-8">
                  <!-- Eliminada la animación del círculo exterior con gradiente -->
                  
                  <!-- Botón del visor con nueva clase para efecto de clic -->
                  <button 
                    @click="openVisor"
                    class="visor-button relative bg-black/20 backdrop-blur-lg hover:bg-black/30 text-white rounded-full p-10 w-72 h-72 flex flex-col items-center justify-center transform transition-all duration-500 hover:scale-105 group-hover:shadow-xl shadow-green-500/20 border border-white/20 overflow-hidden"
                  >
                    <!-- Icono de globo terráqueo/mapa -->
                    <div class="relative z-10 mb-2 group-hover:scale-110 transition-transform duration-700">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-24 w-24 text-white drop-shadow-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M20.893 13.393l-1.135-1.135a2.252 2.252 0 01-.421-.585l-1.08-2.16a.414.414 0 00-.663-.107.827.827 0 01-.812.21l-1.273-.363a.89.89 0 00-.738 1.595l.587.39c.59.395.674 1.23.172 1.732l-.2.2c-.212.212-.33.498-.33.796v.41c0 .409-.11.809-.32 1.158l-1.315 2.191a2.11 2.11 0 01-1.81 1.025 1.055 1.055 0 01-1.055-1.055v-1.172c0-.92-.56-1.747-1.414-2.089l-.655-.261a2.25 2.25 0 01-1.383-2.46l.007-.042a2.25 2.25 0 01.29-.787l.09-.15a2.25 2.25 0 012.37-1.048l1.178.236a1.125 1.125 0 001.302-.795l.208-.73a1.125 1.125 0 00-.578-1.315l-.665-.332-.091.091a2.25 2.25 0 01-1.591.659h-.18c-.249 0-.487.1-.662.274a.931.931 0 01-1.458-1.137l1.411-2.353a2.25 2.25 0 00.286-.76m11.928 9.869A9 9 0 008.965 3.525m11.928 9.868A9 9 0 118.965 3.525" />
                      </svg>
                    </div>
                    
                    <!-- Texto VISOR mejorado -->
                    <div class="relative z-10 flex flex-col items-center">
                      <span class="text-4xl font-bold tracking-widest text-white drop-shadow-lg mb-3">VISOR</span>
                      <span class="text-xs text-green-300 font-medium tracking-wide drop-shadow-md">EXPLORAR TERRITORIOS</span>
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
                  
                  <!-- Etiqueta descriptiva -->
                  <div class="mt-6 text-center">
                    <h3 class="text-xl font-semibold text-white">Visor de Mapas</h3>
                    <p class="text-gray-300 mt-2 max-w-xs">Explore datos geográficos con nuestro visor interactivo</p>
                  </div>
                </div>
                
                <!-- Círculo 2: Estadísticas y Análisis -->
                <div class="relative group mb-8">
                  <!-- Eliminada la animación del círculo exterior con gradiente -->
                  
                  <!-- Botón de estadísticas -->
                  <button 
                    @click="openStats"
                    class="stats-button relative bg-black/20 backdrop-blur-lg hover:bg-black/30 text-white rounded-full p-10 w-72 h-72 flex flex-col items-center justify-center transform transition-all duration-500 hover:scale-105 group-hover:shadow-xl shadow-blue-500/20 border border-white/20 overflow-hidden"
                  >
                    <!-- Icono de estadísticas -->
                    <div class="relative z-10 mb-2 group-hover:scale-110 transition-transform duration-700">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-24 w-24 text-white drop-shadow-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
                      </svg>
                    </div>
                    
                    <!-- Texto DATOS mejorado -->
                    <div class="relative z-10 flex flex-col items-center">
                      <span class="text-4xl font-bold tracking-widest text-white drop-shadow-lg mb-3">DATOS</span>
                      <span class="text-xs text-blue-300 font-medium tracking-wide drop-shadow-md">ANÁLISIS Y ESTADÍSTICAS</span>
                    </div>
                    
                    <!-- Efecto de brillo al hacer hover mejorado -->
                    <div class="absolute inset-0 rounded-full overflow-hidden">
                      <div class="absolute inset-0 bg-gradient-to-br from-blue-300/30 to-transparent opacity-0 group-hover:opacity-60 transition-opacity duration-700"></div>
                    </div>
                    
                    <!-- Anillo exterior adicional -->
                    <div class="absolute -inset-1.5 rounded-full border border-blue-400/30 opacity-50 group-hover:opacity-80 transition-opacity"></div>
                    
                    <!-- Indicador pulsante para llamar la atención -->
                    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full rounded-full border-4 border-blue-400/50 animate-ping-slow opacity-0 group-hover:opacity-100"></div>
                  </button>
                  
                  <!-- Etiqueta descriptiva -->
                  <div class="mt-6 text-center">
                    <h3 class="text-xl font-semibold text-white">Análisis y Estadísticas</h3>
                    <p class="text-gray-300 mt-2 max-w-xs">Visualice datos agrícolas con gráficas y análisis interactivos</p>
                  </div>
                </div>
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

    <!-- Renderizado condicional basado en el tipo de componente a mostrar -->
    <Dashboard v-if="!showWelcome && transitionTarget === 'map'" 
               @show-welcome="showWelcome = true"
               @save-success="showNotification('Mapa guardado exitosamente', 'success')"
               @logout="showWelcome = true" />
    
    <StatsDashboard v-if="!showWelcome && transitionTarget === 'stats'"
                   @show-welcome="showWelcome = true" />
    
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

/* Nuevos estilos para las etiquetas elegantes */
.text-sm.text-green-300,
.text-sm.text-blue-300 {
  letter-spacing: 0.05em;
  backdrop-filter: blur(2px);
  transition: all 0.3s ease;
}

.visor-button:hover .text-sm.text-green-300,
.stats-button:hover .text-sm.text-blue-300 {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

/* Estilos refinados para el plasma del visor */
.plasma-bg {
  background: linear-gradient(125deg, 
    rgba(6, 78, 59, 0.9), 
    rgba(6, 95, 70, 0.9), 
    rgba(4, 120, 87, 0.9), 
    rgba(5, 150, 105, 0.9)
  );
  background-size: 300% 300%;
  animation: plasma-shift 15s ease infinite;
  border-radius: 50%;
  z-index: -1;
}

.plasma-layer1 {
  background: radial-gradient(circle at 30% 50%, rgba(5, 150, 105, 0.6) 0%, transparent 60%),
              radial-gradient(circle at 80% 80%, rgba(6, 182, 212, 0.6) 0%, transparent 60%);
  background-size: 200% 200%;
  mix-blend-mode: soft-light;
  animation: plasma-pulse 10s ease infinite alternate;
  opacity: 0.8;
  border-radius: 50%;
}

.plasma-layer2 {
  background: radial-gradient(circle at 70% 30%, rgba(16, 185, 129, 0.6) 0%, transparent 60%),
              radial-gradient(circle at 20% 70%, rgba(14, 165, 233, 0.6) 0%, transparent 60%);
  background-size: 150% 150%;
  mix-blend-mode: screen;
  animation: plasma-move 12s ease-in-out infinite alternate-reverse;
  opacity: 0.7;
  border-radius: 50%;
}

/* Estilos refinados para el plasma de estadísticas */
.stats-plasma-bg {
  background: linear-gradient(125deg, 
    rgba(30, 64, 175, 0.9), 
    rgba(59, 130, 246, 0.9), 
    rgba(96, 165, 250, 0.9), 
    rgba(147, 197, 253, 0.9)
  );
  background-size: 300% 300%;
  animation: plasma-shift 15s ease infinite;
  border-radius: 50%;
}

.stats-plasma-layer1 {
  background: radial-gradient(circle at 30% 50%, rgba(59, 130, 246, 0.6) 0%, transparent 60%),
              radial-gradient(circle at 80% 80%, rgba(99, 102, 241, 0.6) 0%, transparent 60%);
  background-size: 200% 200%;
  mix-blend-mode: soft-light;
  animation: plasma-pulse 10s ease infinite alternate;
  opacity: 0.8;
  border-radius: 50%;
}

.stats-plasma-layer2 {
  background: radial-gradient(circle at 70% 30%, rgba(37, 99, 235, 0.6) 0%, transparent 60%),
              radial-gradient(circle at 20% 70%, rgba(79, 70, 229, 0.6) 0%, transparent 60%);
  background-size: 150% 150%;
  mix-blend-mode: screen;
  animation: plasma-move 12s ease-in-out infinite alternate-reverse;
  opacity: 0.7;
  border-radius: 50%;
}

/* Animaciones refinadas */
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
    transform: scale(1.05);
  }
}

@keyframes plasma-move {
  0% {
    background-position: 0% 0%;
    transform: rotate(0deg);
  }
  100% {
    background-position: 100% 100%;
    transform: rotate(8deg);
  }
}

/* Animación en dirección contraria más suave */
.animate-spin-reverse {
  animation: spin-reverse 20s linear infinite;
}

@keyframes spin-reverse {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(-360deg);
  }
}

/* Ajustes para la transición */
.transition-wave.stats-transition {
  background: radial-gradient(
    circle,
    rgba(255, 255, 255, 0.95) 0%,
    rgba(219, 234, 254, 0.9) 30%,
    rgba(147, 197, 253, 0.85) 70%,
    rgba(37, 99, 235, 0.8) 100%
  );
}

.transition-wave.map-transition {
  background: radial-gradient(
    circle,
    rgba(255, 255, 255, 0.95) 0%,
    rgba(209, 250, 229, 0.9) 30%,
    rgba(147, 197, 253, 0.85) 70%,
    rgba(37, 99, 235, 0.8) 100%
  );
}

/* Responsive para pantallas pequeñas */
@media (max-width: 640px) {
  .flex.flex-wrap.justify-center {
    flex-direction: column;
    align-items: center;
  }
}

/* Eliminar las animaciones de plasma verde y morada de la transición-wave */
.transition-wave {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.95);
  transform: scale(0);
  transition: transform 1.2s cubic-bezier(0.645, 0.045, 0.355, 1);
}

/* Simplificar las transiciones eliminando los gradientes animados */
.transition-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  pointer-events: none;
  overflow: hidden;
}

/* Estilos para la transición simple sin el efecto de plasma */
.transition-wave {
  transform-origin: center;
}

/* Estilos básicos para mantener la funcionalidad de transición */
.map-transition {
  transform: scale(20);
  background-color: rgba(230, 250, 240, 0.95);
}

.stats-transition {
  transform: scale(20);
  background-color: rgba(240, 240, 255, 0.95);
}

/* Animación pulsante para el logo */
@keyframes logo-pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.animate-logo-pulse {
  animation: logo-pulse 3s ease-in-out infinite;
}

/* Estilos para el texto elegante */
.elegant-text {
  font-family: 'Poppins', sans-serif;
  letter-spacing: 1px;
  text-shadow: 0 2px 10px rgba(255, 255, 255, 0.3);
  position: relative;
  padding-bottom: 6px;
  color: white;
}

.elegant-text::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent);
  transform: translateX(-50%);
}

/* Nueva animación con efecto de brillo verde claro horizontal */
.elegant-animation {
  position: relative;
  display: inline-block;
}

.elegant-animation::before {
  content: attr(data-text);
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0) 0%,
    rgba(144, 238, 144, 0.3) 25%,
    rgba(152, 251, 152, 0.7) 50%,
    rgba(144, 238, 144, 0.3) 75%,
    rgba(255, 255, 255, 0) 100%
  );
  background-size: 200% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shineGreen 6s linear infinite;
  pointer-events: none;
}

@keyframes shineGreen {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
</style>
