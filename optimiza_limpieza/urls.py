"""
URL configuration for optimiza_limpieza project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from solver_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Páginas principales
    path('', views.index, name='index'),
    path('rutas/', views.listar_rutas, name='listar_rutas'),
    path('camiones/', views.listar_camiones, name='listar_camiones'),
    
    # Optimización
    path('ejecutar-solver/', views.ejecutar_solver, name='ejecutar_solver'),
    path('resultados/', views.resultados_optimizacion, name='resultados_optimizacion'),
    path('limpiar-asignaciones/', views.limpiar_asignaciones, name='limpiar_asignaciones'),
    
    # API endpoints
    path('api/stats/', views.api_stats, name='api_stats'),
]
