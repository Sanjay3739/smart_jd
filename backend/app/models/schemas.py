from pydantic import BaseModel
from typing import List, Dict, Any

class JDResponse(BaseModel):
    text: str

class JDComparisonResponse(BaseModel):
    main_parsed: Dict[str, Any]
    results: List[Dict[str, Any]] 