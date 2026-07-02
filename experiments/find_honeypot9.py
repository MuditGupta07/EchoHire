import json

strict_yoe = 0

with open('candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        total_months = sum(job.get('duration_months', 0) for job in c.get('career_history', []))
        yoe = c['profile'].get('years_of_experience', 0)
        
        # In sample, 82 months = 6.8333... yoe is 6.9. So we round to 1 decimal.
        expected_yoe = round(total_months / 12.0, 1)
        if abs(expected_yoe - yoe) > 0.1: # Allow some floating point variance
            strict_yoe += 1

print(f"strict_yoe: {strict_yoe}")
