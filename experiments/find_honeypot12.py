import json
from datetime import datetime

invalid_dates = 0

with open('candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        s = c.get('redrob_signals', {})
        
        for date_field in ['signup_date', 'last_active_date']:
            val = s.get(date_field)
            if val:
                try:
                    datetime.strptime(val, '%Y-%m-%d')
                except ValueError:
                    invalid_dates += 1

print(f"invalid_dates: {invalid_dates}")
