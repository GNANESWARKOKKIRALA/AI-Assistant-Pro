"""
auth/auth_utils.py — Password hashing, verification, and session helpers
"""
import re
import bcrypt
import streamlit as st
from auth.database import get_user_by_email


# ── Password Hashing ─────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """Hash a plain-text password with bcrypt. Returns the hash as a string."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8")
        )
    except Exception:
        return False


# ── Email Validation ─────────────────────────────────────────────────────────

def is_valid_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


# ── Session Management ───────────────────────────────────────────────────────

def init_session_state() -> None:
    """Initialize auth-related session state keys."""
    defaults = {
        "logged_in": False,
        "user_id": None,
        "user_name": None,
        "user_email": None,
        "auth_page": "login",  # "login" | "register"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login_user(user: dict) -> None:
    """Populate session state after successful login."""
    st.session_state.logged_in = True
    st.session_state.user_id = user["id"]
    st.session_state.user_name = user["name"]
    st.session_state.user_email = user["email"]


def logout_user() -> None:
    """Clear auth-related keys from session state."""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.user_email = None
    st.session_state.auth_page = "login"
    # Also clear chat session so user gets a fresh start
    if "messages" in st.session_state:
        st.session_state.messages = []
    if "session_id" in st.session_state:
        del st.session_state["session_id"]


def is_logged_in() -> bool:
    """Check if user is currently logged in."""
    return st.session_state.get("logged_in", False)


def authenticate(email: str, password: str):
    """
    Attempt to authenticate user by email + password.
    Returns user dict on success, None on failure.
    """
    user = get_user_by_email(email)
    if user and verify_password(password, user["password_hash"]):
        return user
    return None
