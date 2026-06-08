# main.py
import time
import signal
import sys
from config import INTERVALO_POLLING_SEGUNDOS, TAMANO_LOTE, RETRASO_PROCESAMIENTO_SEGUNDOS
from transformer import TransformadorCorreos


class ServicioTransformador:
    """Servicio principal con polling y apagado controlado."""

    def __init__(self):
        self.transformador = TransformadorCorreos(
            tamano_lote=TAMANO_LOTE,
            retraso_procesamiento=RETRASO_PROCESAMIENTO_SEGUNDOS
        )
        self.ejecutando = True
        signal.signal(signal.SIGINT, self._manejador_senal)
        signal.signal(signal.SIGTERM, self._manejador_senal)

    def _manejador_senal(self, signum, frame):
        """Maneja las senales de apagado de forma controlada."""
        print("\nSenal de apagado recibida. Deteniendo servicio...")
        self.ejecutando = False

    def _imprimir_estado(self, resultado: dict, ciclo: int):
        """Imprime el estado del procesamiento."""
        print(f"[Ciclo {ciclo}] Procesados: {resultado['procesados']} | "
              f"Tiempo: {resultado['tiempo_transcurrido']}s | "
              f"Total acumulado: {resultado['total_procesados']} | "
              f"Errores: {resultado['total_errores']}")

    def ejecutar(self):
        """Ejecuta el servicio transformador con polling continuo."""
        ciclo = 0

        print("Servicio Transformador de Correos Iniciado")
        print(f"Consultando cada {INTERVALO_POLLING_SEGUNDOS} segundos")
        print(f"Retraso de procesamiento: {RETRASO_PROCESAMIENTO_SEGUNDOS} segundo por correo")
        print(f"Tamano del lote: {TAMANO_LOTE}")

        while self.ejecutando:
            try:
                ciclo += 1
                resultado = self.transformador.ejecutar_una_vez()

                if resultado["procesados"] > 0:
                    self._imprimir_estado(resultado, ciclo)
                else:
                    if ciclo % 6 == 0:
                        print(f"[Ciclo {ciclo}] No hay correos pendientes. Esperando...")

                time.sleep(INTERVALO_POLLING_SEGUNDOS)

            except Exception as error:
                print(f"Error en el ciclo principal: {error}")
                time.sleep(INTERVALO_POLLING_SEGUNDOS)

        self.apagar()

    def apagar(self):
        """Apagado limpio del servicio."""
        print("\nApagando servicio transformador...")
        self.transformador.cerrar()
        print("Servicio detenido.")


def main():
    servicio = ServicioTransformador()
    servicio.ejecutar()


if __name__ == "__main__":
    main()