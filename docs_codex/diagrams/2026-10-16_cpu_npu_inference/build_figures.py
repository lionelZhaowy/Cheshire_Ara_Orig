#!/usr/bin/env python3
"""Four source-based industrial diagrams; standard library only.

Continuous connectors and explicit text/shape objects support native PPTX export.
The small SVG helper follows the repository's earlier L01 figure generators.
Write to a fresh directory to protect reviewed assets.
"""
import argparse
import json
from html import escape
from pathlib import Path

W, H = 2400, 1350
FONT = "WenQuanYi Zen Hei"
C = dict(ink="#29292D", muted="#606773", control="#765489", data="#314D66",
         local="#187C78", artifact="#B96043", cpu="#F1D7D9", memory="#D8E8F4",
         shared="#D9EEE8", bus="#F5E1C9", software="#E8DFED", region="#F5F7F9")


class Figure:
    def __init__(self, name, title, subtitle):
        self.name, self.boxes, self.arrows = name, {}, []
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
                      f'<title>{escape(title)}</title>', '<defs>']
        for k in ('control', 'data', 'local', 'artifact'):
            self.parts.append(f'<marker id="marker-{k}" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="{C[k]}"/></marker>')
        self.parts.append('</defs>')
        self.rect('page', 0, 0, W, H, '#FFFFFF', stroke='none')
        self.text(1200, 68, title, 42, anchor='middle', bold=True)
        self.text(1200, 117, subtitle, 26, anchor='middle', color=C['muted'])

    def text(self, x, y, text, size=26, anchor='start', bold=False, color=None, owner=''):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{"bold" if bold else "normal"}" text-anchor="{anchor}" fill="{color or C["ink"]}" data-owner="{owner}">{escape(text)}</text>')

    def rect(self, key, x, y, w, h, fill, stroke=None, dashed=False):
        self.boxes[key] = dict(x=x, y=y, width=w, height=h)
        self.parts.append(f'<rect id="{key}" x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke or C["ink"]}" stroke-width="2"' + (' stroke-dasharray="10 6"' if dashed else '') + '/>')

    def box(self, key, x, y, w, h, title, lines=(), fill='#FFFFFF', dashed=False, size=29):
        self.rect(key, x, y, w, h, fill, dashed=dashed)
        first = y + (h - 38 * (1 + len(lines))) / 2 + 29
        self.text(x+w/2, first, title, size, anchor='middle', bold=True, owner=key)
        for i, line in enumerate(lines):
            self.text(x+w/2, first+38*(i+1), line, 25, anchor='middle', owner=key)

    def edge(self, key, points, kind='control', both=False, source='', target=''):
        self.parts.append(f'<polyline id="{key}" points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{C[kind]}" stroke-width="3" stroke-linejoin="miter" marker-end="url(#marker-{kind})"' + (f' marker-start="url(#marker-{kind})"' if both else '') + '/>')
        self.arrows.append(dict(id=key, points=points, kind=kind, bidirectional=both, source=source, target=target))

    def label(self, x, y, text, kind='control', anchor='middle'):
        self.text(x, y, text, 24, anchor=anchor, color=C[kind])

    def save(self, dest):
        (dest/(self.name+'.svg')).write_text('\n'.join(self.parts+['</svg>'])+'\n')
        return dict(name=self.name, canvas=[W, H], boxes=self.boxes, arrows=self.arrows)


def deployment():
    f = Figure('deployment-chain', 'CPU＋NPU 推理：从模型到一次设备任务',
               '通用职责归纳；离线编译与目标执行分开，具体 API 和算子覆盖依平台实现')
    f.rect('host', 50, 170, 2300, 280, C['region'])
    f.text(80, 215, '开发主机：转换与编译', 30, bold=True)
    f.box('model', 100, 265, 500, 130, '模型与输入约束', ['图 / 权重 / 校准数据 / 形状'])
    f.box('compiler', 800, 265, 650, 130, '面向目标的编译', ['量化 / 划分 / 布局 / 分块 / 内存规划'], fill=C['software'])
    f.box('artifact', 1750, 265, 500, 130, '部署产物', ['模型包 / 命令流 / 生成代码'], fill=C['bus'])
    f.edge('compile', [(600,330),(800,330)], 'artifact', source='model', target='compiler')
    f.edge('emit', [(1450,330),(1750,330)], 'artifact', source='compiler', target='artifact')
    f.label(700,307,'解析', 'artifact'); f.label(1600,307,'目标相关产物', 'artifact')
    f.rect('soc', 50, 570, 2300, 600, C['region'])
    f.text(80, 613, '目标 SoC：加载、调度与执行', 30, bold=True)
    f.box('runtime',100,665,520,140,'CPU 应用 / 推理运行时',['加载模型 / 准备张量 / 调度子图'],fill=C['software'])
    f.box('cpu',850,665,500,140,'CPU 算子与后处理',['后端选择的 CPU 工作'],fill=C['cpu'])
    f.box('result',1770,665,480,140,'应用消费结果',['检查状态 / 后处理 / 输出'])
    f.box('driver',100,980,520,140,'设备与平台适配',['地址 / 同步 / 提交 / 等待 / 恢复'],fill=C['software'])
    f.box('npu',850,980,500,140,'NPU 执行资源',['命令控制 / 搬运 / 计算'],fill=C['cpu'])
    f.box('buffers',1770,980,480,140,'张量存储与工作区',['外存 / 片上 SRAM；按平台规划'],fill=C['memory'])
    f.edge('deploy',[(2000,395),(2000,510),(560,510),(560,665)],'artifact',source='artifact',target='runtime')
    f.label(1270,487,'部署与加载', 'artifact')
    f.edge('cpu-call',[(620,735),(850,735)],source='runtime',target='cpu');f.label(735,711,'函数调用')
    f.edge('cpu-result',[(1350,735),(1770,735)],'data',source='cpu',target='result');f.label(1560,711,'CPU 路径结果','data')
    f.edge('submit',[(360,805),(360,980)],source='runtime',target='driver');f.label(380,900,'设备任务',anchor='start')
    f.edge('device-control',[(620,1050),(850,1050)],both=True,source='driver',target='npu');f.label(735,1026,'提交 / 完成')
    f.edge('tensor-access',[(1350,1050),(1770,1050)],'data',both=True,source='npu',target='buffers');f.label(1560,1026,'张量读写 / 搬运','data')
    f.edge('cpu-buffers',[(1100,805),(1100,880),(1880,880),(1880,980)],'data',both=True,source='cpu',target='buffers')
    f.label(1440,857,'CPU 与设备交接缓冲区','data')
    f.edge('consume',[(2150,980),(2150,805)],'data',source='buffers',target='result');f.label(2170,910,'同步后消费','data',anchor='start')
    f.text(1200,1232,'棕：编译产物流转    紫：调用、控制与状态    蓝灰：张量与结果',27,anchor='middle')
    f.text(1200,1290,'图中的边界是软件职责；CPU 回退、内存共享和任务完成都需要明确实现。',26,anchor='middle',color=C['muted'])
    return f


def invocation():
    f=Figure('invocation-paths','三种加速器调用方式：相似目标，不同接口',
             '分别取 NVDLA headless Linux、Ethos-U Cortex-M、Gemmini RoCC 路径')
    columns=[
        (50,'NVDLA','应用加载 loadable',['绑定输入与输出'],
         '用户态运行时 UMD',['构造 DLA task'],
         '内核驱动 KMD',['engine scheduler / 寄存器 / IRQ'],
         'NVDLA 功能块',['DMA / 卷积 / 后处理'],
         'DRAM / 可选片上 SRAM',['张量缓冲区'],['运行时 API','提交任务','配置 / 完成']),
        (835,'Arm Ethos-U','应用执行 TFLite 模型',['Vela 生成 NPU 子图'],
         'TFLM 与 CPU kernels',['CPU 算子 / Ethos-U custom op'],
         'Ethos-U core driver',['命令流 / 区域基址 / 中断处理'],
         'Ethos-U NPU',['执行已编译的命令流'],
         '平台内存 / tensor arena',['常量 / 激活 / scratch'],['Invoke','custom op 调用','启动 / 完成']),
        (1620,'Gemmini','RISC-V 应用 / 算子库',['矩阵 / 卷积 / 可选框架适配'],
         'C 宏与分块算子',['配置 / mvin / compute / mvout'],
         'CPU 自定义指令 → RoCC',['Gemmini 命令与同步'],
         'Gemmini 阵列与本地存储',['scratchpad / accumulator'],
         'SoC 主存层次',['经 DMA 与 TileLink 访问'],['库函数','发射指令','执行命令'])]
    for x,title,app,al,run,rl,interface,il,hw,hl,mem,ml,labels in columns:
        p=title.split()[0].lower()
        f.rect(p+'region',x,175,730,1080,C['region'])
        f.text(x+365,230,title,34,anchor='middle',bold=True)
        f.box(p+'app',x+45,270,640,105,app,al)
        f.box(p+'run',x+45,455,640,125,run,rl,fill=C['software'])
        f.box(p+'if',x+45,665,640,125,interface,il,fill=C['software'],size=28)
        f.box(p+'hw',x+45,900,640,130,hw,hl,fill=C['cpu'])
        f.box(p+'mem',x+45,1140,640,90,mem,ml,fill=C['memory'],size=28)
        for j,(start,end,a,b) in enumerate([(375,455,'app','run'),(580,665,'run','if'),(790,900,'if','hw')]):
            f.edge(p+str(j),[(x+365,start),(x+365,end)],both=(j==2 and title!='Gemmini'),source=p+a,target=p+b)
            f.label(x+390,(start+end)/2+7,labels[j],anchor='start')
        f.edge(p+'data',[(x+365,1030),(x+365,1140)],'data',both=True,source=p+'hw',target=p+'mem')
        f.label(x+390,1094,'数据访问',kind='data',anchor='start')
    f.text(1200,1310,'紫：调用 / 指令 / 控制    蓝灰：数据；各列省略 CPU 的普通访存，三者不是同一总线接口。',26,anchor='middle',color=C['muted'])
    return f


def deeploy():
    f=Figure('deeploy-siracusa','Deeploy / Siracusa：编译安排计算与显式搬运',
             '依据论文的部署机制归纳；图中 L1 / L2 为软件管理的片上存储，不是 CVA6 缓存')
    f.rect('host',50,175,2300,235,C['region'])
    f.text(80,215,'开发主机',29,bold=True)
    f.box('onnx',100,250,440,110,'量化 ONNX',['模型 / 形状 / 数据类型'])
    f.box('planner',760,250,810,110,'Deeploy 编译',['算子映射 / 分块约束 / 静态内存规划'],fill=C['software'])
    f.box('code',1790,250,460,110,'生成 C 代码',['算子调用 / DMA / 同步'],fill=C['bus'])
    f.edge('parse',[(540,305),(760,305)],'artifact',source='onnx',target='planner')
    f.edge('generate',[(1570,305),(1790,305)],'artifact',source='planner',target='code')
    f.rect('chip',50,515,2300,690,C['region'])
    f.text(80,555,'Siracusa：主控与异构计算集群',29,bold=True)
    f.box('controller',100,620,390,140,'主控核',['启动计算集群 / 应用控制'],fill=C['cpu'])
    f.box('cluster',780,620,540,140,'8 核 RISC-V 集群',['执行 CPU kernels / 管理分块'],fill=C['cpu'])
    f.box('npu',1740,620,510,140,'N-Eureka NPU',['常量权重线性层 → 1×1 卷积'],fill=C['cpu'])
    f.edge('deploy',[(2020,360),(2020,460),(680,460),(680,590),(295,590),(295,620)],'artifact',source='code',target='controller')
    f.label(1170,440,'交叉编译与加载到目标程序','artifact')
    f.edge('launch',[(490,690),(780,690)],source='controller',target='cluster');f.label(635,667,'任务派发')
    f.edge('configure',[(1320,690),(1740,690)],source='cluster',target='npu');f.label(1530,666,'配置 / 等待 / 同步')
    f.box('arbiter',900,865,1020,80,'TCDM 访问互连 / 仲裁',fill=C['bus'],size=29)
    f.edge('core-access',[(1070,760),(1070,865)],'local',both=True,source='cluster',target='arbiter');f.label(1090,819,'CPU 读写','local',anchor='start')
    f.edge('npu-access',[(1840,760),(1840,865)],'local',both=True,source='npu',target='arbiter');f.label(1820,819,'NPU 激活读写','local',anchor='end')
    f.box('l2',100,1035,390,125,'L2 片上存储',['输入 / 激活 / KV / 其他权重'],fill=C['memory'])
    f.box('dma',640,1035,300,125,'集群 DMA',['L2 ↔ L1 分块'],fill=C['bus'])
    f.box('l1',1110,1035,600,125,'L1 TCDM',['CPU 与 NPU 共享的数据块'],fill=C['shared'])
    f.box('nms',1900,1035,350,125,'NMS 权重存储',['SRAM / MRAM'],fill=C['memory'])
    f.edge('l2-dma',[(490,1098),(640,1098)],'data',both=True,source='l2',target='dma');f.label(565,1075,'AXI','data')
    f.edge('dma-l1',[(940,1098),(1020,1098),(1020,945)],'local',both=True,source='dma',target='arbiter')
    f.edge('tcdm',[(1410,945),(1410,1035)],'local',both=True,source='arbiter',target='l1');f.label(1430,998,'访问 bank','local',anchor='start')
    f.edge('weights',[(2090,1035),(2090,760)],'data',source='nms',target='npu');f.label(2110,930,'专用供权重','data',anchor='start')
    f.edge('dma-control',[(860,760),(860,825),(790,825),(790,1035)],source='cluster',target='dma')
    f.label(770,930,'搬运控制',anchor='end')
    f.text(1200,1255,'紫：控制与同步    蓝灰：主存 / 权重数据    绿：共享 TCDM 数据    棕：编译产物',26,anchor='middle')
    f.text(1200,1310,'静态权重映射到 NPU；其他算子由集群执行。数据驻留、分块和搬运由部署方案共同决定。',26,anchor='middle',color=C['muted'])
    return f


def llm():
    f=Figure('llm-phases','LLM 推理：阶段、状态与异构分工',
             '上部是通用执行关系；下部是 llm.npu 的 prefill 特有优化，不能等同于 decode 加速')
    f.rect('general',50,170,2300,570,C['region'])
    f.text(80,213,'通用自回归推理',30,bold=True)
    f.box('input',100,265,340,130,'CPU 输入准备',['分词 / 输入张量'],fill=C['cpu'])
    f.box('prefill',640,265,470,130,'Prefill',['处理输入 token / 计算 logits'],fill=C['software'])
    f.box('decode',1330,265,380,130,'Decode',['逐 token 推进'],fill=C['software'])
    f.box('sample',1910,265,340,130,'采样与终止判断',['按实现分配到 CPU 等'],fill=C['cpu'])
    f.edge('tokens',[(440,330),(640,330)],'data',source='input',target='prefill');f.label(540,306,'tokens','data')
    f.edge('logits0',[(875,265),(875,230),(2080,230),(2080,265)],'data',source='prefill',target='sample');f.label(1520,209,'首轮 logits','data')
    f.edge('next-token',[(1910,300),(1710,300)],'data',source='sample',target='decode');f.label(1810,277,'下一 token','data')
    f.edge('logits-loop',[(1710,365),(1910,365)],'data',source='decode',target='sample');f.label(1810,406,'后续 logits','data')
    f.box('kv',670,550,1040,130,'KV cache：跨步保留的算法张量',['本步追加 / 后续读取；容量依上下文增长'],fill=C['memory'])
    f.box('out',1910,550,340,130,'应用输出',['首 token / 持续输出'])
    f.edge('create-kv',[(875,395),(875,550)],'local',source='prefill',target='kv');f.label(895,479,'生成 KV','local',anchor='start')
    f.edge('update-kv',[(1520,395),(1520,550)],'local',both=True,source='decode',target='kv')
    f.label(1540,479,'读取 / 追加 KV','local',anchor='start')
    f.edge('emit',[(2080,395),(2080,550)],'data',source='sample',target='out');f.label(2100,479,'输出 token','data',anchor='start')
    f.rect('special',50,805,2300,400,'#FAF6F0',dashed=True)
    f.text(80,850,'llm.npu 案例：移动平台上的 prefill 优化',30,bold=True)
    f.box('chunks',100,930,410,180,'固定大小的 prompt 块',['保持因果依赖', '复用预编译子图'],fill=C['software'])
    f.box('split',700,930,430,180,'张量 / 块级分配',['识别离群值与硬件适配', '按依赖安排执行'],fill=C['software'])
    f.box('npu',1390,900,400,100,'NPU 主计算',['适配的整数运算'],fill=C['cpu'])
    f.box('cpu-gpu',1390,1070,400,100,'CPU / GPU',['离群值与其他必要工作'],fill=C['cpu'])
    f.box('merge',1980,980,300,140,'同步与合并',['交给后续计算'],fill=C['shared'])
    f.edge('chunk-schedule',[(510,1020),(700,1020)],source='chunks',target='split');f.label(605,996,'调度')
    f.edge('offload',[(1130,975),(1260,975),(1260,950),(1390,950)],source='split',target='npu')
    f.edge('shadow',[(1130,1065),(1210,1065),(1210,1120),(1390,1120)],source='split',target='cpu-gpu')
    f.edge('partial-npu',[(1790,950),(1890,950),(1890,1010),(1980,1010)],'data',source='npu',target='merge')
    f.edge('partial-cpu',[(1790,1120),(1900,1120),(1900,1090),(1980,1090)],'data',source='cpu-gpu',target='merge')
    f.text(1200,1258,'紫：调用 / 调度    蓝灰：token / 结果    绿：KV 数据    虚线区：特定论文机制',26,anchor='middle')
    f.text(1200,1310,'本工程没有已确认的 GPU 路径；Ara 能否承担相关算子，需要另行适配与验证。',26,anchor='middle',color=C['muted'])
    return f


def main():
    p=argparse.ArgumentParser();p.add_argument('--out-dir',required=True,type=Path)
    out=p.parse_args().out_dir;out.mkdir(parents=True,exist_ok=False)
    layouts=[f.save(out) for f in (deployment(),invocation(),deeploy(),llm())]
    (out/'layout.json').write_text(json.dumps(layouts,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'figures':len(layouts),'arrows':sum(len(l['arrows']) for l in layouts),'output':str(out)}))


if __name__=='__main__':main()
