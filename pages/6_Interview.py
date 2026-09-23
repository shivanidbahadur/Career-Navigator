import streamlit as st

from core.gaps import get_skill_gaps
from interview.questions import generate_questions
from interview.evaluate import evaluate_answer


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Career Navigator - Interview",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Personalized Mock Interview")
st.caption("Interview questions are generated from your verified career skill gaps.")


# ============================================================
# RESPONSIBLE AI DISCLAIMER
# ============================================================

st.info(
    "⚠️ Educational use only: Interview scores and feedback are intended "
    "for learning and practice. They are not hiring decisions or predictions "
    "of employment outcomes."
)


# ============================================================
# 1. GET USER PROFILE
# ============================================================

# First try the complete profile dictionary
profile = st.session_state.get("profile", {})

# If the Profile page stores values individually,
# build the profile from those session-state values.
if not profile:

    profile = {
        "name": st.session_state.get("name", ""),
        "email": st.session_state.get("email", ""),
        "level": st.session_state.get("level", "beginner"),
        "skills": st.session_state.get("skills", []),
        "target_career": st.session_state.get("target_career"),
        "target_career_name": st.session_state.get(
            "target_career_name",
            st.session_state.get("target_career")
        )
    }


# Make sure skills is always a list
user_skills = profile.get("skills", [])

if not isinstance(user_skills, list):
    user_skills = []


target_career = profile.get("target_career")

target_career_name = profile.get(
    "target_career_name",
    target_career
)

student_level = profile.get(
    "level",
    "beginner"
)


# ============================================================
# VALIDATE PROFILE
# ============================================================

if not target_career:

    st.warning(
        "Please select a target career in your Profile page "
        "before starting the mock interview."
    )

    st.stop()



if not isinstance(user_skills, list):
    user_skills = []


# ============================================================
# 3. GET VERIFIED SKILL GAPS FROM MEMBER 1
# ============================================================

try:
    gaps = get_skill_gaps(
        user_skills,
        target_career
    )

except Exception as exc:
    st.error(
        "Unable to load the verified skill gaps."
    )
    st.caption(f"Technical details: {exc}")
    st.stop()


# ============================================================
# 4. NO SKILL GAPS
# ============================================================

if not gaps:
    st.success(
        f"No verified skill gaps were found for {target_career_name}."
    )

    st.write(
        "The interview engine requires verified skill gaps before it "
        "can generate gap-based interview questions."
    )

    st.stop()


# ============================================================
# 5. DISPLAY VERIFIED GAPS
# ============================================================

st.subheader("📊 Your Verified Skill Gaps")

st.write(
    "The interview questions below are based only on the skill gaps "
    "identified by the career gap-analysis module."
)

priority_order = {
    "High": 0,
    "Medium": 1,
    "Low": 2
}

sorted_gaps = sorted(
    gaps,
    key=lambda gap: priority_order.get(
        gap.get("priority", "Medium"),
        1
    )
)


# Display gap summary
for gap in sorted_gaps:
    skill = gap.get("skill", "Unknown Skill")
    priority = gap.get("priority", "Medium")
    weight = gap.get("weight", "-")

    if priority == "High":
        badge = "🔴 High"
    elif priority == "Medium":
        badge = "🟡 Medium"
    else:
        badge = "🟢 Low"

    st.markdown(
        f"- **{skill}** — {badge} priority "
        f"(weight: {weight})"
    )


st.divider()


# ============================================================
# 6. GENERATE INTERVIEW QUESTIONS
# ============================================================

if (
    "interview_questions" not in st.session_state
    or st.session_state.get("interview_career") != target_career
    or st.session_state.get("interview_gap_signature") != str(sorted_gaps)
):

    questions = generate_questions(
        gaps=sorted_gaps,
        career_id=target_career,
        profile=profile
    )

    st.session_state["interview_questions"] = questions
    st.session_state["interview_index"] = 0
    st.session_state["interview_results"] = []
    st.session_state["interview_career"] = target_career
    st.session_state["interview_gap_signature"] = str(sorted_gaps)

else:
    questions = st.session_state["interview_questions"]


# ============================================================
# 7. CHECK QUESTIONS
# ============================================================

if not questions:
    st.warning(
        "No interview questions could be generated from the verified "
        "skill gaps."
    )
    st.stop()


# ============================================================
# 8. CURRENT QUESTION
# ============================================================

current_index = st.session_state.get(
    "interview_index",
    0
)


# Interview completed
if current_index >= len(questions):

    st.success("🎉 Interview completed!")

    results = st.session_state.get(
        "interview_results",
        []
    )

    if results:

        st.subheader("📈 Interview Summary")

        scores = [
            result["score"]
            for result in results
            if isinstance(result.get("score"), (int, float))
        ]

        if scores:
            average_score = sum(scores) / len(scores)

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Average Score",
                    f"{average_score:.1f}/100"
                )

            with col2:
                st.metric(
                    "Questions Answered",
                    len(results)
                )

        # ----------------------------------------------------
        # Weak skills
        # ----------------------------------------------------

        weak_results = [
            result
            for result in results
            if result.get("score", 100) < 60
        ]

        if weak_results:

            st.subheader("📚 Skills for More Practice")

            weak_skills = []

            for result in weak_results:
                skill = result.get("skill")

                if skill and skill not in weak_skills:
                    weak_skills.append(skill)

            for skill in weak_skills:
                st.warning(
                    f"**{skill}** — additional practice recommended."
                )

            st.session_state["weak_interview_skills"] = weak_skills

        else:

            st.success(
                "No interview skill scored below 60."
            )

            st.session_state["weak_interview_skills"] = []

        # ----------------------------------------------------
        # Detailed results
        # ----------------------------------------------------

        st.subheader("📝 Question Results")

        for number, result in enumerate(results, start=1):

            score = result.get("score", 0)
            skill = result.get("skill", "Unknown Skill")
            question = result.get("question", "")

            with st.expander(
                f"Question {number} — {skill} — {score}/100"
            ):

                st.write("**Question:**")
                st.write(question)

                st.write(
                    f"**Score:** {score}/100"
                )

    if st.button(
        "🔄 Restart Interview",
        use_container_width=True
    ):

        for key in [
            "interview_questions",
            "interview_index",
            "interview_results",
            "interview_career",
            "interview_gap_signature",
            "weak_interview_skills"
        ]:
            st.session_state.pop(key, None)

        st.rerun()

    st.stop()


# ============================================================
# 9. DISPLAY CURRENT QUESTION
# ============================================================

current_question = questions[current_index]

question_number = current_index + 1
total_questions = len(questions)

st.subheader(
    f"Question {question_number} of {total_questions}"
)


# ============================================================
# 10. QUESTION INFORMATION
# ============================================================

skill = current_question.get(
    "skill",
    "Unknown Skill"
)

difficulty = current_question.get(
    "difficulty",
    "Medium"
)

question_text = current_question.get(
    "question",
    ""
)

why = current_question.get(
    "why",
    ""
)


# ============================================================
# 11. SKILL + DIFFICULTY
# ============================================================

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"**🎯 Skill:** `{skill}`"
    )

with col2:
    st.markdown(
        f"**📊 Difficulty:** `{difficulty}`"
    )


# ============================================================
# 12. WHY THIS QUESTION?
# ============================================================

st.info(
    f"💡 **Why this question?**\n\n{why}"
)


# ============================================================
# 13. QUESTION
# ============================================================

st.markdown("### ❓ Interview Question")

st.markdown(
    f"**{question_text}**"
)


# ============================================================
# 14. ANSWER
# ============================================================

answer_key = f"answer_{current_index}"

answer = st.text_area(
    "Your Answer",
    height=180,
    placeholder="Type your answer here...",
    key=answer_key
)


# ============================================================
# 15. SUBMIT ANSWER
# ============================================================

if st.button(
    "Submit Answer",
    type="primary",
    use_container_width=True
):

    if not answer.strip():

        st.warning(
            "Please enter an answer before submitting."
        )

    else:

        with st.spinner("Evaluating your answer..."):

            feedback = evaluate_answer(
                question_text,
                answer
            )

        # Store feedback in session state
        st.session_state["current_feedback"] = feedback
        st.session_state["current_answer"] = answer
        st.session_state["answer_submitted"] = True

        # Store result
        result = {
            "skill": skill,
            "question": question_text,
            "score": feedback.get("score", 0)
        }

        results = st.session_state.get(
            "interview_results",
            []
        )

        # Remove any previous result for this question
        results = [
            r for r in results
            if r.get("question") != question_text
        ]

        results.append(result)

        st.session_state["interview_results"] = results

        st.rerun()


# ============================================================
# 16. DISPLAY FEEDBACK AFTER SUBMISSION
# ============================================================

if st.session_state.get("answer_submitted", False):

    feedback = st.session_state.get(
        "current_feedback",
        {}
    )

    st.divider()

    st.subheader("📋 AI Feedback")

    score = feedback.get(
        "score",
        0
    )

    st.metric(
        "Score",
        f"{score}/100"
    )


    # --------------------------------------------------------
    # FEEDBACK COLUMNS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### 💪 Strength")

        st.write(
            feedback.get(
                "strength",
                "No strength feedback available."
            )
        )


    with col2:

        st.markdown("### 🔧 Needs Improvement")

        st.write(
            feedback.get(
                "improve",
                "No improvement feedback available."
            )
        )


    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------

    st.markdown("### 💡 Recommendation")

    st.write(
        feedback.get(
            "recommendation",
            "Review the relevant concept."
        )
    )


    # --------------------------------------------------------
    # NEXT PRACTICE
    # --------------------------------------------------------

    st.markdown("### 📚 Next Practice")

    st.write(
        feedback.get(
            "next_practice",
            "Practice the concept again."
        )
    )


    # ========================================================
    # 17. NEXT QUESTION
    # ========================================================

    if current_index + 1 < total_questions:

        if st.button(
            "➡️ Next Question",
            use_container_width=True
        ):

            # Move to next question
            st.session_state["interview_index"] = (
                current_index + 1
            )

            # Clear previous question state
            st.session_state["answer_submitted"] = False
            st.session_state["current_feedback"] = None
            st.session_state["current_answer"] = ""

            st.rerun()

    else:

        if st.button(
            "🎉 Finish Interview",
            use_container_width=True
        ):

            st.session_state["interview_index"] = (
                total_questions
            )

            st.session_state["answer_submitted"] = False
            st.session_state["current_feedback"] = None
            st.session_state["current_answer"] = ""

            st.rerun()


# ============================================================
# 18. PROGRESS
# ============================================================

st.divider()

progress = (
    current_index / total_questions
    if total_questions
    else 0
)

st.progress(
    progress,
    text=f"Interview progress: {current_index}/{total_questions}"
)