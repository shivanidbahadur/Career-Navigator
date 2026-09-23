def generate_resume(profile, career_id):
    """
    Returns an HTML string resume, ordered so the target career's
    most important skills appear first.

    profile: dict with keys like name, email, degree, branch, grad_year,
             skills, projects, experience
    career_id: str, e.g. "data_scientist" or "web_developer"
    """
    # Order the student's skills by relevance to the target career.
    # We use the career's skill weights (from careers.json) if available;
    # skills not listed for this career just go at the end, unordered.
    career_skill_order = get_career_skill_order(career_id)

    ordered_skills = sorted(
        profile.get("skills", []),
        key=lambda s: career_skill_order.get(s, 0),
        reverse=True
    )

    skills_html = "".join(f"<li>{s}</li>" for s in ordered_skills)

    projects_html = "".join(
        f"<li><strong>{p.get('title', 'Project')}</strong>: {p.get('description', '')}</li>"
        for p in profile.get("projects", [])
    )

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #222; }}
            h1 {{ margin-bottom: 0; }}
            h3 {{ border-bottom: 2px solid #444; padding-bottom: 4px; margin-top: 24px; }}
            ul {{ padding-left: 20px; }}
        </style>
    </head>
    <body>
        <h1>{profile.get('name', 'Student Name')}</h1>
        <p>{profile.get('email', '')}</p>

        <h3>Education</h3>
        <p>{profile.get('degree', '')} - {profile.get('branch', '')}, Graduating {profile.get('grad_year', '')}</p>

        <h3>Skills</h3>
        <ul>{skills_html}</ul>

        <h3>Projects</h3>
        <ul>{projects_html}</ul>

        <h3>Experience</h3>
        <p>{profile.get('experience', 'Fresher')}</p>
    </body>
    </html>
    """
    return html


def get_career_skill_order(career_id):
    """
    Loads careers.json and returns a dict of {skill_name: weight}
    for the given career, so skills can be sorted by importance.
    Returns an empty dict if careers.json or the career isn't found
    (so the resume still works even before Member 1's file is ready).
    """
    import json
    import os

    try:
        path = os.path.join("data", "careers.json")
        with open(path, "r") as f:
            careers = json.load(f)
        for career in careers:
            if career["career_id"] == career_id:
                return {s["skill"]: s["weight"] for s in career["skills"]}
    except FileNotFoundError:
        pass
    return {}


def analyze_resume(profile, career_id):
    """
    Compares the student's skills against the target career's Required
    skills and returns suggestions for missing ones.
    Returns an empty list if careers.json isn't available yet.
    """
    import json
    import os

    try:
        path = os.path.join("data", "careers.json")
        with open(path, "r") as f:
            careers = json.load(f)
    except FileNotFoundError:
        return []

    career = next((c for c in careers if c["career_id"] == career_id), None)
    if not career:
        return []

    student_skills = set(profile.get("skills", []))
    suggestions = []

    for s in career["skills"]:
        if s["importance"] == "Required" and s["skill"] not in student_skills:
            suggestions.append({
                "skill": s["skill"],
                "suggestion": f"Add one {s['skill']} project for the {career['name']} role"
            })

    return suggestions


if __name__ == "__main__":
    # Quick manual test with a fake profile (careers.json doesn't exist yet,
    # so get_career_skill_order and analyze_resume will gracefully return
    # empty/default results - that's expected for now).
    test_profile = {
        "name": "Priya Sharma",
        "email": "priya@example.com",
        "degree": "B.Tech",
        "branch": "Computer Science",
        "grad_year": 2027,
        "skills": ["Python", "SQL", "Excel"],
        "projects": [
            {"title": "Student Grade Tracker", "description": "Built a CLI app to track grades using Python."}
        ],
        "experience": "Fresher"
    }

    resume_html = generate_resume(test_profile, "data_analyst")
    print(resume_html[:300])  # print just the start to confirm it works
    print("---")
    print("Suggestions:", analyze_resume(test_profile, "data_analyst"))