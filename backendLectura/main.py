import time
import signal
import sys
from database.mongodb import MongoDB
from services.lector_imap import LectorIMAP
from models.correo_model import CorreoModel

def signal_handler(sig, frame):
    print("\nDeteniendo el servicio")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    print("SERVICIO DE LECTURA DE CORREOS")
    print("Lee correos no leidos cada 30 segundos")
    print("")
    
    db = MongoDB()
    lector = LectorIMAP()
    
    try:
        lector.conectar()
        print("Servicio iniciado correctamente")
        print("")
        
        while True:
            try:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Buscando correos nuevos...")
                correos = lector.leer_correos_no_leidos()
                
                
                if not correos:
                    print("No hay correos nuevos")
                else:
                    print(f"Se encontraron {len(correos)} correos")
                    
                    for correo in correos:
                        print(f"  Procesando: {correo['remitente']} - {correo['asunto'][:50]}")

                        existe = db.collection.find_one({"id_mensaje_imap": correo["id"]})
                        
                        if existe:
                            print(f"    Ya existe en BD, saltando")
                            continue
                        
                        correo_dict = CorreoModel.crear_desde_imap(
                            correo["remitente"],
                            correo["asunto"],
                            correo["contenido"],
                            correo["id"]
                        )
                        
                        resultado = db.guardar_correo(correo_dict)
                        
                
                        db.collection.update_one(
                            {"_id": resultado},
                            {"$set": {"leido": True}}
                        )
                        
                        print(f"    Guardado en MongoDB con ID: {resultado} (leido=True)")
                
                print("")
                print("Esperando 30 segundos...")
                time.sleep(30)
                
            except Exception as e:
                print(f"Error en ciclo: {str(e)}")
                import traceback
                traceback.print_exc()
                print("Intentando reconectar")
                time.sleep(30)
                try:
                    lector.conectar()
                except:
                    print("Error al reconectar, se creara una nueva conexion en el proximo ciclo")
                    lector.mail = None
    
    except KeyboardInterrupt:
        print("\nServicio detenido por el usuario")
    finally:
        lector.desconectar()
        db.cerrar()
        print("Conexiones cerradas")

if __name__ == "__main__":
    main()