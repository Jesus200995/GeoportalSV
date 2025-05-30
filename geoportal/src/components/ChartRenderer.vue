<script setup>
import { ref, onMounted, watch, onBeforeUnmount, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';
import { analyzeData } from '../utils/dataAnalysis';

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
  }
});

const charts = ref([]);
const chartConfigs = ref([]);
const error = ref(null);

// Analizar datos y crear configuraciones de gráficas
const processData = () => {
  try {
    error.value = null;
    
    if (!props.data || !Array.isArray(props.data) || props.data.length === 0) {
      error.value = 'No hay datos disponibles para generar gráficas';
      return;
    }
    
    console.log(`Procesando datos para ${props.layer.name || 'capa'}`);
    const analysis = analyzeData(props.data);
    
    if (!analysis || analysis.length === 0) {
      error.value = 'No se pudieron generar gráficas con los datos disponibles';
      return;
    }
    
    chartConfigs.value = analysis.map(config => ({
      ...config,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              font: {
                size: 12
              }
            }
          },
          title: {
            display: true,
            text: config.title,
            font: {
              size: 16,
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
    }));
    
    console.log(`Se generaron ${chartConfigs.value.length} configuraciones de gráficas`);
  } catch (err) {
    console.error('Error al procesar datos:', err);
    error.value = 'Error al procesar los datos para las gráficas';
  }
};

// Renderizar gráficas con pequeño retraso para asegurar que el DOM esté listo
const renderCharts = () => {
  // Limpiar gráficas existentes
  destroyCharts();
  
  // Crear nuevas gráficas con un pequeño retraso
  setTimeout(() => {
    try {
      chartConfigs.value.forEach((config, index) => {
        const canvas = document.getElementById(`chart-${index}`);
        if (!canvas) {
          console.warn(`Canvas #chart-${index} no encontrado`);
          return;
        }
        
        console.log(`Renderizando gráfica #${index} (${config.type})...`);
        const chart = new Chart(canvas, {
          type: config.type,
          data: config.data,
          options: config.options
        });
        
        charts.value.push(chart);
      });
      console.log(`${charts.value.length} gráficas renderizadas`);
    } catch (err) {
      console.error('Error al renderizar gráficas:', err);
      error.value = 'Error al crear las gráficas';
    }
  }, 100);
};

// Limpiar gráficas
const destroyCharts = () => {
  charts.value.forEach(chart => {
    try {
      chart.destroy();
    } catch (err) {
      console.error('Error al destruir gráfica:', err);
    }
  });
  charts.value = [];
};

// Observar cambios en los datos
watch(() => props.data, (newData) => {
  console.log('Datos actualizados:', newData?.length || 0, 'registros');
  processData();
  nextTick(() => renderCharts());
}, { deep: true });

onMounted(() => {
  processData();
  renderCharts();
});

onBeforeUnmount(() => {
  destroyCharts();
});
</script>

<template>
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
    <p class="text-gray-500">Analizando datos para generar gráficas...</p>
  </div>
  
  <!-- Contenedores para cada gráfica -->
  <template v-for="(config, index) in chartConfigs" :key="`chart-container-${index}`">
    <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all duration-300 flex flex-col">
      <div class="h-[300px] relative">
        <canvas :id="`chart-${index}`"></canvas>
      </div>
      <p class="text-xs text-gray-500 mt-3 text-center">
        {{ config.title }}
      </p>
    </div>
  </template>
</template>

<style scoped>
/* Estilos para las tarjetas de gráficas */
.bg-white {
  position: relative;
  overflow: hidden;
}

.bg-white:hover {
  transform: translateY(-2px);
}

/* Asegurar que el canvas ocupe todo el espacio disponible */
canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>
