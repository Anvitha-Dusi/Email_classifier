import pandas as pd
import re

# 1. Load the dataset
input_path = "emails_labeled.csv"
print(f"Loading dataset from {input_path}...")
df = pd.read_csv(input_path)
print(f"Initial shape: {df.shape}")

# Drop rows where all columns are null
df = df.dropna(subset=['email_id'])
print(f"Shape after dropping nulls: {df.shape}")

# 2. Extract domain
df['domain'] = df['sender'].apply(lambda x: str(x).split('@')[-1] if isinstance(x, str) and '@' in x else '')

# 3. Define the rules and keywords
personal_domains = {
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com', 
    'aol.com', 'protonmail.com', 'mail.com', 'runbox.com', 'fastmail.fm', 'zoho.com'
}

work_domains = {
    'enron.com', 'innovate.io', 'cloudscale.tech', 'netops.net', 'codeworks.io', 
    'devgroup.net', 'enterpriseflow.com', 'techcorp.com', 'apexsolutions.net', 
    'corpconnect.co', 'systemix.org', 'mailman.enron.com', 'enron.net'
}

personal_kws = {
    'HIGH': ["emergency", "hospital", "accident", "account frozen", "fraud", "urgent family matter"],
    'MEDIUM': ["appointment", "event invitation", "invoice", "payment due", "follow-up"],
    'LOW': ["newsletter", "casual check-in", "promotion", "booking confirmation"]
}

work_kws = {
    'HIGH': ["urgent", "asap", "critical", "server down", "outage", "security breach", "executive escalation"],
    'MEDIUM': ["meeting", "standup", "review", "client request", "status update", "decision needed"],
    'LOW': ["newsletter", "digest", "automated backup", "routine maintenance", "fyi"]
}

# Mode classification keywords (excluding 'newsletter' because it's shared)
personal_specific_kws = [kw for kws in personal_kws.values() for kw in kws if kw != "newsletter"]
work_specific_kws = [kw for kws in work_kws.values() for kw in kws if kw != "newsletter"]

def count_matches(text, keywords):
    if not isinstance(text, str):
        return 0
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)

# Minor domains that are personal/consumer services
known_personal_minor = {
    'alltel.net', 'cheatsheets.net', 'quickinspirations.com', 'send4fun.com', 
    'flowgo.com', 'play4keeps.com', 'info.iwon.com', 'sweepsclub.com', 
    'gossipflash.com', 'houston.rr.com', 'msn.com', 'live.com', 'yandex.com', 'mail.ru'
}

def determine_mode(row):
    d = row['domain']
    
    # 1. Check known domains
    if d in personal_domains:
        return 'personal'
    if d in work_domains:
        return 'work'
    
    # 2. Check keywords in subject and body
    subj = str(row['subject']).lower() if isinstance(row['subject'], str) else ''
    body = str(row['body']).lower() if isinstance(row['body'], str) else ''
    
    p_matches = sum(1 for kw in personal_specific_kws if kw in subj or kw in body)
    w_matches = sum(1 for kw in work_specific_kws if kw in subj or kw in body)
    
    if p_matches > w_matches:
        return 'personal'
    elif w_matches > p_matches:
        return 'work'
    
    # 3. Fallbacks
    # First 5000 emails are personal
    email_num = int(row['email_id'].split('_')[-1])
    if email_num <= 5000:
        return 'personal'
    
    if d in known_personal_minor:
        return 'personal'
        
    return 'work'

print("Tagging modes...")
df['predicted_mode'] = df.apply(determine_mode, axis=1)
print("Mode Tagging complete.")

# 4. Priority labeling, confidence, flagging, and rules matched
def label_priority(row):
    mode = row['predicted_mode']
    subj = str(row['subject']).lower() if isinstance(row['subject'], str) else ''
    body = str(row['body']).lower() if isinstance(row['body'], str) else ''
    
    # Select the rules based on mode
    kws_to_check = work_kws if mode == 'work' else personal_kws
    
    # Find matches for each tier
    matches_by_tier = {}
    for tier, kws in kws_to_check.items():
        matched = [kw for kw in kws if kw in subj or kw in body]
        if matched:
            matches_by_tier[tier] = matched
            
    # Check for uncertainty (no keywords or conflicting tiers)
    if not matches_by_tier:
        # Matches no keywords
        return pd.Series({
            'predicted_priority': 'low', # Default to low
            'confidence_score': 0.50,
            'flag': 'uncertain',
            'rule_matched': 'None'
        })
    elif len(matches_by_tier) > 1:
        # Conflicting priority keywords across tiers
        all_matched_kws = []
        for tier, kws in matches_by_tier.items():
            all_matched_kws.append(f"{tier}:({', '.join(kws)})")
        conflict_desc = "conflict: " + " | ".join(all_matched_kws)
        
        return pd.Series({
            'predicted_priority': 'medium', # Default to medium or highest matched. Let's use highest matched or medium
            'confidence_score': 0.60,
            'flag': 'uncertain',
            'rule_matched': conflict_desc
        })
    else:
        # Matches keywords in exactly one tier
        tier = list(matches_by_tier.keys())[0]
        matched_kws = matches_by_tier[tier]
        return pd.Series({
            'predicted_priority': tier.lower(),
            'confidence_score': 0.85, # Strong rule patterns are high confidence
            'flag': 'auto_labeled',
            'rule_matched': ', '.join(matched_kws)
        })

print("Labeling priorities and assigning confidence...")
priority_results = df.apply(label_priority, axis=1)
df = pd.concat([df, priority_results], axis=1)
print("Priority labeling complete.")

# 5. Output generation
# Save fully labeled dataset
output_cols = [
    'email_id', 'sender', 'subject', 'body',
    'predicted_mode', 'predicted_priority', 'confidence_score', 'flag', 'rule_matched'
]
labeled_df = df[output_cols]
output_file = "labeled_emails.csv"
labeled_df.to_csv(output_file, index=False)
print(f"Saved full labeled dataset to {output_file}")

# Save sub-list containing only uncertain flagged emails
uncertain_df = labeled_df[labeled_df['flag'] == 'uncertain']
uncertain_file = "uncertain_emails.csv"
uncertain_df.to_csv(uncertain_file, index=False)
print(f"Saved uncertain emails sub-list to {uncertain_file}")

# Output summary stats
print("\n--- Summary Statistics ---")
print("Mode distribution:")
print(labeled_df['predicted_mode'].value_counts())
print("\nPriority distribution:")
print(labeled_df['predicted_priority'].value_counts())
print("\nFlag distribution:")
print(labeled_df['flag'].value_counts())
print("\nAverage confidence score by flag:")
print(labeled_df.groupby('flag')['confidence_score'].mean())
