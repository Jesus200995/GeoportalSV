<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
/* Importar estilos CSS de Leaflet */
@import 'leaflet/dist/leaflet.css';

/* Resetear estilos para ocupar toda la pantalla */
body, html {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  position: relative;
  margin: 0;
  padding: 0;
}
</style>
