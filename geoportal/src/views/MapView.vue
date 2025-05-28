<script setup>
import Dashboard from '../components/Dashboard.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Función para manejar el evento show-welcome
const handleShowWelcome = () => {
  router.push('/');
}
</script>

<template>
  <Dashboard @show-welcome="handleShowWelcome" />
</template>
