# L01 / SVG 母版与可编辑 PPTX 工作流封装

## 基本信息

- 日期：2026-10-06；用户授权查询现有 skill/MCP，没有符合完整工作方式的工具时创建并提供调用方法。
- 输入 HEAD：`5ddec4fb4`；此前本对话的 diagrams/ 与两份交接已未跟踪，原样保留。
- 状态：本地 skill、通用命令行导出器和安装完成；未新增 MCP 服务或修改 Codex 全局配置。
- 范围：`tools/skills/svg-pptx-diagrams/`、独立验证产物目录、本交接；经执行审批安装个人 skill 与隔离虚拟环境。不改 RTL/sw/工程依赖，未 Git 提交。

## 现有能力检查

- 当前会话暴露 PowerPoint Document Control MCP；只读查询返回无连接的 document sessions，因此未构造/执行文档写命令。
- 现有已提供 skill 中有 Google Slides 模板工作流和 raster imagegen，但没有发现完整规定结构化 SVG → 原生文本/矢量对象 → Office 验证的专用工具。
- 插件目录查询 PowerPoint/presentations/SVG 返回 Gamma、Genspark、Miro 等通用能力，均未安装；元数据不能证明其保留 SVG text、逐对象映射和保真验证。本次未安装/连接插件，不声称全球目录没有其他工具。
- 使用了 openai-docs、plugin-management、skill-creator；参照已读取的官方构建/发现说明。官网已将旧 Codex skills URL 重定向到 https://learn.chatgpt.com/docs/build-skills。

## 交付与安装

- 仓库可搬迁源包：`tools/skills/svg-pptx-diagrams/`，包含 SKILL.md、agents/openai.yaml、requirements.txt、scripts/、SVG 子集说明和无供应商内容的抽象示例。
- 已安装个人包：`/home/zhaowenyao/.codex/skills/svg-pptx-diagrams/`。
- 当前官方发现入口：`/home/zhaowenyao/.agents/skills/svg-pptx-diagrams` 为指向该包的符号链接。
- 独立依赖环境：个人 skill 根目录 `.venv/`，python-pptx 1.0.2、Pillow 12.3.0 等；scripts/run.py 自动选择该环境，否则使用当前 Python。代码没有固定仓库路径或临时依赖路径。
- 包源与安装文件逐文件 diff（排除 .venv）通过；自动匹配保持默认启用。未测试当前 UI 技能列表是否热刷新，列表未显示时按官方说明重启客户端。

## 支持范围与边界

- 作者先核对事实，再设计结构化 SVG；text 保留字符串，独立图形逐对象映射为原生 PowerPoint。默认保持等半径圆角，不再因兼容性一律改成直角。
- 支持 rect、circle、ellipse、line、polyline、polygon、单连续 path、单行 text，及无 transform 分组与属性继承；路径 M/L/H/V/C/Q/Z，绝对/相对坐标。Q 精确转换为 C。
- 不支持的 CSS、marker、tspan、滤镜、渐变、裁剪、变换、透明度等报定位错误，不静默栅格化。限制属于此版转换器，不是格式固有限制。复杂旧 SVG 可由 Agent 按用户要求规范化后再导出。
- 生成器默认拒绝非空输出目录；输入不支持时，在创建输出前失败。报告 Office 实测和 SVG Convert to Shape 为独立验证层级。
- 技能不复制受限 PDF/供应商原图、不要求上云，不扩展成整套演示文稿作者或图片生成器。

## 验证证据

- skill-creator quick_validate.py 检查仓库源包与安装包：退出 0。
- scripts/test_svg_to_pptx.py：3 个行为测试通过，覆盖原生对象/文字/圆角和居中几何、相对和二次曲线、复合路径拒绝、5 种不支持特性在写出前失败、已有产物拒绝覆盖及哈希保持。
- 初次临时测试和安装后复测均通过；最终持久证据：`docs_codex/diagrams/2026-10-06_svg_pptx_skill_validation/`。
- 通过已安装 scripts/run.py 导出抽象示例、Crossbar 兼容母版、DDR 兼容母版：退出 0，3 页原生 PPTX，共 251 个对象、108 个文本对象，无 ppt/media/ 整图图片。
- 本机 PowerPoint 16.0 只读打开生成文件、每页一个字符修改/读取/恢复探针通过，导出三张预览；全部 108 个文本逐项与 SVG 相同。只关闭测试 deck、不 Quit 用户应用，未保存探针修改。
- `export_report.json` 是导出时的结构检查快照，其 office_application_tested=false 表示生成器本身未运行 Office；后续实际应用证据在 `office_verification.json` 和 powerpoint-slide-*.png。没有把静态检查当作 Office 测试。
- 未测试 Office 的 SVG Convert to Shape，未生成论文 PDF，也未进行 RTL 编译/仿真/板测。

## 调用

自然语言：`$svg-pptx-diagrams 根据当前工程绘制结构图，输出结构化 SVG、原生可编辑 PPTX 和预览。`

已有图：`$svg-pptx-diagrams 保持 figure.svg 布局和所有文字，生成可编辑 PPTX，输出到 figures-export-new/。`

已安装命令行：

```sh
python3 /home/zhaowenyao/.codex/skills/svg-pptx-diagrams/scripts/run.py --input figure.svg --out-dir figures-export-new
```

多输入对应多页，可加 `--aspect 16:9`；仅规范 SVG 可加 `--svg-only`。新机器需复制源包并按 requirements 在隔离环境装依赖。

## 下一步

- 在新对话中实际调用该 skill 处理用户新图；根据真实失败再扩充 SVG 子集，不以广告承诺任意 SVG 无损转换。
- 如需要接入 Office MCP，先连接并发现 session/schema；本地文件流程无需 MCP。
- 仓库源包与个人安装包为独立副本，今后更新后需验证再同步。本次不改变工程实现状态，无需更改共享任务表。
