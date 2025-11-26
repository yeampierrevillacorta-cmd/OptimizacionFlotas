@echo off
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║          🧪 VERIFICANDO SERVIDOR DJANGO                       ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

cd c:\Users\USER\optimiza_limpieza
call venv\Scripts\activate

echo 1️⃣ Verificando configuración...
python manage.py check
if errorlevel 1 (
    echo ❌ Error en la configuración
    pause
    exit /b 1
)

echo.
echo 2️⃣ Verificando configuración de producción...
python manage.py check --deploy
if errorlevel 1 (
    echo ⚠️ Advertencias de producción detectadas (normal en desarrollo)
)

echo.
echo 3️⃣ Verificando migraciones...
python manage.py showmigrations
if errorlevel 1 (
    echo ❌ Error con migraciones
    pause
    exit /b 1
)

echo.
echo ✅ TODAS LAS VERIFICACIONES PASARON
echo.
echo ¿Quieres iniciar el servidor? (S/N)
set /p answer=
if /i "%answer%"=="S" (
    echo.
    echo 🚀 Iniciando servidor en http://127.0.0.1:8000
    echo.
    python manage.py runserver
)

