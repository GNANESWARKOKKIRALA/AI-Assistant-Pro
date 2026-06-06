"""
auth/register.py — Register Page (Gold/Space Theme)
"""
import streamlit as st
from auth.auth_utils import hash_password, is_valid_email, login_user
from auth.database import create_user, get_user_by_email


def show_register_page() -> None:
    _inject_css()

    st.markdown("""
    <div class="auth-hero">
        <div class="auth-icon">✦</div>
        <div class="auth-title">Join AI RAG CHATBOT</div>
        <div class="auth-tagline">✦ Create Your AI Workspace ✦</div>
        <div class="auth-subtitle">Start chatting with your documents today</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("register_form", clear_on_submit=False):
        name     = st.text_input("◈  Full Name",         placeholder="Your full name",        key="reg_name")
        email    = st.text_input("◈  Email Address",     placeholder="you@example.com",       key="reg_email")
        password = st.text_input("◈  Password",          placeholder="Minimum 6 characters",  type="password", key="reg_password")
        confirm  = st.text_input("◈  Confirm Password",  placeholder="Repeat your password",  type="password", key="reg_confirm")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✦  Create Account", use_container_width=True)

    if submitted:
        _handle_register(name, email, password, confirm)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="auth-switch">Already have an account?</div>', unsafe_allow_html=True)
    if st.button("⚡  Sign In Instead", key="goto_login", use_container_width=True):
        st.session_state.auth_page = "login"
        st.rerun()


def _handle_register(name, email, password, confirm):
    if not all([name, email, password, confirm]):
        st.error("⚠️ Please fill in all fields.")
        return
    if len(name.strip()) < 2:
        st.error("⚠️ Name must be at least 2 characters.")
        return
    if not is_valid_email(email):
        st.error("⚠️ Enter a valid email address.")
        return
    if len(password) < 6:
        st.error("⚠️ Password must be at least 6 characters.")
        return
    if password != confirm:
        st.error("⚠️ Passwords do not match.")
        return
    if get_user_by_email(email):
        st.error("❌ Email already registered. Please sign in.")
        return
    with st.spinner("Creating your workspace…"):
        pw_hash = hash_password(password)
        success = create_user(name, email, pw_hash)
    if success:
        st.success("✅ Account created! Signing you in…")
        user = get_user_by_email(email)
        login_user(user)
        st.rerun()
    else:
        st.error("❌ Registration failed. Try again.")


def _inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

    :root {
        --gold: #c9a84c; --gold-light: #f0c060; --gold-dark: #8b6914;
        --gold-glow: rgba(201,168,76,0.35); --gold-subtle: rgba(201,168,76,0.06);
        --bg-deep: #080608; --bg-card: #0e0c10;
        --border: rgba(201,168,76,0.3); --border-dim: rgba(201,168,76,0.12);
        --text-main: #e8dcc8; --text-dim: #8a7a60;
    }

    html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif !important; }
    .stApp {
        background: var(--bg-deep);
        background-image: radial-gradient(ellipse at 70% 30%, rgba(201,168,76,0.05) 0%, transparent 60%);
    }

    .main .block-container {
        max-width: 480px !important;
        padding-top: 30px !important;
        margin: 0 auto !important;
    }

    .auth-hero { text-align: center; margin-bottom: 24px; }
    .auth-icon {
        font-size: 4rem;
        color: var(--gold-light);
        filter: drop-shadow(0 0 20px var(--gold-glow));
        margin-bottom: 8px;
        display: block;
    }
    .auth-title {
        font-family: 'Cinzel', serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--gold-light);
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .auth-tagline {
        font-size: 0.72rem;
        color: var(--gold-dark);
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .auth-subtitle { color: var(--text-dim); font-size: 0.92rem; }

    div[data-testid="stForm"] {
        background: linear-gradient(135deg, #0e0b06, #120e08) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 28px 36px !important;
        position: relative;
        overflow: hidden;
    }
    div[data-testid="stForm"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--gold), transparent);
    }

    div[data-testid="stForm"] label p {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: var(--gold) !important;
        letter-spacing: 0.5px !important;
    }

    div[data-testid="stForm"] input {
        background: #070508 !important;
        border: 1px solid var(--border) !important;
        color: var(--text-main) !important;
        border-radius: 10px !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem !important;
        height: 48px !important;
        padding: 0 14px !important;
    }
    div[data-testid="stForm"] input:focus {
        border-color: var(--gold) !important;
        box-shadow: 0 0 16px var(--gold-glow) !important;
    }

    div[data-testid="stForm"] button {
        background: linear-gradient(135deg, var(--gold-dark), var(--gold)) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Cinzel', serif !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        height: 50px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stForm"] button:hover {
        filter: brightness(1.15) !important;
        box-shadow: 0 0 20px var(--gold-glow) !important;
    }

    .auth-switch {
        text-align: center;
        color: var(--text-dim);
        font-size: 0.88rem;
        margin-bottom: 10px;
    }

    div[data-testid="stVerticalBlock"] > div:last-child .stButton > button {
        background: transparent !important;
        border: 1px solid var(--border) !important;
        color: var(--gold) !important;
        border-radius: 10px !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        height: 50px !important;
        letter-spacing: 1px !important;
    }
    div[data-testid="stVerticalBlock"] > div:last-child .stButton > button:hover {
        border-color: var(--gold) !important;
        box-shadow: 0 0 14px var(--gold-glow) !important;
        color: var(--gold-light) !important;
    }
    </style>
    """, unsafe_allow_html=True)
