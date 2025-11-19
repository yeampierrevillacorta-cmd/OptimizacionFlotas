@echo off
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║        🚀 SCRIPT DE DESPLIEGUE AUTOMÁTICO 🚀                 ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo Este script hará commit y push de todos los cambios a GitHub
echo.
pause

echo.
echo 📊 Verificando estado de Git...
git status
echo.

echo 📦 Agregando todos los archivos...
git add .
echo.

echo 📝 Haciendo commit...
git commit -m "Fix: Configuración completa para despliegue en Render - Django WSGI correcto"
echo.

echo 🚀 Subiendo a GitHub...
git push origin main
echo.

echo ✅ ¡Listo! Tu código está en GitHub
echo.
echo 🌐 Render detectará los cambios automáticamente
echo 📺 Monitorea el progreso en: https://dashboard.render.com
echo ⏱️ El deploy tomará 5-10 minutos
echo.
echo 🎯 Tu aplicación estará en: https://optimiza-limpieza.onrender.com
echo    (o el nombre que hayas elegido)
echo.
pause

