<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const username = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);
const showPassword = ref(false);

// Estado para animaciones
const fadeIn = ref(false);
const slideUp = ref(false);

// Array de imágenes de cultivos y plantaciones
const backgroundImages = [
  'https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?q=80&w=1974&auto=format&fit=crop', // Semillas brotando
  'https://images.unsplash.com/photo-1464226184884-fa280b87c399?q=80&w=1974&auto=format&fit=crop', // Plantando
  'https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?q=80&w=1974&auto=format&fit=crop', // Campos cultivados
  'https://images.unsplash.com/photo-1518977676601-b53f82aba655?q=80&w=1974&auto=format&fit=crop'  // Cultivos
];

// Estado para el índice de la imagen actual
const currentImageIndex = ref(0);

// Función para cambiar la imagen de fondo
const changeBackgroundImage = () => {
  currentImageIndex.value = (currentImageIndex.value + 1) % backgroundImages.length;
};

// Función para iniciar sesión
const login = () => {
  // Resetear mensaje de error
  error.value = '';
  loading.value = true;
  
  // Simular un retraso de red
  setTimeout(() => {
    if (username.value === 'root' && password.value === '1234') {
      // Guardar el estado de autenticación en localStorage
      localStorage.setItem('authenticated', 'true');
      localStorage.setItem('user', JSON.stringify({ username: username.value }));
      
      // Redirigir al usuario a la pantalla de carga en lugar de ir directo a la página principal
      router.push('/loading');
    } else {
      error.value = 'Usuario o contraseña incorrectos';
      loading.value = false;
    }
  }, 800);
};

onMounted(() => {
  // Comprobar si el usuario ya está autenticado
  const isAuthenticated = localStorage.getItem('authenticated') === 'true';
  if (isAuthenticated) {
    router.push('/');
  }
  
  // Iniciar animaciones después de que se monte el componente
  setTimeout(() => {
    fadeIn.value = true;
  }, 100);
  
  setTimeout(() => {
    slideUp.value = true;
  }, 300);
  
  // Iniciar carrusel de imágenes de fondo
  const interval = setInterval(changeBackgroundImage, 5000);
  
  // Limpiar intervalo cuando se desmonte el componente
  return () => clearInterval(interval);
});
</script>

<template>
  <div class="min-h-screen w-full flex flex-col-reverse md:flex-row">
    <!-- Panel de imagen decorativa (izquierda en desktop, abajo en móvil) -->
    <div class="w-full md:w-1/2 bg-emerald-800 relative overflow-hidden"
         :class="{ 'fade-in': fadeIn }">
      <!-- Overlay con gradiente -->
      <div class="absolute inset-0 bg-gradient-to-r from-emerald-900/70 to-emerald-700/70 z-10"></div>
      
      <!-- Contenedor de imágenes de carrusel -->
      <div class="absolute inset-0 m-0 p-0">
        <template v-for="(image, index) in backgroundImages" :key="index">
          <div
            class="absolute inset-0 bg-cover bg-center bg-no-repeat transition-opacity duration-1000"
            :style="{
              backgroundImage: `url('${image}')`,
              opacity: currentImageIndex === index ? 1 : 0,
              transform: 'scale(1.05)'
            }"
          ></div>
        </template>
      </div>
      
      <!-- Contenido sobre la imagen -->
      <div class="relative z-20 h-full flex flex-col justify-center items-center p-8 text-center"
           :class="{ 'slide-up': slideUp }">
        <h2 class="text-white text-2xl md:text-4xl font-bold mb-4 font-serif">
          Geoportal Sembrando Datos
        </h2>
        <p class="text-white text-lg mb-6 max-w-md">
          Plataforma para visualización y análisis de datos territoriales
        </p>
      </div>
    </div>
    
    <!-- Panel de inicio de sesión (derecha en desktop, arriba en móvil) -->
    <div class="w-full md:w-1/2 bg-white flex flex-col justify-center items-center p-8 md:p-16 relative"
         :class="{ 'fade-in': fadeIn }">
      <!-- Logo centrado sin animación -->
      <div class="w-full flex justify-center mb-12">
        <img 
          src="@/components/images/logotipo.png" 
          alt="Logotipo Sembrando Datos" 
          class="h-20 md:h-24 w-auto object-contain"
        />
      </div>
      
      <div class="w-full max-w-md">
        <!-- Encabezado -->
        <div class="text-center mb-10">
          <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-3"
              :class="{ 'slide-up': slideUp }">
            Bienvenido
          </h1>
          <p class="text-gray-600"
             :class="{ 'slide-up': slideUp, 'delay-100': true }">
            Inicia sesión para acceder al geoportal
          </p>
        </div>
        
        <!-- Formulario -->
        <form @submit.prevent="login" class="space-y-6">
          <!-- Campo de usuario -->
          <div :class="{ 'slide-up': slideUp, 'delay-200': true }">
            <label for="username" class="block text-sm font-medium text-gray-700 mb-1">
              Usuario
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <input
                v-model="username"
                id="username"
                name="username"
                type="text"
                required
                class="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 transition-all py-3 px-4 border"
                placeholder="Ingrese su usuario"
              />
            </div>
          </div>
          
          <!-- Campo de contraseña -->
          <div :class="{ 'slide-up': slideUp, 'delay-300': true }">
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
              Contraseña
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <input
                v-model="password"
                id="password"
                name="password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 transition-all py-3 px-4 border"
                placeholder="Ingrese su contraseña"
              />
              <button 
                type="button" 
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 flex items-center pr-3"
              >
                <svg v-if="!showPassword" class="w-5 h-5 text-gray-400 hover:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="w-5 h-5 text-emerald-500 hover:text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
                </svg>
              </button>
            </div>
          </div>
          
          <!-- Mensaje de error -->
          <div 
            v-if="error" 
            class="bg-red-50 border-l-4 border-red-400 p-4 rounded"
            :class="{ 'shake-animation': error }"
          >
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-700">{{ error }}</p>
              </div>
            </div>
          </div>
          
          <!-- Botón de inicio de sesión -->
          <div :class="{ 'slide-up': slideUp, 'delay-400': true }">
            <button
              type="submit"
              class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-all duration-300 overflow-hidden"
              :disabled="loading"
            >
              <!-- Efecto de onda al hacer clic -->
              <span class="absolute inset-0 w-full h-full transition-all duration-300 ease-out transform translate-x-0 -translate-y-full bg-emerald-500 group-hover:translate-x-0 group-hover:translate-y-0"></span>
              <span class="absolute inset-0 w-full h-full transition-all duration-300 ease-out transform translate-x-full translate-y-0 bg-emerald-500 group-hover:translate-x-0 group-hover:translate-y-0"></span>
              <span class="absolute inset-0 w-full h-full transition-all duration-300 ease-out transform translate-x-0 translate-y-full bg-emerald-500 group-hover:translate-x-0 group-hover:translate-y-0"></span>
              <span class="absolute inset-0 w-full h-full transition-all duration-300 ease-out transform translate-x-full -translate-y-full bg-emerald-500 group-hover:translate-x-0 group-hover:translate-y-0"></span>
              
              <!-- Texto del botón -->
              <span class="relative flex items-center">
                <span v-if="loading" class="mr-2">
                  <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </span>
                {{ loading ? 'Iniciando sesión...' : 'Iniciar sesión' }}
              </span>
            </button>
          </div>
        </form>
        
        <!-- Pie de página -->
        <div class="mt-8 text-center text-sm text-gray-500"
             :class="{ 'slide-up': slideUp, 'delay-500': true }">
          <p>¿Necesitas ayuda? Contacta al administrador</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Transición para animaciones */
* {
  transition: all 0.35s ease-in-out;
}

/* Animación de entrada con fade */
.fade-in {
  animation: fadeIn 1s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Animación de deslizamiento hacia arriba */
.slide-up {
  animation: slideUp 0.6s ease-out forwards;
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

/* Aplicar retrasos a los elementos en cascada */
.delay-100 {
  animation-delay: 0.1s;
}

.delay-200 {
  animation-delay: 0.2s;
}

.delay-300 {
  animation-delay: 0.3s;
}

.delay-400 {
  animation-delay: 0.4s;
}

.delay-500 {
  animation-delay: 0.5s;
}

/* Animación de vibración para mensajes de error */
.shake-animation {
  animation: shake 0.82s cubic-bezier(.36,.07,.19,.97) both;
  transform: translate3d(0, 0, 0);
  backface-visibility: hidden;
  perspective: 1000px;
}

@keyframes shake {
  10%, 90% {
    transform: translate3d(-1px, 0, 0);
  }
  
  20%, 80% {
    transform: translate3d(2px, 0, 0);
  }

  30%, 50%, 70% {
    transform: translate3d(-4px, 0, 0);
  }

  40%, 60% {
    transform: translate3d(4px, 0, 0);
  }
}

/* Mejorar la transición de imágenes de fondo */
.bg-cover {
  background-size: cover;
  background-position: center;
  transition: opacity 1.5s ease-in-out, transform 10s ease-in-out;
}

/* Añadir efecto de zoom lento para las imágenes de fondo */
@keyframes slow-zoom {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(1.1);
  }
}

.bg-cover {
  animation: slow-zoom 20s infinite alternate;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .w-full.max-w-md {
    margin-top: 1rem;
  }
}
</style>
