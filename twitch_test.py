import httpx

# 1. Tus credenciales reales aquí
CLIENT_ID = '5ur4pbx6nnf2zu8sst4k71xrq4bnyj'
CLIENT_SECRET = 'agokd3j1q6rneen7kxrjgifm5rmbhf'

cid = CLIENT_ID.strip()
csecret = CLIENT_SECRET.strip()

def obtener_token():
    url_auth = "https://id.twitch.tv/oauth2/token"
    datos_formulario = {
        "client_id": cid,
        "client_secret": csecret,
        "grant_type": "client_credentials"
    }
    respuesta = httpx.post(url_auth, data=datos_formulario, follow_redirects=True)
    if respuesta.status_code == 200:
        return respuesta.json()["access_token"]
    return None

def buscar_streamer(token, nombre_streamer):
    # La URL limpia oficial sin parámetros pegados en la cadena
    url_streams = "https://api.twitch.tv/helix/streams"
    
    # Encabezados estrictos con formato correcto exigido por Helix
    cabeceras = {
        "Client-Id": cid,
        "Authorization": f"Bearer {token}"
    }
    
    # Parámetros pasados de forma nativa a httpx
    parametros_busqueda = {
        "user_login": nombre_streamer.strip().lower()
    }
    
    respuesta = httpx.get(url_streams, headers=cabeceras, params=parametros_busqueda, follow_redirects=False)
    
    if respuesta.status_code == 200:
        datos = respuesta.json()["data"]
        print(f"\n🔍 RESULTADO DE BÚSQUEDA PARA: {nombre_streamer.upper()}")
        print("-" * 40)
        
        if not datos:
            print("🔴 ESTADO: APAGADO (Offline) o el nombre está mal escrito.")
        else:
            stream = datos[0] # Extraemos el primer elemento de la lista
            print("🟢 ESTADO: ¡EN VIVO! (Online)")
            print(f"🎮 JUGANDO: {stream['game_name']}")
            print(f"📝 TÍTULO: {stream['title']}")
            print(f"👥 ESPECTADORES: {stream['viewer_count']:,} personas viendo")
        print("-" * 40)
    else:
        print(f"\nTwitch rechazó la consulta. Código HTTP: {respuesta.status_code}")
        print("Texto crudo de error:")
        print(respuesta.text)

if __name__ == "__main__":
    print("--- CONECTANDO CON TWITCH ---")
    token_valido = obtener_token()
    
    if token_valido:
        print("-> Conexión establecida de forma segura.")
        canal = input("\n👉 Escribe el nombre del streamer que deseas buscar: ")
        if canal:
            buscar_streamer(token_valido, canal)
        else:
            print("No escribiste ningún nombre.")
    else:
        print("No se pudo iniciar el programa porque falló el token.")
    print("\n--- FIN DEL SCRIPT ---")
