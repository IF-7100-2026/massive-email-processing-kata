import os
import smtplib
import time
from email.message import EmailMessage
from flask import Flask, render_template, request
from dotenv import load_dotenv
import random

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")
)

SIMULADOR_EMAIL = os.getenv("SIMULADOR_EMAIL")
SIMULADOR_PASSWORD = os.getenv("SIMULADOR_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

correos_prueba = [
    {
        "asunto": "Quiero suscribirme al boletin",
        "contenido": "Hola, deseo suscribirme al boletin de Daily Planet."
    },
    {
        "asunto": "Tengo una queja",
        "contenido": "Buenas, tengo una queja sobre el servicio recibido."
    },
    {
        "asunto": "Necesito informacion",
        "contenido": "Hola, necesito informacion sobre las noticias y servicios."
    },
    {
        "asunto": "Quiero enviar una noticia",
        "contenido": "Hola, quiero reportar una noticia importante de mi comunidad."
    },
    {
        "asunto": "Consulta general",
        "contenido": "Hola, tengo una duda general sobre Daily Planet."
    }
]

def enviar_correo(destino, asunto, contenido):
    mensaje = EmailMessage()
    mensaje["From"] = SIMULADOR_EMAIL
    mensaje["To"] = destino
    mensaje["Subject"] = asunto
    mensaje.set_content(contenido)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as servidor:
        servidor.starttls()
        servidor.login(SIMULADOR_EMAIL, SIMULADOR_PASSWORD)
        servidor.send_message(mensaje)


@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    enviados = []

    if request.method == "POST":
        destino = request.form["destino"]
        cantidad = int(request.form["cantidad"])
        pausa = float(request.form["pausa"])

        inicio = time.time()

        for i in range(cantidad):
            correo = random.choice(correos_prueba)

            asunto = f"{correo['asunto']} #{i + 1}"
            contenido = correo["contenido"]

            enviar_correo(destino, asunto, contenido)

            enviados.append({
                "numero": i + 1,
                "asunto": asunto,
                "destino": destino
            })

            time.sleep(pausa)

        fin = time.time()
        tiempo_total = round(fin - inicio, 2)

        resultado = {
            "cantidad": cantidad,
            "destino": destino,
            "tiempo_total": tiempo_total
        }

    return render_template(
        "simulador.html",
        resultado=resultado,
        enviados=enviados
    )

if __name__ == "__main__":
    app.run(debug=True, port=5001)