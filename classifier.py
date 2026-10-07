"""Hybrid Email Classifier Module.

Architecture:
    Incoming Email -> Subject + Body -> TF-IDF Vectorization -> Logistic Regression
    ├── Mode Classifier (WORK / PERSONAL)
    └── Priority Classifier (HIGH / MEDIUM / LOW)
    Rule-Based Layer (Keyword overrides) -> Confidence Check -> Final Classification
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple, Union
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Confidence threshold required to avoid human review
CONFIDENCE_THRESHOLD: float = 0.60

# Strong high-priority keyword signals
HIGH_PRIORITY_KEYWORDS = [
    "urgent",
    "asap",
    "immediately",
    "critical",
    "emergency",
    "deadline",
    "action required",
    "important",
    "today",
    "immediate attention",
]

# Optional low-priority keyword signals
LOW_PRIORITY_KEYWORDS = [
    "newsletter",
    "unsubscribe",
    "fyi only",
    "no reply required",
    "promotional offer",
]


# ============================================================================
# 1. MODEL LOADING & FALLBACK INITIALIZATION
# ============================================================================

def _build_default_models() -> Tuple[Pipeline, Pipeline]:
    """Builds and fits baseline TF-IDF + LogisticRegression pipelines.

    Used when pre-trained models are not yet available on disk so the system
    works immediately out-of-the-box. Real trained models can simply be placed
    in the models/ directory to replace these without touching any application code.
    """
    # Baseline anchor dataset for Mode (WORK vs PERSONAL)
    mode_texts = [
        "project status report meeting sync budget quarterly agenda client deliverable contract",
        "invoice attached client deliverables sprint review quarterly roadmap architecture api",
        "pull request review deployment production api client contract standup jira ticket",
        "weekly team standup sync jira ticket stakeholder deadline architecture update sprint",
        "critical production database down system server checkout service bug error outage fix",
        "hey are we still having dinner tonight family photos movie plans weekend vacation",
        "weekend trip tickets concert party invitation recipes birthday family dinner",
        "mom called about sunday brunch catching up vacation pictures holiday dinner party",
        "happy birthday dinner reservation friend meetup soccer practice family movie night",
        "casual weekend meetup plans hangout lunch movies family barbecue recipes",
    ]
    mode_labels = [
        "WORK", "WORK", "WORK", "WORK", "WORK",
        "PERSONAL", "PERSONAL", "PERSONAL", "PERSONAL", "PERSONAL",
    ]

    mode_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
        ("clf", LogisticRegression(C=10.0, random_state=42)),
    ])
    mode_pipeline.fit(mode_texts, mode_labels)

    # Baseline anchor dataset for Priority (HIGH vs MEDIUM vs LOW)
    priority_texts = [
        "critical production outage emergency system down immediately server crash",
        "server crash urgent security breach immediate attention required today critical",
        "urgent deadline client escalation action required asap today emergency",
        "weekly team check-in scheduled for thursday please review notes updates",
        "project feedback update documentation review comments for next sprint roadmap",
        "quarterly sync agenda ideas discussion notes for team meeting status",
        "monthly company newsletter casual reading fyi only webinar replay optional",
        "lunch menu cafeteria discount casual blog post no action required optional",
        "random thoughts weekend article links unsubscribe if not interested reading",
    ]
    priority_labels = [
        "HIGH", "HIGH", "HIGH",
        "MEDIUM", "MEDIUM", "MEDIUM",
        "LOW", "LOW", "LOW",
    ]

    priority_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
        ("clf", LogisticRegression(C=10.0, random_state=42)),
    ])
    priority_pipeline.fit(priority_texts, priority_labels)

    return mode_pipeline, priority_pipeline


class ModelRegistry:
    """Manages loading and access to mode and priority classification models."""

    def __init__(
        self,
        mode_model_path: str = "models/mode_model.joblib",
        priority_model_path: str = "models/priority_model.joblib",
    ) -> None:
        self.mode_model_path = mode_model_path
        self.priority_model_path = priority_model_path
        self.mode_model: Optional[Pipeline] = None
        self.priority_model: Optional[Pipeline] = None
        self.load_models()

    def load_models(self) -> None:
        """Loads trained models from disk if present, otherwise uses baseline models."""
        has_mode = os.path.isfile(self.mode_model_path)
        has_priority = os.path.isfile(self.priority_model_path)

        if has_mode and has_priority:
            self.mode_model = joblib.load(self.mode_model_path)
            self.priority_model = joblib.load(self.priority_model_path)
        else:
            default_mode, default_priority = _build_default_models()
            self.mode_model = default_mode
            self.priority_model = default_priority

            # Save the initialized baseline models to disk if models/ dir exists or can be created
            os.makedirs(os.path.dirname(self.mode_model_path) or ".", exist_ok=True)
            if not has_mode:
                try:
                    joblib.dump(default_mode, self.mode_model_path)
                except Exception:
                    pass
            if not has_priority:
                try:
                    joblib.dump(default_priority, self.priority_model_path)
                except Exception:
                    pass


# Global singleton instance for easy import across the application
_REGISTRY = ModelRegistry()


def get_models() -> Tuple[Pipeline, Pipeline]:
    """Returns the current (mode_model, priority_model)."""
    if _REGISTRY.mode_model is None or _REGISTRY.priority_model is None:
        _REGISTRY.load_models()
    return _REGISTRY.mode_model, _REGISTRY.priority_model


# ============================================================================
# 2. HELPER FUNCTIONS
# ============================================================================

def _extract_text(email: Union[Dict[str, Any], Any]) -> str:
    """Extracts and concatenates subject and body from dict or object."""
    if isinstance(email, dict):
        subject = str(email.get("subject", "") or "")
        body = str(email.get("body", "") or "")
    else:
        subject = str(getattr(email, "subject", "") or "")
        body = str(getattr(email, "body", "") or "")

    # Required representation: text = subject + " " + body
    return f"{subject} {body}".strip()


# ============================================================================
# 3. CORE CLASSIFIER FUNCTIONS
# ============================================================================

def calculate_confidence(probabilities: Union[np.ndarray, list]) -> float:
    """Calculates confidence as the maximum predicted class probability.

    Args:
        probabilities: Array or list of probabilities from model.predict_proba().

    Returns:
        float: Highest probability value.
    """
    probs_array = np.asarray(probabilities).flatten()
    if probs_array.size == 0:
        return 0.0
    return float(np.max(probs_array))


def classify_mode(email: Union[Dict[str, Any], Any]) -> Tuple[str, float]:
    """Classifies email mode into WORK or PERSONAL using TF-IDF + Logistic Regression.

    Args:
        email: Email dict or object containing subject and body.

    Returns:
        Tuple[str, float]: (predicted_mode, confidence)
    """
    text = _extract_text(email)
    mode_model, _ = get_models()

    probabilities = mode_model.predict_proba([text])[0]
    best_idx = int(np.argmax(probabilities))
    predicted_mode = str(mode_model.classes_[best_idx])
    confidence = calculate_confidence(probabilities)

    return predicted_mode, confidence


def classify_priority(email: Union[Dict[str, Any], Any]) -> Tuple[str, float]:
    """Classifies email priority into HIGH, MEDIUM, or LOW using TF-IDF + Logistic Regression.

    Args:
        email: Email dict or object containing subject and body.

    Returns:
        Tuple[str, float]: (predicted_priority, confidence)
    """
    text = _extract_text(email)
    _, priority_model = get_models()

    probabilities = priority_model.predict_proba([text])[0]
    best_idx = int(np.argmax(probabilities))
    predicted_priority = str(priority_model.classes_[best_idx])
    confidence = calculate_confidence(probabilities)

    return predicted_priority, confidence


def apply_priority_rules(
    email: Union[Dict[str, Any], Any],
    prediction: str,
) -> Tuple[str, bool]:
    """Applies rule-based keyword overrides to the ML priority prediction.

    If strong high-priority keywords are present, priority is overridden to HIGH.
    If strong low-priority keywords are present and priority was not high, it is adjusted to LOW.

    Args:
        email: Email dict or object.
        prediction: ML predicted priority ('HIGH', 'MEDIUM', 'LOW').

    Returns:
        Tuple[str, bool]: (final_priority, rule_applied)
    """
    text_lower = _extract_text(email).lower()

    # Rule 1: High priority keywords override everything
    for kw in HIGH_PRIORITY_KEYWORDS:
        if kw in text_lower:
            return "HIGH", True

    # Rule 2: Low priority signals (only if ML didn't flag high)
    if prediction != "HIGH":
        for kw in LOW_PRIORITY_KEYWORDS:
            if kw in text_lower:
                return "LOW", True

    # No rule triggered, retain ML prediction
    return prediction, False


def classify_email(email: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
    """Main hybrid classification pipeline for an incoming email.

    Execution Flow:
        1. Extract text: subject + " " + body
        2. ML Mode classification (WORK / PERSONAL) + confidence
        3. ML Priority classification (HIGH / MEDIUM / LOW) + confidence
        4. Rule-based layer to override/adjust priority based on keyword signals
        5. Confidence check (< 0.60 sets needs_human_review = True)

    Args:
        email: Email dict or object with 'subject' and 'body'.

    Returns:
        dict:
            {
                "mode": "WORK" | "PERSONAL",
                "mode_confidence": float,
                "priority": "HIGH" | "MEDIUM" | "LOW",
                "priority_confidence": float,
                "needs_human_review": bool
            }
    """
    # Step 1 & 2: Mode classification
    mode, mode_confidence = classify_mode(email)

    # Step 3: ML Priority classification
    ml_priority, priority_confidence = classify_priority(email)

    # Step 4: Rule-based priority adjustment
    final_priority, rule_applied = apply_priority_rules(email, ml_priority)

    # If an explicit high-priority rule triggered, the rule confidence is 1.0 (authoritative)
    if rule_applied and final_priority == "HIGH":
        effective_priority_conf = max(priority_confidence, 0.95)
    else:
        effective_priority_conf = priority_confidence

    # Step 5: Confidence threshold check
    # If the highest classification confidence for either model is below 0.60, require human review
    needs_human_review = (
        mode_confidence < CONFIDENCE_THRESHOLD
        or effective_priority_conf < CONFIDENCE_THRESHOLD
    )

    return {
        "mode": mode,
        "mode_confidence": round(float(mode_confidence), 2),
        "priority": final_priority,
        "priority_confidence": round(float(effective_priority_conf), 2),
        "needs_human_review": needs_human_review,
    }
