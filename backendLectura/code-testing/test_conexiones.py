import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from database.mongodb import MongoDB
from services.lector_imap import LectorIMAP

class TestConexiones(unittest.TestCase):
    
    def test_conexion_mongodb(self):
        """Verificar que la conexion a MongoDB es exitosa"""
        try:
            db = MongoDB()
            count = db.contar_correos()
            self.assertIsNotNone(count)
            self.assertIsInstance(count, int)
            db.cerrar()
            print("  OK: Conexion MongoDB exitosa")
        except Exception as e:
            self.fail(f"Error de conexion MongoDB: {str(e)}")
    
    def test_conexion_imap(self):
        """Verificar que la conexion IMAP es exitosa"""
        try:
            lector = LectorIMAP()
            lector.conectar()
            self.assertIsNotNone(lector.mail)
            lector.desconectar()
            print("  OK: Conexion IMAP exitosa")

        except Exception as e:
            self.fail(f"Error de conexion IMAP: {str(e)}")

if __name__ == "__main__":
    unittest.main()