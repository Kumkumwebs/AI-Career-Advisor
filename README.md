# AI Career Advisor & Skill-Gap Analyzer

A compact **AIML project** you can run and showcase on your CV/portfolio. It:
- Classifies a user's resume/profile text into likely roles (e.g., *Data Analyst*, *ML Engineer*).
- Estimates expected salary (rough LPA-style proxy using a regression on text features).
- Highlights **skill gaps** vs role requirements and suggests a learning roadmap.
- Exposes a simple **REST API** (FastAPI) for integration with Django/DRF or any frontend.

## 1) Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

## 2) Train models (quick demo on provided toy dataset)

```bash
python src/train_classifier.py
```

Outputs saved to `models/`:
- `tfidf.joblib` – text vectorizer
- `label_encoder.joblib` – role label encoder
- `role_clf.joblib` – LinearSVC role classifier
- `salary_reg.joblib` – Ridge regressor for salary

## 3) Run API server

```bash
uvicorn app.main:app --reload
```

Test with:

```bash
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d @- <<'JSON'
{
  "resume_text": "Python, Django, REST APIs, PostgreSQL, Docker, Git. Built HRMS project and analytics dashboards."
}
JSON
```

## 4) Project structure

```
ai_career_advisor/
  app/
    main.py              # FastAPI endpoints
  data/
    sample_jobs.csv
    skills_taxonomy.json
  models/                # saved models (created after training)
  src/
    train_classifier.py  # training script
    infer.py             # inference helpers
    utils.py             # skills extraction and helpers
  tests/
    test_infer.py
  README.md
  requirements.txt
```

## 5) Replace toy data with real data

- Export job roles with required skills from your sources (O*NET/LinkedIn/JD dumps).
- Keep columns: `role, skills (comma-separated), desc, salary_min, salary_max`.
- Retrain using `src/train_classifier.py`.


## 6) Optional Enhancements (for future work)
- Swap TF-IDF with transformer embeddings (e.g., Sentence-BERT) and cosine role matching.
- Add salary band calibration by city/experience using quantile regression.
- Plug into a Django/DRF backend as `/api/career/predict/` endpoint.
- Track predictions and feedback in PostgreSQL; add retraining pipeline.
