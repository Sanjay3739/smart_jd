from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import os, tempfile

from app.services.prompts import *
from app.models.schemas import EmailGenerationRequest
from app.utils.config import UPLOAD_DIR
from app.services.file_processing import extract_text_from_file
from app.services.calculate_match_score import calculate_match_score
from app.services.generate_email import generate_interview_email, generate_rejection_email
from app.services.generate_jd import generate_jd_with_gemini
from app.services.generate_remarks import analyze_gap
from app.services.generate_jd import *

router = APIRouter()

# Upload JD file
@router.post("/upload_jd_file")
async def upload_jd_file(file: UploadFile = File(...)):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        extracted_text = extract_text_from_file(filepath)
        if len(extracted_text.split()) < 20:
            return JSONResponse(status_code=400, content={"error": "File doesn't contain a valid JD."})
        
        prompt = upload_jd_file_prompt(extracted_text)
        cleaned_jd = generate_jd_with_gemini(prompt)
        return {"filename": file.filename, "text": cleaned_jd}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)

# Manual JD input
@router.post("/manual_jd")
async def manual_jd_input(jd_text: str = Form(...)):
    if len(jd_text.strip().split()) < 20:
        return JSONResponse(status_code=400, content={"error": "JD too short or incomplete."})

    prompt = get_manule_jd_prompt(jd_text)
    cleaned_jd = generate_jd_with_gemini(prompt)
    return {"text": cleaned_jd}

# Generate JD from input fields
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

    prompt = get_jd_generation_prompt(job_title, experience, skills, company, employment_type, industry, location)
    generated_jd = generate_jd_with_gemini(prompt)
    return {"text": generated_jd}

# Compare JD and resume files
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

# Generate emails based on comparison
@router.post("/generate-emails/")
async def generate_emails(jd_text: str = Form(...), files: List[UploadFile] = File(...)):
    try:
        main_parsed = parse_jd_with_gemini(jd_text)
        job_title = main_parsed.get("job_title", "")
        company_name = main_parsed.get("company_name", "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JD parsing failed: {str(e)}")

    results = []
    valid_candidates = []

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

            candidate_name = os.path.splitext(file.filename)[0].replace("_", " ").replace("-", " ").title()

            candidate_data = {
                "filename": file.filename,
                "candidate_name": candidate_name,
                "parsed": parsed,
                "score": score,
                "missing_skills": gap["missing_skills"],
                "candidate_skills": parsed.get("skills", [])
            }

            valid_candidates.append(candidate_data)

        except Exception as e:
            results.append({"filename": file.filename, "error": str(e), "email": None})
        finally:
            os.unlink(tmp_path)

    if valid_candidates:
        best_candidate = max(valid_candidates, key=lambda x: x["score"])
        best_score = best_candidate["score"]

        for candidate in valid_candidates:
            try:
                is_best_match = candidate["score"] == best_score

                email_request = EmailGenerationRequest(
                    jd_text=jd_text,
                    candidate_name=candidate["candidate_name"],
                    filename=candidate["filename"],
                    match_score=candidate["score"],
                    missing_skills=candidate["missing_skills"],
                    candidate_skills=candidate["candidate_skills"],
                    job_title=job_title,
                    company_name=company_name,
                    is_best_match=is_best_match
                )

                if is_best_match:
                    email_content = generate_interview_email(email_request)
                    email_type = "interview"
                else:
                    email_content = generate_rejection_email(email_request)
                    email_type = "rejection"

                results.append({
                    "filename": candidate["filename"],
                    "candidate_name": candidate["candidate_name"],
                    "score": candidate["score"],
                    "email_type": email_type,
                    "email_content": email_content,
                    "is_best_match": is_best_match,
                    "missing_skills": candidate["missing_skills"]
                })

            except Exception as e:
                results.append({
                    "filename": candidate["filename"],
                    "candidate_name": candidate["candidate_name"],
                    "error": f"Email generation failed: {str(e)}",
                    "email_content": None
                })

    return JSONResponse(content={
        "main_parsed": main_parsed,
        "total_candidates": len(files),
        "processed_candidates": len(valid_candidates),
        "best_match_score": best_candidate["score"] if valid_candidates else 0,
        "results": results
    })
