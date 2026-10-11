#!/usr/bin/env python3
"""Generate the two review SVGs; no RTL or external data is modified."""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parents[1] / 'figures'
OUT.mkdir(exist_ok=True)
COLORS = {'data': '#3574A8', 'control': '#7955A0', 'new': '#BE7127'}

class Figure:
    def __init__(self, width, height, title):
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<defs>']
        for key, color in COLORS.items():
            self.parts.append(f'<marker id="{key}" viewBox="0 0 3 3" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="{color}"/></marker>')
        self.parts += ['</defs>', f'<rect x="0" y="0" width="{width}" height="{height}" fill="#FFFFFF"/>']
        self.text(40, 45, title, 26, bold=True)

    def text(self, x, y, value, size=18, color='#20334A', bold=False, anchor='start'):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="WenQuanYi Zen Hei" font-size="{size}" font-weight="{"bold" if bold else "normal"}" text-anchor="{anchor}" fill="{color}">{escape(value)}</text>')

    def box(self, x, y, w, h, title, subtitle='', new=False, fill='#E8F1F8'):
        stroke = COLORS['new'] if new else COLORS['data']
        dash = ' stroke-dasharray="9 5"' if new else ''
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="2"{dash}/>')
        self.text(x+w/2,y+h/2+(0 if subtitle else 7),title,21,bold=True,anchor='middle')
        if subtitle:
            self.text(x+w/2,y+h/2+28,subtitle,16,anchor='middle')

    def arrow(self, points, kind='data', new=False, both=False):
        pts = ' '.join(f'{x},{y}' for x,y in points)
        dash = ' stroke-dasharray="9 5"' if new else ''
        start = f' marker-start="url(#{kind})"' if both else ''
        self.parts.append(f'<polyline points="{pts}" fill="none" stroke="{COLORS[kind]}" stroke-width="3" marker-end="url(#{kind})"{start}{dash}/>')

    def save(self, name):
        (OUT / name).write_text('\n'.join(self.parts+['</svg>'])+'\n')

f=Figure(1440,550,'当前实现：向量配置下的控制与存储路径')
f.box(45,115,190,85,'CVA6','通用计算 / 任务控制')
f.box(45,265,190,85,'Ara','向量执行 / 私有 VRF')
f.arrow([(140,200),(140,265)],'control')
f.text(160,239,'专用指令接口',16)
f.box(285,265,210,85,'失效过滤 / 位宽适配','仅 Ara → CPU L1D 失效')
f.arrow([(235,307),(285,307)])
f.box(555,115,185,235,'系统 AXI 互连','当前 64-bit')
f.arrow([(235,156),(555,156)])
f.arrow([(495,307),(555,307)])
f.box(320,405,175,80,'系统 iDMA','MMIO 提交 / 完成轮询')
f.arrow([(495,445),(648,445),(648,350)],both=True)
f.box(805,115,205,85,'原子适配 + LLC','LLC / SPM 共用 SRAM')
f.arrow([(740,156),(805,156)],both=True)
f.box(1080,115,305,85,'现有平台外存','FPGA DDR4 / 仿真存储模型')
f.arrow([(1010,156),(1080,156)],both=True)
f.box(805,265,205,85,'Regbus / 中断','Boot ROM / PLIC / CLINT')
f.arrow([(740,307),(805,307)],'control',both=True)
f.box(1080,265,305,85,'LVDS / ISP / NPU / 独立 GB','当前顶层尚无接入',new=True,fill='#FFF1E1')
f.text(45,525,'实线：当前 RTL 路径（启用条件见报告）    虚线框：待实现对象；无实线表示尚未接通',17)
f.save('current_implementation.svg')

f=Figure(1500,1000,'推荐首版集成关系：保留系统路径，限定共享存储与搬运职责')
f.box(45,115,175,90,'CVA6 / Ara','保留向量基线')
f.box(280,115,205,90,'系统 AXI 互连','控制 / 普通内存 / 外部窗口')
f.arrow([(220,160),(280,160)],both=True)
f.box(550,115,215,90,'原子适配 + LLC','普通 CPU / Ara 内存')
f.arrow([(485,160),(550,160)],both=True)
f.box(1030,115,200,345,'DDR 合流 / 适配','按交付端口组织',new=True,fill='#FFF1E1')
f.arrow([(765,160),(1030,160)],new=True,both=True)
f.box(1280,210,180,150,'DDR3 子系统','Controller + PHY',new=True,fill='#E5F3EF')
f.arrow([(1230,285),(1280,285)],new=True,both=True)
f.box(550,270,215,90,'静态不缓存共享区','同一 PA / 独立外部路由',new=True)
f.arrow([(485,180),(510,180),(510,315),(550,315)],new=True,both=True)
f.arrow([(765,315),(1030,315)],new=True,both=True)
f.box(280,490,235,110,'GB 访问与 bank 仲裁','首版系统侧用外部 AXI 从口',new=True,fill='#E5F3EF')
f.arrow([(383,205),(383,490)],new=True,both=True)
f.text(145,450,'CPU / Ara / iDMA 可达',16)
f.box(45,490,180,110,'独立 GB SRAM','容量 / 宏组织待定',new=True,fill='#E5F3EF')
f.arrow([(225,545),(280,545)],new=True,both=True)
f.box(595,490,210,110,'NPU 计算模块','Dremi 包含关系待确认',new=True,fill='#E5F3EF')
f.arrow([(515,545),(595,545)],new=True,both=True)
f.box(595,365,285,80,'NPU 数据搬运器','DDR ↔ GB；一个所有者',new=True,fill='#E5F3EF')
f.arrow([(595,405),(545,405),(545,515),(515,515)],new=True,both=True)
f.arrow([(880,405),(1030,405)],new=True,both=True)
f.box(45,780,180,85,'LVDS 接收','解析 / CDC / FIFO',new=True,fill='#FFF1E1')
f.box(285,780,180,85,'ISP','私有行缓冲优先',new=True,fill='#FFF1E1')
f.arrow([(225,822),(285,822)],new=True)
f.box(545,780,195,85,'帧边界选择','RAW / ISP 二选一',new=True,fill='#FFF1E1')
f.arrow([(465,822),(545,822)],new=True)
f.arrow([(245,822),(245,720),(643,720),(643,780)],new=True)
f.text(325,706,'RAW 支路',16)
f.box(820,780,220,85,'图像写入器','打包 / stride / AXI 响应',new=True,fill='#FFF1E1')
f.arrow([(740,822),(820,822)],new=True)
f.arrow([(1040,822),(1130,822),(1130,460)],new=True)
f.box(45,270,225,105,'新增 IP 控制 / 状态','外部 Regbus + PLIC IRQ',new=True,fill='#F1EBF6')
f.arrow([(330,205),(330,325),(270,325)],'control',new=True,both=True)
f.text(45,930,'实线：复用当前路径    虚线：本轮建议、尚未实现    双向箭头：读写访问能力',18)
f.text(45,963,'CPU 调度；控制/完成通知覆盖新增 IP。后续再评估 Ara 宽口直达 GB、ISP 共享 GB 和直接流式交接。',18)
f.save('recommended_integration.svg')
print('Generated current_implementation.svg and recommended_integration.svg')
