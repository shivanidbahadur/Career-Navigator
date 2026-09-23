from interview.evaluate import evaluate_answer

question = "What is the difference between supervised and unsupervised learning?"

answer = """
Supervised learning uses labelled data to train a model.
For example, classification can predict whether an email is spam.
Unsupervised learning works with unlabelled data and can find patterns
or clusters in the data.
"""

result = evaluate_answer(question, answer)

print("\nInterview Evaluation")
print("--------------------")
print("Strength:", result["strength"])
print("Improve:", result["improve"])
print("Recommendation:", result["recommendation"])
print("Next Practice:", result["next_practice"])
print("Score:", result["score"])