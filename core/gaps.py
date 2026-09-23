"""
core/gaps.py
Figures out which skills a student is missing for a target career,
and how urgent each missing skill is (High/Medium/Low priority).
"""

import json

with open("data/careers.json") as f:
    CAREERS_DATA = json.load(f)

with open("data/skills.json") as f:
    SKILLS_DATA = json.load(f)

PREREQUISITES = SKILLS_DATA["prerequisites"]

CAREERS_BY_ID = {c["career_id"]: c for c in CAREERS_DATA}


def _priority_score(missing_skill_entry, all_missing_names):
    """
    Turns importance + weight + prerequisite-dependency into one
    numeric score, higher = more urgent to learn first.

    - importance points: Required=3, Recommended=2, Optional=1
    - weight: already 1-5 from careers.json
    - dependency bonus: +2 for every OTHER missing skill that lists
      this skill as a prerequisite (learning it first unblocks more)
    """
    importance_points = {"Required": 3, "Recommended": 2, "Optional": 1}
    skill_name = missing_skill_entry["skill"]

    score = importance_points[missing_skill_entry["importance"]]
    score += missing_skill_entry["weight"]

    dependents = 0
    for other_skill, prereqs in PREREQUISITES.items():
        if other_skill in all_missing_names and skill_name in prereqs:
            dependents += 1
    score += dependents * 2

    return score


def get_skill_gaps(skills, career_id):
    """
    Compares the student's skills against what a career needs,
    finds what's missing, and ranks each missing skill as
    High / Medium / Low priority.

    Priority cutoffs (score from _priority_score):
      score >= 7  -> High
      score >= 4  -> Medium
      else        -> Low
    """
    career = CAREERS_BY_ID.get(career_id)
    if career is None:
        return []

    missing = [s for s in career["skills"] if s["skill"] not in skills]
    missing_names = [s["skill"] for s in missing]

    gaps = []
    for entry in missing:
        score = _priority_score(entry, missing_names)
        if score >= 7:
            priority = "High"
        elif score >= 4:
            priority = "Medium"
        else:
            priority = "Low"

        gaps.append({
            "skill": entry["skill"],
            "priority": priority,
            "weight": entry["weight"],
        })

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    gaps.sort(key=lambda g: priority_order[g["priority"]])
    return gaps