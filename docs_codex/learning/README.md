# Cheshire / CVA6 / Ara 中文工程教材

用浏览器打开 [index.html](index.html)：**九篇、42章，另有首页及8页实验/参考，共51个主页面**。正文、导航和静态 SVG 可用 `file://` 离线阅读，无服务器或 CDN。当前篇默认展开；H2/H3 页内目录可折叠；手机可收起全书目录。关闭 JavaScript 仍能阅读并使用原生目录。

- [此前机制与维护完善](REFINEMENT.md)：重点章节、启动模式与独立证据输出。
- [此前结构修订](STRUCTURE_REVISION.md)：审查回应、当前职责、旧页迁移和内容保护。
- [实验手册](labs.html)：命令、输入、产物、结果判据和失败首查；贯穿同一个数组示例。
- [来源与验证](evidence.html#teaching-20261007)：结构检查、此前软件构建和目标环境缺口分开。
- [旧站备份](../learning_backup/index.html)：728 文件原样保留；[哈希清单](evidence/restructure-backup.json)。
- [此前深度扩充](DEPTH_EXTENSION.md)、[09-28 编排设计](CONTENT_REDESIGN.md)为历史范围说明；其中 16 章编号不再定义当前目录。[官方来源](OFFICIAL_SOURCES.md)保留原查阅日期。

## 当前维护入口

在仓库根执行；Python 仅需标准库，浏览器检查与 WaveDrom 生成还需本地 `google-chrome`。只检查现有网页时：

```bash
python3 docs_codex/learning/scripts/check_structure.py
python3 docs_codex/learning/scripts/preview_structure_site.py
```

这两个命令只读教材与历史记录，默认各创建一个随机命名的 `/tmp/l01-*` 新目录并打印路径。`run.json` 保存实际时间、HEAD、工作区状态、输入哈希和输出位置；成功或失败报告留在本次目录。需要保存证据时，以 `--out-dir 新目录路径` 指定位置，目录已存在（即使为空）也拒绝执行，不提供覆盖旧证据的选项。

需要比较生成一致性时显式执行：

```bash
python3 docs_codex/learning/scripts/check_structure.py --check-generated
```

它在临时副本运行生成器，并比较 HTML、SVG、寄存器索引；工作区不会被重新生成。仅当实际修改正文/导航后，才执行下面的**写入操作**更新网页：

```bash
python3 docs_codex/learning/scripts/build_site.py
```

正文编辑 `content/*.html`。`scripts/pages.json` 显式定义 `parts` 和 `pages`：页包含 slug、title、subtitle、kind；正文另含 part 与连续 number。目录、面包屑、节号和上下章均由同一清单生成。H2/H3 必须带唯一语义 id，章号不要写死在标题里；完整层次见生成后的页内目录。

移动旧节时更新 `scripts/anchor_migrations.json`，旧 URL 指向真实新正文锚点。跨页迁移具有脚本跳转和禁用脚本静态链接两种形式；同页别名直接落在对应内容前。`legacy_links.json` 留作历史输入，新生成器使用新迁移表。修改后同时检查目的语义和链接是否有效。

需要修改图或寄存器索引时再运行相应生成器；这些命令明确写入教材资产/内容，不是只读检查：

```bash
python3 docs_codex/learning/scripts/build_diagrams.py
python3 docs_codex/learning/scripts/build_depth_diagrams.py
python3 docs_codex/learning/scripts/build_mechanism_diagrams.py
python3 docs_codex/learning/scripts/build_waves.py
python3 docs_codex/learning/scripts/build_registers.py
```

前两个脚本分别维护 16 张原重构结构图与 13 张深度扩充结构/状态图。新增五张机制结构图由 `build_mechanism_diagrams.py` 维护。6 张时序图编辑 `assets/waves/*.json`，使用本地保留许可证的 WaveDrom 3.5.0 导出 SVG；阅读网页不用加载 WaveDrom。时序图必须标明教学示意或真实运行依据。寄存器索引仍为 12 组/429 项，各组直达关键语义与初始化节；宏不代表读写属性或实际实例数量。

`check_structure.py` 核对备份与历史证据/示例/资产哈希、当前九篇/42章、前置顺序、正文清单一致、旧锚点、章号与目标、启动目录、导航/链接；`--check-generated` 另查临时生成一致性。`preview_structure_site.py` 检查桌面/手机、无脚本、迁移与交互。过去 `structure-20260929-*`、`depth-*`、`restructure-*` 保持原样；09-29 发布证据见 `evidence/refinement-20260929/`，日后检查须使用另一个新目录。

寄存器生成器现在只更新索引，不再写固定日期来源报告；本次检查的 `run.json` 保存教材输入快照，定向 RTL/软件来源另记本次 sources.json。旧内容逐块审计仍保留在此前报告，新检查不再用旧轮次的固定段落序号约束后续教学扩充。

旧 `preview_depth_site.py`、`check_depth.py`、`preview_site.py`、`check_integrity.py`、`record_*sources.py` 属于其日期的历史流程，不作为当前入口，其中部分仍使用旧目录格式。需要重现旧版时在独立旧版本副本中执行，不能用旧记录器覆盖当前证据。更新源码后应另建日期记录，并解释漂移，不改旧哈希掩盖变化。

## 示例与验证边界

`examples/journey.c` 贯穿C运行模型、构建、启动、仿真与RVV章节；章号由pages.json确定。原 `build_journey.sh scalar spm`、`scalar dram`、`rvv spm` 保留；`JOURNEY_DEPTH=1` 启用尾部/归约输入，`rvv-intrinsics`、`rvv-auto` 比较编程入口，`INJECT_ERROR=1` 生成负例。每次输出到新的目录，已有内容拒绝覆盖。详细环境、命令和验收见实验手册，不为结构修订重复运行构建。

实验 C/D/F 继续复用此前独立示例。原 `lesson.c`、历史模型和生成器保留用于追溯。静态指令、目标执行、数值结果和性能是独立证据；本次只运行文档生成及网页检查，没有软件构建、生产 RTL 仿真或板测。

复制 `learning/` 可阅读教材；源码链接 `../../hw/...` 等需要完整仓库，备份入口需要相邻 `learning_backup/`。生产 RTL、软件、工具链及 FPGA 工程的维护不属于教材生成流程。

报告的 `run.json` 将 `inputs`（内容源、脚本、资产）与 `tested_html`（根目录主页面及兼容 HTML 的 SHA-256）分开记录。浏览器结束前检查被测 HTML 的文件集合和字节哈希未变；历史报告不回填新字段。

## 2026-10-07 官方资料与源码解读

本轮输入 HEAD 为 `5ddec4fb4e982b460b12c3f3587523807602d5d4`。以官方架构、参数、平台集成和软件栈为概念入口，逐项对照本地模块、字段和调用路径；不同版本的行为在正文及 [OFFICIAL_SOURCES.md](OFFICIAL_SOURCES.md#teaching-20261007) 中明确区分。扩充同时进入现有 HTML 正文和 configuration/software Markdown，未改变七篇/30 章或新增主页面。

维护新增正文时采用“定义职责 → 解释原因 → 推演一个过程 → 指向配置/源码 → 说明验证条件”的顺序。例子中的固定数值只在已给定配置下成立。不要把在线最新参数、候选 ASIC 频率或供应商寄存器填成现有能力。新图 `assets/teaching-*.svg` 是直接维护的结构化 SVG，文字保留为 text 元素；不由旧图生成器覆盖，也不加载 CDN。浏览器检查入口已纳入这三张图的边界检查和截图。

新增内容从 [硬件职责](architecture.html#port-roles)、[CPU 配置族](cva6.html#configuration-families)、[组合约束](configuration.html#legality-levels)、[软件分层](runtime.html#software-stack)、[Platform ROM](boot.html#platform-rom)、[ASIC 资源映射](future.html#resource-mapping)进入。原六项实验保留，不为参数阅读和概念辨析增加重复实验。

本轮证据独立写入 `evidence/teaching-20261007/`：input.json 保存修改前输入，sources.json 保存本次事实依据，检查脚本创建各自的新子目录。历史记录和生产 RTL/软件保持原样。共享状态文档在本轮开始时已有其他修改，实施交接单独提交 C00 合并。

2026-10-07 独立评审定向修正：Platform ROM 的内部 LLC/栈前提，以及 [AXI RT、CLIC、Router 独立案例](configuration.html#case-baseline)。同步现有 Markdown，检查使用 `evidence/review-fixes-20261007/` 新目录；此前 `teaching-20261007/` 报告保持历史身份。

## 2026-10-07 全部现用插图重绘

当前正文使用37张重绘结构图与6张WaveDrom教学时序图；波形按用户最新要求保留WaveDrom绘制。维护入口为 [FIGURES.md](FIGURES.md)，可从[新旧图对照页](figures/20261007/index.html)逐图审阅，或下载[原生可编辑 PPTX](figures/20261007/editable/diagrams.pptx)。旧图、旧生成输入和原路径均保留。结构图由 `build_research_figures.py` 生成；波形由既有 `build_waves.py` 调用WaveDrom 3.5.0生成，输入仍为 `assets/waves/*.json`。当前PPTX只包含37张结构图。

## 2026-10-08 教学重组与诊断入口

七篇/30个主章节保留，新增外设与Ara/RVV两个独立诊断参考页，共36个主页面。正常使用过程与诊断分别维护；旧语义锚点保留并给出诊断链接。源码事实不因迁移而关闭缺陷。新增正文、检查和输入快照见 `evidence/peripheral-20261008/`；名称沿用本轮最初任务，内含后续Ara补充范围。预览脚本增加相关桌面/手机截图，图稿及可编辑资产不变。

## 2026-10-08 系统教学与协同实施

用户明确授权三个子Agent分别实施软件、OS和ASIC正文，主管串行维护公共目录、生成页及验收。当前九篇/42主章/51主页面；完整顺序以scripts/pages.json为准。新增trap、四个OS任务、六个ASIC任务和测量章节，诊断作为独立参考。六项原实验保留，labs新增OS/ASIC/测量机制推演，不增加假装已运行的目标实验。

输入及各组来源/检查保存于新的evidence/system-implementation-20261008/，历史证据和图源保持原样。上一版七篇路线图作为首页历史对照，当前目录替代其旧章号。生产工程、依赖和示例代码只读，未在本轮构建/运行目标、移植OS或实施工艺适配。

本轮维护规则新增前置顺序和正文清单一致性；结构数量按真实课程更新，历史报告数字不回填。章号文本、首页列表、导航与生成页由主管协调；并行正文作者不得运行会覆盖公共产物的生成器。

本次目录改版后，`build_research_figures.py` 的历史路线图使用 `scripts/route_pages_20261007.json` 固定输入；该快照来自改版前目录。这样可以逐字节复现原七篇图，而不覆盖现有SVG/PPTX。当前九篇阅读路线由 `pages.json` 和首页文字导航维护。不要把该历史输入同步成当前目录；若将来重绘路线图，应另建资产并按图形维护流程交付。

## 正式标题规范（2026-10-08恢复）

延续[2026-09-23编排约定](../handoffs/2026-09-23_L01_editorial_revision.md)：**正式标题使用陈述性、名词性技术主题；问题保留在正文、自测与实验。**篇标题概括领域，章标题概括完整主题，H2/H3说明技术组成、流程、接口、条件或影响。标题应能脱离上下文独立理解，保留“候选、示例、适用条件、待验证”等必要限定；不能把方案改称实现、把静态说明改称验证通过。

不得用“为什么/怎样/什么”“先…再…”“跟读/走一遍/讲完整”等提问或授课动作充当正式标题，也不只删除问词或机械统一为“机制”。这一规范同样适用于pages.json的篇/页面标题与副标题、首页导航和诊断页。正文中的引导问题及自测details允许保留；充当导航的折叠入口须遵循正式标题规则。

修改从content和pages.json开始，保留ID、slug、文件名、章序与迁移映射；同步真实标题引用再生成。全量标题人工审阅与关键词筛查分开记录，并检查技术正文、代码、表格、图形、题目保持不变。历史报告/证据/learning_backup与SVG/PPTX不因风格修订而回写。

正式标题中的中文与英文/数字之间统一留空格，例如“RTOS 任务”“嵌入式 Linux 启动”“MBIST 与制造测试”。该排版约定不改变源码标识内部拼写，不用于批量清理正文引导语、自测问句或“主动让出”等技术用语。标题补足对象或用中文展开缩写时，正文仍保留准确英文与源码名称。
