"""
Vistas para la aplicación de optimización de rutas de limpieza
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum, Avg
from solver_app.models import Ruta, Camion, AsignacionOptima
from solver_app.solver_logic import ejecutar_optimizacion
import logging

logger = logging.getLogger(__name__)


def index(request):
    """
    Vista principal - Dashboard con resumen del sistema
    """
    # Obtener estadísticas generales
    total_rutas = Ruta.objects.count()
    total_camiones = Camion.objects.count()
    total_asignaciones = AsignacionOptima.objects.count()
    
    # Estadísticas de rutas
    stats_rutas = Ruta.objects.aggregate(
        distancia_total=Sum('distancia_km'),
        residuos_totales=Sum('residuos_kg'),
        distancia_promedio=Avg('distancia_km'),
        residuos_promedio=Avg('residuos_kg')
    )
    
    # Estadísticas de camiones
    stats_camiones = Camion.objects.aggregate(
        capacidad_total=Sum('capacidad_kg'),
        capacidad_promedio=Avg('capacidad_kg')
    )
    
    # Estadísticas de asignaciones si existen
    hay_asignaciones = total_asignaciones > 0
    stats_asignaciones = None
    
    if hay_asignaciones:
        stats_asignaciones = AsignacionOptima.objects.aggregate(
            distancia_total=Sum('costo_distancia_km'),
            carga_total=Sum('carga_kg')
        )
        
        # Contar asignaciones por turno
        asignaciones_por_turno = {}
        for turno in ['MAÑANA', 'TARDE', 'NOCHE']:
            asignaciones_por_turno[turno] = AsignacionOptima.objects.filter(
                turno=turno
            ).count()
        
        # Camiones utilizados
        camiones_utilizados = AsignacionOptima.objects.values(
            'camion_asignado'
        ).distinct().count()
        
        stats_asignaciones['asignaciones_por_turno'] = asignaciones_por_turno
        stats_asignaciones['camiones_utilizados'] = camiones_utilizados
        stats_asignaciones['eficiencia'] = round(
            (camiones_utilizados / total_camiones * 100) if total_camiones > 0 else 0,
            2
        )
    
    contexto = {
        'total_rutas': total_rutas,
        'total_camiones': total_camiones,
        'total_asignaciones': total_asignaciones,
        'stats_rutas': stats_rutas,
        'stats_camiones': stats_camiones,
        'hay_asignaciones': hay_asignaciones,
        'stats_asignaciones': stats_asignaciones,
    }
    
    return render(request, 'solver_app/index.html', contexto)


def ejecutar_solver(request):
    """
    Vista para ejecutar el solver de optimización
    """
    if request.method == 'POST':
        logger.info("Iniciando proceso de optimización desde la vista...")
        
        # Verificar que hay datos cargados
        if Ruta.objects.count() == 0 or Camion.objects.count() == 0:
            messages.error(
                request,
                'No hay suficientes datos para optimizar. '
                'Asegúrate de cargar rutas y camiones primero.'
            )
            return redirect('index')
        
        # Ejecutar optimización
        resultado = ejecutar_optimizacion()
        
        if resultado['exito']:
            messages.success(
                request,
                f"¡Optimización completada! "
                f"Distancia total: {resultado['resultados']['distancia_total']:.2f} km"
            )
        else:
            messages.error(
                request,
                f"Error en la optimización: {resultado['mensaje']}"
            )
        
        return redirect('resultados_optimizacion')
    
    return redirect('index')


def resultados_optimizacion(request):
    """
    Vista para mostrar los resultados de la optimización
    """
    asignaciones = AsignacionOptima.objects.select_related(
        'ruta_asignada', 'camion_asignado'
    ).order_by('turno', 'camion_asignado__placa')
    
    if not asignaciones.exists():
        messages.warning(
            request,
            'No hay resultados de optimización. Ejecuta el solver primero.'
        )
        return redirect('index')
    
    # Agrupar asignaciones por turno
    asignaciones_por_turno = {
        'MAÑANA': [],
        'TARDE': [],
        'NOCHE': []
    }
    
    for asignacion in asignaciones:
        asignaciones_por_turno[asignacion.turno].append(asignacion)
    
    # Calcular estadísticas
    stats = {
        'total_asignaciones': asignaciones.count(),
        'distancia_total': asignaciones.aggregate(
            Sum('costo_distancia_km')
        )['costo_distancia_km__sum'],
        'carga_total': asignaciones.aggregate(
            Sum('carga_kg')
        )['carga_kg__sum'],
        'camiones_utilizados': asignaciones.values(
            'camion_asignado'
        ).distinct().count(),
    }
    
    # Estadísticas por turno
    stats_por_turno = {}
    for turno in ['MAÑANA', 'TARDE', 'NOCHE']:
        turno_asignaciones = asignaciones.filter(turno=turno)
        stats_por_turno[turno] = {
            'count': turno_asignaciones.count(),
            'distancia': turno_asignaciones.aggregate(
                Sum('costo_distancia_km')
            )['costo_distancia_km__sum'] or 0,
            'carga': turno_asignaciones.aggregate(
                Sum('carga_kg')
            )['carga_kg__sum'] or 0,
            'camiones': turno_asignaciones.values(
                'camion_asignado'
            ).distinct().count(),
        }
    
    contexto = {
        'asignaciones_por_turno': asignaciones_por_turno,
        'stats': stats,
        'stats_por_turno': stats_por_turno,
    }
    
    return render(request, 'solver_app/resultados.html', contexto)


def listar_rutas(request):
    """
    Vista para listar todas las rutas disponibles
    """
    rutas = Ruta.objects.all().order_by('id_sector', 'id_zona_barrido')
    
    # Estadísticas
    stats = rutas.aggregate(
        total=Count('id_zona_barrido'),
        distancia_total=Sum('distancia_km'),
        residuos_totales=Sum('residuos_kg'),
        distancia_promedio=Avg('distancia_km'),
        residuos_promedio=Avg('residuos_kg')
    )
    
    # Agrupar por sector
    sectores = {}
    for ruta in rutas:
        if ruta.id_sector not in sectores:
            sectores[ruta.id_sector] = []
        sectores[ruta.id_sector].append(ruta)
    
    contexto = {
        'rutas': rutas,
        'sectores': sectores,
        'stats': stats,
    }
    
    return render(request, 'solver_app/rutas.html', contexto)


def listar_camiones(request):
    """
    Vista para listar todos los camiones disponibles
    """
    camiones = Camion.objects.all().order_by('-capacidad_kg')
    
    # Estadísticas
    stats = camiones.aggregate(
        total=Count('placa'),
        capacidad_total=Sum('capacidad_kg'),
        capacidad_promedio=Avg('capacidad_kg')
    )
    
    # Agregar información de uso si hay asignaciones
    camiones_con_uso = []
    for camion in camiones:
        asignaciones = AsignacionOptima.objects.filter(camion_asignado=camion)
        uso = {
            'camion': camion,
            'veces_usado': asignaciones.count(),
            'carga_total': asignaciones.aggregate(
                Sum('carga_kg')
            )['carga_kg__sum'] or 0,
            'distancia_total': asignaciones.aggregate(
                Sum('costo_distancia_km')
            )['costo_distancia_km__sum'] or 0,
        }
        if uso['veces_usado'] > 0:
            uso['utilizacion_promedio'] = round(
                (uso['carga_total'] / (float(camion.capacidad_kg) * uso['veces_usado'])) * 100,
                2
            )
        else:
            uso['utilizacion_promedio'] = 0
        
        camiones_con_uso.append(uso)
    
    contexto = {
        'camiones_con_uso': camiones_con_uso,
        'stats': stats,
        'hay_asignaciones': AsignacionOptima.objects.exists(),
    }
    
    return render(request, 'solver_app/camiones.html', contexto)


@require_http_methods(["POST"])
def limpiar_asignaciones(request):
    """
    Vista para limpiar todas las asignaciones
    """
    count = AsignacionOptima.objects.count()
    AsignacionOptima.objects.all().delete()
    
    messages.success(
        request,
        f'Se eliminaron {count} asignaciones. Puedes ejecutar el solver nuevamente.'
    )
    
    return redirect('index')


# API endpoints para uso con JavaScript/Ajax
def api_stats(request):
    """
    API endpoint que devuelve estadísticas en formato JSON
    """
    stats = {
        'rutas': {
            'total': Ruta.objects.count(),
            'distancia_total': float(Ruta.objects.aggregate(
                Sum('distancia_km')
            )['distancia_km__sum'] or 0),
            'residuos_totales': float(Ruta.objects.aggregate(
                Sum('residuos_kg')
            )['residuos_kg__sum'] or 0),
        },
        'camiones': {
            'total': Camion.objects.count(),
            'capacidad_total': float(Camion.objects.aggregate(
                Sum('capacidad_kg')
            )['capacidad_kg__sum'] or 0),
        },
        'asignaciones': {
            'total': AsignacionOptima.objects.count(),
        }
    }
    
    if stats['asignaciones']['total'] > 0:
        stats['asignaciones']['distancia_total'] = float(
            AsignacionOptima.objects.aggregate(
                Sum('costo_distancia_km')
            )['costo_distancia_km__sum'] or 0
        )
        stats['asignaciones']['carga_total'] = float(
            AsignacionOptima.objects.aggregate(
                Sum('carga_kg')
            )['carga_kg__sum'] or 0
        )
    
    return JsonResponse(stats)
