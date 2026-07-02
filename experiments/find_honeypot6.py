import json

impossible = 0

with open('candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        s = c.get('redrob_signals', {})
        
        rr = s.get('recruiter_response_rate', 0)
        rt = s.get('avg_response_time_hours', 0)
        
        if rr == 0.0 and rt > 0.0:
            impossible += 1

print(f"recruiter_response_rate == 0 but avg_response_time_hours > 0: {impossible}")
