"""
auth/login.py — Light mode Claude-style login
"""
import streamlit as st
from auth.auth_utils import authenticate, login_user


def show_login_page() -> None:
    _css()
    st.markdown("""
    <div class="auth-wrap">
        <div class="auth-logo">🤖</div>
        <h1 class="auth-title">Welcome back</h1>
        <p class="auth-sub">Sign in to AI Assistant Pro</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        email    = st.text_input("Email address", placeholder="you@example.com")
        password = st.text_input("Password",      placeholder="Your password", type="password")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Sign in", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Please fill in all fields.")
        else:
            user = authenticate(email.strip().lower(), password)
            if user:
                login_user(user)
                st.rerun()
            else:
                st.error("Invalid email or password.")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="auth-divider"><span>or</span></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown('<p class="auth-switch">Don\'t have an account?</p>', unsafe_allow_html=True)
    if st.button("Create account", key="goto_register", use_container_width=True):
        st.session_state.auth_page = "register"
        st.rerun()


def _css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    *, html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

    .stApp { background: #ffffff !important; color: #0d0d0d !important; }

    .main .block-container {
        max-width: 400px !important;
        padding-top: 52px !important;
        margin: 0 auto !important;
    }

    .auth-wrap { text-align: center; margin-bottom: 24px; }
    .auth-logo { font-size: 3rem; margin-bottom: 12px; display: block; }
    .auth-title {
        font-size: 1.55rem !important; font-weight: 700 !important;
        color: #0d0d0d !important; margin: 0 0 8px !important; letter-spacing: -0.4px;
    }
    .auth-sub { color: #666; font-size: 0.88rem; margin: 0; }

    div[data-testid="stForm"] {
        background: #f9f9f9 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 14px !important;
        padding: 22px !important;
    }
    div[data-testid="stForm"] label p {
        font-size: 0.85rem !important; font-weight: 500 !important; color: #0d0d0d !important;
    }
    div[data-testid="stForm"] input {
        background: #ffffff !important;
        border: 1.5px solid #d0d0d0 !important;
        color: #0d0d0d !important;
        border-radius: 8px !important;
        font-size: 0.93rem !important;
        height: 42px !important;
        padding: 0 12px !important;
    }
    div[data-testid="stForm"] input:focus {
        border-color: #0d0d0d !important;
        box-shadow: 0 0 0 3px rgba(0,0,0,0.08) !important;
    }
    div[data-testid="stForm"] button {
        background: #0d0d0d !important; color: #fff !important;
        border: none !important; border-radius: 8px !important;
        font-size: 0.95rem !important; font-weight: 600 !important; height: 44px !important;
    }
    div[data-testid="stForm"] button:hover { background: #333 !important; }

    .auth-divider {
        display: flex; align-items: center; gap: 12px; color: #bbb; font-size: 0.8rem;
    }
    .auth-divider::before, .auth-divider::after { content: ''; flex: 1; height: 1px; background: #e0e0e0; }
    .auth-switch { text-align: center; color: #888; font-size: 0.85rem; margin-bottom: 8px; }

    div[data-testid="stVerticalBlock"] > div:last-child .stButton > button {
        background: #ffffff !important; border: 1.5px solid #d0d0d0 !important;
        color: #0d0d0d !important; border-radius: 8px !important;
        font-size: 0.9rem !important; font-weight: 500 !important; height: 44px !important;
    }
    div[data-testid="stVerticalBlock"] > div:last-child .stButton > button:hover {
        background: #f5f5f5 !important; border-color: #aaa !important;
    }
    </style>
    """, unsafe_allow_html=True)