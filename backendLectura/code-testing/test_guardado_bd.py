import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from database.mongodb import MongoDB
from models.correo_model import CorreoModel

class TestGuardadoBD(unittest.TestCase):
    
    def setUp(self):
        self.db = MongoDB()
        self.id_test = f"TEST_{int(time.time())}"
    
    def tearDown(self):
        # Limpia correos de prueba
        self.db.collection.delete_many({"id_mensaje_imap": {"$regex": "TEST_"}})
        self.db.cerrar()
    
    def test_guardar_correo(self):
        """Verificar que se puede guardar un correo en MongoDB"""
        correo = CorreoModel.crear_desde_imap(
            remitente="test@unitario.com",
            asunto="Prueba Unitaria",
            contenido="Contenido de prueba",
            id_mensaje=self.id_test
        )
        
        resultado = self.db.guardar_correo(correo)
        self.assertIsNotNone(resultado)
        
        # Verificar que existe
        existe = self.db.collection.find_one({"_id": resultado})
        self.assertIsNotNone(existe)
        self.assertEqual(existe["remitente"], "test@unitario.com")
        
        print(f"  OK: Correo guardado con ID {resultado}")
    
    def test_contar_correos(self):
        """Verifica que la funcion contar_correos funciona"""
        count = self.db.contar_correos()
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)
        print(f"  OK: Total correos en BD: {count}")

if __name__ == "__main__":
    unittest.main()