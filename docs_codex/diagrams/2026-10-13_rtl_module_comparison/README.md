# RTL 模块图 A 与历史 B 图源归档

**当前决定：B 的离散配对端口表达已被用户否定，不再展示为候选，也不再生成。用户比较 C 后再次确认采用 A；C 连续走线版仅保留试绘记录。以下 B 描述仅记录当时产物。**

2026-10-13；L01；输入 `c4162204cfee0c48b81158b4296860a678d92bec` / `mp/ara-pulp-v2`。范围仅为文档、图源、图片和生成脚本。

[打开当前 A/C 连续走线对比页](../2026-10-13_rtl_modules_native_c/index.html) · [阅读模块文档](../../rtl_modules/README.md) · [A PPTX](A/editable/diagrams.pptx)

## 历史生成记录（B 已弃用）

A 延续前一版 `publication-figures` 的连续走线和模块布局，加入技术纠错、遗漏路径以及逐线 E 编号。B 使用 [industrial-svg-pptx](../../../../../.codex/skills/industrial-svg-pptx/SKILL.md) 的方角、薄边框、柔和分区和端口表达；采用电路图的配对连接标识，同一 E 编号在源与目标端口各出现一次。B 没有新增隐藏互联，也没有把原来的一个 IP 复制成多个实例。

两版的节点、连接方向、信号说明和图注来自同一份 [connections.json](connections.json)。E 编号只在本图有效；B 的模块标识用于定位端点。总线双箭头合并请求/响应；单箭头可表示主数据方向，反向握手以共用连接表为准。图不是综合网表；功能合并、寄存器字段展开及逻辑分配关系均在对应章和连接表说明。

每版 24 张 SVG、PNG、PDF，以及 24 页原生 PPTX。2026-10-13 用户已选择 A 连续走线；文档及后续补图、修订沿用 A，B 后被用户明确弃用，文件仅留档。旧日期图稿未覆盖；修改前文档与输入脚本保存在 [备份归档](evidence/before_docs_and_sources.tar.gz)。

## 输入和复现

- 原有 20 图布局来自相邻的 `2026-10-12_rtl_modules/build_figures.py` 及 `2026-10-12_regbus_ip_integration/build_figures.py`；它们保留在原位置。
- [review_00_07.json](review_00_07.json) 与 [review_08_16.json](review_08_16.json) 保存 17 章完整复核、旧边映射及修正依据；不是由旧图自动推定 RTL 正确。
- [integration_graphs.json](integration_graphs.json) 定义新增四图的模块、连接、已有/规划状态和源码依据。
- [build_comparison.py](build_comparison.py) 捕获旧布局、实施明确的技术修正，保留历史关系清单；当前只生成 A，B 生成器已禁用，比较入口转至 A/C。
- [source_manifest.json](source_manifest.json) 保存当前正文引用的实现/本地官方文档哈希。旧清单保持原样；刷新哈希不能替代源码审查。

从仓库根执行，使用环境中已有的 skill 虚拟环境，不安装或升级工程依赖：

```sh
/home/zhaowenyao/.codex/skills/publication-figures/.venv/bin/python docs_codex/diagrams/2026-10-13_rtl_module_comparison/build_comparison.py
/home/zhaowenyao/.codex/skills/publication-figures/.venv/bin/python docs_codex/diagrams/2026-10-13_rtl_module_comparison/render_assets.py
python3 docs_codex/diagrams/2026-10-13_rtl_module_comparison/export_editable.py
/home/zhaowenyao/.codex/skills/publication-figures/.venv/bin/python docs_codex/diagrams/2026-10-13_rtl_modules_native_c/verify_native_c.py
```

PPT 导出使用同级 `svg-pptx-diagrams-native` 后端：整条箭头为一个原生对象，双向端点也是同一对象的属性；没有把整图放成图片。`editable/` 非空时后端拒绝覆盖。后续修改应换一个日期/版本输出目录，并保留用户可能编辑过的 PPT；PNG/PDF 是 SVG 的派生产物。

旧 `verify_comparison.py` / `validation.json` 保留为 A/B 交付时快照；弃用 B、迁移导航后的活动检查以 C 目录的验证脚本和结果为准。

## 检查与限制

[validation.json](validation.json) 检查章节和比较页链接、源码行号范围、原输入哈希、图中边端点与双版本覆盖、文字/画布/走线几何、PPT 文本与无整图图片。[全章审阅覆盖](review_coverage.json)记录21章的复核与修订；各组 `visual_review_*.json` 保存实际逐图查看、修正后复看和 PNG 哈希。USB、AXI 扩展另有灰度预览。几何检测只能辅助人工看图，不能证明 RTL 功能正确。

使用本机 `WenQuanYi Zen Hei` 渲染中文；PDF 保留矢量文本，PPT 不嵌入字体。Microsoft Office 显示/交互编辑未实测；端口与箭头虽为可编辑对象，未自动绑定，移动模块后不会保证自动重连。

本批指南是独立 Markdown，不属于 `learning/content/*.html` 的双格式正文源；本轮没有重生成或覆盖学习站。没有运行 RTL 编译、功能仿真、板测或 ASIC 检查，也没有实施新 IP 接入。
