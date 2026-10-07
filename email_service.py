"""Email Service Integration Layer.

This module demonstrates the 4 key stages of an email in the application lifecycle:
1. Ingress: Where emails enter the application (API / Webhook / Ingestion handler).
2. Processing & Classifier Call: Where `classify_email(email)` is invoked.
3. Storage: Where email data and its classification metadata are persisted.
4. Presentation: Where the classification results are queried and displayed.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional
from classifier import classify_email


class EmailService:
    """Service that handles email ingestion, classification, and storage."""

    def __init__(self) -> None:
        # In-memory email datastore (represents DB / inbox table in production)
        self._email_store: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------------
    # 1. ENTRY POINT: Where emails enter the application
    # ------------------------------------------------------------------------
    def receive_email(
        self,
        sender: str,
        subject: str,
        body: str,
        recipients: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Ingests an incoming email into the application and classifies it immediately.

        Args:
            sender: Sender's email address.
            subject: Subject line.
            body: Body text.
            recipients: Optional recipient list.

        Returns:
            Dict[str, Any]: Saved email record with classification results.
        """
        email_id = f"email_{uuid.uuid4().hex[:8]}"
        created_at = time.strftime("%Y-%m-%d %H:%M:%S")

        raw_email = {
            "id": email_id,
            "sender": sender,
            "recipients": recipients or [],
            "subject": subject,
            "body": body,
            "created_at": created_at,
        }

        # --------------------------------------------------------------------
        # 2. CLASSIFICATION CALL: Where the classifier is invoked
        # --------------------------------------------------------------------
        classification_result = classify_email(raw_email)

        # --------------------------------------------------------------------
        # 3. STORAGE: Where email data and classification results are saved
        # --------------------------------------------------------------------
        email_record = {
            **raw_email,
            "classification": classification_result,
            "status": "NEEDS_REVIEW" if classification_result["needs_human_review"] else "PROCESSED",
        }

        self._email_store[email_id] = email_record
        return email_record

    # ------------------------------------------------------------------------
    # 4. RETRIEVAL & DISPLAY: Where results are queried and displayed
    # ------------------------------------------------------------------------
    def get_email(self, email_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single email record with classification data."""
        return self._email_store.get(email_id)

    def list_emails(
        self,
        mode: Optional[str] = None,
        priority: Optional[str] = None,
        needs_review: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Filters emails by classification attributes for dashboard or inbox view."""
        results = list(self._email_store.values())

        if mode is not None:
            results = [e for e in results if e["classification"]["mode"] == mode]
        if priority is not None:
            results = [e for e in results if e["classification"]["priority"] == priority]
        if needs_review is not None:
            results = [e for e in results if e["classification"]["needs_human_review"] == needs_review]

        return results
