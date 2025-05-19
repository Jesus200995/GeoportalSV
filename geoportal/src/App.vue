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
  width: 100%;
  overflow-x: hidden;
  position: relative;
  margin: 0;
  padding: 0;
}

/* Eliminar grid en App.vue para permitir que el contenido ocupe todo el ancho */
@media (min-width: 1024px) {
  #app {
    display: block;
    padding: 0;
    width: 100vw;
    max-width: 100%;
  }
}

/* Asegurar que RouterView ocupe todo el ancho disponible */
#app > * {
  width: 100%;
  max-width: 100vw;
}
</style>
