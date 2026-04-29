# 🎧 VibeCheck — Music Insight Analyzer

> Análise profunda de músicas: técnica, emocional e visual — direto no browser.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![Spotify API](https://img.shields.io/badge/Spotify-API-green)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple)

---

## ✨ Funcionalidades

| Feature | Descrição |
|---|---|
| 🔍 **Busca de música** | Pesquisa pelo nome ou artista via Spotify API |
| 📊 **Radar sonoro** | Gráfico radar com energia, dançabilidade, valência e mais |
| 🎭 **Classificação de vibe** | Treino, festa, foco, tristeza, relaxar ou viagem |
| 🧠 **Análise de letra (IA)** | GPT-4o-mini analisa significado, tema e emoção dominante |
| 🎧 **Recomendações** | 5 músicas parecidas sugeridas pelo Spotify |
| 🆚 **Modo comparação** | Compara duas músicas em gráfico de barras + vencedores por categoria |
| 🧬 **Perfil musical** | Analisa até 5 favoritas e gera um perfil personalizado do ouvinte |

---

## 🚀 Como rodar localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/vibecheck.git
cd vibecheck
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite o .env com suas chaves de API
```

#### Onde obter as chaves:

- **Spotify:** [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) → crie um app → copie Client ID e Client Secret
- **Genius:** [genius.com/api-clients](https://genius.com/api-clients) → crie um client → copie o Client Access Token
- **OpenAI:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys) *(opcional, mas recomendado)*

### 5. Rodar o app

```bash
streamlit run app.py
```

Acesse em: **http://localhost:8501**

---

## 🌐 Deploy no Streamlit Cloud (gratuito)

1. Faça push do projeto para um repositório público no GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io) e faça login com GitHub
3. Clique em **New app** → selecione o repositório → `app.py`
4. Em **Advanced settings → Secrets**, adicione suas variáveis:

```toml
SPOTIFY_CLIENT_ID = "xxx"
SPOTIFY_CLIENT_SECRET = "xxx"
GENIUS_ACCESS_TOKEN = "xxx"
OPENAI_API_KEY = "xxx"
```

5. Clique em **Deploy!** 🎉

---

## 🛠️ Tecnologias

- **[Streamlit](https://streamlit.io)** — Interface web
- **[Spotipy](https://spotipy.readthedocs.io)** — Spotify Web API
- **[LyricsGenius](https://lyricsgenius.readthedocs.io)** — Genius lyrics API
- **[OpenAI](https://platform.openai.com)** — Análise de letras com GPT-4o-mini
- **[Plotly](https://plotly.com/python/)** — Gráficos interativos
- **[Pandas](https://pandas.pydata.org)** — Tratamento de dados

---

## 📁 Estrutura do projeto

```
vibecheck/
├── app.py                  # App principal
├── requirements.txt        # Dependências
├── .env.example            # Template de variáveis de ambiente
├── .gitignore
├── .streamlit/
│   └── config.toml         # Tema dark customizado
└── README.md
```

---

## 🎨 Design

UI dark com paleta roxa/rosa, tipografia Bebas Neue + DM Sans, gráficos interativos Plotly e barras de progresso animadas. Cores dinâmicas baseadas na vibe detectada da música.

---

## 📝 Licença

MIT — sinta-se livre para usar, modificar e distribuir.
