import json

impossible = 0

with open('candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        s = c.get('redrob_signals', {})
        
        if s.get('saved_by_recruiters_30d', 0) > s.get('search_appearance_30d', 0):
            impossible += 1

print(f"saved_by_recruiters_30d > search_appearance_30d: {impossible}")
