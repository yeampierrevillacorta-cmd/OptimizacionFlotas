"""
Motor de Optimización para Asignación de Rutas de Limpieza
Utiliza programación lineal con Google OR-Tools para asignar camiones a rutas de manera óptima.
"""

from ortools.linear_solver import pywraplp
from solver_app.models import Ruta, Camion, AsignacionOptima
from django.db.models import Sum
import logging

logger = logging.getLogger(__name__)


class SolverRutasLimpieza:
    """
    Resuelve el problema de asignación de camiones a rutas de limpieza.
    Utiliza Google OR-Tools para programación lineal entera mixta.
    
    Objetivo: Minimizar la distancia total recorrida
    Restricciones:
        - Cada ruta debe ser cubierta exactamente una vez
        - La carga asignada a cada camión no puede exceder su capacidad
        - Cada camión puede hacer múltiples viajes en diferentes turnos
    """
    
    TURNOS = ['MAÑANA', 'TARDE', 'NOCHE']
    
    def __init__(self):
        self.rutas = list(Ruta.objects.all())
        self.camiones = list(Camion.objects.all())
        self.solver = None
        self.variables = {}
        self.solucion = []
        
    def crear_modelo(self):
        """Crea el modelo de programación lineal con OR-Tools"""
        logger.info("Creando modelo de optimización con Google OR-Tools...")
        
        # Crear el solver (SCIP es el solver de código abierto para MIP)
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        
        if not self.solver:
            raise Exception("No se pudo crear el solver SCIP de OR-Tools")
        
        # Variables de decisión: x[i,j,t] = 1 si el camión i cubre la ruta j en el turno t
        self.variables = {}
        for camion in self.camiones:
            for ruta in self.rutas:
                for turno in self.TURNOS:
                    var_name = f"x_{camion.placa}_{ruta.id_zona_barrido}_{turno}"
                    # Variable binaria (0 o 1)
                    self.variables[(camion.placa, ruta.id_zona_barrido, turno)] = \
                        self.solver.BoolVar(var_name)
        
        logger.info(f"Creadas {len(self.variables)} variables de decisión binarias")
        
    def agregar_funcion_objetivo(self):
        """
        Función objetivo: Minimizar la distancia total recorrida
        """
        # Crear la expresión de la función objetivo
        objetivo = self.solver.Sum([
            self.variables[(c.placa, r.id_zona_barrido, t)] * float(r.distancia_km)
            for c in self.camiones
            for r in self.rutas
            for t in self.TURNOS
        ])
        
        # Establecer como objetivo de minimización
        self.solver.Minimize(objetivo)
        
        logger.info("Función objetivo agregada: Minimizar distancia total")
        
    def agregar_restricciones(self):
        """Agrega todas las restricciones al modelo"""
        
        # Restricción 1: Cada ruta debe ser cubierta exactamente una vez
        for ruta in self.rutas:
            self.solver.Add(
                self.solver.Sum([
                    self.variables[(c.placa, ruta.id_zona_barrido, t)]
                    for c in self.camiones
                    for t in self.TURNOS
                ]) == 1
            )
        
        logger.info(f"Agregadas {len(self.rutas)} restricciones de cobertura de rutas")
        
        # Restricción 2: Capacidad de cada camión por turno
        for camion in self.camiones:
            for turno in self.TURNOS:
                self.solver.Add(
                    self.solver.Sum([
                        self.variables[(camion.placa, r.id_zona_barrido, turno)] * 
                        float(r.residuos_kg)
                        for r in self.rutas
                    ]) <= float(camion.capacidad_kg)
                )
        
        logger.info(f"Agregadas {len(self.camiones) * len(self.TURNOS)} restricciones de capacidad")
        
        # Restricción 3: Un camión puede hacer como máximo 1 ruta por turno
        # (un camión no puede estar en dos lugares al mismo tiempo)
        for camion in self.camiones:
            for turno in self.TURNOS:
                self.solver.Add(
                    self.solver.Sum([
                        self.variables[(camion.placa, r.id_zona_barrido, turno)]
                        for r in self.rutas
                    ]) <= 1
                )
        
        logger.info(f"Agregadas {len(self.camiones) * len(self.TURNOS)} restricciones de simultaneidad (máximo 1 ruta por camión por turno)")
        
    def resolver(self):
        """
        Resuelve el problema de optimización con OR-Tools
        
        Returns:
            dict: Diccionario con los resultados de la optimización
        """
        logger.info("Iniciando resolución del problema con OR-Tools...")
        
        # Crear modelo completo
        self.crear_modelo()
        self.agregar_funcion_objetivo()
        self.agregar_restricciones()
        
        # Configurar límite de tiempo (opcional, 300 segundos = 5 minutos)
        self.solver.SetTimeLimit(300000)  # en milisegundos
        
        # Resolver
        logger.info("Ejecutando solver...")
        status = self.solver.Solve()
        
        # Verificar estado de la solución
        if status == pywraplp.Solver.OPTIMAL:
            estado = 'Optimal'
            logger.info("✓ Solución óptima encontrada")
        elif status == pywraplp.Solver.FEASIBLE:
            estado = 'Feasible'
            logger.warning("⚠ Solución factible encontrada (no óptima)")
        else:
            estados = {
                pywraplp.Solver.INFEASIBLE: 'Infeasible',
                pywraplp.Solver.UNBOUNDED: 'Unbounded',
                pywraplp.Solver.ABNORMAL: 'Abnormal',
                pywraplp.Solver.NOT_SOLVED: 'Not Solved'
            }
            estado = estados.get(status, 'Unknown')
            raise Exception(f"No se pudo encontrar una solución óptima. Estado: {estado}")
        
        # Extraer solución
        self.extraer_solucion()
        
        # Calcular estadísticas
        estadisticas = self.calcular_estadisticas()
        
        # Obtener valor objetivo
        distancia_total = self.solver.Objective().Value()
        
        # Información adicional del solver
        logger.info(f"Tiempo de resolución: {self.solver.WallTime()} ms")
        logger.info(f"Número de variables: {self.solver.NumVariables()}")
        logger.info(f"Número de restricciones: {self.solver.NumConstraints()}")
        
        return {
            'estado': estado,
            'distancia_total': distancia_total,
            'asignaciones': self.solucion,
            'estadisticas': estadisticas
        }
    
    def extraer_solucion(self):
        """Extrae las asignaciones de la solución de OR-Tools"""
        self.solucion = []
        
        for (placa, zona_id, turno), var in self.variables.items():
            # En OR-Tools, usamos solution_value() para obtener el valor de la variable
            if var.solution_value() == 1:
                # Encontrar la ruta y el camión correspondientes
                ruta = next(r for r in self.rutas if r.id_zona_barrido == zona_id)
                camion = next(c for c in self.camiones if c.placa == placa)
                
                self.solucion.append({
                    'camion': camion,
                    'ruta': ruta,
                    'turno': turno,
                    'distancia_km': float(ruta.distancia_km),
                    'carga_kg': float(ruta.residuos_kg)
                })
        
        logger.info(f"✓ Extraídas {len(self.solucion)} asignaciones óptimas")
        
    def calcular_estadisticas(self):
        """Calcula estadísticas de la solución"""
        total_rutas = len(self.solucion)
        distancia_total = sum(a['distancia_km'] for a in self.solucion)
        carga_total = sum(a['carga_kg'] for a in self.solucion)
        
        # Camiones utilizados
        camiones_usados = set(a['camion'].placa for a in self.solucion)
        num_camiones_usados = len(camiones_usados)
        
        # Asignaciones por turno
        asignaciones_por_turno = {}
        for turno in self.TURNOS:
            asignaciones_por_turno[turno] = len([a for a in self.solucion if a['turno'] == turno])
        
        # Utilización promedio de camiones por turno
        utilizacion_por_turno = {}
        for turno in self.TURNOS:
            asignaciones_turno = [a for a in self.solucion if a['turno'] == turno]
            if asignaciones_turno:
                # Agrupar por camión
                carga_por_camion = {}
                for a in asignaciones_turno:
                    placa = a['camion'].placa
                    if placa not in carga_por_camion:
                        carga_por_camion[placa] = {
                            'carga': 0,
                            'capacidad': float(a['camion'].capacidad_kg)
                        }
                    carga_por_camion[placa]['carga'] += a['carga_kg']
                
                # Calcular utilización promedio
                utilizaciones = [
                    (info['carga'] / info['capacidad']) * 100
                    for info in carga_por_camion.values()
                ]
                utilizacion_por_turno[turno] = sum(utilizaciones) / len(utilizaciones)
            else:
                utilizacion_por_turno[turno] = 0
        
        return {
            'total_rutas_asignadas': total_rutas,
            'distancia_total_km': round(distancia_total, 2),
            'carga_total_kg': round(carga_total, 2),
            'camiones_utilizados': num_camiones_usados,
            'camiones_disponibles': len(self.camiones),
            'asignaciones_por_turno': asignaciones_por_turno,
            'utilizacion_promedio_por_turno': {
                k: round(v, 2) for k, v in utilizacion_por_turno.items()
            }
        }
    
    def guardar_en_base_datos(self):
        """Guarda la solución en la base de datos"""
        logger.info("Guardando solución en la base de datos...")
        
        # Limpiar asignaciones anteriores
        AsignacionOptima.objects.all().delete()
        
        # Guardar nuevas asignaciones
        for asignacion in self.solucion:
            AsignacionOptima.objects.create(
                ruta_asignada=asignacion['ruta'],
                camion_asignado=asignacion['camion'],
                turno=asignacion['turno'],
                costo_distancia_km=asignacion['distancia_km'],
                carga_kg=asignacion['carga_kg']
            )
        
        logger.info(f"Guardadas {len(self.solucion)} asignaciones en la base de datos")


def ejecutar_optimizacion():
    """
    Función principal para ejecutar la optimización.
    
    Returns:
        dict: Resultados de la optimización
    """
    try:
        solver = SolverRutasLimpieza()
        resultados = solver.resolver()
        solver.guardar_en_base_datos()
        
        return {
            'exito': True,
            'mensaje': 'Optimización completada exitosamente',
            'resultados': resultados
        }
    
    except Exception as e:
        logger.error(f"Error durante la optimización: {str(e)}", exc_info=True)
        return {
            'exito': False,
            'mensaje': f'Error: {str(e)}',
            'resultados': None
        }

