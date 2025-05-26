<script setup>
import { computed, ref, onMounted, watch } from 'vue';
import * as XLSX from 'xlsx';

const props = defineProps({
  show: Boolean,
  feature: Object,
  activeLayer: Object,
  attributeLabels: Object
});

const emit = defineEmits(['close']);

// Datos adicionales (simulados) que se obtendrían de la base de datos
const additionalData = ref(null);
const loadingAdditionalData = ref(false);
const dataError = ref(null);

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
  
  if (name) return `Información completa: ${name}`;
  
  // Si no hay nombre, usar el nombre de la capa
  if (props.activeLayer) {
    return `Información completa de ${props.activeLayer.get('name') || props.activeLayer.get('title') || 'la capa'}`;
  }
  
  return 'Información detallada';
});

// Propiedades combinadas (originales + adicionales)
const combinedProperties = computed(() => {
  if (!props.feature || !props.feature.properties) return {};
  
  // Combinar propiedades originales con adicionales
  const original = props.feature.properties;
  const additional = additionalData.value || {};
  
  return { ...original, ...additional };
});

// Propiedades de la entidad organizadas por categorías
const categorizedProperties = computed(() => {
  if (!props.feature || !props.feature.properties) return {};
  
  const properties = combinedProperties.value;
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

// Todas las propiedades sin categorizar para mostrar en la vista completa
const allProperties = computed(() => {
  if (!props.feature || !props.feature.properties) return [];
  
  const properties = combinedProperties.value;
  
  return Object.entries(properties)
    .filter(([key]) => !hiddenAttributes.includes(key.toLowerCase()) && !key.startsWith('_'))
    .map(([key, value]) => ({
      key,
      label: translatePropertyName(key),
      value: formatPropertyValue(value)
    }))
    .sort((a, b) => a.label.localeCompare(b.label));
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
    .replace(/Ãü/g, 'ü')
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

// Modo de visualización (categorizado o completo)
const viewMode = ref('categorized'); // 'categorized' o 'complete'

// Cerrar el modal
const closeModal = () => {
  emit('close');
  // Resetear a vista categorizada al cerrar
  viewMode.value = 'categorized';
};

// Función para cargar datos adicionales de la entidad
const fetchAdditionalData = async () => {
  // Solo cargar si hay feature y no se han cargado ya
  if (!props.feature || additionalData.value) return;
  
  try {
    loadingAdditionalData.value = true;
    dataError.value = null;
    
    // Simular una llamada a la API para obtener datos adicionales
    // En un entorno real, esto sería una llamada fetch a tu backend
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // ID de la entidad (para simular una búsqueda en base de datos)
    const featureId = props.feature.id || 
                     props.feature.properties?.gid || 
                     props.feature.properties?.fid || 
                     Math.floor(Math.random() * 1000);
    
    // Datos simulados adicionales que complementan los datos básicos
    // En un entorno real, estos vendrían de tu base de datos
    additionalData.value = {
      // Datos económicos
      ingreso_promedio: Math.floor(Math.random() * 12000) + 5000,
      pib_local: (Math.random() * 100 + 50).toFixed(2) + ' millones MXN',
      actividad_economica_principal: ['Agricultura', 'Ganadería', 'Comercio', 'Turismo', 'Industria'][Math.floor(Math.random() * 5)],
      tasa_desempleo: (Math.random() * 10).toFixed(2) + '%',
      empresas_registradas: Math.floor(Math.random() * 500) + 10,
      
      // Datos agrícolas extendidos
      superficie_sembrada: Math.floor(Math.random() * 10000) + 1000 + ' hectáreas',
      rendimiento_promedio: (Math.random() * 10 + 2).toFixed(2) + ' ton/ha',
      sistema_riego: ['Aspersión', 'Goteo', 'Inundación', 'Temporal', 'Mixto'][Math.floor(Math.random() * 5)],
      cultivos_alternos: ['Maíz, Frijol', 'Trigo, Cebada', 'Chile, Jitomate', 'Nopal, Maguey', 'Café, Cacao'][Math.floor(Math.random() * 5)],
      produccion_anual: Math.floor(Math.random() * 50000) + 5000 + ' toneladas',
      valor_produccion_anual: '$' + (Math.floor(Math.random() * 100000000) + 1000000).toLocaleString() + ' MXN',
      periodo_cosecha: ['Enero-Marzo', 'Abril-Junio', 'Julio-Septiembre', 'Octubre-Diciembre', 'Todo el año'][Math.floor(Math.random() * 5)],
      
      // Datos ambientales extendidos
      biodiversidad: ['Alta', 'Media', 'Baja'][Math.floor(Math.random() * 3)],
      areas_protegidas: Math.floor(Math.random() * 3) === 0 ? 'Sí' : 'No',
      especies_endemicas: Math.floor(Math.random() * 20) + 5,
      temperatura_minima: (Math.random() * 15).toFixed(1) + '°C',
      temperatura_maxima: (20 + Math.random() * 15).toFixed(1) + '°C',
      humedad_promedio: (40 + Math.random() * 40).toFixed(1) + '%',
      calidad_aire: ['Buena', 'Regular', 'Mala'][Math.floor(Math.random() * 3)],
      indice_erosion: ['Bajo', 'Moderado', 'Alto', 'Severo'][Math.floor(Math.random() * 4)],
      
      // Datos sociales extendidos
      grupos_indigenas: ['Nahua', 'Maya', 'Zapoteco', 'Mixteco', 'Otomí', 'Ninguno'][Math.floor(Math.random() * 6)],
      idiomas_hablados: ['Español', 'Español y Náhuatl', 'Español y Maya', 'Español y lenguas indígenas'][Math.floor(Math.random() * 4)],
      escolaridad_promedio: (6 + Math.random() * 6).toFixed(1) + ' años',
      centros_educativos: Math.floor(Math.random() * 20) + 1,
      centros_salud: Math.floor(Math.random() * 5) + 1,
      acceso_internet: (Math.random() * 100).toFixed(1) + '%',
      
      // Infraestructura
      vias_comunicacion: ['Carretera federal, caminos rurales', 'Autopista, terracería', 'Caminos rurales'][Math.floor(Math.random() * 3)],
      distancia_ciudad: Math.floor(Math.random() * 100) + 5 + ' km',
      transporte_publico: Math.floor(Math.random() * 2) === 0 ? 'Sí' : 'No',
      acceso_agua_potable: (50 + Math.random() * 50).toFixed(1) + '%',
      acceso_electricidad: (70 + Math.random() * 30).toFixed(1) + '%',
      
      // Datos sobre riesgos
      riesgo_inundacion: ['Bajo', 'Moderado', 'Alto', 'Muy alto'][Math.floor(Math.random() * 4)],
      riesgo_deslizamiento: ['Bajo', 'Moderado', 'Alto', 'Muy alto'][Math.floor(Math.random() * 4)],
      riesgo_incendio: ['Bajo', 'Moderado', 'Alto', 'Muy alto'][Math.floor(Math.random() * 4)],
      
      // Datos históricos y culturales
      fundacion: Math.floor(Math.random() * 500) + 1500,
      sitios_arqueologicos: Math.floor(Math.random() * 3),
      festividades_principales: ['Fiesta patronal', 'Día de la Independencia', 'Feria agrícola', 'Festival cultural'][Math.floor(Math.random() * 4)],
      artesanias: ['Alfarería', 'Textiles', 'Cestería', 'Talla en madera', 'Ninguna'][Math.floor(Math.random() * 5)],
      
      // Proyectos y programas
      programas_gubernamentales: Math.floor(Math.random() * 2) === 0 ? 'Sí' : 'No',
      proyectos_desarrollo: Math.floor(Math.random() * 2) === 0 ? 'Sí' : 'No',
      organizaciones_civiles: Math.floor(Math.random() * 5)
    };
    
  } catch (error) {
    console.error('Error al cargar datos adicionales:', error);
    dataError.value = 'No se pudieron cargar todos los datos complementarios.';
  } finally {
    loadingAdditionalData.value = false;
  }
};

// Cargar datos adicionales cuando se muestre el modal
onMounted(() => {
  if (props.show && props.feature) {
    fetchAdditionalData();
  }
});

// Observar cambios en props.show para cargar datos cuando se abra el modal
watch(() => props.show, (newValue) => {
  if (newValue && props.feature) {
    fetchAdditionalData();
  }
});

// Observar cambios en props.feature para cargar datos cuando cambie la feature seleccionada
watch(() => props.feature, (newValue) => {
  if (newValue && props.show) {
    // Resetear datos adicionales para la nueva feature
    additionalData.value = null;
    fetchAdditionalData();
  }
});

// Función para descargar información en formato Excel
const downloadExcel = () => {
  if (!props.feature || !combinedProperties.value) return;
  
  try {
    // Preparar los datos para el Excel
    const data = [];
    
    // Convertir propiedades a formato tabular para Excel
    Object.entries(combinedProperties.value).forEach(([key, value]) => {
      data.push({
        Atributo: translatePropertyName(key),
        Valor: typeof value === 'object' ? JSON.stringify(value) : value
      });
    });
    
    // Crear libro de trabajo y hoja
    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    
    // Ajustar ancho de columnas
    const wscols = [
      { wch: 30 }, // Ancho para columna de Atributo
      { wch: 50 }  // Ancho para columna de Valor
    ];
    worksheet['!cols'] = wscols;
    
    // Añadir la hoja al libro
    const sheetName = props.feature.properties?.nombre_territorio || 
                     props.feature.properties?.nombre || 
                     'Información del lugar';
    
    XLSX.utils.book_append_sheet(workbook, worksheet, sheetName.substring(0, 30)); // Limitar nombre a 30 caracteres
    
    // Generar archivo y descargar
    const fileName = `${sheetName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${new Date().getTime()}.xlsx`;
    XLSX.writeFile(workbook, fileName);
  } catch (error) {
    console.error('Error al generar archivo Excel:', error);
    alert('Hubo un problema al generar el archivo Excel. Por favor intente de nuevo.');
  }
};
</script>

<template>
  <Transition name="modal">
    <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-xl shadow-xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col animate-modal-in">
        <!-- Encabezado del modal con tema verde -->
        <div class="p-5 bg-gradient-to-r from-emerald-600 to-green-700 text-white flex items-center justify-between sticky top-0 z-10">
          <h2 class="text-xl font-medium flex items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>{{ modalTitle }}</span>
          </h2>
          
          <!-- Botones de modos de visualización -->
          <div class="flex items-center space-x-2 ml-4">
            <button 
              @click="viewMode = 'categorized'" 
              class="px-3 py-1.5 text-sm rounded-md transition-colors"
              :class="viewMode === 'categorized' ? 'bg-white/20' : 'hover:bg-white/10'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              Categorizado
            </button>
            <button 
              @click="viewMode = 'complete'" 
              class="px-3 py-1.5 text-sm rounded-md transition-colors"
              :class="viewMode === 'complete' ? 'bg-white/20' : 'hover:bg-white/10'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
              Vista completa
            </button>
          </div>
          
          <button @click="closeModal" class="p-1 hover:bg-white/20 rounded-full transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Indicador de carga de datos adicionales -->
        <div v-if="loadingAdditionalData" class="absolute inset-0 bg-white/80 flex items-center justify-center z-20">
          <div class="flex flex-col items-center">
            <div class="w-10 h-10 border-4 border-t-green-500 border-green-200 rounded-full animate-spin mb-3"></div>
            <p class="text-gray-600">Cargando información completa...</p>
          </div>
        </div>
        
        <!-- Contenido del modal con scroll -->
        <div class="flex-1 overflow-y-auto p-5 relative">
          <div v-if="!feature" class="flex items-center justify-center h-40">
            <p class="text-gray-500">No hay información disponible</p>
          </div>
          
          <div v-else>
            <!-- Mensaje de error si hay problemas con los datos adicionales -->
            <div v-if="dataError" class="bg-amber-50 border-l-4 border-amber-500 p-4 mb-4">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-sm text-amber-700">
                    {{ dataError }}
                    <button @click="fetchAdditionalData" class="font-medium underline hover:text-amber-800">
                      Reintentar
                    </button>
                  </p>
                </div>
              </div>
            </div>
            
            <!-- Vista categorizada (por defecto) -->
            <div v-if="viewMode === 'categorized'" class="space-y-6">
              <!-- Propiedades organizadas por categorías -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <template v-for="(category, index) in ['general', 'identificacion', 'geografico', 'agricola', 'social', 'fechas', 'otros']" :key="category">
                  <div v-if="categorizedProperties[category] && categorizedProperties[category].length > 0" class="space-y-3">
                    <!-- Título de la categoría con tema verde -->
                    <div class="flex items-center text-sm font-medium text-gray-700 mb-2">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getCategoryIcon(category)" />
                      </svg>
                      <h3>{{ getCategoryTitle(category) }}</h3>
                    </div>
                    
                    <!-- Card con propiedades de la categoría -->
                    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 space-y-3 h-full">
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
            
            <!-- Vista completa (todos los datos en forma de tabla) -->
            <div v-else class="space-y-4">
              <!-- Barra de búsqueda para filtrar datos -->
              <div class="relative mb-6">
                <input 
                  type="text" 
                  placeholder="Buscar en todos los datos..." 
                  class="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  v-model="searchTerm"
                />
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              
              <!-- Tabla con todos los datos -->
              <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Atributo
                      </th>
                      <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Valor
                      </th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="property in allProperties" :key="property.key" class="hover:bg-gray-50">
                      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-700">
                        {{ property.label }}
                      </td>
                      <td class="px-6 py-4 whitespace-normal text-sm text-gray-800">
                        {{ property.value }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <!-- Mensaje si no hay datos -->
              <div v-if="allProperties.length === 0" class="text-center py-8">
                <p class="text-gray-500">No se encontraron datos para mostrar</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Pie del modal con tema verde -->
        <div class="p-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
          <span class="text-sm text-gray-500">
            {{ activeLayer ? activeLayer.get('name') || activeLayer.get('title') : 'Capa' }}
          </span>
          <div class="flex space-x-3">
            <!-- Botón para descargar Excel -->
            <button 
              @click="downloadExcel" 
              class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors flex items-center space-x-2 shadow-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Descargar Excel</span>
            </button>
            
            <!-- Botón para cerrar (existente) -->
            <button @click="closeModal" class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
              Cerrar
            </button>
          </div>
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

/* Estilo para tabla completa */
table {
  border-collapse: separate;
  border-spacing: 0;
}

th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: #f9fafb;
}

/* Estilos para el scrollbar */
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
