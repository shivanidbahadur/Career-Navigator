"""
app.py
Main entry point for the Streamlit app. Sets up the page config,
sidebar, state initialization, and auth guards.
"""

import streamlit as st
from core.state import init_state
from learning.auth import require_login, show_user_sidebar

# Page configuration must be the very first Streamlit command
st.set_page_config(page_title="AI Career Navigator", layout="wide")

# Initialize shared session state from M1's core engine
init_state()

# Apply auth guard and sidebar navigation provided by your module
require_login()
show_user_sidebar()

st.title("AI Career Navigator")

st.write(
    "Welcome! Fill in your profile, then explore career matches, "
    "your skill roadmap, jobs, resume, and mock interview."
)

# Safely check profile name from session state
profile = st.session_state.get("profile", {})
name = profile.get("name", "")

if name:
    st.write(f"Logged in as: **{name}**")
else:
    st.info("No profile yet — go to the Profile page to get started.")