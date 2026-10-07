# L01 / 配置覆盖、教学深度与官方资料融入评审

## 基本信息

- 日期：2026-10-07；任务 L01，评审者。
- 最终授权范围：复审三项收尾，确认 CVA6 / Cheshire / 软件栈的配置教学缺口，比较用户提供的四份讲解，向另一个实施 Agent 提出修改要求。附加要求为将官方资料细化融入 HTML 和 Markdown；本对话不实施教材修改。
- 状态：评审及修改要求完成；教学扩充待实施。
- 输入：`mp/ara-pulp-v2`，HEAD `5ddec4fb4e982b460b12c3f3587523807602d5d4`。
- 输入工作区已有 AGENTS.md、PROJECT_STATE.md、AGENT_TASKS.md、handoffs/README.md 修改，以及 10 月 6 日独立交接、平台约定、diagrams/、tools/ 等未跟踪内容。全部保留。
- 负责文件：仅本独立评审交接。共享索引已有其他工作修改，交 C00 串行合并。
- 范围纠正：曾误把用户附加条目理解为实施授权，短暂编辑五个 `learning/content/*.html`。收到纠正后仅撤回本轮这五个文件的改动；逐文件 SHA-256 已与输入快照核对一致。未生成新网页或图片，最终网站与参考手册保持输入状态。

## 本轮结果

### 1. 三项定向收尾复审

三项已落实，不重复要求修改：

1. `content/boot.html:7,23,25,28` 明确 SD/NOR 调用采用 mtime 绝对阈值，并区分 `clint_spin_until` 与相对等待；对照 `hw/bootrom/cheshire_bootrom.c::boot_spi_sdcard/boot_spi_s25fs512s` 和 CLINT 实现确认。
2. `content/clocks.html:19` 区分 C1 支路分频与共享 M/N、参考源重配，保留具体 IP 独立调整能力的前提。该表是教学/未来实现要求，不是 ASIC PLL 已实现证据。
3. `scripts/report_run.py` 记录 54 个 HTML 的 `tested_html` 哈希；`preview_structure_site.py:146` 结束时核对文件集合和哈希。本轮执行成功。

网站结构与离线显示可用。当前主要问题已转为“是否能帮助读者独立解释、选择和推演”，而非页面数、目录层次或资源链接。

### 2. 配置覆盖确认

| 对象 | 已有内容 | 仍缺少的教学层 |
| --- | --- | --- |
| CVA6 | `configuration/CVA6.md` 列出全部 88 个本地用户配置字段；对照标量/向量 profile，标出 SoC 覆盖。网页 cva6 讲两组 profile、资源与功能 | 按能力分类的可选项、profile 家族及适用范围；枚举与约束；从需求选配置并追踪最终有效值的完整实例 |
| Cheshire | `configuration/CHESHIRE.md` 列出全部 113 个字段；RECIPES 有组合、修改与已知缺口。网页配置章列六个关键 SoC/Ara 字段和六类用途 | 全部参数族的导航；结构合法、系统依赖、软件匹配与动态验证的分层；每类用途可独立使用的完整组合记录 |
| 软件栈 | `software/BUILD_AND_SDK.md` 已列 flags、Make 变量、SDK、镜像入口。网页 build 主要围绕教材隔离构建 | 裸机与 Linux 栈的职责总览；库/运行时/驱动/加载器关系；工具链、ISA/ABI、链接、启动状态和镜像选择之间的决策链 |

本轮用标准库解析 `cheshire_cfg_t`、`cva6_user_cfg_t` 的字段名，并与相应 Markdown 第一列比对：113/88，缺失集合均为空。这证明**字段名覆盖**，不证明每行语义、任意取值或组合已经验证。

本地 CVA6 `core/include` 下有 20 个 `cv*_config_pkg*.sv` 文件，包括 deprecated、RV32 和其他平台变体。当前网页只着重讲实际相关的两个 profile 是合理取舍，但应提供其余类别的适用范围，让读者知道选择边界；不能把这 20 个文件列为当前 Cheshire 的 20 套受支持配置。

### 3. 按优先级的修改意见

#### P1：Platform ROM 的现状未进入网页

- 位置：`learning/content/boot.html:3` 仅写“平台 ROM 若被配置，则按源码约定调用”；clocks 章也未连接最新平台决策。
- 影响：读者无法解释入口如何传入、谁执行平台程序、需要什么初始资源，以及为何当前普通返回路径不能直接使用。
- 依据：`hw/bootrom/cheshire_bootrom.S:80` 的 `jalr t0` 后紧跟 `boot_next_stage`；`_boot` 位于其后。10 月 6 日已记录现有 ROM 指令同样受影响，登记 S01-B01。上游修复 `9b4c222df72f74f90ab9f36d80ba7b527f92e62b`（#187）存在，本地未应用。
- 要求：讲清 `Bootrom=1/PlatformRom=0`、内置 ROM 调非零平台入口、`Bootrom=0` 直接复位到平台入口三类关系。默认入口为 0 与缺陷触发条件分别说明。将用户已确认的安全启动 PLL / 运行软件保留配置能力融入正文。
- 验收：读者可画出官方意图与本地缺陷位置；实施 Agent 只同步教学边界，修源码仍属独立 S01-B01。

#### P1：配置表提供了数据，但尚不足以指导选择

- 位置：`content/cva6.html` 的 profile 段和资源表；`content/configuration.html:13–18,29–33`。
- 具体缺口：配置章六类用途表将 AXI RT / CLIC / Router 合在一行，其生成规模、CPU、软件入口不同；表中“候选合法”未逐行给出确认过的约束和未确认条件。
- 要求：建立三层阅读结构——按需求选择的解释正文、具体组合推演、完整参数参考；无需在主文中重复 88+113 行。
- 字段记录至少包括：精确名称、概念/单位、类型与已知允许范围、当前值、上游原值/SoC 覆盖/派生、消费者、联动、验证状态。类型可表示的范围与模块支持的范围应分开。
- 组合记录至少包括：用途、唯一 CPU profile、宏/decoder、SoC 字段差异、生成 IP 规模、启动/内存/加载方式、工具链/ISA/ABI/crt0、已知阻塞及最小验证。
- 覆盖路线：标量 SPM；Ara 整数/浮点；DRAM；AXI RT；CLIC/Router；保留/旁路/关闭 LLC；保留或关闭启动外设；Platform ROM；Linux 前置条件。后四项可以作为条件与依赖推演，不要求实现或运行。
- 不声称穷举所有合法组合。区分“值能表示 → 满足已查明结构约束 → 系统依赖闭合 → 软件匹配 → 已执行验证”；SoC 末尾仍有多项合法性检查 TODO。

#### P1：软件栈和启动概念的基础解释仍有断层

- 位置：`content/runtime.html`、`build.html`、`boot.html`；详表散落在软件 Markdown。
- 已有优点：runtime 已用 seed/result/greeting 解释对象、BSS、栈和输入节到输出节的合并；build 已讲重定位、ELF、装载段。这些不应在下一轮重做或删除。
- 缺口：网页没有连续解释 libcheshire/HAL/DIF、ZSL、OpenSBI、U-Boot、DTB/rootfs 的职责与关系；Boot 章以 BIST/CFG_SPM/way/sp 等细节开篇，先给实现步骤，再补对象定义，初学者负担较重。
- 要求：先区分程序、库、固件、介质、运行存储；再分“构建依赖”“启动控制交接”“运行时调用”三种关系。用 NOR→SPM 和主机 ELF→RAM 两条具体轨迹解释 PC 所在位置、代码搬运者及入口。
- Linux 部分应解释各层职责和数据位置，暂不扩成整套操作系统移植教程。当前 `sw/boot/zsl.c` 在调用固件前已向 DRAM 加载 DTB/firmware；未来 DDR 初始化须在首次访问前完成。

#### P2：配置接口与初始化策略之间缺少完整因果链

- 位置：`content/clocks.html` 与 boot、DDR 章之间。
- 要求：按照“上电安全硬件状态 → CPU 可执行 → 平台程序设安全工作点 → 介质可读 → 可更新固件读/校验配置 → 运行软件受控调整”解释。
- 区分：ROM 中的算法是否可更新；算法读取的数据是否可更新；IP 是否支持重新配置；控制通路在目标时钟停止时是否仍可用。
- 保留 10 月 6 日决策，不把多 PLL、独立 CPU/Ara/NPU 域、具体频率、电压、cpufreq 当成用户冻结方案。外部配置格式和供应商 PLL/PHY 合法参数仍待资料。

#### P2：精确名称与教学语气的小范围修订

- 网页 cva6/configuration 使用了 `DcacheType`，本地用户配置字段实际为 `DCacheType`；profile 辅助常量另有 `CVA6ConfigDcacheType`。应按对象区分，便于源码搜索。
- boot 章仍有“本节不授权写卡”等对 Agent 的实施边界；建议放入维护/实验范围说明，面向读者的正文集中讲机制和操作条件。
- 证据边界保留在具体结论旁或统一提示框，不在每个解释段反复插入“不能/不代表/不自动”。必要否定句应带原因与可行路径。
- 主线关键解释应在 HTML 正文自足；Markdown 参数字典用于查询。浏览器可打开一个 `.md` 文件不等于它已成为格式清晰的网页教学环节。

## 四份附件的借鉴与版本审查

已读取用户四份附件。可借鉴的是：先建立对象区别、每次引入少量概念、通过具体程序串联调用/加载/取指、解释设计原因、用图分离存储位置与执行顺序。应保留教材陈述性标题，不照搬聊天式反问、重复结论或大量极短段落。

不可直接搬运的内容：

1. 第一份附件使用新版 `hw/cheshire.rdl → PeakRDL` 和结构体式寄存器 API；本地 `sw/sw.mk:69–84` 使用 HJSON 和 `REGTOOL --cdefines`。当前 UART 示例也必须使用本地偏移及 `reg8` 语义，不能把假设的 CTRL/STATUS/TX 表作为真实寄存器图。
2. 附件中有将 ZSL 与“初始化 DDR”连在一起的概念图；本地 zsl.c 负责装载，没有未来外购 DDR/PLL 初始化实现。DRAM 在载入 DTB 和 firmware 前须可访问。
3. Platform ROM 的正常返回属于官方设计意图；本地缺陷另述，不能直接用箭头写成现已可用。
4. 频率、电压、PLL 数量和独立域是讨论示例。动态配置能力取决于真实 IP 和安全控制路径，不能因存在 C 函数概念图就宣称已有实现。

## 官方资料的融入安排

不是在章末增加链接清单，也不是翻译整本上游手册。应将相关官方内容按本教材的学习依赖拆分，在正文解释概念，再用本地实例和源码检验适用范围。

| 官方主题 | HTML 主要落点 | Markdown 承载 | 必须说明的边界 |
| --- | --- | --- | --- |
| CVA6 Introduction、Parameters and Configuration | cva6、configuration | configuration/CVA6.md、RECIPES.md | 官方配置族、当前目录中的文件、Cheshire 实际选源是三个集合；枚举存在不等于集成已验证 |
| CVA6 Programmer View、PMA/PMP、CSR | cva6、address-map、interrupts | CVA6.md 与相关软件小节 | MMU/PMP/PMA 不同职责；参数硬件能力与运行 CSR 不同阶段；取值按本地覆盖后配置 |
| CVA6 CV-X-IF 与系统接口 | ara、adapters、sharing | ARA.md、CVA6.md | 本地 CvxifEn=0，Ara 走专用接口；不把通用 CV-X-IF 文档的限制/握手直接套用 |
| Cheshire Architecture / Components | architecture、configuration、memory、interconnect、设备章 | CHESHIRE.md、PERIPHERALS.md | 固定地址区与实际实体容量、生成端口/规则、LLC 与启动 SPM 关系；各参数族有完整入口 |
| Cheshire Instantiating / Platform ROM | configuration、boot、clocks、reset、ddr | RECIPES.md、RUNTIME_AND_DEBUG.md，链接 03 平台约定 | DefaultCfg 派生法、接口类型、启动前置条件；本地 S01-B01 与新决策 |
| Cheshire Software Stack / Baremetal | runtime、build、boot-debug | BUILD_AND_SDK.md、LIBRARIES.md | HAL/运行时/工具链，启动代码与库并入 ELF，直接装载的责任 |
| Cheshire Boot Flow / ZSL / Firmware / Linux | boot | RUNTIME_AND_DEBUG.md、BUILD_AND_SDK.md | 固定代码与可更新载荷、DTB/固件装载位置、裸机和 Linux 分支、SDK 可用范围 |

资料查阅事实：

- 本轮成功打开 [Cheshire 软件栈](https://pulp-platform.github.io/cheshire/um/sw/)、[架构](https://pulp-platform.github.io/cheshire/um/arch/)、[集成](https://pulp-platform.github.io/cheshire/tg/integr/)，并读取本地 `docs/um/sw.md` / `docs/tg/integr.md` 与消费者。
- 本轮成功打开 [CVA6 参数配置](https://cva6.readthedocs.io/en/latest/01_cva6_user/Parameters_Configuration.html)、[Introduction](https://cva6.readthedocs.io/en/latest/01_cva6_user/Introduction.html)、[PMA](https://cva6.readthedocs.io/en/latest/01_cva6_user/PMA.html)。在线 `Configuring_CVA6.html` 无可用正文，正确入口为 Parameters_Configuration；在线 PMP 页面此次失败，使用随依赖的 `docs/01_cva6_user/PMP.rst`。
- 已定向读取本地 Introduction、Parameters_Configuration、Core_Integration、Compiler_Command_Lines、PMA、PMP、CSR_Cache_Control、CVX_Interface_Coprocessor 等资料。部分章节为待补写内容，不能称其提供了具体实施流程。
- 在线 CVA6 参数表含本地用户结构体没有的 ALUBypass、BPType、BHTHist 等字段；本地 Introduction 有文档覆盖范围限制，不能用其中缓存覆盖声明否认本地 WB 实现。
- 本地 Cheshire 文档将 EEPROM boot mode 写为 0b10，当前 C switch 与在线软件文档均为 3/0b11；本地及在线被动加载说明的 scratch bit0 与实际 `boot_passive` 的掩码 2 也需分别记录。网页已有按本地表达式解释的内容，继续保留。
- `OFFICIAL_SOURCES.md` 当前保存 09-29 查阅事实，下一轮应追加 10 月 7 日来源与差异，不把旧失败/历史状态悄悄改成过去已成功查阅。

## 给实施 Agent 的具体要求

以下内容可作为下一对话任务说明，连同本记录路径交付。

> 请承担 L01 教材实施，先读根 AGENTS.md、PROJECT_STATE、相关 L01 交接及本评审。目标是补足配置选择和软件启动的解释深度，保留已有七篇组织、有效技术内容、证据、实验和旧链接。不要把任务简化为增加标题、复制参数表或补官方外链。
>
> 1. 先完成本评审三个主项：同步三项收尾的已完成状态；补全 CVA6/SoC/软件配置的选项—约束—组合—结果关系；建立软件栈与启动对象的连续讲解。附加完成官方资料按上表融入 HTML 与 Markdown。最新用户要求为评审者提出要求，实际实施需在你的对话取得明确实施任务后进行。
> 2. CVA6 主文说明能力分类、常用 profile 差异和有效值推导；参考手册补可选枚举、条件和适用范围。Cheshire 主文按参数族说明结构后果，并用具体组合演算；未知范围标待确认，不从类型位宽虚构支持矩阵。
> 3. 在运行模型前建立软件对象与职责总览；构建章解释工具链/SDK、flags/ABI/库/链接选择；启动章按对象定义、一般流程、分模式动作、平台钩子、应用或 Linux 后续交接展开。每个步骤说明 CPU 在哪里取指、谁搬运哪些字节、入口如何交接和依赖哪些资源。
> 4. 在 Boot/PLL 正文回答四个问题：ROM 固定为何有多模式；Platform ROM 与 Boot ROM/ZSL 的关系；固定代码如何读取可变配置；启动安全频率如何与运行时重配置衔接。用本地 S01-B01 和已确认决策约束示意图，不修生产启动代码。
> 5. 官方资料按主题消化，给出来源、版本/读取日期、本地符号和差异。官方未说明、文档占位、消费者未实现的部分明确留白为待设计，不用想象填成现有能力。保留版权与来源，不复制供应商受限材料。
> 6. 关键教学单元包含：具体动机 → 新概念的定义 → 因果/机制 → 一条完整推演 → 本地实现与配置 → 边界及验证。先解释后列参数；每张表前说明怎样选择，表后给一个选择或计算例。源码链接支持解释，不能替代解释。
> 7. 图按问题绘制：配置覆盖/派生图，ROM/外部介质/RAM 位置与控制交接图，安全启动与配置阶段依赖图。数据搬运和控制权转移分箭头；硬件拓扑与时间线分开。无需为每个知识点新增实验或图片，也不要只追求篇幅。
> 8. 实验保留能验证关键概念的现有闭环；普通参数检索作为阅读练习。明确预期结果和失败判据。网页/构建通过与目标运行通过分别记，不运行未经授权的大型 RTL/SDK 构建。
> 9. 维护既有 content / pages.json / 生成流程；需要时调整 H2/H3，不为扩充重写 UI 或建立新框架。先形成一个完整样章及同批章节正文，再统一生成、检查锚点/导航和浏览器。所有证据输出到新目录，保留历史哈希。
> 10. 交付时逐项回答下面的理解验收题，标出读者在正文哪里能获得答案；无法回答的地方继续补解释，不以“有标题、有链接、已过页面检查”判定教学完成。

### 理解深度的验收题

1. 不打开源码，能解释为什么切换 profile 同时改变 RVV、缓存和部分能力，以及哪些值最终又被 SoC 覆盖。
2. 能为同一数组程序选择标量 SPM 与 RVV 两组候选配置，并明确软件编译成功以后还缺什么硬件证据。
3. 能说明关掉 SPI 或 LLC 后，实例、启动路径、存储和软件调用分别如何受影响。
4. 能区分 Boot ROM 中的加载代码、NOR 中的载荷和 SPM 中运行的程序；画出加载前后 PC 与数据移动位置。
5. 能解释平台钩子由谁执行、入口来自哪里、普通返回的本地缺陷，以及启动前至少哪条时钟/取指路径已可用。
6. 能分别说明 libcheshire、crt0、HAL、ZSL、DTB、OpenSBI、U-Boot 的职责，并判断哪些是裸机应用必经阶段。
7. 能指出 ZSL 第一次使用 DRAM 的位置，据此安排 DDR 初始化；不把未来 IP 驱动当作已有 ZSL 能力。
8. 能解释 ROM 算法固定、外部配置可更新、IP 可重新配置这三种不同性质，并识别读取配置的循环依赖。

## 改动与接口

- 最终新增：本独立评审记录；未提交 Git。
- 教材正文的临时改动已撤回并与输入哈希一致；无最终 HTML/MD 教材、生成器、图片、配置/profile/宏/地址/中断/位宽变化。
- 未改 RTL、sw、依赖、filelist、旧 FPGA 工程、平台约定或其他已有未提交内容。
- 无需改变工程事实。C00 可在任务/交接索引登记本评审及后续教材实施要求；S01-B01 仍为原有未实施任务。

## 验证证据

工作目录为仓库根，输入 HEAD 如上。

1. `python3 docs_codex/learning/scripts/check_structure.py`，退出 0，输出 `/tmp/l01-checks-fbch71c8/checks.txt`：54 HTML、2711 本地链接/资源、68 SVG、510 Markdown 链接/片段、目录/标题/锚点检查通过；875 历史资产与 728 备份文件未变，17 项定向源码哈希匹配。未执行生成一致性选项。
2. `python3 docs_codex/learning/scripts/preview_structure_site.py` 首次沙箱内退出 1，Chrome 未产生 DevToolsActivePort，报告目录 `/tmp/l01-browser-yw7siotd/`；随后获工具自动批准在沙箱外运行同一只读命令，退出 0，报告 `/tmp/l01-browser-yj_14ma5/browser.txt`，Chrome `151.0.7922.108`，file:// 离线。
3. 浏览器实际检查 34 主页面桌面 1440×1100 / 手机 390×844、7 个禁脚本页面、199 个旧书签、寄存器搜索/计算器/折叠和图表；54 个被测 HTML 的集合与哈希结束时不变，无页面 HTTP(S) 请求或 JS 异常。另人工查看启动页桌面和手机菜单截图。此检查不等于逐段教学内容均完整。
4. 参数字段名比对结果为 113 / 88，缺失集合为空；目录 profile 文件数为 20。仅检查名称覆盖和存在性，未展开全部组合。
5. 临时编辑前输入快照 `/tmp/l01-depth-20261007-_tvf45kb/input.json` 记录网站/配置/软件参考、重点生产及共享文档哈希；撤回五个正文文件后，快照中全部文件逐一匹配。因网站与浏览器检查时字节相同，没有重复浏览器测试。
6. `/tmp` 日志为本机临时证据路径，本交接摘要可随仓库搬迁；若需长期保留完整截图/报告，由实施任务另存到新的证据目录，勿覆盖历史记录。

未编译软件、未 RTL 编译/仿真、未 SDK/Linux 构建、未板测、未综合、未修复 Platform ROM。网页通过不构成目标运行证据。

## 决策与下一步

1. 将本记录交给教材实施 Agent；重点先把配置选择与 Boot/Platform ROM 写成足够深入的样章，再按同一标准扩充相关章节。
2. 实施前重读平台约定与 S01-B01，保持安全启动、持续配置接口方向和现有保护边界。
3. 按主题覆盖表更新正文及现有参数/软件参考；完成后以八个理解题和真实页面检查联合验收。
4. C00 串行补本交接索引；本评审未改已处于修改状态的共享文件。
