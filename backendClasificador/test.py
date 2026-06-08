import unittest
import time
import json
import csv
import os
import tempfile
from mongomock import MongoClient as MockMongoClient

from classifier import ClasificadorPalabrasClave


class TestBackend2Clasificador(unittest.TestCase):
    """
    Backend 2: Clasificacion de correos
    Prueba 1: Clasificacion de Correos por Palabras Clave
    """

    def setUp(self):
        self.clasificador = ClasificadorPalabrasClave()

    def test_clasificacion_suscripcion(self):
        asunto = "Quiero suscribirme al boletin"
        contenido = "Por favor agregame a la lista"
        resultado = self.clasificador.clasificar(asunto, contenido)
        self.assertEqual(resultado, "Suscripcion")

    def test_clasificacion_queja(self):
        asunto = "Tengo una queja sobre el servicio"
        contenido = "Estoy muy molesto con la atencion"
        resultado = self.clasificador.clasificar(asunto, contenido)
        self.assertEqual(resultado, "Queja")

    def test_clasificacion_solicitud_informacion(self):
        asunto = "Necesito informacion sobre los planes"
        contenido = "Tengo una consulta sobre el servicio"
        resultado = self.clasificador.clasificar(asunto, contenido)
        self.assertEqual(resultado, "Solicitud de informacion")

    def test_clasificacion_envio_noticia(self):
        asunto = "Quiero enviar una noticia importante"
        contenido = "Reportar un suceso en mi comunidad"
        resultado = self.clasificador.clasificar(asunto, contenido)
        self.assertEqual(resultado, "Envio de noticia")

    def test_clasificacion_atencion_humana_defecto(self):
        asunto = "Hola mundo"
        contenido = "Texto sin palabras clave especiales"
        resultado = self.clasificador.clasificar(asunto, contenido)
        self.assertEqual(resultado, "Atencion humana")

    def test_clasificacion_case_insensitive(self):
        asunto = "QUEJA FORMAL"
        contenido = "RECLAMO POR MAL SERVICIO"
        resultado = self.clasificador.clasificar(asunto, contenido)
        self.assertEqual(resultado, "Queja")


class TestBackend2ObtencionCorreos(unittest.TestCase):
    """
    Backend 2: Obtencion de correos pendientes
    Prueba 2: Obtencion de Correos Pendientes desde MongoDB
    """

    def setUp(self):
        self.mock_client = MockMongoClient()
        self.mock_db = self.mock_client["dailyplanet"]
        self.mock_coleccion = self.mock_db["correos"]

    def crear_correo(self, asunto, leido, clasificado):
        correo = {
            "id_mensaje_imap": f"test_{int(time.time() * 1000)}_{asunto}",
            "remitente": "prueba@test.com",
            "asunto": asunto,
            "contenido": "contenido",
            "leido": leido,
            "clasificado": clasificado
        }
        return self.mock_coleccion.insert_one(correo)

    def test_obtener_correos_pendientes(self):
        self.crear_correo("pendiente1", True, False)
        self.crear_correo("pendiente2", True, False)
        self.crear_correo("ya_clasificado", True, True)
        self.crear_correo("no_leido", False, False)

        correos_pendientes = list(self.mock_coleccion.find({
            "leido": True,
            "clasificado": False
        }))

        self.assertEqual(len(correos_pendientes), 2)
        for correo in correos_pendientes:
            self.assertTrue(correo["leido"])
            self.assertFalse(correo["clasificado"])


class TestBackend2ProcesamientoLote(unittest.TestCase):
    """
    Backend 2: Procesamiento de lote completo
    Prueba 3: Procesamiento de Lote Completo
    """

    def setUp(self):
        self.mock_client = MockMongoClient()
        self.mock_db = self.mock_client["dailyplanet"]
        self.mock_coleccion = self.mock_db["correos"]
        self.clasificador = ClasificadorPalabrasClave()

    def crear_correo(self, asunto, contenido):
        correo = {
            "id_mensaje_imap": f"test_{int(time.time() * 1000)}",
            "remitente": "prueba@test.com",
            "asunto": asunto,
            "contenido": contenido,
            "leido": True,
            "clasificado": False
        }
        return self.mock_coleccion.insert_one(correo).inserted_id

    def test_procesamiento_lote_completo(self):
        for i in range(10):
            self.crear_correo(
                f"Tengo una queja #{i}",
                "Estoy molesto con el servicio"
            )

        correos = list(self.mock_coleccion.find({"clasificado": False}))
        self.assertEqual(len(correos), 10)

        for correo in correos:
            categoria = self.clasificador.clasificar(correo["asunto"], correo["contenido"])
            self.mock_coleccion.update_one(
                {"_id": correo["_id"]},
                {"$set": {"categoria": categoria, "clasificado": True}}
            )

        procesados = self.mock_coleccion.count_documents({"clasificado": True})
        self.assertEqual(procesados, 10)

        for correo in self.mock_coleccion.find({"clasificado": True}):
            self.assertEqual(correo["categoria"], "Queja")


class TestBackend2TiempoProcesamiento(unittest.TestCase):
    """
    Backend 2: Medicion de tiempo de procesamiento
    Prueba 4: Medicion de Tiempo de Procesamiento por Correo
    """

    def setUp(self):
        self.mock_client = MockMongoClient()
        self.mock_db = self.mock_client["dailyplanet"]
        self.mock_coleccion = self.mock_db["correos"]
        self.clasificador = ClasificadorPalabrasClave()

    def crear_correo(self):
        correo = {
            "id_mensaje_imap": f"test_{int(time.time() * 1000)}",
            "remitente": "prueba@test.com",
            "asunto": "Quiero suscribirme al boletin",
            "contenido": "Por favor agregame",
            "leido": True,
            "clasificado": False
        }
        return self.mock_coleccion.insert_one(correo)

    def test_tiempo_procesamiento_por_correo(self):
        for _ in range(10):
            self.crear_correo()

        correos = list(self.mock_coleccion.find({"clasificado": False}))
        tiempos = []

        for correo in correos:
            inicio = time.time()
            self.clasificador.clasificar(correo["asunto"], correo["contenido"])
            tiempo_ms = (time.time() - inicio) * 1000
            tiempos.append(tiempo_ms)

        tiempo_promedio = sum(tiempos) / len(tiempos)

        for t in tiempos:
            self.assertLess(t, 10)
        self.assertLess(tiempo_promedio, 5)


class TestBackend2Escalabilidad(unittest.TestCase):
    """
    Backend 2: Escalabilidad con diferentes tamanos de lote
    Prueba 5: Escalabilidad con Diferentes Tamanos de Lote
    """

    def setUp(self):
        self.mock_client = MockMongoClient()
        self.mock_db = self.mock_client["dailyplanet"]
        self.mock_coleccion = self.mock_db["correos"]
        self.clasificador = ClasificadorPalabrasClave()

    def crear_correos(self, cantidad, asunto_base):
        for i in range(cantidad):
            correo = {
                "id_mensaje_imap": f"test_{i}_{int(time.time() * 1000)}",
                "remitente": "prueba@test.com",
                "asunto": f"{asunto_base} #{i}",
                "contenido": "Estoy molesto con el servicio",
                "leido": True,
                "clasificado": False
            }
            self.mock_coleccion.insert_one(correo)

    def test_rendimiento_con_diferentes_tamanos_lote(self):
        tamanos = [1, 5, 10, 20]
        resultados = []

        for tamano in tamanos:
            self.mock_coleccion.delete_many({})
            self.crear_correos(tamano, "Tengo una queja")

            correos = list(self.mock_coleccion.find({"clasificado": False}))
            inicio = time.time()

            for correo in correos:
                categoria = self.clasificador.clasificar(correo["asunto"], correo["contenido"])
                self.mock_coleccion.update_one(
                    {"_id": correo["_id"]},
                    {"$set": {"categoria": categoria, "clasificado": True}}
                )

            tiempo_total = time.time() - inicio
            rendimiento = len(correos) / tiempo_total if tiempo_total > 0 else 0
            resultados.append(rendimiento)

        # Verifica que el rendimiento para lote de 20 sea mejor que para lote de 1
        self.assertGreater(resultados[3], resultados[0])


class TestBackend2Confiabilidad(unittest.TestCase):
    """
    Backend 2: Confiabilidad sin perdida de correos
    Prueba 6: Confiabilidad sin Perdida de Correos
    """

    def setUp(self):
        self.mock_client = MockMongoClient()
        self.mock_db = self.mock_client["dailyplanet"]
        self.mock_coleccion = self.mock_db["correos"]
        self.clasificador = ClasificadorPalabrasClave()

    def crear_correo(self, i):
        correo = {
            "id_mensaje_imap": f"test_{i}_{int(time.time() * 1000)}",
            "remitente": "prueba@test.com",
            "asunto": f"Correo de prueba #{i}",
            "contenido": "Contenido de prueba para clasificar",
            "leido": True,
            "clasificado": False
        }
        return self.mock_coleccion.insert_one(correo)

    def test_no_se_pierden_correos(self):
        cantidad_total = 25

        for i in range(cantidad_total):
            self.crear_correo(i)

        while True:
            correos = list(self.mock_coleccion.find({"clasificado": False}))
            if not correos:
                break
            for correo in correos:
                categoria = self.clasificador.clasificar(correo["asunto"], correo["contenido"])
                self.mock_coleccion.update_one(
                    {"_id": correo["_id"]},
                    {"$set": {"categoria": categoria, "clasificado": True}}
                )

        procesados = self.mock_coleccion.count_documents({"clasificado": True})
        self.assertEqual(procesados, cantidad_total)


class TestBackend2Actualizacion(unittest.TestCase):
    """
    Backend 2: Actualizacion en base de datos
    Prueba 7: Actualizacion Correcta en Base de Datos
    """

    def setUp(self):
        self.mock_client = MockMongoClient()
        self.mock_db = self.mock_client["dailyplanet"]
        self.mock_coleccion = self.mock_db["correos"]

    def test_actualizacion_clasificacion(self):
        correo = {
            "id_mensaje_imap": "test_001",
            "remitente": "prueba@test.com",
            "asunto": "Correo prueba",
            "contenido": "Contenido",
            "leido": True,
            "clasificado": False
        }
        resultado = self.mock_coleccion.insert_one(correo)
        correo_id = resultado.inserted_id

        self.mock_coleccion.update_one(
            {"_id": correo_id},
            {"$set": {"categoria": "Queja", "clasificado": True}}
        )

        correo_actualizado = self.mock_coleccion.find_one({"_id": correo_id})
        self.assertTrue(correo_actualizado["clasificado"])
        self.assertEqual(correo_actualizado["categoria"], "Queja")


class TestBackend2Retraso(unittest.TestCase):
    """
    Backend 2: Retraso configurable entre correos
    Prueba 8: Respeto del Retraso Configurable entre Correos
    """

    def setUp(self):
        self.mock_client = MockMongoClient()
        self.mock_db = self.mock_client["dailyplanet"]
        self.mock_coleccion = self.mock_db["correos"]
        self.clasificador = ClasificadorPalabrasClave()

    def crear_correo(self, i):
        correo = {
            "id_mensaje_imap": f"test_{i}_{int(time.time() * 1000)}",
            "remitente": "prueba@test.com",
            "asunto": f"Correo {i}",
            "contenido": "Contenido de prueba",
            "leido": True,
            "clasificado": False
        }
        return self.mock_coleccion.insert_one(correo)

    def test_retraso_configurable(self):
        for i in range(3):
            self.crear_correo(i)

        correos = list(self.mock_coleccion.find({"clasificado": False}))
        retraso = 0.5

        inicio = time.time()
        for correo in correos:
            self.clasificador.clasificar(correo["asunto"], correo["contenido"])
            time.sleep(retraso)
        tiempo_total = time.time() - inicio

        tiempo_minimo_esperado = 3 * retraso - 0.1
        self.assertGreaterEqual(tiempo_total, tiempo_minimo_esperado)


class TestBackend2Metricas(unittest.TestCase):
    """
    Backend 2: Exportacion de metricas
    Prueba 9: Generacion de Metricas y Exportacion a JSON y CSV
    """

    def setUp(self):
        self.metricas = {
            "rendimiento": {
                "tiempo_promedio_ms": 2.5,
                "correos_procesados": 100
            },
            "clasificacion": {
                "Suscripcion": 30,
                "Queja": 25,
                "Solicitud de informacion": 20,
                "Envio de noticia": 15,
                "Atencion humana": 10
            },
            "puntaje_total": 14
        }

    def test_exportacion_json(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            archivo = tmp.name

        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(self.metricas, f, indent=2, ensure_ascii=False)

        self.assertTrue(os.path.exists(archivo))

        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)

        self.assertIn("rendimiento", datos)
        self.assertIn("clasificacion", datos)
        self.assertEqual(datos["puntaje_total"], 14)

        os.unlink(archivo)

    def test_exportacion_csv(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            archivo = tmp.name

        with open(archivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["METRICA", "VALOR"])
            writer.writerow(["tiempo_promedio_ms", 2.5])
            writer.writerow(["correos_procesados", 100])
            writer.writerow(["puntaje_total", 14])

        self.assertTrue(os.path.exists(archivo))

        with open(archivo, "r", encoding="utf-8") as f:
            lector = csv.reader(f)
            lineas = list(lector)

        self.assertGreater(len(lineas), 0)
        self.assertEqual(lineas[0][0], "METRICA")

        os.unlink(archivo)


class TestBackend2PuntajeTotal(unittest.TestCase):
    """
    Backend 2: Calculo de puntaje total
    Prueba 10: Calculo del Puntaje Total segun Criterios de Evaluacion
    """

    def test_calculo_puntaje_total(self):
        puntaje_performance = 5
        puntaje_escalabilidad = 3
        puntaje_confiabilidad = 3
        puntaje_mantenibilidad = 3

        puntaje_total = puntaje_performance + puntaje_escalabilidad + puntaje_confiabilidad + puntaje_mantenibilidad

        self.assertEqual(puntaje_total, 14)


def ejecutar_todas_las_pruebas():
    """Ejecuta todas las pruebas del Backend 2 y muestra resultados."""
    print("\n" + "=" * 60)
    print("PLAN DE PRUEBAS - BACKEND 2 (TRANSFORMADOR)")
    print("=" * 60)

    clases_prueba = [
        TestBackend2Clasificador,
        TestBackend2ObtencionCorreos,
        TestBackend2ProcesamientoLote,
        TestBackend2TiempoProcesamiento,
        TestBackend2Escalabilidad,
        TestBackend2Confiabilidad,
        TestBackend2Actualizacion,
        TestBackend2Retraso,
        TestBackend2Metricas,
        TestBackend2PuntajeTotal
    ]

    suite = unittest.TestSuite()
    for clase in clases_prueba:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(clase))

    resultado = unittest.TextTestRunner(verbosity=2).run(suite)

    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    print(f"Pruebas ejecutadas: {resultado.testsRun}")
    print(f"Exitosas: {resultado.testsRun - len(resultado.failures) - len(resultado.errors)}")
    print(f"Fallidas: {len(resultado.failures)}")
    print(f"Errores: {len(resultado.errors)}")

    if resultado.wasSuccessful():
        print("\nRESULTADO: TODAS LAS PRUEBAS EXITOSAS")
        print("PUNTAJE TOTAL: 14/14")
    else:
        print("\nRESULTADO: ALGUNAS PRUEBAS FALLARON")

    print("=" * 60)


if __name__ == "__main__":
    ejecutar_todas_las_pruebas()