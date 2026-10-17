#!/usr/bin/env python3
"""Revise only slide 4; inherit slide-3 colours and the final deck's theme."""
import argparse,colorsys,json,hashlib,subprocess
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from copy import deepcopy
from lxml import etree as E
from build_page4 import Diagram,C
from append_uniform_page import NS

D=Path(__file__).resolve().parent
A=NS['a']

def resolve_colour(fill,theme):
    c=fill[0];kind=E.QName(c).localname
    raw=c.get('val') if kind=='srgbClr' else theme[c.get('val')]
    rgb=[int(raw[i:i+2],16)/255 for i in (0,2,4)]
    h,l,s=colorsys.rgb_to_hls(*rgb)
    for modifier in c:
        name=E.QName(modifier).localname;v=int(modifier.get('val'))/100000
        if name=='lumMod':l*=v
        elif name=='lumOff':l+=v
        else:raise ValueError(name)
    return '#'+''.join(f'{round(v*255):02X}' for v in colorsys.hls_to_rgb(h,max(0,min(l,1)),s))

def source_colours(deck):
    with ZipFile(deck) as z:
        t=E.fromstring(z.read('ppt/theme/theme1.xml'))
        theme={E.QName(n).localname:n[0].get('lastClr',n[0].get('val')) for n in t.find('a:themeElements/a:clrScheme',NS)}
        s=E.fromstring(z.read('ppt/slides/slide3.xml'))
    fills={}
    for el in s.findall('p:cSld/p:spTree/p:sp',NS):
        fill=el.find('p:spPr/a:solidFill',NS)
        if fill is not None:fills[el.find('p:nvSpPr/p:cNvPr',NS).get('name')]=fill
    return fills,theme

# Every retained box uses the actual slide-3 fill, not a hard-coded preview colour.
MATCH={'compute':'cpu-platform','cva6':'cva6','ara':'ara-core','ara-filter':'ara-filter','ara-width':'ara-width',
'gb-region':'npu-subsystem','npu':'npu-compute','gb-adapter':'gb-router','global-buffer':'global-buffer','gb-mover':'npu-transfer',
'image-rx':'image-subsystem','lvds-rx':'lvds','rx-cdc':'pixel-cdc','isp':'isp','frame-select':'frame-select','frame-dma':'frame-dma',
'axi-crossbar':'axi-crossbar','debug-sba':'debug-sba','idma-master':'idma-master','slink-rx':'slink-rx','vga':'vga-master','usb-dma':'usb-master','ext-master':'ext-master',
'debug-target':'debug-target','reg-bridge':'reg-bridge','memory-target':'memory-target','atomics':'atomics','llc-spm':'llc-spm','idma-config':'idma-config','slink-tx':'slink-tx','gb-interface':'gb-axi-interface','ext-target':'ext-target',
'reg-region':'reg-subsystem','regbus':'regbus','ddr-controller':'ddr-controller','ddr-phy':'ddr-phy','ddr-device':'dram','pll':'clock-reset'}
for i in range(1,10):MATCH[f'config-C{i}']=f'config-C{i}'


def config_tag(d,ref,x,y):
    d.tag(ref,x,y)
    name="reg-badge-"+ref
    d.boxes[-1]["id"]=name
    d.texts[-1]["id"]=name+"-text"
    d.texts[-1]["owner"]=name

def make(fills,theme):
    d=Diagram()
    d.rect('soc-boundary',21.25,20,3325,1983.1,'white',True)
    for id,x,w,title,fill in [('compute',71.25,935,'CVA6–Ara 计算平台','pink'),('gb-region',1061.25,1135,'NPU / 独立 Global Buffer 子系统','green'),('image-rx',2246.25,1065,'图像采集与 ISP','orange')]:
        d.rect(id,x,60,w,425,fill,True,id!='compute');d.text(id+'-title',x+w/2,96,title,36,True,owner=id)
    d.block('cva6',96.25,140,250,215,['CVA6 core 0','L1 I / D cache','MMU / AXI 适配'],sizes=[32,30,28])
    d.block('ara',396.25,140,580,125,['Ara 向量处理器','2 lanes · VLSU / AXI：64 bit'],sizes=[32,30])
    d.block('ara-filter',416.25,310,190,86,['失效过滤','现有 filter'])
    d.block('ara-width',826.25,310,150,86,['等宽透传','64 → 64 bit'],sizes=[30,26])
    d.edge('cpu-ara-command','cva6','ara',[(346.25,200),(396.25,200)],'cfg',True)
    d.text('command-label',370,130,'指令 / MMU',26,color='cfg')
    d.edge('ara-filter-edge','ara','ara-filter',[(511.25,265),(511.25,310)])
    d.edge('filter-width','ara-filter','ara-width',[(606.25,353),(826.25,353)])
    d.block('npu',1086.25,140,270,175,['NPU 计算引擎','GB 数据读写'],fill='pink');d.tag('C6',1296.25,273)
    d.block('gb-adapter',1391.25,215,230,235,['GB 访问适配','局部仲裁 / 路由','bank 冲突处理'],fill='white')
    d.block('global-buffer',1661.25,140,505,170,['Global Buffer','独立 SRAM · 分 bank','CPU / Ara / NPU / ISP'],fill='green',sizes=[32,28,28]);d.tag('C9',2106.25,270)
    d.block('gb-mover',1661.25,345,505,120,['NPU / GB 搬运引擎','DDR ↔ GB · AXI 主口']);d.tag('C7',2106.25,427)
    d.edge('npu-gb','npu','gb-adapter',[(1356.25,250),(1391.25,250)],'gb',True)
    d.edge('adapter-sram','gb-adapter','global-buffer',[(1621.25,270),(1661.25,270)],'gb',True)
    d.edge('mover-gb','gb-mover','gb-adapter',[(1661.25,405),(1621.25,405)],'gb',True)
    blocks=[('lvds-rx',2271.25,165,['LVDS 接收','解串 / 帧行']),('rx-cdc',2466.25,160,['CDC / FIFO','像素流缓冲']),('isp',2656.25,165,['ISP','行缓存 / 处理']),('frame-select',2851.25,180,['帧边界选择','RAW / ISP']),('frame-dma',3066.25,215,['帧写入 DMA','地址 / stride'])]
    for id,x,w,ls in blocks:d.block(id,x,200,w,185,ls,fill='pink' if id=='isp' else 'white')
    for a,b in zip(blocks,blocks[1:]):d.edge(a[0]+'-to-'+b[0],a[0],b[0],[(a[1]+a[2],290),(b[1],290)],'pixel')
    d.edge('raw-bypass','rx-cdc','frame-select',[(2546.25,200),(2546.25,155),(2941.25,155),(2941.25,200)],'pixel')
    d.text('raw-bypass-label',2740,143,'RAW 旁路',26,color='pixel')
    for tag,x in [('C4',2376.25),('C5',2761.25),('C8',3221.25)]:d.tag(tag,x,343)
    d.edge('isp-gb','isp','gb-adapter',[(2656.25,345),(2640,345),(2640,500),(1506.25,500),(1506.25,450)],'gb',both=True,dash=True)
    d.text('isp-gb-label',2490,480,'ISP 中间数据 ↔ GB',26,color='gb')
    # Crossbar source row: eMMC S7 and the separate S_EXT remain distinct.
    d.rect('axi-crossbar',71.25,700,2830,135,'blue')
    d.text('crossbar-title',1486.25,750,'AXI Crossbar',36,True,owner='axi-crossbar')
    d.text('crossbar-caption',1486.25,790,'8 × 6 固定端口 + 扩展 | 64 bit 数据 / 48 bit 地址 | 地址译码 / 各目标仲裁',26,owner='axi-crossbar')
    d.text('crossbar-rt-note',290,815,'输入侧 AXI RT · 按配置可选',24,color='muted',owner='axi-crossbar')
    d.text('crossbar-error-note',2710,815,'未映射请求：DECERR',24,color='muted',owner='axi-crossbar')
    top=[71.25+(i+.5)*2830/9 for i in range(9)];bottom=[71.25+(i+.5)*2830/7 for i in range(7)]
    for i,cx in enumerate(top):d.block('xbar-in-'+('S_EXT' if i==8 else 'S'+str(i)),cx-48,686,96,28,['S_EXT' if i==8 else 'S'+str(i)],'white',[22.5])
    masters={1:('debug-sba',['Debug / SBA','JTAG 总线访问']),3:('idma-master',['iDMA 数据主口','内存 → 内存']),4:('slink-rx',['Serial Link RX','远端请求入口']),5:('vga',['VGA','帧缓冲读取']),6:('usb-dma',['USB DMA','OHCI 主口']),7:('emmc-host',['eMMC Host / DMA','存储块 ↔ 内存']),8:('ext-master',['AXI 外部 master','可选扩展入口'])}
    for i,(id,ls) in masters.items():
        d.block(id,top[i]-143,555,286,100,ls,dash=i==8)
        d.edge('master-'+str(i),id,'xbar-in-'+('S_EXT' if i==8 else 'S'+str(i)),[(top[i],655),(top[i],686)],'optional' if i==8 else 'data')
    d.tag('C10',top[7]+82,624)
    d.edge('cpu-xbar','cva6','xbar-in-S0',[(top[0],355),(top[0],686)])
    d.edge('ara-xbar','ara-width','xbar-in-S2',[(901.25,396),(901.25,530),(top[2],530),(top[2],686)])
    target_data=[('debug-target',['Debug 目标','调试模块窗口'],'blue'),('reg-bridge',['AXI → Regbus','原子适配 / 32 bit 桥'],'purple'),('memory-target',['主存 / SPM 共用目标'],'blue'),('idma-config',['iDMA 配置','原子适配 → AXI→Reg','wrapper 内部寄存器'],'blue'),('slink-tx',['Serial Link TX','远端目标窗口'],'blue'),('gb-interface',['GB AXI 接口','CPU / Ara / eMMC DMA','64-bit 数据窗口 · 共用'],'green'),('ext-target',['AXI 外部 slave','可选外部目标扩展'],'#F5F5F7')]
    for i,(id,ls,fill) in enumerate(target_data):
        cx=bottom[i];label='M_EXT' if i==6 else 'M'+str(i)
        d.block('xbar-out-'+label,cx-48,821,96,28,[label],'white',[22.5])
        d.edge('target-'+str(i),'xbar-out-'+label,id,[(cx,849),(cx,900)])
        if i==2:
            d.rect(id,cx-200,900,400,155,fill);d.text('memory-title',cx,934,ls[0],30,True,owner=id)
            d.block('atomics',cx-190,960,185,84,['原子适配','AMO / LRSC'],'white',[26.25,30])
            d.block('llc-spm',cx+20,960,170,84,['LLC / SPM','SRAM 阵列'],'white',[26.25,28])
            d.edge('atomics-llc','atomics','llc-spm',[(cx-5,1002),(cx+20,1002)])
        else:d.block(id,cx-180,900,360,155,ls,fill,dash=i==6)
    d.edge('m5-gb','gb-interface','gb-adapter',[(bottom[5]+180,975),(2495,975),(2495,870),(2945,870),(2945,520),(1450,520),(1450,450)],'gb')
    d.block('emmc-device',3370,555,210,100,['eMMC','模型 / 校正参数'],'#EAECEE',[34,26])
    d.edge('emmc-physical','emmc-device','emmc-host',[(3370,605),(3350,605),(3350,535),(2584,535),(2584,605),(top[7]+143,605)],'pixel',True)
    # Regbus stays at lower left; old extensions regain their bottom-row positions.
    d.rect('reg-region',51.25,1115,1720,625,'#FAF8FB',True)
    d.block('regbus',71.25,1135,1680,65,['Regbus decode / demux · 32 bit'],'purple',[34])
    d.edge('bridge-regbus','reg-bridge','regbus',[(bottom[1],1055),(bottom[1],1135)],'cfg')
    rows=[['Boot ROM','CLINT','SoC 寄存器','PLIC','LLC 配置'],['UART','I²C','SPI Host','GPIO','Serial Link 配置'],['VGA 配置','USB 配置','Bus-error · VGA','Bus-error · iDMA','Bus-error · CPU'],['IRQ router','AXI RT 配置','CLIC','reg_err_slv','RegExt 扩展']]
    ids=[['bootrom','clint','soc-regs','plic','llc-regs'],['uart','i2c','spi','gpio','slink-regs'],['vga-regs','usb-regs','err-vga','err-dma','err-cpu'],['irq-router','axi-rt-config','clic','reg-error','reg-ext']]
    desc=[['启动代码','软件 / 定时中断','平台信息 / scratch','外部中断控制','SPM way / cache'],['串口控制','两线串行接口','Flash / SD','通用 IO','链路控制'],['时序 / 帧地址','OHCI 寄存器','错误记录','每传输错误记录','每核错误记录'],['可选中断路由','可选流量调节','可选每核中断控制','未匹配地址','新增 IP 配置出口']]
    for col in range(5):
        x=106.25+col*330
        d.edge('reg-column-'+str(col),'regbus','reg-column-'+str(col),[(x-22,1200),(x-22,1569)],'cfg',arrow=False)
        for row in range(4):
            id=ids[row][col];y=1230+row*100
            d.block(id,x,y,300,78,[rows[row][col],desc[row][col]],'white',[30,26],dash=row==3 and col!=3)
            d.edge(id+'-cfg','reg-column-'+str(col),id,[(x-22,y+39),(x,y+39)],'cfg');d.dot(x-22,y+39,'cfg');MATCH[id]=id
    # New configuration endpoints are in Regbus, without external control/IRQ lines.
    for i,(id,title,desc) in enumerate([('C10','eMMC 配置 / 状态','DMA / 完成与错误'),('C11','ROI / VDMA / LVDS TX','任务表 / 完成与错误'),('C12','压缩存储前端配置','区域 / 状态 / 错误')]):
        x=106.25+i*550
        d.block('config-'+id,x,1640,500,78,[title,desc],'purple',[30,26]);config_tag(d,id,x+7,1643)
    d.edge('new-reg-config','reg-ext','new-config-trunk',[(1576.25,1608),(1576.25,1624),(356.25,1624)],'cfg',arrow=False)
    for i,id in enumerate(['C10','C11','C12']):
        x=356.25+i*550
        d.edge('cfg-'+id,'new-config-trunk','config-'+id,[(x,1624),(x,1640)],'cfg')
    # Four AXI paths share services but keep source/return identity.
    d.rect('compression-front',1810,1170,1120,350,'green',True,True)
    fx=[1950,2225,2500,2775]
    for i,x in enumerate(fx):
        d.block('front-F'+str(i),x-48,1156,96,28,['F'+str(i)],'white',[22.5])
        d.edge('front-input-'+str(i),'front-F'+str(i),'front-adapt',[(x,1184),(x,1210)],arrow=False)
    d.block('front-adapt',1830,1210,1080,60,['共享压缩存储前端 · 四口适配 / 区域选择'],'blue',[30])
    services=[('compressor',1830,['四口共享压缩器','写 W ↓ · 无损按块'],'orange'),('decompressor',2105,['四口共享解压器','读 R ↑ · 独立解码'],'orange'),('plain-bypass',2380,['普通数据旁路','未压缩区域 · 读写'],'blue'),('metadata',2655,['块地址 / 元数据','格式 / 长度 / 状态'],'purple')]
    for id,x,ls,fill in services:d.block(id,x,1300,255,120,ls,fill,[30,26])
    d.block('front-route',1830,1450,1080,50,['端口 / 返回路由 · F0↔S0，F1↔S1，F2↔S2，F3↔S3'],'blue',[28])
    for id,x,kind in [('compressor',1957.5,'data'),('decompressor',2232.5,'gb'),('plain-bypass',2507.5,'data'),('metadata',2782.5,'cfg')]:
        if id=='decompressor':
            d.edge('decoder-up',id,'front-adapt',[(x,1300),(x,1270)],kind);d.edge('read-to-decoder','front-route',id,[(x,1450),(x,1420)],kind)
        else:
            d.edge('adapt-'+id,'front-adapt',id,[(x,1270),(x,1300)],kind,both=id in ['plain-bypass','metadata'])
            d.edge(id+'-route',id,'front-route',[(x,1420),(x,1450)],kind,both=id in ['plain-bypass','metadata'])
    d.tag('C12',2850,1179)
    d.rect('ddr-controller',1810,1565,1120,170,'blue',True,True)
    for i,x in enumerate(fx):
        d.block('ddr-S'+str(i),x-48,1551,96,28,['S'+str(i)],'white',[22.5])
        d.edge('front-ddr-'+str(i),'front-route','ddr-S'+str(i),[(x,1500),(x,1551)])
        d.edge('ddr-arb-'+str(i),'ddr-S'+str(i),'ddr-arb',[(x,1579),(x,1595)],arrow=False)
    d.block('ddr-arb',1830,1595,1080,40,['四口仲裁 / QoS · 共享 DDR 带宽'],'white',[28])
    d.block('ddr-rw',1830,1645,475,50,['读写调度 · Bank / Row'],'white',[30])
    d.block('ddr-command',2425,1645,485,50,['命令调度 · Controller → PHY'],'white',[28])
    d.edge('arb-rw','ddr-arb','ddr-rw',[(2067.5,1635),(2067.5,1645)],arrow=False)
    d.edge('rw-command','ddr-rw','ddr-command',[(2305,1670),(2425,1670)])
    d.text('ddr-title',2370,1725,'DDR Controller · 4 个 AXI slave',30,True,owner='ddr-controller');d.tag('C2',2850,1700)
    d.block('ddr-phy',3030,1670,255,100,['DDR PHY','训练 / 校准'],'purple',[30,28],True);d.tag('C3',3220,1738)
    d.block('ddr-device',3396.25,1670,150,100,['DDR','片外器件'],'#EAECEE',[34,28])
    d.edge('controller-phy','ddr-command','ddr-phy',[(2910,1670),(2970,1670),(2970,1710),(3030,1710)],both=True)
    d.edge('phy-ddr','ddr-phy','ddr-device',[(3285,1710),(3396.25,1710)],both=True)
    # LVDS output flows vertically in the freed right-side space, no off-chip peer.
    d.rect('roi-region',3000,1115,320,530,'orange',True,True)
    d.text('roi-title',3160,1150,'图像裁切输出',32,True,owner='roi-region')
    d.text('roi-count',3160,1178,'≤256 ROI / 帧',26,owner='roi-region')
    d.text('roi-no-scale',3160,1204,'纯裁切 · 不缩放',26,owner='roi-region')
    for id,y,ls in [('roi-scheduler',1215,['ROI 任务表','顺序调度']),('roi-vdma',1320,['二维读 VDMA','起址 / 行跨度']),('roi-fifo',1425,['像素整理','输出 FIFO']),('lvds-tx',1530,['LVDS TX','子图帧行封装'])]:d.block(id,3030,y,260,80,ls,'white',[30,26])
    d.edge('roi-vdma-control','roi-scheduler','roi-vdma',[(3160,1295),(3160,1320)],'cfg')
    d.edge('vdma-pixels','roi-vdma','roi-fifo',[(3160,1400),(3160,1425)],'pixel')
    d.edge('fifo-lvds','roi-fifo','lvds-tx',[(3160,1505),(3160,1530)],'pixel')
    d.tag('C11',3250,1615)
    d.edge('llc-f0','llc-spm','front-F0',[(bottom[2]+105,1044),(bottom[2]+105,1095),(1950,1095),(1950,1156)])
    d.edge('mover-f1','gb-mover','front-F1',[(2166.25,405),(2215,405),(2215,540),(2960,540),(2960,1075),(2225,1075),(2225,1156)],dash=True)
    d.edge('frame-f2','frame-dma','front-F2',[(3281.25,340),(3300,340),(3300,1060),(2500,1060),(2500,1156)],dash=True)
    d.edge('roi-f3-request','roi-vdma','front-F3',[(3030,1345),(2975,1345),(2975,1105),(2760,1105),(2760,1156)])
    d.edge('f3-roi-read-data','front-F3','roi-vdma',[(2790,1156),(2790,1120),(2987,1120),(2987,1375),(3030,1375)],'gb')
    # Original page-3 PLL and C1-C9 positions are retained exactly.
    d.rect('pll',2126.25,1753.1,525,74,'orange',False,True)
    d.text('pll-title',2350,1800,'PLL / 时钟与复位分发',32,True,owner='pll');d.tag('C1',2580.25,1774.1)
    d.text('pll-interface',2930,1800,'RefClk / POR → clk_i / rst_ni',26,color='cfg')
    cfg=[('PLL / 时钟复位','配置 / 锁定 / 切换'),('DDR Controller','初始化 / QoS / 状态'),('DDR PHY','training / 校准'),('LVDS RX','通道 / 对齐 / 帧行'),('ISP','尺寸 / 模式 / 参数'),('NPU 计算','命令 / GB 数据位置'),('NPU / GB 搬运','地址 / 长度 / stride'),('帧写入 DMA','缓冲区 / 格式 / 帧状态'),('GB 管理','能力 / bank / 错误')]
    d.edge('regext-old-config','reg-ext','old-config-trunk',[(1726.25,1569),(1785,1569),(1785,1853.1)],'cfg',arrow=False)
    d.edge('old-config-trunk','old-config-trunk','old-config-trunk',[(238.75,1853.1),(3158.75,1853.1)],'cfg',arrow=False)
    d.dot(1785,1853.1,'cfg')
    for i,(title,desc) in enumerate(cfg):
        x=71.25+i*365;id='C'+str(i+1)
        d.rect('config-'+id,x,1878.1,335,100,'purple',False,True)
        d.text('config-'+id+'-title',x+185,1920,title,30,True,owner='config-'+id)
        d.text('config-'+id+'-desc',x+167.5,1960,desc,26,owner='config-'+id)
        config_tag(d,id,x+8,1887.1)
        d.edge('old-cfg-'+id,'old-config-trunk','config-'+id,[(x+167.5,1853.1),(x+167.5,1878.1)],'cfg')
    # Minimal legend to the right of the crossbar; no IRQ diagram wiring.
    for i,(kind,txt) in enumerate([('data','AXI 请求 / 返回'),('gb','GB / 读返回'),('pixel','像素 / eMMC'),('cfg','配置 / 控制')]):
        y=720+i*75
        d.edge('legend-'+kind,'legend','legend',[(3020,y),(3070,y)],kind,both=kind=='gb')
        d.text('legend-'+kind+'-text',3210,y+10,txt,26,color=kind)
    for b in d.boxes+d.regions:
        if b['id'] in MATCH:b['fill']=resolve_colour(fills[MATCH[b['id']]],theme)
    return d


def revise(input,overlay,output,fills):
    with ZipFile(input) as z:parts={n:z.read(n) for n in z.namelist()}
    root=E.fromstring(parts['ppt/slides/slide4.xml']);tree=root.find('p:cSld/p:spTree',NS)
    for el in list(tree):
        if E.QName(el).localname not in ['nvGrpSpPr','grpSpPr']:tree.remove(el)
    with ZipFile(overlay) as z:new=E.fromstring(z.read('ppt/slides/slide1.xml'))
    for el in new.find('p:cSld/p:spTree',NS):
        if E.QName(el).localname not in ['sp','cxnSp']:continue
        el=deepcopy(el);name=el.find('.//p:cNvPr',NS).get('name').split(': ')[0]
        if name in MATCH:
            sp=el.find('p:spPr',NS)
            for old in sp.findall('a:solidFill',NS):sp.remove(old)
            sp.insert(2,deepcopy(fills[MATCH[name]]))
        tree.append(el)
    # Only slide4 drawing changes: original masters, theme, relationships and other pages stay raw.
    parts['ppt/slides/slide4.xml']=E.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True)
    with ZipFile(output,'w',ZIP_DEFLATED) as z:
        for name,raw in parts.items():z.writestr(name,raw)


def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--native-skill-root',type=Path,required=True);a=p.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=False);fills,theme=source_colours(a.input);d=make(fills,theme);svg=a.out_dir/'slide-04.svg';d.save(svg)
    subprocess.run(['python3','-B',str(a.native_skill_root/'scripts/run.py'),'--input',str(svg),'--out-dir',str(a.out_dir/'native'),'--aspect','source','--slide-width-in',str(12192000/914400),'--font','Microsoft YaHei','--font-file','/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'],check=True)
    revise(a.input,a.out_dir/'native/diagrams.pptx',a.out_dir/'soc_landscape_m5_gb.pptx',fills)
    (a.out_dir/'colour_map.json').write_text(json.dumps({k:{'source_name':v,'rgb':resolve_colour(fills[v],theme),'fill_xml':E.tostring(fills[v]).decode()} for k,v in MATCH.items()},ensure_ascii=False,indent=2)+'\n')
    print('Generated revised slide 4 with inherited slide-3 fills.')

if __name__=='__main__':main()
