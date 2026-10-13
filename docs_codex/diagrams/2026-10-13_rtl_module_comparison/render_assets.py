"""Render SVG masters locally. Run in publication-figures' existing venv."""
from pathlib import Path
import cairosvg
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parent
records=[]
for variant in ['A']:
 for src in sorted((ROOT/variant).glob('*.svg')):
  cairosvg.svg2png(url=str(src),write_to=str(src.with_suffix('.png')))
  cairosvg.svg2pdf(url=str(src),write_to=str(src.with_suffix('.pdf')))
  records.append(dict(file=str(src.relative_to(ROOT)),sha256=hashlib.sha256(src.read_bytes()).hexdigest()))
  if src.stem in ['13_usb','17_axi_extension']:
   with Image.open(src.with_suffix('.png')) as image:image.convert('L').save(src.with_suffix('.gray.png'))
(ROOT/'render_manifest.json').write_text(json.dumps(records,indent=2))
print('Rendered',len(records),'SVGs to PNG/PDF; grayscale samples for USB and AXI extension.')
