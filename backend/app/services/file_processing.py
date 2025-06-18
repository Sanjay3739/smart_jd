import docx2txt, fitz, textract
from fastapi import HTTPException
from app.utils.config import *

# Extract text from supported JD file formats
def extract_text_from_file(file_path: str) -> str:
    try:
        if file_path.endswith(".docx"):
            # Extract text from .docx
            return docx2txt.process(file_path).strip()
        elif file_path.endswith(".pdf"):
            # Extract text from PDF
            with fitz.open(file_path) as doc:
                return "".join([page.get_text() for page in doc]).strip()
        elif file_path.endswith(".doc"):
            # Extract text from legacy .doc
            return textract.process(file_path).decode("utf-8").strip()
        elif file_path.endswith(".txt"):
            # Read plain text
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        return ""
    except Exception as e:
        # Handle text extraction errors
        raise HTTPException(status_code=400, detail=f"Text extraction failed: {str(e)}")