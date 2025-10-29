# Script para limpiar caché - Ejecutar en PowerShell como Administrador

Write-Host "🧹 Limpiando caché del proyecto Geoportal..." -ForegroundColor Green

$projectPath = "c:\Users\Admin_1\Pictures\Desarrollo\GeoportalSV\geoportal"

# Navegar a la carpeta del proyecto
cd $projectPath

# Eliminar carpeta de distribución
if (Test-Path "dist") {
    Write-Host "Eliminando carpeta 'dist'..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force dist
}

# Limpiar caché de npm
Write-Host "Limpiando caché de npm..." -ForegroundColor Yellow
npm cache clean --force

# Limpiar caché de Vite
if (Test-Path ".vite") {
    Write-Host "Eliminando carpeta '.vite'..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .vite
}

Write-Host "✅ Caché limpiado correctamente" -ForegroundColor Green
Write-Host "Ahora ejecuta: npm run dev" -ForegroundColor Cyan
