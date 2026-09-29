#!/usr/bin/env python3
"""Validate an actual run log; it does not create or imply execution evidence."""
import argparse,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('log',type=Path);p.add_argument('--stage',required=True,choices=['hello','array','mmio','timer','dma','rvv']);a=p.parse_args()
s=a.log.read_text(errors='replace')
checks={
 'VIP completion': '[JTAG] SUCCESS' in s,
 'software result': bool(re.search(r'\[UART\].*LEARN sum='+('0' if a.stage=='hello' else '28085')+r' errors=0\b',s)),
 'no reported simulation failure': not re.search(r'\*\*\s+(?:Error|Fatal)|\bFAILED:|\b(?:Error|Fatal)-\[|\$fatal|\bLEARN.*errors=[1-9]',s),
 'right stage': bool(re.search(r'\[UART\].*LEARN stage='+str(['hello','array','mmio','timer','dma','rvv'].index(a.stage))+r' Hello Cheshire!',s)),
}
if a.stage in ['timer','dma','rvv']:
 checks['stage marker']={'timer':'timer ticks>=8','dma':'DMA copied=548','rvv':'RVV checked=137'}[a.stage] in s
for name,ok in checks.items():print(('PASS' if ok else 'FAIL')+': '+name)
raise SystemExit(0 if all(checks.values()) else 1)
