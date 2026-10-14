#!/usr/bin/env python3
"""L01: functional component overview, native SVG text/shapes/whole arrows."""
from pathlib import Path
from html import escape
import json
ROOT = Path(__file__).resolve().parent
W, H = 2920, 1810
C = {'call':('#edf3fd','#4679b2'), 'device':('#e8f5f1','#2c8274'),
     'isa':('#f2edfa','#8756ac'), 'host':('#fff3e3','#bb7137'),
     'start':('#eaf3fa','#577e96'), 'os':('#edf3e5','#698847'),
     'gap':('#fff5e9','#a67949')}
p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','<defs>']
for k, (_, c) in C.items():
 p.append(f'<marker id="{k}" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="{c}"/></marker>')
p += ['</defs>',f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fafcff"/>']
boxes, edges = {}, []
def txt(x,y,s,size=24,bold=False,anchor='start',color='#293c50'):
 p.append(f'<text x="{x}" y="{y}" font-family="Microsoft YaHei" font-size="{size}" font-weight="{"bold" if bold else "normal"}" text-anchor="{anchor}" fill="{color}">{escape(s)}</text>')
def rect(x,y,w,h,fill,stroke='none',dash=False):
 p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"'+(' stroke-dasharray="10 6"' if dash else '')+'/>')
def box(id,x,y,w,h,title,lines=(),kind='call',size=23):
 fill,stroke=C[kind]; rect(x,y,w,h,fill,stroke)
 txt(x+w/2,y+35,title,22 if id in ('event','memory') else 26,True,'middle')
 for i,s in enumerate(lines): txt(x+w/2,y+69+i*31,s,size,anchor='middle')
 boxes[id] = dict(x=x,y=y,width=w,height=h,title=title)
def arrow(id,points,label='',lx=0,ly=0,kind='call',anchor='middle'):
 p.append(f'<polyline id="{id}" points="'+ ' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{C[kind][1]}" stroke-width="3" marker-end="url(#{kind})"/>')
 if label: txt(lx,ly,label,22,anchor=anchor,color=C[kind][1])
 edges.append(dict(id=id,points=points,label=label,kind=kind))
# Regions and layer captions precede nodes, so no line is hidden by a background.
rect(400,190,1490,1500,'#f4f7fc','#bdcce0')
rect(1940,190,340,1500,'#f3f7fa','#becfdb')
rect(2360,190,520,1500,'#f5f8ef','#c3d0b5')
rect(415,360,1155,918,'none','#7e9dbb',True)
txt(35,56,'Cheshire + CVA6 + Ara｜当前工程全组件软件栈',38,True)
txt(35,98,'功能组件总览 · 裸机 BSP 主路 + Ara 指令通路 + 可选 Linux 分路',26)
txt(35,155,'开发主机',28,True)
txt(430,155,'目标端：裸机应用与基础软件',28,True)
txt(1955,155,'启动与运行支撑',28,True)
txt(2380,155,'Linux / SDK 可选分路',28,True)
for x,s in [(430,'控制台 / 调试'),(720,'存储介质'),(1010,'GPIO / 中断 / 计时'),(1300,'DMA / 存储控制'),(1590,'向量计算')]:
 txt(x+130,207,s,22,True,'middle')
txt(435,383,'基础支持代码',21,True)
# Main software lanes.
box('apps',430,220,1130,90,'裸机应用 · 外设测试 · 启动固件',['main / sw/tests / flash.spm.elf'])
box('vector_apps',1590,220,260,90,'Ara 应用 / benchmark',['向量内核 · RVV 测试'])
box('printf',440,440,240,100,'printf',['格式化 · 字符回调'])
box('gpt',730,440,240,100,'GPT 公共服务',['分区解析 · 读回调'])
box('uart_debug',440,640,240,110,'UART debug HAL',['命令 / 读写 / 执行'], 'device')
box('media',730,620,240,170,'器件 HAL',['SPI Flash · SPI SD','I²C EEPROM','器件命令 / 分块'], 'device')
box('uart',440,875,240,135,'UART DIF',['收发 · 轮询','_putchar / _getchar'], 'device')
box('spi_i2c',730,875,240,135,'OpenTitan DIF',['SPI Host / I²C','FIFO · 事务 · 配置'], 'device')
box('event',1020,875,240,135,'GPIO / PLIC / CLINT',['GPIO / PLIC：OT DIF','CLINT：本地 DIF'], 'device',21)
box('memory',1310,875,240,135,'DMA / LLC / AXI RT',['DMA：头文件接口','LLC / RT：依赖驱动'], 'device',21)
box('vector_util',1590,440,260,110,'向量辅助代码',['cheshire_util / vector_util','计时 · 校验 · 内核准备'],size=20)
box('rvv',1590,640,260,140,'向量内核实现',['内联汇编 / intrinsics','编译器生成 RVV','启用 VS；按需启用 FS'],'isa')
box('base',440,1130,1110,125,'MMIO / 位域 / 内存辅助代码 + 平台定义',
    ['reg8 / reg32 · mmio_region_* · bitfield / memory', 'params.h · __base_* · 生成 regs/*.h'],'device')
box('csr',1590,1130,260,125,'CSR / 屏障辅助',['util.h：CSR / fence','计时 · IRQ · WFI'],'isa')
txt(435,1300,'归档：C/S 支持对象 → libcheshire.a',20,color='#577e96')
txt(435,1330,'.h 内联由调用者编译；crt0 也参与归档',20,color='#577e96')
box('mmio_contract',430,1370,1130,115,'软硬件接口：MMIO / 地址空间 / 异常与中断',
    ['地址与字段 · 访问宽度 · 副作用 · IRQ · 访问顺序 / 缓存与数据可见性'],'isa',22)
box('isa_contract',1590,1370,260,115,'指令接口：ISA / CSR',['标量 / RVV · 特权状态','trap · 内存访问语义'],'isa',21)
box('peripherals',430,1570,1130,90,'SoC 控制器与存储子系统',
    ['UART · SPI / I²C · GPIO / PLIC / CLINT · iDMA · LLC / AXI RT · AXI / Reg / 存储'],'device',21)
box('core',1590,1570,260,90,'CVA6 + Ara',['取指 / 执行 / 访存'],'isa')
# Host tool stack, executable on the host, not in the target call chain.
box('make',30,220,290,110,'构建与依赖入口',['Make · sw.mk / Ara Makefile','Bender path · 本地依赖'],'host',20)
box('compile',30,440,290,150,'编译 / 归档 / 链接',['GCC · as · ld · ar','源码 / .o / .a / .ld','→ ELF / map'],'host')
box('gen',30,720,290,140,'寄存器 / 描述生成',['Python regtool：HJSON','→ C 宏 / RTL','dtc：DTS → DTB'],'host',21)
box('inspect',30,950,290,155,'产物转换 / 检查',['objcopy · objdump','readelf · nm · size','ELF → bin / memh / dump'],'host',22)
box('debug',30,1370,290,150,'装载 / 调试',['GDB · OpenOCD','flash_disk.sh / .gdb','JTAG · ELF / 介质镜像'],'host')
# Side support: separate ROM, application runtime entry, and OS loader.
box('rom',1960,220,300,155,'Boot ROM',['LLC → SPM / 栈','启动模式 · 介质 / 调试','cheshire_bootrom.S / .c'],'start',22)
box('crt',1960,520,300,190,'应用 crt0 / 链接布局',['sp / gp · BSS · FS','trap 入口 / _exit','smp.h：hart 协调辅助','link/*.ld · params.h'],'start',22)
box('platform',1960,800,300,135,'平台初始化缺口',['DDR / 时钟 / PAD','需平台实现与独立验收'],'gap')
box('zsl',1960,1040,300,140,'ZSL / 介质装载',['GPT + ROM 读回调','DTB / firmware → DRAM','sw/boot/zsl.c'],'start',22)
box('runtime',1960,1330,300,150,'链接后运行支持',['工具链 libgcc / libc','按需要引入目标代码','系统调用 / 堆未证完整'],'start',22)
# Optional SDK: host build region explicitly separated from target boxes.
box('sdk',2380,220,470,260,'主机：Ara Makefile → cva6-sdk',['Buildroot → Linux 交叉工具链 / rootfs',
    'Linux / BusyBox 配置 · DTS → DTB','U-Boot 源码 → mkimage（主机程序）',
    'ELF / Image → uImage · fw_payload','Spike / riscv-tests：可选主机入口'],'host',22)
box('userspace',2390,600,440,115,'目标：用户空间 / rootfs',['BusyBox · 应用 / 可选 RVV benchmark'],'os',22)
box('linux',2390,815,440,140,'Linux 内核 / 平台驱动',['调度 / 内存管理 / 系统调用','设备树 · IRQ / timer / 设备驱动'],'os')
box('opensbi',2390,1060,440,115,'OpenSBI · M 模式固件',['SBI 服务；fw_payload 含 U-Boot'],'os',22)
box('uboot',2390,1275,440,115,'U-Boot · 启动程序',['装载 Linux / DTB · 移交执行'],'start',23)
box('os_status',2390,1490,440,160,'支持边界',['源码 / 配方存在 ≠ 当前启动通过','版本 / DTS / ISA / 向量上下文待验收','RTOS：待移植，未展开为现有栈'],'gap',22)
# Continuous relationships, routed through gaps.
arrow('host_build',[(175,330),(175,440)],'构建',212,391,'host')
arrow('link_elf',[(320,480),(365,480),(365,265),(430,265)],'ELF',363,249,'host')
arrow('elf_inspect',[(175,590),(345,590),(345,920),(175,920),(175,950)],'产物',291,916,'host')
arrow('headers',[(320,790),(375,790),(375,1190),(440,1190)],'生成 C 宏',375,1170,'host',anchor='end')
arrow('load',[(175,1520),(175,1615),(430,1615)],'装载 / 调试访问',279,1598,'host')
arrow('use_printf',[(560,310),(560,440)],'调用',591,428)
arrow('use_gpt',[(850,310),(850,440)],'调用',881,428)
arrow('direct_event',[(1140,310),(1140,875)],'直接调用',1160,684,anchor='start')
arrow('direct_memory',[(1430,310),(1430,875)],'直接调用',1450,738,anchor='start')
arrow('debug_protocol',[(680,310),(705,310),(705,696),(680,696)],'协议服务',700,611,anchor='end')
arrow('printf_callback',[(440,490),(425,490),(425,922),(440,922)],'',0,0)
txt(443,576,'字符回调（直达 DIF）',20,color=C['call'][1])
arrow('debug_uart',[(560,750),(560,875)],'调用',591,789)
arrow('gpt_read',[(850,540),(850,620)],'读回调',899,586)
arrow('hal_dif',[(850,790),(850,875)],'控制器调用',907,843)
for cx in (560,850,1140,1430):
 arrow(f'regs_{cx}',[(cx,1010),(cx,1130)],'寄存器访问',cx+14,1074,'device',anchor='start')
arrow('vector_helpers',[(1720,310),(1720,440)],'调用',1760,411)
arrow('vector_kernel',[(1720,550),(1720,640)],'执行内核',1773,602)
arrow('rvv_execute',[(1850,710),(1872,710),(1872,1420),(1850,1420)],'',kind='isa')
txt(1740,910,'RVV 指令执行',20,color=C['isa'][1])
arrow('csr_use',[(1720,780),(1720,1130)],'CSR / 屏障',1736,1047,'isa',anchor='start')
arrow('csr_execute',[(1720,1255),(1720,1370)],'CSR/fence',1740,1338,'isa',anchor='start')
arrow('mmio_access',[(990,1255),(990,1370)],'load / store',1100,1351,'device')
arrow('bus_transaction',[(990,1485),(990,1570)],'寄存器事务 / 事件',1110,1541,'device')
arrow('core_instruction',[(1720,1485),(1720,1570)],'指令执行',1780,1541,'isa')
arrow('rom_crt',[(2110,375),(2110,520)],'裸机装载',2125,457,'start',anchor='start')
arrow('crt_main',[(1960,596),(1915,596),(1915,177),(995,177),(995,220)],'初始化后进入 main',1500,171,'start')
arrow('rom_zsl',[(2260,300),(2320,300),(2320,1095),(2260,1095)],'OS 介质启动',2310,1010,'start',anchor='end')
arrow('zsl_firmware',[(2260,1115),(2390,1115)],'进入固件',2324,1145,'start')
arrow('sdk_build',[(2605,480),(2605,600)],'构建 / 打包',2620,548,'host',anchor='start')
arrow('syscall',[(2605,715),(2605,815)],'系统调用',2670,774,'os')
arrow('sbi',[(2605,955),(2605,1060)],'SBI 调用',2670,1014,'os')
arrow('payload',[(2605,1175),(2605,1275)],'启动 payload',2680,1236,'start')
arrow('boot_linux',[(2830,1330),(2862,1330),(2862,887),(2830,887)],'',kind='start')
txt(2610,1437,'启动：ZSL → OpenSBI → U-Boot → Linux',20,anchor='middle')
# Compact coverage/legend lines; detailed evidence remains in the chapter.
txt(430,1725,'覆盖缺口：VGA / Serial Link 有寄存器头；未见同级完整 DIF/HAL。USB / CLIC 见源码索引。',23)
for x,k,label in [(35,'call','函数调用'),(440,'host','构建 / 装载'),(900,'device','寄存器访问'),(1400,'isa','指令执行'),(1900,'start','初始化 / 启动'),(2450,'os','OS 服务')]:
 arrow('legend_'+k,[(x,1770),(x+60,1770)],kind=k)
 txt(x+75,1778,label,23,color=C[k][1])
(ROOT/'complete-software-stack.svg').write_text('\n'.join(p+['</svg>'])+'\n')
(ROOT/'layout.json').write_text(json.dumps(dict(canvas=[W,H],boxes=boxes,arrows=edges),ensure_ascii=False,indent=2)+'\n')
print(f'{len(boxes)} component groups; {len(edges)} whole arrows')
