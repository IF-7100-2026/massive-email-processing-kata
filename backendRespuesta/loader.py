# loader.py
from datetime import datetime, timezone
from typing import Dict, Any
import unicodedata

from mongo_client import ClienteMongo
from email_sender import EnviadorCorreo
from cola_humana_writer import EscritorColaHumana
from metricas_writer import EscritorMetricas

class CargadorCorreos:

    DESTINO_HUMANO = "Cola de atención humana"
    DESTINO_AUTOMATICO = "Respuesta automática"

    def __init__(self, tamano_lote: int = 10):
        self.mongo = ClienteMongo()
        self.enviador = EnviadorCorreo()
        self.cola_humana = EscritorColaHumana()
        self.tamano_lote = tamano_lote
        self.cargados = 0
        self.errores = 0
        self.metricas = EscritorMetricas()

    def _normalizar(self, texto: str) -> str:
        texto = str(texto).strip().lower()
        texto = unicodedata.normalize("NFD", texto)

        return "".join(
            caracter for caracter in texto
            if unicodedata.category(caracter) != "Mn"
        )

    def _obtener_destino(self, categoria: str) -> str:
        categoria_normalizada = self._normalizar(categoria)

        if categoria_normalizada in ["atencion humana", "queja"]:
            return self.DESTINO_HUMANO

        return self.DESTINO_AUTOMATICO

    def _obtener_tiempo_final(self):
        return datetime.now(timezone.utc)

    def _calcular_tiempo_procesamiento(self, documento):
        inicio = documento["fecha_extraccion"]

        if inicio.tzinfo is None:
            inicio = inicio.replace(tzinfo=timezone.utc)

        ahora = datetime.now(timezone.utc)
        tiempo_total = (ahora - inicio).total_seconds()

        return round(tiempo_total, 4)

    def cargar_documento(self, documento: Dict[str, Any]) -> bool:
        try:
            categoria = documento.get("categoria", "")
            destino = self._obtener_destino(categoria)

            print("CATEGORIA:", categoria)
            print("DESTINO:", destino)

            tiempo_final = self._obtener_tiempo_final()

            tiempo_procesamiento = self._calcular_tiempo_procesamiento(
                documento
            )

            self.metricas.guardar(
                documento=documento,
                categoria=categoria,
                destino=destino,
                tiempo_procesamiento=tiempo_procesamiento
            )

            if destino == self.DESTINO_HUMANO:
                self.cola_humana.guardar(
                    documento,
                    categoria
                )

            respuesta_enviada = self.enviador.enviar_respuesta(
                destinatario=documento["remitente"],
                asunto_original=documento["asunto"],
                categoria=categoria,
                destino=destino
            )

            actualizado = self.mongo.actualizar_load(
                id_documento=documento["_id"],
                destino=destino,
                tiempo_final=tiempo_final,
                tiempo_procesamiento=tiempo_procesamiento,
                respuesta_enviada=respuesta_enviada
            )

            if actualizado:
                self.cargados += 1
                print(f"LOAD aplicado: {documento['_id']} -> {destino}")
            else:
                self.errores += 1
                print(f"No se pudo actualizar: {documento['_id']}")

            return actualizado

        except Exception as error:
            self.errores += 1
            print(f"Error procesando: {error}")
            return False

    def procesar_lote(self) -> int:
        documentos = self.mongo.obtener_documentos_clasificados(
            self.tamano_lote
        )

        if not documentos:
            return 0

        procesados = 0

        for documento in documentos:
            if self.cargar_documento(documento):
                procesados += 1

        return procesados

    def ejecutar_una_vez(self):
        procesados = self.procesar_lote()

        return {
            "procesados": procesados,
            "total_cargados": self.cargados,
            "total_errores": self.errores
        }

    def cerrar(self):
        self.mongo.cerrar()