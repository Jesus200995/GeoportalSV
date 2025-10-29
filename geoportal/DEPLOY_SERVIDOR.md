# 🚀 COMANDOS PARA DESPLEGAR EN EL SERVIDOR

## Problema encontrado:
- Error: `terser not found` al compilar con Vite

## Solución aplicada:
- Cambié `minify: 'terser'` por `minify: 'esbuild'` en vite.config.js
- esbuild es el minificador predeterminado y no requiere instalación adicional

## Comandos para ejecutar en el servidor:

```bash
# Conectar al servidor
ssh root@srv824686

# Navegar a la carpeta del proyecto
cd /var/www/GeoportalSV/geoportal

# Obtener los últimos cambios
git pull origin main

# Instalar dependencias (si es necesario)
npm install

# Limpiar caché de npm
npm cache clean --force

# Eliminar build anterior (opcional pero recomendado)
rm -rf dist

# Compilar para producción
npm run build

# Si la compilación es exitosa, reiniciar nginx
systemctl restart nginx

# Verificar que nginx está corriendo
systemctl status nginx
```

## Script rápido (una línea):

```bash
cd /var/www/GeoportalSV/geoportal && git pull origin main && npm install && npm run build && systemctl restart nginx && systemctl status nginx
```

## Verificar que todo funcionó:

1. Abre el navegador en el servidor: https://tu-dominio.com
2. Deberías ver el carrusel con 6 botones
3. El nuevo botón "FORMULARIOS" en color rosa debe aparecer
4. Abre DevTools (F12) y verifica que no hay errores en la consola

## Si aún hay problemas:

```bash
# Limpiar completamente
rm -rf node_modules dist
npm install
npm run build
systemctl restart nginx
```

## Para ver logs en tiempo real:

```bash
# Ver errores de nginx
tail -f /var/log/nginx/error.log

# Ver accesos
tail -f /var/log/nginx/access.log
```
