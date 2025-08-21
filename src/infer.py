import os, joblib
from typing import Dict, List
from .utils import load_skills, extract_skills

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")

TFIDF_PATH = os.path.join(MODELS_DIR, "tfidf.joblib")
ROLE_CLF_PATH = os.path.join(MODELS_DIR, "role_clf.joblib")
LE_PATH = os.path.join(MODELS_DIR, "label_encoder.joblib")
TFIDF_REG_PATH = os.path.join(MODELS_DIR, "tfidf_reg.joblib")
SALARY_REG_PATH = os.path.join(MODELS_DIR, "salary_reg.joblib")
SKILLS_PATH = os.path.join(DATA_DIR, "skills_taxonomy.json" )

class Advisor:
    def __init__(self):
        self.tfidf = joblib.load(TFIDF_PATH)
        self.role_clf = joblib.load(ROLE_CLF_PATH)
        self.le = joblib.load(LE_PATH)
        self.tfidf_reg = joblib.load(TFIDF_REG_PATH)
        self.salary_reg = joblib.load(SALARY_REG_PATH)
        self.taxonomy = load_skills(SKILLS_PATH)

    def predict_role(self, resume_text: str) -> str:
        X = self.tfidf.transform([resume_text])
        y = self.role_clf.predict(X)[0]
        return self.le.inverse_transform([y])[0]

    def predict_salary(self, resume_text: str) -> float:
        X = self.tfidf_reg.transform([resume_text])
        s = float(self.salary_reg.predict(X)[0])
        return max(0.0, s)

    def skills_from_text(self, resume_text: str) -> List[str]:
        return extract_skills(resume_text, self.taxonomy)

    def skill_gap(self, resume_text: str, target_role_skills: List[str]) -> Dict[str, List[str]]:
        have = set(self.skills_from_text(resume_text))
        need = set([s.strip().lower() for s in target_role_skills])
        missing = [s for s in need if s not in have]
        extra = [s for s in have if s not in need]
        return {"have": sorted(list(have)), "missing": sorted(missing), "extra": sorted(extra)}
