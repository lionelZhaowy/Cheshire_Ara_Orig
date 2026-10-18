#!/usr/bin/env python3
"""Rasterize final-PPT-derived SVGs and the requested routing review crops."""
import argparse
from pathlib import Path
from lxml import etree as E
import cairosvg

CROPS={
    'gb-acquisition-detail':(1370,470,1750,245),
    'emmc-detail':(2240,635,1360,205),
    'f1-f2-return-detail':(2110,1160,960,180),
    'legend-corridor-detail':(2865,765,480,480),
    'm5-return-detail':(2230,980,800,240),
    'isp-crossings-detail':(2680,545,95,85),
    'emmc-crossings-detail':(2915,660,125,65),
}

def render(directory):
    p=directory/'slide-08.svg';assert not p.with_suffix('.png').exists()
    cairosvg.svg2png(url=str(p),write_to=str(p.with_suffix('.png')))
    for name,(x,y,w,h) in CROPS.items():
        root=E.parse(str(p));s=root.getroot();s.set('viewBox',f'{x} {y} {w} {h}')
        scale=4 if 'crossings' in name else 1;s.set('width',str(w*scale));s.set('height',str(h*scale))
        q=directory/(name+'.svg');assert not q.exists();root.write(str(q),encoding='utf-8',xml_declaration=True)
        cairosvg.svg2png(url=str(q),write_to=str(q.with_suffix('.png')))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--preview-dir',type=Path,required=True);a=p.parse_args();render(a.preview_dir)
