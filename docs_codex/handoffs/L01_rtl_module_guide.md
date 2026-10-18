# L01 / RTL 模块图文指南交接

## 当前结论与未关闭事项

2026-10-13 最终选择已完成：正式指南为 **21 篇正文、24 张 A 连续走线图、213 条连接**。B 已弃用，C 未采用；下文“待评价”“B 保留比较”“等待反馈”等属于相应阶段的历史描述，均由最终 A 决定替代。当前维护只使用 [A 图源入口](../diagrams/2026-10-13_rtl_module_comparison/README.md)，试绘及原脚本的恢复见[整理归档](../maintenance/L01/archive/documentation_organization/README.md)。

技术输入仍为各节所列版本。Platform ROM 返回、ROM C 栈对齐、iDMA 位宽/错误处理、CLINT HAL、I²C 分块/STOP 等静态发现未关闭；图稿检查不替代 S01/V01 动态验证。原日期、角色、命令和验证结果保留下文。

## 修改记录

| 日期 | 对话/角色 | 输入版本 | 修改与验证摘要 |
|---|---|---|---|
| 2026-10-13 | L01 文档整理，root；未委派子 Agent | `5a1338e0a0bf115ddd54c19e0ae367ac2d541892` / `mp/ara-pulp-v2` | 正式导航与检查独立于 B/C；试绘集中归档；正文仅改图览链接和查线句，技术内容/图像未变。详细数量、备份及检查见[组织交接](L01_documentation_organization.md) |
| 2026-10-12 | L01 图文作者，root Agent | `c4162204cfee0c48b81158b4296860a678d92bec` / `mp/ara-pulp-v2` | 新建 17 章指南；18 张新图加既有 Regbus 两图；20 页原生 PPT 与逐图 PDF/PNG；源码定位和图稿检查通过 |
| 2026-10-13 | L01 主管及三组并行审阅 | `c4162204cfee0c48b81158b4296860a678d92bec` / `mp/ara-pulp-v2` | 原17章全审修复，新增4章；24组A/B共48图，213条连接说明；渲染/链接/图源/PDF/PPT检查通过 |

## 2026-10-12 基本信息（历史）

- 用户授权：批量生成指定外设/中断/LLC 的 RTL 模块图及详细解读，统一收录先前 Regbus 内容；本轮用户明确选择“统一入口 + 每模块一篇 Markdown”。
- 状态：文档/图稿交付完成，等待用户阅读反馈；硬件功能验证不在本轮授权工作中。
- 输入工作区已有多份共享文档修改、旧图目录迁移的删除/未跟踪状态及前轮 Regbus 图稿。全部保留；没有覆盖旧图、切分支、升级依赖或修改生产代码。
- 负责路径：`docs_codex/rtl_modules/`、`docs_codex/diagrams/2026-10-12_rtl_modules/`、`docs_codex/maintenance/L01/planning/rtl_module_figures.md`、本文件。
- 使用 publication-figures；没有子 Agent，没有创建/修改 skill。共享任务表/状态文档已有其他修改，本轮只交付独立交接，待协调者合并入口。

## 2026-10-12 交付（历史记录）

- [统一入口](../rtl_modules/README.md)：Regbus、UART、I²C、SPI、GPIO、PLIC、CLINT/CLIC、IRQ Router、BootROM、SoC Regs、JTAG、Serial Link、VGA、USB、iDMA、中断异常、LLC/SPM，共 17 章。
- [图稿/复现入口](../diagrams/2026-10-12_rtl_modules/README.md)、[20 页原生 PPTX](../diagrams/2026-10-12_rtl_modules/export/diagrams.pptx)。每章一至两图，章节按图中编号解释实际电路，附软件访问、时钟/复位、中断、扩展与复用边界。
- [绘图约定/扩充 Prompt](../maintenance/L01/planning/rtl_module_figures.md)明确不重复 SoC 全景、不逐 FIFO 拆页、使用真实模块名、保留当前缺口与验证等级。
- [源码清单](../diagrams/2026-10-12_rtl_modules/source_manifest.json)：57 个文件 SHA-256，111 个可搜索的文件/行号/符号锚点。生成脚本可刷新表格，刷新哈希不能替代技术复核。

## 新结论及保留问题

本轮以当前源码确认 UART 内部 Reg→APB、USB 内部 Reg→AXI、iDMA 独立 AXI 控制窗口下仍有 Reg、Router mask 默认仅发 PLIC、CLINT RTC 沿用于同域计数使能。详细解释保存在正式章节，本交接不重复正文。

- 既有 iDMA 控制位宽缺口保留：wrapper 内部 Reg DW 跟系统位宽，2D 生成 reg_top DW32；没有完成 IRQ 端口，ErrorCap=NO_ERROR_HANDLING。图不作为可运行证明。
- 当前 LLC 配置 wrapper 用 Regbus，旧依赖文档 AXI-Lite 描述已过时；`axi_llc_events_o` 在 SoC 未接，未宣称完整软件性能计数器已落地。
- **S01 待核查的静态发现**：`sw/lib/dif/clint.c:55` 的 `clint_sleep_until()` 在 `current < target` 时早退，与等待未来目标的预期不符；`:14` 的 MTIME 高/低读没有高—低—高重试，不能当作原子快照；比较寄存器分拆写也需审查暂态。依据及使用边界见 [06 章](../rtl_modules/06_clint_clic.md)。未修改软件，未声称已复现硬件失败，未自行新建修复任务编号。
- 既有 Platform ROM 返回问题、USB/VGA 错误处理待办、JTAG ndmreset 未接等继续保留，不由图稿关闭。

## 改动与接口

- 所有新增均在上述文档/图稿/独立交接路径；生产 RTL、软件、配置、地址、中断编号和依赖版本变化：无。
- 当前图源 SVG、layout JSON、生成脚本；export 中有 PNG/灰度 PNG、可编辑 SVG、矢量 PDF 和一份 PPTX。Regbus 两个 SVG 引用前轮目录，因此单独搬迁本目录时需一并保留该相邻目录，或导出独立最终产物。
- 文档源链接相对仓库根，需要完整工作区才能跳转。未提交 Git commit。

## 验证证据

工作目录：仓库根。命令及工具入口见图稿 README；以下最终运行均退出 0：

1. `python3 .../build_figures.py`：生成 18 张新 SVG。
2. `python3 .../build_sources.py`：17 章、111 锚点、57 源文件。
3. publication-figures venv `verify_figures.py --source-only`：源码锚点/哈希、文档链接、字体度量/走线穿字检查通过。
4. `python3 .../export_figures.py`：20 页，1239 个原生对象、624 个文本对象；最小有效字号约 9.70 pt。20 份 PDF 均无栅格图片，所用字体嵌入检查通过。
5. venv `verify_figures.py`：[validation.json](../diagrams/2026-10-12_rtl_modules/validation.json)，新图 18、导出 20，源码/链接/文字保留/无 PPT 媒体图片检查通过；`git diff --stat -- hw .bender sw` 无输出。

[visual_review.json](../diagrams/2026-10-12_rtl_modules/visual_review.json)记录逐张最终 PNG 查看、灰度抽查和输入 SVG 哈希匹配。发现并在最终导出前修正了文字穿线、GPIO 内部信号名、SPM 别名和 LLC 性能计数描述。初次脚本发现的源路径/搜索锚点和生成前暂缺链接已修正；没有掩盖未通过的硬件测试。

未编译、未仿真、未板测、未签核；Office 外观/编辑未实测，PPT 字体不嵌入，连线端点不自动绑定模块。自动几何检查和作者查看不构成真人试读验收。

## 下一步与协调

1. 用户从统一入口选一章评审展开深度与解释方式，再决定是否调整或封装 skill；本次不要求额外批准即可阅读现成产物。
2. 若改图，用生成脚本并导出到新目录后复核，保护前轮材料；若只改解释，保留源码证据和版本。
3. C00 需要时在 L01 任务索引加本指南/交接入口，并把 CLINT 软件静态发现交给 S01 核查。该交接不自动授权 RTL/软件修复或工程迁移。

最少阅读：统一入口、对应模块章、本交接；深入才打开该章源码表中的文件。


## 2026-10-13 用户反馈后的完整修订

本节是当前结果；上文2026-10-12的文件数、图风格和“无子Agent”是当日事实，不代表本轮。用户授权的范围仍是文档、图源、图片与脚本；未修改生产 RTL/sw、地址配置或依赖。工作前对未提交的原指南/脚本/交接做了[可恢复备份](../diagrams/2026-10-13_rtl_module_comparison/evidence/before_docs_and_sources.tar.gz)，旧日期图稿原样保留。

### 当前交付

- [文档统一入口](../rtl_modules/README.md)：原17章全部复核修复，新增17–20四章，共21章。
- [A/B对比页](../diagrams/2026-10-13_rtl_module_comparison/index.html)：24组/48图、213条连接。A连续走线，B采用industrial-svg-pptx的配对端口，技术清单共用；用户随后明确选择A连续走线；文档和后续修订沿用A，B保留作比较参考。
- [图源/复现入口](../diagrams/2026-10-13_rtl_module_comparison/README.md)：SVG/PNG/矢量PDF与两份24页原生PPTX；本轮没有封装skill。
- [全章审阅覆盖](../diagrams/2026-10-13_rtl_module_comparison/review_coverage.json)：三组并行审查分工00–07、08–16、17–20；主管实施图源、连线表、统一入口与最终核对。各组视觉检查保留首次发现、修正和最终哈希。

### 关键修正和集成发现

正文修正CLIC reg_adapter在寄存器字段侧、CLINT寄存器字段与独立实例的区别、UART/SPI/GPIO遗漏支路、iDMA二维midend完成、LLC独立W/R/B数据支路，以及CVA6并行中断/异常控制。连接表解释每条线，不把AXI双箭头理解成每根信号双向。

新增四章覆盖外部主从口/ID/适配/BusErr覆盖、寄存器跨域/复位/Platform ROM启动、LVDS/ISP/帧DMA和GB搬运、CPU/Ara/PMA/缓存和所有权。已有AXI扩展口访问LLC目标仍走LLC；新DDR旁路不是配置端口数即可获得。当前向量profile的L1D为WT，但在途写、LLC副本和所有权仍须处理；Ara失效过滤器不覆盖新旁路master。FPGA MIG校准完成输出悬空，不能描述成统一DDR ready闭环。

原S01-B01、iDMA位宽/错误处理及CLINT HAL问题未关闭。新增静态疑点已放[02章](../rtl_modules/02_i2c.md)：EEPROM写分块的half_fill与buf/addr推进、末字节STOP注释与实际枚举不一致，需S01/V01定向复核；本轮未修改或动态复现。默认trap_vector自旋、LLC COMMIT接受不等于flush完成、scratch启动用途等使用边界也已补入。

### 验证与未决项

最终 [validation.json](../diagrams/2026-10-13_rtl_module_comparison/validation.json)：21章、24组、213条连接；48张最终PNG逐张实看并按SHA匹配；48份PDF无栅格图片且字体嵌入；A/B各24页PPT，分别1548/2156个原生对象，文本保留与无整图媒体检查通过。源码/图片/导航链接、行号范围、渲染哈希和走线穿字检查通过。命令入口见图稿README；没有运行旧学习站生成器，这批是独立Markdown正文。

Microsoft Office显示/编辑未实测，浏览器交互未执行端到端测试；比较页已做本地链接/图像引用检查。未编译RTL、未运行功能仿真、未板测。`git diff --stat -- hw sw .bender target` 无输出；共享状态文件已有其他修改，本轮由主题交接提供更新，不覆盖共享状态。

仍需最终IP/平台资料确定DDR AXI端口/ID/在途与训练ready、LVDS格式/背压、GB容量/bank/端口、PLL时钟复位域、寄存器窗口和IRQ分配、DMA共享区及缓存维护契约。这些分别影响适配器、FIFO与吞吐预算、启动顺序和软件可见性，未由示意图冻结。用户已选择A连续走线；后续图文修订按A推进，真实IP接入仍按独立集成任务的授权和输入实施。


## 2026-10-13 表达方式确认

用户明确反馈“更喜欢A连续走线”。已将该系列默认方式写入AGENTS、指南入口、绘图约定和对比页及其生成源；后续主图使用连续连接，并保留信号说明/编号表。B版及两版图源、图片、PPT均保留，本次未重新绘图、修改技术正文或封装skill。

输入仍为 `c4162204cfee0c48b81158b4296860a678d92bec`；本次仅更新上述选择状态。修改前文本已存入日期图稿目录 `evidence/before_style_selection.tar.gz`。未改变此前硬件验证边界。


## 2026-10-13 C 版试绘与 B 版弃用（选择结果见下节）

本节取代上文“B 保留作比较参考”的状态。用户明确否定离散模块通过文字名/配对端口表达连接，并要求尝试 `svg-pptx-diagrams-native`。所有后续试绘必须使用可追踪的连续连线/箭头，E 编号只辅助查信号表。A 仍为正文默认，C 待用户评价；B 仅保留历史资产，不再作为候选、模板或生成目标。

输入提交仍为 `c4162204cfee0c48b81158b4296860a678d92bec` / `mp/ara-pulp-v2`。本轮未委派子 Agent，未改 RTL、软件、配置或依赖。修改范围：AGENTS 的本系列偏好条款、21 章的对比链接/查线说明、指南入口、L01 绘图约定、本交接，以及新旧日期图稿目录的导航/生成脚本。共享 PROJECT_STATE / AGENT_TASKS 的已有改动未覆盖。

交付 [A/C 对比页](../diagrams/backup_no_use/2026-10-13_rtl_modules_native_c/index.html) 和 [图源/复现说明](../diagrams/backup_no_use/2026-10-13_rtl_modules_native_c/README.md)：24 张 C SVG/PNG/矢量 PDF、一份 24 页原生 PPTX；C 使用彩色标题带、浅色主体、柔和边框，复用 A 的全部布局和 213 条连续连接。以前 A/B 已使用 native 导出后端；本次使用其绘图约定改变外观，不宣称新的后端或 RTL 拓扑。没有修改或封装 skill。

旧 B 生成函数显式拒绝调用，旧批量生成/渲染/导出默认只处理 A；旧对比页改为 A/C 导航页，B 图片/PDF/PPT 原样留档。原 A/B validation 和审阅哈希属于当时快照，当前导航检查使用 C 目录的脚本，未通过刷新旧哈希掩盖正文变化。本轮正文相对于备份仅允许对比链接和 B 查线句替换，已自动检查。

验证命令：publication-figures 已有 venv 执行 `build_native_c.py`、`verify_native_c.py`；native skill `scripts/run.py --input …/C/*.svg --out-dir …/C/editable --aspect source`。24 PNG 均实际用 view_image 查看并保存哈希；检查 213 条线、78 个源码/本地资料哈希、21 章导航、24 个矢量 PDF 字体嵌入和 24 页 PPT（1708 原生对象、无整图图片）。最终结果见 [validation.json](../diagrams/backup_no_use/2026-10-13_rtl_modules_native_c/validation.json)。首轮检查时验证报告尚未生成导致其自身链接暂缺，生成后复查关闭。

Office 显示/编辑、浏览器交互未实测；未运行 RTL 编译、仿真或板测。后续由用户评价 A/C 的视觉偏好；无论选择何种配色，连续连线要求不再作为待决项。所有修改前文档和脚本保存于新图稿 `evidence/before_c_style.tar.gz`。


## 2026-10-13 比较 C 后确认采用 A（最新决定）

用户明确回复“还是用A吧”。本节关闭上文 C 待评价状态：A 为 RTL 模块指南正式采用版本，后续补图和修订沿用 A 的连续走线；C 仅保留试绘记录，B 继续弃用。已同步 AGENTS、指南入口、A/C 图稿说明与比较页生成源、L01 绘图约定。没有重新生成图片、替换正文插图、修改技术内容或封装 skill。

输入仍为 `c4162204cfee0c48b81158b4296860a678d92bec`；修改前文本保存在 C 图稿目录 `evidence/before_final_a_selection.tar.gz`。仅重生成比较页的选择状态，执行 `verify_native_c.py` 检查导航、图源哈希及原生导出一致性；不新增硬件或 Office 验证结论。共享状态文件未覆盖。
