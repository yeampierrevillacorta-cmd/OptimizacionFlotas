from django.db import models


class Ruta(models.Model):
    """
    Define una Zona de Barrido (variable 'j').
    Combina los datos de rutas.csv y demanda.csv.
    """
    id_zona_barrido = models.IntegerField(primary_key=True, unique=True)
    id_sector = models.IntegerField()

    # Parámetro C_j (Costo)
    distancia_km = models.DecimalField(max_digits=5, decimal_places=2)

    # Parámetro D_j (Demanda)
    residuos_kg = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"Zona {self.id_zona_barrido} (Sector {self.id_sector})"


class Camion(models.Model):
    """
    Define un vehículo de la flota (recurso 'i').
    Se extrae del CSV de la Dataton.
    """
    placa = models.CharField(max_length=10, primary_key=True, unique=True)

    # Parámetro Q_i (Capacidad)
    # Guardamos en Kg para ser consistentes con la demanda de la ruta
    capacidad_kg = models.DecimalField(max_digits=10, decimal_places=2)

    # Podríamos añadir más datos del CSV si quisiéramos
    # unidad_nombre = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.placa} ({self.capacidad_kg} Kg)"


class AsignacionOptima(models.Model):
    """
    Esta tabla guardará los *resultados* de la optimización.
    """
    ruta_asignada = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    camion_asignado = models.ForeignKey(Camion, on_delete=models.CASCADE)
    turno = models.CharField(max_length=20)  # Ej. "MAÑANA", "TARDE", "NOCHE"

    # Guardamos los costos y demandas de esta asignación
    costo_distancia_km = models.DecimalField(max_digits=5, decimal_places=2)
    carga_kg = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"{self.camion_asignado.placa} -> {self.ruta_asignada.id_zona_barrido} (Turno: {self.turno})"