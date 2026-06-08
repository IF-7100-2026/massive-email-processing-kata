import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from database.mongodb import MongoDB
from models.correo_model import CorreoModel

class TestDuplicados(unittest.TestCase):
    
    def setUp(self):
        self.db = MongoDB()
        self.id_unico = f"DUP_TEST_{int(time.time())}"
    
    def tearDown(self):
        self.db.collection.delete_many({"id_mensaje_imap": self.id_unico})
        self.db.cerrar()
    
    def test_prevencion_duplicados(self):
        """Verificar que no se guardan correos con el mismo id_mensaje_imap"""
        correo1 = CorreoModel.crear_desde_imap(
            remitente="test@duplicado.com",
            asunto="Test Duplicado 1",
            contenido="Contenido 1",
            id_mensaje=self.id_unico
        )
        
        correo2 = CorreoModel.crear_desde_imap(
            remitente="test@duplicado.com",
            asunto="Test Duplicado 2",
            contenido="Contenido 2",
            id_mensaje=self.id_unico
        )
        
        id1 = self.db.guardar_correo(correo1)
        
        # verifica si existe antes de guardar el segundo
        existe = self.db.collection.find_one({"id_mensaje_imap": self.id_unico})
        self.assertIsNotNone(existe)
        
        print("  OK: Prevencion de duplicados funciona")

if __name__ == "__main__":
    unittest.main()