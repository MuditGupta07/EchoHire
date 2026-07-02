import json
from datetime import datetime

signup_gt_active = 0
last_active_future = 0
endorsements_gt_connections = 0
exp_contradiction = 0

with open('candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        s = c.get('redrob_signals', {})
        p = c.get('profile', {})
        
        # Check exp contradiction
        total_months = sum(job.get('duration_months', 0) for job in c.get('career_history', []))
        yoe = p.get('years_of_experience', 0)
        # Using abs > 0.5 difference
        if abs(total_months / 12.0 - yoe) > 0.5:
            exp_contradiction += 1
            
        signup = s.get('signup_date')
        last_active = s.get('last_active_date')
        
        if signup and last_active:
            # Parse dates
            try:
                ds = datetime.strptime(signup, '%Y-%m-%d')
                da = datetime.strptime(last_active, '%Y-%m-%d')
                if ds > da:
                    signup_gt_active += 1
            except:
                pass
                
        if s.get('endorsements_received', 0) > s.get('connection_count', 0):
            endorsements_gt_connections += 1

print(f"exp_contradiction (>0.5 yrs): {exp_contradiction}")
print(f"signup_gt_active (Time travel): {signup_gt_active}")
print(f"endorsements_gt_connections: {endorsements_gt_connections}")

