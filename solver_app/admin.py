from django.contrib import admin
from .models import Ruta, Camion, AsignacionOptima


@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Ruta
    """
    list_display = ['id_zona_barrido', 'id_sector', 'distancia_km', 'residuos_kg', 'densidad']
    list_filter = ['id_sector']
    search_fields = ['id_zona_barrido', 'id_sector']
    ordering = ['id_sector', 'id_zona_barrido']
    
    def densidad(self, obj):
        """Calcula la densidad de residuos por kilómetro"""
        if obj.distancia_km > 0:
            return f"{(obj.residuos_kg / obj.distancia_km):.2f} kg/km"
        return "N/A"
    densidad.short_description = 'Densidad'


@admin.register(Camion)
class CamionAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Camion
    """
    list_display = ['placa', 'capacidad_kg', 'veces_usado', 'carga_total_asignada']
    search_fields = ['placa']
    ordering = ['-capacidad_kg']
    
    def veces_usado(self, obj):
        """Cuenta cuántas veces se ha asignado este camión"""
        return obj.asignacionoptima_set.count()
    veces_usado.short_description = 'Veces Usado'
    
    def carga_total_asignada(self, obj):
        """Suma la carga total asignada a este camión"""
        total = sum(a.carga_kg for a in obj.asignacionoptima_set.all())
        return f"{total:.2f} kg"
    carga_total_asignada.short_description = 'Carga Total'


@admin.register(AsignacionOptima)
class AsignacionOptimaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo AsignacionOptima
    """
    list_display = [
        'id', 
        'camion_asignado', 
        'ruta_asignada', 
        'turno', 
        'costo_distancia_km', 
        'carga_kg',
        'utilizacion_capacidad'
    ]
    list_filter = ['turno', 'camion_asignado']
    search_fields = ['camion_asignado__placa', 'ruta_asignada__id_zona_barrido']
    ordering = ['turno', 'camion_asignado__placa']
    
    def utilizacion_capacidad(self, obj):
        """Calcula el porcentaje de utilización de la capacidad del camión"""
        porcentaje = (obj.carga_kg / obj.camion_asignado.capacidad_kg) * 100
        return f"{porcentaje:.1f}%"
    utilizacion_capacidad.short_description = 'Utilización'
