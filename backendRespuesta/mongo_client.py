# mongo_client.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from config import (
    MONGO_URI,
    MONGO_DB,
    MONGO_COLECCION
)


class ClienteMongo:

    def __init__(self):

        self.cliente = None
        self.coleccion = None

        self._conectar()

    def _conectar(self):

        try:

            self.cliente = MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=5000
            )

            self.cliente.admin.command(
                "ping"
            )

            db = self.cliente[
                MONGO_DB
            ]

            self.coleccion = db[
                MONGO_COLECCION
            ]

            self._crear_indices()

            print(
                "Conexión a MongoDB establecida"
            )

        except ConnectionFailure as error:

            raise ConnectionError(
                f"Error MongoDB: {error}"
            )

    def _crear_indices(self):

        self.coleccion.create_index([
            ("clasificado", 1)
        ])

        self.coleccion.create_index([
            ("procesado", 1)
        ])

    def obtener_documentos_clasificados(
        self,
        limite: int
    ):

        consulta = {
            "clasificado": True,
            "$or": [
                {
                    "procesado": False
                },
                {
                    "procesado": {
                        "$exists": False
                    }
                }
            ]
        }

        return list(
            self.coleccion.find(
                consulta
            ).limit(limite)
        )

    def actualizar_load(
        self,
        id_documento,
        destino,
        tiempo_final,
        tiempo_procesamiento,
        respuesta_enviada
    ):

        resultado = (
            self.coleccion.update_one(
                {
                    "_id": id_documento
                },
                {
                    "$set": {
                        "destino": destino,

                        "tiempo_final":
                        tiempo_final,

                        "tiempo_procesamiento":
                        tiempo_procesamiento,

                        "procesado": True,

                        "respuesta_enviada":
                        respuesta_enviada
                    }
                }
            )
        )

        return (
            resultado.modified_count > 0
        )

    def cerrar(self):

        if self.cliente:
            self.cliente.close()