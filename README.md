# 🚛 Sistema de Optimización de Rutas de Limpieza - Pueblo Libre

Sistema web desarrollado con Django y PuLP para optimizar la asignación de camiones recolectores a rutas de limpieza en el distrito de Pueblo Libre, Lima.

## 📋 Características

- **Gestión de Rutas**: Administración de zonas de barrido con información de distancia y cantidad de residuos
- **Gestión de Flota**: Control de camiones disponibles con sus capacidades
- **Motor de Optimización**: Algoritmo de programación lineal que minimiza la distancia total recorrida
- **Asignación por Turnos**: Optimización considerando turnos de mañana, tarde y noche
- **Dashboard Interactivo**: Visualización de estadísticas y resultados en tiempo real
- **Panel de Administración**: Interface administrativa de Django completamente configurada

## 🛠️ Tecnologías

- **Backend**: Django 5.2.8
- **Base de Datos**: SQLite3 (desarrollo) / PostgreSQL (producción)
- **Optimización**: Google OR-Tools 9.11+
- **Procesamiento de Datos**: Pandas 2.2.3
- **Frontend**: Bootstrap 5.3 + Bootstrap Icons

## 📦 Instalación

### 1. Clonar el repositorio

```bash
cd optimiza_limpieza
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
python manage.py migrate
```

### 5. Cargar datos iniciales

```bash
python manage.py load_data
```



### 6. (Opcional) Crear superusuario para el admin

```bash
python manage.py createsuperuser
```

### 7. Ejecutar el servidor

```bash
python manage.py runserver
```

El sistema estará disponible en: `http://localhost:8000`

## 🚀 Uso

### Dashboard Principal

Accede a `http://localhost:8000` para ver:
- Estadísticas generales del sistema
- Información de rutas y camiones
- Botón para ejecutar la optimización
- Resultados de la última optimización

### Ejecutar Optimización

1. Haz clic en el botón **"Ejecutar Solver"** en el dashboard
2. El sistema procesará los datos (puede tomar algunos segundos)
3. Serás redirigido a la página de resultados automáticamente

### Ver Resultados

La página de resultados muestra:
- Distancia total optimizada
- Carga total asignada
- Número de camiones utilizados
- Asignaciones detalladas por turno
- Gráficos de utilización de capacidad

### Administrar Datos

Accede al panel de administración en `http://localhost:8000/admin`:
- Gestionar rutas individualmente
- Ver estadísticas de uso de camiones
- Revisar asignaciones optimizadas
- Exportar datos


## 📁 Estructura del Proyecto

```
optimiza_limpieza/
├── data/                          # Datos CSV
│   ├── rutas.csv                 # Información de rutas
│   ├── demanda.csv               # Demanda de residuos por zona
│   └── dataton_pueblo_libre.csv  # Datos de camiones
├── solver_app/                   # Aplicación principal
│   ├── management/
│   │   └── commands/
│   │       └── load_data.py     # Comando para cargar datos
│   ├── templates/               # Templates HTML
│   │   └── solver_app/
│   │       ├── base.html       # Template base
│   │       ├── index.html      # Dashboard
│   │       ├── resultados.html # Resultados
│   │       ├── rutas.html      # Lista de rutas
│   │       └── camiones.html   # Lista de camiones
│   ├── admin.py                # Configuración del admin
│   ├── models.py               # Modelos de BD
│   ├── views.py                # Vistas del sistema
│   └── solver_logic.py         # Motor de optimización
├── optimiza_limpieza/          # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3                  # Base de datos
├── manage.py                   # CLI de Django
├── requirements.txt            # Dependencias
└── README.md                   # Este archivo
```

## 🔧 Comandos Útiles

### Recargar datos

```bash
python manage.py load_data
```

### Verificar sistema

```bash
python manage.py check
```

### Ver estadísticas en consola

```bash
python manage.py shell
>>> from solver_app.models import Ruta, Camion, AsignacionOptima
>>> print(f"Rutas: {Ruta.objects.count()}")
>>> print(f"Camiones: {Camion.objects.count()}")
>>> print(f"Asignaciones: {AsignacionOptima.objects.count()}")
```

### Ejecutar tests

```bash
python manage.py test
```

## 📈 Resultados Esperados

Con los datos de ejemplo (46 rutas, 42 camiones):
- **Distancia Total Optimizada**: ~120-140 km
- **Camiones Utilizados**: ~15-20 camiones
- **Utilización Promedio**: 60-80% de capacidad
- **Tiempo de Resolución**: 1-5 segundos

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📝 Licencia

Este proyecto fue desarrollado para la optimización de rutas de limpieza en Pueblo Libre, Lima.

## 👥 Autores

Sistema desarrollado con Django y PuLP para optimizar operaciones de limpieza urbana.

## 🐛 Reportar Problemas

Si encuentras algún problema o tienes sugerencias, por favor crea un issue en el repositorio.

## 📞 Soporte

Para preguntas y soporte:
- Revisa la documentación de [Django](https://docs.djangoproject.com/)
- Consulta la documentación de [Google OR-Tools](https://developers.google.com/optimization)
- Revisa el código fuente y comentarios en el proyecto

---

## ⚙️ Motor de Optimización: Google OR-Tools

El sistema utiliza **Google OR-Tools**, una suite de código abierto de Google para optimización y programación lineal.

### Ventajas de OR-Tools:
- **Rendimiento**: Altamente optimizado para problemas grandes
- **Solvers múltiples**: Incluye SCIP, GLOP, CP-SAT y más
- **Escalabilidad**: Maneja problemas con miles de variables
- **Soporte**: Respaldado por Google con actualizaciones constantes
- **Versatilidad**: Programación lineal, entera, restricciones y routing

---

**¡Gracias por usar el Sistema de Optimización de Rutas de Limpieza!** 🚛♻️

