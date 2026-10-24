# E01 / CheshireAra 官方后续维护评估

查询与现场核查日期：**2026-10-23（Asia/Shanghai）**。输入本地 HEAD：`c9abbb48946fe3a7244bfb3159919b7c9731cb59`，保留进入时的未提交文档、图稿及未跟踪文件。主 Agent 汇总，三个本地子 Agent 分查 CPU/Ara、互连/DMA、启动/软件，并复查重要候选的后续问题。

**状态：阶段 A，已调查、待验证。未修改服务器源码/依赖，未构建、仿真、生成 RTL 或清理产物。本文不授权阶段 B/C。** 既有修正的“已验证、已同步”仅指此前记录，不是本轮重新运行结果。

**2026-10-23 用户确认：仅进行局部代码修复，不整包升级组件或依赖。** 后续只评估选定修复及确有必要的前置修改；此确认限定维护范围，不等于已选择候选或授权阶段B实施。

## 1. 建议先看什么

建议先从 **Ara #481（store 队列绕回停滞）、Ara #482（不同延迟浮点结果写错目标寄存器）、MVP #18（0/0 多报除零标志）** 中选择一个小修复验证。另有 **iDMA一维提交修复**值得优先：当前2D前端在关闭ND时仍把reps强制为0，既有wrapper及#80/#204没有修这一点。四项都命中当前启用路径，实际文件仍有旧逻辑；逐项选择和验证，不一起迁入后只测一次。

验证入口另有 **Cheshire #191/#192**：正式工程默认 Serial Link ELF 预加载仍有空 burst 和跨 4 KiB 边界风险。若选择维护预加载，先记录 #191 的中间对照，再单独验证 #192 完整函数；静态复核发现 #191 单独使用可能截断非拍对齐整倍长输入，不能先承诺独立采用。

**不建议直接采用“最新版本”。** Cheshire 主线与向量分支、CVA6 pulp-v3 与当前 PULP 版本均有分叉。FS Dirty 修复也不能按标题直接采用：#2936 修正 `fld`，但开放 #3173 记录了 `fcvt` 修改 `fflags` 后未置 Dirty；MVP #16 则有精确次正规结果多报 NX 的后续报告。下面分别列出条件与停止点。

## 2. 两工程的实际输入

简称 **R**＝`/home/zhaowy24/CheshireAraPULP`，**F**＝`/home/zhaowy24/CheshireAra`，服务器 `zhaowy24@172.16.0.243`。

### 2.1 本轮核对结果

- R 的 HEAD 仍为 `e040b7bbc7851a37faff3c4657ff8d656cc6e20a`。根差异含 `.gitignore`、DMA wrapper/HAL、`crt0.S`、三个 DMA 调用点、VCS start 和未跟踪 `wave.tcl`。它不是纯上游提交。
- 读取 R 的 `Bender.lock`，并逐项读取 26 个依赖的真实 HEAD、`git status --short`、`git diff --binary`；HEAD 和差异哈希均匹配 F 的 `provenance/reference.json`。未运行 Bender。
- F 没有 `.git`。按现有 `provenance/source_manifest.json` 逐项读取 **962 条记录**的目标文件并计算 SHA256，全部匹配记录；这些记录包含源、头、软件、文档等，不是“962 个 RTL”。对可对应到现存 R 文件的记录做字节哈希比较，差异仅为下述十项；`source=new` 等无原文件的新增集成对象不计入此比较。
- 十项差异：`src/config/cheshire_pkg.sv`、fixture、SoC TB、Serial RX 回归 TB、LLC `probe.tcl`、两份外设模型许可证摘录、`sw/tests/regressions/dma_long_2d.c`、`check_result.py`、`start.cheshire_soc.sh`。这些是已有配置/层次/入口适配；所选 CPU/Ara/浮点/总线候选文件及原 ROM 在 R/F 一致。
- **配置合并已实施**：F 只有 `src/config/{cheshire_pkg.sv,cv64a6_imafdcv_sv39_config_pkg.sv}` 两个活动输入，`Cfg=DefaultCfg`，由同一包派生 CPU 配置及接口类型。`DefaultCfg.Ara` 原默认 0→1，原有效值已是 1。不能重新创建旧独立 cfg 包。
- **入口简化已实施**：`sim/scripts/compile.cheshire_soc.sh` 编译；`start.cheshire_soc.sh` 展开/运行；`check_result.py` 解析；`sw/Makefile` 单独构建软件。F 没有活动 `run.py`。日常允许复用输出并打印 WARNING；本次候选比较仍拟显式指定新输出，以保存前后结果。

来源记录本身不替代源码；以上哈希检查后，又沿候选调用路径核对了配置、实例和具体旧代码。没有据哈希一致宣称生成差异语义等价或动态测试通过。临时读取摘要保存在本地 `/tmp/e01_maintenance_stage_a/`；长期事实与官方链接汇入本文，不新增维护脚本或证据平台。

### 2.2 当前版本、修正及启用情况

下表路径相对 F；完整 26 项锁定 SHA 见附录。R 的依赖路径来自现有 `provenance/reference.json`，不使用本地 FPGA 工作区代替。

| 组件 / 官方仓库 | 锁定 SHA / 来源 | 实际本地修正与 F 路径 | 当前相关配置 |
| --- | --- | --- | --- |
| [Cheshire](https://github.com/pulp-platform/cheshire) | `e040b7bbc7851a37faff3c4657ff8d656cc6e20a`，`mp/ara-pulp-v2` | `src/cheshire_soc/cheshire_top`、`src/config`、`sw`；DMA wrapper/HAL、FS Clean；F 另有共同 wrapper、配置合并、静态清单和软件入口 | 1 核；地址48/data64；Ara/DMA/SerialLink/Bootrom=1；AXI最大事务24；AxiRt/Clic/IrqRouter=0 |
| [CVA6 PULP](https://github.com/pulp-platform/cva6) | `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c` | `src/cheshire_soc/cva6`；仅两份 WT 读断言局部修正 | `cv64a6_imafdcv_sv39`、WT；RVF/D/A/V=1，RVH=0，MMU=1，UseSharedTlb=0，非超标量，提交口2；PMP实际0；Data/FetchUser=0 |
| [Ara](https://github.com/pulp-platform/ara) | `2895ba907e9eb14b3464609dc791a969d159a7c3` | `src/cheshire_soc/ara`；依赖无本地差异 | 真实 decoder，2 lanes/VLEN2048；CPU profile VLEN64是另一字段；Half/Single/Double、FP扩展及定点默认启用 |
| [FPnew / CVFPU PULP](https://github.com/pulp-platform/cvfpu) | `e5aa6a01b5bbe1675c3aa8872e1203413ded83d1`，0.2.3 | `src/cheshire_soc/fpnew`；无本地差异 | CPU `fpu_wrap` 与 Ara `vmfpu` 均选 `DivSqrtSel=PULP` |
| [MVP div/sqrt](https://github.com/pulp-platform/fpu_div_sqrt_mvp) | `86e1f558b3c95e91577c41b2fc452c86b04e85ac`，1.0.4 | `src/cheshire_soc/fpu_div_sqrt_mvp`；无本地差异 | 实际经 `fpnew_divsqrt_multi` 实例化，结果及 fflags 回传 |
| [AXI](https://github.com/pulp-platform/axi) | `39f5f2d51c5e524f6fc5cf8b6e901f7dcc5622d7`，0.39.6 | `src/cheshire_soc/axi`；无本地差异 | Xbar、串行链路和各适配器；不能把目录内所有模块视为已实例化 |
| [原子适配](https://github.com/pulp-platform/axi_riscv_atomics) | `0ac3a78fe342c5a5b9b10bff49d58897f773059e`，0.8.2 | `src/cheshire_soc/axi_riscv_atomics`；无本地差异 | 实际 LLC/寄存器等路径，RVA=1；LRSC FF仍为阻塞赋值 |
| [iDMA](https://github.com/pulp-platform/iDMA) | `c12caf59bb482fe44b27361f6924ad346b2d22fe`，0.6.3 | `src/cheshire_soc/idma`；#80+#204，含模板/生成器/生成 RTL | AXI64、2D、在途16、MemSysDepth8；共享LLC三类已知失败保留 |
| [LLC](https://github.com/pulp-platform/axi_llc) | `559bcbd09a5a884dbe31e2d72fd95d024e357f39`，0.2.1 | `src/cheshire_soc/axi_llc`；无本地差异 | 非旁路、128 KiB（8 ways×256 lines×8 blocks×8 B）；读写各16；DDR范围0x80000000–0x100000000 |
| [common_cells](https://github.com/pulp-platform/common_cells) / [register_interface](https://github.com/pulp-platform/register_interface) | `13f28aa0021fc22c0d01a12d618fda58d2c93239` / `ae616e5a1ec2b41e72d200e5ab09c65e94aebd3d` | 同名 `src/cheshire_soc/`；无本地差异 | FIFO/仲裁/CDC、旧regbus及`axi_to_reg_v2`实际消费者；不迁SystemRDL/APB体系 |
| [Serial Link](https://github.com/pulp-platform/serial_link) | `5a25f5a71074f1ebb6de7b5280f2b16924bcc666`，1.1.1 | `src/cheshire_soc/serial_link`；单通道寄存器HJSON/生成RTL已有差异 | SerialLink=1；**F默认**ELF使用BOOTMODE0/PRELMODE1；R当前start实际PRELMODE0（JTAG）；SlinkBurstBytes1024；RX已验范围不等于TX |
| [riscv-dbg](https://github.com/pulp-platform/riscv-dbg) | `358f90110220adf7a083f8b65d157e836d706236`，0.8.1 | `src/cheshire_soc/riscv-dbg`；无本地差异 | DebugEn=1；F默认预加载不是JTAG，R当前start默认是JTAG |
| CLINT / OpenTitan外设 / AXI-RT | 完整SHA见附录 | 同名源目录；已有CLINT、PLIC及AXI-RT寄存器源/生成物差异，差异哈希本轮保持 | CLINT及UART/I2C/SPI/GPIO等配置启用；AxiRt=0。启用不表示I2C/GPIO等外部功能已验收 |

已有修正明确保留：FS 清位后显式设 Clean；DMA wrapper 32/64位转换及编号读回、HAL四类32位指针/按次CONF；iDMA #80+#204；WT按有效读字节检查。它们与后续官方候选不是整包覆盖关系。原生成 ROM、已有 HJSON/RTL 本地差异、版权与来源也必须保留。

## 3. 官方变更概览与调查范围

下表是 **2026-10-23 查询到的分支快照**，不是推荐升级版本。提交链接内的完整SHA固定查询对象；PR是否合并另查 `merged`，不以 `closed` 代替。

| 组件 / 查询分支 | 确切 head | 与现版本的关系及主要变化 |
| --- | --- | --- |
| Cheshire `mp/ara-pulp-v2` / `main` | `e040b7bbc7851a37faff3c4657ff8d656cc6e20a` / `6c6dd5e834347f72c7be31cd6c41021ec293c5b9` | [比较](https://github.com/pulp-platform/cheshire/compare/e040b7bbc7851a37faff3c4657ff8d656cc6e20a...6c6dd5e834347f72c7be31cd6c41021ec293c5b9)：分叉，main多64/少17，merge-base `68a7836c0f8998581808efb561bd2fc275a95323`。启动/VIP/地址区域修复、DMA接口、RDL/APB迁移、工具和平台变化；不整树覆盖向量分支 |
| CVA6 `pulp-v2` | `4c02b24fe7c04690f626776a92274da24f80d1da` | [比较](https://github.com/pulp-platform/cva6/compare/99eac9a649001bdf5b8f9da52e0ca73d5c48db1c...4c02b24fe7c04690f626776a92274da24f80d1da)：后续37提交，含FS/MMU正确性、RAW/WAW发射优化及不同cache/profile修复 |
| CVA6 默认 `pulp-v3` | `a0501599ea9e9741f76d34a9377272f23921fdbf` | 分叉，多318/少11，merge-base `2d411b2dc85abe00398e7d404542f0bf1b96f648`；重基于OpenHW `81245a47fad8fe1a5d562d953ef2662e099def76`，更换CVFPU并更新AXI/common_cells等。[PULP变更说明](https://github.com/pulp-platform/cva6/blob/a0501599ea9e9741f76d34a9377272f23921fdbf/CHANGELOG-PULP.md)。另外沿当前WT/加速器路径查OpenHW后续修复；没有声称穷尽其所有profile |
| Ara `main` | `34bd3bc152421b4601a7bf3d6e8e91ffb545c99e` | [比较](https://github.com/pulp-platform/ara/compare/2895ba907e9eb14b3464609dc791a969d159a7c3...34bd3bc152421b4601a7bf3d6e8e91ffb545c99e)：后续18提交，六组/七项功能修复、工具适配，Bender.yml未变；另有未合并mask/reshuffle/归约/异常等PR |
| CVFPU `pulp` | `682f31e376ad796e2fea2eecfdaa2ef0141b2ca9` | 后续13提交主要MXDOTP、低精度FP4/6/8、PACE及流水线可配置化；不是当前传统FPU的必需维护包 |
| MVP `master` | `917dd79cb2dc1a8f43df1a84e0e4231508a980e9` | 1.0.4之后#16/#18两个修复；已读后续#29/#30，不能称master已消除所有浮点错误 |
| AXI `master` | `70b8e54fd460e3308e58be596ceb3566a6e3576e` | 后续154提交；含remap并发、counter语义、适配器修复，以及common_cells v2/模块名/端口变更。后者不适合整包回移 |
| axi_riscv_atomics `master` | `97a1dd2ac643c276880420a0cf8eea697f228aa9` | 后续30提交；LRSC赋值竞态小修、reservation容量/PLRU新功能及工具变化；新PLRU仍有开放问题 |
| axi_llc `master` | `31059c4be62985f81bc46138f09e442d996aa3f3` | 运行时SPM/cache转换、合并flush及配置快照修复，另有生成/依赖调整；不等同DMA系统死锁修复 |
| iDMA `master/devel` | `a6b1d6657c03998b6df0baf905d7babd006ba614` | v0.7.4；后续正确性、compute/transpose/多head、SystemRDL、common_cells v2、生成目录变化并存；不能只按版本号同步 |
| common_cells `master` | `e73baaec2ca665cd80c3c384e9258e35242b829c` | 后续138提交；按FIFO/计数消费者筛选；v2命名/接口变化不作为默认维护 |
| register_interface `master` | `d6e1d4cdaab7870f4faf3f88a1c788eaf5ac129d` | v0.4.7，后续10提交；含reg_to_axi错误标志及工具/lint维护 |
| riscv-dbg `master` | `643607e19df3435cfd77cc56143e2637f5900a6e` | command错误屏蔽、总线位宽、多hart/debug支持；区分当前64位单hart路径 |
| serial_link `main` | `521908b92919ac143cbc489623d2300f17589c52` | 后续32提交；SDR/serializer新功能、v2寄存器与接口重构、common_cells v2；无当前必须整升证据 |

## 4. 候选分类与适用性

所有新增候选均为 **已调查、待验证，未同步**。这里的“适用”指当前代码和配置具备触发条件，不等于本轮已经复现。只把有原测试记录的既有修正列为已验证/已同步。

### 4.1 优先验证的局部候选与入口候选

| 候选 / 官方链接与提交 | 类别 | 当前是否适用 | 已有修正是否覆盖 | 前置依赖及移植范围 | 预期收益 | 验证方法 | 建议 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **P1 Ara #481** [PR](https://github.com/pulp-platform/ara/pull/481) / [ae8297af0af38b52136826e591782042025725da](https://github.com/pulp-platform/ara/commit/ae8297af0af38b52136826e591782042025725da)，已合并 | 停滞修复：队列全部store已issue而未commit，环指针绕回相等，被误判无待提交项 | 是；`vstu.sv`仍比较`issue_pnt!=commit_pnt`；与lane数无此排除条件 | 未覆盖；不是DMA/LLC的等待链 | 仅`ara/hardware/src/vlsu/vstu.sv`，改比较计数；不改变队列深度、接口/配置/ISA或清单 | 消除这一种向量store停滞 | 见§5：控制B返回时机、数据/提交计数及向量回归 | **优先验证，建议首个** |
| **P2 Ara #482** [PR](https://github.com/pulp-platform/ara/pull/482) / [a987112abed1339ecc9723555759be79427224bf](https://github.com/pulp-platform/ara/commit/a987112abed1339ecc9723555759be79427224bf)，已合并 | 正确性：低延迟FP结果抢在高延迟结果前写错vd | 是；VMFPU启用，缺比较操作延迟分类且判断晚一拍 | 未覆盖；原精确浮点加法/矩阵乘不证明混合延迟次序 | 仅`ara/hardware/src/lane/vmfpu.sv`；补延迟分类及及时组合判定，不升级FPnew | 正确排序；可能增加必要等待，**不称性能提升** | FP32/64比较/转换/算术混排，独立与依赖vd、mask；结果及fflags检查 | **优先验证** |
| **P3 MVP #18** [PR](https://github.com/pulp-platform/fpu_div_sqrt_mvp/pull/18) / [2ec0514c1d538781a26df23fb8a947a60fcdccfc](https://github.com/pulp-platform/fpu_div_sqrt_mvp/commit/2ec0514c1d538781a26df23fb8a947a60fcdccfc)，已合并 | 正确性：0/0应NV，却同时置DZ | 是；CPU/Ara均PULP除法器，`norm_div_sqrt_mvp.sv`旧分支仍置DZ | 未覆盖 | 仅`hdl/norm_div_sqrt_mvp.sv`一行；**不需要先迁#16**，不升级FPnew/生成RTL | 修正标量及向量0/0异常标志 | ±0/±0与非零/0对照，NaN/NV/DZ、mask及fflags累积；精确正常算例回归 | **优先验证**；不扩大成完整IEEE浮点验收 |
| **P4a Cheshire #191** [PR](https://github.com/pulp-platform/cheshire/pull/191) / [1b893efc6ee520be7d135a1adda397af94fa1c45](https://github.com/pulp-platform/cheshire/commit/1b893efc6ee520be7d135a1adda397af94fa1c45)，已合并 | 正确性/协议（验证平台）：预加载末尾多发空burst | 是；F默认PRELMODE1，实际VIP仍`i<=sec_len`；R验证时显式选1 | 未覆盖；旧ELF通过不覆盖所有section长度 | R `target/sim/src/vip_cheshire_soc.sv` → F `src/tb/src/vip_cheshire_soc.sv`，`<=`→`<`一行 | 可消除拍对齐整倍长的空写，但非拍对齐有截断风险 | 1024倍数/非整倍数、非拍对齐、loader跳过空PT_LOAD；核对全部字节 | **有条件入口维护**；先作中间对照，未过边界不独立同步 |
| **P4b Cheshire #192** [PR](https://github.com/pulp-platform/cheshire/pull/192) / [ae5795dfdb177a8dc3ef2f43dcc7ceaa36fd9238](https://github.com/pulp-platform/cheshire/commit/ae5795dfdb177a8dc3ef2f43dcc7ceaa36fd9238)，已合并 | 协议（验证平台）：单burst跨4KiB，并重新处理非对齐beat | 是；1024 B最大长度不能避免非页对齐起点跨页；VIP尚无页边界切分 | 未覆盖；RX专项不是该ELF加载过程 | 与P4a同一task；在记录#191中间结果后，单独比较完整函数；不改SLINK生产接口 | 避免非法边界，保留完整加载 | 页尾起点、多section、非拍对齐整倍长、尾字节/邻区；与原版和P4a分别比较 | **有条件采用**，不能用P4a的局部通过替代最终装载边界验收 |
| **P5 iDMA 1D-in-ND修复** [#66 / 92799c5fabcf2cd1f224f970bbb040b290d08fd5](https://github.com/pulp-platform/iDMA/commit/92799c5fabcf2cd1f224f970bbb040b290d08fd5)的reps hunk＋[Cheshire #203 / bca9aadb7588de7046460daf91b39fe863a7a9d1](https://github.com/pulp-platform/cheshire/commit/bca9aadb7588de7046460daf91b39fe863a7a9d1)的HAL对应hunk | 正确性；启用2D前端、用1D API令ENABLE_ND=0时前端仍强制reps0，midend拒绝传输/合成错误响应 | **适用**：DmaConfEnableTwoD1、当前reg64_2d及汇总均旧值，HAL1D另清reps0；机制已静态核实，未动态复现 | wrapper/HAL宽度、#80/#204均未覆盖；不能把#203整体标已回移 | 仅ND关闭时reps归一hunk、对应模板/派生RTL及HAL删1D清reps行；不用#66新协议字段/后端工具改动，不升依赖 | 使当前1D API真正发起一维搬运；不改变2D API或宣称通用无死锁 | 官方`dma_1d.spm.c`的18 B小搬运＋保护字符、ID与实际请求；2D→1D→2D顺序及原小DMA回归，见§5 | **优先验证**，与LLC长搬运排查分开 |

以上候选不要求改变寄存器/地址图、软件ABI、cache类型、lane数、生成工具或依赖锁。P5必须同步所涉模板和已有派生RTL，但不需重生成全IP。P4只修验证平台，不宣称修复芯片硬件行为。

P4静态反例：`sec_addr=0x10000001, sec_len=1024`时，旧首轮只装`bf[0..1022]`，最后一次`i=1024`装`bf[1023]`；单改`<`删除该轮。#192的`b=-bus_offs`重新计算beat覆盖。**这是源码推导，未仿真**；把它列为必测，不靠当前17个对齐ELF掩盖。若阶段B只授权P4a，遇此失败即报告停止；若明确授权P4a/P4b分步评估，可保留该预期中间失败后继续验证P4b，最终通过前不写回原件。

### 4.2 有条件、暂缓及不适用候选

#### CPU、Ara及浮点

| 候选 / 官方链接与提交 | 类别 | 当前是否适用 | 已有修正是否覆盖 | 前置依赖及移植范围 | 预期收益 | 验证方法 | 建议 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **C1 FS Dirty #2936** [PULP ecb138010de2868532f43131697e38231162ddb5](https://github.com/pulp-platform/cva6/commit/ecb138010de2868532f43131697e38231162ddb5)，原OpenHW merge `2700d14471963909923bdcfa1b013b4d1b30e567` | 正确性；括号/优先级使`fld`等未置FS Dirty，并增加不写FPR操作筛选 | 是；当前`commit_stage`仍旧表达式 | **FS=Clean启动修正未覆盖硬件状态跟踪** | `core/commit_stage.sv`＋`core/include/ariane_pkg.sv` helper，无接口升级 | 能修fld路径；与历史FS保持Initial现象相符，但尚未本工程复现确认 | Initial/Clean→fld/fadd，F2I触发NX/NV，读FPR操作、flush、FS/SD分别检查；见下文风险 | **有条件验证，不直接采用**：#3173仍开放，失败停止，不宣称完整FS修复 |
| **C2 加速器取消 #3310** [a31b556c30d5f71be9124b0f910ebce3f5c34514](https://github.com/openhwfoundation/cva6/commit/a31b556c30d5f71be9124b0f910ebce3f5c34514)，已合并 | 正确性；同拍flush和acc_commit留下ready，ID复用后误送投机向量指令 | 当前acc_dispatcher清pending后又设ready；非超标量不自动排除此时序 | 未覆盖 | 仅`core/acc_dispatcher.sv`，flush优先并清pending/ready | 防错误发送/副作用 | 异常＋待提交向量＋trans_id复用；核对取消指令不进入Ara，正常向量回归 | 有条件采用；优先于大版本升级，但需定向取消时序证据 |
| Ara #433 [e970f7736cde544eb2a44c6a44ad7eb0f8789f1a](https://github.com/pulp-platform/ara/commit/e970f7736cde544eb2a44c6a44ad7eb0f8789f1a) | 正确性；SEW改变后标量提取缺reshuffle | 旧dispatcher在用 | 未覆盖 | `ara_dispatcher.sv`一行；无依赖升级 | 修`vmv.x.s/vfmv.f.s`读值 | SEW A写入→SEW B提取，整数/FP/符号；现有固定SEW加法不足 | 有条件采用：内核使用该模式时 |
| Ara #432 [0bfbcfca0ad2eaf6a7e6fd38ff5edd7f1208c2d1](https://github.com/pulp-platform/ara/commit/0bfbcfca0ad2eaf6a7e6fd38ff5edd7f1208c2d1)＋[7ab0206a258e2dbbd00935cd88656a66ef9ebf84](https://github.com/pulp-platform/ara/commit/7ab0206a258e2dbbd00935cd88656a66ef9ebf84) | 正确性；整数扩展源EMUL误按LMUL检查，合法指令误trap | 当前缺两处检查修正；如m2的`vzext.vf2 v2,v1` | 未覆盖 | **同PR两提交为配套组**：dispatcher及`vsext.c/vzext.c`新增CASE7 | 正确区分源/目的EMUL与非法目的 | m2/4/8、vf2/4/8、合法/非法寄存器；对照官方新增用例 | 有条件采用；维护者明确一般src/dst重叠检查仍不完整 |
| Ara #439 [4f876b5948aebd53dd948dce52f4aae244cfe574](https://github.com/pulp-platform/ara/commit/4f876b5948aebd53dd948dce52f4aae244cfe574) | 正确性；背靠背整数归约在VRF真正提交前清计数 | 当前`lane/valu.sv`为旧逻辑 | 未覆盖 | 仅VALU提交状态/计数 | 防归约次序错误 | 连续/依赖归约、VRF反压、各整数归约操作 | 有条件采用；不覆盖开放#470的其他问题 |
| Ara #440 [ce6a67427eb9b1ee7d89cf9d682cb801714b77cf](https://github.com/pulp-platform/ara/commit/ce6a67427eb9b1ee7d89cf9d682cb801714b77cf) | 正确性；slide1up误按stride减少提交数 | 2lane在用 | 未覆盖 | `masku.sv`和`sldu.sv`两处一起 | 正确计数/完成 | VL0/1/2、lane边界、mask/tail及标量插入 | 有条件验证；含该补丁的main仍有[#508](https://github.com/pulp-platform/ara/issues/508)边界问题，不能承诺完整slide支持 |
| CVA6 MMU #2798/#2802/#2976，[8a6028b646e649b811854ba27e9f2d0e39f612a8](https://github.com/pulp-platform/cva6/commit/8a6028b646e649b811854ba27e9f2d0e39f612a8)、[5576a2267f1a53ccc4e753ae61e7092c37f77786](https://github.com/pulp-platform/cva6/commit/5576a2267f1a53ccc4e753ae61e7092c37f77786)、[b56fbbb9bda82bd217c28b9338904e31ab4cd134](https://github.com/pulp-platform/cva6/commit/b56fbbb9bda82bd217c28b9338904e31ab4cd134) | 正确性；非对齐异常与请求错拍 | MMU=1/RVH=0，仍直通misaligned_ex；裸机也不能完全排除 | 未覆盖 | `cva6_mmu.sv`；**不能孤立#2798**，其RVH=0锁存回归需#2976纠正，#2802选正确有效信号；[#2989/00d8acf4f82a4d30c4a22e24682dad84860989ce](https://github.com/pulp-platform/cva6/commit/00d8acf4f82a4d30c4a22e24682dad84860989ce)的阻止错误DTLB请求hunk另注明，不搬无关Python部分 | 异常归属及请求时序正确 | 连续对齐/非对齐访存、mcause/mepc/mtval、无额外请求；Sv39与trap后恢复 | 有条件采用；不是运行既有572项即可证明 |
| CVA6 shared TLB #2945 [407787890aea1d1c91d2ac219bd82e9b815a4bd1](https://github.com/pulp-platform/cva6/commit/407787890aea1d1c91d2ac219bd82e9b815a4bd1) | 正确性；逐way比较ASID/VMID漏`[i]` | **当前UseSharedTlb=0**，错误分支不执行；仅MMU=1或启用Sv39不使其适用 | 未回移但当前无须 | `cva6/core/cva6_mmu/cva6_shared_tlb.sv` | 对其他配置修多way匹配 | 只有将来明确启用shared TLB后才做多ASID/替换/flush验证 | **当前不适用** |
| **MVP #16** [0d7807af3a1822f9c932dbcd3c8e33f90697ff6e](https://github.com/pulp-platform/fpu_div_sqrt_mvp/commit/0d7807af3a1822f9c932dbcd3c8e33f90697ff6e) | 正确性；UF/OF漏NX | 当前PULP路径适用 | 未覆盖 | 同norm文件一行，逻辑独立于P3；不能因此自动合并 | 修部分标志，但有后续反例 | OF/总下溢＋精确次正规对照，FP32/64和舍入模式 | **暂缓原样回移**；[#29](https://github.com/pulp-platform/fpu_div_sqrt_mvp/issues/29)报告新增精确次正规NX误报 |

**C1不能被简化为“已有官方完整FS补丁”。** 本轮实际读取 `csr_regfile.sv`：显式CSR写会置Dirty，但硬件`csr_write_fflags_i`分支只累积标志，没有独立置Dirty路径。[开放 #3173](https://github.com/openhwfoundation/cva6/issues/3173)给出F2I修改fcsr但FS仍Clean的复现。已合并[#3469 / 6ee41edb289f9480282493388ae39693df69f76d](https://github.com/openhwfoundation/cva6/pull/3469)另修SD摘要使用旧FS值晚一拍，**不修F2I→FS**；开放[#3638](https://github.com/openhwfoundation/cva6/pull/3638)还涉及VS→SD。若选择C1，只承诺验证fld收益和这些边界；F2I/SD检查失败时停止，不能现场扩大为自研CSR修复或删除FS=Clean。

**MVP后续报告是风险证据，不冒充本工程复现。** #29报告 `0x00800000 / 0x40000000` 的精确FP32次正规结果，原版已有多报UF，#16还多报NX；同时报告1 ulp、NX和无穷特殊值等剩余问题。#18仅消除0/0的DZ，与这些错误分开。即使P3通过，也不关闭整个除法器正确性限制。

#### Cheshire启动、软件与配置

| 候选 / 官方链接与提交 | 类别 | 当前是否适用 | 已有修正是否覆盖 | 前置依赖及移植范围 | 预期收益 | 验证方法 | 建议 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **C3 uncached SPM执行 #189** [7ecb93a324aee8d1562a8ea347cfb714abe837e9](https://github.com/pulp-platform/cheshire/commit/7ecb93a324aee8d1562a8ea347cfb714abe837e9) 的执行区域hunk | 正确性；0x14000000别名取指未纳入可执行区 | 当前128KiB，旧`AmSpm+2*SizeSpm`不包含相隔64MiB的别名；普通访存通过不等于可执行 | 同PR的HAL能力已回移，**执行区未覆盖** | 仅当前`src/config/cheshire_pkg.sv::gen_cva6_cfg`规则数、基址/长度；不覆盖已合并Cfg/类型，也不重复迁HAL | 允许既有非缓存SPM别名执行，不新增地址窗口 | 官方`spm_uncached.spm.c`思路＋最小别名取指；cached正常、非法区仍拒绝 | 有条件采用：需要别名执行时；若官方DMA用例触发旧LLC限制则停止，不扩排查 |
| **C4 Platform ROM返回 #187** [9b4c222df72f74f90ab9f36d80ba7b527f92e62b](https://github.com/pulp-platform/cheshire/commit/9b4c222df72f74f90ab9f36d80ba7b527f92e62b) | 启动正确性；非零PlatformRom钩子ret落错路径 | 原S/SV仍有旧布局；**默认PlatformRom=0，当前普通启动不触发** | 未覆盖；原SPI padding豁免无关 | 源`.S`与生成SV成对；精确裁取启动布局/必要对齐，保留FS；同提交sw.mk flash改动不相关 | 平台初始化返回后继续内置启动 | 可返回的最小平台钩子、默认0、原ROM/SPI完整启动；源/反汇编/SV对应 | 有条件采用，沿S01-B01；**单列重生成ROM授权**，不顺手重生成 |
| **C5 CLINT sleep条件 #252** [6234e9e9898951e7b6ab818f4e699831eb76d74e](https://github.com/pulp-platform/cheshire/commit/6234e9e9898951e7b6ab818f4e699831eb76d74e) 中一行 | 软件正确性；未来deadline反而提前return | 两边`sw/lib/dif/clint.c`仍`now < target`；所选应用未调用该sleep API | 未覆盖 | 只将`<`改`>=`，**无需同PR的CLINT/APB/SystemRDL迁移** | 正确等待未来deadline | 当前CLINT、真实timer中断、会返回的handler：未来/过期/相等deadline；默认trap自循环不能作通过测试 | 有条件采用：使用sleep API时 |

#### 互连、原子、DMA及LLC

| 候选 / 官方链接与提交 | 类别 | 当前是否适用 | 已有修正是否覆盖 | 前置依赖及移植范围 | 预期收益 | 验证方法 | 建议 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **C6 LRSC FF #35** [PR](https://github.com/pulp-platform/axi_riscv_atomics/pull/35) / code [1ad48f389da7cef3d4b5169baeb214febe02a0ba](https://github.com/pulp-platform/axi_riscv_atomics/commit/1ad48f389da7cef3d4b5169baeb214febe02a0ba)，merge `3617819b8f0d9283b9122e4cef690bcfc7c1df4d` | 正确性/仿真竞态；连续burst令clr_len误取下一笔0而下溢、多等AW_BURST | 当前真实LRSC FF仍阻塞赋值；官方在Verilator发现，VCS是否出现待验证 | 未覆盖 | 仅`axi_riscv_atomics/src/axi_riscv_lrsc.sv`的7项复位/更新`=`→`<=`；不升级0.8.3 | 消除该竞态；“10×simulation speed”不是本工程硬件收益 | 连续不同len AW、LR/SC＋普通写清reservation、数据/握手及572项；旧新版VCS都过则明示未复现 | **有条件采用，小范围次优先**；不增加首批任务数量 |
| **C7 LLC配置/flush链** [d410d306abafe4d242c702336d6a1a8cf4e2c753](https://github.com/pulp-platform/axi_llc/commit/d410d306abafe4d242c702336d6a1a8cf4e2c753)、[0c581edae31996bf4190af9350952648f553adfa](https://github.com/pulp-platform/axi_llc/commit/0c581edae31996bf4190af9350952648f553adfa)、[08fef39c1cc473669f03231d93b2c9a2da804002](https://github.com/pulp-platform/axi_llc/commit/08fef39c1cc473669f03231d93b2c9a2da804002)、[#44/f8ca916a53d9c0ecea68acbddcd90c2275816817](https://github.com/pulp-platform/axi_llc/pull/44) | 正确性/停滞；在途事务时重配、SPM→cache同时flush、busy时改配置 | 当前`spm_lock=cfg_spm`立即生效，flush/SPM二选一；配置代码未修；启动全SPM不证明运行时转换触发 | 未覆盖；**不修DMA三类循环** | 主要`axi_llc_config.sv`：寄存SPM锁→合并flush→修合并算法flushed更新→快照请求；不能孤立迁0c58而遗漏08fe；完整最终语义须核对这一依赖链 | 正确转换/排空、不会因忙时配置变化无限flush；最终flush多一周期，不是加速 | 借官方[#32/dee54d390784aa04ce62b288a0bd09851a68a5a4](https://github.com/pulp-platform/axi_llc/commit/dee54d390784aa04ce62b288a0bd09851a68a5a4)场景，dirty写回/way属性/命中计数/数据；从DDR执行，避免重配自身SPM栈 | **有条件采用**：近期确需运行时cache/SPM/flush；否则暂缓。旧平台直接复制新TB有时序差异，见下文 |
| **C8 reg_to_axi #54** [78547839e3036eb1585966137a1096974fc54124](https://github.com/pulp-platform/register_interface/commit/78547839e3036eb1585966137a1096974fc54124) | 正确性；OKAY被映为error=1 | Usb=1，OHCI控制路径实例化；当前仍旧比较 | 未覆盖；其他外设通过不证明USB此路径 | `register_interface/src/reg_to_axi.sv`一处`==RESP_OKAY`→`!=RESP_OKAY`，无接口/前置 | 正确响应成功/错误 | Regbus→AXI读写OKAY/SLVERR/DECERR，rdata/error/ready；复用相关CSR检查 | 有条件采用：使用USB控制口前；非图像通路首要任务 |
| AXI id_remap #409 [e11c4f9ff48f2c5dfd15a6dbe31404908df7c34b](https://github.com/pulp-platform/axi/commit/e11c4f9ff48f2c5dfd15a6dbe31404908df7c34b) | 等待/并发改善，可产生性能收益 | 当前HoldAR阻AW/反向，**SerialLink TX**实际实例化；RX回归不能证明TX收益 | 未覆盖 | 仅`axi_id_remap.sv`；保留ATOP双向ID规则/公平性，无参数变化 | 解除独立读写通道不必要互挡 | 双向TX、独立ARREADY/AWREADY反压；校验ID/顺序/ATOP后看目标事务周期与握手数 | 有条件验证，性能细则见§6；不是共享LLC修复 |
| AXI counter #440 [da8793b0e3f14c9186c94fac9ed6ec06375c254e](https://github.com/pulp-platform/axi/commit/da8793b0e3f14c9186c94fac9ed6ec06375c254e) | 配置语义/容量行为改变；2幂少1、非2幂超上限 | 主Xbar MaxTrans24旧可至31，新严格24；其他4/8路径另核 | 未覆盖 | 新上游拆出`axi_demux_id_counters`并用cc v2；旧版应仅适配`axi_demux_simple`语义，不能孤立复制新文件 | 精确容量边界，**不保证吞吐提升** | 4/8/24无返回压力、ATOP同拍加2、正确顺序/反压；官方声称测试但merge只带2个RTL文件 | **暂缓，单列配置行为变更** |
| LLC BIST比较 [06a4020d135de5d6c13b8dbcebfcfa2937e8239d](https://github.com/pulp-platform/axi_llc/commit/06a4020d135de5d6c13b8dbcebfcfa2937e8239d) | 工具兼容/比较正确性，packed struct XNOR改逐字段 | 官方特定VCS/Simon路径错误；当前BIST已有通过记录，未见同样触发 | 未覆盖，但不等于当前失效 | 单`axi_llc_tag_store.sv` | 避免特定编译器错误比较 | 相同工具/参数下BIST pattern/way比较，不仅看编译成功 | 暂缓，出现具体工具证据再选 |
| riscv-dbg #206 [643607e19df3435cfd77cc56143e2637f5900a6e](https://github.com/pulp-platform/riscv-dbg/commit/643607e19df3435cfd77cc56143e2637f5900a6e)，code `b1fd38ad58e564e45611f85c7e425594bddd7cdc` | Debug规范正确性；cmderr非0仍触发command/autoexec | 当前单hart也可能适用；未证明现有调试流程触发 | 未覆盖 | `dm_csrs.sv`命令与4个autoexec点，无需多hart更新 | 错误未清时正确拒绝新命令 | 注入cmderr、各autoexec读写、清错恢复及busy状态；官方未随PR加新测试源码 | 有条件采用：JTAG/调试器验收时 |
| iDMA零尺寸 #247 [892434bd794e55e9c918c6bcba20a0e494a0e955](https://github.com/pulp-platform/iDMA/commit/892434bd794e55e9c918c6bcba20a0e494a0e955) / #267 [6d640580919b96d3b63c6c4e615b7c6abe22b34a](https://github.com/pulp-platform/iDMA/commit/6d640580919b96d3b63c6c4e615b7c6abe22b34a) | 正确性；零长/零reps反压及后续地址污染 | ND/RejectZeroTransfers启用，但nd_rsp_ready固定1排除部分响应反压；backend被挡的零reps仍待验证 | #80/#204不覆盖 | #247模板及所用rw_axi生成/汇总成对，需保留已有模板改动；#267 ND midend及directed TB；不迁compute字段 | 零尺寸响应及后续strided地址正确 | 官方zero_transfer_busy/NDZ按当前可达条件裁取，不为未启用反压造框架 | 暂缓/有条件验证；无当前零尺寸工作负载依据 |
| common_cells FIFO [c777d27e5aa585f6c53cc68fbbcae6a542d9b1c1](https://github.com/pulp-platform/common_cells/commit/c777d27e5aa585f6c53cc68fbbcae6a542d9b1c1) | 正确性；full/empty握手与pointer更新 | iDMA使用passthrough_stream_fifo，但当前读push已含ready、写pop已含有效mask；所查路径未找到对应非法推进 | 未覆盖，但不能称当前DMA数据损坏 | v1单文件条件适配，不能整升v2 | 对其他消费者防无效推进 | 消费者确需时借官方[a49dc11f1b2360accea6b567a8d7aa36512c0f77](https://github.com/pulp-platform/common_cells/commit/a49dc11f1b2360accea6b567a8d7aa36512c0f77)反压测试 | 暂缓 |

LLC #44与原子#35后续问题也做了复查：LLC [#47](https://github.com/pulp-platform/axi_llc/issues/47)涉及借用#32计数TB的时序及DPLLC，不能把完整新TB照搬；partitioned分支[#49](https://github.com/pulp-platform/axi_llc/issues/49)不用于当前主线。atomics新limited-PLRU的[#43](https://github.com/pulp-platform/axi_riscv_atomics/pull/43)（head `481df4a253d75a9a8a2ffd669e81fad12667195a`）/[#46](https://github.com/pulp-platform/axi_riscv_atomics/issues/46)不在当前旧实现，进一步反对整包升级；旧实现还有开放[#32](https://github.com/pulp-platform/axi_riscv_atomics/issues/32)失败SC不清reservation、[#44](https://github.com/pulp-platform/axi_riscv_atomics/pull/44)（head `b8e3c184f72cdfcdd195bc2d822f3f6ad3306c8a`）冲突写时LR误回EXOKAY，**#35不覆盖这些边界**。以上均未在本工程运行验证。

### 4.3 已覆盖修正、开放候选与当前不适用项

| 对象 | 本轮核实的状态与采用判断 |
| --- | --- |
| 既有DMA wrapper/HAL | [bca9aadb7588de7046460daf91b39fe863a7a9d1](https://github.com/pulp-platform/cheshire/commit/bca9aadb7588de7046460daf91b39fe863a7a9d1)的宽度转换hunk＋[ef11799d00d9c7b19d042864529d03cbe41fac5b](https://github.com/pulp-platform/cheshire/commit/ef11799d00d9c7b19d042864529d03cbe41fac5b)端口、[4c2390f25f250c9ea75d314dd107da11a52aa8fa](https://github.com/pulp-platform/cheshire/commit/4c2390f25f250c9ea75d314dd107da11a52aa8fa)按次CONF及本地32位控制指针：此前已验证、已同步R/F。**只覆盖这些hunk，不是整个#203已覆盖** |
| 既有iDMA #80/#204 | [40fe6a67b6d734b6d75409803af5eea9d0eb51c8](https://github.com/pulp-platform/iDMA/commit/40fe6a67b6d734b6d75409803af5eea9d0eb51c8)＋[497c1f2300091121d5de9344f3a9e5e501af44c5](https://github.com/pulp-platform/iDMA/commit/497c1f2300091121d5de9344f3a9e5e501af44c5)均已合并；当前36文件本地回移与生成物仍在，此前已验证、已同步。#80写首拍驱动AW、#204空队列保护/按任务标志及许可计数共同保留；不重复实施 |
| 既有WT读断言 | 本地按有效字节适配已验证、已同步；官方[e606cdfe36b49d09c8f60975fd10f88948677c6d](https://github.com/pulp-platform/cva6/commit/e606cdfe36b49d09c8f60975fd10f88948677c6d)改的是HPD/std，仍整字检查，不是WT替代方案 |
| Cheshire FS #201 / #202 | [#201](https://github.com/pulp-platform/cheshire/pull/201) `closed`但`merged=false`，head `d9c413fa65559234aaddc31b14fb816ff857b9b6`；不是官方已合并启动修复。[#202](https://github.com/pulp-platform/cheshire/issues/202)关闭并指向CPU修复，也不能覆盖C1的残留或取代本地Clean |
| DMA共享LLC | [Cheshire #219](https://github.com/pulp-platform/cheshire/issues/219)查询时仍open、无修复提交。本工程三类循环由既有实际记录支持，暂缓扩展排查决定不变 |
| iDMA [#227](https://github.com/pulp-platform/iDMA/pull/227) | **open、未合并**，head `ac6a0d088904264fa5be17bd6d774e9c935d1d68`，base devel `a6b1d6657c03998b6df0baf905d7babd006ba614`；说明依赖仍开放的[#161](https://github.com/pulp-platform/iDMA/pull/161)，head `5fb2a81c4d0b462a87e55ede6f1a464124ce8324`。39文件：每byte lane为读返回预留容量、新deadlock_free字段贯穿请求/寄存器/生成层；当前BufferDepth3会使读burst限到2拍，可能降吞吐。admission不使用同周期pop以防组合环。**不是保行为小修，也不保证LLC写依赖/Bloom锁无环**；暂缓，不启动试验 |
| iDMA [#273](https://github.com/pulp-platform/iDMA/pull/273) | **open、未合并**，head `728e7330ecc45c2f0849e74e60535a8d1cb27788`，base同上；声明依赖#227/#228/#272，60文件、删除decouple_rw语义并把旧位保留reserved、读写始终独立legalize。架构/行为重构，不能替换现有HAL/#80/#204；暂缓 |
| iDMA [#221](https://github.com/pulp-platform/iDMA/issues/221) | open，ErrorHandling=1＋读错误场景，官方根因未定；当前**NO_ERROR_HANDLING**，不列当前已知可触发缺陷。#67 `d77382f069df9043a86bb78ba25ff53d149e2b7b`多协议read mux、#53 `ea201b0d62324d71668481bbe78790d754f3f1d3` no_burst/page_burst不属于当前单rw_axi/pow2分割路径 |
| Ara开放mask/reshuffle/定点修复 | [#469](https://github.com/pulp-platform/ara/pull/469) head `aee901c70f9eb9be644da556dc4a2ddd0de48661`；[#502](https://github.com/pulp-platform/ara/pull/502) `16edd3ba8a734b7cc52dee124bd86adb53fa66ff`；[#483](https://github.com/pulp-platform/ara/pull/483) `6b664a2c7437b4b2bea51af17b8a26a20b6d38e7`；[#503](https://github.com/pulp-platform/ara/pull/503) `8581df7d40f5041e1d8478a29e7751c82bbb83cf`。**均未合并**。#469有4个reproducer；#502虽报告2lane/VLEN2048，但基于含#469等额外补丁的树，去早退也可能增加周期；#483与已合并#433不是同问题；#503是SEW16 vsmul移位，定点虽启用但工作负载未定。暂缓，需求命中后固定依赖再选；不把开放PR称为main能力 |
| CVA6其他cache/profile修复 | WB fence.i `ad1c5e902ea87ef59db30293bbdeea07a7e5a8f6`、HPD refill `5d59eaed64a64b0bbfc5a50938c0c5ee2344533c`当前WT不适用；DTLB ASID `bb11e1d826ad1e219784fd0d1ecd86094bc1e0ce`在RVH0两选择相同；WT user切片 `2272df3e0339247a6e9718551eef6d819ec9b1a2`的DataUserEn=0；WT data_error `e978838530c1117e8df7457b184460d95f5d3313`针对后续新接口，当前load_unit无该字段消费者。均不为回移而引入新接口 |
| 其他基础IP边界 | common_cells delta_counter新修复针对后续引入的问题，当前v1.33复位已有正确`~rst_ni`；stream_join_dynamic在所查DMA/AXI/Cheshire/SLINK链未实例化，未推定所有其他消费者无问题。AXI HideStrb修复在已查debug adapter的HideStrb0不触发；dbg总线/抽象寄存器位宽修复在当前64/64无差异。GPIO/I2C/USB/板级PHY未因源码调查获得功能验收 |

### 4.4 新功能、重构与工具变化：不混入保行为维护

| 官方变化 / 提交 | 为什么暂缓或不适用 |
| --- | --- |
| Cheshire SystemRDL/APB [#260 / 519464ed4c123888c20dff53d2e9309d3e469ce6](https://github.com/pulp-platform/cheshire/pull/260)，首生成改动 `3aed98131242eac999219602c7397892946dda6c`；CLINT #252；SLINK [#253 / 79a5f5c477241ea515ad5ba1cf55b550382ad950](https://github.com/pulp-platform/cheshire/pull/253) | HJSON/regbus→SystemRDL/PeakRDL/APB，连同RTL/头/链接地址/ROM/生成工具变化；需配套新IP。当前集中配置/静态清单已完成，不为维护引入整套迁移。只摘C5一行不要求这套前置 |
| Cheshire UART [#225 / f6096ff2ac42db7a3f3f5374770947932b45f587](https://github.com/pulp-platform/cheshire/pull/225) | apb_uart0.2.3 `8182a85d234417db46fe833533f8536644d3bee3`改为obi_uart包装、增加obi_peripherals并升相关库；与旧UART分支无共同祖先，新实现的修复不代表原UART同病。暂缓 |
| AXI/common_cells v2，[aa799ec1b11e0ffc4d975938e1b3ea66a89c6f71](https://github.com/pulp-platform/axi/commit/aa799ec1b11e0ffc4d975938e1b3ea66a89c6f71)与[d4114f691b172ec1970165f1b5e63e6269a71836](https://github.com/pulp-platform/axi/commit/d4114f691b172ec1970165f1b5e63e6269a71836) | cc_重命名、test_i删除及版本不兼容；#409等局部改动不需要整升。iDMA/SerialLink同步迁v2、compute/SDR/新serializer也无当前必需收益依据 |
| Cheshire SD启动频率 [#197 / 5c63c992c827d6ed4b8daaf0e6818c78ac709d16](https://github.com/pulp-platform/cheshire/pull/197) | SD SPI频率取min(24MHz,core/2)，适用于低于48MHz核心的SD启动；当前验的是SPI NOR raw，非SD，无SD验收。当前不适用，涉及C与生成ROM不能顺手替换 |
| Cheshire [#246 / fcf135015e1a26ea4a2ad74c4c071f5a8fa645fa](https://github.com/pulp-platform/cheshire/pull/246)；Ara [e561b79de74daa38351b68ddd5559dc78c3af36e](https://github.com/pulp-platform/ara/commit/e561b79de74daa38351b68ddd5559dc78c3af36e) | 前者数组初始化语法工具兼容；后者“Update verilator”还含simd_mul四处默认赋值和C++修改。不是只读标题认定无RTL影响；当前VCS无对应故障，暂缓，必要时只取相关hunk |
| Cheshire MEMH [#263](https://github.com/pulp-platform/cheshire/pull/263)，`c60404ad7a3c1840235495ec3d67757604da6101`＋`2a77a408a1c5cf1babb23514d12f40865b830607` | 新直接内存加载/启动模式，改VIP/TB/DPI，减少主机加载时间；当前无此需求，不新增模式或替代原SLINK/ROM验收 |
| Cheshire [#290 / faa7d15287e1f491d38a7f1f77ca52210e6b77a7](https://github.com/pulp-platform/cheshire/pull/290)、[#284 / a315a828abb61cf3cb9f4419b910ebe6739b90bf](https://github.com/pulp-platform/cheshire/pull/284) | 修迁移后的APB禁用端口/配置，还改ID默认/LLC；当前未引入apb_mask，不能说修当前同一缺陷 |
| Python uv/pip [#261 / a4fa6988e9b6fe52aab3edbaac62399f369462c9](https://github.com/pulp-platform/cheshire/pull/261)、[#291 / 78e0181615b56135d8b867d405b65d5fb0216080](https://github.com/pulp-platform/cheshire/pull/291)；Questa/DRAMSys [#267 / 703de67b50d2fc53fe833eb18a9269058b39dd46](https://github.com/pulp-platform/cheshire/pull/267) | 当前工具环境已用、日常不生成RTL/装包；UseDramSys0＋VCS/GCC13不受GCC8 stdc++fs问题影响，不升级环境 |
| SDK [#256 / 4a3932e1bfb8ab72b2d934d65667caefbe2884fc](https://github.com/pulp-platform/cheshire/pull/256)；FPGA/新板卡/Verilator路线 | 固定裸机Make不等于SDK；没有针对当前libgcc编译模式的修复证据。保护本地FPGA，不改板卡/工具。开放[#306](https://github.com/pulp-platform/cheshire/pull/306)/[#259](https://github.com/pulp-platform/cheshire/pull/259)的pulp-v3/HPD/CMO方案属于架构迁移，开放[#230](https://github.com/pulp-platform/cheshire/pull/230)/[#307](https://github.com/pulp-platform/cheshire/pull/307)的主机仿真速度不是硬件性能 |

## 5. 最小验证范围与停止点

本节是拟执行的检查，**本轮一项也未运行**。优先复用已有非stub CSR、RVV 5976项、访存原子572项、22 B向量复制、32×32 fmatmul、HelloWorld、DMA及Serial RX用例；不是把它们全部套在每个补丁上。

| 候选 | 最小改动 / 对照单位 | 已发现的测试缺口与最小补充 | 受影响既有回归 | 候选特有停止点 |
| --- | --- | --- | --- | --- |
| P1 | 一份VSTU源码；其余源/配置/ELF相同 | 现有复制/尾部检查未强制“整队列先issue、B返回尚未commit”。在现有Ara测试平台控制返回/反压，提交恰好队列深度的store，随后释放B；检查每项提交、AW/W/B数量、数据及保护区。若SoC软件无法自然构造，报告定向单元证据，另跑SoC正常回归 | 22 B向量复制、RVV边界/存储；HelloWorld仅作基本启动 | 新增丢写/重复完成/通道不稳定，或需改变队列/LLC参数才能运行即停止。旧/新均超时须先辨别推进/异常/停滞，不能直接称补丁无效或死锁 |
| P2 | 一份VMFPU源码；保留当前FPnew与延迟参数 | 5976项含精确浮点加法，未覆盖相邻不同延迟结果竞争。优先复用官方blackscholes/现有Ara FP测试输入；不足时在既有RVV用例追加短混排序列，FP32/64、比较/转换/乘加/除法、独立vd及依赖vd、mask，核对每个目标寄存器与fflags。除法固有数值边界单列 | 原精确FP、32×32 fmatmul、非stub CSR；不把完整blackscholes成功当全部数值空间 | 新错误或未解释数值差异停止；等待周期变化先按正确性需要解释，不预先宣称加速；不为通过改FPU延迟或替换除法器 |
| P3 | norm一行；单独验证#18，不引#16 | 既有精确算例未测异常标志。最小补充标量fdiv.s/d与向量vfdiv：±0/±0、非零/±0、正常精确除法、被mask掉的异常lane及fflags累积。每项先准备操作数和清fflags，再设所需FS并执行/读取，防准备动作污染结果 | 精确FP及fmatmul；非stub CSR确认标志读取 | P3定向仍错或正常路径新增异常则停止；#29所述已有1ulp/UF/NX等问题保留，不把它们临时混为本补丁扩展范围 |
| P4a | VIP一行；相同测试ELF跑旧/新，作为中间对照 | 已静态读17个现有ELF：均单PT_LOAD、4KiB对齐、memsz非1024倍数，**不覆盖空尾burst**。复用HelloWorld源，仅在候选测试输出调整link布局产生1024/2048 B实载入段及非整倍数对照；**加0x10000001起1024 B截断反例**；先readelf确认。空PT_LOAD应由loader跳过，不伪造DPI/stub | F默认HelloWorld、原RVV ELF；R测试显式PRELMODE1；核对全部装载字节 | 无空burst不足以通过，还须完整装载；预期截断若复现，记P4a不能独立采用。是否继续P4b依该次授权，不自扩范围 |
| P4b | P4a实测中间结果＋VIP页切分；对原版和P4a分别比较 | 现有17ELF虽可跨多页，但1024 B burst均由页内0/0x400/0x800/0xc00开始，不能触发跨页。加合法第二PT_LOAD：页内0xff8起16 B，另测P4a截断反例、非8倍尾部、多/相邻段。核对每个burst不跨4KiB、全部字节和最终入口 | P4a输入、HelloWorld/RVV/fmatmul；SPI默认启动只作不受影响对照，不冒充该预加载路径 | 官方VIP仍按整beat补零；只检查定义允许的padding与邻段最终内容，不承诺任意guard不变。新的覆盖相邻段错误即停，不扩为SLINK接口重构 |
| P5 | 先固定旧HAL/同一ELF验证reps RTL修复，再单独去HAL多余清reps写并重建软件，明确两类变化的贡献 | 历史已有2D及wrapper检查不覆盖正常1D API。采用公开`dma_1d.spm.c`18 B搬运及`!\0`保护，源/目的初始化为不同值，核对完成ID、一次ND→backend传输提交且有实际读写、每字节和保护区；再检查不同残留reps状态下1D及2D→1D→2D顺序 | 原小2D、编号/上下半部访问、原通过长AW解耦、HelloWorld；iDMA后端未改，不预设重跑所有后端组合 | 若1D仍仅合成完成而没搬数据、2D退化或生成一致性不符，停止；触发共享LLC旧循环则记录并停，不降低在途数/改LLC求通过 |

P1/P2官方PR给出原因与触发描述，没有新增专用回归文件；P4a/P4b也没有配套新回归文件。维护者合并或第三方报告只能支持候选选择，不能代替上述实际验证。P3的后续#29提供0/0反例与独立复测线索，仍需在当前CPU/Ara集成中检查传播。P5的公开小用例来自Cheshire #203；未访问其nonfree CI，也不把私有CI声明当本工程证据。

**P5的生成来源范围已核实。** R中为iDMA `src/frontend/reg/tpl/idma_reg.sv.tpl`、`target/rtl/idma_reg64_2d_top.sv`和活动`target/rtl/idma_generated.sv`。若采用官方通用模板的完整reps hunk，同时保持现有`idma_reg32_3d_top.sv`及汇总内3D派生两行一致；3D未实例化，不能宣称动态验证。F已有映射只有`provenance/generation/idma/src/frontend/reg/tpl/idma_reg.sv.tpl`及`src/cheshire_soc/idma/target/rtl/idma_generated.sv`，**不新增独立_top文件**。另改`sw/include/dif/dma.h`删1D清reps行，保留四类32位指针和CONF接口；不用#66的protocol字段、hjson、寄存器包/头、新生成工具或清单改动。模板与当前派生文件按选定hunk同步，不默认全量再生成。

如选择C1，最小允许文件为`commit_stage.sv`与`ariane_pkg.sv`；保留crt0 Clean及WT断言。测试应在操作数准备、fflags清除后重新设FS=Initial/Clean，分别测fld、FPR算术、F2I改变NX/NV、仅读FPR、显式CSR写、取消指令；逐项观察FS及SD。规范允许保守置Dirty，因此仅读FPR后Dirty不是必然错误；真正修改FPR/fflags后仍Clean才是必查错误，见[官方FS/VS规则](https://docs.riscv.org/reference/isa/v20260120/priv/machine.html)。**F2I/SD失败即报告局部收益及残留，不写回原件，不自行串入#3469/#3638或自定义逻辑。** C2–C8及MMU/Ara其他候选若被选中，以§4各行给定最小范围和触发测试制定该轮具体命令；它们不自动加入P1回归任务。

## 6. 性能候选单列

| 候选 / 精确版本 | 性质及当前关系 | 本工程需要比较什么 | 建议 |
| --- | --- | --- | --- |
| CVA6 RAW/WAW #2881：[dcd5de6016f8643f431d5baa480549585632de31](https://github.com/pulp-platform/cva6/commit/dcd5de6016f8643f431d5baa480549585632de31)；后续#3009：[197f371c72d883ec6452809d82fb4299d8b5a939](https://github.com/pulp-platform/cva6/commit/197f371c72d883ec6452809d82fb4299d8b5a939) | **性能改进**：重写RAW选择、减少不必要WAW停顿；改`issue_read_operands`并新增`raw_checker.sv`，F静态清单需加入。#3009进一步移除rr_arb_tree以改善覆盖，不无依据称必需bug前置 | 相同ELF、输入、时钟/访存延迟/lanes/初态；标量准备及搬运循环，fmatmul标量金值与向量内核分别测`mcycle/instret`，配合WAW短序列issue停顿；同时检查结果、异常及原子/向量交互 | **暂缓**：尚无本工程瓶颈/收益数据，范围大于首批正确性修复；若专门选择性能任务，再定可接受收益与回退条件 |
| AXI id_remap #409：[e11c4f9ff48f2c5dfd15a6dbe31404908df7c34b](https://github.com/pulp-platform/axi/commit/e11c4f9ff48f2c5dfd15a6dbe31404908df7c34b) | 不改变配置的并发改善，当前实际作用点是SerialLink TX双向流量；单向RX或当前默认ELF装载未证明收益 | 同样ID/读写数据流、seed、AR/AW反压与端点延迟，检查数据/ID/ATOP/公平性，再测单位硬件周期完成事务、总周期及读写被无关通道阻塞的周期。先用已有平台可构造流量；若没有TX需求可不做 | 有条件验证；不由官方标题或主机耗时推算提升百分比 |
| Ara load/slide hazard下移 [开放#203](https://github.com/pulp-platform/ara/pull/203)，head `6b229498bd4fdf117ebcd2c3c414b9661a3b7f50` | 性能候选，改9文件/下游hazard；未合并，IPC/frequency检查不能视为已证明 | 固定向量复制/slide/依赖链及fmatmul，正确性后比较目标周期和停顿；不能只读PR宣传值 | 暂缓；不与正确性补丁打包 |
| CVFPU低精度、MXDOTP/PACE、新FMA流水线；CVA6 HPD/WB、超标量、新BHT等 | **新功能/架构或配置变化**，会改变操作/延迟/接口或支持范围；不是保行为维护 | 需要独立软件/ISA与数值范围、硬件参数、实现结果评估；本轮没有产品需求映射 | 不纳入本轮优先实施列表 |
| Cheshire MEMH/Verilator、原子PR中“10×仿真速度”等 | 工具/主机执行开销或修复错误等待后的观察；不能直接作为CPU/SoC硬件性能数据 | 若以后选择，只能分别记录主机耗时与目标周期，说明固定环境和原因 | 不作为本工程硬件加速依据 |

任何改变cache类型、LLC/总线拓扑、在途数、lane/VLEN或其他硬件参数的方案，均单列为架构/配置任务。本轮没有获得频率、面积或功耗数据；仿真周期减少不能推导这些实现指标。若正确性需要增加等待（例如P2），不得为了保留旧周期数撤掉必要等待。

## 7. 阶段 B/C 及授权边界

### A：本轮交付并停止

已完成实际版本/差异/配置核对、官方分支与候选diff/讨论检查、本文及现有索引/交接。只读访问现有产物的README/记录和ELF布局；没有执行ELF或仿真。没有恢复已清理工作区、生成RTL、升级工具或依赖。保护本地FPGA/RTL/sw、R/F及`.bender`、历史归档、TTY及其他工程、`/opt`和EDA工具。

### B：参考环境的隔离候选验证——另行授权

1. **先冻结本次实际输入。** 重新检查R/F变化，仅针对已选候选记录当前源、来源SHA、现有本地差异及配置。使用R现有成功编译清单和真实源码；不能从纯`e040`或官方最新分支重建一个遗漏FS/DMA/断言修正的“基线”。
2. **副本只携带当前候选需要的输入。** 对SoC候选，包含既有有效编译清单引用的源/include、原生成物、通用技术单元、TB/VIP/DPI、所需外设模型、当前配置、既有编译/运行入口、选定测试及必要软件/链接输入、来源许可。保持参考相对路径或在已有导出脚本中明确重定位；不把可写候选硬链接到原件。只有候选需要单元测试时再加入其现有单元平台。**不复制整个`.git`、整个`_e01`、历史simv/FSDB/trace、全部未使用依赖或整个验收归档。** 候选文件必须落在隔离目录，不能只换输出而仍编译原件。
3. **复用已有入口，不新增框架。** R成功静态编译脚本的历史位置为 `_e01/dma_vector_check/pr80_204_20261021/production_build/`，另有已使用的结果判定方法；实施前核实它们的现存位置和实际输入，若已归档只读取所需成员。局部调整候选源/输出引用即可，不预设重新Bender导出。若旧`run.py`隐式读取原输出绑定，先在该候选副本明确绑定当前输入，不能读旧缓存冒充新结果。**R当前start默认PRELMODE0；P4及拟保持F装载条件的候选须显式选BOOTMODE0/PRELMODE1**，不能依赖R默认。stub勿用。
4. **一次一个修复或确实不可拆组。** P1/P2/P3/P5各自独立；P4a→P4b保留中间测试；P5先RTL同ELF、再HAL重建对照；Ara #432的两个提交、MMU三个配套提交按组，不顺带迁相邻工具/架构变化。保留修改前文件及官方原始patch、局部适配差异；先旧后新使用同一测试输入与条件、不同新输出。若继续第二个候选，明确它是以上一已接受候选为基准，还是重新取原基准，不能混淆累计变化。
5. **证明范围。** 尽可能先复现旧行为，再验证修复和受影响既有用例；若当前配置无法复现，写明只有静态适用性/单元证明/回归通过中的哪一种证据。不能写伪造的“前失败后通过”。普通运行串行、无波形、每例默认600秒；超时先判断推进、异常或停滞；只在解释已出现失败需要时按原调试约定处理。
6. **结果必须按实际判据。** 保留目标、simv和入口三层结果、完成标记、断言、实际源/ELF/配置/命令/日志。F的现行解析语义是0正常、1目标失败、2断言/仿真错误、3其他simv错误、4未完成、124超时；R候选也须沿现有已验判据，不能仅看simv=0。原SPI padding仅“两读两写”已定位事件允许单列功能接受，仍返回2；不能放行其他告警。
7. **失败及停止。** 出现新增功能错误、未解释trace/协议变化、适配需要越过已选文件/接口/参数/依赖范围，保留失败输入和输出并停止；**已明确授权并列明的P4中间对照失败按§4的分步规则处理**，不当作最终通过。恢复只针对本轮候选改动；不用reset hard、整包覆盖或清理。**隔离副本通过不表示R原件已更新。** 是否写回R由阶段B授权明确；建议默认不写回。阶段B报告后停止，等用户决定是否采纳及授权C。

### C：同步独立正式工程并复验——另行授权

1. 只同步B已接受的hunk及必要前置项。按来源映射：依赖源→`src/cheshire_soc/<组件>/`，VIP→`src/tb/src/`，配置→当前合并版`src/config/cheshire_pkg.sv`，HAL按实际文件→`sw/include/dif/`或`sw/lib/dif/`；ROM仅在专门授权时同步`provenance/generation/bootrom/`源资料与`src/cheshire_soc/cheshire_top/bootrom/`活动生成SV。核对R验证后F是否又有改动，保留集中配置、共同wrapper、Bash入口及Make，不整包覆盖。
2. 先保存将改文件及相关来源/patch记录，作为可恢复输入；检查静态分组/include、重复定义、生成模板/生成物及许可证。P1–P5不应需要新增源或改变静态分组，P5需同步现有生成资料；RAW/WAW优化若另选才添加`raw_checker`。没有依据就不改清单。修改后更新现有来源清单/差异记录，不新增依赖管理机制。
3. 用F现行compile/start与Make，在**显式新BUILD_DIR/RUN_DIR/软件输出**重建受影响部分并运行已选定向和受影响回归。RTL候选可先复用同ELF做纯硬件对照；改软件才重建相关软件。不调用Bender，不在线下载/解析/更新依赖；不引入R绝对路径、旧`.bender`活动路径或旧缓存。正常联网及VCS既有许可通信沿用，无额外工程禁网要求。
4. 正式工程通过才记“已同步、正式复验通过”；R通过不能替代F。失败保留报告与日志，按本轮文件备份恢复到修改前的**实际版本**，不影响其他后续改动。若授权只允许报告不允许恢复原件，则停止等待处理，不扩大为全量升级。
5. 更新本文候选状态、现有E01交接及必要共享状态：官方SHA、实际版本/适配差异、运行证据、恢复方法及未关闭项。阶段C结束停止。上述通用模型仿真不代表ASIC/物理实现/流片验收。

### 保留的限制

DMA共享LLC的读挡写、写挡读、Bloom行锁循环保持；用户暂停扩展排查的决定不变。选了某个iDMA/LLC/原子修复也不自动重开该任务。原FS Dirty原因、libgcc特定128-bit除法在DRAM高地址的重定位限制、未解释旧warning、ROM padding限定事件逐项保留；只有对应实际新证据才改结论。历史测试路径按 `~/CheshireAra_validation_archive_20261022/validation.tar.gz` 内原目录名前缀定位，按需读取单个成员，不能恢复整个旧工作区。

## 8. 当前需要用户决定的事项

1. **选择首个阶段B候选。** 建议P1；若当前更关注浮点结果，选P2或P3；若要先完善DMA现有API，选P5。日常加载入口可另选P4a/P4b分步评估，明确P4a只是中间对照且可能失败。也可以保持现状，不安排更新。
2. **阶段B的写回边界。** 建议只允许隔离候选副本及新输出，验证后报告；如希望通过后写回R原件，需要在该次授权中明确。无论是否写回R，F均等待阶段C另行授权。

不需要用户现在决定整套依赖升级、换cache、改拓扑/参数或引入新工具。C1等条件候选及性能任务只有被明确选中时再实施。**本轮在阶段A交付后停止。**

## 附录：完整锁定版本与补充范围

本表逐项锁SHA与本轮实际依赖HEAD相符；F路径通常为`src/cheshire_soc/<组件>/`，配置、TB、软件和生成资料以现有manifest为准。`无`仅指当前依赖相对锁定HEAD无跟踪差异，不表示该组件无缺陷。

| 组件 / 官方源 | 锁定版本 | 完整SHA | 当前依赖差异 |
| --- | --- | --- | --- |
| [apb](https://github.com/pulp-platform/apb) | 0.2.4 | `77ddf073f194d44b9119949d2421be59789e69ae` | 无 |
| [apb_uart](https://github.com/pulp-platform/apb_uart.git) | 0.2.1 | `6c7dde3d749ac8274377745c105da8c8b8cd27c6` | 无 |
| [ara](https://github.com/pulp-platform/ara.git) | 固定提交 | `2895ba907e9eb14b3464609dc791a969d159a7c3` | 无 |
| [axi](https://github.com/pulp-platform/axi.git) | 0.39.6 | `39f5f2d51c5e524f6fc5cf8b6e901f7dcc5622d7` | 无 |
| [axi_llc](https://github.com/pulp-platform/axi_llc.git) | 0.2.1 | `559bcbd09a5a884dbe31e2d72fd95d024e357f39` | 无 |
| [axi_riscv_atomics](https://github.com/pulp-platform/axi_riscv_atomics.git) | 0.8.2 | `0ac3a78fe342c5a5b9b10bff49d58897f773059e` | 无 |
| [axi_rt](https://github.com/pulp-platform/axi_rt.git) | 0.0.0-alpha.9 | `641ea950e24722af747033f2ab85f0e48ea8d7f8` | HJSON、生成RTL及头4文件；功能关闭 |
| [axi_stream](https://github.com/pulp-platform/axi_stream.git) | 0.1.1 | `54891ff40455ca94a37641b9da4604647878cc07` | 无 |
| [axi_vga](https://github.com/pulp-platform/axi_vga.git) | 0.1.3 | `3718b9930f94a9eaad8ee50b4bccc71df0403084` | 无 |
| [clic](https://github.com/pulp-platform/clic.git) | 2.0.0 | `8ed76ffc779a435d0ed034f3068e4c3334fe2ecf` | 无 |
| [clint](https://github.com/pulp-platform/clint.git) | 0.2.0 | `d5390a805c20f9226758a152ba1645f61da73349` | HJSON及生成RTL4文件 |
| [common_cells](https://github.com/pulp-platform/common_cells.git) | 1.33.0 | `13f28aa0021fc22c0d01a12d618fda58d2c93239` | 无 |
| [common_verification](https://github.com/pulp-platform/common_verification.git) | 0.2.3 | `9c07fa860593b2caabd9b5681740c25fac04b878` | 无 |
| [cva6](https://github.com/pulp-platform/cva6.git) | 固定提交 | `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c` | 两份WT读断言 |
| [dram_rtl_sim](https://github.com/pulp-platform/dram_rtl_sim.git) | 0.1.1 | `2cac4a9e12a60537567276b539ab6c919c87b5dc` | 无 |
| [fpnew](https://github.com/pulp-platform/cvfpu.git) | 0.2.3 | `e5aa6a01b5bbe1675c3aa8872e1203413ded83d1` | 无 |
| [fpu_div_sqrt_mvp](https://github.com/pulp-platform/fpu_div_sqrt_mvp.git) | 1.0.4 | `86e1f558b3c95e91577c41b2fc452c86b04e85ac` | 无 |
| [idma](https://github.com/pulp-platform/iDMA.git) | 0.6.3 | `c12caf59bb482fe44b27361f6924ad346b2d22fe` | #80/#204，共36文件 |
| [irq_router](https://github.com/pulp-platform/irq_router.git) | 0.0.1-beta.1 | `d1d31350b24f3965b3a51e1bc96c71eb34e94db3` | 无 |
| [obi](https://github.com/pulp-platform/obi.git) | 0.1.5 | `5321106817e177d6c16ecc4daa922b96b1bc946b` | 无 |
| [opentitan_peripherals](https://github.com/pulp-platform/opentitan_peripherals.git) | 0.4.0 | `cd3153de2783abd3d03d0595e6c4b32413c62f14` | PLIC配置/生成RTL及头7文件 |
| [register_interface](https://github.com/pulp-platform/register_interface.git) | 0.4.4 | `ae616e5a1ec2b41e72d200e5ab09c65e94aebd3d` | 无 |
| [riscv-dbg](https://github.com/pulp-platform/riscv-dbg.git) | 0.8.1 | `358f90110220adf7a083f8b65d157e836d706236` | 无 |
| [serial_link](https://github.com/pulp-platform/serial_link.git) | 1.1.1 | `5a25f5a71074f1ebb6de7b5280f2b16924bcc666` | 单通道HJSON NumBits16→8及生成RTL3文件 |
| [tech_cells_generic](https://github.com/pulp-platform/tech_cells_generic.git) | 0.2.13 | `7968dd6e6180df2c644636bc6d2908a49f2190cf` | 无 |
| [unbent](https://github.com/pulp-platform/unbent.git) | 0.1.6 | `e9c9d5cfb635f2d4668c816ce9235798cfecb297` | 无 |

其他基础IP按版本及实际消费者登记；本轮未逐提交审查apb、axi_stream、axi_vga、clic、irq_router、obi、unbent等所有功能。Clic/AXI-RT/IRQ router及DRAMSys未启用；其他目录存在或通过编译不构成其全部功能验收。重点调查深度已在§3–4逐项说明，不作“全部上游缺陷已排除”的结论。

复查入口：

- [E01现行提取计划](server_reference_extraction_plan.md)，包括配置合并、Bash入口和历史搬迁结果。
- [E01主题交接](../../../handoffs/E01_fixed_vector_extraction.md)。
- [参考测试与限制](../reports/reference_rebuild_check.md)：§3启动/FS，§5 WT断言，§8 #80/#204，§9–10 LLC限制，§12剩余验收。
- 服务器现有`provenance/{reference,source_manifest,regression_inputs}.json`、`patches/`、当前README/docs及编译入口；旧路径以验收归档成员为准。
