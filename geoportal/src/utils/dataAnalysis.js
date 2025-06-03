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

  // Analizar cada columna para determinar qué tipo de gráfica es apropiada
  columns.forEach(column => {
    // Ignorar columnas con nombres técnicos o geometrías
    if (column.toLowerCase().includes('geom') || 
        column.toLowerCase().includes('id') ||
        column.toLowerCase().includes('_uid') ||
        column.toLowerCase().includes('shape') ||
        column.toLowerCase() === 'fid') {
      return;
    }
    
    // Obtener valores únicos y contar su frecuencia
    const values = data.map(item => item[column]);
    const uniqueValues = [...new Set(values.filter(v => v !== null && v !== undefined))];
    
    // Si hay demasiados valores únicos (más de 15), es probable que sea numérico
    // y debemos agrupar los valores para hacer un histograma
    if (uniqueValues.length > 15 && uniqueValues.every(val => !isNaN(parseFloat(val)))) {
      // Es numérico, crear histograma
      const numericValues = values.filter(v => v !== null && v !== undefined).map(v => parseFloat(v));
      
      // Determinar rango y número de bins para el histograma
      const min = Math.min(...numericValues);
      const max = Math.max(...numericValues);
      const range = max - min;
      const binCount = Math.min(10, Math.ceil(Math.sqrt(numericValues.length)));
      const binSize = range / binCount;
      
      // Crear bins y contar valores en cada uno
      const bins = Array(binCount).fill(0);
      const binLabels = Array(binCount).fill('');
      
      numericValues.forEach(val => {
        const binIndex = Math.min(Math.floor((val - min) / binSize), binCount - 1);
        bins[binIndex]++;
      });
      
      // Crear etiquetas para los bins
      for (let i = 0; i < binCount; i++) {
        const lowerBound = min + (i * binSize);
        const upperBound = lowerBound + binSize;
        binLabels[i] = `${lowerBound.toFixed(1)} - ${upperBound.toFixed(1)}`;
      }
      
      // Configuración de la gráfica de histograma
      configs.push({
        type: 'bar',
        title: `Distribución de ${formatColumnName(column)}`,
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
      
      // Si hay suficientes datos, también crear gráfico de box plot
      if (numericValues.length >= 5) {
        configs.push({
          type: 'boxplot',
          title: `Estadísticas de ${formatColumnName(column)}`,
          data: {
            labels: [formatColumnName(column)],
            datasets: [{
              label: 'Valores',
              data: [calculateBoxPlotData(numericValues)],
              backgroundColor: 'rgba(54, 162, 235, 0.5)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
            }]
          }
        });
      }
    } 
    // Si hay pocos valores únicos, crear gráfica de barras o pie
    else if (uniqueValues.length > 0 && uniqueValues.length <= 15) {
      // Es categórico, crear conteo
      const valueCounts = {};
      values.forEach(val => {
        if (val === null || val === undefined) return;
        valueCounts[val] = (valueCounts[val] || 0) + 1;
      });
      
      const sortedValues = Object.keys(valueCounts).sort((a, b) => valueCounts[b] - valueCounts[a]);
      const colors = generateColors(sortedValues.length);
      
      // Decidir entre gráfica de pastel o barras según el número de valores
      if (sortedValues.length <= 6) {
        // Gráfica de pastel para pocos valores
        configs.push({
          type: 'pie',
          title: `Distribución de ${formatColumnName(column)}`,
          data: {
            labels: sortedValues,
            datasets: [{
              data: sortedValues.map(val => valueCounts[val]),
              backgroundColor: colors,
              borderColor: colors.map(color => color.replace('0.7', '1')),
              borderWidth: 1
            }]
          }
        });
      } else {
        // Gráfica de barras para más valores
        configs.push({
          type: 'bar',
          title: `Distribución de ${formatColumnName(column)}`,
          data: {
            labels: sortedValues,
            datasets: [{
              label: formatColumnName(column),
              data: sortedValues.map(val => valueCounts[val]),
              backgroundColor: colors,
              borderColor: colors.map(color => color.replace('0.7', '1')),
              borderWidth: 1
            }]
          }
        });
      }
    }
  });
  
  // Buscar relaciones entre columnas numéricas
  const numericColumns = columns.filter(column => {
    const values = data.map(item => item[column]);
    return values.some(val => val !== null && val !== undefined && !isNaN(parseFloat(val)));
  });
  
  // Crear gráficas de correlación para pares de columnas numéricas
  // Limitamos a 2 pares para no generar demasiadas gráficas
  if (numericColumns.length >= 2) {
    const pairs = [];
    for (let i = 0; i < numericColumns.length - 1 && pairs.length < 2; i++) {
      for (let j = i + 1; j < numericColumns.length && pairs.length < 2; j++) {
        pairs.push([numericColumns[i], numericColumns[j]]);
      }
    }
    
    pairs.forEach(([colX, colY]) => {
      // Filtrar datos donde ambas columnas tienen valores válidos
      const validData = data.filter(item => 
        item[colX] !== null && item[colX] !== undefined && !isNaN(parseFloat(item[colX])) &&
        item[colY] !== null && item[colY] !== undefined && !isNaN(parseFloat(item[colY]))
      );
      
      if (validData.length >= 5) {
        configs.push({
          type: 'scatter',
          title: `Relación entre ${formatColumnName(colX)} y ${formatColumnName(colY)}`,
          data: {
            datasets: [{
              label: 'Datos',
              data: validData.map(item => ({
                x: parseFloat(item[colX]),
                y: parseFloat(item[colY])
              })),
              backgroundColor: 'rgba(54, 162, 235, 0.7)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1,
              pointRadius: 4
            }]
          }
        });
      }
    });
  }
  
  return configs;
};

// Función para formatear nombres de columnas (snake_case a Title Case)
const formatColumnName = (name) => {
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Función para calcular datos de box plot
const calculateBoxPlotData = (values) => {
  // Ordenar valores
  const sortedValues = [...values].sort((a, b) => a - b);
  const n = sortedValues.length;
  
  // Calcular cuartiles
  const q1Index = Math.floor(n * 0.25);
  const q2Index = Math.floor(n * 0.5);
  const q3Index = Math.floor(n * 0.75);
  
  const q1 = sortedValues[q1Index];
  const q2 = sortedValues[q2Index];
  const q3 = sortedValues[q3Index];
  
  // Calcular rango intercuartílico (IQR)
  const iqr = q3 - q1;
  
  // Definir límites para outliers
  const lowerBound = q1 - 1.5 * iqr;
  const upperBound = q3 + 1.5 * iqr;
  
  // Encontrar min/max sin outliers
  let min = sortedValues[0];
  let max = sortedValues[n - 1];
  
  for (let i = 0; i < n; i++) {
    if (sortedValues[i] >= lowerBound) {
      min = sortedValues[i];
      break;
    }
  }
  
  for (let i = n - 1; i >= 0; i--) {
    if (sortedValues[i] <= upperBound) {
      max = sortedValues[i];
      break;
    }
  }
  
  return {
    min,
    q1,
    median: q2,
    q3,
    max
  };
};
