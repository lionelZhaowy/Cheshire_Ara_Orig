"""Reuse all current browser checks and add the five reviewed title locations.
The shared maintenance script is read, never edited.
"""
from pathlib import Path
import sys
repo=Path(__file__).resolve().parents[3]
script=repo/'docs_codex/learning/scripts/preview_structure_site.py'
source=script.read_text()
old="('configuration','case-irq-router')]:"
new="('configuration','case-irq-router'),('accelerators','control-registers'),('stream-io','vga-registers'),('vector','implementation'),('sharing','cpu-ara-mechanism'),('traps','local-handler')]:"
assert source.count(old)==1
sys.path.insert(0,str(script.parent))
exec(compile(source.replace(old,new),str(script),'exec'),{'__name__':'__main__','__file__':str(script)})
