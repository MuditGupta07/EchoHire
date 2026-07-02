import json
from collections import defaultdict

counts = defaultdict(int)

with open('candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        s = c.get('redrob_signals', {})
        
        # Test many many conditions
        counts['offers_gt_interviews'] += (s.get('offer_acceptance_rate', 0) > s.get('interview_completion_rate', 0) and s.get('offer_acceptance_rate', 0) > 0)
        counts['saves_gt_views_by_100'] += (s.get('saved_by_recruiters_30d', 0) > s.get('profile_views_received_30d', 0) * 100)
        
        # Are there any NaN values?
        for k, v in s.items():
            if isinstance(v, float) and v != v:
                counts['nan_in_signals'] += 1
                
        # Are there any probabilities < 0? (except offer_acceptance_rate == -1)
        if s.get('recruiter_response_rate', 0) < 0: counts['response_rate_lt_0'] += 1
        if s.get('interview_completion_rate', 0) < 0: counts['interview_rate_lt_0'] += 1
        if s.get('offer_acceptance_rate', 0) < -1: counts['offer_rate_lt_m1'] += 1
        
        # What if notice period > 180?
        if s.get('notice_period_days', 0) > 180: counts['notice_gt_180'] += 1
        
        # What if completeness > 100?
        if s.get('profile_completeness_score', 0) > 100: counts['completeness_gt_100'] += 1
        
        # What if expected salary min > max by a lot?
        
print({k: v for k, v in counts.items() if v > 0})
