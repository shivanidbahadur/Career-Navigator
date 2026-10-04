import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from employment.resume import generate_resume, analyze_resume
from ui.theme import apply_theme, section_title

st.set_page_config(
    page_title="AI Career Navigator - Resume",
    page_icon="📄",
    layout="wide",
)
apply_theme()

st.markdown(
    """
    <div class="fg-hero fg-rise" style="padding:34px 38px; margin-bottom:24px;">
        <div class="fg-eyebrow">✦ Resume Studio</div>
        <h1 style="font-size:clamp(30px,3.6vw,46px);">Build a resume that <span class="fg-gradient-text">gets noticed</span>.</h1>
        <p style="font-size:15.5px;">
            Add projects, generate a clean ATS-friendly resume, and get
            suggestions to make it stronger.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# Load the profile saved by the Profile page
if "profile" not in st.session_state or not st.session_state["profile"]:
    st.warning("Please complete and save your profile first.")
    st.stop()

saved_profile = st.session_state["profile"]

# Keep additional projects added through the Resume page
if "resume_extra_projects" not in st.session_state:
    st.session_state["resume_extra_projects"] = []

# Prepare profile data for resume generation
profile = {
    "name": saved_profile.get("name", ""),
    "email": saved_profile.get("email", ""),
    "degree": saved_profile.get("degree", ""),
    "branch": saved_profile.get("branch", ""),
    "grad_year": saved_profile.get("grad_year", ""),
    "skills": saved_profile.get("skills", []),
    "interests": saved_profile.get("interests", []),
    "experience": saved_profile.get("experience", "Fresher"),
    "projects": [
        (
            {
                "title": project.get("title", "Project"),
                "description": project.get("description", "")
            }
            if isinstance(project, dict)
            else {
                "title": str(project),
                "description": ""
            }
        )
        for project in saved_profile.get("projects", [])
    ] + st.session_state["resume_extra_projects"]
}

# Use the selected career
career_id = saved_profile.get("target_career") or "data_analyst"


st.subheader("Add a Project")

with st.form("project_form", clear_on_submit=True):
    proj_title = st.text_input("Project Title")
    proj_desc = st.text_area("Project Description")
    submitted = st.form_submit_button("Add Project")

    if submitted and proj_title.strip():
        project = {
            "title": proj_title.strip(),
            "description": proj_desc.strip()
        }
        st.session_state["resume_extra_projects"].append(project)
        st.session_state["resume_generated"] = False
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
