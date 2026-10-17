# DDR–GB 同步说明：交接、排空与错误完成修订

2026-10-16，L01；输入 `mp/ara-pulp-v2` / `322bd6ce9`。正文入口：[DDR–GB 数据同步设计](../../engineering/DDR_GB_Coherence_Design.md)。沿用 `industrial-svg-pptx` 与已安装的原生导出后端。

| 图 | SVG 源 | Chrome 预览 | 本次变化 |
|---|---|---|---|
| 系统连接 | [system.svg](figures/system.svg) | [PNG](previews/system.png) | 与上版逐字节一致，保留工业底图及 S0/S1/S2 |
| 数据版本 | [versions.svg](figures/versions.svg) | [PNG](previews/versions.png) | 与上版逐字节一致 |
| 裸机时序 | [timeline.svg](figures/timeline.svg) | [PNG](previews/timeline.png) | 加入上下文、冲突准入、排空确认、错误判断及最终失效 |

[三页原生可编辑 PPTX](export/diagrams.pptx) · [正文阅读预览](design-preview.html) · [生成源](build.py) · [下一轮评审 Prompt](../../maintenance/L01/reviews/ddr_gb_coherence_review_prompt.md)

复现命令（输出目录须为空；重跑时使用新目录保护证据）：

```sh
python3 docs_codex/diagrams/2026-10-16_ddr_gb_coherence_review/build.py --out-dir <新图目录>
python3 docs_codex/diagrams/2026-10-16_cache_coherence/render.py --source-dir <新图目录> --out-dir <新预览目录>
python3 <svg-pptx-diagrams-native>/scripts/run.py --input <新图目录>/system.svg <新图目录>/versions.svg <新图目录>/timeline.svg --out-dir <新导出目录> --aspect 16:9
```

生成源复用现有 Figure 后端，系统图只取已认可的 2026-10-12 工业底图。原图稿和历史检查保留在[上版目录](../2026-10-16_ddr_gb_coherence_design/README.md)。修订前正文与交接已备份到 `evidence/before/`；[输入清单](evidence/input.json)记录允许修改范围及保护文件哈希。

检查入口：[validate.py](validate.py)、[Chrome 图稿记录](previews/browser.json)、[正文浏览器记录](evidence/document-browser.json)、[最终检查](evidence/validation.json)。逐张查看 PNG，并重读 PPTX 核对文字、原生形状、箭头、虚线及零整图位图。Office 显示／编辑尚未实测；本次未执行 RTL 构建、仿真、板测或故障注入。
