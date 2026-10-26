# E01：LLVM 工具链适配、两工程同步与回退计划

日期：2026-10-25起草，2026-10-26更新。状态：**P7两工程修复已验证；LLVM默认编译器迁移现已完成。R38新ELF/40项主矩阵及两运行库探针、F49新ELF/51项独立运行完成，普通正例通过，SPI/LLC限制和预期负例分别保留；两地备份与实际恢复检查通过。R八份受Git管理的LLVM修改已提交并推送[`6f2b2a3b`](https://github.com/lionelZhaowy/CheshireAraPULP/commit/6f2b2a3be50eeb15eb93c0ada2164029a102c94c)，远端main读回一致。见[发布与剩余工作区内容](#llvm-github-push-20261026)及[第12节](#llvm-resume-20261026)；第1–11节为此前快照。**

**2026-10-26 P7同步结果：**F先独立重建RTL及14ELF，17次串行仿真全部PASS；P7 68组/13416项0错，三份归档编译器对照均未重编通过，12回归保持。随后R四份P7源码正常提交/推送，2诊断修改保持。P7是RTL正确性修复，不代表LLVM构建入口或整套迁移验收已经完成。来源、结果及恢复位置见[修复报告13.6](../reports/official_pr_failure_fixes_review.md#p7-reference-formal-sync-20261026)；13.5保留仅R验证历史。下文迁移各阶段及第11节为此前记录。

用户已选择以 Ara 配套 LLVM 替换当前目标软件的 GCC，并要求先在参考工程 R 验证，再同步正式工程 F；规划完成后已明确回复“好的，开始实施”。阶段通过后按下述顺序继续，不另设逐条命令审批；超出范围或无法恢复的冲突须先报告。

## 1. 已核对的输入

| 输入 | 本轮只读确认结果 |
| --- | --- |
| 本地 L | `mp/ara-pulp-v2`，HEAD `ca8395677691ba8d9d226ce4b5b5b49192b90f1c`，已有文档修改和未跟踪备份保留 |
| Ara | L 的 `Bender.yml`、实际 Ara checkout 与 R checkout 均为 `2895ba907e9eb14b3464609dc791a969d159a7c3` |
| LLVM | 该 Ara 提交的 gitlink 为 `24a30daaa559829ad079f2ff7f73eb4e18095f88`；官方源码版本文件为 **20.1.0** |
| newlib | 同一 Ara 提交锁定 `2e4ecbb3f0d574d18eddb97eff9421db45fb0da7` |
| R | `/home/zhaowy24/CheshireAraPULP`，`main` / `cb20a03c063d208d17eef024a1f6491152d509e8`，含已验收 P1–P6 |
| R 原未提交修改 | `_e01/dma_vector_check/pr80_204_20261021/llc_recheck/probe.tcl`、`_e01/dma_vector_check/slink_llc_rx_20261021/final/tb_slink_llc_rx.sv`；不属于本任务 |
| F | `/home/zhaowy24/CheshireAra`，无 Git 元数据；P6 已同步，现有 ELF 为日常7、维护29、可选Ara11，共47项 |
| 当前目标工具链 | `/opt/riscv/bin/riscv64-unknown-elf-gcc` 13.2.0；保留其安装和旧产物 |
| 构建环境 | 现有 CMake 3.26.5、Ninja 1.8.2、主机 GCC/G++ toolset-13；规划不升级系统工具 |

版本一致的含义是**使用上述精确提交**，不是任意 LLVM 20.1.x。Ara 工具链子模块目前未展开，不能把对空子目录执行 `git rev-parse` 得到的父仓库 HEAD 当作 LLVM HEAD；获取源码后须再次核对提交和版本文件。

官方依据：[Ara 工具链 gitlink](https://github.com/pulp-platform/ara/tree/2895ba907e9eb14b3464609dc791a969d159a7c3/toolchain)、[Ara 构建规则](https://github.com/pulp-platform/ara/blob/2895ba907e9eb14b3464609dc791a969d159a7c3/Makefile)、[LLVM 版本文件](https://github.com/llvm/llvm-project/blob/24a30daaa559829ad079f2ff7f73eb4e18095f88/cmake/Modules/LLVMVersion.cmake)。两工程路径和配置例外遵守[现有同步规范](server_reference_rebuild_guide.md#cross-project-sync-rules)。

## 2. 目标、范围与不变项

目标是让**当前已采用的 RISC-V 裸机软件构建链**默认使用 Clang、LLD、llvm-ar、llvm-objcopy、llvm-objdump，并以匹配的 newlib、compiler-rt 提供运行库；不再由目标 GCC、GNU binutils 或 libgcc 完成本轮 LLVM 构建。服务器主机 G++/VCS DPI、Linux SDK 不属于这次目标编译器替换。

- 顺序固定为：工程外工具链准备 → R 适配和验证 → 按映射同步 F → F 独立验证和默认入口确认。
- R/F 继续保留各自目录、源码定位和测试分组；不把 R 重构成 F，不整包复制 Makefile。
- LLVM 安装到现有 `~/CheshireAra_maintenance/` 下一个确认不存在的新版本目录，源码、build、install 分开；两工程共用这一工程外安装。普通 Make 不下载或构建工具链。
- 新软件输出使用各工程的 `sw/build/llvm`，仿真使用新输出/运行目录。旧 `sw/build/default`、旧 ELF、镜像、simv、日志和验收归档保留。
- 不覆盖 `/opt/riscv`，不改 shell 启动文件、全局 PATH 或系统默认工具；不执行 clean、依赖升级、Bender 解析/下载或子模块递归更新。
- 不改 RTL、硬件参数、地址图、CPU profile、wrapper、TB 断言或结果判定。原生成 Boot ROM RTL/ELF/bin及其历史证据保持，不运行 `bootrom-all`，不把改用 LLVM 后的 ROM 生成能力列为已验证。
- 本计划不包含 Git 提交、推送、分支切换、综合或板测。

## 3. 拟修改文件及必要性

| 阶段/文件 | 必要改动 |
| --- | --- |
| R `sw/Makefile` | 替换默认编译/归档/链接/反汇编工具，适配选项、LTO、运行库、镜像生成和新 OUT；保留原 all 与 p6-regressions 集合 |
| R `sw/sw.mk` | 同步根软件入口的目标工具和选项，处理其原有 ELF→memh、GPT→memh 规则；不能留下根软件目标默认调用 GCC |
| R `cheshire.mk` | 仅在实际兼容需要处调整目标软件相关选项；不改硬件依赖组织或扩大到 ROM 重生成 |
| R 现有 `vector_fixed` 源及其 F 对应文件 | 保留手写复制检查，增加独立的普通 C 计算函数，验证自动向量化与手写 RVV 在同一 ELF 中共存；优先原文件内增加，不另建运行框架 |
| R 启动/链接及已有头文件 | 原件先保持；仅实际编译、链接或执行证实有兼容问题时作最小软件适配，保存原因与前后差异；不能借此改变启动机制或硬件布局 |
| F `sw/Makefile` | 按对应改动适配自身路径、库源和47项构建目标；保留 all/regressions/ara-tests 组织及已有 P1–P6 |
| F `sim/scripts/start.cheshire_soc.sh` | 验证通过后仅将默认 BINARY/IMAGE 指向 LLVM 输出；保留 TARGET、超时和结果判定 |
| 两工程当前用户指南、F `provenance/source_manifest.json` 等现有来源记录 | 更新真正改变的入口、工具版本、文件和实际结果；保留原来源、历史记录及并发修改，不新增平行来源管理机制 |

R/F 的 `vector_fixed` 源位置、指南入口和所有实际修改名单在实施前按磁盘再次核对并纳入备份；只有完成备份的文件才写入。原始源码版权/许可证保留。确需新增一个软件源文件时，先说明现有用例为什么不能满足，不预设增加脚本、配置包或编译器选择框架。

## 4. 技术实施安排

### 4.1 工程外构建工具链

在新目录获取固定 LLVM/newlib 源码，参考 Ara 官方 clang/lld → newlib → compiler-rt 的组成和次序，只构建所需 RISC-V 后端与裸机运行库。主机工具继续沿用服务器既有环境，限制构建并行度。

不能直接在受保护 Ara checkout 中执行官方 `make toolchain-llvm`：其依赖会递归更新子模块，规则含删除 build 的操作。官方 newlib 配置中的 `llvm-as`/`llvm-ld`，compiler-rt 的 `CMAKE_SIZEOF_VOID_P=4` 和硬编码资源目录也需对照实际 LLVM20/RV64构建核对；按真实调用最小适配，不照抄不适用参数。使用 Clang 驱动正确选择汇编器/LLD，并检查 RV64、lp64d、资源目录和最终库搜索路径。

运行库采用当前标量 ISA/ABI 和适用的 medany 设置，不从旧 `/opt/riscv` 偷用 libgcc/newlib。对原 libgcc 高地址失败涉及的辅助运算，在 SPM 与 DRAM 布局实际检查 compiler-rt 的解析、重定位和执行结果；通过前不把原限制写成已解决。

### 4.2 编译、LTO及自动向量化

- 保留现有 O2、库 `rv64gc_zifencei`、应用 `rv64gcv_zifencei`、ABI `lp64d` 和 medany 意图；不顺带启用 zfh/zvfh、fast-math 或改变 P3 浮点异常语义。
- 移除 GCC LTO 插件、`-fuse-linker-plugin`、GNU ld 专用 LTO 传参及不适用的 GCC 选项；用 LLVM 对象、llvm-ar、LLD 完成原有 LTO 用途。所有目标对象和工程库重建，不能混入旧 GCC LTO 对象。
- 底层库、启动/异常处理、标量参考及手写固定向量寄存器的用例保持标量或显式 `-fno-vectorize -fno-slp-vectorize` 的用途；不能全局打开自动向量化后使 VS 初始化之前出现向量指令。
- 在现有向量用例中增加一个独立的普通 C 函数，启用 VS 后调用；用函数/循环控制及必要的 noinline 保持它与手写寄存器存活区分开。编译器报告和最终反汇编须证明该 C 循环实际生成了 RVV，而不是仅接受了 `v` 选项。
- 核对内联汇编的输入/输出、clobber、内存及 vl/vtype 交接。通过更换编译器发现真实软件约束问题时，只修对应软件，不降低测试或断言来迁就失败。

### 4.3 LLD 与镜像

优先复用现有链接脚本，核对入口、PT_LOAD 的 VMA/LMA、段权限、SPM/DRAM 区域、P4 相邻段/跨页/尾部条件和栈 ABI。编译器更换会改变指令和段大小，不要求新旧 ELF 逐字节相同，但不能丢失原定向覆盖条件。

LLVM20 [llvm-objcopy 格式清单](https://github.com/llvm/llvm-project/blob/24a30daaa559829ad079f2ff7f73eb4e18095f88/llvm/docs/CommandGuide/llvm-objcopy.rst#supported-formats)不含 verilog。复用 Makefile 已使用的 Python3.9 完成必要转换，不新增转换脚本。区分原始 binary 的偏移0和 ELF 的实际装载地址，保留字节顺序、空洞/起始地址及镜像语义；F SPI raw仍从offset0装载49152字节、超限失败并填充0x9a。按新 bin 与新 memh 逐字节解码比较，不能拿不同编译器的程序内容要求一致。

### 4.4 R 根软件入口的单独保护

现场 `sw/sw.mk` 在源码旁生成 `.o` 并写 `sw/lib/libcheshire.a`；设置独立 `sw/Makefile` 的 OUT **不能保护这些产物**。根 `cheshire.mk` 在解析时调用 Bender，并可能自动重建缺失 include，因此 `make -n` 也不能直接当作无副作用检查。

先以 R 的独立 `sw/Makefile` 完成当前采用目标的适配。根软件规则同样改为 LLVM，但首次构建在**工程外可写隔离副本**进行，仅复制该入口所需源码、既有生成头及依赖；可写对象不得通过硬链接或符号链接回指 R/F。保留 R 的目录组织，通过一次性 Make 输入（如 `make -f -`）只加载隔离副本的原 `sw/sw.mk`，注入已经确定的依赖路径并使用已有生成头，仅指定软件目标；**不包含 `cheshire.mk`，不让 Make 重生成头文件或依赖**。不新增常驻 Makefile、启动器或 Bender 替代脚本。

这样验证编译、归档、链接及实际采用镜像规则；`cheshire.mk` 中相关工具引用另作静态核对。结果明确称为“根软件规则隔离验证”，不能写成“已运行根目录 make all/sw-all”。根默认 all、其依赖生成和未执行的全部历史链接模式不属于本轮运行验收。

不为了统一 OUT 重构 R 的官方布局，也不新增软件启动器或常驻 Bender 替代脚本。若隔离副本仍不能在本范围内避免触及依赖生成或 ROM，该入口阶段停止并说明具体原因，不宣称全面替换已完成。

## 5. 实施前备份与实际恢复检查

每个工程在首次写入前分别完成，R 的备份不能代替 F 的备份：

1. 保存实际 HEAD/status/相关 diff；逐项保存拟改文件的 before 原件、权限和符号链接目标，记录新增路径原先不存在。R 两处原诊断差异另行保护。F 无 Git，不能用旧提交或来源包代替其实际原件。
2. 服务器工程外现有维护目录保存一份，本地既有 `.e01_backups/` 保存第二份；比较归档和成员内容。不因此复制整棵依赖或建立自动归档框架。
3. **在独立临时目录实际展开备份**，逐项比较内容、权限和链接目标，确认可恢复；只列归档目录、只检查命令返回0均不够。恢复检查通过后才写工程。
4. 写入前再次重读拟改文件，与 before 比较；有并发变化时先合并/重新备份，不覆盖别的对话。每个阶段保存实际 after 差异，使回退时能识别后续修改。
5. 新安装、新软件和新仿真输出目录先确认未占用、不经链接落入旧目录。R 根软件规则可能覆盖的产物只在隔离副本生成，旧原位产物不触碰。

本轮规划文档修改前的已有 E01 交接已保存在本地 `.e01_backups/llvm_planning_20261025_a0mm0039/`；这只是**本地文档备份**，不是服务器实施备份或工具链恢复检查已完成。

## 6. 阶段、验证及推进条件

| 阶段 | 修改/验证 | 推进条件 |
| --- | --- | --- |
| A 工具链 | 工程外固定版本构建；检查实际编译/链接命令、库来源、SPM/DRAM基础运算与LTO | 可独立生成并执行当前 ABI/ISA 的程序，未借用目标 GCC/libgcc；否则不写 R/F |
| B 参考工程 | R独立入口全部现有 all、p6-regressions；根软件入口按4.4隔离验证；验证普通C自动向量化与手写RVV共存 | 现有检查保持有效，无未解释新失败；完成 R 的 before/after 和恢复核对，再进入 F |
| C 正式工程 | 按文件映射合入，不复制R整份Makefile；重建7日常＋29维护＋11Ara共47 ELF、map/dump/镜像；使用F自身入口准备并验证当前P6对应的仿真构建 | F运行结果满足原判据并验证混合向量化功能，来源记录与实际改动相符 |
| D 默认入口及交付 | 验证两工程日常入口 `make -C sw` 和实际默认 ELF/镜像路径，确保未运行旧 GCC 产物；R历史根软件规则按4.4验证；更新最少必要指南/来源和主题交接 | R/F各自结果、差异、失败记录及回退方法可查；旧工具和旧产物保持可用 |

具体运行按现有 ELF/TARGET 表及 R 对应入口，不新建回归调度器。R 未登记的 F 可选 Ara 项不借本任务复制一套到 R；它们在 F 阶段全部构建和验证。

- 软件与系统检查覆盖 HelloWorld、SPI、CSR/vstart、RVV5976项、访存/原子572项、fmatmul、DMA、Serial RX、P1–P6及11项Ara。P2/P3/P4/P5继续带原有监视/CASE参数，P6保留原508组/38452项检查意图，不能只看程序返回0。若编译变化影响某项真实触发条件，先确认覆盖仍成立。
- 普通仿真串行、无波形、默认每例600秒；已有 simv/输入须与当前 P6 源码对应。为 F 独立验证使用其自身编译/运行入口及新输出，不直接搬 R 的 simv 或 ELF。独立 iDMA 后端不使用 ELF，不因目标编译器替换预设需要重测全部后端。
- 原 ROM padding限定告警、共享LLC已知失败、故意目标失败/超时负例和 FS/其余覆盖边界分别报告；新编译器下的新停滞不能未经定位就归为旧问题。P3非整拍VL异常屏蔽、#479等并不因本轮通过自动关闭，也不夹带RTL修复。
- 自动向量化检查需要编译报告、最终指令及运行结果三者一致；性能只记录实际目标周期等测量，不以主机耗时或开启优化选项宣称性能改善，不把性能提升设为迁移通过的先验条件。

## 7. 回退触发与具体操作

出现未解释的新构建/链接/运行失败，或需要改 RTL、硬件参数、Boot ROM、升级其他依赖，或不能消解并发修改时，停止对应阶段。保留失败版本和日志，不把失败方案作为日常默认继续使用。

**R 失败：**F 保持完全未写入。先保存本轮 after/失败差异，再确认待恢复文件仍等于本轮最后写入版本；逐文件恢复 R 自身 before 原件和原默认输入/输出路径，核对原两处诊断差异及已验收 P1–P6仍在。旧工具/旧产物原样保留，可用于最小入口检查。不执行 reset、checkout、clean、切换分支或整树覆盖。

**F 失败：**同样先保存失败状态、检查后续修改，再逐文件恢复 F 自身 before 和默认 BINARY/IMAGE；来源清单只逆向本轮条目/维护记录，保留其他会话新条目。新增路径若无后续变化，只移出活动路径保存到本轮备份，不直接删除；有后续变化先按差异合并。F 回退不要求撤销已通过的 R 适配。

若当前文件已被后来工作修改，**不得用旧备份整文件覆盖**；从 before→after 差异只逆向本任务内容。旧默认路径恢复后核对配置和输入文件；确需动态确认时，用保留的旧 ELF 在新运行目录做最小检查，不覆盖旧验证日志。

新 LLVM 安装、构建目录和失败输出可以保留供定位，回退不需要卸载它们；因为没有改系统工具或全局环境，恢复工程 Makefile/默认路径即可回到旧工具链。实际回退完成与否、恢复检查结果必须如实记录，不以“存在备份”替代“已恢复”。

## 8. 规划阶段记录（实施前快照）

本轮主 Agent 完成本地/服务器只读核查，两名**本地**子 Agent分别只读复核编译兼容和恢复安排；未委派服务器 Agent。只写本计划和 E01 既有交接的导航，不修改共享状态/任务表及其他对话的报告。

**未执行：**下载LLVM/newlib、安装、修改R/F、构建软件/硬件、仿真、实际服务器备份恢复、Git提交/推送。以上阶段是建议实施范围，不能引用为已执行结果。

用户确认本计划并明确开始实施后，先完成 A 和 R 的实际备份/恢复检查；R通过后才同步F。实施前再次核对最新磁盘状态，不能将本轮 `cb20a03c` 或47项快照当作不可变化的现场状态。

## 9. 实施进度（2026-10-25）

- 已在服务器工程外新目录 `/home/zhaowy24/CheshireAra_maintenance/llvm_20.1.0_20261025` 获取固定 LLVM/newlib 源码；LLVM Release 构建和安装完成，实际 `clang --version` 为20.1.0。newlib/compiler-rt构建通过；SPM/DRAM独立探针均PASS。
- LLVM 源归档 SHA256 为 `fda11e2841bce0818326aebb640f435d3aaa89261ee7e2147b736af20f6f5fd9`；newlib 源归档为 `886d233d4e5b14b1cb59621a4c230bdc0f3db2fd09fd6d3cfc3c18829a2468f5`。
- R 拟改原件及原两处诊断差异共16文件已保存至上述目录的 `backup_r/`，`before.tar` SHA256 为 `dcb63a2cda40615b24ee605505b78fe187173322d2660b1cdf5856c54fff2e56`。独立目录实际展开后逐项核对内容和权限通过；本地第二份位于 `.e01_backups/llvm_migration_20261025/backup_r_local/backup_r/`，同样已核对。
- 首次展开使用 Python 默认过滤器，文件权限被收紧，检查未通过；原工程未写入。保留该展开结果，确认成员都是白名单普通文件后重新按原权限展开，第二次检查通过。详见服务器 `backup_r/restore_check.txt`。
- 本地草稿检查确认需同时约束 LLD LTO 的默认向量化；不能仅依靠编译阶段 `-fno-vectorize`。使用固定 LLVM 源码支持的 `-Wl,-mllvm,-vectorize-loops=false,-mllvm,-vectorize-slp=false`，显式循环 pragma 仍可启用自动向量化。最终须由报告、反汇编及运行结果核实。
- 现场编译发现 Clang 拒绝 `rv64gc_zifencei` 中重复的扩展名；LLVM 入口改用等价 `rv64gc`／`rv64gcv`，实际宏已确认 `__riscv_zicsr=2000000`、`__riscv_zifencei=2000000`、XLEN/FLEN均64，不改变硬件配置。首次失败目录及日志保留。
- 实际 Clang 查询的 compiler-rt 路径为 `install/lib/clang/20/lib/riscv64-unknown-unknown-elf/libclang_rt.builtins.a`，采用该版本的 per-target runtime 布局；不使用规划时尚未确认的 baremetal 旧目录猜测。
- 首次独立软件构建找不到已安装的 `assert.h`。进一步检查固定版 `BareMetal.cpp::findRISCVMultilibs`，确认 `rv64gc` 硬编码选择 `rv64imafdc/lp64d` 后缀，而本次 newlib 使用 plain include/lib；初步归因于旧 GCC 探测不准确，已纠正。试探性的 `--gcc-toolchain` 会让 `Driver.cpp` 选择另一 RISC-V 驱动并默认链接 `libgloss`，现已撤回。最终草稿保留 BareMetal 驱动，以 `-isystem <sysroot>/include` 和 `-L<sysroot>/lib` 明确本次真实布局；运行库与探针重新构建。各次构建/失败日志保留，尚未写入R/F。
- 阶段A首次两例各79项通过，但memcpy实际来自原HAL，未作为newlib执行证据；增加真实newlib `memmove` 后两例各152项、0错并PASS，实际拉入 `libc_a-memmove-stub.o`、compiler-rt `udivti3`/`udivmodti4`。根软件规则隔离构建SPM/ROM/DRAM通过，ROM ELF的LMA0/896字节和GPT44032字节memh逐项比较通过。结果为服务器 `evidence/stage_a_result.json`。
- R已临时写入 `sw/Makefile`、`sw/sw.mk`、`cheshire.mk` 和 `vector_fixed.c`；全量重建另暴露两处已有软件问题：R旧 `dma_long_2d.c` 缺当前HAL的第七配置参数（采用F已有 `DMA_CONF_DECOUPLE_NONE` 同一行），`sw/tests/rvv_test.h` 的void wrapper返回指针值（仅去掉return、保留调用）。两文件均另做服务器原件/实际恢复和本地第二备份，位置为 `backup_r_api_compat/`、`backup_r_clang_header/`。F头文件与R原件相同，但尚未改F。
- 为丢弃ISA属性段的现有ELF，在三份Make草稿及R活动dump规则显式增加 `llvm-objdump --mattr=+m,+a,+f,+d,+c,+v,+zicsr,+zifencei`；只影响译码显示。R最终 `make -C sw -j4 all p6-regressions` 返回0，36 ELF/map/dump和SPI镜像生成；构建日志为 `logs/r_software_build.log`。根规则隔离测试不是根默认all验收；出现的LTO硬浮点ABI提示尚未完成解释，不笼统称无告警。
- R已准备当前P6对应的独立RX simv，未改RTL；38条现有运行器调用安排在 `evidence/r_validation_invocations.json`/`r_validation_commands.sh`。实际执行到第2例即停止：HelloWorld PASS，混合向量例手写复制22字节0错，但新增465项自动向量检查256错、TARGET_FAIL/目标256/入口1。剩余36条未执行，不能将36 ELF构建写成36项运行通过。
- 初始失败ELF、源码、map/dump、完整log/trace已保存为服务器 `vector_failure_01/artifacts.tar.gz`，SHA256 `d923537ea68fe4ef95b9d59772082a2d286f5de02963afb1cc68b545004fdc7b`；本地同名备份已核对。当前仅在工程外诊断副本作受控指令对照，不以补丁二进制作为交付，不改RTL，不用绕过用例宣称自动向量化全面可用。F仍完全未写入。
- R六个变化文件已按after哈希检查后逐项恢复原件；共18项输入内容/权限与before匹配，HEAD及原两处诊断Git差异与开始时一致。F八个涉及输入保持。服务器 `evidence/rollback_result.json` 记录实际回退结果；新LLVM安装和失败候选输出保留，未卸载或清理。随后原GCC HelloWorld历史ELF用同一P6 simv新运行PASS（`llvm_rollback_gcc_helloworld_01`），不是重新构建GCC全组的证据。

<a id="llvm-vector-failure-analysis-20261025"></a>

## 10. 新增自动向量化失败的原因分析（2026-10-25）

本节只对应R `cb20a03c`、Ara `2895ba907`及固定LLVM20.1.0生成的本次程序。旧GCC `vector_fixed.c`只检查22字节手写RVV复制；新增`auto_add`不在历史GCC覆盖中，不能把二者当作同一个已通过程序。新增循环为 `uint32_t dst[i] = src[i] + 7u`，两个数组独立、restrict成立、最大索引在界内；六种长度1/3/63/64/65/257，共453个数据及12个保护字检查。

### 10.1 已检查的编译设置及一个实际遗漏

- 前端及最终应用IR具有 `rv64gcv`、`lp64d`、`+d,+f,+v,+zicsr,+zifencei`，最终ELF flags为RVC/double-float ABI；没有把CPU VLEN64传给Ara循环。实际`vlenb=256`，`e32,m2`每轮128元素、步长512字节，257长度为两轮向量加一项标量尾部。源/目的地址及保护字范围核对正确。
- LTO出现的硬浮点ABI告警确有一项设置因素：只在外部相同链接命令增加 **`-Wl,-mllvm,-mattr=+d`**，最小HelloWorld告警消失；同样重链失败向量程序。两个ELF各自的所有PT_LOAD地址、大小、权限及内容均与原件完全一致。因此这项遗漏应在后续适配中修正，但修正没有改变本例实际加载的程序，不能解释256项数据错误。结果为服务器 `compiler_controls/{hello,vector}_lto_mattr_d.json`。
- 固定LLVM中相同警告文字同时存在于`RISCVAsmParser.cpp`与`RISCVISelLowering.cpp`；未捕获实际打印栈，不能锁定为汇编解析器。合并HelloWorld IR无module asm，函数仍有+D；不能仅凭告警文字认定本例已改为软浮点，也不能把警告一概忽略。上述结论不宣称LLVM全部设置或浮点调用边界均已验证。

### 10.2 合法向量序列及受控对照

失败ELF `auto_add` 的核心为：

```asm
vsetvli a3, zero, e32, m2, ta, ma
vl2re32.v v8, (a5)
vadd.vi  v8, v8, 7
vs2r.v   v8, (a4)
```

v8–v9满足m2对齐，算术源/目的EEW同为32，允许完全重叠；VL=VLMAX，不依赖tail/mask不确定值。[RVV1.0向量操作数规则及whole-register语义](https://github.com/riscvarchive/riscv-v-spec/blob/v1.0/v-spec.adoc#vector-operands)不要求为这次加法另分配目的寄存器。whole-load的EEW提示不改变读入寄存器的架构字节内容。

| 诊断 | 自动加法检查 | 状态/证据 |
| --- | --- | --- |
| 原LLVM自动向量化 | 465项，256错 | `llvm_r_vector_fixed_01`，手写复制22字节0错；目标256/入口1 |
| 只把load提示32改8 | 465项，256错 | `llvm_r_vector_whole_eew8_diag_01`，单条opcode外部副本 |
| 只把add目的及store源由v8改v10 | 465项，0错 | `llvm_r_vector_separate_dest_diag_01`，仅两条opcode变化，PASS |
| 同完整C、同LLVM库，仅关闭新增循环的向量化pragma | 465项，0错 | `llvm_diag_clang_scalar_01`，PASS；最终auto_add为lw/addi/sw循环 |
| 同完整C、GCC13标量版及独立重建GCC库 | 465项，0错 | `llvm_diag_gcc_scalar_01`，PASS；最终auto_add为lw/addiw/sw循环，不混用LLVM bitcode |

前五种短长度走标量路径；257长度的前256个向量结果全错、最后一个标量结果正确。以上诊断均使用同一P6 simv、原配置/启动/结果判定，串行、每例600秒、无波形；外部二进制改动不是生产修复或验收替代品。

### 10.3 当前R源码可以解释全部错误值

以下定位来自服务器实际R源码拷贝，保存在本地 `.e01_backups/llvm_migration_20261025/vector_diag_sources/`，不是本地旧RTL：

1. `ara_dispatcher.sv:3042–3051`将whole-load内部宽度统一为EW8，`3675–3687`也按EW8记录v8/v9的布局；`vldu.sv:367–380`按该宽度分配各lane的字节。
2. 后续`vadd.vi`要求EW32。`ara_dispatcher.sv:3617`本会请求源操作数布局转换；但`3622`在vs2==vd时屏蔽该请求，意图复用目的寄存器的转换。
3. 同时`3618`因vstart=0、VL=VLMAX且完整覆盖目的寄存器，又省去目的转换。两条优化组合使本来仍须读取的旧源数据没有转换；“结果会全部覆盖”不等于“计算不需要旧源值”。
4. vadd于是把EW8物理布局按EW32解释；`vstu.sv:339–349`再按EW32存出。把目的换成v10后，源v8不再被同寄存器条件屏蔽，恰好符合该对照通过的现象。

独立字节模型从`ara_pkg.sv`的实际2-lane EW8/EW32 shuffle表提取排列，假设缺少上述转换；预测与原trace **257/257逐项一致**（含256个错误及正确标量尾项）。首项应为`0x12340007`，模型和trace同为`0x5d1f3e07`。本地主Agent实际复跑 [vector_layout_model.py](../../../../.e01_backups/llvm_migration_20261025/vector_layout_model.py)，结果及输入SHA见同目录`vector_layout_model_result.json`。

这使“合法LLVM序列触发当前Ara源数据重排缺口”成为有直接源码、受控运行和完整错误值支持的原因判断；尚未采集内部reshuffle请求信号，也未实施/验证RTL修复，模型不是独立ISA参考执行器。不由此推断其他LLVM设置、RVV指令或自动向量化程序均正确。

同源控制的命令、输入哈希、ELF/map/dump、LLVM20 IR、运行结果/日志及告警修正对照已保存为服务器 `compiler_controls_01.tar.gz`，SHA256 `fbd0ef74e657ff82efa0648a9f24d12448d776e6a1cd8fe417ac9765f0a94525`；本地第二份已核对并展开于 `.e01_backups/llvm_migration_20261025/compiler_controls_01/`。完整新trace保留服务器并记哈希。诊断结束再次核对R六个原件/权限及原Git差异、F八个涉及输入均保持，见归档内`compiler_controls/final_checks.json`。

## 11. P7首次候选验证与回退（2026-10-25，历史）

用户随后批准仅R实施固定[Ara #483](https://github.com/pulp-platform/ara/pull/483) `6b664a2c…`局部7增1删。候选编译成功，但初版同ELF对照在第51组VMACC e32/m2仍有数据错误，独立OPMVV默认EMUL=1缺口超出本次补丁范围；两次初版诊断还包含超出当前支持范围的非零vstart算术X/断言。用户已批准将该两组换为部分VL乘加，修订版54组ELF构建后，因候选另有失败而未继续运行，17项修订验收均未执行。

已按失败计划保存两版源码/ELF、候选差异/日志/trace及模型，再仅恢复R本轮dispatcher/Make，新C移入证据；4321项原输入及原Git差异匹配，F未写。原LLVM失败ELF `287c24ef…`从归档冻结但本轮未运行，不能声称465/0。**P7未验收，LLVM迁移仍停止，未恢复LLVM Makefile适配、未提交推送。**实际原因、逐项状态、备份与回退集中在[修复报告13.4](../reports/official_pr_failure_fixes_review.md#p7-implementation-result-20261025)，不以此前评估或P6结果替代P7验证。


<a id="llvm-resume-20261026"></a>

## 12. LLVM默认编译器迁移已完成（2026-10-26）

本次按用户要求先验证R，再同步并独立验证F。输入R HEAD为`4e30feec288f0157f2ae6c0fb9ea736314de902e`，F为此前已同步P7状态；WT、2 lanes、Ara VLEN=2048及原两处诊断修改保持。固定工具链为Ara `2895ba907…`配套LLVM20.1.0提交`24a30daaa559829ad079f2ff7f73eb4e18095f88`、newlib `2e4ecbb3f0d574d18eddb97eff9421db45fb0da7`和同LLVM提交的compiler-rt，安装在服务器`~/CheshireAra_maintenance/llvm_20.1.0_20261025/install`。

**当前两工程的所选裸机软件默认使用Clang/LLD/LLVM工具，输出均为`sw/build/llvm_p7`；实际编译日志及全部链接图不依赖目标GCC/GNU binutils/libgcc。** ABI保持`lp64d`，库/应用ISA分别保持`rv64gc/rv64gcv`，O2、medany保持，LTO继续启用。宿主g++继续用于VCS DPI；旧GCC安装、`sw/build/default`、前轮`llvm`产物及历史记录保留。迁移验收结束时尚未提交，R HEAD当时仍为P7提交；随后获用户授权的提交与推送见[12.4](#llvm-github-push-20261026)。

| 实际修改 | R | F |
| --- | --- | --- |
| 所选软件构建 | `sw/Makefile`切换工具、LTO、运行库、选项与镜像；保留原目标 | `sw/Makefile`同类适配，保持日常7/维护31/Ara11分组 |
| 历史根软件规则 | `sw/sw.mk`及`cheshire.mk`必要选项；仅工程外隔离验证 | 无根Makefile，不复制R入口 |
| 混合C/RVV示例 | `_e01/dma_vector_check/aw_config_20261020/src/vector_fixed.c` | `sw/tests/regressions/vector_fixed.c`；自动C加法与手写复制共存 |
| 当前C兼容 | R的`dma_long_2d.c`补当前HAL配置参数；两份RVV头删除void wrapper的返回值，保留调用 | HAL参数原已正确；`sw/deps/ara/include/rvv_test.h`同一行Clang兼容修正 |
| 默认运行与说明 | README及docs/gs，说明所选入口与上游历史流程的区别 | start仅改默认ELF/IMAGE目录；三份指南及既有来源清单 |

R现场`sw/tests/rvv_test.h`为ignored副本，受Git管理的头位于`.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/include/rvv_test.h`；两者均修正且哈希相同，不能只改ignored副本。F按现有目录映射适配，未复制R整份Makefile或另建编译器选择框架。实际差异为`evidence/R_final_task.patch`和`F_final.patch`；前者不夹带原两处诊断差异。

根软件规则只在工程外使用软件专用Make输入构建，未调用根all/hw-all、Bender或重生Boot ROM。ROM ELF按稀疏LMA映射至memh、原始bin，GPT对应bin/memh及sector42固件比对通过；SPM/DRAM运行库探针各152项0错，实际使用newlib memmove及compiler-rt 128位运算。这不代表全部历史根链接模式或任意高地址布局已经验证。

### 12.1 本轮DMA隐式RVV异常及软件设置修正

首轮第9项`dma_original`在PC `0x100001bc`执行Clang生成的`vsetivli`时VS仍为Off，trace记录Illegal Instruction（`tval=cc087057`），随后进入`trap_vector`的`j .`。已明确定位后主动停止这一例，保留实际SIM_ERROR结果与原38份产物，未把它计作合格负例或泛称硬件死锁。

固定LLVM源码`RISCVISelLowering.cpp::getOptimalMemOpType`仍可把普通C数组初始化/memcpy降为RVV，`-fno-vectorize/-fno-slp-vectorize`只关闭两个向量化优化过程，不能禁止这个后端行为。最小修正为R/F软件`TESTFLAGS`默认增加`-mno-implicit-float`，`vector_fixed`目标末尾明确恢复`-mimplicit-float`，保留其pragma自动向量化。固定版本LangRef/driver/属性合并源码和工程外试编译均确认：此设置禁止标量代码隐式使用向量/浮点寄存器，仍允许显式浮点运算和RVV汇编；不是软浮点ABI，也不修改FS/VS启动机制或RTL。

修正后R38份ELF已全部重建，仅`dma_original`、`dma_checked`、`p5_dma_1d`、`p5_dma_sequence`四份ELF变化；前8个已通过程序的完整ELF哈希全部一致，因此可以复用其同一P7仿真器下的实际结果。新的DMA ELF反汇编无RVV；mixed及fmatmul试编译哈希与已通过版本完全一致。第9项已重跑通过，其余矩阵也按各自判据完成。首轮产物/结果保存在本轮服务器目录`attempt_01/`，源码依据与试编译在`evidence/implicit_codegen_probe.json`及本地对应资料；首轮失败及旧设置下的产物均保留，不混作合格负例。

### 12.2 实际运行与结果

| 工程 | 新LLVM ELF | 主矩阵记录 | 正常PASS | SPI原限定告警 | 保留LLC未完成 | 预期负例 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| R | 38 | 40 | 36 | 1 | 1 | 2 |
| F | 49 | 51 | 47 | 1 | 1 | 2 |

R前8项在软件设置修正前已经通过；重新构建后逐份完整ELF及simv SHA均相同，故复用实际结果，不伪称重新运行。失败的第9项始终重跑。R实际调用为首轮9＋后轮32＋两个root探针＝43，F自身入口实际运行51次，合计94次，包含保留的首轮DMA诊断失败。运行串行、无波形、通常600秒，超时识别负例使用1秒。F的HelloWorld和SPI省略BINARY/IMAGE环境覆盖，验证了新默认输入路径。

| 检查内容 | R/F当前结果 |
| --- | --- |
| 自动C循环＋手写RVV | 六长度465项0错、复制22字节0错；报告和最终`auto_add`反汇编均有向量化。R本轮新构建ELF SHA为`287c24ef…`，与原失败归档相同；本轮不是拿归档ELF代替重建 |
| P7两项 | 54主组＋14控制组，共13416项0错，errors/control_errors/失败mask均0 |
| P6五项 | 508组/38452项0错 |
| P1–P5 | P1触发及64字节数据；P2三项835/124/483；P3两项177/753；P4六项5195；P5 18/138字节及backend/退休计数均通过。未覆盖的P3非整拍VL异常屏蔽仍保留 |
| 日常及访存 | HelloWorld、fmatmul、非stub CSR通过；RVV边界5976、访存/原子572项0错。CSR三次异常与ELF的vl/vlenb/vtype写零指令逐项相符；DMA实际保存submit=done=2、data_errors=0 |
| Serial RX | 64KiB、CPU并发192KiB、非对齐间断8193B均通过数据、保护区及DDR检查；统计按本轮实际值检查 |
| Ara可选指令组 | 仅F现有11目标：59 case/147组比较0错；R未另宣称运行这一组 |

SPI仍为`ASSERTION_OR_SIM_ERROR/2`、目标0：确认为原byte6/7两读两写四事件，READ_DATA_X字段和时刻一致；CPU trace的ROM PC `0200170e/1710`读取连续8字节，再经`02001716`调用及`0200049e/4a0`写出同一配置值`xxxx0000000f0f0f`。对照实际by-value配置调用和16字节结构体，尾部两padding字节相符；没有新增事件。不能改写成普通PASS或笼统忽略断言。

`default_long`仍为`INCOMPLETE/4`，2ms至3ms的85字段全部保持，next/done=3/1、read FIFO满/DMA r_ready=0/read busy=1与原控制签名相符，CPU无新异常。实际地址、索引和Bloom位变化已记录，不按旧GCC地址硬匹配。`unaligned16/dense32`则在当前LLVM下正常完成，实际IDs/done均[2,3]、polls分别[15,15]/[25,25]、case_errors=0，数据、间隙、源及保护区检查均执行；**没有修改LLC RTL，也不以这两种布局完成关闭历史LLC缺陷。** 目标失败负例返回41/入口1；1秒限时负例为TIMEOUT/124，均符合各自判据。

逐项原始结果及复核在`evidence/reference_runs.json`、`formal_runs.json`、`R_special_review_final.json`、`F_special_review_final.json`与`software_postcheck_R/F.json`；root探针见`root_probe_runs.json`。不是只按simv返回0判定，也不以主机耗时、内核周期或选项开启宣称性能/PPA改善。

### 12.3 保护、恢复与交付位置

服务器目录为`/home/zhaowy24/CheshireAra_maintenance/llvm_resume_20261026_tctflt0s/`，本地为仓库`.e01_backups/llvm_resume_20261026_tctflt0s/`。实施前R十原件加追加受Git管理的头、F八原件均两地保存并在独立目录实际展开比较内容/大小/权限；完成后R九文件、F八文件after也分别完成服务器和本地恢复检查。本轮保留LLVM修改，未执行生产回退。

R初始4395项＝4394项Git输入＋ignored头副本，修改9项，其余4386项及原两处诊断修改保持，HEAD/暂存区保持；F1054项修改8项，其他1046项内容、模式、链接均保持，未初始化Git。实际软件产物最终哈希仍与验证记录一致，默认Make干跑均Nothing to be done；F七个源/指南条目的当前SHA与来源清单相符，原revision/source_sha保留。保护结果见`evidence/final_protection.json`。

- 原件：`before/R_before.tar.gz`、`before/R_header_original.tar.gz`、`before/F_before.tar.gz`。R原包含两处诊断文件，回退只能选择本轮九个变更文件，不能覆盖诊断或后续修改。
- 完成源码：`after/R_final_after.tar.gz`（SHA `7b947b6815a0b626cb5ee1c24b25d293a332d8dc4231fbeac965c8ba07718414`）、`after/F_final_after.tar.gz`（SHA `28946b3be63c93148f4788e29e541f63bd4de88fe936acb2d285e9f9a197ab4f`）。两地实际恢复目录与检查JSON分别保存。
- 完整结果包：`final_evidence.tar.gz`，31783952字节、827成员，SHA `eacf3cee9760770b462115c5297762d788087ae90b3f138d26f4880d6959abc7`。两地SHA一致，本地逐成员读取并核对269份软件产物的哈希/大小/模式；含实际ELF/map/dump、日志、前后源码、原失败及SPI/LLC完整trace。其余完整CPU trace继续在服务器原运行目录，188份trace的哈希见`runtime_trace_manifest.json`，不声称全部trace已复制到本地。

回退前须逐项确认当前文件仍等于本轮after；只恢复本轮R九/F八文件或逆向本轮差异，发现后续修改则合并，不整树覆盖、不reset/clean。恢复默认路径后仍使用保留旧产物；不需要删除LLVM安装或任何历史证据。当前官方目录/集中配置/静态入口保持，不涉及SRAM宏、综合、板测、#479补测或上游发言；既有FS及覆盖边界保留。上述归档记录迁移验收结束时的未提交状态；后续GitHub发布另见12.4，不改写旧归档或F当时的来源快照。


<a id="llvm-github-push-20261026"></a>

### 12.4 LLVM修改已推送，其他工作区内容检查（2026-10-26）

用户明确授权推送并检查其他未推送部分。R仅提交8份已验证文件，提交[`6f2b2a3b`](https://github.com/lionelZhaowy/CheshireAraPULP/commit/6f2b2a3be50eeb15eb93c0ada2164029a102c94c)，父提交为P7 `4e30feec`；正常推送`personal HEAD:refs/heads/main`，随后SSH重新读取远端main，与新提交一致。既有8个个人发布标签保持；R另12个本地继承标签未镜像到personal，但已逐对象核对与官方发布一致，不属于未发布私人改动。无强推、无上游PR操作。

提交包含`cheshire.mk`、`sw/sw.mk`、`sw/Makefile`、`_e01/dma_vector_check/aw_config_20261020/src/vector_fixed.c`、`_e01/dma_vector_check/fix_validation_20261020/src/dma_long_2d.c`、`.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/include/rvv_test.h`、`README.md`、`docs/gs.md`，合计123增62删。提交前后逐文件内容和模式与验收记录一致，暂存差异检查通过；本次只处理Git发布，未重新构建或仿真，沿用12.2的实际结果。

剩余内容分别为：

- **R无未推送分支提交**，暂存区为空；原两处诊断修改`_e01/dma_vector_check/pr80_204_20261021/llc_recheck/probe.tcl`、`_e01/dma_vector_check/slink_llc_rx_20261021/final/tb_slink_llc_rx.sv`仍未提交，内容和权限保持，未混入LLVM提交。
- **R忽略项仍留现场**：完整清单858条路径或目录，涉及运行记录/历史、构建产物、环境、依赖子目录等，不能全部称为编译产物，也不等于已纳入Git备份。`sw/tests/rvv_test.h`为忽略的副本，与本次已提交的受管头内容一致。未强制加入忽略文件或上传整份历史目录。
- **本地旧仓库是另一个仓库`lionelZhaowy/Cheshire_Ara_Orig`**：当前`mp/ara-pulp-v2` HEAD与实际远端main同为`ca839567…`，没有待推送的当前分支提交；有17份已修改和4份未跟踪文件，含工作约定、共享状态、E01/P01/LVDS等文档、两幅SVG及ABC记录。它们未提交或推送。逐文件清单保存在本次发布目录的`local_workspace_before.json`和`local_branch_review.json`，不能当作R待发布代码。
- 本地另一个`main`为官方历史`79a5f5c4…`；官方GitHub比较确认它是当前官方main `6c6dd5e8…`的祖先，16个本地继承标签也与官方已发布对象一致。相对个人main额外的48条官方历史提交不是48份未发布私人改动；未向个人仓库镜像这些分支/标签，未fetch或切换分支。
- **F无Git**：已同步并独立验证的正式工程文件保持，本次没有初始化Git或另行上传F。服务器工程外LLVM安装及历史测试完整产物继续按12.3位置保留，不包含在这8份源码提交中。

本次记录在服务器`~/CheshireAra_maintenance/llvm_resume_20261026_tctflt0s/github_push/`及本地`.e01_backups/llvm_resume_20261026_tctflt0s/github_push/`。提交前完整工作区差异和8文件差异、原文件状态/哈希、忽略项清单已先两地保存；随后增量`llvm_commit.bundle`两地SHA256为`379f5bd7e4be45898fde1350be3b71a6c2778d4c3c7142f7d66139ccced89644`，服务器`git bundle verify`通过，本地内容哈希核对通过。该增量包需要父基线`4e30feec`，不能当作独立完整仓库恢复包。`push_result.json`记录远端读回、剩余状态及来源保护结果。本地本次文档修改前原件也保存在`docs_before/`，没有提交本地仓库。


<a id="workspace-publish-20261026"></a>

### 12.5 按后续授权发布剩余两处诊断及本地工作区（2026-10-26）

用户已明确要求将本地当前工程提交到其对应仓库，并同步R剩余两处修改。本节取代12.4中的“原诊断和本地文件仍未提交”作为最新处理进展，保留此前快照。

R仅两文件`probe.tcl`和`tb_slink_llc_rx.sv`提交为[`29f1e6f9`](https://github.com/lionelZhaowy/CheshireAraPULP/commit/29f1e6f935f028ae947a1eae113370e5fe8db0b7)，父提交为LLVM `6f2b2a3b`，669增114删；正常推送personal/main并读回相同SHA。受管工作区干净，无未推送分支提交。提交前后哈希/权限与12.4保护的两份诊断文件相同，未修改功能RTL或重新运行测试，不以发布诊断文件宣称LLC已修复。

本地原17修改＋4新增的21文件均按本次授权纳入本地当前分支`mp/ara-pulp-v2`提交，目标远端为`git@github.com:lionelZhaowy/Cheshire_Ara_Orig.git`的main；不是官方origin/main，也不把本地旧源码同步到正式F。文件归属和内容保持，只在现有交接/状态中追加本次发布记录。此前“本地未提交”是授权前快照；本次精确提交SHA、推送结果和远端读回保存在本地发布目录的`local_push_result.json`，不在同一提交的正文内预先填写自身SHA。

发布目录为本地`.e01_backups/workspace_publish_20261026_8jhtomhm/`及服务器工程外`~/CheshireAra_maintenance/workspace_publish_20261026_8jhtomhm/`。本地21文件提交前原件归档已逐成员读取核对；R两原件/差异双份保存并检查内容/模式，提交增量bundle双份SHA为`212ae686192f7f449ab279df67d84169350c6ba8ff0fed6f501fec6809c41c95`，需父基线`6f2b2a3b`，服务器verify通过。R发布结果见`push_result.json`，本地副本在`server/`下。忽略的备份、环境、工具链、产物及官方标签未批量上传；没有新增功能验证或改动F。
