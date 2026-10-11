# 2026-10-06_svg_pptx_skill_validation · 新版图稿

使用 publication-figures；旧目录原样保留。所有图宽182 mm，英文短标签/中文图注。源图、PDF和PNG各自保持比例；PPT页宽182 mm，组内统一页面高度。

[可编辑 PPTX](export/diagrams.pptx) · [导出报告](export/export_report.json)

## example

![example](export/example.png)

[SVG](example.svg) · [PDF](export/example.pdf) · [PNG](export/example.png) · [灰度](export/example.gray.png)

通用处理/反馈示例用于验证文本、矩形、曲线、箭头和独立对象导出，不表示实际硬件或实验结果。输入/处理/输出关系沿用旧验证图；外围说明移到本图注。

内容映射：输入/处理/输出/反馈→本图；可编辑性说明→导出报告。

原图：[旧母版](../2026-10-06_svg_pptx_skill_validation/example.editable.svg)

## crossbar_ara

![crossbar_ara](export/crossbar_ara.png)

[SVG](crossbar_ara.svg) · [PDF](export/crossbar_ara.pdf) · [PNG](export/crossbar_ara.png) · [灰度](export/crossbar_ara.gray.png)

仿真 Ara 配置的 7×5 全连接 AXI Crossbar。每个输入按 AR/AW 地址译码；每个输出独立仲裁。矩阵实心点表示可达连接，蓝色折线是 Ara→主存端口的请求示例；不同输出可并行，同一输出在该处竞争。S 为 Crossbar 从端口，接发起者；M 为主端口，接目标。箭头是逻辑请求方向，R/B 返回通道省略。

内容映射：7个输入、5个输出、每输入DEMUX/每输出MUX、全连接→本图；配置、地址窗口、RT与FPGA差异→图注补充。

原图：[旧母版](../2026-10-06_axi_crossbar_ara/ppt_editable_final/crossbar_ara_ppt.svg)

## ddr_qos_proposal

![ddr_qos_proposal](export/ddr_qos_proposal.png)

[SVG](ddr_qos_proposal.svg) · [PDF](export/ddr_qos_proposal.pdf) · [PNG](export/ddr_qos_proposal.png) · [灰度](export/ddr_qos_proposal.gray.png)

2026-10-06 三端口接入建议的重绘：SoC 经现有原子适配和 LLC 接 S0，ISP 与 NPU 数据分别旁路至 S1/S2。虚线轮廓表示候选控制器边界，内部逻辑为接入抽象；多端口共享同一 DDR 带宽。该历史方案与 2026-10-10 的 GB/统一搬运器方案并列保留，不把两个版本拼成已经实现的架构。

内容映射：三个请求源、LLC旁路、端口仲裁与命令调度→本图；供应商约束和一致性边界→图注。

原图：[旧母版](../2026-10-06_axi_crossbar_ara/ppt_editable_final/ddr_qos_proposal_ppt.svg)

## 随图补充

本组复用新版Crossbar与DDR候选图验证批量导出，技术图注补充见 [Crossbar组](../2026-10-06_axi_crossbar_ara_new/README.md)。不覆盖旧验证日志。

## 来源与验证边界

技术事实沿用原目录正式母版、README及对应交接，不升级依赖、不改RTL。实际重绘/导出测试见本组JSON及[总交付](../2026-10-10_publication_figure_research_new/README.md)。没有重新编译/仿真/板测；Office实际外观与编辑未验证。

复现：使用总交付内 build_figures.py --out-root <新临时目录> 生成全部SVG，再用新skill的 scripts/run.py --width-mm 182 --render 导出；命令所用Python需安装对应依赖。
