<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

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
  uploadStatus.value = null;
  statusMessage.value = '';

  try {
    const formData = new FormData();
    formData.append('file', selectedFile.value); // Asegurarse que el campo se llama 'file'

    console.log(`Enviando solicitud a: ${API_URL}/upload-shapefile`);
    const response = await axios.post(`${API_URL}/upload-shapefile`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      // Aumentar el timeout para archivos grandes
      timeout: 60000 // 60 segundos
    });

    // Manejar respuesta exitosa
    uploadStatus.value = 'success';
    statusMessage.value = response.data.message || 'Archivo subido correctamente. La capa estará disponible en breve.';
    
    // Resetear el formulario después de 3 segundos en caso de éxito
    setTimeout(() => {
      selectedFile.value = null;
      fileName.value = '';
      fileSize.value = '';
    }, 3000);
  } catch (error) {
    // Manejar error con información más detallada
    uploadStatus.value = 'error';
    console.error('Error detallado:', error);
    
    if (error.code === 'ECONNABORTED') {
      statusMessage.value = 'La conexión ha expirado. El archivo puede ser demasiado grande o el servidor está tardando demasiado en responder.';
    } else if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
      statusMessage.value = `Error de conexión: No se pudo conectar al servidor en ${API_URL}. Verifique que el backend esté en ejecución.`;
    } else if (error.response) {
      statusMessage.value = `Error ${error.response.status}: ${error.response.data.error || 'No se pudo procesar el archivo'}`;
    } else if (error.request) {
      statusMessage.value = 'Error: No se recibió respuesta del servidor. Verifique que el backend esté en ejecución.';
    } else {
      statusMessage.value = `Error: ${error.message}`;
    }
  } finally {
    isUploading.value = false;
  }
};

// Comprobar si el usuario está autenticado
onMounted(() => {
  const isAuthenticated = localStorage.getItem('authenticated') === 'true';
  if (!isAuthenticated) {
    router.push('/login');
  }
});
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
        <div class="flex items-center">
          <img 
            src="@/components/images/logotipo.png" 
            alt="Logotipo Sembrando Datos" 
            class="h-10 sm:h-12 w-auto object-contain"
          />
        </div>
      </div>
    </header>

    <main class="container mx-auto px-4 py-8">
      <div class="max-w-3xl mx-auto">
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
                  <h4 class="text-md font-medium text-gray-800 truncate">{{ fileName }}</h4>
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
                 'bg-red-50 border-l-4 border-red-500': uploadStatus === 'error'
               }"
          >
            <div class="flex">
              <div class="flex-shrink-0">
                <svg v-if="uploadStatus === 'success'" class="h-5 w-5 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <svg v-else class="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="ml-3">
                <p :class="{
                  'text-green-700': uploadStatus === 'success',
                  'text-red-700': uploadStatus === 'error'
                }">{{ statusMessage }}</p>
              </div>
            </div>
          </div>
          
          <!-- Botón de acción -->
          <div class="mt-6 flex justify-center">
            <button 
              @click="uploadFile" 
              :disabled="isUploading || !selectedFile"
              class="px-6 py-3 bg-green-600 text-white rounded-lg shadow-md hover:bg-green-700 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <!-- Indicador de carga -->
              <svg v-if="isUploading" class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span v-else>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L9 8m4-4v12" />
                </svg>
              </span>
              <span>{{ isUploading ? 'Subiendo...' : 'Subir Capa' }}</span>
            </button>
          </div>
          
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Estilos específicos para este componente */
.list-decimal {
  list-style-type: decimal;
}
</style>
