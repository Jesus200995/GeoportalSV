/**
 * Servicio para obtener información de entidades geográficas mediante WMS GetFeatureInfo
 */

/**
 * Obtiene información de una característica geográfica en una ubicación específica del mapa
 * 
 * @param {Object} map - Instancia del mapa OpenLayers
 * @param {Array} coordinate - Coordenadas [x, y] donde se hizo clic
 * @param {Object} layer - Capa WMS activa sobre la que se quiere consultar
 * @param {Object} options - Opciones adicionales para la consulta
 * @returns {Promise} - Promesa que resuelve con la información de la característica
 */
export async function getFeatureInfo(map, coordinate, layer, options = {}) {
  try {
    if (!map || !layer || !coordinate) {
      throw new Error('Parámetros incompletos para GetFeatureInfo');
    }

    // Verificar que la capa tiene un origen WMS válido
    const source = layer.getSource();
    if (!source || !source.getFeatureInfoUrl) {
      throw new Error('La capa no soporta GetFeatureInfo');
    }

    // Obtener resolución actual y proyección
    const view = map.getView();
    const resolution = view.getResolution();
    const projection = view.getProjection().getCode();
    
    // Configurar parámetros de la consulta
    const params = {
      'INFO_FORMAT': options.format || 'application/json',
      'FEATURE_COUNT': options.featureCount || 10,
      'QUERY_LAYERS': layer.getSource().getParams().LAYERS
    };

    // Construir URL para GetFeatureInfo
    const url = source.getFeatureInfoUrl(
      coordinate,
      resolution,
      projection,
      params
    );

    if (!url) {
      throw new Error('No se pudo generar URL para GetFeatureInfo');
    }

    // Realizar la consulta HTTP
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Error en la respuesta: ${response.status}`);
    }

    // Devolver los datos como JSON
    const data = await response.json();
    
    return {
      success: true,
      layerName: layer.get('name') || layer.get('title'),
      layerId: layer.get('id'),
      data: data,
      features: data.features || [],
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.error('Error en GetFeatureInfo:', error);
    return {
      success: false,
      error: error.message,
      layerName: layer?.get('name') || 'desconocida',
      features: []
    };
  }
}

/**
 * Obtiene información de todas las capas visibles en una ubicación
 * 
 * @param {Object} map - Instancia del mapa OpenLayers
 * @param {Array} coordinate - Coordenadas [x, y] donde se hizo clic
 * @param {Array} visibleLayers - Lista de capas visibles (opcional)
 * @returns {Promise} - Promesa que resuelve con la información de todas las capas
 */
export async function getFeatureInfoFromAllLayers(map, coordinate, visibleLayers = null) {
  if (!map || !coordinate) {
    return { success: false, error: 'Parámetros incompletos' };
  }

  // Si no se proporcionan capas visibles, obtenerlas del mapa
  const layers = visibleLayers || map.getLayers().getArray().filter(layer => {
    // Solo consultar capas WMS visibles
    return layer.getVisible() && 
           layer.getSource() && 
           typeof layer.getSource().getFeatureInfoUrl === 'function';
  });

  if (layers.length === 0) {
    return { 
      success: false, 
      error: 'No hay capas visibles que soporten GetFeatureInfo',
      features: []
    };
  }

  // Consultar cada capa y combinar resultados
  const results = await Promise.all(
    layers.map(layer => getFeatureInfo(map, coordinate, layer))
  );

  // Filtrar resultados exitosos y combinar características
  const successfulResults = results.filter(result => result.success && result.features.length > 0);
  
  if (successfulResults.length === 0) {
    return { 
      success: false, 
      error: 'No se encontraron características en esta ubicación',
      features: []
    };
  }

  // Devolver el primer resultado con características
  return successfulResults[0];
}
