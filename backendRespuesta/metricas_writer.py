import csv
from pathlib import Path
from datetime import datetime

RUTA_CSV = Path(__file__).parent / "metricas.csv"

class EscritorMetricas:

    def __init__(self):
        self._inicializar_archivo()

    def _inicializar_archivo(self):
        if not RUTA_CSV.exists():
            with open(RUTA_CSV, mode="w", newline="", encoding="utf-8") as archivo:
                writer = csv.writer(archivo)
                writer.writerow([
                    "fecha_registro",
                    "id_mensaje_imap",
                    "remitente",
                    "asunto",
                    "categoria",
                    "destino",
                    "fecha_extraccion",
                    "tiempo_procesamiento_segundos"
                ])

    def guardar(self, documento, categoria, destino, tiempo_procesamiento):
        fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        id_mensaje = documento.get("id_mensaje_imap", "")
        remitente = documento.get("remitente", "")
        asunto = documento.get("asunto", "")
        fecha_extraccion = documento.get("fecha_extraccion", "")

        if fecha_extraccion and isinstance(fecha_extraccion, datetime):
            fecha_extraccion = fecha_extraccion.strftime("%Y-%m-%d %H:%M:%S")

        with open(RUTA_CSV, mode="a", newline="", encoding="utf-8") as archivo:
            writer = csv.writer(archivo)
            writer.writerow([
                fecha_registro,
                id_mensaje,
                remitente,
                asunto,
                categoria,
                destino,
                fecha_extraccion,
                tiempo_procesamiento
            ])