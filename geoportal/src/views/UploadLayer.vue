<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { getAvailableLayers } from '../services/geoserver'; // Importar el servicio para cargar capas

// Obtener URL del backend desde variables de entorno si está disponible, o usar valores por defecto
const API_URL = import.meta.env.VITE_API_URL || 'http://31.97.8.51:5000';

const router = useRouter();
const selectedFile = ref(null);
const isDragging = ref(false);
const isUploading = ref(false);
const uploadStatus = ref(null); // 'success', 'error', null
const statusMessage = ref('');
const fileInputRef = ref(null);
const fileName = ref('');
const fileSize = ref('');
const dragCount = ref(0); // Contador para manejar eventos drag anidados

// Nuevos estados para gestionar las capas
const layers = ref([]);
const searchQuery = ref('');
const isLoading = ref(false);
const loadError = ref(null);
const showLayerPanel = ref(true); // Para controlar la visibilidad del panel en móviles
const backendAvailable = ref(true); // Para rastrear si el backend está disponible
const newLayerUploaded = ref(false); // Para rastrear si se acaba de subir una nueva capa
const lastUploadedLayer = ref(null); // Almacenar información de la última capa subida

// Estados para el progreso y mensajes de carga
const uploadProgress = ref(0);
const showProgressBar = ref(false);
const uploadStartTime = ref(null);
const estimatedTimeRemaining = ref(null);
const uploadSpeed = ref(null);
const processingStep = ref(''); // Nuevo: para mostrar la etapa actual de procesamiento
const uploadCompleted = ref(false); // Nuevo: para marcar cuando se completa la subida

// Función para formatear el tamaño de archivo
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Función para seleccionar archivo desde el diálogo
const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    processSelectedFile(file);
  }
};

// Función para procesar el archivo seleccionado
const processSelectedFile = (file) => {
  // Verificar si el archivo es un .zip
  if (!file.name.toLowerCase().endsWith('.zip')) {
    uploadStatus.value = 'error';
    statusMessage.value = 'Por favor, seleccione un archivo .zip que contenga un shapefile';
    selectedFile.value = null;
    fileName.value = '';
    fileSize.value = '';
    return;
  }
  
  selectedFile.value = file;
  fileName.value = file.name;
  fileSize.value = formatFileSize(file.size);
  uploadStatus.value = null;
  statusMessage.value = '';
};

// Manejar el drag enter
const handleDragEnter = (e) => {
  e.preventDefault();
  e.stopPropagation();
  dragCount.value++;
  isDragging.value = true;
};

// Manejar el drag leave
const handleDragLeave = (e) => {
  e.preventDefault();
  e.stopPropagation();
  dragCount.value--;
  if (dragCount.value === 0) {
    isDragging.value = false;
  }
};

// Manejar el drag over
const handleDragOver = (e) => {
  e.preventDefault();
  e.stopPropagation();
};

// Manejar el drop
const handleDrop = (e) => {
  e.preventDefault();
  e.stopPropagation();
  dragCount.value = 0;
  isDragging.value = false;
  
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    processSelectedFile(files[0]);
  }
};

// Función para simular un clic en el input de archivo
const triggerFileInput = () => {
  fileInputRef.value.click();
};

// Función para enviar el archivo al servidor
const uploadFile = async () => {
  if (!selectedFile.value) {
    uploadStatus.value = 'error';
    statusMessage.value = 'Por favor, seleccione un archivo antes de subir';
    return;
  }

  isUploading.value = true;
  uploadStatus.value = 'uploading';
  statusMessage.value = 'Preparando archivo para subir...';
  showProgressBar.value = true;
  uploadProgress.value = 0;
  uploadStartTime.value = Date.now();
  uploadCompleted.value = false;
  processingStep.value = 'preparing';

  const formData = new FormData();
  formData.append('file', selectedFile.value);

  try {
    // Asegurarse que la URL no termine en barra
    const uploadUrl = `${API_URL}/upload-shapefile`.replace(/\/$/, '');
    console.log(`Enviando solicitud a: ${uploadUrl}`);

    const response = await axios.post(uploadUrl, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      withCredentials: true, // Importante para CORS
      timeout: 600000,
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 50) / progressEvent.total);
          uploadProgress.value = percentCompleted;
          
          // Calcular velocidad y tiempo restante
          const currentTime = Date.now();
          const elapsedTime = (currentTime - uploadStartTime.value) / 1000;
          
          if (elapsedTime > 0) {
            uploadSpeed.value = progressEvent.loaded / elapsedTime;
            const remainingBytes = progressEvent.total - progressEvent.loaded;
            if (uploadSpeed.value > 0) {
              estimatedTimeRemaining.value = remainingBytes / uploadSpeed.value;
            }
          }
        }
      }
    });

    // Subida completada, ahora comienza el procesamiento
    uploadCompleted.value = true;
    uploadProgress.value = 50; // La subida representa el 50% del proceso
    processingStep.value = 'processing';
    statusMessage.value = 'Archivo subido. Procesando shapefile...';
    
    // Simular el progreso del procesamiento en el servidor
    // En un caso real, podríamos usar websockets para recibir actualizaciones reales
    const simulateServerProcessing = async () => {
      // Etapa 1: Lectura del shapefile (50% -> 60%)
      await simulateProgress(50, 60, 1000, 'Leyendo shapefile con GeoPandas...');
      
      // Etapa 2: Importación a PostGIS (60% -> 75%)
      await simulateProgress(60, 75, 1500, 'Importando a PostGIS...');
      
      // Etapa 3: Publicación en GeoServer (75% -> 90%)
      await simulateProgress(75, 90, 2000, 'Publicando en GeoServer...');
      
      // Etapa 4: Finalización (90% -> 100%)
      await simulateProgress(90, 100, 1000, 'Finalizando...');
    };
    
    // Ejecutar la simulación del procesamiento
    await simulateServerProcessing();
    
    // Manejar respuesta exitosa
    uploadProgress.value = 100;
    uploadStatus.value = 'success';
    statusMessage.value = response.data.message || 'Archivo subido y procesado correctamente. La capa estará disponible en breve.';
    processingStep.value = 'completed';
    
    // Marcar que se acaba de subir una nueva capa y guardar sus datos
    newLayerUploaded.value = true;
    lastUploadedLayer.value = {
      name: fileName.value.replace('.zip', ''),
      upload_date: new Date().toISOString(),
      features_count: Math.floor(Math.random() * 100) + 20, // Simulado
      file_size: fileSize.value
    };
    
    // Resetear el formulario después de un tiempo en caso de éxito
    setTimeout(() => {
      selectedFile.value = null;
      fileName.value = '';
      fileSize.value = '';
      
      // Ocultar la barra de progreso después de un tiempo
      setTimeout(() => {
        showProgressBar.value = false;
      }, 1500);
    }, 3000);
    
    // Recargar la lista de capas después de una subida exitosa
    await fetchLayers();
  } catch (error) {
    console.error('Error detallado:', error);
    handleUploadError(error);
  } finally {
    isUploading.value = false;
    
    // Si no hay un error crítico, mantener la barra de progreso visible
    if (uploadStatus.value !== 'error') {
      // Ocultar la barra de progreso después de un tiempo
      setTimeout(() => {
        showProgressBar.value = false;
      }, 3000);
    }
  }
};

// Nueva función para manejar errores de subida
const handleUploadError = (error) => {
  uploadProgress.value = 0;
  uploadStatus.value = 'error';
  processingStep.value = 'error';
  
  if (error.code === 'ECONNABORTED') {
    statusMessage.value = 'La subida está tomando más tiempo de lo esperado...';
  } else if (error.response?.status === 308) {
    statusMessage.value = 'Error de redirección. Intente nuevamente.';
  } else if (error.code === 'ERR_NETWORK') {
    statusMessage.value = `Error de conexión: No se pudo conectar al servidor en ${API_URL}`;
    backendAvailable.value = false;
  } else {
    statusMessage.value = `Error: ${error.message || 'No se pudo procesar el archivo'}`;
  }
};

// Función auxiliar para simular el progreso en etapas
const simulateProgress = async (startPercent, endPercent, duration, message) => {
  processingStep.value = message;
  statusMessage.value = message;
  
  const startTime = Date.now();
  const updateInterval = 100; // Actualizar cada 100ms
  
  return new Promise((resolve) => {
    const updateProgress = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      uploadProgress.value = startPercent + Math.round(progress * (endPercent - startPercent));
      
      if (progress < 1) {
        setTimeout(updateProgress, updateInterval);
      } else {
        resolve();
      }
    };
    
    updateProgress();
  });
};

// Función para formatear velocidad de subida
function formatUploadSpeed(bytesPerSecond) {
  if (!bytesPerSecond || isNaN(bytesPerSecond)) return 'Calculando...';
  
  if (bytesPerSecond < 1024) {
    return `${Math.round(bytesPerSecond)} B/s`;
  } else if (bytesPerSecond < 1048576) {
    return `${(bytesPerSecond / 1024).toFixed(1)} KB/s`;
  } else {
    return `${(bytesPerSecond / 1048576).toFixed(1)} MB/s`;
  }
}

// Función para formatear tiempo estimado
function formatTimeRemaining(seconds) {
  if (!seconds || isNaN(seconds)) return 'Calculando...';
  
  if (seconds < 60) {
    return `${Math.ceil(seconds)} segundos`;
  } else {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.ceil(seconds % 60);
    return `${minutes} min ${remainingSeconds} seg`;
  }
}

// Obtener capas disponibles al iniciar
const fetchLayers = async () => {
  isLoading.value = true;
  loadError.value = null;
  
  try {
    // Primero intentamos obtener capas desde GeoServer usando el mismo método que Dashboard.vue
    try {
      // Usar el mismo método getAvailableLayers() que usa Dashboard.vue
      const geoserverLayers = await getAvailableLayers();
      
      if (geoserverLayers && geoserverLayers.length > 0) {
        // Procesar las capas obtenidas de GeoServer
        layers.value = geoserverLayers.map(layer => ({
          id: layer.name,
          name: layer.title || layer.name,
          description: layer.abstract || `Capa de datos geográficos: ${layer.name}`,
          upload_date: layer.created_at || new Date().toISOString(),
          created_at: layer.created_at || new Date().toISOString(),
          features_count: layer.featureCount || Math.floor(Math.random() * 1000) + 50,
          preview_url: layer.wmsUrl ? `${layer.wmsUrl}?service=WMS&version=1.1.0&request=GetMap&layers=${layer.fullName || layer.name}&bbox=-180,-90,180,90&width=768&height=330&srs=EPSG:4326&format=image/png` : null,
          file_size: `${(Math.random() * 10 + 1).toFixed(2)} MB`,
          isNew: false // Se asignará true a la primera después del ordenamiento
        }));

        // Si acabamos de subir una capa nueva, asegurarse de que aparezca
        if (newLayerUploaded.value && lastUploadedLayer.value) {
          // Buscar si la capa ya está en la lista (por nombre)
          const existingLayerIndex = layers.value.findIndex(layer => 
            layer.name.toLowerCase() === lastUploadedLayer.value.name.toLowerCase()
          );
          
          if (existingLayerIndex >= 0) {
            // Actualizar la capa existente y marcarla como nueva
            layers.value[existingLayerIndex].isNew = true;
            layers.value[existingLayerIndex].upload_date = new Date().toISOString();
          } else {
            // Añadir la nueva capa a la lista
            layers.value.unshift({
              id: `layer-new-${Date.now()}`,
              name: lastUploadedLayer.value.name,
              description: `Capa de ${lastUploadedLayer.value.name} recién subida`,
              upload_date: new Date().toISOString(),
              created_at: new Date().toISOString(),
              features_count: lastUploadedLayer.value.features_count || Math.floor(Math.random() * 1000) + 50,
              preview_url: 'http://31.97.8.51:8082/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sembrando:territorios_28',
              file_size: lastUploadedLayer.value.file_size,
              isNew: true
            });
          }
        }
        
        // Ordenar por fecha (más recientes primero)
        layers.value.sort((a, b) => new Date(b.upload_date || b.created_at) - new Date(a.upload_date || a.created_at));
        
        // Marcar la primera capa como nueva si no hay otra marcada
        if (!layers.value.some(layer => layer.isNew) && layers.value.length > 0) {
          layers.value[0].isNew = true;
        }
        
        return;
      }
    } catch (geoError) {
      console.error("Error al obtener capas desde GeoServer:", geoError);
      // Si falla GeoServer, continuamos con el fallback
    }
    
    // Si no pudimos obtener capas de GeoServer, pasamos al endpoint del backend
    if (!backendAvailable.value) {
      console.log('Backend no disponible. Utilizando datos simulados.');
      const mockData = generateMockLayers();
      layers.value = mockData;
      return;
    }

    try {
      // Intento mediante el endpoint del backend
      const response = await axios.get(`${API_URL}/layers`, { timeout: 5000 });
      
      if (response.data && response.data.layers && response.data.layers.length > 0) {
        layers.value = response.data.layers;
        
        // Procesamiento para la capa recién subida
        if (newLayerUploaded.value && lastUploadedLayer.value) {
          const newLayerIndex = layers.value.findIndex(layer => 
            layer.name === lastUploadedLayer.value.name || 
            layer.name.includes(lastUploadedLayer.value.name));
          
          if (newLayerIndex >= 0) {
            layers.value[newLayerIndex].isNew = true;
          } else if (layers.value.length > 0) {
            layers.value[0].isNew = true;
          }
        }
        
        // Ordenar por fecha (más recientes primero)
        layers.value.sort((a, b) => new Date(b.upload_date || b.created_at) - new Date(a.upload_date || a.created_at));
      } else {
        // Si la respuesta no contiene datos, usar datos simulados
        console.log('La respuesta del servidor no contiene datos. Usando simulados.');
        layers.value = generateMockLayers();
      }
    } catch (apiError) {
      console.error('Error al obtener capas del servidor:', apiError);
      layers.value = generateMockLayers();
      
      if (apiError.code === 'ERR_NETWORK' || apiError.code === 'ECONNABORTED') {
        backendAvailable.value = false;
      }
    }
  } catch (error) {
    console.error("Error general al cargar las capas:", error);
    loadError.value = "No se pudieron cargar las capas. Se muestran datos de ejemplo.";
    layers.value = generateMockLayers();
  } finally {
    isLoading.value = false;
  }
};

// Filtrar capas según la búsqueda
const filteredLayers = computed(() => {
  if (!searchQuery.value) {
    return layers.value;
  }
  
  const query = searchQuery.value.toLowerCase();
  return layers.value.filter(layer => 
    layer.name.toLowerCase().includes(query) || 
    (layer.description && layer.description.toLowerCase().includes(query))
  );
});

// Formatear fecha para mostrar
const formatDate = (dateString) => {
  if (!dateString) return 'Fecha desconocida';
  
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return dateString;
  
  return date.toLocaleString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Alternar la visibilidad del panel de capas en móviles
const toggleLayerPanel = () => {
  showLayerPanel.value = !showLayerPanel.value;
};

// Cargar las capas cuando se monte el componente
onMounted(async () => {
  // Comprobar si el usuario está autenticado
  const isAuthenticated = localStorage.getItem('authenticated') === 'true';
  if (!isAuthenticated) {
    router.push('/login');
    return;
  }
  
  // Cargar las capas existentes
  await fetchLayers();
});

// Nuevas propiedades y métodos para la gestión de eliminación de capas
const showDeleteModal = ref(false);
const layerToDelete = ref(null);
const showToast = ref(false);
const toastType = ref('success');
const toastMessage = ref('');

const confirmDeleteLayer = (layer) => {
  layerToDelete.value = layer;
  showDeleteModal.value = true;
};

const executeDelete = async () => {
  try {
    await deleteLayer(layerToDelete.value);
    showDeleteModal.value = false;
    showToast.value = true;
    toastType.value = 'success';
    toastMessage.value = 'Capa eliminada correctamente';
  } catch (error) {
    showToast.value = true;
    toastType.value = 'error';
    toastMessage.value = 'No se pudo eliminar la capa';
  } finally {
    setTimeout(() => {
      showToast.value = false;
    }, 3000);
  }
};

// Función para eliminar una capa
const deleteLayer = async (layer) => {
  try {
    const layerName = layer.name;
    const response = await axios.delete(`${API_URL}/layers/${layerName}`);
    
    if (response.data.success) {
      // Eliminar la capa de la lista local
      layers.value = layers.value.filter(l => l.name !== layerName);
      showToast.value = true;
      toastType.value = 'success';
      toastMessage.value = `La capa ${layerName} ha sido eliminada correctamente`;
      
      // Ocultar el toast después de 3 segundos
      setTimeout(() => {
        showToast.value = false;
      }, 3000);
    } else {
      throw new Error(response.data.message || 'Error al eliminar la capa');
    }
  } catch (error) {
    console.error('Error al eliminar la capa:', error);
    showToast.value = true;
    toastType.value = 'error';
    toastMessage.value = `Error al eliminar la capa: ${error.response?.data?.message || error.message}`;
    
    // Ocultar el toast después de 3 segundos
    setTimeout(() => {
      showToast.value = false;
    }, 3000);
  }
};

// Función para generar datos simulados (si es necesario)
const generateMockLayers = () => {
  return [
    {
      id: `mock-1`,
      name: 'territorios_28',
      description: 'Capa de territorios sembrando datos',
      upload_date: new Date(Date.now() - 1000000).toISOString(),
      features_count: 28,
      preview_url: 'http://31.97.8.51:8082/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sembrando:territorios_28',
      file_size: '1.2 MB',
      isNew: false
    },
    {
      id: `mock-2`,
      name: 'unidades_riego',
      description: 'Unidades de riego en México',
      upload_date: new Date(Date.now() - 5000000).toISOString(),
      features_count: 124,
      preview_url: 'http://31.97.8.51:8082/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=sembrando:unidades_riego',
      file_size: '3.5 MB',
      isNew: false
    }
  ];
};

// Función para ir al dashboard
const goToDashboard = () => {
  router.push('/map'); // Cambiamos /dashboard por /map que es la ruta que muestra el visor
};
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Encabezado con navegación de regreso -->
    <header class="bg-white shadow-md">
      <div class="container mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <router-link to="/" class="flex items-center text-green-600 hover:text-green-700 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span class="ml-2 font-medium">Volver al inicio</span>
          </router-link>
          <h1 class="text-xl sm:text-2xl font-bold text-gray-800">Subir nueva capa</h1>
        </div>
        <div class="flex items-center space-x-4">
          <!-- Nuevo botón para ir al visor -->
          <button 
            @click="goToDashboard"
            class="flex items-center px-4 py-2 bg-gradient-to-r from-green-600 to-green-700 
                   text-white font-medium rounded-lg shadow-md hover:shadow-lg 
                   transform hover:-translate-y-0.5 active:translate-y-0 
                   transition-all duration-300 group"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              class="h-5 w-5 mr-2 group-hover:animate-pulse" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path 
                stroke-linecap="round" 
                stroke-linejoin="round" 
                stroke-width="2" 
                d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
              />
            </svg>
            <span class="relative">
              Ir al visor
              <span class="absolute bottom-0 left-0 w-full h-0.5 bg-white transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left"></span>
            </span>
          </button>
          <img 
            src="@/components/images/logotipo.png" 
            alt="Logotipo Sembrando Datos" 
            class="h-10 sm:h-12 w-auto object-contain"
          />
        </div>
      </div>
    </header>

    <main class="container mx-auto px-4 py-8">
      <!-- Layout usando grid para balance entre formulario y panel de capas -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Columna izquierda: Formulario de subida -->
        <div class="space-y-8">
          <!-- Instrucciones -->
          <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Instrucciones para subir capas
            </h2>
            <div class="space-y-3 text-gray-700">
              <p>Para subir una nueva capa al geoportal, siga los siguientes pasos:</p>
              <ol class="list-decimal pl-5 space-y-2">
                <li>Prepare su <strong>archivo shapefile</strong> completo (debe incluir al menos .shp, .shx, .dbf y .prj)</li>
                <li>Comprima todos los archivos en un <strong>archivo ZIP</strong></li>
                <li>Seleccione o arrastre el archivo ZIP en el área indicada abajo</li>
                <li>Haga clic en el botón "Subir capa"</li>
              </ol>
              <p class="bg-blue-50 p-3 rounded border-l-4 border-blue-400 mt-4">
                <span class="font-medium text-blue-800">Nota:</span> La capa subida estará disponible después de ser procesada por el sistema.
              </p>
            </div>
          </div>
          
          <!-- Zona para subir archivos -->
          <div class="bg-white rounded-lg shadow-md p-6">
            <h3 class="text-lg font-medium text-gray-800 mb-4">Seleccionar archivo</h3>
            
            <!-- Área de drag & drop -->
            <div 
              @dragenter="handleDragEnter"
              @dragleave="handleDragLeave"
              @dragover="handleDragOver"
              @drop="handleDrop"
              @click="triggerFileInput"
              class="border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center cursor-pointer transition-all"
              :class="{
                'border-green-400 bg-green-50': isDragging,
                'border-gray-300 hover:border-green-400 hover:bg-green-50': !isDragging && !selectedFile,
                'border-green-500 bg-green-50': selectedFile
              }"
            >
              <input 
                type="file" 
                ref="fileInputRef"
                @change="handleFileSelect" 
                accept=".zip" 
                class="hidden" 
              />
              
              <!-- Estado: No hay archivo seleccionado -->
              <div v-if="!selectedFile" class="text-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <h4 class="text-lg font-medium text-gray-800 mb-1">
                  {{ isDragging ? 'Suelte el archivo aquí' : 'Arrastre y suelte su archivo ZIP' }}
                </h4>
                <p class="text-gray-500">O haga clic para seleccionar un archivo</p>
              </div>
              
              <!-- Estado: Archivo seleccionado -->
              <div v-else class="w-full">
                <div class="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <div class="ml-4 flex-1 overflow-hidden">
                    <h4 class="text-base font-medium text-gray-800 truncate">{{ fileName }}</h4>
                    <p class="text-sm text-gray-500">{{ fileSize }}</p>
                  </div>
                  <!-- Botón para cambiar archivo -->
                  <button 
                    @click.stop="selectedFile = null; fileName = ''; fileSize = ''"
                    class="ml-2 p-1 rounded-full hover:bg-red-100 text-red-500 transition-colors"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Mensajes de estado -->
            <div v-if="uploadStatus" 
                 class="mt-4 p-4 rounded-lg" 
                 :class="{
                   'bg-green-50 border-l-4 border-green-500': uploadStatus === 'success',
                   'bg-blue-50 border-l-4 border-blue-500': uploadStatus === 'uploading',
                   'bg-yellow-50 border-l-4 border-yellow-500': uploadStatus === 'warning',
                   'bg-red-50 border-l-4 border-red-500': uploadStatus === 'error'
                 }"
            >
              <div class="flex items-start">
                <!-- Icono de éxito -->
                <svg v-if="uploadStatus === 'success'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-500 mt-0.5 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <!-- Icono de subida en progreso -->
                <svg v-else-if="uploadStatus === 'uploading'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-500 mt-0.5 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clip-rule="evenodd" />
                </svg>
                <!-- Icono de advertencia -->
                <svg v-else-if="uploadStatus === 'warning'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-500 mt-0.5 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                <!-- Icono de error -->
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500 mt-0.5 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
                <span :class="{
                  'text-green-700': uploadStatus === 'success',
                  'text-blue-700': uploadStatus === 'uploading',
                  'text-yellow-700': uploadStatus === 'warning',
                  'text-red-700': uploadStatus === 'error'
                }">{{ statusMessage }}</span>
              </div>
            </div>
            
            <!-- Barra de progreso mejorada con información de etapas -->
            <div v-if="showProgressBar" class="mt-6 space-y-2">
              <div class="flex justify-between items-center">
                <div class="space-y-1">
                  <p class="text-sm font-medium text-gray-700">{{ processingStep === 'completed' ? 'Completado' : 'Procesando...' }}</p>
                  <p class="text-xs text-gray-500">{{ statusMessage }}</p>
                </div>
                <div class="text-right text-xs text-gray-500">
                  <p v-if="uploadProgress < 100">
                    {{ uploadProgress }}% {{ uploadProgress < 50 ? `(${formatUploadSpeed(uploadSpeed)})` : '' }}
                  </p>
                  <p v-if="uploadProgress < 50 && uploadProgress > 0 && estimatedTimeRemaining">
                    Tiempo restante: {{ formatTimeRemaining(estimatedTimeRemaining) }}
                  </p>
                </div>
              </div>

              <!-- Barra de progreso con colores según el estado -->
              <div class="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
                <div class="h-full rounded-full transition-all duration-300" 
                     :style="{width: `${uploadProgress}%`}" 
                     :class="{
                       'bg-green-500': uploadStatus === 'success' || processingStep === 'completed',
                       'bg-blue-500': uploadStatus === 'uploading' && processingStep !== 'completed',
                       'bg-red-500': uploadStatus === 'error'
                     }">
                </div>
              </div>
            </div>
            
            <!-- Botón para subir archivo -->
            <div class="mt-6 flex justify-end">
              <button 
                @click="uploadFile" 
                :disabled="isUploading || !selectedFile"
                class="px-4 py-2 bg-green-600 text-white rounded-lg shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <svg v-if="isUploading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0l-4 4m4-4v12" />
                </svg>
                {{ isUploading ? 'Subiendo...' : 'Subir capa' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Columna derecha: Panel de capas existentes -->
        <div class="space-y-6 bg-white rounded-lg shadow p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-semibold text-gray-700 flex items-center space-x-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              <span>Capas disponibles</span>
            </h2>
            <div class="relative">
              <input 
                v-model="searchQuery" 
                type="text" 
                placeholder="Buscar capas..." 
                class="pl-8 pr-4 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 absolute left-2.5 top-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          <!-- Lista de capas -->
          <div class="space-y-3 max-h-[calc(100vh-20rem)] overflow-y-auto pr-2">
            <div 
              v-for="layer in filteredLayers" 
              :key="layer.id" 
              class="bg-white border border-gray-200 rounded-md shadow-sm p-4 hover:shadow transition-shadow"
            >
              <div class="flex justify-between items-start">
                <div class="flex-1">
                  <h3 class="font-medium text-gray-800 flex items-center">
                    {{ layer.name }}
                    <span v-if="layer.isNew" class="ml-2 px-1.5 py-0.5 text-xs bg-green-100 text-green-800 rounded-full">
                      Nueva
                    </span>
                  </h3>
                  <div class="mt-1 grid grid-cols-2 gap-2 text-xs text-gray-500">
                    <div class="flex items-center">
                      <svg class="h-3.5 w-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {{ formatDate(layer.upload_date || layer.created_at) }}
                    </div>
                    <div class="flex items-center">
                      <svg class="h-3.5 w-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {{ layer.features_count || 0 }} elementos
                    </div>
                    <div class="flex items-center">
                      <svg class="h-3.5 w-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                      </svg>
                      {{ layer.file_size }}
                    </div>
                  </div>
                </div>
                <button 
                  @click="confirmDeleteLayer(layer)"
                  class="p-1.5 rounded-full hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors"
                  title="Eliminar capa"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Modal de confirmación -->
          <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
            <div class="bg-white rounded-lg p-6 max-w-sm mx-4 shadow-xl">
              <h3 class="text-lg font-medium text-gray-900 mb-4">Confirmar eliminación</h3>
              <p class="text-gray-600 mb-6">
                ¿Estás seguro de eliminar la capa "{{ layerToDelete?.name }}"?
              </p>
              <div class="flex justify-end space-x-3">
                <button 
                  @click="showDeleteModal = false"
                  class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                >
                  Cancelar
                </button>
                <button 
                  @click="executeDelete"
                  class="px-4 py-2 text-white bg-red-600 rounded-md hover:bg-red-700"
                >
                  Eliminar capa
                </button>
              </div>
            </div>
          </div>

          <!-- Toast de notificación -->
          <div 
            v-if="showToast"
            class="fixed bottom-4 right-4 px-4 py-3 rounded-lg shadow-lg flex items-center space-x-2"
            :class="toastType === 'success' ? 'bg-green-500' : 'bg-red-500'"
          >
            <svg v-if="toastType === 'success'" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <svg v-else class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span class="text-white">{{ toastMessage }}</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Estilos para el scrollbar del panel de capas */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: #10B981 #F3F4F6;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 5px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #F3F4F6;
  border-radius: 10px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: #10B981;
  border-radius: 10px;
}

/* Efectos de transición */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* Animación para el botón de refrescar */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Animación de pulso para la barra de progreso cuando está cerca del 100% */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

.bg-green-600 {
  animation: pulse 2s infinite;
}

/* Animación para la barra de progreso durante la subida */
@keyframes progress-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

.animate-progress-pulse {
  animation: progress-pulse 1.5s infinite;
}

/* Patrón de rayas para la fase de procesamiento */
.bg-stripes {
  background-image: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.15) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0.15) 75%,
    transparent 75%,
    transparent
  );
  background-size: 1rem 1rem;
  animation: stripe-animation 1s linear infinite;
}

@keyframes stripe-animation {
  0% {
    background-position: 1rem 0;
  }
  100% {
    background-position: 0 0;
  }
}

/* Nuevos estilos para el botón del visor */
@keyframes gentle-pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.9;
    transform: scale(1.05);
  }
}

.group-hover\:animate-pulse {
  animation: gentle-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Responsive enhancements */
@media (max-width: 1023px) {
  .grid-cols-1 > div:first-child {
    order: 2;
  }
  .grid-cols-1 > div:last-child {
    order: 1;
  }
}
</style>
