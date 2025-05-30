// Servicio para interactuar con la base de datos PostgreSQL/PostGIS

// URL base para las peticiones a la API
const API_URL = import.meta.env.VITE_API_URL || 'http://31.97.8.51:5000';

/**
 * Obtiene los datos tabulares de una capa específica
 * @param {string} layerName - Nombre de la capa
 * @returns {Promise<Array>} - Datos de la capa
 */
export const getLayerData = async (layerName) => {
  try {
    if (!layerName) {
      throw new Error('Nombre de capa no especificado');
    }
    
    // Aquí normalmente iríamos a la API
    // const response = await fetch(`${API_URL}/api/layers/${layerName}/data`);
    // if (!response.ok) throw new Error('Error al obtener datos de la capa');
    // return await response.json();
    
    // Solución temporal con datos de prueba
    console.log(`Generando datos de prueba para la capa: ${layerName}`);
    const mockData = generateMockData(layerName);
    console.log(`Datos generados:`, mockData.slice(0, 2), `... (total: ${mockData.length})`);
    return mockData;
  } catch (error) {
    console.error('Error al obtener datos de la capa:', error);
    throw error; // Propagar el error original para mejor manejo
  }
};

/**
 * Función para generar datos de prueba según el tipo de capa
 * @param {string} layerName - Nombre de la capa
 * @returns {Array} - Datos simulados
 */
const generateMockData = (layerName) => {
  // Normalizamos el nombre para hacer la detección más robusta
  const normalizedName = (layerName || '').toLowerCase();
  
  // Generamos entre 20-50 registros aleatorios
  const count = Math.floor(Math.random() * 30) + 20;
  const result = [];
  
  // Determinamos las columnas según el nombre de la capa
  let columns = {};
  
  // Asignamos columnas según el tipo de capa
  if (normalizedName.includes('municipio') || normalizedName.includes('admin') || 
      normalizedName.includes('territorio') || normalizedName.includes('limites')) {
    columns = {
      id: 'number',
      nombre: 'string',
      poblacion: 'number',
      area: 'number',
      densidad: 'number',
      region: 'category'
    };
  } else if (normalizedName.includes('cultivo') || normalizedName.includes('agricola') || 
             normalizedName.includes('cosecha') || normalizedName.includes('produccion')) {
    columns = {
      id: 'number',
      tipo_cultivo: 'category',
      area_hectareas: 'number',
      produccion_ton: 'number',
      valor_produccion: 'number',
      rendimiento: 'number'
    };
  } else if (normalizedName.includes('clima') || normalizedName.includes('precipitacion') || 
             normalizedName.includes('temperatura')) {
    columns = {
      id: 'number',
      fecha: 'date',
      temperatura: 'number',
      precipitacion: 'number',
      humedad: 'number'
    };
  } else {
    // Columnas genéricas para cualquier otra capa
    columns = {
      id: 'number',
      nombre: 'string',
      valor: 'number',
      categoria: 'category',
      fecha: 'date'
    };
  }
  
  // Generamos los datos aleatorios
  for (let i = 0; i < count; i++) {
    const record = {};
    Object.entries(columns).forEach(([key, type]) => {
      if (type === 'number') {
        // Números positivos aleatorios con variedad
        record[key] = key === 'id' ? i + 1 : Math.floor(Math.random() * 10000) / 10;
      } else if (type === 'string') {
        // Nombres variados para más realismo
        const names = ['San Salvador', 'Santa Ana', 'San Miguel', 'Sonsonate', 
                      'La Libertad', 'Ahuachapán', 'La Unión', 'La Paz', 
                      'Chalatenango', 'Cuscatlán', 'Morazán', 'San Vicente', 
                      'Cabañas', 'Usulután'];
        record[key] = key === 'nombre' && i < names.length ? 
                      names[i] : `Item ${i + 1}`;
      } else if (type === 'category') {
        // Categorías más descriptivas
        let categories;
        if (key === 'region') {
          categories = ['Norte', 'Sur', 'Este', 'Oeste', 'Central'];
        } else if (key === 'tipo_cultivo') {
          categories = ['Maíz', 'Frijol', 'Café', 'Caña', 'Arroz'];
        } else {
          categories = ['Categoría A', 'Categoría B', 'Categoría C', 'Categoría D', 'Categoría E'];
        }
        record[key] = categories[Math.floor(Math.random() * categories.length)];
      } else if (type === 'date') {
        // Fechas más recientes para datos temporales
        const date = new Date();
        date.setDate(date.getDate() - Math.floor(Math.random() * 365));
        record[key] = date.toISOString().split('T')[0];
      }
    });
    result.push(record);
  }
  
  return result;
};
