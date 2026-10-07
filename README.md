# Hybrid Email Classification System

A modular, lightweight **Hybrid Email Classification System** combining Machine Learning (**TF-IDF + Logistic Regression**) with a **Rule-Based Priority Layer** and a **Confidence Gatekeeper**.

---

## Architecture Overview

```text
Incoming Email (subject + body)
             ↓
    text = subject + " " + body
             ↓
    TF-IDF Vectorization
             ↓
Two Independent Classifiers:
    ├── Mode Classifier (Logistic Regression)     → WORK / PERSONAL
    └── Priority Classifier (Logistic Regression) → HIGH / MEDIUM / LOW
             ↓
    Rule-Based Layer (High-priority keyword overrides)
             ↓
    Confidence Check (< 0.60 threshold)
             ↓
    Final Classification Result
```

---

## File Structure

```text
d:/Email classifier/
├── classifier.py          # Core classification logic, rule-based layer, & plug-and-play model loader
├── email_service.py       # Application service illustrating ingestion, storage, & classifier invocation
├── main.py                # Demonstration script running real-world sample emails
├── test_classifier.py     # Automated unit & integration test suite (pytest)
├── requirements.txt       # Dependencies (scikit-learn, joblib, numpy, pytest)
└── models/                # Storage directory for trained models (.joblib / .pkl)
    ├── mode_model.joblib
    └── priority_model.joblib
```

---

## Plug-and-Play Model Architecture

- If pre-trained models exist in `models/mode_model.joblib` and `models/priority_model.joblib`, the system loads them automatically.
- If no models are present on disk, `classifier.py` automatically initializes and persists baseline pipelines so the entire application runs out-of-the-box without failure.
- When you train models later, simply save them to `models/` without changing any application code.
