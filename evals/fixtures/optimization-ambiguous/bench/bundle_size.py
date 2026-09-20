import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.home import render_home


print(len(render_home("Ada").encode()))
