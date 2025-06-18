from app.models.schemas import EmailGenerationRequest
from fastapi import HTTPException
from app.utils.config import *
from app.services.prompts import *


# Generate personalized interview call email using Gemini
def generate_interview_email(request: EmailGenerationRequest) -> str:
    job_title = request.job_title or "this position"
    company_name = request.company_name or "our company"
    candidate_name = request.candidate_name
    match_score = request.match_score
    candidate_skills = {', '.join(request.candidate_skills[:3])} 
    missing_skills = {', '.join(request.missing_skills) if request.missing_skills else 'None'}
    
    prompt = generate_interview_email_prompt(candidate_name, job_title, company_name, match_score, candidate_skills, missing_skills)

    try:
        response = gemini.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interview email generation failed: {str(e)}")

# Generate polite rejection email using Gemini
def generate_rejection_email(request: EmailGenerationRequest) -> str:
    job_title = request.job_title or "this position"
    company_name = request.company_name or "our company"
    candidate_name = request.candidate_name
    match_score = request.match_score
    candidate_skills = {', '.join(request.candidate_skills[:3])} 
    
    prompt = generate_rejection_email_prompt(candidate_name, job_title, company_name, match_score, candidate_skills)
    
    try:
        response = gemini.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rejection email generation failed: {str(e)}")
