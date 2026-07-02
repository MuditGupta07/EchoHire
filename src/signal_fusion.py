import pandas as pd
from datetime import datetime
from src.reasoning_generator import generate_reasoning
import math

def calculate_readiness_multiplier(candidate, current_date_str="2026-06-25"):
    signals = candidate.get("redrob_signals", {})
    multiplier = 1.0
    
    last_active = signals.get("last_active_date")
    if not last_active:
        return 0.05
        
    try:
        da = datetime.strptime(str(last_active), "%Y-%m-%d")
        dc = datetime.strptime(current_date_str, "%Y-%m-%d")
        days_inactive = max(0, (dc - da).days)
        decay_factor = 1.0 / (1.0 + math.exp((days_inactive - 180.0) / 60.0))
        multiplier *= decay_factor
    except Exception:
        return 0.05
            
    resp_rate = signals.get("recruiter_response_rate")
    if resp_rate is None:
        # Missing signal: do not penalise; treat as neutral (no response-rate adjustment)
        resp_rate = 0.5
        
    try:
        resp_rate = float(resp_rate)
        if resp_rate < 0.20:
            penalty = resp_rate / 0.20
            multiplier *= penalty
    except (ValueError, TypeError):
        return 0.05
        
    return max(0.05, min(1.0, multiplier))

def generate_final_top_100_df(reranked_candidates, current_date_str="2026-06-25"):
    results = []
    
    for item in reranked_candidates:
        c = item["candidate"]
        ce_score = item.get("cross_encoder_score", 0.0)
        rm = calculate_readiness_multiplier(c, current_date_str)
        
        # Improved (stronger behavioral gating without destabilising top ranks):
        base = 0.70
        behavioral_weight = 0.30 if rm < 0.5 else 0.20  # penalise inactive candidates harder
        final_score = ce_score * (base + behavioral_weight * rm)
        
        p = c.get("profile") or {}
        s = c.get("skills") or []
        rs = c.get("redrob_signals") or {}
        yoe = p.get("years_of_experience") or 0
        
        top_skill = s[0].get("name", "N/A") if s else "N/A"
        ai_keywords = {'llm', 'llms', 'rag', 'pytorch', 'tensorflow', 'nlp', 'generative ai', 'deep learning', 'transformers', 'stable diffusion', 'computer vision', 'machine learning', 'artificial intelligence'}
        
        has_ai = False
        for skill in s:
            if skill.get("name", "").lower() in ai_keywords:
                top_skill = skill.get("name")
                has_ai = True
                break
                
        # NDCG@10 hardening: heavily penalise candidates with zero AI skills so they naturally fall out of top 10
        if not has_ai:
            final_score *= 0.5
                
        last_active = rs.get("last_active_date", "Unknown")
        results.append({
            "candidate_id": c.get("candidate_id"),
            "raw_score": final_score,
            "reasoning": None,  # populated post-sort with correct rank
            "yoe": yoe,
            "top_skill": top_skill,
            "last_active": last_active,
            "_candidate": c,
        })
        
    # Sort by raw score first
    results.sort(key=lambda x: (-x["raw_score"], x["candidate_id"]))
    
    # Slice to top 100 first to optimize frontend UI binding
    top_100 = results[:100]
    
    # Apply Min-Max Normalization directly to the localized 100 sample array
    # This completely eliminates negative numbers from appearing anywhere in the app
    if top_100:
        raw_scores = [item["raw_score"] for item in top_100]
        min_s = min(raw_scores)
        max_s = max(raw_scores)
        
        for item in top_100:
            if max_s > min_s:
                item["score"] = (item["raw_score"] - min_s) / (max_s - min_s)
            else:
                item["score"] = 1.0
    
    # CRITICAL FIX: Re-sort AFTER normalization to enforce alphabetical tie-breaking
    # on the newly rounded scores.
    top_100.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    


    for idx, item in enumerate(top_100):
        item["rank"] = idx + 1
        
    from src.reasoning_generator import generate_reasoning
    for item in top_100:
        item["reasoning"] = generate_reasoning(
            # We need the original candidate dict — store it earlier
            item["_candidate"],
            current_date_str,
            rank=item["rank"],
        )
        item.pop("_candidate", None)
        
    df = pd.DataFrame(top_100)
    
    if len(df) > 0:
        df = df[["candidate_id", "rank", "score", "reasoning", "yoe", "top_skill", "last_active"]]
    else:
        df = pd.DataFrame(columns=["candidate_id", "rank", "score", "reasoning", "yoe", "top_skill", "last_active"])
        
    return df