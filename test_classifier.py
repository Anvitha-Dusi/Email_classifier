"""Unit and Integration Tests for Hybrid Email Classifier."""

import pytest
from classifier import (
    calculate_confidence,
    classify_mode,
    classify_priority,
    apply_priority_rules,
    classify_email,
    CONFIDENCE_THRESHOLD,
)
from email_service import EmailService


def test_calculate_confidence():
    """Validates calculate_confidence returns highest probability."""
    probs = [0.15, 0.75, 0.10]
    conf = calculate_confidence(probs)
    assert pytest.approx(conf, 0.001) == 0.75

    empty_conf = calculate_confidence([])
    assert empty_conf == 0.0


def test_classify_mode():
    """Validates mode classification between WORK and PERSONAL."""
    work_email = {
        "subject": "Sprint planning agenda",
        "body": "Hi team, let's sync on the roadmap and sprint deliverables.",
    }
    mode, conf = classify_mode(work_email)
    assert mode == "WORK"
    assert 0.0 <= conf <= 1.0

    personal_email = {
        "subject": "Dinner tonight",
        "body": "Hey are we still having dinner and watching the movie?",
    }
    mode, conf = classify_mode(personal_email)
    assert mode == "PERSONAL"
    assert 0.0 <= conf <= 1.0


def test_classify_priority_ml():
    """Validates priority classification output classes."""
    email = {
        "subject": "Team weekly update",
        "body": "General updates on our ongoing projects.",
    }
    priority, conf = classify_priority(email)
    assert priority in {"HIGH", "MEDIUM", "LOW"}
    assert 0.0 <= conf <= 1.0


def test_apply_priority_rules_high_override():
    """Validates that strong keywords override priority to HIGH."""
    email_urgent = {
        "subject": "Action Required: System alert",
        "body": "Please address this immediately asap before deadline.",
    }
    # Even if ML returned LOW, the rule should override to HIGH
    final_priority, rule_applied = apply_priority_rules(email_urgent, "LOW")
    assert final_priority == "HIGH"
    assert rule_applied is True


def test_apply_priority_rules_no_override():
    """Validates that when no rule keywords exist, prediction is preserved."""
    normal_email = {
        "subject": "Discussion notes",
        "body": "Attached are our notes from the afternoon discussion.",
    }
    final_priority, rule_applied = apply_priority_rules(normal_email, "MEDIUM")
    assert final_priority == "MEDIUM"
    assert rule_applied is False


def test_classify_email_output_format():
    """Validates the output contract of classify_email()."""
    email = {
        "subject": "Urgent: Client invoice deadline today",
        "body": "Action required immediately on client deliverables.",
    }
    result = classify_email(email)

    assert "mode" in result
    assert result["mode"] in {"WORK", "PERSONAL"}
    assert "mode_confidence" in result
    assert isinstance(result["mode_confidence"], float)

    assert "priority" in result
    assert result["priority"] in {"HIGH", "MEDIUM", "LOW"}
    assert "priority_confidence" in result
    assert isinstance(result["priority_confidence"], float)

    assert "needs_human_review" in result
    assert isinstance(result["needs_human_review"], bool)

    # Urgent keywords should produce HIGH priority
    assert result["priority"] == "HIGH"


def test_confidence_threshold_and_human_review():
    """Validates that confidences below 0.60 trigger needs_human_review = True."""
    # Obscure gibberish / out-of-vocabulary email to test low confidence behavior
    ambiguous_email = {
        "subject": "qwerty asdf zxcv",
        "body": "lorem ipsum dolor sit amet",
    }
    result = classify_email(ambiguous_email)

    # Verify logic consistency: if either confidence < 0.60, needs_human_review must be True
    if (
        result["mode_confidence"] < CONFIDENCE_THRESHOLD
        or result["priority_confidence"] < CONFIDENCE_THRESHOLD
    ):
        assert result["needs_human_review"] is True
    else:
        assert result["needs_human_review"] is False


def test_email_service_end_to_end_flow():
    """Validates full ingress, classification, storage, and retrieval flow."""
    service = EmailService()
    record = service.receive_email(
        sender="lead@company.com",
        subject="Critical: Production outage emergency",
        body="Immediate attention required! The server is down.",
    )

    assert record["id"].startswith("email_")
    assert record["classification"]["mode"] == "WORK"
    assert record["classification"]["priority"] == "HIGH"
    assert record["status"] in {"PROCESSED", "NEEDS_REVIEW"}

    # Verify query and filtering
    stored = service.get_email(record["id"])
    assert stored is not None
    assert stored["id"] == record["id"]

    high_priority_emails = service.list_emails(priority="HIGH")
    assert len(high_priority_emails) == 1
