<script setup>
import { ref, onMounted, computed } from 'vue';
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

// Estados para filtros y búsqueda
const filters = ref({
  search: '',
  date: 'all',
  sortBy: 'recent',
  category: 'all'
});

// Mejorar la función getTimeAgo para un cálculo más preciso
const getTimeAgo = (dateStr) => {
  const date = new Date(dateStr);
  const now = new Date();
  
  // Resetear las horas para comparar solo fechas
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const mapDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  
  const diffTime = today - mapDate;
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return 'today';
  if (diffDays <= 7) return 'week';
  if (diffDays <= 30) return 'month';
  return 'older';
};

// Modificar el computed filteredMaps para mejor filtrado
const filteredMaps = computed(() => {
  let result = [...savedMaps.value];
  
  // Filtrar por fecha primero
  if (filters.value.date !== 'all') {
    result = result.filter(map => {
      const timeAgo = getTimeAgo(map.lastModified);
      return filters.value.date === timeAgo;
    });
  }
  
  // Luego filtrar por búsqueda
  if (filters.value.search.trim()) {
    const searchTerm = filters.value.search.toLowerCase().trim();
    result = result.filter(map => 
      map.name.toLowerCase().includes(searchTerm) ||
      map.lastModified.toLowerCase().includes(searchTerm)
    );
  }

  // Ordenar resultados
  result.sort((a, b) => {
    const dateA = new Date(a.lastModified);
    const dateB = new Date(b.lastModified);
    return filters.value.sortBy === 'recent' ? dateB - dateA : dateA - dateB;
  });

  return result;
});

const resetFilters = () => {
  filters.value = {
    search: '',
    date: 'all',
    sortBy: 'recent',
    category: 'all'
  };
};

// Cerrar el modal de éxito al hacer clic
const closeSuccessModal = () => {
  successModal.value.show = false;
};

// Cerrar el modal de confirmación al hacer clic fuera del área del modal
const closeConfirmationModal = (event) => {
  const modal = event.target.closest('.modal');
  if (!modal) {
    confirmationModal.value.show = false;
  }
};

// Cerrar el modal de edición al hacer clic fuera del área del modal
const closeEditModal = (event) => {
  const modal = event.target.closest('.modal');
  if (!modal) {
    editModal.value.show = false;
  }
};

// Cerrar el mapa actual y mostrar la página de inicio
const closeMap = () => {
  showWelcome.value = true;
  // Aquí puedes agregar cualquier otra lógica para cerrar el mapa
};

// Lógica para el botón de guardar mapa
const handleSaveMap = async () => {
  // Aquí va la lógica para guardar el mapa
  // Por ejemplo, llamar a la función saveMapState()
  await saveMapState();
  
  // Mostrar notificación de éxito
  showNotification('Mapa guardado correctamente');
  
  // Cerrar el mapa actual y mostrar la página de inicio
  closeMap();
};

// Lógica para el botón de abrir mapa
const handleOpenMap = (map) => {
  // Aquí va la lógica para abrir el mapa
  // Por ejemplo, cargar el mapa en el componente del mapa
  openMap(map);
};

// Lógica para el botón de eliminar mapa
const handleDeleteMap = (map) => {
  // Aquí va la lógica para eliminar el mapa
  // Por ejemplo, llamar a la función confirmDelete()
  confirmDelete(map);
};

// Lógica para el botón de renombrar mapa
const handleRenameMap = (map) => {
  // Aquí va la lógica para renombrar el mapa
  // Por ejemplo, abrir el modal de edición con el mapa seleccionado
  renameMap(map);
};
</script>

<template>
  <main class="min-h-screen w-full bg-gradient-to-br from-green-50 to-teal-50">
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

      <!-- Contenedor principal modificado -->
      <div class="flex-1 w-full px-4 py-6">
        <!-- Panel de búsqueda y filtros mejorado -->
        <div class="max-w-[95%] xl:max-w-[90%] mx-auto bg-white rounded-2xl shadow-lg p-4 sm:p-6 mb-8">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Buscador mejorado -->
            <div class="sm:col-span-1 lg:col-span-1">
              <div class="relative">
                <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" 
                     fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
                <input
                  v-model="filters.search"
                  type="text"
                  placeholder="Buscar por nombre..."
                  class="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl
                         focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                />
              </div>
            </div>

            <!-- Filtros modificados -->
            <div class="sm:col-span-1 lg:col-span-1">
              <select
                v-model="filters.date"
                class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl
                       focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="all">Todas las fechas</option>
                <option value="today">Creados hoy</option>
                <option value="week">Última semana</option>
                <option value="month">Último mes</option>
                <option value="older">Más antiguos</option>
              </select>
            </div>

            <div class="sm:col-span-1 lg:col-span-1">
              <select
                v-model="filters.sortBy"
                class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl
                       focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="recent">Más recientes primero</option>
                <option value="oldest">Más antiguos primero</option>
              </select>
            </div>
          </div>

          <!-- Filtros activos y contador modificado -->
          <div v-if="filters.search || filters.date !== 'all'"
               class="flex flex-wrap items-center gap-2 mt-4 pt-4 border-t border-gray-100">
            <span class="text-sm text-gray-500 w-full sm:w-auto mb-2 sm:mb-0">
              {{ filteredMaps.length }} resultado{{ filteredMaps.length !== 1 ? 's' : '' }}
            </span>
            
            <div class="flex-1 flex flex-wrap gap-2">
              <div v-if="filters.search"
                   class="inline-flex items-center px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                <span>Búsqueda: "{{ filters.search }}"</span>
                <button @click="filters.search = ''"
                        class="ml-2 hover:text-green-600">×</button>
              </div>
              <div v-if="filters.date !== 'all'"
                   class="inline-flex items-center px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                <span>{{ 
                  filters.date === 'today' ? 'Creados hoy' :
                  filters.date === 'week' ? 'Última semana' :
                  filters.date === 'month' ? 'Último mes' : 'Más antiguos'
                }}</span>
                <button @click="filters.date = 'all'"
                        class="ml-2 hover:text-green-600">×</button>
              </div>
            </div>

            <button v-if="filters.search || filters.date !== 'all'"
                    @click="resetFilters"
                    class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 
                           hover:bg-gray-100 rounded-full transition-colors">
              Limpiar filtros
            </button>
          </div>
        </div>

        <!-- Grid de mapas responsiva -->
        <div class="max-w-[95%] xl:max-w-[90%] mx-auto">
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
            <!-- Tarjeta de nuevo mapa (reducida) -->
            <div 
              @click="showWelcome = false"
              class="group bg-gradient-to-br from-white to-green-50 rounded-xl shadow-md 
                     hover:shadow-lg transform hover:-translate-y-1 transition-all duration-300 
                     overflow-hidden h-48 relative"
            >
              <div class="relative p-4 h-full flex flex-col justify-between">
                <div class="aspect-video bg-gradient-to-br from-green-100 to-emerald-50 
                            rounded-lg overflow-hidden flex items-center justify-center flex-1">
                  <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-green-500/20 
                              group-hover:scale-110 transition-transform duration-500"></div>
                  <div class="relative z-10 transform group-hover:scale-105 transition-all duration-300">
                    <svg class="w-10 h-10 text-green-600 group-hover:text-green-500 transition-colors" 
                         fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                            d="M12 4v16m8-8H4"/>
                    </svg>
                  </div>
                </div>
                <div class="mt-2 text-center">
                  <h3 class="text-sm font-medium text-green-800 group-hover:text-green-600 
                             transition-colors">Nuevo Mapa</h3>
                </div>
                <div class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r 
                            from-green-500 to-emerald-500 transform scale-x-0 group-hover:scale-x-100 
                            transition-transform duration-500 origin-left"></div>
              </div>
            </div>

            <!-- Mapas filtrados con transición -->
            <TransitionGroup name="map-card" tag="div" class="contents">
              <div v-for="map in filteredMaps" 
                   :key="map.id"
                   class="bg-white rounded-xl shadow-md overflow-hidden group 
                          hover:shadow-lg transform hover:-translate-y-1 transition-all duration-300 h-48"
              >
                <div class="relative h-32">
                  <img 
                    :src="map.thumbnail || '/src/components/images/vizual2.png'"
                    :alt="map.name"
                    class="w-full h-full object-cover"
                    @error="$event.target.src = '/src/components/images/vizual2.png'"
                  >
                  <!-- Overlay con botones mejorados -->
                  <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/40 to-transparent 
                              opacity-0 group-hover:opacity-100 transition-all duration-300 
                              flex items-center justify-center">
                    <div class="flex items-center space-x-2 transform translate-y-4 
                                group-hover:translate-y-0 transition-transform duration-300">
                      <button 
                        @click="openMap(map)"
                        class="p-2 bg-green-500 text-white rounded-lg hover:bg-green-600 
                               transform hover:scale-105 transition-all duration-200 
                               shadow-lg hover:shadow-green-500/25"
                        title="Abrir mapa"
                      >
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                        </svg>
                      </button>
                      <button 
                        @click="renameMap(map)"
                        class="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 
                               transform hover:scale-105 transition-all duration-200 
                               shadow-lg hover:shadow-blue-500/25"
                        title="Renombrar mapa"
                      >
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button 
                        @click="confirmDelete(map)"
                        class="p-2 bg-red-500 text-white rounded-lg hover:bg-red-600 
                               transform hover:scale-105 transition-all duration-200 
                               shadow-lg hover:shadow-red-500/25"
                        title="Eliminar mapa"
                      >
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
                <div class="p-2">
                  <h3 class="text-sm font-medium text-gray-800 truncate">{{ map.name }}</h3>
                  <p class="text-xs text-gray-500 mt-1">{{ map.lastModified }}</p>
                </div>
              </div>
            </TransitionGroup>
          </div>

          <!-- Mensaje sin resultados centrado -->
          <div v-if="filteredMaps.length === 0" 
               class="text-center py-12 w-full">
            <div class="bg-gray-50 rounded-2xl p-8 inline-block max-w-md mx-auto">
              <p class="text-gray-500 mb-2">No se encontraron mapas que coincidan con tu búsqueda</p>
              <button @click="resetFilters"
                      class="mt-4 px-4 py-2 bg-green-500 text-white rounded-lg 
                             hover:bg-green-600 transition-colors">
                Limpiar filtros
              </button>
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
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent,
    rgba(255, 255, 255, 0.1),
    transparent
  );
  transform: translate(-100%, -100%) rotate(45deg);
  transition: all 0.3s ease-out;
}

button:hover::after {
  transform: translate(100%, 100%) rotate(45deg);
}

/* Animación suave para los íconos de los botones */
button svg {
  transition: transform 0.2s ease;
}

button:hover svg {
  transform: scale(1.1);
}

/* Mejoras para las tarjetas y botones */
.map-card-enter-active,
.map-card-leave-active {
  transition: all 0.4s ease-out;
}

.map-card-enter-from,
.map-card-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
