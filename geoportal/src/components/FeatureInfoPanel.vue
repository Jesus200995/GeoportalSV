<script setup>
import { computed } from 'vue';

const props = defineProps({
  featureInfo: Object,
  selectedFeature: Object,
  loading: Boolean,
  error: String,
  showPanel: Boolean,
  activeLayer: Object
});

const emit = defineEmits(['close']);

// Título del panel según la capa activa
const panelTitle = computed(() => {
  if (props.loading) return 'Cargando información...';
  if (props.error) return 'Información';
  if (props.activeLayer) return props.activeLayer.get('name') || props.activeLayer.get('title') || 'Información de capa';
  return 'Información';
});

// Propiedades de la entidad seleccionada
const properties = computed(() => {
  if (!props.selectedFeature) return {};
  return props.selectedFeature.properties || {};
});

// Lista de propiedades para mostrar (excluyendo geometría y propiedades especiales)
const propertyList = computed(() => {
  if (!properties.value) return [];
  
  // Filtrar propiedades que no queremos mostrar
  return Object.entries(properties.value)
    .filter(([key]) => !key.startsWith('_') && key !== 'geometry' && key !== 'bbox')
    .map(([key, value]) => ({
      key: formatPropertyName(key),
      originalKey: key,
      value: formatPropertyValue(value)
    }));
});

// Formateo de nombres de propiedades (snake_case a Title Case)
const formatPropertyName = (name) => {
  if (!name) return '';
  
  // Convertir de snake_case a palabras separadas y capitalizar
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Formateo de valores de propiedades
const formatPropertyValue = (value) => {
  if (value === null || value === undefined) return 'N/A';
  
  // Formateo según tipo
  if (typeof value === 'number') {
    // Formatear números con separadores de miles y decimales según sea necesario
    return value % 1 === 0 
      ? value.toLocaleString('es-MX') 
      : value.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  
  if (typeof value === 'boolean') {
    return value ? 'Sí' : 'No';
  }
  
  // Intentar formatear fechas
  if (typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}/)) {
    try {
      const date = new Date(value);
      if (!isNaN(date)) {
        return date.toLocaleDateString('es-MX', { 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        });
      }
    } catch (e) {
      // Si falla el formateo de fecha, devolver el valor original
    }
  }
  
  return String(value);
};

// Cerrar el panel
const closePanel = () => {
  emit('close');
};
</script>

<template>
  <div v-if="showPanel" 
       class="feature-info-panel absolute top-20 right-0 bottom-8 w-80 sm:w-96 bg-white shadow-lg rounded-l-xl z-30 overflow-hidden flex flex-col transition-all duration-300 transform">
    
    <!-- Encabezado del panel -->
    <div class="p-4 bg-gradient-to-r from-emerald-500 to-green-600 text-white flex items-center justify-between">
      <h2 class="font-medium truncate">
        {{ panelTitle }}
      </h2>
      <button @click="closePanel" 
              class="p-1 hover:bg-white/20 rounded-full transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    
    <!-- Contenido del panel -->
    <div class="flex-1 overflow-y-auto p-4">
      <!-- Estado de carga -->
      <div v-if="loading" class="flex flex-col items-center justify-center h-full">
        <div class="w-10 h-10 border-2 border-t-green-500 border-green-200 rounded-full animate-spin mb-3"></div>
        <p class="text-gray-500 text-sm">Cargando información...</p>
      </div>
      
      <!-- Mensaje de error -->
      <div v-else-if="error" class="bg-red-50 p-4 rounded-lg text-red-600 my-4">
        <p class="flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ error }}
        </p>
      </div>
      
      <!-- Detalles de la entidad -->
      <div v-else-if="selectedFeature && propertyList.length > 0" class="space-y-6">
        <!-- ID de la entidad si existe -->
        <div v-if="selectedFeature.id" class="bg-gray-50 p-3 rounded-lg">
          <span class="text-xs text-gray-500 block">ID</span>
          <span class="font-medium text-gray-800">{{ selectedFeature.id }}</span>
        </div>
        
        <!-- Lista de propiedades -->
        <div class="space-y-4">
          <div v-for="(property, index) in propertyList" 
               :key="property.originalKey"
               class="border-b border-gray-100 pb-3 last:border-0">
            <span class="text-xs text-gray-500 block">{{ property.key }}</span>
            <span class="font-medium text-gray-800">{{ property.value }}</span>
          </div>
        </div>
      </div>
      
      <!-- Caso sin datos -->
      <div v-else class="flex flex-col items-center justify-center h-full">
        <svg class="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0  11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-gray-500 text-center">No hay información disponible para esta ubicación</p>
      </div>
    </div>
    
    <!-- Pie del panel -->
    <div class="p-3 bg-gray-50 text-center text-xs text-gray-500">
      <span v-if="featureInfo && featureInfo.timestamp">
        Consultado: {{ new Date(featureInfo.timestamp).toLocaleString() }}
      </span>
      <span v-else>
        {{ activeLayer ? activeLayer.get('name') : 'Capa' }} - Haga clic en el mapa para ver información
      </span>
    </div>
  </div>
</template>

<style scoped>
.feature-info-panel {
  box-shadow: -4px 0 15px rgba(0, 0, 0, 0.1);
  animation: slide-in 0.3s forwards;
}

@keyframes slide-in {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

/* Estilo para el scrollbar */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: #10B981 #E5E7EB;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #E5E7EB;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: #10B981;
  border-radius: 3px;
}
</style>
