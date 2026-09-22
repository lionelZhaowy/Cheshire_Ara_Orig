#!/usr/bin/env python3
"""Build an offline register reference from a bounded set of local headers.
Offsets/fields are factual extracts; access semantics must be read in RTL/HJSON.
Original headers retain their own copyright and licenses, linked per group.
"""
from pathlib import Path
from html import escape as e
import re,json,hashlib
ROOT=Path(__file__).resolve().parent.parent
REPO=ROOT.parent.parent
OT='.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/include/'
GROUPS=[
 ('SoC','0x03000000','sw/include/regs/cheshire.h','boot-debug'),
 ('LLC','0x03001000','sw/include/regs/axi_llc.h','dma-llc'),
 ('GPIO','0x03005000',OT+'gpio_regs.h','uart-gpio'),
 ('I2C','0x03003000',OT+'i2c_regs.h','i2c'),
 ('SPI host','0x03004000',OT+'spi_host_regs.h','spi'),
 ('CLINT','0x02040000','sw/include/regs/clint.h','interrupts'),
 ('PLIC','0x04000000',OT+'rv_plic_regs.h','interrupts'),
 ('iDMA 2D','0x01000000','sw/include/regs/idma.h','dma-llc'),
 ('Serial Link','0x03006000','sw/include/regs/serial_link.h','stream-io'),
 ('VGA','0x03007000','sw/include/regs/axi_vga.h','stream-io'),
 ('AXI RT（可选）','0x020c0000','sw/include/regs/axi_rt.h','dma-llc'),
 ('Bus error 单元','见章节内各读/写子块','.bender/git/checkouts/unbent-a93c32aef5b319fd/driver/bus_err_unit.h','dma-llc'),
]
def main():
    intro='''<div class="goals"><strong>用途与前置</strong><p>学会由基址、字节偏移和字段组成访问；先读寄存器与驱动方法。本表不代替外设章节的访问语义。</p></div>
<p><span class="badge">源码静态确认</span>只提取下列本地头文件中的常量宏；没有对总线执行自动扫描。头文件含预生成的多实例项，不代表本配置实例全部存在，例如 iDMA 仅配置一个 stream。</p>
<p>访问属性、读清零、读触发、保留位和对齐不能由宏名推出。原始文件的版权及许可证沿源码链接保留；此索引不是重新授权的完整驱动。</p>
<label class="search-label" for="reg-search">查寄存器、字段或地址</label><input id="reg-search" type="search" placeholder="例如 GPIO、NEXT_ID、0x03004000" autocomplete="off"><p id="reg-count" aria-live="polite"></p>
<p>关闭 JavaScript 后所有寄存器仍可阅读。UART 的 DLAB 别名、CLIC、USB OHCI、IRQ Router、Debug 见 <a href="uart-gpio.html">UART</a>、<a href="interrupts.html">中断</a>、<a href="stream-io.html#usb">USB</a>、<a href="boot-debug.html#debug">调试</a>中的手工核对表；这些接口没有在这里强行套用统一生成头。</p>'''
    out=[intro]; manifest={}; total=0
    for i,(label,base,path,chapter) in enumerate(GROUPS):
        data=(REPO/path).read_text(); manifest[path]=hashlib.sha256(data.encode()).hexdigest()
        data=data.replace('\\\n',' ')
        macros=re.findall(r'^#define\s+(\w+)\s+([^\n]+)',data,re.M)
        offsets=[(n,v.strip())for n,v in macros if n.endswith('_REG_OFFSET')]
        rows=[]
        for n,v in offsets:
            prefix=n[:-len('_REG_OFFSET')]
            fields=[f'{k} = {value.strip()}'for k,value in macros if k.startswith(prefix+'_') and k!=n and k.endswith(('_BIT','_MASK','_OFFSET'))]
            try: address=f'0x{int(base,16)+int(v,0):08x}'
            except ValueError: address='子块基址 + 偏移'
            rows.append(f'<tr data-register="{e(label)}"><td>{e(prefix)}</td><td>{e(v)}<br>{address}</td><td>'+('<br>'.join(e(x)for x in fields) or '整字/语义见源码')+'</td></tr>')
        total+=len(rows)
        out.append(f'<section class="register-group"><h2 id="group-{i}">{label} · {base}</h2><p><a href="{chapter}.html">回到教学章节</a> · <a href="../../{path}">{e(path)}</a></p><table><thead><tr><th>寄存器</th><th>偏移 / 地址</th><th>字段常量（不是访问权限）</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></section>')
    out.append('''<h2 id="quiz">自测</h2><details><summary>看到 REG_OFFSET 就可以无副作用读取吗？</summary><p>不可以。iDMA NEXT_ID 读取会提交任务，bus error 的 ERR_CODE 读取会弹出记录，UART RBR 读取会取走数据。先查访问语义。</p></details><details><summary>头文件中的所有索引都能访问吗？</summary><p>不一定。还要确认实例数量、参数化寄存器生成版本及地址译码范围。先用 HW_FEATURES 和硬件配置核对，禁止靠扫描未知 MMIO 探测。</p></details>''')
    (ROOT/'content/registers.html').write_text('\n'.join(out)+'\n')
    (ROOT/'evidence/advanced-register-sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'{len(GROUPS)} header groups, {total} register offsets; no hardware accesses')
if __name__=='__main__':main()
