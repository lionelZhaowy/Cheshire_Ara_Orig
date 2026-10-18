#!/usr/bin/env python3
"""Generate the RTL-derived Regbus figure; refuse to overwrite an existing SVG."""
from pathlib import Path
from html import escape
import argparse

def build():
    elements = []
    dark, muted = '#29292D', '#606773'
    axi, reg, ctl = '#314D66', '#765489', '#187C78'
    def rect(id_, x, y, w, h, fill='#FFFFFF', dash=False, stroke=dark):
        d = ' stroke-dasharray="8 5"' if dash else ''
        elements.append(f'<rect id="{id_}" x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1.8"{d}/>')
    def text(id_, x, y, value, size=24, color=dark, bold=False, anchor='middle'):
        weight='bold' if bold else 'normal'
        elements.append(f'<text id="{id_}" x="{x}" y="{y}" font-family="Microsoft YaHei" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}">{escape(value)}</text>')
    def line(id_, points, color=reg, both=False, arrow=True):
        a = f' marker-end="url(#arrow-{color[1:]})"' if arrow else ''
        if both: a += f' marker-start="url(#arrow-{color[1:]})"'
        coords=' '.join(f'{x},{y}' for x,y in points)
        elements.append(f'<polyline id="{id_}" points="{coords}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linejoin="miter"{a}/>')
    def block(id_, x, y, w, h, lines, fill, dash=False, size=25):
        rect(id_,x,y,w,h,fill,dash)
        step=31
        first=y+h/2-(len(lines)-1)*step/2+8
        for i,s in enumerate(lines): text(f'{id_}-t{i}',x+w/2,first+i*step,s,size if i==0 else 21,bold=i==0)

    rect('background',0,0,2400,1350,stroke='#FFFFFF')
    text('title',55,65,'Cheshire 公共 Regbus 结构',40,bold=True,anchor='start')
    text('subtitle',55,103,'AXI 配置分支 → 协议转换 → 地址解码与寄存器访问分发',25,color=muted,anchor='start')
    rect('clock-domain',55,135,2290,840,'#FAF8FB',stroke='#645C5D')
    text('clock-label',85,174,'系统时钟域 clk_i  ·  桥与内部寄存器同域；解码／分发为组合逻辑；此路径无分频、无 CDC',25,anchor='start')

    block('xbar',90,220,360,110,['主 AXI Crossbar','i_axi_xbar','AxiOut.reg_demux'], '#F5E1C9')
    block('atomics',570,220,400,110,['原子适配','axi_riscv_atomics_structs','i_reg_atomics'], '#D8E8F4')
    block('cut',1090,220,340,110,['AXI 寄存器切片','i_reg_atomics_cut','RegAmoPostCut 可旁路'], '#D8E8F4')
    block('bridge',1550,220,620,110,['AXI → Regbus','i_axi_to_reg_v2','AxiDataWidth → 32 bit'], '#E8DFED')
    for id_,a,b in [('axi0',450,570),('axi1',970,1090),('axi2',1430,1550)]:
        line(id_,[(a,275),(b,275)],axi,both=True)
    line('reg-main',[(2170,275),(2310,275),(2310,700),(2290,700)],reg,both=True)
    text('reg-main-label',2205,308,'Reg',21,color=reg)
    # Address tap is taken from the bridge output, not from an unrelated config block.
    elements.append(f'<circle id="addr-tap" cx="2310" cy="367" r="4" fill="{reg}" stroke="{reg}" stroke-width="1"/>')
    line('addr-to-decode',[(2310,367),(320,367),(320,400)],ctl)
    text('addr-label',1500,357,'reg_in_req.addr',22,color=ctl)
    block('decode',90,400,460,87,['地址解码  i_reg_demux_decode','addr_decode · 未匹配 → RegOut.err'], '#D9EEE8',size=24)
    block('map',700,400,570,87,['静态地址规则 RegMap','gen_reg_out(Cfg) → gen_reg_map()'], '#FFFFFF',size=24)
    line('map-to-decode',[(700,443),(550,443)],ctl)
    line('select-to-demux',[(90,460),(72,460),(72,723),(90,723)],ctl)
    text('select-label',100,513,'选择控制：reg_select',21,color=ctl,anchor='start')
    text('bridge-cut-note',1630,433,'桥内 CutMemReqs = Cfg.RegAdaptMemCut',22,color=muted)
    text('bridge-width-note',1630,469,'地址宽度 = Cfg.AddrWidth（默认 48 bit）',22,color=muted)

    top=[
      ('bootrom','Boot ROM','bootrom',True),
      ('clint','CLINT','clint',False),
      ('plic','PLIC','plic',False),
      ('clic','CLIC','clic[i] · 每核一组',True),
      ('irq','IRQ Router','irq_router',True),
      ('rt','AXI RT 配置','axirt',True),
      ('soc','SoC 寄存器','regs',False),
      ('llc','LLC 配置','llc',True),
      ('buserr','Bus-error 记录','bus_err[j] · 2+核数',True),
    ]
    bottom=[
      ('uart','UART','uart',True),
      ('i2c','I2C','i2c',True),
      ('spi','SPI Host','spi_host',True),
      ('gpio','GPIO','gpio',True),
      ('slink','Serial Link 配置','slink',True),
      ('vga','VGA 配置','vga',True),
      ('usb','USB 配置','usb',True),
      ('error','错误响应','err · reg_err_slv',False),
      ('ext','外部 RegExt','ext_base + k',True),
    ]
    rect('demux',90,675,2200,90,'#E8DFED')
    text('demux-name',1200,710,'i_reg_demux  ·  单入口／多目标',30,bold=True)
    text('demux-behavior',1200,746,'请求仅送选中端口；响应从同一端口返回  ·  无事务 ID、无 burst、无独立读写通道',23)
    for row,items,y in [('top',top,525),('bottom',bottom,835)]:
        for i,(name,title,port,optional) in enumerate(items):
            x=90+i*247.5
            fill='#FFFFFF' if name!='error' else '#F1D7D9'
            block(name,x,y,220,90,[title,port],fill,optional,size=24)
            cy=x+110
            if row=='top': line(f'port-{name}',[(cy,675),(cy,615)],reg,both=True)
            else: line(f'port-{name}',[(cy,765),(cy,835)],reg,both=True)
    text('bottom-port-caption',100,954,'端口下标为 RegOut.<名称>；每个端口独立连接 reg_out_req[p] / reg_out_rsp[p]',21,color=reg,anchor='start')
    text('ext-note',2230,953,'同域接口；外部异步 IP 需适配',19,color=muted,anchor='end')

    rect('signals',55,1010,1115,180,'#F3F7FA')
    text('signals-title',85,1050,'Regbus 接口',27,bold=True,anchor='start')
    text('signals-req',85,1091,'请求：addr / write / wdata[31:0] / wstrb[3:0] / valid',24,anchor='start')
    text('signals-rsp',85,1130,'响应：rdata[31:0] / error / ready',24,anchor='start')
    text('signals-complete',85,1169,'上升沿 valid && ready：当前寄存器访问完成',24,anchor='start')
    rect('routing',1200,1010,1145,180,'#F3F7FA')
    text('routing-title',1230,1050,'两级地址路由',27,bold=True,anchor='start')
    text('routing-axi',1230,1091,'一级 AXI：原窗口 [0x0200_0000, 0x0c00_0000)',24,anchor='start')
    text('routing-ext',1230,1130,'RegExtRegion* 也由 AXI 表送入同一 Regbus 分支',24,anchor='start')
    text('routing-reg',1230,1169,'二级 Reg：按 RegMap 选目标；空洞转向错误响应',24,anchor='start')

    line('legend-axi',[(75,1240),(140,1240)],axi,both=True)
    text('legend-axi-t',155,1248,'AXI 请求／响应',22,anchor='start')
    line('legend-reg',[(420,1240),(485,1240)],reg,both=True)
    text('legend-reg-t',500,1248,'Regbus 请求／响应',22,anchor='start')
    line('legend-ctl',[(820,1240),(885,1240)],ctl)
    text('legend-ctl-t',900,1248,'地址／选择控制',22,anchor='start')
    rect('legend-optional',1200,1226,58,28,'#FFFFFF',True)
    text('legend-optional-t',1275,1248,'虚线：按 Cfg 条件生成的目标／扩展口',22,anchor='start')
    text('legend-scope',55,1305,'目标类别按 RTL 展开；不代表某一 FPGA 配置全部启用。iDMA 使用独立 AXI 配置目标，不在此公共分支。',23,color=muted,anchor='start')
    defs=[]
    for color in [axi,reg,ctl]:
        defs.append(f'<marker id="arrow-{color[1:]}" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="{color}"/></marker>')
    return '<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1350" viewBox="0 0 2400 1350">\n<defs>'+''.join(defs)+'</defs>\n'+'\n'.join(elements)+'\n</svg>\n'

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path(__file__).with_name('regbus_structure.svg'))
    args=parser.parse_args()
    with args.output.open('x',encoding='utf-8') as f: f.write(build())
    print(args.output)
