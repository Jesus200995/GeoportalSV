<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { Chart, registerables } from 'chart.js';
import UserProfile from './UserProfile.vue';

// Registrar todos los componentes de Chart.js
Chart.register(...registerables);

// Props y emisiones
const emit = defineEmits(['show-welcome']);

// Estado reactivo
const loading = ref(true);
const selectedPeriod = ref('anual');
const selectedCultivo = ref('todos');
const selectedRegion = ref('todas');

// Referencias a los gráficos
const barChartRef = ref(null);
const pieChartRef = ref(null);
const lineChartRef = ref(null);
const radarChartRef = ref(null);
const barChart = ref(null);
const pieChart = ref(null);
const lineChart = ref(null);
const radarChart = ref(null);

// Datos de ejemplo
const datosProductividad = {
  anual: {
    labels: ['2018', '2019', '2020', '2021', '2022', '2023'],
    datasets: [
      {
        label: 'Producción (Toneladas)',
        data: [12500, 19000, 16200, 25100, 23400, 28700],
        backgroundColor: 'rgba(16, 185, 129, 0.6)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 1
      }
    ]
  },
  mensual: {
    labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
    datasets: [
      {
        label: 'Producción (Toneladas)',
        data: [1200, 1900, 2500, 2100, 2400, 2700, 3100, 3400, 2900, 2500, 2000, 1800],
        backgroundColor: 'rgba(16, 185, 129, 0.6)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 1
      }
    ]
  }
};

const datosCultivos = {
  todos: {
    labels: ['Maíz', 'Frijol', 'Caña de Azúcar', 'Café', 'Hortalizas', 'Otros'],
    datasets: [
      {
        label: 'Distribución de Cultivos',
        data: [35, 20, 15, 10, 12, 8],
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
          'rgba(255, 159, 64, 0.6)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)'
        ],
        borderWidth: 1
      }
    ]
  }
};

const datosRendimiento = {
  anual: {
    labels: ['2018', '2019', '2020', '2021', '2022', '2023'],
    datasets: [
      {
        label: 'Rendimiento (Ton/Ha)',
        data: [3.2, 3.5, 3.4, 3.8, 4.1, 4.3],
        fill: false,
        borderColor: 'rgba(59, 130, 246, 1)',
        tension: 0.4,
        pointBackgroundColor: 'rgba(59, 130, 246, 1)',
        pointRadius: 4
      }
    ]
  }
};

const datosFactores = {
  todos: {
    labels: ['Agua', 'Fertilizante', 'Tecnología', 'Mano de Obra', 'Gestión', 'Clima'],
    datasets: [
      {
        label: 'Factores Actuales',
        data: [65, 59, 80, 81, 56, 55],
        fill: true,
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
      },
      {
        label: 'Factores Óptimos',
        data: [70, 65, 85, 80, 70, 75],
        fill: true,
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
        borderColor: 'rgba(16, 185, 129, 1)',
        pointBackgroundColor: 'rgba(16, 185, 129, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(16, 185, 129, 1)'
      }
    ]
  }
};

// Inicializar gráficos
const initCharts = () => {
  // Gráfico de barras
  if (barChartRef.value) {
    barChart.value = new Chart(barChartRef.value, {
      type: 'bar',
      data: datosProductividad[selectedPeriod.value],
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: 'Producción Agrícola por Periodo',
            font: {
              size: 16
            }
          }
        }
      }
    });
  }

  // Gráfico de pastel
  if (pieChartRef.value) {
    pieChart.value = new Chart(pieChartRef.value, {
      type: 'pie',
      data: datosCultivos[selectedCultivo.value],
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right'
          },
          title: {
            display: true,
            text: 'Distribución de Cultivos',
            font: {
              size: 16
            }
          }
        }
      }
    });
  }

  // Gráfico de líneas
  if (lineChartRef.value) {
    lineChart.value = new Chart(lineChartRef.value, {
      type: 'line',
      data: datosRendimiento[selectedPeriod.value],
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: 'Rendimiento por Hectárea',
            font: {
              size: 16
            }
          }
        }
      }
    });
  }

  // Gráfico de radar
  if (radarChartRef.value) {
    radarChart.value = new Chart(radarChartRef.value, {
      type: 'radar',
      data: datosFactores[selectedRegion.value],
      options: {
        responsive: true,
        maintainAspectRatio: false,
        elements: {
          line: {
            borderWidth: 3
          }
        },
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: 'Factores de Producción',
            font: {
              size: 16
            }
          }
        }
      }
    });
  }
};

// Actualizar gráficos cuando cambian los filtros
const updateCharts = () => {
  if (barChart.value) {
    barChart.value.data = datosProductividad[selectedPeriod.value];
    barChart.value.update();
  }
  
  if (lineChart.value) {
    lineChart.value.data = datosRendimiento[selectedPeriod.value];
    lineChart.value.update();
  }
};

// Función para volver a la página de inicio
const goHome = () => {
  emit('show-welcome');
};

// Lifecycle hooks
onMounted(() => {
  // Simular tiempo de carga
  setTimeout(() => {
    loading.value = false;
    // Inicializar gráficos después de un pequeño retraso para asegurar que el DOM esté listo
    setTimeout(() => {
      initCharts();
    }, 100);
  }, 1500);
  
  // Añadir animación de entrada
  document.body.classList.add('dashboard-enter-animation');
  setTimeout(() => {
    document.body.classList.remove('dashboard-enter-animation');
  }, 1000);
});

onBeforeUnmount(() => {
  // Limpiar los gráficos para evitar memory leaks
  if (barChart.value) barChart.value.destroy();
  if (pieChart.value) pieChart.value.destroy();
  if (lineChart.value) lineChart.value.destroy();
  if (radarChart.value) radarChart.value.destroy();
});
</script>

<template>
  <div class="min-h-screen bg-gray-50 overflow-hidden flex flex-col">
    <!-- Overlay de carga con animación -->
    <div v-if="loading" 
         class="fixed inset-0 bg-white bg-opacity-90 z-50 flex flex-col items-center justify-center transition-opacity duration-500"
         :class="loading ? 'opacity-100' : 'opacity-0 pointer-events-none'">
      <div class="w-16 h-16 border-4 border-t-blue-500 border-blue-200 rounded-full animate-spin mb-4"></div>
      <p class="text-blue-700 font-medium">Cargando datos estadísticos...</p>
    </div>

    <!-- Encabezado -->
    <header class="bg-white shadow-md z-10">
      <div class="container mx-auto px-4 py-3 sm:py-4 flex justify-between items-center">
        <!-- Logo y título -->
        <div class="flex items-center space-x-3">
          <img src="@/components/images/logotipo.png" alt="Logotipo Sembrando Datos" class="h-10 sm:h-12 w-auto object-contain" />
          <h1 class="text-xl sm:text-2xl md:text-3xl font-serif font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-500">
            Análisis y Estadísticas
          </h1>
        </div>

        <!-- Botones de acción -->
        <div class="flex items-center space-x-2 sm:space-x-4">
          <!-- Componente de perfil de usuario -->
          <UserProfile />
          
          <!-- Botón de inicio -->
          <button 
            @click="goHome"
            class="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-lg transition-all duration-300 flex items-center space-x-2 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transform hover:-translate-y-0.5 active:translate-y-0"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7m-7-7v14" />
            </svg>
            <span class="hidden sm:inline">Inicio</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Filtros -->
    <div class="bg-white border-b border-gray-200 shadow-sm">
      <div class="container mx-auto px-4 py-3">
        <div class="flex flex-wrap items-center gap-4">
          <div class="flex items-center space-x-2">
            <label for="periodo" class="text-sm font-medium text-gray-700">Periodo:</label>
            <select 
              id="periodo" 
              v-model="selectedPeriod" 
              @change="updateCharts"
              class="px-3 py-1.5 text-sm bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="anual">Anual</option>
              <option value="mensual">Mensual</option>
            </select>
          </div>
          
          <div class="flex items-center space-x-2">
            <label for="cultivo" class="text-sm font-medium text-gray-700">Cultivo:</label>
            <select 
              id="cultivo" 
              v-model="selectedCultivo"
              class="px-3 py-1.5 text-sm bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="todos">Todos los cultivos</option>
              <option value="maiz">Maíz</option>
              <option value="frijol">Frijol</option>
              <option value="cafe">Café</option>
            </select>
          </div>
          
          <div class="flex items-center space-x-2">
            <label for="region" class="text-sm font-medium text-gray-700">Región:</label>
            <select 
              id="region" 
              v-model="selectedRegion"
              class="px-3 py-1.5 text-sm bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="todas">Todas las regiones</option>
              <option value="norte">Norte</option>
              <option value="centro">Centro</option>
              <option value="sur">Sur</option>
            </select>
          </div>
          
          <button 
            class="ml-auto px-4 py-1.5 bg-blue-600 text-white rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 flex items-center space-x-1"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            <span>Exportar</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Contenido principal -->
    <main class="flex-1 overflow-auto py-6 px-4">
      <div class="container mx-auto">
        <!-- Tarjetas de indicadores -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <div class="flex items-center">
              <div class="flex-shrink-0 p-3 bg-blue-100 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div class="ml-4">
                <h2 class="text-gray-600 text-sm">Producción Total</h2>
                <p class="text-2xl font-semibold text-gray-800">28,700 Ton</p>
                <p class="text-green-500 text-xs flex items-center mt-1">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
                  </svg>
                  22.6% vs 2022
                </p>
              </div>
            </div>
          </div>
          
          <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <div class="flex items-center">
              <div class="flex-shrink-0 p-3 bg-green-100 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="ml-4">
                <h2 class="text-gray-600 text-sm">Valor Estimado</h2>
                <p class="text-2xl font-semibold text-gray-800">$12.5M</p>
                <p class="text-green-500 text-xs flex items-center mt-1">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
                  </svg>
                  15.3% vs 2022
                </p>
              </div>
            </div>
          </div>
          
          <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <div class="flex items-center">
              <div class="flex-shrink-0 p-3 bg-amber-100 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div class="ml-4">
                <h2 class="text-gray-600 text-sm">Rendimiento</h2>
                <p class="text-2xl font-semibold text-gray-800">4.3 Ton/Ha</p>
                <p class="text-green-500 text-xs flex items-center mt-1">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
                  </svg>
                  4.9% vs 2022
                </p>
              </div>
            </div>
          </div>
          
          <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
            <div class="flex items-center">
              <div class="flex-shrink-0 p-3 bg-rose-100 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div class="ml-4">
                <h2 class="text-gray-600 text-sm">Área Cultivada</h2>
                <p class="text-2xl font-semibold text-gray-800">6,674 Ha</p>
                <p class="text-green-500 text-xs flex items-center mt-1">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
                  </svg>
                  2.3% vs 2022
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Gráficos -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <!-- Gráfico de barras: Producción -->
          <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
            <div class="h-80">
              <canvas ref="barChartRef"></canvas>
            </div>
          </div>
          
          <!-- Gráfico de pastel: Distribución de cultivos -->
          <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
            <div class="h-80">
              <canvas ref="pieChartRef"></canvas>
            </div>
          </div>
          
          <!-- Gráfico de líneas: Rendimiento -->
          <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
            <div class="h-80">
              <canvas ref="lineChartRef"></canvas>
            </div>
          </div>
          
          <!-- Gráfico de radar: Factores de producción -->
          <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
            <div class="h-80">
              <canvas ref="radarChartRef"></canvas>
            </div>
          </div>
        </div>
        
        <!-- Tabla de datos -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100">
            <h3 class="text-lg font-medium text-gray-800">Datos de Producción por Cultivo</h3>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cultivo
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Área (Ha)
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Producción (Ton)
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rendimiento (Ton/Ha)
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Valor Estimado ($)
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">Maíz</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">2,335</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">10,045</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">4.3</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">$4,375,642</td>
                </tr>
                <tr>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">Frijol</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">1,334</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">5,740</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">4.3</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">$3,502,140</td>
                </tr>
                <tr>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">Caña de Azúcar</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">1,005</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">4,305</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">4.3</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">$1,875,420</td>
                </tr>
                <tr>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">Café</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">667</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">2,870</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">4.3</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">$1,246,720</td>
                </tr>
                <tr>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">Hortalizas</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">800</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">3,444</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">4.3</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">$1,500,078</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>

    <!-- Pie de página -->
    <footer class="bg-white border-t border-gray-200 py-4">
      <div class="container mx-auto px-4 text-center text-sm text-gray-500">
        <p>© 2023 Geoportal Sembrando Datos. Todos los derechos reservados.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Animación para la entrada del dashboard */
.dashboard-enter-animation {
  animation: fadeIn 1s ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Scrollbar personalizado */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: #3b82f6;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #2563eb;
}

/* Animaciones para las tarjetas */
.grid > div {
  animation: cardSlideIn 0.5s ease-out forwards;
  opacity: 0;
}

.grid > div:nth-child(1) { animation-delay: 0.1s; }
.grid > div:nth-child(2) { animation-delay: 0.2s; }
.grid > div:nth-child(3) { animation-delay: 0.3s; }
.grid > div:nth-child(4) { animation-delay: 0.4s; }

@keyframes cardSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Transiciones generales */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
