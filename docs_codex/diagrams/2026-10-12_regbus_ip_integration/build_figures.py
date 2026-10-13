"""Two integration-oriented views; no changes to RTL or earlier figures."""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent
helper = ROOT.parent/'2026-10-12_axi_to_detailed_mem/build_figures.py'
spec = importlib.util.spec_from_file_location('svg_primitives', helper)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
d.OUT = ROOT


def canvas(height):
    f=d.Figure(height)
    f.items[0]=f.items[0].replace('1600','1800')
    f.items[1]=f.items[1].replace('1600','1800')
    return f


def bus(f,points):
    f.line(points,width=3)
    x,y=points[0]; a,b=points[1]
    import math
    dx,dy=x-a,y-b; n=math.hypot(dx,dy); ux,uy=dx/n,dy/n
    tip=[(x,y),(x-11*ux+4.5*uy,y-11*uy-4.5*ux),(x-11*ux-4.5*uy,y-11*uy+4.5*ux)]
    f.items.append(f'<polygon points="{" ".join(f"{a},{b}" for a,b in tip)}" fill="{d.DATA}"/>')


def whole():
    f=canvas(980)
    f.text(35,45,'① Regbus 全路径：现有互连 + 自有 IP 接入边界',30)
    f.text(35,90,'蓝色双向线 = 请求向右 / 响应返回；棕色虚线 = 地址与选择；虚线边框 = 拟新增。',24,d.GRAY)
    f.rect(220,150,1545,585,'#FFFFFF')
    f.text(245,188,'Cheshire 内部互连与寄存器目标：clk_i / rst_ni',25)
    f.box(25,330,155,105,['CPU 等','AXI 发起端'])
    f.box(250,315,180,140,['主 AXI','Crossbar','第一级选路'])
    bus(f,[(180,385),(250,385)])
    f.box(500,285,350,195,['现有 AXI → Regbus 通路','i_reg_atomics','→ i_reg_atomics_cut','→ i_axi_to_reg_v2','64-bit AXI → 32-bit Reg'])
    bus(f,[(430,385),(500,385)])
    f.text(450,271,'AxiOut.reg_demux',23)
    f.box(1000,315,240,150,['i_reg_demux','请求分发','响应选择'])
    bus(f,[(850,385),(1000,385)])
    f.text(905,425,'Regbus',24)
    f.box(1000,200,240,75,['地址解码 RegMap'],'#F8F0E6')
    f.line([(885,385),(885,235),(1000,235)],d.CTRL,True)
    f.dot(885,385,d.CTRL)
    f.text(875,216,'addr',23,d.CTRL)
    f.line([(1120,275),(1120,315)],d.CTRL,True)
    f.text(1150,300,'reg_select',22,d.CTRL)
    f.box(1400,215,320,90,['片内寄存器目标','SoC / UART / GPIO / …'])
    f.box(1400,375,320,90,['i_reg_err_slv','未命中：ready=1, error=1'])
    f.box(1400,540,320,115,['外部 Regbus 端口 [k]','reg_ext_slv_req_o[k]','reg_ext_slv_rsp_i[k]'],'#EDF5EB')
    bus(f,[(1240,340),(1280,340),(1280,260),(1400,260)])
    bus(f,[(1240,390),(1320,390),(1320,420),(1400,420)])
    bus(f,[(1240,440),(1355,440),(1355,595),(1400,595)])
    f.text(470,548,'需要配置：RegExtNumSlv / RegExtNumRules',24)
    f.text(470,587,'RegExtRegionStart / End / Idx',24)
    f.text(470,627,'gen_axi_out + gen_reg_out 自动生成两级地址规则',24)
    f.text(470,684,'默认外部端口数为 0；打开端口后，还要在外层顶层接线。',24,d.GRAY)
    f.rect(1380,805,350,120,'#EDF5EB')
    f.items[-1]=f.items[-1].replace('stroke-width="2"','stroke-width="2" stroke-dasharray="8 5"')
    f.text(1555,841,'自有 IP 寄存器接口',26,anchor='middle')
    f.text(1555,877,'NPU / ISP / DMA / …',24,anchor='middle')
    f.text(1555,908,'内部职责见图②',23,anchor='middle')
    bus(f,[(1560,655),(1560,805)])
    f.text(1150,770,'同域直连；异域增加 reg_cdc',24)
    f.text(40,810,'IP 收到：addr[47:0] / write / wdata[31:0] / wstrb[3:0] / valid',24)
    f.text(40,851,'IP 返回：rdata[31:0] / error / ready',24)
    f.text(40,904,'配置走 Regbus；图像、权重、帧数据等批量搬运走独立的数据接口。',24,d.GRAY)
    f.save('01_regbus_whole')


def endpoint():
    f=canvas(970)
    f.text(35,45,'② 自有 IP：需要实现的寄存器接口（建议结构，尚未接入）',30)
    f.text(35,90,'本图采用同 clk_i 域示例；配置访问完成与 IP 运算完成是两个事件。',24,d.GRAY)
    f.rect(340,170,1040,635,'#FFFFFF')
    f.items[-1]=f.items[-1].replace('stroke-width="2"','stroke-width="2" stroke-dasharray="8 5"')
    f.text(365,209,'IP 寄存器封装：可手写，或使用现有 reggen 生成',25)
    f.text(35,294,'reg_ext_slv_req_o[k]',24)
    f.text(35,329,'addr / write / wdata',24)
    f.text(35,364,'wstrb / valid',24)
    f.line([(45,390),(410,390)])
    f.box(410,260,310,185,['地址译码与访问控制','offset = addr - BASE','fire = valid & ready','wr_en = fire & write','按译码 / wstrb 写入'],'#F8F0E6')
    f.box(960,270,360,130,['配置 / 命令寄存器','参数、地址低位 / 高位','写 START 时提交命令'],'#EDF5EB')
    f.line([(720,340),(960,340)])
    f.text(745,316,'写使能 / 写数据',23)
    f.rect(1470,280,290,415,'#F1F5F9')
    for y,s in [(320,'IP 工作逻辑'),(400,'接受命令'),(450,'计算 / 搬运 / 接收'),(535,'维护 busy / done / error'),(620,'数据口另接 AXI / 流接口')]:
        f.text(1615,y,s,24,anchor='middle')
    f.line([(1320,340),(1470,340)])
    f.text(1340,320,'配置 / 启动',23)
    f.box(1080,625,270,110,['状态 / 中断状态','busy / done / error','建议写 1 清除事件位'],'#EDF5EB')
    f.line([(1470,675),(1350,675)])
    f.text(1390,649,'状态',23)
    f.box(490,575,350,170,['读数据选择与访问响应','rdata = 选中寄存器值','ready = 本次访问可完成','error = 地址 / 权限等错误'])
    f.line([(570,445),(570,575)],d.CTRL,True)
    f.text(594,515,'offset / 访问属性',23,d.CTRL)
    f.line([(1120,400),(1120,480),(900,480),(900,620),(840,620)])
    f.text(950,462,'配置回读',23)
    f.line([(1080,685),(840,685)])
    f.text(901,666,'状态回读',23)
    f.line([(1215,772),(1215,735)],d.CTRL,True)
    f.text(1070,797,'合法 W1C 写生成清除使能',23,d.CTRL)
    f.line([(490,655),(45,655)])
    f.text(35,599,'reg_ext_slv_rsp_i[k]',24)
    f.text(35,634,'rdata / error / ready',24)
    f.text(40,862,'短寄存器访问及时应答；长任务用 busy / done 或中断报告，不让 ready 一直等到任务完成。',24)
    f.text(40,909,'中断另接 SoC 中断输入；跨时钟时，事务或配置/状态传递必须有明确的 CDC 与复位方案。',24,d.GRAY)
    f.save('02_ip_register_contract')


if __name__=='__main__':
    whole(); endpoint()
    print('Wrote two integration figures.')
