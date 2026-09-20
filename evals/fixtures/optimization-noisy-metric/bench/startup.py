import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cli import initialize


samples = []
for _ in range(7):
    started = time.perf_counter()
    initialize()
    samples.append((time.perf_counter() - started) * 1000)
print(f"median_ms={statistics.median(samples):.3f}")
print(f"spread_ms={max(samples) - min(samples):.3f}")
