import os
import sys

# 1. Force absolute paths. This fixes the Windows offline symlink bug.
base_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(base_dir, "models")

# 2. Set environment variables BEFORE any Hugging Face imports
os.environ["HF_HOME"] = models_dir
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"
# (Removed the deprecated TRANSFORMERS_CACHE to stop the warnings)

import argparse
import pickle
import faiss
import subprocess

from sentence_transformers import SentenceTransformer, CrossEncoder
from src.signal_fusion import generate_final_top_100_df

def run_rank(candidates_path, out_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    faiss_path = os.path.join(base_dir, "faiss_index.bin")
    meta_path = os.path.join(base_dir, "candidates_meta.pkl")
    
    if not os.path.exists(faiss_path) or not os.path.exists(meta_path):
        subprocess.run([sys.executable, os.path.join(base_dir, "scripts", "precompute_index.py"), candidates_path], check=True)
        
    index = faiss.read_index(faiss_path)
    with open(meta_path, "rb") as f:
        valid_candidates = pickle.load(f)
        
    bi_encoder = SentenceTransformer("all-MiniLM-L6-v2")
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    
    job_description = "Looking for a senior AI engineer with deep knowledge in LLMs, RAG, and production system architecture."
    
    jd_emb = bi_encoder.encode([job_description], convert_to_numpy=True)
    faiss.normalize_L2(jd_emb)
    
    # Sandbox optimization: ensure the candidate limits match lower constraint pools safely
    k = min(100, len(valid_candidates))
    distances, indices = index.search(jd_emb, k)
    
    top_k_candidates = [valid_candidates[idx] for idx in indices[0] if idx != -1]
    
    pairs = []
    for c in top_k_candidates:
        p = c.get("profile", {})
        title = p.get("current_title", "")
        summary = p.get("summary", "")
        history_text = " ".join([h.get("title", "") for h in c.get("career_history", [])])
        text = f"{title}. {summary} {history_text}"
        pairs.append([job_description, text])
        
    cross_scores = cross_encoder.predict(pairs, batch_size=32, show_progress_bar=False)
    
    reranked = []
    for i, c in enumerate(top_k_candidates):
        reranked.append({
            "candidate": c,
            "cross_encoder_score": float(cross_scores[i])
        })
        
    df = generate_final_top_100_df(reranked)
    
    # Column matching compliance check
    final_export_df = df[['candidate_id', 'rank', 'score', 'reasoning']]
    final_export_df.to_csv(out_path, index=False)
    print(f"Success! Exported to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True, help="Path to candidates data")
    parser.add_argument("--out", required=True, help="Path to output CSV file")
    args = parser.parse_args()
    
    run_rank(args.candidates, args.out)