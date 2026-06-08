from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import MONGO_URI, MONGO_DB, MONGO_COLECCION


class ClienteMongo:
    """Cliente de MongoDB con manejo de conexion y operaciones."""

    def __init__(self):
        self.cliente = None
        self.base_datos = None
        self.coleccion = None
        self._conectar()

    def _conectar(self):
        """Establece conexion con MongoDB."""
        try:
            self.cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            self.cliente.admin.command('ping')
            self.base_datos = self.cliente[MONGO_DB]
            self.coleccion = self.base_datos[MONGO_COLECCION]
            self._asegurar_indices()
            print("Conexion a MongoDB establecida correctamente")
        except ConnectionFailure as error:
            raise ConnectionError(f"Error al conectar a MongoDB: {error}")

    def _asegurar_indices(self):
        """Crea indices para optimizar las consultas de consulta."""
        self.coleccion.create_index([("leido", 1), ("clasificado", 1)])

    def obtener_correos_pendientes(self, limite: int):
        """Obtiene los correos que necesitan ser clasificados."""
        consulta = {
            "leido": True,
            "clasificado": False
        }
        return list(self.coleccion.find(consulta).limit(limite))

    def actualizar_clasificacion(self, id_correo, categoria: str) -> bool:
        """Actualiza un correo con el resultado de la clasificacion."""
        resultado = self.coleccion.update_one(
            {"_id": id_correo},
            {
                "$set": {
                    "categoria": categoria,
                    "clasificado": True
                }
            }
        )
        return resultado.modified_count > 0

    def cerrar(self):
        """Cierra la conexion a la base de datos."""
        if self.cliente:
            self.cliente.close()
            print("Conexion a MongoDB cerrada")