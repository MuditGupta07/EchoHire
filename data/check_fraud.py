import json

fields = {}
with open('candidates.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        c = json.loads(line)
        s = c.get('redrob_signals', {})
        if s.get('profile_views_received_30d', 0) > s.get('search_appearance_30d', 0):
            fields['views>searches'] = fields.get('views>searches', 0) + 1
        if s.get('saved_by_recruiters_30d', 0) > s.get('profile_views_received_30d', 0):
            fields['saves>views'] = fields.get('saves>views', 0) + 1
        
        for k, v in s.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                if k not in fields: fields[k] = [v, v]
                fields[k][0] = min(fields[k][0], v)
                fields[k][1] = max(fields[k][1], v)
print(fields)
