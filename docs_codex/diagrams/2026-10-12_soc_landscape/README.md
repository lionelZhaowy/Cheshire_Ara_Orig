# SoC 横向架构图 · 2026-10-12

本轮按用户要求生成两个版本，使用 `svg-pptx-diagrams-native`。AXI、Regbus、DDR Controller 横向组织，CVA6–Ara、NPU/GB、LVDS/ISP 放在中上部。图稿按生成日期归档；旧图位于 [2026-10-11_native_reconstruction](../2026-10-11_native_reconstruction/README.md)，本轮未改写旧目录。

## 查看与编辑

- [本地预览入口](index.html)
- [两页原生 PPTX 合辑](soc_landscape_comparison.pptx)：版本 1 → 版本 2；统一 16:9，按比例居中，不拉伸。

| 版本 | 布局特点 | 预览 | 矢量母版 | 原生 PowerPoint |
| --- | --- | --- | --- | --- |
| 1 · 参考图风格 | 工业芯片框图；薄深色边框、柔和彩色分区、嵌套 IP；Regbus 左下、DDR 右下 | [PNG](soc_reference_style.png) | [SVG](soc_reference_style.svg) | [PPTX](soc_reference_style.pptx) |
| 2 · 原版重排 | 保留蓝/绿/橙/紫语义配色和圆角；AXI 与 DDR 并排，Regbus 横贯下部 | [PNG](soc_rearranged.png) | [SVG](soc_rearranged.svg) | [PPTX](soc_rearranged.pptx) |

版本 1 为 3600×2025（16:9）；版本 2 为 3400×1850，自由横向画布，合辑中上下有少量留白。PNG 来自本地 SVG 渲染，不是 Office 截图。

## 图中范围与约定

- 主 AXI：CVA6、Debug/SBA、Ara、iDMA 数据主口、Serial Link RX、VGA、USB，共 7 个内部发起端；另列外部 master 扩展。
- 主 AXI 目标：Debug、AXI→Regbus、LLC/SPM、iDMA 配置、Serial Link TX，共 5 类；另列外部 slave 扩展。S 编号是 Crossbar 接收 master 请求的接口，M 编号是 Crossbar 通向 slave 的接口；它们不是 IP 自身角色反转。
- Regbus：Boot ROM、CLINT、SoC 寄存器、PLIC、LLC 配置、UART、I2C、SPI host、GPIO、Slink 配置、VGA 配置、USB 配置、VGA/iDMA/CPU 三项 bus-error、IRQ router、AXI RT 配置、CLIC，共 18 项；另列 `reg_err_slv` 与 RegExt。
- 新 IP 配置：C1 PLL/时钟复位，C2 DDR Controller，C3 DDR PHY，C4 LVDS，C5 ISP，C6 NPU 计算，C7 NPU/GB 搬运，C8 帧写入 DMA，C9 GB 管理。上下相同 C 标号代表同一 IP 的配置端，不是第二份 IP；RegExt 是当前候选配置通路。
- DDR：S0 接 LLC 下游；S1 接统一 NPU/GB 搬运器；S2 接帧写入 DMA。三口都进入共同端口仲裁/QoS，再由控制器调度访问同一 DDR 空间。合流线表示控制器内部共享仲裁，不是把三个 AXI 端口直接短接。

端口编号采用单核 Ara 参考配置。实例数/端口存在性仍取决于 `Cfg`；IRQ router、AXI RT、CLIC 在所参考的 Ara 仿真配置中关闭。可选项及新增候选用虚线标示。图中 AXI 箭头是请求/数据路径总览，返回通道合并表达；局部宽度适配、CDC、复位树和中断线没有逐项展开。

iDMA 的配置目标与数据 master 分开：配置由主 AXI 到 wrapper，再在内部转换到寄存器接口，不挂主 Regbus。C7/C8 的寄存器配置与其 DDR 数据主口也分开，但当前使用 RegExt 的画法只是新 IP 接口规划，不表示 RTL 已实现。

Ara GB 分支位于失效过滤之后、位宽转换之前，仍为新增候选。GB 是独立 SRAM，不等于 LLC/SPM；GB 访问适配协调 Ara、NPU、ISP 和搬运器。RAW/ISP 在帧边界二选一写入，保留 ISP 与 NPU 并行能力。三 DDR 端口成立的条件仍是 NPU 与 GB 共用 S1 搬运出口；若保留独立 NPU master 和 GB DMA，需另评估 S3。图稿未冻结地址、GB 容量/bank、DDR 实际位宽、lane/VLEN、时钟域或中断分配。

## 依据

输入：分支 `mp/ara-pulp-v2`，HEAD `c4162204cfee0c48b81158b4296860a678d92bec`，保留输入时的未提交修改。

- [原完整图](../2026-10-11_native_reconstruction/soc_full_architecture.svg)、[Crossbar 参考](../2026-10-11_native_reconstruction/crossbar_ara.png)、[DDR 参考](../2026-10-11_native_reconstruction/ddr_interconnect.png)。用户提供的工业芯片框图仅用于视觉风格。
- [cheshire_pkg.sv](../../../hw/cheshire_pkg.sv)：`gen_axi_in`、`gen_axi_out`、`gen_reg_out`。
- [cheshire_soc.sv](../../../hw/cheshire_soc.sv)、[cheshire_idma_wrap.sv](../../../hw/cheshire_idma_wrap.sv)：实际互连、Ara 过滤/位宽转换、LLC、iDMA 内部配置路径。
- [IP/DDR 接口契约](../../engineering/IP_DDR_Interface_Contract.md) §12：候选 DDR/GB/图像结构与未冻结条件。

## 验证与复现

两版均已人工查看整图；另进行独立交叉审图，修正 GB/RAW 跨线、C 标号留白、文字越界及 DDR 共同仲裁入口。字体度量检查无文本互相重叠/越界，PPTX 保存重读文字逐项一致，无 `ppt/media/` 栅格图片。

| 版本 | 原生对象 | 文本 | 原生箭头对象 | 原生虚线对象 | 报告 |
| --- | ---: | ---: | ---: | ---: | --- |
| 1 | 386 | 198 | 71 | 28 | [导出](soc_reference_style.export.json) / [审图](soc_reference_style.validation.json) / [独立结构检查](soc_reference_style.check.json) |
| 2 | 370 | 185 | 72 | 24 | [导出](soc_rearranged.export.json) / [检查](soc_rearranged.validation.json) |

[合辑报告](soc_landscape_comparison.export.json)记录两页对象与比例；[交付检查](delivery_checks.json)记录旧文件保护和链接检查。Office 显示/编辑未实测，字体未嵌入；箭头为完整对象，但未绑定模块端口，移动模块后需要调整连线。本轮未修改 RTL/配置，未编译、仿真或板测。

在仓库根目录运行以下命令；输出目录须新建或为空。脚本拒绝覆盖已有产物。

```sh
~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/2026-10-12_soc_landscape/build_reference_style.py \
  --out-dir /tmp/soc-reference-rebuild

~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/2026-10-12_soc_landscape/build_rearranged.py \
  --out-dir /tmp/soc-rearranged-rebuild

~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/2026-10-12_soc_landscape/export_comparison.py \
  --out-dir /tmp/soc-comparison-rebuild
```

PNG 使用安装了 CairoSVG 的 Python，以 `cairosvg.svg2png(url=svg_path, write_to=png_path)` 生成；本轮复用本机 `publication-figures/.venv` 中的 CairoSVG 2.9.1，仅作渲染器，未采用该 skill 的设计规则。两份 `*.layout.json` 保存模块与文字坐标。

```sh
~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/2026-10-12_soc_landscape/verify_landscape.py \
  --stem soc_reference_style

~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/2026-10-12_soc_landscape/verify_landscape.py \
  --stem soc_rearranged
```

检查新导出目录时增加 `--directory`，该目录需含 SVG、PNG、PPTX、layout 和 export JSON；`--report` 可保存检查结果。
