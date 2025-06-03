<script setup>
import { computed, ref, watch } from 'vue';
import FeatureDetailModal from './FeatureDetailModal.vue';

const props = defineProps({
  featureInfo: Object,
  selectedFeature: Object,
  loading: Boolean,
  error: String,
  showPanel: Boolean,
  activeLayer: Object
});

const emit = defineEmits(['close']);

// Diccionario para traducir nombres de atributos (clave original -> nombre mostrado)
const attributeLabels = {
  // Identificadores y claves
  'gid': 'ID',
  'id': 'ID',
  'fid': 'ID',
  'objectid': 'ID del Objeto',
  'cvegeo': 'Clave GEO',
  'cve_geo': 'Clave GEO',
  'cve_ent': 'Clave de Entidad',
  'cve_mun': 'Clave Municipal',
  'clave_mun': 'Clave Municipal',
  'clave mun': 'Clave Municipal',
  
  // Nombres y descripciones
  'nomgeo': 'Nombre Geográfico',
  'nom_geo': 'Nombre Geográfico',
  'nombre': 'Nombre',
  'nombre_territorio': 'Nombre del Territorio',
  'nom_ent': 'Nombre de Entidad',
  'nom_mun': 'Nombre de Municipio',
  'descripcion': 'Descripción',
  'desc': 'Descripción',
  
  // Atributos geográficos
  'area': 'Área',
  'superficie': 'Superficie',
  'superficie_ha': 'Superficie (ha)',
  'perimetro': 'Perímetro',
  'region': 'Región',
  'altitud': 'Altitud',
  'altitud_m': 'Altitud (m)',
  'coordenadas': 'Coordenadas',
  'latitud': 'Latitud',
  'longitud': 'Longitud',
  
  // Atributos agrícolas y ambientales
  'n_cultivos': 'Número de Cultivos',
  'cultivo_principal': 'Cultivo Principal',
  'cultivos': 'Cultivos',
  'temperatura': 'Temperatura',
  'temperatura_c': 'Temperatura (°C)',
  'precipitacion': 'Precipitación',
  'precipitacion_mm': 'Precipitación (mm)',
  'tipo_suelo': 'Tipo de Suelo',
  
  // Atributos sociales
  'poblacion': 'Población',
  'viviendas': 'Viviendas',
  'habitantes': 'Habitantes',
  'densidad': 'Densidad Poblacional',
  
  // Identificadores especiales
  'unicos': 'Identificadores Únicos',
  'Ãºnicos': 'Identificadores Únicos',
  'llave': 'Llave',
  'cve_localidad': 'Clave de Localidad',
  
  // Estados y fechas
  'estado': 'Estado',
  'municipio': 'Municipio',
  'fecha': 'Fecha',
  'fecha_registro': 'Fecha de Registro',
  'fecha_actualizacion': 'Fecha de Actualización',
  
  // Atributos económicos
  'valor': 'Valor',
  'valor_produccion': 'Valor de Producción',
  'produccion': 'Producción',
  'produccion_estimada': 'Producción Estimada'
};

// Prioridad de los atributos (los de menor número aparecerán primero)
const attributePriority = {
  'nombre_territorio': 1,
  'nombre': 2,
  'nomgeo': 3,
  'nom_geo': 4,
  'nom_ent': 5,
  'nom_mun': 6,
  'municipio': 7,
  'estado': 8,
  'region': 9,
  'cve_ent': 10,
  'cve_mun': 11,
  'clave_mun': 12,
  'cvegeo': 13,
  'superficie_ha': 14,
  'poblacion': 15,
  'n_cultivos': 16,
  'cultivo_principal': 17,
  'altitud_m': 18,
  'precipitacion_mm': 19,
  'temperatura_c': 20
};

// Categorías para agrupar atributos
const attributeCategories = {
  'identificacion': ['gid', 'id', 'fid', 'objectid', 'cvegeo', 'cve_geo', 'cve_ent', 'cve_mun', 'clave_mun', 'llave'],
  'general': ['nombre', 'nombre_territorio', 'nomgeo', 'nom_geo', 'nom_ent', 'nom_mun', 'descripcion', 'desc', 'municipio', 'estado', 'region'],
  'geografico': ['area', 'superficie', 'superficie_ha', 'perimetro', 'altitud', 'altitud_m', 'coordenadas', 'latitud', 'longitud'],
  'agricola': ['n_cultivos', 'cultivo_principal', 'cultivos', 'tipo_suelo', 'precipitacion', 'precipitacion_mm', 'temperatura', 'temperatura_c'],
  'social': ['poblacion', 'viviendas', 'habitantes', 'densidad'],
  'fechas': ['fecha', 'fecha_registro', 'fecha_actualizacion']
};

// Atributos que deberían ocultarse (técnicos o redundantes)
const hiddenAttributes = [
  'geom', 'geometry', 'the_geom', 'shape', 'bbox', 'shape_length', 'shape_area',
  'timestamp', 'created_at', 'updated_at', 'version', '_uid', '_version',
  'ogc_fid', 'json', 'xml', 'wkt'
];

// Título del panel según la capa activa
const panelTitle = computed(() => {
  if (props.loading) return 'Cargando información...';
  if (props.error) return 'Información';
  
  // Obtener un título adecuado basado en la capa activa
  if (props.activeLayer) {
    const name = props.activeLayer.get('name') || props.activeLayer.get('title');
    if (name) {
      // Formatear el nombre para hacerlo más legible
      return name
        .replace(/_/g, ' ')
        .replace(/:/g, ' - ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
    }
    return 'Información de la capa';
  }
  return 'Información';
});

// Decodificar texto con problemas de codificación
const decodeText = (text) => {
  if (typeof text !== 'string') return text;
  
  // Decodificar caracteres típicos que se encuentran mal codificados
  return text
    .replace(/Ã¡/g, 'á')
    .replace(/Ã©/g, 'é')
    .replace(/Ã­/g, 'í')
    .replace(/Ã³/g, 'ó')
    .replace(/Ãº/g, 'ú')
    .replace(/Ã/g, 'Á')
    .replace(/Ã‰/g, 'É')
    .replace(/Ã/g, 'Í')
    .replace(/Ã"/g, 'Ó')
    .replace(/Ãš/g, 'Ú')
    .replace(/Ã±/g, 'ñ')
    .replace(/Ã'/g, 'Ñ')  // Esto evita el problema con la comilla
    .replace(/Ã¼/g, 'ü')
    .replace(/Ãœ/g, 'Ü');
};

// Propiedades de la entidad seleccionada
const properties = computed(() => {
  if (!props.selectedFeature) return {};
  return props.selectedFeature.properties || {};
});

// Lista de propiedades para mostrar (excluyendo geometría y propiedades especiales)
const propertyList = computed(() => {
  if (!properties.value) return [];
  
  // Extraer los pares clave-valor y decodificar valores
  let entries = Object.entries(properties.value)
    .filter(([key]) => !key.startsWith('_') && !hiddenAttributes.includes(key.toLowerCase()))
    .map(([key, value]) => ({
      originalKey: key,
      key: formatPropertyName(key),
      label: attributeLabels[key.toLowerCase()] || formatPropertyName(key),
      value: formatPropertyValue(value),
      priority: attributePriority[key.toLowerCase()] || 100
    }));
  
  // Ordenar por prioridad (menor número = mayor prioridad)
  entries.sort((a, b) => a.priority - b.priority);
  
  // Agrupar por categorías
  const categorized = {
    general: [],
    identificacion: [],
    geografico: [],
    agricola: [],
    social: [],
    fechas: [],
    otros: []
  };
  
  // Asignar cada propiedad a su categoría
  entries.forEach(prop => {
    let assigned = false;
    for (const [category, keys] of Object.entries(attributeCategories)) {
      if (keys.includes(prop.originalKey.toLowerCase())) {
        categorized[category].push(prop);
        assigned = true;
        break;
      }
    }
    
    // Si no se asignó a ninguna categoría, va a "otros"
    if (!assigned) {
      categorized.otros.push(prop);
    }
  });
  
  return categorized;
});

// Formateo de nombres de propiedades (snake_case a Title Case)
const formatPropertyName = (name) => {
  if (!name) return '';
  
  // Verificar si existe un nombre traducido
  if (attributeLabels[name.toLowerCase()]) {
    return attributeLabels[name.toLowerCase()];
  }
  
  // Convertir de snake_case a palabras separadas y capitalizar
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Formateo de valores de propiedades
const formatPropertyValue = (value) => {
  if (value === null || value === undefined) return 'N/A';
  
  // Decodificar texto con problemas de codificación
  if (typeof value === 'string') {
    value = decodeText(value);
  }
  
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

// Mostrar todas las propiedades
const showAllProperties = ref(false);

// Cerrar el panel
const closePanel = () => {
  emit('close');
};

// Determinar si hay propiedades en una categoría
const hasCategoryProperties = (category) => {
  return propertyList.value[category] && propertyList.value[category].length > 0;
};

// Función para obtener el ícono según la categoría
const getCategoryIcon = (category) => {
  switch(category) {
    case 'general':
      return 'M10 19l-7-7m0 0l7-7m-7 7h18'; // Información general
    case 'identificacion':
      return 'M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2'; // Identificación
    case 'geografico':
      return 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7'; // Geográfico
    case 'agricola':
      return 'M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064'; // Agrícola
    case 'social':
      return 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z'; // Social
    case 'fechas':
      return 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z'; // Fechas
    default:
      return 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'; // Otros
  }
};

// Título para cada categoría
const getCategoryTitle = (category) => {
  const titles = {
    general: 'Información General',
    identificacion: 'Identificación',
    geografico: 'Datos Geográficos',
    agricola: 'Datos Agrícolas',
    social: 'Datos Sociales',
    fechas: 'Fechas Relevantes',
    otros: 'Otros Datos'
  };
  
  return titles[category] || 'Otros Datos';
};

// Añadir estado para el modal
const showDetailModal = ref(false);

// Determinar las propiedades importantes para el resumen
const keyProperties = computed(() => {
  if (!properties.value) return [];
  
  // Lista de claves prioritarias para mostrar en el resumen
  const priorityKeys = [
    'nombre', 'nombre_territorio', 'nomgeo', 'nom_geo', 'nom_mun', 'nom_ent', 
    'municipio', 'estado', 'entidad', 'cvegeo', 'cve_geo', 'clave_mun', 'cve_mun',
    'region', 'n_cultivos', 'cultivo_principal', 'poblacion'
  ];
  
  // Filtrar propiedades para mostrar solo las importantes
  const filteredProps = Object.entries(properties.value)
    .filter(([key]) => priorityKeys.includes(key.toLowerCase()))
    .map(([key, value]) => ({
      key,
      label: attributeLabels[key.toLowerCase()] || formatPropertyName(key),
      value: formatPropertyValue(value),
      priority: attributePriority[key.toLowerCase()] || 100
    }))
    .sort((a, b) => {
      // Ordenar según la posición en la lista de prioridades
      const indexA = priorityKeys.indexOf(a.key.toLowerCase());
      const indexB = priorityKeys.indexOf(b.key.toLowerCase());
      return indexA - indexB;
    });

  // Buscar cultivo principal si no está explícitamente
  if (!filteredProps.some(prop => prop.key.toLowerCase() === 'cultivo_principal') && properties.value) {
    // Buscar en campos que puedan contener información de cultivos
    const cultivoCandidates = Object.entries(properties.value)
      .filter(([key, value]) => 
        typeof value === 'string' && 
        (key.toLowerCase().includes('cultivo') || 
         key.toLowerCase().includes('crop') ||
         key.toLowerCase().includes('sembrado'))
      );
    
    if (cultivoCandidates.length > 0) {
      filteredProps.push({
        key: 'cultivo_principal',
        label: 'Cultivo Principal',
        value: formatPropertyValue(cultivoCandidates[0][1]),
        priority: 15  // Prioridad alta
      });
    }
  }
  
  return filteredProps.slice(0, 5); // Mostrar máximo 5 propiedades en el resumen
});

// Función para abrir el modal con información completa
const openDetailModal = () => {
  showDetailModal.value = true;
};

// Función para cerrar el modal
const closeDetailModal = () => {
  showDetailModal.value = false;
};

// Añadir propiedad computada para verificar si hay información de características
const hasFeatureInfo = computed(() => {
  return props.featureInfo && 
         props.featureInfo.success && 
         props.featureInfo.features && 
         props.featureInfo.features.length > 0 &&
         props.selectedFeature;
});

// Computed para verificar si la capa activa está visible
const isLayerVisible = computed(() => {
  if (!props.activeLayer) return false;
  return props.activeLayer.getVisible();
});

// Observar cambios en la capa activa para verificar su visibilidad
watch(() => props.activeLayer, (newLayer) => {
  if (!newLayer || !newLayer.getVisible()) {
    // Si la capa se desactiva o cambia a una inactiva, cerrar el panel
    emit('close');
  }
}, { immediate: true });
</script>

<template>
  <div v-if="showPanel && (hasFeatureInfo || (loading && !error)) && isLayerVisible" 
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
      
      <!-- Mensaje de error - Solo se muestra para errores informativos, no para "No hay capas visibles" -->
      <div v-else-if="error && !error.includes('No hay capas visibles') && !error.includes('No se encontraron características')" 
           class="bg-red-50 p-4 rounded-lg text-red-600 my-4">
        <p class="flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ error }}
        </p>
      </div>
      
      <!-- Resumen de información (versión mejorada) -->
      <div v-else-if="selectedFeature" class="space-y-4">
        <!-- Tarjeta de resumen mejorada -->
        <div class="bg-white rounded-lg shadow border-l-4 border-green-600 p-4 space-y-3">
          <h3 class="text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-1">
            Resumen de información
          </h3>
          
          <!-- Propiedades clave -->
          <div v-for="property in keyProperties" :key="property.key" class="py-1">
            <div class="flex items-start">
              <span class="font-semibold text-gray-700 min-w-[130px]">{{ property.label }}:</span>
              <span class="text-gray-800 ml-2">{{ property.value }}</span>
            </div>
          </div>
          
          <!-- Botón para ver información completa -->
          <button 
            @click="openDetailModal"
            class="mt-3 w-full py-2.5 px-4 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors duration-300 flex items-center justify-center space-x-2 shadow-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Ver información completa</span>
          </button>
        </div>
        
        <!-- Mapa en miniatura o vista previa si está disponible -->
        <div v-if="selectedFeature.geometry" class="bg-gray-50 rounded-lg p-2 border border-gray-200">
          <p class="text-xs text-gray-500 mb-1">Ubicación geográfica:</p>
          <div class="h-32 bg-green-50 rounded overflow-hidden flex items-center justify-center">
            <span class="text-green-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </span>
          </div>
        </div>
      </div>
      
      <!-- Caso sin datos - No debería mostrarse debido a la condición v-if del componente -->
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
  
  <!-- Usar el componente modal -->
  <FeatureDetailModal 
    :show="showDetailModal && isLayerVisible"
    :feature="selectedFeature"
    :activeLayer="activeLayer"
    :attributeLabels="attributeLabels"
    @close="closeDetailModal"
  />
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

.property-item {
  padding-bottom: 0.5rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
}

.property-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

/* Animación del modal */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .bg-white,
.modal-leave-to .bg-white {
  transform: scale(0.9);
  opacity: 0;
}

@keyframes modal-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-modal-in {
  animation: modal-in 0.3s forwards;
}
</style>
