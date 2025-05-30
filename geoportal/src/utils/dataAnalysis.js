/**
 * Función para determinar el tipo de dato de una columna
 * @param {Array} values - Valores de una columna
 * @returns {string} - Tipo de dato (numeric, date, categorical)
 */
const getColumnType = (values) => {
  // Filtrar valores nulos o indefinidos
  const validValues = values.filter(v => v !== null && v !== undefined);
  if (validValues.length === 0) return 'unknown';
  
  const sample = validValues[0];
  
  // Verificar tipo numérico
  if (typeof sample === 'number' || (typeof sample === 'string' && !isNaN(parseFloat(sample)))) {
    return 'numeric';
  }
  
  // Verificar tipo fecha
  if (typeof sample === 'string') {
    // Intentar parsear como fecha
    try {
      const date = new Date(sample);
      if (!isNaN(date.getTime()) && sample.match(/^\d{4}-\d{2}-\d{2}/)) {
        return 'date';
      }
    } catch (e) {
      // No es una fecha válida
    }
  }
  
  // Por defecto, considerar categórico
  return 'categorical';
};

/**
 * Función para analizar datos y generar configuraciones de gráficas
 * @param {Array} data - Datos a analizar
 * @returns {Array} - Configuraciones de gráficas
 */
export const analyzeData = (data) => {
  if (!data || data.length === 0) {
    console.warn('No hay datos para analizar');
    return [];
  }

  console.log('Analizando datos:', data.length, 'registros');
  const columns = Object.keys(data[0]);
  const configs = [];

  // Generar colores para las gráficas
  const generateColors = (count) => {
    const baseColors = [
      'rgba(255, 99, 132, 0.7)',   // Rojo
      'rgba(54, 162, 235, 0.7)',   // Azul
      'rgba(255, 206, 86, 0.7)',   // Amarillo
      'rgba(75, 192, 192, 0.7)',   // Verde azulado
      'rgba(153, 102, 255, 0.7)',  // Púrpura
      'rgba(255, 159, 64, 0.7)',   // Naranja
      'rgba(199, 199, 199, 0.7)',  // Gris
      'rgba(83, 102, 255, 0.7)',   // Azul-violeta
      'rgba(255, 99, 255, 0.7)',   // Rosa
      'rgba(0, 162, 150, 0.7)',    // Verde-azul
    ];
    
    const colors = [];
    for (let i = 0; i < count; i++) {
      colors.push(baseColors[i % baseColors.length]);
    }
    return colors;
  };

  // Analizar cada columna
  columns.forEach(column => {
    try {
      const values = data.map(row => row[column]);
      const type = getColumnType(values);
      console.log(`Columna "${column}" detectada como: ${type}`);

      if (type === 'numeric') {
        // 1. Gráfica de barras para datos numéricos
        const validValues = values.filter(v => v !== null && v !== undefined)
                                 .map(v => typeof v === 'string' ? parseFloat(v) : v);
        
        if (validValues.length === 0) return;
        
        const min = Math.min(...validValues);
        const max = Math.max(...validValues);
        const avg = validValues.reduce((a, b) => a + b, 0) / validValues.length;
        
        configs.push({
          type: 'bar',
          title: `Estadísticas de ${column}`,
          data: {
            labels: ['Mínimo', 'Promedio', 'Máximo'],
            datasets: [{
              label: column,
              data: [min, avg, max],
              backgroundColor: ['rgba(255, 99, 132, 0.7)', 'rgba(54, 162, 235, 0.7)', 'rgba(75, 192, 192, 0.7)']
            }]
          }
        });
        
        // 2. Histograma de distribución
        // Dividir en intervalos
        const range = max - min;
        const binCount = Math.min(10, Math.ceil(Math.sqrt(data.length)));
        const binSize = range / binCount;
        const bins = Array(binCount).fill(0);
        
        validValues.forEach(val => {
          const binIndex = Math.min(binCount - 1, Math.floor((val - min) / binSize));
          bins[binIndex]++;
        });
        
        const binLabels = Array(binCount).fill(0).map((_, i) => {
          const binMin = min + i * binSize;
          const binMax = binMin + binSize;
          return `${binMin.toFixed(1)} - ${binMax.toFixed(1)}`;
        });
        
        configs.push({
          type: 'bar',
          title: `Distribución de ${column}`,
          data: {
            labels: binLabels,
            datasets: [{
              label: 'Frecuencia',
              data: bins,
              backgroundColor: 'rgba(54, 162, 235, 0.7)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
            }]
          }
        });
        
      } else if (type === 'categorical') {
        // Gráfica de pastel para datos categóricos
        const categories = {};
        values.forEach(value => {
          if (value === null || value === undefined) return;
          categories[value] = (categories[value] || 0) + 1;
        });

        const categoryLabels = Object.keys(categories);
        const categoryValues = Object.values(categories);
        
        if (categoryLabels.length > 0) {
          configs.push({
            type: 'pie',
            title: `Distribución de ${column}`,
            data: {
              labels: categoryLabels,
              datasets: [{
                data: categoryValues,
                backgroundColor: generateColors(categoryLabels.length),
                borderWidth: 1
              }]
            }
          });
          
          // También añadir gráfica de barras para categorías
          configs.push({
            type: 'bar',
            title: `Frecuencia de ${column}`,
            data: {
              labels: categoryLabels,
              datasets: [{
                label: 'Cantidad',
                data: categoryValues,
                backgroundColor: generateColors(categoryLabels.length),
                borderWidth: 1
              }]
            }
          });
        }
      } else if (type === 'date') {
        // Análisis temporal básico
        const validDates = values
          .filter(v => v !== null && v !== undefined)
          .map(dateStr => new Date(dateStr))
          .filter(date => !isNaN(date.getTime()));
          
        if (validDates.length === 0) return;
        
        // Ordenar fechas
        validDates.sort((a, b) => a - b);
        
        // Agrupar por mes/año para simplificar
        const dateGroups = {};
        validDates.forEach(date => {
          const key = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
          dateGroups[key] = (dateGroups[key] || 0) + 1;
        });
        
        const dateLabels = Object.keys(dateGroups).sort();
        const dateCounts = dateLabels.map(label => dateGroups[label]);
        
        configs.push({
          type: 'line',
          title: `Tendencia temporal de ${column}`,
          data: {
            labels: dateLabels,
            datasets: [{
              label: 'Cantidad',
              data: dateCounts,
              fill: false,
              borderColor: 'rgba(75, 192, 192, 1)',
              tension: 0.4
            }]
          }
        });
      }
    } catch (err) {
      console.error(`Error al analizar columna ${column}:`, err);
    }
  });

  return configs;
};
