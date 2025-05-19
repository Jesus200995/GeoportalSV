<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const loadingProgress = ref(0);
const isAnimationComplete = ref(false);

onMounted(() => {
  // Simular progreso de carga gradual
  const interval = setInterval(() => {
    loadingProgress.value += 2;
    if (loadingProgress.value >= 100) {
      clearInterval(interval);
      // Añadir pequeño retraso después del 100% para mostrar la animación completa
      setTimeout(() => {
        isAnimationComplete.value = true;
        // Navegar a la página principal después de completar la animación
        setTimeout(() => {
          router.push('/');
        }, 1000);
      }, 500);
    }
  }, 50);
});
</script>

<template>
  <div class="loading-screen">
    <!-- Fondo con gradiente -->
    <div class="background-gradient"></div>
    
    <!-- Animación principal -->
    <div class="plant-container">
      <!-- Planta -->
      <div class="plant" :class="{ 'grown': loadingProgress > 95 }">
        <!-- Tallo -->
        <div class="stem"></div>
        
        <!-- Hojas (aparecen gradualmente) -->
        <div class="leaf leaf-left" :style="{ opacity: loadingProgress > 30 ? 1 : 0 }"></div>
        <div class="leaf leaf-right" :style="{ opacity: loadingProgress > 45 ? 1 : 0 }"></div>
        <div class="leaf leaf-left-top" :style="{ opacity: loadingProgress > 60 ? 1 : 0 }"></div>
        <div class="leaf leaf-right-top" :style="{ opacity: loadingProgress > 75 ? 1 : 0 }"></div>
        
        <!-- Flor (aparece al final) -->
        <div class="flower" :class="{ 'bloom': loadingProgress > 90 }"></div>
      </div>
      
      <!-- Tierra con ondulación -->
      <div class="soil"></div>
      
      <!-- Raíces animadas -->
      <div class="roots">
        <div class="root root-left" :style="{ height: `${loadingProgress * 0.3}px` }"></div>
        <div class="root root-center" :style="{ height: `${loadingProgress * 0.25}px` }"></div>
        <div class="root root-right" :style="{ height: `${loadingProgress * 0.35}px` }"></div>
      </div>
    </div>
    
    <!-- Texto y barra de progreso -->
    <div class="loading-info">
      <h2 class="loading-text">{{ isAnimationComplete ? '¡Bienvenido al Geoportal!' : 'Sembrando Datos...' }}</h2>
      <div class="progress-container">
        <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
      </div>
      <p class="loading-percentage">{{ loadingProgress }}%</p>
    </div>
    
    <!-- Elementos decorativos animados -->
    <div class="floating-elements">
      <div class="floating-leaf" v-for="i in 6" :key="i"></div>
      <div class="floating-particle" v-for="i in 12" :key="i+6"></div>
    </div>
  </div>
</template>

<style scoped>
.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f6fef9;
  z-index: 9999;
  overflow: hidden;
}

.background-gradient {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(240, 253, 244, 1) 0%, rgba(220, 252, 231, 1) 100%);
  z-index: -1;
}

.plant-container {
  position: relative;
  width: 200px;
  height: 300px;
  margin-bottom: 40px;
}

/* Estilo del suelo */
.soil {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 140px;
  height: 40px;
  background: #8B5E3C;
  border-radius: 50%;
  z-index: 1;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  animation: soilPulse 3s infinite alternate;
}

@keyframes soilPulse {
  0% {
    transform: translateX(-50%) scale(1);
  }
  100% {
    transform: translateX(-50%) scale(1.05);
  }
}

.soil::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    rgba(139, 94, 60, 0.8) 0%, 
    rgba(139, 94, 60, 0.5) 50%, 
    rgba(139, 94, 60, 0.8) 100%);
  animation: soilWave 3s infinite alternate;
}

@keyframes soilWave {
  0% {
    transform: translateX(-30px);
  }
  100% {
    transform: translateX(30px);
  }
}

/* Estilo del tallo */
.stem {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  width: 8px;
  height: 0;
  background: linear-gradient(to right, #2E8B57, #3CB371, #2E8B57);
  border-radius: 4px;
  z-index: 2;
  transform-origin: bottom center;
  animation: stemGrow 3s ease-out forwards;
}

@keyframes stemGrow {
  0% {
    height: 0;
  }
  100% {
    height: 180px;
  }
}

/* Estilos de las hojas */
.leaf {
  position: absolute;
  width: 40px;
  height: 20px;
  background: #4CAF50;
  border-radius: 50% 50% 50% 10px;
  z-index: 2;
  transform-origin: bottom right;
  transition: opacity 1s ease;
}

.leaf-left {
  bottom: 120px;
  left: 85px;
  transform: rotate(30deg);
  animation: leafWave 3s ease-in-out infinite alternate;
}

.leaf-right {
  bottom: 100px;
  left: 105px;
  transform: rotate(-30deg) scaleX(-1);
  animation: leafWave 3s ease-in-out infinite alternate-reverse;
}

.leaf-left-top {
  bottom: 160px;
  left: 87px;
  transform: rotate(20deg);
  animation: leafWave 4s ease-in-out infinite alternate 0.5s;
}

.leaf-right-top {
  bottom: 140px;
  left: 107px;
  transform: rotate(-20deg) scaleX(-1);
  animation: leafWave 4s ease-in-out infinite alternate-reverse 0.5s;
}

@keyframes leafWave {
  0% {
    transform: rotate(20deg);
  }
  100% {
    transform: rotate(30deg);
  }
}

/* Estilo de la flor */
.flower {
  position: absolute;
  bottom: 220px;
  left: 50%;
  transform: translateX(-50%) scale(0);
  width: 30px;
  height: 30px;
  background: radial-gradient(circle, #FFEB3B 0%, #FFC107 100%);
  border-radius: 50%;
  z-index: 3;
  box-shadow: 0 0 10px rgba(255, 235, 59, 0.7);
  opacity: 0;
  transition: all 0.5s ease;
}

.flower.bloom {
  transform: translateX(-50%) scale(1);
  opacity: 1;
  animation: flowerBloom 1s ease-out forwards, flowerPulse 2s infinite alternate 1s;
}

@keyframes flowerBloom {
  0% {
    transform: translateX(-50%) scale(0);
    opacity: 0;
  }
  60% {
    transform: translateX(-50%) scale(1.2);
    opacity: 1;
  }
  100% {
    transform: translateX(-50%) scale(1);
    opacity: 1;
  }
}

@keyframes flowerPulse {
  0% {
    box-shadow: 0 0 10px rgba(255, 235, 59, 0.7);
  }
  100% {
    box-shadow: 0 0 20px rgba(255, 235, 59, 0.9);
  }
}

/* Estilos de las raíces */
.roots {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  z-index: 0;
}

.root {
  position: absolute;
  bottom: 0;
  width: 4px;
  background: linear-gradient(to bottom, #8B4513, transparent);
  border-radius: 2px;
}

.root-left {
  left: 10px;
  transform: rotate(15deg);
  height: 0;
  transition: height 4s ease-out;
}

.root-center {
  left: 28px;
  transform: rotate(-5deg);
  height: 0;
  transition: height 4s ease-out;
}

.root-right {
  left: 46px;
  transform: rotate(-20deg);
  height: 0;
  transition: height 4s ease-out;
}

/* Información de carga */
.loading-info {
  text-align: center;
  width: 300px;
  margin-top: 20px;
}

.loading-text {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: #2E8B57;
  animation: fadeInUp 0.5s ease-out;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.progress-container {
  width: 100%;
  height: 10px;
  background-color: #E8F5E9;
  border-radius: 5px;
  overflow: hidden;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  border-radius: 5px;
  transition: width 0.3s ease;
  box-shadow: 0 0 5px rgba(76, 175, 80, 0.5);
}

.loading-percentage {
  font-family: 'Inter', sans-serif;
  font-size: 0.9rem;
  color: #388E3C;
  margin-top: 8px;
}

/* Elementos decorativos flotantes */
.floating-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
}

.floating-leaf {
  position: absolute;
  background-color: rgba(76, 175, 80, 0.7);
  width: 15px;
  height: 15px;
  border-radius: 50% 0;
  animation: float 15s infinite linear;
  opacity: 0.6;
}

.floating-leaf:nth-child(1) { top: 15%; left: 10%; animation-delay: 0s; transform: rotate(45deg); }
.floating-leaf:nth-child(2) { top: 25%; left: 80%; animation-delay: 2s; transform: rotate(20deg); }
.floating-leaf:nth-child(3) { top: 60%; left: 15%; animation-delay: 4s; transform: rotate(70deg); }
.floating-leaf:nth-child(4) { top: 75%; left: 70%; animation-delay: 6s; transform: rotate(120deg); }
.floating-leaf:nth-child(5) { top: 35%; left: 30%; animation-delay: 8s; transform: rotate(190deg); }
.floating-leaf:nth-child(6) { top: 50%; left: 90%; animation-delay: 10s; transform: rotate(230deg); }

.floating-particle {
  position: absolute;
  background-color: rgba(255, 235, 59, 0.5);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  animation: floatParticle 20s infinite linear;
  opacity: 0.7;
}

.floating-particle:nth-child(7) { top: 10%; left: 20%; animation-delay: 0s; }
.floating-particle:nth-child(8) { top: 30%; left: 5%; animation-delay: 1s; }
.floating-particle:nth-child(9) { top: 70%; left: 25%; animation-delay: 2s; }
.floating-particle:nth-child(10) { top: 90%; left: 60%; animation-delay: 3s; }
.floating-particle:nth-child(11) { top: 20%; left: 40%; animation-delay: 4s; }
.floating-particle:nth-child(12) { top: 40%; left: 85%; animation-delay: 5s; }
.floating-particle:nth-child(13) { top: 60%; left: 75%; animation-delay: 6s; }
.floating-particle:nth-child(14) { top: 80%; left: 30%; animation-delay: 7s; }
.floating-particle:nth-child(15) { top: 15%; left: 65%; animation-delay: 8s; }
.floating-particle:nth-child(16) { top: 45%; left: 15%; animation-delay: 9s; }
.floating-particle:nth-child(17) { top: 55%; left: 50%; animation-delay: 10s; }
.floating-particle:nth-child(18) { top: 85%; left: 90%; animation-delay: 11s; }

@keyframes float {
  0% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.6;
  }
  90% {
    opacity: 0.6;
  }
  100% {
    transform: translateY(-100vh) rotate(360deg);
    opacity: 0;
  }
}

@keyframes floatParticle {
  0% {
    transform: translateY(100vh);
    opacity: 0;
  }
  10% {
    opacity: 0.7;
  }
  90% {
    opacity: 0.7;
  }
  100% {
    transform: translateY(-100vh);
    opacity: 0;
  }
}

/* Animaciones adicionales */
@keyframes fadeInUp {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.plant.grown .stem {
  animation: stemShakeSuccess 0.5s ease-in-out;
}

@keyframes stemShakeSuccess {
  0%, 100% { transform: translateX(-50%) rotate(0deg); }
  25% { transform: translateX(-50%) rotate(-3deg); }
  50% { transform: translateX(-50%) rotate(0deg); }
  75% { transform: translateX(-50%) rotate(3deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .plant-container {
    transform: scale(0.8);
  }
  
  .loading-info {
    width: 90%;
    max-width: 300px;
  }
  
  .loading-text {
    font-size: 1.2rem;
  }
}
</style>
