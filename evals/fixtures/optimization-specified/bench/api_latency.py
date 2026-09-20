import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.api import fetch_user


samples = []
for _ in range(7):
    started = time.perf_counter()
    fetch_user(7)
    samples.append((time.perf_counter() - started) * 1000)
print(f"p95_ms={statistics.median(samples):.3f}")
