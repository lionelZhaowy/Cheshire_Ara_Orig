#!/usr/bin/env python3
"""Assemble offline pages from content/*.html; stdlib only. Never reads the network."""
from pathlib import Path
from html import escape
import re
ROOT = Path(__file__).resolve().parent.parent
PAGES = [
 ('index','学习路线','从熟悉的 RTL 出发，把程序运行的每一步连起来。'),
 ('architecture','01 · 一张图认识系统','CVA6 执行标量指令，Ara 执行向量指令，Cheshire 把系统接起来。'),
 ('foundations','02 · 必要基础','从数组、寄存器和一次总线握手理解 RISC-V 与 AXI。'),
 ('configuration','03 · 配置何时生效','先选源码，再展开硬件；软件选项与运行时状态还要分别对齐。'),
 ('lifecycle','04 · C 程序的一生','从一行 C 到 ELF，再从复位走到 main 和退出码。'),
 ('simulation','05 · 仿真实验闭环','把软件、RTL、DPI、展开、加载和结果检查分成可定位的步骤。'),
 ('memory','06 · 访存、DMA 与 RVV','沿真实连接追踪数据，知道哪些路径并不自动一致。'),
 ('labs','实验手册 · 从 Hello 到 RVV','同一个程序，六个阶段；每一步都有产物、判据和停止条件。'),
 ('future','07 · 独立工程与 AI 导读','从可重现基线走向 ASIC；用明确假设估算模型容量和带宽。'),
 ('evidence','证据、缺口与源码索引','源码基准 379ae454 · 2026-09-22 · L01'),
 ('advanced','进阶路线 · 外设与执行机制','从寄存器语义走到驱动、硬件行为和可检验的结果。'),
 ('system','08 · 完整系统与时钟复位','逐层展开 SoC、互连、板级资源和时钟边界；区分电源意图与现有实现。'),
 ('execution','09 · 从软件到硬件执行','CVA6 如何发射与提交指令，Ara 如何分发和完成向量工作。'),
 ('register-driver','10 · 寄存器与驱动方法','读写副作用、访问宽度、并发、超时与观测，构成驱动的基本契约。'),
 ('uart-gpio','11 · UART 与 GPIO','从寄存器别名、FIFO 到引脚，再从 GPIO 事件走回 CPU。'),
 ('i2c','12 · I2C 与 EEPROM','把一笔事务拆成格式队列、开漏信号、ACK、时序与软件状态。'),
 ('spi','13 · SPI、NOR 与 SD','控制器负责移位，设备协议决定命令、地址、忙等待和数据校验。'),
 ('interrupts','14 · CLINT、PLIC 与 CLIC','追踪一次中断的产生、屏蔽、路由、接收、清源和完成。'),
 ('dma-llc','15 · DMA、LLC 与总线治理','描述符、缓冲区所有权、缓存边界、带宽约束与错误记录。'),
 ('stream-io','16 · Serial Link、VGA 与 USB','剖析三个主动访存的接口，以及当前环境离端到端验证的距离。'),
 ('boot-debug','17 · 启动、调试与系统寄存器','串起 Boot ROM、JTAG、系统总线访问、scratch 协议和外部存储。'),
 ('capstone','18 · 中断与 DMA 综合实验','一个可构建的单核示例：软注入 GPIO 中断、定时器、DMA 校验与失败隔离。'),
 ('registers','附录 · 离线寄存器索引','从本地头文件提取偏移与字段，搜索后返回对应的教学解释。'),
 ('advanced-evidence','进阶证据与实验清单','源码证据、轻量构建、页面预览及尚未执行的硬件验收。'),
]

def render():
    for i,(slug,title,subtitle) in enumerate(PAGES):
        body=(ROOT/'content'/f'{slug}.html').read_text()
        nav=''
        for j,(s,t,_) in enumerate(PAGES):
            if j in (0,10): nav += f'<p class="nav-group">{"入门主线" if j==0 else "进阶剖析"}</p>'
            nav += f'<a href="{s}.html"'+(' aria-current="page"' if s==slug else '')+f'>{escape(t)}</a>'
        heads=re.findall(r'<h2 id="([^"]+)">(.*?)</h2>',body)
        toc=''.join(f'<a href="#{id}">{re.sub("<[^>]+>","",txt)}</a>' for id,txt in heads)
        prev=f'<a href="{PAGES[i-1][0]}.html">← {PAGES[i-1][1]}</a>' if i else '<a href="labs.html">打开实验手册 →</a>'
        nxt=f'<a href="{PAGES[i+1][0]}.html">{PAGES[i+1][1]} →</a>' if i+1<len(PAGES) else '<a href="index.html">回到学习路线</a>'
        text=f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} | Cheshire 实验课堂</title><link rel="stylesheet" href="assets/site.css"><script defer src="assets/site.js"></script></head>
<body><a class="skip" href="#main">跳到正文</a><aside class="sidebar"><a class="brand" href="index.html">CHESHIRE <span>实验课堂</span></a><p class="edition">CVA6 × Ara · 本地源码教材</p><nav aria-label="章节">{nav}</nav><div class="sidebar-foot">离线可读 · 无 CDN<br>证据与执行状态请看每章标记<br><a href="README.md">维护说明</a></div></aside>
<div class="workspace"><header class="topbar"><span>L01 / {"进阶剖析" if i>=10 else "入门学习主线"}</span><a href="{"advanced-evidence" if i>=10 else "evidence"}.html">源码与证据 ↗</a></header><main id="main"><div class="chapter-head"><p class="eyebrow">READ · TRACE · BUILD · EXPLAIN</p><h1>{title}</h1><p class="subtitle">{subtitle}</p></div><nav class="toc" aria-label="本页目录">{toc}</nav>{body}<nav class="nextprev" aria-label="上下章">{prev}{nxt}</nav></main><footer>本教材图表为教学示意；步骤演示不是真实仿真波形。已有板测不等于本轮回归。</footer></div></body></html>'''
        (ROOT/f'{slug}.html').write_text(text)
    print(f'Built {len(PAGES)} offline pages')
if __name__=='__main__': render()
