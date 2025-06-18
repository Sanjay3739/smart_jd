# prompts.py

def get_jd_generation_prompt(job_title, experience, skills, company, employment_type, industry, location):
    return f"""
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

def get_manule_jd_prompt(jd_text):
    return f"""Please professionally format and rewrite the following job description:\n\n{jd_text}
    ### STRICT RULES:
        1. **ONLY keep sections explicitly mentioned in the input text.**  
        - If a section (e.g., \"Compensation & Benefits\") is **not** in the input, **omit it entirely**.  
        - **DO NOT** add placeholder text like \"Not specified\" or \"Information not provided.\"  

        2. **Preserve the original meaning** while improving clarity and conciseness.  
        3. **Standardize formatting** (use bullet points, headings, and consistent spacing).
    """

def upload_jd_file_prompt(extracted_text):
    return f"""Please rephrase and format this job description:\n\n{extracted_text}
        ### STRICT RULES:
            1. **ONLY keep sections explicitly mentioned in the input text.**  
            - If a section (e.g., \"Compensation & Benefits\") is **not** in the input, **omit it entirely**.  
            - **DO NOT** add placeholder text like \"Not specified\" or \"Information not provided.\"  

            2. **Preserve the original meaning** while improving clarity and conciseness.  
            3. **Standardize formatting** (use bullet points, headings, and consistent spacing).
        """

def generate_rejection_email_prompt(candidate_name, job_title, company_name, match_score, candidate_skills):
    return f"""
    Generate a polite, respectful rejection email for a candidate who wasn't selected.
    
    **Context:**
    - Candidate: {candidate_name}
    - Position: {job_title}
    - Company: {company_name}
    - Match Score: {match_score}/100
    - Candidate Skills: {candidate_skills}  # Mention some positive skills
    
    **Email Requirements:**
    1. Respectful and appreciative tone
    2. Thank them for their interest and time
    3. Briefly mention something positive about their profile
    4. Inform them we've moved forward with another candidate
    5. Encourage future applications
    6. Keep it brief but warm
    7. Don't mention specific reasons for rejection or match scores
    
    **Structure:**
    - Subject line (separate)
    - Greeting
    - Thank them for applying
    - Mention something positive
    - Inform about decision
    - Encourage future applications
    - Professional closing
    
    Format as:
    Subject: [subject line]
    
    [email body]
    """

def generate_interview_email_prompt(candidate_name, job_title, company_name, match_score, candidate_skills, missing_skills) :
    return f"""
    Generate a professional, personalized interview invitation email for the best-matched candidate.
    
    **Context:**
    - Candidate: {candidate_name}
    - Position: {job_title}
    - Company: {company_name}
    - Match Score: {match_score}/100
    - Strong Skills: {candidate_skills}
    - Missing Skills: {missing_skills}
    
    **Email Requirements:**
    1. Professional and personalized tone
    2. Mention specific skills that impressed us
    3. Express genuine interest in their candidacy
    4. Include clear next steps for interview scheduling
    5. Keep it concise but warm
    6. Don't mention the exact match score number
    
    **Structure:**
    - Subject line (separate)
    - Greeting
    - Why we're impressed (specific skills/experience)
    - Interview invitation
    - Next steps
    - Professional closing
    
    Format as:
    Subject: [subject line]
    
    [email body]
    """

def parse_jd_with_gemini_prompt(text: str) -> str:
    return f"""
    Analyze this job description and return JSON with ONLY explicitly mentioned keywords:

    {{
        "experience": "X+ years",
        "education": "highest degree required",
        "skills": [list of skills like languages, frameworks, cloud, databases],
        "job_title": "extracted job title",
        "company_name": "company name if mentioned"
    }}

    Job Description:
    {text}

    ### STRICT RULES:
    1. Extract ONLY exact words/phrases that appear in the text
    2. NEVER add:
    - Explanations
    - Placeholder text (e.g., "Nice to have", "Preferred")
    - Implied requirements
    - Any text not verbatim from the job description
    3. If a field has no explicit mention in the text, omit it entirely
    4. For skills:
    - Only include specific technologies/tools (e.g., "Python", "AWS")
    - Exclude generic terms (e.g., "teamwork", "communication")
    5. For experience:
    - Only include exact phrases like "5+ years"
    - Don't interpret ranges
    """
