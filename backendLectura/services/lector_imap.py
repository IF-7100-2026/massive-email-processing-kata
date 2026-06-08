import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()

class LectorIMAP:
    def __init__(self):
        self.email_user = os.getenv("EMAIL_USER")
        self.email_pass = os.getenv("EMAIL_PASSWORD")
        self.imap_server = os.getenv("IMAP_SERVER")
        self.mail = None
    
    def conectar(self):
        print(f"Conectando a {self.imap_server} como {self.email_user}")
        self.mail = imaplib.IMAP4_SSL(self.imap_server, 993)
        self.mail.login(self.email_user, self.email_pass)
        self.mail.select("inbox")
        print("Conexion IMAP exitosa")
    
    def desconectar(self):
        if self.mail:
            self.mail.logout()
            print("Desconectado de IMAP")
    
    def refrescar_bandeja(self):
        if self.mail:
            self.mail.select("inbox")
            print("Bandeja refrescada")
    
    def limpiar_texto(self, texto):
        if texto is None:
            return ""
        
        partes = decode_header(texto)
        resultado = ""
        
        for parte, codificacion in partes:
            if isinstance(parte, bytes):
                try:
                    codificacion = codificacion or "utf-8"
                    resultado += parte.decode(codificacion, errors="ignore")
                except:
                    resultado += parte.decode("utf-8", errors="ignore")
            else:
                resultado += parte
        
        return resultado.strip()
    
    def obtener_cuerpo(self, mensaje):
        cuerpo = ""
        
        if mensaje.is_multipart():
            for parte in mensaje.walk():
                tipo_contenido = parte.get_content_type()
                disposicion = str(parte.get("Content-Disposition"))
                
                if tipo_contenido == "text/plain" and "attachment" not in disposicion:
                    try:
                        cuerpo = parte.get_payload(decode=True).decode('utf-8', errors="ignore")
                        break
                    except:
                        cuerpo = ""
        else:
            try:
                cuerpo = mensaje.get_payload(decode=True).decode('utf-8', errors="ignore")
            except:
                cuerpo = ""
        
        return cuerpo.strip()
    
    def leer_correos_no_leidos(self):
        correos = []
        
        if not self.mail:
            self.conectar()
        else:
            # Refrescar la bandeja para ver nuevos correos
            self.refrescar_bandeja()
        
        try:
            estado, mensajes = self.mail.search(None, "UNSEEN")
            
            if estado != "OK":
                print("Error buscando correos no leidos")
                return correos
            
            lista_ids = mensajes[0].split()
            print(f"Correos no leidos encontrados: {len(lista_ids)}")
            
            for num in lista_ids:
                estado, datos = self.mail.fetch(num, "(RFC822)")
                
                if estado != "OK":
                    continue
                
                mensaje = email.message_from_bytes(datos[0][1])
                
                asunto = self.limpiar_texto(mensaje["Subject"])
                remitente = email.utils.parseaddr(mensaje["From"])[1]
                contenido = self.obtener_cuerpo(mensaje)
                
                correos.append({
                    "id": num.decode() if isinstance(num, bytes) else str(num),
                    "remitente": remitente,
                    "asunto": asunto,
                    "contenido": contenido
                })
                
                self.mail.store(num, "+FLAGS", "\\Seen")
            
        except Exception as e:
            print(f"Error leyendo correos: {str(e)}")
        
        return correos