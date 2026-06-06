"""
app.py — AI Assistant Pro  |  Light mode — Claude/ChatGPT style
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
    page_title="AI Assistant Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_session_state()

if "session_id" not in st.session_state:
    st.session_state.session_id = new_session_id()
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    color-scheme: light !important;
}

/* ── Main background ── */
.stApp {
    background: #ffffff !important;
    color: #0d0d0d !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #f9f9f9 !important;
    border-right: 2px solid #1a1a1a !important;
}
section[data-testid="stSidebar"] > div {
    padding-top: 8px !important;
}

/* ── Sidebar brand ── */
.sb-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px 14px;
    border-bottom: 1.5px solid #1a1a1a;
    margin-bottom: 10px;
}
.sb-brand .icon { font-size: 1.4rem; }
.sb-brand .name { font-size: 0.95rem; font-weight: 600; color: #0d0d0d; }
.sb-brand .sub  { font-size: 0.65rem; color: #888; margin-top: 1px; }

/* ── Profile card ── */
.profile-card {
    background: #f0f0f0;
    border: 1.5px solid #1a1a1a;
    border-radius: 10px;
    padding: 10px 13px;
    margin: 0 8px 10px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.profile-avatar {
    width: 32px; height: 32px;
    background: #0d0d0d;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.78rem; font-weight: 700; color: white;
    flex-shrink: 0;
}
.profile-info .pname  { font-size: 0.83rem; font-weight: 600; color: #0d0d0d; }
.profile-info .pemail { font-size: 0.7rem; color: #888; margin-top: 1px; }

/* ── Metrics ── */
.metric-row { display: flex; gap: 8px; margin: 0 8px 10px; }
.metric-card {
    flex: 1;
    background: #f0f0f0;
    border: 1.5px solid #1a1a1a;
    border-radius: 8px;
    padding: 10px 8px;
    text-align: center;
}
.metric-card .num { font-size: 1.4rem; font-weight: 700; color: #0d0d0d; line-height: 1; }
.metric-card .lbl { font-size: 0.63rem; color: #888; margin-top: 3px; text-transform: uppercase; letter-spacing: 0.5px; }

/* ── Sidebar section label ── */
.sb-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 8px 16px 4px;
}

/* ── Doc chip ── */
.doc-chip {
    background: #f0f0f0;
    border: 1.5px solid #1a1a1a;
    border-radius: 7px;
    padding: 7px 10px;
    margin: 3px 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.78rem;
}
.doc-chip .dname {
    color: #0d0d0d; font-weight: 500;
    white-space: nowrap; overflow: hidden;
    text-overflow: ellipsis; max-width: 150px;
}
.doc-chip .dmeta { color: #888; font-size: 0.68rem; flex-shrink: 0; margin-left: 6px; }

/* ── File uploader ── */
div[data-testid="stFileUploader"] {
    background: #f5f5f5 !important;
    border: 1.5px dashed #1a1a1a !important;
    border-radius: 10px !important;
    margin: 0 8px;
}
div[data-testid="stFileUploader"] label { color: #888 !important; }
div[data-testid="stFileUploader"] p     { color: #555 !important; }

/* ── ALL sidebar buttons ── */
section[data-testid="stSidebar"] .stButton > button {
    background: #ffffff !important;
    color: #0d0d0d !important;
    border: 1.5px solid #1a1a1a !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    height: 38px !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #f0f0f0 !important;
    border-color: #000 !important;
}

/* Clear */
.btn-clear > button { color: #b45309 !important; border-color: #b45309 !important; }
.btn-clear > button:hover { background: #fff7ed !important; }

/* Reset */
.btn-reset > button { color: #dc2626 !important; border-color: #dc2626 !important; }
.btn-reset > button:hover { background: #fff1f1 !important; }

/* Logout */
.btn-logout > button {
    background: #fff1f1 !important;
    color: #dc2626 !important;
    border-color: #dc2626 !important;
    height: 40px !important;
    font-weight: 600 !important;
}
.btn-logout > button:hover { background: #ffe4e4 !important; }

/* Delete doc */
section[data-testid="stSidebar"] .del-btn > button {
    background: transparent !important;
    border: none !important;
    color: #aaa !important;
    font-size: 0.75rem !important;
    height: 26px !important;
    width: 26px !important;
    padding: 0 !important;
    min-width: unset !important;
}
section[data-testid="stSidebar"] .del-btn > button:hover {
    color: #dc2626 !important;
    background: #fff1f1 !important;
    border-radius: 4px !important;
}

/* ── Main chat area ── */
.main .block-container {
    max-width: 760px !important;
    margin: 0 auto !important;
    padding: 24px 24px 8px !important;
    background: #ffffff !important;
}

/* ── Messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 10px 0 !important;
    margin: 0 !important;
}
[data-testid="stChatMessage"] p {
    color: #0d0d0d !important;
    font-size: 0.97rem !important;
    line-height: 1.75 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #f7f7f7 !important;
    border-radius: 12px !important;
    border: 1.5px solid #1a1a1a !important;
    padding: 14px 16px !important;
    margin-bottom: 4px !important;
}

/* ── Native chat input ── */
div[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 2px solid #1a1a1a !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.10) !important;
    outline: none !important;
}
div[data-testid="stChatInput"]:focus-within {
    border-color: #1a1a1a !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.12) !important;
    outline: none !important;
}
/* Kill Streamlit's inner focus ring / orange outline completely */
div[data-testid="stChatInput"] > div,
div[data-testid="stChatInput"] > div:focus-within,
div[data-testid="stChatInput"] > div > div,
div[data-testid="stChatInput"] > div > div:focus-within {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}
div[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: #0d0d0d !important;
    font-size: 0.97rem !important;
    caret-color: #0d0d0d !important;
}
div[data-testid="stChatInput"] textarea:focus {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}
div[data-testid="stChatInput"] textarea::placeholder { color: #aaa !important; }
div[data-testid="stChatInput"] button {
    background: #0d0d0d !important;
    border-radius: 8px !important;
    color: white !important;
    border: none !important;
}
div[data-testid="stChatInput"] button:hover { background: #333 !important; }

/* ── Mic bar (custom component above chat input) ── */
iframe[title="render_mic"] {
    border: none !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* ── Divider ── */
hr { border-color: #1a1a1a !important; margin: 8px 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #ccc; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #888; }

/* ── Alerts ── */
div[data-testid="stAlert"] { border-radius: 8px !important; font-size: 0.88rem !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #0d0d0d !important; }

/* ── Welcome card ── */
.welcome-card { text-align: center; padding: 60px 24px 40px; }
.welcome-card .wc-icon { font-size: 3.2rem; margin-bottom: 16px; }
.welcome-card h2 {
    font-size: 1.6rem; font-weight: 700;
    color: #0d0d0d; margin-bottom: 10px; letter-spacing: -0.5px;
}
.welcome-card p { font-size: 0.9rem; color: #666; line-height: 1.65; }
.welcome-pills { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 22px; }
.welcome-pill {
    background: #f5f5f5;
    border: 1.5px solid #1a1a1a;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.78rem;
    color: #555;
    cursor: default;
}

#MainMenu, footer { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)


# ── Auth gate ────────────────────────────────────────────────────
if not is_logged_in():
    with st.sidebar:
        st.markdown("""
        <div class="sb-brand">
            <div class="icon">🤖</div>
            <div>
                <div class="name">AI Assistant Pro</div>
                <div class="sub">LLaMA 3.3 70B · Groq</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    if st.session_state.auth_page == "register":
        show_register_page()
    else:
        show_login_page()
    st.stop()


# ── Sidebar ──────────────────────────────────────────────────────
session_id = st.session_state.session_id

with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
        <div class="icon">🤖</div>
        <div>
            <div class="name">AI Assistant Pro</div>
            <div class="sub">LLaMA 3.3 70B · Groq · RAG</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    initials = (st.session_state.user_name or "U")[:2].upper()
    st.markdown(
        f'<div class="profile-card">'
        f'<div class="profile-avatar">{initials}</div>'
        f'<div class="profile-info">'
        f'<div class="pname">{st.session_state.user_name}</div>'
        f'<div class="pemail">{st.session_state.user_email}</div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

    docs   = get_documents()
    chunks = count_chunks()
    st.markdown(
        f'<div class="metric-row">'
        f'<div class="metric-card"><div class="num">{len(docs)}</div><div class="lbl">Docs</div></div>'
        f'<div class="metric-card"><div class="num">{chunks}</div><div class="lbl">Chunks</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="sb-label">Upload Documents</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "upload", type=["pdf","txt","md","docx","csv"],
        accept_multiple_files=True, label_visibility="collapsed"
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
                        tmp.write(uf.read()); tmp_path = tmp.name
                    text        = load_file(tmp_path); os.unlink(tmp_path)
                    chunks_list = chunk_text(text)
                    embeddings  = embed_texts(chunks_list)
                    doc_id      = save_document(uf.name, suffix.lstrip("."), len(chunks_list))
                    add_chunks(chunks_list, embeddings, uf.name, doc_id)
                    st.success(f"✅ {uf.name} · {len(chunks_list)} chunks")
                except Exception as e:
                    st.error(f"❌ {e}")

    docs = get_documents()
    if docs:
        st.markdown('<div class="sb-label">Your Documents</div>', unsafe_allow_html=True)
        for doc in docs:
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(
                    f'<div class="doc-chip">'
                    f'<span class="dname">📄 {doc["filename"]}</span>'
                    f'<span class="dmeta">{doc["chunk_count"]}c</span>'
                    f'</div>', unsafe_allow_html=True
                )
            with c2:
                st.markdown('<div class="del-btn">', unsafe_allow_html=True)
                if st.button("✕", key=f"del_{doc['id']}"):
                    from rag.vector_store import delete_document
                    delete_document(doc["id"])
                    delete_document_record(doc["id"])
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="btn-clear">', unsafe_allow_html=True)
    if st.button("🧹  Clear Chat", use_container_width=True, key="btn_clear"):
        clear_history(session_id)
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="btn-reset">', unsafe_allow_html=True)
    if st.button("🗑️  Reset Everything", use_container_width=True, key="btn_reset"):
        reset_store(); clear_history(session_id); st.session_state.messages = []
        import sqlite3 as _sq
        conn = _sq.connect("chat_history.db")
        conn.execute("DELETE FROM documents"); conn.commit(); conn.close()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown(
        '<div style="font-size:0.63rem;color:#bbb;text-align:center;padding:2px 0 8px;">'
        'GapMind AI · LLaMA 3.3 70B · Groq · ChromaDB'
        '</div>', unsafe_allow_html=True
    )

    st.markdown('<div class="btn-logout">', unsafe_allow_html=True)
    if st.button("→  Sign Out", use_container_width=True, key="btn_logout"):
        logout_user(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ── Chat ─────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.session_state.messages = get_history(session_id)

if not st.session_state.messages:
    st.markdown(f"""
    <div class="welcome-card">
        <div class="wc-icon">🤖</div>
        <h2>How can I help you today?</h2>
        <p>Upload your documents in the sidebar and ask me anything.<br>
        Powered by <strong>LLaMA 3.3 70B</strong> via Groq.</p>
        <div class="welcome-pills">
            <span class="welcome-pill">📄 Upload a PDF</span>
            <span class="welcome-pill">💬 Ask a question</span>
            <span class="welcome-pill">🎙️ Voice input</span>
            <span class="welcome-pill">⚡ Groq fast inference</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "🧑"):
            st.markdown(msg["content"])


# ── Mic + Chat input row ──────────────────────────────────────────
# The mic is injected as an overlay INSIDE the chat input via JS.
# We render a hidden component that hooks into the parent DOM.
import streamlit.components.v1 as components

components.html("""
<script>
(function injectMic() {
    const parent = window.parent.document;

    function attachMic(inputDiv) {
        // Remove any stale mic button (left over from previous render)
        const old = parent.getElementById('gm-mic-btn');
        if (old) old.remove();

        // Style the input container
        inputDiv.style.display = 'flex';
        inputDiv.style.alignItems = 'center';
        inputDiv.style.padding = '4px 8px';
        inputDiv.style.gap = '6px';

        // Create mic button
        const mic = parent.createElement('button');
        mic.id = 'gm-mic-btn';
        mic.innerHTML = '🎙️';
        mic.title = 'Voice input';
        mic.style.cssText = [
            'flex-shrink:0',
            'order:-1',
            'background:transparent',
            'border:none',
            'font-size:1.2rem',
            'cursor:pointer',
            'padding:4px 6px',
            'border-radius:8px',
            'line-height:1',
            'transition:background 0.15s',
        ].join(';');
        mic.onmouseenter = () => { if (!mic._listening) mic.style.background = '#f0f0f0'; };
        mic.onmouseleave = () => { if (!mic._listening) mic.style.background = 'transparent'; };

        inputDiv.insertBefore(mic, inputDiv.firstChild);

        // Speech recognition
        let recognition = null;
        let listening = false;

        function resetMic() {
            listening = false;
            mic._listening = false;
            mic.innerHTML = '🎙️';
            mic.style.background = 'transparent';
            recognition = null;
        }

        mic.addEventListener('click', () => {
            const SR = window.parent.SpeechRecognition || window.parent.webkitSpeechRecognition;
            if (!SR) { alert('Voice input not supported. Please use Chrome.'); return; }

            if (listening) {
                recognition && recognition.stop();
                return;
            }

            recognition = new SR();
            recognition.lang = 'en-US';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onstart = () => {
                listening = true;
                mic._listening = true;
                mic.innerHTML = '⏹️';
                mic.style.background = '#fee2e2';
            };

            recognition.onresult = (e) => {
                const text = e.results[0][0].transcript;
                const ta = parent.querySelector('div[data-testid="stChatInput"] textarea');
                if (ta) {
                    const nativeSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, 'value').set;
                    nativeSetter.call(ta, text);
                    ta.dispatchEvent(new Event('input', { bubbles: true }));
                    ta.focus();
                }
            };

            recognition.onerror = () => resetMic();
            recognition.onend   = () => resetMic();

            try { recognition.start(); } catch(e) { resetMic(); }
        });
    }

    // Watch for the chat input to appear / re-appear after every Streamlit rerun.
    // We use a MutationObserver on the body so we catch DOM rebuilds, plus
    // an interval as a fallback for the initial load.
    let lastInputDiv = null;

    function checkAndInject() {
        const inputDiv = parent.querySelector('div[data-testid="stChatInput"]');
        if (!inputDiv) return;

        const micAlreadyInside = inputDiv.querySelector('#gm-mic-btn');
        if (micAlreadyInside && lastInputDiv === inputDiv) return; // already injected into this exact node

        lastInputDiv = inputDiv;
        attachMic(inputDiv);
    }

    // Interval for initial load
    const iv = setInterval(() => {
        checkAndInject();
        if (parent.querySelector('#gm-mic-btn')) clearInterval(iv);
    }, 200);

    // MutationObserver catches every Streamlit rerun DOM update
    const observer = new MutationObserver(() => checkAndInject());
    observer.observe(parent.body, { childList: true, subtree: true });
})();
</script>
""", height=0)

prompt = st.chat_input("AI Assistant Pro…")

if prompt:
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message(session_id, "user", prompt)

    hits         = retrieve(prompt) if count_chunks() > 0 else []
    context      = format_context(hits)
    sources_text = format_sources(hits)

    with st.chat_message("assistant", avatar="🤖"):
        placeholder   = st.empty()
        full_response = ""
        history_for_llm = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        for chunk in chat(history_for_llm, context=context, stream=True):
            full_response += chunk
            placeholder.markdown(full_response + "▌")
        if sources_text:
            full_response += f"\n\n{sources_text}"
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_message(session_id, "assistant", full_response)
    st.rerun()
