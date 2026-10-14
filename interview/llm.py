
import os
import json
import re
import anthropic


# ============================================================
# CONFIGURATION
# ============================================================

# True = offline mode, no API calls or API charges.
# False = use the configured Anthropic API.
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
# LOCAL INTERVIEW QUESTION GENERATOR
# ============================================================

def _mock_question_response(system, user):
    """Generate questions locally from supplied skill gaps."""

    try:
        match = re.search(
            r"Verified skill gaps:\s*(\[.*?\])",
            user,
            re.DOTALL | re.IGNORECASE,
        )
        data = json.loads(match.group(1)) if match else []
    except (AttributeError, json.JSONDecodeError):
        data = []

    if not isinstance(data, list):
        data = []

    question_bank = {
        "Excel": "How would you use Excel to clean and analyze a dataset?",
        "Statistics": "What is the difference between mean, median, and standard deviation?",
        "Data Visualization": "How would you choose an appropriate chart for presenting a dataset?",
        "Pandas": "How would you use Pandas to load, clean, and analyze a dataset?",
        "Power BI": "What is Power BI and how can it be used to create useful dashboards?",
        "Communication": "How would you explain a technical data finding to a non-technical person?",
        "Business Acumen": "Why are business requirements important when analyzing data?",
        "Data Cleaning": "What steps would you take to clean a dataset?",
        "Tableau": "How would you use Tableau to communicate insights?",
        "Google Sheets": "How can Google Sheets support collaborative data analysis?",
        "Critical Thinking": "How would you determine whether a conclusion from data is reliable?",
        "Machine Learning": "What is the difference between supervised and unsupervised learning?",
        "Deep Learning": "What is deep learning, and how is it different from traditional machine learning?",
        "SQL": "How would you use SQL to retrieve and analyze data?",
        "Python": "Explain how you have used Python in a project.",
        "Git": "Why is Git useful when developing software?",
        "Data Structures": "Why are data structures important when developing software?",
        "Algorithms": "What is an algorithm, and how would you choose one for a problem?",
        "Cloud Computing": "What is cloud computing, and what are common use cases?",
        "Docker": "What problem does Docker solve in software development?",
        "Kubernetes": "What is Kubernetes used for?",
        "Networking": "What are the basic components of computer networking?",
        "Linux": "Why is Linux commonly used in server environments?",
        "Security": "What are basic practices for protecting an application?",
        "HTML": "What is HTML used for in a web application?",
        "CSS": "How does CSS control the appearance of a web page?",
        "JavaScript": "What role does JavaScript play in a web application?",
        "React": "What is React, and why is it useful?",
        "Node.js": "What is Node.js, and where can it be used?",
        "Testing": "Why is software testing important?",
        "Problem Solving": "How would you solve an unfamiliar programming problem?",
        "System Design": "What factors matter when designing a scalable software system?",
    }

    priority_order = {"High": 0, "Medium": 1, "Low": 2}

    valid_gaps = [
        gap for gap in data
        if isinstance(gap, dict)
        and isinstance(gap.get("skill"), str)
        and gap["skill"].strip()
    ]

    valid_gaps.sort(
        key=lambda gap: priority_order.get(
            gap.get("priority", "Medium"), 1
        )
    )

    questions = []

    for gap in valid_gaps:
        skill = gap["skill"].strip()
        priority = gap.get("priority", "Medium")

        questions.append({
            "question": question_bank.get(
                skill,
                f"Explain the key concepts of {skill} and how you would apply them in a practical project."
            ),
            "why": (
                f"{skill} is required for the target career, and your "
                f"profile shows a {priority}-priority skill gap in {skill}."
            ),
            "skill": skill,
            "difficulty": "Easy" if priority == "Low" else "Medium",
        })

    return json.dumps(questions)


# ============================================================
# LOCAL INTERVIEW EVALUATOR
# ============================================================

def _mock_evaluation_response(user):
    """
    Offline rule-based evaluator.

    Important: this is a limited rubric-based grader, not a
    general-purpose semantic fact-checker.
    """

    question_match = re.search(
        r"Interview question:\s*(.*?)\s*Student answer:",
        user,
        re.DOTALL | re.IGNORECASE,
    )

    answer_match = re.search(
        r"Student answer:\s*(.*?)(?:\s*Evaluate the answer|\Z)",
        user,
        re.DOTALL | re.IGNORECASE,
    )

    question = question_match.group(1).strip() if question_match else ""
    answer = answer_match.group(1).strip() if answer_match else ""

    def make_result(
        score, strength, improve, recommendation, next_practice
    ):
        return json.dumps({
            "strength": strength,
            "improve": improve,
            "recommendation": recommendation,
            "next_practice": next_practice,
            "score": int(max(0, min(100, score))),
        })

    def zero_result(reason, correction, practice):
        return make_result(
            0,
            reason,
            correction,
            "Review the topic and correct the misunderstanding.",
            practice,
        )

    if not answer:
        return zero_result(
            "No answer was provided.",
            "Provide an answer that addresses the question.",
            "Practise explaining the concept in your own words.",
        )

    q = question.lower()
    a = answer.lower()

    words = re.findall(r"\b[a-zA-Z]+\b", answer)

    if len(words) < 3:
        return zero_result(
            "The answer is too short to demonstrate understanding.",
            "Explain the concept using a complete sentence.",
            "Write a short explanation in your own words.",
        )

    # Reject obvious irrelevant answers for technical questions.
    irrelevant_phrases = [
        "i like playing cricket",
        "watching movies",
        "my favorite food",
        "i love dancing",
        "i like music",
    ]

    if any(phrase in a for phrase in irrelevant_phrases):
        return zero_result(
            "The answer is unrelated to the interview question.",
            "Answer the technical question directly.",
            "Identify the main concept and explain its purpose.",
        )

    # Each concept group represents one marking point.
    # A group is matched if at least one alternative is present.
    concept_rules = [
        (
            ["supervised", "unsupervised"],
            [
                ["supervised learning"],
                ["labelled data", "labeled data", "labelled examples",
                 "labeled examples"],
                ["unsupervised learning"],
                ["unlabelled data", "unlabeled data",
                 "without labels", "no labels"],
            ],
        ),
        (
            ["mean", "median", "standard deviation"],
            [
                ["mean", "average"],
                ["median", "middle value"],
                ["standard deviation", "spread", "dispersion"],
            ],
        ),
        (
            ["html"],
            [
                ["structure", "markup", "elements"],
                ["web page", "website", "web document"],
            ],
        ),
        (
            ["css"],
            [
                ["style", "styling", "appearance", "presentation"],
                ["layout", "color", "font", "spacing"],
            ],
        ),
        (
            ["sql"],
            [
                ["query", "select", "retrieve"],
                ["database", "table"],
                ["filter", "join", "sort", "aggregate", "analyze"],
            ],
        ),
        (
            ["overfitting"],
            [
                ["training data", "training set"],
                ["unseen data", "test data", "generalization",
                 "generalisation"],
                ["memorize", "memorise", "performs poorly"],
            ],
        ),
        (
            ["deep learning"],
            [
                ["neural network", "neural networks"],
                ["layers", "multiple layers"],
                ["learn features", "complex patterns", "representations"],
            ],
        ),
        (
            ["docker"],
            [
                ["container", "containers"],
                ["dependencies", "environment"],
                ["portable", "consistent", "isolation"],
            ],
        ),
        (
            ["kubernetes"],
            [
                ["container", "containers"],
                ["orchestration", "manage containers"],
                ["scaling", "deployment", "availability"],
            ],
        ),
        (
            ["git"],
            [
                ["version control"],
                ["track changes", "history"],
                ["branch", "commit", "collaboration", "merge"],
            ],
        ),
        (
            ["regression"],
            [
                ["continuous value", "continuous output",
                 "numerical value", "predict a value"],
                ["prediction", "predict"],
            ],
        ),
        (
            ["classification"],
            [
                ["class", "category", "categories", "label"],
                ["predict", "assign", "categorize", "categorise"],
            ],
        ),
        (
            ["data structures"],
            [
                ["organize", "organise", "store", "manage"],
                ["efficient", "access", "search", "retrieve", "modify"],
                ["array", "list", "tree", "stack", "queue", "hash"],
            ],
        ),
        (
            ["algorithm"],
            [
                ["steps", "procedure", "instructions"],
                ["solve", "solution"],
                ["problem", "task"],
            ],
        ),
        (
            ["machine learning"],
            [
                ["data"],
                ["model"],
                ["training", "patterns", "prediction", "learn"],
            ],
        ),
        (
            ["power bi"],
            [
                ["dashboard"],
                ["visualization", "visualisation", "chart", "graph"],
                ["report", "data", "insight"],
            ],
        ),
        (
            ["data visualization", "data visualisation"],
            [
                ["chart", "graph", "visualization", "visualisation"],
                ["data"],
                ["trend", "comparison", "pattern", "relationship"],
            ],
        ),
        (
            ["data cleaning"],
            [
                ["missing values", "null values", "duplicates"],
                ["clean", "remove", "correct", "handle", "impute"],
                ["data"],
            ],
        ),
        (
            ["cloud computing"],
            [
                ["cloud"],
                ["internet", "remote server", "servers"],
                ["storage", "compute", "resources", "scaling"],
            ],
        ),
        (
            ["node.js", "node js"],
            [
                ["javascript"],
                ["server", "backend", "runtime"],
            ],
        ),
        (
            ["react"],
            [
                ["component", "components"],
                ["user interface", "ui"],
                ["reusable", "state", "props"],
            ],
        ),
        (
            ["networking"],
            [
                ["router", "switch", "ip", "protocol", "packet"],
                ["communication", "devices", "data"],
            ],
        ),
        (
            ["database"],
            [
                ["table", "records", "data"],
                ["query", "retrieve", "store", "manage"],
            ],
        ),
    ]

    selected_groups = None

    for question_terms, groups in concept_rules:
        if all(term in q for term in question_terms):
            selected_groups = groups
            break

    # --------------------------------------------------------
    # Specific contradiction check: supervised learning
    # --------------------------------------------------------

    if (
        selected_groups is not None
        and "supervised" in q
        and "unsupervised" in q
    ):
        supervised_wrong = re.search(
            r"supervised learning.{0,120}"
            r"(?:unlabelled|unlabeled|without labels|no labels)",
            a,
        )

        unsupervised_wrong = re.search(
            r"unsupervised learning.{0,120}"
            r"(?:labelled data|labeled data|uses labels|with labels)",
            a,
        )

        if supervised_wrong and unsupervised_wrong:
            return zero_result(
                "The answer reverses the definitions.",
                "Supervised learning uses labelled data; "
                "unsupervised learning works with unlabelled data.",
                "Explain both learning types and give an example of each.",
            )

    # --------------------------------------------------------
    # Specific relevance check: data structures
    # --------------------------------------------------------

    if "data structures" in q:
        # Mentioning the topic alone is not enough.
        relevant_purpose = any(
            term in a
            for term in [
                "organize", "organise", "store", "manage",
                "access", "retrieve", "search", "modify",
            ]
        )

        irrelevant_only = (
            any(term in a for term in ["decorate", "decoration", "styling"])
            and not relevant_purpose
        )

        if irrelevant_only or not relevant_purpose:
            return zero_result(
                "The answer does not explain the purpose of data structures.",
                "Data structures organize and store data to support efficient access and modification.",
                "Explain why data organization matters and give an example.",
            )

    # --------------------------------------------------------
    # Score supported questions
    # --------------------------------------------------------

    if selected_groups is not None:
        matched_groups = sum(
            1
            for group in selected_groups
            if any(term in a for term in group)
        )

        if matched_groups == 0:
            return zero_result(
                "The answer does not demonstrate the expected concepts.",
                "Cover the main concepts required by the question.",
                "Try again using the key concepts in your own words.",
            )

        score = round(100 * matched_groups / len(selected_groups))

        if score < 100:
            return make_result(
                score,
                "The answer includes some expected concepts.",
                "Some important concepts are missing or need more explanation.",
                "Study the missing concepts and explain how they relate.",
                "Try again and address every part of the question.",
            )

        return make_result(
            100,
            "The answer mentions all expected concepts.",
            "Ensure that the concepts are explained accurately, not just named.",
            "Continue practising clear technical explanations.",
            "Explain the concepts in your own words and give an example.",
        )

    # No rubric: do not pretend correctness has been verified.
    return make_result(
        0,
        "Automatic correctness checking is not configured for this question.",
        "The offline evaluator cannot reliably verify this answer.",
        "Review the answer against trusted course material.",
        "Add a question-specific marking rubric before grading this question.",
    )


# ============================================================
# MOCK RESPONSE ROUTER
# ============================================================

def _mock_response(system, user):
    system_lower = system.lower()

    if "interview-question engine" in system_lower:
        return _mock_question_response(system, user)

    if "interview evaluator" in system_lower:
        return _mock_evaluation_response(user)

    return "Mock response generated successfully."


# ============================================================
# MAIN LLM FUNCTION
# ============================================================

def call_claude(system, user):
    """Central LLM helper for the interview module."""

    if USE_MOCK_LLM:
        return _mock_response(system, user)

    api_key = _get_api_key()

    if not api_key:
        raise RuntimeError("Anthropic API key not found.")

    try:
        client = anthropic.Anthropic(api_key=api_key)

        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=2000,
            system=system,
            messages=[
                {"role": "user", "content": user}
            ],
        )

        for block in response.content:
            if block.type == "text":
                return block.text

        raise RuntimeError("Claude returned no text.")

    except anthropic.APIError as exc:
        raise RuntimeError(f"Claude API error: {exc}") from exc
