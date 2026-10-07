"""CLI Demonstration & Verification Runner for Hybrid Email Classifier."""

import json
from classifier import classify_email
from email_service import EmailService


def run_demo() -> None:
    print("=" * 80)
    print("HYBRID EMAIL CLASSIFIER - VERIFICATION & DEMONSTRATION")
    print("=" * 80)

    # Sample emails demonstrating distinct real-world categories
    sample_emails = [
        {
            "id": "1",
            "title": "Case 1: Urgent Work Email (Rule Override to HIGH)",
            "email": {
                "sender": "sarah.lead@company.com",
                "subject": "CRITICAL: Production database down, action required asap!",
                "body": "The checkout service is throwing 500 errors. We need immediate attention on this emergency.",
            },
        },
        {
            "id": "2",
            "title": "Case 2: Standard Work Email (ML Predicts WORK + MEDIUM/LOW)",
            "email": {
                "sender": "product@company.com",
                "subject": "Weekly sprint sync agenda and roadmap review",
                "body": "Hi team, please find attached the meeting notes and project status report for this sprint.",
            },
        },
        {
            "id": "3",
            "title": "Case 3: Personal Email (ML Predicts PERSONAL)",
            "email": {
                "sender": "david.friend@gmail.com",
                "subject": "Dinner reservations and concert tickets for this weekend",
                "body": "Hey, I booked the table for 7 PM. Let me know if you want to grab coffee before the concert!",
            },
        },
        {
            "id": "4",
            "title": "Case 4: Ambiguous Email (Low Confidence -> Needs Human Review)",
            "email": {
                "sender": "unknown@domain.xyz",
                "subject": "Notice regarding reference 98124",
                "body": "Kindly refer to document attached regarding prior correspondence.",
            },
        },
    ]

    for item in sample_emails:
        print(f"\n--- {item['title']} ---")
        email_data = item["email"]
        print(f"Subject: {email_data['subject']}")
        print(f"Body:    {email_data['body']}")

        # Direct classifier call
        result = classify_email(email_data)
        print("Classification Result:")
        print(json.dumps(result, indent=4))

    print("\n" + "=" * 80)
    print("TESTING EMAIL SERVICE END-TO-END WORKFLOW")
    print("=" * 80)
    service = EmailService()

    for item in sample_emails:
        email_data = item["email"]
        service.receive_email(
            sender=email_data["sender"],
            subject=email_data["subject"],
            body=email_data["body"],
        )

    print("\n[Service Summary] Emails processed and stored in datastore:")
    all_emails = service.list_emails()
    for e in all_emails:
        c = e["classification"]
        review_flag = "[!] NEEDS HUMAN REVIEW" if c["needs_human_review"] else "[OK]"
        print(
            f"- ID: {e['id']} | Mode: {c['mode']:<8} ({c['mode_confidence']:.2f}) | "
            f"Priority: {c['priority']:<6} ({c['priority_confidence']:.2f}) | {review_flag}"
        )


if __name__ == "__main__":
    run_demo()
