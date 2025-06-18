@echo off
echo ==========================================
echo Reiniciando servidor de desarrollo GeoportalSV
echo ==========================================

echo Deteniendo procesos de Node.js en el puerto 5173...
FOR /F "tokens=5" %%P IN ('netstat -a -n -o ^| findstr :5173') DO (
    echo Terminando proceso con PID: %%P
    taskkill /F /PID %%P
)

echo.
echo Limpiando cache de Vite...
if exist "node_modules/.vite" rmdir /s /q "node_modules\.vite"

echo.
echo Verificando dependencias...
call npm install

echo.
echo Iniciando el servidor de desarrollo con configuracion optimizada...
call npm run dev

pause
