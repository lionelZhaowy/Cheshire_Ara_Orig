#!/usr/bin/env python3
"""Export the six redraw groups with the bundled, self-contained skill snapshot."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    here=Path(__file__).resolve().parent
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=here.parent)
    ap.add_argument('--font-file',type=Path,default=Path('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'))
    args=ap.parse_args()
    data=json.loads((here/'manifest.json').read_text())
    script=here/'skill/publication-figures/scripts/svg_to_pptx.py'
    for name,figures in data.items():
        folder=args.root/(name+'_new')
        command=[sys.executable,str(script),'--input',*[str(folder/(f['name']+'.svg')) for f in figures],
                 '--out-dir',str(folder/'export'),'--width-mm','182','--min-font-pt','9','--render','--font-file',str(args.font_file)]
        p=subprocess.run(command,capture_output=True,text=True)
        if p.returncode:
            print(p.stdout+p.stderr,file=sys.stderr); raise SystemExit(p.returncode)
        report=json.loads((folder/'export/export_report.json').read_text())
        print(name,':',len(report['figures']),'figures, min font',round(min(x['min_text_pt'] for x in report['figures']),2),'pt')


if __name__=='__main__': main()
