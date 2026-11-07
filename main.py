from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from app.analyzer import analyze_profile
from app.config import settings

app = FastAPI(title="GitHub Repository Complexity Analyzer",
              description="Evidence-based LLM assessment of public GitHub repositories.")

class AnalyzeRequest(BaseModel):
    github_url: HttpUrl

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    try:
        return analyze_profile(str(request.github_url), settings)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
