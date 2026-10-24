# DDR–GB：软件触发的缓存维护

2026-10-20，L01；输入 `mp/ara-pulp-v2` / `c9abbb48946fe3a7244bfb3159919b7c9731cb59`。本轮按用户确认的方案修订文档和配图：交接前复用 FENCE＋LLC 全量 flush，设备写后由软件提交输出范围，硬件完成两级缓存失效。新增维护控制集中在缓存侧；F1 不增加监听，搬运顺序由软件保持。

- [主说明](../../engineering/DDR_GB_Coherence_Design.md) · [当前正文预览](design-preview.html)
- [硬件实现规划](../../engineering/Cache_Coherence_Architecture.md#hardware-plan) · [规划预览](architecture-preview.html)
- [三页原生 PPTX](export/design/diagrams.pptx)：系统、数据版本、五阶段时间线
- [六页原生 PPTX](export/planning/diagrams.pptx)：系统、生命周期、数据路径、三张通用分类

| 修订图 | SVG | PNG | 变更 |
|---|---|---|---|
| 系统连接 | [源图](figures/system.svg) | [预览](previews/system.png) | 保留 v1 数据路径，新增 MMIO 表达，维护专用线只接 L1D／写缓冲和 LLC |
| 五阶段时间线 | [源图](figures/timeline-simple.svg) | [预览](previews/timeline-simple.png) | 保留五框四箭头，明确一次全量写回、软件触发输出范围失效 |
| 数据生命周期 | [源图](figures/ownership.svg) | [预览](previews/ownership.png) | 同步写前准备、写后失效和软件排序；原布局与阶段关系保留 |

数据版本示例、数据路径比较和通用分类图继续使用旧原件；比较图描述 clean 的数据路径，初版全量 flush 的额外驱逐及范围外写回成本见规划第 4 章。[旧五阶段交付](../2026-10-20_ddr_gb_simple_timeline/README.md)和[旧 v1 图集](../2026-10-20_ddr_gb_coherence_v1/README.md)保留。原 16 箭头图及原表在规划第 3.2 节作为历史职责展开，不再表示当前硬件连线。

## 制作与检查

[build.py](build.py)复用既有工业图工具，仅修改相关对象与标签；[render_documents.py](render_documents.py)沿用既有 Markdown／Chrome 预览方式，范围限定为两份正文。未重绘九页 SoC 主 PPT，未修改 RTL、驱动、配置、共享状态或任务表。

SVG 原生导出使用 `svg-pptx-diagrams-native/scripts/run.py`，输入本目录三张 SVG，参数为 `--aspect 16:9 --font 'Microsoft YaHei' --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`，中间结果在 `export/revised/`。最终图集沿旧 PPT 复制，只替换主说明第 1、3 页和规划第 1、2 页的 slide XML；主题、母版、布局、其余页面及 ZIP 成员逐字节保留，见[图集差异和原生对象统计](evidence/deck-diff.json)。

SVG 用既有 `2026-10-16_cache_coherence/render.py` 经 Chrome 渲染；最终 PPTX 用 `2026-10-16_soc_landscape_m5_gb/preview_deck_colours.py` 重读，再渲染修改页。已查看三张 SVG 及最终 PPT 修改页的整页与维护区域；PPT 预览为 DrawingML／本地字体近似，Office 显示与编辑未实测。首版 MMIO 框覆盖 ISP→GB 绿色线段的问题已通过缩短新增框修正，原数据路径不变，首版保存在 `evidence/layout-01/`。

[输入备份与保护清单](evidence/input.json)、[检查结果](evidence/validation.json)、[SVG 布局检查](previews/browser.json)、[正文检查](evidence/document-browser.json)、[主说明 PPT 预览检查](evidence/ppt-design-render/browser.json)和[规划 PPT 预览检查](evidence/ppt-planning-render/browser.json)分别记录实际输入。旧渲染器的固定日期字段不作为本轮日期；以本目录输入记录为准。未运行 RTL 构建、仿真、板测、故障注入或性能测量。
