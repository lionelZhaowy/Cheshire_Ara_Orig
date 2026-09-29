#!/usr/bin/env python3
"""Require explicit TB success and no errors, independent of simulator exit behavior."""
import pathlib,re,sys
s=pathlib.Path(sys.argv[1]).read_text(errors='replace')
m=re.search(r'HW_UNIT_PASS checks=(\d+)',s)
if not m or int(m[1])<35 or re.search(r'HW_UNIT_FAIL|\*\* (?:Error|Fatal)',s):
 raise SystemExit('FAIL: inspect '+sys.argv[1])
print(m[0])
