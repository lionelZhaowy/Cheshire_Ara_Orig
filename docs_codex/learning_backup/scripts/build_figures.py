#!/usr/bin/env python3
"""Generate repository-native SVG teaching diagrams; no renderer/CDN required."""
from pathlib import Path
from html import escape
OUT=Path(__file__).resolve().parent.parent/'assets'
COL={'data':'#136fa1','control':'#12836f','irq':'#9656b4'}
def diagram(name,title,nodes,edges,height=510,foot='教学示意 · 省略部分适配器、流水寄存器与响应通道；不代表逐周期行为'):
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 {height}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(foot)}</desc><defs>']
    for k,c in COL.items(): parts.append(f'<marker id="{k}" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="{c}"/></marker>')
    parts+=['</defs><rect width="1000" height="100%" fill="#fff"/>',f'<text x="25" y="32" font-size="21" font-weight="700" fill="#173749">{escape(title)}</text>']
    for key,(x,y,w,h,lines) in nodes.items():
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#eef5f7" stroke="#b5ccd7"/>')
        for i,line in enumerate(lines.split('|')):
            parts.append(f'<text x="{x+w/2}" y="{y+25+i*23}" text-anchor="middle" font-size="{16 if i==0 else 14}" fill="#193e50">{escape(line)}</text>')
    for pts,label,kind,tx,ty in edges:
        dash=' stroke-dasharray="7 4"' if kind=='control' else (' stroke-dasharray="2 4"' if kind=='irq' else '')
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{COL[kind]}" stroke-width="2.2"{dash} marker-end="url(#{kind})"/>')
        parts.append(f'<text x="{tx}" y="{ty}" text-anchor="middle" font-size="13" fill="{COL[kind]}" stroke="white" stroke-width="5" paint-order="stroke">{escape(label)}</text>')
    y=height-44
    for x,k,txt in [(25,'data','数据 / 事务'),(225,'control','控制 / 步骤'),(440,'irq','中断 / 失效通知')]:
        parts.append(f'<path d="M{x} {y}h38" stroke="{COL[k]}" stroke-width="2" marker-end="url(#{k})"/><text x="{x+48}" y="{y+5}" font-size="13" fill="#506777">{txt}</text>')
    parts.append(f'<text x="25" y="{height-12}" font-size="12" fill="#647681">{escape(foot)}</text></svg>')
    (OUT/f'{name}.svg').write_text(''.join(parts))

diagram('route','学习路线：先解释，再动手，再证明',{
'a':(30,80,260,75,'01 架构 + 02 基础|能画出 printf / load 的路径'),
'b':(370,80,260,75,'03 配置|分清编译、展开、运行时'),
'c':(710,80,260,75,'04 C → ELF → main|看懂入口、段、栈和退出'),
'd':(710,265,260,75,'05 仿真 + 实验 0—3|Hello / 数组 / ELF 检查'),
'e':(370,265,260,75,'06 访存 + 实验 4—7|MMIO / timer / DMA / RVV'),
'f':(30,265,260,75,'07 进阶导读|固定工程 / ASIC / AI 预算')},[
('290,117 370,117','概念 → 配置','control',330,104),('630,117 710,117','匹配软件','control',670,104),('840,155 840,265','编译产物 → 运行','control',840,213),('710,302 630,302','可重复闭环','control',670,289),('370,302 290,302','带着证据扩展','control',330,289)],430)

diagram('architecture','当前 Cheshire–CVA6–Ara 功能关系',{
'cpu':(25,75,260,95,'CVA6|标量 / CSR / MMU / L1|复位后取指'),
'ara':(365,75,260,95,'Ara|向量寄存器 / lanes / VLSU|不独立取指'),
'dma':(730,75,245,95,'iDMA / Debug|其他 AXI 发起者'),
'x':(235,260,530,58,'Cheshire AXI crossbar · 地址路由'),
'llc':(40,395,270,70,'原子适配器 → LLC/SPM|外部出口接存储模型或 DDR'),
'p':(365,395,270,70,'AXI → reg → 外设|UART / CLINT / PLIC / ROM'),
'e':(690,395,270,70,'外部扩展端口|是否存在取决于配置')},[
('285,110 365,110','指令 / 操作数 / 返回','control',325,97),('155,170 155,290 235,290','CPU AXI','data',155,238),('495,170 495,260','Ara AXI','data',540,220),('850,170 850,290 765,290','DMA / 调试 AXI','data',850,238),('355,318 175,395','主存事务','data',233,357),('500,318 500,395','寄存器事务','data',550,357),('660,318 820,395','扩展事务','data',790,354),('380,395 335,370 335,205 270,170','PLIC / CLINT → CPU IRQ','irq',370,230)],550)

diagram('config','配置生效：不存在一个开关替你修改所有层',{
'a':(25,70,270,85,'源文件与宏 · RTL 编译|唯一 CVA6 profile / decoder|ARA / NR_LANES / VLEN'),
'b':(365,70,270,85,'SoC 参数 · RTL 展开|SELCFG → Cfg.Ara / lanes|gen_cva6_cfg → build_config'),
'c':(705,70,270,85,'生成源与产物|HJSON → RTL + C 头|PLIC / CLINT / DMA 等'),
'd':(25,265,270,85,'软件编译与链接|-march / -mabi / *.ld|决定指令与地址'),
'e':(365,265,270,85,'实例化的硬件|CPU + Ara + 互连 + 存储|参数不能靠软件变更'),
'f':(705,265,270,85,'运行时状态|VS / FS / UART divisor|LLC way 用途 / DMA 长度')},[
('295,112 365,112','profile 输入','control',330,97),('500,155 500,265','展开','control',530,215),('840,155 620,265','尺寸须匹配','control',742,215),('295,305 365,305','人工对齐','control',330,290),('705,305 635,305','MMIO / CSR','control',670,289),('160,155 160,265','人工核对 ISA','control',170,215)],440)

diagram('lifecycle','程序生命周期：主机工具与目标执行分开',{
'a':(25,75,210,78,'lesson.c + 头文件|gcc -E → 预处理 C'),
'b':(270,75,210,78,'编译 + 汇编|-S / -c → .s / .o'),
'c':(515,75,210,78,'链接器 + crt0 + 库|*.ld → ELF / map'),
'd':(760,75,210,78,'ELF 检查|入口 / PT_LOAD / 指令'),
'e':(760,270,210,78,'DPI + VIP|解析文件 / JTAG SBA 写入'),
'f':(515,270,210,78,'SPM / DRAM|字节已放在链接地址'),
'g':(270,270,210,78,'CPU 执行 _start|清 BSS / main / printf'),
'h':(25,270,210,78,'可验收结果|UART + scratch2 + 校验')},[
('235,114 270,114','文本','data',252,100),('480,114 515,114','对象','data',497,100),('725,114 760,114','ELF','data',742,100),('865,153 865,270','BINARY 路径','control',865,215),('760,309 725,309','装载','data',742,296),('515,309 480,309','取指','data',497,296),('270,309 235,309','输出','data',252,296)],430)

diagram('reset','复位到 main：JTAG 直载与自主启动在这里分叉',{
'a':(25,75,270,75,'reset 释放|CPU PC → AmBrom 0x02000000'),
'b':(365,75,270,75,'Boot ROM 汇编|等 LLC BIST → 全 SPM|栈设在 SPM 高端'),
'c':(705,75,270,75,'Boot ROM main|按 boot_mode 选择路径'),
'd':(25,250,270,95,'JTAG 路径（本课）|VIP 等 SPM 标志，halt CPU|PT_LOAD → 内存，DPC → entry'),
'e':(365,250,270,95,'serial link / 自主路径|scratch[1:0] + scratch2&2|或 Flash/GPT 拷贝后跳转'),
'f':(705,250,270,95,'应用 crt0._start|栈 / gp / mtvec / BSS / FS|call 用户 main'),
'g':(705,415,270,70,'main 返回 → _exit|scratch2 编码返回值与完成位')},[
('295,112 365,112','复位取指','control',330,97),('635,112 705,112','call','control',670,97),('840,150 840,205 160,205 160,250','mode 0：调试加载','control',330,192),('840,205 500,205 500,250','按模式选择','control',580,192),('295,296 335,370 680,370 705,322','resume 至 ELF entry','control',497,390),('635,280 705,280','跳转','control',670,266),('840,345 840,415','运行 → 返回','control',891,383)],575, '教学时序示意 · 向下表示先后，不按比例；JTAG 改 DPC，不走 scratch 启动触发')

diagram('address','地址空间与 LLC/SPM：地址窗口 ≠ 物理容量',{
'a':(25,75,360,85,'0x02000000 / 0x03002000|Boot ROM / UART MMIO|寄存器路径，不是 DDR'),
'b':(25,205,360,85,'0x10000000—0x1001ffff|默认 128 KiB SPM 可缓存窗口|链接脚本默认仅用低 64 KiB'),
'c':(25,335,360,85,'0x14000000—0x1401ffff|同一 SPM 的非缓存别名|不是新增 128 KiB'),
'd':(625,205,340,85,'LLC 的同一组 SRAM 阵列|8 ways × 256 × 8 × 8 B|Boot ROM 初始化为全 SPM'),
'e':(625,75,340,85,'0x80000000—0xffffffff|外部主存路由窗口（2 GiB）|dram.ld 仅声明 8 MiB'),
'f':(625,335,340,85,'运行时可重配 LLC ways|cache / SPM / 混合|须迁走栈与活数据再重配')},[
('385,248 625,248','地址译码 → SPM','data',505,235),('385,378 510,378 510,275 625,275','减 0x04000000 映射','data',512,335),('790,160 790,205','主存访问经 LLC 路径','data',790,183),('790,335 790,290','配置 way 用途','control',790,322)],510)

diagram('coherence','CPU / Ara / DMA：共享总线不等于共享缓存',{
'a':(25,75,275,80,'CPU L1 D-cache|WB 标量 / WT 向量 profile|命中可不去下游'),
'b':(365,75,275,80,'Ara VLSU|写路径 axi_inval_filter|acc_cons_en 控制失效通知'),
'c':(705,75,270,80,'iDMA|独立读写通路|不自动经过 Ara 的 filter'),
'd':(290,265,420,75,'AXI crossbar → 原子适配器|原子适配器仅观察经过它的事务'),
'e':(290,400,420,75,'LLC / SPM → 外部存储|cache 可能保留数据与脏行')},[
('160,155 160,300 290,300','miss / 写事务','data',178,235),('500,155 500,265','向量访存','data',550,220),('840,155 840,300 710,300','DMA 事务','data',840,235),('365,110 300,110','L1 失效','irq',333,96),('500,340 500,400','主存 / SPM 数据','data',577,372)],555)

diagram('debug','仿真排错：找到最早失效的一层',{
'a':(25,75,270,72,'编译成功？|先看第一个 error / 缺文件'),
'b':(365,75,270,72,'展开 / DPI 成功？|唯一 profile / decoder / C++'),
'c':(705,75,270,72,'reset / ROM 在前进？|时钟 / PC / BIST / SPM'),
'd':(705,260,270,72,'ELF 已写入并 resume？|路径 / p_paddr / DPC / 栈'),
'e':(365,260,270,72,'main / UART 在前进？|mtvec / mcause / 波特率'),
'f':(25,260,270,72,'结果与退出正确？|gold / scratch2 / timeout')},[
('295,110 365,110','是 →','control',330,98),('635,110 705,110','是 →','control',670,98),('840,147 840,260','是 ↓','control',875,209),('705,295 635,295','是 →','control',670,282),('365,295 295,295','是 →','control',330,282)],425,'教学示意 · 任一节点为否：保留该阶段首错与上下文；不要跳到最后一条报错')

diagram('future','未来方案：控制、数据与中断分别设计（尚未实现）',{
'a':(25,75,250,80,'CVA6 / Ara|保留 SoC / LLC 路径'),
'b':(380,75,250,80,'ISP + NPU 控制寄存器|CPU 配置 / 状态 / doorbell'),
'c':(735,75,240,80,'中断控制器|完成 / 错误 → CPU'),
'd':(25,270,250,80,'传感器 → LVDS → ISP|采集 / 像素处理 / DMA'),
'e':(380,270,250,80,'脉动阵列 / NPU|tensor DMA + 片上缓冲'),
'f':(735,270,240,80,'DDR 前第二级互连|仲裁 / ID / 回压 / CDC'),
'g':(735,415,240,65,'外购 AXI4 DDR + PHY|初始化 / 存储 / 板外接口')},[
('275,110 380,110','MMIO 控制','control',327,98),('735,110 690,190 155,190 155,155','中断通知','irq',430,181),('505,155 505,270','配置任务','control',550,217),('505,155 150,270','配置图像流','control',264,217),('275,310 345,380 715,380 735,327','ISP DMA：绕过 LLC','data',478,399),('630,310 735,310','NPU DMA','data',682,296),('855,270 855,155','完成 / 错误','irq',900,215),('275,132 320,230 720,230 760,270','CPU/Ara 经 LLC → DDR','data',535,246),('855,350 855,415','AXI4 请求 / 响应','data',868,386)],570)

# Clock-edge table makes independent write channels and backpressure explicit.
parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 580" role="img" aria-labelledby="title"><title id="title">AXI 读写握手教学示意：只有 VALID 与 READY 同时为 1 才传输</title><rect width="1000" height="580" fill="white"/><text x="25" y="32" font-size="21" fill="#173749">AXI 五通道：每列表示一个上升沿采样值</text>']
rows=[('时钟沿','t0','t1','t2','t3','t4','t5'),('AWVALID / AWREADY','1 / 0','1 / 1','0 / 1','0 / 1','0 / 1','0 / 1'),('WVALID / WREADY','0 / 1','1 / 0','1 / 1','1 / 1','0 / 1','0 / 1'),('WDATA / WLAST','—','D0 / 0','D0 / 0','D1 / 1','—','—'),('BVALID / BREADY','0 / 1','0 / 1','0 / 1','0 / 1','1 / 1','0 / 1'),('ARVALID / ARREADY','1 / 1','0 / 1','0 / 1','0 / 1','0 / 1','0 / 1'),('RVALID / RREADY','0 / 1','1 / 0','1 / 1','1 / 1','0 / 1','0 / 1'),('RDATA / RLAST','—','Q0 / 0','Q0 / 0','Q1 / 1','—','—')]
for r,row in enumerate(rows):
    for c,txt in enumerate(row):
        x=25 if c==0 else 280+(c-1)*113; w=255 if c==0 else 113; y=62+r*46
        fill='#d9efe5' if txt=='1 / 1' else ('#eaf2f6' if r==0 or c==0 else '#fff')
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="46" fill="{fill}" stroke="#d5e1e8"/><text x="{x+12}" y="{y+29}" font-size="15" fill="#193e50">{txt}</text>')
for y,txt in [(465,'绿色格：本通道完成一次握手。AW 接受不表示写完成；等全部 W 与最后的 B。'),(495,'t1 的 W / R 被回压，发送端保持 VALID、数据与 LAST 到 t2；AW 与 W 独立。'),(525,'读：AR（地址）→ R（数据/响应）；写：AW（地址）+ W（数据）→ B（响应）。'),(555,'教学示意，不是真实仿真波形；两个事务独立，真实返回延迟、ID 与突发长度可不同。')]:
    parts.append(f'<text x="25" y="{y}" font-size="15" fill="#4b6779">{escape(txt)}</text>')
parts.append('</svg>');(OUT/'axi.svg').write_text(''.join(parts))
print('Built 10 SVG figures')

# A separate time axis for the default JTAG path; not a cycle-accurate waveform.
parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 720" role="img" aria-labelledby="title"><title id="title">reset 到 Boot ROM、crt0、main 的 JTAG 启动时序教学示意</title><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#12836f"/></marker></defs><rect width="1000" height="720" fill="white"/><text x="25" y="32" font-size="21" fill="#173749">JTAG 直载启动时序 · 时间向下，间隔不按比例</text>']
for x,label in [(125,'CVA6 / PC'),(375,'Boot ROM / 存储'),(625,'主机 VIP / JTAG'),(875,'应用 crt0 / main')]:
 parts.append(f'<rect x="{x-112}" y="58" width="224" height="46" rx="7" fill="#eaf2f6" stroke="#b5ccd7"/><text x="{x}" y="87" text-anchor="middle" font-size="17" fill="#193e50">{label}</text><path d="M{x} 104V620" stroke="#b9cbd5" stroke-dasharray="5 5"/>')
for x1,x2,y,msg in [(125,375,143,'reset → 取指 0x02000000'),(375,375,205,'等 BIST；全 SPM；设置栈'),(625,375,264,'轮询 LLC SPM 配置标志'),(625,125,321,'halt hart0'),(625,375,378,'SBA 写入 ELF 的 PT_LOAD'),(625,125,435,'写 DPC = ELF entry；resume'),(125,875,493,'执行应用 _start'),(875,875,551,'栈 / gp / BSS / FS → call main'),(875,625,609,'main 返回；scratch2 结束码')]:
 if x1==x2:
  parts.append(f'<path d="M{x1} {y-20}h45v20h-45" fill="none" stroke="#12836f" stroke-width="2" marker-end="url(#a)"/>')
  tx=x1-4;anchor='end'
 else:
  parts.append(f'<path d="M{x1} {y}H{x2}" fill="none" stroke="#12836f" stroke-width="2" marker-end="url(#a)"/>')
  tx=(x1+x2)/2;anchor='middle'
 parts.append(f'<text x="{tx}" y="{y-9}" text-anchor="{anchor}" font-size="14" fill="#126b60" stroke="white" stroke-width="4" paint-order="stroke">{escape(msg)}</text>')
parts.append('<text x="25" y="657" font-size="14" fill="#4b6779">箭头为控制先后 / 操作说明；存储写入和结束码读取实际经过调试、AXI 与 MMIO 路径。</text><text x="25" y="684" font-size="14" fill="#4b6779">教学示意，非真实波形。Flash/GPT 与 serial link 的入口交接见正文，不套用此 JTAG 时序。</text></svg>')
(OUT/'reset.svg').write_text(''.join(parts))
