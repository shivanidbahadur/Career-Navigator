"""
Run this from the project root: python learning/check_resources.py
Compares data/careers.json's required skills against data/resources.json.
Prints any skill that has no resources, so gaps show up before a demo,
not during one.
"""
import json


def main():
    with open("data/careers.json", encoding="utf-8") as f:
        careers = json.load(f)
    with open("data/resources.json", encoding="utf-8") as f:
        resources = json.load(f)

    needed_skills = set()
    for career in careers:
        for s in career["skills"]:
            needed_skills.add(s["skill"])

    have_resources = {r["skill"] for r in resources}

    missing = sorted(needed_skills - have_resources)
    covered = sorted(needed_skills & have_resources)

    print(f"{len(needed_skills)} skills needed across careers.json")
    print(f"{len(covered)} have resources")
    print(f"{len(missing)} MISSING resources:")
    for skill in missing:
        print(f"  - {skill}")


if __name__ == "__main__":
    main()