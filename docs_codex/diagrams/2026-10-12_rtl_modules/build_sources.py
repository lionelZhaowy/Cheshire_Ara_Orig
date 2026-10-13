"""Attach checked RTL anchors to the hand-written module guide; fingerprint inputs."""
from pathlib import Path
import hashlib
import json
import os
import subprocess

OUT = Path(__file__).resolve().parent
REPO = OUT.parents[2]
GUIDE = REPO/'docs_codex/rtl_modules'
DEP = '.bender/git/checkouts/'
SOC = 'hw/cheshire_soc.sv'
PKG = 'hw/cheshire_pkg.sv'
REG = DEP+'register_interface-902ad5bfde7bb98c/src/'
CC = DEP+'common_cells-7f7ae0f5e6bf7fb5/src/'
AXI = DEP+'axi-ecdc900686449c15/src/'
OT = DEP+'opentitan_peripherals-7b624fb57f78de9a/src/'
UART = DEP+'apb_uart-38dcfab592cbc1a1/src/'
CLINT = DEP+'clint-de4a234303f657d0/src/'
CLIC = DEP+'clic-360fff7ce2d41116/src/'
ROUTER = DEP+'irq_router-376b3d113c15d0ef/'
DBG = DEP+'riscv-dbg-1a98531d53bb4602/src/'
SL = DEP+'serial_link-6e09ea4800bad616/'
VGA = DEP+'axi_vga-74c838b44ce780d5/src/'
DMA = DEP+'idma-77bf7fa56d324e6a/target/rtl/'
CPU = DEP+'cva6-20c9d7cbe0dd6995/core/'
LLC = DEP+'axi_llc-5fb8850caad4fcfa/'

# A role, actual path, and a verbatim, searchable source anchor per row.
SOURCES = {
'00_regbus': [
 ('SoC：AXI 到 Regbus',SOC,'axi_to_reg_v2 #('),
 ('SoC：地址选择',SOC,') i_reg_demux_decode ('),
 ('扩展配置/两级路由',PKG,'RegExtRegionIdx;'),
 ('桥：bank 数与具体参数',REG+'axi_to_reg_v2.sv','localparam int unsigned NumBanks'),
 ('AXI 请求与返回信息',AXI+'axi_to_detailed_mem.sv',') i_fork ('),
 ('元数据缓冲',AXI+'axi_to_detailed_mem.sv',') i_meta_buf ('),
 ('流到存储握手',CC+'stream_to_mem.sv','module stream_to_mem'),
 ('分拆请求与重组响应',CC+'mem_to_banks_detailed.sv','module mem_to_banks_detailed'),
 ('跨域完整请求/响应',REG+'reg_cdc.sv','module reg_cdc'),
 ('项目本地架构说明','docs/um/arch.md','Regbus'),
],
'01_uart': [
 ('SoC 条件生成与接线',SOC,') i_uart ('),
 ('图①：Regbus/APB 适配',UART+'reg_uart_wrap.sv','reg_to_apb #('),
 ('图②：APB 地址位选择',UART+'reg_uart_wrap.sv','.PADDR'),
 ('图③：波特率发生器',UART+'apb_uart.sv','uart_baudgen UART_BG16'),
 ('图④⑦：TX/RX 队列',UART+'apb_uart.sv','UART_TXFF'),
 ('图⑤⑥：收发器',UART+'apb_uart.sv','uart_transmitter UART_TX'),
 ('图⑧：IRQ',UART+'apb_uart.sv','uart_interrupt UART_IIC'),
 ('软件初始化/访问宽度','sw/lib/dif/uart.c','void uart_init'),
],
'02_i2c': [
 ('SoC 15 路事件/引脚',SOC,') i_i2c ('),
 ('图①：寄存器与 core 连接',OT+'i2c/rtl/i2c.sv',') u_reg ('),
 ('图②：FMT 字段组合',OT+'i2c/rtl/i2c_core.sv','assign fmt_fifo_wdata'),
 ('图②④⑥⑦：FIFO 实例',OT+'i2c/rtl/i2c_core.sv','prim_fifo_sync #('),
 ('图③⑤：时序与引脚',OT+'i2c/rtl/i2c_core.sv',') u_i2c_fsm ('),
 ('图⑧：事件锁存/使能',OT+'i2c/rtl/i2c_core.sv','intr_hw_fmt_threshold'),
],
'03_spi': [
 ('SoC 片选/引脚/IRQ',SOC,') i_spi_host ('),
 ('图①②：命令队列',OT+'spi_host/rtl/spi_host.sv','spi_host_command_queue #('),
 ('图④：数据窗口',OT+'spi_host/rtl/spi_host.sv','spi_host_window #('),
 ('图⑤⑨：数据 FIFO',OT+'spi_host/rtl/spi_host.sv','spi_host_data_fifos #('),
 ('图③⑥⑦⑧：核心实例',OT+'spi_host/rtl/spi_host_core.sv','spi_host_byte_merge'),
 ('溢出/下溢/使能约束',OT+'spi_host/rtl/spi_host.sv','assign error_overflow'),
],
'04_gpio': [
 ('SoC GPIO 参数/接线',SOC,') i_gpio ('),
 ('图①：输入滤波',OT+'gpio/rtl/gpio.sv','prim_filter_ctr #('),
 ('图⑤⑥：输出/使能更新',OT+'gpio/rtl/gpio.sv','cio_gpio_q'),
 ('图②③：中断检测/锁存',OT+'gpio/rtl/gpio.sv','prim_intr_hw #('),
 ('图④：寄存器连接',OT+'gpio/rtl/gpio.sv','gpio_reg_top #('),
],
'05_plic': [
 ('SoC PLIC 目标连接',SOC,') i_plic ('),
 ('图①：同步与触发类型',OT+'rv_plic/rtl/rv_plic.sv','LevelEdgeTrig ='),
 ('图②：pending/active',OT+'rv_plic/rtl/rv_plic_gateway.sv','module rv_plic_gateway'),
 ('图③：最大值树/阈值',OT+'rv_plic/rtl/rv_plic_target.sv','prim_max_tree #('),
 ('图④：claim/complete',OT+'rv_plic/rtl/rv_plic.sv','claim_re'),
 ('生成寄存器入口',OT+'rv_plic/rtl/rv_plic_reg_top.sv','module rv_plic_reg_top'),
],
'06_clint_clic': [
 ('SoC CLINT 连接',SOC,') i_clint ('),
 ('图 A：计数、比较、MSIP',CLINT+'clint.sv','module clint'),
 ('RTC 同步与边沿',CLINT+'clint.sv','clint_sync_wedge'),
 ('图 B①：输入与生成条件',SOC,'assign clic_intr'),
 ('图 B②③④：选择/握手',CLIC+'clic.sv','module clic'),
 ('图 B⑤：逐源寄存器',CLIC+'clic.sv','clicint_reg_top #('),
 ('当前时间读取 HAL','sw/lib/dif/clint.c','uint64_t clint_get_mtime'),
 ('待核查睡眠条件','sw/lib/dif/clint.c','void clint_sleep_until'),
 ('已有 CLIC 程序（未本次运行）','sw/tests/clic_basic.spm.S','main:'),
],
'07_irq_router': [
 ('图①：外部源同步',SOC,') i_ext_intr_sync ('),
 ('SoC Router/旁路生成',SOC,') i_irq_router ('),
 ('图②③④：源复制与掩码',ROUTER+'rtl/irq_router.sv','module irq_router'),
 ('目标掩码复位规格',ROUTER+'gen/irq_router_regs.hjson','resval: 1'),
 ('SoC 目标编号定义',SOC,'IntrRtdCoreBase'),
],
'08_bootrom': [
 ('图①③：存储适配与 FF',SOC,') i_reg_to_bootrom ('),
 ('图②：组合 ROM', 'hw/bootrom/cheshire_bootrom.sv','localparam unsigned NumWords'),
 ('启动汇编入口','hw/bootrom/cheshire_bootrom.S','_start:'),
 ('启动 C 软件','hw/bootrom/cheshire_bootrom.c','int main'),
 ('ROM 链接布局','hw/bootrom/cheshire_bootrom.ld','SECTIONS'),
],
'09_soc_regs': [
 ('图③：硬件只读字段来源',SOC,'assign reg_hw2reg'),
 ('图①④：直接 Regbus/响应','hw/regs/cheshire_reg_top.sv','assign reg_we'),
 ('图②：存储寄存器实例','hw/regs/cheshire_reg_top.sv','prim_subreg #('),
 ('寄存器规格修改入口','hw/regs/cheshire_regs.hjson','name:     "scratch"'),
],
'10_jtag_debug': [
 ('SoC DM / ndmreset 接线',SOC,') i_dbg_dm_top ('),
 ('图①：DMI CDC',DBG+'dmi_jtag.sv','dmi_cdc i_dmi_cdc'),
 ('图②：DM 子模块',DBG+'dm_top.sv','module dm_top'),
 ('图④：SBA 转 AXI',SOC,') i_dbg_sba_axi_from_mem ('),
 ('图⑤：调试存储窗',SOC,'axi_to_mem_interleaved #('),
 ('CPU Debug 地址配置',PKG,'ret.HaltAddress'),
],
'11_serial_link': [
 ('图①：SoC 出站适配',SOC,') i_serial_link_tx_id_remap ('),
 ('SoC 时钟/复位/隔离接线',SOC,') i_serial_link ('),
 ('图②：network',SL+'src/serial_link.sv',') i_serial_link_network ('),
 ('图③④⑤：层间连接',SL+'src/serial_link.sv',') i_serial_link_data_link ('),
 ('图⑥：可选配置跨域',SL+'src/serial_link.sv',') i_cdc_cfg ('),
 ('官方分层说明',SL+'doc/README.md','## Architecture'),
],
'12_vga': [
 ('SoC 配置/AXI/错误观察',SOC,'axi_vga #('),
 ('图①③：寄存器和像素使能',VGA+'axi_vga.sv','assign clk_cnt_d'),
 ('图②：读取与像素选择',VGA+'axi_vga_fetcher.sv','module axi_vga_fetcher'),
 ('图④⑤：拆分/FIFO/信用',VGA+'axi_vga.sv','axi_burst_splitter #('),
 ('显示时序',VGA+'axi_vga_timing_fsm.sv','module axi_vga_timing_fsm'),
 ('当前 RRESP 待处理点',VGA+'axi_vga_fetcher.sv','TODO check req.r.resp'),
],
'13_usb': [
 ('SoC 两时钟域接线',SOC,') i_spinal_usb_ohci ('),
 ('图①：Reg→AXI','hw/future/spinal_usb_ohci.sv',') i_reg_to_axi_ctrl ('),
 ('图⑤：DMA 位宽/地址适配','hw/future/spinal_usb_ohci.sv',') i_axi_dw_converter_dma ('),
 ('图②：OHCI 前端','hw/future/UsbOhciAxi4.v','UsbOhciAxi4_UsbOhci front_ohci ('),
 ('图③：CDC','hw/future/UsbOhciAxi4.v','UsbOhciAxi4_CtrlCc cc ('),
 ('图④：数字 PHY','hw/future/UsbOhciAxi4.v','UsbOhciAxi4_UsbLsFsPhy back_phy ('),
],
'14_idma': [
 ('SoC 独立控制与数据端口',SOC,') i_idma ('),
 ('图①：内部 Reg typedef 与转换','hw/cheshire_idma_wrap.sv','`REG_BUS_TYPEDEF_ALL'),
 ('图②：读 NEXT_ID 提交',DMA+'idma_reg64_2d_top.sv','proc_launch'),
 ('控制位宽缺口',DMA+'idma_reg64_2d_reg_top.sv','localparam int DW = 32;'),
 ('图③：二维展开','hw/cheshire_idma_wrap.sv',') i_idma_midend ('),
 ('图④：后端 legalizer',DMA+'idma_backend_rw_axi.sv',') i_idma_legalizer ('),
 ('图⑤：读写口合并','hw/cheshire_idma_wrap.sv',') i_axi_rw_join ('),
 ('图⑥：任务进度','hw/cheshire_idma_wrap.sv',') i_transfer_id_gen_2d ('),
],
'15_interrupt_exception': [
 ('图①②⑤：CPU 实际连接',CPU+'cva6.sv',') commit_stage_i ('),
 ('图③：中断 cause 选择',CPU+'decoder.sv','interrupt_cause ='),
 ('图④：scoreboard 结构',CPU+'scoreboard.sv','module scoreboard'),
 ('图⑤：提交与异常',CPU+'commit_stage.sv','module commit_stage'),
 ('图②：trap 状态',CPU+'csr_regfile.sv','// Manage Exception Stack'),
 ('图⑥：flush',CPU+'controller.sv','always_comb begin : flush_ctrl'),
 ('运行库汇编入口','sw/lib/crt0.S','_start:'),
],
'16_llc_spm': [
 ('SoC 生成/别名/Regbus',SOC,'if (Cfg.LlcOutConnect && Cfg.LlcNotBypass)'),
 ('图 A：描述符与数据单元',LLC+'src/axi_llc_top.sv',') i_hit_miss_unit ('),
 ('图 A⑥：data ways',LLC+'src/axi_llc_ways.sv','module axi_llc_ways'),
 ('图 B①：当前 Regbus 封装',LLC+'src/axi_llc_reg_wrap.sv',') i_llc_config_regfile ('),
 ('图 B②：配置提交/flush',LLC+'src/axi_llc_config.sv','module axi_llc_config'),
 ('SPM 别名常量',PKG,'AmSpmBaseUncached'),
 ('CPU cache 属性定义',PKG,'ret.CachedRegionAddrBase'),
 ('旧官方说明（控制口描述已与代码不同）',LLC+'doc/axi_llc.md','## Configuration and Flush'),
],
}


def main():
    resolved={}
    fingerprints={}
    for topic, rows in SOURCES.items():
        page=GUIDE/(topic+'.md')
        table=['## 代码对应（本次源码快照）','',
               '| 图中职责 | 文件与行号 | 可搜索符号 |',
               '|---|---|---|']
        resolved[topic]=[]
        for role,path,anchor in rows:
            source=REPO/path
            data=source.read_bytes()
            lines=data.decode().splitlines()
            matches=[i+1 for i,s in enumerate(lines) if anchor in s]
            assert matches, (topic,path,anchor)
            line=matches[0]
            rel=os.path.relpath(source,page.parent)
            literal=anchor.strip()
            code=('`` '+literal+' ``') if '`' in literal else ('`'+literal+'`')
            table.append(f'| {role} | [{source.name}:{line}]({rel}#L{line}) | {code} |')
            resolved[topic].append(dict(role=role,path=path,line=line,anchor=anchor))
            fingerprints[path]=hashlib.sha256(data).hexdigest()
        content=page.read_text().split('<!-- RTL_SOURCES -->')[0]
        page.write_text(content+'<!-- RTL_SOURCES -->\n\n'+'\n'.join(table)+'\n')
    report=dict(date='2026-10-12',input_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
                source_sha256=fingerprints,anchors=resolved,
                scope='Local official source/document snapshot; no RTL simulation or board test.')
    (OUT/'source_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(f'Attached {sum(map(len,resolved.values()))} source anchors across {len(resolved)} chapters; {len(fingerprints)} input files.')


if __name__=='__main__':
    main()
