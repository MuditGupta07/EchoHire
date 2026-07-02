import pytest
from src.fraud_detector import check_fraud

def test_valid_candidate():
    candidate = {
        "profile": {"years_of_experience": 5.0, "current_title": "Software Engineer"},
        "career_history": [{"duration_months": 60}],
        "skills": [{"name": "Python", "proficiency": "advanced"}],
        "redrob_signals": {
            "recruiter_response_rate": 0.5,
            "interview_completion_rate": 0.8,
            "applications_submitted_30d": 2,
            "last_active_date": "2026-06-20",
            "endorsements_received": 5,
            "github_activity_score": 50
        }
    }
    is_fraud, reason = check_fraud(candidate)
    assert not is_fraud
    assert reason == "Valid"

def test_yoe_mismatch():
    candidate = {
        "profile": {"years_of_experience": 10.0, "current_title": "Data Scientist"},
        "career_history": [{"duration_months": 24}],  # only 2 years
        "skills": [],
        "redrob_signals": {}
    }
    is_fraud, reason = check_fraud(candidate)
    assert is_fraud
    assert reason == "YoE Mismatch"

def test_math_impossible_rate():
    candidate = {
        "profile": {"years_of_experience": 2.0, "current_title": "Developer"},
        "career_history": [{"duration_months": 24}],
        "skills": [],
        "redrob_signals": {"recruiter_response_rate": 1.5}
    }
    is_fraud, reason = check_fraud(candidate)
    assert is_fraud
    assert reason == "Impossible Rate"

def test_impossible_funnel():
    candidate = {
        "profile": {"years_of_experience": 2.0, "current_title": "Developer"},
        "career_history": [{"duration_months": 24}],
        "skills": [],
        "redrob_signals": {
            "interview_completion_rate": 0.5,
            "applications_submitted_30d": 0,
            "profile_views_received_30d": 0
        }
    }
    is_fraud, reason = check_fraud(candidate)
    assert is_fraud
    assert reason == "Impossible Funnel"

def test_keyword_stuffer():
    candidate = {
        "profile": {"years_of_experience": 2.0, "current_title": "Sales Executive"},
        "career_history": [{"duration_months": 24}],
        "skills": [
            {"name": "LLMs", "proficiency": "expert"},
            {"name": "RAG", "proficiency": "expert"},
            {"name": "PyTorch", "proficiency": "expert"},
            {"name": "TensorFlow", "proficiency": "expert"},
            {"name": "NLP", "proficiency": "expert"},
            {"name": "Generative AI", "proficiency": "expert"},
            {"name": "Deep Learning", "proficiency": "expert"},
            {"name": "Transformers", "proficiency": "expert"},
        ],
        "redrob_signals": {}
    }
    is_fraud, reason = check_fraud(candidate)
    assert is_fraud
    assert reason == "Keyword Stuffer"

def test_ghost_trap():
    candidate = {
        "profile": {"years_of_experience": 2.0, "current_title": "Engineer"},
        "career_history": [{"duration_months": 24}],
        "skills": [],
        "redrob_signals": {
            "last_active_date": "2025-01-01",  # older than 180 days from 2026-06-25
            "recruiter_response_rate": 0.05
        }
    }
    is_fraud, reason = check_fraud(candidate, current_date_str="2026-06-25")
    assert is_fraud
    assert reason == "Ghost Trap"

def test_endorsement_trap():
    candidate = {
        "profile": {"years_of_experience": 2.0, "current_title": "AI Researcher"},
        "career_history": [{"duration_months": 24}],
        "skills": [
            {"name": "PyTorch", "proficiency": "expert"}
        ],
        "redrob_signals": {
            "endorsements_received": 0,
            "github_activity_score": -1
        }
    }
    is_fraud, reason = check_fraud(candidate)
    assert is_fraud
    assert reason == "Endorsement Trap"
