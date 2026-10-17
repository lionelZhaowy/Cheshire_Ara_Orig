# DDR–GB 一致性图稿：工业底图最小增补

2026-10-16，L01。配套正文：[缓存一致性：条件审查与架构比较](../../engineering/Cache_Coherence_Architecture.md)。本目录保留此前逐行协调比较的图稿快照；现行方案及更新图稿见[软硬件协同维护](../2026-10-16_coherence_hybrid/README.md)。`industrial-base/` 是本轮继续沿用的系统布局来源。

| 图 | SVG 母版 | PNG 预览 |
|---|---|---|
| DDR 三口互连与新增一致性协调 | [system.svg](industrial-base/system.svg) | [system.png](industrial-base/system.png) |
| DDR 地址数据搬入 GB | [read-to-gb.svg](industrial-base/read-to-gb.svg) | [read-to-gb.png](industrial-base/read-to-gb.png) |
| GB 数据写入 DDR | [write-to-ddr.svg](industrial-base/write-to-ddr.svg) | [write-to-ddr.png](industrial-base/write-to-ddr.png) |

[三页原生可编辑 PPTX](industrial-base/export/diagrams.pptx) · [导出报告](industrial-base/export/export_report.json) · [检查结果](evidence/minimal-validation.json)

## 图 1 的最小修改

唯一底图为用户指定的[2026-10-12 工业版 DDR 互连图](../2026-10-12_industrial_redraw/ddr_interconnect.pptx)。生成脚本直接读取该版 SVG，保留原画布、模块坐标、尺寸和全部数据连线。在原有空白区域增加一个“缓存一致性协调”模块，以及连接 CVA6、原子适配、LLC、S1/S2 接入侧和 DDR 在途管理的紫色控制线。

DDR Controller 的三个入口原位保留：S0 接 SoC/LLC，S1 接 NPU/GB 搬运，S2 接帧 DMA。Ara、NPU、ISP 和搬运器仍通过原 GB 访问适配模块访问 SRAM，该框改标为“共享数据代理”。其余两处文字调整为 CVA6 的“L1D / 写缓冲”和 LLC 的“WB 缓存 / 片上 SPM”，便于说明协调对象。

紫线表达候选探测、请求准入和完成接口，相关职责需在缓存侧与 DDR 接入适配中实现。缓存直接供数仍是正文和图 2 中的评审选项；图 1 保留底图的数据路径。三口分组沿用原方案示意，具体 IP 及端口实现待评审。

图 1 保持底图 2800×1575；图 2/3 保持 1920×1080，均为 16:9。采用 `industrial-svg-pptx` 和原生 PPTX 后端。SVG/PNG 使用本机文泉驿正黑，PPTX 指定 Microsoft YaHei。原图文字位置及字号保留，新增控制连线以跳线表示独立交叉。

## 生成与检查

[build_figures.py](build_figures.py) 的 `system()` 只读取上述工业版底图；图 2/3 沿用上次已验收的 SVG 内容。[render.py](render.py) 使用已安装 Chrome 渲染。

```sh
python3 docs_codex/diagrams/2026-10-16_cache_coherence/build_figures.py --out-dir /tmp/coherence-source-new
python3 docs_codex/diagrams/2026-10-16_cache_coherence/render.py --source-dir /tmp/coherence-source-new --out-dir /tmp/coherence-render-new
```

PPTX 使用已安装 skill 的 `svg-pptx-diagrams-native/scripts/run.py`，依次传入三图，参数为 `--aspect source --font 'Microsoft YaHei' --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`，输出到新目录。

检查内容包括：底图全部原对象的几何与样式、原数据连线、S0/S1/S2 各自的连接、文字避让、连续线端点，以及 PPTX 的文字、形状和原生箭头。已查看最终图 1 PNG；图 2/3 与上一版内容一致。Office 显示和编辑尚未实测，移动独立模块后需相应调整线条。

```sh
python3 docs_codex/diagrams/2026-10-16_cache_coherence/validate.py --out-file /tmp/coherence-validation-new.json
```

当前证据：[输入与唯一底图哈希](evidence/minimal-input.json)、[生成结构](evidence/minimal-source-01/layout.json)、[Chrome 检查](evidence/minimal-render-01/browser.json)、[最终验收](evidence/minimal-validation.json)。`evidence/before-minimal/` 保存此次修正前的文档与脚本。

本目录根级 SVG/PNG、`export/` 和较早 evidence 属于先前的重布局稿及历史检查。该图 1 已被用户否定，当前入口统一指向 `industrial-base/`。详细修正记录见[主题交接](../../handoffs/L01_cache_coherence_architecture.md)。
