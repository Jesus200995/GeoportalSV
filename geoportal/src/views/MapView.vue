<script setup>
import Dashboard from '../components/Dashboard.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <Dashboard @go-home="router.push('/')" />
</template>
