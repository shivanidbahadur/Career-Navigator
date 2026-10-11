import json
import os
import re

import bcrypt
import streamlit as st

USERS_FILE = "data/users.json"
MIN_PASSWORD_LENGTH = 6
MAX_NAME_LENGTH = 50
MAX_EMAIL_LENGTH = 100
MAX_PASSWORD_BYTES = 72  # bcrypt cannot handle more than 72 bytes


# Data that belongs to one user. Cleared on logout so the next person
# starts fresh.
USER_DATA_KEYS = ["profile", "progress", "interview_results", "resume_generated"]


# ---------- Storage ----------
def load_users():
    """Read all accounts from the JSON file ({} if there are none yet)."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    os.makedirs("data", exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


# ---------- Passwords ----------
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
    """Create an account. Returns (True, "") or (False, error message)."""
    email = email.strip().lower()
    users = load_users()
    if email in users:
        return False, "An account with this email already exists. Please log in."

    users[email] = {
        "name": name.strip(),
        "password_hash": hash_password(password),
    }
    save_users(users)
    return True, ""


def check_login(email, password):
    """Return {"name", "email"} if the password is right, else None."""
    email = email.strip().lower()
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        return None
    record = load_users().get(email)
    if record is None:
        return None
    if verify_password(password, record["password_hash"]):
        return {"name": record["name"], "email": email}
    return None


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
                    # Log them in straight away
                    st.session_state["user"] = {
                        "name": name.strip(),
                        "email": new_email.strip().lower(),
                    }
                    st.rerun()


def logout():
    """Remove the user and ALL their data, then reload."""
    st.session_state.clear()
    st.rerun()


def require_login():
    """Call at the top of every page. Shows login and stops if not logged in."""
    if not is_logged_in():
        st.title("AI Career Navigator")
        login_form()
        st.stop()  # nothing below this line runs until the user logs in


def show_user_sidebar():
    """Show who is logged in, plus a Log out button, in the sidebar."""
    user = st.session_state.get("user")
    if not user:
        return

    with st.sidebar:
        st.write(f"Logged in as **{user['name']}**")
        if st.button("Log out", key="logout_btn"):
            logout()