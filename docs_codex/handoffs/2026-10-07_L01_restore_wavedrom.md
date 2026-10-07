# L01 / 波形图恢复 WaveDrom 绘制

## 基本信息

- 日期：2026-10-07；L01 教材修改者。
- 用户最新要求：波形继续使用 WaveDrom，不使用自行绘制的 SVG 波形。该要求修正前一轮43图重绘中的波形处理方式。
- 输入 HEAD：`f01487c2f3c3e990b515bff813227b97049976a3`；已有教材、评审及插图修改保留，未提交/推送，未启动子Agent。
- 范围：6张波形的引用与生成职责、图集/PPTX、维护检查及状态记录；37张结构图和生产源码不变。

## 本轮结果

- 6张波形恢复引用原 `assets/depth-{axi-backpressure,boot-phases,vector-arithmetic,vector-load,reset-release,handoff}.svg`。这些是本地 WaveDrom 3.5.0 的离线显示产物，绘制来源仍是 `assets/waves/*.json` 与 `scripts/build_waves.py`。
- 从 `build_research_figures.py` 删除自写波形绘制器及注册入口，只生成37张结构图；37张SVG与前一轮逐字节一致。
- 手工波形、原43页PPTX和相关生成输入转入 `figure_archive/20261007-withdrawn-manual-waves/`，用于历史追溯。没有删除原始WaveDrom JSON、脚本、vendor许可证或历史证据。
- 图集仍展示43张现用图，6张波形标明WaveDrom并链接JSON母版；当前可编辑PPTX仅包含37张结构图，已重新导出。
- 同步FIGURES.md、README、证据页、共享状态和任务表，说明今后的波形维护必须使用WaveDrom。七篇/30章与R1/R2修正保留。

## 验证证据

证据目录：`docs_codex/learning/evidence/wavedrom-restoration-20261007/`，使用新目录，不覆盖前一轮报告。

- 6份WaveDrom JSON与6张原生成图均与归档哈希一致。
- 37张结构图与前一轮相同；当前PPTX导出器重新核对文本、对象数及无整图图片。未重试前一轮受Windows签名策略阻止的Office实测。
- `browser/browser.txt`通过：34主页面桌面/手机、7页无脚本、199旧书签、43图画布边界与图集86资源。`structure/checks.txt`通过：54 HTML、2838本地链接/资源、108 SVG、657 Markdown链接，37张结构图及清单、包括6张WaveDrom波形在内的126个原生成产物均一致。`git diff --check`通过；保护核对见 `protection.json`。
- 生成一致性检查在临时副本运行既有 `build_waves.py`，确认6张WaveDrom产物与当前网页引用文件一致；不手写SVG替代生成。

```bash
python3 docs_codex/learning/scripts/build_research_figures.py --out-dir <新的37张结构图目录>
python3 docs_codex/learning/scripts/build_figure_gallery.py --out-dir <新的图集目录>
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/preview_structure_site.py --out-dir <新的浏览器目录>
python3 docs_codex/learning/scripts/check_structure.py --check-generated --out-dir <新的结构检查目录>
git diff --check
```

未执行软件构建、生产RTL编译/仿真、综合、板测或ASIC实施。待独立评审，不自行宣布通过。

## 决策与下一步

1. 后续波形内容/样式修改通过WaveDrom JSON、WaveDrom支持的配置及既有生成流程完成；结构图生成器不再处理波形。
2. 独立评审以“37张重绘结构图 + 6张WaveDrom波形”为当前范围；前一轮43张手工母版/PPTX记录为历史快照。
3. 当前教材、图集和37页PPTX入口不变，维护入口为 `learning/FIGURES.md`。
