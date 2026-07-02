import json

conditions = {}

with open('candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        s = c.get('redrob_signals', {})
        p = c.get('profile', {})
        
        # Track various boolean conditions
        total_months = sum(job.get('duration_months', 0) for job in c.get('career_history', []))
        yoe = p.get('years_of_experience', 0)
        
        conds = {
            'yoe_diff_gt_1': abs(total_months / 12.0 - yoe) > 1.0,
            'yoe_diff_gt_2': abs(total_months / 12.0 - yoe) > 2.0,
            'yoe_diff_gt_3': abs(total_months / 12.0 - yoe) > 3.0,
            'views_lt_saves': s.get('profile_views_received_30d', 0) < s.get('saved_by_recruiters_30d', 0),
            'interviews_but_no_apps': s.get('interview_completion_rate', 0) > 0 and s.get('applications_submitted_30d', 0) == 0, # wait, might be sourced
            'accepted_but_no_interviews': s.get('offer_acceptance_rate', -1) > 0 and s.get('interview_completion_rate', 0) == 0,
            'response_rate_gt_0_but_no_views': s.get('recruiter_response_rate', 0) > 0 and s.get('profile_views_received_30d', 0) == 0,
            'saves_gt_views': s.get('saved_by_recruiters_30d', 0) > s.get('profile_views_received_30d', 0),
            'skill_assessment_gt_100': any(v > 100 for v in s.get('skill_assessment_scores', {}).values()),
            'skill_assessment_lt_0': any(v < 0 for v in s.get('skill_assessment_scores', {}).values()),
        }
        
        for k, v in conds.items():
            if v:
                conditions[k] = conditions.get(k, 0) + 1

print(conditions)
