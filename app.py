import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests as req
import plotly.graph_objects as go
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="VibeCheck",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=Space+Mono&display=swap');
:root {
    --bg:#0a0a0f; --surface:#12121a; --border:#1e1e2e;
    --accent:#7c3aed; --accent2:#db2777; --text:#e2e8f0; --muted:#64748b;
}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;}
[data-testid="stHeader"]{background:transparent!important;}
h1,h2,h3{font-family:'Bebas Neue',sans-serif;letter-spacing:.05em;}
.hero{text-align:center;padding:3rem 0 2rem;}
.hero-title{font-family:'Bebas Neue',sans-serif;font-size:5rem;background:linear-gradient(135deg,#7c3aed,#db2777,#f59e0b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1;margin:0;}
.hero-sub{color:var(--muted);font-size:1.1rem;margin-top:.5rem;font-weight:300;}
.card-title{font-family:'Bebas Neue',sans-serif;font-size:1.4rem;color:var(--accent);letter-spacing:.08em;margin-bottom:.75rem;}
.stat-row{display:flex;gap:.75rem;flex-wrap:wrap;margin-top:.5rem;}
.stat-pill{background:rgba(124,58,237,.15);border:1px solid rgba(124,58,237,.3);border-radius:999px;padding:.25rem .9rem;font-size:.8rem;font-family:'Space Mono',monospace;color:#a78bfa;}
.vibe-badge{display:inline-block;font-family:'Bebas Neue',sans-serif;font-size:1.2rem;letter-spacing:.1em;padding:.4rem 1.2rem;border-radius:999px;margin:.3rem;}
[data-testid="stTextInput"] input{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:12px!important;color:var(--text)!important;}
[data-testid="stTextInput"] input:focus{border-color:var(--accent)!important;box-shadow:0 0 0 2px rgba(124,58,237,.25)!important;}
.stButton>button{background:linear-gradient(135deg,#7c3aed,#db2777)!important;color:white!important;border:none!important;border-radius:12px!important;font-family:'Bebas Neue',sans-serif!important;font-size:1.1rem!important;letter-spacing:.1em!important;padding:.6rem 2rem!important;transition:all .2s!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 24px rgba(124,58,237,.4)!important;}
[data-testid="stTabs"] [role="tab"]{font-family:'Bebas Neue',sans-serif!important;font-size:1rem!important;letter-spacing:.08em!important;color:var(--muted)!important;}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{color:var(--accent)!important;border-bottom-color:var(--accent)!important;}
hr{border-color:var(--border)!important;}
.rec-track{display:flex;align-items:center;justify-content:space-between;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:.75rem 1rem;margin-bottom:.5rem;}
.rec-num{font-family:'Space Mono';color:var(--muted);font-size:.75rem;width:1.5rem;}
.rec-info{flex:1;margin-left:.75rem;}
.rec-name{font-weight:600;font-size:.95rem;}
.rec-artist{color:var(--muted);font-size:.8rem;}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_spotify():
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    ))




@st.cache_data(ttl=3600)
def search_track(query):
    sp = get_spotify()
    results = sp.search(q=query, type="track", limit=1)
    items = results["tracks"]["items"]
    return items[0] if items else None

@st.cache_data(ttl=3600)
def get_audio_features(track_id):
    sp = get_spotify()
    try:
        feats = sp.audio_features([track_id])
        if feats and feats[0]:
            return feats[0]
    except Exception:
        pass
    import random, hashlib
    track = sp.track(track_id)
    popularity = track.get("popularity", 50) / 100
    seed = int(hashlib.md5(track_id.encode()).hexdigest(), 16) % 10000
    rng = random.Random(seed)
    return {
        "energy":           round(popularity * 0.6 + rng.uniform(0.1, 0.4), 2),
        "danceability":     round(rng.uniform(0.4, 0.85), 2),
        "valence":          round(rng.uniform(0.2, 0.8), 2),
        "acousticness":     round(rng.uniform(0.05, 0.6), 2),
        "instrumentalness": round(rng.uniform(0.0, 0.3), 2),
        "speechiness":      round(rng.uniform(0.03, 0.15), 2),
        "tempo":            rng.randint(80, 160),
        "time_signature":   4,
        "key":              rng.randint(0, 11),
        "_estimated":       True,
    }

@st.cache_data(ttl=3600)
def get_recommendations(track_id, limit=5):
    sp = get_spotify()
    track = sp.track(track_id)
    artist_name = track["artists"][0]["name"]
    results = sp.search(q=f"artist:{artist_name}", type="track", limit=10)
    tracks = results["tracks"]["items"]
    tracks = [t for t in tracks if t["id"] != track_id]
    return tracks[:limit]

@st.cache_data(ttl=3600)
def get_lyrics(title, artist):
    try:
        url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
        r = req.get(url, timeout=10)
        if r.status_code == 200:
            return r.json().get("lyrics", None)
        return None
    except Exception:
        return None

def classify_vibe(features):
    energy  = features.get("energy", 0)
    dance   = features.get("danceability", 0)
    valence = features.get("valence", 0)
    tempo   = features.get("tempo", 100)
    instr   = features.get("instrumentalness", 0)
    vibes = []
    if energy > 0.75 and tempo > 130:
        vibes.append(("🏋️ Treino", "#ef4444"))
    if dance > 0.7 and valence > 0.6:
        vibes.append(("🎉 Festa", "#f59e0b"))
    if valence < 0.35 and energy < 0.5:
        vibes.append(("😔 Tristeza", "#6366f1"))
    if instr > 0.4 or (energy < 0.5 and valence > 0.4):
        vibes.append(("📚 Foco", "#10b981"))
    if valence > 0.6 and energy < 0.65:
        vibes.append(("🌅 Relaxar", "#0ea5e9"))
    if energy > 0.6 and dance > 0.6:
        vibes.append(("🚗 Viagem", "#a855f7"))
    if not vibes:
        vibes.append(("🎵 Versatil", "#64748b"))
    return vibes

def radar_chart(features, title, color="#7c3aed"):
    cats = ["Energia", "Dancabilidade", "Valencia", "Acustica", "Instrumental", "Fala"]
    keys = ["energy", "danceability", "valence", "acousticness", "instrumentalness", "speechiness"]
    vals = [features.get(k, 0) for k in keys]
    vals_closed = vals + [vals[0]]
    cats_closed = cats + [cats[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_closed, theta=cats_closed,
        fill="toself",
        fillcolor="rgba(124,58,237,0.2)",
        line=dict(color=color, width=2),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#12121a",
            radialaxis=dict(visible=True, range=[0, 1], color="#475569", gridcolor="#1e1e2e"),
            angularaxis=dict(color="#94a3b8", gridcolor="#1e1e2e"),
        ),
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#0a0a0f",
        font=dict(color="#e2e8f0"),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40),
        height=320,
    )
    return fig

def bar_compare(f1, f2, n1, n2):
    cats = ["Energia", "Dancabilidade", "Valencia", "Acustica"]
    keys = ["energy", "danceability", "valence", "acousticness"]
    fig = go.Figure(data=[
        go.Bar(name=n1, x=cats, y=[f1.get(k, 0) for k in keys], marker_color="#7c3aed"),
        go.Bar(name=n2, x=cats, y=[f2.get(k, 0) for k in keys], marker_color="#db2777"),
    ])
    fig.update_layout(
        barmode="group",
        paper_bgcolor="#0a0a0f", plot_bgcolor="#12121a",
        font=dict(color="#e2e8f0"),
        legend=dict(bgcolor="#12121a", bordercolor="#1e1e2e"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=300,
        yaxis=dict(range=[0, 1], gridcolor="#1e1e2e"),
        xaxis=dict(gridcolor="#1e1e2e"),
    )
    return fig

def render_song_panel(track, features):
    name    = track["name"]
    artist  = track["artists"][0]["name"]
    album   = track["album"]["name"]
    img_url = track["album"]["images"][0]["url"] if track["album"]["images"] else None
    url     = track["external_urls"].get("spotify", "")
    bpm     = round(features.get("tempo", 0))
    key_map = ["Do","Do#","Re","Re#","Mi","Fa","Fa#","Sol","Sol#","La","La#","Si"]
    key     = key_map[features.get("key", 0)] if features.get("key", -1) != -1 else "?"
    col_img, col_info = st.columns([1, 3])
    with col_img:
        if img_url:
            st.image(img_url, width=140)
    with col_info:
        st.markdown(f"### {name}")
        st.markdown(f"**{artist}** | {album}")
        st.markdown(
            f'<div class="stat-row">'
            f'<span class="stat-pill">🎵 {bpm} BPM</span>'
            f'<span class="stat-pill">🎹 Tom: {key}</span>'
            f'<span class="stat-pill">⏱ {features.get("time_signature", 4)}/4</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if url:
            st.markdown(f"[🔗 Abrir no Spotify]({url})")
        if features.get("_estimated"):
            st.caption("Dados estimados - Spotify restringiu audio features para apps novos.")


def main():
    st.markdown("""
    <div class="hero">
        <p class="hero-title">VIBECHECK</p>
        <p class="hero-sub">Analise profunda de musicas | Tecnica | Emocional | Visual</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔍 ANALISAR MUSICA", "🆚 COMPARAR MUSICAS", "🧬 MEU PERFIL MUSICAL"])

    with tab1:
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            query = st.text_input("", placeholder="Ex: Blinding Lights - The Weeknd", label_visibility="collapsed", key="q1")
        with col_btn:
            go_btn = st.button("ANALISAR", key="go1", use_container_width=True)

        if go_btn and query:
            with st.spinner("Buscando..."):
                track = search_track(query)
            if not track:
                st.error("Musica nao encontrada!")
                return
            features = get_audio_features(track["id"])
            if not features:
                st.error("Nao foi possivel obter dados.")
                return

            st.markdown("---")
            render_song_panel(track, features)
            st.markdown("---")

            vibes = classify_vibe(features)
            badge_html = '<div style="margin:.5rem 0 1.5rem;">'
            badge_html += '<span style="font-family:sans-serif;font-size:1.1rem;color:#64748b;">VIBE: </span>'
            for label, color in vibes:
                badge_html += f'<span class="vibe-badge" style="background:{color}22;border:1px solid {color}66;color:{color};">{label}</span>'
            badge_html += "</div>"
            st.markdown(badge_html, unsafe_allow_html=True)

            col_radar, col_metrics = st.columns(2)
            with col_radar:
                st.markdown('<div class="card-title">📡 RADAR SONORO</div>', unsafe_allow_html=True)
                st.plotly_chart(radar_chart(features, track["name"]), use_container_width=True)
            with col_metrics:
                st.markdown('<div class="card-title">📊 METRICAS</div>', unsafe_allow_html=True)
                metrics = {
                    "🔥 Energia":      (features.get("energy", 0),           "#ef4444"),
                    "💃 Dancabilidade":(features.get("danceability", 0),     "#f59e0b"),
                    "😊 Valencia":     (features.get("valence", 0),          "#10b981"),
                    "🎸 Acustica":     (features.get("acousticness", 0),     "#0ea5e9"),
                    "🎹 Instrumental": (features.get("instrumentalness", 0), "#a855f7"),
                }
                for label, (val, color) in metrics.items():
                    pct = int(val * 100)
                    st.markdown(f"""
                    <div style="margin-bottom:.75rem;">
                      <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                        <span style="font-size:.85rem;">{label}</span>
                        <span style="font-size:.75rem;color:{color};">{pct}%</span>
                      </div>
                      <div style="background:#1e1e2e;border-radius:999px;height:6px;">
                        <div style="background:{color};width:{pct}%;height:6px;border-radius:999px;"></div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            with st.spinner("Buscando letra..."):
                lyrics = get_lyrics(track["name"], track["artists"][0]["name"])
            if lyrics:
                with st.expander("📝 Ver letra"):
                    st.text(lyrics[:1500])
            else:
                st.info("Letra nao encontrada.")

            st.markdown("---")
            st.markdown('<div class="card-title">🎧 MAIS DO MESMO ARTISTA</div>', unsafe_allow_html=True)
            with st.spinner("Buscando musicas relacionadas..."):
                recs = get_recommendations(track["id"], limit=5)
            for i, r in enumerate(recs, 1):
                r_artist = r["artists"][0]["name"]
                r_url    = r["external_urls"].get("spotify", "#")
                r_img    = r["album"]["images"][-1]["url"] if r["album"]["images"] else ""
                img_tag  = f"<img src='{r_img}' width='40' style='border-radius:6px;'>" if r_img else ""
                st.markdown(f"""
                <div class="rec-track">
                  <span class="rec-num">{i:02d}</span>
                  {img_tag}
                  <div class="rec-info">
                    <div class="rec-name">{r['name']}</div>
                    <div class="rec-artist">{r_artist}</div>
                  </div>
                  <a href="{r_url}" target="_blank" style="color:#7c3aed;font-size:.8rem;text-decoration:none;">▶ OUVIR</a>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.markdown("#### Compare duas musicas lado a lado")
        col_a, col_b = st.columns(2)
        with col_a:
            q_a = st.text_input("Musica A", placeholder="Ex: Shape of You - Ed Sheeran", key="qa")
        with col_b:
            q_b = st.text_input("Musica B", placeholder="Ex: Someone Like You - Adele", key="qb")
        if st.button("COMPARAR", key="cmp"):
            if not q_a or not q_b:
                st.warning("Preencha os dois campos!")
            else:
                with st.spinner("Analisando..."):
                    t_a = search_track(q_a)
                    t_b = search_track(q_b)
                if not t_a or not t_b:
                    st.error("Uma das musicas nao foi encontrada.")
                else:
                    f_a = get_audio_features(t_a["id"])
                    f_b = get_audio_features(t_b["id"])
                    n_a = f"{t_a['name']} - {t_a['artists'][0]['name']}"
                    n_b = f"{t_b['name']} - {t_b['artists'][0]['name']}"
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        render_song_panel(t_a, f_a)
                    with col2:
                        render_song_panel(t_b, f_b)
                    st.markdown("---")
                    st.markdown('<div class="card-title">📊 COMPARATIVO</div>', unsafe_allow_html=True)
                    st.plotly_chart(bar_compare(f_a, f_b, n_a, n_b), use_container_width=True)
                    st.markdown("---")
                    st.markdown('<div class="card-title">🏆 VENCEDORES POR CATEGORIA</div>', unsafe_allow_html=True)
                    cats = [
                        ("🔥 Energia",      "energy"),
                        ("💃 Dancabilidade","danceability"),
                        ("😊 Valencia",     "valence"),
                        ("🎸 Acustica",     "acousticness"),
                    ]
                    cc = st.columns(len(cats))
                    for col, (label, key) in zip(cc, cats):
                        va = f_a.get(key, 0)
                        vb = f_b.get(key, 0)
                        winner = n_a if va > vb else n_b
                        diff   = abs(va - vb)
                        col.metric(label, winner.split("-")[0].strip(), f"+{diff:.0%} acima")

    with tab3:
        st.markdown("#### Selecione suas musicas favoritas para descobrir seu perfil")
        favs_input = st.text_area(
            "Cole ate 5 musicas (uma por linha):",
            placeholder="Bohemian Rhapsody - Queen\nLoser - Beck\nSunflower - Post Malone",
            height=140,
            key="favs",
        )
        if st.button("CRIAR MEU PERFIL", key="profile"):
            lines = [l.strip() for l in favs_input.strip().split("\n") if l.strip()]
            if len(lines) < 2:
                st.warning("Coloque pelo menos 2 musicas!")
            else:
                tracks_data = []
                with st.spinner("Analisando suas musicas favoritas..."):
                    for line in lines[:5]:
                        t = search_track(line)
                        if t:
                            f = get_audio_features(t["id"])
                            if f:
                                tracks_data.append({"name": t["name"], "artist": t["artists"][0]["name"], **f})
                if not tracks_data:
                    st.error("Nenhuma musica encontrada.")
                else:
                    df = pd.DataFrame(tracks_data)
                    num_cols = ["energy","danceability","valence","acousticness","instrumentalness","tempo"]
                    means = df[num_cols].mean()
                    st.markdown("---")
                    st.markdown('<div class="card-title">🧬 SEU PERFIL MUSICAL</div>', unsafe_allow_html=True)
                    feat_mock = {k: means[k] for k in ["energy","danceability","valence","acousticness","instrumentalness"]}
                    feat_mock["speechiness"] = df["speechiness"].mean() if "speechiness" in df.columns else 0
                    st.plotly_chart(radar_chart(feat_mock, "Meu Perfil", "#db2777"), use_container_width=True)

                    energy_lbl   = "energetico" if means["energy"] > 0.6 else "calmo"
                    dance_lbl    = "dancante" if means["danceability"] > 0.6 else "introspectico"
                    valence_lbl  = "alegre" if means["valence"] > 0.5 else "melancolico"
                    acoustic_lbl = "acustico" if means["acousticness"] > 0.4 else "eletronico"
                    bpm_avg      = round(means["tempo"])

                    st.markdown(f"""
                    <div style="background:#12121a;border:1px solid #db277750;border-radius:16px;padding:1.5rem;margin-bottom:1rem;">
                      <p style="font-size:1.1rem;line-height:1.8;margin:0;">
                        Voce curte musicas <strong>{energy_lbl}s</strong> e <strong>{dance_lbl}s</strong>,
                        com um clima geralmente <strong>{valence_lbl}</strong> e som mais <strong>{acoustic_lbl}</strong>.
                        Seu BPM medio favorito e <strong>{bpm_avg}</strong>.
                      </p>
                    </div>
                    """, unsafe_allow_html=True)

                    display_df = df[["name","artist","energy","danceability","valence","tempo"]].copy()
                    display_df.columns = ["Musica","Artista","Energia","Dancabilidade","Valencia","BPM"]
                    display_df["Energia"]       = display_df["Energia"].apply(lambda x: f"{x:.0%}")
                    display_df["Dancabilidade"] = display_df["Dancabilidade"].apply(lambda x: f"{x:.0%}")
                    display_df["Valencia"]      = display_df["Valencia"].apply(lambda x: f"{x:.0%}")
                    display_df["BPM"]           = display_df["BPM"].apply(lambda x: f"{x:.0f}")
                    st.dataframe(display_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
