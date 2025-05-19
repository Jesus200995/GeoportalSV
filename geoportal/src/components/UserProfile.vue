<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const user = ref(null);
const showDropdown = ref(false);
const logoutModal = ref(false);

onMounted(() => {
  // Obtener información del usuario desde localStorage
  const userData = localStorage.getItem('user');
  if (userData) {
    user.value = JSON.parse(userData);
  } else {
    router.push('/login');
  }
});

// Función para cerrar sesión
const logout = () => {
  logoutModal.value = true;
  showDropdown.value = false;
};

// Confirmar cierre de sesión
const confirmLogout = () => {
  localStorage.removeItem('authenticated');
  localStorage.removeItem('user');
  router.push('/login');
};
</script>

<template>
  <div class="relative">
    <!-- Botón de perfil -->
    <button 
      @click="showDropdown = !showDropdown"
      class="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-white/90 hover:bg-white transition-all duration-300 border border-gray-200"
    >
      <div class="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center text-white font-semibold">
        {{ user?.username?.charAt(0).toUpperCase() || '?' }}
      </div>
      <span class="text-sm font-medium text-gray-700">{{ user?.username || 'Usuario' }}</span>
      <svg class="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>
    
    <!-- Menú desplegable -->
    <div 
      v-if="showDropdown"
      class="absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50 animate-fade-in-down"
    >
      <div class="py-1">
        <div class="px-4 py-2 border-b border-gray-100">
          <p class="text-sm text-gray-500">Conectado como</p>
          <p class="font-medium text-gray-800">{{ user?.username || 'Usuario' }}</p>
        </div>
        <button 
          @click="logout"
          class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
        >
          <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Cerrar sesión
          </div>
        </button>
      </div>
    </div>
    
    <!-- Modal de confirmación de cierre de sesión -->
    <Transition name="modal-fade">
      <div v-if="logoutModal" 
           class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
           @click.self="logoutModal = false">
        <div class="bg-white rounded-2xl p-6 w-[90%] max-w-md transform transition-all duration-300
                    scale-100 opacity-100 shadow-xl">
          <div class="text-center">
            <div class="mb-4 transform transition-all duration-500 hover:rotate-12">
              <span class="text-5xl">🚪</span>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-4">
              Cerrar sesión
            </h3>
            <p class="text-gray-600 mb-8">
              ¿Estás seguro de que deseas cerrar sesión?
            </p>
            <div class="flex space-x-3 justify-center">
              <button 
                @click="logoutModal = false"
                class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 
                       rounded-lg transition-colors duration-300"
              >
                Cancelar
              </button>
              <button 
                @click="confirmLogout"
                class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white 
                       rounded-lg transition-colors duration-300 flex items-center space-x-2"
              >
                <span>Cerrar sesión</span>
                <span class="text-xl">→</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
    
    <!-- Overlay para cerrar dropdown si se hace clic fuera -->
    <div 
      v-if="showDropdown"
      class="fixed inset-0 z-40"
      @click="showDropdown = false"
    ></div>
  </div>
</template>

<style scoped>
.animate-fade-in-down {
  animation: fadeInDown 0.2s ease-out forwards;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Transiciones para el modal */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .bg-white,
.modal-fade-leave-to .bg-white {
  transform: scale(0.9);
  opacity: 0;
}
</style>
