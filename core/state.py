"""
core/state.py
Sets up all the shared session_state keys with default values.
Every page in the app calls init_state() at the top so it can safely
read/write st.session_state without KeyError.
"""

import streamlit as st


def init_state():
    """Create every shared session_state key with a default value,
    but only if it doesn't already exist (so we don't wipe data on
    every page navigation)."""

    if "profile" not in st.session_state:
        st.session_state["profile"] = {
            "name": "",
            "email": "",
            "degree": "",
            "branch": "",
            "grad_year": "",
            "skills": [],
            "interests": [],
            "experience": "Fresher",
            "projects": [],
            "target_career": None,
        }

    if "progress" not in st.session_state:
        st.session_state["progress"] = {}

    if "interview_results" not in st.session_state:
        st.session_state["interview_results"] = []

    if "resume_generated" not in st.session_state:
        st.session_state["resume_generated"] = False