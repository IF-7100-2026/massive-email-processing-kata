# main.py
import time
import signal

from config import (
    TAMANO_LOTE,
    INTERVALO_POLLING_SEGUNDOS
)

from loader import (
    CargadorCorreos
)


class ServicioLoad:

    def __init__(self):

        self.cargador = (
            CargadorCorreos(
                tamano_lote=TAMANO_LOTE
            )
        )

        self.ejecutando = True

        signal.signal(
            signal.SIGINT,
            self._detener
        )

        signal.signal(
            signal.SIGTERM,
            self._detener
        )

    def _detener(
        self,
        signum,
        frame
    ):

        print(
            "\nDeteniendo LOAD..."
        )

        self.ejecutando = False

    def ejecutar(self):

        print(
            "Servicio LOAD iniciado"
        )

        while self.ejecutando:

            resultado = (
                self.cargador.ejecutar_una_vez()
            )

            print(
                f"Procesados: "
                f"{resultado['procesados']} | "
                f"Total: "
                f"{resultado['total_cargados']} | "
                f"Errores: "
                f"{resultado['total_errores']}"
            )

            time.sleep(
                INTERVALO_POLLING_SEGUNDOS
            )

        self.cargador.cerrar()


if __name__ == "__main__":

    servicio = ServicioLoad()

    servicio.ejecutar()