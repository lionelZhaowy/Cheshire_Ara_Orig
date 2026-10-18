"""Rasterize the current PPT-derived v1 SVG; never overwrite existing outputs."""
from pathlib import Path
import argparse
import cairosvg
from lxml import etree as E

CROPS = {
    'title-core': (0, 0, 3150, 720),
    'gb-capture': (1370, 240, 1750, 520),
    'storage-roi': (2100, 750, 1500, 1275),
    'controls': (0, 1400, 2160, 625),
    'xbar-emmc': (0, 670, 3600, 550),
}

parser = argparse.ArgumentParser()
parser.add_argument('--svg', type=Path, required=True)
parser.add_argument('--out-dir', type=Path, required=True)
args = parser.parse_args()
args.out_dir.mkdir(parents=True, exist_ok=False)
cairosvg.svg2png(url=str(args.svg), write_to=str(args.out_dir / 'soc-architecture-v1.png'))
for name, (x, y, w, h) in CROPS.items():
    root = E.parse(str(args.svg))
    node = root.getroot()
    node.set('viewBox', f'{x} {y} {w} {h}')
    node.set('width', str(w))
    node.set('height', str(h))
    cairosvg.svg2png(bytestring=E.tostring(root), write_to=str(args.out_dir / (name + '.png')))
