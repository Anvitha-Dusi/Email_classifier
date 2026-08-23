import pandas as pd

df = pd.read_csv("uncertain_emails.csv")
conflicts = df[df['rule_matched'].str.startswith('conflict', na=False)]

print("Number of conflicts:", len(conflicts))
print("\nUnique subjects of conflicts:")
print(conflicts['subject'].value_counts())

print("\nUnique domains of conflicts:")
print(conflicts['domain'].value_counts())
