<script setup>
const props = defineProps({
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'success' // success, error, warning, info
  },
  show: {
    type: Boolean,
    required: true
  }
});

const getIcon = (type) => {
  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️'
  };
  return icons[type] || icons.info;
};
</script>

<template>
  <Transition name="toast">
    <div v-if="show" 
         :class="[
           'fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50 flex items-center space-x-2',
           {
             'bg-green-500 text-white': type === 'success',
             'bg-red-500 text-white': type === 'error',
             'bg-yellow-500 text-white': type === 'warning',
             'bg-blue-500 text-white': type === 'info'
           }
         ]">
      <span class="text-xl">{{ getIcon(type) }}</span>
      <p class="font-medium">{{ message }}</p>
    </div>
  </Transition>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(30px);
}
</style>
