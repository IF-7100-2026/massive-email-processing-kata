from datetime import datetime, timezone

class CorreoModel:
    @staticmethod
    def crear_desde_imap(remitente, asunto, contenido, id_mensaje):
        return {
            "remitente": remitente,
            "asunto": asunto,
            "contenido": contenido,
            "id_mensaje_imap": str(id_mensaje),
            "fecha_extraccion": datetime.now(timezone.utc),  # UTC desde el inicio
            "leido": False,
            "tiempo_final": None,
            "tiempo_procesamiento": None,
            "procesado": False,
            "clasificado": False,
            "categoria": None,
            "destino": None,
            "respuesta_enviada": False,
            "errores": []
        }