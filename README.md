![EchoHire Sandbox UI](./frontend/public/hero_screenshot.png)

# EchoHire

> **Beyond Semantic Matching.** Identifying mathematically viable, highly responsive talent for the modern enterprise.

## The Problem & Our Solution

**The Problem**: Existing AI hiring tools operate on a fundamental flaw—they blindly match keywords. They fall victim to "keyword stuffers" and continually recommend "ghosts" (candidates who never respond or haven't logged in for months). This burns recruiter trust and wastes critical hiring cycles.

**The Solution**: We built **EchoHire**. Our engine doesn't just evaluate semantic similarity; it evaluates *truth* and *availability*. By fusing deep context analysis with strict behavioral guardrails, we ensure that the top candidates are not only technically elite but actively responsive and genuine.

## Core Innovations

Here is how we ensure world-class precision:

- **The Fraud Detector**: Our pre-computation engine actively hunts anomalies. It successfully intercepted and purged exactly **1,691** honeypots, keyword-stuffers, and impossible profiles *before* they ever hit the FAISS index.
- **The Readiness Multiplier**: We mathematically penalize candidates who are structurally unavailable despite high semantic scores. Our engine leverages a strict behavioral decay curve:
  - A severe decay penalty is applied if a candidate's `last_active_date` is >180 days in the past.
  - A steep linear penalty is applied if their `recruiter_response_rate` falls below 20%.

## Architecture & Beating the 5-Minute Constraint

To comply with the strict Redrob CPU constraints on a 100,000-candidate dataset, we completely decoupled our architecture into an Offline/Online model.

- **Phase 1 (Offline Pre-computation)**: Executed locally in **~67 minutes**. This phase cleans the massive dataset, computes dense vector embeddings via `sentence-transformers/all-MiniLM-L6-v2`, and serializes the outputs into `faiss_index.bin` and `candidates_meta.pkl`. *Note: this is the only phase that downloads models.*
- **Phase 2 (Online Inference)**: Lightning-fast precision reranking using the `ms-marco-MiniLM-L-6-v2` Cross-Encoder. By instantly loading the pre-computed index, our official CLI script extracts the Top 1,000 candidates and generates the final CSV submission entirely offline in roughly **~10 seconds**—well under the 5-minute threshold.

## How to Run

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Phase 1 - Pre-computation (Offline Indexing)
Execute this command first to build the FAISS index and clean the data. This script is permitted to download models locally.
```bash
python scripts/precompute_index.py ./candidates.jsonl
```

### Step 3: Phase 2 - Online Ranking (Official Submission)
The hackathon-mandated CLI execution to rank the Top 100 and export the valid CSV. This runs strictly offline using cached models and local data.
```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv
```

### Step 3: Launching the Sandbox UI
Boot the "Midnight Intelligence" Sandbox UI to interact with sample data instantly (Requires 2 terminals):

**Terminal 1 (FastAPI Backend):**
```bash
uvicorn src.main:app --reload
```
**Terminal 2 (Vite React Frontend):**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```text
EchoHire/
├── data/                  # Raw hackathon datasets and validation schemas
├── experiments/           # Sandboxed exploration and honeypot scripts
├── frontend/              # The "Midnight Intelligence" Vite React UI
├── scripts/
│   └── precompute_index.py  # Phase 1: FAISS & Metadata generation
├── src/
│   ├── main.py            # FastAPI backend endpoints
│   ├── semantic_engine.py # Core NLP matching logic
│   ├── signal_fusion.py   # Readiness Multiplier & Final Scoring
│   ├── fraud_detector.py  # Keyword stuffer & Ghost trap logic
│   ├── data_parser.py     # JSONL memory-safe streaming
│   └── reasoning_generator.py # Zero-latency human string generator
├── rank.py                # Phase 2: Official 5-minute ranking CLI
├── README.md              # Documentation
└── requirements.txt       # Unified Python dependencies
```
