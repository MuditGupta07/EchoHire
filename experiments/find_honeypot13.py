import json
import math

nans = 0
infs = 0

with open('candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        s = c.get('redrob_signals', {})
        for k, v in s.items():
            if isinstance(v, float):
                if math.isnan(v):
                    nans += 1
                if math.isinf(v):
                    infs += 1

print(f"NaNs: {nans}, Infs: {infs}")
