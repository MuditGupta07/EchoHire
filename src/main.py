import os
import shutil
import tempfile
import json
import traceback
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from src.fraud_detector import check_fraud
from src.semantic_engine import SemanticEngine
from src.signal_fusion import generate_final_top_100_df
from src.data_parser import parse_candidates

app = FastAPI(title="EchoHire Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For sandbox
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global singleton for semantic engine
engine = None

@app.on_event("startup")
async def startup_event():
    global engine
    # Load models into memory
    engine = SemanticEngine()

@app.post("/api/run_pipeline")
async def run_pipeline(
    file: UploadFile = File(...),
    job_description: str = Form(default="Looking for a senior AI engineer with deep knowledge in LLMs, RAG, and production system architecture.")
):
    global engine
    try:
        content = await file.read()
        candidates = json.loads(content.decode("utf-8"))
        
        if not isinstance(candidates, list):
            raise HTTPException(status_code=400, detail="JSON must be an array of candidates.")

        # Step 1: Fraud Detection
        valid_candidates = []
        for c in candidates:
            is_fraud, reason = check_fraud(c)
            if not is_fraud:
                valid_candidates.append(c)

        if len(valid_candidates) == 0:
            return {"error": "All candidates dropped by fraud detector."}

        # Step 2: Semantic Engine (Build FAISS)
        engine.build_index(valid_candidates)
        
        # Step 2: Retrieve Top 1000
        top_k = engine.retrieve_top_k(job_description, k=1000)
        
        # Step 2: Cross Encoder Precision Rerank
        reranked = engine.rerank(job_description, top_k)
        
        # Step 3 & 4: Fusion & Reasoning Generation
        df = generate_final_top_100_df(reranked)
        
        # Convert to dictionary for JSON response
        results = df.to_dict(orient="records")
        return {"status": "success", "results": results}
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
