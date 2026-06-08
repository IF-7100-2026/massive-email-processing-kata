# cola_humana_writer.py
import csv
from pathlib import Path
from datetime import datetime


RUTA_CSV_COLA_HUMANA = (
    Path(__file__).parent
    / "cola_humana.csv"
)


class EscritorColaHumana:

    def guardar(
        self,
        documento,
        categoria
    ):

        archivo_existe = (
            RUTA_CSV_COLA_HUMANA.exists()
        )

        with open(
            RUTA_CSV_COLA_HUMANA,
            mode="a",
            newline="",
            encoding="utf-8"
        ) as archivo:

            writer = csv.writer(
                archivo
            )

            if not archivo_existe:

                writer.writerow([
                    "fecha_registro",
                    "id_mensaje_imap",
                    "remitente",
                    "asunto",
                    "categoria",
                    "estado"
                ])

            writer.writerow([
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

                documento.get(
                    "id_mensaje_imap",
                    ""
                ),

                documento.get(
                    "remitente",
                    ""
                ),

                documento.get(
                    "asunto",
                    ""
                ),

                categoria,

                "Pendiente de revisión humana"
            ])

        print(
            f"Guardado en CSV: "
            f"{RUTA_CSV_COLA_HUMANA}"
        )