/**
 * Servicio para interactuar con GeoServer
 */

// URL base del servidor GeoServer
const GEOSERVER_URL = import.meta.env.VITE_GEOSERVER_URL || 'https://geoportal.sembrandodatos.com/geoserver';
const WORKSPACE = 'sembrando';

// Credenciales de autenticación para GeoServer
const GEOSERVER_AUTH = {
  username: 'admin',
  password: 'geoserver'
};

/**
 * Obtiene las capacidades del servicio WMS de GeoServer
 * @returns {Promise<Array>} Lista de capas disponibles
 */
export async function getWMSCapabilities() {
  try {
    // Construir la URL para el request GetCapabilities
    const url = `${GEOSERVER_URL}/${WORKSPACE}/wms?service=WMS&version=1.1.1&request=GetCapabilities`;
    
    // Hacer la solicitud HTTP
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Error en la respuesta: ${response.status}`);
    }

    // Obtener el texto XML de la respuesta
    const xmlText = await response.text();
    
    // Parsear el XML
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlText, "text/xml");
    
    // Extraer la lista de capas
    return parseWMSCapabilities(xmlDoc);
  } catch (error) {
    console.error("Error al obtener capacidades WMS:", error);
    return [];
  }
}

/**
 * Parsea el documento XML de GetCapabilities para extraer información de las capas
 * @param {Document} xmlDoc - Documento XML de respuesta
 * @returns {Array} Lista de capas con sus propiedades
 */
function parseWMSCapabilities(xmlDoc) {
  const layers = [];
  
  // Buscar todos los elementos Layer que tengan Name y Title
  const layerElements = xmlDoc.getElementsByTagName('Layer');
  
  for (const layerElement of layerElements) {
    // Solo procesar capas que no sean Layer contenedoras (capas con capas hijas)
    const nameElement = layerElement.getElementsByTagName('Name')[0];
    const titleElement = layerElement.getElementsByTagName('Title')[0];
    
    // Verificar que tenga nombre (las carpetas/grupos no lo tienen)
    if (nameElement && titleElement) {
      const name = nameElement.textContent;
      const title = titleElement.textContent;
      
      // Solo incluir capas del workspace especificado
      if (name.startsWith(`${WORKSPACE}:`)) {
        // Extraer propiedades adicionales si están disponibles
        const abstractElement = layerElement.getElementsByTagName('Abstract')[0];
        const abstract = abstractElement ? abstractElement.textContent : '';
        
        // Obtener los límites geográficos de la capa
        const boundingBox = getBoundingBox(layerElement);
        
        // Verificar si hay un estilo predeterminado
        const styles = getLayerStyles(layerElement);
        
        // Crear el objeto de la capa
        layers.push({
          id: name.replace(`${WORKSPACE}:`, ''),  // Quitar el prefijo del workspace
          name: name,
          title: title,
          description: abstract,
          boundingBox: boundingBox,
          styles: styles,
          legendUrl: getLegendUrl(name)
        });
      }
    }
  }
  
  return layers;
}

/**
 * Extrae el bounding box de un elemento Layer
 * @param {Element} layerElement - Elemento XML de la capa
 * @returns {Object} Objeto con las coordenadas del bounding box
 */
function getBoundingBox(layerElement) {
  const boundingBoxElement = layerElement.getElementsByTagName('BoundingBox')[0];
  
  if (boundingBoxElement) {
    return {
      minx: boundingBoxElement.getAttribute('minx'),
      miny: boundingBoxElement.getAttribute('miny'),
      maxx: boundingBoxElement.getAttribute('maxx'),
      maxy: boundingBoxElement.getAttribute('maxy'),
      crs: boundingBoxElement.getAttribute('CRS') || boundingBoxElement.getAttribute('SRS')
    };
  }
  
  return null;
}

/**
 * Extrae los estilos disponibles para una capa
 * @param {Element} layerElement - Elemento XML de la capa
 * @returns {Array} Lista de estilos disponibles
 */
function getLayerStyles(layerElement) {
  const styles = [];
  const styleElements = layerElement.getElementsByTagName('Style');
  
  for (const styleElement of styleElements) {
    const nameElement = styleElement.getElementsByTagName('Name')[0];
    const titleElement = styleElement.getElementsByTagName('Title')[0];
    
    if (nameElement && titleElement) {
      styles.push({
        name: nameElement.textContent,
        title: titleElement.textContent
      });
    }
  }
  
  return styles;
}

/**
 * Genera la URL para obtener la leyenda de una capa
 * @param {string} layerName - Nombre completo de la capa (con prefijo de workspace)
 * @returns {string} URL de la leyenda
 */
function getLegendUrl(layerName) {
  return `${GEOSERVER_URL}/wms?REQUEST=GetLegendGraphic&VERSION=1.0.0&FORMAT=image/png&WIDTH=20&HEIGHT=20&LAYER=${layerName}`;
}

/**
 * Genera los parámetros para una capa WMS
 * @param {string} layerName - Nombre completo de la capa (con prefijo de workspace)
 * @returns {Object} Parámetros para la capa WMS
 */
export function getWMSLayerParams(layerName) {
  return {
    LAYERS: layerName,
    TILED: true,
    FORMAT: 'image/png',
    TRANSPARENT: true,
    VERSION: '1.1.1'
  };
}

/**
 * Obtiene la URL base del servidor GeoServer
 * @returns {string} URL base
 */
export function getGeoServerUrl() {
  return GEOSERVER_URL;
}

/**
 * Obtiene la URL de WMS para el workspace actual
 * @returns {string} URL del servicio WMS
 */
export function getWMSUrl() {
  return `${GEOSERVER_URL}/${WORKSPACE}/wms`;
}

/**
 * Obtiene el nombre del workspace
 * @returns {string} Nombre del workspace
 */
export function getWorkspace() {
  return WORKSPACE;
}

/**
 * Obtiene la lista de capas disponibles utilizando el API REST de GeoServer
 * @returns {Promise<Array>} Lista de capas disponibles
 */
export async function getAvailableLayers() {
  try {
    // URL del API REST de GeoServer para listar feature types
    const url = `${GEOSERVER_URL}/rest/workspaces/${WORKSPACE}/featuretypes.json`;
    
    // Generar las credenciales de autenticación básica
    const authHeader = 'Basic ' + btoa(`${GEOSERVER_AUTH.username}:${GEOSERVER_AUTH.password}`);
    
    console.log('Obteniendo capas desde:', url);
    
    // Hacer la solicitud HTTP con autenticación
    const response = await fetch(url, {
      headers: {
        'Authorization': authHeader,
        'Accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Error en la respuesta: ${response.status}`);
    }

    // Obtener los datos en formato JSON
    const data = await response.json();
    console.log('Respuesta API REST GeoServer:', data);
    
    // Verificar que la estructura esperada de datos existe
    if (!data.featureTypes || !data.featureTypes.featureType) {
      console.warn('No se encontraron capas en el API REST de GeoServer');
      return [];
    }
    
    // Procesar y devolver la lista de capas
    const processedLayers = data.featureTypes.featureType.map(layer => ({
      name: layer.name,
      title: layer.title || layer.name,
      abstract: layer.abstract || '',
      fullName: `${WORKSPACE}:${layer.name}`,
      workspace: WORKSPACE,
      wmsUrl: `${GEOSERVER_URL}/${WORKSPACE}/wms`,
      wfsUrl: `${GEOSERVER_URL}/wfs`,
      legendUrl: `${GEOSERVER_URL}/wms?REQUEST=GetLegendGraphic&VERSION=1.0.0&FORMAT=image/png&WIDTH=20&HEIGHT=20&LAYER=${WORKSPACE}:${layer.name}`
    }));
    
    console.log('Capas procesadas:', processedLayers);
    return processedLayers;
  } catch (error) {
    console.error("Error al obtener capas desde GeoServer REST API:", error);
    return [];
  }
}

/**
 * Comprueba si una capa existe en GeoServer
 * @param {string} layerName - Nombre de la capa (sin el prefijo del workspace)
 * @returns {Promise<boolean>} Si la capa existe o no
 */
export async function checkLayerExists(layerName) {
  try {
    const url = `${GEOSERVER_URL}/rest/workspaces/${WORKSPACE}/featuretypes/${layerName}`;
    const authHeader = 'Basic ' + btoa(`${GEOSERVER_AUTH.username}:${GEOSERVER_AUTH.password}`);
    
    const response = await fetch(url, {
      headers: {
        'Authorization': authHeader,
        'Accept': 'application/json'
      }
    });
    
    return response.ok;
  } catch (error) {
    console.error(`Error al comprobar si existe la capa ${layerName}:`, error);
    return false;
  }
}

/**
 * Monitorea la disponibilidad de una capa recién subida
 * @param {string} layerName - Nombre de la capa (sin el prefijo del workspace)
 * @param {number} maxAttempts - Número máximo de intentos (por defecto 10)
 * @param {number} interval - Intervalo entre intentos en ms (por defecto 1000)
 * @returns {Promise<boolean>} Si la capa está disponible
 */
export async function waitForLayerAvailability(layerName, maxAttempts = 10, interval = 1000) {
  console.log(`Esperando a que la capa ${layerName} esté disponible en GeoServer...`);
  let attempts = 0;
  
  while (attempts < maxAttempts) {
    const exists = await checkLayerExists(layerName);
    
    if (exists) {
      console.log(`Capa ${layerName} disponible en GeoServer después de ${attempts + 1} intentos`);
      return true;
    }
    
    console.log(`Intento ${attempts + 1}/${maxAttempts}: La capa ${layerName} aún no está disponible`);
    attempts++;
    
    // Esperar el intervalo antes de intentar nuevamente
    await new Promise(resolve => setTimeout(resolve, interval));
  }
  
  console.warn(`La capa ${layerName} no está disponible después de ${maxAttempts} intentos`);
  return false;
}
