
import streamlit as st

from learning.auth import require_login, show_user_sidebar
from learning.roadmap import build_roadmap, get_resources, update_progress
from core.gaps import get_skill_gaps
from ui.theme import apply_theme, section_title, stat_card, tool_step_nav
from core import db


# ---------- Page Configuration ----------
st.set_page_config(
    page_title="AI Career Navigator - Roadmap",
    page_icon="🗺️",
    layout="wide",
)

apply_theme()

require_login()
show_user_sidebar()


# ---------- Page Header ----------
st.markdown(
    """
    <div class="fg-hero fg-rise" style="padding:34px 38px; margin-bottom:24px;">
        <div class="fg-eyebrow">✦ Skill Roadmap</div>
        <h1 style="font-size:clamp(30px,3.6vw,46px);">
            Your path, <span class="fg-gradient-text">phase by phase</span>.
        </h1>
        <p style="font-size:15.5px;">
            Work through prioritized skill phases with curated resources
            and track progress as you go.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------- 1. Get Skill Gaps ----------
profile = st.session_state.get("profile", {})
target_career = profile.get("target_career") or st.session_state.get("target_career")
user_skills = profile.get("skills", [])

if target_career:
    gaps = get_skill_gaps(user_skills, target_career)
else:
    # Fallback if no target career has been selected
    gaps = [
        {"skill": "Statistics", "priority": "High", "weight": 5},
        {"skill": "Machine Learning", "priority": "High", "weight": 5},
        {"skill": "Pandas", "priority": "Medium", "weight": 3},
        {"skill": "Data Visualization", "priority": "Medium", "weight": 3},
        {"skill": "Cloud Computing", "priority": "Low", "weight": 2},
    ]


# ---------- 2. Build Roadmap and Progress Tracker ----------
if not gaps:
    st.success(
        "You have no skill gaps for this career! You're ready to go."
    )

else:
    roadmap = build_roadmap(gaps)

    # Initialize progress states from database if not already present
    if "progress" not in st.session_state:
        user_id = st.session_state.get("user_id")
        st.session_state["progress"] = db.get_progress(user_id) if user_id else {}

    progress_dict = st.session_state["progress"]

    # ---------- Calculate Overall Progress ----------
    total_skills = len(gaps)

    completed_count = sum(
        1
        for item in gaps
        if progress_dict.get(item["skill"]) == "Completed"
    )

    progress_pct = (
        completed_count / total_skills
        if total_skills > 0
        else 0.0
    )

    # ---------- Overall Progress ----------
    section_title("Overall Progress", "📈")

    progress_label = (
        f"{completed_count} of {total_skills} skills completed"
    )

    progress_width = max(
        0.0,
        min(progress_pct * 100, 100.0),
    )

    # Custom HTML progress bar.
    # Rendered with st.html() instead of st.markdown(): markdown would end
    # the HTML block at the blank line below, and the following indented
    # <div> would then be shown as a literal code block instead of a bar.
    st.html(
        f"""
        <div style="
            width:100%;
            margin:8px 0 20px;
            font-family:inherit;
        ">
            <div style="
                color:#ffffff;
                font-size:15px;
                font-weight:500;
                margin-bottom:10px;
                line-height:1.5;
            ">
                {progress_label}
            </div>

            <div
                role="progressbar"
                aria-label="{progress_label}"
                aria-valuemin="0"
                aria-valuemax="100"
                aria-valuenow="{progress_width:.2f}"
                style="
                    display:block;
                    width:100%;
                    height:12px;
                    background:#172033;
                    border:1px solid #334155;
                    border-radius:999px;
                    overflow:hidden;
                    box-sizing:border-box;
                "
            >
                <div style="
                    display:block;
                    width:{progress_width:.2f}%;
                    height:100%;
                    background:linear-gradient(
                        90deg,
                        #22d3ee 0%,
                        #818cf8 55%,
                        #c084fc 100%
                    );
                    border-radius:inherit;
                    transition:width 0.4s ease;
                "></div>
            </div>
        </div>
        """
    )

    st.write("---")

    # ---------- 3. Render Roadmap Phases and Skills ----------
    for phase_item in roadmap:
        phase_name = phase_item["phase"]
        phase_skills = phase_item["skills"]

        st.markdown(f"### 🚀 Phase: {phase_name}")

        for skill in phase_skills:

            # Find skill metadata and priority
            gap_info = next(
                (
                    item
                    for item in gaps
                    if item["skill"] == skill
                ),
                {"priority": "Medium"},
            )

            priority = gap_info.get("priority", "Medium")

            # Priority labels
            if priority == "High":
                badge = "🔴 High Priority"
            elif priority == "Medium":
                badge = "🟡 Medium Priority"
            else:
                badge = "🟢 Low Priority"

            with st.expander(f"{skill} ({badge})"):

                # Current skill status
                current_status = progress_dict.get(
                    skill,
                    "Not Started",
                )

                status_options = [
                    "Not Started",
                    "In Progress",
                    "Completed",
                ]

                new_status = st.selectbox(
                    "Status",
                    status_options,
                    index=(
                        status_options.index(current_status)
                        if current_status in status_options
                        else 0
                    ),
                    key=f"status_{skill}",
                )

                # Update status using existing function
                if new_status != current_status:
                    update_progress(skill, new_status)
                    st.rerun()

                # ---------- Learning Resources ----------
                st.markdown("**Learning Resources:**")

                resources = get_resources(skill)

                if not resources:
                    st.info(
                        "No resources found for this skill yet."
                    )
                else:
                    for resource in resources:
                        st.markdown(
                            f"- [{resource['title']}]"
                            f"({resource['url']}) "
                            f"*(Type: {resource['type'].title()} "
                            f"| Difficulty: "
                            f"{resource['difficulty'].title()})*"
                        )

        st.write("")

# ---- Walk the toolkit one tool at a time ----
tool_step_nav("pages/3_Roadmap.py")

