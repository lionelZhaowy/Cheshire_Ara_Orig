---
name: svg-pptx-diagrams
description: "Create scientific and engineering diagrams as structured SVG and native editable PowerPoint shapes, or convert existing structured SVG while retaining text, geometry, and independent objects. Use for architecture, dataflow, interface, and mechanism figures; not raster illustration or full presentation authoring."
---

# SVG 与可编辑 PPTX 科研图

使用结构化 SVG 作为设计母版，按同一布局生成原生 PowerPoint 对象。SVG 文本保持为 text；PPTX 文本为可编辑文本框。不是 Office 的“插入图片后转换为形状”，也不是 PNG 描摹。

## 工作方式

- 新图：先核对用户提供的事实、对象与连接关系，再绘制 SVG。沿用明确指定的参考布局；设计建议与已实现能力分开标注。以层级、留白、字体和连接清晰度控制外观，不默认添加阴影或大量装饰。
- 已有图：先查看原图并读取 SVG。保持技术内容和可用布局；把 CSS、marker 等改写为显式属性/独立箭头时检查内容与外观。不要为了转换擅自删除文字或改变结构。
- 生成 PPTX 时先读 [支持的 SVG 子集](references/svg-profile.md)。默认保持圆角、字体与对象分离，不将文字转 path；不支持的效果应说明并按用户意图重新设计，不能悄悄栅格化。
- 母版、衍生 SVG、PPTX 和预览放在用户指定的新输出目录。已有输出默认拒绝覆盖。PPT 中的手工改动不会自动同步回 SVG。

## 导出

脚本路径相对本 skill 根目录；支持任意输入路径，不依赖 Cheshire 或某个临时 Python 环境。

```sh
python3 scripts/run.py --input figure.svg --out-dir output-new
python3 scripts/run.py --input overview.svg details.svg --out-dir output-new --aspect 16:9
```

需要 `python-pptx` 和 Pillow；run.py 自动使用 skill 根目录的 .venv（如果已安装），否则使用当前 Python。没有依赖时根据 [依赖清单](requirements.txt) 在隔离环境安装，不修改任务仓库的依赖清单。仅生成/检查结构化 SVG 可加 `--svg-only`，不需要这些依赖。

Windows 调用用 `python scripts/run.py`；Linux/WSL 用 `python3 scripts/run.py`。各平台必须分别建立 .venv，不能复制 WSL/Linux 的虚拟环境到 Windows。个人安装及验证步骤见 [跨平台同步](references/platform-install.md)。

交付：每个输入对应一个 `.editable.svg`；一个 `diagrams.pptx`（每图一页）；`export_report.json` 记录输入哈希、对象数、文本一致性和实际测试边界。PNG 预览按当前可用本地渲染工具生成，不上传用户资料到外部服务。

## 验证与交付

- 导出器验证源文字和重新读取 PPTX 的文字逐项相同、对象数相同、文件没有整图图片。它不会证明外观无碰撞，仍须查看实际预览。
- 有本地 PowerPoint 时，可运行 `scripts/verify_powerpoint.ps1`，只读打开生成文件、在内存修改/恢复一个字符并导出预览。只关闭测试文档，不操作用户的现有文档，不调用应用 Quit。遵守环境执行权限。
- 没有 PowerPoint 时报告“结构检查通过，未在 Office 实测”，不能用浏览器 SVG 渲染代替 PPTX 验证。Office 的 SVG Convert to Shape 是另一条路径，未经测试不要声称通过。
- 按最终用途检查字号和信息密度：报告和论文可以采用不同详细程度，出版尺寸遵循目标期刊。期刊需要的 PDF/PNG 需另行导出并检查，不自动宣称可投稿。

## 调用示例

`$svg-pptx-diagrams 根据本地 RTL 绘制 SoC 架构图，保留 SVG text，输出原生可编辑 PPTX 和预览。`

`$svg-pptx-diagrams 把 figure.svg 转成独立文本框和矢量对象，保持原图布局，输出到 figures-export-new/。`

`$svg-pptx-diagrams 将 overview.svg 和 details.svg 制成两页 16:9 可编辑 PPTX，并检查字号和拥挤区域。`
