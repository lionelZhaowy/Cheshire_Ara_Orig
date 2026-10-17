#!/usr/bin/env python3
"""Generate the two L01 OS-selection figures into a new directory.

SVG is the editable source; PNG and PPTX must be derived from these same files.
Only the Python standard library is needed. No production sources are changed.
"""
import argparse
import json
from html import escape
from pathlib import Path

W, H = 2400, 1350
FONT = "WenQuanYi Zen Hei"
C = dict(ink="#29292D", muted="#606773", control="#765489",
         data="#314D66", vector="#187C78", blue="#EAF2FA",
         purple="#F0EAF6", green="#E8F3ED", memory="#D8E8F4",
         gb="#D9EEE8", compute="#F1D7D9", interconnect="#F5E1C9")


class Figure:
    def __init__(self, name, title, subtitle):
        self.name, self.boxes, self.arrows = name, {}, []
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
                      f'<title>{escape(title)}</title>', '<defs>']
        for key in ("control", "data", "vector"):
            self.parts.append(f'<marker id="{key}" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="{C[key]}"/></marker>')
        self.parts.append('</defs>')
        self.rect("page", 0, 0, W, H, "#FFFFFF", stroke="none")
        self.text(W/2, 68, title, 43, anchor="middle", bold=True)
        self.text(W/2, 115, subtitle, 27, anchor="middle", color=C["muted"])

    def text(self, x, y, value, size=27, color=None, anchor="start", bold=False, owner=""):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="{color or C["ink"]}" text-anchor="{anchor}" data-owner="{owner}">{escape(value)}</text>')

    def rect(self, key, x, y, w, h, fill, stroke=None, dashed=False, rounded=False):
        self.boxes[key] = dict(x=x, y=y, width=w, height=h)
        self.parts.append(f'<rect id="{key}" x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke or C["ink"]}" stroke-width="2"'
                          + (' rx="14"' if rounded else '')
                          + (' stroke-dasharray="10 6"' if dashed else '') + '/>')

    def box(self, key, x, y, w, h, title, lines=(), fill="#FFFFFF", stroke=None, dashed=False, rounded=False, size=29):
        self.rect(key, x, y, w, h, fill, stroke, dashed, rounded)
        count = 1 + len(lines)
        first = y + (h - count * 37) / 2 + 29
        self.text(x+w/2, first, title, size, anchor="middle", bold=True, owner=key)
        for i, line in enumerate(lines):
            self.text(x+w/2, first+37*(i+1), line, 25, anchor="middle", owner=key)

    def arrow(self, key, points, kind="control", both=False, source="", target=""):
        self.parts.append(f'<polyline id="{key}" points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{C[kind]}" stroke-width="3" stroke-linejoin="miter" marker-end="url(#{kind})"'
                          + (f' marker-start="url(#{kind})"' if both else '') + '/>')
        self.arrows.append(dict(id=key, points=points, kind=kind,
                                bidirectional=both, source=source, target=target))

    def save(self, directory):
        (directory/f"{self.name}.svg").write_text("\n".join(self.parts+['</svg>'])+'\n')
        return dict(name=self.name, canvas=[W,H], boxes=self.boxes, arrows=self.arrows)


def software_stacks():
    f = Figure("software-stacks", "裸机、RTOS 与 Embedded Linux：推理软件栈",
               "三种替代执行环境；计算算法可复用，资源管理与设备交接分别适配")
    columns = [
        (60, "裸机", C["blue"], "#5C83AE", "主循环 / 中断 / 状态机",
         "手动组织资源、事件与错误", "裸机设备驱动", "平台地址 / 同步 / 轮询或 IRQ",
         ["显式配置", "VS / FS 状态"], "调用 / 事件"),
        (830, "RTOS", C["purple"], "#9076AC", "任务 / 队列 / 信号量",
         "按优先级调度与同步", "RTOS 设备驱动", "互斥 / 提交 / ISR 唤醒",
         ["FP / RVV 上下文", "需适配与验收"], "服务 / 等待"),
        (1600, "Embedded Linux", C["green"], "#679980", "进程 / 线程 / 系统服务",
         "文件、内存与生命周期管理", "Linux 内核设备驱动", "DMA 映射 / 同步 / IRQ",
         ["用户态 RVV", "上下文需验收"], "系统服务")]
    for i,(x,title,fill,stroke,env,env_line,driver,driver_line,rvv_lines,call) in enumerate(columns):
        p=f"c{i}"
        f.rect(p, x, 160, 740, 1000, fill, stroke, rounded=True)
        f.text(x+370, 220, title, 36, anchor="middle", bold=True, color=stroke)
        f.box(p+"app", x+30,260,680,90,"模型应用",["输入处理 / 分词 / 采样 / 输出"],stroke=stroke,rounded=True)
        f.box(p+"runtime", x+30,410,680,110,"推理运行时 / 算子后端",["模型与张量 / 执行计划 / 工作区与 KV"],stroke=stroke,rounded=True)
        f.arrow(p+"a",[(x+370,350),(x+370,410)],source=p+"app",target=p+"runtime")
        f.box(p+"env",x+30,585,420,110,env,[env_line],stroke=stroke,rounded=True,size=27)
        f.box(p+"driver",x+30,770,420,115,driver,[driver_line],stroke=stroke,rounded=True,size=28)
        f.box(p+"rvv",x+485,585,225,300,"向量算子代码",["RVV 指令",*rvv_lines],fill="#F5FBF8",stroke=C["vector"],rounded=True,size=27)
        f.arrow(p+"service",[(x+240,520),(x+240,585)],source=p+"runtime",target=p+"env")
        f.text(x+259,559,call,23,color=C["control"])
        f.arrow(p+"device",[(x+240,695),(x+240,770)],source=p+"env",target=p+"driver")
        f.text(x+259,739,"设备请求",23,color=C["control"])
        f.arrow(p+"rvvcode",[(x+597,520),(x+597,585)],"vector",source=p+"runtime",target=p+"rvv")
        f.text(x+615,559,"算子执行",22,color=C["vector"])
        f.box(p+"npu",x+30,985,420,110,"NPU 设备（候选）",["命令 / 数据搬运 / 完成状态"],fill="#F8F3EB",stroke=stroke,dashed=True,rounded=True,size=28)
        f.box(p+"cpuara",x+485,985,225,110,"CVA6 / Ara",["RVV 执行路径"],fill="#E0F0E8",stroke=C["vector"],rounded=True,size=28)
        f.arrow(p+"submit",[(x+240,885),(x+240,985)],both=True,source=p+"driver",target=p+"npu")
        f.text(x+259,944,"提交 / 完成",23,color=C["control"])
        f.arrow(p+"execute",[(x+597,885),(x+597,985)],"vector",source=p+"rvv",target=p+"cpuara")
        f.text(x+615,944,"指令执行",22,color=C["vector"])
        f.text(x+370,1134,"共享平台资源：主存 / 缓存 / 中断",25,anchor="middle",color=stroke)
    f.text(1200,1225,"共同契约：张量布局 · 设备地址 · 缓存交接 · 缓冲区所有权 · 完成与错误恢复",31,anchor="middle",bold=True)
    f.text(1200,1295,"紫色箭头：服务与设备控制    绿色箭头：RVV 指令路径    虚线设备框：未来候选",26,anchor="middle",color=C["muted"])
    return f


def inference_flow():
    f=Figure("inference-flow","一次推理任务：控制、计算与数据交接",
             "未来 NPU / GB 场景的逻辑职责；不是冻结的 RTL 拓扑，也不引入 CPU 直访 GB")
    f.rect("control-region",50,200,2300,235,C["purple"],stroke="#645C5D")
    f.text(75,233,"控制与完成",29,bold=True)
    f.box("app",80,255,420,130,"CVA6 应用 / 运行时",["分词 / 执行计划 / 采样"],fill="#FFFFFF")
    f.box("driver",650,255,450,130,"驱动 / OS 适配",["发布 / 提交 / 等待 / 恢复"],fill="#FFFFFF")
    f.box("task",1320,255,440,130,"NPU 任务控制（候选）",["协调搬运与计算状态"],fill="#FFFFFF",dashed=True)
    f.box("done",1930,255,350,130,"完成与错误状态",["按任务契约交付"],fill="#FFFFFF",dashed=True)
    f.arrow("app-driver",[(500,320),(650,320)],source="app",target="driver")
    f.text(575,298,"请求",25,color=C["control"],anchor="middle")
    f.arrow("driver-task",[(1100,320),(1320,320)],source="driver",target="task")
    f.text(1210,298,"有序提交",25,color=C["control"],anchor="middle")
    f.arrow("task-done",[(1760,320),(1930,320)],source="task",target="done")
    f.text(1845,298,"状态汇总",25,color=C["control"],anchor="middle")
    f.arrow("completion",[(2105,255),(2105,175),(875,175),(875,255)],source="done",target="driver")
    f.text(1510,158,"状态 / IRQ 通知；驱动核实结果可见与错误",25,color=C["control"],anchor="middle")
    f.rect("data-region",50,540,2300,595,"#F4F7F8",stroke="#645C5D")
    f.text(1100,580,"数据与计算资源",29,bold=True)
    f.box("ddr",80,680,380,180,"DDR 主存",["权重 / KV / 输入", "需回主存的结果"],fill=C["memory"])
    f.box("mover",650,680,400,180,"DDR ↔ GB 搬运职责",["候选实现", "地址 / 长度 / 同步 / 错误"],fill=C["interconnect"],dashed=True,size=28)
    f.box("gb",1250,680,400,180,"GB：独立片上 SRAM",["需求已确认，尚待实现", "分块就绪 / 所有权 / 复用"],fill=C["gb"],dashed=True,size=28)
    f.box("npu",1900,680,380,180,"NPU 计算单元",["候选算子后端", "读取输入 / 写入结果"],fill=C["compute"],dashed=True)
    f.arrow("cpu-memory",[(290,385),(290,680)],"data",both=True,source="app",target="ddr")
    f.text(310,482,"经现有普通内存路径",25,color=C["data"])
    f.text(310,518,"含 L1D / 写缓冲 / LLC",25,color=C["data"])
    f.arrow("move-control",[(1430,385),(1430,475),(850,475),(850,680)],both=True,source="task",target="mover")
    f.text(1120,459,"搬运命令 / 状态",25,color=C["control"],anchor="middle")
    f.arrow("compute-control",[(1550,385),(1550,490),(2090,490),(2090,680)],both=True,source="task",target="npu")
    f.text(1820,474,"计算命令 / 状态",25,color=C["control"],anchor="middle")
    f.arrow("ddr-move",[(460,770),(650,770)],"data",both=True,source="ddr",target="mover")
    f.text(555,739,"旁路数据",25,color=C["data"],anchor="middle")
    f.arrow("move-gb",[(1050,770),(1250,770)],"vector",both=True,source="mover",target="gb")
    f.text(1150,739,"显式搬运",25,color=C["vector"],anchor="middle")
    f.arrow("gb-npu",[(1650,770),(1900,770)],"vector",both=True,source="gb",target="npu")
    f.text(1775,739,"计算读 / 写",25,color=C["vector"],anchor="middle")
    for x,title,lines in [
        (100,"① 发布输入",["顺序与可见性成立后交给设备", "同步措施依平台一致性契约"]),
        (880,"② 分块执行",["GB 就绪后计算；结果按需搬回 DDR", "不得把 GB 当作透明缓存"]),
        (1640,"③ 交付结果",["计算结束 ≠ 结果可消费", "写回、同步与错误检查满足任务契约"])]:
        f.text(x,963,title,30,bold=True)
        for j,line in enumerate(lines):f.text(x,1009+42*j,line,27)
    f.text(1200,1200,"紫：控制与状态    蓝灰：主存访问    绿：GB 数据    虚线：候选或尚待实现的职责",27,anchor="middle")
    f.text(1200,1260,"OS 负责组织任务和资源；平台负责兑现地址、缓存与完成语义。算子分工及具体连接仍待验证。",27,anchor="middle",color=C["muted"])
    return f


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",type=Path,required=True)
    args=ap.parse_args()
    args.out_dir.mkdir(parents=True,exist_ok=False)
    layouts=[f.save(args.out_dir) for f in (software_stacks(),inference_flow())]
    (args.out_dir/"layout.json").write_text(json.dumps(layouts,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'figures':len(layouts),'arrows':sum(len(f['arrows']) for f in layouts),'output':str(args.out_dir)}))


if __name__=="__main__":main()
