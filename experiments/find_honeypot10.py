import json

duration_lt_0 = 0
signal_neg = 0

with open('candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        for job in c.get('career_history', []):
            if job.get('duration_months', 0) < 0:
                duration_lt_0 += 1
                break
                
        s = c.get('redrob_signals', {})
        
        # Are there any negative values in redrob_signals that shouldn't be?
        for k, v in s.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                if k != 'offer_acceptance_rate' and k != 'github_activity_score' and v < 0:
                    signal_neg += 1
                    break

print(f"duration_lt_0: {duration_lt_0}")
print(f"signal_neg: {signal_neg}")
