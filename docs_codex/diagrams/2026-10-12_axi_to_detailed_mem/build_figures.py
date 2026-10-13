"""RTL teaching figures: separate payload, handshakes and width conversion.

Run from any directory. Only writes SVG masters beside this script.
"""
from pathlib import Path
from html import escape
import json
import math

OUT = Path(__file__).resolve().parent
INK = '#253447'
DATA = '#205F9C'
CTRL = '#925021'
GRAY = '#536174'
FONT = 'WenQuanYi Zen Hei'


class Figure:
    def __init__(self, height):
        self.h = height
        self.items = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{height}" viewBox="0 0 1600 {height}">',
                      f'<rect x="0" y="0" width="1600" height="{height}" fill="#FFFFFF"/>']
        self.labels = []

    def text(self, x, y, s, size=24, color=INK, anchor='start'):
        self.items.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{escape(s)}</text>')
        self.labels.append(dict(x=x, y=y, text=s, size=size, anchor=anchor))

    def rect(self, x, y, w, h, fill='#FFFFFF', color=INK):
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{color}" stroke-width="2"/>')

    def line(self, points, color=DATA, dashed=False, arrow=True, width=2.4):
        dash = ' stroke-dasharray="8 5"' if dashed else ''
        self.items.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="miter"{dash}/>')
        if arrow:
            x,y = points[-1]; a,b = points[-2]
            dx,dy = x-a,y-b; n=math.hypot(dx,dy); ux,uy=dx/n,dy/n
            tip = [(x,y),(x-11*ux+4.5*uy,y-11*uy-4.5*ux),(x-11*ux-4.5*uy,y-11*uy+4.5*ux)]
            self.items.append(f'<polygon points="{" ".join(f"{a},{b}" for a,b in tip)}" fill="{color}"/>')

    def dot(self,x,y,color=DATA):
        self.items.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>')

    def box(self,x,y,w,h,lines,fill='#F1F5F9'):
        self.rect(x,y,w,h,fill)
        for i,s in enumerate(lines): self.text(x+w/2,y+34+i*32,s,anchor='middle')

    def fifo(self,x,y,w,h,name,detail):
        self.rect(x,y,w,h,'#EEF5EE')
        self.text(x+w/2,y+32,name,anchor='middle')
        self.text(x+w/2,y+63,detail,22,anchor='middle')
        self.rect(x+25,y+h-38,w-50,23,'#FFFFFF')
        if '深度 2' in detail:
            self.line([(x+w/2,y+h-38),(x+w/2,y+h-15)],INK,arrow=False,width=1.5)

    def save(self,name):
        (OUT/f'{name}.svg').write_text('\n'.join(self.items+['</svg>']))
        (OUT/f'{name}.labels.json').write_text(json.dumps(self.labels,ensure_ascii=False,indent=2))


def request():
    f=Figure(680)
    f.text(40,43,'① 请求内容：独立读 / 写来源，共用一个内部请求出口',30)
    f.text(40,85,'实线 = 请求字段；虚线 = 选择控制。valid / ready 另见图②。',23,GRAY)
    f.box(230,180,300,115,['读请求生成逻辑','rd_meta_q / r_cnt_q','每个读拍生成 rd_meta'])
    f.box(230,365,300,115,['写请求生成逻辑','wr_meta_q / w_cnt_q','每个写拍生成 wr_meta'])
    f.text(45,222,'AR 字段',25)
    f.line([(45,242),(230,242)])
    f.text(40,402,'AW 字段',24)
    f.text(40,434,'W.strb',24)
    f.line([(45,452),(230,452)])
    f.items.append(f'<polygon points="660,185 735,225 735,430 660,470" fill="#F8F0E6" stroke="{INK}" stroke-width="2"/>')
    f.text(697,310,'2:1',25,anchor='middle')
    f.text(697,345,'MUX',23,anchor='middle')
    f.text(640,165,'i_ax_mux',24)
    f.line([(530,242),(660,242)]); f.text(548,228,'rd_meta',22)
    f.line([(530,422),(660,422)]); f.text(548,408,'wr_meta',22)
    f.line([(735,325),(940,325)]); f.text(798,308,'meta',25)
    f.box(940,230,270,185,['组合接线','addr = meta.addr','we = meta.write','id = meta.id','其余请求属性随行'])
    f.text(1040,130,'axi_req_i.w.data / w.strb',24,anchor='middle')
    f.line([(870,148),(1080,148),(1080,230)])
    f.text(1220,307,'m2s_req',22)
    f.line([(1210,325),(1340,325)])
    f.box(1340,245,220,160,['请求入口','图③','i_stream_to_mem'])
    f.box(570,535,245,90,['读写仲裁逻辑','含选择保持状态'],'#F8F0E6')
    f.line([(697,535),(697,452)],CTRL,True)
    f.text(835,578,'选择信号：meta_sel_d',24,CTRL)
    f.dot(845,325)
    f.line([(845,325),(845,462),(1000,462)])
    f.text(1015,470,'meta → 图②两个 FIFO 的数据来源',23)
    f.text(40,658,'注意：W.data 不经过 i_ax_mux，也不写入 i_meta_buf。',24,GRAY)
    f.save('01_request_payload')


def fork():
    f=Figure(1130)
    f.text(40,43,'② 一项访问分成三条握手支路：执行请求、保存元数据、保存响应选择',28)
    f.text(40,85,'实线 = 数据字段；虚线 = valid / ready。i_fork 无数据端口。',23,GRAY)
    f.rect(300,170,285,715,'#FBF4E9')
    f.text(442,216,'i_fork',28,anchor='middle')
    f.text(442,249,'N_OUP = 3',24,anchor='middle')
    f.text(442,325,'输入状态寄存器',24,anchor='middle')
    f.text(442,362,'+ 三路输出状态',24,anchor='middle')
    f.text(442,516,'记住哪些支路',24,anchor='middle')
    f.text(442,551,'已接收当前项',24,anchor='middle')
    f.text(442,730,'三路各接收一次后',23,anchor='middle')
    f.text(442,766,'才确认上游完成',23,anchor='middle')
    f.text(50,391,'来自 i_ax_mux',23)
    f.line([(50,425),(300,425)],CTRL,True); f.text(70,414,'arb_valid',24,CTRL)
    f.line([(300,475),(50,475)],CTRL,True); f.text(70,508,'arb_ready',24,CTRL)
    for y, valid,ready in [(270,'m2s_req_valid','m2s_req_ready'),(540,'meta_valid','meta_ready'),(810,'sel_valid','sel_ready')]:
        f.line([(585,y),(1000,y)],CTRL,True)
        f.text(680,y-13,valid,24,CTRL)
        f.line([(1000,y+50),(585,y+50)],CTRL,True)
        f.text(680,y+82,ready,24,CTRL)
    f.box(1000,225,310,125,['i_stream_to_mem','执行本拍请求','内部见图③'])
    f.text(1155,160,'m2s_req（图①）',24,anchor='middle')
    f.line([(1155,178),(1155,225)])
    f.fifo(1000,485,310,130,'i_meta_buf','meta_t；深度 2')
    f.text(1155,425,'meta（图①）',24,anchor='middle')
    f.line([(1155,443),(1155,485)])
    f.line([(1310,545),(1470,545)]); f.text(1330,526,'meta_buf',24)
    f.text(1328,585,'供响应字段构造',23,GRAY)
    f.fifo(1000,755,310,130,'i_sel_buf','logic[1:0]；深度 2')
    f.text(1155,684,'{sel_b, sel_r}',24,anchor='middle')
    f.line([(1155,702),(1155,755)])
    f.line([(1310,815),(1470,815)])
    f.text(1328,776,'sel_buf_b',24)
    f.text(1328,803,'sel_buf_r',24)
    f.text(1328,855,'供 R / B 握手选择',23,GRAY)
    f.text(40,961,'sel_b = meta.write & meta.last',25)
    f.text(40,1004,'sel_r = ~meta.write | meta.atop[5]',25)
    f.text(770,961,'普通读：(B,R) = (0,1)',24)
    f.text(770,1004,'普通写中间拍：(0,0)；最后拍：(1,0)',24)
    f.text(40,1081,'三条支路可以分不同周期接收；FIFO 均为 fall-through，不代表固定延迟两拍。',24,GRAY)
    f.save('02_fork_and_metadata')


def adapter():
    f=Figure(1090)
    f.text(40,43,'③ i_stream_to_mem：请求直通 + 在途计数 + 返回缓冲',30)
    f.text(40,85,'默认 BufDepth = 1；括号内为外层 axi_to_detailed_mem 的连线名。',23,GRAY)
    f.text(55,139,'上游 stream 接口',25)
    f.text(1195,139,'下游 memory 接口',25)
    f.text(55,199,'req_i (m2s_req)',24)
    f.text(1160,199,'mem_req_o (mem_req)',24)
    f.line([(60,220),(1500,220)])
    f.text(625,204,'结构体直接连线，不改字段',24,DATA)
    f.rect(810,300,65,65,'#FBF4E9'); f.text(842,343,'&',32,anchor='middle')
    f.text(55,288,'req_valid_i',24,CTRL)
    f.line([(60,330),(810,330)],CTRL,True)
    f.line([(875,330),(1500,330)],CTRL,True)
    f.text(1180,310,'mem_req_valid_o',24,CTRL)
    f.rect(810,405,65,65,'#FBF4E9'); f.text(842,448,'&',32,anchor='middle')
    f.text(55,413,'req_ready_o',24,CTRL)
    f.line([(810,438),(60,438)],CTRL,True)
    f.line([(1500,438),(875,438)],CTRL,True)
    f.text(1180,418,'mem_req_ready_i',24,CTRL)
    f.box(950,530,580,95,['req_ready = (cnt_q < BufDepth)','| (resp_valid_o & resp_ready_i)'],'#FBF4E9')
    f.line([(1240,530),(1240,493),(842,493),(842,470)],CTRL,True)
    f.dot(1240,493,CTRL)
    f.line([(1240,493),(1570,493),(1570,265),(842,265),(842,300)],CTRL,True)
    f.box(450,530,325,95,['cnt_q：在途计数寄存器','接收请求 +1；交付响应 -1'],'#FBF4E9')
    f.line([(775,574),(950,574)],CTRL,True); f.text(810,556,'cnt_q',23,CTRL)
    f.text(55,742,'resp_o',24)
    f.text(55,775,'(m2s_resp)',24)
    f.fifo(590,710,360,150,'i_resp_buf','深度 1；fall-through')
    f.line([(590,765),(260,765)])
    f.text(1170,738,'mem_resp_i',24)
    f.text(1170,770,'(mem_rdata)',24)
    f.line([(1150,765),(950,765)])
    f.line([(1150,815),(950,815)],CTRL,True)
    f.text(1170,814,'mem_resp_valid_i',24,CTRL)
    f.line([(590,810),(260,810)],CTRL,True); f.text(55,822,'resp_valid_o',24,CTRL)
    f.line([(260,880),(680,880),(680,860)],CTRL,True); f.text(55,891,'resp_ready_i',24,CTRL)
    f.text(1120,880,'没有 mem_resp_ready 输出',24,CTRL)
    f.text(55,960,'request_fire = req_valid_i & req_ready_o',24)
    f.text(55,1003,'response_fire = resp_valid_o & resp_ready_i',24)
    f.text(825,1003,'cnt_d = cnt_q + request_fire - response_fire',24)
    f.text(55,1062,'请求是否放行由预留容量决定；响应到达后，即使上游暂停，也有 FIFO 可接住。',24,GRAY)
    f.save('03_stream_to_mem')


def banks():
    f=Figure(1170)
    f.text(40,43,'④ i_mem_to_banks：字段切片、两路独立请求、两路响应收齐',29)
    f.text(40,85,'64-bit 数据 / 48-bit 地址；NumBanks = 2，FifoDepth = 1，HideStrb = 0。',23,GRAY)
    f.text(40,142,'请求方向 →',25,DATA)
    f.box(50,210,260,180,['mem_req.addr [47:0]','mem_req.wdata [63:0]','mem_req.strb [7:0]','mem_req.we','其余属性随行'])
    f.box(420,175,340,120,['组合切片：子通路 0','addr = align8(addr)','wdata[31:0] / strb[3:0]'])
    f.box(420,355,340,120,['组合切片：子通路 1','addr = align8(addr) + 4','wdata[63:32] / strb[7:4]'])
    f.line([(310,300),(365,300),(365,235),(420,235)])
    f.line([(365,300),(365,415),(420,415)]); f.dot(365,300)
    for i,y in [(0,180),(1,360)]:
        f.fifo(820,y,210,105,'请求 FIFO','深度 1')
        f.line([(760,y+55),(820,y+55)])
        f.line([(1030,y+45),(1160,y+45)])
        f.text(1175,y+6,f'mem_addr_o[{i}] / mem_wdata_o[{i}]',22)
        f.text(1175,y+36,f'mem_strb_o[{i}] / mem_we_o[{i}]',22)
        f.text(1175,y+72,f'mem_req_o[{i}] → / ← mem_gnt_i[{i}]',22,CTRL)
        f.text(1175,y+104,'接外层第 '+str(i)+' 路适配器',23,GRAY)
    f.text(40,539,'地址是 48 bit，切片的是数据与字节使能；最终仍汇入外层的同一个 Regbus。',24,GRAY)
    f.line([(40,570),(1560,570)],INK,arrow=False,width=1)
    f.text(40,620,'响应方向 ←',25,DATA)
    f.box(320,710,355,220,['组合拼接','mem_rdata.data [31:0]','← 第 0 路响应数据','mem_rdata.data [63:32]','← 第 1 路响应数据','err / exokay 按路保留'])
    for i,y in [(0,680),(1,910)]:
        f.fifo(855,y,240,120,'响应 FIFO '+str(i),'深度 1')
        f.text(1160,y+22,f'mem_rdata_i[{i}] [31:0]',24)
        f.text(1160,y+56,f'mem_err_i[{i}] / mem_exokay_i[{i}]',22)
        f.line([(1140,y+50),(1095,y+50)])
        f.line([(1140,y+90),(1095,y+90)],CTRL,True)
        f.text(1160,y+95,f'mem_rvalid_i[{i}]',24,CTRL)
    f.line([(855,730),(675,730)])
    f.line([(855,960),(740,960),(740,880),(675,880)])
    f.text(45,781,'64-bit 结果',24)
    f.line([(320,805),(45,805)])
    f.text(45,850,'送回图③',24)
    f.text(45,883,'mem_resp_i',24)
    f.text(45,1090,'mem_rvalid = resp_valid[0] & resp_valid[1]：两路都到齐才交付整拍结果。',25,CTRL)
    f.text(45,1135,'读、写都必须返回完成响应；先到的一路保存在自己的响应 FIFO 中。',24,GRAY)
    f.save('04_banks_and_ports')


if __name__ == '__main__':
    request(); fork(); adapter(); banks()
    print('Wrote four SVG masters.')
