import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from services.lector_imap import LectorIMAP

class TestLecturaIMAP(unittest.TestCase):
    
    def setUp(self):
        self.lector = LectorIMAP()
        self.lector.conectar()
    
    def tearDown(self):
        self.lector.desconectar()
    
    def test_leer_correos_no_leidos(self):
        """Verificar que se pueden leer correos no leidos"""
        correos = self.lector.leer_correos_no_leidos()
        self.assertIsInstance(correos, list)
        print(f"  OK: Lectura IMAP - {len(correos)} correos encontrados")
    
    def test_estructura_correo(self):
        """Verificar que cada correo tiene la estructura correcta"""
        correos = self.lector.leer_correos_no_leidos()
        
        if len(correos) > 0:
            primer_correo = correos[0]
            campos = ["id", "remitente", "asunto", "contenido"]
            for campo in campos:
                self.assertIn(campo, primer_correo)
            print("  OK: Estructura del correo correcta")
        else:
            print("  OK: No hay correos para verificar estructura")
    
    def test_limpiar_texto(self):
        """Verificar que la funcion limpiar_texto funciona"""
        texto_limpio = self.lector.limpiar_texto("  texto con espacios  ")
        self.assertEqual(texto_limpio, "texto con espacios")
        self.assertEqual(self.lector.limpiar_texto(None), "")
        print("  OK: Funcion limpiar_texto correcta")

if __name__ == "__main__":
    unittest.main()