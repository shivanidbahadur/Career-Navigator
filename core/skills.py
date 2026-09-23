"""
core/skills.py
Handles skill name cleanup (synonyms) and figuring out what skills
a student effectively has (profile skills + completed roadmap skills).
"""

import json

with open("data/skills.json") as f:
    SKILLS_DATA = json.load(f)


def normalize_skills(raw_skills):
    """
    STUB: takes a list of raw skill strings, returns them unchanged
    for now. Real version will lowercase, strip, and map synonyms
    to the standard skill name from data/skills.json.
    """
    return list(raw_skills)


def get_effective_skills(state):
    """
    A student's real skill set = skills they entered in their profile
    PLUS any skill marked "Completed" in their learning progress.
    This way, finishing a roadmap course actually improves their
    career match and readiness score.
    """
    profile_skills = state["profile"]["skills"]
    completed_skills = [
        skill for skill, status in state["progress"].items()
        if status == "Completed"
    ]

    combined = profile_skills + completed_skills
    # remove duplicates, keep order
    seen = set()
    result = []
    for skill in combined:
        if skill not in seen:
            seen.add(skill)
            result.append(skill)
    return result