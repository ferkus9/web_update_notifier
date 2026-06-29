import requests
import hashlib
import os

# 1. Configuración
URL = "https://refugeoulettesdegaube.ffcam.fr/"
TELEGRAM_TOKEN = "TU_TOKEN_DE_BOTFATHER"
TELEGRAM_CHAT_ID = "TU_CHAT_ID_DE_USERINFOBOT"

# Archivo de texto donde se guardará el hash de forma permanente en el servidor
ARCHIVO_HASH = "ultimo_hash_refugio.txt"

def enviar_mensaje_telegram(mensaje):
    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    datos = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
    try:
        requests.post(url_telegram, data=datos, timeout=10)
    except Exception as e:
        print(f"Error de conexión con Telegram: {e}")

def obtener_firma_pagina(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        respuesta = requests.get(url, headers=headers, timeout=15)
        if respuesta.status_code == 200:
            return hashlib.sha256(respuesta.text.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"Error al conectar con la web: {e}")
    return None

def ejecutar_revision():
    nueva_firma = obtener_firma_pagina(URL)
    if not nueva_firma:
        print("No se pudo leer la web en esta revisión.")
        return

    # Si el archivo NO existe, es la primera vez que se ejecuta el script
    if not os.path.exists(ARCHIVO_HASH):
        with open(ARCHIVO_HASH, "w") as f:
            f.write(nueva_firma)
        print("Primer guardado de hash completado con éxito.")
        enviar_mensaje_telegram("🚀 ¡Monitor de Oulettes activado en PythonAnywhere! Todo listo.")
        return

    # Si el archivo SÍ existe, leemos el hash guardado anteriormente
    with open(ARCHIVO_HASH, "r") as f:
        firma_guardada = f.read().strip()

    # Comparamos
    if nueva_firma != firma_guardada:
        mensaje_alerta = (
            "🚨 **¡ALERTA REAPERTURA!** 🚨\n\n"
            "La página del Refugio de Oulettes de Gaube ha cambiado.\n"
            f"Entra ya a revisar y reservar: {URL}"
        )
        enviar_mensaje_telegram(mensaje_alerta)
        
        # Actualizamos el archivo por si acaso cambian más cosas en el futuro
        with open(ARCHIVO_HASH, "w") as f:
            f.write(nueva_firma)
    else:
        print("Revisión hecha: La página sigue igual.")

if __name__ == "__main__":
    ejecutar_revision()