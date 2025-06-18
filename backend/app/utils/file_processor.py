import os
import docx2txt
import fitz
import textract
from fastapi import HTTPException

def extract_text_from_file(file_path: str) -> str:
    try:
        if file_path.endswith(".docx"):
            return docx2txt.process(file_path).strip()
        elif file_path.endswith(".pdf"):
            with fitz.open(file_path) as doc:
                return "".join([page.get_text() for page in doc]).strip()
        elif file_path.endswith(".doc"):
            return textract.process(file_path).decode("utf-8").strip()
        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        return ""
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Text extraction failed: {str(e)}") 