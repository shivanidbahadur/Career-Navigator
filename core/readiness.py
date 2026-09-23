"""
core/readiness.py
Combines skill match, learning progress, interview performance,
resume status, and experience into one overall readiness score.
"""

from core.skills import get_effective_skills
from core.recommend import _skill_match_pct, CAREERS_DATA

CAREERS_BY_ID = {c["career_id"]: c for c in CAREERS_DATA}

EXPERIENCE_POINTS = {
    "Fresher": 0,
    "Projects": 40,
    "Internship": 70,
    "Work": 100,
}


def _learning_score(progress):
    """
    % of roadmap skills marked Completed out of all skills that have
    a progress entry at all (Not Started/In Progress/Completed).
    If nothing is tracked yet, learning score is 0.
    """
    if not progress:
        return 0
    completed = sum(1 for status in progress.values() if status == "Completed")
    return round((completed / len(progress)) * 100, 1)


def _interview_score(interview_results):
    """
    Average score (0-100) across all mock interview answers so far.
    If no interviews taken yet, score is 0.
    """
    if not interview_results:
        return 0
    total = sum(r["score"] for r in interview_results)
    return round(total / len(interview_results), 1)


def compute_readiness(state):
    """
    readiness = 0.4*skill_match + 0.2*learning + 0.2*interview
                + 0.1*resume + 0.1*experience
    All sub-scores are 0-100. Weighted this way because having the
    right skills matters most, then actually building them
    (learning) and proving them (interview), with resume/experience
    as smaller supporting signals.
    """
    profile = state["profile"]
    target_id = profile["target_career"]

    if target_id and target_id in CAREERS_BY_ID:
        effective_skills = get_effective_skills(state)
        career = CAREERS_BY_ID[target_id]
        skill_match = _skill_match_pct(effective_skills, career)
    else:
        skill_match = 0

    learning = _learning_score(state["progress"])
    interview = _interview_score(state["interview_results"])
    resume = 100 if state["resume_generated"] else 0
    experience = EXPERIENCE_POINTS.get(profile["experience"], 0)

    readiness = round(
        0.4 * skill_match + 0.2 * learning + 0.2 * interview
        + 0.1 * resume + 0.1 * experience,
        1,
    )

    return {
        "skill_match": skill_match,
        "learning": learning,
        "interview": interview,
        "resume": resume,
        "experience": experience,
        "readiness": readiness,
    }