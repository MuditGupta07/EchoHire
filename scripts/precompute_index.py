import os
import torch
import argparse

# 1. CPU Thread Throttling: Prevent PyTorch from locking OS threads
os.environ["OMP_NUM_THREADS"] = "4"
torch.set_num_threads(4)

# Enforce local model caching to prevent network calls
base_dir = os.path.join(os.path.dirname(__file__), '..')
model_cache_dir = os.path.join(base_dir, "models")
os.environ["HF_HOME"] = model_cache_dir

import pickle
import faiss
import sys
import gc
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, CrossEncoder

# Allow importing from src
sys.path.append(base_dir)

from src.data_parser import parse_candidates
from src.fraud_detector import check_fraud

def precompute():
    # Use argparse to properly extract the --candidates path
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=False, help="Path to candidates.jsonl.gz")
    args = parser.parse_args()
    
    if args.candidates:
        data_path = args.candidates
    else:
        data_path = os.path.join(base_dir, "data", "candidates.jsonl.gz")
        if not os.path.exists(data_path):
            data_path = os.path.join(base_dir, "data", "candidates.jsonl")
            if not os.path.exists(data_path):
                print("Error: Could not find candidates file in data/")
                sys.exit(1)
            
    print("Initializing Bi-Encoder (all-MiniLM-L6-v2) with throttled CPU threads and local caching...")
    encoder = SentenceTransformer("all-MiniLM-L6-v2")
    
    print("Pre-caching Cross-Encoder (ms-marco-MiniLM-L-6-v2) for offline phase...")
    CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    
    # Initialize FAISS index
    dimension = encoder.get_sentence_embedding_dimension()
    index = faiss.IndexFlatIP(dimension)
    
    print("Streaming candidates, filtering honeypots, and encoding in micro-batches...")
    valid_candidates = []
    batch_candidates = []
    batch_texts = []
    
    # 4. Progress Resilience
    pbar = tqdm(desc="Processing Candidates (Micro-Batched)")
    
    for c in parse_candidates(data_path):
        is_fraud, _ = check_fraud(c)
        if not is_fraud:
            p = c.get("profile", {})
            title = p.get("current_title", "")
            summary = p.get("summary", "")
            history_text = " ".join([h.get("title", "") for h in c.get("career_history", [])])
            text = f"{title}. {summary} {history_text}"
            
            batch_candidates.append(c)
            batch_texts.append(text)
            
            # 2. Strict Micro-Batching
            if len(batch_texts) == 32:
                embeddings = encoder.encode(batch_texts, show_progress_bar=False, convert_to_numpy=True)
                faiss.normalize_L2(embeddings)
                index.add(embeddings)
                
                valid_candidates.extend(batch_candidates)
                
                batch_candidates = []
                batch_texts = []
                
                pbar.update(32)
                
                # 3. Memory Management
                gc.collect()

    # Process final partial batch
    if len(batch_texts) > 0:
        embeddings = encoder.encode(batch_texts, show_progress_bar=False, convert_to_numpy=True)
        faiss.normalize_L2(embeddings)
        index.add(embeddings)
        valid_candidates.extend(batch_candidates)
        pbar.update(len(batch_texts))
        gc.collect()
        
    pbar.close()
    
    print(f"Total valid candidates processed: {len(valid_candidates)}")
    
    out_faiss = os.path.join(base_dir, "faiss_index.bin")
    faiss.write_index(index, out_faiss)
    print(f"Saved {out_faiss}")
    
    out_meta = os.path.join(base_dir, "candidates_meta.pkl")
    with open(out_meta, "wb") as f:
        pickle.dump(valid_candidates, f)
    print(f"Saved {out_meta}")

if __name__ == "__main__":
    precompute()