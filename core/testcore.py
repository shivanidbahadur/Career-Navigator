"""
core/test_core.py
Runs one sample student through the entire M1 pipeline and prints
the results at each stage. Use this to sanity-check that all core
functions still work correctly after any change.

Sanity check to look for: this sample student knows Python, SQL,
Pandas, Statistics and is interested in AI/Data — so Data Scientist
and Data Analyst should rank near the top of recommend_careers.
"""

from core.skills import normalize_skills, get_effective_skills
from core.recommend import recommend_careers
from core.gaps import get_skill_gaps
from core.readiness import compute_readiness


def run_test():
    # ---- Step 1: build a sample profile ----
    raw_skills = ["python 3", "SQL", "pandas library", "stats"]
    interests = ["AI", "Data"]

    profile = {
        "name": "Sample Student",
        "email": "sample@test.com",
        "degree": "B.Tech",
        "branch": "CSE",
        "grad_year": "2026",
        "skills": normalize_skills(raw_skills),
        "interests": interests,
        "experience": "Fresher",
        "projects": [],
        "target_career": None,
    }

    print("=" * 60)
    print("STEP 1: normalize_skills")
    print("Raw skills:", raw_skills)
    print("Normalized:", profile["skills"])

    # ---- Step 2: recommend careers ----
    print("=" * 60)
    print("STEP 2: recommend_careers (top 5)")
    recommendations = recommend_careers(profile)
    for r in recommendations:
        print(f"  {r['name']:<25} skill={r['skill_match']:<6} "
              f"interest={r['interest_match']:<6} final={r['final']}")

    # sanity check
    top_names = [r["name"] for r in recommendations]
    if "Data Scientist" in top_names[:3] or "Data Analyst" in top_names[:3]:
        print("  Sanity check PASSED: Data Scientist/Analyst near top.")
    else:
        print("  Sanity check FAILED: expected Data Scientist/Analyst near top!")

    # ---- Step 3: pick a target career and find gaps ----
    profile["target_career"] = recommendations[0]["career_id"]
    print("=" * 60)
    print(f"STEP 3: get_skill_gaps for target career = {profile['target_career']}")
    gaps = get_skill_gaps(profile["skills"], profile["target_career"])
    for g in gaps:
        print(f"  {g['skill']:<25} priority={g['priority']:<8} weight={g['weight']}")

    # ---- Step 4: build a state and compute readiness ----
    print("=" * 60)
    print("STEP 4: compute_readiness")
    state = {
        "profile": profile,
        "progress": {},
        "interview_results": [],
        "resume_generated": False,
    }
    readiness = compute_readiness(state)
    for key, value in readiness.items():
        print(f"  {key:<15}: {value}")

    # ---- Step 5: simulate progress and show readiness changes ----
    print("=" * 60)
    print("STEP 5: after completing top gap skill, readiness should improve")
    if gaps:
        skill_to_complete = gaps[0]["skill"]
        state["progress"][skill_to_complete] = "Completed"
        new_effective_skills = get_effective_skills(state)
        new_readiness = compute_readiness(state)
        print(f"  Marked '{skill_to_complete}' as Completed.")
        print(f"  Effective skills now: {new_effective_skills}")
        for key, value in new_readiness.items():
            print(f"  {key:<15}: {value}")

        if new_readiness["readiness"] > readiness["readiness"]:
            print("  Sanity check PASSED: readiness increased after progress.")
        else:
            print("  Sanity check FAILED: readiness did not increase!")

    print("=" * 60)
    print("All tests completed.")


if __name__ == "__main__":
    run_test()