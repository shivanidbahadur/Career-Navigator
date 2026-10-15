from html import escape

def generate_resume(profile, career_id):
    """Generate a professional, ATS-friendly HTML resume."""

    # Sort skills according to their relevance to the selected career.
    career_skill_order = get_career_skill_order(career_id)

    skills = profile.get("skills") or []
    ordered_skills = sorted(
        skills,
        key=lambda skill: career_skill_order.get(str(skill), 0),
        reverse=True
    )

    # Safely format project details.
    projects_html = ""
    for project in profile.get("projects") or []:
        if isinstance(project, dict):
            title = project.get("title") or "Project"
            description = project.get("description") or ""
        else:
            title = str(project)
            description = ""

        if title.strip() or description.strip():
            projects_html += f"""
            <div class="project">
                <strong>{escape(str(title))}</strong>
                {f'<p>{escape(str(description))}</p>' if description else ''}
            </div>
            """

    # Skills as clean text / comma-separated (removed border boxes as requested)
    skills_html = ", ".join(
        f'<span>{escape(str(skill))}</span>'
        for skill in ordered_skills
    ) if ordered_skills else ""

    # Certifications formatting
    certs_html = ""
    for cert in profile.get("certifications") or []:
        if cert.strip():
            certs_html += f"<li>{escape(str(cert))}</li>"

    name = escape(str(profile.get("name") or "Student Name"))
    email = escape(str(profile.get("email") or ""))
    phone = escape(str(profile.get("phone") or ""))
    linkedin = escape(str(profile.get("linkedin") or ""))
    github = escape(str(profile.get("github") or ""))
    
    degree = escape(str(profile.get("degree") or ""))
    branch = escape(str(profile.get("branch") or ""))
    institution = escape(str(profile.get("institution") or ""))
    grad_year = escape(str(profile.get("grad_year") or ""))

    # Detailed experience fields
    exp_title = escape(str(profile.get("experience_title") or ""))
    exp_company = escape(str(profile.get("experience_company") or ""))
    exp_desc = escape(str(profile.get("experience_desc") or ""))
    fallback_experience = escape(str(profile.get("experience") or ""))

    # Build contact line cleanly
    contact_items = []
    if email: contact_items.append(email)
    if phone: contact_items.append(phone)
    if linkedin: contact_items.append(f'<a href="{linkedin}">LinkedIn</a>')
    if github: contact_items.append(f'<a href="{github}">GitHub</a>')
    
    contact_section = (
        f'<div class="contact">{" | ".join(contact_items)}</div>' if contact_items else ""
    )

    # Education title assembly
    edu_parts = [p for p in [degree, branch] if p]
    edu_line = " - ".join(edu_parts)
    if institution:
        edu_line = f"{edu_line} at {institution}" if edu_line else institution
    if grad_year:
        edu_line += f" (Expected Graduation: {grad_year})" if edu_line else f"Expected Graduation: {grad_year}"

    education_section = ""
    if edu_line.strip():
        education_section = f"""
        <section>
            <h2>Education</h2>
            <p>{edu_line}</p>
        </section>
        """

    skills_section = ""
    if skills_html:
        skills_section = f"""
        <section>
            <h2>Technical Skills</h2>
            <p>{skills_html}</p>
        </section>
        """

    projects_section = ""
    if projects_html:
        projects_section = f"""
        <section>
            <h2>Projects</h2>
            {projects_html}
        </section>
        """

    experience_section = ""
    if exp_title or exp_company or exp_desc:
        experience_section = f"""
        <section>
            <h2>Experience</h2>
            <p><strong>{exp_title}</strong>{f" at <em>{exp_company}</em>" if exp_company else ""}</p>
            {f"<p>{exp_desc}</p>" if exp_desc else ""}
        </section>
        """
    elif fallback_experience and fallback_experience != "Fresher":
        experience_section = f"""
        <section>
            <h2>Experience</h2>
            <p>{fallback_experience}</p>
        </section>
        """

    certifications_section = ""
    if certs_html:
        certifications_section = f"""
        <section>
            <h2>Certifications</h2>
            <ul>{certs_html}</ul>
        </section>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Resume</title>
    <style>
        @page {{
            size: A4;
            margin: 15mm;
        }}
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: Arial, Helvetica, sans-serif;
            font-size: 10.5pt;
            line-height: 1.5;
            color: #263238;
            background: #ffffff;
            max-width: 800px;
            margin: 0 auto;
            padding: 32px;
        }}
        header {{
            border-bottom: 3px solid #24476b;
            padding-bottom: 16px;
            margin-bottom: 22px;
        }}
        h1 {{
            color: #183653;
            font-size: 27pt;
            margin: 0 0 5px;
            overflow-wrap: anywhere;
        }}
        .contact {{
            color: #4b5563;
            overflow-wrap: anywhere;
        }}
        .contact a {{
            color: #24476b;
            text-decoration: none;
        }}
        section {{
            margin-top: 20px;
            break-inside: avoid;
        }}
        h2 {{
            font-size: 13pt;
            color: #24476b;
            text-transform: uppercase;
            letter-spacing: 0.7px;
            border-bottom: 1px solid #b8c7d6;
            padding-bottom: 5px;
            margin: 0 0 10px;
        }}
        p, ul {{
            margin: 5px 0;
            overflow-wrap: anywhere;
        }}
        ul {{
            padding-left: 20px;
        }}
        .project {{
            margin-bottom: 12px;
            break-inside: avoid;
        }}
        .project strong {{
            color: #183653;
        }}
        @media print {{
            body {{
                max-width: none;
                margin: 0;
                padding: 0;
                font-size: 10pt;
            }}
            header, section, .project {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>{name}</h1>
        {contact_section}
    </header>

    {education_section}
    {experience_section}
    {skills_section}
    {projects_section}
    {certifications_section}
</body>
</html>
"""
    return html


def get_career_skill_order(career_id):
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