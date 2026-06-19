"""
app.py — UI del MVP con Streamlit
Ejecutar desde la raíz: .venv/bin/streamlit run mvp/app.py
"""
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from rag import RAGEngine

st.set_page_config(
    page_title="Uendi — Asistente Banco Ueno",
    page_icon="🏦",
    layout="centered",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600&family=Inter:wght@400;500&display=swap');

  :root {
    --primary:         #F97316;
    --surface-alt:     #F4F4F0;
    --text:            #18181B;
    --text-muted:      #71717A;
    --border:          #E4E4E7;
    --citation-bg:     #FFF7ED;
    --citation-border: #FDBA74;
  }

  .stApp { background: #FAFAF9; }
  h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: var(--text); }
  p, div, span { font-family: 'Inter', sans-serif; }

  .user-bubble {
    background: var(--text);
    color: #FAFAF9;
    padding: 12px 16px;
    border-radius: 12px 12px 2px 12px;
    max-width: 75%;
    margin-left: auto;
    margin-bottom: 8px;
    font-size: 14px;
    white-space: pre-wrap;
    word-break: break-word;
  }
  .bot-bubble {
    background: var(--surface-alt);
    color: var(--text);
    padding: 12px 16px;
    border-radius: 12px 12px 12px 2px;
    max-width: 80%;
    margin-right: auto;
    margin-bottom: 4px;
    font-size: 14px;
    white-space: pre-wrap;
    word-break: break-word;
  }
  .citation {
    background: var(--citation-bg);
    border-left: 2px solid var(--citation-border);
    padding: 6px 10px;
    border-radius: 0 4px 4px 0;
    font-size: 12px;
    color: var(--text-muted);
    max-width: 80%;
    margin-bottom: 6px;
  }
  .citation a { color: var(--primary); text-decoration: none; }
</style>
""", unsafe_allow_html=True)


# ─── Engine (carga una sola vez por proceso) ──────────────────────────────────
@st.cache_resource(show_spinner="Cargando Uendi...")
def load_engine() -> RAGEngine:
    """Inicializa el motor RAG una sola vez."""
    return RAGEngine()


try:
    engine = load_engine()
except Exception as e:
    st.error(f"No se pudo inicializar el motor RAG: {e}")
    st.info("Asegurate de haber corrido `python mvp/ingest.py` y de tener `GROQ_API_KEY` en `.env`")
    st.stop()


# ─── Header ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown("### 🏦")
with col2:
    st.markdown("### Uendi")
    st.caption(f"Asistente del Banco Ueno · {engine.chunk_count()} artículos indexados")

st.divider()

# ─── Estado de sesión ─────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "groq_history" not in st.session_state:
    st.session_state.groq_history = []

# ─── Mensajes ─────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown(
        '<div class="bot-bubble">¡Hola! Soy Uendi, el asistente virtual del Banco Ueno. '
        "¿En qué te puedo ayudar hoy?</div>",
        unsafe_allow_html=True,
    )

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="user-bubble">{html.escape(msg["content"])}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="bot-bubble">{html.escape(msg["content"])}</div>',
            unsafe_allow_html=True,
        )
        for src in msg.get("sources", [])[:2]:
            url = html.escape(src["metadata"]["source_url"])
            title = html.escape(src["metadata"]["title"])
            st.markdown(
                f'<div class="citation">📄 <a href="{url}" target="_blank">{title}</a></div>',
                unsafe_allow_html=True,
            )

# ─── Input ────────────────────────────────────────────────────────────────────
query = st.chat_input("Hacé tu consulta sobre productos Banco Ueno...")

if query:
    st.markdown(
        f'<div class="user-bubble">{html.escape(query)}</div>',
        unsafe_allow_html=True,
    )
    st.session_state.messages.append({"role": "user", "content": query})

    with st.spinner("Uendi está buscando..."):
        try:
            answer, sources = engine.ask(query, st.session_state.groq_history)
        except Exception as e:
            answer = "Hubo un error al procesar tu consulta. Intentá de nuevo en unos segundos."
            sources = []
            st.error(str(e))

    st.markdown(
        f'<div class="bot-bubble">{html.escape(answer)}</div>',
        unsafe_allow_html=True,
    )
    for src in sources[:2]:
        url = html.escape(src["metadata"]["source_url"])
        title = html.escape(src["metadata"]["title"])
        st.markdown(
            f'<div class="citation">📄 <a href="{url}" target="_blank">{title}</a></div>',
            unsafe_allow_html=True,
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })
    st.session_state.groq_history.extend([
        {"role": "user", "content": query},
        {"role": "assistant", "content": answer},
    ])

    st.rerun()
