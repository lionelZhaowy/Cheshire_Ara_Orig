#!/usr/bin/env python3
"""Render new SVG previews; requires CairoSVG and Pillow. Refuses overwrite."""
import argparse,json
from pathlib import Path
import cairosvg
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);a=p.parse_args()
figs=json.loads((a.directory/'source_inventory.json').read_text())['figures']
for f in figs:
 out=a.directory/(f['name']+'.png');assert not out.exists(),out
 cairosvg.svg2png(url=str(a.directory/(f['name']+'.svg')),write_to=str(out))
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
for start in range(0,len(figs),3):
 sheet=Image.new('RGB',(1500,915*3),'#EDEFF2');d=ImageDraw.Draw(sheet)
 for i,f in enumerate(figs[start:start+3]):
  im=Image.open(a.directory/(f['name']+'.png')).convert('RGB');im.thumbnail((1460,835))
  d.text((25,i*915+20),f['name'],font=font,fill='#29292D')
  sheet.paste(im,((1500-im.width)//2,i*915+63))
 out=a.directory/f'contact-{start//3+1:02}.png';assert not out.exists();sheet.save(out)
print('Rendered',len(figs),'previews and 3 contact sheets')
