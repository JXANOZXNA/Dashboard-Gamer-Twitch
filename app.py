from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import httpx

app = FastAPI(title="Dashboard Gamer - Twitch Helix")

# Credenciales activas
CLIENT_ID = '5ur4pbx6nnf2zu8sst4k71xrq4bnyj'
CLIENT_SECRET = 'agokd3j1q6rneen7kxrjgifm5rmbhf'

cid = CLIENT_ID.strip()
csecret = CLIENT_SECRET.strip()

def obtener_token():
    """Autenticación con la API de Twitch OAUTH."""
    url_auth = "https://id.twitch.tv/oauth2/token"
    datos_formulario = {
        "client_id": cid,
        "client_secret": csecret,
        "grant_type": "client_credentials",
    }
    try:
        respuesta = httpx.post(url_auth, data=datos_formulario, follow_redirects=True)
        if respuesta.status_code == 200:
            return respuesta.json().get("access_token")
    except Exception:
        pass
    return None

# 1. RUTA PRINCIPAL: FACHADA VISUAL CON ACORDEÓN DESPLEGABLE
@app.get("/", response_class=HTMLResponse)
def inicio():
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Gamer - Twitch</title>
        <style>
            body {
                background-color: #0e0e10; color: #efeff1;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex; flex-direction: column; align-items: center;
                padding: 40px 20px; min-height: 100vh; margin: 0; box-sizing: border-box;
            }
            .container {
                text-align: center; background-color: #1f1f23; padding: 40px;
                border-radius: 12px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
                border: 2px solid #9147ff; width: 520px; margin-bottom: 30px;
            }
            h1 { color: #9147ff; margin-top: 0; margin-bottom: 10px; }
            p { color: #adadb8; margin-bottom: 30px; }
            .search-box { display: flex; gap: 10px; justify-content: center; margin-bottom: 20px; }
            input[type="text"] {
                background-color: #464649; border: 2px solid transparent; color: white;
                padding: 12px 20px; border-radius: 6px; font-size: 16px; outline: none; width: 60%;
                transition: border 0.3s;
            }
            input[type="text"]:focus { border: 2px solid #9147ff; }
            button {
                background-color: #9147ff; color: white; border: none; padding: 12px 24px;
                border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer;
                transition: background-color 0.2s;
            }
            button:hover { background-color: #772ce8; }
            .result-card {
                margin-top: 20px; padding: 20px; border-radius: 8px; text-align: left;
                display: none; background-color: #0e0e10; border-left: 5px solid #9147ff;
            }
            .online { border-left-color: #00f593; }
            .offline { border-left-color: #eb0400; }
            .btn-twitch {
                display: inline-block; margin-top: 15px; background-color: #9147ff; color: white;
                text-decoration: none; padding: 10px 18px; border-radius: 6px; font-weight: bold;
                font-size: 14px; transition: background-color 0.2s;
            }
            .btn-twitch:hover { background-color: #772ce8; }

            /* ESTILOS DEL TOP JUEGOS Y MENÚ DESPLEGABLE */
            .games-container {
                background-color: #1f1f23; padding: 30px; border-radius: 12px;
                border: 2px solid #2a2a30; width: 520px; text-align: left;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5); box-sizing: border-box;
            }
            .games-header {
                display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
            }
            .games-container h2 { color: #00f593; margin: 0; font-size: 20px; }
            .btn-refresh {
                background-color: #26262c; color: #adadb8; border: 1px solid #464649;
                padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer;
            }
            .btn-refresh:hover { background-color: #323239; color: white; }
            
            .game-wrapper { margin-bottom: 12px; }
            .game-item {
                background-color: #0e0e10; padding: 12px 15px; border-radius: 8px;
                border-left: 4px solid #9147ff; display: flex; align-items: center; gap: 15px;
                cursor: pointer; transition: background-color 0.2s;
            }
            .game-item:hover { background-color: #18181c; }
            .game-rank { font-size: 18px; font-weight: bold; color: #9147ff; width: 25px; }
            .game-img { width: 45px; height: 60px; border-radius: 6px; object-fit: cover; }
            .game-info { flex-grow: 1; }
            .game-name { font-size: 16px; font-weight: bold; color: white; display: block; }
            .game-tag { font-size: 12px; color: #adadb8; }
            .game-arrow { color: #9147ff; font-weight: bold; font-size: 14px; }

            /* CONTENEDOR DESPLEGABLE DE STREAMERS */
            .streamers-dropdown {
                display: none; background-color: #141416; margin-top: 5px; padding: 12px 15px;
                border-radius: 8px; border-left: 4px solid #00f593;
            }
            .streamer-row {
                display: flex; justify-content: space-between; align-items: center;
                padding: 8px 0; border-bottom: 1px solid #26262c;
            }
            .streamer-row:last-child { border-bottom: none; }
            .streamer-user { font-weight: bold; color: white; }
            .streamer-viewers { color: #00f593; font-size: 13px; font-weight: bold; }
            .btn-mini-twitch {
                background-color: #9147ff; color: white; text-decoration: none;
                padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: bold;
            }
            .btn-mini-twitch:hover { background-color: #772ce8; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎮 DASHBOARD GAMER</h1>
            <p>Proyecto de Ingeniería de Software — Desarrollado por Juandi</p>
            
            <div class="search-box">
                <input type="text" id="streamerNombre" placeholder="Escribe un streamer...">
                <button onclick="buscarStreamerWeb()">Buscar Canal</button>
            </div>

            <div id="resultado" class="result-card"></div>
        </div>

        <div class="games-container">
            <div class="games-header">
                <h2>🏆 TOP 5 JUEGOS EN TWITCH</h2>
                <button class="btn-refresh" onclick="cargarTopJuegos()">🔄 Refrescar</button>
            </div>
            <div id="listaJuegos">⏳ Cargando carátulas y tendencias...</div>
        </div>

        <script>
            async function buscarStreamerWeb() {
                const nombre = document.getElementById('streamerNombre').value;
                const contenedor = document.getElementById('resultado');
                if (!nombre) { alert('Por favor, escribe un nombre primero'); return; }
                
                contenedor.style.display = "block";
                contenedor.innerHTML = "<p>⏳ Buscando información en Twitch...</p>";
                
                try {
                    const respuesta = await fetch(`/api/buscar/${nombre}`);
                    const datos = await respuesta.json();
                    
                    if (datos.status === "error") {
                        contenedor.className = "result-card offline";
                        contenedor.innerHTML = `<p>❌ Error: ${datos.mensaje}</p>`;
                        return;
                    }

                    if (datos.en_vivo) {
                        contenedor.className = "result-card online";
                        contenedor.innerHTML = `
                            <h3 style="color: #00f593; margin-top:0;">🟢 EN VIVO</h3>
                            <p><strong>Título:</strong> ${datos.titulo}</p>
                            <p><strong>Juego:</strong> ${datos.juego}</p>
                            <p><strong>Espectadores:</strong> ${datos.espectadores.toLocaleString()}</p>
                            <a class="btn-twitch" href="https://twitch.tv/${nombre.toLowerCase()}" target="_blank">🔴 Ver Directo en Twitch</a>
                        `;
                    } else {
                        contenedor.className = "result-card offline";
                        contenedor.innerHTML = `
                            <h3 style="color: #eb0400; margin-top:0;">🔴 DESCONECTADO</h3>
                            <p>El canal no está transmitiendo en este momento.</p>
                        `;
                    }
                } catch (e) {
                    contenedor.className = "result-card offline";
                    contenedor.innerHTML = "<p>❌ Error de conexión al servidor local.</p>";
                }
            }

            async function cargarTopJuegos() {
                const contenedorJuegos = document.getElementById('listaJuegos');
                contenedorJuegos.innerHTML = "<p style='color: #adadb8;'>⏳ Actualizando lista...</p>";
                try {
                    const respuesta = await fetch('/api/top-juegos');
                    const datos = await respuesta.json();

                    if (datos.status === "error") {
                        contenedorJuegos.innerHTML = `<p style="color: #eb0400;">❌ ${datos.mensaje}</p>`;
                        return;
                    }

                    let html = "";
                    datos.juegos.forEach((juego, index) => {
                        html += `
                            <div class="game-wrapper">
                                <div class="game-item" onclick="toggleStreamers('${juego.id}')">
                                    <span class="game-rank">#${index + 1}</span>
                                    <img class="game-img" src="${juego.portada}" alt="${juego.nombre}">
                                    <div class="game-info">
                                        <span class="game-name">${juego.nombre}</span>
                                        <span class="game-tag">Haz clic para ver más vistos 🔽</span>
                                    </div>
                                </div>
                                <div id="dropdown-${juego.id}" class="streamers-dropdown">
                                    <p style="color: #adadb8; margin: 5px 0;">⏳ Cargando transmisiones masivas...</p>
                                </div>
                            </div>
                        `;
                    });
                    contenedorJuegos.innerHTML = html;
                } catch (e) {
                    contenedorJuegos.innerHTML = "<p style='color: #eb0400;'>❌ Error al obtener el Top de juegos.</p>";
                }
            }

            // FUNCIÓN PARA DESPLEGAR Y CARGAR STREAMERS DEL JUEGO SELECCIONADO
            async function toggleStreamers(gameId) {
                const dropdown = document.getElementById(`dropdown-${gameId}`);
                
                // Si ya está visible, lo ocultamos
                if (dropdown.style.display === "block") {
                    dropdown.style.display = "none";
                    return;
                }

                // Si está oculto, lo mostramos y consultamos la API
                dropdown.style.display = "block";
                
                try {
                    const respuesta = await fetch(`/api/top-streamers-juego/${gameId}`);
                    const datos = await respuesta.json();

                    if (datos.status === "error" || datos.streamers.length === 0) {
                        dropdown.innerHTML = "<p style='color: #adadb8; margin: 5px 0;'>Sin transmisiones populares en este momento.</p>";
                        return;
                    }

                    let html = "<p style='color: #00f593; font-weight: bold; margin-top: 0; margin-bottom: 8px;'>🔥 CANALES MÁS VISTOS:</p>";
                    datos.streamers.forEach(streamer => {
                        html += `
                            <div class="streamer-row">
                                <div>
                                    <span class="streamer-user">${streamer.usuario}</span>
                                    <span class="streamer-viewers"> (${streamer.espectadores.toLocaleString()} 👁️)</span>
                                </div>
                                <a class="btn-mini-twitch" href="https://twitch.tv/${streamer.usuario.toLowerCase()}" target="_blank">🔴 Ver</a>
                            </div>
                        `;
                    });
                    dropdown.innerHTML = html;
                } catch (e) {
                    dropdown.innerHTML = "<p style='color: #eb0400; margin: 5px 0;'>Error al cargar transmisiones.</p>";
                }
            }

            window.onload = cargarTopJuegos;
        </script>
    </body>
    </html>
    """
    return html_content

# 2. RUTA BACKEND: BÚSQUEDA INDIVIDUAL
@app.get("/api/buscar/{nombre_streamer}")
def api_buscar(nombre_streamer: str):
    try:
        token = obtener_token()
        if not token:
            return {"status": "error", "mensaje": "No se pudo obtener el token"}
        
        url_streams = "https://api.twitch.tv/helix/streams"
        cabeceras = {"Client-Id": cid, "Authorization": f"Bearer {token}"}
        parametros = {"user_login": nombre_streamer.strip().lower()}
        
        respuesta = httpx.get(url_streams, headers=cabeceras, params=parametros, follow_redirects=True)
        
        if respuesta.status_code == 200:
            datos = respuesta.json().get("data", [])
            if not datos:
                return {"en_vivo": False}
            
            stream = datos[0]
            return {
                "en_vivo": True,
                "juego": stream.get("game_name", "Sin información"),
                "titulo": stream.get("title", "Sin título"),
                "espectadores": stream.get("viewer_count", 0)
            }
        return {"status": "error", "mensaje": f"Twitch HTTP {respuesta.status_code}"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

# 3. RUTA BACKEND: TOP 5 JUEGOS
@app.get("/api/top-juegos")
def api_top_juegos():
    try:
        token = obtener_token()
        if not token:
            return {"status": "error", "mensaje": "No se pudo obtener el token"}
        
        url_top = "https://api.twitch.tv/helix/games/top?first=5"
        cabeceras = {"Client-Id": cid, "Authorization": f"Bearer {token}"}
        
        respuesta = httpx.get(url_top, headers=cabeceras, follow_redirects=True)
        
        if respuesta.status_code == 200:
            lista_juegos = respuesta.json().get("data", [])
            resultado = []
            for juego in lista_juegos:
                portada_url = juego.get("box_art_url", "").replace("{width}", "90").replace("{height}", "120")
                resultado.append({
                    "id": juego.get("id"),
                    "nombre": juego.get("name"),
                    "portada": portada_url
                })
            return {"status": "ok", "juegos": resultado}
            
        return {"status": "error", "mensaje": f"Twitch HTTP {respuesta.status_code}"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

# 4. NUEVO BACKEND: TOP 3 STREAMERS POR ID DE JUEGO
@app.get("/api/top-streamers-juego/{game_id}")
def api_top_streamers_juego(game_id: str):
    try:
        token = obtener_token()
        if not token:
            return {"status": "error", "mensaje": "No se pudo obtener el token"}
        
        # Consultamos los 3 streams con más espectadores para este juego
        url_streams_juego = f"https://api.twitch.tv/helix/streams?game_id={game_id}&first=3"
        cabeceras = {"Client-Id": cid, "Authorization": f"Bearer {token}"}
        
        respuesta = httpx.get(url_streams_juego, headers=cabeceras, follow_redirects=True)
        
        if respuesta.status_code == 200:
            lista_streams = respuesta.json().get("data", [])
            resultado = []
            for stream in lista_streams:
                resultado.append({
                    "usuario": stream.get("user_name"),
                    "espectadores": stream.get("viewer_count", 0)
                })
            return {"status": "ok", "streamers": resultado}
            
        return {"status": "error", "mensaje": f"Twitch HTTP {respuesta.status_code}"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)