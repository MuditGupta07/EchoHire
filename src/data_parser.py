import json
import gzip
from pathlib import Path

def parse_candidates(filepath: str):
    """
    Highly optimized generator that yields candidates one by one.
    Handles both .jsonl and .jsonl.gz transparently.
    """
    path = Path(filepath)
    if path.suffix == '.gz':
        f = gzip.open(path, 'rt', encoding='utf-8')
    else:
        f = open(path, 'r', encoding='utf-8')
        
    try:
        for line in f:
            if line.strip():
                yield json.loads(line)
    finally:
        f.close()
