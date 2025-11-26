@echo off
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║        🚀 INICIANDO SERVIDOR DE DESARROLLO DJANGO            ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo 📦 Activando entorno virtual...
call venv\Scripts\activate

echo.
echo 🔍 Verificando configuración de Django...
python manage.py check

echo.
echo 🗄️ Verificando migraciones...
python manage.py showmigrations --list | find "[X]" > nul
if errorlevel 1 (
    echo ⚠️ Aplicando migraciones...
    python manage.py migrate
)

echo.
echo 📊 Cargando datos si es necesario...
python manage.py load_data 2>nul || echo ℹ️ Datos ya cargados

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║           ✅ SERVIDOR LISTO - Iniciando...                   ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo 🌐 Abre tu navegador en: http://127.0.0.1:8000
echo 🛑 Presiona Ctrl+C para detener el servidor
echo.

python manage.py runserver

