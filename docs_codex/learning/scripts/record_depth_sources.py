#!/usr/bin/env python3
"""Record current local inputs; this is provenance, never a runtime test."""
from pathlib import Path
import re,json,hashlib,subprocess
ROOT=Path(__file__).resolve().parent.parent
REPO=ROOT.parent.parent
files=set()
for page in (ROOT/'content').glob('*.html'):
 files.update(re.findall(r'href="../../([^"#]+)',page.read_text()))
files.update(['sw/include/util.h','sw/lib/crt0.S','sw/link/spm.ld','sw/link/dram.ld','sw/link/common.ldh','sw/lib/dif/uart.c','sw/lib/dif/clint.c','docs_codex/learning/examples/journey.c','docs_codex/learning/examples/rvv_add.S','docs_codex/learning/scripts/build_journey.sh'])
files.update(str(p.relative_to(REPO)) for p in (ROOT/'examples').glob('rvv_*'))
files.update(['Bender.yml','Bender.lock','hw/bootrom/cheshire_bootrom.S'])
manifest={'date':'2026-09-29','head':subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),'scope':'Local references and example inputs; static provenance, not execution evidence','files':{f:hashlib.sha256((REPO/f).read_bytes()).hexdigest() for f in sorted(files) if (REPO/f).is_file()}}
(ROOT/'evidence/depth-20260929-sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(f'Recorded {len(manifest["files"])} local source/reference hashes')
