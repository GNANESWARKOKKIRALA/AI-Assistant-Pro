"""
app.py — GapMind AI
Gold/Space luxury theme — LLaMA 3.3 70B via Groq + RAG + Auth + Voice + TTS
"""
import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from auth.database import init_users_db
from auth.auth_utils import init_session_state, is_logged_in, logout_user
from auth.login import show_login_page
from auth.register import show_register_page
from voice.tts import text_to_speech_base64, get_audio_html

from rag.loader import load_file
from rag.chunker import chunk_text
from rag.embedder import embed_texts
from rag.vector_store import add_chunks, reset_store, count_chunks
from rag.retriever import retrieve, format_context
from llm.groq_client import chat
from utils.helpers import (
    init_db, save_document, get_documents, delete_document_record,
    save_message, get_history, clear_history, format_sources, new_session_id
)

init_db()
init_users_db()

st.set_page_config(
    page_title="GapMind AI — LLaMA 3.3 70B",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_session_state()

if "session_id" not in st.session_state:
    st.session_state.session_id = new_session_id()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""
if "tts_index" not in st.session_state:
    st.session_state.tts_index = None

# ══════════════════════════════════════════════════════════════════
# GOLD / SPACE THEME CSS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

/* ── CSS Variables ── */
:root {
    --gold:        #c9a84c;
    --gold-light:  #f0c060;
    --gold-dark:   #8b6914;
    --gold-glow:   rgba(201,168,76,0.35);
    --gold-subtle: rgba(201,168,76,0.08);
    --bg-deep:     #080608;
    --bg-card:     #0e0c10;
    --bg-panel:    #120f14;
    --border:      rgba(201,168,76,0.25);
    --border-dim:  rgba(201,168,76,0.12);
    --text-main:   #e8dcc8;
    --text-dim:    #8a7a60;
    --text-muted:  #4a4035;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    color: var(--text-main);
}

.stApp {
    background: var(--bg-deep);
    background-image:
        radial-gradient(ellipse at 20% 20%, rgba(201,168,76,0.04) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 80%, rgba(100,60,20,0.06) 0%, transparent 60%),
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='400' height='400' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--bg-panel) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 4px 0 40px rgba(0,0,0,0.6);
}
section[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}

/* ── Sidebar brand ── */
.sidebar-brand {
    text-align: center;
    padding: 20px 8px 12px;
    border-bottom: 1px solid var(--border-dim);
    margin-bottom: 16px;
}
.sidebar-brand .brand-icon { font-size: 2.4rem; margin-bottom: 6px; }
.sidebar-brand .brand-name {
    font-family: 'Cinzel', serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--gold-light);
    letter-spacing: 2px;
    text-transform: uppercase;
}
.sidebar-brand .brand-sub {
    font-size: 0.7rem;
    color: var(--text-dim);
    letter-spacing: 1px;
    margin-top: 3px;
    text-transform: uppercase;
}

/* ── Profile card ── */
.profile-card {
    background: var(--gold-subtle);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
}
.profile-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.profile-card .pname {
    color: var(--gold-light);
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.5px;
}
.profile-card .pemail {
    color: var(--text-dim);
    font-size: 0.75rem;
    margin-top: 2px;
}

/* ── Metric cards ── */
.metric-card {
    background: var(--gold-subtle);
    border: 1px solid var(--border-dim);
    border-radius: 10px;
    padding: 12px 8px;
    text-align: center;
}
.metric-card .num {
    font-family: 'Cinzel', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--gold);
    line-height: 1;
}
.metric-card .lbl {
    font-size: 0.68rem;
    color: var(--text-dim);
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Cinzel', serif;
    font-size: 0.72rem;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 14px 0 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-heading::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border-dim);
}

/* ── Doc chip ── */
.doc-chip {
    background: var(--gold-subtle);
    border: 1px solid var(--border-dim);
    border-radius: 7px;
    padding: 7px 10px;
    margin: 4px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.78rem;
}
.doc-chip .dname { color: var(--gold-light); font-weight: 500; }
.doc-chip .dmeta { color: var(--text-dim); font-size: 0.7rem; }

/* ── Upload area ── */
div[data-testid="stFileUploader"] {
    background: var(--gold-subtle) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 10px !important;
}
div[data-testid="stFileUploader"] label {
    color: var(--text-dim) !important;
}

/* ── All sidebar buttons base → gold theme ── */
section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #1a1408, #2a2010) !important;
    color: var(--gold-light) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.5px !important;
    transition: all 0.25s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #2a2010, #3a3015) !important;
    border-color: var(--gold) !important;
    box-shadow: 0 0 12px var(--gold-glow) !important;
    color: #fff !important;
}

/* ── Clear Chat button — amber ── */
.clear-btn > button {
    border-color: rgba(217,119,6,0.5) !important;
    color: #fbbf24 !important;
}
.clear-btn > button:hover {
    border-color: #f59e0b !important;
    box-shadow: 0 0 12px rgba(245,158,11,0.3) !important;
}

/* ── Reset button — red ── */
.reset-btn > button {
    border-color: rgba(220,38,38,0.5) !important;
    color: #f87171 !important;
}
.reset-btn > button:hover {
    border-color: #ef4444 !important;
    box-shadow: 0 0 12px rgba(239,68,68,0.3) !important;
}

/* ── Logout button ── */
.logout-btn > button {
    background: linear-gradient(135deg, #3d0000, #5a0000) !important;
    border-color: rgba(220,38,38,0.6) !important;
    color: #fca5a5 !important;
    font-size: 0.9rem !important;
    height: 46px !important;
}
.logout-btn > button:hover {
    background: linear-gradient(135deg, #5a0000, #7a0000) !important;
    border-color: #ef4444 !important;
    box-shadow: 0 0 16px rgba(239,68,68,0.35) !important;
    color: #fff !important;
}

/* ── MAIN chat area ── */
.main .block-container {
    padding-top: 20px !important;
    padding-bottom: 10px !important;
}

/* ── Chat header banner ── */
.chat-header {
    position: relative;
    background: linear-gradient(135deg, #1a1000 0%, #0e0800 50%, #120a00 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    overflow: hidden;
}
.chat-header::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse at 90% 50%, rgba(201,168,76,0.12) 0%, transparent 60%),
        radial-gradient(ellipse at 10% 50%, rgba(120,80,20,0.08) 0%, transparent 50%);
}
.chat-header::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.chat-header-icon {
    font-size: 2.6rem;
    position: relative;
    z-index: 1;
    filter: drop-shadow(0 0 12px var(--gold-glow));
}
.chat-header-text { position: relative; z-index: 1; }
.chat-header h1 {
    font-family: 'Cinzel', serif !important;
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    color: var(--gold-light) !important;
    margin: 0 0 4px !important;
    letter-spacing: 1.5px !important;
    background: none !important;
    -webkit-text-fill-color: var(--gold-light) !important;
}
.chat-header p {
    color: var(--text-dim);
    margin: 0;
    font-size: 0.82rem;
    letter-spacing: 0.5px;
}
.chat-header-badge {
    position: absolute;
    right: 24px;
    top: 50%;
    transform: translateY(-50%);
    background: var(--gold-subtle);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.72rem;
    color: var(--gold);
    letter-spacing: 1px;
    text-transform: uppercase;
    font-family: 'Cinzel', serif;
    z-index: 1;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-dim) !important;
    border-radius: 12px !important;
    margin-bottom: 10px !important;
    position: relative !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    border-color: var(--border) !important;
    background: linear-gradient(135deg, #100d08, #0e0c0a) !important;
}
[data-testid="stChatMessage"] p {
    color: var(--text-main) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
    line-height: 1.65 !important;
}

/* ── Chat input ── */
div[data-testid="stChatInput"] textarea {
    background: #0e0c08 !important;
    border: 1px solid var(--border) !important;
    color: var(--text-main) !important;
    border-radius: 12px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
}
div[data-testid="stChatInput"] textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 16px var(--gold-glow) !important;
}
div[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, var(--gold-dark), var(--gold)) !important;
    border-radius: 10px !important;
    color: #000 !important;
}

/* ── TTS speaker button ── */
.tts-btn > button {
    background: var(--gold-subtle) !important;
    border: 1px solid var(--border-dim) !important;
    color: var(--gold) !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    padding: 4px 10px !important;
    height: 32px !important;
    font-weight: 600 !important;
}
.tts-btn > button:hover {
    border-color: var(--gold) !important;
    box-shadow: 0 0 8px var(--gold-glow) !important;
    color: var(--gold-light) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover { background: var(--gold-dark); }

/* ── Text inputs (auth forms) ── */
.stTextInput > div > div > input {
    background: #0e0c08 !important;
    border: 1px solid var(--border) !important;
    color: var(--text-main) !important;
    border-radius: 10px !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* ── Divider ── */
hr {
    border-color: var(--border-dim) !important;
    margin: 10px 0 !important;
}

/* ── Audio player ── */
audio {
    filter: sepia(0.8) saturate(2) hue-rotate(10deg);
    border-radius: 8px;
    width: 100%;
    margin-top: 6px;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--gold) !important; }

/* ── Success/Warning/Error alerts ── */
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* ── Main area default button (TTS etc) ── */
.main .stButton > button {
    background: var(--gold-subtle) !important;
    border: 1px solid var(--border-dim) !important;
    color: var(--gold) !important;
    border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
.main .stButton > button:hover {
    border-color: var(--gold) !important;
    box-shadow: 0 0 10px var(--gold-glow) !important;
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# AUTH GATE
# ════════════════════════════════════════════════════════════════════════════
if not is_logged_in():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="brand-icon">🤖</div>
            <div class="brand-name">AI RAG CHATBOT</div>
            <div class="brand-sub">Powered by LLaMA 3.3 70B</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(
            '<div style="text-align:center;font-size:0.75rem;color:var(--text-muted);padding:8px;">'
            '✦ Sign in to access your AI workspace ✦'
            '</div>', unsafe_allow_html=True
        )

    if st.session_state.auth_page == "register":
        show_register_page()
    else:
        show_login_page()
    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ════════════════════════════════════════════════════════════════════════════
session_id = st.session_state.session_id

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    # Brand
    st.markdown("""
    <div class="sidebar-brand">
        <div class="brand-icon">🤖</div>
        <div class="brand-name">AI RAG CHATBOT</div>
        <div class="brand-sub">LLaMA 3.3 70B · Groq · RAG</div>
    </div>
    """, unsafe_allow_html=True)

    # Profile
    st.markdown(
        f'<div class="profile-card">'
        f'<div class="pname">◈ {st.session_state.user_name}</div>'
        f'<div class="pemail">{st.session_state.user_email}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # Metrics
    docs = get_documents()
    chunks = count_chunks()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div class="metric-card"><div class="num">{len(docs)}</div>'
            f'<div class="lbl">Documents</div></div>',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f'<div class="metric-card"><div class="num">{chunks}</div>'
            f'<div class="lbl">Chunks</div></div>',
            unsafe_allow_html=True
        )

    # Upload
    st.markdown('<div class="section-heading">⬆ Upload</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "upload",
        type=["pdf", "txt", "md", "docx", "csv"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        for uf in uploaded_files:
            existing = [d["filename"] for d in get_documents()]
            if uf.name in existing:
                st.warning(f"'{uf.name}' already uploaded.")
                continue
            with st.spinner(f"Processing {uf.name}…"):
                try:
                    suffix = os.path.splitext(uf.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(uf.read())
                        tmp_path = tmp.name
                    text = load_file(tmp_path)
                    os.unlink(tmp_path)
                    chunks_list = chunk_text(text)
                    embeddings = embed_texts(chunks_list)
                    doc_id = save_document(uf.name, suffix.lstrip("."), len(chunks_list))
                    add_chunks(chunks_list, embeddings, uf.name, doc_id)
                    st.success(f"✅ {uf.name} — {len(chunks_list)} chunks")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    # Document list
    docs = get_documents()
    if docs:
        st.markdown('<div class="section-heading">◈ Documents</div>', unsafe_allow_html=True)
        for doc in docs:
            col_n, col_x = st.columns([5, 1])
            with col_n:
                st.markdown(
                    f'<div class="doc-chip">'
                    f'<span class="dname">📄 {doc["filename"]}</span>'
                    f'<span class="dmeta">{doc["chunk_count"]} chunks</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col_x:
                if st.button("✕", key=f"del_{doc['id']}", help="Remove"):
                    from rag.vector_store import delete_document
                    delete_document(doc["id"])
                    delete_document_record(doc["id"])
                    st.rerun()

    st.divider()

    # Clear / Reset
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("🧹  Clear Chat History", use_container_width=True, key="clear_chat_btn"):
        clear_history(session_id)
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
    if st.button("🗑️  Reset Everything", use_container_width=True, key="reset_all_btn"):
        reset_store()
        clear_history(session_id)
        st.session_state.messages = []
        import sqlite3 as _sq
        conn = _sq.connect("chat_history.db")
        conn.execute("DELETE FROM documents")
        conn.commit()
        conn.close()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown(
        '<div style="text-align:center;font-size:0.68rem;color:var(--text-muted);'
        'letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;">'
        'LLaMA 3.3 · Groq · ChromaDB · Streamlit'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("🚪  Logout", use_container_width=True, key="sidebar_logout"):
        logout_user()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ── Chat Header ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="chat-header">
    <div class="chat-header-icon">🤖</div>
    <div class="chat-header-text">
        <h1>GNANESWAR KOKKIRALA AI CHATBOT</h1>
        <p>Ask questions about your documents · Powered by LLaMA 3.3 70B via Groq API</p>
    </div>
    <div class="chat-header-badge">⚡ Groq</div>
</div>
""", unsafe_allow_html=True)

# Load history
if not st.session_state.messages:
    st.session_state.messages = get_history(session_id)

# ── Display messages ──────────────────────────────────────────────────────────
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "🧑"):
        st.markdown(msg["content"])

        if msg["role"] == "assistant":
            st.markdown('<div class="tts-btn">', unsafe_allow_html=True)
            btn_col, _ = st.columns([1, 9])
            with btn_col:
                if st.button("🔊 Listen", key=f"tts_{i}", help="Read aloud"):
                    st.session_state.tts_index = i
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.tts_index == i and msg["role"] == "assistant":
            with st.spinner("Generating audio…"):
                try:
                    audio_b64 = text_to_speech_base64(msg["content"])
                    st.markdown(get_audio_html(audio_b64), unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"TTS error: {e}")

# Welcome message
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(
            f"✦ **Welcome, {st.session_state.user_name}!**\n\n"
            "I'm **GapMind AI** — your intelligent document assistant powered by **LLaMA 3.3 70B via Groq**.\n\n"
            "📂 Upload your documents in the sidebar (PDF, DOCX, TXT, CSV) and ask me anything about them.\n\n"
            "⚡ Groq gives ultra-fast responses — try it!"
        )

# ── Browser mic + Chat input ─────────────────────────────────────────────────
from voice.stt import render_browser_mic
render_browser_mic(key="main_mic")

prompt = st.chat_input("Ask a question about your documents…")

if prompt:
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message(session_id, "user", prompt)

    hits = retrieve(prompt) if count_chunks() > 0 else []
    context = format_context(hits)
    sources_text = format_sources(hits)

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_response = ""

        history_for_llm = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        for chunk in chat(history_for_llm, context=context, stream=True):
            full_response += chunk
            placeholder.markdown(full_response + "▌")

        if sources_text:
            full_response += f"\n\n{sources_text}"

        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_message(session_id, "assistant", full_response)
    st.rerun()
