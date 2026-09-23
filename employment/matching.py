import json


def load_jobs():
    """Load all jobs from data/jobs.json"""
    with open("data/jobs.json", "r") as f:
        return json.load(f)


def match_jobs(skills, career_id):
    """
    Given the student's skills and their target career_id,
    return jobs sorted by match percentage (best first).

    skills: list[str] - the student's current skills
    career_id: str - the student's target career, e.g. "data_scientist"
    """
    jobs = load_jobs()
    skill_set = set(skills)
    results = []

    for job in jobs:
        required = job["required_skills"]
        matched = [s for s in required if s in skill_set]
        missing = [s for s in required if s not in skill_set]

        match_pct = (len(matched) / len(required)) * 100 if required else 0

        # Small boost if the job relates to the student's target career.
        # We check this by seeing if the career name (with spaces removed
        # and lowercased) appears in the job title.
        career_name = career_id.replace("_", " ").lower()
        if career_name in job["title"].lower():
            match_pct = min(100, match_pct + 10)

        results.append({
            "title": job["title"],
            "company": job["company"],
            "match_pct": round(match_pct, 1),
            "missing": missing
        })

    results.sort(key=lambda x: x["match_pct"], reverse=True)
    return results


if __name__ == "__main__":
    # Quick manual test using the example from the spec:
    # student has Python, SQL, Excel; a job needs Python, SQL, Excel, Power BI -> 75%
    test_skills = ["Python", "SQL", "Excel"]
    test_career = "data_analyst"

    output = match_jobs(test_skills, test_career)
    for job in output[:5]:
        print(job)