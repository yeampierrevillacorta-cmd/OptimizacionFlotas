import pandas as pd
from django.core.management.base import BaseCommand
from solver_app.models import Ruta, Camion

class Command(BaseCommand):
    help = 'Carga los datos de los CSV a la base de datos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando carga de datos...'))

        # --- Cargar Rutas y Demandas ---
        df_rutas = pd.read_csv('data/rutas.csv')
        df_demanda = pd.read_csv('data/demanda.csv')

        # Unimos los dos dataframes por el id de la zona
        df_zonas = pd.merge(df_rutas, df_demanda, on='id_zona_barrido')

        Ruta.objects.all().delete() # Limpiamos datos antiguos
        for _, row in df_zonas.iterrows():
            Ruta.objects.create(
                id_zona_barrido=row['id_zona_barrido'],
                id_sector=row['id_sector'],
                distancia_km=row['distancia_km'],
                residuos_kg=row['residuos_kg']
            )
        self.stdout.write(self.style.SUCCESS(f'Se cargaron {Ruta.objects.count()} rutas.'))

        # --- Cargar Camiones y Capacidades ---
        # Asume que tu CSV se llama 'dataton_pueblo_libre.csv'
        df_operaciones = pd.read_csv('data/dataton_pueblo_libre.csv')

        # Agrupamos por placa y encontramos la capacidad MÁXIMA registrada
        # Asumimos que la 'CANTIDAD' está en Toneladas
        df_camiones = df_operaciones.groupby('PLACA')['CANTIDAD'].max().reset_index()

        Camion.objects.all().delete() # Limpiamos datos antiguos
        for _, row in df_camiones.iterrows():
            Camion.objects.create(
                placa=row['PLACA'],
                capacidad_kg=row['CANTIDAD'] * 1000  # Convertimos a Kg
            )
        self.stdout.write(self.style.SUCCESS(f'Se cargaron {Camion.objects.count()} camiones.'))

        self.stdout.write(self.style.SUCCESS('¡Carga de datos completada!'))