# L01 / 文档审查、知识结构与 HTML/Markdown 同步

> 记录日期：2026-10-11。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-11；任务L01；授权范围为既有文档审查、修订、重构及文档脚本与页面验证。
- 输入：`mp/ara-pulp-v2` / `2784340240915fe4338ec54bfd613723b127d62e`。
- 开始时M01手册有未提交修改，另有未跟踪图稿/交接；本轮全部保护，不覆盖。
- 负责范围：根README、docs_codex文档入口/教材/配置软件参考/文档脚本；主管维护目录与共享索引，三个子任务分别审查软件、存储、配置，并交叉复核。
- 状态：完成（文档重构、格式同步及文档/页面验收）。

## 本轮结果

沿用既有51页内容源，重排42章的知识前置；将HTML源同步导出Markdown阅读版，参考/操作手册按职责归并。问题、迁移与修正见[维护记录](../learning/STRUCTURE_REVISION.md#review-20261011)，推荐入口为[00](../00_README.md)或[教材首页](../learning/index.html)。

源码确认：修正SlinkMaxClkDiv截断说法、ROM/crt0责任、FS/VS与共源测频表述；补Cache地址算例、iDMA双向路径、独立GB需求和一致性条件。新增ROM C调用栈对齐缺口仅为静态确认，待实际ROM指令/目标验证。没有改变工程配置、profile、地址、中断或接口。

## 改动与接口

`learning/content`与`pages.json`为教程源，`learning/*.html`和`learning/markdown/*.md`为同步输出；样式/交互/检查脚本随之调整。configuration/software共11份参考修订。原图、PPTX、旧站、历史证据及生产代码保持。

无Git提交或推送。E01/S01/V01/M01工程任务没有由本轮自动实施。

## 验证证据

结果在[本轮独立目录](../learning/evidence/review-20261011/)，详细命令及初次失败原因见[维护记录](../learning/STRUCTURE_REVISION.md#review-20261011)。

- `build_site.py`、`check_site.py`、`check_structure.py --check-generated`（最终structure-delivery）、`preview_structure_site.py`（browser-delivery）、输入保护与`git diff --check`均退出0。
- 静态/生成：71 HTML、51 MD；194项临时再生成一致；373项兼容映射；508旧ID和43图引用保留；873历史资产/证据与728旧站文件不变。
- 独立MarkdownIt渲染：51文档、30代码、43图、2324表格单元保真；检查器见markdown-review/review.py，以已有MarkdownIt进行验证，生成仅需标准库。
- Chrome151实际file://检查：51页桌面/手机、12无脚本页、199跨页锚点；130截图中人工查看6张关键页面/表格/代码截图。检查期间71个HTML哈希未变。
- 15个既有归档断链（20次引用）仍列警告，原件受保护；不是现用教程链接通过项。既有M01保持；376个初始工作文件在保护检查时一致。交付前图稿工具与资产仍有并行变化（delivery快照见57项），本任务未触碰，详见本轮证据delivery.json，不回滚其他工作。未构建目标软件，未编译/仿真RTL，未综合/板测；预期输出不记为运行通过。

## 决策与下一步

1. 后续正文从 `learning/README.md` 维护规则开始，改源后生成并检查双格式；不要独立编辑生成MD。
2. S01/V01复核ROM C入口与非零平台钩子的栈对齐、实际指令和影响，同时保留原S01-B01返回修复任务。
3. iDMA/向量/GB/DDR和ASIC实施继续使用既有任务边界，不因文档完整而视为工程就绪。

共享状态与任务表由主管串行同步；历史备份失效链接登记保留，不修改受保护原件。
