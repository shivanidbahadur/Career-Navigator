from interview.questions import generate_questions


gaps = [
    {
        "skill": "Machine Learning",
        "priority": "High"
    },
    {
        "skill": "Statistics",
        "priority": "High"
    },
    {
        "skill": "Data Visualization",
        "priority": "Medium"
    }
]


profile = {
    "career": "Data Scientist",
    "level": "beginner",
    "skills": ["Python", "SQL"]
}


questions = generate_questions(
    gaps=gaps,
    career_id="data_scientist",
    profile=profile
)


for i, question in enumerate(questions, 1):
    print(f"\nQuestion {i}")
    print("Question:", question["question"])
    print("Why:", question["why"])
    print("Skill:", question["skill"])
    print("Difficulty:", question["difficulty"])