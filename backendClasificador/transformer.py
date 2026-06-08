import time
from typing import Dict, Any
from mongo_client import ClienteMongo
from classifier import ClasificadorPalabrasClave


class TransformadorCorreos:
    """Servicio transformador de correos para proceso ETL."""

    def __init__(self, tamano_lote: int = 10, retraso_procesamiento: float = 1.0):
        self.mongo = ClienteMongo()
        self.clasificador = ClasificadorPalabrasClave()
        self.tamano_lote = tamano_lote
        self.retraso_procesamiento = retraso_procesamiento
        self.estadisticas = {
            "procesados": 0,
            "errores": 0,
            "tiempo_total": 0.0
        }

    def _procesar_un_correo(self, correo: Dict[str, Any]) -> bool:
        """Procesa un solo correo: clasifica y actualiza."""
        try:
            asunto = correo.get("asunto", "")
            contenido = correo.get("contenido", "")

            categoria = self.clasificador.clasificar(asunto, contenido)

            exito = self.mongo.actualizar_clasificacion(correo["_id"], categoria)

            if exito:
                self.estadisticas["procesados"] += 1
                print(f"  Correo clasificado: {asunto[:50]} -> {categoria}")
            else:
                self.estadisticas["errores"] += 1
                print(f"  Error al actualizar correo: {asunto[:50]}")

            return exito

        except Exception as error:
            self.estadisticas["errores"] += 1
            print(f"  Error al procesar correo: {error}")
            return False

    def procesar_lote(self) -> int:
        """Procesa un lote de correos pendientes."""
        correos = self.mongo.obtener_correos_pendientes(self.tamano_lote)

        if not correos:
            return 0

        print(f"Lote encontrado: {len(correos)} correos por procesar")

        procesados = 0

        for correo in correos:
            if self._procesar_un_correo(correo):
                procesados += 1

            if self.retraso_procesamiento > 0:
                time.sleep(self.retraso_procesamiento)

        return procesados

    def ejecutar_una_vez(self) -> Dict[str, Any]:
        """Ejecuta un ciclo de transformacion."""
        inicio = time.time()

        procesados = self.procesar_lote()

        tiempo_transcurrido = time.time() - inicio

        self.estadisticas["tiempo_total"] += tiempo_transcurrido

        return {
            "procesados": procesados,
            "tiempo_transcurrido": round(tiempo_transcurrido, 2),
            "total_procesados": self.estadisticas["procesados"],
            "total_errores": self.estadisticas["errores"]
        }

    def cerrar(self):
        """Libera los recursos."""
        self.mongo.cerrar()