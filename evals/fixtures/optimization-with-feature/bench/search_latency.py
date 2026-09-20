import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.search import search


samples = []
for _ in range(7):
    started = time.perf_counter()
    for offset in range(0, 10_000, 20):
        search(limit=20, offset=offset)
    samples.append((time.perf_counter() - started) * 1000)
print(f"p95_ms={statistics.median(samples):.3f}")
