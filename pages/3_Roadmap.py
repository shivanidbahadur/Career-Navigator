import streamlit as st
from learning.auth import require_login, show_user_sidebar
from learning.roadmap import build_roadmap, get_resources, update_progress
from core.gaps import get_skill_gaps
from ui.theme import apply_theme, section_title, stat_card

st.set_page_config(
    page_title="AI Career Navigator - Roadmap",
    page_icon="🗺️",
    layout="wide",
)
apply_theme()

require_login()
show_user_sidebar()

st.markdown(
    """
    <div class="fg-hero fg-rise" style="padding:34px 38px; margin-bottom:24px;">
        <div class="fg-eyebrow">✦ Skill Roadmap</div>
        <h1 style="font-size:clamp(30px,3.6vw,46px);">Your path, <span class="fg-gradient-text">phase by phase</span>.</h1>
        <p style="font-size:15.5px;">
            Work through prioritized skill phases with curated resources
            and track progress as you go.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- 1. Get Gaps using M1's core engine ----------
profile = st.session_state.get("profile", {})
target_career = profile.get("target_career")
user_skills = profile.get("skills", [])

if target_career:
    gaps = get_skill_gaps(user_skills, target_career)
else:
    # Fallback if no target career selected yet
    gaps = [
        {"skill": "Statistics", "priority": "High", "weight": 5},
        {"skill": "Machine Learning", "priority": "High", "weight": 5},
        {"skill": "Pandas", "priority": "Medium", "weight": 3},
        {"skill": "Data Visualization", "priority": "Medium", "weight": 3},
        {"skill": "Cloud Computing", "priority": "Low", "weight": 2},
    ]

if not gaps:
    st.success("You have no skill gaps for this career! You're ready to go.")
else:
    # ---------- 2. Build Roadmap & Progress Tracker ----------
    roadmap = build_roadmap(gaps)

    # Initialize progress states if not already present
    if "progress" not in st.session_state:
        st.session_state["progress"] = {}

    progress_dict = st.session_state["progress"]

    # Calculate overall progress percentage
    total_skills = len(gaps)
    completed_count = sum(1 for s in gaps if progress_dict.get(s["skill"]) == "Completed")
    progress_pct = completed_count / total_skills if total_skills > 0 else 0

    section_title("Overall Progress", "📈")
    st.progress(progress_pct, text=f"{completed_count} of {total_skills} skills completed")
    st.write("---")

    # ---------- 3. Render Phases and Skills ----------
    for phase_item in roadmap:
        phase_name = phase_item["phase"]
        phase_skills = phase_item["skills"]

        st.markdown(f"### 🚀 Phase: {phase_name}")

        for skill in phase_skills:
            # Find the gap metadata (priority) for styling/display
            gap_info = next((g for g in gaps if g["skill"] == skill), {"priority": "Medium"})
            priority = gap_info.get("priority", "Medium")

            # Color tag for priority
            if priority == "High":
                badge = "🔴 High Priority"
            elif priority == "Medium":
                badge = "🟡 Medium Priority"
            else:
                badge = "🟢 Low Priority"

            with st.expander(f"{skill} ({badge})"):
                # Current status dropdown
                current_status = progress_dict.get(skill, "Not Started")
                new_status = st.selectbox(
                    "Status",
                    ["Not Started", "In Progress", "Completed"],
                    index=["Not Started", "In Progress", "Completed"].index(current_status),
                    key=f"status_{skill}"
                )

                if new_status != current_status:
                    update_progress(skill, new_status)
                    st.rerun()

                # Show learning resources
                st.markdown("**Learning Resources:**")
                resources = get_resources(skill)

                if not resources:
                    st.info("No resources found for this skill yet.")
                else:
                    for r in resources:
                        st.markdown(
                            f"- [{r['title']}]({r['url']}) "
                            f"*(Type: {r['type'].title()} | Difficulty: {r['difficulty'].title()})*"
                        )
        st.write("")