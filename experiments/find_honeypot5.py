import json
from datetime import datetime

future_active = 0
future_signup = 0

with open('candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        s = c.get('redrob_signals', {})
        
        last_active = s.get('last_active_date')
        signup = s.get('signup_date')
        
        if last_active:
            try:
                if last_active > "2026-06-25":
                    future_active += 1
            except: pass
            
        if signup:
            try:
                if signup > "2026-06-25":
                    future_signup += 1
            except: pass

print(f"future_active: {future_active}")
print(f"future_signup: {future_signup}")
