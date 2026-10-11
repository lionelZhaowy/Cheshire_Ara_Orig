# Cheshire SoC 软硬件分层结构图

2026-10-09；输入分支 `mp/ara-pulp-v2`，HEAD `278434024`。按用户确认后的分层方案绘制，主线为当前裸机工程。

## 交付

- [PNG 预览](export_final/cheshire_software_hardware.png)：2000 × 1500，4:3。
- [SVG 母版](cheshire_software_hardware.svg)：保留 text 和独立图形，含 Linux 字体回退。
- [可编辑 PowerPoint](export_final/diagrams.pptx)：单页，334 个原生对象，其中 108 个文本对象。
- [导出后的 SVG](export_final/cheshire_software_hardware.editable.svg)、[导出报告](export_final/export_report.json)、[文字宽度检查](layout_checks.json)。

`export_final/` 为正式交付；`export/` 保留字体回退和底部留白调整前的中间产物。SVG 母版是编辑来源；PPT 中的手工修改不会自动回写母版。

## 图的含义

主图从应用软件、基础软件、软硬件接口标注带，向下展开到 SoC 硬件和片外器件。接口标注带是软件可见契约，不是独立软件模块；应用和基础软件都由处理器执行，不表示每个算法都先进入驱动。

- 基础软件中的蓝箭头是代表性函数调用，保留 printf→UART DIF、器件 HAL→SPI/I²C DIF，以及 MMIO 工具。GPT 经介质读取回调调用 HAL；UART debug、GPIO 等未展开全部连线。
- DIF 的取名和 HAL 的职责按当前项目表达，并非所有软件栈的通用命名规范。应用可以直接调用 DIF，当前代码也有 HAL 直接访问 MMIO 的路径。
- `libcheshire.a` 表示归档方式，覆盖多个职责；并非单独的调用层。底部 LLC/AXI RT 专用库归入软件，但为控制密度未展开它们的寄存器读写连线。
- CPU/Ara 的专用交互与两者 AXI 访存路径分开表达；没有把 RVV 画成 MMIO 启动的外设。
- 硬件棕箭头表示连接/事务关系，双向端点代表请求和反馈，不是精确的 AXI 各通道图。主存路径展示原子适配、LLC/SPM 和外部出口；SPM 使用 LLC 阵列。具体 cache hit、SPM hit、miss 行为未展开。
- 片外 DDR 经控制器/PHY 接入。FPGA/ASIC 是实现方式，放侧栏；不暗示采购的 AXI4 DDR 子系统已经集成。
- 虚线模块是图像/NPU/ISP 等规划扩展；尚未连通的真实接口不虚构连线。未来 DDR 旁路仅标注待实现。
- RTOS/Linux 放在可选环境侧栏；Linux 不默认复用本地裸机 HAL，图不声称目标 OS 已运行。
- 图内实线框代表已有源码、结构或当前平台器件类别，不代表所有配置启用、设备存在或功能已验证。外设和存储型号仍以具体板级配置为准。

## 工程依据

| 图中关系 | 当前代码 |
| --- | --- |
| printf 与字符输出 | `sw/deps/printf/printf.c:149,862`；`sw/lib/dif/uart.c:38,67` |
| GPT 回调与器件 HAL | `sw/lib/gpt.c:14,22,73`；`sw/lib/hal/spi_s25fs512s.c:40,56` |
| SPI DIF 与寄存器操作 | `.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/device/lib/dif/dif_spi_host.c:398,455` |
| MMIO 工具 | `sw/include/util.h:16,20`；上述依赖的 `sw/device/lib/base/mmio.h:143` |
| 库归档、启动与链接 | `sw/sw.mk:44-64`；`sw/lib/crt0.S:24,42,46,114`；`sw/link/spm.ld` |
| SoC 结构与 CVA6/Ara 连接 | `hw/cheshire_soc.sv` 的 `i_axi_xbar`、`i_llc_atomics`、`i_llc`、`i_core_cva6`、`gen_ara.i_ara`、寄存器外设与 iDMA wrapper |
| 规划边界 | `docs_codex/PROJECT_STATE.md`；本次方案复核交接 |

## 生成与验证

使用用户指定的 `svg-pptx-diagrams` 技能。母版使用其支持的 SVG 子集，虚线用独立线段表达，箭头为独立三角形，全部转换为可编辑 PowerPoint 对象。源 SVG 使用 Microsoft YaHei，并为 Linux 预览提供 WenQuanYi Zen Hei / sans-serif 回退；PPTX 使用 Microsoft YaHei。

复现时选择新的输出目录；生成器和导出器均拒绝覆盖既有图稿：

```sh
# 使用装有 Pillow 的 Python；本次使用技能自带的隔离环境。
python3 build_figure.py --out-dir /tmp/cheshire-layers-new
python3 /home/zhaowenyao/.codex/skills/svg-pptx-diagrams/scripts/run.py \
  --input /tmp/cheshire-layers-new/cheshire_software_hardware.svg \
  --out-dir /tmp/cheshire-layers-new/export \
  --font-file /mnt/c/Windows/Fonts/msyh.ttc
```

Windows 字体文件路径用于本机测量，不是图稿的外部依赖；其他机器可指定相应字体文件。生成器在本机检查了文字宽度与画布边界。正式 SVG 经本地 Chrome 离线渲染，人工查看全部区域，未见文字/连线重叠和裁切。

导出器重新读取 PPTX，核对文字、对象数量和 ZIP 完整性；无整图位图/SVG 图片，文字未转路径。最小字号约 9.58 pt（14 × 10.5 英寸画布），适合缩放阅读，嵌入较小页面时应先检查可读性。

PowerPoint 验证脚本被本机 Windows 数字签名策略拒绝，**未在 Office 实测打开、编辑或渲染**。没有绕过或修改执行策略，SVG 预览不能替代 Office 显示验证。未编译软件或 RTL、未仿真、未板测。
