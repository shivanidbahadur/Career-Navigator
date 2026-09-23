import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from employment.resume import generate_resume, analyze_resume

st.title("Resume Builder")

# --- Temporary hardcoded profile for testing (Step 7 connects real state) ---
if "resume_profile" not in st.session_state:
    st.session_state.resume_profile = {
        "name": "Priya Sharma",
        "email": "priya@example.com",
        "degree": "B.Tech",
        "branch": "Computer Science",
        "grad_year": 2027,
        "skills": ["Python", "SQL", "Excel"],
        "projects": [],
        "experience": "Fresher"
    }
career_id = "data_analyst"
# -----------------------------------------------------------------------

profile = st.session_state.resume_profile

st.subheader("Add a Project")
with st.form("project_form", clear_on_submit=True):
    proj_title = st.text_input("Project Title")
    proj_desc = st.text_area("Project Description")
    submitted = st.form_submit_button("Add Project")
    if submitted and proj_title:
        profile["projects"].append({"title": proj_title, "description": proj_desc})
        st.success(f"Added project: {proj_title}")

if profile["projects"]:
    st.write("**Current projects:**")
    for p in profile["projects"]:
        st.write(f"- {p['title']}: {p['description']}")

st.subheader("Generate Resume")
if st.button("Generate Resume"):
    resume_html = generate_resume(profile, career_id)
    st.session_state["resume_generated"] = True
    st.session_state["resume_html"] = resume_html

if st.session_state.get("resume_generated"):
    st.subheader("Preview")
    st.iframe(st.session_state["resume_html"], height=500)

    st.download_button(
        label="Download Resume (HTML)",
        data=st.session_state["resume_html"],
        file_name="resume.html",
        mime="text/html"
    )

    st.subheader("Suggestions")
    suggestions = analyze_resume(profile, career_id)
    if suggestions:
        for s in suggestions:
            st.write(f"- {s['suggestion']}")
    else:
        st.write("No suggestions right now — either you're fully matched, or career data isn't loaded yet.")