import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      'chart.js': path.resolve(__dirname, 'node_modules/chart.js/dist/chart.js')
    },
  },
  optimizeDeps: {
    include: ['chart.js']
  },
  publicDir: 'public',
  assetsInclude: ['**/*.png', '**/*.jpg', '**/*.jpeg', '**/*.svg'],
  build: {
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        assetFileNames: 'assets/[name][extname]'
      }
    }
  },  // Configuración de servidor con proxy para evitar problemas CORS
  server: {
    port: 5173,
    proxy: {
      // Proxy para la API del backend
      '/api': {
        target: 'https://geoportal.sembrandodatos.com',
        changeOrigin: true,
        secure: false,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('Error de proxy:', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Enviando:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Recibido:', proxyRes.statusCode, req.url);
          });
        }
      },
      // Proxy para GeoServer
      '/geoserver': {
        target: 'https://geoportal.sembrandodatos.com',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
