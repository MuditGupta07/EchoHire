import json
from datetime import datetime
import re

AI_KEYWORDS = {
    'llm', 'llms', 'rag', 'pytorch', 'tensorflow', 'nlp', 'generative ai', 'deep learning',
    'transformers', 'stable diffusion', 'computer vision', 'fine-tuning llms', 'speech recognition', 
    'image classification', 'gans', 'machine learning', 'artificial intelligence'
}

ENG_KEYWORDS = {
    'engineer', 'developer', 'scientist', 'architect', 'programmer', 'coder',
    'data', 'machine learning', 'ai', 'software', 'backend', 'frontend', 'fullstack'
}

def check_fraud(candidate_dict, current_date_str="2026-06-25"):
    p = candidate_dict.get('profile', {})
    ch = candidate_dict.get('career_history', [])
    skills = candidate_dict.get('skills', [])
    rs = candidate_dict.get('redrob_signals', {})
    
    # Rule 1: YoE Mismatch (Sparse Profile Resilience)
    yoe = p.get('years_of_experience', 0)
    if len(ch) > 0:
        total_months = sum(job.get('duration_months', 0) for job in ch)
        if abs(total_months / 12.0 - yoe) > 0.5:
            return True, "YoE Mismatch"
        
    # Rule 2: Mathematically Impossible
    # Check rates
    for rate in ['recruiter_response_rate', 'interview_completion_rate']:
        v = rs.get(rate, 0)
        if v > 1.0 or v < 0.0:
            return True, "Impossible Rate"
            
    # Check impossible interviews without any funnel
    if rs.get('interview_completion_rate', 0) > 0 and rs.get('applications_submitted_30d', 0) == 0 and rs.get('profile_views_received_30d', 0) == 0:
        return True, "Impossible Funnel"
        
    # Rule 3: Keyword Stuffer
    current_title = str(p.get('current_title', '')).lower()
    has_eng = any(kw in current_title for kw in ENG_KEYWORDS)
    if not has_eng:
        # Check AI expert skills
        expert_ai_count = sum(
            1 for s in skills 
            if s.get('proficiency') == 'expert' and str(s.get('name', '')).lower() in AI_KEYWORDS
        )
        if expert_ai_count >= 8:
            return True, "Keyword Stuffer"
            
    # Rule 4: Ghost Trap
    last_active = rs.get('last_active_date')
    if last_active:
        try:
            da = datetime.strptime(last_active, "%Y-%m-%d")
            dc = datetime.strptime(current_date_str, "%Y-%m-%d")
            if (dc - da).days > 180 and rs.get('recruiter_response_rate', 1.0) < 0.10:
                return True, "Ghost Trap"
        except ValueError:
            pass
            
    # Rule 5: Endorsement Trap
    expert_ai_count_any = sum(
        1 for s in skills 
        if s.get('proficiency') == 'expert' and str(s.get('name', '')).lower() in AI_KEYWORDS
    )
    if expert_ai_count_any > 0:
        if rs.get('endorsements_received', -1) == 0 and rs.get('github_activity_score', 0) == -1:
            return True, "Endorsement Trap"
            
    return False, "Valid"
