import pandas as pd
import json
import re

# Load the uncertain emails list
input_file = "uncertain_emails.csv"
print(f"Loading uncertain emails from {input_file}...")
df = pd.read_csv(input_file)
print(f"Loaded {len(df)} emails to triage.")

# Fill NaN values in text columns with empty strings
df['subject'] = df['subject'].fillna('')
df['body'] = df['body'].fillna('')

resolved_list = []

# Compile regex patterns for semantic classification
pat_newsletter = re.compile(r'\b(newsletter|newsletter[s]?|digest|digests|weekly update|monthly update|daily update|announcement|announcements|subscribe|unsubscribe|mailing list)\b', re.IGNORECASE)
pat_promotion = re.compile(r'\b(promotion|promotions|offer|offers|discount|discounts|free|points|coupon|coupons|savings|deal|deals|special offer|save)\b', re.IGNORECASE)

pat_deadline = re.compile(r'\b(by eod|by end of day|immediately|due tomorrow|deadline|deadline[s]?|due date|asap|urgent|action required|call back immediately)\b', re.IGNORECASE)
pat_operational_risk = re.compile(r'\b(outage|outages|downtime|hacked|breach|security breach|server down|crash|overloaded|incident|failure|unstable|critical|compromised|unauthorized|frozen|account frozen|fraud|emergency|hospital|accident|admission|medical|surgery)\b', re.IGNORECASE)
pat_action = re.compile(r'\b(please review|please complete|feedback needed|approval|confirm|verify|action items|to-do|todo|task|tasks|request|requests|require|requires|required)\b', re.IGNORECASE)

pat_personal_high = re.compile(r'\b(emergency|hospital|accident|account frozen|fraud|urgent family matter)\b', re.IGNORECASE)
pat_personal_med = re.compile(r'\b(appointment|event invitation|invoice|payment due|follow-up|follow up)\b', re.IGNORECASE)

for idx, row in df.iterrows():
    email_id = row['email_id']
    mode = row['predicted_mode']
    subj = row['subject']
    body = row['body']
    text = (subj + " " + body).lower()
    rule_matched = str(row['rule_matched'])
    
    resolved_priority = 'medium' # Default fallback
    adjusted_confidence = 0.70
    rationale = ""
    
    # Check if this was a conflict email from the previous step
    is_conflict = rule_matched.startswith('conflict')
    
    # 1. Mode determination (we keep the previously predicted mode, but verify with details if needed)
    resolved_mode = mode
    
    # 2. Semantic Priority Triaging
    
    # Case A: Informational/Newsletter/Promotion
    if pat_newsletter.search(text) or pat_promotion.search(text):
        # Mixed signal check: does it contain direct action requirements or operational risk?
        if pat_deadline.search(text) or pat_operational_risk.search(text):
            # Newsletter with critical info (e.g. security breach announcement)
            resolved_priority = 'high'
            adjusted_confidence = 0.85
            rationale = "Identified as a digest containing critical security alerts or operational warnings. Set to HIGH priority for safety."
        elif pat_action.search(text):
            resolved_priority = 'medium'
            adjusted_confidence = 0.80
            rationale = "Informational update containing secondary action items or review requests. Priority set to MEDIUM."
        else:
            resolved_priority = 'low'
            adjusted_confidence = 0.88
            rationale = "Marketing, newsletter, or promotional digest with informational intent and no immediate action required."
            
    # Case B: High Operational Risk, Security Threat, or Personal Emergency
    elif pat_operational_risk.search(text):
        # Lean HIGH due to cost-sensitive weighting (FN is 5x worse)
        resolved_priority = 'high'
        adjusted_confidence = 0.90
        if is_conflict:
            rationale = f"Resolved conflict in favor of HIGH priority due to critical keywords ({rule_matched}) and operational safety principles."
        else:
            rationale = "Contains indicator of potential system outage, security breach, or personal emergency. Risk-escalated to HIGH."
            
    # Case C: Action required, deadlines, scheduling, or billing
    elif pat_action.search(text) or pat_deadline.search(text) or pat_personal_med.search(text):
        # Check if it has a hard deadline or urgent indicator
        if pat_deadline.search(text):
            resolved_priority = 'high'
            adjusted_confidence = 0.85
            rationale = "Contains immediate actionable request with implicit deadline or callback urgency. Priority set to HIGH."
        else:
            resolved_priority = 'medium'
            adjusted_confidence = 0.82
            if is_conflict:
                rationale = f"Resolved conflict: email represents structured operational review or standard request. Set to MEDIUM priority."
            else:
                rationale = "Direct business request, follow-up, invoice, or scheduling coordination. Categorized as MEDIUM priority."
                
    # Case D: Genuely Ambiguous (Default Fallback)
    else:
        resolved_priority = 'medium'
        adjusted_confidence = 0.70
        rationale = "Genuinely ambiguous content. Defaulted to MEDIUM priority to maintain operational visibility and prevent triage leakage."
        
    resolved_list.append({
        'email_id': email_id,
        'resolved_mode': resolved_mode,
        'resolved_priority': resolved_priority,
        'adjusted_confidence': round(adjusted_confidence, 2),
        'decision_rationale': rationale
    })

# Save to JSON
output_file = "resolved_emails.json"
with open(output_file, 'w') as f:
    json.dump(resolved_list, f, indent=2)

print(f"Successfully triaged and resolved {len(resolved_list)} uncertain emails.")
print(f"Saved results to {output_file}")

# Analyze distribution
resolved_df = pd.DataFrame(resolved_list)
print("\n--- Triaged Distribution ---")
print("Priority counts:")
print(resolved_df['resolved_priority'].value_counts())
print("\nAverage confidence score by resolved priority:")
print(resolved_df.groupby('resolved_priority')['adjusted_confidence'].mean())
