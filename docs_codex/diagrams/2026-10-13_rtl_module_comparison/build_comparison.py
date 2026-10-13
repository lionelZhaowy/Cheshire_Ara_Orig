"""Generate the adopted A diagrams and guide navigation. B/C are historical only."""
from pathlib import Path
from html import escape
import importlib.util
import json, math, re, copy, hashlib

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
BASE=ROOT.parent/'2026-10-12_rtl_modules'
FONT='WenQuanYi Zen Hei'
INK='#23354B'; DATA='#28699B'; CTRL='#9C5B25'; IRQ='#765096'
GRAPHS={}

def module(path,name):
 s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

class Record:
 def __init__(self,name,title='',height=980):
  self.name=name;self.height=height;self.title=title;self.items=[];self.nodes=[];self.edges=[];self.texts=[];self.zones=[]
  self.text(40,49,title,32) if title else None
 def text(self,x,y,value,size=24,color=INK,anchor='start'):
  a=dict(type='text',x=x,y=y,text=value,size=size,color=color,anchor=anchor);self.items.append(a);self.texts.append(a)
 def rect(self,x,y,w,h,fill='#FFFFFF',stroke=INK,dash=False,**kw):
  self.items.append(dict(type='rect',x=x,y=y,w=w,h=h,fill=fill,stroke=stroke,dash=dash))
 def box(self,x,y,w,h,lines,fill='#EAF1F8',memory=False):
  n=dict(id=f'N{len(self.nodes)+1:02}',x=x,y=y,w=w,h=h,lines=lines,fill=fill,memory=memory)
  self.nodes.append(n);self.items.append(dict(type='box',node=n))
 def arrow(self,points,color=DATA,dash=False,both=False):
  e=dict(id=f'E{len(self.edges)+1:02}',points=points,color=color,dash=dash,both=both)
  self.edges.append(e);self.items.append(dict(type='edge',edge=e))
 def line(self,points,color=DATA,dashed=False,arrow=True,width=2.4): self.arrow(points,color,dashed)
 def ctl(self,points,color=CTRL):self.arrow(points,color,True)
 def dot(self,x,y,color=DATA):self.items.append(dict(type='dot',x=x,y=y,color=color))
 def zone(self,x,y,w,h,label):
  self.zones.append(dict(x=x,y=y,w=w,h=h,label=label));self.rect(x,y,w,h,stroke='#9DAABA',dash=False);self.text(x+15,y+30,label,23,'#56697F')
 def save(self,name=None):
  if name:self.name={'01_regbus_whole':'00a_regbus','02_ip_register_contract':'00b_ip_contract'}.get(name,name)
  GRAPHS[self.name]=self

def capture():
 m=module(BASE/'build_figures.py','baseline');m.Figure=Record
 for f in ['uart','i2c','spi','gpio','plic','clint','clic','router','bootrom','socregs','jtag','serial','vga','usb','idma','traps','llc','spm']:getattr(m,f)()
 # Keep the old Regbus arrangement, substituting only its drawing primitives.
 old=module(ROOT.parent/'2026-10-12_regbus_ip_integration/build_figures.py','regbaseline')
 source=(ROOT.parent/'2026-10-12_regbus_ip_integration/build_figures.py').read_text()
 source='\n'.join(line for line in source.splitlines() if 'f.items[-1]=' not in line)
 exec(compile(source,old.__file__,'exec'),old.__dict__)
 old.canvas=lambda h: Record('',height=h)
 old.bus=lambda f,p:f.arrow(p,both=True)
 old.whole();old.endpoint()
 for name in ['00a_regbus','00b_ip_contract']:
  f=GRAPHS[name];f.title=f.texts[0]['text']
  # These two old blocks were drawn as a rectangle plus free text; promote to
  # semantic nodes without changing their visual content/position.
  area=(1380,805,350,120) if name=='00a_regbus' else (1470,280,290,415)
  x,y,w,h=area
  texts=[t for t in f.texts if x<=t['x']<=x+w and y<=t['y']<=y+h]
  n=dict(id=f'N{len(f.nodes)+1:02}',x=x,y=y,w=w,h=h,lines=[t['text'] for t in texts],fill='#EDF5EB',memory=False,status='planned',virtual=True)
  f.nodes.append(n)
 return GRAPHS

# External ports retain their real functional meaning; no implied device is added.
PORTS={
 '01_uart':{(1730,450):'UART TX 输出',(1730,710):'UART RX 输入',(182,580):'SoC UART IRQ'},
 '06a_clint':{(65,300):'rtc_i',(1720,420):'MTIP / timer_irq_o',(65,665):'Regbus 32',(1720,725):'MSIP / ipi_o'},
 '07_irq_router':{(1415,225):'target 0 → PLIC',(1415,275):'target 1… → hart CLIC',(1415,325):'后续 target → 外部 IRQ'},
 '08_bootrom':{(50,330):'Regbus 32'},
 '10_jtag_debug':{(1720,860):'主 AXI：AxiIn.dbg',(40,690):'主 AXI：AxiOut.dbg'},
 '11_serial_link':{(1485,870):'链路 DDR 引脚'},
 '12_vga':{(1720,265):'RGB / HS / VS 引脚',(1720,860):'系统 AXI AR',(1720,710):'系统 AXI R'},
 '13_usb':{(55,665):'主 AXI：AxiIn.usb',(1570,255):'SoC USB IRQ',(1570,880):'DP / DM / OE 引脚'},
 '14_idma':{(55,675):'主 AXI：AxiIn.dma'},
 '15_interrupt_exception':{(60,665):'处理程序取指（逻辑结果）'},
 '16b_spm':{(1420,515):'同一组 data SRAM（way 0…3 示例）'},
 '05_plic':{(1535,470):'xeip → hart'},
 '04_gpio':{(1720,620):'GPIO PAD 输出值',(1720,760):'GPIO PAD 输出使能'},
 '00b_ip_contract':{(45,390):'Regbus 请求',(45,655):'Regbus 响应',(1215,772):'W1C 写清除使能'},
}

def on_segment(p,a,b):
 return (a[0]==b[0]==p[0] and min(a[1],b[1])<=p[1]<=max(a[1],b[1])) or (a[1]==b[1]==p[1] and min(a[0],b[0])<=p[0]<=max(a[0],b[0]))

def resolve(f,e,end,seen=()):
 p=e['points'][0 if end=='source' else -1]
 candidates=[n for n in f.nodes if not n.get('port') and n['x']-12<=p[0]<=n['x']+n['w']+12 and n['y']-12<=p[1]<=n['y']+n['h']+12 and not n.get('port')]
 if candidates:return min(candidates,key=lambda n:n['w']*n['h'])['id']
 for other in f.edges:
  if other is e or other['id'] in seen:continue
  if any(on_segment(p,a,b) for a,b in zip(other['points'],other['points'][1:])):
   return resolve(f,other,'source',seen+(e['id'],))
 title=PORTS.get(f.name,{}).get(tuple(p))
 if not title:
  # Unknown endpoints must be reviewed, never silently called an AXI connection.
  title='待核对端点 '+str(p)
 existing=next((n for n in f.nodes if n.get('port_position')==p),None)
 if existing:return existing['id']
 n=dict(id=f'P{len([n for n in f.nodes if n.get("port")])+1:02}',lines=[title],port=True,port_position=p,kind='boundary',fill='#FFFFFF')
 f.nodes.append(n);return n['id']

def resolve_all():
 for f in GRAPHS.values():
  for e in f.edges:
   e['source']=resolve(f,e,'source');e['target']=resolve(f,e,'target')


class SVG:
 def __init__(self,w,h):
  self.w=w;self.h=h;self.items=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'];self.labels=[];self.boxes=[]
  colors=[INK,DATA,CTRL,IRQ,'#314D66','#765489','#187C78','#B96043','#205F9C','#925021','#253447']
  self.items.append('<defs>')
  for c in colors:self.items.append(f'<marker id="m{c[1:]}" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="{c}"/></marker>')
  self.items.append('</defs>');self.rect(0,0,w,h,'#FFFFFF','none')
 def rect(self,x,y,w,h,fill='#FFFFFF',stroke=INK,dash=False,width=1.7):
  d=' stroke-dasharray="8 5"' if dash else ''
  self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"{d}/>')
 def text(self,x,y,text,size=24,color=INK,anchor='start',bold=False):
  weight=' font-weight="bold"' if bold else ''
  self.items.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{color}" text-anchor="{anchor}"{weight}>{escape(text)}</text>')
  # The actual font is used for bounding boxes when the skill venv runs this.
  try:
   from PIL import ImageFont
   font=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',int(size*4));w=font.getlength(text)/4
  except ImportError:w=sum(size*(1 if ord(c)>127 else .57) for c in text)
  left=x-w/2 if anchor=='middle' else x-w if anchor=='end' else x
  self.labels.append(dict(x=left,y=y-size,w=w,h=size*1.2,text=text))
 def line(self,p,color=DATA,dash=False,both=False,arrow=True,id=None):
  d=' stroke-dasharray="8 5"' if dash else '';markers=f' marker-end="url(#m{color[1:]})"' if arrow else ''
  if both:markers+=f' marker-start="url(#m{color[1:]})"'
  ident=f' id="{id}"' if id else ''
  self.items.append(f'<polyline{ident} points="{" ".join(f"{x},{y}" for x,y in p)}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linejoin="miter"{d}{markers}/>')
 def box(self,n):
  x,y,w,h=[n[k] for k in ['x','y','w','h']];self.rect(x,y,w,h,n.get('fill','#EAF1F8'),dash=n.get('status') in ['planned','tbd'])
  self.boxes.append(dict(x=x,y=y,w=w,h=h,id=n['id']))
  if n.get('memory'):self.line([(x+12,y),(x+12,y+h)],INK,arrow=False)
  lines=n['lines'];top=y+h/2-(len(lines)-1)*16+8
  for i,line in enumerate(lines):self.text(x+w/2,top+i*32,line,24 if i==0 else 22,anchor='middle')
 def save(self,path):path.write_text('\n'.join(self.items+['</svg>']))

def intersect(a,b,pad=0):return a['x']<b['x']+b['w']+pad and a['x']+a['w']+pad>b['x'] and a['y']<b['y']+b['h']+pad and a['y']+a['h']+pad>b['y']

def edge_label(svg,e,used):
 # Keep E labels separate from module text and existing captions. Each line has
 # its own stable ID; full signal names are in the shared interface table.
 segs=sorted(zip(e['points'],e['points'][1:]),key=lambda s:-(abs(s[0][0]-s[1][0])+abs(s[0][1]-s[1][1])))
 best=None
 for a,b in segs:
  for q in [.5,.3,.7,.15,.85]:
   x=a[0]+q*(b[0]-a[0]);y=a[1]+q*(b[1]-a[1])
   offsets=[(-25,-31),(-25,7)] if a[1]==b[1] else [(9,-14),(-58,-14)]
   for dx,dy in offsets:
    r=dict(x=x+dx,y=y+dy,w=49,h=27)
    collision=sum(intersect(r,t,3) for t in svg.labels+svg.boxes+used)
    score=collision*1000+abs(q-.5)*10
    if r['x']<8 or r['y']<70 or r['x']+49>svg.w-8:score+=10000
    if best is None or score<best[0]:best=(score,r)
 r=best[1];used.append(r)
 svg.rect(r['x'],r['y'],49,27,'#FFFFFF','none');svg.text(r['x']+24.5,r['y']+21,e['id'],22,e['color'],anchor='middle',bold=True)
 return dict(edge=e['id'],**r,placement_score=best[0])

def render_a(f,path):
 svg=SVG(1800,f.height+60)
 for it in f.items:
  t=it['type']
  if t=='text':svg.text(it['x'],it['y'],it['text'],it['size'],it['color'],it['anchor'])
  elif t=='rect':svg.rect(it['x'],it['y'],it['w'],it['h'],it['fill'],it['stroke'],it['dash'])
  elif t=='box':svg.box(it['node'])
  elif t=='edge':
   e=it['edge'];svg.line(e['points'],e['color'],e['dash'],e['both'],id=e['id'])
  elif t=='dot':svg.items.append(f'<circle cx="{it["x"]}" cy="{it["y"]}" r="4" fill="{it["color"]}"/>')
 used=[];placements=[edge_label(svg,e,used) for e in f.edges]
 y=f.height+20
 svg.text(40,y,'E 编号对应图下连接表；总线双箭头合并请求/响应；单箭头含义以表为准。',22)
 svg.text(40,y+28,'虚线连线表示控制/事件；虚线模块表示规划。交叉无圆点不连接。A：连续走线。',22,'#56697F')
 svg.save(path)
 return dict(labels=svg.labels,boxes=svg.boxes,edge_labels=placements)

def new_figure(g):
 import heapq
 rows=math.ceil(len(g['nodes'])/3)
 f=Record(g['name'],g['title'],height=rows*290+170)
 caption=g.get('caption','')
 c_lines=[];line='';units=0
 for ch in caption:
  units+=1 if ord(ch)>127 else .55
  if units>74:c_lines.append(line);line='';units=0
  line+=ch
 if line:c_lines.append(line)
 for i,line in enumerate(c_lines):f.text(40,94+i*30,line,22,'#56697F')
 for i,n in enumerate(g['nodes']):
  x=60+(i%3)*590;y=180+(i//3)*290
  lines=n['lines']
  f.box(x,y,490,170,lines,{'control':'#E8F2EA','memory':'#F2EEF8','boundary':'#F8F0E6'}.get(n.get('kind'),'#EAF1F8'),n.get('kind')=='memory')
  f.nodes[-1].update(id=n['id'],kind=n.get('kind','data'),status=n.get('status','implemented'),group=n.get('group'))
 ns={n['id']:n for n in f.nodes}
 usage={};occupied={}
 def port(n,side,e):
  key=(n['id'],side);j=usage.get(key,0);usage[key]=j+1
  if side in ['L','R']:
   # Separate connection groups by port, so two protocols are not shorted.
   p=(n['x']+(n['w'] if side=='R' else 0),n['y']+40+(j%4)*30);q=(p[0]+(20 if side=='R' else -20),p[1])
  else:
   p=(n['x']+90+(j%4)*90,n['y']+(n['h'] if side=='B' else 0));q=(p[0],p[1]+(20 if side=='B' else -20))
  return p,q
 reserved=set()
 plans=[]
 for e in g['edges']:
  a,b=ns[e['source']],ns[e['target']]
  if abs(a['x']-b['x'])>50:s1,s2=('R','L') if a['x']<b['x'] else ('L','R')
  else:s1,s2=('B','T') if a['y']<b['y'] else ('T','B')
  p,q=port(a,s1,e);r,s=port(b,s2,e)
  plans.append((e,p,q,r,s));reserved.update([(q[0]//10,q[1]//10),(s[0]//10,s[1]//10)])
 def route(a,b):
  start=(a[0]//10,a[1]//10);end=(b[0]//10,b[1]//10)
  obstacles=set()
  for n in f.nodes:
   for xx in range((n['x']-10)//10,(n['x']+n['w']+10)//10+1):
    for yy in range((n['y']-10)//10,(n['y']+n['h']+10)//10+1):obstacles.add((xx,yy))
  todo=[(0,0,start,None)];best={(start,None):0};prev={};last=None
  while todo:
   _,cost,p,d=heapq.heappop(todo)
   if p==end:last=(p,d);break
   if cost>best.get((p,d),1e20):continue
   for di,(dx,dy) in enumerate([(1,0),(0,1),(-1,0),(0,-1)]):
    q=(p[0]+dx,p[1]+dy)
    if q in reserved and q not in [start,end]:continue
    if q in obstacles or not(2<=q[0]<=178 and 15<=q[1]<f.height//10-2):continue
    axis='H' if dx else 'V'
    if axis in occupied.get(q,set()) or axis in occupied.get(p,set()):continue
    nc=cost+1+(2 if d is not None and d!=di else 0)+(5 if q in occupied else 0)
    if nc<best.get((q,di),1e20):
     best[(q,di)]=nc;prev[(q,di)]=(p,d);heapq.heappush(todo,(nc+abs(q[0]-end[0])+abs(q[1]-end[1]),nc,q,di))
  if last is None:raise ValueError(('no route',f.name,a,b))
  ps=[]
  while last in prev:ps.append(last[0]);last=prev[last]
  ps.append(start);ps.reverse()
  for aa,bb in zip(ps,ps[1:]):
   axis='H' if aa[1]==bb[1] else 'V'
   occupied.setdefault(aa,set()).add(axis);occupied.setdefault(bb,set()).add(axis)
  points=[(x*10,y*10) for x,y in ps];simple=[points[0]]
  for i in range(1,len(points)-1):
   a0,b0,c0=points[i-1:i+2]
   if (b0[0]-a0[0],b0[1]-a0[1])!=(c0[0]-b0[0],c0[1]-b0[1]):simple.append(b0)
  simple.append(points[-1]);return simple
 for e,p,q,r,s in plans:
  pts=[p]+route(q,s)+[r]
  f.arrow(pts,IRQ if e.get('kind')=='irq' else CTRL if e.get('kind')=='control' else DATA,e.get('kind') in ['irq','control'],e.get('direction')=='both')
  f.edges[-1].update({k:v for k,v in e.items() if k not in ['id','direction']})
  if e.get('status') in ['planned','tbd']:f.edges[-1]['detail']='规划/待确认连接：'+e.get('detail',e.get('label',''))
 f.save();return f

def apply_review():
 reviews={}
 for name in ['review_00_07.json','review_08_16.json']:
  reviews.update(json.loads((ROOT/name).read_text())['figures'])
 for name,f in GRAPHS.items():
  review=reviews[name];assert len(review['edges'])==len(f.edges),(name,len(review['edges']),len(f.edges))
  for e,d in zip(f.edges,review['edges']):
   e['detail']=d['label'] if isinstance(d,dict) else d
  f.review=review
 def n(name,id):return next(n for n in GRAPHS[name].nodes if n['id']==id)
 def edge(name,id):return next(e for e in GRAPHS[name].edges if e['id']==id)
 def txt(name,old,new):
  for t in GRAPHS[name].texts:
   if old in t['text']:t['text']=t['text'].replace(old,new)
 def add(name,source,target,pts,detail,both=False,color=CTRL):
  f=GRAPHS[name];f.arrow(pts,color,color!=DATA,both);f.edges[-1].update(source=source,target=target,detail=detail,reviewed_addition=True)
 def both(name,ids):
  for id in ids:edge(name,id)['both']=True
 # Explicitly distinguish an enabled RTL block from a proposal / disabled branch.
 for name,id in [('13_usb','N01'),('09_soc_regs','N01'),('04_gpio','N01'),('05_plic','N01'),('14_idma','N01'),('10_jtag_debug','N01')]:n(name,id)['kind']='boundary'
 n('00a_regbus','N08')['lines'].append('默认端口数为 0')
 n('00a_regbus','N08')['h']=145
 edge('00a_regbus','E09')['points'][0]=(1560,685)
 n('00b_ip_contract','N05')['kind']='data'
 n('06b_clic','N04')['kind']='boundary'
 for t in GRAPHS['00b_ip_contract'].texts:
  if t['text']=='offset / 访问属性':t['y']=499;t['x']=710
 for t in GRAPHS['05_plic'].texts:
  if t['text']=='claim / complete':t['x']=1030
  if t['text']=='Regbus 请求 / 响应':t['x']=740
 for nn in GRAPHS['00b_ip_contract'].nodes:nn['status']='planned'
 for item in GRAPHS['00a_regbus'].items:
  if item['type']=='rect' and item['x']==1380:item['dash']=True
 for item in GRAPHS['00b_ip_contract'].items:
  if item['type']=='rect' and item['x'] in [340,1470]:item['dash']=True
 edge('00b_ip_contract','E08')['points']=[(680,445),(680,520),(1215,520),(1215,625)]
 edge('00b_ip_contract','E08')['detail']='建议：地址/访问译码生成 W1C 清除使能，N01→N03；没有独立外部 W1C 端口。'
 txt('00b_ip_contract','合法 W1C 写生成清除使能','合法 W1C 写从访问译码生成清除使能')
 n('01_uart','N05')['lines']=['5  TX 保持 / 发送逻辑','iTSR + uart_transmitter','起始 / 数据 / 校验 / 停止']
 n('01_uart','N03')['lines']=['3  baudgen + 节拍逻辑','DLL / DLM → baud ticks']
 both('01_uart',['E12']);txt('01_uart','收发状态汇入中断逻辑','RX / 线路事件；TX 另有输入')
 add('01_uart','N04','N08',[(925,510),(925,550),(345,550),(345,865),(182,865),(182,800)],'TX FIFO/顶层控制派生 iTHRInterrupt → UART_IIC.THI；发送空事件。',color=IRQ)
 both('02_i2c',['E10'])
 txt('02_i2c','CONTROL / TIMING / FIFO reset','CONTROL / TIMING → FSM')
 txt('02_i2c','Target 队列的软件读写也经 reg_top；图中省略其回线。','FIFO reset 由 reg_top 直接作用队列；N08 汇总 FSM/FIFO 事件。')
 n('02_i2c','N08')['lines']=['8  事件整合 / prim_intr_hw','FSM / FIFO 状态锁存','15 路 IRQ → SoC']
 add('02_i2c','N01','N06',[(285,330),(285,725),(410,725)],'reg2hw.txdata → tx_fifo_wdata/wvalid；Target TX 队列由软件填充。',color=DATA)
 add('02_i2c','N07','N01',[(1040,785),(1040,860),(100,860),(100,330)],'acq_fifo_rdata → hw2reg.acqdata；软件读消费由 reg2hw 返回。',both=True,color=DATA)
 n('03_spi','N09')['lines'][-1]='SD[3:0] 输入 / 输出'
 txt('03_spi','SCK / CS 与移位节拍','移位 / 采样及 ready 反馈')
 both('03_spi',['E10'])
 add('03_spi','N03',None,[(805,215),(740,215),(740,110),(1700,110)],'sck_o/csb_o/sd_en_o：FSM 产生 SCK、片选和数据输出使能。')
 PORTS.setdefault('03_spi',{})[(1700,110)]='SPI SCK / CS / SD OE 引脚'
 GRAPHS['03_spi'].text(1260,92,'SCK / CS / SD OE → 引脚',22,CTRL)
 add('03_spi','N09',None,[(1690,505),(1755,505)],'sd_o[3:0]/sd_i[3:0]：移位逻辑输出数据、采样引脚数据。',both=True,color=DATA)
 PORTS['03_spi'][(1755,505)]='SPI SD[3:0] 数据引脚'
 both('04_gpio',['E04','E05','E10'])
 add('04_gpio','N02','N05',[(475,330),(475,565)],'data_in_d → hw2reg.data_in.d/de；CPU 回读采样输入。',color=DATA)
 add('04_gpio','N04',None,[(1545,180),(1545,110),(1730,110)],'intr_gpio_o[31:0] → intr.intn.gpio，进入 SoC IRQ 汇聚。',color=IRQ)
 PORTS['04_gpio'][(1730,110)]='SoC GPIO IRQ'
 GRAPHS['04_gpio'].text(1365,92,'intr_gpio_o → SoC',22,IRQ)
 n('05_plic','N01')['lines'][1]='IRQ Router 或旁路'
 add('05_plic','N03','N05',[(895,370),(895,580),(520,580),(520,655)],'ip → hw2reg.ip.d/de；pending 状态供软件回读。',color=DATA)
 n('06a_clint','N02')['lines']=['2  MTIME[63:0] 字段','reg_top 存储；可由软件写','RTC 沿使能自动加 1']
 n('06a_clint','N04')['lines']=['4  MTIMECMP[63:0] 字段','reg_top 内的比较值']
 n('06a_clint','N06')['lines']=['6  MSIP 字段','reg_top 内；软件写']
 n('06a_clint','N05')['lines'][0]='5  clint_reg_top 访问控制'
 n('06b_clic','N05')['lines']=['5  mclic_reg_top + clicint_reg_top × 源','Regbus 地址译码 → 对应寄存器','reg_adapter：整理 reg2hw / hw2reg 字段','全局 level 划分；每源 pending / enable / attr / ctl']
 n('06b_clic','N03')['lines']=['3  clic_target + 顶层整理','pending / enable','level / priority / mode','获胜源与 SHV / level 格式化']
 both('06b_clic',['E05'])
 txt('06b_clic','Cfg.Clic 控制生成','当前默认 / FPGA：Cfg.Clic = 0')
 txt('07_irq_router','Cfg.IrqRouter = 0 时：','当前默认 / FPGA 为 0；Cfg.IrqRouter = 0 时：')
 add('11_serial_link','N06','N04',[(950,620),(950,440),(1670,440),(1670,365)],'reg2hw.channel_alloc_*：通道使能/clear/flush/同步配置；仅 NumChannels>1。')
 both('11_serial_link',['E07'])
 n('12_vga','N04')['lines']=['4  splitter + 信用门控','axi_burst_splitter','顶层 credit / stream_join']
 # For stream edges, the table defines the forward payload and return ready.
 # Keep the original forward-data arrow convention to avoid treating ready as data.
 both('14_idma',['E04'])
 edge('14_idma','E08')['points']=[(1470,365),(1470,530),(795,530),(795,505)]
 edge('14_idma','E08')['detail']='2D retire：midend 的 idma_nd_rsp_valid & idma_nd_rsp_ready → transfer_id_gen；1D 配置则使用 backend 的 idma_rsp 握手。'
 edge('14_idma','E07')['detail']='issue：frontend → Job FIFO 入口 valid & ready；不是 midend 每派发一个一维子任务就 issue 新 ID。'
 n('14_idma','N04')['lines']=['3  Job FIFO + midend','入口握手 issue ID','2D：展开并汇总完成','1D：不生成 midend']
 n('15_interrupt_exception','N04')['lines']=['4  issue_stage','/ scoreboard','指令与结果关联','ex 随指令保存']
 add('15_interrupt_exception','N01','N03',[(215,165),(215,100),(1200,100),(1200,155)],'irq_i 直接输入译码；CLIC 经 clic_adapter 后为 clic_irq_req_id/cause_id。',color=IRQ)
 add('15_interrupt_exception','N05','N07',[(1470,670),(1390,670),(1390,775),(850,775),(850,710),(820,710)],'ex_commit.valid → controller.ex_valid_i / frontend.ex_valid_i，与 CSR trap 状态更新并行。',color=IRQ)
 edge('15_interrupt_exception','E08').update(dash=True,color=CTRL,kind='logical_effect')
 add('16a_llc','N01','N05',[(210,365),(210,535),(1360,535),(1360,605),(1395,605)],'to_llc_req.w/w_valid/wstrb → write_unit；to_llc_resp.r/b 返回原请求者。独立于 AW/AR 描述符处理。',both=True,color=DATA)
 edge('16b_spm','E03').update(dash=True,color=CTRL,kind='logical_selection')
 edge('16b_spm','E03')['detail']='逻辑分配关系：地址/way 选择决定使用哪组 SRAM；实际访问经过 merge → read/write → ways，见 LLC 图。不是 config 直接驱动 SRAM 数据口。'
 return reviews

DOCS={
 '00a_regbus':'00_regbus.md','00b_ip_contract':'00_regbus.md','06a_clint':'06_clint_clic.md','06b_clic':'06_clint_clic.md','16a_llc':'16_llc_spm.md','16b_spm':'16_llc_spm.md'
}

def graph_dict(f):
 nodes=[{k:v for k,v in n.items() if k not in ['x','y','w','h','fill','virtual','port_position']} for n in f.nodes]
 edges=[{k:v for k,v in e.items() if k not in ['points','color','dash']} for e in f.edges]
 return dict(name=f.name,title=f.title,doc=DOCS.get(f.name,f.name+'.md'),nodes=nodes,edges=edges,notes=[t['text'] for t in f.texts if t['size']<30])

def update_docs(graphs):
 docs=REPO/'docs_codex/rtl_modules'
 for doc in sorted(set(g['doc'] for g in graphs)):
  p=docs/doc;s=p.read_text()
  s=re.sub(r'\n<!-- CONNECTIONS:.*?<!-- /CONNECTIONS -->\n','\n',s,flags=re.S)
  gs=[g for g in graphs if g['doc']==doc]
  for g in gs:
   name=g['name'];old={'00a_regbus':'01_regbus_whole','00b_ip_contract':'02_ip_register_contract'}.get(name,name)
   prefix='../diagrams/'+ROOT.name
   image=f'![{g["title"]}]({prefix}/A/{name}.png)\n\n[SVG]({prefix}/A/{name}.svg) · [PDF]({prefix}/A/{name}.pdf) · [A 图总览](../diagrams/2026-10-13_rtl_module_comparison/index.html#{name})'
   pat=r'!\[[^\]]*\]\([^\n]*\/'+old+r'\.png\)\s*\n\s*\[SVG\][^\n]*'
   if re.search(pat,s):s=re.sub(pat,lambda _:image,s)
   elif 'FIGURE_PLACEHOLDER' in s:s=s.replace('FIGURE_PLACEHOLDER',image,1)
   elif f'/A/{name}.png' not in s:raise ValueError(('missing figure position',doc,name))
   ns={n['id']:n for n in g['nodes']}
   def title(id):return ns[id]['lines'][0].replace('|','\\|')
   block=f'\n\n<!-- CONNECTIONS:{name} -->\n\n### 图中连线与信号组\n\n编号仅在本图内有效。总线双箭头合并请求与响应；单箭头表示表内说明的主数据、控制或逻辑方向，握手返回不能据箭头省略。主图以连续连线表达连接，编号只用于查表。源码依据见本章代码对应。\n\n| 连线 | 端点与方向 | 信号、用途和需要保留的约定 |\n|---|---|---|\n'
   for e in g['edges']:
    direction='↔' if e.get('both') else '→'
    detail=e.get('detail',e.get('label','')).replace('|','\\|').replace('\n',' ')
    block+=f'| {e["id"]} | {title(e["source"])} {direction} {title(e["target"])} | {detail} |\n'
   block+='\n<!-- /CONNECTIONS -->\n'
   anchor=f'[A 图总览](../diagrams/2026-10-13_rtl_module_comparison/index.html#{name})';s=s.replace(anchor,anchor+block,1)
  p.write_text(re.sub(r'\n{3,}','\n\n',s))

def gallery(graphs):
 out=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>RTL 模块正式 A 图</title><style>body{font-family:sans-serif;max-width:1500px;margin:2em auto;padding:0 1em;color:#23354b;background:#fafbfd}img{width:100%;height:auto}section{margin:3em 0}nav a{display:inline-block;margin:.5em}a{color:#28699b}</style><h1>RTL 模块正式 A 图</h1><p>21 篇正文，24 张图，213 条连续连接。2026-10-13 用户最终确认采用 A；后续补图与修订沿用此版本。</p><nav><a href="../../rtl_modules/README.md">模块指南</a><a href="A/editable/diagrams.pptx">可编辑 PPTX</a><a href="README.md">图源与维护</a></nav>']
 out.append('<nav>'+''.join(f'<a href="#{g["name"]}">{escape(g["name"])}</a>' for g in graphs)+'</nav>')
 for g in graphs:
  name=g['name'];title=escape(g['title'])
  out.append(f'<section id="{name}"><h2>{title}</h2><p><a href="../../rtl_modules/{g["doc"]}">正文与信号表</a> · <a href="A/{name}.svg">SVG</a> · <a href="A/{name}.pdf">PDF</a> · <a href="A/{name}.png">原尺寸 PNG</a></p><img loading="lazy" src="A/{name}.png" alt="{title}"></section>')
 out.append('</html>')
 (ROOT/'index.html').write_text('\n'.join(out))


def main():
 import argparse
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--navigation-only',action='store_true',help='Update guide links/tables and gallery from the existing connection inventory; do not redraw')
 args=parser.parse_args()
 if args.navigation_only:
  graphs=json.loads((ROOT/'connections.json').read_text())['figures']
  update_docs(graphs);gallery(graphs)
  return
 capture();apply_review();resolve_all()
 for f in GRAPHS.values():
  assert not any(n['lines'][0].startswith('待核对') for n in f.nodes),f.name
 if (ROOT/'integration_graphs.json').exists():
  data=json.loads((ROOT/'integration_graphs.json').read_text())
  for g in data['figures']:
   DOCS[g['name']]=g['doc'];new_figure(g)
 graphs=[];layouts={}
 for name,f in sorted(GRAPHS.items()):
  for v,renderer in [('A',render_a)]:
   (ROOT/v).mkdir(exist_ok=True)
   layout=renderer(f,ROOT/v/(name+'.svg'));(ROOT/v/(name+'.layout.json')).write_text(json.dumps(layout,ensure_ascii=False,indent=2));layouts[v+'/'+name]=layout
  graphs.append(graph_dict(f))
 (ROOT/'connections.json').write_text(json.dumps(dict(figures=graphs),ensure_ascii=False,indent=2))
 update_docs(graphs);gallery(graphs)
 print(json.dumps(dict(figures=len(graphs),edges=sum(len(g['edges']) for g in graphs)),ensure_ascii=False))

if __name__=='__main__':main()
