
import json
import os


def load_jobs():
    """Load all jobs from data/jobs.json."""
    project_root = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
    jobs_path = os.path.join(project_root, "data", "jobs.json")

    with open(jobs_path, "r", encoding="utf-8") as f:
        return json.load(f)


def match_jobs(skills, career_id):
    """Match jobs based on skills and target career."""

    jobs = load_jobs()

    # Ignore differences in capitalization and extra spaces.
    skill_set = {
        skill.strip().casefold()
        for skill in skills
        if isinstance(skill, str) and skill.strip()
    }

    results = []

    for job in jobs:
        required = job.get("required_skills", [])

        matched = [
            skill for skill in required
            if isinstance(skill, str)
            and skill.strip().casefold() in skill_set
        ]

        missing = [
            skill for skill in required
            if not isinstance(skill, str)
            or skill.strip().casefold() not in skill_set
        ]

        match_pct = (
            (len(matched) / len(required)) * 100
            if required else 0
        )

        # Small bonus when the title matches the target career.
        career_name = (
            career_id.replace("_", " ").casefold()
            if isinstance(career_id, str)
            else ""
        )

        job_title = job.get("title", "").casefold()

        if career_name and career_name in job_title:
            match_pct = min(100, match_pct + 10)

        results.append({
            "title": job.get("title", "Untitled Role"),
            "company": job.get("company", "Unknown Company"),
            "match_pct": round(match_pct, 1),
            "missing": missing,
        })

    results.sort(
        key=lambda job: job["match_pct"],
        reverse=True,
    )

    return results


if __name__ == "__main__":
    test_skills = ["python", "SQL", "Excel"]
    test_career = "data_analyst"

    for job in match_jobs(test_skills, test_career)[:5]:
        print(job)
