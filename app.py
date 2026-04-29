import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius
from openai import OpenAI
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os
from dotenv import load_dotenv
import time

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VibeCheck",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=Space+Mono&display=swap');

:root {
    --bg:        #0a0a0f;
    --surface:   #12121a;
    --border:    #1e1e2e;
    --accent:    #7c3aed;
    --accent2:   #db2777;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --green:     #10b981;
    --yellow:    #f59e0b;
    --red:       #ef4444;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
}
[data-testid="stHeader"] { background: transparent !important; }

/* Typography */
h1, h2, h3 { font-family: 'Bebas Neue', sans-serif; letter-spacing: 0.05em; }
body, p, div, span { font-family: 'DM Sans', sans-serif; }
code, pre { font-family: 'Space Mono', monospace; }

/* Hero */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 5rem;
    background: linear-gradient(135deg, #7c3aed, #db2777, #f59e0b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin: 0;
}
.hero-sub {
    color: var(--muted);
    font-size: 1.1rem;
    margin-top: 0.5rem;
    font-weight: 300;
}

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.4rem;
    color: var(--accent);
    letter-spacing: 0.08em;
    margin-bottom: 0.75rem;
}

/* Song header */
.song-header {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    background: linear-gradient(135deg, #12121a, #1a0a2e);
    border: 1px solid #2d1b69;
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}
.song-info h2 { font-family: 'Bebas Neue', sans-serif; font-size: 2rem; margin: 0; }
.song-info p { color: var(--muted); margin: 0.2rem 0 0; }

/* Stat pill */
.stat-row { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.5rem; }
.stat-pill {
    background: rgba(124,58,237,0.15);
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 999px;
    padding: 0.25rem 0.9rem;
    font-size: 0.8rem;
    font-family: 'Space Mono', monospace;
    color: #a78bfa;
}

/* Vibe badge */
.vibe-badge {
    display: inline-block;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.2rem;
    letter-spacing: 0.1em;
    padding: 0.4rem 1.2rem;
    border-radius: 999px;
    margin: 0.3rem;
}

/* Input styling */
[data-testid="stTextInput"] input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.25) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #db2777) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.1em !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(124,58,237,0.4) !important;
}

/* Tabs */
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1rem !important;
    letter-spacing: 0.08em !important;
    color: var(--muted) !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* Plotly dark bg fix */
.js-plotly-plot { border-radius: 12px; overflow: hidden; }

/* Rec track */
.rec-track {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}
.rec-track:hover { border-color: var(--accent); }
.rec-num { font-family: 'Space Mono'; color: var(--muted); font-size: 0.75rem; width: 1.5rem; }
.rec-info { flex: 1; margin-left: 0.75rem; }
.rec-name { font-weight: 600; font-size: 0.95rem; }
.rec-artist { color: var(--muted); font-size: 0.8rem; }
.rec-match { font-family: 'Space Mono'; font-size: 0.75rem; color: #10b981; }
</style>
""", unsafe_allow_html=True)


# ── API clients ───────────────────────────────────────────────────────────────
@st.cache_resource
def get_spotify():
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    ))

@st.cache_resource
def get_genius():
    token = os.getenv("GENIUS_ACCESS_TOKEN")
    if not token:
        return None
    return lyricsgenius.Genius(token, verbose=False, remove_section_headers=True)

@st.cache_resource
def get_openai():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    return OpenAI(api_key=key)


# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def search_track(query: str):
    sp = get_spotify()
    results = sp.search(q=query, type="track", limit=1)
    items = results["tracks"]["items"]
    return items[0] if items else None

@st.cache_data(ttl=3600)
def get_audio_features(track_id: str):
    sp = get_spotify()
    feats = sp.audio_features([track_id])
    return feats[0] if feats else None

@st.cache_data(ttl=3600)
def get_recommendations(track_id: str, limit=5):
    sp = get_spotify()
    recs = sp.recommendations(seed_tracks=[track_id], limit=limit)
    return recs["tracks"]

@st.cache_data(ttl=3600)
def get_lyrics(title: str, artist: str) -> str | None:
    genius = get_genius()
    if not genius:
        return None
    try:
        song = genius.search_song(title, artist)
        return song.lyrics[:3000] if song else None
    except Exception:
        return None

def ai_analyze_lyrics(lyrics: str, title: str, artist: str) -> dict:
    client = get_openai()
    if not client or not lyrics:
        return {}
    prompt = f"""Analise a música "{title}" de {artist}.

LETRA (trecho):
{lyrics[:1500]}

Responda em português, de forma concisa e direta:
1. SIGNIFICADO: 2 frases resumindo o significado/história da música.
2. TEMA: uma palavra ou expressão curta (ex: amor perdido, superação, festa, saudade).
3. EMOÇÃO_DOMINANTE: uma emoção (ex: melancolia, euforia, nostalgia, raiva, alegria).
4. PUBLICO: para quem essa música fala? (1 frase curta)

Formato de resposta — apenas isso, sem markdown:
SIGNIFICADO: ...
TEMA: ...
EMOÇÃO: ...
PUBLICO: ..."""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.7,
    )
    text = resp.choices[0].message.content
    result = {}
    for line in text.strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            result[k.strip()] = v.strip()
    return result

def classify_vibe(features: dict) -> list[tuple[str, str]]:
    energy = features.get("energy", 0)
    dance  = features.get("danceability", 0)
    valence = features.get("valence", 0)
    tempo  = features.get("tempo", 100)
    instrumentalness = features.get("instrumentalness", 0)

    vibes = []
    if energy > 0.75 and tempo > 130:
        vibes.append(("🏋️ Treino", "#ef4444"))
    if dance > 0.7 and valence > 0.6:
        vibes.append(("🎉 Festa", "#f59e0b"))
    if valence < 0.35 and energy < 0.5:
        vibes.append(("😔 Tristeza", "#6366f1"))
    if instrumentalness > 0.4 or (energy < 0.5 and valence > 0.4):
        vibes.append(("📚 Foco", "#10b981"))
    if valence > 0.6 and energy < 0.65:
        vibes.append(("🌅 Relaxar", "#0ea5e9"))
    if energy > 0.6 and dance > 0.6:
        vibes.append(("🚗 Viagem", "#a855f7"))
    if not vibes:
        vibes.append(("🎵 Versátil", "#64748b"))
    return vibes

def radar_chart(features: dict, title: str, color: str = "#7c3aed"):
    cats = ["Energia", "Dançabilidade", "Valência", "Acústica", "Instrumentalidade", "Fala"]
    keys = ["energy", "danceability", "valence", "acousticness", "instrumentalness", "speechiness"]
    vals = [features.get(k, 0) for k in keys]
    vals_closed = vals + [vals[0]]
    cats_closed  = cats + [cats[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_closed, theta=cats_closed,
        fill="toself",
        fillcolor=color.replace(")", ",0.2)").replace("rgb(", "rgba(") if "rgb" in color else color + "33",
        line=dict(color=color, width=2),
        name=title,
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#12121a",
            radialaxis=dict(visible=True, range=[0, 1], color="#475569", gridcolor="#1e1e2e"),
            angularaxis=dict(color="#94a3b8", gridcolor="#1e1e2e"),
        ),
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#0a0a0f",
        font=dict(color="#e2e8f0", family="DM Sans"),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40),
        height=320,
    )
    return fig

def bar_compare(f1: dict, f2: dict, n1: str, n2: str):
    cats = ["Energia", "Dançabilidade", "Valência", "Acústica"]
    keys = ["energy", "danceability", "valence", "acousticness"]
    v1 = [f1.get(k, 0) for k in keys]
    v2 = [f2.get(k, 0) for k in keys]

    fig = go.Figure(data=[
        go.Bar(name=n1, x=cats, y=v1, marker_color="#7c3aed"),
        go.Bar(name=n2, x=cats, y=v2, marker_color="#db2777"),
    ])
    fig.update_layout(
        barmode="group",
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#12121a",
        font=dict(color="#e2e8f0", family="DM Sans"),
        legend=dict(bgcolor="#12121a", bordercolor="#1e1e2e"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=300,
        yaxis=dict(range=[0, 1], gridcolor="#1e1e2e"),
        xaxis=dict(gridcolor="#1e1e2e"),
    )
    return fig


# ── Song panel ────────────────────────────────────────────────────────────────
def render_song_panel(track, features, slot=None):
    name    = track["name"]
    artist  = track["artists"][0]["name"]
    album   = track["album"]["name"]
    img_url = track["album"]["images"][0]["url"] if track["album"]["images"] else None
    url     = track["external_urls"].get("spotify", "")
    bpm     = round(features.get("tempo", 0))
    key_map = ["Dó","Dó#","Ré","Ré#","Mi","Fá","Fá#","Sol","Sol#","Lá","Lá#","Si"]
    key     = key_map[features.get("key", 0)] if features.get("key", -1) != -1 else "?"

    col_img, col_info = (slot or st).columns([1, 3])
    with col_img:
        if img_url:
            st.image(img_url, width=140)
    with col_info:
        st.markdown(f"### {name}")
        st.markdown(f"**{artist}** · {album}")
        st.markdown(
            f'<div class="stat-row">'
            f'<span class="stat-pill">🎵 {bpm} BPM</span>'
            f'<span class="stat-pill">🎹 Tom: {key}</span>'
            f'<span class="stat-pill">⏱ {features.get("time_signature",4)}/4</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if url:
            st.markdown(f"[🔗 Abrir no Spotify]({url})")


# ── Main app ──────────────────────────────────────────────────────────────────
def main():
    # Hero
    st.markdown("""
    <div class="hero">
        <p class="hero-title">VIBECHECK</p>
        <p class="hero-sub">Análise profunda de músicas • Técnica · Emocional · Visual</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔍 ANALISAR MÚSICA", "🆚 COMPARAR MÚSICAS", "🧬 MEU PERFIL MUSICAL"])

    # ── TAB 1: Analyze ──────────────────────────────────────────────────────
    with tab1:
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            query = st.text_input("", placeholder="Ex: Blinding Lights - The Weeknd", label_visibility="collapsed", key="q1")
        with col_btn:
            go_btn = st.button("ANALISAR", key="go1", use_container_width=True)

        if go_btn and query:
            with st.spinner("Buscando na galáxia musical..."):
                track = search_track(query)

            if not track:
                st.error("Música não encontrada. Tente outro nome!")
                return

            features = get_audio_features(track["id"])
            if not features:
                st.error("Não foi possível obter dados técnicos.")
                return

            st.markdown("---")
            render_song_panel(track, features)
            st.markdown("---")

            # Vibe badges
            vibes = classify_vibe(features)
            badge_html = '<div style="margin: 0.5rem 0 1.5rem;">'
            badge_html += '<span style="font-family:\'Bebas Neue\';font-size:1.1rem;color:#64748b;letter-spacing:0.1em;">VIBE: </span>'
            for label, color in vibes:
                badge_html += f'<span class="vibe-badge" style="background:{color}22;border:1px solid {color}66;color:{color};">{label}</span>'
            badge_html += "</div>"
            st.markdown(badge_html, unsafe_allow_html=True)

            # Two-column layout
            col_radar, col_metrics = st.columns([1, 1])

            with col_radar:
                st.markdown('<div class="card-title">📡 RADAR SONORO</div>', unsafe_allow_html=True)
                st.plotly_chart(radar_chart(features, track["name"]), use_container_width=True)

            with col_metrics:
                st.markdown('<div class="card-title">📊 MÉTRICAS</div>', unsafe_allow_html=True)
                metrics = {
                    "🔥 Energia":       (features.get("energy", 0), "#ef4444"),
                    "💃 Dançabilidade": (features.get("danceability", 0), "#f59e0b"),
                    "😊 Valência":      (features.get("valence", 0), "#10b981"),
                    "🎸 Acústica":      (features.get("acousticness", 0), "#0ea5e9"),
                    "🎹 Instrumental":  (features.get("instrumentalness", 0), "#a855f7"),
                }
                for label, (val, color) in metrics.items():
                    pct = int(val * 100)
                    st.markdown(f"""
                    <div style="margin-bottom:0.75rem;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                            <span style="font-size:0.85rem;">{label}</span>
                            <span style="font-family:'Space Mono';font-size:0.75rem;color:{color};">{pct}%</span>
                        </div>
                        <div style="background:#1e1e2e;border-radius:999px;height:6px;">
                            <div style="background:{color};width:{pct}%;height:6px;border-radius:999px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Lyrics AI analysis
            st.markdown("---")
            name   = track["name"]
            artist = track["artists"][0]["name"]

            with st.spinner("Buscando letra e analisando com IA..."):
                lyrics  = get_lyrics(name, artist)
                ai_data = ai_analyze_lyrics(lyrics, name, artist) if lyrics else {}

            if ai_data:
                st.markdown('<div class="card-title">🧠 ANÁLISE DA LETRA (IA)</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if "SIGNIFICADO" in ai_data:
                        st.markdown(f"**Significado**\n\n{ai_data['SIGNIFICADO']}")
                    if "PUBLICO" in ai_data:
                        st.markdown(f"**Para quem?**\n\n{ai_data['PUBLICO']}")
                with c2:
                    if "TEMA" in ai_data:
                        st.markdown(f"**Tema:** `{ai_data['TEMA']}`")
                    if "EMOÇÃO" in ai_data:
                        st.markdown(f"**Emoção dominante:** `{ai_data['EMOÇÃO']}`")
            elif not get_openai():
                st.info("💡 Configure OPENAI_API_KEY para análise de letras com IA.")
            else:
                st.info("Letra não encontrada para essa música.")

            # Recommendations
            st.markdown("---")
            st.markdown('<div class="card-title">🎧 VOCÊ TAMBÉM VAI CURTIR</div>', unsafe_allow_html=True)
            with st.spinner("Buscando recomendações..."):
                recs = get_recommendations(track["id"], limit=5)

            for i, r in enumerate(recs, 1):
                r_artist = r["artists"][0]["name"]
                r_url    = r["external_urls"].get("spotify", "#")
                r_img    = r["album"]["images"][-1]["url"] if r["album"]["images"] else ""
                st.markdown(f"""
                <div class="rec-track">
                    <span class="rec-num">{i:02d}</span>
                    {"<img src='" + r_img + "' width='40' style='border-radius:6px;'>" if r_img else ""}
                    <div class="rec-info">
                        <div class="rec-name">{r['name']}</div>
                        <div class="rec-artist">{r_artist}</div>
                    </div>
                    <a href="{r_url}" target="_blank" style="color:#7c3aed;font-size:0.8rem;text-decoration:none;">▶ OUVIR</a>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 2: Compare ──────────────────────────────────────────────────────
    with tab2:
        st.markdown("#### Compare duas músicas lado a lado")
        col_a, col_b = st.columns(2)
        with col_a:
            q_a = st.text_input("Música A", placeholder="Ex: Shape of You - Ed Sheeran", key="qa")
        with col_b:
            q_b = st.text_input("Música B", placeholder="Ex: Someone Like You - Adele", key="qb")

        if st.button("COMPARAR", key="cmp"):
            if not q_a or not q_b:
                st.warning("Preencha os dois campos!")
            else:
                with st.spinner("Analisando as músicas..."):
                    t_a = search_track(q_a)
                    t_b = search_track(q_b)

                if not t_a or not t_b:
                    st.error("Uma das músicas não foi encontrada.")
                else:
                    f_a = get_audio_features(t_a["id"])
                    f_b = get_audio_features(t_b["id"])
                    n_a = f"{t_a['name']} – {t_a['artists'][0]['name']}"
                    n_b = f"{t_b['name']} – {t_b['artists'][0]['name']}"

                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        render_song_panel(t_a, f_a)
                    with col2:
                        render_song_panel(t_b, f_b)

                    st.markdown("---")
                    st.markdown('<div class="card-title">📊 COMPARATIVO</div>', unsafe_allow_html=True)
                    st.plotly_chart(bar_compare(f_a, f_b, n_a, n_b), use_container_width=True)

                    # Winner cards
                    st.markdown("---")
                    st.markdown('<div class="card-title">🏆 VENCEDORES POR CATEGORIA</div>', unsafe_allow_html=True)
                    cats = [
                        ("🔥 Energia",       "energy",       n_a, n_b),
                        ("💃 Dançabilidade", "danceability", n_a, n_b),
                        ("😊 Valência",      "valence",      n_a, n_b),
                        ("🎸 Acústica",      "acousticness", n_a, n_b),
                    ]
                    cc = st.columns(len(cats))
                    for col, (label, key, na, nb) in zip(cc, cats):
                        va = f_a.get(key, 0)
                        vb = f_b.get(key, 0)
                        winner = na if va > vb else nb
                        diff   = abs(va - vb)
                        col.metric(label, winner.split("–")[0].strip(), f"+{diff:.0%} acima")

    # ── TAB 3: Profile ──────────────────────────────────────────────────────
    with tab3:
        st.markdown("#### Selecione suas músicas favoritas para descobrir seu perfil")
        favs_input = st.text_area(
            "Cole até 5 músicas (uma por linha):",
            placeholder="Bohemian Rhapsody - Queen\nLoser - Beck\nSunflower - Post Malone",
            height=140,
            key="favs",
        )
        if st.button("CRIAR MEU PERFIL", key="profile"):
            lines = [l.strip() for l in favs_input.strip().split("\n") if l.strip()]
            if len(lines) < 2:
                st.warning("Coloque pelo menos 2 músicas!")
            else:
                tracks_data = []
                with st.spinner("Analisando suas músicas favoritas..."):
                    for line in lines[:5]:
                        t = search_track(line)
                        if t:
                            f = get_audio_features(t["id"])
                            if f:
                                tracks_data.append({"name": t["name"], "artist": t["artists"][0]["name"], **f})

                if not tracks_data:
                    st.error("Nenhuma música encontrada.")
                else:
                    df = pd.DataFrame(tracks_data)
                    num_cols = ["energy","danceability","valence","acousticness","instrumentalness","tempo"]
                    means    = df[num_cols].mean()

                    st.markdown("---")
                    st.markdown('<div class="card-title">🧬 SEU PERFIL MUSICAL</div>', unsafe_allow_html=True)

                    # Radar
                    feat_mock = {
                        "energy": means["energy"],
                        "danceability": means["danceability"],
                        "valence": means["valence"],
                        "acousticness": means["acousticness"],
                        "instrumentalness": means["instrumentalness"],
                        "speechiness": df.get("speechiness", pd.Series([0])).mean() if "speechiness" in df else 0,
                    }
                    st.plotly_chart(radar_chart(feat_mock, "Meu Perfil", "#db2777"), use_container_width=True)

                    # Personality text
                    energy_lbl  = "energético" if means["energy"] > 0.6 else "calmo"
                    dance_lbl   = "dançante" if means["danceability"] > 0.6 else "introspectivo"
                    valence_lbl = "alegre" if means["valence"] > 0.5 else "melancólico"
                    acoustic_lbl = "acústico" if means["acousticness"] > 0.4 else "eletrônico"
                    bpm_avg      = round(means["tempo"])

                    st.markdown(f"""
                    <div class="card" style="border-color:#db277750;">
                        <p style="font-size:1.1rem;line-height:1.8;">
                        Você curte músicas <strong>{energy_lbl}s</strong> e <strong>{dance_lbl}s</strong>,
                        com um clima geralmente <strong>{valence_lbl}</strong> e som mais <strong>{acoustic_lbl}</strong>.
                        O seu BPM médio favorito é <strong>{bpm_avg}</strong>.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Table
                    st.markdown('<div class="card-title" style="margin-top:1rem;">📋 MÚSICAS ANALISADAS</div>', unsafe_allow_html=True)
                    display_df = df[["name","artist","energy","danceability","valence","tempo"]].copy()
                    display_df.columns = ["Música","Artista","Energia","Dançabilidade","Valência","BPM"]
                    display_df["Energia"]      = display_df["Energia"].apply(lambda x: f"{x:.0%}")
                    display_df["Dançabilidade"] = display_df["Dançabilidade"].apply(lambda x: f"{x:.0%}")
                    display_df["Valência"]      = display_df["Valência"].apply(lambda x: f"{x:.0%}")
                    display_df["BPM"]           = display_df["BPM"].apply(lambda x: f"{x:.0f}")
                    st.dataframe(display_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
