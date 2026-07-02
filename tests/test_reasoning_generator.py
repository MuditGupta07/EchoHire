import pytest
from src.reasoning_generator import generate_reasoning

def test_generate_reasoning():
    candidate1 = {
        "profile": {"current_title": "Backend Engineer", "years_of_experience": 4},
        "skills": [{"name": "Python"}, {"name": "PyTorch"}, {"name": "LLMs"}],
        "redrob_signals": {"recruiter_response_rate": 0.85, "last_active_date": "2026-06-20"}
    }
    
    res1 = generate_reasoning(candidate1, current_date_str="2026-06-25")
    assert "Backend Engineer" in res1
    assert "4 years" in res1
    assert "2 core AI skills" in res1
    assert "85% recruiter response rate" in res1
    assert "5 days" in res1
    print(f"\nSample 1: {res1}")
    
    # Test Jargon Filter
    candidate2 = {
        "profile": {"current_title": "Data Scientist", "years_of_experience": 2},
        "skills": [{"name": "RAG pipeline"}, {"name": "FAISS"}],
        "redrob_signals": {"recruiter_response_rate": 1.0, "last_active_date": "2026-06-25"}
    }
    res2 = generate_reasoning(candidate2, current_date_str="2026-06-25")
    print(f"Sample 2: {res2}")
    
    # Assert jargon is replaced
    assert "FAISS" not in res2
    assert "RAG pipeline" not in res2
    assert "technical methodology" in res2

    # Test No AI Skills
    candidate3 = {
        "profile": {"current_title": "Product Manager", "years_of_experience": 10},
        "skills": [{"name": "Agile"}],
        "redrob_signals": {"recruiter_response_rate": 0.45, "last_active_date": "2026-06-01"}
    }
    res3 = generate_reasoning(candidate3, current_date_str="2026-06-25")
    print(f"Sample 3: {res3}")
    assert "Agile" in res3
    assert "core AI" not in res3
