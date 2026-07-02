import json
from collections import defaultdict

counts = defaultdict(int)

with open('candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        s = c.get('redrob_signals', {})
        
        # We will test hundreds of arbitrary combinations
        
        # 1. Exact equality
        counts['views_eq_saves'] += (s.get('profile_views_received_30d', -1) == s.get('saved_by_recruiters_30d', -2))
        counts['views_eq_search'] += (s.get('profile_views_received_30d', -1) == s.get('search_appearance_30d', -2))
        
        # 2. Impossibility of ratios
        if s.get('recruiter_response_rate', 0) > s.get('interview_completion_rate', 1):
            counts['rr_gt_ic'] += 1
            
        # 3. Time travel exact
        # We know signup > last_active is 7496
        
        # 4. Values exactly 0
        if s.get('profile_views_received_30d') == 0: counts['views_0'] += 1
        
        # Let's check for impossible counts
        if s.get('endorsements_received', 0) > s.get('connection_count', 0) * 10:
            counts['end_gt_10x_conn'] += 1
            
        if s.get('saved_by_recruiters_30d', 0) > s.get('search_appearance_30d', 0):
            counts['saves_gt_search'] += 1
            
        if s.get('saved_by_recruiters_30d', 0) > s.get('profile_views_received_30d', 0) + s.get('search_appearance_30d', 0):
            counts['saves_gt_views_and_search'] += 1
            
        if s.get('applications_submitted_30d', 0) > s.get('profile_views_received_30d', 0):
            counts['apps_gt_views'] += 1
            
        if s.get('interview_completion_rate', 0) > 0 and s.get('applications_submitted_30d', 0) == 0 and s.get('profile_views_received_30d', 0) == 0:
            counts['interviews_no_apps_no_views'] += 1
            
        if s.get('offer_acceptance_rate', -1) > 0 and s.get('interview_completion_rate', 0) == 0:
            counts['offers_no_interviews'] += 1
            
        if s.get('notice_period_days', 0) > 90:
            counts['notice_gt_90'] += 1

print({k: v for k, v in counts.items() if 10 <= v <= 100})
