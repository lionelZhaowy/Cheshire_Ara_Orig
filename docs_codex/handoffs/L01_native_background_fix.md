# L01 / PPTX 自动排除画布背景矩形

> 记录日期：2026-10-11。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-11；输入 HEAD `2784340240915fe4338ec54bfd613723b127d62e`。
- 授权：用户要求修复 PPTX 将白色背景导出为可选矩形、需手工删除的问题。按此前保护边界，仅修改新版 `svg-pptx-diagrams-native`，旧 skill 不变。
- 状态：实现、安装及现有 native 图稿重新导出完成；Office 实际显示/编辑未验证。
- 负责路径：新版 skill 安装目录、`diagrams/2026-10-11_native_pptx_validation/` 中的快照/ZIP/示例、`diagrams/native_reconstruction/` 的 PPTX/复现脚本/报告，本交接。
- 起始工作区已有大批文档/教材修改，未触碰这些改动或共享状态文件，未启动子 Agent。

## 本轮结果与实现

- 新增 `svg_to_pptx.py::pptx_figure`：只识别首个图元，要求矩形坐标与 viewBox 完全对应、无圆角/虚线、描边不存在或不可见/与填充同色。白色背景不生成形状，也不强制设置页面背景；其他实色转为 PPT 页面填充。
- 图内白色模块、异色边框、圆角框，以及覆盖在其他内容之上的矩形保持独立对象。SVG 数据不变；导出与重读校验使用过滤后的 PPT 对象列表，报告明确记录省略的背景 ID。
- 45 张图：42 张白底、3 张浅色底，全部省略背景矩形。45 个单图 PPTX 与合辑均已更新；合辑从 3154 降至 3109 个对象，1653 个文本、306 个完整箭头、4 个虚线框保持。示例 PPT 从 26 降至 25 个对象。
- 新版 skill 安装目录、源码快照及 ZIP 同步；旧 `svg-pptx-diagrams` 的 12 个源文件哈希不变。背景修正无需用户另行切换 skill。
- [交付说明](../diagrams/native_reconstruction/README.md)、[合辑](../diagrams/native_reconstruction/all_diagrams.pptx)、[修正验证报告](../diagrams/native_reconstruction/background_update_report.json)。新目录仍为单层，无子目录。

## 验证证据

在仓库根目录执行：

```sh
~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B -m unittest discover \
  -s docs_codex/diagrams/2026-10-11_native_pptx_validation/skill/svg-pptx-diagrams-native/scripts \
  -p 'test_*.py' -v

~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/native_reconstruction/rebuild.py \
  --skill docs_codex/diagrams/2026-10-11_native_pptx_validation/skill/svg-pptx-diagrams-native \
  --out-dir /tmp/cheshire-native-no-background-export

~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/native_reconstruction/verify_outputs.py \
  --report docs_codex/diagrams/native_reconstruction/validation.json
```

- 最终测试 10 项全部通过（7 项既有回归 + 3 项背景行为测试，含多种子场景）。新测试覆盖非零 viewBox 原点、继承样式、同色描边、彩色页面背景、保留普通白色模块/圆角/异色边框/虚线框/后置矩形，以及 SVG 不被修改。
- 测试初次失败是测试将深拷贝后的 XML Element 按对象身份比较；改为比较对象数据和 XML 序列化后通过，未通过削弱背景语义断言回避问题。
- 在临时目录完成全部导出后，对比 46 个 PPTX 的 90 页：仅删除第一个 `rect-001`，其余所有图形 XML 除顺序对象 ID 重新编号外完全一致，才替换当前 native 产物。
- 45 SVG 与 50 PNG 的 SHA-256 全部不变；45 个原始输入哈希不变；旧 skill 哈希不变。完整对象/文字/箭头/虚线/ZIP 检查与程序化编辑保存检查通过。
- 已安装新版 CLI 实际调用通过，输出 `/tmp/native-background-installed-smoke/`；`quick_validate.py` 对快照与安装目录均通过；15 个源码文件在安装目录和快照间完全一致，ZIP 已更新。
- Office 显示与 UI 编辑未运行；没有为本次背景修正重新渲染未改变的 SVG/PNG。合辑浅色页面背景覆盖整页，包括不同比例图稿的留白。
- 未修改 RTL/sw、工程配置、教材正文和旧图产物；未编译/未仿真/未板测；未 Git 提交。

## 下一步

- 用户打开已更新合辑或单图 PPTX，画布背景不再是可选图形，无需手工删除；可继续在 Office 中检查实际显示。
- 后续使用新版 skill 默认应用此行为；若要修改判定范围，先读 `test_canvas_background.py`，保留图内白色模块的保护条件。
- 项目工程事实未变化，无需合并生产状态变更。
