import json

salary_min_gt_max = 0

with open('candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        s = c.get('redrob_signals', {})
        sal = s.get('expected_salary_range_inr_lpa', {})
        
        if sal.get('min', 0) > sal.get('max', 0):
            salary_min_gt_max += 1

print(f"salary_min_gt_max: {salary_min_gt_max}")
