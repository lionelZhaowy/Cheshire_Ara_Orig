"""Export A to a new explicit directory, preserving existing decks and evidence."""
from pathlib import Path
import argparse, subprocess, sys
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out-dir',type=Path,required=True)
args=parser.parse_args()
out=args.out_dir.resolve()
if out.exists() and any(out.iterdir()):parser.error('Output directory must be empty')
command=[sys.executable,str(Path.home()/'.codex/skills/svg-pptx-diagrams-native/scripts/run.py'),'--input',*map(str,sorted((ROOT/'A').glob('*.svg'))),'--out-dir',str(out),'--aspect','source']
raise SystemExit(subprocess.run(command).returncode)
