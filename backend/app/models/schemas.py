from pydantic import BaseModel
from typing import List, Optional

class EmailGenerationRequest(BaseModel):
    jd_text: str
    candidate_name: str
    filename: str
    match_score: float
    missing_skills: List[str]
    candidate_skills: List[str]
    job_title: Optional[str] = ""
    company_name: Optional[str] = ""
    is_best_match: bool = False
