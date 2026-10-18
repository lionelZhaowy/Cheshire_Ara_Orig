#!/usr/bin/env python3
"""Render the PPT-derived SVG and review crops (not an Office screenshot)."""
import argparse
from pathlib import Path
from lxml import etree as E
import cairosvg

CROPS={
    'image-input-detail':(2210,210,1390,510),
    'config-detail':(30,1660,1750,360),
    'config-pll-detail':(30,1695,3300,330),
    'storage-output-detail':(1780,1190,1820,620),
    'gb-input-detail':(1040,210,2300,520),
    'tx-external-detail':(2990,1585,610,225),
    'f2-crossing-detail':(2665,548,110,95),
}

def render(directory):
    p=directory/'slide-07.svg'
    assert not p.with_suffix('.png').exists()
    cairosvg.svg2png(url=str(p),write_to=str(p.with_suffix('.png')))
    for name,(x,y,w,h) in CROPS.items():
        root=E.parse(str(p));s=root.getroot();s.set('viewBox',f'{x} {y} {w} {h}')
        scale=4 if name=='f2-crossing-detail' else 1
        s.set('width',str(w*scale));s.set('height',str(h*scale))
        q=directory/(name+'.svg');assert not q.exists()
        root.write(str(q),encoding='utf-8',xml_declaration=True)
        cairosvg.svg2png(url=str(q),write_to=str(q.with_suffix('.png')))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--preview-dir',type=Path,required=True);a=p.parse_args();render(a.preview_dir)
