#!/usr/bin/env python3
"""Five-stage application timeline; export uses the installed native SVG backend."""
from pathlib import Path
from xml.sax.saxutils import escape
import json
D=Path(__file__).resolve().parent
W,H=1600,900
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
'<defs><marker id="next" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="#314D66"/></marker></defs>',
f'<rect x="0" y="0" width="{W}" height="{H}" fill="#FFFFFF" stroke="none"/>']
layout={'name':'timeline-simple','canvas':[W,H],'boxes':{},'arrows':[]}
def text(x,y,s,size=25,bold=False,owner=None):
 attr=f' data-owner="{owner}"' if owner else ''
 parts.append(f'<text x="{x}" y="{y}" font-family="WenQuanYi Zen Hei" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="middle" fill="#29292D"{attr}>{escape(s)}</text>')
text(800,53,'一次推理的两次数据交接',36,True)
nodes=[
 ('CPU／Ara 准备输入',['计算结束，交出输入与输出范围'],'#F1D7D9'),
 ('交接前同步',['先排空旧事务，再清理输入、清理并失效输出','确认设备端口可见，允许启动搬运'],'#E8DFED'),
 ('设备执行',['DDR → GB → NPU 计算 → 结果从 GB 写回 DDR'],'#D9EEE8'),
 ('交回 CPU 前同步',['确认写回成功且 CPU 端口可见','处理相关回填，再失效 L1D／LLC 输出副本'],'#E8DFED'),
 ('CPU 读取结果并后处理',['同步成功后重新取得输出使用权'],'#F1D7D9')]
for i,(title,lines,color) in enumerate(nodes):
 y=100+i*144;owner=f'stage-{i+1}';b=dict(x=180,y=y,width=1240,height=112);layout['boxes'][owner]=b
 parts.append(f'<rect id="{owner}" x="180" y="{y}" width="1240" height="112" fill="{color}" stroke="#29292D" stroke-width="1.7"/>')
 text(800,y+35,title,29,True,owner)
 for j,line in enumerate(lines):text(800,y+(80 if len(lines)==1 else 68+j*30),line,25,False,owner)
 if i<4:
  points=[[800,y+112],[800,y+144]];eid=f'next-{i+1}';layout['arrows'].append({'id':eid,'points':points})
  parts.append(f'<line id="{eid}" x1="800" y1="{y+112}" x2="800" y2="{y+144}" stroke="#314D66" stroke-width="2.8" marker-end="url(#next)"/>')
text(800,850,'箭头表示先后顺序；每个阶段成功后才进入下一阶段。',24)
parts.append('</svg>')
(D/'figures/timeline-simple.svg').write_text('\n'.join(parts)+'\n')
(D/'figures/layout.json').write_text(json.dumps([layout],ensure_ascii=False,indent=2)+'\n')
