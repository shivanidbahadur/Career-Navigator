"""
core/recommend.py
Recommends careers based on skill match + interest match.
"""

import json

with open("data/careers.json") as f:
    CAREERS_DATA = json.load(f)


def _skill_match_pct(student_skills, career):
    """
    skill_match = (sum of weights of skills the student HAS)
                  / (sum of weights of ALL skills this career needs)
    Expressed as a percentage 0-100.
    This rewards having the heavily-weighted (important) skills more
    than having lots of low-weight ones.
    """
    total_weight = sum(s["weight"] for s in career["skills"])
    if total_weight == 0:
        return 0
    matched_weight = sum(
        s["weight"] for s in career["skills"] if s["skill"] in student_skills
    )
    return round((matched_weight / total_weight) * 100, 1)


def _interest_match_pct(student_interests, career):
    """
    interest_match = (interest tags the student picked that also
                       appear on this career) / (total tags on this career)
    Expressed as a percentage 0-100.
    """
    career_tags = career["interest_tags"]
    if not career_tags:
        return 0
    matched = [tag for tag in career_tags if tag in student_interests]
    return round((len(matched) / len(career_tags)) * 100, 1)


def recommend_careers(profile):
    """
    Scores every career for this student and returns the top 5,
    sorted by final score (highest first).

    final = 0.7 * skill_match + 0.3 * interest_match
    Skill match is weighted higher because "can you actually do the
    job" matters more than "are you interested in it" for a
    realistic recommendation.
    """
    student_skills = profile["skills"]
    student_interests = profile["interests"]

    results = []
    for career in CAREERS_DATA:
        skill_pct = _skill_match_pct(student_skills, career)
        interest_pct = _interest_match_pct(student_interests, career)
        final = round(0.7 * skill_pct + 0.3 * interest_pct, 1)

        results.append({
            "career_id": career["career_id"],
            "name": career["name"],
            "skill_match": skill_pct,
            "interest_match": interest_pct,
            "final": final,
        })

    results.sort(key=lambda r: r["final"], reverse=True)
    return results[:5]