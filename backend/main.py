from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as app_router
import os
from app.utils.config import UPLOAD_DIR

app = FastAPI(title="Recruitment AI - Complete JD Management with Email Generation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Register all routes
app.include_router(app_router)

@app.get("/health")
async def health_check():
    return {"message": "Recruitment AI API with Email Generation is running"}

# Run the app directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
