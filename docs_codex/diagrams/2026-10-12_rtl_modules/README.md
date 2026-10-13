# RTL 模块图集

2026-10-12 / L01。主交付是[统一阅读入口](../../rtl_modules/README.md)和 17 篇逐模块解释。本目录存图源、可编辑输出及复现/检查记录；正文和代码对应以模块文档为准。

[20 页原生 PPTX](export/diagrams.pptx)；[源码行号与哈希清单](source_manifest.json)；[检查结果](validation.json)；[本次扩充后的绘图 Prompt](../../maintenance/L01/planning/rtl_module_figures.md)。

## 图稿与内容

| 编号 | 机制 | SVG 母版 |
|---|---|---|
| 00A/B | Regbus 现有通路与自有 IP 寄存器契约，沿用上一轮两图 | [A](../2026-10-12_regbus_ip_integration/01_regbus_whole.svg) / [B](../2026-10-12_regbus_ip_integration/02_ip_register_contract.svg) |
| 01 | UART APB、节拍、独立收发队列 | [UART](01_uart.svg) |
| 02 | I²C 命令/接收与 Target 队列 | [I²C](02_i2c.svg) |
| 03 | SPI 命令队列、数据窗口和串并转换 | [SPI](03_spi.svg) |
| 04 | GPIO 滤波/边沿与 OUT/OE | [GPIO](04_gpio.svg) |
| 05 | PLIC gateway 与 per-target 选择 | [PLIC](05_plic.svg) |
| 06A/B | RTC 计数/比较；CLIC 逐源选择与握手 | [CLINT](06a_clint.svg) / [CLIC](06b_clic.svg) |
| 07 | 源复制与目标位掩码 | [IRQ Router](07_irq_router.svg) |
| 08 | ROM 查表与应答 FF | [BootROM](08_bootrom.svg) |
| 09 | reggen scratch 与 hw2reg | [SoC Regs](09_soc_regs.svg) |
| 10 | DMI CDC、DM 存储窗和 SBA | [JTAG Debug](10_jtag_debug.svg) |
| 11 | Network/Data Link/Allocator/Physical | [Serial Link](11_serial_link.svg) |
| 12 | AR 请求、R FIFO、像素选择与时序 | [VGA](12_vga.svg) |
| 13 | Reg→AXI、OHCI DMA、PHY CDC | [USB](13_usb.svg) |
| 14 | 内部 Reg、任务 FIFO、ND midend 与 AXI backend | [iDMA](14_idma.svg) |
| 15 | CVA6 异常信息与提交/CSR/重定向 | [中断与异常](15_interrupt_exception.svg) |
| 16A/B | Cache miss/数据 way；SPM 分配与提交 | [LLC](16a_llc.svg) / [SPM](16b_spm.svg) |

每个母版对应 `export/<名称>.png`、`.pdf`、`.editable.svg`、`.gray.png`。PPT 顺序为 Regbus 两页，再按 01–16 排序。新的图源共 18 张，没有重写旧 Regbus 图或 SoC 全景图。

## 绘图约定与复现

使用 `publication-figures` 的 SVG→原生 PPT/PDF 后端。画布 1800×980，导出宽 280 mm，图内最小字体 22 SVG units（约 9.7 pt）；这是本批教学图的尺寸选择，不是工艺/出版标准。字体 WenQuanYi Zen Hei；PPT 中字体不嵌入，对端需安装兼容字体。

```sh
python3 docs_codex/diagrams/2026-10-12_rtl_modules/build_figures.py
python3 docs_codex/diagrams/2026-10-12_rtl_modules/build_sources.py
/home/zhaowenyao/.codex/skills/publication-figures/.venv/bin/python \
  docs_codex/diagrams/2026-10-12_rtl_modules/verify_figures.py --source-only
python3 docs_codex/diagrams/2026-10-12_rtl_modules/export_figures.py
/home/zhaowenyao/.codex/skills/publication-figures/.venv/bin/python \
  docs_codex/diagrams/2026-10-12_rtl_modules/verify_figures.py
```

导出器拒绝覆盖非空目录。复现时用 `export_figures.py --out-dir /tmp/rtl-module-export-review` 或另一新目录；不要为重跑删除已有交付。`build_sources.py` 只替换章节 `RTL_SOURCES` 标记后的代码表，手写正文保留；源码改变后必须重新评审文字含义，更新行号/哈希本身不等于技术复核。

## 检查与证据边界

检查覆盖源文件哈希/111 个代码锚点、Markdown 文件链接、字体度量下的文字越界/互相覆盖/连线穿字、SVG 与 PPT 文本一致性、20 页对象数量及无整图栅格媒体。后端另检查逐图 PDF/字体/尺寸。已逐张查看最终预览；几何检查不能代替电路语义评审。

图是依据 RTL 手工归纳的模块机制图，不是综合网表，也未画出所有端口。组内多个实例的合并含义见对应章节。已核对的表达差异包括 UART 的 4-byte 地址步长与 reg8 HAL、GPIO 真实 `cio_gpio_q/en_q` 名称、Router mask 复位值、iDMA 的 NEXT_ID 读触发、LLC 当前 Regbus 控制口及未接出的性能事件端口。

没有运行 RTL 仿真、综合、板测、工艺签核或 Microsoft Office 外观/编辑验收；PPT 是独立原生形状与文本，但移动模块后箭头端点不会自动跟随。没有新增/修改 skill，也没有启用子 Agent。
