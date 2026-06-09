"""
auth/register.py — Light mode Claude-style register (matches login UI)
"""
import streamlit as st
from auth.auth_utils import hash_password, is_valid_email, login_user
from auth.database import create_user, get_user_by_email


def show_register_page() -> None:
    _css()
    st.markdown("""
    <div class="auth-wrap">
        <div class="auth-logo">🤖</div>
        <h1 class="auth-title">Create your account</h1>
        <p class="auth-sub">Start chatting with your documents</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("register_form"):
        name     = st.text_input("Full name",        placeholder="Your name")
        email    = st.text_input("Email address",    placeholder="you@example.com")
        password = st.text_input("Password",         placeholder="Min 6 characters", type="password")
        confirm  = st.text_input("Confirm password", placeholder="Repeat password",  type="password")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Create account", use_container_width=True)

    if submitted:
        err = None
        if not all([name, email, password, confirm]):
            err = "Please fill in all fields."
        elif len(name.strip()) < 2:
            err = "Name must be at least 2 characters."
        elif not is_valid_email(email):
            err = "Enter a valid email address."
        elif len(password) < 6:
            err = "Password must be at least 6 characters."
        elif password != confirm:
            err = "Passwords do not match."
        elif get_user_by_email(email.strip().lower()):
            err = "Email already registered. Sign in instead."
        if err:
            st.error(err)
        else:
            with st.spinner("Creating account…"):
                success = create_user(name.strip(), email.strip().lower(), hash_password(password))
            if success:
                login_user(get_user_by_email(email.strip().lower()))
                st.rerun()
            else:
                st.error("Something went wrong. Please try again.")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="auth-divider"><span>or</span></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown('<p class="auth-switch">Already have an account?</p>', unsafe_allow_html=True)
    if st.button("Sign in", key="goto_login", use_container_width=True):
        st.session_state.auth_page = "login"
        st.rerun()


def _css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    *, *::before, *::after { box-sizing: border-box !important; }
    html {
        -webkit-text-size-adjust: 100% !important;
        text-size-adjust: 100% !important;
        overflow-x: hidden !important;
    }
    body { overflow-x: hidden !important; }

    /* Force override everything — no system theme leaking */
    html, body, [class*="css"], * {
        font-family: 'Inter', sans-serif !important;
        color-scheme: light !important;
    }

    .stApp {
        background: #ffffff !important;
        color: #0d0d0d !important;
    }

    /* Kill any dark background from system theme */
    .stApp > div, .main, section.main {
        background: #ffffff !important;
    }
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }

    /* Center the auth form — fluid width, caps at 400px */
    .main .block-container {
        max-width: 400px !important;
        width: 100% !important;
        padding-top: 40px !important;
        padding-left: 16px !important;
        padding-right: 16px !important;
        padding-bottom: 40px !important;
        margin: 0 auto !important;
        background: #ffffff !important;
    }

    /* Header */
    .auth-wrap { text-align: center; margin-bottom: 24px; }
    .auth-logo { font-size: 3rem; margin-bottom: 12px; display: block; }
    .auth-title {
        font-size: 1.55rem !important;
        font-weight: 700 !important;
        color: #0d0d0d !important;
        margin: 0 0 8px !important;
        letter-spacing: -0.4px;
    }
    .auth-sub { color: #666 !important; font-size: 0.88rem; margin: 0; }

    /* Form card */
    div[data-testid="stForm"] {
        background: #f9f9f9 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 14px !important;
        padding: 22px !important;
        box-shadow: none !important;
    }

    /* Labels */
    div[data-testid="stForm"] label p,
    div[data-testid="stForm"] label {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #0d0d0d !important;
        background: transparent !important;
    }

    /* Inputs — font-size 16px prevents iOS zoom */
    div[data-testid="stForm"] input,
    div[data-testid="stForm"] input[type="text"],
    div[data-testid="stForm"] input[type="password"] {
        background: #ffffff !important;
        border: 1.5px solid #d0d0d0 !important;
        color: #0d0d0d !important;
        border-radius: 8px !important;
        font-size: 16px !important;
        height: 46px !important;
        padding: 0 12px !important;
        box-shadow: none !important;
        touch-action: manipulation !important;
        width: 100% !important;
    }
    div[data-testid="stForm"] input:focus {
        border-color: #0d0d0d !important;
        box-shadow: 0 0 0 3px rgba(0,0,0,0.08) !important;
        outline: none !important;
    }
    div[data-testid="stForm"] input::placeholder {
        color: #aaa !important;
    }

    /* Password eye icon container */
    div[data-testid="stForm"] [data-testid="stTextInput"] > div {
        background: #ffffff !important;
        border: 1.5px solid #d0d0d0 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stForm"] [data-testid="stTextInput"] > div > div {
        background: transparent !important;
    }
    div[data-testid="stForm"] [data-testid="stTextInput"] button {
        background: transparent !important;
        border: none !important;
        color: #888 !important;
        height: 44px !important;
        width: 44px !important;
        min-height: 44px !important;
        box-shadow: none !important;
        touch-action: manipulation !important;
    }

    /* Submit button */
    div[data-testid="stForm"] button[kind="primaryFormSubmit"],
    div[data-testid="stForm"] > div > div > div > button {
        background: #0d0d0d !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        height: 46px !important;
        min-height: 44px !important;
        box-shadow: none !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        font-family: 'Inter', sans-serif !important;
        touch-action: manipulation !important;
        width: 100% !important;
    }
    div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover {
        background: #333333 !important;
    }

    /* Divider */
    .auth-divider {
        display: flex;
        align-items: center;
        gap: 12px;
        color: #bbb;
        font-size: 0.8rem;
    }
    .auth-divider::before,
    .auth-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: #e0e0e0;
    }

    /* Switch text */
    .auth-switch {
        text-align: center;
        color: #888 !important;
        font-size: 0.85rem;
        margin-bottom: 8px;
    }

    /* Sign in button (outside form) */
    .stButton > button {
        background: #ffffff !important;
        border: 1.5px solid #d0d0d0 !important;
        color: #0d0d0d !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        height: 46px !important;
        min-height: 44px !important;
        box-shadow: none !important;
        font-family: 'Inter', sans-serif !important;
        touch-action: manipulation !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background: #f5f5f5 !important;
        border-color: #aaa !important;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden !important; }

    /* Small phones: reduce top padding */
    @media (max-width: 480px) {
        .main .block-container {
            padding-top: 20px !important;
            padding-left: 12px !important;
            padding-right: 12px !important;
        }
        .auth-logo { font-size: 2.4rem !important; margin-bottom: 8px !important; }
        .auth-title { font-size: 1.3rem !important; }
        div[data-testid="stForm"] { padding: 16px !important; }
    }

    /* Very small phones */
    @media (max-width: 360px) {
        .main .block-container {
            padding-top: 12px !important;
            padding-left: 8px !important;
            padding-right: 8px !important;
        }
        .auth-title { font-size: 1.2rem !important; }
        .auth-sub { font-size: 0.82rem !important; }
        div[data-testid="stForm"] { padding: 12px !important; }
    }
    </style>
    """, unsafe_allow_html=True)