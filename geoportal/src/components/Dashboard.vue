<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { useRouter } from 'vue-router'; 
import 'ol/ol.css';
import { Map, View } from 'ol';
import { defaults as defaultControls, ScaleLine, FullScreen, ZoomSlider } from 'ol/control';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import TileWMS from 'ol/source/TileWMS';
import { fromLonLat } from 'ol/proj';
import { watchEffect } from 'vue';
import MeasurementTool from './map-tools/MeasurementTool.vue';
import UserProfile from './UserProfile.vue';
import LayersTool from './map-tools/LayersTool.vue';
import DrawTool from './map-tools/DrawTool.vue';
import SearchTool from './map-tools/SearchTool.vue';
import { useLayers } from '../composables/useLayers';
import AvailableLayers from './map-tools/AvailableLayers.vue';
import LayerManager from './LayerManager.vue'; // Importamos el nuevo componente
// Importaciones para el marcador animado
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';
import { Vector as VectorSource } from 'ol/source';
import { Vector as VectorLayer } from 'ol/layer';
import { Style, Circle as CircleStyle, Fill, Stroke } from 'ol/style';
import Overlay from 'ol/Overlay';
// Importar nuevo componente y composable
import FeatureInfoPanel from './FeatureInfoPanel.vue';
import { useFeatureInfo } from '../composables/useFeatureInfo';

// Unificar definición de emisiones - combinar 'save-success', 'logout' y 'show-welcome'
const emit = defineEmits(['save-success', 'logout', 'show-welcome']);

// Estado reactivo
const sidebarOpen = ref(true);
const map = ref(null);
const loading = ref(true); // Para mostrar animación de carga
const activeTab = ref('principal'); // Para controlar pestañas de grupos de capas
const activeToolPanel = ref(''); // layers, measure, draw, search
const layerOpacity = ref({}); // Para almacenar opacidad de capas
const searchQuery = ref('');
const searchResults = ref([]);

// Nuevo estado para manejar la visibilidad del LayerManager
const showLayerManager = ref(true);

// Estado para el panel de detalles del territorio
const territorioSeleccionado = ref(null);
const territorioDetalles = ref(null);
const detailsPanelOpen = ref(false);
const loadingDetails = ref(false);
const errorDetails = ref(null);

// Estado para el modal de cierre de sesión
const logoutModal = ref(false);

// Estado para el modal de reporte completo
const reporteModal = ref(false);
const reporteCargando = ref(false);
const reporteError = ref(null);
const reporteCompleto = ref(null);
const formatoDescarga = ref('json'); // Opciones: 'json', 'pdf', 'csv'
const descargando = ref(false);

// Estado para el marcador personalizado
const markerSource = ref(null);
const markerLayer = ref(null);
const markerOverlay = ref(null);

// Importar configuración de capas desde el composable con sus funciones extendidas
const { layerGroups, isLoadingLayers, loadError, loadAvailableLayers, lastUpdated } = useLayers();

// Referencias a elementos DOM
const mapElement = ref(null);

// Funciones
const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value;
};

const changeTab = (tab) => {
  activeTab.value = tab;
  
  // Sincronizar estado de capas al cambiar de pestaña
  // Independientemente de la pestaña a la que cambiemos, debemos actualizar los estados
  if (map.value) {
    refreshLayersState();
  }
};

// Función para actualizar el estado de visibilidad de las capas desde el mapa
const refreshLayersState = () => {
  if (!map.value || !layerGroups.value) return;
  
  const mapLayers = map.value.getLayers().getArray();
  
  // Actualizar todas las capas en los grupos
  for (const groupKey in layerGroups.value) {
    if (Array.isArray(layerGroups.value[groupKey])) {
      layerGroups.value[groupKey].forEach((layer, index) => {
        const mapLayer = mapLayers.find(l => l.get('name') === layer.name);
        if (mapLayer) {
          // Usar Vue.set o su equivalente para asegurar reactividad
          layerGroups.value[groupKey][index] = {
            ...layerGroups.value[groupKey][index],
            visible: mapLayer.getVisible()
          };
          // Actualizar también la opacidad
          layerOpacity.value[layer.id] = mapLayer.getOpacity();
        }
      });
    }
  }
};

// Función para refrescar las capas - para ser usada con el botón de refrescar
const refreshLayers = () => {
  loadAvailableLayers();
  setTimeout(() => {
    refreshLayersState();
  }, 300);
};

// Nuevo método para manejar solicitudes de refresco
const handleRefreshRequest = () => {
  refreshLayers();
};

// Obtener todas las capas para el mapa, asegurándose que existan
const getAllLayers = () => {
  if (!layerGroups.value) return [];
  
  const principal = layerGroups.value.principal || [];
  const extras = layerGroups.value.extras || [];
  const dinamicas = layerGroups.value.dinamicas || [];
  
  return [...principal, ...extras, ...dinamicas];
};

// Versión mejorada de toggleLayerVisibility
const toggleLayerVisibility = (layer) => {
  if (!map.value) return;
  
  const mapLayer = map.value.getLayers().getArray()
    .find(l => l.get('name') === layer.name);
    
  if (mapLayer) {
    // Toggle visibilidad en la capa del mapa
    const currentVisibility = mapLayer.getVisible();
    const newVisibility = !currentVisibility;
    mapLayer.setVisible(newVisibility);
    
    // Determinar a qué grupo pertenece la capa y actualizarlo
    let groupFound = false;
    
    for (const groupKey in layerGroups.value) {
      if (Array.isArray(layerGroups.value[groupKey])) {
        const layerIndex = layerGroups.value[groupKey].findIndex(l => l.name === layer.name);
        if (layerIndex !== -1) {
          // Crear un nuevo objeto para asegurar reactividad
          layerGroups.value[groupKey][layerIndex] = {
            ...layerGroups.value[groupKey][layerIndex],
            visible: newVisibility
          };
          groupFound = true;
          break;
        }
      }
    }
    
    // Si no encontramos el grupo, pero sabemos el ID podemos intentar una asignación directa
    if (!groupFound) {
      const groupKey = layer.id < 10 ? 'principal' : 'extras';
      const layerIndex = layerGroups.value[groupKey]?.findIndex(l => l.name === layer.name);
      if (layerIndex !== -1 && layerIndex !== undefined) {
        layerGroups.value[groupKey][layerIndex] = {
          ...layerGroups.value[groupKey][layerIndex],
          visible: newVisibility
        };
      }
    }
    
    // Forzar actualización del UI
    map.value.render();
  }
};

// Función para cambiar opacidad de capa
const updateLayerOpacity = (layer, opacity) => {
  if (map.value) {
    const mapLayers = map.value.getLayers().getArray();
    const olLayer = mapLayers.find(l => l.get('name') === layer.name);
    if (olLayer) {
      olLayer.setOpacity(opacity);
      layerOpacity.value[layer.id] = opacity;
      
      // Actualizar también en el modelo de capas
      for (const groupKey in layerGroups.value) {
        if (Array.isArray(layerGroups.value[groupKey])) {
          const layerIndex = layerGroups.value[groupKey].findIndex(l => l.name === layer.name);
          if (layerIndex !== -1) {
            layerGroups.value[groupKey][layerIndex].opacity = opacity;
            break;
          }
        }
      }
    }
  }
};

// Función para mover capa arriba/abajo
const moveLayer = (layer, direction) => {
  if (map.value) {
    const mapLayers = map.value.getLayers().getArray();
    const index = mapLayers.findIndex(l => l.get('name') === layer.name);
    if (index !== -1) {
      const newIndex = direction === 'up' ? index + 1 : index - 1;
      if (newIndex >= 0 && newIndex < mapLayers.length) {
        const layerToMove = mapLayers[index];
        mapLayers.splice(index, 1);
        mapLayers.splice(newIndex, 0, layerToMove);
        map.value.render();
      }
    }
  }
};

// Función para búsqueda
const searchFeatures = async () => {
  if (!searchQuery.value) return;
  
  // Implementar búsqueda WFS aquí
  try {
    const geoserverUrl = 'http://31.97.8.51:8082/geoserver'; // URL actualizada
    const response = await fetch(`${geoserverUrl}/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=sembrando:territorios_28&outputFormat=application/json&CQL_FILTER=nombre_territorio ILIKE '%${searchQuery.value}%'`);
    const data = await response.json();
    searchResults.value = data.features;
  } catch (error) {
    console.error('Error en la búsqueda:', error);
  }
};

// Función mejorada para guardar mapa
const saveMapState = async () => {
  if (!newMapName.value.trim()) {
    alert('Por favor ingrese un nombre para el mapa');
    return;
  }

  const mapState = {
    id: Date.now(),
    name: newMapName.value.trim(),
    lastModified: new Date().toLocaleString(),
    thumbnail: '/src/components/images/vizual2.png', // Usar ruta absoluta
    center: map.value.getView().getCenter(),
    zoom: map.value.getView().getZoom(),
    layers: getAllLayers().map(layer => ({
      ...layer,
      visible: layer.visible,
      opacity: layerOpacity.value[layer.id] || 1
    }))
  };
  
  // Guardar en localStorage
  const savedMaps = JSON.parse(localStorage.getItem('savedMaps') || '[]');
  savedMaps.push(mapState);
  localStorage.setItem('savedMaps', JSON.stringify(savedMaps));
  
  emit('save-success');
  showSaveDialog.value = false;
  newMapName.value = '';
};

// Botón para guardar en la interfaz
const showSaveDialog = ref(false);
const newMapName = ref('');

const saveMap = () => {
  if (!newMapName.value.trim()) {
    alert('Por favor ingrese un nombre para el mapa');
    return;
  }
  
  // Crear captura de pantalla del mapa (o usar imagen predeterminada)
  const mapState = {
    id: Date.now(),
    name: newMapName.value.trim(),
    lastModified: new Date().toLocaleString(),
    thumbnail: '/src/components/images/vizual2.png', // Usar ruta absoluta
    center: map.value.getView().getCenter(),
    zoom: map.value.getView().getZoom(),
    layers: getAllLayers().map(layer => ({
      ...layer,
      visible: layer.visible,
      opacity: layerOpacity.value[layer.id] || 1
    }))
  };
  
  // Guardar en localStorage
  const savedMaps = JSON.parse(localStorage.getItem('savedMaps') || '[]');
  savedMaps.push(mapState);
  localStorage.setItem('savedMaps', JSON.stringify(savedMaps));
  
  emit('save-success');
  showSaveDialog.value = false;
  newMapName.value = '';
};

// Función para hacer zoom a un resultado de búsqueda
const zoomToFeature = (feature) => {
  if (feature && feature.geometry && map.value) {
    // Lógica para hacer zoom a la geometría
    console.log("Zoom a característica", feature);
  }
};

// Inicializar mapa y cargar capas cuando el componente se monte
const initializeMap = () => {
  try {
    // Crear capa base OSM
    const osmLayer = new TileLayer({
      source: new OSM(),
      visible: true,
      properties: {
        name: 'OpenStreetMap',
        group: 'base'
      },
      zIndex: 0  // Asegurar que esté en el fondo
    });

    // Verificar que el elemento del mapa existe
    if (!mapElement.value) {
      console.error("El elemento del mapa no existe");
      return;
    }

    // Crear mapa con la capa base
    map.value = new Map({
      target: mapElement.value,
      layers: [osmLayer],
      view: new View({
        center: fromLonLat([-98.9, 20.1]), // Centrado en Hidalgo, México
        zoom: 9,
        projection: 'EPSG:3857' // Usar Web Mercator como estándar
      }),
      controls: defaultControls({
        attributionOptions: { collapsible: false }
      }).extend([
        new ScaleLine(),
        new FullScreen(),
        new ZoomSlider()
      ])
    });

    // Inicializar opacidades
    map.value.getLayers().forEach(layer => {
      const name = layer.get('name');
      layerOpacity.value[name] = layer.getOpacity();
    });

    // Inicializar la fuente de datos para el marcador si es necesario
    markerSource.value = new VectorSource();
    markerLayer.value = new VectorLayer({
      source: markerSource.value,
      zIndex: 1000, // Asegurar que el marcador esté por encima de otras capas
      style: new Style({
        image: new CircleStyle({
          radius: 9,
          fill: new Fill({ color: '#28a745' }),
          stroke: new Stroke({ color: '#fff', width: 3 })
        })
      })
    });
    
    map.value.addLayer(markerLayer.value);

    // Agregar event listener para capturar clics en el mapa
    map.value.on('singleclick', handleMapClick);
    
    // Cargar las capas disponibles después de inicializar el mapa
    loadAvailableLayers();
    
    // Agregar listeners para mantener actualizado el estado de las capas
    map.value.getLayers().on('add', () => setTimeout(refreshLayersState, 100));
    map.value.getLayers().on('remove', () => setTimeout(refreshLayersState, 100));
    
    // Ejecutar una actualización inicial después de que todo se haya cargado
    setTimeout(refreshLayersState, 1000);

    console.log("Mapa inicializado correctamente");
  } catch (error) {
    console.error("Error durante la inicialización del mapa:", error);
    throw error;
  }
};

// Función para manejar clics en el mapa y obtener información de la característica
const handleMapClick = async (event) => {
  // Usar el nuevo sistema de obtención de información
  await fetchFeatureInfo(map.value, event.coordinate);
  
  // Si se encontró información, añadir marcador en la posición del clic
  if (showFeatureInfoPanel.value) {
    addMarkerAtCoordinate(event.coordinate);
  } else {
    removeMarker();
  }
};

// Función para agregar el marcador animado en una coordenada específica
const addMarkerAtCoordinate = (coordinate) => {
  // Eliminar el marcador anterior si existe
  removeMarker();
  
  if (!map.value) return;
  
  // Crear un elemento HTML para el marcador personalizado
  const markerElement = document.createElement('div');
  markerElement.className = 'custom-marker';
  
  // Crear un overlay para el marcador
  markerOverlay.value = new Overlay({
    position: coordinate,
    positioning: 'center-center',
    element: markerElement,
    stopEvent: false
  });
  
  // Añadir el overlay al mapa
  map.value.addOverlay(markerOverlay.value);
};

// Función para eliminar el marcador actual
const removeMarker = () => {
  if (markerOverlay.value && map.value) {
    map.value.removeOverlay(markerOverlay.value);
    markerOverlay.value = null;
  }
};

// Cerrar el panel de detalles y eliminar el marcador
const cerrarPanelDetalles = () => {
  closeFeatureInfoPanel();
  removeMarker();
};

// Función para obtener detalles completos del territorio desde el backend
const obtenerDetallesTerritorio = async (fid) => {
  try {
    // En un entorno real, esta sería la URL de tu backend
    // const response = await fetch(`/api/territorio/${fid}`);
    
    // Como no tenemos un backend real, simulamos la respuesta
    // En una implementación real, descomentar la línea anterior y eliminar este retardo simulado
    await new Promise(resolve => setTimeout(resolve, 600));
    
    // Datos simulados para el ejemplo - CORREGIDO: Preservar el nombre si existe
    const mockResponse = {
      fid: parseInt(fid),
      clave_mun: territorioSeleccionado.value.clave_mun || 12007,
      // Usar el nombre que viene de la API o construir un fallback
      nombre: territorioSeleccionado.value.nombre || null,
      nombre_territorio: territorioSeleccionado.value.nombre_territorio || null,
      n_cultivos: Math.floor(Math.random() * 15) + 1,
      superficie_ha: Math.floor(Math.random() * 5000) + 100,
      poblacion: Math.floor(Math.random() * 50000) + 1000,
      altitud_m: Math.floor(Math.random() * 2500) + 100,
      precipitacion_mm: Math.floor(Math.random() * 1500) + 300,
      temperatura_c: (15 + Math.random() * 10).toFixed(1),
      cultivo_principal: ['Maíz', 'Frijol', 'Café', 'Caña', 'Aguacate'][Math.floor(Math.random() * 5)]
    };
    
    // En una implementación real se usaría:
    // const data = await response.json();
    // territorioDetalles.value = data;
    
    territorioDetalles.value = mockResponse;
  } catch (error) {
    console.error('Error al obtener detalles del territorio:', error);
    errorDetails.value = 'No se pudieron cargar los detalles completos del territorio.';
  }
};

// Nueva función para obtener el título del territorio
const getTituloTerritorio = () => {
  if (!territorioDetalles.value) return 'Territorio';
  
  // Verificar diferentes posibles nombres de campo
  const nombre = territorioDetalles.value.nombre_territorio || 
                territorioDetalles.value.nombre || 
                territorioDetalles.value.territorio_nombre;
  
  // Si existe algún nombre, usarlo; si no, usar el ID como fallback
  return nombre || `Territorio #${territorioDetalles.value.fid}`;
};

// Computed para verificar si hay datos disponibles
const hayDatosTerritorio = computed(() => {
  return territorioDetalles.value !== null;
});

// Añadir referencia reactiva para el ancho de la ventana
const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 0);

// Función para actualizar el ancho de la ventana
const updateWindowWidth = () => {
  windowWidth.value = window.innerWidth;
};

onMounted(() => {
  // Simular tiempo de carga
  loading.value = true;
  setTimeout(() => {
    try {
      initializeMap();
      // Añadir el event listener para cambios de tamaño
      window.addEventListener('resize', updateWindowWidth);
      // Asegurarnos de tener el ancho correcto al inicio
      updateWindowWidth();
      
      // Establecer un temporizador para refrescar el estado de las capas
      setTimeout(refreshLayersState, 1000);
      
      loading.value = false;
    } catch (error) {
      console.error("Error inicializando el mapa:", error);
      // Asegurarse de quitar la pantalla de carga incluso si hay un error
      loading.value = false;
    }
  }, 1000);
});

// Limpiar recursos cuando el componente se desmonte
onBeforeUnmount(() => {
  if (map.value) {
    try {
      // Remover listeners antes de destruir el mapa
      if (map.value.getTargetElement()) {
        const listeners = map.value.getTargetElement().listeners;
        if (listeners) {
          Object.keys(listeners).forEach(type => {
            listeners[type].forEach(listener => {
              map.value.getTargetElement().removeEventListener(type, listener);
            });
          });
        }
      }
      
      // Remover observadores de capas
      if (map.value.getLayers()) {
        map.value.getLayers().un('add', refreshLayersState);
        map.value.getLayers().un('remove', refreshLayersState);
      }
      
      // Eliminar el marcador si existe
      removeMarker();
      
      map.value.setTarget(undefined);
      map.value = null;
    } catch (error) {
      console.error("Error al desmontar el mapa:", error);
    }
  }
  
  // Eliminar el event listener
  window.removeEventListener('resize', updateWindowWidth);
});

// Agregar funcionalidad de zoom
const zoomIn = () => {
  if (map.value) {
    const view = map.value.getView();
    const zoom = view.getZoom();
    view.animate({
      zoom: zoom + 1,
      duration: 250
    });
  }
};

const zoomOut = () => {
  if (map.value) {
    const view = map.value.getView();
    const zoom = view.getZoom();
    view.animate({
      zoom: zoom - 1,
      duration: 250
    });
  }
};

// Función para obtener el icono de cada herramienta - Reemplazar con iconos SVG modernos
const getToolIcon = (tool) => {
  // Ya no necesitamos esta función con los nuevos iconos SVG
  return '';
};

// Herramientas para el mapa con etiquetas más descriptivas
const mapTools = ref([
  { id: 'layers', name: 'Capas', description: 'Gestionar capas del mapa' },
  { id: 'measure', name: 'Medir', description: 'Herramientas de medición' },
  { id: 'draw', name: 'Dibujar', description: 'Dibujar en el mapa' },
  { id: 'search', name: 'Buscar', description: 'Buscar elementos en el mapa' }
]);

// Agregar estado para controlar visibilidad del panel de herramientas en móviles
const showToolsPanel = ref(false);

// Toggle para el panel de herramientas en móviles
const toggleToolsPanel = () => {
  showToolsPanel.value = !showToolsPanel.value;
};

// Agregar router para la navegación
const router = useRouter();

// Estado para el modal de confirmación de salida
const showExitModal = ref(false);

// Función para manejar el clic en el botón de inicio
const handleGoHome = () => {
  // Limpiar recursos del mapa antes de navegar
  if (map.value) {
    try {
      // Eliminar el marcador si existe
      removeMarker();
      
      // Limpiar listeners y capas
      const mapLayers = map.value.getLayers().getArray();
      for (let i = mapLayers.length - 1; i > 0; i--) {
        map.value.removeLayer(mapLayers[i]);
      }
      
      // Desasociar el mapa del elemento DOM
      map.value.setTarget(undefined);
    } catch (error) {
      console.error("Error al limpiar el mapa:", error);
    }
  }
  
  // Emitir evento antes de navegar
  emit('show-welcome');
  
  // Navegar a la página principal
  router.push('/').catch(err => {
    console.error("Error de navegación:", err);
    // Recargar la página como fallback
    window.location.href = '/';
  });
};

// Función para confirmar la salida y navegar a la página de inicio
const confirmExit = () => {
  navigateToHome();
  showExitModal.value = false;
};

// Función de navegación a la página de inicio
const navigateToHome = () => {
  router.push('/');
};

// Función para cerrar sesión
const logout = () => {
  // Mostrar modal de confirmación
  logoutModal.value = true;
};

// Función para confirmar cierre de sesión
const confirmLogout = () => {
  localStorage.removeItem('authenticated');
  localStorage.removeItem('user');
  logoutModal.value = false;
  // Usar el emit definido arriba en lugar de un nuevo emitLogout
  emit('logout');
  router.push('/login');
};

// Función para abrir el reporte completo
const verReporteCompleto = async () => {
  if (!territorioDetalles.value || !territorioDetalles.value.fid) {
    console.error('No hay territorio seleccionado para mostrar reporte');
    return;
  }
  
  reporteCargando.value = true;
  reporteError.value = null;
  reporteModal.value = true;

  try {
    // Verificar si ya tenemos todos los datos necesarios o si necesitamos cargar datos adicionales
    if (territorioDetalles.value && Object.keys(territorioDetalles.value).length > 10) {
      // Ya tenemos suficientes datos, solo asignamos al reporte
      reporteCompleto.value = { ...territorioDetalles.value };
    } else {
      // Necesitamos cargar datos adicionales
      // En un entorno real, aquí haríamos una llamada API:
      // const response = await fetch(`/api/territorios/${territorioDetalles.value.fid}`);
      // const data = await response.json();
      
      // Simulamos una carga más completa de datos desde el backend
      await new Promise(resolve => setTimeout(resolve, 800)); // Simular tiempo de carga
      
      // Crear un objeto más completo con datos aleatorios simulados adicionales
      reporteCompleto.value = {
        ...territorioDetalles.value,
        // Datos adicionales detallados
        fecha_registro: new Date().toLocaleDateString(),
        superficie_cultivable_ha: Math.floor(territorioDetalles.value.superficie_ha * 0.65),
        densidad_poblacion: (territorioDetalles.value.poblacion / territorioDetalles.value.superficie_ha).toFixed(2),
        cultivos_secundarios: ['Maíz', 'Frijol', 'Chile', 'Café', 'Caña', 'Aguacate', 'Jitomate']
                            .sort(() => 0.5 - Math.random())
                            .slice(0, 3)
                            .join(', '),
        tipo_suelo: ['Arcilloso', 'Arenoso', 'Franco', 'Limoso'][Math.floor(Math.random() * 4)],
        ph_suelo: (5 + Math.random() * 3).toFixed(1),
        materia_organica: (1 + Math.random() * 4).toFixed(2) + '%',
        nitrogeno: (0.05 + Math.random() * 0.5).toFixed(3) + '%',
        fosforo: (5 + Math.random() * 30).toFixed(1) + ' ppm',
        potasio: (50 + Math.random() * 300).toFixed(1) + ' ppm',
        capacidad_hidrica: (Math.random() * 100).toFixed(1) + '%',
        coordenadas: {
          latitud: (19 + Math.random() * 2).toFixed(6), 
          longitud: (-99 - Math.random() * 2).toFixed(6)
        },
        municipio: territorioDetalles.value.municipio || 'Tulancingo',
        estado: territorioDetalles.value.estado || 'Hidalgo',
        uso_agua: (Math.random() * 1000).toFixed(1) + ' m³/año',
        fuente_agua: ['Pozo', 'Río', 'Presa', 'Temporal'][Math.floor(Math.random() * 4)],
        ecosistema: ['Bosque', 'Selva', 'Pastizal', 'Matorral'][Math.floor(Math.random() * 4)],
        fauna_principales: ['Aves', 'Reptiles', 'Mamíferos pequeños', 'Insectos'][Math.floor(Math.random() * 4)],
        flora_principales: ['Encino', 'Pino', 'Matorral xerófilo', 'Selva baja'][Math.floor(Math.random() * 4)],
        riesgo_sequia: ['Bajo', 'Moderado', 'Alto', 'Muy alto'][Math.floor(Math.random() * 4)],
        riesgo_inundacion: ['Bajo', 'Moderado', 'Alto', 'Muy alto'][Math.floor(Math.random() * 4)],
        erosion_suelo: ['Leve', 'Moderada', 'Severa', 'Muy severa'][Math.floor(Math.random() * 4)],
        produccion_estimada: Math.floor(1000 + Math.random() * 9000) + ' kg/ha',
        valor_produccion: '$' + Math.floor(50000 + Math.random() * 950000).toLocaleString(),
        fecha_actualizacion: '2023-' + 
          (Math.floor(Math.random() * 12) + 1).toString().padStart(2, '0') + '-' + 
          (Math.floor(Math.random() * 28) + 1).toString().padStart(2, '0')
      };
    }
  } catch (error) {
    console.error('Error al cargar el reporte completo:', error);
    reporteError.value = 'No se pudo cargar el reporte completo. Intente nuevamente.';
  } finally {
    reporteCargando.value = false;
  }
};

// Función para cerrar el modal de reporte
const cerrarReporteModal = () => {
  reporteModal.value = false;
  reporteCompleto.value = null; // Limpiamos el reporte al cerrar
};

// Función para descargar el reporte en el formato seleccionado
const descargarReporte = async () => {
  if (!reporteCompleto.value) return;
  
  descargando.value = true;
  
  try {
    const nombreArchivo = `territorio_${reporteCompleto.value.fid}_${Date.now()}`;
    
    if (formatoDescarga.value === 'json') {
      // Descargar como JSON
      const jsonString = JSON.stringify(reporteCompleto.value, null, 2);
      const blob = new Blob([jsonString], { type: 'application/json' });
      descargarArchivo(blob, `${nombreArchivo}.json`);
    } 
    else if (formatoDescarga.value === 'csv') {
      // Convertir a CSV
      const csvContent = convertirACSV(reporteCompleto.value);
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      descargarArchivo(blob, `${nombreArchivo}.csv`);
    }
    else if (formatoDescarga.value === 'pdf') {
      // Aquí se implementaría la generación de PDF
      // En un entorno real, generalmente se usaría una librería como jsPDF o
      // se haría una petición al backend para generar el PDF
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simular tiempo de generación
      alert('La generación de PDF estaría implementada aquí con una librería como jsPDF');
    }
  } catch (error) {
    console.error('Error al descargar el reporte:', error);
    alert('Error al generar la descarga. Intente nuevamente.');
  } finally {
    descargando.value = false;
  }
};

// Función auxiliar para descargar el archivo
const descargarArchivo = (blob, fileName) => {
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// Función auxiliar para convertir objeto a formato CSV
const convertirACSV = (obj) => {
  // Aplanar el objeto para que las propiedades anidadas se representen con notación de punto
  const flattenedObject = {};
  
  function flatten(obj, prefix = '') {
    for (const key in obj) {
      if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
        flatten(obj[key], `${prefix}${key}.`);
      } else {
        flattenedObject[`${prefix}${key}`] = obj[key];
      }
    }
  }
  
  flatten(obj);
  
  // Crear encabezados y valores
  const headers = Object.keys(flattenedObject);
  const values = Object.values(flattenedObject).map(value => 
    typeof value === 'string' ? `"${value.replace(/"/g, '""')}"` : value
  );
  
  return headers.join(',') + '\n' + values.join(',');
};

// Función para formatear fecha
const formatearFecha = (fechaStr) => {
  try {
    const fecha = new Date(fechaStr);
    return fecha.toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch (error) {
    return fechaStr;
  }
};

// Añadir useFeatureInfo al script setup
const { 
  featureInfo, 
  selectedFeature, 
  loading: featureInfoLoading, 
  error: featureInfoError, 
  showPanel: showFeatureInfoPanel,
  activeLayer: activeFeatureLayer,
  fetchFeatureInfo,
  closePanel: closeFeatureInfoPanel 
} = useFeatureInfo();

// Función para navegar a la página de subida de mapas
const goToUploadMaps = () => {
  router.push('/upload-layer'); // Ruta que coincide con la definida en router/index.js
};
</script>

<template>
  <!-- Contenedor principal a pantalla completa -->
  <div class="h-screen w-screen overflow-hidden relative bg-gray-50 flex">
    <!-- Nueva barra lateral fija -->
    <aside 
      class="h-full bg-white border-r border-gray-200 flex flex-col transition-all duration-500 ease-in-out z-20"
      :class="sidebarOpen ? 'w-80 sm:w-96' : 'w-16'"
    >
      <!-- Encabezado de la barra lateral -->
      <div class="h-14 sm:h-16 flex items-center justify-between px-4 border-b border-gray-100 bg-gradient-to-r from-green-50 to-emerald-50">
        <div class="flex items-center space-x-3 overflow-hidden">
          <img 
            src="@/components/images/logotipo.png" 
            alt="Logo" 
            class="h-8 w-8 object-contain flex-shrink-0"
          />
          <h2 class="font-medium text-green-800 truncate transition-opacity duration-300"
              :class="sidebarOpen ? 'opacity-100' : 'opacity-0'">
            Herramientas
          </h2>
        </div>
        <!-- Botón para colapsar/expandir la barra lateral -->
        <button 
          @click="toggleSidebar" 
          class="p-1.5 rounded-lg hover:bg-green-100 text-green-700 transition-all duration-300 transform"
          :class="sidebarOpen ? '' : 'rotate-180'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      </div>

      <!-- Contenido de la barra lateral -->
      <div class="flex-1 overflow-hidden flex flex-col">
        <!-- Pestañas de navegación -->
        <div class="flex border-b border-gray-200">
          <button 
            @click="changeTab('principal')" 
            class="px-3 py-3 text-sm font-medium transition-colors duration-200 flex-1 border-b-2 flex items-center justify-center space-x-1"
            :class="activeTab === 'principal' ? 'border-green-500 text-green-700' : 'border-transparent hover:text-green-600 text-gray-600'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <span v-if="sidebarOpen" class="truncate">Capas</span>
          </button>
          <button 
            @click="changeTab('extras')" 
            class="px-3 py-3 text-sm font-medium transition-colors duration-200 flex-1 border-b-2 flex items-center justify-center space-x-1"
            :class="activeTab === 'extras' ? 'border-green-500 text-green-700' : 'border-transparent hover:text-green-600 text-gray-600'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            <span v-if="sidebarOpen" class="truncate">Herramientas</span>
          </button>
        </div>

        <!-- Contenido según la pestaña activa -->
        <div class="flex-1 overflow-y-auto scrollbar-thin scrollbar-track-gray-100 scrollbar-thumb-green-500">
          <transition name="fade" mode="out-in">
            <!-- Pestaña Capas con el nuevo LayerManager y botón de refrescar -->
            <div v-if="activeTab === 'principal' && sidebarOpen" class="p-4 animate-fade-in">
              <!-- Cabecera con título y botón de refrescar -->
              <div class="flex justify-between items-center mb-4">
                <h2 class="text-lg font-semibold text-gray-800">Capas disponibles</h2>
                <button 
                  @click="handleRefreshRequest" 
                  class="p-1.5 text-gray-500 hover:text-green-600 rounded-full hover:bg-gray-100 transition-colors"
                  :class="{'animate-spin': isLoadingLayers}"
                  :disabled="isLoadingLayers"
                  title="Refrescar capas"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </div>
              
              <!-- Mostrar estado de carga o error -->
              <div v-if="isLoadingLayers" class="flex items-center justify-center py-4 bg-gray-50 rounded-lg mb-4">
                <div class="flex flex-col items-center">
                  <div class="w-8 h-8 border-2 border-t-green-500 border-green-200 rounded-full animate-spin mb-2"></div>
                  <p class="text-sm text-gray-600">Actualizando capas...</p>
                </div>
              </div>
              
              <div v-else-if="loadError" class="bg-red-50 border-l-4 border-red-500 p-4 mb-4 text-sm text-red-700">
                <p>{{ loadError }}</p>
                <button @click="refreshLayers" class="mt-1 text-red-600 underline hover:text-red-800">
                  Reintentar
                </button>
              </div>
              
              <!-- Mensaje si no hay capas -->
              <div v-else-if="getAllLayers().length === 0" class="text-center py-8 bg-gray-50 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5-5 5-5m6 10l5-5-5-5" />
                </svg>
                <p class="text-gray-600 font-medium">No hay capas disponibles</p>
                <p class="text-gray-500 text-sm mt-2">
                  No se encontraron capas en el servidor. Sube una nueva capa desde el panel de "Subir Capas".
                </p>
                <button 
                  @click="refreshLayers" 
                  class="mt-4 px-4 py-2 bg-green-100 hover:bg-green-200 text-green-700 rounded-lg transition-colors flex items-center space-x-2 mx-auto"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>Actualizar capas</span>
                </button>
              </div>
              
              <!-- Componente LayerManager cuando hay capas disponibles -->
              <div v-else>
                <!-- Tiempo de última actualización -->
                <div v-if="lastUpdated" class="text-xs text-gray-500 mb-3 italic">
                  Actualizado: {{ lastUpdated.toLocaleTimeString() }}
                </div>
                
                <!-- Componente de gestión de capas -->
                <LayerManager :map="map" />
              </div>
            </div>

            <!-- Contenido de la pestaña Extras con iconos solo en modo colapsado -->
            <div v-else-if="activeTab === 'extras'" class="animate-fade-in">
              <!-- Contenido detallado cuando la sidebar está expandida -->
              <div v-if="sidebarOpen" class="p-4 space-y-4">
                <h2 class="text-lg font-semibold text-green-800 flex items-center space-x-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                  </svg>
                  <span>Herramientas</span>
                </h2>
                
                <!-- Herramientas del mapa mejoradas -->
                <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 shadow-sm">
                  <h3 class="text-base font-medium text-green-700 mb-4 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    Herramientas del mapa
                  </h3>
                  
                  <!-- Herramientas con iconos y efectos mejorados -->
                  <div class="grid grid-cols-2 gap-3">
                    <button 
                      v-for="tool in mapTools" 
                      :key="tool.id"
                      @click="activeToolPanel = activeToolPanel === tool.id ? '' : tool.id"
                      class="tool-button relative flex flex-col items-center justify-center p-3 rounded-xl transition-all duration-300 overflow-hidden group"
                      :class=" [
                        activeToolPanel === tool.id 
                          ? 'bg-green-100 text-green-700 shadow-md ring-2 ring-green-400 ring-opacity-50' 
                          : 'bg-white hover:bg-gray-50 text-gray-700 hover:text-green-600 shadow-sm hover:shadow'
                      ]"
                    >
                      <!-- Efecto de onda al hacer clic -->
                      <span class="absolute inset-0 bg-green-100 opacity-0 group-active:animate-ripple-effect"></span>
                      
                      <!-- Gradiente de fondo con efecto hover -->
                      <span class="absolute inset-0 bg-gradient-to-br from-green-50 to-emerald-50 opacity-0 group-hover:opacity-100 transition-all duration-500"></span>
                      
                      <!-- Iconos SVG para cada herramienta -->
                      <div class="relative z-10 mb-1 transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                        <!-- Icono para capas -->
                        <svg v-if="tool.id === 'layers'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 00-3.7-3.7 48.678 48.678 0 00-7.324 0 4.006 4.006 0 00-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3l-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 003.7 3.7 48.656 48.656 0 007.324 0 4.006 4.006 0 003.7-3.7c.017-.22.032-.441.046-.662M4.5 12l3 3m-3-3l-3 3" />
                        </svg>
                        
                        <!-- Icono para medición -->
                        <svg v-if="tool.id === 'measure'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                        </svg>
                        
                        <!-- Icono para dibujo -->
                        <svg v-if="tool.id === 'draw'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M15.042 21.672L13.684 16.6m0 0l-2.51 2.225.569-9.47 5.227 7.917-3.286-.672zm-7.518-.267A8.25 8.25 0 1120.25 10.5M8.288 14.212A5.25 5.25 0 1117.25 10.5" />
                        </svg>
                        
                        <!-- Icono para búsqueda -->
                        <svg v-if="tool.id === 'search'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                        </svg>
                      </div>
                      
                      <!-- Nombre de la herramienta -->
                      <span class="text-xs font-medium mt-1">{{ tool.name }}</span>
                      
                      <!-- Indicador de herramienta activa -->
                      <span v-if="activeToolPanel === tool.id" class="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                    </button>
                  </div>
                  
                  <!-- Descripción de la herramienta seleccionada -->
                  <div v-if="activeToolPanel" class="mt-3 px-4 py-2 bg-white/80 backdrop-blur-sm text-green-800 text-xs rounded-lg shadow-inner animate-fade-in">
                    <p class="flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {{ mapTools.find(t => t.id === activeToolPanel)?.description }}
                    </p>
                  </div>
                </div>
                
                <!-- Lista de capas adicionales -->
                <div class="mt-6">
                  <h3 class="text-sm font-medium text-gray-700 mb-3">Capas adicionales</h3>
                  <ul class="space-y-2">
                    <li v-for="layer in layerGroups.extras" :key="layer.id" 
                        class="transform transition-all duration-300 hover:translate-x-1">
                      <div class="flex items-center p-2 rounded-lg hover:bg-green-50 transition-colors">
                        <div class="relative inline-block w-10 mr-2 align-middle select-none">
                          <input 
                            type="checkbox" 
                            :id="`layer-extras-${layer.id}`" 
                            :checked="layer.visible"
                            @change="toggleLayerVisibility(layer)" 
                            class="opacity-0 absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
                          />
                          <label 
                            :for="`layer-extras-${layer.id}`" 
                            class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"
                            :class="{'active': layer.visible}"
                          ></label>
                        </div>
                        <div>
                          <label :for="`layer-extras-${layer.id}`" class="text-sm font-medium text-gray-700 cursor-pointer">
                            {{ layer.name }}
                          </label>
                          <p class="text-xs text-gray-500">{{ layer.description }}</p>
                        </div>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Contenido minimalista cuando la sidebar está colapsada -->
              <div v-else class="py-4">
                <div class="flex flex-col items-center space-y-8">
                  <button v-for="tool in mapTools" 
                          :key="tool.id"
                          @click="activeToolPanel = activeToolPanel === tool.id ? '' : tool.id; sidebarOpen = true;"
                          class="p-2 rounded-lg hover:bg-green-50 transition-all duration-300 relative group"
                          :class="{'bg-green-100': activeToolPanel === tool.id}">
                    <!-- Tooltip para mostrar el nombre de la herramienta -->
                    <div class="absolute left-full ml-2 px-2 py-1 bg-gray-800 text-white text-xs rounded whitespace-nowrap opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
                      {{ tool.name }}
                      <div class="absolute top-1/2 -left-1 transform -translate-y-1/2 rotate-45 w-2 h-2 bg-gray-800"></div>
                    </div>

                    <!-- Icono para capas -->
                    <svg v-if="tool.id === 'layers'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 00-3.7-3.7 48.678 48.678 0 00-7.324 0 4.006 4.006 0 00-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3l-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 003.7 3.7 48.656 48.656 0 007.324 0 4.006 4.006 0 003.7-3.7c.017-.22.032-.441.046-.662M4.5 12l3 3m-3-3l-3 3" />
                    </svg>
                    
                    <!-- Icono para medición -->
                    <svg v-if="tool.id === 'measure'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                    
                    <!-- Icono para dibujo -->
                    <svg v-if="tool.id === 'draw'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15.042 21.672L13.684 16.6m0 0l-2.51 2.225.569-9.47 5.227 7.917-3.286-.672zm-7.518-.267A8.25 8.25 0 1120.25 10.5M8.288 14.212A5.25 5.25 0 1117.25 10.5" />
                    </svg>
                    
                    <!-- Icono para búsqueda -->
                    <svg v-if="tool.id === 'search'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                    </svg>
                    
                    <!-- Indicador de herramienta activa -->
                    <span v-if="activeToolPanel === tool.id" class="absolute -right-1 top-1/2 transform -translate-y-1/2 w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                  </button>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- Pie de la barra lateral -->
      <div class="p-3 bg-gradient-to-r from-green-50 to-emerald-50 border-t border-green-100 flex items-center justify-center">
        <p v-if="sidebarOpen" class="text-xs text-green-700">Geoportal Sembrando Datos</p>
        <span v-else class="text-green-700">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </span>
      </div>
    </aside>

    <!-- Contenido principal que se ajusta al espacio restante -->
    <div class="flex-1 relative">
      <!-- Overlay de carga con animación -->
      <div v-if="loading" 
           class="fixed inset-0 bg-white bg-opacity-90 z-50 flex flex-col items-center justify-center transition-opacity duration-500"
           :class="loading ? 'opacity-100' : 'opacity-0 pointer-events-none'">
        <div class="w-16 h-16 border-4 border-t-green-500 border-green-200 rounded-full animate-spin mb-4"></div>
        <p class="text-green-700 font-medium">Cargando geoportal...</p>
      </div>

      <!-- Animación de entrada para el dashboard -->
      <div class="dashboard-enter-animation"></div>

      <!-- Mapa a pantalla completa -->
      <div ref="mapElement" class="absolute inset-0 z-0"></div>
      
      <!-- Header flotante con título y botones de acción -->
      <header class="absolute top-0 left-0 right-0 bg-white bg-opacity-95 shadow-md z-10 transition-all duration-300">
        <div class="container mx-auto px-4 py-2 sm:py-3 flex justify-between items-center">
          <!-- Logo y título -->
          <div class="flex items-center space-x-3">
            <img 
              src="@/components/images/logotipo.png" 
              alt="Logotipo Sembrando Datos" 
              class="h-10 sm:h-12 w-auto object-contain"
            />
            <h1 class="text-xl sm:text-2xl md:text-3xl font-serif font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-600 to-teal-500">
              Geoportal Sembrando Datos
            </h1>
          </div>

          <!-- Botones de acción redistribuidos -->
          <div class="flex items-center">
            <!-- Botón de inicio actualizado sin contorno ni fondo -->
            <button 
              @click="handleGoHome"
              class="px-4 py-2 text-green-600 rounded-lg transition-all duration-300 flex items-center space-x-2 hover:text-green-800 focus:outline-none transform hover:-translate-y-0.5 active:translate-y-0 font-semibold mr-4"
              aria-label="Volver a la página de inicio"
            >
              <span class="home-icon">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                  <polyline points="9 22 9 12 15 12 15 22"></polyline>
                </svg>
              </span>
              <span class="hidden sm:inline">Inicio</span>
            </button>
            
            <!-- Botón para subir capas -->
            <button 
              @click="goToUploadMaps"
              class="modern-button upload-button px-4 py-2 bg-gradient-to-r from-blue-400 to-blue-500 text-white rounded-lg transition-all duration-300 flex items-center space-x-2 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50 transform hover:-translate-y-0.5 active:translate-y-0 font-semibold group mr-4"
              aria-label="Subir nuevas capas"
            >
              <span class="upload-icon relative">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </span>
              <span class="hidden sm:inline">IR a subir capas</span>
            </button>

            <!-- Componente de perfil de usuario -->
            <UserProfile class="ml-auto" />
          </div>
        </div>
      </header>

      <!-- Panel lateral de herramientas - Ajustado para estar casi pegado a la barra lateral -->
      <div 
        v-if="activeToolPanel && sidebarOpen"
        class="absolute top-20 z-10 bg-white rounded-lg shadow-lg w-72 transition-all duration-500 ease-in-out animate-slide-in-right"
        :style="{ left: sidebarOpen ? (windowWidth >= 640 ? '5px' : '65px') : '0' }"
      >
        <!-- Contenido según herramienta activa -->
        <div v-if="activeToolPanel === 'measure'">
          <MeasurementTool :map="map" />
        </div>
        
        <!-- Panel de búsqueda -->
        <div v-if="activeToolPanel === 'search'">
          <SearchTool :map="map" />
        </div>
        
        <!-- Panel de dibujo -->
        <div v-if="activeToolPanel === 'draw'">
          <DrawTool :map="map" />
        </div>
        
        <!-- Panel de capas -->
        <div v-if="activeToolPanel === 'layers'">
          <LayersTool :map="map" :layers="getAllLayers()" />
        </div>
      </div>

      <!-- Reemplazar el panel de detalles del territorio por el nuevo FeatureInfoPanel -->
      <FeatureInfoPanel
        :featureInfo="featureInfo"
        :selectedFeature="selectedFeature"
        :loading="featureInfoLoading"
        :error="featureInfoError"
        :showPanel="showFeatureInfoPanel"
        :activeLayer="activeFeatureLayer"
        @close="cerrarPanelDetalles"
      />
      
      <!-- Modal para reporte completo del territorio -->
      <Transition name="modal-fade">
        <div 
          v-if="reporteModal" 
          class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[60] p-4 sm:p-6 md:p-8 overflow-y-auto"
          @click.self="cerrarReporteModal"
        >
          <div class="bg-white rounded-2xl shadow-xl w-full max-w-5xl max-h-[95vh] overflow-hidden transform transition-all duration-300 animate-modal-in">
            <!-- Cabecera del modal -->
            <div class="bg-gradient-to-r from-emerald-500 to-green-600 p-5 text-white flex justify-between items-center sticky top-0 z-10">
              <h2 class="text-xl sm:text-2xl font-medium flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Reporte completo: {{ getTituloTerritorio() }}</span>
              </h2>
              <button 
                @click="cerrarReporteModal"
                class="p-2 hover:bg-white/20 rounded-full transition-colores"
                aria-label="Cerrar"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <!-- Contenido del reporte con scroll -->
            <div class="p-5 sm:p-8 overflow-y-auto max-h-[calc(95vh-6rem)]">
              <!-- Estado de carga -->
              <div v-if="reporteCargando" class="flex flex-col items-center justify-center py-16">
                <div class="w-16 h-16 border-4 border-t-green-500 border-green-200 rounded-full animate-spin mb-4"></div>
                <p class="text-gray-500">Cargando información detallada...</p>
              </div>
              
              <!-- Mensaje de error -->
              <div v-else-if="reporteError" class="bg-red-50 p-6 rounded-xl text-red-600 my-4 text-center">
                <svg class="w-12 h-12 mx-auto text-red-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="font-medium">{{ reporteError }}</p>
                <button 
                  @click="verReporteCompleto"
                  class="mt-4 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-colores"
                >
                  Intentar nuevamente
                </button>
              </div>
              
              <!-- Reporte completo -->
              <div v-else-if="reporteCompleto" class="space-y-8">
                <!-- Resumen del territorio -->
                <section class="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-xl shadow-sm">
                  <h3 class="text-xl font-semibold text-green-800 mb-3 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                    </svg>
                    Información general
                  </h3>
                  
                  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                    <!-- Identificación -->
                    <div class="bg-white rounded-lg p-4 shadow-sm">
                      <h4 class="text-sm font-medium text-gray-500 mb-3">Identificación</h4>
                      <div class="space-y-2">
                        <div class="flex justify-between">
                          <span class="text-sm text-gray-500">ID:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.fid }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-sm text-gray-500">Clave Municipal:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.clave_mun }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-sm text-gray-500">Municipio:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.municipio }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-sm text-gray-500">Estado:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.estado }}</span>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Geografía -->
                    <div class="bg-white rounded-lg p-4 shadow-sm">
                      <h4 class="text-sm font-medium text-gray-500 mb-3">Geografía</h4>
                      <div class="space-y-2">
                        <div class="flex justify-between">
                          <span class="text-sm text-gray-500">Superficie total:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.superficie_ha }} ha</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-sm text-gray-500">Superficie cultivable:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.superficie_cultivable_ha }} ha</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-sm text-gray-500">Altitud:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.altitud_m }} msnm</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-sm text-gray-500">Coordenadas:</span>
                          <span class="text-sm font-medium">
                            {{ reporteCompleto.coordenadas?.latitud }}, {{ reporteCompleto.coordenadas?.longitud }}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Demografía -->
                    <div class="bg-white rounded-lg p-4 shadow-sm">
                      <h4 class="text-sm font-medium text-gray-500 mb-3">Demografía</h4>
                      <div class="space-y-2">
                        <div class="flex justify-between">
                          <span class="text-sm text-gray-500">Población:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.poblacion?.toLocaleString() }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-sm text-gray-500">Densidad poblacional:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.densidad_poblacion }} hab/ha</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-sm text-gray-500">Registro:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.fecha_registro }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-sm text-gray-500">Actualización:</span>
                          <span class="text-sm font-medium">{{ formatearFecha(reporteCompleto.fecha_actualizacion) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </section>
                
                
                <!-- Información climática y ambiental -->
                <section>
                  <h3 class="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
                    </svg>
                    Información climática y ambiental
                  </h3>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Clima -->
                    <div class="bg-blue-50 rounded-xl p-5 border border-blue-100">
                      <h4 class="text-base font-medium text-blue-800 mb-4">Clima</h4>
                      
                      <div class="grid grid-cols-2 gap-4">
                        <div class="bg-white rounded-lg p-4 shadow-sm flex flex-col items-center">
                          <span class="text-4xl mb-2 text-blue-700">
                            {{ reporteCompleto.temperatura_c }}°C
                          </span>
                          <span class="text-sm text-gray-500">Temperatura media</span>
                        </div>
                        
                        <div class="bg-white rounded-lg p-4 shadow-sm flex flex-col items-center">
                          <span class="text-4xl mb-2 text-blue-700">
                            {{ reporteCompleto.precipitacion_mm }} mm
                          </span>
                          <span class="text-sm text-gray-500">Precipitación anual</span>
                        </div>
                      </div>
                      
                      <div class="mt-4 space-y-2">
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Riesgo de sequía:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.riesgo_sequia }}</span>
                        </div>
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Riesgo de inundación:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.riesgo_inundacion }}</span>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Ecosistema -->
                    <div class="bg-green-50 rounded-xl p-5 border border-green-100">
                      <h4 class="text-base font-medium text-green-800 mb-4">Ecosistema</h4>
                      
                      
                      <div class="space-y-2">
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Tipo de ecosistema:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.ecosistema }}</span>
                        </div>
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Flora principal:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.flora_principales }}</span>
                        </div>
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Fauna principal:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.fauna_principales }}</span>
                        </div>
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Fuente de agua:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.fuente_agua }}</span>
                        </div>
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Uso de agua anual:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.uso_agua }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </section>
                
                <!-- Información agrícola -->
                <section>
                  <h3 class="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064" />
                    </svg>
                    Información agrícola y suelo
                  </h3>
                  
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <!-- Cultivo -->
                    <div class="col-span-1 md:col-span-2 bg-amber-50 rounded-xl p-5 border border-amber-100">
                      <h4 class="text-base font-medium text-amber-800 mb-4">Datos de Cultivo</h4>
                      
                      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                        <div class="bg-white rounded-lg p-4 shadow-sm flex flex-col">
                          <span class="text-2xl mb-2 text-amber-700">
                            {{ reporteCompleto.n_cultivos }}
                          </span>
                          <span class="text-sm text-gray-500">Tipos de cultivos</span>
                        </div>
                        
                        <div class="bg-white rounded-lg p-4 shadow-sm flex flex-col">
                          <span class="text-2xl mb-2 text-amber-700">
                            {{ reporteCompleto.produccion_estimada }}
                          </span>
                          <span class="text-sm text-gray-500">Producción estimada</span>
                        </div>
                      </div>
                      
                      <div class="space-y-2">
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Cultivo principal:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.cultivo_principal }}</span>
                        </div>
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Cultivos secundarios:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.cultivos_secundarios }}</span>
                        </div>
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Valor de la producción:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.valor_produccion }}</span>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Suelo -->
                    <div class="bg-amber-50 rounded-xl p-5 border border-amber-100">
                      <h4 class="text-base font-medium text-amber-800 mb-4">Características del Suelo</h4>
                      
                      <div class="space-y-2">
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Tipo de suelo:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.tipo_suelo }}</span>
                        </div>
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">pH:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.ph_suelo }}</span>
                        </div>
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Materia orgánica:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.materia_organica }}</span>
                        </div>
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Nitrógeno:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.nitrogeno }}</span>
                        </div>
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Fósforo:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.fosforo }}</span>
                        </div>
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Potasio:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.potasio }}</span>
                        </div>
                        <div class="flex justify-between p-2 bg-white/80 rounded-lg">
                          <span class="text-sm text-gray-600">Erosión:</span>
                          <span class="text-sm font-medium">{{ reporteCompleto.erosion_suelo }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </section>
              </div>
            </div>
            
            <!-- Pie del modal con opciones de descarga -->
            <div class="p-5 border-t border-gray-200 bg-gray-50 flex flex-col sm:flex-row items-center justify-between sticky bottom-0">
              <!-- Selector de formato -->
              <div class="flex items-center space-x-3 w-full sm:w-auto mb-4 sm:mb-0">
                <label for="formato-descarga" class="text-sm text-gray-600">Formato de descarga:</label>
                <select 
                  id="formato-descarga"
                  v-model="formatoDescarga"
                  class="px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-green-500"
                >
                  <option value="json">JSON</option>
                  <option value="csv">CSV</option>
                  <option value="pdf">PDF</option>
                </select>
              </div>
              
              <!-- Botones de acción -->
              <div class="flex space-x-3 w-full sm:w-auto justify-end">
                <button 
                  @click="cerrarReporteModal"
                  class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colores"
                >
                  Cerrar
                </button>
                <button 
                  @click="descargarReporte"
                  :disabled="descargando || !reporteCompleto"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg v-if="descargando" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0l-4 4m3-3v12" />
                  </svg>
                  <span>{{ descargando ? 'Descargando...' : 'Descargar reporte' }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
      
      <!-- Modal elegante para confirmar salida -->
      <Transition name="modal-fade">
        <div v-if="showExitModal" 
             class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
             @click.self="showExitModal = false">
          <div class="bg-white rounded-2xl p-6 w-[90%] max-w-md transform transition-all duration-300
                      scale-100 opacity-100 shadow-xl animate-modal-in">
            <div class="text-center">
              <div class="mb-4 transform transition-all duration-500 hover:rotate-12">
                <span class="text-5xl">🏠</span>
              </div>
              <h3 class="text-xl font-bold text-gray-900 mb-4">
                ¿Volver al inicio?
              </h3>
              <p class="text-gray-600 mb-8">
                ¿Estás seguro de que deseas salir del mapa actual? Los cambios no guardados se perderán.
              </p>
              <div class="flex space-x-3 justify-center">
                <button 
                  @click="showExitModal = false"
                  class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 
                         rounded-lg transition-colores duration-300"
                >
                  Cancelar
                </button>
                <button 
                  @click="confirmExit"
                  class="px-4 py-2 bg-green-500 hover:bg-green-600 text-white 
                         rounded-lg transition-colores duration-300 flex items-center space-x-2
                         transform hover:scale-105 active:scale-100"
                >
                  <span>Volver al inicio</span>
                  <span class="text-xl transition-transform transform group-hover:translate-x-1">→</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Modal de cierre de sesión -->
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
                ¿Estás seguro de que deseas cerrar sesión? Los cambios no guardados se perderán.
              </p>
              <div class="flex space-x-3 justify-center">
                <button 
                  @click="logoutModal = false"
                  class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 
                         rounded-lg transition-colores duration-300"
                >
                  Cancelar
                </button>
                <button 
                  @click="confirmLogout"
                  class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white 
                         rounded-lg transition-colores duration-300 flex items-center space-x-2"
                >
                  <span>Cerrar sesión</span>
                  <span class="text-xl">→</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
/* Corregir los selectores que usan @apply */
.tool-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tool-btn.active {
  background-color: #10B981;
  color: white;
}

/* Mejorar estilos de botones de acción */
button {
  font-weight: 500;
  font-size: 0.875rem;
}

button:active {
  transform: translateY(1px);
}

/* Animación suave para los botones */
.flex.items-center.space-x-4 button {
  position: relative;
  overflow: hidden;
}

.flex.items-center.space-x-4 button::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 60%);
  transform: translate(-50%, -50%) scale(0);
  transition: transform 0.5s ease;
  pointer-events: none;
}

.flex.items-center.space-x-4 button:hover::after {
  transform: translate(-50%, -50%) scale(2);
}

/* Estilos para tooltips de medición */
:global(.ol-tooltip) {
  position: relative;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 4px;
  color: white;
  padding: 4px 8px;
  font-size: 12px;
  white-space: nowrap;
  font-weight: bold;
}

:global(.ol-tooltip-measure) {
  opacity: 1;
  font-weight: bold;
}

:global(.ol-tooltip-static) {
  background-color: rgba(0, 128, 0, 0.7);
}

/* Estilos para botones de herramientas */
.tool-btn {
  width: 48px;
  height: 48px;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4B5563;
  transition: all 0.3s ease;
  transform: scale(1);
  animation: slideIn 0.5s ease-out forwards;
  animation-delay: var(--delay);
  opacity: 0;
}

@keyframes slideIn {
  0% {
    opacity: 0;
    transform: translateX(20px);
  }
  100% {
    opacity: 1;
    transform: translateX(0);
  }
}

.tool-btn:hover {
  color: #059669;
  transform: scale(1.05);
}

.tool-btn.active {
  background-color: #10B981;
  color: white;
  transform: scale(1.05);
}

.tool-background {
  position: absolute;
  inset: 0;
  background-color: #D1FAE5;
  opacity: 0;
  transition: all 0.3s ease;
  transform: scale(0);
  border-radius: inherit;
}

.tool-btn:hover .tool-background {
  transform: scale(1);
  opacity: 0.2;
}

.tool-label {
  position: absolute;
  left: 100%;
  margin-left: 0.5rem;
  padding: 0.25rem 0.5rem;
  background-color: #1F2937;
  color: white;
  font-size: 0.75rem;
  border-radius: 0.375rem;
  opacity: 0;
  transform: translateX(0.5rem);
  pointer-events: none;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.tool-btn:hover .tool-label {
  opacity: 1;
  transform: translateX(0);
}

/* Estilos específicos para el componente Dashboard.vue */
.dashboard-enter-animation {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(
    circle,
    rgba(255, 255, 255, 1) 0%,
    rgba(209, 250, 229, 0.95) 30%,
    rgba(147, 197, 253, 0.9) 70%,
    rgba(37, 99, 235, 0.85) 100%
  );
  z-index: 99;
  opacity: 1;
  animation: dashboard-fade-out 1s ease-out forwards;
  pointer-events: none;
}

@keyframes dashboard-fade-out {
  0% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}

/* Animaciones para el modal */
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

/* Animación para elementos deslizados desde la derecha */
@keyframes slide-in-right {
  from {
    transform: translateX(20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.animate-slide-in-right {
  animation: slide-in-right 0.5s ease-out forwards;
}

/* Animación de fade-in para elementos */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.5s ease-out forwards;
}

/* Nuevos estilos para los botones de herramientas */
.tool-button {
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(229, 231, 235, 1);
}

.tool-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.tool-button:active {
  transform: translateY(0);
}

/* Animación para entrada deslizante desde abajo */
@keyframes slide-in-up {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.animate-slide-in-up {
  animation: slide-in-up 0.3s ease-out forwards;
}

/* Añadir estilos específicos para las capas */
.toggle-label {
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-label::after {
  content: '';
  position: absolute;
  top: 0.25rem;
  left: 0.25rem;
  width: 1rem;
  height: 1rem;
  background-color: white;
  border-radius: 50%;
  transition: transform 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.toggle-label.active {
  background-color: #10B981;
}

.toggle-label.active::after {
  transform: translateX(1.5rem);
}
</style>
