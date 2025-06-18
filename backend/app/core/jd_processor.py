import os
import json
from typing import Dict, Any
import google.generativeai as genai
from difflib import SequenceMatcher

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini = genai.GenerativeModel("gemini-1.5-flash")

def generate_jd_with_gemini(prompt: str) -> str:
    try:
        response = gemini.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise Exception(f"JD generation failed: {str(e)}")

def parse_jd_with_gemini(text: str) -> Dict[str, Any]:
    prompt = f"""
    Analyze this job description and return JSON:

    {{
        "experience": "X+ years",
        "education": "highest degree required",
        "skills": [list of skills like languages, frameworks, cloud, databases]
    }}

    Job Description:
    {text}
    """
    try:
        response = gemini.generate_content(prompt)
        json_str = response.text.strip()

        if json_str.startswith("```json"):
            json_str = json_str[7:]
        elif json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]

        parsed = json.loads(json_str)
        parsed["skills"] = list(set(parsed.get("skills", [])))
        parsed["experience"] = parsed.get("experience", "")
        parsed["education"] = parsed.get("education", "")
        return parsed

    except Exception as e:
        raise Exception(f"JD parsing failed: {str(e)}")

def calculate_match_score(main: dict, other: dict) -> float:
    def list_overlap_score(list1, list2):
        if not list1 or not list2:
            return 0.0
        overlap = len(set(list1) & set(list2))
        return (overlap / len(set(list1))) * 100

    def text_similarity(a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100 if a and b else 0.0

    skill_score = list_overlap_score(main.get("skills", []), other.get("skills", []))
    exp_score = text_similarity(main.get("experience", ""), other.get("experience", ""))
    edu_score = text_similarity(main.get("education", ""), other.get("education", ""))

    total_score = 0.7 * skill_score + 0.2 * exp_score + 0.1 * edu_score
    return round(total_score, 2)

def analyze_gap(main: dict, other: dict) -> dict:
    missing_skills = list(set(main.get("skills", [])) - set(other.get("skills", [])))
    remarks = []

    if missing_skills:
        remarks.append(f"Lacks skills: {', '.join(missing_skills)}")
    else:
        remarks.append("All required skills are covered.")

    if main.get("experience") != other.get("experience"):
        remarks.append(f"Experience mismatch: Expected {main['experience']} but found {other['experience']}.")

    return {
        "missing_skills": missing_skills,
        "remarks": remarks
    } 