import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini = genai.GenerativeModel(os.getenv("GEMINI_MODEL"))

# Create directory for uploaded JDs
UPLOAD_DIR = "uploaded_jds"