import hashlib
import json
import os
import secrets

import streamlit as st

USERS_FILE = "data/users.json"
MIN_PASSWORD_LENGTH = 6

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
def hash_password(password, salt):
    """Scramble the password with the salt. One-way: cannot be reversed."""
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), 100000
    ).hex()


def register_user(name, email, password):
    """Create an account. Returns (True, "") or (False, error message)."""
    email = email.strip().lower()
    users = load_users()
    if email in users:
        return False, "An account with this email already exists. Please log in."

    salt = secrets.token_hex(16)  # random, different for every user
    users[email] = {
        "name": name.strip(),
        "salt": salt,
        "password_hash": hash_password(password, salt),
    }
    save_users(users)
    return True, ""


def check_login(email, password):
    """Return {"name", "email"} if the password is right, else None."""
    email = email.strip().lower()
    record = load_users().get(email)
    if record is None:
        return None
    attempt = hash_password(password, record["salt"])
    if secrets.compare_digest(attempt, record["password_hash"]):
        return {"name": record["name"], "email": email}
    return None


# ---------- Session helpers ----------
def is_logged_in():
    """True if someone has logged in."""
    return st.session_state.get("user") is not None


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
            if not name.strip():
                st.error("Please enter your name.")
            elif "@" not in new_email or "." not in new_email:
                st.error("Please enter a valid email.")
            elif len(new_password) < MIN_PASSWORD_LENGTH:
                st.error(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
            elif new_password != confirm:
                st.error("Passwords do not match.")
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
    """Remove the user and their data, then reload."""
    st.session_state.pop("user", None)
    for key in USER_DATA_KEYS:
        st.session_state.pop(key, None)
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
    if user:
        with st.sidebar:
            st.write(f"Logged in as **{user['name']}**")
            if st.button("Log out"):
                logout()