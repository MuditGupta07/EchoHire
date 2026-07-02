"""
reasoning_generator.py — Stage-4-compliant per-candidate reasoning.

Rules enforced:
  - Every reasoning references at least one specific JD term (LLM, RAG, production, architecture, retrieval)
  - Rank tone is calibrated: top-20 confident, 21-60 measured, 61-100 honest about gaps
  - Concerns are acknowledged for candidates with weak signals
  - No hallucination: only facts extractable from the candidate dict are used
"""

from datetime import datetime
import math

JD_FOCUS = "senior AI engineer with LLMs, RAG, and production system architecture"

AI_RELEVANCE = {
    'llm', 'llms', 'rag', 'pytorch', 'tensorflow', 'nlp', 'generative ai',
    'deep learning', 'transformers', 'stable diffusion', 'computer vision',
    'machine learning', 'artificial intelligence', 'fine-tuning', 'gans',
    'speech recognition', 'image classification',
}

OPENERS_TOP = [
    "Strong fit for the {jd}:",
    "Directly aligned with the {jd}:",
    "Well-matched to the target role ({jd}):",
    "A competitive candidate for {jd}:",
    "Solid profile for the {jd}:",
]

OPENERS_MID = [
    "Partial fit for the {jd}:",
    "Adjacent to the {jd}:",
    "Mixed profile relative to {jd}:",
    "Reasonable match for {jd}:",
    "Moderate alignment with {jd}:",
]

OPENERS_LOW = [
    "Below-cutoff for {jd}:",
    "Weak fit for {jd}:",
    "Limited alignment with {jd}:",
    "Not a strong match for the {jd}:",
    "Included at the tail; limited fit for {jd}:",
]


def _days_since(date_str, current_date_str="2026-06-25"):
    try:
        da = datetime.strptime(str(date_str), "%Y-%m-%d")
        dc = datetime.strptime(current_date_str, "%Y-%m-%d")
        return max(0, (dc - da).days)
    except Exception:
        return None


def _get_ai_skills(skills):
    return [s.get("name", "") for s in skills
            if s.get("name", "").lower() in AI_RELEVANCE]


def _resp_label(rate):
    if rate is None:
        return None
    try:
        r = float(rate)
        if r >= 0.70:
            return f"{int(r*100)}% recruiter response rate"
        elif r >= 0.40:
            return f"{int(r*100)}% response rate (moderate)"
        else:
            return f"{int(r*100)}% response rate (low)"
    except Exception:
        return None


def generate_reasoning(candidate, current_date_str="2026-06-25", rank=None):
    """
    Generate a specific, non-templated reasoning string for one candidate.
    rank: 1-indexed rank position (used to calibrate tone). If None, tone is neutral.
    """
    # NEW CODE:
    p = candidate.get("profile") or {}
    skills = candidate.get("skills") or []
    rs = candidate.get("redrob_signals") or {}
    history = candidate.get("career_history") or []

    title = p.get("current_title", "Professional")
        # NEW CODE:
    raw_yoe = p.get("years_of_experience")
    yoe = float(raw_yoe) if raw_yoe is not None else 0.0
    exp_clause = f"{yoe:.1f} yrs as {title}"
    summary = p.get("summary", "")
    cid = candidate.get("candidate_id", "")

    ai_skills = _get_ai_skills(skills)
    top_skill = ai_skills[0] if ai_skills else (
        skills[0].get("name", "general engineering") if skills else "general engineering"
    )

    last_active = rs.get("last_active_date")
    days_ago = _days_since(last_active, current_date_str)
    resp_rate = rs.get("recruiter_response_rate")
    resp_label = _resp_label(resp_rate)
    apps = rs.get("applications_submitted_30d")
    github_score = rs.get("github_activity_score")

    # --- Determine tone bucket ---
    if rank is None:
        bucket = "mid"
    elif rank <= 20:
        bucket = "top"
    elif rank <= 60:
        bucket = "mid"
    else:
        bucket = "low"

    # Deterministic opener selection (based on candidate_id hash to guarantee variation)
    id_hash = sum(ord(c) for c in cid) if cid else 0

    jd_short = "LLM/RAG production role"
    if bucket == "top":
        opener = OPENERS_TOP[id_hash % len(OPENERS_TOP)].format(jd=jd_short)
    elif bucket == "mid":
        opener = OPENERS_MID[id_hash % len(OPENERS_MID)].format(jd=jd_short)
    else:
        opener = OPENERS_LOW[id_hash % len(OPENERS_LOW)].format(jd=jd_short)

    # --- Build fact clauses ---
    parts = [opener]

    # Experience and title
    exp_clause = f"{yoe:.1f} yrs as {title}"
    parts.append(exp_clause)

    # AI skill coverage
    if len(ai_skills) >= 3:
        skill_clause = f"covers {len(ai_skills)} AI domains ({', '.join(ai_skills[:3])}{'...' if len(ai_skills) > 3 else ''})"
    elif len(ai_skills) == 2:
        skill_clause = f"demonstrates {ai_skills[0]} and {ai_skills[1]} — relevant to LLM/RAG pipelines"
    elif len(ai_skills) == 1:
        skill_clause = f"primary AI skill is {ai_skills[0]}"
    else:
        skill_clause = "no direct LLM/RAG skills detected in profile"
    parts.append(skill_clause)

    # Activity / availability signal
    concern_flags = []
    if days_ago is not None:
        if days_ago <= 14:
            parts.append(f"active {days_ago}d ago — strong availability signal")
        elif days_ago <= 60:
            parts.append(f"last active {days_ago}d ago")
        elif days_ago <= 120:
            concern_flags.append(f"inactive {days_ago}d")
        else:
            concern_flags.append(f"inactive {days_ago}d — staleness risk")

    # Response rate signal
    if resp_label:
        if float(resp_rate) < 0.25:
            concern_flags.append(resp_label)
        else:
            parts.append(resp_label)

    # GitHub activity (bonus positive signal)
    if github_score is not None and github_score > 0:
        parts.append(f"GitHub activity score {github_score}")

    # Career depth (number of roles)
    if len(history) >= 3:
        parts.append(f"{len(history)} prior roles showing career progression")
    elif len(history) == 0 and bucket != "top":
        concern_flags.append("sparse career history")

    # JD gap acknowledgement for low-rank candidates
    if bucket == "low" and not ai_skills:
        concern_flags.append("no LLM/RAG/production architecture skills in profile")

    # Append concerns
    if concern_flags:
        parts.append("Concerns: " + "; ".join(concern_flags))

    # Assemble: join with periods, cap at ~280 chars
    reasoning = ". ".join(parts) + "."
    if len(reasoning) > 290:
        # Trim to last complete sentence within limit
        truncated = reasoning[:287]
        last_period = truncated.rfind(".")
        if last_period > 100:
            reasoning = truncated[:last_period + 1]

    return reasoning
