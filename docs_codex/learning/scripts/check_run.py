#!/usr/bin/env python3
"""Validate an actual run log; it does not create or imply execution evidence."""
import argparse,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('log',type=Path);p.add_argument('--stage',required=True,choices=['hello','array','mmio','timer','dma','rvv']);p.add_argument('--depth',action='store_true',help='require extended RVV result markers');a=p.parse_args()
if a.depth and a.stage!='rvv':p.error('--depth requires --stage rvv')
s=a.log.read_text(errors='replace')
checks={
 'VIP completion': '[JTAG] SUCCESS' in s,
 'software result': bool(re.search(r'\[UART\].*LEARN sum='+('0' if a.stage=='hello' else '28085')+r' errors=0\b',s)),
 'no reported simulation failure': not re.search(r'\*\*\s+(?:Error|Fatal)|\bFAILED:|\b(?:Error|Fatal)-\[|\$fatal|\bLEARN.*errors=[1-9]',s),
 'right stage': bool(re.search(r'\[UART\].*LEARN stage='+str(['hello','array','mmio','timer','dma','rvv'].index(a.stage))+r' Hello Cheshire!',s)),
}
if a.stage in ['timer','dma','rvv']:
 checks['stage marker']={'timer':'timer ticks>=8','dma':'DMA copied=548','rvv':'RVV checked=137'}[a.stage] in s
if a.depth:
 checks['RVV reduction'] = bool(re.search(r'\[UART\].*RVV_REDUCE n=137 sum=28085\b',s))
 checks['RVV edge cases'] = bool(re.search(r'\[UART\].*RVV_DEPTH cases=6 errors=0\b',s))
 checks['no depth errors'] = not re.search(r'RVV_DEPTH.*errors=[1-9]',s)
for name,ok in checks.items():print(('PASS' if ok else 'FAIL')+': '+name)
raise SystemExit(0 if all(checks.values()) else 1)
