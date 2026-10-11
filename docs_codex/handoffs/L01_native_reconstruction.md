# L01 / 原版图稿集中重建为原生 PPT 对象

> 记录日期：2026-10-11。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-11；输入 HEAD `2784340240915fe4338ec54bfd613723b127d62e`。
- 用户授权：使用新建的 `svg-pptx-diagrams-native` 重建旧 skill 生成的全部图片；产物集中到 `native_reconstruction` 单个新目录，不建下级目录、不覆盖原文件。
- 状态：45 张图的 SVG、PNG、单页 PPTX 和 45 页合辑完成；结构验收通过，Office 实际显示/编辑未验证。
- 本轮负责路径：`docs_codex/diagrams/native_reconstruction/` 与本交接。未启动子 Agent。
- 起始已有 M01 接口文档修改及多个图目录/交接未跟踪；全部保留。`backup_new` 中的 publication 版未移动或改写。

## 本轮结果

- [图稿入口](../diagrams/native_reconstruction/index.html)、[说明与完整列表](../diagrams/native_reconstruction/README.md)、[45 页合辑](../diagrams/native_reconstruction/all_diagrams.pptx)。
- 范围：diagrams 下 8 张不同的正式图稿，加教材当前 37 张结构图。重复导出/历史修订按正式最终版重建一份；100 个相关原 SVG 的覆盖关系见 `source_inventory.json`。旧 DDR `before_datasheet` 草案保留原件和来源记录，不作为当前方案重发。
- 排除 WaveDrom、已撤回的 6 张手工波形、publication 版以及 native skill 自测示例。这些不属于本次旧 skill 的当前结构图集合。
- 固定原图布局、配色、文字和 viewBox，按已核对的线身/端点关系重建 306 个完整箭头，其中 18 个双向，共 324 个端点；4 处曲线附加短线合并到原曲线，136 条虚线碎片合并为 4 个完整矩形边框。
- 3618 个旧对象变为 3154 个对象，1653 个文本对象全部保留。24 个早期图中与线身不同色的箭头端点归一为线身颜色；箭头形状采用 native skill 的中号端点，记录视觉差异，不声称逐像素一致。
- 新目录内 SVG/PNG/PPTX、预览索引、接触图、映射、复现脚本和报告全部平铺，没有子目录。没有修改或新建任何全局 skill。

## 验证证据

工作目录为仓库根目录。主要命令：

```sh
~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/native_reconstruction/rebuild.py \
  --out-dir /tmp/cheshire-native-reconstruction-export

~/.codex/skills/publication-figures/.venv/bin/python -B \
  docs_codex/diagrams/native_reconstruction/render_previews.py \
  --directory docs_codex/diagrams/native_reconstruction

~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/native_reconstruction/verify_outputs.py \
  --report docs_codex/diagrams/native_reconstruction/validation.json
```

- 全部退出 0。正式目录先保存固定映射/复现脚本；导出在临时目录执行，逐文件确认目标不存在后复制到正式目录。
- 导出后重新读取各 PPTX，校验文字、对象数、原生箭头与虚线属性及 ZIP 完整性，无整图图片嵌入。所有未参与迁移的 SVG 对象和文本对象逐项比较相等。
- PNG 使用 CairoSVG 2.9.1，复用已安装的渲染环境，不采用 publication skill 的设计规则。查看 5 张总览中的全部 45 张图，并放大检查示例、DDR 双向路径、软硬件分层虚线框、教材 Crossbar 曲线。
- 程序化修改四个代表 PPT 的箭头线宽/边框宽度，在临时目录保存重读，原生属性和对象数保持。此结果不是 Office UI 验证。
- 验收报告：45 个输入 SHA-256 保持不变，旧 skill 的 12 个源文件与上轮留存哈希一致；45 SVG、45 图稿 PNG、5 总览 PNG、45 单图 PPTX、1 合辑 PPTX；索引链接有效，目录平铺。
- 当前 PNG 是 SVG 渲染，不是 PPT 截图；字体不嵌入。Office 显示、实际编辑和端口跟随未验证；当前连接器未绑定模块端口。
- 未改 RTL/sw、工程配置、原图、教材页面引用或旧 skill；未编译/未仿真/未板测；未 Git 提交。

## 决策与下一步

- 本次是原版图稿的对象语义迁移，保留原图技术快照与候选/待验证说明，不改变项目实现结论。
- 最小下一步：用户查看 `index.html`，在允许的 Office 环境打开合辑或单图文件确认显示和编辑体验；如需调整箭头大小/图中文字，另行按具体图稿修改新目录内母版。
- 共享项目状态/任务表没有工程事实变化；本次图稿子任务由本独立交接留档。
