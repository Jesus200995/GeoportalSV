<script setup>
import { ref, onMounted, computed } from 'vue';
import Dashboard from '../components/Dashboard.vue';
import ToastNotification from '../components/notifications/ToastNotification.vue';

const showWelcome = ref(true);
const savedMaps = ref([]);
const searchMapQuery = ref('');

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

// Estado para modales
const deleteModal = ref({
  show: false,
  map: null
});

const editModal = ref({
  show: false,
  map: null,
  newName: ''
});

// Agregar estados para modales de confirmación
const confirmationModal = ref({
  show: false,
  title: '',
  message: '',
  onConfirm: null,
  type: 'info' // info, warning, danger
});

// Agregar estado para modal de confirmación de acción completada
const successModal = ref({
  show: false,
  title: '',
  message: '',
  type: 'success'
});

// Función para eliminar mapa con confirmación
const confirmDelete = (map) => {
  confirmationModal.value = {
    show: true,
    title: 'Eliminar Mapa',
    message: `¿Estás seguro de que deseas eliminar el mapa "${map.name}"?`,
    type: 'danger',
    onConfirm: () => {
      deleteMap(map.id);
      confirmationModal.value.show = false;
      
      // Mostrar modal de éxito después de eliminar
      successModal.value = {
        show: true,
        title: 'Mapa Eliminado',
        message: 'El mapa ha sido eliminado correctamente',
        type: 'success'
      };
      
      // Ocultar modal de éxito después de 2 segundos
      setTimeout(() => {
        successModal.value.show = false;
      }, 2000);
    }
  };
};

// Función para renombrar mapa
const renameMap = (map) => {
  editModal.value = {
    show: true,
    map,
    newName: map.name
  };
};

// Modificar la función executeRename
const executeRename = () => {
  const { map, newName } = editModal.value;
  if (map && newName && newName.trim()) {
    const maps = savedMaps.value;
    const mapIndex = maps.findIndex(m => m.id === map.id);
    if (mapIndex !== -1) {
      maps[mapIndex].name = newName.trim();
      localStorage.setItem('savedMaps', JSON.stringify(maps));
      editModal.value = { show: false, map: null, newName: '' };
      
      // Mostrar modal de éxito
      successModal.value = {
        show: true,
        title: 'Mapa Renombrado',
        message: 'El nombre del mapa ha sido actualizado correctamente',
        type: 'success'
      };
      
      // Ocultar modal de éxito después de 2 segundos
      setTimeout(() => {
        successModal.value.show = false;
      }, 2000);
    }
  }
};

// Agregar estado para búsqueda
// Función para filtrar mapas
const filteredMaps = computed(() => {
  const query = searchMapQuery.value.toLowerCase().trim();
  if (!query) return savedMaps.value;
  
  return savedMaps.value.filter(map => {
    const nameMatch = map.name.toLowerCase().includes(query);
    const dateMatch = map.lastModified.toLowerCase().includes(query);
    return nameMatch || dateMatch;
  });
});

// Agregar estados para el carrusel
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

// Cargar mapas guardados al iniciar
onMounted(() => {
  loadSavedMaps();
  // Cambiar imagen cada 5 segundos
  setInterval(changeBackgroundImage, 5000);
});

// Actualizar los thumbnails de los mapas existentes
const updateExistingMapThumbnails = () => {
  const maps = JSON.parse(localStorage.getItem('savedMaps') || '[]');
  const updatedMaps = maps.map(map => ({
    ...map,
    thumbnail: '/src/components/images/vizual2.png' // Ruta absoluta
  }));
  localStorage.setItem('savedMaps', JSON.stringify(updatedMaps));
  savedMaps.value = updatedMaps;
};

// Modificar la función saveMapState
const saveMapState = async () => {
  if (!newMapName.value.trim()) {
    alert('Por favor ingrese un nombre para el mapa');
    return;
  }

  const mapState = {
    id: Date.now(),
    name: newMapName.value.trim(),
    lastModified: new Date().toLocaleString(),
    thumbnail: '/src/components/images/vizual2.png', // Ruta absoluta
    center: map.value.getView().getCenter(),
    zoom: map.value.getView().getZoom(),
    layers: getAllLayers().map(layer => ({
      ...layer,
      visible: layer.visible,
      opacity: layerOpacity.value[layer.id] || 1
    }))
  };

  // Guardar el estado del mapa en el almacenamiento local
  const maps = JSON.parse(localStorage.getItem('savedMaps')) || [];
  maps.push(mapState);
  localStorage.setItem('savedMaps', JSON.stringify(maps));

  // Mostrar notificación de éxito
  showNotification('Mapa guardado correctamente');

  // Reiniciar el nombre del nuevo mapa
  newMapName.value = '';

  // Cerrar el mapa actual y mostrar la página de inicio
  showWelcome.value = true;
};

// Iniciar el carrusel cuando el componente se monta y actualizar thumbnails
onMounted(() => {
  loadSavedMaps();
  updateExistingMapThumbnails(); // Asegurar que se actualicen los thumbnails
  setInterval(changeBackgroundImage, 5000);
});
</script>

<template>
  <main class="min-h-screen w-full bg-gradient-to-br from-green-50 to-teal-50">
    <!-- Página de bienvenida -->
    <div v-if="showWelcome" class="min-h-screen w-full flex flex-col">
      <!-- Header con carrusel de imágenes -->
      <header class="relative overflow-hidden h-48 sm:h-56 w-full">
        <div class="absolute inset-0 m-0 p-0">
          <template v-for="(image, index) in backgroundImages" :key="index">
            <div
              class="absolute inset-0 bg-cover bg-center bg-no-repeat transition-opacity duration-1000"
              :style="{
                backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.4)), url('${image}')`,
                opacity: currentImageIndex === index ? 1 : 0,
                transform: 'scale(1.01)'
              }"
            ></div>
          </template>
        </div>

        <!-- Contenido del header -->
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="text-center">
            <!-- Contenedor del logo y título -->
            <div class="flex flex-col items-center space-y-2">
              <img 
                src="@/components/images/logotipo.png" 
                alt="Logotipo Sembrando Datos" 
                class="h-16 md:h-20 w-auto object-contain animate-fade-in drop-shadow-lg"
              />
              <div>
                <h1 class="text-xl md:text-3xl font-serif font-bold text-white animate-fade-in drop-shadow-lg">
                  Geoportal Sembrando Datos
                </h1>
                <p class="text-sm md:text-base text-gray-100 max-w-xl mx-auto drop-shadow">
                  Visualización y análisis territorial
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Contenido principal centrado -->
      <div class="flex-1 container mx-auto px-4 py-8">
        <!-- Barra de búsqueda mejorada -->
        <div class="max-w-6xl mx-auto mb-6">
          <div class="relative">
            <input
              v-model="searchMapQuery"
              type="text"
              placeholder="Buscar mapas guardados..."
              class="w-full px-4 py-3 pl-12 bg-white rounded-xl shadow-sm border border-gray-200 
                     focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-300"
            />
            <span class="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400">
              🔍
            </span>
            <!-- Indicador de resultados -->
            <span v-if="searchMapQuery" 
                  class="absolute right-4 top-1/2 transform -translate-y-1/2 text-sm text-gray-500">
              {{ filteredMaps.length }} resultado(s)
            </span>
          </div>
        </div>

        <!-- Grid de mapas con transiciones -->
        <div class="max-w-6xl mx-auto">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <!-- Tarjeta de nuevo mapa siempre visible -->
            <div 
              @click="showWelcome = false"
              class="bg-gradient-to-br from-white to-green-50 rounded-xl shadow-lg overflow-hidden 
                     group hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300"
            >
              <div class="relative p-4">
                <div class="aspect-video bg-gradient-to-br from-green-100 to-emerald-50 
                          rounded-lg flex items-center justify-center overflow-hidden group-hover:scale-105 transition-transform duration-300">
                  <img 
                    src="@/components/images/vizual.png" 
                    alt="Nuevo mapa" 
                    class="w-full h-full object-cover opacity-90 group-hover:opacity-100 transition-opacity"
                  >
                  <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 
                              transition-all duration-300 flex items-center justify-center">
                    <span class="text-4xl transform scale-0 group-hover:scale-100 transition-transform duration-300">
                      ➕
                    </span>
                  </div>
                </div>
                <div class="p-4 text-center">
                  <h3 class="text-lg font-bold text-green-800 mb-2">Nuevo Mapa</h3>
                  <p class="text-sm text-green-600 opacity-75">Crear una nueva visualización</p>
                </div>
              </div>
            </div>

            <!-- Mapas filtrados con transición -->
            <TransitionGroup
              name="map-card"
              tag="div"
              class="contents"
            >
              <div 
                v-for="map in filteredMaps" 
                :key="map.id"
                class="bg-white rounded-xl shadow-lg overflow-hidden group hover:shadow-xl 
                       transform hover:-translate-y-1 transition-all duration-300"
              >
                <div class="relative">
                  <div class="aspect-video bg-green-50 flex items-center justify-center overflow-hidden">
                    <img 
                      :src="map.thumbnail || '/src/components/images/vizual2.png'"
                      :alt="map.name"
                      class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      @error="$event.target.src = '/src/components/images/vizual2.png'"
                    >
                    <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 
                                transition-all duration-300 flex items-center justify-center opacity-0 
                                group-hover:opacity-100 space-x-3">
                      <button 
                        @click.stop="openMap(map)"
                        class="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 
                               transition-colors transform hover:scale-105"
                        title="Abrir mapa"
                      >
                        🗺️ Abrir
                      </button>
                      <button 
                        @click.stop="renameMap(map)"
                        class="bg-blue-500 text-white p-2 rounded-lg hover:bg-blue-600 
                               transition-colors transform hover:scale-105"
                        title="Renombrar mapa"
                      >
                        ✏️
                      </button>
                      <button 
                        @click.stop="confirmDelete(map)"
                        class="bg-red-500 text-white p-2 rounded-lg hover:bg-red-600 
                               transition-colors transform hover:scale-105"
                        title="Eliminar mapa"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                  <div class="p-4">
                    <h3 class="text-lg font-semibold text-green-800 mb-2 truncate">{{ map.name }}</h3>
                    <p class="text-xs text-gray-500">Última modificación: {{ map.lastModified }}</p>
                  </div>
                </div>
              </div>
            </TransitionGroup>

            <!-- Mensaje cuando no hay resultados mejorado -->
            <div v-if="searchMapQuery && filteredMaps.length === 0" 
                 class="col-span-full p-8 text-center">
              <div class="bg-gray-50 rounded-xl p-6 animate-fade-in">
                <p class="text-gray-500 mb-2">No se encontraron mapas que coincidan con "{{ searchMapQuery }}"</p>
                <p class="text-sm text-gray-400">Intenta con otro término de búsqueda</p>
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

    <!-- Modal de confirmación genérico -->
    <Transition name="modal">
      <div 
        v-if="confirmationModal.show" 
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-[55]"
      >
        <div 
          class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 transform transition-all"
          :class="{ 'scale-100 opacity-100': confirmationModal.show, 'scale-95 opacity-0': !confirmationModal.show }"
        >
          <div class="p-6">
            <div class="text-center">
              <!-- Icono según tipo -->
              <span class="text-5xl mb-4 inline-block animate-bounce-slow">
                {{ confirmationModal.type === 'danger' ? '⚠️' : 
                   confirmationModal.type === 'warning' ? '⚡' : 'ℹ️' }}
              </span>
              
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                {{ confirmationModal.title }}
              </h3>
              
              <p class="text-gray-600 mb-6">
                {{ confirmationModal.message }}
              </p>
            </div>
            
            <div class="flex justify-center space-x-3">
              <button 
                @click="confirmationModal.show = false"
                class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Cancelar
              </button>
              <button 
                @click="confirmationModal.onConfirm"
                :class="{
                  'bg-red-500 hover:bg-red-600': confirmationModal.type === 'danger',
                  'bg-yellow-500 hover:bg-yellow-600': confirmationModal.type === 'warning',
                  'bg-green-500 hover:bg-green-600': confirmationModal.type === 'info'
                }"
                class="px-4 py-2 text-white rounded-lg transition-colors"
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal de éxito -->
    <Transition name="modal">
      <div 
        v-if="successModal.show" 
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-[60]"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 transform transition-all animate-fade-in">
          <div class="p-6">
            <div class="text-center">
              <!-- Icono de éxito -->
              <span class="text-5xl mb-4 inline-block animate-bounce-slow">
                {{ successModal.type === 'success' ? '✅' : '❌' }}
              </span>
              
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                {{ successModal.title }}
              </h3>
              
              <p class="text-gray-600">
                {{ successModal.message }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal de edición de nombre -->
    <Transition name="modal">
      <div 
        v-if="editModal.show"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 transform transition-all">
          <div class="p-6">
            <div class="text-center">
              <span class="text-5xl mb-4 inline-block">✏️</span>
              <h3 class="text-xl font-semibold text-gray-900 mb-4">
                Renombrar mapa
              </h3>
              <input 
                v-model="editModal.newName"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Nuevo nombre del mapa"
                @keyup.enter="executeRename"
              />
            </div>
            <div class="mt-6 flex justify-center space-x-3">
              <button 
                @click="editModal.show = false"
                class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Cancelar
              </button>
              <button 
                @click="executeRename"
                class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                :disabled="!editModal.newName.trim()"
              >
                Guardar
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
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

/* Modificar estilos del header */
header {
  min-height: unset;
  margin: 0;
  padding: 0;
  background-attachment: unset;
  position: relative;
  top: 0;
  left: 0;
  right: 0;
}

/* Asegurar que las imágenes cubran todo el espacio */
.bg-cover {
  background-size: cover;
  background-position: center;
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
}

/* Ajustar el contenedor principal */
.min-h-screen {
  margin-top: 0;
  padding-top: 0;
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

/* Estilos para los modales */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.modal-enter-to,
.modal-leave-from {
  opacity: 1;
  transform: scale(1);
}

/* Animaciones para el modal de confirmación */
.transform {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* Mejorar la apariencia de los botones del modal */
button {
  position: relative;
  overflow: hidden;
}

button::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 60%);
  transform: translate(-50%, -50%) scale(0);
  transition: transform 0.5s;
  pointer-events: none;
}

button:hover::after {
  transform: translate(-50%, -50%) scale(2);
}

button:active {
  transform: scale(0.98);
}

/* Estilo para botón deshabilitado */
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Agregar estilos para el modal de éxito */
.modal-success-enter-active,
.modal-success-leave-active {
  transition: all 0.3s ease;
}

.modal-success-enter-from,
.modal-success-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* Agregar z-index más alto para el modal de éxito */
.z-[60] {
  z-index: 60;
}

/* Agregar animación de rebote lento */
.animate-bounce-slow {
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(-5%);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: translateY(0);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
}

/* Agregar efecto hover suave para las tarjetas */
.aspect-video {
  aspect-ratio: 16 / 9;
}

/* Mejorar animación del botón de nuevo mapa */
.group:hover .scale-0 {
  transition-delay: 0.1s;
}

/* Mejorar sombras de las tarjetas */
.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 
              0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.hover\:shadow-xl:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 
              0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Mejorar transición de la barra de búsqueda */
input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
}

/* Animaciones para las tarjetas de mapas */
.map-card-move {
  transition: transform 0.5s ease;
}

.map-card-enter-active,
.map-card-leave-active {
  transition: all 0.5s ease;
}

.map-card-enter-from,
.map-card-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.map-card-leave-active {
  position: absolute;
}

/* Mejorar la transición de la barra de búsqueda */
input {
  transition: all 0.3s ease;
}

input:focus {
  transform: scale(1.01);
}

/* Animación para el contador de resultados */
span {
  transition: all 0.3s ease;
}

/* Optimizar rendimiento de animaciones */
* {
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}
</style>
