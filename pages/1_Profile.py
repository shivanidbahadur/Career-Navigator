import json
import os 
import streamlit as st

from learning.auth import require_login, show_user_sidebar

require_login()
show_user_sidebar()

st.title("Your Profile")
# ---------- Option lists (easy to edit) ----------
SKILL_OPTIONS = [
    "Python", "Java", "JavaScript", "SQL", "Git", "HTML", "CSS", "React",
    "Statistics", "Machine Learning", "Deep Learning", "Pandas",
    "Data Visualization", "Networking", "Linux", "AWS", "Docker",
]
INTEREST_OPTIONS = [
    "AI", "Web Development", "Data", "Cybersecurity", "Cloud",
    "Mobile Apps", "Game Development",
]
EXPERIENCE_OPTIONS = ["Fresher", "Internship", "Projects", "Work"]
DONT_KNOW = "I don't know"

# ---------- Skill normalization (M1's function, with a temporary fake) ----------
try:
    from core.skills import normalize_skills
except ImportError:
    def normalize_skills(skills):
        return [s.strip().title() for s in skills]

# ---------- Careers list ----------
def load_careers():
    """Return a list of {"career_id", "name"}. Uses M1's file if it exists."""
    path="data/careers.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [{"career_id": c["career_id"], "name": c["name"]} for c in data]
    # Fallback until M1's file exists
    return [
        {"career_id": "data_scientist", "name": "Data Scientist"},
        {"career_id": "web_developer", "name": "Web Developer"},
        {"career_id": "cloud_engineer", "name": "Cloud Engineer"},
    ]

careers = load_careers()
career_names = [c["name"] for c in careers]
name_to_id = {c["name"]: c["career_id"] for c in careers}

# Pre-fill name/email if we already have a profile (or a login later)
existing = st.session_state.get("profile", {})

# ---------- The form ----------
with st.form("profile_form"):
    name = st.text_input("Full name", value=existing.get("name", ""))
    email = st.text_input("Email", value=existing.get("email", ""))

    degree = st.text_input("Degree (e.g. B.Tech)")
    branch = st.text_input("Branch (e.g. Computer Science)")
    grad_year = st.number_input(
        "Graduation year", min_value=2020, max_value=2035, value=2027, step=1
    )

    selected_skills = st.multiselect("Skills you have", SKILL_OPTIONS)
    extra_skills = st.text_input(
        "Other skills (separate with commas)", placeholder="e.g. ML, Figma"
    )

    interests = st.multiselect("Interests", INTEREST_OPTIONS)
    experience = st.selectbox("Experience level", EXPERIENCE_OPTIONS)
    projects_text = st.text_area("Projects (one per line)")

    career_choice = st.selectbox("Career preference", [DONT_KNOW] + career_names)

    submitted = st.form_submit_button("Save profile")


# ---------- Handle submit ----------
if submitted:
    if not name.strip() or not email.strip():
        st.error("Please fill in your name and email.")
    else:
        # Merge multiselect + free-text skills
        typed = [s.strip() for s in extra_skills.split(",") if s.strip()]
        all_skills = normalize_skills(selected_skills + typed)

        # Remove duplicates but keep order
        unique_skills = list(dict.fromkeys(all_skills))

        # One project per line, skip blank lines
        projects = [p.strip() for p in projects_text.split("\n") if p.strip()]

        target = None if career_choice == DONT_KNOW else name_to_id[career_choice]

        st.session_state["profile"] = {
            "name": name.strip(),
            "email": email.strip(),
            "degree": degree.strip(),
            "branch": branch.strip(),
            "grad_year": int(grad_year),
            "skills": unique_skills,
            "interests": interests,
            "experience": experience,
            "projects": projects,
            "target_career": target,
        }
        st.success("Profile saved!")
        st.json(st.session_state["profile"])  # for testing; remove later