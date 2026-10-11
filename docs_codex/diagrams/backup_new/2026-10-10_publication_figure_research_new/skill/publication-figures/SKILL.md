---
name: publication-figures
description: "Design publication-sized circuit, computer architecture, and AI method diagrams with concise labels, external captions, editable SVG/PPTX, and vector PDF. Use for new scientific structure/mechanism figures and substantive redraws; not raster illustration, full slide decks, or data-free quantitative charts."
---

# Publication figures

把技术关系变成图，而不是把对话变成说明板。结构化 SVG 是母版；PPTX 保留独立原生对象；PDF 用于排版。保留旧版本供比较。

## 图意与内容

先从输入确定本图要解释的关系、必须保留的事实/连接、语言、最终宽度与使用场景。用已有授权和上下文决定常规选项；无需为这些步骤逐次请求确认。没有投稿规格时，可用 182 mm 宽、9–10 pt 正文字号作为工作起点，明确这是工作默认值，不是所有会议的规定。按[领域图式](references/figure-grammar.md)选择拓扑、原理图、存储阵列、时序或模型数据流。

图内只放定位对象、辨认连接和解释机制所必需的标签。模块名、端口、位宽、地址字段、面板号和必要状态可留；背景介绍、实现限制、例子前提放 caption；来源、版本、测试与交接记录放配套文档。不要自动添加大标题、副标题、阅读指南、外围说明框、聊天提醒或底部证据条。用户明确要求教学注解时，按其目的加入。[内容分工示例](references/content-policy.md)。

删减图面不能删掉事实：拟新增模块仍要能识别，候选架构的成立条件仍须随图提供，箭头语义必须明确。来源不支持的连接不要靠布局补造。重绘需记录旧图到新图/图注的内容映射；保真转换请求则保持用户布局，不强行套新风格。

## 绘制

先排主关系与连线，再放标签，最后配色。默认白底、深色线字、少量有语义的强调色。模块用矩形，存储用阵列/字段，选择用 mux，运算用实际算子；不用同一种圆角卡片包办一切。圆角、色块和边界都可以使用，但要有语义。控制、数据、时序线分别定义；交叉与连接点不能混淆。

不要靠缩小字号容纳长句。过密时拆成互相引用的图，保留 caption 与对照。给实际端口留走线空间；优先清晰路径，不追求装饰性对称或大量重复标签。颜色不是唯一编码，灰度下仍可识别。

## 导出与检查

导出前读[导出约定](references/editable-export.md)。在隔离环境安装 `requirements.txt`；入口优先使用本 skill 的 `.venv`。代码随本 skill 提供，不依赖旧 skill 或特定工程。

```sh
python3 scripts/run.py --input topology.svg mechanism.svg --out-dir export-new \
  --width-mm 182 --min-font-pt 9 --render --font-file /path/to/matching-font.ttf
```

输出 `.editable.svg`、`diagrams.pptx`、逐图 PDF/PNG/灰度预览及 JSON。输出非空时拒绝覆盖。多图 PPT 共用最大高宽比的页面，各图按相同实际宽度置中；PDF 各自保持源图比例。不要将 SVG 转曲或整图栅格化来冒充可编辑 PPT。

查看每张最终预览：文字可读、路线可追踪、无裁切、无非预期覆盖；按[审查要点](references/review.md)复核技术关系、灰度及实际尺寸。脚本的文字/对象保留检查不能证明技术正确或外观一致。Office 未实际打开测试时，明确报告。不要以 SVG/PDF 的渲染代替 Office 外观验收。

真实照片/实验图拼图、数学排版增强、PPT 语义分组与连接器端点绑定不由本版后端支持。AI 方法结构图可以使用此流程；定量结果用有真实数据的标准绘图库；混合图片面板另选能保持来源和独立元素的工具，并说明可编辑范围。具体投稿前复核[场所资料](references/venue-profiles.md)中的当年官方要求。
