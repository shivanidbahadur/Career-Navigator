"""
AI Career Navigator
Main Streamlit entry point with a modern "Aurora Glass" 3D dashboard UI.
Existing authentication, state management, and feature modules are preserved.
"""

import streamlit as st
from core.state import init_state
from learning.auth import require_login, show_user_sidebar
from ui.theme import apply_theme, section_title, tilt_card, stat_card

# Page configuration must be the first Streamlit command.
st.set_page_config(
    page_title="AI Career Navigator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global styling + ambient 3D background (presentation only).
apply_theme()

# Initialize shared session state from the existing core engine.
init_state()

# Existing authentication and sidebar navigation are intentionally preserved.
require_login()
show_user_sidebar()

# -------------------------------------------------------------------
# Modern home page
# -------------------------------------------------------------------
profile = st.session_state.get("profile", {})
name = profile.get("name", "")
display_name = name if name else "Student"

st.markdown(
    f"""
    <div class="fg-hero fg-rise">
        <div class="fg-eyebrow">✦ Welcome back, {display_name}</div>
        <h1>Build your <span class="fg-gradient-text">career</span><br>with AI.</h1>
        <p>
            Discover suitable career paths, identify your skill gaps,
            build a personalized learning roadmap, prepare your resume,
            explore opportunities, and practice interviews — all in one place.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

section_title("Your Career Toolkit", "🧰")

features = [
    ("🎯", "Career Recommendations", "Find career paths that match your profile, skills and interests."),
    ("📊", "Skill-Gap Analysis", "Understand the skills you already have and the areas you need to improve."),
    ("🗺️", "Learning Roadmap", "Follow a personalized step-by-step plan toward your target career."),
    ("💼", "Jobs & Internships", "Explore opportunities that match your career profile."),
    ("📄", "Resume Builder", "Create a professional, ATS-friendly resume."),
    ("🎤", "AI Mock Interview", "Practice personalized interview questions and receive feedback."),
]

cols = st.columns(3, gap="medium")
for col, (icon, title, description) in zip(cols * 2, features):
    with col:
        tilt_card(icon, title, description)

section_title("Profile Status", "📡")

c1, c2, c3 = st.columns(3)
with c1:
    stat_card("Profile", "Complete" if name else "Not started")
with c2:
    stat_card("Career Journey", "Ready to explore")
with c3:
    stat_card("AI Interview", "Personalized")

if not name:
    st.info("Complete your Profile first to unlock personalized career guidance.")
