from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import os
import tempfile

from ..core.jd_processor import generate_jd_with_gemini, parse_jd_with_gemini, calculate_match_score, analyze_gap
from ..utils.file_processor import extract_text_from_file

router = APIRouter()

# Create directory for uploaded JDs
UPLOAD_DIR = "uploaded_jds"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload_jd_file")
async def upload_jd_file(file: UploadFile = File(...)):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        extracted_text = extract_text_from_file(filepath)
        if len(extracted_text.split()) < 20:
            return JSONResponse(status_code=400, content={"error": "Uploaded file doesn't seem to contain a valid job description."})

        prompt = f"""Please rephrase and format this job description:\n\n{extracted_text}
        ### STRICT RULES:
            1. **ONLY keep sections explicitly mentioned in the input text.**  
            - If a section (e.g., \"Compensation & Benefits\") is **not** in the input, **omit it entirely**.  
            - **DO NOT** add placeholder text like \"Not specified\" or \"Information not provided.\"  

            2. **Preserve the original meaning** while improving clarity and conciseness.  
            3. **Standardize formatting** (use bullet points, headings, and consistent spacing).
        """

        cleaned_jd = generate_jd_with_gemini(prompt)
        return {"filename": file.filename, "text": cleaned_jd}

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)

@router.post("/manual_jd")
async def manual_jd_input(jd_text: str = Form(...)):
    if len(jd_text.strip().split()) < 20:
        return JSONResponse(status_code=400, content={"error": "JD too short or incomplete. Please provide a more detailed description."})

    prompt = f"""Please professionally format and rewrite the following job description:\n\n{jd_text}
    ### STRICT RULES:
        1. **ONLY keep sections explicitly mentioned in the input text.**  
        - If a section (e.g., \"Compensation & Benefits\") is **not** in the input, **omit it entirely**.  
        - **DO NOT** add placeholder text like \"Not specified\" or \"Information not provided.\"  

        2. **Preserve the original meaning** while improving clarity and conciseness.  
        3. **Standardize formatting** (use bullet points, headings, and consistent spacing).
    """

    cleaned_jd = generate_jd_with_gemini(prompt)
    return {"text": cleaned_jd}

@router.post("/generate_jd")
async def generate_jd(
    job_title: str = Form(...),
    experience: str = Form(...),
    skills: str = Form(...),
    company: str = Form(...),
    employment_type: str = Form(...),
    industry: str = Form(...),
    location: str = Form(...)
):
    if not job_title.strip() or not skills.strip():
        return JSONResponse(status_code=400, content={"error": "Job Title and Skills are mandatory."})

    prompt = f"""
    Write a professional job description using the following details:

    - Job Title: {job_title}
    - Experience: {experience} years
    - Must-have Skills: {skills}
    - Company: {company}
    - Employment Type: {employment_type}
    - Industry: {industry}
    - Location: {location}

    ### STRICT INSTRUCTIONS:
    1. DO NOT include any \"To Apply\" section.
    2. DO NOT include any \"About the Company\" or company introduction paragraph.
    3. Focus only on role-specific responsibilities, qualifications, skills, and compensation (if applicable).
    4. Keep the tone professional and concise.
    """

    generated_jd = generate_jd_with_gemini(prompt)
    return {"text": generated_jd}

@router.post("/compare-jd-and-files/")
async def compare_jd_and_files(jd_text: str = Form(...), files: List[UploadFile] = File(...)):
    try:
        main_parsed = parse_jd_with_gemini(jd_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Main JD parsing failed: {str(e)}")

    results = []
    for file in files:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            text = extract_text_from_file(tmp_path)
            if not text:
                raise ValueError("Empty content")

            parsed = parse_jd_with_gemini(text)
            score = calculate_match_score(main_parsed, parsed)
            gap = analyze_gap(main_parsed, parsed)

            results.append({
                "filename": file.filename,
                "parsed": parsed,
                "score": score,
                "missing_skills": gap["missing_skills"],
                "remarks": gap["remarks"]
            })
        except Exception as e:
            results.append({"filename": file.filename, "error": str(e)})
        finally:
            os.unlink(tmp_path)

    return JSONResponse(content={"main_parsed": main_parsed, "results": results})

@router.get("/health")
async def health_check():
    return {"message": "Recruitment AI API is running"} 