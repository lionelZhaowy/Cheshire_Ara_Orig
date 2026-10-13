# RTL 模块正式 A 图与生成入口

当前采用 A 连续走线：21 篇正文、24 张图、213 条连接。技术核对输入为 `c4162204cfee0c48b81158b4296860a678d92bec`；2026-10-13 整理输入为 `5a1338e0a0bf115ddd54c19e0ae367ac2d541892`。本轮仅调整文档导航和维护流程，未重新绘图或复核 RTL 功能。

[正式 A 图总览](index.html) · [模块指南](../../rtl_modules/README.md) · [可编辑 PPTX](A/editable/diagrams.pptx)

## 正式资料与依赖

- `A/` 保存 24 份 SVG 母版、正文 PNG、矢量 PDF、布局清单及原生可编辑 PPTX/导出 SVG。保留所有正式交付格式。
- [connections.json](connections.json) 是节点、213 条连接和信号说明的统一清单；[source_manifest.json](source_manifest.json) 保存 78 个源码/本地官方资料的原始哈希，不随检查刷新。
- [build_comparison.py](build_comparison.py) 仅生成 A；沿用文件名以保持脚本入口稳定。它依赖相邻 `2026-10-12_rtl_modules/build_figures.py`、`2026-10-12_regbus_ip_integration/build_figures.py` 及前者的绘图工具，早期目录不可整批删除。
- [review_00_07.json](review_00_07.json)、[review_08_16.json](review_08_16.json) 和 [integration_graphs.json](integration_graphs.json) 保存修正依据与新增模块清单。

## 当前检查和定向导航生成

从仓库根执行；使用已有环境，无需安装或升级工程依赖：

```sh
/home/zhaowenyao/.codex/skills/publication-figures/.venv/bin/python docs_codex/diagrams/2026-10-13_rtl_module_comparison/verify_a.py --output /tmp/rtl-a-check.json
python3 -B docs_codex/diagrams/2026-10-13_rtl_module_comparison/build_comparison.py --navigation-only
```

检查只读取 A、正文、源码清单及历史记录中属于 A 的哈希，不要求 B/C 存在；报告写入指定新路径，拒绝覆盖。旧命令 `verify_comparison.py` 转调此检查，不再改写原 `validation.json` 或源码哈希。

需要改图时，先复制本目录至新的日期图稿目录并保留早期布局依赖，再在副本上运行 `build_comparison.py`（不加选项）和 [render_assets.py](render_assets.py)。原生导出用 [export_editable.py](export_editable.py) 的 `--out-dir` 指定新的空目录。修改后须实际看图、更新独立检查与视觉记录；不要覆盖用户可能编辑过的 PPT。纯导航整理不重生成 SVG/PNG/PDF/PPTX。

## 历史材料与验证边界

2026-10-13：B 被用户弃用；比较 C 后用户再次确认 A。B/C 图源及全部格式集中存入[维护归档](../../maintenance/L01/archive/documentation_organization/README.md)，不再作为候选、模板或默认生成目标。原始 [validation.json](validation.json)、[review_coverage.json](review_coverage.json)、`visual_review_*.json`、`pdf_checks.json`、`render_manifest.json` 和 `evidence/` 原样保留，属于当时 A/B 交付快照；其中 B 文件路径通过归档清单恢复。原检查脚本也在归档中，仅适用于当时输入。

本次整理检查见[组织交接](../../handoffs/L01_documentation_organization.md)。历史人工看图记录不等于本次重新看图；Office 显示/编辑、浏览器交互、RTL 仿真、板测和 ASIC 签核均未由本次检查验证。中文渲染依赖 WenQuanYi Zen Hei；PPT 不嵌入字体，连线未自动绑定模块端口。
