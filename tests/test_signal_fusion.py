import os
import subprocess
import pytest
from src.signal_fusion import calculate_readiness_multiplier, generate_final_top_100_df

def test_readiness_multiplier():
    # Base case
    c_base = {"redrob_signals": {"recruiter_response_rate": 0.5, "last_active_date": "2026-06-20"}}
    assert calculate_readiness_multiplier(c_base, "2026-06-25") == 1.0
    
    # Severe decay > 180 days (e.g. 1 year ago)
    c_old = {"redrob_signals": {"recruiter_response_rate": 0.5, "last_active_date": "2025-06-25"}}
    rm_old = calculate_readiness_multiplier(c_old, "2026-06-25")
    assert rm_old < 1.0
    assert rm_old <= 0.5 # Has severe penalty
    
    # Linear penalty < 0.20
    c_low_resp = {"redrob_signals": {"recruiter_response_rate": 0.1, "last_active_date": "2026-06-20"}}
    rm_low = calculate_readiness_multiplier(c_low_resp, "2026-06-25")
    assert rm_low == 0.5  # 0.1 / 0.20

def test_fusion_and_csv_validation(tmp_path):
    # Generate 150 dummy candidates
    reranked = []
    for i in range(150):
        # Format CAND_XXXXXXX
        cid = f"CAND_{i:07d}"
        reranked.append({
            "candidate": {
                "candidate_id": cid,
                "profile": {"current_title": "AI Engineer", "years_of_experience": 5},
                "skills": [{"name": "PyTorch"}, {"name": "LLMs"}],
                "redrob_signals": {
                    "recruiter_response_rate": 0.5 if i % 2 == 0 else 0.1,
                    "last_active_date": "2026-06-20"
                }
            },
            "cross_encoder_score": float(i) # Higher score for later ones
        })
        
    df = generate_final_top_100_df(reranked, "2026-06-25")
    
    assert len(df) == 100
    assert list(df.columns) == ["candidate_id", "rank", "score", "reasoning"]
    
    # Check descending sort
    scores = df["score"].tolist()
    assert scores == sorted(scores, reverse=True)
    
    # Export to CSV
    csv_path = tmp_path / "team_antigravity.csv"
    df.to_csv(csv_path, index=False)
    
    # Run validation script from data/validate_submission.py
    script_path = os.path.join(os.getcwd(), "data", "validate_submission.py")
    result = subprocess.run(
        ["python", script_path, str(csv_path)],
        capture_output=True,
        text=True
    )
    
    # The output should say "Submission is valid."
    assert result.returncode == 0, f"Validation failed: {result.stdout}\n{result.stderr}"
    assert "Submission is valid." in result.stdout

