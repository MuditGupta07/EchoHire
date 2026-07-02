import json
import time
import pytest
from pathlib import Path
from src.semantic_engine import SemanticEngine, build_candidate_text

@pytest.fixture(scope="module")
def sample_candidates():
    path = Path("data/sample_candidates.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="module")
def engine():
    # Model loading happens once per test session to avoid timing the download
    return SemanticEngine()

def test_build_candidate_text(sample_candidates):
    c = sample_candidates[0]
    text = build_candidate_text(c)
    assert isinstance(text, str)
    assert len(text) > 50
    assert c["profile"]["current_title"] in text

def test_stage1_recall_latency_and_accuracy(engine, sample_candidates):
    # Time the FAISS index building
    start_time = time.time()
    engine.build_index(sample_candidates)
    build_time = time.time() - start_time
    
    # Assert building doesn't take outrageously long (e.g., > 10s for the sample)
    assert build_time < 30.0, f"FAISS index build took {build_time:.2f}s"

    query = "Looking for a backend engineer with Python, SQL, and Kafka experience."
    
    start_time = time.time()
    top_k = engine.retrieve_top_k(query, k=10)
    retrieve_time = time.time() - start_time
    
    assert retrieve_time < 2.0, f"FAISS retrieval took {retrieve_time:.2f}s"
    assert len(top_k) <= 10
    assert "faiss_score" in top_k[0]
    assert "candidate" in top_k[0]
    
    print(f"\n[Stage 1] Index Build Time: {build_time:.4f}s")
    print(f"[Stage 1] Retrieve Time: {retrieve_time:.4f}s")

def test_stage2_precision_latency_and_accuracy(engine, sample_candidates):
    # Ensure index is built
    if engine.index is None:
        engine.build_index(sample_candidates)
        
    query = "Looking for a backend engineer with Python, SQL, and Kafka experience."
    
    # We must explicitly limit to top 1000, but sample might have fewer. 
    # Let's retrieve 1000.
    top_1000 = engine.retrieve_top_k(query, k=1000)
    
    start_time = time.time()
    reranked = engine.rerank(query, top_1000)
    rerank_time = time.time() - start_time
    
    # Since cross-encoder is heavy, assert it runs within a reasonable budget 
    # for the sample set (max 1000 items). 
    # For a few hundred/thousand items, it shouldn't take more than 60 seconds on CPU.
    assert rerank_time < 120.0, f"Cross encoder took {rerank_time:.2f}s, too slow for budget!"
    
    assert len(reranked) == len(top_1000)
    assert "cross_encoder_score" in reranked[0]
    
    # Validate sorting
    scores = [item["cross_encoder_score"] for item in reranked]
    assert scores == sorted(scores, reverse=True)

    print(f"\n[Stage 2] Cross-Encoder Rerank Time for {len(top_1000)} items: {rerank_time:.4f}s")
