# L01 / 新版 DDR、LVDS、ISP 与 GB 互联图

## 基本信息

- 日期：2026-10-10；用户明确要求使用 svg-pptx-diagrams 绘制新版 DDR 互联示意图。
- 输入 HEAD：278434024。保留已有 M01 契约修改、其他图与交接；未修改 RTL、配置或共享状态。
- 状态：候选架构图交付完成，未实施拓扑；未提交。

## 本轮结果与依据

- 按 `2026-10-10_L01_lvds_isp_gb_soc_topology.md` 绘制：S0 为 LLC 下游；S1 为 NPU/GB 统一搬运出口候选；S2 为 RAW/ISP 二选一后的图像 DMA。
- 分开标示现有 LLC/SPM 与新增独立 GB，保留 ISP、NPU、Ara 及搬运器访问 GB 的候选路径。
- Ara 现有单 AXI 出口增加按地址分流，而非描述为当前已有双口。现有路径依据 `hw/cheshire_soc.sv` 的 LLC 出口、Ara filter、width converter、主 Xbar 接线；详见前述交接的源码与官方依据。
- 用户确认的是“先保留 ISP/NPU 并行能力”，不是已冻结资源预算。三口方案依赖共用 S1；独立 GB DMA 可另增 S3。图中分区、仲裁及数据流是设计建议，不是已实现能力。
- 控制/中断、详细 CDC、缓存维护未展开；连线交叉无结点者不表示连接。GB 不自动一致；RAW/ISP 暂按不同时录制。

## 产物

- `docs_codex/diagrams/2026-10-10_ddr_lvds_isp_gb/ddr_interconnect.svg`：结构化母版。
- 同目录 `ddr_interconnect.png`：1920×1080 SVG 渲染预览。
- 同目录 `final/ddr_interconnect.editable.svg`、`final/diagrams.pptx`、`final/export_report.json`：最终可编辑交付与报告。
- 排版修正前的本轮中间导出已移至 `/tmp/cheshire-ddr-20261010-editable-draft`，未删除用户文件；交付只使用 final。

## 验证证据

- 技能脚本：`python3 /home/zhaowenyao/.codex/skills/svg-pptx-diagrams/scripts/run.py --input docs_codex/diagrams/2026-10-10_ddr_lvds_isp_gb/ddr_interconnect.svg --out-dir docs_codex/diagrams/2026-10-10_ddr_lvds_isp_gb/final --aspect 16:9`，退出 0。
- 最终母版 SHA-256：`512aa9578d5811b669e6f75cbd9a0fd381ea1a7409a78d1c4e87db1f79f6939b`。报告为 164 个对象、74 个文字对象，文字未转轮廓，PPTX 已生成。
- Chrome 本地渲染并人工查看 PNG，修正了 GB 说明文字与连线相交及 RAW 标注位置；最终预览检查通过。Linux 缺少 Microsoft YaHei，渲染存在字体回退；Windows 字体排版仍需 Office 复核。
- Office 验证先因沙箱 socket 限制失败；提升权限后，首次误用 Ubuntu-22.04 UNC，随后用 wslpath 核实为 Ubuntu-24.04 并重试。两次 Windows 调用均持续无输出，以 Ctrl-C 中止，退出 1；没有 Office 验证报告。不得宣称 Office 实测通过。
- 未编译、未仿真、未板测，未进行任何带宽/实时性保证验证。

## 最小下一步

1. 用户在 PowerPoint 检查最终 PPTX 的中文字体、文字编辑及版式。
2. M01/I01确认统一 S1 搬运出口是否可行，再冻结三口或四口。
3. 明确图像格式/吞吐和并发使用矩阵，核算 GB bank 服务与 DDR QoS。无需据此图自动修改 RTL 或共享决策文档。
