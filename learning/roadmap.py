import json
import os

PROGRESS_STATUSES = ["Not Started", "In Progress", "Completed"]
PHASE_NAMES = ["Foundation", "Data Handling", "Core Skill", "Projects"]
PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}


# ---------- Reading data ----------
def load_prerequisites():
    """Read the prerequisite map from skills.json. {} if the file or key is missing."""
    path = "data/skills.json"
    if not os.path.exists(path):
        # TEMPORARY: used until M1 pushes skills.json
        return {
            "Machine Learning": ["Python", "Statistics"],
            "Deep Learning": ["Machine Learning"],
            "Data Visualization": ["Pandas"],
            "Pandas": ["Python"],
        }
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("prerequisites", {})


def load_resources():
    """Read data/resources.json. [] if it is missing."""
    path = "data/resources.json"
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- Public functions (per the function contract) ----------
def build_roadmap(gaps):
    """
    gaps: [{"skill", "priority": "High"|"Medium"|"Low", "weight"}]
    Returns: [{"phase", "skills": [...]}] in prerequisite order.
    """
    if not gaps:
        return []

    prereqs = load_prerequisites()
    gap_skills = {g["skill"] for g in gaps}
    priority_by_skill = {g["skill"]: g["priority"] for g in gaps}

    ordered = _topological_order(gap_skills, prereqs, priority_by_skill)
    return _group_into_phases(ordered)


def _topological_order(gap_skills, prereqs, priority_by_skill):
    """
    Repeatedly pick any not-yet-placed skill whose prerequisites (if in the
    gap list) are already placed. Among ready skills, place High priority
    first. This guarantees prerequisites always come before what needs them.
    """
    placed = []
    remaining = set(gap_skills)

    while remaining:
        # A skill is "ready" if every one of its prerequisites that is
        # also in our gap list has already been placed.
        ready = [
            skill
            for skill in remaining
            if all(
                req in placed or req not in gap_skills
                for req in prereqs.get(skill, [])
            )
        ]

        if not ready:
            # Safety net: a prerequisite cycle (shouldn't normally happen).
            # Place whatever is left, alphabetically, so we never crash.
            ready = sorted(remaining)

        # Highest priority first; alphabetical as a tie-breaker for stability.
        ready.sort(key=lambda s: (priority_by_skill.get(s, "Low") != "High",
                                   priority_by_skill.get(s, "Low") != "Medium",
                                   s))

        next_skill = ready[0]
        placed.append(next_skill)
        remaining.remove(next_skill)

    return placed


def _group_into_phases(ordered_skills):
    """Split the ordered list into 4 roughly equal named phases."""
    total = len(ordered_skills)
    phase_count = len(PHASE_NAMES)
    # How many skills per phase, spreading any remainder over the first phases
    base = total // phase_count
    extra = total % phase_count

    phases = []
    start = 0
    for i, name in enumerate(PHASE_NAMES):
        size = base + (1 if i < extra else 0)
        if size == 0:
            continue
        phase_skills = ordered_skills[start:start + size]
        phases.append({"phase": name, "skills": phase_skills})
        start += size

    return phases


def get_resources(skill):
    """Return [{"title","type","url","difficulty"}] for one skill."""
    all_resources = load_resources()
    return [
        {
            "title": r["title"],
            "type": r["type"],
            "url": r["url"],
            "difficulty": r["difficulty"],
        }
        for r in all_resources
        if r["skill"] == skill
    ]


def update_progress(skill, status):
    """Update st.session_state['progress'] for one skill."""
    import streamlit as st  # imported here so this file can be unit-tested without Streamlit

    if status not in PROGRESS_STATUSES:
        raise ValueError(f"status must be one of {PROGRESS_STATUSES}")

    if "progress" not in st.session_state:
        st.session_state["progress"] = {}
    st.session_state["progress"][skill] = status