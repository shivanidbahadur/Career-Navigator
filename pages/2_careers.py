"""
pages/2_Careers.py
Shows the student's top 5 career matches, lets them pick a target
career, and shows the skill gaps for that career with priority badges.
"""

import streamlit as st
from core.state import init_state
from core.skills import normalize_skills, get_effective_skills
from core.recommend import recommend_careers
from core.gaps import get_skill_gaps

init_state()

st.title("Career Matches")

profile = st.session_state["profile"]

# ---- Fallback quick-entry if profile is empty ----
# (Remove this block once M2's Profile page is ready and tested,
# since it will fill st.session_state["profile"] properly.)
if not profile["skills"]:
    st.warning("No profile found yet. Enter your skills and interests below "
               "to test career matching (or fill the Profile page first).")

    skills_input = st.text_input(
        "Your skills (comma-separated)",
        placeholder="e.g. Python, SQL, Pandas, Statistics"
    )
    interests_input = st.text_input(
        "Your interests (comma-separated)",
        placeholder="e.g. AI, Data"
    )

    if st.button("Save and find my matches"):
        raw_skills = skills_input.split(",")
        profile["skills"] = normalize_skills(raw_skills)
        profile["interests"] = [i.strip() for i in interests_input.split(",") if i.strip()]
        st.rerun()

    st.stop()  # don't show the rest of the page until skills exist

# ---- Show top 5 career recommendations ----
st.subheader("Your Top 5 Career Matches")

effective_skills = get_effective_skills(st.session_state)
recommendations = recommend_careers(profile)

# simple table
table_data = [
    {
        "Career": r["name"],
        "Skill Match %": r["skill_match"],
        "Interest Match %": r["interest_match"],
        "Overall Score": r["final"],
    }
    for r in recommendations
]
st.table(table_data)

# bar chart of overall score
chart_data = {r["name"]: r["final"] for r in recommendations}
st.bar_chart(chart_data)

# ---- Let student pick a target career ----
st.subheader("Choose Your Target Career")

career_options = {r["name"]: r["career_id"] for r in recommendations}
chosen_name = st.selectbox("Select a career to focus on:", list(career_options.keys()))

if st.button("Set as my target career"):
    profile["target_career"] = career_options[chosen_name]
    st.success(f"Target career set to: {chosen_name}")

# ---- Show skill gaps for the current target career ----
if profile["target_career"]:
    st.subheader(f"Skill Gaps for: {chosen_name}")

    gaps = get_skill_gaps(effective_skills, profile["target_career"])

    if not gaps:
        st.success("No gaps found — you have all the skills for this career!")
    else:
        priority_colors = {
            "High": "🔴",
            "Medium": "🟠",
            "Low": "🟢",
        }
        for gap in gaps:
            badge = priority_colors.get(gap["priority"], "⚪")
            st.write(f"{badge} **{gap['skill']}** — {gap['priority']} priority "
                     f"(weight {gap['weight']})")