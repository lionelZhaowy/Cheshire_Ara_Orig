#!/usr/bin/env python3
"""Native page 4: preserve the input package, clone page 3, then reflow its diagram."""
import argparse
from copy import deepcopy
import hashlib,json,subprocess
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
from append_uniform_page import NS,REL,R,CT,EP,VT

SVG='http://www.w3.org/2000/svg'
C={'ink':'#29292D','muted':'#606773','data':'#314D66','gb':'#187C78','pixel':'#B96043','cfg':'#765489','irq':'#A54D5D','optional':'#93939D','blue':'#D8E8F4','green':'#D9EEE8','pink':'#F1D7D9','orange':'#F5E1C9','purple':'#E8DFED'}
W,H=3600,2025

class Diagram:
    def __init__(self):self.regions=[];self.boxes=[];self.texts=[];self.edges=[];self.dots=[];self.bridges=[]
    def rect(self,id,x,y,w,h,fill='white',region=False,dash=False):
        b={'id':id,'x':x,'y':y,'w':w,'h':h,'fill':C.get(fill,fill),'dash':dash}
        (self.regions if region else self.boxes).append(b);return b
    def text(self,id,x,y,s,size=30,bold=False,color='ink',owner=None,anchor='middle'):
        self.texts.append(dict(id=id,x=x,y=y,text=s,size=size,bold=bold,color=C.get(color,color),owner=owner,anchor=anchor))
    def block(self,id,x,y,w,h,lines,fill='blue',sizes=None,dash=False):
        self.rect(id,x,y,w,h,fill,dash=dash);sizes=sizes or [30]+[26]*(len(lines)-1)
        total=sum(s*1.2 for s in sizes);yy=y+(h-total)/2
        for i,(s,fs) in enumerate(zip(lines,sizes)):
            self.text(id+f'-t{i}',x+w/2,yy+fs*.94,s,fs,i==0,owner=id);yy+=fs*1.2
    def tag(self,name,x,y):
        id='badge-'+name;self.rect(id,x,y,53,25,'purple');self.text(id+'-text',x+26.5,y+20,name,21,True,'cfg',id)
    def edge(self,id,src,dst,pts,kind='data',both=False,arrow=True,dash=False):
        self.edges.append(dict(id=id,src=src,dst=dst,points=pts,kind=kind,both=both,arrow=arrow,dash=dash))
    def dot(self,x,y,kind):self.dots.append((x,y,kind))
    def save(self,p):
        root=E.Element('{'+SVG+'}svg',nsmap={None:SVG},width=str(W),height=str(H),viewBox=f'0 0 {W} {H}')
        def add(parent,tag,**attrs):return E.SubElement(parent,'{'+SVG+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
        defs=add(root,'defs')
        for kind in ['data','gb','pixel','cfg','irq','optional']:
            m=add(defs,'marker',id='arr-'+kind,markerUnits='strokeWidth',markerWidth=3,markerHeight=3,viewBox='0 0 3 3',refX=3,refY=1.5,orient='auto-start-reverse')
            add(m,'polygon',points='0,0 3,1.5 0,3',fill=C[kind])
        add(root,'rect',id='canvas',x=0,y=0,width=W,height=H,fill='#FFFFFF',stroke='none')
        def box(b):
            kw={'stroke_dasharray':'14 9'} if b['dash'] else {}
            fill='#FFFFFF' if b['fill']=='white' else b['fill']
            add(root,'rect',id=b['id'],x=b['x'],y=b['y'],width=b['w'],height=b['h'],fill=fill,stroke=C['ink'],stroke_width=3.8,**kw)
        for b in self.regions:box(b)
        previous=[]
        # Later continuous paths receive a small bridge at each true geometric
        # crossing. Connections at endpoints remain joined; no edge is split.
        for edge in self.edges:
            pts=edge['points'];d=f'M {pts[0][0]} {pts[0][1]}'
            for a,b in zip(pts,pts[1:]):
                assert a[0]==b[0] or a[1]==b[1],edge['id']
                horizontal=a[1]==b[1];axis=0 if horizontal else 1;direction=1 if b[axis]>a[axis] else -1
                hits=[]
                for old in previous:
                    for c,e in zip(old['points'],old['points'][1:]):
                        if horizontal and c[0]==e[0]:q=(c[0],a[1])
                        elif not horizontal and c[1]==e[1]:q=(a[0],c[1])
                        else:continue
                        if min(a[axis],b[axis])+7<q[axis]<max(a[axis],b[axis])-7 and min(c[1-axis],e[1-axis])+1<q[1-axis]<max(c[1-axis],e[1-axis])-1:
                            hits.append((q,old['id']))
                unique={q:old for q,old in hits}
                for q,old in sorted(unique.items(),key=lambda v:direction*v[0][axis]):
                    x,y=q;r=6;h=8
                    if horizontal:d+=f' L {x-direction*r} {y} Q {x} {y-h} {x+direction*r} {y}'
                    else:d+=f' L {x} {y-direction*r} Q {x+h} {y} {x} {y+direction*r}'
                    self.bridges.append({'edge':edge['id'],'over':old,'at':[x,y]})
                d+=f' L {b[0]} {b[1]}'
            kw={}
            if edge['arrow']:kw['marker_end']='url(#arr-'+edge['kind']+')'
            if edge['both']:kw['marker_start']='url(#arr-'+edge['kind']+')'
            if edge['dash']:kw['stroke_dasharray']='18 11'
            add(root,'path',id=edge['id'],d=d,fill='none',stroke=C[edge['kind']],stroke_width=4.8,stroke_linejoin='miter',**kw)
            previous.append(edge)
        for x,y,kind in self.dots:add(root,'circle',id=f'junction-{x}-{y}',cx=x,cy=y,r=5,fill=C[kind],stroke='none')
        for b in self.boxes:box(b)
        for t in self.texts:
            add(root,'text',id=t['id'],x=t['x'],y=t['y'],font_family='Microsoft YaHei',font_size=t['size'],font_weight='bold' if t['bold'] else 'normal',text_anchor=t['anchor'],fill=t['color']).text=t['text']
        E.ElementTree(root).write(str(p),encoding='utf-8',xml_declaration=True,pretty_print=True)
        p.with_suffix('.json').write_text(json.dumps({'regions':self.regions,'boxes':self.boxes,'texts':self.texts,'edges':self.edges,'bridges':self.bridges,'dots':self.dots},ensure_ascii=False,indent=2)+'\n')


def make_diagram():
    d=Diagram()
    d.rect('title-band',0,0,3600,110,'#084B8B',True)
    d.text('page-title',1800,75,'SoC 硬件层',60,True,'#FFFFFF')
    d.rect('soc-boundary',30,150,3315,1845,'white',True)
    d.text('subtitle',1660,143,'SoC 初版规划：参数加载 / ROI 子图输出 / 四口共享压缩存储',34,True,'muted')
    for id,x,w,title,fill in [('compute',70,890,'CVA6–Ara 计算平台','pink'),('gb-region',1000,1040,'NPU / 独立 Global Buffer 子系统','green'),('image-rx',2080,1060,'图像采集与 ISP','orange')]:
        d.rect(id,x,180,w,380,fill,True,id!='compute');d.text(id+'-title',x+w/2,220,title,36,True,owner=id)
    d.block('cva6',100,260,250,250,['CVA6 core 0','L1 I / D cache','MMU / AXI 适配'],sizes=[32,30,28])
    d.block('ara',390,260,530,105,['Ara 向量处理器','2 lanes · VLSU / AXI：64 bit'],sizes=[32,30])
    d.block('ara-filter',390,410,210,100,['失效过滤','现有 filter'])
    d.block('ara-width',720,410,200,100,['等宽透传','64 → 64 bit'])
    d.edge('cpu-ara-command','cva6','ara',[(350,310),(390,310)],'cfg',True)
    d.text('command-label',545,249,'指令 / MMU',26,color='cfg')
    d.edge('ara-filter-edge','ara','ara-filter',[(495,365),(495,410)])
    d.edge('filter-width','ara-filter','ara-width',[(600,460),(720,460)])
    d.block('npu',1020,250,225,190,['NPU 计算引擎','GB 数据读写'],fill='pink');d.tag('C6',1180,410)
    d.block('gb-adapter',1280,290,250,220,['GB 访问适配','局部仲裁 / 路由','bank 冲突处理'],fill='white')
    d.block('global-buffer',1570,250,440,115,['Global Buffer','独立 SRAM · 分 bank','CPU / Ara / NPU / ISP'],fill='green',sizes=[32,26,26]);d.tag('C9',1950,332)
    d.block('gb-mover',1570,405,440,110,['NPU / GB 搬运引擎','DDR ↔ GB · AXI 主口']);d.tag('C7',1950,482)
    d.edge('npu-gb','npu','gb-adapter',[(1245,340),(1280,340)],'gb',True)
    d.edge('adapter-sram','gb-adapter','global-buffer',[(1530,345),(1570,345)],'gb',True)
    d.edge('mover-gb','gb-mover','gb-adapter',[(1570,455),(1530,455)],'gb',True)
    image_blocks=[('lvds-rx',2110,175,['LVDS 接收','解串 / 帧行']),('rx-cdc',2315,170,['CDC / FIFO','像素流缓冲']),('isp',2520,175,['ISP','行缓存 / 处理']),('frame-select',2725,170,['帧边界选择','RAW / ISP']),('frame-dma',2930,190,['帧写入 DMA','地址 / stride'])]
    for id,x,w,ls in image_blocks:d.block(id,x,300,w,160,ls,fill='white' if id!='isp' else 'pink')
    for a,b in zip(image_blocks,image_blocks[1:]):d.edge(a[0]+'-to-'+b[0],a[0],b[0],[(a[1]+a[2],380),(b[1],380)],'pixel')
    d.edge('raw-bypass','rx-cdc','frame-select',[(2400,300),(2400,260),(2810,260),(2810,300)],'pixel')
    d.text('raw-bypass-label',2600,250,'RAW 旁路',26,color='pixel')
    for tag,x in [('C4',2220),('C5',2630),('C8',3055)]:d.tag(tag,x,426)
    d.edge('isp-gb','isp','gb-adapter',[(2520,420),(2500,420),(2500,575),(1470,575),(1470,510)],'gb',True,dash=True)
    d.text('isp-gb-label',2150,552,'ISP 中间数据 ↔ GB',26,color='gb')
    d.block('pll',1040,660,960,105,['PLL / 时钟与复位分发','RefClk / POR → clk_i / rst_ni'],fill='orange',sizes=[34,28],dash=True);d.tag('C1',1935,667)
    d.rect('roi-region',2080,630,1050,160,'orange',True,dash=True)
    d.text('roi-title',2600,667,'图像裁切输出 · ≤256 ROI / 帧 · 不缩放',32,True,owner='roi-region');d.tag('C11',3070,638)
    for id,x,w,ls in [('roi-scheduler',2110,240,['ROI 任务表','顺序调度']),('roi-vdma',2380,230,['二维读 VDMA','起址 / 行跨度']),('roi-fifo',2640,210,['像素整理','输出 FIFO']),('lvds-tx',2880,220,['LVDS TX','子图帧行封装'])]:d.block(id,x,685,w,90,ls,fill='white')
    d.edge('roi-vdma-control','roi-scheduler','roi-vdma',[(2350,730),(2380,730)],'cfg')
    d.edge('vdma-pixels','roi-vdma','roi-fifo',[(2610,730),(2640,730)],'pixel')
    d.edge('fifo-lvds','roi-fifo','lvds-tx',[(2850,730),(2880,730)],'pixel')
    d.block('lvds-peer',3370,685,210,90,['片外接收端','LVDS 子图'],fill='#EEEEEE')
    d.block('emmc-device',3370,800,210,100,['eMMC','模型 / 校正参数'],fill='#EEEEEE',sizes=[34,26])
    # Main crossbar and both equally spaced port rows.
    d.rect('axi-crossbar',70,980,3070,90,'#4776C2')
    d.text('crossbar-title',1605,1026,'AXI Crossbar',36,True,owner='axi-crossbar')
    d.text('crossbar-caption',1605,1052,'8 × 6 固定端口 + 扩展 | 64 bit 数据 / 48 bit 地址 | 地址译码 / 各目标仲裁',26,owner='axi-crossbar')
    d.text('crossbar-rt-note',340,1052,'输入侧 AXI RT · 按配置可选',24,color='muted',owner='axi-crossbar')
    d.text('crossbar-error-note',2920,1052,'未映射请求：DECERR',24,color='muted',owner='axi-crossbar')
    top=[70+(i+.5)*3070/9 for i in range(9)];bottom=[70+(i+.5)*3070/7 for i in range(7)]
    for i,cx in enumerate(top):
        label='S_EXT' if i==8 else 'S'+str(i)
        d.block('xbar-in-'+label,cx-48,966,96,28,[label],fill='white',sizes=[22.5])
    masters={1:('debug-sba',['Debug / SBA','JTAG 总线访问']),3:('idma-master',['iDMA 数据主口','内存 → 内存']),4:('slink-rx',['Serial Link RX','远端请求入口']),5:('vga',['VGA','帧缓冲读取']),6:('usb-dma',['USB DMA','OHCI 主口']),7:('emmc-host',['eMMC Host / DMA','存储块 ↔ 内存']),8:('ext-master',['AXI 外部 master','可选扩展入口'])}
    for i,(id,ls) in masters.items():
        d.block(id,top[i]-143,835,286,100,ls,dash=i==8)
        d.edge('master-'+str(i),id,'xbar-in-'+('S_EXT' if i==8 else 'S'+str(i)),[(top[i],935),(top[i],966)],'optional' if i==8 else 'data')
    d.tag('C10',top[7]+82,906)
    d.edge('cpu-xbar','cva6','xbar-in-S0',[(top[0],510),(top[0],966)])
    d.edge('ara-xbar','ara-width','xbar-in-S2',[(820,510),(820,780),(top[2],780),(top[2],966)])
    target_data=[('debug-target',['Debug 目标','调试模块窗口'],'blue'),('reg-bridge',['AXI → Regbus','原子适配 / 32 bit 桥'],'purple'),('memory-target',['主存 / SPM 共用目标'],'blue'),('idma-config',['iDMA 配置','原子适配 → AXI→Reg','wrapper 内部寄存器'],'blue'),('slink-tx',['Serial Link TX','远端目标窗口'],'blue'),('gb-interface',['GB AXI 接口','CPU / Ara / eMMC DMA','64-bit 数据窗口 · 共用'],'green'),('ext-target',['AXI 外部 slave','可选外部目标扩展'],'white')]
    for i,(id,ls,fill) in enumerate(target_data):
        cx=bottom[i];label='M_EXT' if i==6 else 'M'+str(i)
        d.block('xbar-out-'+label,cx-48,1056,96,28,[label],fill='white',sizes=[22.5])
        d.edge('target-'+str(i),'xbar-out-'+label,id,[(cx,1084),(cx,1130)])
        if i==2:
            d.rect(id,cx-210,1130,420,145,fill);d.text('memory-title',cx,1165,ls[0],30,True,owner=id)
            d.block('atomics',cx-200,1182,180,83,['原子适配','AMO / LRSC'],fill='white',sizes=[26.25,30])
            d.block('llc-spm',cx+20,1182,180,83,['LLC / SPM','SRAM 阵列'],fill='white',sizes=[26.25,30])
            d.edge('atomics-llc','atomics','llc-spm',[(cx-20,1224),(cx+20,1224)])
        else:d.block(id,cx-200,1130,400,145,ls,fill,dash=i==6)
    d.edge('m5-gb','gb-interface','gb-adapter',[(bottom[5]+200,1200),(2710,1200),(2710,1105),(3170,1105),(3170,595),(1335,595),(1335,510)],'gb')
    # Four independent DDR classes, with explicit read-data return for the ROI engine.
    d.edge('llc-f0','llc-spm','front-F0',[(bottom[2]+110,1265),(bottom[2]+110,1295),(2005,1295),(2005,1386)])
    d.edge('mover-f1','gb-mover','front-F1',[(2010,455),(2030,455),(2030,615),(3210,615),(3210,1310),(2315,1310),(2315,1386)],dash=True)
    d.edge('frame-f2','frame-dma','front-F2',[(3120,410),(3250,410),(3250,1325),(2625,1325),(2625,1386)],dash=True)
    d.edge('roi-f3-request','roi-vdma','front-F3',[(2495,775),(2495,790),(3290,790),(3290,1360),(2940,1360),(2940,1386)])
    d.edge('f3-roi-read-data','front-F3','roi-vdma',[(2970,1386),(2970,1375),(3300,1375),(3300,810),(2515,810),(2515,775)],'gb')
    d.edge('lvds-external','lvds-tx','lvds-peer',[(3100,730),(3370,730)],'pixel')
    d.edge('emmc-physical','emmc-device','emmc-host',[(3370,850),(3350,850),(3350,828),(2470,828),(2470,850),(top[7]-143,850)],'pixel',True)
    # Regbus matrix retains all prior target/IP configuration names.
    d.rect('reg-region',70,1320,1670,650,'purple',True)
    d.block('regbus',80,1350,1640,55,['Regbus decode / demux · 32 bit'],fill='purple',sizes=[34])
    d.edge('bridge-regbus','reg-bridge','regbus',[(bottom[1],1275),(bottom[1],1350)],'cfg')
    rows=[['Boot ROM','CLINT','SoC 寄存器','PLIC','LLC 配置'],['UART','I²C','SPI Host','GPIO','Serial Link 配置'],['VGA 配置','USB 配置','Bus-error · VGA','Bus-error · iDMA','Bus-error · CPU'],['IRQ router','AXI RT 配置','CLIC','reg_err_slv','RegExt 扩展译码'],['C1 · PLL 配置','C2 · DDR 配置','C3 · PHY 配置','C4 · LVDS RX','C5 · ISP 配置'],['C6 · NPU 配置','C7 · GB 搬运','C8 · 帧写 DMA','C9 · GB 管理','外部 IRQ 同步 / 路由']]
    for col in range(5):
        x=105+col*320
        d.edge('reg-column-'+str(col),'regbus','reg-column-'+str(col),[(x-17,1405),(x-17,1840)],'cfg',arrow=False)
        for row,labels in enumerate(rows):
            y=1430+row*75;id='reg-'+str(row)+'-'+str(col)
            if row==5 and col==4:
                d.block('new-irq-sync',x,y,280,60,[labels[col]],fill='pink',sizes=[26]);continue
            d.block(id,x,y,280,60,[labels[col]],fill='white',sizes=[30],dash=row==3 and col<3)
            d.edge(id+'-cfg','reg-column-'+str(col),id,[(x-17,y+30),(x,y+30)],'cfg')
            d.dot(x-17,y+30,'cfg')
    d.text('reg-config-note',895,1916,'C1–C9：原有 IP 配置目标；新增 C10–C12 经 RegExt 接出',26,color='cfg',owner='reg-region')
    d.text('reg-init-note',895,1955,'配置地址、IRQ 编号及各 IP 参数尚未冻结',26,color='muted',owner='reg-region')
    # Shared compression frontend is outside the purchased DDR controller.
    d.rect('compression-front',1840,1400,1300,350,'green',True,dash=True)
    frontxs=[2005,2315,2625,2955]
    for i,x in enumerate(frontxs):
        d.block('front-F'+str(i),x-50,1386,100,28,['F'+str(i)],fill='white',sizes=[22.5])
        d.edge('front-input-'+str(i),'front-F'+str(i),'front-adapt',[(x,1414),(x,1440)],arrow=False)
    d.block('front-adapt',1870,1440,1240,60,['共享压缩存储前端 · 四口事务适配 / 区域选择'],fill='blue',sizes=[30])
    for id,x,w,ls,fill in [('compressor',1870,270,['四口共享压缩器','写入 W ↓','无损 / 按块'],'orange'),('decompressor',2180,270,['四口共享解压器','读返回 R ↑','独立块解码'],'orange'),('plain-bypass',2490,270,['普通数据旁路','未压缩区域','读 / 写'],'blue'),('metadata',2800,310,['块地址 / 元数据','格式 / 长度 / 状态'],'purple')]:d.block(id,x,1530,w,120,ls,fill,sizes=[30]+[26]*(len(ls)-1))
    d.block('front-route',1870,1670,1240,60,['端口路由 / B、R 响应匹配 · F0↔S0，F1↔S1，F2↔S2，F3↔S3'],fill='blue',sizes=[28])
    for id,x,kind in [('compressor',2005,'data'),('decompressor',2315,'gb'),('plain-bypass',2625,'data'),('metadata',2955,'cfg')]:
        if id=='decompressor':
            d.edge('decoder-up',id,'front-adapt',[(x,1530),(x,1500)],kind)
            d.edge('read-to-decoder','front-route',id,[(x,1670),(x,1650)],kind)
        else:
            d.edge('adapt-'+id,'front-adapt',id,[(x,1500),(x,1530)],kind,both=id in ['plain-bypass','metadata'])
            d.edge(id+'-route',id,'front-route',[(x,1650),(x,1670)],kind,both=id in ['plain-bypass','metadata'])
    d.tag('C12',3080,1507)
    d.rect('ddr-controller',1840,1785,1300,175,'blue',True,dash=True)
    for i,x in enumerate(frontxs):
        d.block('ddr-S'+str(i),x-50,1771,100,28,['S'+str(i)],fill='white',sizes=[22.5])
        d.edge('front-ddr-'+str(i),'front-route','ddr-S'+str(i),[(x,1730),(x,1771)])
        d.edge('ddr-arb-'+str(i),'ddr-S'+str(i),'ddr-arb',[(x,1799),(x,1818)],arrow=False)
    d.block('ddr-arb',1870,1818,1240,40,['四口仲裁 / QoS · 共享 DDR 带宽'],fill='white',sizes=[28])
    d.block('ddr-rw',1870,1870,500,55,['读写调度 · Bank / Row'],fill='white',sizes=[30])
    d.block('ddr-command',2490,1870,620,55,['命令调度 · Controller → PHY'],fill='white',sizes=[30])
    d.edge('arb-rw','ddr-arb','ddr-rw',[(2120,1858),(2120,1870)],arrow=False)
    d.edge('rw-command','ddr-rw','ddr-command',[(2370,1897.5),(2490,1897.5)])
    d.text('ddr-title',2490,1950,'DDR Controller · 4 个 AXI slave',30,True,owner='ddr-controller')
    d.tag('C2',3078,1929)
    d.block('ddr-phy',3180,1860,130,90,['DDR PHY','训练 / 校准'],fill='purple',sizes=[28,24],dash=True);d.tag('C3',3250,1828)
    d.block('ddr-device',3370,1860,210,90,['DDR','片外器件'],fill='#EEEEEE',sizes=[34,28])
    d.edge('controller-phy','ddr-command','ddr-phy',[(3110,1897.5),(3180,1897.5)],both=True)
    d.edge('phy-ddr','ddr-phy','ddr-device',[(3310,1897.5),(3370,1897.5)],both=True)
    # Continuous newly added register-access and interrupt paths.
    d.edge('regext-new-config','reg-3-4','roi-region',[(1665,1685),(1760,1685),(1760,1305),(3310,1305),(3310,672),(3130,672)],'cfg')
    d.edge('config-emmc','new-config-trunk','emmc-host',[(3310,945),(2690,945),(2690,935)],'cfg')
    d.edge('config-codec','new-config-trunk','compression-front',[(3310,1305),(3310,1520),(3140,1520)],'cfg')
    for y in [945,1305]:d.dot(3310,y,'cfg')
    d.edge('roi-irq','roi-region','new-irq-sync',[(3130,760),(3330,760),(3330,1968),(1685,1968),(1685,1835),(1665,1835)],'irq')
    d.edge('emmc-irq','emmc-host','new-irq-trunk',[(top[7]+143,905),(2790,905),(2790,955),(3330,955)],'irq',arrow=False)
    d.edge('codec-irq','compression-front','new-irq-trunk',[(3140,1655),(3330,1655)],'irq',arrow=False)
    for y in [955,1655]:d.dot(3330,y,'irq')
    d.edge('new-irq-plic','new-irq-sync','reg-0-3',[(1385,1835),(1355,1835),(1355,1418),(1205,1418),(1205,1430)],'irq')
    # Compact legend outside the SoC boundary; explicit read return for S3.
    d.text('legend-title',3475,1030,'接口图例',30,True)
    for i,(kind,l1,l2) in enumerate([('data','AXI 请求','响应沿接口返回'),('gb','GB 读写 /','S3 读返回'),('pixel','像素流 /','eMMC 数据'),('cfg','Regbus','配置访问'),('irq','完成 / 错误','独立 IRQ 向量'),('optional','虚线：可选','或新增规划')]):
        y=1090+i*95
        d.edge('legend-'+kind,'legend','legend',[(3370,y),(3420,y)],kind,both=kind=='gb',dash=kind=='optional')
        d.text('legend-'+kind+'-a',3500,y-4,l1,24,color=kind)
        d.text('legend-'+kind+'-b',3500,y+29,l2,24,color=kind)
    return d


def append(input,overlay,out):
    serialize=lambda x:E.tostring(x,encoding='UTF-8',xml_declaration=True,standalone=True)
    with ZipFile(input) as z:parts={n:z.read(n) for n in z.namelist()}
    pres=E.fromstring(parts['ppt/presentation.xml']);sids=pres.find('p:sldIdLst',NS);assert len(sids)==3
    slide=E.fromstring(parts['ppt/slides/slide3.xml']);tree=slide.find('p:cSld/p:spTree',NS)
    for el in list(tree):
        if E.QName(el).localname not in ['nvGrpSpPr','grpSpPr']:tree.remove(el)
    with ZipFile(overlay) as z:generated=E.fromstring(z.read('ppt/slides/slide1.xml'))
    for el in generated.find('p:cSld/p:spTree',NS):
        if E.QName(el).localname in ['sp','cxnSp']:tree.append(deepcopy(el))
    parts['ppt/slides/slide4.xml']=serialize(slide)
    sr=E.fromstring(parts['ppt/slides/_rels/slide3.xml.rels'])
    for rel in sr:
        if rel.get('Type').endswith('/notesSlide'):rel.set('Target','../notesSlides/notesSlide4.xml')
    parts['ppt/slides/_rels/slide4.xml.rels']=serialize(sr)
    notes=E.fromstring(parts['ppt/notesSlides/notesSlide3.xml'])
    for field in notes.xpath('//a:fld[@type="slidenum"]/a:t',namespaces=NS):field.text='4'
    for sp in notes.findall('p:cSld/p:spTree/p:sp',NS):
        if sp.find('p:nvSpPr/p:nvPr/p:ph[@type="body"]',NS) is None:continue
        body=sp.find('p:txBody',NS)
        for p in body.findall('a:p',NS):body.remove(p)
        p=E.SubElement(body,'{'+NS['a']+'}p');r=E.SubElement(p,'{'+NS['a']+'}r');E.SubElement(r,'{'+NS['a']+'}t').text='初版规划：eMMC 内置 DMA 经 S7/M5 加载 GB；≤256 ROI 纯裁切经 DDR S3；四口共享外置无损压缩存储前端，普通区域旁路。地址、IRQ、格式、速率与 IP 选型未冻结；未实施 RTL。'
    parts['ppt/notesSlides/notesSlide4.xml']=serialize(notes)
    nr=E.fromstring(parts['ppt/notesSlides/_rels/notesSlide3.xml.rels'])
    for rel in nr:
        if rel.get('Type').endswith('/slide'):rel.set('Target','../slides/slide4.xml')
    parts['ppt/notesSlides/_rels/notesSlide4.xml.rels']=serialize(nr)
    pr=E.fromstring(parts['ppt/_rels/presentation.xml.rels']);rid='rId'+str(max(int(r.get('Id')[3:]) for r in pr)+1)
    E.SubElement(pr,'{'+REL+'}Relationship',Id=rid,Type=R+'/slide',Target='slides/slide4.xml')
    E.SubElement(sids,'{'+NS['p']+'}sldId',{'id':str(max(int(s.get('id')) for s in sids)+1),'{'+R+'}id':rid})
    parts['ppt/presentation.xml']=serialize(pres);parts['ppt/_rels/presentation.xml.rels']=serialize(pr)
    ct=E.fromstring(parts['[Content_Types].xml'])
    for name,kind in [('slides/slide4.xml','slide'),('notesSlides/notesSlide4.xml','notesSlide')]:E.SubElement(ct,'{'+CT+'}Override',PartName='/ppt/'+name,ContentType='application/vnd.openxmlformats-officedocument.presentationml.'+kind+'+xml')
    parts['[Content_Types].xml']=serialize(ct)
    app=E.fromstring(parts['docProps/app.xml'])
    for tag in ['Slides','Notes']:app.find('{'+EP+'}'+tag).text='4'
    app.find('{'+EP+'}HeadingPairs').findall('.//{'+VT+'}i4')[-1].text='4'
    titles=app.find('{'+EP+'}TitlesOfParts/{'+VT+'}vector');E.SubElement(titles,'{'+VT+'}lpstr').text='SoC 初版规划：eMMC / ROI / 四口共享压缩存储';titles.set('size',str(len(titles)))
    parts['docProps/app.xml']=serialize(app)
    with ZipFile(out,'w',ZIP_DEFLATED) as z:
        for n,b in parts.items():z.writestr(n,b)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);ap.add_argument('--native-skill-root',type=Path,required=True);a=ap.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=False);d=make_diagram();svg=a.out_dir/'slide-04.svg';d.save(svg)
    subprocess.run(['python3','-B',str(a.native_skill_root/'scripts/run.py'),'--input',str(svg),'--out-dir',str(a.out_dir/'native'),'--aspect','source','--slide-width-in',str(12192000/914400),'--font','Microsoft YaHei','--font-file','/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'],check=True)
    output=a.out_dir/'soc_landscape_m5_gb.pptx';append(a.input,a.out_dir/'native/diagrams.pptx',output)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    report={'input':str(a.input),'input_sha256':sha(a.input),'output_sha256':sha(output),'page_count':4,'copy_source':3,'native_boxes':len(d.boxes),'native_texts':len(d.texts),'native_paths':len(d.edges),'intentional_bridges':len(d.bridges),'office_tested':False}
    (a.out_dir/'edit_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
