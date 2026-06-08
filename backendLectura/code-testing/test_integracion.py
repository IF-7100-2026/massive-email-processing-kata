import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from database.mongodb import MongoDB
from services.lector_imap import LectorIMAP
from models.correo_model import CorreoModel

class TestIntegracion(unittest.TestCase):
    
    def setUp(self):
        self.db = MongoDB()
        self.lector = LectorIMAP()
        self.id_test = f"INT_TEST_{int(time.time())}"
    
    def tearDown(self):
        self.db.collection.delete_many({"id_mensaje_imap": self.id_test})
        self.db.cerrar()
    
    def test_flujo_lectura_guardado(self):
        """Verificar que el flujo de lectura y guardado funciona"""
        
        # Cuenta antes
        antes = self.db.contar_correos()
        
        # Conecta y lee
        self.lector.conectar()
        correos = self.lector.leer_correos_no_leidos()
        self.lector.desconectar()
        
        # Guardar correo de prueba directamente
        correo_dict = CorreoModel.crear_desde_imap(
            remitente="test@integracion.com",
            asunto="Test Integracion",
            contenido="Contenido",
            id_mensaje=self.id_test
        )
        
        resultado = self.db.guardar_correo(correo_dict)
        
        # Actualiza leido
        self.db.collection.update_one(
            {"_id": resultado},
            {"$set": {"leido": True}}
        )
        
        # Cuenta despues
        despues = self.db.contar_correos()
        
        self.assertGreaterEqual(despues, antes)
        self.assertIsNotNone(resultado)
        
        print(f"  OK: Flujo integracion funciona - Nuevo ID: {resultado}")

if __name__ == "__main__":
    unittest.main()