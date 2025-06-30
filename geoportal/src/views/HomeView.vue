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

// Función para abrir la biblioteca de datos con animación
const openBiblioteca = () => {
  isTransitioning.value = true;
  transitionTarget.value = 'biblioteca';
  
  // Simulación de transición a biblioteca
  setTimeout(() => {
    showWelcome.value = false;
    
    setTimeout(() => {
      isTransitioning.value = false;
    }, 50);
  }, 300);
};

// Estado para el carrusel
const currentSlide = ref(0);
const totalSlides = 5; // Total de botones
const isTransitioningCarousel = ref(false);

// Definir los datos de los botones para el carrusel
const buttons = ref([
  {
    id: 'visor',
    title: 'VISOR',
    subtitle: 'EXPLORAR TERRITORIOS',
    description: 'Visor de Mapas',
    detail: 'Explore datos geográficos interactivos',
    color: 'green',
    action: 'openVisor',
    icon: 'M20.893 13.393l-1.135-1.135a2.252 2.252 0 01-.421-.585l-1.08-2.16a.414.414 0 00-.663-.107.827.827 0 01-.812.21l-1.273-.363a.89.89 0 00-.738 1.595l.587.39c.59.395.674 1.23.172 1.732l-.2.2c-.212.212-.33.498-.33.796v.41c0 .409-.11.809-.32 1.158l-1.315 2.191a2.11 2.11 0 01-1.81 1.025 1.055 1.055 0 01-1.055-1.055v-1.172c0-.92-.56-1.747-1.414-2.089l-.655-.261a2.25 2.25 0 01-1.383-2.46l.007-.042a2.25 2.25 0 01.29-.787l.09-.15a2.25 2.25 0 012.37-1.048l1.178.236a1.125 1.125 0 001.302-.795l.208-.73a1.125 1.125 0 00-.578-1.315l-.665-.332-.091.091a2.25 2.25 0 01-1.591.659h-.18c-.249 0-.487.1-.662.274a.931.931 0 01-1.458-1.137l1.411-2.353a2.25 2.25 0 00.286-.76m11.928 9.869A9 9 0 008.965 3.525m11.928 9.868A9 9 0 118.965 3.525'
  },
  {
    id: 'capas',
    title: 'CAPAS',
    subtitle: 'CARGAR SHAPEFILES',
    description: 'Subir Capas',
    detail: 'Cargue sus archivos shapefile',
    color: 'emerald',
    action: 'router',
    route: '/upload-layer',
    icon: 'M3 16.5V21h18v-4.5M12 3v15m0 0l-3-3m3 3l3-3'
  },
  {
    id: 'datos',
    title: 'DATOS',
    subtitle: 'ANÁLISIS Y ESTADÍSTICAS',
    description: 'Análisis y Estadísticas',
    detail: 'Visualice datos con gráficos',
    color: 'blue',
    action: 'openStats',
    icon: 'M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z'
  },
  {
    id: 'biblioteca',
    title: 'BIBLIOTECA',
    subtitle: 'REPOSITORIO DE DATOS',
    description: 'Biblioteca de Datos',
    detail: 'Acceda al repositorio central',
    color: 'purple',
    action: 'openBiblioteca',
    icon: 'M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25'
  },
  {
    id: 'supervisar',
    title: 'SUPERVISAR',
    subtitle: 'MONITOREAR PERSONAL',
    description: 'Supervisar Personal',
    detail: 'Monitoree ubicaciones en campo',
    color: 'red',
    action: 'openSupervisar',
    icon: 'M15 10.5a3 3 0 11-6 0 3 3 0 016 0z M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z'
  }
]);

// Configuración del carrusel lateral moderno
const carouselConfig = ref({
  blurIntensity: 2, // Desenfoque sutil en pixeles
  scaleReduction: 0.15, // Reducción de escala para botones laterales
  opacityReduction: 0.3, // Reducción de opacidad para botones laterales
  transitionDuration: 800, // Duración de transición más suave
  slideDistance: 320 // Distancia de deslizamiento entre botones
});

// Función para calcular la posición y estado de cada botón en el carrusel lateral
const getButtonPosition = (buttonIndex) => {
  const totalButtons = totalSlides;
  let position = buttonIndex - currentSlide.value;
  
  // Manejo de carrusel infinito - encuentra la distancia más corta
  if (position > totalButtons / 2) {
    position -= totalButtons;
  } else if (position < -totalButtons / 2) {
    position += totalButtons;
  }
  
  // Calcular propiedades visuales basadas en la posición
  const absPosition = Math.abs(position);
  
  // SOLO el botón central (posición 0) es clickeable
  const isClickable = position === 0 && buttonIndex === currentSlide.value;
  
  // Botón central (posición 0)
  if (position === 0) {
    return {
      translateX: 0,
      opacity: 1,
      scale: 1,
      blur: 0,
      zIndex: 10,
      isClickable: true, // Solo el centro es clickeable
      brightness: 1,
      visible: true
    };
  }
  
  // Botones laterales inmediatos (posición ±1)
  if (absPosition === 1) {
    return {
      translateX: position * carouselConfig.value.slideDistance,
      opacity: 1 - carouselConfig.value.opacityReduction,
      scale: 1 - carouselConfig.value.scaleReduction,
      blur: carouselConfig.value.blurIntensity,
      zIndex: 5,
      isClickable: false, // Laterales NO clickeables
      brightness: 0.8,
      visible: true
    };
  }
  
  // Botones más alejados (posición ±2)
  if (absPosition === 2) {
    return {
      translateX: position * carouselConfig.value.slideDistance * 0.7, // Menos distancia para efecto perspectiva
      opacity: 0.2,
      scale: 0.6,
      blur: carouselConfig.value.blurIntensity * 2,
      zIndex: 2,
      isClickable: false, // Alejados NO clickeables
      brightness: 0.6,
      visible: true
    };
  }
  
  // Botones muy lejanos (casi invisibles)
  return {
    translateX: position * carouselConfig.value.slideDistance * 0.5,
    opacity: 0.05,
    scale: 0.4,
    blur: carouselConfig.value.blurIntensity * 3,
    zIndex: 1,
    isClickable: false, // Lejanos NO clickeables
    brightness: 0.4,
    visible: false // Ocultos para mejor rendimiento
  };
};

// Funciones del carrusel con deslizamiento lateral
const nextSlide = () => {
  if (isTransitioningCarousel.value) return;
  isTransitioningCarousel.value = true;
  
  // Carrusel infinito hacia adelante
  currentSlide.value = (currentSlide.value + 1) % totalSlides;
  
  setTimeout(() => {
    isTransitioningCarousel.value = false;
  }, carouselConfig.value.transitionDuration);
};

const prevSlide = () => {
  if (isTransitioningCarousel.value) return;
  isTransitioningCarousel.value = true;
  
  // Carrusel infinito hacia atrás
  currentSlide.value = currentSlide.value === 0 ? totalSlides - 1 : currentSlide.value - 1;
  
  setTimeout(() => {
    isTransitioningCarousel.value = false;
  }, carouselConfig.value.transitionDuration);
};

const goToSlide = (index) => {
  if (isTransitioningCarousel.value || index === currentSlide.value) return;
  isTransitioningCarousel.value = true;
  
  // Calcular la dirección más corta para el deslizamiento
  const currentPos = currentSlide.value;
  const targetPos = index;
  const totalButtons = totalSlides;
  
  const directDistance = targetPos - currentPos;
  const wrapDistance = directDistance > 0 ? 
    directDistance - totalButtons : 
    directDistance + totalButtons;
  
  // Elegir la ruta más corta
  if (Math.abs(directDistance) <= Math.abs(wrapDistance)) {
    currentSlide.value = targetPos;
  } else {
    currentSlide.value = targetPos;
  }
  
  setTimeout(() => {
    isTransitioningCarousel.value = false;
  }, carouselConfig.value.transitionDuration);
};

// Función para manejar clics de botones con validación estricta
const handleButtonClick = (button, index, event) => {
  // VALIDACIÓN TRIPLE: Prevenir cualquier acción si el botón no está activo (centrado)
  const isCurrentSlide = index === currentSlide.value;
  const buttonState = getButtonPosition(index);
  const isButtonClickable = buttonState.isClickable;
  
  // Primera verificación: índice del slide actual
  if (!isCurrentSlide) {
    console.log(`Botón ${button.title} no está en el centro. Acción bloqueada.`);
    event.preventDefault();
    event.stopPropagation();
    return false;
  }
  
  // Segunda verificación: estado calculado del botón
  if (!isButtonClickable) {
    console.log(`Botón ${button.title} no es clickeable según getButtonPosition. Acción bloqueada.`);
    event.preventDefault();
    event.stopPropagation();
    return false;
  }
  
  // Tercera verificación: el carrusel no debe estar en transición
  if (isTransitioningCarousel.value) {
    console.log(`Carrusel en transición. Acción de ${button.title} bloqueada.`);
    event.preventDefault();
    event.stopPropagation();
    return false;
  }
  
  // Si todas las validaciones pasan, proceder con la acción
  console.log(`Ejecutando acción para botón ${button.title}`);
  
  // Solo ejecutar acción si es un botón normal (no router-link)
  if (button.action !== 'router') {
    executeButtonAction(button);
  }
  // Para router-links, el componente manejará la navegación automáticamente
};

// Función adicional para validar eventos de teclado
const handleKeyEvent = (event, button, index) => {
  // Solo permitir eventos de teclado en el botón central
  if (index !== currentSlide.value || !getButtonPosition(index).isClickable) {
    event.preventDefault();
    event.stopPropagation();
    return false;
  }
  
  // Permitir solo Enter y Space para activar el botón
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    handleButtonClick(button, index, event);
  }
};

// Función para ejecutar la acción del botón
const executeButtonAction = (button) => {
  switch (button.action) {
    case 'openVisor':
      openVisor();
      break;
    case 'openStats':
      openStats();
      break;
    case 'openBiblioteca':
      openBiblioteca();
      break;
    case 'openSupervisar':
      openSupervisar();
      break;
    case 'router':
      // Para router-link, se manejará en el template
      break;
  }
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
  
  // Agregar navegación con teclado para el carrusel
  const handleKeydown = (event) => {
    if (showWelcome.value) {
      switch (event.key) {
        case 'ArrowLeft':
          event.preventDefault();
          prevSlide();
          break;
        case 'ArrowRight':
          event.preventDefault();
          nextSlide();
          break;
        case 'Enter':
        case ' ':
          if (document.activeElement?.classList?.contains('carousel-indicator')) {
            event.preventDefault();
            const index = parseInt(document.activeElement.dataset.index);
            if (!isNaN(index)) {
              goToSlide(index);
            }
          }
          break;
        case 'Home':
          event.preventDefault();
          goToSlide(0);
          break;
        case 'End':
          event.preventDefault();
          goToSlide(totalSlides - 1);
          break;
      }
    }
  };
  
  document.addEventListener('keydown', handleKeydown);
  
  // Limpiar event listener al desmontar
  return () => {
    document.removeEventListener('keydown', handleKeydown);
  };
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
        <header class="py-4 sm:py-6 px-4">
          <div class="container mx-auto flex justify-between items-center">
            <div class="flex items-center space-x-2 sm:space-x-3">
              <!-- Logo responsivo -->
              <img src="@/components/images/logotipo.png" alt="Logo" class="h-12 w-12 sm:h-14 sm:w-14 md:h-16 md:w-16 animate-logo-pulse" />
              <h1 class="text-white text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl font-serif font-bold">
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
            <!-- Contenedor para el carrusel - Posición ajustada más arriba -->
            <div class="flex flex-col items-center justify-center mt-[-40px]">
              <!-- Texto mejorado con mejor tipografía y animación más elegante -->
              <h2 class="text-xl sm:text-2xl md:text-3xl font-semibold text-white mb-6 sm:mb-8 md:mb-10 tracking-wider elegant-text px-4">
                <span class="elegant-animation" data-text="Seleccione una herramienta">Seleccione una herramienta</span>
              </h2>
              
              <!-- Contenedor del carrusel -->
              <div class="relative w-full max-w-4xl mx-auto px-4">
                <!-- Flecha izquierda -->
                <button 
                  @click="prevSlide"
                  :disabled="isTransitioningCarousel"
                  aria-label="Botón anterior"
                  class="absolute left-2 top-1/2 -translate-y-1/2 z-20 bg-white/15 backdrop-blur-md text-white rounded-full p-2 sm:p-3 
                         transition-all duration-200 hover:bg-white/25 hover:shadow-xl active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed
                         border border-white/30 shadow-lg focus:outline-none focus:ring-2 focus:ring-white/50"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                
                <!-- Flecha derecha -->
                <button 
                  @click="nextSlide"
                  :disabled="isTransitioningCarousel"
                  aria-label="Botón siguiente"
                  class="absolute right-2 top-1/2 -translate-y-1/2 z-20 bg-white/15 backdrop-blur-md text-white rounded-full p-2 sm:p-3 
                         transition-all duration-200 hover:bg-white/25 hover:shadow-xl active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed
                         border border-white/30 shadow-lg focus:outline-none focus:ring-2 focus:ring-white/50"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
                
                <!-- Carrusel lateral moderno con deslizamiento -->
                <div class="overflow-visible mx-20 sm:mx-28 lateral-carousel-container">
                  <div class="carousel-viewport">
                    <!-- Todos los botones se renderizan simultáneamente para el efecto slide -->
                    <div 
                      v-for="(button, index) in buttons" 
                      :key="`slide-${button.id}`"
                      class="carousel-slide-lateral"
                      :style="{
                        '--slide-translate-x': `${getButtonPosition(index).translateX}px`,
                        '--slide-opacity': getButtonPosition(index).opacity,
                        '--slide-scale': getButtonPosition(index).scale,
                        '--slide-blur': `${getButtonPosition(index).blur}px`,
                        '--slide-brightness': getButtonPosition(index).brightness,
                        '--slide-z-index': getButtonPosition(index).zIndex,
                        '--transition-duration': `${carouselConfig.transitionDuration}ms`,
                        'visibility': getButtonPosition(index).visible ? 'visible' : 'hidden'
                      }"
                      :class="{
                        'slide-active-lateral': index === currentSlide,
                        'slide-inactive-lateral': index !== currentSlide
                      }"
                    >
                      <!-- Container del botón con animación lateral -->
                      <div class="lateral-button-wrapper">
                        <!-- Botón principal con efectos laterales -->
                        <component 
                          :is="button.action === 'router' ? 'router-link' : 'button'"
                          :to="getButtonPosition(index).isClickable && button.route ? button.route : undefined"
                          @click="handleButtonClick(button, index, $event)"
                          @mousedown="!getButtonPosition(index).isClickable ? $event.preventDefault() : undefined"
                          @mouseup="!getButtonPosition(index).isClickable ? $event.preventDefault() : undefined"
                          @keydown="handleKeyEvent($event, button, index)"
                          @keyup="!getButtonPosition(index).isClickable ? $event.preventDefault() : undefined"
                          @touchstart="!getButtonPosition(index).isClickable ? $event.preventDefault() : undefined"
                          @touchend="!getButtonPosition(index).isClickable ? $event.preventDefault() : undefined"
                          @mouseenter="button.id === 'supervisar' && getButtonPosition(index).isClickable ? toggleSmokeEffect() : undefined"
                          :disabled="!getButtonPosition(index).isClickable"
                          :tabindex="getButtonPosition(index).isClickable ? 0 : -1"
                          :aria-disabled="!getButtonPosition(index).isClickable"
                          :aria-hidden="!getButtonPosition(index).isClickable"
                          :role="getButtonPosition(index).isClickable ? (button.action === 'router' ? 'link' : 'button') : 'presentation'"
                          :style="{
                            pointerEvents: getButtonPosition(index).isClickable ? 'auto' : 'none',
                            userSelect: getButtonPosition(index).isClickable ? 'auto' : 'none'
                          }"
                          :class="[
                            `${button.id}-button`,
                            'lateral-carousel-button',
                            'relative bg-black/20 backdrop-blur-lg text-white rounded-full',
                            'p-6 sm:p-8 md:p-10 w-56 h-56 sm:w-64 sm:h-64 md:w-72 md:h-72',
                            'flex flex-col items-center justify-center',
                            'border border-white/20 overflow-hidden',
                            `shadow-${button.color}-500/30`,
                            {
                              'cursor-pointer': getButtonPosition(index).isClickable,
                              'cursor-default': !getButtonPosition(index).isClickable,
                              'lateral-button-active': index === currentSlide,
                              'lateral-button-inactive': index !== currentSlide,
                              'select-none': !getButtonPosition(index).isClickable
                            }
                          ]"
                        >
                          <!-- Contenedor para el efecto de humo (solo para supervisar) -->
                          <div v-if="button.id === 'supervisar'" class="absolute inset-0 smoke-container overflow-hidden rounded-full">
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
                          
                          <!-- Icono responsivo lateral -->
                          <div class="relative z-10 mb-3 lateral-icon-container">
                            <svg 
                              xmlns="http://www.w3.org/2000/svg" 
                              :class="[
                                'text-white drop-shadow-xl lateral-icon',
                                'h-12 w-12 sm:h-14 sm:w-14 md:h-16 md:w-16',
                                button.id === 'supervisar' ? 'opacity-70' : ''
                              ]"
                              fill="none" 
                              viewBox="0 0 24 24" 
                              stroke="currentColor" 
                              stroke-width="1.5"
                            >
                              <path stroke-linecap="round" stroke-linejoin="round" :d="button.icon" />
                            </svg>
                          </div>
                          
                          <!-- Texto del botón responsivo lateral -->
                          <div class="relative z-10 flex flex-col items-center lateral-text-container">
                            <span 
                              :class="[
                                'font-bold tracking-widest text-white drop-shadow-xl mb-2 lateral-title',
                                'text-lg sm:text-xl md:text-2xl',
                                button.id === 'supervisar' ? 'opacity-70' : ''
                              ]"
                            >
                              {{ button.title }}
                            </span>
                            <span 
                              :class="[
                                'font-medium tracking-wide text-center px-2 lateral-subtitle',
                                'text-xs sm:text-sm md:text-base',
                                `text-${button.color}-300`
                              ]"
                            >
                              {{ button.subtitle }}
                            </span>
                          </div>
                          
                          <!-- Efectos visuales laterales -->
                          <div class="absolute inset-0 rounded-full overflow-hidden lateral-effects">
                            <!-- Efecto de brillo para botón activo -->
                            <div 
                              :class="`bg-gradient-to-br from-${button.color}-300/30 to-transparent lateral-glow`"
                              class="absolute inset-0"
                            ></div>
                          </div>
                          
                          <!-- Anillo exterior lateral -->
                          <div 
                            :class="`border-${button.color}-400/30 lateral-ring`"
                            class="absolute -inset-1.5 rounded-full border"
                          ></div>
                          
                          <!-- Efecto pulsante solo para botón activo -->
                          <div 
                            v-if="index === currentSlide"
                            :class="`border-${button.color}-400/50 lateral-pulse`"
                            class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full rounded-full border-4"
                          ></div>
                        </component>
                        
                        <!-- Etiqueta descriptiva lateral -->
                        <div class="mt-2 sm:mt-3 text-center lateral-description">
                          <h3 class="text-sm sm:text-base md:text-lg font-semibold text-white mb-1 lateral-desc-title">{{ button.description }}</h3>
                          <p class="text-xs sm:text-sm text-gray-300 max-w-xs lateral-desc-detail">{{ button.detail }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Indicadores de posición -->
                <div class="flex justify-center mt-6 sm:mt-8 space-x-3" role="tablist" aria-label="Navegación del carrusel">
                  <button
                    v-for="(button, index) in buttons"
                    :key="`indicator-${index}`"
                    @click="goToSlide(index)"
                    :data-index="index"
                    :aria-label="`Ir a ${button.description}`"
                    :aria-selected="currentSlide === index"
                    role="tab"
                    :class="[
                      'carousel-indicator w-3 h-3 rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-white/50',
                      currentSlide === index 
                        ? 'bg-white shadow-lg scale-125 active' 
                        : 'bg-white/40 hover:bg-white/60'
                    ]"
                  >
                    <span class="sr-only">{{ button.description }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </main>

        <!-- Pie de página -->
        <footer class="py-4 sm:py-6 px-4 text-center text-white/70 text-xs sm:text-sm">
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
    
    <!-- Componente de Biblioteca (placeholder por ahora) -->
    <div v-if="!showWelcome && transitionTarget === 'biblioteca'" class="min-h-screen bg-gray-900 text-white flex items-center justify-center">
      <div class="text-center">
        <h1 class="text-4xl font-bold mb-4">Biblioteca de Datos</h1>
        <p class="text-xl mb-8">Repositorio central de información geográfica</p>
        <button @click="showWelcome = true" class="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-lg transition-colors">
          Volver al Inicio
        </button>
      </div>
    </div>
    
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

/* Estilos antiguos problemáticos eliminados - causaban recuadros negros */
/*
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
*/

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

/* Responsive para pantallas pequeñas - Estilos antiguos (comentados) */
/*
@media (max-width: 640px) {
  .flex.flex-wrap.justify-center {
    flex-direction: column;
    align-items: center;
  }
  
  .grid {
    gap: 1rem;
  }
  
  .biblioteca-button,
  .visor-button,
  .upload-button,
  .stats-button,
  .supervisar-button {
    width: 11rem !important;
    height: 11rem !important;
    padding: 1rem !important;
  }
  
  .biblioteca-button svg,
  .visor-button svg,
  .upload-button svg,
  .stats-button svg,
  .supervisar-button svg {
    width: 2.5rem !important;
    height: 2.5rem !important;
  }
  
  .biblioteca-button span:first-child,
  .visor-button span:first-child,
  .upload-button span:first-child,
  .stats-button span:first-child,
  .supervisar-button span:first-child {
    font-size: 1rem !important;
  }
}
*/

/* Efectos especiales para el botón biblioteca */
.biblioteca-button {
  position: relative;
  overflow: hidden;
}

.biblioteca-button::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(147, 51, 234, 0.1), transparent);
  transform: rotate(45deg);
  transition: all 0.5s;
  opacity: 0;
}

.biblioteca-button:hover::before {
  animation: shimmer 1.5s ease-in-out infinite;
  opacity: 1;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%) translateY(-100%) rotate(45deg);
  }
  50% {
    transform: translateX(0%) translateY(0%) rotate(45deg);
  }
  100% {
    transform: translateX(100%) translateY(100%) rotate(45deg);
  }
}

/* Animación de rotación para iconos en biblioteca */
.biblioteca-button:hover svg {
  animation: bookFlip 0.6s ease-in-out;
}

@keyframes bookFlip {
  0% { transform: rotateY(0deg); }
  50% { transform: rotateY(90deg); }
  100% { transform: rotateY(0deg); }
}

/* Mejoras para el efecto de humo en móviles */
@media (max-width: 640px) {
  .smoke-container div {
    filter: blur(4px) !important;
  }
}

/* Animación para partículas de datos en biblioteca */
@keyframes dataFlow {
  0% {
    transform: translateY(20px) translateX(0);
    opacity: 0;
  }
  50% {
    opacity: 0.8;
  }
  100% {
    transform: translateY(-20px) translateX(10px);
    opacity: 0;
  }
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

/* Estilos del carrusel */
.carousel-container {
  position: relative;
  overflow: hidden;
}

/* Animaciones suaves para las flechas del carrusel - Estáticas */
.carousel-arrow {
  backdrop-filter: blur(12px);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.carousel-arrow:hover {
  box-shadow: 0 6px 20px rgba(255, 255, 255, 0.25);
}

.carousel-arrow:active {
  transform: scale(0.95);
}

/* Efecto de entrada para los botones del carrusel */
.carousel-slide {
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0.7;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Mejoras para los indicadores del carrusel */
.carousel-indicator {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(4px);
}

.carousel-indicator:hover {
  transform: scale(1.2);
}

.carousel-indicator.active {
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.6);
}

/* Animación de pulso para el botón activo */
@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 8px rgba(255, 255, 255, 0.4);
  }
  50% {
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.8);
  }
}

.carousel-indicator.active {
  animation: pulse-glow 2s ease-in-out infinite;
}

/* Efectos de transición modernos y profesionales para botones del carrusel */
.carousel-button {
  transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: center;
  position: relative;
  overflow: hidden;
}

.carousel-button:hover {
  transform: scale(1.1) translateY(-5px);
  filter: brightness(1.2) contrast(1.1);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

/* Efecto de onda moderna al hacer hover */
.carousel-button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  pointer-events: none;
  opacity: 0;
}

.carousel-button:hover::before {
  width: 100%;
  height: 100%;
  opacity: 1;
}

/* Efecto de resplandor específico para cada color */
.visor-button:hover {
  box-shadow: 
    0 20px 40px rgba(34, 197, 94, 0.4),
    0 0 60px rgba(34, 197, 94, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.capas-button:hover {
  box-shadow: 
    0 20px 40px rgba(5, 150, 105, 0.4),
    0 0 60px rgba(5, 150, 105, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.datos-button:hover {
  box-shadow: 
    0 20px 40px rgba(59, 130, 246, 0.4),
    0 0 60px rgba(59, 130, 246, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.biblioteca-button:hover {
  box-shadow: 
    0 20px 40px rgba(147, 51, 234, 0.4),
    0 0 60px rgba(147, 51, 234, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.supervisar-button:hover {
  box-shadow: 
    0 20px 40px rgba(239, 68, 68, 0.4),
    0 0 60px rgba(239, 68, 68, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

/* Efecto de partículas flotantes modernas */
.carousel-button::after {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: conic-gradient(from 0deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  border-radius: inherit;
  animation: rotate-border 3s linear infinite;
  opacity: 0;
  transition: opacity 0.6s ease;
  pointer-events: none;
}

.carousel-button:hover::after {
  opacity: 1;
}

@keyframes rotate-border {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* Animación de entrada con efecto de rebote moderno */
.modern-button {
  animation: modernEntrance 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes modernEntrance {
  0% {
    opacity: 0;
    transform: scale(0.8) translateY(30px);
    filter: blur(10px);
  }
  60% {
    transform: scale(1.05) translateY(-10px);
    filter: blur(0px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
    filter: blur(0px);
  }
}

/* Animación de entrada con retraso escalonado */
.stagger-animation {
  opacity: 0;
  animation: staggerIn 0.6s ease-out forwards;
}

@keyframes staggerIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Estilos antiguos comentados - reemplazados por efectos modernos */
/*
.visor-button:hover {
  box-shadow: 0 8px 32px rgba(34, 197, 94, 0.3);
}

.capas-button:hover,
.upload-button:hover {
  box-shadow: 0 8px 32px rgba(5, 150, 105, 0.3);
}

.datos-button:hover,
.stats-button:hover {
  box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
}

.biblioteca-button:hover {
  box-shadow: 0 8px 32px rgba(147, 51, 234, 0.3);
}

.supervisar-button:hover {
  box-shadow: 0 8px 32px rgba(239, 68, 68, 0.3);
}
*/

/* Animación de respiración para el botón activo del carrusel */
@keyframes breathe {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
}

.carousel-active-button {
  animation: breathe 3s ease-in-out infinite;
}

/* Efecto de partículas flotantes para el carrusel */
.carousel-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  animation: floating-particles 8s ease-in-out infinite;
  pointer-events: none;
  z-index: 1;
}

@keyframes floating-particles {
  0%, 100% {
    opacity: 0.3;
    transform: translateY(0px);
  }
  50% {
    opacity: 0.6;
    transform: translateY(-10px);
  }
}

/* Responsividad mejorada para el carrusel */
@media (max-width: 640px) {
  .carousel-container {
    padding: 0 0.5rem;
  }
  
  .carousel-button {
    width: 16rem !important;
    height: 16rem !important;
    padding: 1.5rem !important;
  }
  
  .carousel-arrow {
    padding: 0.5rem !important;
  }
  
  .carousel-arrow svg {
    width: 1rem !important;
    height: 1rem !important;
  }
}

@media (min-width: 768px) and (max-width: 1024px) {
  .carousel-button {
    width: 18rem !important;
    height: 18rem !important;
    padding: 2rem !important;
  }
}

/* Animación de deslizamiento suave */
.carousel-slide-container {
  transition: transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* Efecto de enfoque en el botón activo */
.carousel-focused {
  position: relative;
}

.carousel-focused::after {
  content: '';
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: inherit;
  animation: focus-pulse 2s ease-in-out infinite;
  pointer-events: none;
}

@keyframes focus-pulse {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.02);
  }
}

/* ===== CARRUSEL LATERAL MODERNO CON DESLIZAMIENTO ===== */

/* Contenedor principal del carrusel lateral */
.lateral-carousel-container {
  position: relative;
  height: 450px; /* Altura suficiente para contener los botones */
  overflow: visible; /* Permitir que los elementos se vean fuera del contenedor */
  perspective: 1200px; /* Perspectiva 3D para profundidad */
}

/* Viewport del carrusel - donde se ven los elementos */
.carousel-viewport {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Slides laterales con posicionamiento absoluto para deslizamiento */
.carousel-slide-lateral {
  position: absolute;
  left: 50%;
  top: 50%;
  width: auto;
  height: auto;
  
  /* Transformaciones dinámicas para el efecto de deslizamiento */
  transform: 
    translate(-50%, -50%) 
    translateX(var(--slide-translate-x)) 
    scale(var(--slide-scale));
  
  opacity: var(--slide-opacity);
  filter: blur(var(--slide-blur)) brightness(var(--slide-brightness));
  z-index: var(--slide-z-index);
  
  /* Transición suave para el deslizamiento lateral */
  transition: 
    transform var(--transition-duration) cubic-bezier(0.25, 0.46, 0.45, 0.94),
    opacity var(--transition-duration) cubic-bezier(0.25, 0.46, 0.45, 0.94),
    filter var(--transition-duration) cubic-bezier(0.25, 0.46, 0.45, 0.94);
  
  /* Optimización de rendimiento */
  will-change: transform, opacity, filter;
  backface-visibility: hidden;
}

/* Wrapper del botón lateral */
.lateral-button-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all var(--transition-duration) cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* Botón del carrusel lateral */
.lateral-carousel-button {
  transition: all var(--transition-duration) cubic-bezier(0.25, 0.46, 0.45, 0.94);
  transform-style: preserve-3d;
}

/* Estado activo del botón lateral (centro) */
.lateral-button-active {
  /* Efecto sutil de respiración para el botón central */
  animation: lateral-breathe 3s ease-in-out infinite alternate;
  box-shadow: 
    0 12px 35px rgba(255, 255, 255, 0.12),
    0 0 45px rgba(255, 255, 255, 0.08);
}

/* Estado inactivo del botón lateral */
.lateral-button-inactive {
  pointer-events: none !important; /* Forzar no interacción */
  user-select: none !important; /* Prevenir selección */
  -webkit-user-select: none !important;
  -moz-user-select: none !important;
  -ms-user-select: none !important;
  -webkit-touch-callout: none !important; /* Prevenir menú contextual en iOS */
  -webkit-tap-highlight-color: transparent !important; /* Eliminar highlight en móviles */
  cursor: default !important; /* Cursor por defecto */
}

/* Refuerzo de reglas para botones no clickeables */
.lateral-carousel-button[disabled],
.lateral-carousel-button[aria-disabled="true"],
.lateral-carousel-button:not(.lateral-button-active) {
  pointer-events: none !important;
  user-select: none !important;
  -webkit-user-select: none !important;
  -moz-user-select: none !important;
  -ms-user-select: none !important;
  -webkit-touch-callout: none !important;
  -webkit-tap-highlight-color: transparent !important;
  cursor: default !important;
  outline: none !important;
  
  /* Prevenir eventos de teclado */
  -webkit-user-focus: none !important;
  -moz-user-focus: none !important;
}

/* Anular cualquier hover o focus en botones inactivos */
.lateral-carousel-button:not(.lateral-button-active):hover,
.lateral-carousel-button:not(.lateral-button-active):focus,
.lateral-carousel-button:not(.lateral-button-active):active,
.lateral-carousel-button[disabled]:hover,
.lateral-carousel-button[disabled]:focus,
.lateral-carousel-button[disabled]:active {
  transform: none !important;
  box-shadow: none !important;
  border: none !important;
  outline: none !important;
  background-color: rgba(0, 0, 0, 0.2) !important;
  cursor: default !important;
}

/* Restaurar interactividad SOLO para botones clickeables y activos */
.lateral-carousel-button:not(:disabled).lateral-button-active {
  pointer-events: auto !important;
  user-select: auto;
  cursor: pointer !important;
}

/* Asegurar que los botones deshabilitados no sean clickeables */
.lateral-carousel-button:disabled {
  pointer-events: none !important;
  cursor: not-allowed !important;
  opacity: 0.6;
}

/* Iconos laterales con animación suave */
.lateral-icon-container {
  transition: transform var(--transition-duration) cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.slide-active-lateral .lateral-icon-container {
  transform: scale(1.05);
}

/* Texto lateral con transiciones */
.lateral-text-container {
  transition: all var(--transition-duration) cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.lateral-title,
.lateral-subtitle {
  transition: all var(--transition-duration) cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* Efectos visuales laterales */
.lateral-effects {
  transition: opacity var(--transition-duration) cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.lateral-glow {
  opacity: 0;
  transition: opacity var(--transition-duration) cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.lateral-button-active .lateral-glow {
  opacity: 0.5;
}

/* Anillo exterior lateral */
.lateral-ring {
  opacity: 0.2;
  transition: all var(--transition-duration) cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.lateral-button-active .lateral-ring {
  opacity: 0.7;
  transform: scale(1.03);
}

/* Efecto pulsante lateral para botón activo */
.lateral-pulse {
  animation: lateral-pulse-effect 2.5s ease-in-out infinite;
}

/* Descripción lateral */
.lateral-description {
  transition: all var(--transition-duration) cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.slide-inactive-lateral .lateral-description {
  opacity: 0.5;
  transform: translateY(3px);
}

.lateral-desc-title,
.lateral-desc-detail {
  transition: all var(--transition-duration) cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* Animaciones laterales */
@keyframes lateral-breathe {
  0% {
    transform: scale(1);
    box-shadow: 
      0 12px 35px rgba(255, 255, 255, 0.12),
      0 0 45px rgba(255, 255, 255, 0.08);
  }
  100% {
    transform: scale(1.01);
    box-shadow: 
      0 16px 45px rgba(255, 255, 255, 0.16),
      0 0 55px rgba(255, 255, 255, 0.12);
  }
}

@keyframes lateral-pulse-effect {
  0%, 100% {
    opacity: 0.5;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 0.2;
    transform: translate(-50%, -50%) scale(1.05);
  }
}

/* Hover mejorado solo para botón activo lateral */
.lateral-button-active:hover {
  transform: scale(1.03);
  box-shadow: 
    0 18px 55px rgba(255, 255, 255, 0.18),
    0 0 65px rgba(255, 255, 255, 0.15);
}

.lateral-button-active:hover .lateral-icon-container {
  transform: scale(1.15);
}

.lateral-button-active:hover .lateral-glow {
  opacity: 0.7;
}

/* Efectos de entrada suave para nuevos slides */
.carousel-slide-lateral[style*="translateX(0px)"] {
  /* Slide central con efecto especial */
  filter: blur(0px) brightness(1) saturate(1.1);
}

/* Overlay visual para botones no interactivos */
.lateral-carousel-button:not(.lateral-button-active)::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.1);
  border-radius: inherit;
  pointer-events: none;
  z-index: 100;
  transition: opacity 0.3s ease;
}

/* Indicador visual sutil para botón activo */
.lateral-carousel-button.lateral-button-active::before {
  content: '';
  position: absolute;
  top: -3px;
  left: -3px;
  right: -3px;
  bottom: -3px;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1), transparent, rgba(255, 255, 255, 0.1));
  border-radius: inherit;
  pointer-events: none;
  z-index: -1;
  animation: active-glow 3s ease-in-out infinite;
}

@keyframes active-glow {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.6;
  }
}

/* Responsive para carrusel lateral */
@media (max-width: 768px) {
  .lateral-carousel-container {
    height: 380px;
  }
  
  .carousel-slide-lateral {
    /* En móviles, reducir efectos para mejor rendimiento */
    filter: blur(calc(var(--slide-blur) * 0.6)) brightness(var(--slide-brightness));
  }
}

@media (max-width: 640px) {
  .lateral-carousel-container {
    height: 320px;
  }
}

/* Optimizaciones de rendimiento para carrusel lateral */
.carousel-slide-lateral,
.lateral-carousel-button,
.lateral-button-wrapper {
  transform-style: preserve-3d;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}

/* Suavizado de animaciones en dispositivos de gama baja */
@media (prefers-reduced-motion: reduce) {
  .carousel-slide-lateral,
  .lateral-carousel-button,
  .lateral-icon-container,
  .lateral-text-container {
    transition-duration: 0.2s !important;
  }
  
  .lateral-button-active {
    animation: none !important;
  }
  
  .lateral-pulse {
    animation: none !important;
  }
}
</style>