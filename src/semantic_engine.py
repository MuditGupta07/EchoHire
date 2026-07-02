import numpy as np
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder

def build_candidate_text(candidate):
    """
    Concatenate summary, current_title, and career_history text into a clean string.
    """
    profile = candidate.get("profile", {})
    title = profile.get("current_title", "")
    summary = profile.get("summary", "")
    
    career_texts = []
    for job in candidate.get("career_history", []):
        job_title = job.get("title", "")
        desc = job.get("description", "")
        career_texts.append(f"{job_title}. {desc}")
        
    history_text = " ".join(career_texts)
    
    # Normalize strings (basic cleaning)
    raw_text = f"Title: {title}. Summary: {summary}. Experience: {history_text}"
    return " ".join(raw_text.split())

class SemanticEngine:
    def __init__(self, bi_encoder_model='sentence-transformers/all-MiniLM-L6-v2', cross_encoder_model='cross-encoder/ms-marco-MiniLM-L-6-v2'):
        self.bi_encoder = SentenceTransformer(bi_encoder_model)
        self.cross_encoder = CrossEncoder(cross_encoder_model)
        self.index = None
        self.candidates = []

    def build_index(self, candidates):
        """
        Build FAISS index for stage 1 recall.
        """
        self.candidates = candidates
        texts = [build_candidate_text(c) for c in candidates]
        
        # Bi-Encoder output is already normalized by default for all-MiniLM, but let's be safe
        embeddings = self.bi_encoder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim) # Inner Product is Cosine Similarity if normalized
        self.index.add(embeddings)

    def retrieve_top_k(self, query, k=1000):
        """
        Stage 1: Recall top-k candidates using FAISS.
        """
        if self.index is None or len(self.candidates) == 0:
            return []
            
        k = min(k, len(self.candidates))
        query_emb = self.bi_encoder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        scores, indices = self.index.search(query_emb, k)
        
        top_candidates = []
        for rank, idx in enumerate(indices[0]):
            top_candidates.append({
                "candidate": self.candidates[idx],
                "faiss_score": float(scores[0][rank])
            })
        return top_candidates

    def rerank(self, query, top_candidates):
        """
        Stage 2: Precision scoring using Cross-Encoder.
        """
        if not top_candidates:
            return []
            
        pairs = []
        for item in top_candidates:
            text = build_candidate_text(item["candidate"])
            pairs.append([query, text])
            
        # Cross encoder returns raw logits, higher is more similar
        cross_scores = self.cross_encoder.predict(pairs)
        
        for i, item in enumerate(top_candidates):
            item["cross_encoder_score"] = float(cross_scores[i])
            
        # Sort by cross encoder score descending
        reranked = sorted(top_candidates, key=lambda x: x["cross_encoder_score"], reverse=True)
        return reranked
