# L01 标题评审建议的定向收尾

2026-10-08；mp/ara-pulp-v2，HEAD 459f9d6f5748e39063f7bb67e959c2f27859915d。用户授权落实[标题独立复审](handoffs/2026-10-08_L01_title_style_independent_review.md)的三类非阻断建议。本次为标题润色，不重新组织课程或审计技术正文。

## 实际修改

- 补足IP、VGA、RVV三个标题的技术对象；两处WT/pending、trap handler显示名改用中文技术主题，准确英文/源码标识保留正文。
- 统一5个篇标题、4个章标题的中英文间距；同步首页5个篇标题、实验页1个标题及首页4处章标题引用。
- 共20项标题源字段修改、4处可见引用同步；生成页中的重复显示不另计数。其他合规标题、正文中的先后引导、自测问句和“主动让出”等技术用语保留。
- 从content/pages.json生成当前51主页面和20旧入口。文件名、slug、语义ID、链接目标、章序与迁移映射保持。

## 修改对照

|来源/锚点|原文|改后|类型|
|---|---|---|---|
|scripts/pages.json#parts/foundations/title|系统与CPU使用模型|系统与 CPU 使用模型|metadata-spacing|
|scripts/pages.json#parts/vector/title|Ara向量执行与数据交接|Ara 向量执行与数据交接|metadata-spacing|
|scripts/pages.json#parts/os/title|RTOS与嵌入式Linux|RTOS 与嵌入式 Linux|metadata-spacing|
|scripts/pages.json#parts/integration/title|IP、DDR与系统协作|IP、DDR 与系统协作|metadata-spacing|
|scripts/pages.json#parts/platform/title|ASIC平台与物理实现|ASIC 平台与物理实现|metadata-spacing|
|scripts/pages.json#pages/cva6/title|CVA6与RISC-V程序使用模型|CVA6 与 RISC-V 程序使用模型|metadata-spacing|
|scripts/pages.json#pages/rtos/title|RTOS任务、调度与同步|RTOS 任务、调度与同步|metadata-spacing|
|scripts/pages.json#pages/linux/title|嵌入式Linux启动与用户程序|嵌入式 Linux 启动与用户程序|metadata-spacing|
|scripts/pages.json#pages/manufacturing-test/title|Scan、MBIST与制造测试|Scan、MBIST 与制造测试|metadata-spacing|
|content/accelerators.html#control-registers|寄存器与软件|IP 控制寄存器与软件接口|technical-title|
|content/index.html#part-foundations|第一篇 · 系统与CPU使用模型|第一篇 · 系统与 CPU 使用模型|heading-spacing|
|content/index.html#part-vector|第五篇 · Ara向量执行与数据交接|第五篇 · Ara 向量执行与数据交接|heading-spacing|
|content/index.html#part-os|第六篇 · RTOS与嵌入式Linux|第六篇 · RTOS 与嵌入式 Linux|heading-spacing|
|content/index.html#part-integration|第七篇 · IP、DDR与系统协作|第七篇 · IP、DDR 与系统协作|heading-spacing|
|content/index.html#part-platform|第八篇 · ASIC平台与物理实现|第八篇 · ASIC 平台与物理实现|heading-spacing|
|content/index.html#cva6.html|<a href="cva6.html">02 · CVA6与RISC-V程序使用模型</a>|<a href="cva6.html">02 · CVA6 与 RISC-V 程序使用模型</a>|visible-reference|
|content/index.html#rtos.html|<a href="rtos.html">23 · RTOS任务、调度与同步</a>|<a href="rtos.html">23 · RTOS 任务、调度与同步</a>|visible-reference|
|content/index.html#linux.html|<a href="linux.html">25 · 嵌入式Linux启动与用户程序</a>|<a href="linux.html">25 · 嵌入式 Linux 启动与用户程序</a>|visible-reference|
|content/index.html#manufacturing-test.html|<a href="manufacturing-test.html">38 · Scan、MBIST与制造测试</a>|<a href="manufacturing-test.html">38 · Scan、MBIST 与制造测试</a>|visible-reference|
|content/labs.html#system-exercises|OS、ASIC与测量的机制推演|OS、ASIC 与测量的机制推演|heading-spacing|
|content/sharing.html#cpu-ara-mechanism|当前 CPU/Ara：WT、pending 与失效通知|CPU/Ara 写直达、在途访存与缓存失效协作|technical-title|
|content/stream-io.html#vga-registers|参数和关键寄存器|VGA 参数与关键寄存器|technical-title|
|content/traps.html#local-handler|本地 trap handler 的适用范围|本地异常与中断处理入口的适用范围|technical-title|
|content/vector.html#implementation|状态、循环和编程入口|RVV 运行状态、分块循环与编程入口|technical-title|

## 证据与范围

[独立证据目录](learning/evidence/title-polish-20261008/)保存3271个输入文件哈希、Git状态、51页原正文、原pages.json及逐项变化。历史标题报告的664/319计数继续代表原轮次，未回填成此次结果；先前生成/浏览器报告保持原输入身份。

本轮按新输入进行非标题内容、ID、链接和顺序保护，以及生成/结构/浏览器检查；实际结果由下方发布记录及[独立交接](handoffs/2026-10-08_L01_title_polish.md)记录。生产RTL、sw、依赖、地址、链接与构建入口只读；无目标编译、仿真、综合、板测或性能验证。

## 本轮检查结果

- [差异保护](learning/evidence/title-polish-20261008/protection/result.json)：51页维护源与修改前快照逐字比较，仅允许列明的20项标题字段及4处引用同步；508个ID、链接目标和顺序保持。3271个已有文件中3208个未变，63个变化均属于授权范围。
- [结构与生成检查](learning/evidence/title-polish-20261008/structure/checks.txt)：71个HTML、5068个本地链接/资源、108个SVG检查通过；临时目录重新生成的143个产物一致。历史证据、备份及定向源码哈希保护通过。
- [浏览器检查](learning/evidence/title-polish-20261008/browser/browser.txt)：Chrome 151.0.7922.108离线检查51页桌面/手机视口、12项无脚本入口及199项跨页旧锚点跳转；无JavaScript异常、资源失败或页面溢出。五处技术标题另留桌面/手机截图，人工检查了每处至少一个视口，未见标题或目录遮挡。
- 正式标题中英文间距扫描及`git diff --check`通过。本轮没有遗留的标题收尾阻塞项；上述结果仅证明文档修改和发布检查，不代表重新审核全部技术正文或完成目标运行验证。
