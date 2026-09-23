import json
import re

from interview.llm import call_claude


FALLBACK_QUESTIONS = {
    "Machine Learning": {
        "question": "What is the difference between supervised and unsupervised learning?",
        "skill": "Machine Learning",
        "difficulty": "Easy",
    },
    "Statistics": {
        "question": "What is the difference between mean and median, and when might you prefer one over the other?",
        "skill": "Statistics",
        "difficulty": "Easy",
    },
    "Data Visualization": {
        "question": "Why is choosing the right chart type important when presenting data?",
        "skill": "Data Visualization",
        "difficulty": "Easy",
    },
}


def _clean_json(text):
    text = text.strip()

    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    return text.strip()


def _fallback_questions(gaps, profile):
    questions = []

    # Exactly one warm-up question about an existing skill.
    existing_skills = profile.get("skills", []) if isinstance(profile, dict) else []

    if existing_skills:
        skill = existing_skills[0]
    else:
        skill = "your existing technical skills"

    questions.append({
        "question": f"Briefly explain one project or task where you used {skill}.",
        "why": f"This is a warm-up because your profile already shows {skill}.",
        "skill": skill,
        "difficulty": "Easy",
    })

    priority_order = {"High": 0, "Medium": 1, "Low": 2}

    sorted_gaps = sorted(
        gaps,
        key=lambda x: priority_order.get(
            str(x.get("priority", x.get("level", "Medium"))),
            1
        )
    )

    for gap in sorted_gaps:
        skill = gap.get("skill", "Unknown Skill")
        priority = gap.get("priority", gap.get("level", "Medium"))

        base = FALLBACK_QUESTIONS.get(
            skill,
            {
                "question": f"Explain the key concepts of {skill} and how you would apply them in a practical project.",
                "skill": skill,
                "difficulty": "Medium",
            }
        )

        questions.append({
            "question": base["question"],
            "why": (
                f"{skill} is required for the target career and "
                f"your profile shows a {priority} priority skill gap in {skill}."
            ),
            "skill": skill,
            "difficulty": base["difficulty"],
        })

    return questions


def generate_questions(gaps, career_id, profile):
    """
    Generate interview questions only from verified skill gaps.

    gaps example:
    [
        {"skill": "Machine Learning", "priority": "High"},
        {"skill": "Statistics", "priority": "High"},
        {"skill": "Data Visualization", "priority": "Medium"}
    ]
    """

    if not gaps:
        return []

    target_career = (
        profile.get("career", career_id)
        if isinstance(profile, dict)
        else career_id
    )

    level = (
        profile.get("level", "beginner")
        if isinstance(profile, dict)
        else "beginner"
    )

    gap_text = json.dumps(gaps, indent=2)

    system = """
You are the interview-question engine for an AI Career Navigator.

Your job is NOT to conduct a generic interview.

Every gap question MUST correspond to a real skill gap supplied by the
career guidance system.

Return STRICT JSON ONLY.
Do not use markdown.
Do not use code fences.
Do not add explanations outside JSON.

The JSON must be a list of objects with exactly these fields:

[
  {
    "question": "...",
    "why": "...",
    "skill": "...",
    "difficulty": "Easy|Medium|Hard"
  }
]
"""

    user = f"""
Target career: {target_career}

Student level: {level}

Verified skill gaps:
{gap_text}

Student profile:
{json.dumps(profile, indent=2)}

Rules:

1. Generate EXACTLY one Easy warm-up question about a skill
   the student already has.

2. Then generate EXACTLY one question for EACH verified skill gap.

3. Order the gap questions High priority first, then Medium,
   then Low.

4. Never invent a skill gap.

5. Every gap question's "skill" MUST exactly match a supplied gap.

6. Every gap question's "why" MUST explicitly explain the
   connection to that specific gap.

7. Example:
   "Machine Learning is required for Data Scientist and your
   profile shows a High-priority gap in Machine Learning."

8. Keep questions appropriate for the student's level.

Return JSON only.
"""

    try:
        raw = call_claude(system, user)
        cleaned = _clean_json(raw)
        result = json.loads(cleaned)

        if not isinstance(result, list):
            raise ValueError("Expected a JSON list.")

        required = {"question", "why", "skill", "difficulty"}

        for item in result:
            if not isinstance(item, dict):
                raise ValueError("Invalid question object.")

            if not required.issubset(item.keys()):
                raise ValueError("Missing required fields.")

        # Safety check: don't allow Claude to invent gap skills.
        allowed_skills = {
            gap.get("skill")
            for gap in gaps
            if gap.get("skill")
        }

        for item in result[1:]:
            if item["skill"] not in allowed_skills:
                raise ValueError(
                    f"Question contains non-gap skill: {item['skill']}"
                )

        return result

    except Exception:
        return _fallback_questions(gaps, profile)