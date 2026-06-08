# email_sender.py
import smtplib
from email.message import EmailMessage

from config import (
    EMAIL_USER,
    EMAIL_PASSWORD,
    SMTP_SERVER,
    SMTP_PORT
)


class EnviadorCorreo:

    def enviar_respuesta(
        self,
        destinatario,
        asunto_original,
        categoria,
        destino
    ):

        mensaje = EmailMessage()

        mensaje["From"] = EMAIL_USER
        mensaje["To"] = destinatario

        mensaje["Subject"] = (
            f"Respuesta a: {asunto_original}"
        )

        mensaje.set_content(
            self._generar_cuerpo(
                categoria,
                destino
            )
        )

        with smtplib.SMTP(
            SMTP_SERVER,
            SMTP_PORT
        ) as servidor:

            servidor.starttls()

            servidor.login(
                EMAIL_USER,
                EMAIL_PASSWORD
            )

            servidor.send_message(
                mensaje
            )

        return True

    def _generar_cuerpo(
        self,
        categoria,
        destino
    ):

        if destino == "Cola de atención humana":

            return (
                "Hola,\n\n"
                "Tu caso fue enviado "
                "a revisión humana.\n\n"
                "Gracias por contactar "
                "a Daily Planet."
            )

        return (
            "Hola,\n\n"
            f"Tu solicitud fue "
            f"clasificada como: "
            f"{categoria}.\n\n"
            "Gracias por contactar "
            "a Daily Planet.\n\n"
            "Este es un mensaje automático."
        )