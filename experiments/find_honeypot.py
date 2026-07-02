import json

views_lt_saves = 0
views_gt_searches = 0
exp_contradiction = 0

impossible_counts = {}

with open('candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        s = c.get('redrob_signals', {})
        p = c.get('profile', {})
        
        # Check exp contradiction
        total_months = sum(job.get('duration_months', 0) for job in c.get('career_history', []))
        yoe = p.get('years_of_experience', 0)
        # Assuming discrepancy of > 1 year is contradiction? 
        # Wait, duration_months is exact, yoe is float. 
        if abs(total_months / 12.0 - yoe) > 0.5:  # Try to find exactly what contradicts
            exp_contradiction += 1
            
        # check mathematically impossible signals
        if s.get('profile_views_received_30d', 0) < s.get('saved_by_recruiters_30d', 0):
            views_lt_saves += 1
            
        # check if any rate > 1 or < 0
        for rate in ['recruiter_response_rate', 'interview_completion_rate', 'offer_acceptance_rate']:
            v = s.get(rate, 0)
            if rate == 'offer_acceptance_rate' and v == -1:
                continue
            if v > 1.0 or v < 0.0:
                impossible_counts[f"{rate}_out_of_bounds"] = impossible_counts.get(f"{rate}_out_of_bounds", 0) + 1
        
        # Check if applications submitted is negative
        if s.get('applications_submitted_30d', 0) < 0:
            impossible_counts['apps_negative'] = impossible_counts.get('apps_negative', 0) + 1
            
        # Check connection_count negative
        if s.get('connection_count', 0) < 0:
            impossible_counts['conn_negative'] = impossible_counts.get('conn_negative', 0) + 1
            
        # Check notice_period_days < 0
        if s.get('notice_period_days', 0) < 0:
            impossible_counts['notice_negative'] = impossible_counts.get('notice_negative', 0) + 1

print(f"exp_contradiction (>0.5 yrs): {exp_contradiction}")
print(f"views_lt_saves: {views_lt_saves}")
print(f"impossible_counts: {impossible_counts}")

