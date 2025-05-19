import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import MapView from '../views/MapView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { 
        requiresAuth: true 
      }
    },
    {
      path: '/map',
      name: 'map',
      component: MapView,
      meta: { 
        requiresAuth: true 
      }
    }
  ]
})

// Guardia de navegación para proteger rutas
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('authenticated') === 'true';
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Si la ruta requiere autenticación y el usuario no está autenticado
    next('/login');
  } else if (to.path === '/login' && isAuthenticated) {
    // Si el usuario ya está autenticado e intenta acceder a login
    next('/');
  } else {
    // En cualquier otro caso, continuar
    next();
  }
})

export default router
