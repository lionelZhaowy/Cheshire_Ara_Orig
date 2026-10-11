# L01 文档结构与维护记录

<a id="review-20261011"></a>

## 2026-10-11 既有文档审查与重构

输入：`mp/ara-pulp-v2 / 2784340240915fe4338ec54bfd613723b127d62e`。范围限根/本地文档入口、现用教程及配置/软件参考、样式、文档生成/检查脚本。未修改生产代码、构建入口或依赖；既有 M01 未提交差异及未跟踪图稿/交接按输入哈希保护。完整输入见 [input.json](evidence/review-20261011/input.json)，简短交付见 [本轮交接](../handoffs/L01_documentation_restructure.md)。

### 盘点与内容职责

现用主入口为根 README、`00_README`、教材首页、configuration/software README；主教程 42 章、8 页实验/参考和首页，共 51 页，另有 20 个旧页入口。`learning/content/*.html` 由已有 `build_site.py` 生成站点；配置/软件共 11 份 Markdown 原来独立维护，相同解释存在漂移。`docs/` 为随附官方说明；`01`、早期规划/审查报告、learning_backup 和各日期证据保留历史身份。图稿、PPTX、WaveDrom 输入及脚本均复用，本轮没有新增图。

主教程负责连续解释；configuration 按子系统提供参数字典和修改影响；software 与 labs 负责操作和排错；M01/P01/02/03 负责工程契约。原计划 03–08 已有这些承载位置，不再补一套同名平行文档。审查覆盖所有现用章的职责/前置/标题和关键事实，定向源码复核重点在启动、地址/AXI、缓存/SPM、DMA、Ara、配置与时钟；不称为逐行 RTL 全审计。

### 问题位置与实际处理

| 问题位置 | 问题性质 | 对理解/使用的影响 | 处理方式 |
| --- | --- | --- | --- |
| 根 README、00 索引与旧03–08计划 | 入口及状态混杂 | 读者仍进入旧快照，误以为已有主题尚未编写 | 当前入口置顶，旧调查整体保留为历史补充，列出现有承载位置 |
| 原第3章配置、第6章启动 | 前置关系倒置 | 未学地址、Cache/SPM就开始读参数和存储初始化 | runtime/build先给全链，地址/存储/协作前置，详细启动与配置后置 |
| 首页手写目录 | 多份导航来源 | 篇章/副标题容易与侧栏和上下页漂移 | 首页目录也由 pages.json 生成，保留九个篇锚点与所有页面路径 |
| HTML 教程与 Markdown 摘要 | 内容独立维护 | 同一知识点不同表述/维护日期，无完整MD主线 | HTML既有源同次导出51篇MD，参考/操作手册保留独立职责 |
| software 日期补丁 | 重复和顺序割裂 | 关键前提埋在末尾 | 编译过程/装载/库调用归回对应节，旧标题锚点保留 |
| RUNTIME_AND_DEBUG 主图、crt0 描述 | 控制流/责任错误 | JTAG被误排在ROM C之后，应用栈调整被算到ROM | 分开ROM早期初始化、JTAG接管与应用crt0，精确列保存的sp/gp/ra |
| ROM C 入口栈对齐 | 新发现的源码缺口 | 不能用应用的24B栈调整证明ROM调用满足ABI | 诊断记录默认sp模16为8；官方psABI与当前源核对，生成指令和运行影响仍待验证 |
| memory | 概念缺口与术语混同 | 不理解容量、冲突和scratch差别 | 增加组/路/行/地址算例，明确SPM固定way槽与SLVERR、MMIO/CSR scratch分义 |
| dma 与软件入门顺序 | 路径/能力解释不足 | 容易误解iDMA只能输入、需专线、默认可跑 | 展开官方名称、控制/读/写的互连路径，先讲二维推导，保留Reg64/DW32与无完成IRQ门槛 |
| CVA6 88字段长表、Cheshire机制分散 | 参考组织不当 | 只查名词，缺子系统与消费者上下文 | 拆六组，保留88/113行有效字典；补影响、软件依赖及验收 |
| SlinkMaxClkDiv | 事实错误 | 将无效覆盖归因于1024截断 | 字段为16位shrt_bt；实际SoC/VIP消费包常量，配置字段不生效 |
| Ara/共享/加速器及模型 | 当前拓扑和后续GB需求脱节 | 误把共享互连当一致性，或把GB流量都算DDR | 说明原访存路径、独立SRAM GB已确认性质/待实现支路，区分逻辑读写量与DDR流量 |
| clocks/measurement、os-debug | 使用条件和术语 | 共源RTC被当独立测频；crt0被写为开启VS | 注明VCU118 RTC与CPU共源、locked悬空；VS由应用开启 |
| 阅读页面 | 卡片及位置提示 | 原理被视觉分隔，宽表/代码不易定位 | 弱化goals/source外框，增加当前小节标记、表格键盘滚动及格式入口，保持正文字号 |

### 内容迁移与兼容

本轮保留42章规模和51主页面，按九篇重排：系统/程序4章 → 地址/互连/存储5章 → DMA/Ara/共享4章 → 启动/外设8章 → 时钟/复位/配置3章 → OS4章 → IP/DDR4章 → ASIC8章 → 验证2章。全部语义URL继续可用；章号不作为永久标识。旧图保留原号并明确历史身份。旧 `index.html#part-devices` 通过语义别名落到当前启动/外设篇；系统管理篇改用 `part-management`，避免把旧外设书签重新解释为配置入口。

具体章内归并：interconnect的验证案例归末尾；memory的容量与way机制放在共享使用条件之前；dma的2D推导放在CSR字段之前；sharing的现有数组协作留在当前机制；CHESHIRE的日期补充并入第3/5节；software的对象/构建/库/装载补充并回主题节。未移除独有命令、限制、错误条件或历史实验结果。

HTML是沿用的唯一教程正文源，Markdown是可审阅、可链接的生成阅读版，不反向解析回HTML。新增导出器仅用标准库；保留代码、图注和语义锚点，寄存器与计算器交互留HTML，Markdown保留数据/默认值。转换遇到未知标签即失败；源码与生成结果漂移由检查器拒绝。

### 验证结果与未解决项

全部检查产物在 [本轮独立目录](evidence/review-20261011/)，不覆盖旧报告。以下为本轮实际结果：

- [输入保护](evidence/review-20261011/protection-compatible/result.json)：保护检查时，开始已有的376个文件字节不变；51个源页的508个旧ID、43图引用和代码命令保留。只澄清RVV示例中一行输出目录注释，未改命令。Cheshire113/CVA6 88项字段标识完整；生产代码、历史资产和示例未改。
- [结构与临时生成](evidence/review-20261011/structure-delivery/checks.txt)：九篇42章/51页、373项迁移、71 HTML、5149本地链接/资源与3234 Markdown链接/片段检查完成；51对格式同源，194项临时再生成产物一致。873历史证据/示例/资产及728旧站文件保持。
- [独立Markdown渲染](evidence/review-20261011/markdown-delivery/result.json)：用环境已有MarkdownIt 2.2.0检查51个实际生成文件，513标题/目录、30代码块、43图片、2324表格单元、518源ID及1786本地链接保持；7组转换边界样本及非法标签拒绝通过。MarkdownIt仅用于本次独立验证，不是生成依赖。
- [Chrome离线页面](evidence/review-20261011/browser-delivery/browser.txt)：Chrome151，1440×1100桌面与390×844手机逐页检查；12页禁用脚本、199个跨页旧锚点、寄存器筛选/计算器/目录/图缩放通过。宽表与代码内部滚动，字号不小于14px，无页面整体溢出、失败资源、JS异常或联网请求；71个被测HTML前后哈希一致。
- 人工实际查看首页桌面/手机、Cache组路地址算例、配置取值层表、手机长寄存器表和代码区的6张截图。段落、表头、图文与导航可读；手机长表/代码截图刻意滚到最右以验收内部滚动，并非内容截断。130张浏览器截图包含原有图稿回归；本轮未重绘图稿。
- [定向源码证据](evidence/review-20261011/sources.json)记录32个文件及符号/哈希；新增栈检查按当前ROM/CRT和官方psABI交叉核对，不以源码检查冒充生成指令或运行证据。

仓库根的可重跑命令如下；`新目录`必须换成不存在的路径：

```bash
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/check_site.py
python3 docs_codex/learning/scripts/check_structure.py --check-generated --out-dir 新目录1
python3 docs_codex/learning/scripts/preview_structure_site.py --out-dir 新目录2
python3 docs_codex/learning/evidence/review-20261011/check_protection.py --out-dir 新目录3
git diff --check
```

交付前末检发现既有未跟踪图稿工具与资产仍有并行更新（native PPTX skill、native_reconstruction及相关产物）；它们不属于本轮写入范围，本任务没有覆盖或回滚。上述376文件一致结论对应已保存的protection-compatible检查时点；交付快照所见57个并行变化逐项保存在delivery.json，不能将这些变化归为本轮修改，也不承诺其他任务随后停止写入。教材源/脚本/资产与71个被测HTML仍和最终浏览器输入完全一致，M01原未提交内容也保持。

初次保护检查因已审阅的RVV注释改写失败，加入精确差异规则后通过；初次结构检查暴露旧脚本将现用CSS/JS当历史不可变资产，现已限定保护为历史图稿/示例/证据。另一次Chrome启动被沙箱socket限制阻止，获准运行本地Chrome检查后完整通过。失败日志也保留，未伪装为首轮全通过。

保留事项：Platform ROM正常返回缺陷、ROM C入口栈对齐影响、iDMA控制桥与HAL、Ara/并发和OS目标运行仍待专门工程任务。当前只做文档生成、源码抽查和轻量文档检查。未重新构建软件、仿真生产RTL、综合、刷板或迁移IP。

开始时已有的未跟踪交接/图稿备份含15个独立失效相对链接，精确列在 [known_link_gaps.json](scripts/known_link_gaps.json)。这些受保护原件没有改写；检查仍打印警告，不把它们记为通过。现用教程、参考和本轮交付的断链必须修正，新增错误仍使检查失败。

---

以下为原始2026-09-29记录，旧章号/“当前”指当时版本，保留独有迁移和证据，不作为现行目录。

# L01 篇章结构修订 · 2026-09-29

输入为 `69fabdd227e225bf9f5f0b9ec5fe9d056999fea6` 的深度扩充版本。依据[结构审查](../handoffs/L01_structure_review.md)修订；该审查原文及索引记录保留。本次授权是教材、配图与必要维护工具，不涉及生产 RTL、软件、平台或依赖修改。

## 对上一轮问题的反思

上一轮把“补齐知识点”当成主要完成标准，继续向 16 个页面追加平级小节。正文加深了，目录却仍只理解 H2；既没有按新增主题调整章节职责，也没有同步检查前置关系。有效链接检查还漏掉了“目标存在但含义不对”和“历史记录被称为本轮”的问题。

本次以读者需要完成的任务划分章节，再迁移已有内容。全书为七篇、30 章，另有首页、六项实验合册及两页参考，共 34 个主页面。篇是导航分组，不增加空白篇首页。章节内部采用 H1 章、H2 节、H3 小节；不为追求层数强行添加 H4。

## 逐项回应审查

| 项目 | 已落实的修订 | 检查入口 |
| --- | --- | --- |
| R1 导航扁平 | 显式篇/章清单；当前篇默认展开，当前章列节；页内目录嵌套 H2/H3；面包屑、章号、上下章共用清单 | [目录清单](scripts/pages.json)、[生成器](scripts/build_site.py) |
| R2 职责过密 | 原存储页拆至 11/12/22/26；向量页拆至 24/25/26/29 | 下方目录及[148 个原 H2 归属](evidence/structure-20260929-allocation.json) |
| R3 顺序倒置 | 地址与协议先于 Crossbar；外设按结构/复位寄存器/初始化/操作/错误验证排列；实验 E 扩充降为 H3 | [UART/GPIO](uart-gpio.html)、[实验 E](labs.html#lab-e) |
| R4 重点不足 | 独立 CVA6、时钟、复位、电源、DDR；真实字段/消费者/约束表；寄存器索引直达关键语义；IP 交付边界表 | [配置](configuration.html#fields)、[DDR](ddr.html)、[扩展集成](accelerators.html#delivery-contracts) |
| R5 字段名 | `EnAra` 改为 `Cfg.Ara`；同处标明 `Cfg.AraNrLanes/AraVLEN`，不把配置层混写 | [配置依据](../../hw/cheshire_pkg.sv) |
| R6 启动依赖 | ROM 自主启动与 JTAG 接管分开；后者条件为相应配置下检查 `CFG_SPM_LOW.bit0`，再请求 halt 并等应答；没有等待 ROM C 测频 | [JTAG](boot-debug.html#takeover)、[VIP](../../target/sim/src/vip_cheshire_soc.sv) |
| R7 证据指向 | 本次结构报告为 `#structure`，此前扩充为 `#depth`，09-28 为 `#current`；V 仅在汇编内核的说法限定初始示例 | [证据页](evidence.html)、[RVV 编程](vector.html#programming) |

额外定向纠错：UART 的槽间隔为 4 字节，但当前 `uart.c` 使用 `reg8`，现已区分 C 访问宽度与 Reg/APB 接口宽度，并给出初始化调用、DLAB 顺序、分频合法范围与超时缺口。GPIO 的复位语义移到输出操作之前。

JTAG 配图同步修正：流程图标明检查配置位，WaveDrom 不再把 `BIST / SPM / stack` 合成一个已完成事件。ROM 写配置及 COMMIT 后还有扩展 sp 的指令；应用若继承栈须独立验收实际 PC/sp。两图均为教学图，不是仿真波形。时序继续由本地 WaveDrom 3.5.0 导出，无 0/1 表格拼图。

## 当前章节职责

| 篇 | 章 | 学习出口 |
| --- | --- | --- |
| 第一篇 | 01 · [整体架构与平台边界](architecture.html) | 沿取指、数组与字符输出辨认模块职责。 |
| 第一篇 | 02 · [CVA6 功能与 RISC-V 系统基础](cva6.html) | 把 ISA、CSR、访存与实现资源联系起来。 |
| 第一篇 | 03 · [Cheshire、CVA6、Ara 与软件配置](configuration.html) | 按真实字段及消费者建立自洽组合。 |
| 第二篇 | 04 · [时钟系统与 PLL](clocks.html) | 区分时钟域、使能、同步器和平台时钟源。 |
| 第二篇 | 05 · [复位体系与平台启动条件](reset.html) | 从请求生命周期定义复位、就绪与恢复。 |
| 第二篇 | 06 · [电源域与低功耗规划](power.html) | 区分现有 RTL 边界和待实现的电源契约。 |
| 第三篇 | 07 · [地址空间与访问属性](address-map.html) | 分别核对路由窗口、实际容量和 CPU 属性。 |
| 第三篇 | 08 · [AXI 通道、突发与握手](axi.html) | 沿真实握手语义理解一笔读写事务。 |
| 第三篇 | 09 · [AXI Crossbar 结构与事务路由](interconnect.html) | 追踪译码、仲裁、W 路由、ID 与响应。 |
| 第三篇 | 10 · [接口适配与 RegBus](adapters.html) | 解释位宽、协议、ID 转换及跨域边界。 |
| 第三篇 | 11 · [Cache、LLC/SPM 与存储路径](memory.html) | 区分缓存副本、地址别名与共享物理阵列。 |
| 第三篇 | 12 · [DDR 控制器、PHY 与 AXI4 接入](ddr.html) | 从平台初始化到软件可用建立交付条件。 |
| 第四篇 | 13 · [裸机 C 程序运行模型](runtime.html) | 从对象、调用和初始化理解存储布局。 |
| 第四篇 | 14 · [工具链、链接与 ELF](build.html) | 让同一数组程序形成可解释的装载产物。 |
| 第四篇 | 15 · [Boot ROM、启动模式与应用初始化](boot.html) | 分别追踪 ROM 服务、自主加载和应用入口。 |
| 第四篇 | 16 · [JTAG 与程序加载调试](boot-debug.html) | 核实外部调试接管的真实等待条件。 |
| 第四篇 | 17 · [Questa/VCS 仿真与结果验证](simulation.html) | 按阶段检查输入、运行、数值和退出。 |
| 第五篇 | 18 · [MMIO 驱动、UART 与 GPIO](uart-gpio.html) | 从寄存器语义推进到初始化与引脚行为。 |
| 第五篇 | 19 · [定时器与中断系统](interrupts.html) | 建立计时、使能、服务、清源与返回闭环。 |
| 第五篇 | 20 · [I2C 与 EEPROM](i2c.html) | 从线路、FIFO 和控制寄存器到器件读取。 |
| 第五篇 | 21 · [SPI、NOR 与 SD](spi.html) | 把控制器事务和外部设备协议分开。 |
| 第五篇 | 22 · [iDMA、流量管理与总线错误](dma.html) | 理解搬运提交、完成、限流与故障门槛。 |
| 第五篇 | 23 · [Serial Link、VGA 与 USB](stream-io.html) | 按设备追踪控制、数据、时钟及验证条件。 |
| 第六篇 | 24 · [Ara 结构与 CVA6 协处理器接口](ara.html) | 分清请求、应答、CPU 提交和实际完成。 |
| 第六篇 | 25 · [RVV 编程与结果验证](vector.html) | 用同一数组比较汇编、intrinsics 和自动向量化。 |
| 第六篇 | 26 · [CPU、Ara、DMA 与 NPU 的共享数据](sharing.html) | 建立可见性、所有权和有界恢复协议。 |
| 第七篇 | 27 · [自定义 IP 的控制、数据和中断接入](integration.html) | 从独立 Reg 单元逐步进入系统。 |
| 第七篇 | 28 · [LVDS、ISP、NPU 与外部 DDR 集成](accelerators.html) | 逐 IP 明确接口、缓冲、跨域和验收交付。 |
| 第七篇 | 29 · [模型任务划分与容量带宽预算](models.html) | 用透明假设衡量 Ara/NPU 协作成本。 |
| 第七篇 | 30 · [固定配置工程与 ASIC 集成验收](future.html) | 冻结可搬迁输入并形成分阶段实现证据。 |

首次运行程序走[首页短路线](index.html#route)：架构/配置/地址 → C 运行模型 → ELF → 实验 A → ROM/JTAG → 仿真与实验 B。其余硬件设计章节按需要查阅；每个正文页列具体前置章节。

## 内容和旧链接如何保留

原 20 个内容页中的 148 个 H2 均有归属记录。正文按职责移动，节号重新生成但语义锚点保留。原架构页的 ASIC 时钟/复位/电源混合节拆至 04/05/06，旧组合锚点指向 06 并链接相关两章。原介绍性目标段改写为新职责和前置；来源集中整理，旧源码链接仍可从相应章节访问。

[迁移清单](scripts/anchor_migrations.json)记录 373 条旧页/锚点到正文的映射。例如：

| 旧链接 | 当前位置 |
| --- | --- |
| `configuration.html#isa` | [02 指令能力](cva6.html#isa) |
| `interconnect.html#address-map` | [07 地址图](address-map.html#address-map) |
| `memory.html#ddr-subsystem` | [12 DDR](ddr.html#ddr-subsystem) |
| `memory.html#dma` | [22 iDMA](dma.html#dma) |
| `vector.html#interface` | [24 协处理器接口](ara.html#interface) |
| `vector.html#model-case` | [29 模型案例](models.html#model-case) |
| `future.html#calculator` | [29 容量计算器](models.html#calculator) |

保留的旧页面遇到已移走的 hash 会跳到新节；禁用 JavaScript 则在原锚点显示明确链接。更早的 20 个旧页继续保留兼容入口。生成器验证目的锚点必须存在于当前正文，禁止转到另一个迁移占位符；浏览器逐条验证跨页迁移。

## 验证和边界

[结构校验](evidence/structure-20260929-checks.txt)检查导航层次、标题、页内目录、上下章、链接/锚点、生成一致性、原内容归属与历史保护。[内容比对](evidence/structure-20260929-content-audit.json)逐块比对旧正文并列出有意改写；首页/参考页按专项规则检查。[浏览器记录](evidence/structure-20260929-browser.txt)覆盖桌面/手机、禁用脚本、目录展开、迁移、寄存器搜索、计算器和修订图的边界。

旧站 728 文件、此前 evidence、独立示例均保留原内容。没有重新构建软件、运行生产 RTL、板测或性能测量。源码核对不能替代执行；ASIC 电源域、PLL、DDR 寄存器与 NPU 接口仍是待实现/待交付方案。官方资料继续沿用[此前已记录的版本和查阅日期](OFFICIAL_SOURCES.md)，本次未重新核验上游网页。
