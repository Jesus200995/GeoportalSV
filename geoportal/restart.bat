@echo off
echo Deteniendo procesos de Node.js en el puerto 5173...
FOR /F "tokens=5" %%P IN ('netstat -a -n -o ^| findstr :5173') DO (
    echo Terminando proceso con PID: %%P
    taskkill /F /PID %%P
)
echo Instalando dependencias...
call npm install
echo Iniciando el servidor de desarrollo...
call npm run dev
