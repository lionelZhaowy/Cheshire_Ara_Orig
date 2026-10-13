#!/usr/bin/env python3
"""Render local SVG previews and flat contact sheets (CairoSVG + Pillow)."""
import argparse
import json
from pathlib import Path
import cairosvg
from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    rows = json.loads((args.directory/'export_report.json').read_text())['figures']
    targets = [args.directory/(r['name']+'.png') for r in rows]
    targets += [args.directory/f'contact-{n+1:02d}.png' for n in range((len(rows)+8)//9)]
    if any(p.exists() for p in targets):
        parser.error('Refusing to overwrite existing previews')
    for row in rows:
        cairosvg.svg2png(url=str(args.directory/(row['name']+'.svg')),
                        write_to=str(args.directory/(row['name']+'.png')),
                        background_color='white')
    for offset in range(0, len(rows), 9):
        sheet = Image.new('RGB', (1500, 1200), '#edf1f5')
        draw = ImageDraw.Draw(sheet)
        for n, row in enumerate(rows[offset:offset+9]):
            im = Image.open(args.directory/(row['name']+'.png')).convert('RGB')
            im.thumbnail((480, 370))
            x, y = (n % 3)*500+10, (n // 3)*400+27
            sheet.paste(im, (x, y))
            draw.text((x, y-19), f'{offset+n+1:02d}: '+row['name'], fill='#18364d')
        sheet.save(args.directory/f'contact-{offset//9+1:02d}.png')
    print(f'Rendered {len(rows)} full-size PNGs and {(len(rows)+8)//9} contact sheets')


if __name__ == '__main__':
    main()
