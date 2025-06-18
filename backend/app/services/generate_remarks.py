from typing import List, Dict

# Identify missing skills and generate remarks
def analyze_gap(main: dict, other: dict) -> dict:
    missing_skills = list(set(main.get("skills", [])) - set(other.get("skills", [])))
    remarks = []

    if missing_skills:
        # If any skills are missing
        remarks.append(f"Lacks skills: {', '.join(missing_skills)}")
    else:
        # If all required skills are present
        remarks.append("All required skills are covered.")

    if main.get("experience") != other.get("experience"):
        # Highlight experience mismatch
        remarks.append(f"Experience mismatch: Expected {main['experience']} but found {other['experience']}.")

    return {
        "missing_skills": missing_skills,
        "remarks": remarks
    }