"""Operating characteristics of the frozen stopping rule (prereg section 5). Usage: python3 scripts/power_sim.py"""
import random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze as a

def sim(p, cap=a.BATCH_CAP, sims=600, seed=5):
    r, rej = random.Random(seed), 0
    for _ in range(sims):
        s = n = 0
        for _b in range(cap):
            s += sum(r.random() < p for _ in range(10)); n += 10
            if a.e_value(s, n) >= a.E_REJECT:
                rej += 1; break
    return rej / sims

for p in (0.05, 0.10, 0.15, 0.20, 0.30):
    print(f"true rate {p:.2f}: P(reject H0 within {a.BATCH_CAP} batches) = {sim(p):.3f}")
