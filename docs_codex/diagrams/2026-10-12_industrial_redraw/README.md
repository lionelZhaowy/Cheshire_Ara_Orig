# 非教程图稿 · 工业风格重绘

2026-10-12 使用 `industrial-svg-pptx`，对 `2026-10-11_native_reconstruction` 中非 `learn` 前缀的 **9 张独立图稿**生成工业风格版。输入目录和教程图均未改写。

直接打开 [新图预览 / 新旧对照](index.html)，或下载 [9 页原生可编辑 PPTX 合辑](all_industrial.pptx)。网页支持切换“仅看新版 / 新旧对照”和按图筛选；图片可打开 SVG 母版。

## 图稿列表

| 页 | 内容 | SVG | PNG | PPTX |
| --- | --- | --- | --- | --- |
| 1 | AXI Crossbar 实际结构 | [SVG](crossbar_ara.svg) | [PNG](crossbar_ara.png) | [PPTX](crossbar_ara.pptx) |
| 2 | DDR 多端口仲裁与 QoS · 历史方案 | [SVG](ddr_qos_proposal.svg) | [PNG](ddr_qos_proposal.png) | [PPTX](ddr_qos_proposal.pptx) |
| 3 | 数据处理与反馈 | [SVG](example.svg) | [PNG](example.png) | [PPTX](example.pptx) |
| 4 | 启动初始化的软硬件对应 | [SVG](initialization_hw_sw.svg) | [PNG](initialization_hw_sw.png) | [PPTX](initialization_hw_sw.pptx) |
| 5 | 从复位到应用返回 | [SVG](program_execution_flow.svg) | [PNG](program_execution_flow.png) | [PPTX](program_execution_flow.pptx) |
| 6 | Cheshire SoC 软硬件分层 | [SVG](cheshire_software_hardware.svg) | [PNG](cheshire_software_hardware.png) | [PPTX](cheshire_software_hardware.pptx) |
| 7 | DDR / GB / 图像互联候选 | [SVG](ddr_interconnect.svg) | [PNG](ddr_interconnect.png) | [PPTX](ddr_interconnect.pptx) |
| 8 | LLC Cache / SPM | [SVG](llc_cache_spm.svg) | [PNG](llc_cache_spm.png) | [PPTX](llc_cache_spm.pptx) |
| 9 | 完整 SoC 架构 | [SVG](soc_full_architecture.svg) | [PNG](soc_full_architecture.png) | [PPTX](soc_full_architecture.pptx) |

缩略预览：[1–3](contact-01.png)、[4–6](contact-02.png)、[7–9](contact-03.png)。这些是本轮生成的预览拼图，不是新增工程图。

## 内容处理

- 排除 37 张 `learning_*` 图，排除旧 `contact-01` 至 `contact-05` 辅助拼图；PPT 合辑、脚本、报告和锁文件不作为独立图片重绘。`example` 是独立非教程示例，纳入本轮。
- 8 张图按各自内容重新布局、绘制边框/分区/连线；完整 SoC 图沿用刚获用户认可的工业版，通过冻结的 `soc_layout.py` 重新导出。没有仅给旧 PNG 换色或把整图图片嵌入 PPT。
- 所有新图均为 16:9 横向画布；方角深色细边框、低饱和功能色区、独立文本、语义完整箭头。Crossbar 内部用全连接矩阵表达 35 条可达关系；启动图采用职责/阶段分区；LLC 保留组/way 阵列和配置转换过程。
- 图内压缩长段说明；重要条件、原输入版本及原长说明的技术内容收录在 [图意与版本说明](figure_notes.md)。[来源清单](source_inventory.json)保存 9 个源 SVG 哈希、原始文本和排除列表，支持逐图追溯。
- 旧 QoS 图的 S1=ISP、S2=NPU 保留为历史独立主口方案；DDR/GB 与完整 SoC 图则为 S1=NPU/GB、S2=帧写入。重绘不强行统一两个阶段的候选定义，不冻结新地址/参数。

## 验证

[结构检查](validation.json)、[导出报告](export_report.json)、[交付检查](delivery_checks.json)。9 个单图及 9 页合辑均保存重读，核对文本、对象数、原生箭头/虚线及 ZIP 完整性，无 `ppt/media/` 图片。检查 Crossbar 7×5 矩阵、DDR 端口、LLC 阵列/分区等关键对象覆盖，字体度量未发现文字重叠/越界。

实际查看全部 9 张 PNG，并修正连线穿标签、文字间距、跨线表示和 LLC 省略号缺字。PNG 使用 CairoSVG 2.9.1 渲染；中文测量/本地回退字体为 WenQuanYi Zen Hei，目标字体为 Microsoft YaHei，未嵌入字体。

**Office 显示/编辑未实测。** 箭头是完整原生对象，但未绑定模块端口，移动模块后需调整连线。图稿继承原技术快照和候选/未验证边界，本轮未改 RTL、软件、Cfg、地址图或依赖，未编译/仿真/板测。原图与既有 PPT 合辑保留。

## 复现

输入分支 `mp/ara-pulp-v2`，HEAD `c4162204cfee0c48b81158b4296860a678d92bec`。从仓库根目录执行，输出目录必须不存在或为空：

```sh
~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/2026-10-12_industrial_redraw/build_industrial.py \
  --out-dir /tmp/industrial-redraw-rebuild

~/.codex/skills/publication-figures/.venv/bin/python -B \
  docs_codex/diagrams/2026-10-12_industrial_redraw/render_previews.py \
  --directory /tmp/industrial-redraw-rebuild

~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/2026-10-12_industrial_redraw/verify_outputs.py \
  --directory /tmp/industrial-redraw-rebuild \
  --report /tmp/industrial-redraw-rebuild/validation.json

python3 docs_codex/diagrams/2026-10-12_industrial_redraw/write_gallery.py \
  --directory /tmp/industrial-redraw-rebuild
```

`build_industrial.py` 可通过 `--repo` / `--skill` 指定路径。`soc_layout.py` 是本目录冻结的已认可布局副本，不依赖修改上轮图稿。渲染脚本只需 CairoSVG/Pillow，示例复用本机现有环境，不应用 publication skill 的绘图规则。图库中的旧图相对链接按正式日期目录组织，临时重建目录应在复制到同级正式目录后查看新旧对照。

本轮交接见 [L01 图稿主题交接](../../handoffs/L01_native_reconstruction.md)。
