import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    def __init__(self):
        uri = os.getenv("MONGO_URI")
        db_name = os.getenv("DB_NAME")
        collection_name = os.getenv("COLLECTION_NAME")
        
        print(f"Conectando a MongoDB: {db_name}.{collection_name}")
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        print("Conexion a MongoDB exitosa")
    
    def guardar_correo(self, correo_data):
        resultado = self.collection.insert_one(correo_data)
        return resultado.inserted_id
    
    def obtener_no_procesados(self):
        return self.collection.find({"procesado": False})
    
    def obtener_todos(self):
        return self.collection.find()
    
    def contar_correos(self):
        return self.collection.count_documents({})
    
    def cerrar(self):
        self.client.close()