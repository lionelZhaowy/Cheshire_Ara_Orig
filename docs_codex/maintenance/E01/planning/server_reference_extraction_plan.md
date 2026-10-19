# E01 / 243 服务器向量参考工程与固定工程实施方案

分步命令与简要解释见[同版本重建速查](server_reference_rebuild_guide.md)；实际执行结果及未关闭项见 [E01 最新交接](../../../handoffs/E01_fixed_vector_extraction.md)。下文阶段 0/第 1 步的“目录为空、尚未编译、等待第 2 步”等保留为当时快照，不代表当前状态；参考工程已有标量与单个修正 FS 后 fmatmul 的运行证据，完整参考验收和独立提取仍未完成。

**2026-10-19 用户确认的配置管理更新：**固定 CVA6＋Ara 功能组合，在 `src/config/` 集中维护参数，每次构建选择一个有效配置；先保持 2 lanes/VLEN 2048 及原 Cache/LLC 基线完成提取对照，再逐步开放参数，以应用验证和面积、时序、功耗评估确定产品配置。原“长期只用一个固定参数配置”的限制被替代，具体候选值和支持组合尚未验收。本次只同步文档，未改参数、提取工程或执行试验。规范见 [02 第 3.3 节](../../../02_Cheshire_Ara_ASIC_Extraction_Handoff.md#parameter-policy)，评估方法见[资源指南 Q7/Q8](../../../engineering/Fixed_Vector_SoC_Resource_Guide.md#q7)。

2026-10-18 用户补充“如无必要、勿增实体”：优先直接使用官方入口，不为记录或预防假设故障新增通用框架。下文原先要求的独立 SV/DPI 前置探针改为按需诊断，先由参考工程实际构建检验许可和联编；既定日志、超时及功能验收要求保留。

更新：2026-10-18。输入：`mp/ara-pulp-v2` / `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`。本轮完成只读调查和方案，**未复制工程、未编译、未展开、未仿真**。

同日实施增量：用户已确认并完成第1步，见[实际报告](../reports/toolchain_preflight.md)。工具链最小编译/链接已执行，发现并保留libgcc特定高地址重定位限制；未执行VCS或目标程序。下文只读调查表保留为阶段0快照，不能替代实际报告。第2步等待确认。

同日用户调整来源：明确不复制本地官方工程，希望从 GitHub 官方仓库重建，并要求先分析两种方案。**原第2步“复制本地快照”已被替代，不能继续照旧执行。** 目前仅完成来源方案比较（第8节）；官方具体提交、依赖组合及环境配方尚未冻结，未授权直接采用最新主线或重建/升级工具链。第4节原复制流程保留为旧方案依据，不再是待执行动作。

同日进一步澄清（当前有效）：用户明确重建当初克隆的 **`mp/ara-pulp-v2` 同版本**，不重新选新版官方工程。按本地Git历史定位，原始上游基准为 `e040b7bbc7851a37faff3c4657ff8d656cc6e20a`，配套依赖沿该提交锁文件；服务器负责重新获取、搭建环境和构建。本地后加修改逐项对照，不自动回放。上段“版本待选”由本澄清取代；剩余工作是核对该历史提交的官方可获取性和服务器环境，不再评选最新主线。此澄清未启动第2步下载/构建。

用户明确要求人工把关：先规划，每一步报告后等待确认，再执行该步。此要求取代原提示词前半段的连续实施授权。普通实现选择在已确认步骤内处理；参数探索按已确认的具体试验范围执行，超出开放范围的结构变化、受保护工程修改或依赖升级另报具体问题。本文更新本身不构成任何配置试验的执行授权。

## 1. 输入、目标与保护范围

| 对象 | 本轮核实与计划 |
| --- | --- |
| 本地输入 | `/home/zhaowenyao/RISC_CVA6_prj/cheshire_ara`，上述 HEAD；源码以当前磁盘内容和后续逐文件 SHA256 为准 |
| 未提交输入 | 7 个已有文档修改、2 个未跟踪文档；包括 PROJECT_STATE、AGENT_TASKS、handoffs/README、架构/排期/资源文档。本轮不覆盖 |
| 参考工程 | `zhaowy24@172.16.0.243:/home/zhaowy24/CheshireAraPULP`，本轮 SSH 检查：存在且为空 |
| 固定工程 | `zhaowy24@172.16.0.243:/home/zhaowy24/CheshireAra`，本轮 SSH 检查：存在且为空；这是 `cheshire_ara_asic` 工程的实际目录名，不额外嵌套同名目录 |
| 只读参考 | `/home/zhaowy24/Desktop/mycheshire_24`；不在其目录内构建、修改或清理 |
| 首次提取边界 | 保留地址、中断、外设、LLC/SPM、原子路径和既有 Boot ROM；不实施 v1 产品新增 IP、外设裁切、真实 DDR/工艺宏 |

实施前再次检查路径内容。预期为空的目标出现新文件时先比对，不用覆盖、删除或改名来消除冲突。参考工程内新增 `_e01/` 保存本次适配、清单导出、探针和证据，保持官方主目录可辨识。

依赖来源以 `.bender/SNAPSHOT.tsv`、`.bender/UPSTREAM.lock`、`Bender.local/lock/yml` 配套记录，不能由目录名或锁文件替代当前文件内容。主要记录值：

| 组件 | 上游来源记录 |
| --- | --- |
| Ara | `2895ba907e9eb14b3464609dc791a969d159a7c3` |
| CVA6 | `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c` |
| AXI | `39f5f2d51c5e524f6fc5cf8b6e901f7dcc5622d7` |
| LLC | `559bcbd09a5a884dbe31e2d72fd95d024e357f39` |
| 原子适配器 | `0ac3a78fe342c5a5b9b10bff49d58897f773059e` |
| 根软件 printf 子模块 | 本地实际展开为 `0dd4b64bc778bf55229428cefccba4c0a81f384b` |

根 `sw/deps/cva6-sdk` 未初始化；Ara 内另有 SDK 快照，不能混称根 SDK 已完备。首次裸机闭环不以 Linux SDK 或可选 benchmark 为前置。已纳入主仓库的本地修改由输入 HEAD 及文件内容保留，后续新补丁单独登记。

## 2. 服务器和 TTY 的实际情况

只读 SSH 成功；系统为 x86_64、EL8 内核。`/home` 约 36 TiB 可用，64 个逻辑 CPU；容量只是本次查询快照，不据此占满机器。`vcs -full64 -ID` 本轮退出 0，返回 `VCS W-2024.09-SP1_Full64`。未测试许可证 checkout 或实际编译。

TTY 目录为：

```text
mycheshire_24/
  src/filelist.f
  src/cheshire_soc/<component>/
  src/tb/{src,models}/
  sim/{scripts,work,log}/
  sw/tests/
```

实际检查所得：

- `src/filelist.f` 为 308 个不重复源码条目、12 个 include 目录，从 `sim/work` 解析均存在；这只是路径检查。
- 第 177 行为 `cv64a6_imafdchsclic_sv39_wb_config_pkg.sv`，无 Ara 源码/宏；TB 默认 `SelectedCfg=0`。
- TTY 的配置 3 是 **vCLIC**；本地当前源码的配置 3 才是 **Ara**。不能把两者的 SELCFG 数字互用。
- `compile.sh`、`sim.sh`、`verdi.sh` 写死 `/home/dell/Desktop/test/mycheshire_24`，与本次登录位置不同。前者含 `-full64`、本机 C++/DPI、`-j4`、`-fgp` 和较重调试选项；后者固定旧 ELF 和 Serial Link preload，管道没有可靠失败传播。
- TTY TB 强制调用 FSDB dump；不把 Verdi/FSDB 作为首轮批处理必需项。其 TB/SoC 源与本地有差别，不能整套复制后视为当前源码参考。
- `sw/` 检查到测试源码和已有 ELF/dump，没有完整启动、链接、运行库构建目录；已有 `simv`、日志、波形、ELF 均不作为本轮验证证据。

借鉴的是目录约定与 VCS/DPI 流程。新脚本须自行定位根目录，显式设置输出、编译组、工具路径、超时、退出码与结果判据；不直接复用 TTY 的绝对路径、标量清单和现成 TB。

## 3. 工具链结论及待执行检查

| 类别 | 已只读核实 | 当前结论 |
| --- | --- | --- |
| RISC-V 编译器 | `/opt/riscv/bin/riscv64-unknown-elf-gcc`，13.2.0 (`gc891d8dc23e`)，triple `riscv64-unknown-elf` | 首选待测候选；尚未实际编译 |
| ISA/ABI 默认 | `-Q --help=target`：`rv64imafdc_zicsr_zifencei`、`lp64d`，默认 code model 为 medlow | 工程显式指定 ISA/ABI；软件按当前入口使用 medany |
| 汇编器/链接器 | GNU as/ld 2.43.1；已查询 GCC 实际选择的工具路径 | 指令与重定位能力待最小测试 |
| 运行库/multilib | `-print-multi-lib` 仅 `.;`；libc.a、libgcc.a、newlib.h、riscv_vector.h 存在 | 一个 multilib 不直接说明 RVV 缺失；须实链两组 ISA 并核查实际库 |
| 服务器本机 C/C++ | PATH 为 `/opt/rh/gcc-toolset-13/root/usr/bin/{gcc,g++}` 13.3.1，triple `x86_64-redhat-linux`；`/usr/bin/gcc` 为 8.5.0 | 与 RISC-V 工具链分开；DPI 编译、VCS 联编和动态库兼容待验证 |
| 其他工具 | make 4.2.1、默认 Python 3.6.8、另有 `/usr/bin/python3.9` 3.9.25、python3.11 3.11.13、python3.12 3.12.14；rsync 3.1.3、Bender 0.32.1、timeout 可用，rg 不在远端 PATH | 官方 `docs/gs.md` 要求 Python >=3.9；必要生成步骤显式选现有 python3.9 并检查 requirements，不能沿用默认 python3。Python 包尚未验证，不升级系统 |

当前本地根软件 ISA 为 `rv64gc_zifencei`，Ara Cheshire 软件入口改为 `rv64gcv_zifencei`，ABI 均为 `lp64d`。ISA 与调用约定分别明确指定；其含义参见 [GCC 13.2 官方选项](https://gcc.gnu.org/onlinedocs/gcc-13.2.0/gcc/RISC-V-Options.html)。现有标量运行库是否可用于本次向量软件，最终以实际链接输入、反汇编和目标运行确认。

Ara README 声明 RVV 1.0，实际 dispatcher 含 vma/vta 和 vsetivli；同目录旧 DEPENDENCIES.md 仍提 0.9，存在文档冲突。采用当前 README、实际 RTL 和 Cheshire 集成入口的 1.0 路线，不据旧说明安装 0.9 工具链。Ara 独立 apps 的 LLVM 建议不等同于本轮必须构建全部 apps/LLVM。

下一步的最小探针：

1. 分别以 `-march=rv64gc_zifencei`、`-march=rv64gcv_zifencei`，`-mabi=lp64d -mcmodel=medany` 查询库选择，编译 `.S`/C、链接并生成 map、`readelf` 和 `objdump`。标量覆盖基本整数、浮点及原子指令；向量覆盖 vsetvli/vsetivli、整数 load/add/store 和一个简单浮点向量操作。用明确的运算引用检查 libc/libgcc 的实际解析，不能只看库文件存在。
2. 区分裸指令探针与完整启动/运行库：探针通过后，在参考源码到位时，用现行 crt0、common.ldh、spm/rom/dram 链接布局及必要 libcheshire 源重建小程序；不运行 Linux 或整套 benchmark。
   `common.ldh` 会丢弃最终 ELF 的 `.riscv.attributes`；ISA 属性同时检查中间 `.o`，最终 ELF 检查实际指令。软件 SPM 链接窗口为 64 KiB，硬件 LLC/SPM 为 128 KiB，两者不混同。
3. 服务器本机 C++ 编译简单程序以及复制的 `elfloader.cpp`，使用实际 VCS `svdpi.h`；后续小型 SV/DPI 运行才验证 VCS 联编与许可。不能用交叉编译器生成宿主 DPI。
4. 保存每条命令、版本、输入 SHA256、退出码、输出和失败日志。不适配时先报告具体汇编、ABI、重定位、runtime 或 intrinsic 缺项；不覆盖 `/opt`，不自动安装新工具。

## 4. 参考工程重建与固定配置

当前本地 [官方仿真说明](../../../../docs/tg/sim.md) 明列 VCS >=2024.09。Ara `cheshire/Makefile:29,60–62` 提供向量 targets/defines，并调用根 VCS 清单生成；根 `cheshire.mk:158–160` 使用 `bender script vcs`。官方 VCS start 已有 `-full64` 和 ELF DPI。这是存在官方入口的源码证据，尚非本组合运行证据。

原本地快照复制方案（历史，已被第 8 节同版本 GitHub 重建方向替代；以下 1—6 条不作为当前执行步骤）：

1. 在本地建立输入清单，复制当前磁盘的必要官方目录、26 项硬件依赖快照、已展开的必要软件子模块、include、现有生成 RTL/头文件、模型及许可证。保留来源结构；传输前后 SHA256 比对。不使用 `git archive HEAD` 丢失实际子模块或工作树内容，也不复制旧构建输出来充当新验证。
2. 参考根保留 `Makefile`、`cheshire.mk`、`hw/`、`sw/`、`target/`、`.bender/` 和 Bender 来源文件。版本元数据、纳入/排除清单及差异放 `_e01/provenance/`；不复制凭据、Git 对象库、FPGA/EDA 缓存、旧 ELF/库/波形。可选 Linux/benchmark 大数据排除项逐项记录，不声称复制了完整 SDK。
3. 在新参考目录内用 Bender 本地模式受控导出一次正确向量清单；同时归档 VCS 分组清单和结构化信息。不更新依赖、不下载。若必要路径缺失，停止该导出并报告，按 02 规格有限回退，不修整个旧管理系统。
4. 采用官方支持的 `sim/test` 目标及 Ara targets：`rtl cva6 cv64a6_imafdcv_sv39 exclude_first_pass_decoder`，宏 `ARA NR_LANES=2 VLEN=2048`。实际命令按已安装 Bender 的帮助和官方 recipe 确认，明确 `vlogan`/`vcs` 均使用 64 位模式。
5. 不直接跑 `make all`/`ara-chs-all`。根 make 在 `.chs_deps` 缺失时可能触发 checkout/submodule，模型规则可能下载；这些入口先限定依赖/生成步骤。归档原入口；仅在新目录补必要的离线构建包装和最小兼容修改。
6. 本地现成 `compile.cheshire_soc.sh` 含旧绝对路径、标量 profile、两份 decoder，不能直接运行。官方 start 的参数传递须经实际展开核验，管道退出状态由受控包装保证；把本次适配与官方原件区别记录。首次保留已生成的 ROM/寄存器 RTL；如确需重生成，先验证解释器与对应包，不因主机存在 Python 就认定官方生成器可运行。

当前参考来源为服务器 `~/CheshireAraPULP` 的官方历史版本重建及已记录的必要修正，提取目标为 `~/CheshireAra`。本地副本用于差异审查，不直接回放到参考工程；重建入口及实测状态分别查重建速查和最新交接。后续提取仍遵守保护、离线独立和来源记录要求。

首次提取对照的基线值保持，后续参数试验不覆盖这份基线记录：

| 项目 | 参考 / 固定工程共同基线 |
| --- | --- |
| CPU | `cv64a6_imafdcv_sv39`，RVV=1，WT D-cache |
| SoC/Ara | 当前 `gen_cheshire_ara_cfg()`：Ara=1、2 lanes、VLEN=2048 |
| decoder | Ara 真实 `cva6_accel_first_pass_decoder`；排除 CVA6 同名 stub |
| LLC/SPM | 8 ways × 256 lines × 8 blocks × 8 bytes = 128 KiB，保留原子适配和 Boot ROM 初始化 |
| 其余 | 完整 DefaultCfg 实际快照；48-bit 地址、64-bit AXI、RTC=32768、PlatformRom=0，地址/IRQ/外设不重排 |
| 验证模型 | `UseDramSys=0`，沿现有 AXI memory model；不是 DDR Controller/PHY 验证 |

CPU profile 的 `VLEN=64` 是另一字段，保持原值；不能按 Ara VLEN 修改。参考 TB 的 `SelectedCfg=3` 只选 SoC，仍须独立选择 CPU profile。展开时打印/断言 CPU RVV、SoC Ara、lane/VLEN、LLC容量与派生位宽，证明实际选中了目标组合。

提取工程在 `src/config/` 集中保存唯一向量 CPU profile 副本、完整 SoC 配置包及参数说明；每次构建导出一个确定配置。沿用 `gen_cva6_cfg()`、`build_config()`、`CHESHIRE_TYPEDEF_ALL` 等配置和类型派生；仿真 fixture 与后续综合共同使用该配置和 wrapper，TB 不再用 `SELCFG` 或私有字段改写硬件配置，不重写底层参数化 IP。

保持可复现基线和各候选的有效配置快照，编译输出按配置隔离、测试输出按运行隔离，避免复用另一配置的 `simv`。首次对照完成后，先开放 L1 容量和 LLC 行数，再按瓶颈评估预测器/TLB/队列/VLEN；lane、Cache 路数/行长、总线宽度或 Cache 类型单独评估。候选值不等于支持列表，分别记录静态约束、定向测试和完整候选回归状态。宏按实际消费者核查，不能仅修改 `NR_LANES/VLEN` 就认定当前 Cheshire 的 `Cfg.AraNrLanes/AraVLEN` 已改变。

## 5. 对齐 TTY 的提取目录

```text
~/CheshireAra/
  README.md
  src/
    config/
      cv64a6_imafdcv_sv39_config_pkg.sv # 唯一 cva6_config_pkg；向量 CPU 配置副本
      cheshire_ara_asic_cfg_pkg.sv     # 本次有效 SoC 配置及统一派生出口
      README.md                       # 参数含义、覆盖链、约束与验证状态
    top/cheshire_ara_asic_soc.sv
    cheshire_soc/cheshire_top/        # 对齐 TTY 的 SoC 源路径
    cheshire_soc/<component>/        # CVA6、Ara、AXI、LLC 等必要源/include
    tb/{src,dpi,models}/             # TB、VIP、DPI、存储/外设模型
    filelists/{rtl.f,sim.f,synth.f}   # 明确路径基准与编译组
    filelist.f                      # TTY 风格仿真入口
  sim/{scripts,work,log}/             # 输出按配置/运行隔离，保存有效配置快照
  sw/{startup,link,lib,include,tests,bootrom,build}/
  tech/{sim,asic}/
  constraints/
  provenance/{source_manifest.tsv,configuration.md,patches,original_manifests}/
  LICENSES/
```

目录只描述待实施职责，不表示已经创建。`src/cheshire_soc` 保存功能 RTL/vendor；`src/tb` 保存验证源码；`sim/scripts` 管理仿真脚本；`sw` 保存可重建软件。`src/config/` 与 02 规格一致，不新增第二个硬件配置入口，不同时编译多份同名配置包。技术单元从功能源中分责管理，同名模型只选一份。`synth.f` 在工艺映射未就绪时须明确拒绝最终工艺构建，不能把行为 SRAM 当最终宏。

静态清单保留顺序、include、宏及 VCS 编译单元分组；如单个 `.f` 无法表达作用域，使用有序分组清单配合简单脚本。禁止递归通配符。来源 manifest 记录原路径、组件版本、原/新 SHA256、许可证、用途和改动说明；工具链安装路径是显式外部依赖，原仓库和 TTY 目录不是。

源码闭包覆盖已声明支持的参数范围，保留所选向量功能组合的 package/include、参数化实现及相关 generate/宽度转换/技术单元分支；不能根据一次展开结果删除所有未实例化代码。增加支持范围或切换实现时先检查闭包，再更新静态清单和验证记录，不恢复日常 Bender 解析。

## 6. V01 验收用例和证据

| 用例 | 验收内容 |
| --- | --- |
| 标量小程序 | 从复位执行原 Boot ROM，观察 LLC BIST 完成、全 SPM 配置与栈建立；载入新编译程序并核对明确结果/退出值 |
| ROM 完整启动 | 另跑 `BOOTMODE=2` SPI raw 小镜像：由原 ROM 读介质、搬到 SPM、交接执行；不修改 CPU PC，不用直接 ELF 加载替代。构造从 flash offset 0 开始的 `.rom.bin`/memh，核对 LMA/VMA 和 raw fallback 读取范围，预留有效填充值 |
| RVV 结果测试 | SEW=32/64、LMUL=1，运行时读取 VLMAX，取 N=0、1、VLMAX−1、VLMAX、VLMAX+3、2×VLMAX+5；strip-mining 每轮使用实际 VL，整数运算逐项对照标量金值，并做小型精确浮点算例 |
| 尾部/越界 | 输入输出前后哨兵、尾轮检查；仅检查有效元素与内存边界，不对 tail-agnostic 寄存器尾部作确定值假设 |
| 基础访存 | SPM 与 `0x80000000` 起的 DDR 模型区，按合法对齐的 8/16/32/64-bit load/store、字节使能、跨 cache-line 数组与确定图样读回 |
| 原子 | AMO add/swap、LR/SC 成功和有界重试，核对返回旧值/最终内存；选当前非缓存可达测试地址或明确维护，保留原子适配通路。无竞争场景不能强制要求 SC 必须失败；首次不扩展成 DMA 竞争验证 |
| 失败传播 | 故意结果不匹配的小负例应被脚本标 FAIL 并非零返回；正常 PASS、目标退出码及 simv 退出码分别记录 |

普通 JTAG preload 当前先等待 ROM 配 LLC，随后 halt/load/改 dpc：可证明部分初始化，不能代替上表 ROM 启动项。官方 TB 支持 SPI 自主启动，SD 分支明确不支持；首轮不恢复 GPT/Linux 全套流程。

历史检查发现原 `crt0.S` 不统一开 VS，HelloWorld 只在 main 中开 VS；最初建议在独立启动副本中补齐初始化。后续用户已直接修改服务器 `crt0.S`，显式设置 FS=Clean，并通过单个 fmatmul，详见 [E01 交接](../../../handoffs/E01_fixed_vector_extraction.md)。提取时保留并溯源该兼容修正，重新核对 VS/FS 在任何可能的向量/浮点指令前已正确初始化及反汇编顺序，不恢复旧 FS 写法；两工程使用相同输入，FS Dirty 状态跟踪原因仍未关闭。

已知启动问题保持显式：默认 PlatformRom=0 不触发其返回缺陷；ROM C 入口栈对齐及载荷返回链仍须观测，首次不顺手修改原 ROM。若阻塞目标用例，先定位实际指令/官方最小修复，再报告需增加的具体修复范围。原软件手册 passive start 位与 C 源存在差异（当前 C 用 scratch[2] 的 bit1，bit0 用于完成）；本方案主验收走已有 SPI 路径，未来补 passive 测试时必须核对实际 ROM，不照旧文字写位。

每条结果绑定源码清单 SHA、配置快照、软件 ELF/image SHA、命令、工具版本、超时和退出值。对照参考/提取的配置、结果与必要初始化行为，不要求时间戳完全相同。先用同一批 ELF/image 隔离硬件差异，再在提取工程内重新构建软件并重跑，验证软件独立性。

参数试验在基线对照及独立性验收后分步进行。每次先检查参数约束与实际展开，再针对变更覆盖新增索引/地址边界、冲突替换、脏行回写/flush、SPM 启动以及向量尾部/mask/跨 lane 等行为；完整候选回归还覆盖适用的并发、背压、原子及异常场景。每层分别记录结果，既有 FS Dirty 等未关闭问题不能由参数改变后的单例成功隐去。

应用对照固定算法、输入和编译选项，尽量复用同一 ELF；明确存储位置、冷热状态、Cache/SPM 分配、测量区间与频率，分别记录目标周期数和端到端时间，不将 VCS 主机耗时当作芯片性能。**当前启动默认全 SPM，测 LLC 缓存收益必须启用 Cache ways 并保护栈/程序数据。** 先单变量比较，再检验候选组合。面积、时序、功耗比较使用一致工艺/宏/约束和测量口径；Pad 围出的空间不免除供电、布线、测试和带宽要求。详细记录字段沿用资源指南，不新增通用试验框架。

## 7. 分步确认与交付

以下每一步均须先报告动作/写入路径，取得用户对该步的确认后执行；完成即汇报结果和下一步，不自动跨步。

| 步骤 | 动作与写入范围 | 通过后交付 |
| --- | --- | --- |
| 0（本轮） | 只读本地/服务器；只新增本地 E01 方案、证据摘要和主题交接 | 当前事实、目录映射、实施/验收方案；无工程运行结论 |
| 1（已执行） | 仅在 `~/CheshireAraPULP/_e01/preflight/` 新建最小工具链探针；复制必要小输入；实际编译/链接/反汇编 RISC-V 标量/RVV 和本机 C++/ELF loader | [结果](../reports/toolchain_preflight.md)：SPM与DPI源编译通过，libgcc特定高地址链接失败未关闭；不编译完整SoC，不写提取目录 |
| 2（同版本方向已确认，执行待确认） | 从GitHub官方仓库重新获取当初 `mp/ara-pulp-v2` 的历史提交 `e040b7bbc…` 及其锁定依赖，在 `~/CheshireAraPULP` 搭建环境并重建；先核实官方可获取性。原本地快照只用于差异审查，不作复制源；保留preflight证据 | 官方历史提交与依赖锁、差异分类、服务器环境和必要补丁；具体执行子步骤重新报告，尚不称参考验收通过 |
| 3 | 优先用参考工程官方入口进行 VCS 编译、展开及许可/联编检查；出现错误时按需增加最小探针；依次运行标量、ROM启动、RVV、访存/原子 | 参考向量基线的实际 PASS/FAIL、日志及缺口；失败先定位，不带病称对照基线 |
| 4 | 在 `~/CheshireAra` 提取集中配置/类型/共同 wrapper、静态清单、软件和来源记录；保持原基线重建并运行相同测试 | 独立工程与参考结果对照、可复制命令、配置支持状态和已知限制 |
| 5 | 复制提取工程源码到预先检查不存在的独立验收路径，使用全新输出重新构建 RTL 和软件并重跑 | 搬迁验证与依赖审计；最终交接和最小下一步 |
| 6（基线独立验收后，另行分步确认） | 按开放范围选择参数试验，独立构建并进行定向/候选回归和应用比较；工艺资料具备后评估面积、时序和功耗 | 有效配置及输入快照、分层验证状态、性能/物理实现证据和未关闭项；不预定最终参数 |

拟用最终入口为 `bash sim/scripts/compile.sh`、`bash sim/scripts/run_tests.sh` 与 `make -C sw`；这些是待实现接口，**目前不能当已可执行命令**。每步执行前交付实际脚本/参数，日志按步骤与测试分目录，不覆盖失败证据。

资源上限建议：单个 VCS 构建，编译并发最多 2，测试串行；探针单条 60 秒、全量编译/展开各 30 分钟、单个仿真默认 10 分钟硬超时，SPI 启动如需更长先报实际进展再调整。使用后台作业/短轮询保持可报告，避免长阻塞等待。默认不启用 FGP/全量 FSDB，首错定位后才加必要波形。

独立性审计覆盖所有执行中的清单、脚本、软件依赖、include、符号链接及构建实际输入；原路径允许出现在 provenance 的来源记录中，不允许参与执行。搬迁位置从空输出重新构建，记录实际访问/编译输入；不重命名、移走或限制访问原工程/TTY 以做验证。

历史阶段 1 的下一步曾为表中第 2 步，不能据此重新下载或覆盖现有参考工程；当前实际进度和最小下一步以页首 E01 交接为准，仍按用户逐步确认执行。第 1 步工具链检查仅覆盖所测用例，不等于运行库全部适配；通用模型仿真通过不等于 ASIC 工艺、真实 DDR 或流片验收。

## 8. 官方重新获取与本地快照复现的比较（来源调整）

用户担心WSL时期工具链/环境报错后存在绕过，因此选择官方GitHub来源。源代码来源、主机环境、交叉工具链/运行库是三个独立对象：复制源码不等于复制WSL安装环境；从GitHub获取源码也不自动修复服务器 `/opt/riscv` 的S01-T01。

| 维度 | 原方案：本地实际快照 | 新方向：官方固定版本重建 |
| --- | --- | --- |
| 首先证明什么 | 当前本地实现能在服务器重新构建和运行 | 明确的官方原始版本组合能在可记录的环境中构建和运行 |
| 本地修改 | 随源码带入，逐项归档后验证 | 默认不带入；只作问题定位参考，确有需要才形成新的最小补丁 |
| 版本控制 | 当前磁盘内容＋主仓库HEAD＋依赖SHA | 官方仓库URL＋主工程提交＋依赖锁/子模块提交＋后续补丁 |
| 环境问题 | 在服务器重新搭建，仍可暴露问题 | 同样需要独立准备/验证，clone本身不包含已验证工具环境 |
| 成本/风险 | 通常迁移较快，但继承历史源码绕过 | 下载/版本配套/生成步骤较多，旧错误可能重新出现；问题来源更容易区分 |
| 与现有FPGA的关系 | 源码连续性较强，但没有重新板测保证 | 有意建立新来源基线；旧HelloWorld不能转移成新基线证据 |
| 后续提取 | 从实测本地快照参考提取 | 从实测官方重建参考提取；两者最终都需静态清单和离线独立验收 |

本轮定向差异证据：

- 本地首次保存提交 `4175f440144fba38a2c7d3b7411e26b51d4c5e56` 的父提交是 `e040b7bbc7851a37faff3c4657ff8d656cc6e20a`；本地历史 `origin/mp/ara-pulp-v2` 也指向后者。它是待核实的官方来源候选，不宣称当前远端分支仍在该位置。
- 该候选的 `Bender.lock` 指向 Ara `2895ba907e9eb14b3464609dc791a969d159a7c3`、CVA6 `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c`，与本地快照记录吻合。可以先评估同版本官方重建，避免同时引入全套升级。
- `git diff e040b7bbc HEAD -- sw/sw.mk` 确认关闭 GPT 镜像规则及其测试构建项；根HelloWorld有VS/printf改动。不能把所有本地差异统称工具链错误或硬件修复。
- Ara子仓库实际HEAD为上述提交，`git diff`确认8个受跟踪文件修改：板卡默认VCU128→VCU118、`eew/printf`默认参数、C函数/类型和打印相关修改、`vector_helloworld.c`加入O0并将一处向量store intrinsic替换为内联汇编。原始报错日志未找到，本轮不推断每项修改的必要性和正确性。
- 本轮查看的CVA6子仓库没有工作树差异；根hw/TB源相对该父提交也未显示差异。此有限检查不代表已审计所有26项依赖或全部生成文件。

“从官方获取固定版本”和“直接取最新main”必须分开：最新版本可能更换CPU集成、参数和构建配方，属于另一个版本迁移决策。当前在线 [Getting Started](https://pulp-platform.github.io/cheshire/gs/) 已要求Python>=3.11并使用pyproject.toml/uv.lock；本地版本为Python>=3.9和requirements.txt。不能拿最新文档套用旧提交，或把旧固定CPU profile默认认为最新主线仍支持。

建议把下一步拆成可审查的小步骤：先确认官方Ara集成提交及配套锁文件，列出本地差异处理表和该版本所需环境；随后按确认的组合从官方获取，默认不回放本地改动，只执行当前裸机向量/VCS任务需要的官方步骤。必要修改以原始错误、原因、补丁和验证逐项记录。默认不重建LLVM/Spike/Linux整套工具链，也不因为本地曾绕过可选目标而强迫当前任务完成它们。

后续用户已澄清上述版本选择：就是当初克隆的 `mp/ara-pulp-v2`。据此，`e040b7bbc…` 从比较时的候选成为本地历史定位的重建基准；获取时核验完整SHA和配套锁文件，不能只checkout可能已经移动的分支名。Ara/CVA6沿原组合，既定CPU profile、2 lanes/VLEN=2048和首次提取范围保持。与本地源码的预期差异主要来自本地后来加入的修改、生成物及环境，但仍须逐项核对，不能事先声称完全相同。

第1步工具链证据保留：若新版本继续使用同一服务器安装及相同ISA/ABI，相关检查仍有参考价值；若更换工具链，必须针对新安装重跑，不能沿用旧通过结论。独立提取工程日常无Bender/无联网要求不变，官方参考初次获取需要联网与受控依赖解析并不冲突。
