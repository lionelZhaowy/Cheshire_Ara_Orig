"""L01: RTL teaching figures. Explicit topology, editable SVG, no RTL mutation.

Only the figures in this directory are generated. The two existing Regbus
figures are linked by the guide and copied into the combined export by export.sh.
"""
from pathlib import Path
from html import escape
import json
import math

OUT = Path(__file__).resolve().parent
FONT = 'WenQuanYi Zen Hei'
INK = '#23354B'
DATA = '#28699B'
CTRL = '#9C5B25'
IRQ = '#765096'
REG = '#E8F2EA'
LOGIC = '#EAF1F8'
STATE = '#FFF0DB'
MEM = '#F2EEF8'


class Figure:
    def __init__(self, name, title, height=980):
        self.name, self.height = name, height
        self.items = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="{height}" viewBox="0 0 1800 {height}">']
        self.labels, self.boxes, self.edges = [], [], []
        self.rect(0, 0, 1800, height, '#FFFFFF', stroke='none')
        self.text(40, 49, title, 32)

    def text(self, x, y, value, size=24, color=INK, anchor='start'):
        assert value.strip()
        self.items.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{escape(value)}</text>')
        self.labels.append(dict(x=x, y=y, text=value, size=size, anchor=anchor))

    def rect(self, x, y, w, h, fill='#FFFFFF', stroke=INK, dash=False):
        d = ' stroke-dasharray="9 6"' if dash else ''
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="2"{d}/>')

    def box(self, x, y, w, h, lines, fill=LOGIC, memory=False):
        self.rect(x, y, w, h, fill)
        self.boxes.append(dict(x=x, y=y, w=w, h=h, lines=lines))
        if memory:
            self.items.append(f'<line x1="{x+12}" y1="{y}" x2="{x+12}" y2="{y+h}" stroke="{INK}" stroke-width="1.5"/>')
        dy = 32
        top = y + h/2 - (len(lines)-1)*dy/2 + 8
        for i, line in enumerate(lines):
            self.text(x+w/2, top+i*dy, line, 24 if i == 0 else 22, anchor='middle')

    def arrow(self, points, color=DATA, dash=False, both=False):
        assert all(a[0]==b[0] or a[1]==b[1] for a,b in zip(points,points[1:])), points
        d = ' stroke-dasharray="8 5"' if dash else ''
        coords = ' '.join(f'{x},{y}' for x,y in points)
        self.items.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2.5"{d}/>')
        self.edges.append(dict(points=points, color=color, dash=dash))
        def head(a,b):
            x,y=b; dx=x-a[0]; dy=y-a[1]; n=math.hypot(dx,dy)
            ux,uy=dx/n,dy/n
            ps=[(x,y),(x-12*ux+5*uy,y-12*uy-5*ux),(x-12*ux-5*uy,y-12*uy+5*ux)]
            self.items.append(f'<polygon points="{" ".join(f"{px},{py}" for px,py in ps)}" fill="{color}"/>')
        head(points[-2],points[-1])
        if both: head(points[1],points[0])

    def ctl(self, points, color=CTRL):
        self.arrow(points,color,True)

    def dot(self,x,y,color=DATA):
        self.items.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>')

    def zone(self,x,y,w,h,label):
        self.rect(x,y,w,h,stroke='#9DAABA',dash=True)
        self.text(x+15,y+30,label,23,color='#56697F')

    def save(self):
        y=self.height-34
        self.arrow([(42,y-6),(118,y-6)])
        self.text(130,y,'数据 / 请求；双箭头含返回',22)
        self.ctl([(575,y-6),(655,y-6)])
        self.text(667,y,'配置 / 控制（标注 IRQ、使能时按标签）',22)
        self.text(1270,y,'编号与正文逐块对应',22,color='#56697F')
        (OUT/f'{self.name}.svg').write_text('\n'.join(self.items+['</svg>']))
        (OUT/f'{self.name}.layout.json').write_text(json.dumps(dict(labels=self.labels,boxes=self.boxes,edges=self.edges),ensure_ascii=False,indent=2))


def uart():
    f=Figure('01_uart','01  UART：寄存器访问与独立收发通路')
    f.text(415,140,'apb_uart 内部展开：CLK = clk_i；收发节拍由波特率计数器产生',23)
    f.box(40,360,285,135,['1  reg_uart_wrap','reg_to_apb','Regbus 32 → APB 32'])
    f.text(45,320,'Regbus 请求 / 响应',24)
    f.box(425,360,290,155,['2  APB 地址译码','PADDR = addr[4:2]','DLAB / THR / RBR','IER / IIR / LSR …'],REG)
    f.arrow([(325,425),(425,425)],both=True)
    f.box(790,185,310,120,['3  uart_baudgen','DLL / DLM → baud ticks'],STATE)
    f.ctl([(570,360),(570,245),(790,245)])
    f.box(790,390,270,120,['4  TX FIFO','slib_fifo：字节队列'],MEM,True)
    f.box(1180,390,330,120,['5  uart_transmitter','起始 / 数据 / 校验 / 停止'],STATE)
    f.arrow([(715,450),(790,450)])
    f.arrow([(1060,450),(1180,450)])
    f.arrow([(1510,450),(1730,450)])
    f.text(1570,424,'TX → 引脚',23)
    f.box(790,650,270,120,['7  RX FIFO','字节 + 接收错误位'],MEM,True)
    f.box(1180,650,330,120,['6  uart_receiver','采样 / 组字节 / 校验'],STATE)
    f.arrow([(1730,710),(1510,710)])
    f.text(1570,684,'RX ← 引脚',23)
    f.arrow([(1180,710),(1060,710)])
    f.arrow([(790,710),(575,710),(575,515)])
    f.text(596,628,'RBR 读出队头',22)
    f.ctl([(1100,245),(1350,245),(1350,390)])
    f.ctl([(1350,245),(1750,245),(1750,595),(1350,595),(1350,650)])
    f.dot(1350,245,CTRL)
    f.box(40,685,285,115,['8  uart_interrupt','状态 / IER → INT'],MEM)
    f.ctl([(790,770),(790,835),(182,835),(182,800)],IRQ)
    f.text(365,819,'收发状态汇入中断逻辑',22,IRQ)
    f.ctl([(425,490),(370,490),(370,740),(325,740)],IRQ)
    f.ctl([(182,685),(182,580)],IRQ)
    f.text(45,556,'IRQ → SoC 中断源',22,IRQ)
    f.save()


def i2c():
    f=Figure('02_i2c','02  I²C：命令 FIFO 驱动总线时序，接收 FIFO 返回字节')
    f.zone(370,130,1390,745,'i2c_core：Host 与 Target 使用不同队列；当前整合使用 clk_i')
    f.box(40,180,275,150,['1  i2c_reg_top','CONTROL / TIMING','FDATA / RDATA','INTR_STATE / ENABLE'],REG)
    f.text(40,140,'Regbus 32',24)
    f.box(410,220,330,125,['2  Host FMT FIFO','8-bit 字节 + 5-bit 标志','START / STOP / READ …'],MEM,True)
    f.arrow([(315,245),(410,245)])
    f.box(410,425,330,110,['4  Host RX FIFO','接收字节 → RDATA'],MEM,True)
    f.box(880,270,350,255,['3  i2c_fsm','SCL / SDA 时序状态机','Host / Target 控制','ACK / NAK / stretching','按 TIMING 寄存器计数'],STATE)
    f.arrow([(740,282),(800,282),(800,330),(880,330)])
    f.arrow([(880,480),(740,480)])
    f.arrow([(410,480),(175,480),(175,330)])
    f.box(1390,305,310,175,['5  SCL / SDA 接口','采样输入','输出值 + 输出使能','外层 PAD / 上拉另接'])
    f.arrow([(1230,390),(1390,390)],both=True)
    f.box(410,665,330,120,['6  Target TX FIFO','软件送字节 → 总线'],MEM,True)
    f.box(880,665,350,120,['7  Target ACQ FIFO','接收字节 + 事务标志'],MEM,True)
    f.arrow([(740,725),(795,725),(795,570),(950,570),(950,525)])
    f.arrow([(1090,525),(1090,665)])
    f.ctl([(175,180),(175,100),(1055,100),(1055,270)])
    f.text(585,92,'CONTROL / TIMING / FIFO reset',23,CTRL)
    f.box(1390,665,310,120,['8  prim_intr_hw × 事件','状态锁存 / 屏蔽 / 测试','15 路 IRQ → SoC'],MEM)
    f.ctl([(1230,450),(1320,450),(1320,725),(1390,725)],IRQ)
    f.ctl([(315,285),(350,285),(350,830),(1545,830),(1545,785)],IRQ)
    f.text(415,905,'Target 队列的软件读写也经 reg_top；图中省略其回线。',22)
    f.save()


def spi():
    f=Figure('03_spi','03  SPI Host：命令队列控制移位，数据窗口连接收发 FIFO')
    f.zone(755,150,1005,640,'spi_host_core：一个命令可以包含多个串行数据拍')
    f.box(40,175,300,145,['1  spi_host_reg_top','CONTROL / CONFIGOPTS','CSID / COMMAND','STATUS / INTR_*'],REG)
    f.text(40,130,'Regbus 32',24)
    f.box(415,180,275,130,['2  command_queue','方向 / 长度 / 速度','片选与时序配置'],MEM,True)
    f.arrow([(340,235),(415,235)])
    f.box(805,195,350,130,['3  spi_host_fsm','SCK / CS / sample / shift','CPOL / CPHA / 分频'],STATE)
    f.arrow([(690,245),(805,245)])
    f.box(40,455,300,155,['4  spi_host_window','TX 写窗口 / RX 读窗口','32-bit + byte enables','FIFO 满空由软件检查'])
    f.arrow([(190,320),(190,455)],both=True)
    f.box(410,435,290,115,['5  data_fifos：TX','32-bit 数据队列'],MEM,True)
    f.box(410,670,290,115,['9  data_fifos：RX','32-bit 接收字队列'],MEM,True)
    f.arrow([(340,490),(410,490)])
    f.arrow([(410,725),(190,725),(190,610)])
    f.box(805,435,350,115,['6  byte_select','32-bit → 有效发送字节'])
    f.box(805,670,350,115,['8  byte_merge','接收字节 → 32-bit'])
    f.arrow([(700,490),(805,490)])
    f.arrow([(805,725),(700,725)])
    f.box(1330,425,360,165,['7  shift_register','串 / 并转换','标准 / 双线 / 四线','SD[3:0] 输入 / 输出 / OE'],STATE)
    f.arrow([(1155,490),(1330,490)])
    f.arrow([(1510,590),(1510,725),(1155,725)])
    f.ctl([(1155,260),(1510,260),(1510,425)])
    f.text(1250,242,'SCK / CS 与移位节拍',22,CTRL)
    f.text(90,862,'IRQ：ERROR / SPI_EVENT；片选数量、FIFO 深度和字节顺序以当前参数为准。',24)
    f.save()


def gpio():
    f=Figure('04_gpio','04  GPIO：输入滤波、边沿检测与独立的输出值 / 输出使能')
    f.box(40,200,290,125,['GPIO 输入 32 路','gpio_i[31:0]'])
    f.box(435,175,340,155,['1  prim_filter_ctr × 32','可选输入同步','可选计数滤波','DATA_IN → 软件'],STATE)
    f.arrow([(330,260),(435,260)])
    f.box(895,180,340,145,['2  data_in_q + 比较','上升沿 / 下降沿','高电平 / 低电平'],STATE)
    f.arrow([(775,260),(895,260)])
    f.box(1370,180,355,145,['3  prim_intr_hw','事件状态 + enable/test','32 路 intr_gpio_o'],MEM)
    f.ctl([(1235,260),(1370,260)],IRQ)
    f.box(440,565,370,215,['4  gpio_reg_top','DIRECT_OUT / DIRECT_OE','MASKED_OUT / MASKED_OE','INTR_CTRL / STATE','INPUT_FILTER / DATA_IN'],REG)
    f.text(50,613,'Regbus 请求 / 响应',24)
    f.box(1030,570,345,90,['5  cio_gpio_q[31:0]'],MEM,True)
    f.box(1030,715,345,90,['6  cio_gpio_en_q[31:0]'],MEM,True)
    f.arrow([(810,620),(1030,620)])
    f.arrow([(810,745),(1030,745)])
    f.arrow([(1375,620),(1720,620)])
    f.text(1440,598,'输出值 → PAD',23)
    f.arrow([(1375,760),(1720,760)])
    f.text(1420,735,'输出使能 → PAD',23)
    f.ctl([(605,565),(605,330)])
    f.ctl([(735,565),(735,430),(1065,430),(1065,325)])
    f.ctl([(810,680),(860,680),(860,480),(1545,480),(1545,325)],IRQ)
    f.text(1000,465,'中断使能 / 清除 / 测试',22,IRQ)
    f.text(45,870,'MASKED 写：掩码选中哪些位，只更新这些位；输入、输出值和输出使能是三条不同路径。',24)
    f.save()


def plic():
    f=Figure('05_plic','05  PLIC：源侧 pending / active 与目标侧优先级选择')
    f.box(40,205,280,140,['外设 IRQ 电平','经 IRQ Router','PLIC 目标分支'])
    f.box(420,205,300,140,['1  prim_flop_2sync','同步输入','本集成按电平触发'])
    f.arrow([(320,275),(420,275)])
    f.box(835,180,350,190,['2  rv_plic_gateway','每源 pending：ip','每源 active：ia','claim 清 pending','complete 允许再触发'],STATE)
    f.arrow([(720,275),(835,275)])
    f.box(1345,180,385,190,['3  rv_plic_target × 目标','pending & enable','priority > threshold','选择获胜源 / 产生 IRQ'],STATE)
    f.arrow([(1185,275),(1345,275)])
    f.ctl([(1535,370),(1535,470)],IRQ)
    f.text(1490,500,'xeip → hart',24,IRQ)
    f.text(1490,536,'M / S 外部中断',22,IRQ)
    f.box(410,655,775,180,['4  rv_plic_reg_top','源 priority；每目标 enable / threshold','读 claim → 源 ID；写 complete ← 已处理 ID','源 ID = 0 保留；设备自身状态需驱动清除'],REG)
    f.text(440,615,'Regbus 请求 / 响应',24)
    f.ctl([(1070,655),(1070,535),(1010,535),(1010,370)])
    f.text(760,510,'claim / complete',23,CTRL)
    f.arrow([(1410,370),(1410,570),(1140,570),(1140,655)])
    f.text(1210,594,'获胜源 ID',22)
    f.ctl([(1185,760),(1695,760),(1695,370)])
    f.text(1320,801,'priority / enable / threshold',23,CTRL)
    f.save()


def clint():
    f=Figure('06a_clint','06A  CLINT：RTC 边沿变为计数使能；比较器产生定时中断')
    f.zone(370,145,1375,690,'clint：寄存器、计数器和比较器均在 clk_i / rst_ni 域')
    f.text(70,270,'rtc_i',28)
    f.arrow([(65,300),(415,300)])
    f.box(415,235,340,140,['1  clint_sync_wedge','同步 + 上升沿检测','increase_timer：一拍使能'],STATE)
    f.box(900,235,350,140,['2  MTIME[63:0]','寄存器反馈 + 加 1','仅 RTC 上升沿使能更新'],MEM,True)
    f.ctl([(755,300),(900,300)])
    f.box(1380,250,220,120,['3  ≥ 比较','无条件保持比较'],STATE)
    f.arrow([(1250,300),(1380,300)])
    f.ctl([(1600,300),(1720,300),(1720,420)],IRQ)
    f.text(1570,463,'MTIP → hart',24,IRQ)
    f.box(900,525,350,120,['4  MTIMECMP[63:0]','每 hart 一个比较值'],MEM,True)
    f.arrow([(1250,585),(1490,585),(1490,370)])
    f.box(415,555,340,165,['5  clint_reg_top','MTIME_LO / HI','MTIMECMP_LO / HI','MSIP'],REG)
    f.text(70,630,'Regbus 32',25)
    f.arrow([(65,665),(415,665)],both=True)
    f.arrow([(755,600),(900,600)])
    f.arrow([(705,555),(705,440),(990,440),(990,375)],both=True)
    f.box(1380,675,250,100,['6  MSIP 位','软件置位 / 清零'],MEM,True)
    f.arrow([(755,690),(835,690),(835,760),(1380,760),(1380,725)])
    f.ctl([(1630,725),(1720,725)],IRQ)
    f.text(1400,810,'MSIP → hart',24,IRQ)
    f.text(45,890,'MTIP 的清除方法是让 MTIMECMP 大于 MTIME；这里没有 PLIC claim / complete。',24)
    f.save()


def clic():
    f=Figure('06b_clic','06B  CLIC：每个 hart 的中断选择器与 CPU 握手接口')
    f.box(40,190,365,215,['1  clic_intr 输入拼装','IRQ Router 的本 hart 分支','MEIP / SEIP（来自 PLIC）','MTIP / MSIP（来自 CLINT）','保留源按 SoC 定义连接'])
    f.box(570,205,330,190,['2  clic_gateway','电平 / 边沿 pending','软件置 pending','来自 target 的 claim'],STATE)
    f.arrow([(405,300),(570,300)])
    f.box(1070,205,335,190,['3  clic_target','pending / enable','level / priority / mode','选择待提交中断'],STATE)
    f.arrow([(900,300),(1070,300)])
    f.arrow([(1160,395),(1160,470),(735,470),(735,395)],CTRL)
    f.text(895,456,'claim',23,CTRL)
    f.box(1505,175,255,245,['4  CVA6 CLIC 接口','valid / ready','id / level','shv / priv','kill_req / kill_ack'],MEM)
    f.arrow([(1405,280),(1505,280)],both=True)
    f.box(555,640,865,180,['5  mclic_reg_top + clicint_reg_top × 源','全局配置：level / priority 的划分','每源配置：pending / enable / attr / ctl','Regbus → reg_adapter → 对应寄存器'],REG)
    f.text(45,565,'Cfg.Clic 控制生成',23)
    f.ctl([(725,640),(725,520),(625,520),(625,395)])
    f.ctl([(1215,640),(1215,395)])
    f.text(45,865,'CLIC 不产生 RTC 计数；CPU 接受中断的握手也不等于清除了外设事件。',24)
    f.save()


def router():
    f=Figure('07_irq_router','07  IRQ Router：每条源中断对应一个目标位掩码')
    f.box(45,180,315,180,['1  intr 源向量','片内外设 IRQ','外部 IRQ 经 sync','源 0 固定为 0'])
    f.box(485,195,330,145,['2  irqs_cloned','每个目标一份源向量','组合逻辑复制'])
    f.arrow([(360,270),(485,270)])
    f.box(1000,180,285,180,['3  按位 AND','out[target][source]','= src[source]','& mask[source][target]'],STATE)
    f.arrow([(815,270),(1000,270)])
    f.arrow([(1285,225),(1415,225)])
    f.arrow([(1285,275),(1415,275)])
    f.arrow([(1285,325),(1415,325)])
    f.text(1435,231,'target 0 → PLIC',24)
    f.text(1435,281,'target 1… → 各 hart CLIC',24)
    f.text(1435,331,'后续 target → 外部输出',24)
    f.box(450,595,470,195,['4  irq_router_reg_top × 源','每源一个 IRQ_TARGET_MASK','地址低位 addr[15:2] 选择源','复位 mask = 1：仅 target 0'],REG)
    f.text(455,548,'Regbus 请求 / 响应',24)
    f.ctl([(920,690),(1140,690),(1140,360)])
    f.text(1170,536,'掩码重排为目标 × 源',23,CTRL)
    f.text(55,870,'Cfg.IrqRouter = 0 时：绕过掩码，原始源向量复制给各目标；模块没有 pending 或优先级队列。',24)
    f.save()


def bootrom():
    f=Figure('08_bootrom','08  BootROM：组合 ROM 内容与 Regbus 应答延迟')
    f.zone(365,155,1375,565,'Cfg.Bootrom 生成分支；clk_i / rst_ni')
    f.text(45,280,'Regbus 32',25)
    f.box(405,230,345,195,['1  reg_to_mem','地址截为 16-bit','req / we / addr','gnt = req','rvalid / rerror 返回'])
    f.arrow([(50,330),(405,330)],both=True)
    f.box(900,220,400,195,['2  cheshire_bootrom','word = addr / 4','case(word) → data[31:0]','当前生成内容：2048 words','组合查表；clk / rst 未用'],MEM,True)
    f.arrow([(750,280),(900,280)])
    f.box(1440,220,245,195,['3  FF 延迟对齐','data_q ← data','req_q ← req','we_q ← we'],MEM,True)
    f.arrow([(1300,280),(1440,280)])
    f.ctl([(750,380),(815,380),(815,480),(1560,480),(1560,415)])
    f.text(1020,468,'req / we 同步延迟',22,CTRL)
    f.arrow([(1440,350),(1370,350),(1370,595),(585,595),(585,425)])
    f.text(835,575,'rdata = data_q；rvalid = req_q；rerror = we_q',23)
    f.text(60,795,'软件源 .S / .c → 链接与 ROM 生成脚本 → cheshire_bootrom.sv 常量内容',26)
    f.text(60,851,'写访问返回错误；16-bit 接口窗口不等于 64 KiB 唯一 ROM 内容。',24)
    f.save()


def socregs():
    f=Figure('09_soc_regs','09  SoC Regs：软件 scratch 与只读硬件能力信息')
    f.box(40,340,310,160,['Regbus 32 请求','addr / write / wstrb','wdata / valid'])
    f.box(480,195,430,185,['1  地址与访问译码','cheshire_reg_top','reg_we / reg_re','字节写使能 / 未命中错误'],STATE)
    f.arrow([(350,400),(410,400),(410,285),(480,285)])
    f.box(1100,155,615,165,['2  scratch[0…15]','prim_subreg：16 × 32-bit RW','保存软件数据；复位为 0；不是 SRAM'],MEM,True)
    f.arrow([(910,250),(1100,250)])
    f.box(1100,460,615,195,['3  硬件只读字段','boot_mode_i；RtcFreq；PlatformRom','NumIntHarts；HW_FEATURES；LLC_SIZE','VGA RGB 位宽','来自 SoC 的 hw2reg 连线'],REG)
    f.box(480,630,430,155,['4  读回选择 / 响应','rdata = 地址选中值','ready = 1；error = 非法访问'])
    f.arrow([(1200,320),(1200,395),(970,395),(970,680),(910,680)])
    f.arrow([(1100,570),(1020,570),(1020,735),(910,735)])
    f.ctl([(690,380),(690,630)])
    f.arrow([(480,710),(195,710),(195,500)])
    f.text(45,793,'rdata / error / ready',24)
    f.text(60,865,'功能位描述当前综合配置，不是动态电源开关，也不是 PLL 或 DDR 初始化控制器。',24)
    f.save()


def jtag():
    f=Figure('10_jtag_debug','10  JTAG Debug：DMI 控制、hart 调试与系统总线访问')
    f.box(40,185,270,155,['JTAG 引脚','TCK / TMS / TDI','TDO / TRSTn'])
    f.box(430,175,390,175,['1  dmi_jtag','JTAG TAP / DTM','DMI 请求 / 响应跨域','TCK 域 ↔ clk_i 域'],STATE)
    f.arrow([(310,265),(430,265)],both=True)
    f.box(975,160,375,205,['2  dm_top','dm_csrs：DMI 配置','dm_mem：调试执行存储窗','dm_sba：系统总线访问','dmactive → dbg_active_o'],REG)
    f.arrow([(820,265),(975,265)],both=True)
    f.text(855,243,'DMI',23)
    f.box(1485,175,265,175,['3  hart 调试入口','debug_req','执行 debug ROM','访问程序缓冲区'],MEM)
    f.ctl([(1350,250),(1485,250)],IRQ)
    f.box(1010,610,375,170,['4  axi_from_mem','SBA req / gnt / rvalid','→ AXI master','AxiIn.dbg'])
    f.arrow([(1175,365),(1175,610)],both=True)
    f.arrow([(1195,780),(1195,860),(1720,860)],both=True)
    f.text(1410,841,'访问系统地址空间',23)
    f.box(430,605,390,185,['5  调试存储窗适配','AXI atomics / cut','axi_to_mem_interleaved','→ dm_top.slave_*','供 hart 执行调试代码'])
    f.arrow([(40,690),(430,690)],both=True)
    f.text(45,650,'AxiOut.dbg',24)
    f.arrow([(625,605),(625,465),(1030,465),(1030,365)],both=True)
    f.text(45,864,'当前 ndmreset_o 未接出；不能由 DMI 寄存器存在就推断 SoC 复位已实现。',24)
    f.save()


def serial():
    f=Figure('11_serial_link','11  Serial Link：AXI 通道编码、流控与源同步物理传输')
    f.box(40,185,335,190,['1  SoC 外层适配','出站地址 domain / mask','axi_id_remap','AMO 标记适配','对端入站 → 本地 AXI'])
    f.box(500,185,365,190,['2  serial_link_network','AXI AW / W / B / AR / R','通道仲裁 / 封装 / 还原','AXI ↔ payload stream'])
    f.arrow([(375,280),(500,280)],both=True)
    f.box(1000,185,345,190,['3  serial_link_data_link','接收缓冲 / 流控','payload 拆分 / 重组','raw mode 支路'],STATE)
    f.arrow([(865,280),(1000,280)],both=True)
    f.box(1440,195,320,170,['4  channel_allocator','NumChannels > 1 时','分配与还原通道','单通道直接连接'])
    f.arrow([(1345,280),(1440,280)],both=True)
    f.box(1260,600,475,180,['5  serial_link_physical × 通道','发送时钟分频 / 相位控制','DDR 引脚收发 / 接收跨域','ddr_rcv_clk + ddr 数据 lanes'],STATE)
    f.arrow([(1600,365),(1600,600)],both=True)
    f.arrow([(1485,780),(1485,870)],both=True)
    f.text(1145,905,'外部串行链路；此处 DDR 指双边沿传输',23)
    f.box(465,620,540,160,['6  serial_link_reg_top','Regbus → 可选 reg_cdc → 配置','TX clk_div / raw mode / FIFO 控制','当前 SoC 的三路逻辑时钟都接 clk_i'],REG)
    f.ctl([(1005,695),(1260,695)])
    f.ctl([(735,620),(735,485),(1170,485),(1170,375)])
    f.text(45,855,'AXI 事务跨芯片传输，不是 UART，也不自动提供缓存一致性。',24)
    f.save()


def vga():
    f=Figure('12_vga','12  VGA：AXI 读取帧缓冲，再按像素节拍消耗数据')
    f.box(40,180,345,185,['1  axi_vga_reg_top','START_ADDR / FRAME_SIZE','BURST_LEN / ENABLE','水平 / 垂直时序','CLK_DIV'],REG)
    f.text(45,130,'Regbus 32',24)
    f.box(505,185,360,175,['2  axi_vga_fetcher','地址 / 长度状态机','拆取 RGB 像素','保持 beat / pixel offset'],STATE)
    f.ctl([(385,250),(505,250)])
    f.box(1040,185,370,175,['3  timing_fsm','水平 / 垂直计数','可见区与消隐区','消费像素 valid / ready'],STATE)
    f.arrow([(865,280),(1040,280)])
    f.text(875,260,'RGB',23)
    f.arrow([(1410,265),(1720,265)])
    f.text(1450,244,'RGB / HS / VS',23)
    f.box(505,630,360,150,['4  axi_burst_splitter','把请求拆成单拍事务','信用计数限制在途读取'])
    f.arrow([(620,360),(620,630)])
    f.text(642,483,'AR 请求',23)
    f.box(1040,630,370,150,['5  R 通道 FIFO','BufferDepth + 1','缓冲存储器返回数据'],MEM,True)
    f.arrow([(865,700),(975,700),(975,860),(1720,860)])
    f.text(1120,886,'AR → 内存',23)
    f.arrow([(1720,710),(1410,710)])
    f.text(1490,684,'R ← 内存',23)
    f.arrow([(1040,720),(865,720)])
    f.arrow([(765,630),(765,360)])
    f.text(782,563,'返回 beat',22)
    f.ctl([(385,315),(435,315),(435,435),(1230,435),(1230,360)])
    f.text(990,475,'clk_cnt_q == 0 → fsm_en',23,CTRL)
    f.text(45,850,'同一个 clk_i 域；CLK_DIV 控制像素状态机使能。',23)
    f.save()


def usb():
    f=Figure('13_usb','13  USB OHCI：控制适配、描述符 DMA 与独立 PHY 时钟域')
    f.zone(385,115,1360,720,'spinal_usb_ohci：控制 / DMA 在 soc_clk_i；PHY 使用 phy_clk_i')
    f.box(35,185,275,140,['Regbus 32','ctrl_req / ctrl_rsp'])
    f.box(420,185,330,140,['1  reg_to_axi','32-bit Reg → AXI32','控制地址取低 12 位'])
    f.arrow([(310,255),(420,255)],both=True)
    f.box(895,185,410,190,['2  UsbOhciAxi4：前端','ctrlBridge → front_ohci','OHCI 寄存器 / 帧调度','读取 ED / TD、搬运数据','完成状态 / IRQ'],STATE)
    f.arrow([(750,255),(895,255)],both=True)
    f.box(420,595,395,150,['5  AXI DMA 适配','axi_dw_converter：32 → 系统','axi_modify_address','32-bit 地址 domain / mask'])
    f.arrow([(895,340),(860,340),(860,665),(815,665)],both=True)
    f.arrow([(420,665),(55,665)],both=True)
    f.text(50,627,'AXI DMA ↔ 内存',23)
    f.box(945,580,365,165,['3  CtrlCc','命令 / 数据 / 状态跨域','生成 RTL 的握手同步','两域分别复位'],MEM)
    f.arrow([(1125,375),(1125,580)],both=True)
    f.box(1415,575,280,175,['4  UsbLsFsPhy','数字收发逻辑','LS / FS；4 个端口','DP / DM + OE'],STATE)
    f.arrow([(1310,665),(1415,665)],both=True)
    f.ctl([(1305,255),(1570,255)],IRQ)
    f.text(1370,233,'intr_o → SoC',23,IRQ)
    f.arrow([(1570,750),(1570,880)],both=True)
    f.text(1180,908,'PAD / 电气 / VBUS 由平台实现',23)
    f.text(45,866,'DMA 内核地址为 32-bit；系统 AXI 更宽不会自动解除这一限制。',24)
    f.save()


def idma():
    f=Figure('14_idma','14  iDMA：AXI 控制入口、任务前端与独立搬运后端')
    f.box(35,185,275,165,['AXI slave 控制口','AxiOut.dma','atomics / cut','CPU 发起配置访问'])
    f.box(420,185,320,165,['1  axi_to_reg','i_axi_translate','内部 Reg 数据宽度','随 AxiDataWidth'])
    f.arrow([(310,270),(420,270)],both=True)
    f.box(850,175,405,190,['2  idma_reg64_1d / 2d','SRC / DST / LENGTH','STRIDE / REPS（2D）','NEXT_ID / DONE_ID','访问触发任务提交'],REG)
    f.arrow([(740,270),(850,270)],both=True)
    f.box(1390,175,365,190,['3  Job FIFO + midend','队列缓冲传输请求','2D：idma_nd_midend','展开为一维传输'],MEM,True)
    f.arrow([(1255,270),(1390,270)])
    f.box(995,575,595,210,['4  idma_backend_rw_axi','legalizer：长度 / 地址 / burst 合法化','transport：读数据、移位 / 缓冲、写数据','独立 AXI read / write 通道','当前 ErrorCap = NO_ERROR_HANDLING'],STATE)
    f.arrow([(1570,365),(1570,575)])
    f.box(420,610,395,135,['5  axi_rw_join','合并 AXI 读写端口','AXI master → AxiIn.dma'])
    f.arrow([(995,665),(815,665)],both=True)
    f.arrow([(420,675),(55,675)],both=True)
    f.text(50,637,'AXI ↔ SRC / DST 内存',23)
    f.box(455,420,340,110,['6  transfer_id_gen','issue / retire → ID'],MEM)
    f.ctl([(1390,315),(1330,315),(1330,470),(795,470)])
    f.ctl([(1120,575),(1120,530),(795,530),(795,505)])
    f.arrow([(625,420),(625,395),(970,395),(970,365)])
    f.text(45,865,'既有控制宽度缺口未关闭；wrapper 未导出任务完成 IRQ；总线错误 IRQ 是另一路。',24)
    f.save()


def traps():
    f=Figure('15_interrupt_exception','15  CVA6 Trap：异步中断与同步异常在提交路径汇合')
    f.box(40,165,330,180,['1  平台中断输入','PLIC：irq_i（M / S）','CLINT：time_irq_i / ipi_i','可选 CLIC 握手'])
    f.box(480,155,395,200,['2  csr_regfile','pending / enable / 委托','mip / mie / mstatus …','trap 状态：epc / cause / tval','trap_vector_base / eret'],REG)
    f.ctl([(370,245),(480,245)],IRQ)
    f.box(1030,155,350,200,['3  decoder / id_stage','结合特权级与 IRQ 控制','选出可接受的中断','或生成译码异常','写入指令的 ex 信息'],STATE)
    f.ctl([(875,245),(1030,245)],IRQ)
    f.box(1480,175,280,160,['4  scoreboard','指令与结果关联','ex 随指令保存'],MEM,True)
    f.arrow([(1380,245),(1480,245)])
    f.box(1470,565,295,180,['5  commit_stage','按提交顺序选异常','阻止错误指令提交','ex_commit → CSR'],STATE)
    f.arrow([(1620,335),(1620,565)])
    f.box(980,580,330,155,['执行 / 访存异常','非法操作 / 访问故障等','结果携带 exception_t'])
    f.arrow([(1145,580),(1145,440),(1550,440),(1550,335)])
    f.arrow([(1570,745),(1570,805),(930,805),(930,400),(775,400),(775,355)])
    f.text(1090,837,'ex_commit / PC',23)
    f.box(450,590,370,160,['6  controller + frontend','flush 错误路径流水线','PC 转向 trap 入口','xRET 恢复返回 PC'],STATE)
    f.ctl([(590,355),(590,590)])
    f.arrow([(450,665),(60,665)])
    f.text(50,626,'CPU 开始执行处理程序',23)
    f.text(45,865,'图中软件处理程序不在硬件中：保存现场、处理设备 / 控制器、恢复现场，再执行返回指令。',24)
    f.save()


def llc():
    f=Figure('16a_llc','16A  LLC：描述符命中 / 缺失路径与共享数据 SRAM')
    f.box(35,185,340,180,['1  isolate / demux','入口隔离与 bypass','chan_splitter / 仲裁','AW / AR → 描述符'])
    f.box(510,185,340,180,['2  axi_llc_hit_miss','tag_store / valid / dirty','锁定与同 ID 顺序约束','cache 或 SPM 地址判定'],STATE)
    f.arrow([(375,265),(510,265)])
    f.box(1010,185,335,180,['3  evict → refill','必要时写回脏行','从外存补入 cache line','完成后传递描述符'],STATE)
    f.arrow([(850,305),(1010,305)])
    f.text(875,289,'miss',23)
    f.box(1455,185,300,180,['4  merge_unit','汇合命中 / 补入路径','分发 read / write'])
    f.arrow([(1345,285),(1455,285)])
    f.arrow([(680,185),(680,105),(1605,105),(1605,185)])
    f.text(890,92,'hit / SPM 快路径（仍受顺序约束）',23)
    f.box(1395,565,355,145,['5  read_unit / write_unit','连接 AXI R / W / B','访问选定的数据 way'])
    f.arrow([(1610,365),(1610,565)])
    f.box(750,570,470,180,['6  axi_llc_ways','read / write / evict / refill 仲裁','每个 way 的 SRAM','按地址、way、byte strobe 访问'],MEM,True)
    f.arrow([(1395,640),(1220,640)],both=True)
    f.arrow([(1175,365),(1175,570)],both=True)
    f.box(40,615,420,130,['7  AXI 外存出口','bypass 与 refill / evict','经 axi_bypass_mux 汇合'])
    f.arrow([(117,365),(117,615)],both=True)
    f.text(135,495,'bypass',23)
    f.arrow([(1010,345),(935,345),(935,465),(350,465),(350,615)],both=True)
    f.text(480,446,'外存读 / 写',23)
    f.text(45,865,'实线表示描述符或数据路径，标签区分；图中省略返回 ID 队列与逐通道握手。',24)
    f.save()


def spm():
    f=Figure('16b_spm','16B  LLC / SPM：相同 SRAM 的 way 分配与配置提交')
    f.box(40,175,390,190,['1  axi_llc_reg_top','CFG_SPM / CFG_FLUSH','COMMIT_CFG / FLUSHED','BIST / 容量 / 版本','当前控制接口：Regbus'],REG)
    f.box(590,175,430,190,['2  axi_llc_config','提交新配置 / 停止接收新事务','等待在途工作 / 发 flush 描述符','必要时写回脏行','更新 spm_lock / flushed'],STATE)
    f.arrow([(430,260),(590,260)],both=True)
    f.box(1170,175,565,190,['3  地址与 way 选择','cache 地址：tag lookup → cache way','SPM 地址：直接选择被锁定的 way','未配置为 SPM 的对应 way 不可当 RAM 用','SPM 访问不进行外存 refill'],STATE)
    f.ctl([(1020,260),(1170,260)])
    f.zone(610,515,1125,280,'4  同一组数据 SRAM：下图仅为分区示例，不代表当前运行配置')
    for i in range(4):
        x=645+265*i
        f.box(x,585,240,155,[f'way {i}', 'SPM' if i<2 else 'Cache','相同 data SRAM'],MEM if i<2 else LOGIC,True)
    f.arrow([(1420,365),(1420,515)])
    f.text(70,580,'SoC 的 SPM 地址别名',24)
    f.text(70,630,'AmSpm / AmSpmBaseUncached',22)
    f.text(70,680,'外层地址重映射到同一存储',23)
    f.text(70,730,'CPU 缓存属性需另外匹配',23)
    f.text(45,865,'LLC/SPM 不是独立 Global Buffer；DDR 旁路 master 也不会自动窥探 CPU / LLC 中的脏数据。',24)
    f.save()


if __name__ == '__main__':
    for draw in [uart, i2c, spi, gpio, plic, clint, clic, router, bootrom, socregs, jtag,
                 serial, vga, usb, idma, traps, llc, spm]:
        draw()
    print('Generated RTL SVG sources.')
