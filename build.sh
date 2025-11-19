#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🔧 Instalando dependencias..."
pip install -r requirements.txt

echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input

echo "🗄️ Ejecutando migraciones de base de datos..."
python manage.py migrate

echo "📊 Cargando datos iniciales..."
python manage.py load_data || echo "⚠️ Datos ya cargados o no disponibles, continuando..."

echo "✅ Build completado exitosamente!"

