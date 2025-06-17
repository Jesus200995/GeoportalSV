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

// Usar solo la primera imagen de fondo
const backgroundImage = 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop'; // Campo de maíz dorado

// Nueva función simplificada para precargar la imagen
const preloadImage = () => {
  const img = new Image();
  img.src = backgroundImage;
};

// Función para abrir el visor de mapa con animación de transición más rápida
const openVisor = () => {
  isTransitioning.value = true;
  transitionTarget.value = 'map';
  
  // Reducir tiempo de espera para transición más rápida
  setTimeout(() => {
    showWelcome.value = false;
    
    // Reducir tiempo de reinicio de estado de transición
    setTimeout(() => {
      isTransitioning.value = false;
    }, 50);
  }, 300); // Reducido de 1200ms a 300ms para una transición más rápida
};

// Función para abrir el dashboard de estadísticas con animación más rápida
const openStats = () => {
  isTransitioning.value = true;
  transitionTarget.value = 'stats';
  
  // Reducir tiempo de espera para transición más rápida
  setTimeout(() => {
    showWelcome.value = false;
    
    // Reducir tiempo de reinicio de estado de transición
    setTimeout(() => {
      isTransitioning.value = false;
    }, 50);
  }, 300); // Reducido de 1200ms a 300ms para una transición más rápida
};

// Función para ir a la pantalla de Supervisar (nuevo)
const openSupervisar = () => {
  // Activar la transición con flor girando
  isTransitioning.value = true;
  transitionTarget.value = 'supervisar';
  
  // Mostrar la animación de carga por 3 segundos antes de redirigir
  setTimeout(() => {
    // Redirigir a la URL externa
    window.location.href = 'https://adminpwa.sembrandodatos.com/dashboard';
  }, 3000);
};

// Estado para el efecto de humo
const smokeParticles = ref([]);
const isSmokeActive = ref(false);

// Función para generar partículas de humo
const generateSmokeParticles = () => {
  // Limpiar partículas anteriores
  smokeParticles.value = [];
  
  // Generar nuevas partículas
  for (let i = 0; i < 20; i++) {
    smokeParticles.value.push({
      id: i,
      size: Math.random() * 30 + 10,
      posX: Math.random() * 80 - 40,
      posY: Math.random() * 80 - 40,
      opacity: Math.random() * 0.6 + 0.2,
      delay: Math.random() * 2,
      duration: Math.random() * 3 + 2
    });
  }
};

// Función para activar/desactivar el efecto de humo
const toggleSmokeEffect = () => {
  if (!isSmokeActive.value) {
    generateSmokeParticles();
    isSmokeActive.value = true;
    
    // Desactivar automáticamente después de unos segundos
    setTimeout(() => {
      isSmokeActive.value = false;
    }, 3000);
  }
};

// Iniciar con imagen estática
onMounted(() => {
  // Precargar imagen para evitar problemas de carga
  preloadImage();
  
  // Ya no necesitamos el intervalo de cambio de imagen
  // setInterval(changeBackgroundImage, 5000); // Removido
  
  // Generar partículas de humo iniciales
  generateSmokeParticles();
});
</script>

<template>
  <div>    <!-- Animación de transición al hacer clic -->
    <div v-if="isTransitioning" class="transition-overlay">      <!-- Transición especial para supervisar con flor girando -->
      <div v-if="transitionTarget === 'supervisar'" class="flower-loading-container">
        <div class="flower-animation">
          <!-- Pétalos externos -->
          <div class="flower-layer outer-petals">
            <div class="petal-group">
              <div class="petal large-petal" v-for="n in 8" :key="'outer-' + n" :style="{ '--rotation': (n-1) * 45 + 'deg' }"></div>
            </div>
          </div>
          
          <!-- Pétalos internos -->
          <div class="flower-layer inner-petals">
            <div class="petal-group">
              <div class="petal small-petal" v-for="n in 6" :key="'inner-' + n" :style="{ '--rotation': (n-1) * 60 + 22.5 + 'deg' }"></div>
            </div>
          </div>
          
          <!-- Centro de la flor -->
          <div class="flower-center">
            <div class="center-core"></div>
            <div class="center-ring"></div>
          </div>
          
          <!-- Hojas rotatorias -->
          <div class="flower-leaves">
            <div class="leaf leaf-1"></div>
            <div class="leaf leaf-2"></div>
            <div class="leaf leaf-3"></div>
            <div class="leaf leaf-4"></div>
          </div>
        </div>
        
        <div class="loading-text">
          <p>Conectando con el sistema de supervisión...</p>
          <div class="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
      
      <!-- Transiciones para otros botones -->
      <div v-else class="transition-wave"></div>
    </div>
    
    <!-- Vista de bienvenida -->
    <div v-if="showWelcome" class="min-h-screen flex flex-col">
      <!-- Fondo con imagen estática -->
      <div class="fixed inset-0 bg-black fancy-fade-container">
        <div 
          :style="{
            backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.6)), url(${backgroundImage})`
          }"
          class="absolute inset-0 bg-cover bg-center"
        ></div>
        
        <!-- Superposición con patrón de puntos -->
        <div class="absolute inset-0 bg-pattern opacity-20"></div>
        
        <!-- Partículas mágicas en la transición -->
        <div class="magic-particles"></div>
        
        <!-- Efecto verde durante transiciones -->
        <div class="green-mist"></div>
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
              
              <!-- Contenedor horizontal para los círculos - Botones aún más grandes en línea -->
              <div class="flex flex-row flex-wrap justify-center gap-4 sm:gap-6 md:gap-8">
                <!-- Círculo 1: Visor de Mapa -->
                <div class="relative group mb-6">
                  <!-- Botón más grande -->
                  <button 
                    @click="openVisor"
                    class="visor-button relative bg-black/20 backdrop-blur-lg hover:bg-black/30 text-white rounded-full p-8 w-72 h-72 flex flex-col items-center justify-center transform transition-all duration-500 hover:scale-105 group-hover:shadow-xl shadow-green-500/20 border border-white/20 overflow-hidden"
                  >
                    <!-- Icono más pequeño -->
                    <div class="relative z-10 mb-2 group-hover:scale-110 transition-transform duration-700">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-white drop-shadow-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M20.893 13.393l-1.135-1.135a2.252 2.252 0 01-.421-.585l-1.08-2.16a.414.414 0 00-.663-.107.827.827 0 01-.812.21l-1.273-.363a.89.89 0 00-.738 1.595l.587.39c.59.395.674 1.23.172 1.732l-.2.2c-.212.212-.33.498-.33.796v.41c0 .409-.11.809-.32 1.158l-1.315 2.191a2.11 2.11 0 01-1.81 1.025 1.055 1.055 0 01-1.055-1.055v-1.172c0-.92-.56-1.747-1.414-2.089l-.655-.261a2.25 2.25 0 01-1.383-2.46l.007-.042a2.25 2.25 0 01.29-.787l.09-.15a2.25 2.25 0 012.37-1.048l1.178.236a1.125 1.125 0 001.302-.795l.208-.73a1.125 1.125 0 00-.578-1.315l-.665-.332-.091.091a2.25 2.25 0 01-1.591.659h-.18c-.249 0-.487.1-.662.274a.931.931 0 01-1.458-1.137l1.411-2.353a2.25 2.25 0 00.286-.76m11.928 9.869A9 9 0 008.965 3.525m11.928 9.868A9 9 0 118.965 3.525" />
                      </svg>
                    </div>
                    
                    <!-- Texto VISOR reducido -->
                    <div class="relative z-10 flex flex-col items-center">
                      <span class="text-2xl font-bold tracking-widest text-white drop-shadow-lg mb-2">VISOR</span>
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
                  
                  <!-- Etiqueta descriptiva más compacta -->
                  <div class="mt-3 text-center">
                    <h3 class="text-lg font-semibold text-white">Visor de Mapas</h3>
                    <p class="text-xs text-gray-300 mt-1 max-w-xs">Explore datos geográficos interactivos</p>
                  </div>
                </div>
                
                <!-- Botón de SUBIR CAPAS (MOVIDO para estar después de VISOR) -->
                <div class="relative group mb-6">
                  <!-- Botón más grande -->
                  <router-link to="/upload-layer" class="upload-button relative bg-black/20 backdrop-blur-lg hover:bg-black/30 text-white rounded-full p-8 w-72 h-72 flex flex-col items-center justify-center transform transition-all duration-500 hover:scale-105 group-hover:shadow-xl shadow-emerald-500/20 border border-white/20 overflow-hidden">
                    <!-- Icono más pequeño -->
                    <div class="relative z-10 mb-2 group-hover:scale-110 transition-transform duration-700">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-white drop-shadow-lg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5V21h18v-4.5M12 3v15m0 0l-3-3m3 3l3-3" />
                      </svg>
                    </div>
                    
                    <!-- Texto SUBIR CAPAS reducido -->
                    <div class="relative z-10 flex flex-col items-center">
                      <span class="text-2xl font-bold tracking-widest text-white drop-shadow-lg mb-2">CAPAS</span>
                      <span class="text-xs text-emerald-300 font-medium tracking-wide drop-shadow-md">CARGAR SHAPEFILES</span>
                    </div>
                    
                    <!-- Efecto de brillo al hacer hover mejorado -->
                    <div class="absolute inset-0 rounded-full overflow-hidden">
                      <div class="absolute inset-0 bg-gradient-to-br from-emerald-300/30 to-transparent opacity-0 group-hover:opacity-60 transition-opacity duration-700"></div>
                    </div>
                    
                    <!-- Anillo exterior adicional -->
                    <div class="absolute -inset-1.5 rounded-full border border-emerald-400/30 opacity-50 group-hover:opacity-80 transition-opacity"></div>
                    
                    <!-- Indicador pulsante para llamar la atención -->
                    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full rounded-full border-4 border-emerald-400/50 animate-ping-slow opacity-0 group-hover:opacity-100"></div>
                  </router-link>
                  
                  <!-- Etiqueta descriptiva más compacta -->
                  <div class="mt-3 text-center">
                    <h3 class="text-lg font-semibold text-white">Subir Capas</h3>
                    <p class="text-xs text-gray-300 mt-1 max-w-xs">Cargue sus archivos shapefile</p>
                  </div>
                </div>
                
                <!-- Círculo 2: Estadísticas y Análisis (MOVIDO para estar después de CAPAS) -->
                <div class="relative group mb-6">
                  <!-- Botón más grande -->
                  <button 
                    @click="openStats"
                    class="stats-button relative bg-black/20 backdrop-blur-lg hover:bg-black/30 text-white rounded-full p-8 w-72 h-72 flex flex-col items-center justify-center transform transition-all duration-500 hover:scale-105 group-hover:shadow-xl shadow-blue-500/20 border border-white/20 overflow-hidden"
                  >
                    <!-- Icono más pequeño -->
                    <div class="relative z-10 mb-2 group-hover:scale-110 transition-transform duration-700">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-white drop-shadow-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
                      </svg>
                    </div>
                    
                    <!-- Texto DATOS reducido -->
                    <div class="relative z-10 flex flex-col items-center">
                      <span class="text-2xl font-bold tracking-widest text-white drop-shadow-lg mb-2">DATOS</span>
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
                  
                  <!-- Etiqueta descriptiva más compacta -->
                  <div class="mt-3 text-center">
                    <h3 class="text-lg font-semibold text-white">Análisis y Estadísticas</h3>
                    <p class="text-xs text-gray-300 mt-1 max-w-xs">Visualice datos con gráficos</p>
                  </div>
                </div>
                
                <!-- NUEVO: Círculo de Supervisar con efecto de humo -->
                <div class="relative group mb-6">
                  <!-- Botón más grande con color rojo -->
                  <button 
                    @click="openSupervisar"
                    @mouseenter="toggleSmokeEffect"
                    class="supervisar-button relative bg-black/20 backdrop-blur-lg hover:bg-black/30 text-white rounded-full p-8 w-72 h-72 flex flex-col items-center justify-center transform transition-all duration-500 hover:scale-105 group-hover:shadow-xl shadow-red-500/20 border border-white/20 overflow-hidden"
                  >
                    <!-- Contenedor para el efecto de humo -->
                    <div class="absolute inset-0 smoke-container overflow-hidden rounded-full">
                      <!-- Partículas de humo que se desvanecen -->
                      <div 
                        v-for="particle in smokeParticles" 
                        :key="particle.id"
                        :class="{ 'animate-smoke': isSmokeActive }"
                        class="absolute rounded-full bg-white/30 backdrop-blur-sm"
                        :style="{
                          width: `${particle.size}px`,
                          height: `${particle.size}px`,
                          left: `calc(50% + ${particle.posX}px)`,
                          top: `calc(50% + ${particle.posY}px)`,
                          opacity: particle.opacity,
                          animationDelay: `${particle.delay}s`,
                          animationDuration: `${particle.duration}s`,
                          filter: 'blur(8px)'
                        }"
                      ></div>
                    </div>
                    
                    <!-- Icono más pequeño -->
                    <div class="relative z-10 mb-2 group-hover:scale-110 transition-transform duration-700">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-white drop-shadow-lg opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
                      </svg>
                    </div>
                    
                    <!-- Texto SUPERVISAR con color rojo -->
                    <div class="relative z-10 flex flex-col items-center">
                      <span class="text-xl font-bold tracking-widest text-white drop-shadow-lg mb-2 opacity-70">SUPERVISAR</span>
                      <span class="text-xs text-red-300 font-medium tracking-wide drop-shadow-md">MONITOREAR PERSONAL</span>
                    </div>
                    
                    <!-- Efecto de brillo al hacer hover en rojo -->
                    <div class="absolute inset-0 rounded-full overflow-hidden">
                      <div class="absolute inset-0 bg-gradient-to-br from-red-300/30 to-transparent opacity-0 group-hover:opacity-60 transition-opacity duration-700"></div>
                    </div>
                    
                    <!-- Anillo exterior adicional en rojo -->
                    <div class="absolute -inset-1.5 rounded-full border border-red-400/30 opacity-50 group-hover:opacity-80 transition-opacity"></div>
                    
                    <!-- Indicador pulsante para llamar la atención en rojo -->
                    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full rounded-full border-4 border-red-400/50 animate-ping-slow opacity-0 group-hover:opacity-100"></div>
                  </button>
                    <!-- Etiqueta descriptiva más compacta -->
                  <div class="mt-3 text-center">
                    <h3 class="text-lg font-semibold text-white">Supervisar Personal</h3>
                    <p class="text-xs text-gray-300 mt-1 max-w-xs">Monitoree ubicaciones en campo</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>

        <!-- Pie de página -->
        <footer class="py-6 px-4 text-center text-white/70 text-sm">
          <div class="container mx-auto">
            <p>© 2025 Geoportal Sembrando Datos. Todos los derechos reservados.</p>
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

/* Eliminar las animaciones de plasma verde y morado de la transición-wave */
.transition-wave {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.95);
  transform: scale(0);
  transition: transform 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
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
  transition: transform 0.3s ease-out;
}

.stats-transition {
  transform: scale(20);
  background-color: rgba(240, 240, 255, 0.95);
  transition: transform 0.3s ease-out;
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

/* Nuevas animaciones para el efecto de humo */
@keyframes smoke-animation {
  0% {
    opacity: 0.7;
    transform: scale(0.8) translate(0px, 0px);
  }
  25% {
    opacity: 0.5;
  }
  50% {
    opacity: 0.3;
    transform: scale(1.2) translate(var(--smoke-x, 10px), var(--smoke-y, -20px));
  }
  75% {
    opacity: 0.2;
  }
  100% {
    opacity: 0;
    transform: scale(2) translate(var(--smoke-x, 15px), var(--smoke-y, -40px));
  }
}

.animate-smoke {
  animation: smoke-animation 3s ease-out forwards;
  --smoke-x: calc(20px - 40px * var(--random, 0.5));
  --smoke-y: calc(-30px * var(--random, 0.7));
}

/* Estilizado del nuevo botón de supervisar */
.supervisar-button {
  position: relative;
  background-color: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(8px);
}

.supervisar-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 9999px;
  background: radial-gradient(
    circle at center,
    rgba(239, 68, 68, 0.2),
    rgba(185, 28, 28, 0.1),
    transparent
  );
  opacity: 0;
  transition: opacity 0.5s ease;
}

.supervisar-button:hover::before {
  opacity: 1;
}

/* Contenedor de la animación de humo */
.smoke-container {
  z-index: 5;
  pointer-events: none;
}

/* Animar solo cuando se activa el efecto */
.supervisar-button:hover .smoke-container {
  animation: pulse-glow 2s infinite alternate;
}

@keyframes pulse-glow {
  0% {
    filter: brightness(1) blur(0px);
  }
  100% {
    filter: brightness(1.1) blur(1px);
  }
}

/* Animación de desvanecido mejorada con efectos verdes */
.fancy-fade-enter-active {
  animation: fadeInWithGreenGlow 1.8s ease-out;
}

.fancy-fade-leave-active {
  animation: fadeOutWithGreenMist 1.8s ease-in;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

@keyframes fadeInWithGreenGlow {
  0% {
    opacity: 0;
    transform: scale(1.05);
    filter: brightness(1.3) blur(8px) hue-rotate(60deg);
  }
  30% {
    filter: brightness(1.2) blur(5px) hue-rotate(40deg);
  }
  70% {
    filter: brightness(1.1) blur(2px) hue-rotate(20deg);
  }
  100% {
    opacity: 1;
    transform: scale(1);
    filter: brightness(1) blur(0) hue-rotate(0deg);
  }
}

@keyframes fadeOutWithGreenMist {
  0% {
    opacity: 1;
    filter: brightness(1) blur(0);
  }
  30% {
    opacity: 0.8;
    filter: brightness(1.2) blur(2px) hue-rotate(20deg);
  }
  70% {
    opacity: 0.4;
    filter: brightness(1.5) blur(5px) hue-rotate(40deg);
  }
  100% {
    opacity: 0;
    filter: brightness(1.8) blur(10px) hue-rotate(60deg);
  }
}

/* Efecto de humo verde adicional para las transiciones */
.green-mist {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 2;
  opacity: 0;
  background: radial-gradient(
    circle at center,
    rgba(72, 187, 120, 0.2) 0%,
    rgba(72, 187, 120, 0.1) 40%,
    transparent 70%
  );
  pointer-events: none;
  transition: opacity 0.3s ease;
}

.fancy-fade-container.transition-active .green-mist {
  animation: green-mist-pulse 1.8s ease-in-out;
}

@keyframes green-mist-pulse {
  0% {
    opacity: 0;
    transform: scale(0.95);
  }
  30% {
    opacity: 0.3;
    transform: scale(1.05);
  }
  70% {
    opacity: 0.2;
    transform: scale(1.02);
  }
  100% {
    opacity: 0;
    transform: scale(1);
  }
}

/* Mejorar el efecto de partículas mágicas con toques verdes */
.magic-particles::before {
  content: '';
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  background-image: radial-gradient(
    circle at center,
    rgba(72, 187, 120, 0.15) 0%,
    rgba(72, 187, 120, 0) 70%
  );
  background-size: 100% 100%;
  animation: green-particle-glow 8s ease-in-out infinite;
  opacity: 0;
}

.magic-particles::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='1' fill='%2348BB78' fill-opacity='0.2'/%3E%3C/svg%3E");
  opacity: 0;
  animation: green-dust 10s ease-in-out infinite alternate;
}

@keyframes green-particle-glow {
  0%, 100% {
    opacity: 0;
    transform: scale(0.8);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.3);
  }
}

@keyframes green-dust {
  0% {
    opacity: 0;
    background-position: 0% 0%;
  }
  50% {
    opacity: 0.15;
  }
  100% {
    opacity: 0;
    background-position: 100% 100%;
  }
}

/* Estilos para la animación de flor girando en supervisar */
.flower-loading-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 50, 0, 0.95), rgba(10, 40, 10, 0.98));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  overflow: hidden;
}

.flower-animation {
  position: relative;
  width: 200px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.flower-layer {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

.petal-group {
  position: relative;
  width: 100%;
  height: 100%;
}

/* Pétalos externos grandes */
.outer-petals {
  animation: rotate-clockwise 4s linear infinite;
}

.large-petal {
  position: absolute;
  width: 25px;
  height: 70px;
  background: linear-gradient(145deg, #10b981, #059669, #047857);
  border-radius: 50% 50% 50% 50% / 80% 80% 20% 20%;
  top: 50%;
  left: 50%;
  transform-origin: 12.5px 70px;
  transform: translate(-50%, -100%) rotate(var(--rotation));
  box-shadow: 
    inset 0 2px 8px rgba(255, 255, 255, 0.2),
    0 2px 12px rgba(16, 185, 129, 0.4);
  opacity: 0.9;
}

/* Pétalos internos pequeños */
.inner-petals {
  animation: rotate-counter-clockwise 3s linear infinite;
}

.small-petal {
  position: absolute;
  width: 18px;
  height: 45px;
  background: linear-gradient(145deg, #34d399, #10b981, #059669);
  border-radius: 50% 50% 50% 50% / 75% 75% 25% 25%;
  top: 50%;
  left: 50%;
  transform-origin: 9px 45px;
  transform: translate(-50%, -100%) rotate(var(--rotation));
  box-shadow: 
    inset 0 1px 6px rgba(255, 255, 255, 0.3),
    0 1px 8px rgba(52, 211, 153, 0.5);
  opacity: 0.8;
}

/* Centro de la flor */
.flower-center {
  position: relative;
  width: 40px;
  height: 40px;
  z-index: 10;
  animation: center-breathe 2s ease-in-out infinite;
}

.center-core {
  position: absolute;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, #fbbf24, #f59e0b, #d97706);
  border-radius: 50%;
  box-shadow: 
    0 0 0 3px #10b981,
    0 0 20px rgba(251, 191, 36, 0.7),
    inset 0 2px 8px rgba(217, 119, 6, 0.3);
}

.center-core::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 16px;
  height: 16px;
  background: radial-gradient(circle, #92400e, #78350f);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
}

.center-ring {
  position: absolute;
  top: -5px;
  left: -5px;
  width: 50px;
  height: 50px;
  border: 2px solid rgba(16, 185, 129, 0.6);
  border-radius: 50%;
  animation: ring-pulse 1.5s ease-in-out infinite;
}

/* Hojas rotatorias */
.flower-leaves {
  position: absolute;
  width: 120%;
  height: 120%;
  animation: rotate-leaves 6s linear infinite;
}

.leaf {
  position: absolute;
  width: 15px;
  height: 30px;
  background: linear-gradient(135deg, #065f46, #047857, #059669);
  border-radius: 0 100% 0 100%;
  opacity: 0.7;
}

.leaf-1 {
  top: 10%;
  left: 50%;
  transform: translateX(-50%) rotate(0deg);
}

.leaf-2 {
  top: 50%;
  right: 10%;
  transform: translateY(-50%) rotate(90deg);
}

.leaf-3 {
  bottom: 10%;
  left: 50%;
  transform: translateX(-50%) rotate(180deg);
}

.leaf-4 {
  top: 50%;
  left: 10%;
  transform: translateY(-50%) rotate(270deg);
}

.loading-text {
  margin-top: 50px;
  text-align: center;
  color: white;
}

.loading-text p {
  font-size: 18px;
  margin-bottom: 20px;
  opacity: 0.9;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.loading-dots {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.loading-dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: linear-gradient(45deg, #34d399, #10b981);
  animation: dots-bounce 1.4s ease-in-out infinite both;
  box-shadow: 0 2px 8px rgba(52, 211, 153, 0.4);
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

/* Animaciones */
@keyframes rotate-clockwise {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes rotate-counter-clockwise {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(-360deg); }
}

@keyframes rotate-leaves {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes center-breathe {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.15);
  }
}

@keyframes ring-pulse {
  0%, 100% {
    opacity: 0.6;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

@keyframes dots-bounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1.2);
    opacity: 1;
  }
}
</style>