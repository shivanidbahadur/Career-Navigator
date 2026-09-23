import os
import json
import streamlit as st

from learning.auth import require_login, show_user_sidebar


# ============================================================
# LOGIN / SIDEBAR
# ============================================================

require_login()
show_user_sidebar()


# ============================================================
# PAGE
# ============================================================

st.title("👤 Your Profile")
st.write(
    "Create your profile so AI Career Navigator can personalize "
    "career guidance, learning gaps, and interview practice."
)


# ============================================================
# OPTIONS
# ============================================================

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
    "AI",
    "Data",
    "Software",
    "Web",
    "Cloud",
    "Cybersecurity",
    "Business",
    "Research",
    "Design",
    "Mobile",
    "Engineering",
]


DONT_KNOW = "I don't know yet"


# ============================================================
# LOAD CAREERS
# ============================================================

def load_careers():
    """
    Load careers from the shared data/careers.json file.

    Returns:
        [
            {
                "career_id": "...",
                "name": "..."
            }
        ]
    """

    path = "data/careers.json"

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
# PROFILE FORM
# ============================================================

with st.form("profile_form"):

    st.subheader("Personal Information")

    name = st.text_input(
        "Full Name",
        value=existing.get("name", "")
    )

    email = st.text_input(
        "Email",
        value=existing.get("email", "")
    )

    degree = st.text_input(
        "Degree / Course",
        value=existing.get("degree", "")
    )


    # ========================================================
    # SKILLS
    # ========================================================

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


    # ========================================================
    # INTERESTS
    # ========================================================

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


    # ========================================================
    # EXPERIENCE
    # ========================================================

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


    # ========================================================
    # PROJECTS
    # ========================================================

    existing_projects = existing.get(
        "projects",
        []
    )

    if isinstance(existing_projects, list):
        projects_default = "\n".join(
            existing_projects
        )
    else:
        projects_default = ""

    projects_text = st.text_area(
        "Projects (one per line)",
        value=projects_default,
        placeholder=(
            "Example:\n"
            "AI Road Pothole Detection\n"
            "AI Career Navigator"
        )
    )


    # ========================================================
    # CAREER
    # ========================================================

    st.subheader("Career Goal")

    career_options = [
        DONT_KNOW
    ] + career_names

    # Determine current selection
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


    # ========================================================
    # SUBMIT
    # ========================================================

    submitted = st.form_submit_button(
        "💾 Save Profile",
        use_container_width=True
    )


# ============================================================
# SAVE PROFILE
# ============================================================

if submitted:

    # Clean projects
    projects = [
        project.strip()
        for project in projects_text.split("\n")
        if project.strip()
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
        "degree": degree.strip(),
        "skills": unique_skills,
        "interests": interests,
        "experience": experience,
        "projects": projects,

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

    st.json(
        st.session_state["profile"]
    )