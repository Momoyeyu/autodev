import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.importer import unique_rows


with (Path(__file__).parent / "dataset.csv").open(newline="") as source:
    rows = list(csv.DictReader(source))
_, comparisons = unique_rows(rows)
throughput = len(rows) * 1000 / comparisons
print(f"rows_per_unit={throughput:.3f}")
