import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import time

def run_all_tests():
    print("=" * 60)
    print("EJECUTANDO TODAS LAS PRUEBAS UNITARIAS")
    print("Backend 1 - Lectura, Envio y Guardado")
    print("=" * 60)
    print()
    
    inicio = time.time()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    from test_conexiones import TestConexiones
    from test_lectura_imap import TestLecturaIMAP
    from test_guardado_bd import TestGuardadoBD
    from test_duplicados import TestDuplicados
    from test_integracion import TestIntegracion
    
    print()
    suite.addTests(loader.loadTestsFromTestCase(TestConexiones))
    suite.addTests(loader.loadTestsFromTestCase(TestLecturaIMAP))
    suite.addTests(loader.loadTestsFromTestCase(TestGuardadoBD))
    suite.addTests(loader.loadTestsFromTestCase(TestDuplicados))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegracion))
    
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    fin = time.time()
    
    print()
    print("=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"Pruebas ejecutadas: {resultado.testsRun}")
    print(f"Exitosas: {resultado.testsRun - len(resultado.failures) - len(resultado.errors)}")
    print(f"Fallidas: {len(resultado.failures)}")
    print(f"Errores: {len(resultado.errors)}")
    print(f"Tiempo total: {round(fin - inicio, 2)} segundos")
    
    if resultado.wasSuccessful():
        print("\nRESULTADO: TODAS LAS PRUEBAS PASARON")
    else:
        print("\nRESULTADO: HAY PRUEBAS FALLIDAS")
    
    return resultado

if __name__ == "__main__":
    run_all_tests()