import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, r2_score, mean_absolute_error
import joblib
import os

DATA_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "sample_jobs.csv")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

def load_data(path: str):
    df = pd.read_csv(path)
    # combine desc + skills for text
    df["text"] = df["desc"].fillna("") + "\n" + df["skills"].fillna("")
    # salary target: mean of band
    df["salary_mean"] = (df["salary_min"] + df["salary_max"]) / 2.0
    return df

def main():
    os.makedirs(MODELS_DIR, exist_ok=True)
    df = load_data(DATA_CSV)

    X = df["text"].values
    y = df["role"].values
    y_salary = df["salary_mean"].values

    # Encode labels
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    # Vectorizer shared
    tfidf = TfidfVectorizer(ngram_range=(1,2), min_df=1, max_features=2500)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y_enc, test_size=0.25, random_state=42)
    _, X_test_salary, y_train_salary, y_test_salary = train_test_split(X, y_salary, test_size=0.25, random_state=42)

    # Role classifier
    clf = Pipeline([
        ("tfidf", tfidf),
        ("svm", LinearSVC())
    ])
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    # Salary regressor (separate vectorizer to keep artifacts explicit)
    tfidf_reg = TfidfVectorizer(ngram_range=(1,2), min_df=1, max_features=2500)
    X_feats = tfidf_reg.fit_transform(X)
    reg = Ridge(alpha=1.0)
    reg.fit(X_feats, y_salary)

    # Save artifacts
    joblib.dump(le, os.path.join(MODELS_DIR, "label_encoder.joblib"))
    # Pull out steps to save separately for easier loading in inference
    joblib.dump(clf.named_steps["tfidf"], os.path.join(MODELS_DIR, "tfidf.joblib"))
    joblib.dump(clf.named_steps["svm"], os.path.join(MODELS_DIR, "role_clf.joblib"))
    joblib.dump(tfidf_reg, os.path.join(MODELS_DIR, "tfidf_reg.joblib"))
    joblib.dump(reg, os.path.join(MODELS_DIR, "salary_reg.joblib"))

    print("=== Classification Report (labels encoded) ===")
    print(classification_report(y_test, y_pred, zero_division=0, digits=3))

    # Salary evaluation
    X_test_feats = tfidf_reg.transform(X_test_salary)
    y_salary_pred = reg.predict(X_test_feats)
    print("=== Salary R2:", round(r2_score(y_test_salary, y_salary_pred), 3))
    print("=== Salary MAE:", int(mean_absolute_error(y_test_salary, y_salary_pred)))

if __name__ == "__main__":
    main()
