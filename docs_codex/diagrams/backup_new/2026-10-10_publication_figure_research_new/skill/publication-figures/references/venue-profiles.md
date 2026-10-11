# 场所资料与代表图式

核查日期：2026-10-10。以下为当时的研究快照；仅实际投稿任务需要重新读取对应年份的官方模板。样本观察不是规范，链接不授予再分发原图的许可。APLOPS 按 ASPLOS 理解。

## 3. 官方规范：必须按年份和出版阶段区分

### 3.1 IEEE 通用图稿要求

[IEEE 尺寸和分辨率指南](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/resolution-and-size/)优先建议矢量图。其页面列出的常用宽度为单栏 88.9 mm、双栏 182 mm；非矢量彩色/灰度图要求大于 300 dpi，黑白线稿大于 600 dpi。提高已有低清图片的 dpi 标签不能补回细节。这是通用参照，实际仍以目标模板的栏宽为准。

[IEEE 文件格式指南](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/file-formatting/)列出 PDF/EPS/PS/PNG/TIFF 等交付格式，要求处理好字体嵌入或文字轮廓；建议图中文字在最终尺寸约 9–10 pt。**9–10 pt 是该指南的建议，不是所有会议统一的硬性下限。** SVG 和原生 PPTX 可以作为编辑母版，但不应自动视为投稿文件。

[IEEE 可访问性建议](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/)强调颜色之外再用线型、标记、明暗或直接标签表达区别。灰度打印仍能理解是实际检查项。

旧 skill 要求母版文本可编辑，与最终投稿 PDF 的字体嵌入并不冲突。建议默认使用嵌入字体的出版 PDF，始终保留原 SVG/PPTX 文本；如特定交付必须转轮廓，仅处理另存的出版副本。

### 3.2 场所要求对照

| 场所与本次版本 | 核查到的相关要求 | 对新方案的影响 |
|---|---|---|
| [ISSCC 2026 CFP](https://submissions.mirasmart.com/ISSCC2026/PDF/ISSCC2026CFP.pdf) | 文字与图稿分别提交；图稿模板每页 6 个槽，最多两页；前 7 幅图需正文引用，可另有 3 幅补充图；普通纸打印须可读 | 单独的 ISSCC 图槽 profile；不能套用宽屏幻灯片，也不能把评审补图和最终 digest 混为一谈 |
| [JSSC 作者指南](https://sscs.ieee.org/publications/ieee-journal-of-solid-state-circuits-jssc/jssc-submission/) | IEEE TRANSACTIONS 双栏；图表置于正文相关位置，尺寸必须可读 | 期刊图与正文共同排版；不是 ISSCC 图页格式 |
| [VLSI 2026 Paper Preparation](https://archive.vlsisymposium.org/26web/paper-preparation/) | 三页模板，图页 Arial，不小于 8 pt；要求 PDF eXpress 检查 | 建立年份明确的模板，按图页最终尺寸检查 |
| [VLSI 2027 Author’s Guide](https://www.vlsisymposium.org/authorsguide.html) | 2026-09 更新；图中文字至少 8 pt；Arial/Calibri 为推荐；第 2、3 页采用规定的 2×3 图槽 | 新一年字体措辞和布局要求有变化；不能把 2026、2027 规则拼成一套“永恒规范” |
| [TCAS-I 投稿指南](https://ieee-cas.org/publication/TCAS-I/tcas-i-manuscript-submission-guide) | IEEE TRANSACTIONS 双栏，提供图稿提交指引并链接 IEEE 图形资料 | 使用 IEEE 图稿基础规则，再按具体稿件宽度检验 |
| [TCAS-II 投稿指南](https://ieee-cas.org/publication/TCAS-II/tcas-ii-manuscript-submission-guide) | 正确嵌入和引用图表，尽可能使用矢量；当前页面限定 4.5 页内容与 0.5 页参考文献 | 压缩的是叙事范围，不能靠把所有图缩得更小来满足篇幅 |
| TVLSI | 本轮期刊专属作者网页未成功直接读取；查到 IEEE 通用图稿规则和已发表样本 | 不宣称核实了 TVLSI 特有字号/格式；具体投稿前补读该刊当期指南 |
| [ISCA 2026](https://www.iscaconf.org/isca2026/submit/guidelines.php) | 图表可读、正文引用、彩色图灰度可辨；采用对应模板 | 灰度验证列入检查；模板中的 caption 字号不等于图中所有文字字号 |
| [MICRO 2026 样稿](https://www.microarch.org/micro59/submit/micro59-sample-paper.pdf) | 使用当年模板，图表可读、正文引用、灰度可辨 | 不因 ISCA 与 MICRO 都属体系结构而混用模板 |
| [ASPLOS 2026](https://www.asplos-conference.org/asplos2026/cfp/) | 图表中的文字按缩放后的效果一般应至少 9 pt，低于 8 pt 不允许；100% 阅读不应另行放大；彩色须照顾色觉差异 | 明确检查最终字号，而非 SVG 坐标字号或 PPT 编辑字号 |
| TC | 查阅 Computer Society 通用[作者资源](https://www.computer.org/publications/author-resources)和 IEEE 图稿规则；本轮 TC 专属作者页未能读取 | 不发明 TC 特有的配色、形状或字号要求；以通用规则作候选基线 |
| [CVPR 2026 指南](https://cvpr.thecvf.com/Conferences/2026/AuthorGuidelines)及[官方模板](https://github.com/cvpr-org/author-kit/blob/CVPR2026-v1%28latex%29/sec/2_formatting.tex) | 使用当年模板；图表 caption 为 9 pt；图中文字大小应与正文协调，线宽须适合打印 | 分开处理 caption 与图内标签；不能只检查像素预览 |
| [ICCV 2025 指南](https://iccv.thecvf.com/Conferences/2025/AuthorGuidelines) | 使用 ICCV 对应 author kit 与页数规范 | 可参考 CVF 图式，但不能声称 CVPR 2026 模板就是 ICCV 2025 的逐条规定 |
| [ECCV 2026 政策](https://eccv.ecva.net/Conferences/2026/SubmissionPolicies)及[官方链接模板](https://github.com/paolo-favaro/paper-template/blob/main/main.tex) | LNCS 版式；本次模板有变，不可沿用 ECCV 2024；Figures 节要求清楚可读，图中文字不应小于 6 pt，图注置于图下 | 6 pt 不是本项目默认目标；不把 LNCS 版心当 IEEE 双栏 |
| [AAAI-26 Submission Instructions](https://aaai.org/conference/aaai/aaai-26/submission-instructions/) | 官方检索内容确认使用当年双栏 author kit；页面/完整 kit 直接读取遭 403 | 不采用第三方镜像里的字号、CMYK 等条文冒充本轮已核实的官方要求；AAAI 数字化 profile 待官方 kit 复核 |

没有在本轮查到“只能黑白”“不得圆角”“一张图最多三种颜色”“所有图必须 Arial”等跨场所统一规定。下面涉及颜色数量、留白、线宽和图式的内容，均是设计建议。

## 4. 实際查看的代表图例

选择标准是能说明一种设计方法、能追溯原图、与任务相关；并不意味着这些图的每个视觉细节都值得照搬。链接用于查看原文，不授予将原图放入新 skill 素材包的再分发许可。

| 场所 | 样本与查看位置 | 可借鉴之处 | 不应机械复制 |
|---|---|---|---|
| ISSCC 2016 | [Eyeriss](https://eems.mit.edu/wp-content/uploads/2016/02/eyeriss_isscc_2016.pdf)，p.2，Fig.14.5.2–14.5.6 | 总体架构、逻辑/物理数据流、NoC、PE、实测结果分别承担不同解释任务；使用运算符与存储图形 | 老 digest 图很密，不作为现代字号下限或拥挤程度的目标 |
| JSSC 2017 | [Eyeriss](https://eems.mit.edu/wp-content/uploads/2016/11/eyeriss_jssc_2017.pdf)，p.2 Fig.2、p.3 Fig.3 | 系统概览与逐操作序列分开；颜色绑定 filter/ifmap/psum 身份 | 某些阴影、深底白字是样本选择，不建议默认沿用 |
| VLSI 2026 | [官方图例目录](https://archive.vlsisymposium.org/26web/images-captions/)，C4.4 Fig.1/2：28-GHz WLL；C28.5 Fig.1：正交 CT ΔΣ 调制器 | WLL 用基线与方案、波形/相位关系解释机制；ΔΣ 用积分器、电阻、电容、反馈和 I/Q 对称支路表达电路 | 官方网页单张 PNG 有的小到约 400 px，只作图式观察，不能作可投稿分辨率样板 |
| VLSI 2026，反向参照 | 同目录 C21.1 TinyNPU Fig.1 | 展示应用概览可以承担场景介绍 | 大标题、装饰图标和大底色也会出现在顶会图中；发表地点不能自动证明符合本用户偏好 |
| TCAS-I 2017 | [Fulmine](https://arxiv.org/pdf/1612.05974)，p.3 Fig.1 | 用图形区分 SoC/cluster，展开互连、处理核和 SRAM bank，颜色承担域归属 | 分区必须有技术含义，不能每段说明都铺一个色底 |
| TCAS-II 2023 | [Cheshire](https://arxiv.org/pdf/2305.04760)，p.2 Fig.1–3 | 总线骨架、模块短名、边界端口；从平台图逐层展开到内存接口、控制器 | 它是论文对应版本，不能据图替代当前仓库事实，更不能自动沿用其外存方案 |
| TVLSI 2021 | [Arnold](https://arxiv.org/pdf/2006.14256)，p.4 Fig.1、p.5 Fig.2，作者公开稿 | 系统到局部放大；时钟域边界、CDC 和接口位宽有具体位置 | 灰色面积、竖排文本和细密结构同样可能难读，不应因为是论文就照搬 |
| ISCA 2016 | [Eyeriss dataflow](https://eems.mit.edu/wp-content/uploads/2016/04/eyeriss_isca_2016.pdf)，p.5 Fig.3、p.6 Fig.5 | 用张量切片和时间序列表达复用，图的主体就是计算/映射关系 | 不把每个维度都画成立体块；空间维与时间维必须明确 |
| MICRO 2016 | [Stripes](https://people.ece.ubc.ca/aamodt/papers/stripes-final.pdf)，p.3 Fig.1 | 三个同尺度算例直接比较 bit-parallel、bit-serial 与吞吐补偿，逻辑/运算符比说明框更有效 | 基线与改进的语义必须来自本次技术问题，不能虚构性能优势 |
| ASPLOS 2018 | [MAERI](https://anands09.github.io/papers/maeri_asplos2018.pdf)，p.2 Fig.1 | 树形分发/归约网络的几何结构直接揭示创新；图例解释节点与连线 | 多种颜色与较重背景是样本风格，不是 ASPLOS 规定 |
| TC 2024 | [Ara2](https://arxiv.org/pdf/2311.07493)，p.3 Fig.1、p.4 Fig.2/3 | 总体与 lane 局部展开；slide unit 的基线/优化并列，并以资源曲线连接机制和代价 | 图1饱和颜色多、标签很密；可学层级关系，不必学其全部配色和密度 |
| CVPR 2016 | [ResNet](https://openaccess.thecvf.com/content_cvpr_2016/papers/He_Deep_Residual_Learning_CVPR_2016_paper.pdf)，p.2 Fig.2 | 两个层、一条 identity 支路、求和节点已经解释残差机制；几乎没有外围说明 | 简洁来自问题聚焦，不是所有系统都必须压到几个框 |
| ICCV 2021 | [Swin Transformer](https://openaccess.thecvf.com/content/ICCV2021/papers/Liu_Swin_Transformer_Hierarchical_Vision_Transformer_Using_Shifted_Windows_ICCV_2021_paper.pdf)，p.2 Fig.2、p.4 Fig.3 | 用窗口网格解释 shifted window；用 stage/重复次数/张量维度组织架构 | 圆角与虚线可有明确层级意义，不能一律禁止 |
| ECCV 2020 | [DETR](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123460205.pdf)，p.2 Fig.1、p.6 Fig.2 | 输入图、query、预测框颜色相互对应；概念图与具体架构分开 | 输入照片是任务证据，不是装饰；不可用生成图伪装模型实测输出 |
| AAAI 2024 | [EAN](https://ojs.aaai.org/index.php/AAAI/article/download/28093/28191)，p.3 Fig.2 | 特征图、归一化、乘/加算子、旁路和局部展开组合，数学符号对齐正文 | 示意 feature map 与真实实验热图要区分，不能只为视觉效果加热图 |

如需确认样本的期刊归属，可参见 Fulmine 的[作者提交记录](https://arxiv.org/abs/1612.05974)、Cheshire 的[作者提交记录](https://arxiv.org/abs/2305.04760)、Ara2 的[机构出版记录](https://cris.unibo.it/handle/11585/1004690)及 Arnold 的[机构出版记录](https://cris.unibo.it/handle/11585/859966)。Arnold 的厂商 PDF 旧链接本轮直连 404，实际视觉检查使用上述 arXiv 作者稿，不能称为看过正式排版版本。

