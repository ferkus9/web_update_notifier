import requests
import hashlib
import os

URL = "https://refugeoulettesdegaube.ffcam.fr/"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Guardamos el archivo en la carpeta temporal /tmp de Linux para evitar conflictos de rutas
ARCHIVO_HASH = os.path.join(os.getcwd(), "ultimo_hash_refugio.txt")

def enviar_mensaje_telegram(mensaje):
    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    datos = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
    try:
        requests.post(url_telegram, data=datos, timeout=10)
    except Exception as e:
        print(f"Error Telegram: {e}")

def obtener_firma_pagina(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        respuesta = requests.get(url, headers=headers, timeout=15)
        if respuesta.status_code == 200:
            return hashlib.sha256(respuesta.text.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"Error Web: {e}")
    return None

def ejecutar_revision():
    nueva_firma = obtener_firma_pagina(URL)
    if not nueva_firma:
        print("No se pudo obtener la firma de la página web.")
        return
        
    # 👇 NUEVA LÍNEA PARA DEBUG: Imprime los primeros 500 caracteres en el log
    # Esto te ayudará a ver si hay fechas, horas o IDs dinámicos arriba del todo
    respuesta = requests.get(URL)
    texto_pagina = respuesta.text
    print("--- MUESTRA DEL TEXTO OBTENIDO ---")
    print(texto_pagina) 
    print("----------------------------------")
    print(f"El nuevo has es: {nueva_firma}")
    # Comprobamos si el artefacto descargado existe en el sistema de archivos
    firma_guardada = ""
    if os.path.exists(ARCHIVO_HASH):
        with open(ARCHIVO_HASH, "r") as f:
            firma_guardada = f.read().strip()
        print(f"Hash anterior recuperado: {firma_guardada}")
    else:
        print("No se encontró un hash anterior (es la primera ejecución).")

    # Comparación lógica
    if nueva_firma != firma_guardada:
        if firma_guardada == "":
            print("Primer registro de control exitoso.")
            enviar_mensaje_telegram("🚀 ¡Monitor de Oulettes activado con éxito usando GitHub Artifacts!")
        else:
            # ¡La página ha cambiado!
            mensaje_alerta = (
                "🚨 **¡ALERTA REAPERTURA!** 🚨\n\n"
                "La página del Refugio de Oulettes de Gaube ha cambiado su contenido.\n"
                f"Entra ya a revisar y reservar: {URL}"
            )
            enviar_mensaje_telegram(mensaje_alerta)
        
        # Escribimos el nuevo hash en el archivo para que luego el Workflow lo suba a la nube
        with open(ARCHIVO_HASH, "w") as f:
            f.write(nueva_firma)
    else:
        print("La página no ha sufrido ningún cambio. Todo sigue igual.")
        enviar_mensaje_telegram("🔍 Revisión rutinaria: El refugio sigue sin cambios. Todo en orden. 👍")

if __name__ == "__main__":
    ejecutar_revision()
