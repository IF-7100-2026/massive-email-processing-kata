from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

from loader import CargadorCorreos


def crear_cargador_sin_infraestructura():
    cargador = CargadorCorreos.__new__(CargadorCorreos)

    cargador.mongo = MagicMock()
    cargador.enviador = MagicMock()
    cargador.cola_humana = MagicMock()
    cargador.tamano_lote = 10
    cargador.cargados = 0
    cargador.errores = 0

    return cargador


def crear_documento(categoria):
    return {
        "_id": "123",
        "remitente": "cliente@test.com",
        "asunto": "Prueba",
        "contenido": "Mensaje de prueba",
        "id_mensaje_imap": "575",
        "fecha_extraccion": datetime.now(timezone.utc) - timedelta(seconds=2),
        "clasificado": True,
        "categoria": categoria
    }


def test_queja_va_a_cola_humana():
    cargador = crear_cargador_sin_infraestructura()

    destino = cargador._obtener_destino("Queja")

    assert destino == "Cola de atención humana"


def test_atencion_humana_va_a_cola_humana():
    cargador = crear_cargador_sin_infraestructura()

    destino = cargador._obtener_destino("Atención humana")

    assert destino == "Cola de atención humana"


def test_categoria_normal_va_a_respuesta_automatica():
    cargador = crear_cargador_sin_infraestructura()

    destino = cargador._obtener_destino("Consulta")

    assert destino == "Respuesta automática"


def test_queja_guarda_en_csv_y_envia_respuesta():
    cargador = crear_cargador_sin_infraestructura()
    documento = crear_documento("Queja")

    cargador.enviador.enviar_respuesta.return_value = True
    cargador.mongo.actualizar_load.return_value = True

    resultado = cargador.cargar_documento(documento)

    assert resultado is True

    cargador.cola_humana.guardar.assert_called_once_with(
        documento,
        "Queja"
    )

    cargador.enviador.enviar_respuesta.assert_called_once_with(
        destinatario="cliente@test.com",
        asunto_original="Prueba",
        categoria="Queja",
        destino="Cola de atención humana"
    )

    cargador.mongo.actualizar_load.assert_called_once()

    datos_actualizacion = cargador.mongo.actualizar_load.call_args.kwargs

    assert datos_actualizacion["destino"] == "Cola de atención humana"
    assert datos_actualizacion["respuesta_enviada"] is True


def test_consulta_no_guarda_csv_pero_envia_respuesta():
    cargador = crear_cargador_sin_infraestructura()
    documento = crear_documento("Consulta")

    cargador.enviador.enviar_respuesta.return_value = True
    cargador.mongo.actualizar_load.return_value = True

    resultado = cargador.cargar_documento(documento)

    assert resultado is True

    cargador.cola_humana.guardar.assert_not_called()

    cargador.enviador.enviar_respuesta.assert_called_once_with(
        destinatario="cliente@test.com",
        asunto_original="Prueba",
        categoria="Consulta",
        destino="Respuesta automática"
    )

    datos_actualizacion = cargador.mongo.actualizar_load.call_args.kwargs

    assert datos_actualizacion["destino"] == "Respuesta automática"
    assert datos_actualizacion["respuesta_enviada"] is True


def test_procesar_lote_procesa_documentos_pendientes():
    cargador = crear_cargador_sin_infraestructura()

    documento_1 = crear_documento("Queja")
    documento_2 = crear_documento("Consulta")

    cargador.mongo.obtener_documentos_clasificados.return_value = [
        documento_1,
        documento_2
    ]

    cargador.enviador.enviar_respuesta.return_value = True
    cargador.mongo.actualizar_load.return_value = True

    procesados = cargador.procesar_lote()

    assert procesados == 2
    assert cargador.enviador.enviar_respuesta.call_count == 2
    assert cargador.mongo.actualizar_load.call_count == 2
    assert cargador.cola_humana.guardar.call_count == 1


def test_tiempo_procesamiento_es_numerico():
    cargador = crear_cargador_sin_infraestructura()
    documento = crear_documento("Consulta")

    tiempo = cargador._calcular_tiempo_procesamiento(documento)

    assert isinstance(tiempo, float)
    assert tiempo >= 0