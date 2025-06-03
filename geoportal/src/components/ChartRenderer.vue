<script setup>
import { ref, onMounted, watch, onBeforeUnmount, nextTick, computed } from 'vue';
import { Chart, registerables } from 'chart.js';

// Registrar componentes de Chart.js
Chart.register(...registerables);

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  layer: {
    type: Object,
    required: true
  },
  // Añadir class como prop para evitar advertencia
  class: {
    type: String,
    default: ''
  }
});

const charts = ref([]);
const chartConfigs = ref([]);
const error = ref(null);
// Bandera para controlar si se están renderizando gráficas
const isRendering = ref(false);
// ID único para esta instancia del componente
const instanceId = ref(`chart-instance-${Date.now()}-${Math.floor(Math.random() * 1000)}`);

// Determinar el tipo de capa basado en su nombre
const layerType = computed(() => {
  if (!props.layer.name) return 'generic';
  
  const name = props.layer.name.toLowerCase();
  
  if (name.includes('municipio') || name.includes('territorio') || name.includes('admin') || name.includes('limite')) {
    return 'administrative';
  } else if (name.includes('cultivo') || name.includes('agricola') || name.includes('produccion') || name.includes('cosecha')) {
    return 'agricultural';
  } else if (name.includes('clima') || name.includes('temperatura') || name.includes('precipitacion')) {
    return 'climate';
  } else if (name.includes('poblacion') || name.includes('social') || name.includes('demografico')) {
    return 'demographic';
  } else if (name.includes('suelo') || name.includes('terreno') || name.includes('tierra')) {
    return 'soil';
  } else if (name.includes('agua') || name.includes('hidrico') || name.includes('rio')) {
    return 'water';
  }
  
  return 'generic';
});

// Generar colores para las gráficas
const generateColors = (count) => {
  const baseColors = [
    'rgba(54, 162, 235, 0.7)',   // Azul
    'rgba(255, 99, 132, 0.7)',   // Rojo
    'rgba(255, 206, 86, 0.7)',   // Amarillo
    'rgba(75, 192, 192, 0.7)',   // Verde azulado
    'rgba(153, 102, 255, 0.7)',  // Morado
    'rgba(255, 159, 64, 0.7)',   // Naranja
    'rgba(199, 199, 199, 0.7)',  // Gris
    'rgba(83, 102, 255, 0.7)',   // Azul índigo
    'rgba(255, 99, 255, 0.7)',   // Rosa
    'rgba(0, 162, 150, 0.7)',    // Verde esmeralda
  ];
  
  // Si necesitamos más colores que los base, los generamos aleatoriamente
  if (count <= baseColors.length) {
    return baseColors.slice(0, count);
  }
  
  const colors = [...baseColors];
  for (let i = baseColors.length; i < count; i++) {
    const r = Math.floor(Math.random() * 255);
    const g = Math.floor(Math.random() * 255);
    const b = Math.floor(Math.random() * 255);
    colors.push(`rgba(${r}, ${g}, ${b}, 0.7)`);
  }
  
  return colors;
};

// Función principal para procesar datos y generar configuraciones de gráficas
const processData = () => {
  try {
    error.value = null;
    chartConfigs.value = [];
    
    // Verificar que tenemos datos
    if (!props.data || !Array.isArray(props.data) || props.data.length === 0) {
      error.value = 'No hay datos disponibles para generar gráficas';
      return;
    }
    
    console.log(`Procesando datos para capa: ${props.layer.name || 'desconocida'} (Tipo: ${layerType.value})`);

    // Obtener las columnas de los datos
    const columns = Object.keys(props.data[0]);
    
    // Filtrar columnas técnicas o irrelevantes
    const validColumns = columns.filter(column => 
      !column.toLowerCase().includes('geom') && 
      !column.toLowerCase().includes('_uid') &&
      !column.toLowerCase().includes('shape') &&
      column.toLowerCase() !== 'fid' &&
      column.toLowerCase() !== 'ogc_fid'
    );
    
    // Identificar columnas numéricas y categóricas
    const columnTypes = {};
    validColumns.forEach(column => {
      // Analizar los primeros valores para determinar el tipo
      const sampleValues = props.data.slice(0, 10).map(item => item[column]);
      
      // Verificar si es numérico
      const isNumeric = sampleValues.some(val => 
        val !== null && val !== undefined && !isNaN(parseFloat(val))
      );
      
      // Contar valores únicos para determinar si es categórico
      const uniqueValues = new Set(props.data.map(item => 
        item[column] !== null && item[column] !== undefined ? String(item[column]) : null
      ).filter(val => val !== null));
      
      // Si tiene pocos valores únicos, considerarlo categórico
      const isCategorical = uniqueValues.size <= 15;
      
      // Guardar tipo de columna
      columnTypes[column] = {
        isNumeric,
        isCategorical,
        uniqueValues: [...uniqueValues]
      };
    });
    
    // Generar gráficos según el tipo de capa
    generateChartsForLayerType(validColumns, columnTypes);
    
    console.log(`Se generaron ${chartConfigs.value.length} configuraciones de gráficas para ${props.layer.name}`);
  } catch (err) {
    console.error('Error al procesar datos:', err);
    error.value = `Error al procesar los datos: ${err.message}`;
  }
};

// Generar gráficos específicos según el tipo de capa
const generateChartsForLayerType = (columns, columnTypes) => {
  switch (layerType.value) {
    case 'administrative':
      generateAdministrativeCharts(columns, columnTypes);
      break;
    case 'agricultural':
      generateAgriculturalCharts(columns, columnTypes);
      break;
    case 'climate':
      generateClimateCharts(columns, columnTypes);
      break;
    case 'demographic':
      generateDemographicCharts(columns, columnTypes);
      break;
    case 'soil':
      generateSoilCharts(columns, columnTypes);
      break;
    case 'water':
      generateWaterCharts(columns, columnTypes);
      break;
    default:
      generateGenericCharts(columns, columnTypes);
  }
};

// Función para formatear nombres de columnas (snake_case a Title Case)
const formatColumnName = (name) => {
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Generar gráficos para capas administrativas (municipios, territorios)
const generateAdministrativeCharts = (columns, columnTypes) => {
  // Buscar columnas de población, área, región, etc.
  const populationColumn = columns.find(col => 
    col.toLowerCase().includes('pobl') || 
    col.toLowerCase().includes('habit')
  );
  
  const areaColumn = columns.find(col => 
    col.toLowerCase().includes('area') || 
    col.toLowerCase().includes('superficie')
  );
  
  const regionColumn = columns.find(col => 
    col.toLowerCase().includes('region') || 
    col.toLowerCase().includes('zona')
  );
  
  const nameColumn = columns.find(col => 
    col.toLowerCase().includes('nombre') || 
    col.toLowerCase().includes('nom')
  );
  
  // Gráfico de población por municipio/territorio si existe
  if (populationColumn && nameColumn && columnTypes[populationColumn].isNumeric) {
    createBarOrPieChart(
      nameColumn, 
      populationColumn, 
      'Población por ' + formatColumnName(nameColumn), 
      'bar'
    );
  }
  
  // Gráfico de área por municipio/territorio si existe
  if (areaColumn && nameColumn && columnTypes[areaColumn].isNumeric) {
    createBarOrPieChart(
      nameColumn, 
      areaColumn, 
      'Área por ' + formatColumnName(nameColumn), 
      'bar'
    );
  }
  
  // Gráfico de distribución por región si existe
  if (regionColumn && columnTypes[regionColumn].isCategorical) {
    createDistributionChart(regionColumn, 'Distribución por Región');
  }
  
  // Generar al menos dos gráficos genéricos si no se creó ninguno específico
  if (chartConfigs.value.length < 2) {
    generateGenericCharts(columns, columnTypes);
  }
};

// Generar gráficos para capas agrícolas
const generateAgriculturalCharts = (columns, columnTypes) => {
  // Buscar columnas relacionadas con cultivos
  const cropTypeColumn = columns.find(col => 
    col.toLowerCase().includes('cultivo') || 
    col.toLowerCase().includes('crop')
  );
  
  const productionColumn = columns.find(col => 
    col.toLowerCase().includes('produccion') || 
    col.toLowerCase().includes('producción') ||
    col.toLowerCase().includes('production')
  );
  
  const areaColumn = columns.find(col => 
    col.toLowerCase().includes('area') || 
    col.toLowerCase().includes('superficie') ||
    col.toLowerCase().includes('hectarea')
  );
  
  const yieldColumn = columns.find(col => 
    col.toLowerCase().includes('rendimiento') || 
    col.toLowerCase().includes('yield')
  );
  
  // Gráfico de distribución de cultivos
  if (cropTypeColumn && columnTypes[cropTypeColumn].isCategorical) {
    createDistributionChart(cropTypeColumn, 'Distribución de Cultivos');
  }
  
  // Gráfico de producción por tipo de cultivo
  if (cropTypeColumn && productionColumn && columnTypes[productionColumn].isNumeric) {
    createBarOrPieChart(
      cropTypeColumn, 
      productionColumn, 
      'Producción por Tipo de Cultivo', 
      'bar'
    );
  }
  
  // Gráfico de área por tipo de cultivo
  if (cropTypeColumn && areaColumn && columnTypes[areaColumn].isNumeric) {
    createBarOrPieChart(
      cropTypeColumn, 
      areaColumn, 
      'Área por Tipo de Cultivo', 
      'bar'
    );
  }
  
  // Gráfico de rendimiento por tipo de cultivo
  if (cropTypeColumn && yieldColumn && columnTypes[yieldColumn].isNumeric) {
    createBarOrPieChart(
      cropTypeColumn, 
      yieldColumn, 
      'Rendimiento por Tipo de Cultivo', 
      'bar'
    );
  }
  
  // Generar gráficos genéricos si no se creó ninguno específico
  if (chartConfigs.value.length < 2) {
    generateGenericCharts(columns, columnTypes);
  }
};

// Generar gráficos para capas climáticas
const generateClimateCharts = (columns, columnTypes) => {
  // Buscar columnas relacionadas con clima
  const temperatureColumn = columns.find(col => 
    col.toLowerCase().includes('temp') || 
    col.toLowerCase().includes('temperatura')
  );
  
  const precipitationColumn = columns.find(col => 
    col.toLowerCase().includes('precipitacion') || 
    col.toLowerCase().includes('precipitation') ||
    col.toLowerCase().includes('lluvia')
  );
  
  const dateColumn = columns.find(col => 
    col.toLowerCase().includes('fecha') || 
    col.toLowerCase().includes('date') ||
    col.toLowerCase().includes('period')
  );
  
  const regionColumn = columns.find(col => 
    col.toLowerCase().includes('region') || 
    col.toLowerCase().includes('zona') ||
    col.toLowerCase().includes('localidad')
  );
  
  // Gráfico de temperatura por fecha o región
  if (temperatureColumn && columnTypes[temperatureColumn].isNumeric) {
    if (dateColumn) {
      createLineChart(
        dateColumn, 
        temperatureColumn, 
        'Temperatura a lo largo del tiempo'
      );
    } else if (regionColumn) {
      createBarOrPieChart(
        regionColumn, 
        temperatureColumn, 
        'Temperatura por Región', 
        'bar'
      );
    } else {
      createHistogram(temperatureColumn, 'Distribución de Temperatura');
    }
  }
  
  // Gráfico de precipitación por fecha o región
  if (precipitationColumn && columnTypes[precipitationColumn].isNumeric) {
    if (dateColumn) {
      createLineChart(
        dateColumn, 
        precipitationColumn, 
        'Precipitación a lo largo del tiempo'
      );
    } else if (regionColumn) {
      createBarOrPieChart(
        regionColumn, 
        precipitationColumn, 
        'Precipitación por Región', 
        'bar'
      );
    } else {
      createHistogram(precipitationColumn, 'Distribución de Precipitación');
    }
  }
  
  // Gráfico de correlación entre temperatura y precipitación
  if (temperatureColumn && precipitationColumn && 
      columnTypes[temperatureColumn].isNumeric && 
      columnTypes[precipitationColumn].isNumeric) {
    createScatterChart(
      temperatureColumn, 
      precipitationColumn, 
      'Relación entre Temperatura y Precipitación'
    );
  }
  
  // Generar gráficos genéricos si no se creó ninguno específico
  if (chartConfigs.value.length < 2) {
    generateGenericCharts(columns, columnTypes);
  }
};

// Generar gráficos para capas demográficas
const generateDemographicCharts = (columns, columnTypes) => {
  // Implementación similar a las anteriores
  const populationColumn = columns.find(col => 
    col.toLowerCase().includes('pobl') || 
    col.toLowerCase().includes('habit')
  );
  
  const densityColumn = columns.find(col => 
    col.toLowerCase().includes('densidad') || 
    col.toLowerCase().includes('density')
  );
  
  const regionColumn = columns.find(col => 
    col.toLowerCase().includes('region') || 
    col.toLowerCase().includes('zona') ||
    col.toLowerCase().includes('municipio')
  );
  
  // Generar gráficos según columnas disponibles
  if (populationColumn && regionColumn && columnTypes[populationColumn].isNumeric) {
    createBarOrPieChart(
      regionColumn, 
      populationColumn, 
      'Población por ' + formatColumnName(regionColumn), 
      'bar'
    );
  }
  
  if (densityColumn && regionColumn && columnTypes[densityColumn].isNumeric) {
    createBarOrPieChart(
      regionColumn, 
      densityColumn, 
      'Densidad Poblacional por ' + formatColumnName(regionColumn), 
      'bar'
    );
  }
  
  // Generar gráficos genéricos si no se creó ninguno específico
  if (chartConfigs.value.length < 2) {
    generateGenericCharts(columns, columnTypes);
  }
};

// Generar gráficos para capas de suelos
const generateSoilCharts = (columns, columnTypes) => {
  // Implementación para capas de suelos
  const soilTypeColumn = columns.find(col => 
    col.toLowerCase().includes('tipo_suelo') || 
    col.toLowerCase().includes('suelo') ||
    col.toLowerCase().includes('soil')
  );
  
  if (soilTypeColumn && columnTypes[soilTypeColumn].isCategorical) {
    createDistributionChart(soilTypeColumn, 'Distribución de Tipos de Suelo');
  }
  
  // Generar gráficos genéricos si no se creó ninguno específico
  if (chartConfigs.value.length < 2) {
    generateGenericCharts(columns, columnTypes);
  }
};

// Generar gráficos para capas hídricas
const generateWaterCharts = (columns, columnTypes) => {
  // Implementación para capas hídricas
  const waterBodyColumn = columns.find(col => 
    col.toLowerCase().includes('tipo_agua') || 
    col.toLowerCase().includes('agua') ||
    col.toLowerCase().includes('water')
  );
  
  if (waterBodyColumn && columnTypes[waterBodyColumn].isCategorical) {
    createDistributionChart(waterBodyColumn, 'Distribución de Cuerpos de Agua');
  }
  
  // Generar gráficos genéricos si no se creó ninguno específico
  if (chartConfigs.value.length < 2) {
    generateGenericCharts(columns, columnTypes);
  }
};

// Generar gráficos genéricos para cualquier tipo de capa
const generateGenericCharts = (columns, columnTypes) => {
  // Crear gráficos para columnas categóricas
  const categoricalColumns = columns.filter(col => columnTypes[col].isCategorical);
  categoricalColumns.slice(0, 3).forEach(column => {
    createDistributionChart(column, `Distribución por ${formatColumnName(column)}`);
  });
  
  // Crear histogramas para columnas numéricas
  const numericColumns = columns.filter(col => columnTypes[col].isNumeric);
  numericColumns.slice(0, 3).forEach(column => {
    createHistogram(column, `Distribución de ${formatColumnName(column)}`);
  });
  
  // Crear gráficos de correlación entre pares de columnas numéricas (máximo 2)
  if (numericColumns.length >= 2) {
    for (let i = 0; i < Math.min(2, numericColumns.length - 1); i++) {
      createScatterChart(
        numericColumns[i], 
        numericColumns[i + 1], 
        `Relación entre ${formatColumnName(numericColumns[i])} y ${formatColumnName(numericColumns[i + 1])}`
      );
    }
  }
};

// Crear gráfico de barras o pie
const createBarOrPieChart = (labelColumn, valueColumn, title, type = 'bar') => {
  try {
    // Agrupar datos por etiqueta
    const labelValues = {};
    props.data.forEach(item => {
      const label = item[labelColumn];
      const value = parseFloat(item[valueColumn]);
      
      if (label && !isNaN(value)) {
        labelValues[label] = (labelValues[label] || 0) + value;
      }
    });
    
    // Obtener etiquetas y valores ordenados
    const sortedLabels = Object.keys(labelValues)
      .sort((a, b) => labelValues[b] - labelValues[a])
      .slice(0, 10); // Limitar a 10 etiquetas para legibilidad
    
    const values = sortedLabels.map(label => labelValues[label]);
    const colors = generateColors(sortedLabels.length);
    
    // Determinar si usar pie o bar basado en número de categorías
    const chartType = (type === 'auto' && sortedLabels.length <= 5) ? 'pie' : type;
    
    // Crear configuración
    chartConfigs.value.push({
      type: chartType,
      title: title,
      data: {
        labels: sortedLabels,
        datasets: [{
          label: formatColumnName(valueColumn),
          data: values,
          backgroundColor: colors,
          borderColor: colors.map(color => color.replace('0.7', '1')),
          borderWidth: 1
        }]
      }
    });
  } catch (err) {
    console.error(`Error al crear gráfico de ${type}:`, err);
  }
};

// Crear gráfico de distribución (pie o barras)
const createDistributionChart = (column, title) => {
  try {
    // Contar ocurrencias de cada valor
    const valueCounts = {};
    props.data.forEach(item => {
      const value = item[column];
      if (value !== null && value !== undefined) {
        valueCounts[value] = (valueCounts[value] || 0) + 1;
      }
    });
    
    // Ordenar valores por frecuencia
    const sortedValues = Object.keys(valueCounts)
      .sort((a, b) => valueCounts[b] - valueCounts[a])
      .slice(0, 10); // Limitar a 10 categorías
    
    const counts = sortedValues.map(value => valueCounts[value]);
    const colors = generateColors(sortedValues.length);
    
    // Usar pie para pocas categorías, barras para muchas
    const chartType = sortedValues.length <= 5 ? 'pie' : 'bar';
    
    chartConfigs.value.push({
      type: chartType,
      title: title,
      data: {
        labels: sortedValues,
        datasets: [{
          label: 'Frecuencia',
          data: counts,
          backgroundColor: colors,
          borderColor: colors.map(color => color.replace('0.7', '1')),
          borderWidth: 1
        }]
      }
    });
  } catch (err) {
    console.error('Error al crear gráfico de distribución:', err);
  }
};

// Crear histograma para datos numéricos
const createHistogram = (column, title) => {
  try {
    // Obtener valores numéricos
    const values = props.data
      .map(item => parseFloat(item[column]))
      .filter(val => !isNaN(val));
    
    if (values.length < 5) return; // No hay suficientes datos
    
    // Calcular bins para histograma
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min;
    const binCount = Math.min(10, Math.ceil(Math.sqrt(values.length)));
    const binSize = range / binCount;
    
    // Crear bins y contar valores
    const bins = Array(binCount).fill(0);
    const binLabels = Array(binCount).fill('');
    
    values.forEach(val => {
      const binIndex = Math.min(Math.floor((val - min) / binSize), binCount - 1);
      bins[binIndex]++;
    });
    
    // Crear etiquetas para los bins
    for (let i = 0; i < binCount; i++) {
      const lowerBound = min + (i * binSize);
      const upperBound = lowerBound + binSize;
      binLabels[i] = `${lowerBound.toFixed(1)} - ${upperBound.toFixed(1)}`;
    }
    
    chartConfigs.value.push({
      type: 'bar',
      title: title,
      data: {
        labels: binLabels,
        datasets: [{
          label: formatColumnName(column),
          data: bins,
          backgroundColor: 'rgba(75, 192, 192, 0.7)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1
        }]
      }
    });
  } catch (err) {
    console.error('Error al crear histograma:', err);
  }
};

// Crear gráfico de línea (para series temporales)
const createLineChart = (xColumn, yColumn, title) => {
  try {
    // Preparar datos
    const dataPoints = props.data
      .filter(item => item[xColumn] !== null && item[yColumn] !== null)
      .map(item => ({
        x: item[xColumn],
        y: parseFloat(item[yColumn])
      }))
      .filter(point => !isNaN(point.y))
      .sort((a, b) => {
        // Intentar ordenar por fecha si es posible
        const dateA = new Date(a.x);
        const dateB = new Date(b.x);
        
        if (!isNaN(dateA) && !isNaN(dateB)) {
          return dateA - dateB;
        }
        
        // Caer en ordenamiento de string si no son fechas
        return String(a.x).localeCompare(String(b.x));
      });
    
    if (dataPoints.length < 2) return; // No hay suficientes datos
    
    const labels = dataPoints.map(point => point.x);
    const values = dataPoints.map(point => point.y);
    
    chartConfigs.value.push({
      type: 'line',
      title: title,
      data: {
        labels: labels,
        datasets: [{
          label: formatColumnName(yColumn),
          data: values,
          fill: false,
          backgroundColor: 'rgba(54, 162, 235, 0.7)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 2,
          tension: 0.1
        }]
      }
    });
  } catch (err) {
    console.error('Error al crear gráfico de línea:', err);
  }
};

// Crear gráfico de dispersión (scatter)
const createScatterChart = (xColumn, yColumn, title) => {
  try {
    // Preparar datos
    const dataPoints = props.data
      .filter(item => 
        item[xColumn] !== null && 
        item[yColumn] !== null && 
        !isNaN(parseFloat(item[xColumn])) && 
        !isNaN(parseFloat(item[yColumn]))
      )
      .map(item => ({
        x: parseFloat(item[xColumn]),
        y: parseFloat(item[yColumn])
      }));
    
    if (dataPoints.length < 5) return; // No hay suficientes datos
    
    chartConfigs.value.push({
      type: 'scatter',
      title: title,
      data: {
        datasets: [{
          label: `${formatColumnName(xColumn)} vs ${formatColumnName(yColumn)}`,
          data: dataPoints,
          backgroundColor: 'rgba(54, 162, 235, 0.7)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1,
          pointRadius: 5,
          pointHoverRadius: 7
        }]
      }
    });
  } catch (err) {
    console.error('Error al crear gráfico de dispersión:', err);
  }
};

// Limpiar gráficas completamente - versión mejorada
const destroyCharts = () => {
  // Primero intentamos destruir cada instancia de Chart
  charts.value.forEach(chart => {
    try {
      chart.destroy();
    } catch (err) {
      console.error('Error al destruir gráfica:', err);
    }
  });
  
  // Reiniciamos el array de charts
  charts.value = [];
  
  // Limpieza adicional: destruir todas las instancias de Chart.js en el DOM
  // Esto soluciona el problema de "Canvas is already in use"
  const allChartInstances = Object.values(Chart.instances);
  if (allChartInstances.length > 0) {
    console.log(`Limpiando ${allChartInstances.length} instancias de Chart.js huérfanas`);
    allChartInstances.forEach(instance => {
      try {
        instance.destroy();
      } catch (err) {
        console.error('Error al destruir instancia huérfana:', err);
      }
    });
  }
};

// Renderizar gráficas - versión mejorada con reseteo de canvas
const renderCharts = async () => {
  // Evitar múltiples renders simultáneos
  if (isRendering.value) {
    console.log('Ya hay un proceso de renderizado en curso, se omite la solicitud');
    return;
  }
  
  try {
    isRendering.value = true;
    error.value = null;
    
    // 1. Limpiar gráficas existentes completamente
    destroyCharts();
    
    // 2. Esperar a que el DOM se actualice
    await nextTick();
    
    // 3. Recrear los elementos canvas antes de renderizar
    const chartsContainer = document.getElementById('charts-container');
    if (chartsContainer) {
      // Vaciar el contenedor
      chartsContainer.innerHTML = '';
      
      // Crear nuevos canvas para cada gráfica
      chartConfigs.value.forEach((config, index) => {
        const chartWrapper = document.createElement('div');
        chartWrapper.className = 'chart-card';
        
        // Añadir título de la gráfica antes del contenedor
        const titleContainer = document.createElement('div');
        titleContainer.className = 'chart-title-container';
        
        const title = document.createElement('h4');
        title.className = 'chart-title';
        title.textContent = config.title;
        
        titleContainer.appendChild(title);
        chartWrapper.appendChild(titleContainer);
        
        // Contenedor para la gráfica
        const chartContainer = document.createElement('div');
        chartContainer.className = 'chart-container';
        
        const canvas = document.createElement('canvas');
        canvas.id = `chart-${index}-${instanceId.value}`;
        
        chartContainer.appendChild(canvas);
        chartWrapper.appendChild(chartContainer);
        
        chartsContainer.appendChild(chartWrapper);
      });
    }
    
    // 4. Esperar a que el DOM se actualice nuevamente
    await nextTick();
    
    // 5. Crear nuevas gráficas
    setTimeout(() => {
      try {
        chartConfigs.value.forEach((config, index) => {
          const canvasId = `chart-${index}-${instanceId.value}`;
          const canvas = document.getElementById(canvasId);
          
          if (!canvas) {
            console.warn(`Canvas #${canvasId} no encontrado`);
            return;
          }
          
          console.log(`Renderizando gráfica #${index} (${config.type})...`);
          
          // Crear la instancia de Chart
          const chart = new Chart(canvas, {
            type: config.type,
            data: config.data,
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  position: 'top',
                  labels: {
                    font: {
                      size: 11
                    },
                    boxWidth: 12,
                    padding: 8
                  }
                },
                title: {
                  display: false, // Quitamos el título interno ya que lo mostramos fuera
                  text: config.title,
                  font: {
                    size: 14,
                    weight: 'bold'
                  }
                },
                tooltip: {
                  enabled: true,
                  mode: 'index',
                  intersect: false
                }
              }
            }
          });
          
          charts.value.push(chart);
        });
        
        console.log(`${charts.value.length} gráficas renderizadas correctamente`);
      } catch (err) {
        console.error('Error al renderizar gráficas:', err);
        error.value = 'Error al crear las gráficas: ' + err.message;
      } finally {
        isRendering.value = false;
      }
    }, 100);
  } catch (err) {
    console.error('Error en proceso de renderizado:', err);
    error.value = 'Error durante el proceso de renderizado: ' + err.message;
    isRendering.value = false;
  }
};

// Función para optimizar la disposición de las gráficas
const optimizeChartsLayout = (configs) => {
  if (!configs || configs.length === 0) return [];
  
  // Clonar las configuraciones para no modificar las originales
  const layoutConfigs = [...configs].map((config, index) => ({
    ...config,
    originalIndex: index
  }));
  
  // Identificar gráficas más importantes que merecen más espacio
  layoutConfigs.forEach(config => {
    // Pie charts y gráficas de línea generalmente necesitan menos espacio horizontal
    if (config.type === 'pie') {
      config.importance = 'small';
    } 
    // Scatter plots y gráficas de barras horizontales necesitan más espacio
    else if (config.type === 'scatter' || config.type === 'horizontalBar') {
      config.importance = 'large';
    }
    // Por defecto, tamaño mediano
    else {
      config.importance = 'medium';
    }
    
    // Determinar si el título es corto o largo
    config.titleLength = config.title.length < 25 ? 'short' : 'long';
  });
  
  // Ordenar para poner primero las gráficas más importantes
  layoutConfigs.sort((a, b) => {
    // Priorizar por tipo de gráfica
    const importanceOrder = { large: 0, medium: 1, small: 2 };
    return importanceOrder[a.importance] - importanceOrder[b.importance];
  });
  
  // Asignar clases CSS y posición en la cuadrícula según importancia
  let layout = [];
  
  // Si hay pocas gráficas (1-2), darles más espacio
  if (layoutConfigs.length <= 2) {
    layoutConfigs.forEach((config, i) => {
      layout.push({
        ...config,
        className: 'chart-full',
        gridColumn: 'span 2',
        gridRow: 'span 1'
      });
    });
  }
  // Si hay una cantidad media (3-5), algunas pueden ser más grandes
  else if (layoutConfigs.length <= 5) {
    layoutConfigs.forEach((config, i) => {
      if (i === 0 && config.importance === 'large') {
        // La primera gráfica importante ocupa todo el ancho
        layout.push({
          ...config,
          className: 'chart-wide',
          gridColumn: 'span 2',
          gridRow: 'span 1'
        });
      } else {
        // Las demás gráficas ocupan la mitad del ancho
        layout.push({
          ...config,
          className: config.importance === 'small' ? 'chart-small' : 'chart-medium',
          gridColumn: 'span 1',
          gridRow: 'span 1'
        });
      }
    });
  }
  // Para muchas gráficas, optimizar el espacio
  else {
    layoutConfigs.forEach((config, i) => {
      if (i === 0 && config.importance === 'large') {
        // Solo la primera gráfica importante podría ser un poco más grande
        layout.push({
          ...config,
          className: 'chart-medium-wide',
          gridColumn: 'span 2',
          gridRow: 'span 1'
        });
      } else {
        // El resto con tamaño estándar
        layout.push({
          ...config,
          className: 'chart-standard',
          gridColumn: 'span 1',
          gridRow: 'span 1'
        });
      }
    });
  }
  
  // Restaurar el orden original de índices
  layout.sort((a, b) => a.originalIndex - b.originalIndex);
  
  return layout;
};

// Observar cambios en los datos y en la capa seleccionada
watch([() => props.data, () => props.layer.name], async () => {
  console.log('Datos o capa actualizados, regenerando gráficas específicas para:', props.layer.name);
  
  // Regenerar un nuevo ID de instancia para evitar conflictos
  instanceId.value = `chart-instance-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
  
  // Importante: destruir gráficas existentes antes de procesar nuevos datos
  destroyCharts();
  
  // Procesar datos y renderizar gráficas
  processData();
  await nextTick();
  renderCharts();
}, { deep: true });

onMounted(async () => {
  processData();
  await nextTick();
  renderCharts();
});

onBeforeUnmount(() => {
  destroyCharts();
});
</script>

<template>
  <div>
    <!-- Mensaje de error -->
    <div v-if="error" class="col-span-full bg-red-50 p-4 rounded-xl border border-red-200 text-red-700 flex items-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      {{ error }}
    </div>

    <!-- Mostrar mensaje si no hay gráficas -->
    <div v-if="chartConfigs.length === 0 && !error" class="col-span-full text-center py-8">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <p class="text-gray-500">Analizando datos de "{{ layer.title || layer.name }}" para generar gráficas específicas...</p>
    </div>
    
    <!-- Contenedor para gráficas que se llenará dinámicamente, con nuevo sistema de grid -->
    <div id="charts-container" class="charts-grid"></div>
    
    <!-- Elemento invisible para crear espacio adicional al final -->
    <div class="invisible py-6 w-full" aria-hidden="true"></div>
  </div>
</template>

<style scoped>
/* Estilos para las tarjetas de gráficas */
.chart-card {
  background-color: white;
  border-radius: 0.75rem;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-bottom: 1rem;
  animation: fadeUp 0.5s ease-out forwards;
}

/* Animación de entrada para las tarjetas */
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chart-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

/* Contenedor de gráficas con sistema de grid mejorado */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  width: 100%;
}

/* Tamaño de contenedor de gráfico ajustado */
.chart-container {
  position: relative;
  height: 200px;
  width: 100%;
  margin-top: 0.5rem;
}

/* Contenedor del título con mejor alineación */
.chart-title-container {
  width: 100%;
  text-align: center;
  padding: 0.25rem 0.5rem;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 0.5rem;
}

/* Estilo mejorado para el título de la gráfica */
.chart-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: #4b5563;
  margin: 0;
  padding: 0.25rem 0;
  text-align: center;
  font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
  letter-spacing: -0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  position: relative;
  transition: color 0.3s ease;
}

/* Efecto hover en el título */
.chart-card:hover .chart-title {
  color: #3b82f6;
}

/* Asegurar que el canvas ocupe todo el espacio disponible */
canvas {
  width: 100% !important;
  height: 100% !important;
  border-radius: 0.25rem;
}

/* Ajustes responsivos */
@media (max-width: 640px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 220px; /* Un poco más alto en móviles para mejor visualización */
  }
  
  .chart-title {
    font-size: 0.9rem; /* Ligeramente más grande en móviles */
  }
}

@media (min-width: 641px) and (max-width: 1023px) {
  .charts-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .charts-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1536px) {
  .charts-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Efecto de animación escalonada para las tarjetas */
.chart-card:nth-child(1) { animation-delay: 0.1s; }
.chart-card:nth-child(2) { animation-delay: 0.2s; }
.chart-card:nth-child(3) { animation-delay: 0.3s; }
.chart-card:nth-child(4) { animation-delay: 0.4s; }
.chart-card:nth-child(5) { animation-delay: 0.5s; }
.chart-card:nth-child(6) { animation-delay: 0.6s; }
.chart-card:nth-child(n+7) { animation-delay: 0.7s; }
</style>
