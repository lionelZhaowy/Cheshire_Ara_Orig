# E01 / 固定向量提取与服务器参考工程

## 修改记录

| 日期 | 角色 | 输入版本 | 修改与验证摘要 |
| --- | --- | --- | --- |
| 2026-10-19 | E01 UCLI波形调用修复 | 本地 `2f0f2d6f…`；服务器现有调试simv `d0836136…` | 修复服务器wave.tcl，改用官方原生dump；独立20μs短测和FSDB读取通过，未运行完整fmatmul或GUI。同步指南及本交接，失败日志保留，详见下节 |
| 2026-10-19 | E01 波形设置最小化 | 本地 `2f0f2d6f…`＋已有未提交文档；沿用本次服务器链接核查 | 指南第7章保留官方O2/KDB，使用`-debug_access+all`；撤下默认手动PLI链接，启动采集Tcl缩为7条命令，延后窗口按需说明。仅修改指南与本交接，未修改脚本或运行EDA |
| 2026-10-19 | E01 最新仿真检查与历史清理 | 本地 `2f0f2d6f…`＋已有未提交文档；服务器 Cheshire `e040b7bbc…` | 用户确认仿真结束后只读核对官方入口 fmatmul 成功，再按授权删除6个历史目录；394个保留文件清理前后哈希一致。主机退出状态未取得，未重跑；详见下节 |
| 2026-10-19 | E01 最小实现约定固化 | 本地 `2f0f2d6f…`＋已有未提交文档 | 按用户要求在根[AGENTS.md](../../AGENTS.md#最小实现与分步说明2026-10-19-用户确认)新增新对话约定：复用现有入口、逐项证明新增必要性、按当前步骤引入配置，避免用包装或搬移逻辑制造复杂度；只改入口说明与本交接，未操作工程或服务器 |
| 2026-10-19 | E01 按需配置再精简 | 本地 `2f0f2d6f…`＋已有未提交文档 | 第0节收敛为四项用户配置、失败停止及两个官方入口；波形移至第7章，不设开关或自动证据生成逻辑。仅修改指南与本交接，未执行服务器操作 |
| 2026-10-19 | E01 官方入口精简 | 本地 `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`＋已有未提交文档；服务器依据沿用2026-10-18核查 | 按用户确认方案撤下指南中的config/build/run/view包装层，改为官方start顶部配置及三处最小修改，仅新增wave.tcl的保存说明；本轮只修改指南与本交接，未部署或运行EDA |
| 2026-10-19 | E01 文件配置式仿真指南 | 本地`2f0f2d6f…`及已有未提交文档 | 指南第0节提供config.sh/wave.tcl及build/run/view三个脚本的完整保存内容；替换第5/7节重复长命令入口。只改指南与本交接，未在服务器部署或运行 |
| 2026-10-19 | E01 参数开放策略文档同步 | 本地 `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`＋已有未提交文档 | 按用户确认同步 02 规格、资源指南、服务器方案及本交接；固定功能组合、按构建锁定配置，基线对照后逐步开放参数。只改文档，未修改参数或执行提取/试验；检查记录见文末 |
| 2026-10-19 | E01 配置理解与文档整理 | 本地`2f0f2d6f…`；沿用2026-10-18服务器核查证据 | 扩展上手指南第4章与配置手册README/RECIPES，按来源、覆盖、消费者、影响和重做范围梳理pkg/TB/脚本；只改4份文档，未实施脚本封装或修改工程 |
| 2026-10-19 | E01 资源问答整理；独立只读复核 | 本地 `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`＋已有未提交文档；服务器版本沿用既有核查 | 新增固定向量资源专题并接入工程索引；只改正文、索引和本交接。静态复核 SRAM、寄存器/CSR、ROM 与配置约束；文档检查结果见下，未改硬件或远端工程 |
| 2026-10-18 | E01 上手指南撰写 | 本地 `2f0f2d6f…`；服务器 Cheshire `e040b7bbc…` / Ara `2895ba907…` | 按用户确认计划新增八章服务器使用指南并接入软件索引；只读核对源码、脚本和工具手册；教学构建/故障注入/波形与GUI均未实测；未改RTL或服务器 |
| 2026-10-18 | E01 主协调；硬件/VCS 与 S01/V01 只读复核 | `mp/ara-pulp-v2` / `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`，已有 7 个文档修改、2 个未跟踪文档 | 完成只读调查、分步方案；未复制工程、编译或仿真；等待第 1 步确认 |
| 2026-10-18 | E01 / S01 第 1 步实施 | 同一 HEAD；用户明确“开始第1步” | 最小工具链检查完成；SPM标量/RVV与本机DPI源编译通过，发现libgcc特定DRAM高地址重定位失败并隔离；未执行VCS或目标程序，等待第2步确认 |
| 2026-10-18 | E01 来源方案比较 | 同一HEAD；用户明确不复制本地工程，改为官方GitHub重建并先分析 | 原第2步复制方案被替代；已核对部分历史绕过/修改与官方来源候选，未下载、构建或调整服务器 |
| 2026-10-18 | E01 同版本重建澄清 | 同一HEAD；用户明确重建当初clone的ara-pulp-v2 | 确认为原 `mp/ara-pulp-v2` 历史版本在服务器重建；本地Git定位基准e040b7bbc及原依赖锁，不再评选新版本；未执行第2步 |

## 范围与状态

### 2026-10-19 UCLI波形调用修复（短测通过，完整运行待用户执行）

- 用户波形版展开/KDB成功，但`wave.tcl`第1行`call fsdbDumpfile`报`UCLI-CALL-CMD-GENERAL`，退出于0ps，未取得本轮fmatmul成功。原文档中的该调用方式已被实际失败证据否定；不把它归因于RTL，也不因已链接pli.a推断任意UCLI调用都有效。
- 核对服务器安装手册`/eda/synopsys/vcs/W-2024.09-SP1/doc/UserGuide/pdf/vcs_ucli_ug.pdf`第3章dump命令（手册页106—117），采用`dump -file ... -type FSDB`、`dump -add ... -depth 1 -fsdb_opt +struct -fid FSDB0`和`dump -disable -fid FSDB0`。保持两个本层范围、10μs采集窗口和停采后继续运行；没有增加`-P`、包装脚本或修改RTL。
- **实际修复文件：**服务器`~/CheshireAraPULP/target/sim/vcs/wave.tcl`；本地仅`software/SERVER_SIMULATION_GUIDE.md`及本交接。服务器start原已有`-debug_access+all`及`-ucli -do wave.tcl`，无需修改。guide的7.2/7.4同类旧命令及排障表同步修正；可选延后窗口使用官方`dump -enable`，本轮未实测该可选窗口。
- **短测：**在服务器`/tmp/e01-wavefix-blj40e7a/`使用现有simv绝对路径，传入BOOTMODE=0/PRELMODE=1和现有fmatmul绝对路径，运行`-ucli -do probe.tcl`；60秒墙钟上限。probe前5行与交付wave.tcl一致，仅将末尾无限时长`run`换成`run 10us`，总计20μs后退出，主机rc=0。0ps成功打开FSDB，两个层次遍历及结构体支持正常，10μs停采后继续到20μs；无UCLI错误，保留原0ps RT-NCMUCS及ELF零填充提示。短测已开始预加载，不代表完成应用。
- **真实波形检查：**生成550384 B的`wave.fsdb`；用同版Verdi自带`fsdb2vcd wave.fsdb -o wave.vcd`读取成功、rc=0，734个变量，1ps时基。`fix.clk`有4001条值记录，`fix.rst_n`在25000ps释放；10μs处停采产生X记录，后续未继续记录时钟翻转。这验证了采集、可读性和停止采集，不等同于Verdi GUI检查。
- **保护与证据：**短测前无相关工具进程，失败wave.tcl、start及完整simulate/elaborate日志备份到上述临时目录的`before_*`，短测日志`probe.log`、退出值`probe.exit`、FSDB/VCD、读取日志`fsdb_read.log`及`repair_result.json`同目录保留。修复前后比较当前vcs目录其余224项（文件哈希/权限和链接目标）一致，未覆盖正式日志、trace、simv或数据库；start通过`bash -n`。本地两文档输入备份在`/tmp/e01-ucli-fix-2aewfeeg/`，不保存供应商手册正文。
- **交付哈希：**wave.tcl SHA256=`95af50128e8b156bf0b96bd71bf54ac13475c1e4853748e31a7b747de6359804`；短测及交付时现有simv SHA256=`d083613676b800e19c814d8509455cf393d6f35f5cd8945df246d5f86090c9e3`。未重编，未完整重跑fmatmul，未启动Verdi GUI或修改共享状态，未提交Git。
- **文档检查：**指南采集代码块与服务器交付哈希一致，第7章Bash示例通过`bash -n`；相对链接、围栏及`git diff --check`通过，可执行示例中的旧call命令已全部替换。两文档增量差异存于上述本地临时目录。
- **最小下一步：**用户在服务器`target/sim/vcs`执行`bash start.cheshire_soc.sh`，结束后立即读取`echo $?`，核对本轮Passed/SUCCESS及FSDB，再用匹配的simv.daidir打开Verdi。此前普通仿真通过仍是独立证据；本节替代下方“FSDB完全待实测”及旧call采集写法，保留历史失败和未验证范围。

2026-10-19 波形设置最小化（当前波形说明）：按用户要求精简[指南第7章](../software/SERVER_SIMULATION_GUIDE.md#waves)，复用官方start，保留`-O2/-kdb`，仅调整调试访问和增加`-ucli -do wave.tcl`。已有链接证据包含Verdi `pli.a`，撤下默认`VERDI_HOME/-P`配置；实际FSDB错误发生时才定向处理。启动采集Tcl只保留输出文件、两个本层采集范围、10us窗口、停采后运行至结束及退出，移除默认START/LENGTH变量和零时长跳过逻辑；后移窗口方法留在7.2按需查阅，保留限制层次/时间与继续完成程序的要求。此记录替代此前波形方案中“必加显式PLI链接”的要求，不改普通仿真及其验证结论。本轮仅编辑指南与本交接；未新建仓库脚本、访问服务器或运行仿真/Verdi，FSDB/GUI仍待实测。

本轮文档检查：第7章Bash块及将修改应用到官方脚本所得的临时文本通过`bash -n`；相对链接、代码围栏、7条采集命令及第8章未变检查通过，`git diff --check`通过。输入文档备份和增量差异位于`/tmp/e01-minimal-wave-fr15vj9k/`。这些是语法/范围检查，不证明FSDB命令在目标环境运行成功；未提交Git。

### 2026-10-19 最新普通仿真检查与清理（已完成）

- **范围与输入：**用户明确“本次仿真已结束”后才连接 `zhaowy24@172.16.0.243`；本地 HEAD=`2f0f2d6f85979709fbc99dd4098447cb5587ce5f`，服务器 Cheshire HEAD=`e040b7bbc7851a37faff3c4657ff8d656cc6e20a`。本轮仅删除下列服务器历史目录、更新本交接及既有核查报告的最新状态提示；未修改 RTL/sw、依赖、TTY、工具或共享状态文件，未重编/重跑。
- **本次运行定位：**工作目录为 `~/CheshireAraPULP/target/sim/vcs`，入口为 `compile.cheshire_soc.sh`、`start.cheshire_soc.sh`。start 当前设置 `set -e -o pipefail`、`BINARY="../../../sw/tests/fmatmul.spm.elf"`、`BOOTMODE=0`、`PRELMODE=1`、`SELCFG=3`；相对官方版本还恢复了首行 shebang，其余执行逻辑保持。`simulate.log`实际加载上述相对路径（解析为工程内 `sw/tests/fmatmul.spm.elf`），日志内部记载 Oct 19 07:44 启动、07:51:23 结束；`elaborate.log`为 Oct 19 07:44:12。识别依据还包括脚本内容、加载记录、展开重建命令及新 simv 链接库名；不是只按文件 mtime。旧备份实际是 Oct 18 的 HelloWorld，旧04为 Oct 18 fmatmul，不能与本次混用。
- **配置核对：**生成清单及实际 `AN.DB/make.vlogan`只含 `cv64a6_imafdcv_sv39_config_pkg.sv`、Ara 路径的真实 `cva6_accel_first_pass_decoder.sv`，宏为 `ARA/NR_LANES=2/VLEN=2048`；TB配置3明确 `Ara=1/AraNrLanes=2/AraVLEN=2048`。展开日志对 TB/fixture 均记录 `SelectedCfg=3`，`simv.daidir/vcs_rebuild`与官方 start 的展开选项一致。
- **阶段结论：**本次展开日志记录增量编译2个模块、链接完成、`../simv up to date`及 KDB 成功生成；运行日志依次显示标量/向量计算、`Verifying result...`、`Passed.`、`[SLINK] SUCCESS`和正常 `$finish`（26019135000 ps）。程序报告19883内核cycles，主机CPU Time为403.900秒。两份完整trace各1316145行，未检出 `Exception`。独立的 RTL `vlogan` 编译控制台日志未取得，只能确认当前编译库支持这次成功展开/运行，不能补称完整编译日志已审查。
- **退出状态：未取得。**目录未保存本次 `exit.status`；用户只观察到终端 SUCCESS，未保留刚结束时的 `$?`。SSH/检查命令退出0不是仿真退出码，旧04的0也不能移用于本次。
- **警告与边界：**展开仍有245条 SIOB、9条 ENUMASSIGN，未全部完成语义审查；运行有1条 `axi_inval_filter.sv:85` 的0ps RT-NCMUCS。另有 ELF 的 `0x8024` 零填充提示，与 LOAD 段 `MemSiz 0x9d84 − FileSiz 0x1d60`一致，源码crt0包含BSS清零；ASLR提示属于仿真器重执行信息。所读日志未发现错误，官方tee未单独保存stderr，不能声称检查过未留存终端输出。本次未要求/生成FSDB，不据此判失败；只确认官方32×32 fmatmul单例通过，完整RVV、SPI自主启动、FS Dirty原因及ASIC就绪均未验收。

**本轮读取时的SHA256**（检查时快照，不伪称运行前自动记录）：

| 文件（相对工程根） | SHA256 |
| --- | --- |
| `target/sim/vcs/start.cheshire_soc.sh` | `1fcef44a43b7aa6950303c4f6f04701cfc994193c7603ff9cb33f13b091dc680` |
| `target/sim/vcs/compile.cheshire_soc.sh` | `4ee24c78016eaea0800c2470cab3c3b08fe928184950aeae4e2c1bf0c36f9f52` |
| `target/sim/vcs/simv` | `0f3d70968014aebecbbf4cca8bc24b7c9f403ba48aa24ec653e0bc96ae70873e` |
| `sw/tests/fmatmul.spm.elf` | `4746bc7ebd17bae54adf2732e03720e385277ba92e88690474880b91152dc626` |
| `target/sim/vcs/elaborate.log` | `823b28eea33116eab8e561fb7351f809f6a4d3d5dad46679971b7a585ba51150` |
| `target/sim/vcs/simulate.log` | `27b81885f2581a07975c165519e3c68a80d190df8afeb347385775337af2271e` |

**清理清单与保留用途：**

| 处理 | 路径（相对工程根） | 理由/用途 |
| --- | --- | --- |
| 已删除 | `_e01/rvv_fmatmul_01`、`rvv_fmatmul_02`、`rvv_fmatmul_03`、`rvv_fmatmul_04`（均在`_e01`） | 旧失败/成功运行及trace；退出状态依次124/124/124/0，输入哈希与[报告第6节](../maintenance/E01/reports/reference_rebuild_check.md#6-首次-fmatmul-运行超时诊断2026-10-18-增量)所述一致；异常、FS诊断、有效推进超时与最终通过的历史结论已保存 |
| 已删除 | `_e01/vcs_before_wave` | 旧HelloWorld构建/运行备份，非波形运行；simv为旧`540e4f91…`，标量成功已记于报告第1—2节。备份start与服务器Git HEAD原文件逐字一致，compile与当前文件一致，无独有源码修订；没有FSDB |
| 已删除 | `_e01/rebuild_20261018_082329` | 已核实为空目录 |
| 全部保留 | `target/sim/vcs/` | 两个官方入口、完整展开/运行日志、两份trace、simv、运行/调试数据库、增量编译库与内部辅助文件；不把内部`csrc/clean.sh`当教学包装脚本 |
| 保留 | `target/sim/vcs/simv.daidir`、`work.lib++`、`AN.DB`、`csrc` | `readelf -d simv`确认直接依赖`_3946352_archive_1.so`和`_prev_archive_1.so`，均位于simv.daidir；KDB有3个链接指向当前work.lib++。其余用于编译/增量重建及设计查询，未拆分删除 |
| 保留 | `_e01/preflight/`、`_e01/eeprom.zip` | 前者为工具链检查及探针输入/输出；后者含3份EEPROM模型，属于来源包，不按仿真废物删除。软件副本及crt0源码备份均未触碰 |
| 暂留 | `target/sim/vcs/csrc/_3383237_archive_1.so` | 已存在的失效旧链接，当前simv的NEEDED不引用它；尚未全面证明VCS内部增量元数据是否依赖该项，因此随csrc保留。不是本轮删除造成，当前必需的两份设计库链接有效 |

删除前再次检查相关进程和打开文件，未发现VCS/simv/Verdi或目标产物使用者；检查实际路径、设备号与所有链接，使用6个明确路径及不跟随符号链接的删除方式。旧备份中指向当前work.lib++的链接仅随备份移除，目标文件未动。未发现独立的config/build/run/view教学包装脚本，无此类额外删除。

合计删除分配空间859054080 B（约819.26 MiB，未计顶层目录自身）；清理后`_e01`只剩`preflight`和`eeprom.zip`。清理前后对当前vcs全树、preflight、模型zip、当前ELF及crt0/备份共431项进行比较，其中394个普通文件SHA256一致，其余目录/链接的类型、权限、目标及链接有效性一致；服务器Git状态也一致。此为静态完整性检查，**没有重新运行仿真或Verdi**。

本地写入前备份：`/tmp/e01-cleanup-docs-4usb8j4u/`，仅备份两份待编辑文档，不搬存服务器旧产物。下方历史记录所称“保留四次运行/下一步保留旧目录”已由本次明确清理授权替代；历史结论继续有效，原服务器目录已删除。本轮未提交Git，未代改已有并行共享状态。最小下一步仍按用户后续选择开展验证；日常继续使用现有两个官方入口。

### 此前方案与验证记录

2026-10-19 按需配置再精简（当前方案）：按用户确认的“每一步只引入当下必需内容”，[指南第0节](../software/SERVER_SIMULATION_GUIDE.md#quick-workflow)只设BINARY/BOOTMODE/PRELMODE/SELCFG，工具环境沿用重建步骤；仅加`set -e -o pipefail`，保留官方执行末尾。取消上一版重复路径/空值/默认值、WAVES和限时变量、自动哈希及状态文件生成；限时验收引用已有命令。[第7章](../software/SERVER_SIMULATION_GUIDE.md#waves)按需设置调试/FSDB选项、保存wave.tcl并为原simv增加UCLI选项，直接打开Verdi。第2/4/5/6/8章引用与检查口径同步，详细配置追踪保留。只改指南和本交接；已有服务器文件不删除、不部署，原验收与缺陷状态不变。

2026-10-19 官方入口精简（历史，已被上方按需配置方案替代）：用户确认优先复用官方脚本，参数集中写入`start.cheshire_soc.sh`顶部。[指南第0节](../software/SERVER_SIMULATION_GUIDE.md#quick-workflow)现为“备份→编辑官方start及wave.tcl→compile/start→直接Verdi”四步；启动脚本只补充配置、调试/FSDB入口及超时/失败传播，保留官方阶段和日志位置。取消指南的config.sh、build.sh、run.sh、view.sh实现与构建/运行编号、配置指纹、数据库路径管理，第5/6/7章与练习同步。保留详细配置追踪及旧失败/成功证据，日常同名产物覆盖前须归档。该方案替代下面的五文件方案；未删除用户可能已建的服务器文件，也未修改本地或服务器官方脚本。FSDB联编、采集与GUI仍待目标实测，参数逐步开放策略及原验收缺口不变。

2026-10-19 文件配置式操作入口（历史，已被上方官方入口方案替代）：用户要求先在文件中修改参数，再以简短脚本运行VCS及Verdi，避免先读大量追踪参数。[指南第0节](../software/SERVER_SIMULATION_GUIDE.md#quick-workflow)现为首读入口，脚本内容放在折叠区供首次保存；日常改config.sh的ELF/RUN_NAME及wave.tcl采集设置，执行`bash build.sh/run.sh/view.sh`。该样例限定现有配置3/UseDramSys=0和已生成向量清单；不撤销已确认的后续参数逐步开放策略，也未建立独立提取工程。各次构建/运行拒绝覆盖已有目录，run核对所列构建设置，view使用运行记录的build.path；不声称自动识别全部RTL/include变化，源码变化须新建构建。旧第5/7节重复的显式长命令已替换为统一入口，软件构建详解继续保留。仅保存文档中的脚本内容，未生成服务器脚本文件，FSDB/PLI/GUI仍待实测。

2026-10-19 参数策略确认与文档同步：用户同意固定 CVA6＋Ara 功能组合，保留集中参数入口，每次构建锁定有效配置，在原基线完成提取对照后逐步开放 L1 容量/LLC 行数，再按瓶颈评估其他参数；应用结果与一致口径的面积、时序、功耗共同决定产品配置。此决定取代初版“长期只允许一个固定参数配置”的限制，不代表具体候选值、lane 数或最终产品配置已经选定/验收。已同步 [02 规格第 3.3 节](../02_Cheshire_Ara_ASIC_Extraction_Handoff.md#parameter-policy)、[资源指南 Q7/Q8](../engineering/Fixed_Vector_SoC_Resource_Guide.md#q7)及[服务器方案](../maintenance/E01/planning/server_reference_extraction_plan.md)，配置目录统一为待实施的 `src/config/`；源码保留覆盖声明支持范围，TB/综合共用配置与 wrapper，按配置/运行保存独立证据。来源仍为同版本服务器参考 `~/CheshireAraPULP`，提取目标为 `~/CheshireAra`，旧本地复制及阶段 0 状态保留为历史。只改上述三份正文和本交接，保留并行配置导读和原始验证记录；硬件/软件/参数/共享状态均未改，未构建、仿真、综合或访问服务器。输入备份与保护哈希位于 `/tmp/e01-parameter-policy-uqiuf7qd/`，未提交 Git。

2026-10-19 配置导读整理：用户同意先理解当前配置来源/覆盖/作用，再收敛为配置文件与简短脚本。本轮仅文档实施：[上手指南第4章](../software/SERVER_SIMULATION_GUIDE.md#config)增加配置载体解释、CPU/SoC双路径图、Ara/LLC/启动/波形四例及只读判断练习；[配置流程首节](../configuration/RECIPES.md#server-config-trace)列文件地图、当前SoC/CPU关键值、TB/VIP参数与脚本/软件输入的消费者和重做范围；配置README链接并纠正“parameter都是硬件配置”等过度概括。字段全集沿用旧字典，不另建文档。旧本地清单问题及本地eew/printf默认值与服务器状态已分开；指南同步引用此前FS修正和单例成功记录，不新增运行结论。共享状态/其他主题文件不代改；config.sh/build.sh/run.sh尚未创建。

本轮依据与边界：定向阅读本地cheshire_pkg/SoC/typedef、TB/fixture/VIP、CVA6 profile/config/build_config及Ara集成入口；追踪了`Cfg.Ara→gen_ara`、`get_llc_size→i_llc`、`gen_cva6_cfg`覆盖及VIP实例绑定。SSH拟只读比较13个配置定义/消费者文件，但`ssh -o BatchMode=yes -o ConnectTimeout=10 …`在banner交换阶段超时，退出255（`Connection timed out during banner exchange`），未取得服务器文件哈希或新验证结果。表中取值标为当前源码推导，实际构建/运行仅引用2026-10-18报告，未把连接错误写成工程构建失败。文档验收记录见下方“配置导读检查”。

2026-10-19 资源问答文档：用户明确授权实施已确认整理计划，新增[固定向量 SoC 资源、存储组织与配置问答](../engineering/Fixed_Vector_SoC_Resource_Guide.md)，收录资源总览、Cache 策略、bank/word 地址、LLC 深度、TLB/预测器、宏替换、Cache/VRF 扩容和 v1 性能取舍。主要 SRAM 为 163744 B（159.90625 KiB）、48 个逻辑实例，仅含所列 Cache/VRF 数据和标签；采用实际选中的 `sram_pulp` 位宽，区分 TLB 声明/功能字段/综合网表、Boot ROM 内容/链接预算/地址窗口及未验证扩容。正文是技术说明，数值不代表综合总面积或完整 SoC 状态位数；既有服务器运行结论不扩大。本轮仅修改该正文、工程 README 和本交接，不修改共享状态、原封装预算、RTL、软件或依赖，不执行构建、仿真和服务器审计。输入备份与既有 206 个修改/未跟踪文件哈希保存在 `/tmp/e01-resource-guide-_r7jjgc6/`；最终检查见文末资源问答检查记录，未提交 Git。

2026-10-18 fmatmul通过与FS排障归档：用户完成 `_e01/rvv_fmatmul_04`，Agent只读核对Passed、SLINK SUCCESS及exit.status=0；ELF `4746bc7e…` 与03一致、simv不变。启动FS显式Clean修正已通过该32×32测试；程序报告19883内核cycles，VCS CPU Time 402.720秒。已更新[重建速查Q07](../maintenance/E01/planning/server_reference_rebuild_guide.md#q07)、[核查报告第6节](../maintenance/E01/reports/reference_rebuild_check.md)与本交接，保留四次运行及历史判断，备份位于 `/tmp/e01-fs-closure-med62rx7/`。硬件Dirty状态跟踪原因及完整参考/提取验收仍开放；本轮未远程修改或运行工程，不代改并行共享状态。

2026-10-18 第三次运行进展：用户 `_e01/rvv_fmatmul_03` 在180秒限时返回124。只读核对新ELF `4746bc7e…`、后读数FS=Clean(2)，完整trace未检出Exception，旧trap地址计数0；标量fmadd.d已执行24,413/32,768次（74.5%），完成762个输出元素，末尾索引仍推进。判定原FS关闭问题已被软件修正绕过，本次是标量参考计算尚未完成时被限时终止；向量及结果比较仍未验证。建议同一ELF/simv在新run_04目录以600秒限时重跑，不重编或改RTL。证据与范围见[核查报告第6节第三次运行](../maintenance/E01/reports/reference_rebuild_check.md)；硬件Dirty状态跟踪疑问仍开放，本轮未远程修改或执行仿真。

2026-10-18 第二次CSR诊断实证：用户运行 `_e01/rvv_fmatmul_02` 返回124。Agent只读确认新ELF哈希 `e51af8a5…` 与运行前记录一致，清位前t2=`0x0000000a00002000`、清位后t3=`0x0000000a00000000`，FS确由Initial降为Off；随后 `0x100012e8` 的c.fsdsp异常并进入原trap循环。替代此前“FS关闭待证”的状态。下一步建议在用户已改的服务器crt0中显式设置FS=Clean，重编单ELF再运行；尚未修改或验证修复，CVA6为何未置Dirty仍独立待查，见[报告第6节增量](../maintenance/E01/reports/reference_rebuild_check.md)。

2026-10-18 CSR诊断准备增量：用户自行备份服务器 `sw/lib/crt0.S.backup` 并直接修改原 `crt0.S`。Agent只读确认diff恰为原清FS低位指令前后新增 `csrr t2,mstatus`、`csrr t3,mstatus`，尚未修复FS、尚未重新构建。此用户选择替代此前“独立启动副本”的建议；本地原工程仍受保护。服务器fmatmul.c和fmatmul.o已由旧构建流程移除，ELF和测试头文件仍在，因此给出从同版本Ara恢复单个C源、沿官方参数仅重建crt0/库/fmatmul ELF及dump的命令；保留旧失败输入，未代执行构建或仿真。

2026-10-18 首次fmatmul超时：用户运行 `_e01/rvv_fmatmul_01` 返回124；Agent只读确认trace在 `0x100012e0` 的 `c.fsdsp fs0,24(sp)` 报Illegal Instruction，随后 `0x1000018c` 默认trap自循环2,238,884次，尚未执行printf或向量计算。原crt0清FS低位的写法为首要待证线索，现有trace不含mstatus读回，不能直接宣称FS=Off或硬件Dirty更新失效。最小下一步是在独立启动副本加入清位前后两次CSR读数，只重编一个诊断ELF、复用simv，由用户逐步执行；若证实FS关闭再做显式FS初始化修复。详见[核查报告第6节](../maintenance/E01/reports/reference_rebuild_check.md#6-首次-fmatmul-运行超时诊断2026-10-18-增量)。本轮仅本地报告/交接更新，无远程修改、编译或仿真；共享状态不代改。用户另要求后续围绕实际源码、ELF构建、TB输入输出及结果判定提供上手引导。

2026-10-18 上手指南交付：[正文](../software/SERVER_SIMULATION_GUIDE.md)采用用户选择的“实操与源码结合”，以VNC桌面中的Verdi为波形主线，已有重建文档继续负责安装/历史排障。修改文件仅新增正文、软件README入口及本交接；共享状态文件已有并行修改，不代为更新。服务器只读核对确认VCS/Verdi/DVE W-2024.09-SP1安装；原启动脚本未将VCSARGS追加到flags；文档因此给出独立输出目录中的显式调试流程，非已执行适配。核对fmatmul发现无符号输入减法、首元素失败后负下标打印、浮点比较及性能打印局限，已在指南说明；故障注入仅安排在教学副本索引1，不修改第三方源码。旧五步核查结论不因本轮文档交付扩大；新运行目录存在也不作为运行通过证据。下一步由用户分步执行练习，先核对原始fmatmul完整日志，再验证副本构建和有限窗口波形。文档检查见下方“上手指南检查”。

2026-10-18 五步完成核查（本地HEAD仍为`2f0f2d6f…`）：用户报告完成速查1—5步，Agent经SSH只读核对。参考根为e040b7bbc、26项依赖匹配；pip check实测通过（现有pip26.0.1）；向量profile、Ara decoder、2 lanes/VLEN2048及展开SelectedCfg=3正确。现有VCS日志确认标量HelloWorld的`[SLINK] SUCCESS`；18个Ara源的54个ELF及配套产物齐全，抽查含RVV指令。未发现向量运行日志，SPI自主启动/访存原子及独立提取未验收；展开日志245条SIOB、9条ENUMASSIGN和运行时0ps一条RT-NCMUCS需按范围审查。详见[五步核查报告](../maintenance/E01/reports/reference_rebuild_check.md)及其证据快照。本轮未构建、仿真或修改服务器；以下早期“未实施/待确认”保留为历史，不覆盖本段最新事实。

2026-10-18 用户选择版式A：重建速查现为“前半操作流程＋步骤旁问题链接，后半Q01—Q06排障索引及完整记录”，未新增排障文件。Q06补录 `-DEEW= -DPRINTF=`、预处理及连锁错误，给出 `eew=64 printf=1` 的最小命令修正和warning分类；修复后结果待确认。用户反馈第4步无新问题，尚未提供该步完整日志，不扩大为向量仿真通过。本轮仅文档重排及补录，旧稿备份 `/tmp/e01-guide-layout-5zb2j3nv/server_reference_rebuild_guide.md`；既有报错摘录保留，未操作服务器。

2026-10-18 排障说明补全：按用户要求将重建速查的 curl 7、curl 60、Bender E31/W28 及 pip 冲突补为可对应的关键原始日志、原因、处理命令和结果边界；W28附服务器已核对的include关系及清单路径。替代此前过度压缩的说明，不改变工程配置和警告处理结论，本轮仅修订文档。

2026-10-18 W28复核：用户日志显示 Flash 经单次 `curl -k` 下载后，Questa/VCS清单生成走完，剩余两项 `.svh` 未知类型警告。Agent经SSH只读确认服务器上的两份头文件、tracer include关系、VCS清单的tracer源及 `+incdir+` 均存在；判断低严重度，可暂时忽略，不修改Bender清单或源码。[速查第3节](../maintenance/E01/planning/server_reference_rebuild_guide.md#3-生成硬件和向量仿真清单)已补充依据与处理边界，替代此前E31修复结果待确认的状态；未执行RTL编译或仿真。

2026-10-18 清单生成顺序纠正：用户报告 `update_vsim_src` 在 Questa 清单生成阶段因缺少 `s25fs512s.v` 报 Bender E31。原速查将模型下载放在清单生成后，现已在第3节纠正顺序并补充文件检查；补齐模型后重试原入口，无需清理依赖。仅更新文档，未远程执行，修复后结果待确认。

2026-10-18 网络排障：用户第3节 `hw-all` 在下载 printf 子模块时超时。Agent经SSH只读确认 Mihomo HTTP端口17890、管理端口19090；显式使用代理执行 GitHub printf 的 `ls-remote HEAD` 成功、退出0。已在[速查第3节](../maintenance/E01/planning/server_reference_rebuild_guide.md#3-生成硬件和向量仿真清单)补充当前终端的代理设置与重试说明；未修改代理配置、未重跑构建，构建结果仍待用户反馈。

2026-10-18 用户手动实施增量（本地输入仍为 `2f0f2d6f…`）：用户已推进至重建速查第2节，报告 pip 20.2.4 安装后的 tclint 依赖冲突，并随后确认问题解决。[速查第2节](../maintenance/E01/planning/server_reference_rebuild_guide.md#2-准备工具环境)已记录现象、原因及启用 `--use-feature=2020-resolver` 后执行 `pip check` 的方案。未收到修复后完整输出/版本列表，Agent未远程复测；此前“重建尚未实施”仅保留为历史状态，不再代表用户当前进度，完整构建/仿真仍待验收。本轮仅更新两份E01文档，不代改共享状态。

2026-10-18 后续精简（同一输入HEAD）：用户明确“如无必要、勿增实体”。重建速查改用 Ara 官方 `update_vsim_src`，移除自定义 `run` 包装、手动依赖就绪标记和主流程中的扩展验收命令；日志/来源记录要求继续有效。VCS首次构建直接检验联编与许可，只有实际错误需隔离时再补小探针，替代旧方案中的强制前置探针。仅修改文档；上一版未提交速查备份于 `/tmp/e01-guide-before-simplify-kggmid1p/server_reference_rebuild_guide.md`。

2026-10-18 文档增量（输入仍为 `2f0f2d6f…`）：按用户要求交付[同版本重建速查](../maintenance/E01/planning/server_reference_rebuild_guide.md)，包含官方网页/固定源码依据、获取依赖、环境、硬件生成、VCS及软件/启动命令。只做来源与命令静态检查，未执行服务器重建。当前网页与旧版 Python 配方不同；原向量示例 `printf("%s", str_v)` 存在参数问题，正式RVV测试仍待准备。此前核对26个依赖HEAD均匹配原锁文件，不代表各依赖工作树无修改。共享状态不代改。

- 本轮用户最后要求：先规划，后续一步一步报告并由用户确认执行。不能按同条消息前面的连续实施授权跳过确认。
- 路径：服务器 `~/CheshireAraPULP` 为官方结构参考工程，`~/CheshireAra` 为 `cheshire_ara_asic` 提取工程；阶段0时均为空，第1步仅在前者新增 `_e01/preflight/`，后者仍为空。
- 保护：本地原 RTL/sw/FPGA、`.bender`、服务器 TTY 工程 `/home/zhaowy24/Desktop/mycheshire_24` 均未修改；`/opt`未修改。仅创建小型工具链探针与输出。
- 当前状态：参考工程已重建，标量HelloWorld及修正FS后的单个fmatmul向量运行通过；完整参考验收和固定工程提取仍未完成。原工具链S01-T01及FS Dirty状态跟踪原因未关闭。
- 最新来源决定：用户明确从GitHub重新获取当初clone的 `mp/ara-pulp-v2` 同版本，在服务器重新搭建环境和构建。按本地Git历史以 `e040b7bbc7851a37faff3c4657ff8d656cc6e20a` 及原锁文件为基准；不再重新评选官方版本。仍需核验官方可获取性，不能用当前分支尖端替代历史SHA。原快照复制方案仅留历史依据，比较与澄清见[方案第8节](../maintenance/E01/planning/server_reference_extraction_plan.md#8-官方重新获取与本地快照复现的比较来源调整)。

## 交付与证据

- [服务器参考工程使用与仿真上手指南](../software/SERVER_SIMULATION_GUIDE.md)：工程结构、配置阶段、仿真输入输出、fmatmul教学副本、有限窗口FSDB与VNC/Verdi操作；静态核对与待实测项分开记录。
- [实施方案](../maintenance/E01/planning/server_reference_extraction_plan.md)：输入版本、TTY 映射、工具链、官方入口、固定配置、测试判据、六步确认点。
- [只读检查摘要](../maintenance/E01/reports/evidence/server_readonly_2026-10-18/findings.json)与[最后一组远端只读命令](../maintenance/E01/reports/evidence/server_readonly_2026-10-18/remote_detail_check.py)、[脱敏输出](../maintenance/E01/reports/evidence/server_readonly_2026-10-18/remote_detail_check.txt)。不保存许可证环境、凭据或主机授权标识。
- 本轮新增上述 E01 文件，无 Git 提交。已有 PROJECT_STATE、AGENT_TASKS、handoffs/README 存在其他修改，本轮不代为合并。

阶段0历史结果（当时均为只读查询/源码确认；第1步实际检查增量见下）：

1. TTY 是标量 WB profile，308 个源码条目/12 个 include 均存在；配置 3 为 vCLIC，本地配置 3 为 Ara。其脚本写死另一主机路径，不能直接复制运行。
2. 服务器 RISC-V GCC 13.2.0、as/ld 2.43.1；默认 rv64gc/lp64d，单 multilib，libc/libgcc/向量头存在。首选待测，不是兼容验收通过。
3. 本机 C/C++ PATH 为 GCC/G++ 13.3.1；另有系统 GCC 8.5.0。VCS/DPI 与裸机交叉工具链独立核对。
4. `vcs -full64 -ID` 本轮退出 0，版本 `W-2024.09-SP1_Full64`；不表示许可证、编译、展开或运行通过。
5. 本地官方源码支持 VCS 入口；当前生成脚本却是标量配置并同时含 decoder stub/真实实现，须在新目录按向量入口重新受控导出。
6. 既定配置不变：`cv64a6_imafdcv_sv39` + Ara=1、2 lanes、VLEN=2048；完整 DefaultCfg、LLC/SPM/atomics/ROM/地址与外设保持。软件启动副本须在向量执行前开 VS，原 ROM 和生产源码不在本轮修改范围。
7. 当前 Ara README/RTL 走 RVV 1.0，但旧 DEPENDENCIES 提到 0.9；采用当前实现路线。默认 JTAG 流含改 dpc，另列 SPI raw 从复位启动项验收，不能用 HelloWorld/直接 ELF 加载代替。
8. 默认 Python 为 3.6.8，但已有 `/usr/bin/python3.9` 3.9.25（也有 3.11/3.12），可显式选择以满足官方 >=3.9 要求；依赖包尚未验证，无需因默认版本较旧直接升级系统。

本地文档检查：已有 9 个改动/未跟踪文档的 SHA256 与写入前一致；新增 Markdown 相对链接可解析，JSON 与证据脚本语法可读取（没有执行该脚本），方案/交接由两个只读复核角色检查。原始脱敏输出保留了行尾空格，不将日志格式告警当作功能验证失败或运行通过。

## 第 1 步实际结果

- [工具链检查报告](../maintenance/E01/reports/toolchain_preflight.md)、[原始输入及证据](../maintenance/E01/reports/evidence/preflight_2026-10-18/)；服务器证据根为 `~/CheshireAraPULP/_e01/preflight/`。
- run_001：45条命令，2项链接失败，脚本退出1；run_002：29条命令均退出0，隔离结果不关闭原失败。另有3条工具路径查询。全部串行、单条60秒超时。
- 标量/RVV 1.0探针在SPM地址实编/实链通过，实际拉入memcpy和libgcc 128-bit除法；ELF/ABI/反汇编核对通过。原版crt0汇编、SPM LTO链接通过；本机C++小程序运行通过，原样elfloader使用VCS头文件编译通过（22条告警）。
- **S01-T01未关闭**：`libgcc.a(_divdi3.o)`经`__udivmodti4`绝对引用`__clz_tab`，在`0x80000000`产生`R_RISCV_HI20`溢出；应用medany不改变已编好的库。去掉128-bit除法的libc-only隔离程序用原版链接脚本在SPM/DRAM均可链接，故不泛化为整个工具链不可用。
- 建议先用既定SPM布局验证向量与DDR模型访存；如实际DRAM驻留程序需要该库成员，再提同源同版本medany运行库的独立目录方案，未升级或修复`/opt`。
- 16个传输输入、本地取回183个产物/日志的SHA256核对通过；TTY先前抽查的7个文件hash未变。首次传输发现未来mtime，后续复制需避免make时间误判。
- 没有运行RISC-V程序、VCS或许可证检查；完整libcheshire、Boot ROM/LLC/RVV目标验收仍未完成。第1步运行的是新增探针，不是重新验证SoC。

## 按需配置再精简检查（2026-10-19）

- 只修改指南与本交接；输入HEAD为`2f0f2d6f85979709fbc99dd4098447cb5587ce5f`。第0节配置块恰好四项，波形设置只在第7章；沿用官方脚本与已配置工具环境，无新增仓库脚本或自动记录机制。
- 正文12个Bash块及从官方脚本生成的普通/波形两份临时示例均通过`bash -n`。用临时假命令检查普通运行、波形选项、展开失败停止、运行错误传播、展开日志写入失败停止，共5种场景；不调用VCS，不验证PLI、FSDB或GUI。链接/锚点、围栏、空白及`git diff --check`通过。
- 两份输入备份、增量差异、检查程序及结果在`/tmp/e01-minimal-guide-s0y0380n/`；范围外209个文件哈希不变（含本地官方启动脚本）。未修改服务器、RTL、软件、依赖或共享状态，未提交Git。此前真实运行证据保持，波形流程仍待用户目标实测。

## 官方入口精简检查（2026-10-19）

以下为上一版方案的历史检查；当前操作以按需配置再精简为准。

- 负责文件仅为`software/SERVER_SIMULATION_GUIDE.md`和本交接（相对`docs_codex/`）。对照当前本地`target/sim/vcs/start.cheshire_soc.sh`及官方`docs/tg/sim.md`，沿用2026-10-18服务器固定版本/安装路径证据；本轮没有新的服务器连接或工具核查。未将本地标量生成清单用作服务器向量输入。
- 从指南提取三段修改，应用到临时官方脚本副本：完整脚本及正文11个Bash块均通过`bash -n`。临时假命令检查8种情况：波形开启/关闭、展开失败、运行失败、展开日志写入失败、运行日志写入失败、缺少wave.tcl、无效波形开关；确认开关参数、失败停止和运行状态传播。没有调用EDA工具，假命令不验证VCS参数语义、PLI或FSDB有效性。
- 两文档相对链接/锚点、代码围栏和行尾空白检查通过，`git diff --check`通过；既有范围外209个文件的SHA256保持不变，其中包含本地原启动脚本。输入备份、提取的临时脚本、检查程序、模拟输出及`validation.json`在`/tmp/e01-official-entry-d4nifvkx/`。未新增仓库脚本、修改共享状态/RTL/软件/依赖或提交Git。
- 最小下一步：用户按指南先备份，再编辑服务器官方启动脚本和wave.tcl，逐步执行编译、展开、采集与Verdi查看；Agent据实际输出更新结论。已有单例fmatmul成功不扩大为新调试流程或完整向量验收成功。

## 文件配置式流程检查（2026-10-19）

本节保留上一版五文件方案的检查证据；该方案已被官方入口精简替代，不作为当前操作要求。

- 从指南提取11个Bash代码块做`bash -n`；相对链接和新增页内锚点检查通过。在`/tmp/e01-script-doc-check-expsooxf/`使用模拟vcs/simv/verdi检查构建/运行目录拒绝覆盖、配置不匹配拒绝运行、旧运行使用其保存的数据库、编译/展开/运行错误码传播。Tcl通过空操作命令检查变量/语法组织；这些检查没有调用EDA，不证明UCLI/PLI/FSDB或GUI可用。
- 写入前两文档备份在`/tmp/e01-file-config-before-c9wd8eki/`；其他208个已有修改/未跟踪文件哈希保持不变。`git diff --check`通过。未在服务器创建文件或运行工具，未改RTL/依赖/共享状态；未提交Git。

## 配置导读检查（2026-10-19）

- 四份修改文件：`software/SERVER_SIMULATION_GUIDE.md`、`configuration/README.md`、`configuration/RECIPES.md`及本交接。未新建文档或脚本。写入前备份在`/tmp/e01-config-docs-before-x5fgtgno/`，其他205个已有修改/未跟踪文件的SHA256保持不变；共享状态保持原状。
- 静态核对15个DefaultCfg关键取值、TB Ara函数的3项显式赋值及fixture传入VIP的参数集合；复算LLC=131072 B、AXI输入数7、下游ID宽5/6 bit。CPU覆盖/派生、宏消费者和实例链路按源码阅读核对；不称为SV展开测试。
- 四文件相对链接、新增显式锚点、表格列数与代码围栏配对通过；指南11个Bash代码块逐段`bash -n`通过；`git diff --check`通过。未执行这些命令、未渲染GUI/波形或运行仿真。仅以历史报告引用fmatmul成功及FS兼容修正，FS Dirty原因和完整验收仍开放。

## 上手指南检查（2026-10-18）

- 正文11个Bash代码块分别通过`bash -n`；检查了正文、软件README和本交接的相对链接，以及正文显式锚点。新正文/交接无行尾空白，`git diff --check`通过。未执行文档中的构建/仿真命令；语法检查不等于命令在目标环境运行通过。
- SSH只读核对Cheshire/Ara提交、fmatmul及其辅助头文件、官方软件参数、crt0/链接脚本、VIP结束协议和CPU/Ara实例名。波形命令形式按服务器安装的FSDB/UCLI手册及VCS帮助核对，只记录命令接口与受控文档位置，不保存厂商手册正文。GUI打开、许可、PLI联编、FSDB有效性和真实波形解释仍待用户运行验证。
- 写入前备份软件README和已有未跟踪E01交接到`/tmp/e01-guide-before-n5jyr3ge/`；9个已有共享/其他主题修改文件哈希保持不变。未修改本地RTL/sw、依赖、服务器文件或TTY工程，未新增通用执行脚本，未提交Git。

## 最小下一步

当前（fmatmul通过后）：保留四次运行证据及服务器crt0兼容修正；继续核实FS Dirty状态跟踪原因，并按用户逐步确认流程补齐不同VL/尾部、SPI自主启动、访存/原子验收及VCS warning审查。参考验收通过后再提取。C00可据核查报告合并共享状态，本对话未代改并行文件。

### 历史下一步（五步执行前，已被上段替代）

1. 按已明确的同版本方向，核实原官方 `mp/ara-pulp-v2` 提交 `e040b7bbc` / Ara `2895ba90` / CVA6 `99eac9a6` 的可获取性与锁文件，列服务器环境及本地差异处理。报告第2步具体动作，待确认后获取/重建；保留preflight，不触碰TTY或`/opt`。
2. 后续第3步才执行完整参考SoC编译/展开/目标运行，检查VS/FS和原启动路径；保留S01-T01运行库限制及所有既知缺陷。
3. C00可合并：E01第1步完成，已明确官方GitHub同版本 `mp/ara-pulp-v2` 重建，具体第2步执行待确认；S01工具链部分编译/链接证据已取得，S01-T01开放；V01仍无目标仿真证据。共享文件本轮未代改。

后续只需读本交接、实施方案与 [02 规格](../02_Cheshire_Ara_ASIC_Extraction_Handoff.md)，再核对当前工作区和服务器目标是否变化。

## 资源问答文档检查（2026-10-19）

- 负责文件：`engineering/Fixed_Vector_SoC_Resource_Guide.md`、`engineering/README.md`、本交接，路径均相对 `docs_codex/`。原有两个文件只追加内容，已有记录保持；未修改共享状态和原封装预算。
- 静态复核：实际选择 `sram_pulp.sv`、SRAM 数据/标签形状、TLB/预测器与 CSR 字段、ROM 实例/链接/解码口径、Cache/VRF 扩容关系。独立审阅纠正“增路数改变每 way 粒度”的不准确表述，并将源码索引中的性能计数器及 Ara CSR 符号改为实际声明；未扩大到工程缺陷修复。
- 文档检查：三份文档的 123 个本地链接及 Markdown 锚点、19 张表的列数、代码围栏及空白检查通过；60 项容量/位宽/地址和扩容算例复算通过。原有 206 个修改/未跟踪文件中，除本轮授权追加的两份文件，其余 204 个文件哈希保持不变；唯一新增文件为资源正文，HEAD 未变。
- 可复查命令（仓库根）：`python3 /tmp/e01-resource-guide-_r7jjgc6/validate.py`、`git diff --check`。检查脚本、`validation.json`、输入备份及增量差异位于同一临时目录；临时 HTML 仅用于 Markdown 结构解析，不是仿真/性能证据。脚本与空白检查退出 0，未执行构建、仿真、综合、宏映射或新的服务器核查，未提交 Git。
- 当前结论和下一步：资源文档已交付；硬件固定配置及既有验收状态保持。后续如需扩容或选工艺宏，按正文 Q7 的参数联动和定向验证要求另立变更输入，不把候选配置当成已确认配置。

## 参数开放策略文档检查（2026-10-19）

- 输入：`mp/ara-pulp-v2` / `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`＋写入前已有未提交内容。负责文件仅为 `02_Cheshire_Ara_ASIC_Extraction_Handoff.md`、`engineering/Fixed_Vector_SoC_Resource_Guide.md`、`maintenance/E01/planning/server_reference_extraction_plan.md` 和本交接，路径均相对 `docs_codex/`。未新增专题或实现文件。
- 同步结果：固定向量功能组合，采用 `src/config/`，每次构建锁定配置；基线提取对照通过后先试 L1 容量/LLC 行数，再按瓶颈逐步开放。基线、候选、完整验收分开记录，源码闭包覆盖声明支持范围。应用比较区分目标周期与主机耗时、内核与完整任务，明确 LLC 全 SPM 启动条件；物理实现比较纳入宏、时序、功耗和 Pad 约束。具体候选值和最终产品配置仍待评估。
- 交叉审阅：核对四文档的来源/目标、配置入口、阶段顺序和证据边界；修正服务器方案两处旧表述，保留并溯源已有 FS=Clean 兼容修正，将最小 SV/DPI 探针统一为按需诊断。S01-T01、FS Dirty 原因及完整参考/提取验收仍未关闭。
- 静态检查：134 个本地链接（其中 28 个带 Markdown 锚点）、34 张表、14 个代码块的结构检查通过；旧锚点保留。资源 Q1—Q6、原有 83 行含数值表格、两份基线表和无关架构契约保持；47 项原容量/位宽及扩容算例复算通过。原交接仅插入内容，206 个范围外已有修改/未跟踪文件 SHA256 不变，HEAD 未变。
- 可复查命令（仓库根）：`python3 /tmp/e01-parameter-policy-uqiuf7qd/validate.py`、`git diff --check`，退出均为 0。输入备份、保护哈希、四文件增量差异及 `validation.json` 在同一临时目录。本次检查仅支持“文档同步完成”，未创建 RTL 配置目录，未运行构建、仿真、综合或服务器操作，未提交 Git。

共享状态合并建议（交 C00 汇总，本次未修改共享文件）：

- `PROJECT_STATE.md`：记录 2026-10-19 用户确认“固定 CVA6＋Ara 功能组合、集中可调参数、按构建锁定配置”；首次提取基线保持，后续以应用正确性/性能及面积、时序、功耗选择产品配置，替代长期只允许一个参数配置的旧限制。
- `AGENT_TASKS.md`：E01 参数策略文档同步完成；工程提取和参数试验未实施。最小下一步仍是按用户分步确认补齐参考验收，再提取并验证独立性，之后才开展受控参数试验；不把本次文档交付记为 E01 工程验收完成。
