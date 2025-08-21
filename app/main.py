from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import os
import json

from src.infer import Advisor

app = FastAPI(title="AI Career Advisor & Skill-Gap Analyzer", version="1.0.0")
advisor = Advisor()

# Simple static mapping: role -> core skills (for gap analysis)
ROLE_TO_SKILLS = {
    "Data Analyst": ["python","pandas","numpy","sql","power bi","statistics"],
    "Python Developer": ["python","git","linux","oop","data structures"],
    "ML Engineer": ["python","scikit-learn","tensorflow","docker","aws"],
    "Backend Developer (Django)": ["python","django","rest","postgresql","docker"],
    "Data Scientist": ["python","statistics","scikit-learn","matplotlib","pandas"],
    "BI Analyst": ["sql","power bi","tableau","statistics","python"],
    "MLOps Engineer": ["docker","kubernetes","aws","python"],
    "NLP Engineer": ["python","nlp","scikit-learn","pytorch","fastapi"],
    "Computer Vision Engineer": ["python","computer vision","pytorch","tensorflow"],
    "Full-Stack (Django)": ["django","javascript","html","css","rest"],
}

class PredictIn(BaseModel):
    resume_text: str
    target_role: Optional[str] = None

@app.post("/predict")
def predict(inp: PredictIn):
    role = advisor.predict_role(inp.resume_text)
    salary = advisor.predict_salary(inp.resume_text)  # INR per year
    gap = None
    target = inp.target_role or role
    if target in ROLE_TO_SKILLS:
        gap = advisor.skill_gap(inp.resume_text, ROLE_TO_SKILLS[target])
    return {
        "predicted_role": role,
        "estimated_salary_inr": int(round(salary)),
        "target_role": target,
        "skills": gap or {}
    }
