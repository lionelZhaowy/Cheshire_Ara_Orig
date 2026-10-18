---
name: svg-pptx-diagrams-native
description: "Create colourful scientific and conceptual diagrams with flexible SVG canvases and editable PowerPoint objects, including whole-object native arrowheads and dashed outlines. Use for architecture, dataflow and mechanism diagrams or structured SVG conversion; not raster illustration or full slide decks."
---

# SVG 与原生箭头 PPTX 图

这是独立于 svg-pptx-diagrams 的可切换版本，包含自己的导出后端。SVG 是母版，文本保留为 text，PPTX 使用原生图形与文本。旧 skill 和旧产物不自动修改。

## 绘制与用途

- 先根据事实确定对象、关系和箭头语义，再布局。概念解释图、教学图和汇报图使用适合内容的自由画布，不施加论文栏宽、固定物理尺寸或投稿字号阈值。默认保持源图比例；用户明确要求论文插图时才应用指定出版规格。
- 使用协调、适度的语义配色区分数据、控制、存储或阶段；允许柔和色块与适量圆角。不默认黑白，也不把所有图套成同一种卡片布局。保留用户指定的语言与参考风格。
- 图内放必要标签和短注释。不要受聊天影响自动加外围说明框、阅读指南、免责声明或证据条；相关条件和来源放配套说明。用户明确要求解释内容时，按图意加入，不为追求极简删除必要信息。
- 新图的箭头必须画成带 `marker-start` / `marker-end` 的单个 line、polyline 或开放 path；虚线边界使用一个 rect/ellipse/path 的 `stroke-dasharray`。不要用多段小线拼虚线，也不要用额外三角形拼箭头。先读[SVG 与原生对象约定](references/svg-profile.md)，直接参考[完整示例](assets/native_example.svg)。
- 已有 SVG 保真转换时不凭位置自动合并线段/三角形。旧碎片若需变成完整箭头，先明确对应关系，重建成语义路径再导出；细节见[旧图迁移](references/legacy-migration.md)。旧格式仍兼容，但重新导出本身不会让无语义的碎片自动合并。

## 导出

脚本使用本目录 `.venv`（如有），否则使用调用 Python；依赖见 `requirements.txt`。安装说明见[跨平台使用](references/platform-install.md)。没有其他 skill 或工程的绝对路径依赖。

```sh
python3 scripts/run.py --input figure.svg --out-dir output-new
python3 scripts/run.py --input overview.svg mechanism.svg --out-dir output-new --aspect source
python3 scripts/run.py --input figure.svg --out-dir output-new --slide-width-in 16
```

`--slide-width-in` 是 PPT 编辑画布宽度，默认 14 in，可调整；不代表论文最终尺寸。SVG 保持自己的 viewBox。`--aspect 16:9` / `4:3` 仅在用户要求时使用；同一 PPT 的页面尺寸统一，不同比例的图居中留白，不拉伸。PowerPoint 文件格式本身仍有页面尺寸范围。

输出 `.editable.svg`、`diagrams.pptx` 和 `export_report.json`；输出非空时拒绝覆盖。可用 `--svg-only` 只校验/规范化 SVG。PNG 预览由本地 SVG 渲染器生成，不上传用户资料。

PPTX 自动去掉最底层、恰好覆盖 viewBox 的普通背景矩形：白色使用 PPT 默认背景，其他实色转为页面背景填充。仅识别无圆角、无虚线、无可见异色边框的首个图元；内部白色模块、边框和后绘制的矩形保持独立对象。SVG/PNG 背景保留，报告列出省略的背景对象 ID；合辑中的页面背景覆盖整页，包括不同比例图稿的留白。

## 对象行为与验证

- 直线箭头是原生连接线，箭头为线属性；折线/曲线是保留路径的单个原生自定义几何对象，箭头仍为线属性。双向箭头是同一对象的两个端点。虚线轮廓是完整形状的线属性。它们都不需要额外三角形或大量短线。
- “一个对象”不等于“已绑定模块端口”：当前未绑定连接器与模块，移动模块不会保证线条自动追随。折线/曲线保留形状与可编辑顶点，但不承诺 Office 标准肘形连接线的自动路由行为。文字标签仍独立；SVG 的 g 会展开，不保留 PPT 语义组合。
- 保存后重读，校验文字、对象数、原生端点和虚线属性，并检查 ZIP 中没有整图图片。报告区分原生箭头/虚线数量及旧碎片未自动合并。
- 查看每张实际预览，检查线端点、方向、反向/双向箭头、标签遮挡和虚线边界。SVG marker 映射为 PowerPoint 中等大小三角端点，不承诺两种渲染器逐像素一致。
- 有许可且执行环境允许时，可用 `scripts/verify_powerpoint.ps1` 只读打开、在内存试改文本并导出预览。未实际运行 Office 就写“结构检查通过，Office 显示/编辑未验证”；程序化修改对象属性不等于 Office UI 实测。脚本不绕过签名策略。

示例：`$svg-pptx-diagrams-native 用中文画一张适度配色的概念解释图，自由画布，箭头和虚线框在 PPT 中保持完整对象，说明文字不要自动放到外围框。`
