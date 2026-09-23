import json
import re

from interview.llm import call_claude


RUBRIC = """
Use this SAME rubric for every interview answer.

Score 0-100 based on:

1. Relevance - 20 points
   Does the answer directly address the question?

2. Correctness - 25 points
   Are the technical facts and concepts accurate?

3. Completeness - 20 points
   Does the answer cover the important parts?

4. Technical Concepts - 25 points
   Does the student demonstrate appropriate technical
   understanding for their level?

5. Communication - 10 points
   Is the answer clear, understandable, and structured?

This is educational guidance, NOT a hiring decision.
The score must not be presented as a prediction of employability
or a hiring outcome.
"""


def _clean_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _fallback_evaluation(question, answer):
    if not answer.strip():
        return {
            "strength": "No answer was provided.",
            "improve": "Provide a clear technical answer.",
            "recommendation": "Review the core concepts related to this question.",
            "next_practice": "Practice explaining the concept using a simple example.",
            "score": 0,
        }

    return {
        "strength": "You attempted the question and communicated your understanding.",
        "improve": "Add more precise technical concepts and supporting examples.",
        "recommendation": "Review the core concept and connect it to a practical example.",
        "next_practice": "Practice answering the same question using definition, explanation, and example.",
        "score": 50,
    }


def evaluate_answer(question, answer):
    system = f"""
You are an educational AI interview evaluator.

{RUBRIC}

Return STRICT JSON ONLY.

Required format:

{{
  "strength": "...",
  "improve": "...",
  "recommendation": "...",
  "next_practice": "...",
  "score": 0
}}

The score must be an integer from 0 to 100.

Do not make hiring decisions.
Do not say whether the student should or should not be hired.
"""

    user = f"""
Interview question:
{question}

Student answer:
{answer}

Evaluate the answer using the fixed rubric.
Give concise, actionable feedback.

Return JSON only.
"""

    try:
        raw = call_claude(system, user)
        result = json.loads(_clean_json(raw))

        required = {
            "strength",
            "improve",
            "recommendation",
            "next_practice",
            "score",
        }

        if not required.issubset(result.keys()):
            raise ValueError("Missing evaluation fields.")

        result["score"] = max(0, min(100, int(result["score"])))

        return result

    except Exception:
        return _fallback_evaluation(question, answer)