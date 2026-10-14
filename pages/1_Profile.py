import os
import json
import streamlit as st
from core import db

from learning.auth import require_login, show_user_sidebar
from ui.theme import apply_theme, section_title, stat_card

# ============================================================
# PAGE CONFIG + THEME (UI only)
# ============================================================

st.set_page_config(
    page_title="AI Career Navigator - Profile",
    page_icon="👤",
    layout="wide",
)
apply_theme()


# ============================================================
# LOGIN / SIDEBAR
# ============================================================

require_login()
show_user_sidebar()


# ============================================================
# PAGE
# ============================================================

st.markdown(
    """
    <div class="fg-hero fg-rise" style="padding:34px 38px; margin-bottom:24px;">
        <div class="fg-eyebrow">✦ Profile Setup</div>
        <h1 style="font-size:clamp(30px,3.6vw,46px);">Tell us about <span class="fg-gradient-text">yourself</span>.</h1>
        <p style="font-size:15.5px;">
            Create your profile so AI Career Navigator can personalize
            career guidance, learning gaps, and interview practice.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)



SKILL_OPTIONS = [
    "Python",
    "Java",
    "JavaScript",
    "C",
    "C++",
    "SQL",
    "Git",
    "HTML",
    "CSS",
    "React",
    "Node.js",
    "REST API",
    "Data Structures",
    "Algorithms",
    "Object Oriented Programming",
    "Problem Solving",
    "Machine Learning",
    "Deep Learning",
    "Statistics",
    "Data Visualization",
    "Pandas",
    "Power BI",
    "Tableau",
    "Excel",
    "Google Sheets",
    "Data Cleaning",
    "Communication",
    "Business Acumen",
    "Critical Thinking",
    "Cloud Computing",
    "Linux",
    "Networking",
    "Docker",
    "Kubernetes",
    "Security",
    "Cryptography",
    "Ethical Hacking",
    "Scripting",
    "System Design",
    "Testing",
    "Debugging",
    "Software Engineering",
    "Git",
    "TensorFlow",
    "CI/CD",
    "Requirements Gathering",
    "Mobile Development",
    "UI Design",
]


EXPERIENCE_OPTIONS = [
    "Beginner",
    "Intermediate",
    "Advanced",
    "Internship",
    "Fresher",
    "Working Professional",
]


INTEREST_OPTIONS = [
    "AI", "Data", "Software", "Web", "Cloud", 
    "Cybersecurity", "Business", "Research", "Design", 
    "Mobile", "Engineering", "Security", "Infrastructure"
]

# ---------- Skill normalization (M1's function, with a temporary fake) ----------
try:
    from core.skills import normalize_skills
except ImportError:
    def normalize_skills(skills):
        return [s.strip().title() for s in skills]

DONT_KNOW = "I don't know yet"


# ============================================================
# LOAD CAREERS
# ============================================================

def load_careers():
    """Return a list of {"career_id", "name"}. Uses M1's file if it exists."""
    path="data/careers.json"
    if os.path.exists(path):

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return [
                {
                    "career_id": career["career_id"],
                    "name": career["name"]
                }
                for career in data
                if "career_id" in career and "name" in career
            ]

        except Exception as exc:

            st.error(
                f"Unable to load careers.json: {exc}"
            )

    # Fallback only if careers.json cannot be loaded
    return [
        {
            "career_id": "data_analyst",
            "name": "Data Analyst"
        },
        {
            "career_id": "web_developer",
            "name": "Web Developer"
        },
        {
            "career_id": "cloud_engineer",
            "name": "Cloud Engineer"
        },
    ]


# ============================================================
# PREPARE CAREER DATA
# ============================================================

careers = load_careers()

career_names = [
    career["name"]
    for career in careers
]

name_to_id = {
    career["name"]: career["career_id"]
    for career in careers
}

id_to_name = {
    career["career_id"]: career["name"]
    for career in careers
}


# ============================================================
# EXISTING PROFILE
# ============================================================

existing = st.session_state.get(
    "profile",
    {}
)

existing_skills = existing.get(
    "skills",
    []
)

existing_interests = existing.get(
    "interests",
    []
)

existing_target = existing.get(
    "target_career"
)

existing_target_name = existing.get(
    "target_career_name"
)

# Convert existing career ID to career name
if existing_target and not existing_target_name:
    existing_target_name = id_to_name.get(
        existing_target
    )


# ============================================================
# INITIALIZE SESSION STATE FOR PROJECTS
# ============================================================

existing_projects = existing.get("projects", [])
if not isinstance(existing_projects, list):
    existing_projects = []

if "form_projects" not in st.session_state or st.session_state.get("_profile_loaded") != existing:
    formatted_projects = []
    for p in existing_projects:
        if isinstance(p, dict):
            formatted_projects.append(p)
        elif isinstance(p, str) and ":" in p:
            parts = p.split(":", 1)
            formatted_projects.append({"title": parts[0].strip(), "description": parts[1].strip()})
        elif isinstance(p, str) and p.strip():
            formatted_projects.append({"title": p.strip(), "description": ""})
    st.session_state["form_projects"] = formatted_projects if formatted_projects else []
    st.session_state["_profile_loaded"] = existing


# ============================================================
# PROFILE LAYOUT (Natural Order - No st.form wrapper)
# ============================================================

st.subheader("Personal Information")

name = st.text_input(
    "Full Name",
    value=existing.get("name", "")
)

email = st.text_input(
    "Email",
    value=existing.get("email", "")
)

phone = st.text_input(
    "Phone Number",
    value=existing.get("phone", ""),
    placeholder="+91 9876543210"
)

linkedin = st.text_input(
    "LinkedIn Profile URL",
    value=existing.get("linkedin", ""),
    placeholder="https://linkedin.com/in/username"
)

github = st.text_input(
    "GitHub Profile URL",
    value=existing.get("github", ""),
    placeholder="https://github.com/username"
)

degree = st.text_input(
    "Degree / Course",
    value=existing.get("degree", "B.Tech Computer Science and Engineering")
)

institution = st.text_input(
    "Institution Name",
    value=existing.get("institution", "")
)

grad_year = st.text_input(
    "Expected Graduation Year",
    value=existing.get("grad_year", "")
)

st.subheader("Experience & Internships (Optional)")

experience_title = st.text_input(
    "Role / Title",
    value=existing.get("experience_title", ""),
    placeholder="e.g., Data Analytics Intern"
)

experience_company = st.text_input(
    "Company / Organization Name",
    value=existing.get("experience_company", ""),
    placeholder="e.g., Learn Depth"
)

experience_desc = st.text_area(
    "Experience Description / Key Contributions",
    value=existing.get("experience_desc", ""),
    placeholder="e.g., Spearheaded dataset analysis and outlier detection using Python and pandas."
)


# ============================================================
# PROJECTS SECTION (Placed naturally right here)
# ============================================================

st.subheader("Projects (Optional)")
st.markdown("Add any projects you've worked on, or leave blank if you're just starting out.")

updated_projects = []
for i, proj in enumerate(st.session_state["form_projects"]):
    col1, col2, col3 = st.columns([1, 2, 0.5])
    with col1:
        title = st.text_input(f"Project Name {i+1}", value=proj.get("title", ""), key=f"proj_title_{i}")
    with col2:
        desc = st.text_input(f"Description {i+1}", value=proj.get("description", ""), max_chars=150, key=f"proj_desc_{i}")
    with col3:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        if st.button("Remove", key=f"del_proj_{i}"):
            st.session_state["form_projects"].pop(i)
            st.rerun()

    if title.strip() or desc.strip():
        updated_projects.append({"title": title.strip(), "description": desc.strip()})

if st.button("Add Project"):
    st.session_state["form_projects"].append({"title": "", "description": ""})
    st.rerun()

st.write("---")


# ============================================================
# SKILLS
# ============================================================

st.subheader("Skills")

valid_existing_skills = [
    skill
    for skill in existing_skills
    if skill in SKILL_OPTIONS
]

selected_skills = st.multiselect(
    "Select your current skills",
    options=SKILL_OPTIONS,
    default=valid_existing_skills,
    help=(
        "Select only skills you currently have. "
        "The system will compare these with your target "
        "career requirements."
    )
)


# ============================================================
# INTERESTS
# ============================================================

st.subheader("Interests")

valid_existing_interests = [
    interest
    for interest in existing_interests
    if interest in INTEREST_OPTIONS
]

interests = st.multiselect(
    "Select your interests",
    options=INTEREST_OPTIONS,
    default=valid_existing_interests
)


# ============================================================
# EXPERIENCE
# ============================================================

st.subheader("Experience")

current_experience = existing.get(
    "experience",
    "Beginner"
)

if current_experience not in EXPERIENCE_OPTIONS:
    current_experience = "Beginner"

experience = st.selectbox(
    "Experience level",
    EXPERIENCE_OPTIONS,
    index=EXPERIENCE_OPTIONS.index(
        current_experience
    )
)


# ============================================================
# CAREER
# ============================================================

st.subheader("Career Goal")

career_options = [
    DONT_KNOW
] + career_names

if existing_target_name in career_names:
    default_career = existing_target_name
else:
    default_career = DONT_KNOW

default_index = career_options.index(
    default_career
)

career_choice = st.selectbox(
    "Career preference",
    career_options,
    index=default_index
)


# ============================================================
# SUBMIT BUTTON
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)
submitted = st.button(
    "💾 Save Profile",
    use_container_width=True,
    type="primary"
)


# ============================================================
# SAVE PROFILE
# ============================================================

if submitted:

    # Clean structured projects (fully optional)
    final_projects = [
        {"title": p["title"].strip(), "description": p["description"].strip()}
        for p in updated_projects
        if p.get("title") and p.get("title").strip()
    ]

    # Convert career name → career_id
    if career_choice == DONT_KNOW:
        target = None
        target_career_name = None
    else:
        target = name_to_id.get(
            career_choice
        )
        target_career_name = career_choice


    # Remove duplicate skills while preserving order
    unique_skills = list(
        dict.fromkeys(selected_skills)
    )


    # --------------------------------------------------------
    # SAVE COMPLETE PROFILE
    # --------------------------------------------------------

    profile = {
        "name": name.strip(),
        "email": email.strip(),
        
        # --- CONTACT & EDUCATION KEYS ---
        "phone": phone.strip(),
        "linkedin": linkedin.strip(),
        "github": github.strip(),
        "degree": degree.strip(),
        "institution": institution.strip(),
        "grad_year": grad_year.strip(),
        "experience_title": experience_title.strip(),
        "experience_company": experience_company.strip(),
        "experience_desc": experience_desc.strip(),
        # -------------------------------

        "skills": unique_skills,
        "interests": interests,
        "experience": experience,
        "projects": final_projects,

        # IMPORTANT FOR MEMBER 1 + MEMBER 4
        "target_career": target,
        "target_career_name": target_career_name,
    }

    st.session_state["profile"] = profile


    # Also keep these available directly in session state
    # for compatibility with other project modules.
    st.session_state["skills"] = unique_skills
    st.session_state["target_career"] = target
    st.session_state["target_career_name"] = target_career_name
    st.session_state["experience"] = experience
    user_id = st.session_state.get("user_id")
    if user_id:
        try:
            db.save_profile(user_id, profile)
        except Exception as exc:
            st.warning(f"Saved for this session, but not to the database: {exc}")

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    st.success(
        "✅ Profile saved successfully!"
    )


    # --------------------------------------------------------
    # SHOW PROFILE FOR TESTING
    # --------------------------------------------------------

    st.subheader("Saved Profile")

    saved = st.session_state["profile"]

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        stat_card("Name", saved.get("name") or "—")
    with sc2:
        stat_card("Skills", f"{len(saved.get('skills', []))} selected")
    with sc3:
        stat_card(
            "Target Career",
            saved.get("target_career_name") or "Not chosen yet",
        )

    with st.expander("View raw profile data"):
        st.json(
            st.session_state["profile"]
        )