import hashlib
import json
import os
import re
import secrets
from datetime import datetime, timedelta
import time

import bcrypt
import streamlit as st
from streamlit_cookies_controller import CookieController

from core import db

MIN_PASSWORD_LENGTH = 6
MAX_NAME_LENGTH = 50
MAX_EMAIL_LENGTH = 100
MAX_PASSWORD_BYTES = 72  # bcrypt cannot handle more than 72 bytes
SESSIONS_FILE = "data/sessions.json"
COOKIE_NAME = "career_nav_session"
SESSION_DAYS = 7

# Data that belongs to one user. Cleared on logout so the next person
# starts fresh.
USER_DATA_KEYS = ["profile", "progress", "interview_results", "resume_generated"]


# ---------- Passwords & Database Auth ----------
def hash_password(password):
    """Hash with bcrypt (salt is built in). Returns text for storage."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, password_hash):
    """True if the password matches the stored hash. False on any bad data."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False
    
def register_user(name, email, password):
    """Create an account in SQLite. Returns (True, "") or (False, error message)."""
    email = email.strip().lower()
    existing_user = db.get_user_by_email(email)
    if existing_user:
        return False, "An account with this email already exists. Please log in."

    password_hash = hash_password(password)
    user_id = db.create_user(name.strip(), email, password_hash)
    if not user_id:
        return False, "Database error while creating user account."
        
    return True, ""


def check_login(email, password):
    """Return user dict including user_id if password is correct."""
    email = email.strip().lower()
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        return None
    record = db.get_user_by_email(email)
    if record is None:
        return None
    if verify_password(password, record["password_hash"]):
        return {
            "user_id": record["user_id"],
            "name": record["name"],
            "email": email
        }
    return None

# ---------- Persistent sessions (stay logged in) ----------
def _load_sessions():
    if not os.path.exists(SESSIONS_FILE):
        return {}
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError):
        return {}


def _save_sessions(sessions):
    os.makedirs("data", exist_ok=True)
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2)


def _hash_token(token):
    """Fast one-way hash. Tokens are long random strings, so SHA-256 is fine."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _store_session(token_hash, user, expires_at):
    sessions = _load_sessions()
    sessions[token_hash] = {
        "email": user["email"],
        "name": user["name"],
        "expires_at": expires_at.isoformat(),
    }
    _save_sessions(sessions)


def _find_session(token_hash):
    """Return the stored session dict, or None if missing or expired."""
    record = _load_sessions().get(token_hash)
    if record is None:
        return None
    try:
        if datetime.fromisoformat(record["expires_at"]) < datetime.now():
            _remove_session(token_hash)
            return None
    except (ValueError, KeyError):
        return None
    return record


def _remove_session(token_hash):
    sessions = _load_sessions()
    if token_hash in sessions:
        del sessions[token_hash]
        _save_sessions(sessions)


def _cookies():
    """One cookie controller per browser session."""
    if "_cookie_controller" not in st.session_state:
        st.session_state["_cookie_controller"] = CookieController(key="career_nav_cookies")
    return st.session_state["_cookie_controller"]


def start_session(user):
    """Called after a successful login or signup. Sets the stay-logged-in cookie."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=SESSION_DAYS)
    _store_session(_hash_token(token), user, expires_at)
    _cookies().set(COOKIE_NAME, token, max_age=SESSION_DAYS * 24 * 3600)
    st.session_state["session_token"] = token
    time.sleep(1)


def restore_session():
    """If a valid cookie exists, log the user back in. True if restored."""
    token = _cookies().get(COOKIE_NAME)
    if not token:
        return False
    record = _find_session(_hash_token(token))
    if record is None:
        return False
    st.session_state["user"] = {"name": record["name"], "email": record["email"]}
    st.session_state["session_token"] = token
    return True


def end_session():
    """Called on logout. Deletes the stored token and the cookie."""
    token = st.session_state.get("session_token") or _cookies().get(COOKIE_NAME)
    if token:
        _remove_session(_hash_token(token))
    _cookies().remove(COOKIE_NAME)
    time.sleep(1)

# ---------- Session helpers ----------
def is_logged_in():
    """True if someone has logged in."""
    return st.session_state.get("user") is not None

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_signup(name, email, password, confirm):
    """Return an error message, or None if everything is fine."""
    name = name.strip()
    email = email.strip()

    if not name:
        return "Please enter your name."
    if len(name) > MAX_NAME_LENGTH:
        return f"Name must be at most {MAX_NAME_LENGTH} characters."
    if not email:
        return "Please enter your email."
    if len(email) > MAX_EMAIL_LENGTH or not EMAIL_PATTERN.match(email):
        return "Please enter a valid email."
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        return "Password is too long (maximum 72 bytes)."
    if password != confirm:
        return "Passwords do not match."
    return None

def login_form():
    """Show Log in / Sign up tabs."""
    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_clicked = st.form_submit_button("Log in")

            if login_clicked:
                user = check_login(email, password)
                if user is None:
                    st.error("Wrong email or password.")
                else:
                    st.session_state["user"] = user
                    st.session_state["user_id"] = user["user_id"]  # <--- Add this line
                    st.session_state.pop("_just_logged_out", None)
                    start_session(user)
                    st.rerun()

    with tab_signup:
        with st.form("signup_form"):
            name = st.text_input("Name")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            signup_clicked = st.form_submit_button("Create account")

        if signup_clicked:
            error = validate_signup(name, new_email, new_password, confirm)
            if error:
                st.error(error)
            else:
                ok, message = register_user(name, new_email, new_password)
                if not ok:
                    st.error(message)
                else:
                    # Fetch user record to get the generated user_id
                    record = db.get_user_by_email(new_email)
                    new_user = {
                        "user_id": record["user_id"],
                        "name": name.strip(),
                        "email": new_email.strip().lower(),
                    }
                    st.session_state["user"] = new_user
                    st.session_state["user_id"] = record["user_id"]  # <--- Add this line
                    st.session_state.pop("_just_logged_out", None)            
                    start_session(new_user)
                    st.rerun()


def logout():
    """Remove the session cookie and ALL user data, then reload."""
    end_session()
    st.session_state.clear()
    st.session_state["_just_logged_out"] = True
    st.rerun()


def require_login():
    """Call at the top of every page. Restores a saved login, or shows the forms."""
    if not is_logged_in() and not st.session_state.get("_just_logged_out"):
        restore_session()
    if not is_logged_in():
        st.title("AI Career Navigator")
        login_form()
        st.stop()

def show_user_sidebar():
    """Show who is logged in, plus a Log out button, in the sidebar."""
    user = st.session_state.get("user")
    if not user:
        return

    with st.sidebar:
        st.write(f"Logged in as **{user['name']}**")
        if st.button("Log out", key="logout_btn"):
            logout()