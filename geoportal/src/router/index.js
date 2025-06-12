import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import LoadingPlant from '../components/animations/LoadingPlant.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/loading',
      name: 'loading',
      component: LoadingPlant,
      meta: { 
        requiresAuth: true 
      }
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
      component: () => import('../views/MapView.vue'),
      meta: { 
        requiresAuth: true 
      }
    },
    {
      path: '/upload-layer',
      name: 'upload-layer',
      component: () => import('../views/UploadLayer.vue'),
      meta: { 
        requiresAuth: true,
        title: 'Subir Capas - Geoportal Sembrando Datos'
      }
    },
    {
      path: '/supervisar',
      name: 'supervisar',
      component: () => import('../views/SupervisarView.vue')
    }
  ]
})

// Guardia de navegación para proteger rutas
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('authenticated') === 'true';
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  } else if (to.path === '/login' && isAuthenticated) {
    next('/');
  } else {
    // Eliminar la redirección forzada a /loading
    next();
  }
})

export default router
