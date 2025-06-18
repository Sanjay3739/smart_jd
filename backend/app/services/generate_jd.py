import json
from typing import Dict, Any
from fastapi import HTTPException
from app.utils.config import *
from app.services.prompts import *

# Generate JD using Gemini with input prompt
def generate_jd_with_gemini(prompt: str) -> str:
    try:
        # Generate and return cleaned JD content
        response = gemini.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # Handle Gemini API errors
        raise HTTPException(status_code=500, detail=f"JD generation failed: {str(e)}")

# Parse JD text to extract structured data like skills, education, experience
def parse_jd_with_gemini(text: str) -> Dict[str, Any]:
    prompt = parse_jd_with_gemini_prompt(text)

    try:
        # Call Gemini model to parse JD
        response = gemini.generate_content(prompt)
        json_str = response.text.strip()

        # Strip markdown fences if present
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        elif json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]

        # Convert to dict and clean
        parsed = json.loads(json_str)
        parsed["skills"] = list(set(parsed.get("skills", [])))
        parsed["experience"] = parsed.get("experience", "")
        parsed["education"] = parsed.get("education", "")
        parsed["job_title"] = parsed.get("job_title", "")
        parsed["company_name"] = parsed.get("company_name", "")
        return parsed

    except Exception as e:
        # Handle parsing errors
        raise HTTPException(status_code=500, detail=f"JD parsing failed: {str(e)}")
