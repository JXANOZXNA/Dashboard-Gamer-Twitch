from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx

app = FastAPI(title="Dashboard Gamer - Twitch Helix")

# Credenciales activas
CLIENT_ID = '5ur4pbx6nnf2zu8sst4k71xrq4bnyj'
CLIENT_SECRET = 'agokd3j1q6rneen7kxrjgifm5rmbhf'
REDIRECT_URI = 'http://localhost:5000/callback'

cid = CLIENT_ID.strip()
csecret = CLIENT_SECRET.strip()

user_session = {
    "access_token": None,
    "user_info": None
}

def obtener_app_token():
    url_auth = "https://id.twitch.tv/oauth2/token"
    datos = {
        "client_id": cid,
        "client_secret": csecret,
        "grant_type": "client_credentials",
    }
    try:
        r = httpx.post(url_auth, data=datos, follow_redirects=True)
        if r.status_code == 200:
            return r.json().get("access_token")
    except Exception:
        pass
    return None

@app.get("/login")
def login():
    scope = "user:read:follows"
    auth_url = f"https://id.twitch.tv/oauth2/authorize?client_id={cid}&redirect_uri={REDIRECT_URI}&response_type=code&scope={scope}"
    return RedirectResponse(auth_url)

@app.get("/callback")
def callback(code: str = None):
    if not code:
        return RedirectResponse("/")
    
    url_token = "https://id.twitch.tv/oauth2/token"
    datos = {
        "client_id": cid,
        "client_secret": csecret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    
    r = httpx.post(url_token, data=datos)
    if r.status_code == 200:
        token_usuario = r.json().get("access_token")
        user_session["access_token"] = token_usuario
        
        headers = {"Client-Id": cid, "Authorization": f"Bearer {token_usuario}"}
        r_user = httpx.get("https://api.twitch.tv/helix/users", headers=headers)
        if r_user.status_code == 200:
            user_session["user_info"] = r_user.json().get("data", [])[0]
            
    return RedirectResponse("/")

@app.get("/logout")
def logout():
    user_session["access_token"] = None
    user_session["user_info"] = None
    return RedirectResponse("/")

@app.get("/", response_class=HTMLResponse)
def inicio():
    usuario = user_session.get("user_info")
    
    if usuario:
        user_header = f"""
            <div class="user-profile">
                <img src="{usuario['profile_image_url']}" class="avatar-header" alt="Avatar">
                <span class="username-header">{usuario['display_name']}</span>
                <a href="/logout" class="btn-logout">Cerrar Sesión</a>
            </div>
        """
    else:
        user_header = """
            <a href="/login" class="btn-login">🎮 Iniciar Sesión con Twitch</a>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Gamer - Twitch</title>
        <style>
            body {{
                background-color: #0e0e10; color: #efeff1;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex; min-height: 100vh; margin: 0; box-sizing: border-box;
            }}

            /* BARRA LATERAL ESTILO TWITCH */
            .sidebar {{
                width: 280px; background-color: #1f1f23; border-right: 2px solid #2a2a30;
                padding: 15px; display: flex; flex-direction: column; flex-shrink: 0;
                transition: width 0.3s ease, padding 0.3s ease;
                position: relative; box-sizing: border-box;
            }}

            .sidebar.collapsed {{
                width: 70px; padding: 15px 8px;
            }}

            .sidebar-header {{
                display: flex; align-items: center; justify-content: space-between;
                margin-bottom: 20px;
            }}

            .brand-title {{
                color: #9147ff; font-weight: bold; font-size: 16px; display: flex; align-items: center; gap: 6px;
                text-decoration: none;
            }}

            .sidebar.collapsed .brand-title span,
            .sidebar.collapsed .sidebar-section-title,
            .sidebar.collapsed .followed-info {{
                display: none;
            }}

            .btn-toggle-twitch {{
                background-color: #26262c; color: #efeff1; border: 1px solid #464649;
                border-radius: 6px; width: 28px; height: 28px; cursor: pointer;
                display: flex; align-items: center; justify-content: center;
                font-weight: bold; font-size: 14px; transition: background-color 0.2s;
            }}
            .btn-toggle-twitch:hover {{ background-color: #9147ff; color: white; }}

            .sidebar-section-title {{
                color: #adadb8; font-size: 12px; font-weight: bold; text-transform: uppercase;
                margin-bottom: 10px; letter-spacing: 0.5px;
            }}

            .followed-list {{ list-style: none; padding: 0; margin: 0; }}
            .followed-item {{
                display: flex; align-items: center; gap: 10px; padding: 8px;
                border-radius: 6px; text-decoration: none; color: #efeff1; margin-bottom: 5px;
                transition: background-color 0.2s;
            }}
            .followed-item:hover {{ background-color: #26262c; }}
            .followed-avatar {{ width: 36px; height: 36px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }}
            .followed-info {{ flex-grow: 1; overflow: hidden; }}
            .followed-name {{ font-weight: bold; font-size: 13px; white-space: nowrap; text-overflow: ellipsis; display: block; }}
            .followed-game {{ font-size: 11px; color: #00f593; white-space: nowrap; text-overflow: ellipsis; display: block; font-weight: bold; }}
            .followed-title {{ font-size: 10px; color: #adadb8; white-space: nowrap; text-overflow: ellipsis; display: block; overflow: hidden; }}
            .status-dot {{ width: 8px; height: 8px; border-radius: 50%; background-color: #eb0400; flex-shrink: 0; }}
            .status-dot.online {{ background-color: #00f593; box-shadow: 0 0 6px #00f593; }}

            /* CONTENIDO PRINCIPAL */
            .main-content {{
                flex-grow: 1; padding: 25px 30px; display: flex; flex-direction: column; align-items: center; width: 100%;
            }}

            /* BARRA SUPERIOR CON SPOTIFY INTEGRADO */
            .top-bar {{
                width: 100%; max-width: 850px; display: flex; justify-content: space-between;
                align-items: center; margin-bottom: 25px; gap: 20px; flex-wrap: wrap;
            }}

            .top-left-group {{
                display: flex; flex-direction: column; gap: 10px; flex-grow: 1; max-width: 500px;
            }}

            .user-profile {{ display: flex; align-items: center; gap: 10px; background: #1f1f23; padding: 6px 14px; border-radius: 20px; border: 1px solid #9147ff; width: fit-content; }}
            .avatar-header {{ width: 28px; height: 28px; border-radius: 50%; }}
            .username-header {{ font-weight: bold; color: white; font-size: 14px; }}
            .btn-login {{ background-color: #9147ff; color: white; text-decoration: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; width: fit-content; }}
            .btn-login:hover {{ background-color: #772ce8; }}
            .btn-logout {{ color: #eb0400; text-decoration: none; font-size: 12px; font-weight: bold; margin-left: 8px; }}

            /* REPRODUCTOR SPOTIFY COMPACTO */
            .spotify-widget {{
                width: 320px; height: 80px; border-radius: 12px; overflow: hidden;
                border: 1px solid #2a2a30; box-shadow: 0 4px 12px rgba(0,0,0,0.4); flex-shrink: 0;
            }}

            .container {{
                text-align: center; background-color: #1f1f23; padding: 30px;
                border-radius: 12px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
                border: 2px solid #9147ff; width: 100%; max-width: 850px; margin-bottom: 30px; box-sizing: border-box;
            }}
            h1 {{ color: #9147ff; margin-top: 0; font-size: 24px; }}
            .search-box {{ display: flex; gap: 10px; justify-content: center; margin-bottom: 15px; }}
            input[type="text"] {{
                background-color: #464649; border: 2px solid transparent; color: white;
                padding: 10px 15px; border-radius: 6px; font-size: 14px; outline: none; width: 60%;
            }}
            button {{
                background-color: #9147ff; color: white; border: none; padding: 10px 18px;
                border-radius: 6px; font-size: 14px; font-weight: bold; cursor: pointer;
            }}
            .result-card {{
                margin-top: 15px; padding: 15px; border-radius: 8px; text-align: left;
                display: none; background-color: #0e0e10; border-left: 5px solid #9147ff;
            }}
            .online {{ border-left-color: #00f593; }}
            .offline {{ border-left-color: #eb0400; }}

            .games-container {{
                background-color: #1f1f23; padding: 25px; border-radius: 12px;
                border: 2px solid #2a2a30; width: 100%; max-width: 850px; text-align: left; box-sizing: border-box;
            }}
            .games-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
            .games-container h2 {{ color: #00f593; margin: 0; font-size: 18px; }}
            .game-wrapper {{ margin-bottom: 10px; }}
            .game-item {{
                background-color: #0e0e10; padding: 10px 12px; border-radius: 8px;
                border-left: 4px solid #9147ff; display: flex; align-items: center; gap: 12px; cursor: pointer;
            }}
            .game-rank {{ font-size: 16px; font-weight: bold; color: #9147ff; width: 20px; }}
            .game-img {{ width: 40px; height: 53px; border-radius: 4px; object-fit: cover; }}
            .game-info {{ flex-grow: 1; }}
            .game-name {{ font-size: 15px; font-weight: bold; color: white; display: block; }}
            .game-tag {{ font-size: 11px; color: #adadb8; }}
            .streamers-dropdown {{
                display: none; background-color: #141416; margin-top: 5px; padding: 10px 12px;
                border-radius: 6px; border-left: 4px solid #00f593;
            }}
            .streamer-row {{ display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #26262c; }}
            .streamer-row:last-child {{ border-bottom: none; }}
            .btn-mini-twitch {{ background-color: #9147ff; color: white; text-decoration: none; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div id="sidebar" class="sidebar">
            <div class="sidebar-header">
                <a href="/" class="brand-title" title="Refrescar Dashboard">
                    🎮 <span>GAMER HUB</span>
                </a>
                <button id="toggleBtn" class="btn-toggle-twitch" onclick="toggleSidebar()" title="Contraer/Expandir">«</button>
            </div>
            
            <div class="sidebar-section-title">🔴 Canales Seguidos</div>
            <div id="listaSeguidos">
                <p style="color: #adadb8; font-size: 12px;">Inicia sesión con Twitch para ver canales en vivo.</p>
            </div>
        </div>

        <div class="main-content">
            <div class="top-bar">
                <div class="top-left-group">
                    {user_header}
                </div>

                <!-- WIDGET REPRODUCTOR DE SPOTIFY (PLAYLIST VARIADA GAMING/HIP-HOP/SYNTH) -->
                <div class="spotify-widget">
                    <iframe src="https://open.spotify.com/embed/playlist/37i9dQZF1DXdLENR312111?utm_source=generator&theme=0" 
                            width="100%" height="80" frameBorder="0" allowfullscreen="" 
                            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
                            loading="lazy"></iframe>
                </div>
            </div>

            <div class="container">
                <h1>🎮 DASHBOARD GAMER</h1>
                <div class="search-box">
                    <input type="text" id="streamerNombre" placeholder="Buscar canal en Twitch...">
                    <button onclick="buscarStreamerWeb()">Buscar</button>
                </div>
                <div id="resultado" class="result-card"></div>
            </div>

            <div class="games-container">
                <div class="games-header">
                    <h2>🏆 TOP 5 JUEGOS EN TWITCH</h2>
                </div>
                <div id="listaJuegos">⏳ Cargando tendencias...</div>
            </div>
        </div>

        <script>
            function toggleSidebar() {{
                const sidebar = document.getElementById('sidebar');
                const btn = document.getElementById('toggleBtn');
                sidebar.classList.toggle('collapsed');
                if (sidebar.classList.contains('collapsed')) {{
                    btn.innerHTML = '»';
                }} else {{
                    btn.innerHTML = '«';
                }}
            }}

            async function cargarCanalesSeguidos() {{
                const contenedor = document.getElementById('listaSeguidos');
                try {{
                    const respuesta = await fetch('/api/mis-seguidos');
                    const datos = await respuesta.json();
                    
                    if (datos.status === "no_logged") return;
                    if (datos.status === "error") {{
                        contenedor.innerHTML = `<p style="color: #eb0400; font-size: 12px;">❌ Error al cargar seguidos</p>`;
                        return;
                    }}

                    let html = '<div class="followed-list">';
                    datos.seguidos.forEach(c => {{
                        const statusClass = c.en_vivo ? 'online' : '';
                        const gameText = c.en_vivo ? c.juego : 'Desconectado';
                        const titleText = c.en_vivo && c.titulo ? `<span class="followed-title" title="${{c.titulo}}">${{c.titulo}}</span>` : '';
                        
                        html += `
                            <a class="followed-item" href="https://twitch.tv/${{c.usuario.toLowerCase()}}" target="_blank" title="${{c.usuario}} - ${{gameText}}">
                                <img class="followed-avatar" src="${{c.avatar}}" alt="${{c.usuario}}">
                                <div class="followed-info">
                                    <span class="followed-name">${{c.usuario}}</span>
                                    <span class="followed-game">${{gameText}}</span>
                                    ${{titleText}}
                                </div>
                                <span class="status-dot ${{statusClass}}"></span>
                            </a>
                        `;
                    }});
                    html += '</div>';
                    contenedor.innerHTML = html;
                }} catch (e) {{
                    contenedor.innerHTML = `<p style="color: #eb0400; font-size: 12px;">❌ Error de conexión</p>`;
                }}
            }}

            async function buscarStreamerWeb() {{
                const nombre = document.getElementById('streamerNombre').value;
                const contenedor = document.getElementById('resultado');
                if (!nombre) return;
                contenedor.style.display = "block";
                contenedor.innerHTML = "<p>⏳ Buscando...</p>";
                try {{
                    const respuesta = await fetch(`/api/buscar/${{nombre}}`);
                    const datos = await respuesta.json();
                    if (datos.en_vivo) {{
                        contenedor.className = "result-card online";
                        contenedor.innerHTML = `
                            <h3 style="color: #00f593; margin-top:0;">🟢 EN VIVO</h3>
                            <p><strong>Título:</strong> ${{datos.titulo}}</p>
                            <p><strong>Juego:</strong> ${{datos.juego}}</p>
                            <p><strong>Espectadores:</strong> ${{datos.espectadores.toLocaleString()}}</p>
                            <a class="btn-mini-twitch" href="https://twitch.tv/${{nombre.toLowerCase()}}" target="_blank">Ver Directo en Twitch</a>
                        `;
                    }} else {{
                        contenedor.className = "result-card offline";
                        contenedor.innerHTML = `<h3 style="color: #eb0400; margin-top:0;">🔴 DESCONECTADO</h3><p>El canal no está transmitiendo en este momento.</p>`;
                    }}
                }} catch (e) {{}}
            }}

            async function cargarTopJuegos() {{
                const contenedorJuegos = document.getElementById('listaJuegos');
                try {{
                    const respuesta = await fetch('/api/top-juegos');
                    const datos = await respuesta.json();
                    let html = "";
                    datos.juegos.forEach((juego, index) => {{
                        html += `
                            <div class="game-wrapper">
                                <div class="game-item" onclick="toggleStreamers('${{juego.id}}')">
                                    <span class="game-rank">#${{index + 1}}</span>
                                    <img class="game-img" src="${{juego.portada}}" alt="${{juego.nombre}}">
                                    <div class="game-info">
                                        <span class="game-name">${{juego.nombre}}</span>
                                        <span class="game-tag">Ver más vistos 🔽</span>
                                    </div>
                                </div>
                                <div id="dropdown-${{juego.id}}" class="streamers-dropdown"></div>
                            </div>
                        `;
                    }});
                    contenedorJuegos.innerHTML = html;
                }} catch (e) {{}}
            }}

            async function toggleStreamers(gameId) {{
                const dropdown = document.getElementById(`dropdown-${{gameId}}`);
                if (dropdown.style.display === "block") {{ dropdown.style.display = "none"; return; }}
                dropdown.style.display = "block";
                dropdown.innerHTML = "<p style='color: #adadb8;'>⏳ Cargando...</p>";
                try {{
                    const respuesta = await fetch(`/api/top-streamers-juego/${{gameId}}`);
                    const datos = await respuesta.json();
                    let html = "";
                    datos.streamers.forEach(s => {{
                        html += `
                            <div class="streamer-row">
                                <div>
                                    <span style="color:white; font-weight:bold;">${{s.usuario}}</span>
                                    <span style="color:#00f593; font-size:12px;"> (${{s.espectadores.toLocaleString()}} 👁️️)</span>
                                </div>
                                <a class="btn-mini-twitch" href="https://twitch.tv/${{s.usuario.toLowerCase()}}" target="_blank">Ver</a>
                            </div>
                        `;
                    }});
                    dropdown.innerHTML = html;
                }} catch (e) {{}}
            }}

            window.onload = () => {{
                cargarTopJuegos();
                cargarCanalesSeguidos();
            }};
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/api/mis-seguidos")
def api_mis_seguidos():
    token = user_session.get("access_token")
    usuario = user_session.get("user_info")
    if not token or not usuario:
        return {"status": "no_logged"}
    
    headers = {"Client-Id": cid, "Authorization": f"Bearer {token}"}
    user_id = usuario["id"]
    
    r_follows = httpx.get(f"https://api.twitch.tv/helix/channels/followed?user_id={user_id}&first=10", headers=headers)
    if r_follows.status_code != 200:
        return {"status": "error"}
    
    followed_data = r_follows.json().get("data", [])
    if not followed_data:
        return {"status": "ok", "seguidos": []}
    
    broadcaster_ids = [f["broadcaster_id"] for f in followed_data]
    
    params = [("user_id", bid) for bid in broadcaster_ids]
    r_streams = httpx.get("https://api.twitch.tv/helix/streams", headers=headers, params=params)
    live_dict = {}
    if r_streams.status_code == 200:
        for stream in r_streams.json().get("data", []):
            live_dict[stream["user_id"]] = {
                "juego": stream.get("game_name", "En vivo"),
                "titulo": stream.get("title", "")
            }

    r_users = httpx.get("https://api.twitch.tv/helix/users", headers=headers, params=params)
    avatar_dict = {}
    if r_users.status_code == 200:
        for u in r_users.json().get("data", []):
            avatar_dict[u["id"]] = u.get("profile_image_url")

    resultado = []
    for f in followed_data:
        bid = f["broadcaster_id"]
        is_live = bid in live_dict
        stream_info = live_dict.get(bid, {})
        resultado.append({
            "usuario": f["broadcaster_name"],
            "avatar": avatar_dict.get(bid, ""),
            "en_vivo": is_live,
            "juego": stream_info.get("juego", ""),
            "titulo": stream_info.get("titulo", "")
        })

    resultado.sort(key=lambda x: x["en_vivo"], reverse=True)
    return {"status": "ok", "seguidos": resultado}

@app.get("/api/buscar/{nombre_streamer}")
def api_buscar(nombre_streamer: str):
    token = obtener_app_token()
    if not token:
        return {"status": "error"}
    headers = {"Client-Id": cid, "Authorization": f"Bearer {token}"}
    r = httpx.get(f"https://api.twitch.tv/helix/streams?user_login={nombre_streamer.strip().lower()}", headers=headers)
    if r.status_code == 200:
        datos = r.json().get("data", [])
        if not datos: return {"en_vivo": False}
        s = datos[0]
        return {
            "en_vivo": True,
            "titulo": s.get("title", "Sin título"),
            "juego": s.get("game_name", "Sin información"),
            "espectadores": s.get("viewer_count", 0)
        }
    return {"status": "error"}

@app.get("/api/top-juegos")
def api_top_juegos():
    token = obtener_app_token()
    if not token: return {"status": "error"}
    headers = {"Client-Id": cid, "Authorization": f"Bearer {token}"}
    r = httpx.get("https://api.twitch.tv/helix/games/top?first=5", headers=headers)
    if r.status_code == 200:
        juegos = [{"id": j["id"], "nombre": j["name"], "portada": j["box_art_url"].replace("{width}", "90").replace("{height}", "120")} for j in r.json().get("data", [])]
        return {"status": "ok", "juegos": juegos}
    return {"status": "error"}

@app.get("/api/top-streamers-juego/{game_id}")
def api_top_streamers_juego(game_id: str):
    token = obtener_app_token()
    if not token: return {"status": "error"}
    headers = {"Client-Id": cid, "Authorization": f"Bearer {token}"}
    r = httpx.get(f"https://api.twitch.tv/helix/streams?game_id={game_id}&first=3", headers=headers)
    if r.status_code == 200:
        streamers = [{"usuario": s["user_name"], "espectadores": s["viewer_count"]} for s in r.json().get("data", [])]
        return {"status": "ok", "streamers": streamers}
    return {"status": "error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)