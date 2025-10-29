#!/bin/bash

# Script para desplegar los cambios en el servidor
# Ejecutar como: bash deploy.sh

echo "🚀 Iniciando despliegue de GeoportalSV..."

# Navegar a la carpeta del proyecto
cd /var/www/GeoportalSV/geoportal

# Obtener los cambios del repositorio
echo "📥 Obteniendo cambios del repositorio..."
git pull origin main

# Instalar/actualizar dependencias
echo "📦 Instalando dependencias..."
npm install

# Limpiar caché de npm (opcional pero recomendado)
echo "🧹 Limpiando caché..."
npm cache clean --force

# Compilar para producción
echo "🔨 Compilando para producción..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Compilación exitosa"
    
    # Reiniciar nginx
    echo "🔄 Reiniciando nginx..."
    systemctl restart nginx
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx reiniciado correctamente"
        echo "🎉 Despliegue completado exitosamente"
    else
        echo "❌ Error al reiniciar nginx"
        exit 1
    fi
else
    echo "❌ Error en la compilación"
    exit 1
fi
