<script setup>
import { computed } from 'vue';

const props = defineProps({
  show: Boolean,
  feature: Object,
  activeLayer: Object,
  attributeLabels: Object
});

const emit = defineEmits(['close']);

// Diccionario para categorizar atributos
const attributeCategories = {
  'identificacion': ['gid', 'id', 'fid', 'objectid', 'cvegeo', 'cve_geo', 'cve_ent', 'cve_mun', 'clave_mun', 'llave'],
  'general': ['nombre', 'nombre_territorio', 'nomgeo', 'nom_geo', 'nom_ent', 'nom_mun', 'descripcion', 'desc', 'municipio', 'estado', 'region'],
  'geografico': ['area', 'superficie', 'superficie_ha', 'perimetro', 'altitud', 'altitud_m', 'coordenadas', 'latitud', 'longitud'],
  'agricola': ['n_cultivos', 'cultivo_principal', 'cultivos', 'tipo_suelo', 'precipitacion', 'precipitacion_mm', 'temperatura', 'temperatura_c'],
  'social': ['poblacion', 'viviendas', 'habitantes', 'densidad'],
  'fechas': ['fecha', 'fecha_registro', 'fecha_actualizacion']
};

// Atributos que deberían ocultarse
const hiddenAttributes = [
  'geom', 'geometry', 'the_geom', 'shape', 'bbox', 'shape_length', 'shape_area',
  'timestamp', 'created_at', 'updated_at', 'version', '_uid', '_version',
  'ogc_fid', 'json', 'xml', 'wkt'
];

// Título del modal según la entidad y capa
const modalTitle = computed(() => {
  if (!props.feature) return 'Información detallada';
  
  // Intentar obtener un nombre descriptivo de la entidad
  const name = props.feature.properties?.nombre_territorio || 
               props.feature.properties?.nombre || 
               props.feature.properties?.nomgeo || 
               props.feature.properties?.municipio;
  
  if (name) return `Información detallada: ${name}`;
  
  // Si no hay nombre, usar el nombre de la capa
  if (props.activeLayer) {
    return `Información de ${props.activeLayer.get('name') || props.activeLayer.get('title') || 'la capa'}`;
  }
  
  return 'Información detallada';
});

// Propiedades de la entidad organizadas por categorías
const categorizedProperties = computed(() => {
  if (!props.feature || !props.feature.properties) return {};
  
  const properties = props.feature.properties;
  const categorized = {
    general: [],
    identificacion: [],
    geografico: [],
    agricola: [],
    social: [],
    fechas: [],
    otros: []
  };
  
  // Procesar cada propiedad
  Object.entries(properties).forEach(([key, value]) => {
    // Omitir propiedades ocultas y geométricas
    if (hiddenAttributes.includes(key.toLowerCase()) || key.startsWith('_')) {
      return;
    }
    
    // Formatear valor según su tipo
    const formattedValue = formatPropertyValue(value);
    
    // Determinar la categoría a la que pertenece
    let assigned = false;
    
    for (const [category, keys] of Object.entries(attributeCategories)) {
      if (keys.includes(key.toLowerCase())) {
        categorized[category].push({
          key,
          label: translatePropertyName(key),
          value: formattedValue
        });
        assigned = true;
        break;
      }
    }
    
    // Si no se asignó a ninguna categoría, va a "otros"
    if (!assigned) {
      categorized.otros.push({
        key,
        label: translatePropertyName(key),
        value: formattedValue
      });
    }
  });
  
  return categorized;
});

// Traducir nombre de propiedad
const translatePropertyName = (key) => {
  // Verificar si existe un nombre traducido en los props
  if (props.attributeLabels && props.attributeLabels[key.toLowerCase()]) {
    return props.attributeLabels[key.toLowerCase()];
  }
  
  // Diccionario local por si no se pasan traducciones
  const dictionary = {
    'gid': 'ID',
    'id': 'ID',
    'fid': 'ID',
    'objectid': 'ID del Objeto',
    'cvegeo': 'Clave GEO',
    'cve_geo': 'Clave GEO',
    'cve_ent': 'Clave de Entidad',
    'cve_mun': 'Clave Municipal',
    'clave_mun': 'Clave Municipal',
    'nomgeo': 'Nombre Geográfico',
    'nom_geo': 'Nombre Geográfico',
    'nombre': 'Nombre',
    'nombre_territorio': 'Nombre del Territorio',
    'nom_ent': 'Nombre de Entidad',
    'nom_mun': 'Nombre de Municipio',
    'area': 'Área',
    'superficie': 'Superficie',
    'superficie_ha': 'Superficie (ha)',
    'n_cultivos': 'Número de Cultivos',
    'region': 'Región',
    'poblacion': 'Población',
    'fecha': 'Fecha',
    'municipio': 'Municipio',
    'estado': 'Estado',
    'entidad': 'Entidad'
  };
  
  if (dictionary[key.toLowerCase()]) {
    return dictionary[key.toLowerCase()];
  }
  
  // Si no hay traducción, convertir de snake_case a Title Case
  return key.split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Formatear valor de propiedad
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
  
  // Decodificar texto con problemas de codificación
  if (typeof value === 'string') {
    return decodeText(value);
  }
  
  return String(value);
};

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
    .replace(/Ã'/g, 'Ñ')
    .replace(/Ã¼/g, 'ü')
    .replace(/Ãœ/g, 'Ü');
};

// Obtener el ícono para cada categoría
const getCategoryIcon = (category) => {
  switch(category) {
    case 'general':
      return 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'; // Info
    case 'identificacion':
      return 'M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2'; // ID
    case 'geografico':
      return 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7'; // Mapa
    case 'agricola':
      return 'M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064'; // Planta
    case 'social':
      return 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z'; // Personas
    case 'fechas':
      return 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z'; // Calendario
    default:
      return 'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z'; // Estrella
  }
};

// Obtener título para cada categoría
const getCategoryTitle = (category) => {
  const titles = {
    general: 'Información General',
    identificacion: 'Identificación',
    geografico: 'Datos Geográficos',
    agricola: 'Datos Agrícolas',
    social: 'Datos Sociales',
    fechas: 'Fechas',
    otros: 'Otros Datos'
  };
  
  return titles[category] || 'Otros Datos';
};

// Cerrar el modal
const closeModal = () => {
  emit('close');
};
</script>

<template>
  <Transition name="modal">
    <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col animate-modal-in">
        <!-- Encabezado del modal -->
        <div class="p-5 bg-gradient-to-r from-blue-600 to-indigo-700 text-white flex items-center justify-between">
          <h2 class="text-xl font-medium flex items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>{{ modalTitle }}</span>
          </h2>
          <button @click="closeModal" class="p-1 hover:bg-white/20 rounded-full transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Contenido del modal con scroll -->
        <div class="flex-1 overflow-y-auto p-5">
          <div v-if="!feature" class="flex items-center justify-center h-40">
            <p class="text-gray-500">No hay información disponible</p>
          </div>
          
          <div v-else>
            <!-- Propiedades organizadas por categorías -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <template v-for="(category, index) in ['general', 'identificacion', 'geografico', 'agricola', 'social', 'fechas', 'otros']" :key="category">
                <div v-if="categorizedProperties[category] && categorizedProperties[category].length > 0" class="space-y-3">
                  <!-- Título de la categoría -->
                  <div class="flex items-center text-sm font-medium text-gray-700 mb-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getCategoryIcon(category)" />
                    </svg>
                    <h3>{{ getCategoryTitle(category) }}</h3>
                  </div>
                  
                  <!-- Card con propiedades de la categoría -->
                  <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 space-y-3">
                    <div v-for="property in categorizedProperties[category]" 
                         :key="property.key"
                         class="property-item border-b border-gray-100 pb-2 last:border-0 last:pb-0">
                      <span class="font-medium text-gray-700 block">{{ property.label }}:</span>
                      <span class="text-gray-800">{{ property.value }}</span>
                    </div>
                  </div>
                </div>
              </template>
            </div>
            
            <!-- ID de la entidad si existe (al final) -->
            <div v-if="feature.id" class="mt-6 bg-gray-50 p-3 rounded-lg">
              <span class="text-xs text-gray-500 block">ID de la entidad</span>
              <span class="font-medium text-gray-800">{{ feature.id }}</span>
            </div>
          </div>
        </div>
        
        <!-- Pie del modal -->
        <div class="p-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
          <span class="text-sm text-gray-500">
            {{ activeLayer ? activeLayer.get('name') || activeLayer.get('title') : 'Capa' }}
          </span>
          <button @click="closeModal" class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors">
            Cerrar
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
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

.property-item {
  margin-bottom: 0.5rem;
}
</style>
