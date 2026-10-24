# DDR–GB 一致性专题：SoC v1

**当前版本入口：** [软件触发维护图稿与正文预览](../2026-10-20_ddr_gb_software_maintenance/README.md)。2026-10-20 后续修订采用全量写回＋软件提交输出范围失效；本目录原图、PPT、预览和检查保留为当时版本，以下“当前／新版”均按原交付时间理解。

2026-10-20，L01；输入 `mp/ara-pulp-v2` / `c9abbb48946fe3a7244bfb3159919b7c9731cb59`。依据[SoC v1 总纲](../../engineering/SoC_Architecture_v1_Master_Plan.md)，按用户批准的计划同步文档与配图；九页 SoC 主 PPT 保持原件。本目录替代 10 月 16 日一致性图集的当前阅读入口，旧图、评审和验证仍绑定原版本。

**后续阅读更新：** 主说明现采用[五阶段时间线及新版三页图集](../2026-10-20_ddr_gb_simple_timeline/README.md)。本目录的 16 步图及对应旧正文预览保留；16 步对应表移至[架构规划的硬件展开](../../engineering/Cache_Coherence_Architecture.md#detailed-timeline)。系统图、版本图和规划／综述六页 PPTX 继续使用原件。下列图稿检查与精简记录对应各自当时版本。

## 阅读入口与交付

- [主说明](../../engineering/DDR_GB_Coherence_Design.md) · [主说明正文预览](design-preview.html) · [三页可编辑 PPTX](export/design/diagrams.pptx)：系统、数据版本、16 步时序。
- [架构规划](../../engineering/Cache_Coherence_Architecture.md) · [规划正文预览](architecture-preview.html) · [六页可编辑 PPTX](export/planning/diagrams.pptx)：系统、生命周期、数据路径、三张通用分类。
- [供应商会议问题预览](supplier-preview.html) · [软件接口集成页面](../../software/interfaces/integration.html)。

| 图 | SVG 源文件 | Chrome PNG | 本轮修改 |
|---|---|---|---|
| 系统 | [system.svg](figures/system.svg) | [system.png](previews/system.png) | 新作一致性专题图：M2/M5、F0–F3、DDR.S0–S3，共享前端和逻辑维护职责 |
| 数据版本 | [versions.svg](figures/versions.svg) | [versions.png](previews/versions.png) | 保留原 SVG；DDR 框是逻辑版本，不展开压缩布局 |
| 时序 | [timeline.svg](figures/timeline.svg) | [timeline.png](previews/timeline.png) | 保留 16 箭头顺序，增加编号及 F0/F1、前端发布说明 |
| 生命周期 | [ownership.svg](figures/ownership.svg) | [ownership.png](previews/ownership.png) | 纳入数据／元数据可见性，写后先排空回填再失效 |
| 路径比较 | [data-paths.svg](figures/data-paths.svg) | [data-paths.png](previews/data-paths.png) | 经前端供数；N＋D 标为逻辑字节，右图仅作直供比较 |
| 交接方式 | [handover.svg](figures/handover.svg) | [handover.png](previews/handover.png) | 保留通用分类原图 |
| 协调范围 | [coverage.svg](figures/coverage.svg) | [coverage.png](previews/coverage.png) | 保留通用分类原图 |
| 设备代理 | [agent-types.svg](figures/agent-types.svg) | [agent-types.png](previews/agent-types.png) | 保留通用分类原图 |

两套 PPTX 的第 1 页来自同一份 `system.svg`。蓝色双向线合并表示 AXI 请求／返回，F2 仍仅发写并接收 B，F3 仅发读并接收 R。共享前端的压缩器、解压器和元数据服务没有拆成四份；下游四个端口共享一个 Controller。紫色实线合并命令／完成，虚线维护框表示待实现的逻辑职责。GB 本地数据交接与 DDR 缓存维护分别管理。

PPTX 为原生形状、文字和 DrawingML 箭头／虚线；不是整图位图。连线可整体编辑，但没有启用 PowerPoint 对象端点自动吸附。导出声明 Microsoft YaHei，本地度量／预览使用 WenQuanYi Zen Hei；Office 显示和编辑未实测。

## 生成与检查方式

沿用 `industrial-svg-pptx` 风格和已安装的 `svg-pptx-diagrams-native` 原生导出工具。[build.py](build.py)复用 10 月 16 日 Figure 布局工具，新的系统图独立生成；其余图按上表局部修改或逐字节复制。旧目录保留为生成依赖。

从仓库根执行，输出目录须选择尚不存在的新目录：

```sh
python3 docs_codex/diagrams/2026-10-20_ddr_gb_coherence_v1/build.py --out-dir /tmp/ddr-gb-v1-figures
python3 docs_codex/diagrams/2026-10-16_cache_coherence/render.py --source-dir /tmp/ddr-gb-v1-figures --out-dir /tmp/ddr-gb-v1-previews
```

原生导出使用 skill 的 `scripts/run.py --input <按页序的 SVG> --out-dir <新目录> --aspect 16:9 --font 'Microsoft YaHei' --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`；两套各页顺序见上方交付说明，导出清单位于各自 export 目录。时序图按比例居中，不拉伸。

[render_documents.py](render_documents.py)生成当前三份正文预览，并用 Chrome 检查软件集成页面。软件页面从现有 `content/integration.html` 经现有生成器的 `rendered()` 生成，仅写 integration HTML／Markdown，未批量更新其他教材。

最终 PPTX 由既有 `2026-10-16_soc_landscape_m5_gb/preview_deck_colours.py` 重读 DrawingML，使用 skill 已安装的 `.venv/bin/python`。得到的 [主说明预览](evidence/ppt-design/preview_layout.json)及[规划预览](evidence/ppt-planning/preview_layout.json)再用 Chrome 渲染于 `evidence/ppt-*-render/`。这是最终文件对象的本地字体／排版近似，不是 Office 渲染。

## 验证证据与边界

[输入清单](evidence/input.json)和 `evidence/before/` 保存 v1 图文同步开始时的哈希、工作区状态和待改文件原文；[检查结果](evidence/validation.json)汇总该版文件保护、本地链接、16 步、PPTX 原生对象及正文检查。`evidence/validate.py` 保留该版表头与正文哈希要求，不能直接用于下述精简版；旧报告继续对应精简前正文。两个最终 PPTX、八张 SVG 的整页和必要局部预览已实际查看，原件在精简修订中保持不变。

- `evidence/source-01`／`render-01` 保留第一版与发现的控制线穿字，`source-02`／[render-02](evidence/render-02/browser.json)为修正后的最终 SVG；首次沙箱 Chrome 启动失败记录在 `previews/chrome.log`，本机审批后完成渲染。
- 旧 SVG 渲染器的 `date` 字段固定为 2026-10-16；该字段未改动旧工具。本次执行日期与文件 SHA-256 以本目录检查结果为准。
- [正文浏览器检查](evidence/document-browser.json)覆盖主说明、架构规划、供应商问题和生成后的 integration 页面。最终 PPT 预览分别位于 `evidence/ppt-design-render/` 与 `evidence/ppt-planning-render/`。
- 保留全部历史原图、外部论文原图、九页主 PPT 及已有 E01／共享状态修改。未修改 RTL、驱动、地址配置，也未运行构建、仿真、板测、错误注入或性能测量。

四口实际交付、前端完成／错误契约、范围服务及非缓存配置仍待实现与验证。本轮检查只说明文档和图稿的一致性，不作为硬件验收。

## 2026-10-20 主说明精简修订

主说明从 9548 压缩至 4590 汉字，保留八章、三图、16 个箭头及原伪代码。LVDS 场景移至第 7 章，完成／错误／恢复移至第 8 章；架构规划和总纲仅调整对应章节引用。当前主说明与规划 HTML 预览已刷新，配图 SVG／PNG、两套 PPTX、旧评审及旧验证记录保持原件。

[修订输入](evidence/narrative-revision/input.json)及 `evidence/narrative-revision/before/` 保存修订前正文、相关引用和 HTML 预览；[检查结果](evidence/narrative-revision/validation.json)记录字数、图文对应、链接及文件保护。[Chrome 检查](evidence/narrative-revision/document-browser.json)与截图位于该目录，已实际查看正文、伪代码、完整 16 步表和 LVDS／恢复段落。

检查期间发现六个范围外文件并发更新，本轮未写入这些文件，当前内容保留；[首次检查](evidence/narrative-revision/validation-first-pass.json)及[变化记录](evidence/narrative-revision/concurrent-changes.json)单独保留，最终结果区分本轮修订与并发变化。

渲染沿用 `render_documents.py`，本次在临时调用中仅选择主说明／规划，将截图和日志改存 `evidence/narrative-revision/`，增加章节与时序表末端截图，未修改生成工具。检查复用原 `validate.py` 的链接解析方法；没有重做图稿导出或 Office 实测。实施摘要见[主题交接](../../handoffs/L01_cache_coherence_architecture.md#narrative-revision-20261020)。
