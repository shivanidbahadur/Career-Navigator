import os
import json
import re
import anthropic


# ============================================================
# CONFIGURATION
# ============================================================

# Keep True while developing without Anthropic billing.
# Change to False later if you have an active Anthropic account.
USE_MOCK_LLM = True

MODEL_NAME = "claude-sonnet-5"


# ============================================================
# API KEY
# ============================================================

def _get_api_key():
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key:
        return api_key

    try:
        import streamlit as st
        return st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        return None


# ============================================================
# LOCAL INTERVIEW QUESTION MOCK
# ============================================================

def _mock_question_response(system, user):
    """
    Local development question generator.

    No API call and no billing required.
    """

    try:
        data = json.loads(
            re.search(
                r"Verified skill gaps:\s*(\[.*?\])",
                user,
                re.DOTALL
            ).group(1)
        )
    except Exception:

        # Safe fallback
        data = [
            {
                "skill": "Machine Learning",
                "priority": "High",
                "weight": 5
            },
            {
                "skill": "Statistics",
                "priority": "High",
                "weight": 4
            }
        ]


    # --------------------------------------------------------
    # Find existing student skills
    # --------------------------------------------------------

    try:
        profile_match = re.search(
            r"Student profile:\s*(\{.*?\})\s*Rules:",
            user,
            re.DOTALL
        )

        if profile_match:
            profile = json.loads(
                profile_match.group(1)
            )
        else:
            profile = {}

    except Exception:
        profile = {}


    existing_skills = profile.get(
        "skills",
        []
    )

    if not existing_skills:
        existing_skills = ["your existing technical skills"]


    # --------------------------------------------------------
    # Warm-up
    # --------------------------------------------------------

    warmup_skill = existing_skills[0]

    questions = [
        {
            "question": (
                f"Briefly explain a project or task where "
                f"you used {warmup_skill}."
            ),
            "why": (
                f"This is a warm-up because your profile "
                f"already shows {warmup_skill}."
            ),
            "skill": warmup_skill,
            "difficulty": "Easy"
        }
    ]


    # --------------------------------------------------------
    # Gap questions
    # --------------------------------------------------------

    question_bank = {

        "Excel":
            "How would you use Excel to clean and analyze a dataset?",

        "Statistics":
            "What is the difference between mean, median, and standard deviation?",

        "Data Visualization":
            "How would you choose an appropriate chart for presenting a dataset?",

        "Pandas":
            "How would you use Pandas to load, clean, and analyze a dataset?",

        "Power BI":
            "What is Power BI and how can it be used to create useful dashboards?",

        "Communication":
            "How would you explain a technical data finding to a non-technical person?",

        "Business Acumen":
            "Why is understanding business requirements important when analyzing data?",

        "Data Cleaning":
            "What steps would you take to clean a dataset before analysis?",

        "Tableau":
            "How would you use Tableau to communicate insights from a dataset?",

        "Google Sheets":
            "How can Google Sheets be used for collaborative data analysis?",

        "Critical Thinking":
            "How would you determine whether a conclusion from a dataset is reliable?",

        "Machine Learning":
            "What is the difference between supervised and unsupervised learning?",

        "Deep Learning":
            "What is deep learning and how is it different from traditional machine learning?",

        "SQL":
            "How would you use SQL to retrieve and analyze data from a database?",

        "Python":
            "Explain how you have used Python in a project.",

        "Git":
            "Why is Git useful when developing a software project?",

        "Data Structures":
            "Why are data structures important when developing software?",

        "Algorithms":
            "What is an algorithm and how would you choose an appropriate one for a problem?",

        "Cloud Computing":
            "What is cloud computing and what are some common use cases?",

        "Docker":
            "What problem does Docker solve in software development?",

        "Kubernetes":
            "What is Kubernetes used for in a cloud or DevOps environment?",

        "Networking":
            "What are the basic components involved in computer networking?",

        "Linux":
            "Why is Linux commonly used in server and cloud environments?",

        "Security":
            "What are some basic practices for protecting an application or system?",

        "HTML":
            "What is HTML used for when building a web application?",

        "CSS":
            "How does CSS control the appearance of a web page?",

        "JavaScript":
            "What role does JavaScript play in a web application?",

        "React":
            "What is React and why is it useful for building user interfaces?",

        "Node.js":
            "What is Node.js and where can it be used?",

        "Testing":
            "Why is software testing important before releasing an application?",

        "Problem Solving":
            "Describe how you would approach solving an unfamiliar programming problem.",

        "System Design":
            "What factors should be considered when designing a scalable software system?"
    }


    # --------------------------------------------------------
    # Generate ONE question for every real gap
    # --------------------------------------------------------

    priority_order = {
        "High": 0,
        "Medium": 1,
        "Low": 2
    }

    sorted_gaps = sorted(
        data,
        key=lambda x: priority_order.get(
            x.get("priority", "Medium"),
            1
        )
    )


    for gap in sorted_gaps:

        skill = gap.get(
            "skill",
            "Unknown Skill"
        )

        priority = gap.get(
            "priority",
            "Medium"
        )

        question = question_bank.get(
            skill,
            (
                f"Explain the key concepts of {skill} "
                f"and describe how you would apply them "
                f"in a practical project."
            )
        )

        questions.append(
            {
                "question": question,
                "why": (
                    f"{skill} is required for the target career "
                    f"and your profile shows a {priority}-priority "
                    f"skill gap in {skill}."
                ),
                "skill": skill,
                "difficulty": (
                    "Medium" if priority == "High"
                    else "Easy" if priority == "Low"
                    else "Medium"
                )
            }
        )


    return json.dumps(
        questions
    )


# ============================================================
# LOCAL DYNAMIC INTERVIEW EVALUATOR
# ============================================================

def _mock_evaluation_response(user):
    """
    Local rule-based evaluator.

    This replaces the previous fixed 65/100 response.

    It evaluates:
      - relevance
      - completeness
      - technical terminology
      - practical example
      - answer structure
      - communication

    This is an educational offline approximation,
    not a true LLM semantic evaluation.
    """

    # --------------------------------------------------------
    # Extract question and answer
    # --------------------------------------------------------

    question_match = re.search(
        r"Interview question:\s*(.*?)\s*Student answer:",
        user,
        re.DOTALL | re.IGNORECASE
    )

    answer_match = re.search(
        r"Student answer:\s*(.*?)(?:\s*Evaluate the answer|\Z)",
        user,
        re.DOTALL | re.IGNORECASE
    )

    question = (
        question_match.group(1).strip()
        if question_match
        else ""
    )

    answer = (
        answer_match.group(1).strip()
        if answer_match
        else ""
    )


    # --------------------------------------------------------
    # Empty answer
    # --------------------------------------------------------

    if not answer:

        return json.dumps(
            {
                "strength": "No answer was provided.",
                "improve": (
                    "Provide a complete answer that directly "
                    "addresses the question."
                ),
                "recommendation": (
                    "Review the relevant concept before attempting "
                    "the question again."
                ),
                "next_practice": (
                    "Practice answering using definition, "
                    "explanation, and example."
                ),
                "score": 0
            }
        )


    # --------------------------------------------------------
    # Normalize text
    # --------------------------------------------------------

    answer_lower = answer.lower()
    question_lower = question.lower()

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        answer_lower
    )

    word_count = len(words)


    # --------------------------------------------------------
    # Score 1 — Relevance
    # --------------------------------------------------------

    question_words = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            question_lower
        )
    )

    answer_words = set(words)

    overlap = question_words.intersection(
        answer_words
    )

    if len(overlap) >= 4:
        relevance = 20

    elif len(overlap) >= 2:
        relevance = 16

    elif len(overlap) >= 1:
        relevance = 12

    else:
        relevance = 6


    # --------------------------------------------------------
    # Score 2 — Completeness
    # --------------------------------------------------------

    if word_count >= 100:
        completeness = 20

    elif word_count >= 70:
        completeness = 17

    elif word_count >= 45:
        completeness = 14

    elif word_count >= 25:
        completeness = 10

    elif word_count >= 10:
        completeness = 6

    else:
        completeness = 3


    # --------------------------------------------------------
    # Score 3 — Technical concepts
    # --------------------------------------------------------

    technical_terms = [
        "algorithm",
        "data",
        "model",
        "feature",
        "dataset",
        "database",
        "query",
        "classification",
        "regression",
        "mean",
        "median",
        "standard deviation",
        "visualization",
        "dashboard",
        "clean",
        "analysis",
        "python",
        "sql",
        "machine learning",
        "statistics",
        "api",
        "system",
        "network",
        "security",
        "container",
        "docker",
        "kubernetes",
        "testing",
        "class",
        "object",
        "function",
        "code",
        "project",
        "deployment",
        "cloud",
        "server",
        "frontend",
        "backend"
    ]

    matched_terms = [
        term
        for term in technical_terms
        if term in answer_lower
    ]

    if len(matched_terms) >= 5:
        technical = 25

    elif len(matched_terms) >= 3:
        technical = 20

    elif len(matched_terms) >= 2:
        technical = 15

    elif len(matched_terms) >= 1:
        technical = 10

    else:
        technical = 4


    # --------------------------------------------------------
    # Score 4 — Practical example
    # --------------------------------------------------------

    example_indicators = [
        "example",
        "project",
        "used",
        "implemented",
        "developed",
        "built",
        "created",
        "application",
        "in my project",
        "for instance"
    ]

    example_count = sum(
        1
        for indicator in example_indicators
        if indicator in answer_lower
    )

    if example_count >= 2:
        example_score = 10

    elif example_count == 1:
        example_score = 7

    else:
        example_score = 3


    # --------------------------------------------------------
    # Score 5 — Communication
    # --------------------------------------------------------

    sentences = re.split(
        r"[.!?]+",
        answer
    )

    useful_sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    if len(useful_sentences) >= 4:
        communication = 10

    elif len(useful_sentences) >= 3:
        communication = 8

    elif len(useful_sentences) >= 2:
        communication = 6

    else:
        communication = 4


    # --------------------------------------------------------
    # Calculate final score
    #
    # Relevance       20
    # Correctness     25
    # Completeness    20
    # Technical       25
    # Communication   10
    #
    # We approximate correctness using technical coverage.
    # --------------------------------------------------------

    correctness = min(
        25,
        int(
            technical * 0.8
            + relevance * 0.2
        )
    )

    score = (
        relevance
        + correctness
        + completeness
        + technical
        + example_score
        + communication
    )

    # Maximum is 110 because we have example_score separately.
    # Normalize to 100.
    score = int(
        score * 100 / 110
    )

    score = max(
        0,
        min(
            100,
            score
        )
    )


    # --------------------------------------------------------
    # Dynamic feedback
    # --------------------------------------------------------

    if score >= 85:

        strength = (
            "The answer is detailed, relevant, and includes "
            "useful technical concepts and practical context."
        )

        improve = (
            "Continue improving precision and depth by explaining "
            "why the technical approach works."
        )

    elif score >= 70:

        strength = (
            "The answer addresses the question and demonstrates "
            "a reasonable understanding of the topic."
        )

        improve = (
            "Add more technical details and a clearer practical "
            "example to strengthen the explanation."
        )

    elif score >= 50:

        strength = (
            "The answer shows an attempt to explain the concept "
            "and contains some relevant information."
        )

        improve = (
            "Expand the technical explanation and connect the "
            "concept to a concrete project or example."
        )

    elif score >= 30:

        strength = (
            "The answer contains some relevant ideas."
        )

        improve = (
            "The answer needs more technical detail, clearer "
            "explanation, and better connection to the question."
        )

    else:

        strength = (
            "The answer shows an attempt to respond."
        )

        improve = (
            "Provide a more complete and technically focused "
            "answer that directly addresses the question."
        )


    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    if technical >= 20:

        recommendation = (
            "Your technical coverage is developing well. "
            "Focus on explaining concepts more precisely."
        )

    elif technical >= 10:

        recommendation = (
            "Review the core technical concepts and include "
            "more relevant terminology in your explanation."
        )

    else:

        recommendation = (
            "Review the core concept and learn the key technical "
            "terms before practicing this question again."
        )


    # --------------------------------------------------------
    # Next practice
    # --------------------------------------------------------

    if word_count < 25:

        next_practice = (
            "Practice giving a longer answer using three parts: "
            "definition, explanation, and example."
        )

    elif example_count == 0:

        next_practice = (
            "Practice answering the concept and include one "
            "real project or practical example."
        )

    elif len(matched_terms) < 2:

        next_practice = (
            "Practice explaining the concept using at least "
            "two or three relevant technical terms."
        )

    else:

        next_practice = (
            "Practice giving the same explanation more clearly "
            "and with a stronger technical justification."
        )


    # --------------------------------------------------------
    # Return JSON
    # --------------------------------------------------------

    return json.dumps(
        {
            "strength": strength,
            "improve": improve,
            "recommendation": recommendation,
            "next_practice": next_practice,
            "score": score
        }
    )


# ============================================================
# MOCK RESPONSE ROUTER
# ============================================================

def _mock_response(system, user):

    system_lower = system.lower()

    if "interview-question engine" in system_lower:

        return _mock_question_response(
            system,
            user
        )

    if "interview evaluator" in system_lower:

        return _mock_evaluation_response(
            user
        )

    return "Mock response generated successfully."


# ============================================================
# MAIN LLM FUNCTION
# ============================================================

def call_claude(system, user):
    """
    Central LLM helper used by the Member 4 interview module.
    """

    # --------------------------------------------------------
    # Offline mode
    # --------------------------------------------------------

    if USE_MOCK_LLM:

        return _mock_response(
            system,
            user
        )


    # --------------------------------------------------------
    # Real Claude mode
    # --------------------------------------------------------

    api_key = _get_api_key()

    if not api_key:

        raise RuntimeError(
            "Anthropic API key not found."
        )


    try:

        client = anthropic.Anthropic(
            api_key=api_key
        )

        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=2000,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": user
                }
            ]
        )


        for block in response.content:

            if block.type == "text":

                return block.text


        raise RuntimeError(
            "Claude returned no text."
        )


    except anthropic.APIError as exc:

        raise RuntimeError(
            f"Claude API error: {exc}"
        ) from exc