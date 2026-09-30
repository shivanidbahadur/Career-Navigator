"""
pages/7_Dashboard.py
Shows a one-page summary of the student's career journey: target
career, match scores, skill gaps, learning progress, interview
performance, resume status, and overall readiness score.

This page reads directly from st.session_state, so it automatically
updates as the student progresses through other pages (Roadmap,
Jobs, Resume, Interview) — no manual refresh logic needed.
"""

import streamlit as st
from core.state import init_state
from core.skills import get_effective_skills
from core.recommend import recommend_careers
from core.gaps import get_skill_gaps
from core.readiness import compute_readiness
from ui.theme import apply_theme, section_title, stat_card

st.set_page_config(
    page_title="AI Career Navigator - Dashboard",
    page_icon="📊",
    layout="wide",
)
apply_theme()
init_state()

st.markdown(
    """
    <div class="fg-hero fg-rise" style="padding:34px 38px; margin-bottom:24px;">
        <div class="fg-eyebrow">✦ Readiness Dashboard</div>
        <h1 style="font-size:clamp(30px,3.6vw,46px);">How ready are <span class="fg-gradient-text">you?</span></h1>
        <p style="font-size:15.5px;">
            One live snapshot of your target career, skill gaps, learning
            progress, interview performance and resume status.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

profile = st.session_state["profile"]

# ---- Guard: need a target career first ----
if not profile["skills"] or not profile["target_career"]:
    st.warning("No target career set yet. Go to the Careers page first, "
               "enter your skills, and choose a target career.")
    st.stop()

# ---- Find the target career's display name ----
recommendations = recommend_careers(profile)
target_name = next(
    (r["name"] for r in recommendations if r["career_id"] == profile["target_career"]),
    profile["target_career"],  # fallback: show the raw id if not found in top 5
)

st.subheader(f"Target Career: {target_name}")

# ---- Readiness score (the headline number) ----
readiness = compute_readiness(st.session_state)

d1, d2, d3 = st.columns(3)
with d1:
    stat_card("Overall Readiness", f"{readiness['readiness']} / 100")
with d2:
    stat_card("Skill Match", f"{readiness['skill_match']}%")
with d3:
    stat_card("Interview Score", f"{readiness['interview']}%")

# ---- Breakdown of the readiness formula ----
section_title("Readiness Breakdown", "🧮")
col1, col2, col3 = st.columns(3)
col1.metric("Skill Match", f"{readiness['skill_match']}%")
col1.metric("Experience", f"{readiness['experience']}%")
col2.metric("Learning Progress", f"{readiness['learning']}%")
col2.metric("Resume", "Done" if readiness["resume"] == 100 else "Not done")
col3.metric("Interview Score", f"{readiness['interview']}%")

st.caption(
    "Formula: readiness = 0.4×skill match + 0.2×learning + 0.2×interview "
    "+ 0.1×resume + 0.1×experience"
)

# ---- Learning progress summary ----
section_title("Learning Progress", "📚")
progress = st.session_state["progress"]
if not progress:
    st.info("No roadmap progress yet. Visit the Roadmap page to start learning.")
else:
    completed = [s for s, status in progress.items() if status == "Completed"]
    in_progress = [s for s, status in progress.items() if status == "In Progress"]
    not_started = [s for s, status in progress.items() if status == "Not Started"]
    st.write(f"✅ Completed ({len(completed)}): {', '.join(completed) or '—'}")
    st.write(f"🟡 In Progress ({len(in_progress)}): {', '.join(in_progress) or '—'}")
    st.write(f"⬜ Not Started ({len(not_started)}): {', '.join(not_started) or '—'}")

# ---- Interview performance summary ----
section_title("Interview Performance", "🎤")
interview_results = st.session_state["interview_results"]
if not interview_results:
    st.info("No mock interview attempted yet. Visit the Interview page.")
else:
    for r in interview_results:
        st.write(f"- **{r['skill']}**: {r['score']}/100 — {r['question']}")

# ---- Resume status ----
section_title("Resume Status", "📄")
if st.session_state["resume_generated"]:
    st.success("Resume generated.")
else:
    st.info("Resume not generated yet. Visit the Resume page.")

# ---- Remaining skill gaps for the target career ----
section_title("Remaining Skill Gaps", "🧩")
effective_skills = get_effective_skills(st.session_state)
gaps = get_skill_gaps(effective_skills, profile["target_career"])

if not gaps:
    st.success("No gaps left — you're fully matched for this career!")
else:
    priority_colors = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}
    for gap in gaps:
        badge = priority_colors.get(gap["priority"], "⚪")
        st.write(f"{badge} **{gap['skill']}** — {gap['priority']} priority")

st.caption(
    "Note: feedback here is guidance for self-improvement, not a hiring "
    "decision. No sensitive personal attributes are used in scoring."
)