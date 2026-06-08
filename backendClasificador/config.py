import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "")
MONGO_DB = os.getenv("MONGO_DB", "dailyplanet")
MONGO_COLECCION = os.getenv("MONGO_COLECCION", "correos")
INTERVALO_POLLING_SEGUNDOS = int(os.getenv("INTERVALO_POLLING_SEGUNDOS", "10"))
RETRASO_PROCESAMIENTO_SEGUNDOS = float(os.getenv("RETRASO_PROCESAMIENTO_SEGUNDOS", "1"))
TAMANO_LOTE = int(os.getenv("TAMANO_LOTE", "10"))