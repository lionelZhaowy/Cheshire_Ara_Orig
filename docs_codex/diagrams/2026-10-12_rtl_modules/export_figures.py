"""Export a new combined 20-figure deck; never overwrite an existing export."""
from pathlib import Path
import argparse
import subprocess
import sys

OUT=Path(__file__).resolve().parent
SKILL=Path('/home/zhaowenyao/.codex/skills/publication-figures')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out-dir',type=Path,default=OUT/'export')
    a=p.parse_args()
    old=OUT.parent/'2026-10-12_regbus_ip_integration'
    sources=[old/'01_regbus_whole.svg',old/'02_ip_register_contract.svg']+sorted(OUT.glob('*.svg'))
    cmd=[sys.executable,str(SKILL/'scripts/run.py'),'--input',*map(str,sources),
         '--out-dir',str(a.out_dir),'--width-mm','280','--min-font-pt','9','--render',
         '--font-file','/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc']
    raise SystemExit(subprocess.call(cmd))


if __name__=='__main__': main()
