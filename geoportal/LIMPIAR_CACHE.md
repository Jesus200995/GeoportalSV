# 🧹 LIMPIAR CACHÉ - INSTRUCCIONES

Si el carrusel no se ve correctamente después de los cambios, sigue estos pasos:

## Opción 1: Limpiar caché del navegador (Recomendado)

### Chrome / Edge:
1. Abre Developer Tools (F12)
2. Haz clic derecho en el botón de Refresh (Actualizar)
3. Selecciona "Empty cache and hard refresh" (Vaciar caché y actualización forzada)
4. O presiona: **Ctrl + Shift + Delete** → Borra caché → Limpia

### Firefox:
1. Abre Developer Tools (F12)
2. Storage → Cache Storage
3. Selecciona todos los cachés y elimina
4. O presiona: **Ctrl + Shift + Delete** → Borrar datos → Limpia

### Safari:
1. Safari → Preferencias → Privacidad
2. Haz clic en "Gestionar datos del sitio web"
3. Busca tu dominio y elimina
4. O presiona: **Cmd + Shift + Delete**

## Opción 2: Limpiar caché desde terminal

```bash
# Ir a la carpeta del proyecto
cd c:\Users\Admin_1\Pictures\Desarrollo\GeoportalSV\geoportal

# Eliminar carpeta node_modules
rm -r node_modules

# Eliminar package-lock.json
rm package-lock.json

# Reinstalar dependencias
npm install

# Limpiar caché de npm
npm cache clean --force

# Ejecutar en modo desarrollo
npm run dev
```

## Opción 3: Forzar recarga del navegador

- **Chrome/Edge/Firefox**: Ctrl + F5
- **Safari**: Cmd + Shift + R

## ✅ Lo que ya hemos hecho:

1. ✅ Actualizado `vite.config.js` con headers anti-caché
2. ✅ Agregados meta tags en `index.html` para evitar caché
3. ✅ Optimizado el icono de formularios

**Después de cualquiera de estos pasos, el carrusel debería mostrarse correctamente con el nuevo botón de FORMULARIOS en color rosa.**

## 🔍 Si aún tienes problemas:

1. Abre DevTools (F12)
2. Sección "Network"
3. Marca "Disable cache"
4. Recarga la página (Ctrl + F5)
5. Verifica que el archivo HomeView.vue se cargue correctamente

