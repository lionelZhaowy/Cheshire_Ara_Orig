# L01 / 独立原生箭头与虚线 skill

> 记录日期：2026-10-11。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-11；HEAD `2784340240915fe4338ec54bfd613723b127d62e`。
- 授权：用户放弃 publication-figures 的默认黑白/出版尺寸取向，询问旧 SVG→PPT 的箭头/虚线碎片问题；随后明确要求不要改旧 skill，修正版单独创建便于切换，并要求继续。
- 状态：独立 skill、示例、原生对象导出及结构/程序化编辑测试完成；Office UI 验证未完成。
- 本轮负责路径：`docs_codex/diagrams/2026-10-11_native_pptx_validation/`、`~/.codex/skills/svg-pptx-diagrams-native/`、本交接。没有自动启动子 Agent。
- 起始已有 M01 文档修改、多个图目录与交接未跟踪；上轮 `_new` 图已在用户工作区移入 `diagrams/backup_new/`，本轮未移动/恢复/覆盖这些文件。

## 本轮结果

- [总交付](../diagrams/2026-10-11_native_pptx_validation/README.md)、[ZIP](../diagrams/2026-10-11_native_pptx_validation/svg-pptx-diagrams-native.zip)、[新 skill 源快照](../diagrams/2026-10-11_native_pptx_validation/skill/svg-pptx-diagrams-native/SKILL.md)。已安装新目录与独立依赖环境，旧 skill 保持不变；publication-figures 未删除或修改。
- 新后端读取受限的三角 marker，将 marker-start/end 写成同一线/路径对象的 DrawingML headEnd/tailEnd；将 dasharray 写成同一轮廓的 custom dash。直线为 connector，折线/曲线保留一个自由形状，不生成分离箭头三角形。
- 支持自由画布/适度配色，概念图不套用论文栏宽或投稿字号门槛。新增可选 `--slide-width-in`；不将文件格式本身的页面范围误称为“完全无限”。
- 旧碎片仍兼容，不自动推断线段/三角形关系；原生端点绑定模块、自动布线、任意SVG marker、PPT g分组均未实现。迁移旧图的明确说明已放入 skill。
- 示例26个对象，6个完整箭头、2个带虚线属性对象；SVG保留文字，PPT无整图图片。没有重绘全部工程图。

## 验证证据

- `python -m unittest discover -s scripts -p 'test_*.py' -v`：7项通过，先在仓库快照、后在已安装新skill中运行。旧4项回归保留；新增3项覆盖原生对象、编辑保存后保留、SVG往返和不支持输入拒绝。
- `quick_validate.py <新skill路径>` 通过；已安装 `scripts/run.py --slide-width-in 16` 独立调用成功，临时产物 `/tmp/native-installed-smoke-20261011/`。正式示例在交付目录 `export/`，采用默认14in编辑画布。
- 修改线端点、框宽和曲线位置的行为通过 python-pptx 测试，重新读取后对象数与端点/虚线属性仍一致。不能写成 Office UI 实测。
- Chrome 对规范化 SVG 的本地渲染退出0；已实际查看中文彩色 PNG。浏览器使用本机字体回退；目标 PPT 字体 Microsoft YaHei 不嵌入。
- 原12个skill源文件哈希不变，记录于 `old_skill_hashes.json`；新安装目录/源码包/快照核验见 `validation.json`。
- Office 实际打开、编辑和渲染未执行；未重试或绕过此前的脚本签名策略。SVG预览不替代Office验证。
- 未编译/未仿真/未板测；未改RTL/sw、工程配置、用户现有图稿或共享状态/任务表；未Git提交。

## 下一步

1. 用户可分别调用 `$svg-pptx-diagrams-native` / `$svg-pptx-diagrams` 切换新版与旧版。
2. 在允许的 Office 环境打开示例PPT，检查各类箭头与虚线的实际编辑/显示。
3. 若要修复特定旧图，先确定其线段/三角形对应关系，在新输出目录重建语义，再导出，不对历史文件做盲目自动合并。

无需更新工程实现状态；用户的新偏好与两技能并存关系以本交接和新skill说明为准。
