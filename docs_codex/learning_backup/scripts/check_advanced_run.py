#!/usr/bin/env python3
"""Validate one actual JTAG-preloaded advanced log; synthetic tests are not RTL evidence."""
import argparse,re
from pathlib import Path
STAGES=['gpio','timer','capstone','eeprom','flash']
def check(s,stage):
    n=STAGES.index(stage)+1
    checks={'VIP JTAG completion':'[JTAG] SUCCESS' in s,
            'no blocked/failure':not re.search(r'\*\*\s+(?:Error|Fatal)|\b(?:Error|Fatal)-\[|\$fatal|\bFAILED\b|\bBLOCKED\b|\bQUARANTINED\b|\bADV FAIL|errors=[1-9]',s)}
    if n<=3:
        m=re.search(r'\[UART\].*ADV stage='+str(n)+r' gpio=(\d+) timer=(\d+) errors=(\d+)\b',s)
        checks['correct stage and result']=bool(m and int(m[1])>=1 and (int(m[2])==0 if n==1 else int(m[2])>=2) and int(m[3])==0)
    else:
        checks['correct stage, length and data']=bool(re.search(r'\[UART\].*STORAGE stage='+str(n)+r' bytes=16 errors=0\b',s))
    return checks
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('log',type=Path);p.add_argument('--stage',required=True,choices=STAGES);a=p.parse_args()
    result=check(a.log.read_text(errors='replace'),a.stage)
    for k,v in result.items():print(('PASS'if v else 'FAIL')+': '+k)
    raise SystemExit(0 if all(result.values())else 1)
