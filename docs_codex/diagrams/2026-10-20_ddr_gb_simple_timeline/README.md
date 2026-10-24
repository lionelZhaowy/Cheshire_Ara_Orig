# DDR–GB 五阶段时间线

**当前版本入口：** [软件触发维护图稿与正文预览](../2026-10-20_ddr_gb_software_maintenance/README.md)。2026-10-20 后续修订采用全量写回＋软件提交输出范围失效；本目录原图、PPT、预览和检查保留为当时版本，以下“当前／新版”均按原交付时间理解。

2026-10-20，L01；输入 `mp/ara-pulp-v2` / `c9abbb48946fe3a7244bfb3159919b7c9731cb59`。按用户要求简化主说明的时间线：准备输入→交接前同步→设备执行→交回 CPU 前同步→CPU 后处理。两次交接的维护语义不变。

- [主说明](../../engineering/DDR_GB_Coherence_Design.md) · [正文预览](design-preview.html)
- [五阶段 SVG](figures/timeline-simple.svg) · [PNG](previews/timeline-simple.png) · [单页原生 PPTX](export/timeline/diagrams.pptx)
- [新版三页 PPTX](export/design/diagrams.pptx)：系统、数据版本、五阶段时间线。原图集的前两页及主题／布局逐字节保留，仅替换第三页；正文为便于阅读先展示时间线，再展示系统与数据版本。
- [16 步硬件展开与对应表](../../engineering/Cache_Coherence_Architecture.md#detailed-timeline) · [架构规划预览](architecture-preview.html) · [原图及旧图集](../2026-10-20_ddr_gb_coherence_v1/README.md)

简图的四条箭头表示应用阶段的先后关系；框中的同步包含多项硬件动作。原 16 步不再作为主说明的逐项阅读要求，详细对应表原样移入架构规划第 3.1 节。维护成功后才启动依赖阶段，软件继续遵守范围使用约定；失败恢复仍见主说明第 8 章。

## 制作与检查

[build.py](build.py)生成 SVG 及布局清单，沿用 `industrial-svg-pptx` 风格。原生导出使用已安装 `svg-pptx-diagrams-native/scripts/run.py`，参数为 `--input figures/timeline-simple.svg --out-dir <新目录> --aspect 16:9 --font 'Microsoft YaHei' --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`。PPT 字体声明 Microsoft YaHei，本地度量与预览使用 WenQuanYi Zen Hei。

新版三页 PPT 从旧图集复制，只将 `ppt/slides/slide3.xml` 换为单页导出文件的原生对象；两者页面尺寸相同，新页无外部资源引用。[ZIP 差异](evidence/deck-diff.json)记录唯一变化。没有重新生成系统与数据版本页，也没有修改规划／综述六页图集。

SVG 用既有 `2026-10-16_cache_coherence/render.py` 经 Chrome 渲染；最终 PPTX 用既有 `2026-10-16_soc_landscape_m5_gb/preview_deck_colours.py` 重读，再渲染第三页。正文沿用 v1 的 `render_documents.py`，临时调用仅生成两份当前页面并适配表格数量，旧工具和旧预览保持原件。

[输入与文件哈希](evidence/input.json)及 `evidence/before/` 保存修订前文档。[检查结果](evidence/validation.json)汇总本地链接、五节点／四箭头、原 16 步表及伪代码保留、PPTX 原生对象和文件保护；[正文浏览器结果](evidence/document-browser.json)、[SVG 布局结果](previews/browser.json)和[最终 PPT 预览结果](evidence/ppt-render/browser.json)分别记录实际输入。旧渲染器报告中的固定日期字段不作为本次执行日期，本次日期与输入以本目录记录为准。

已实际查看最终 SVG、最终 PPT 第三页的整页与同步框局部、正文开头和伪代码。首版两处文字包围盒相交，保持字号、增大行距后通过检查；首版源文件、PPT、预览和检查保存在 `evidence/attempt-01/`。PPT 预览是 DrawingML 与本地字体近似，Office 显示／编辑未实测；未修改 RTL、驱动、配置或运行硬件测试。
