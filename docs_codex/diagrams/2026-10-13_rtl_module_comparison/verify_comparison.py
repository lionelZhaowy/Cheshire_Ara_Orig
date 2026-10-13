"""Compatibility entry: checks current A only; old A/B checker is archived."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('verify_a.py')), run_name='__main__')
