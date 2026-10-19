# E01 / 参考工程五步完成情况核查

日期：2026-10-18。参考工程：`zhaowy24@172.16.0.243:~/CheshireAraPULP`。本地输入：`2f0f2d6f85979709fbc99dd4098447cb5587ce5f`。

2026-10-19增量：用户按精简官方入口完成新一轮fmatmul；Agent只读确认`target/sim/vcs/simulate.log`中的Passed、SLINK SUCCESS及正常结束，主机退出状态**未取得**。随后按明确授权删除四个旧`rvv_fmatmul_01`～`04`目录、旧HelloWorld备份`vcs_before_wave`及空重建目录，保留最新完整产物及工具链证据；清理前后394个保留文件哈希一致。具体配置、输入哈希、警告、清理清单和边界见[E01交接最新检查节](../../../handoffs/E01_fixed_vector_extraction.md#2026-10-19-最新普通仿真检查与清理已完成)。以下为2026-10-18历史检查，所引已删除服务器目录不再可直接访问，结论与已有本地证据仍保留；不把旧退出码用于新运行。

**最新结论（2026-10-18）：参考工程重建及单个32×32 fmatmul向量测试通过，启动FS兼容修正已在该测试中验证；完整RVV/独立提取验收仍未完成。** 速查第5步命令只构建软件，随后用户另行运行；第1—5节保留五步初查快照，第6节记录故障定位及最终成功，复现修复见[速查Q07](../planning/server_reference_rebuild_guide.md#q07)。

本轮通过SSH只读核查Git、Python包、清单、日志、ELF及反汇编；未重跑编译、展开或仿真，未修改服务器文件、系统工具或TTY工程。详细命令、输出摘录、时间戳和哈希见[证据快照](evidence/reference_check_2026-10-18.json)。

## 1. 五步检查结果

| 步骤 | 核查结果 | 证据与边界 |
| --- | --- | --- |
| 1 源码与依赖 | 匹配既定版本 | Cheshire=`e040b7bbc…`；26项依赖HEAD均匹配原锁文件；Ara=`2895ba907…`、CVA6=`99eac9a64…`；`Bender.lock/yml`无差异；printf子模块为`0dd4b64…` |
| 2 工具环境 | Python依赖一致，VCS/DPI已有实际使用证据 | 本轮`pip check`退出0，输出`No broken requirements found.`；Python3.9.25，当前pip为26.0.1；tclint0.4.2、importlib-metadata6.8.0、pathspec0.11.2、tomli2.0.2。现有展开/运行日志证明当次VCS许可与本机C++联编可用 |
| 3 硬件与清单 | 向量组合正确，显式路径完整 | 716个独立源文件、18个include目录均存在；仅选择`cv64a6_imafdcv_sv39` CPU profile和Ara真实decoder；宏ARA/2 lanes/VLEN2048正确；两份外设模型存在；展开日志确认`SelectedCfg=3` |
| 4 标量仿真 | 已有日志确认成功 | `simulate.log`明确加载`helloworld.spm.elf`，显示`[UART] Hello World!`、`[SLINK] SUCCESS`并正常`$finish`；指令trace从Boot ROM地址`0x02000000`开始。该运行是Serial Link preload，不是SPI自主加载验收 |
| 5 向量软件 | 预期构建产物齐全 | Ara入口的18个C源，对应SPM/DRAM/ROM三种布局共54个ELF、54个dump及36个ROM/GPT memh均存在；抽查ELF含RVV指令。没有找到向量程序运行日志，原软件构建完整控制台日志和退出码未保存于所查目录 |

根仓库已跟踪文件无差异；依赖工作树的axi_rt、clint、opentitan_peripherals、serial_link有生成文件差异，其位置与官方`hw-all`生成范围一致，不当作依赖升级或擅自清理对象。未逐个证明全部生成差异的语义等价。Ara/CVA6已跟踪源码无差异，Boot ROM RTL与固定提交一致。

## 2. 仿真证据

服务器日志目录：`~/CheshireAraPULP/target/sim/vcs/`。

`elaborate.log`关键输出：

```text
assign 3 /tb_cheshire_soc/SelectedCfg (global:"command line":0)
assign 3 /tb_cheshire_soc/fix/SelectedCfg (global:"command line":0)
All of 277 modules done
../simv up to date
```

同一日志记录GCC toolset13的G++编译`elfloader.cpp`并链接`simv`；版本为VCS W-2024.09-SP1_Full64。现有日志中未发现`Error-[...]`。

`simulate.log`关键输出：

```text
[SLINK] Wait for LLC configuration
[SLINK] Preloading ELF binary: /home/zhaowy24/CheshireAraPULP/sw/tests/helloworld.spm.elf
[ELF] INFO: Entrypoint at 0x10000000
[SLINK] Preload complete
[SLINK] Wrote launch signal and entry point 0x0000000010000000
[UART] Hello World!
[SLINK] SUCCESS
$finish at simulation time           2210659000
```

这支持当次标量程序成功完成，不只是`simv`文件存在。但原进程退出码未另存；第5步软件构建时间晚于此日志，当前同名HelloWorld ELF已被重建，因此本轮计算的ELF哈希不能回填为当次运行输入哈希。后续测试需绑定实际ELF及日志，保留本次结果。

## 3. 软件检查与剩余范围

- `vector_helloworld.spm.elf`、`fmatmul.spm.elf`均为RISC-V ELF64、double-float ABI、入口`0x10000000`。
- 前者反汇编包含`vsetivli`、`vle8.v`、`vse8.v`；后者包含`vsetvli`、`vle64.v`、`vfmacc.vf`。已确认真实向量指令，不以文件名判定。
- 抽查vector_helloworld、fmatmul、rvv_test_vstart_csrs：启动代码在首个浮点初始化前设置FS；各自main中可见`li t0,1536`和`csrs mstatus,t0`设置VS，早于所见向量指令。这是反汇编证据，不等于所有路径或所有程序运行正确。
- 官方`vector_helloworld`源码仍有`printf("%s", str_v)`，且没有充分的计算结果/尾部检查；不能将其作为最终RVV验收测试。fmatmul有标量金值比较，可作为后续单个运行候选，但默认32×32也不替代不同VL及尾部测试。
- 全工程共63个测试ELF；18个Ara源的54个目标均已找到，临时复制的Ara C源已按官方成功路径移除。结果与用户报告的软件构建完成一致，但未保留的编译命令/退出码不作补造。
- S01-T01（特定libgcc 128-bit除法成员的DRAM高地址重定位限制）仍开放；本次部分DRAM ELF存在不能证明该库成员已修复。

## 4. 新发现的VCS warning

这些不是此前Bender W28，不能沿用“两份头文件可忽略”的结论。

| 警告 | 日志数量 | 本轮初查与处理 |
| --- | --- | --- |
| `Warning-[SIOB] Select index out of bounds` | 展开日志245条 | 主要在CVA6；抽查`instr_queue`、`issue_read_operands`的越界项位于`SuperscalarEn`条件内，而当前profile该值为0；TLB还存在未选条件分支中的索引表达式。尚未逐条关闭，保留日志并按参数/可达分支分类，不全局屏蔽、不批量改RTL |
| `Warning-[ENUMASSIGN] Illegal assignment to enum variable` | 展开日志9条 | 涉及LLC、Ara等结构体默认赋零。需核对枚举合法值和默认字段使用；未阻止本次标量运行，尚未完成全部语义审查 |
| `Warning-[RT-NCMUCS] No condition matches in statement` | 运行日志1条 | `axi_inval_filter.sv:85`，仅在`0ps`出现；源码状态机复位到Idle，日志现象与时间零状态尚未初始化相符。暂记启动瞬间警告，后续若在复位后复现，必须继续定位 |

代表性原文：

```text
Warning-[SIOB] Select index out of bounds
.../core/frontend/instr_queue.sv, 446
"pc_j[2]"
  The select index is out of declared bounds : [1:0].

Warning-[ENUMASSIGN] Illegal assignment to enum variable
.../src/hit_miss_detect/axi_llc_tag_store.sv, 258
axi_llc_tag_store, "req_q <= '{default:'0};"
  The type bit [0:0] is incompatible with the enum 'tag_mode_e'

Warning-[RT-NCMUCS] No condition matches in statement
.../hardware/src/axi_inval_filter.sv, 85
  No condition matches in 'unique case' statement.
  at time 0ps.
```

## 5. 最小下一步

1. 保留当前标量日志；按用户逐步确认流程，选择一个有明确结果检查的官方小向量程序执行VCS，记录输入ELF哈希、命令、超时、目标返回值及日志。
2. 补齐不同VL/尾部、基础访存和原子测试，以及SPI自主启动路径；现有Serial Link preload与ROM起始trace不能替代自主加载验收。
3. 对上述warning完成必要的参数/分支审查，再确定哪些可保留、哪些需最小适配；不以编译成功直接接受全部警告。

`~/CheshireAra` 仍为空，独立提取和搬迁验收尚未开始。当前成果可作为继续验证的参考工程，尚不能宣称固定向量提取基线已验收。

## 6. 首次 fmatmul 运行超时诊断（2026-10-18 增量）

用户执行前述单测试命令后返回 `124`。Agent本轮经SSH只读核对，未重新编译、仿真或修改服务器。此节更新前文“没有向量程序运行日志”的历史状态：**已有首次尝试，但在向量计算开始前发生异常，未通过。**

**现象与实际证据：**服务器目录 `~/CheshireAraPULP/_e01/rvv_fmatmul_01/` 保留 `simulate.log`、两份trace、`inputs.sha256`、`exit.status`。后者为124，对应用户命令的600秒超时；主日志止于：

```text
[SLINK] Wrote launch signal and entry point 0x0000000010000000
```

`trace_hart_0.log` 第37505行出现唯一一次异常：

```text
Exception @2811345000, PC: 00000000100012e0, Cause: Illegal Instruction,
                tval: 000000000000ac22
```

对实际输入ELF执行以下只读反汇编，确认异常指令是 `main` 序言保存浮点寄存器，默认异常处理则原地循环：

```bash
/opt/riscv/bin/riscv64-unknown-elf-objdump -d \
  --start-address=0x100012bc --stop-address=0x100012e8 \
  ~/CheshireAraPULP/sw/tests/fmatmul.spm.elf
/opt/riscv/bin/riscv64-unknown-elf-objdump -d \
  --start-address=0x1000018c --stop-address=0x10000190 \
  ~/CheshireAraPULP/sw/tests/fmatmul.spm.elf
```

```text
100012e0: ac22       fsd fs0,24(sp)       # 压缩编码 c.fsdsp
1000018c: 0000006f   j   1000018c <trap_vector>
```

Trace共2,276,408行，其中该trap PC出现2,238,884次；最后仿真时间为36,395,105ns。异常在约2.811345ms仿真时间发生，早于首个printf和向量计算。**延长timeout不能解除这个死循环；没有证据将其归因于矩阵规模、VCS许可证或RVV计算耗时。**

输入绑定（当前文件哈希与运行前保存值相同）：

| 文件 | SHA256 |
| --- | --- |
| `target/sim/vcs/simv` | `540e4f917be8bfd5db03239da35c3022e2408a882e894ed78dbf55c52b704920` |
| `sw/tests/fmatmul.spm.elf` | `3c78ea067ab80dcc1dde25e13a0b633e071f4976d7e3c2042de01d76cbc97d89` |
| `sw/lib/crt0.S` | `b6b305f14dc866903fb9d0c0dee51a0758141b6742b793bf265776f19c2ef7f7` |
| 本次 `simulate.log` | `14f6db8204e113b04b6fdb2f0fb5b2b8956248ae4cea41d951eae4dd2d7c1e6c` |

**原因层次：**已确认的直接原因是浮点保存指令触发非法指令异常，默认 `trap_vector` 不报告结束、一直自跳转，最终被timeout终止。首要待证根因是进入main时的FS状态。原版 `sw/lib/crt0.S:111–112` 注释为设置Clean，实际仅执行 `csrc mstatus,t1`，此时t1为0x2000：若FS原为Dirty(11)，结果为Clean(10)；若原为Initial(01)，结果却为Off(00)。[RISC-V特权规范](https://docs.riscv.org/reference/isa/priv/machine.html)规定FS=Off时访问浮点状态触发非法指令。

现有trace只显示该CSR指令的源寄存器值，没有读回mstatus；不能把0x2000当成mstatus实测值，也不能据此断言FS确实变成Off。当前CVA6 RTL另有浮点提交置Dirty逻辑，因此为何出现异常仍须读回状态确认；暂不宣称硬件Dirty逻辑有缺陷。此前“首个浮点初始化前已设置FS”的检查不足以证明进入main时仍然有效，现收紧该结论。

**最小处理方案（待用户执行）：**在独立诊断副本中，仅在上述清位指令前后分别插入 `csrr t2,mstatus`、`csrr t3,mstatus`，复用原始fmatmul输入与官方软件链接规则重编一个诊断ELF；用原simv在新输出目录短时运行，由trace读回 `(mstatus >> 13) & 3`。这一步不改原源码、库、RTL或现有ELF。

- 若读回确认FS由01变00：启动副本改为显式设置FS=Clean，即清0x6000后置0x4000，再进入main；复跑矩阵比较。需要在C函数入口前修复，不能把补丁仅放在main内部，因为异常指令属于编译器生成的函数序言。
- 若main前FS已为10/11：上述假设被否定，转查C.FSDSP展开、标量浮点store译码及实际硬件配置；不盲目改启动代码或批量重编RTL。
- `fmatmul`源码另有printf早于UART初始化的顺序问题，但本次尚未执行到printf，不能把它写成本次已证实根因。

**验证状态：**只读诊断完成，异常/死循环确认；mstatus读回、根因最终确认、修复及RVV结果比较均未完成。保持既定CPU/Ara配置和依赖版本。

### 第二次诊断：FS被关闭已实证（2026-10-18）

用户自行重编并运行 `_e01/rvv_fmatmul_02/`，180秒超时、退出124。Agent经SSH只读核对输入哈希、trace与反汇编；未代运行仿真。simv哈希仍为上表值；诊断ELF哈希为 `e51af8a5bd2e94a7b2cecd9dbe471d3e96af63aa2b7861075861b4f99fc16de8`，当前ELF与本次inputs.sha256一致，两条新增CSR读数已经实际执行：

```text
2810760ns ... 1000010e ... csrr  t2, mstatus  t2:0000000a00002000
2810770ns ... 10000112 ... csrrc t1, mstatus  t1:0000000000002000
2810890ns ... 10000116 ... csrr  t3, mstatus  t3:0000000a00000000
Exception @2811445000, PC: 00000000100012e8, Cause: Illegal Instruction,
                tval: 000000000000ac22
```

`(t2 >> 13) & 3 = 1`，`(t3 >> 13) & 3 = 0`：**FS确实由Initial变为Off**。实际ELF的 `0x100012e8` 仍为 `c.fsdsp fs0,24(sp)`；末尾仍自循环于 `0x1000018c`。这关闭了上一段“是否被关闭”的疑问；诊断不是旧ELF重跑，地址移动8字节与新增两条指令一致。

最小修复建议是在用户已修改的服务器 `sw/lib/crt0.S` 中保留前后读回，将中间设置FS的操作改为显式Clean：`li t1,0x6000; csrc mstatus,t1; li t1,0x4000; csrs mstatus,t1`。重编单个ELF后另存新运行目录，确认后读数FS=2且越过原异常，再检查矩阵结果。该修复尚未应用/验证，不宣称RVV通过。

本次实证说明启动代码对Dirty状态的假定在此运行中不成立；**为何清零浮点寄存器后仍为Initial，仍属独立待查项**，不可将软件显式设置FS的方案当作CVA6状态跟踪已验证或已修复。本轮不升级依赖、不改RTL。

### 第三次运行：FS修正生效，标量计算尚未结束（2026-10-18）

用户运行 `_e01/rvv_fmatmul_03`，沿用180秒限时，退出124。Agent只读核对：simv哈希不变，新ELF哈希 `4746bc7ebd17bae54adf2732e03720e385277ba92e88690474880b91152dc626` 与运行前记录一致。前读数t2=`0x0000000a00002000`，后读数t3=`0x0000000a00004000`，确认FS显式设置为Clean(2)。原main入口异常已越过，现有完整trace未检出 `Exception`，旧trap地址0x1000018c执行次数为0。

UART输出已到 `Calculating fmatmul on scalar core...`。反汇编确认PC `0x100014d6` 是标量三重循环的 `fmadd.d`；trace共执行24,413次，预期32³=32,768次，即约74.5%。已完成762个输出元素，正在计算第763个（零基行23、列26）；末尾循环索引a3从0x2fb推进到0x2fd、边界s0=0x300，持续执行浮点加载/乘加/循环判断，最后仿真时间10,505,645ns。数据表明此轮被限时中断时仍在推进标量参考结果计算，不是此前trap死循环；尚未到向量内核或结果比较，不作RVV通过结论。

最小下一步：无需再改源码、重编软件或RTL，使用同一ELF/simv，在新目录 `_e01/rvv_fmatmul_04` 从复位重跑，将诊断用180秒限时恢复为600秒。这是基于本轮已观察到的有效进展调整预算，不是对前两轮异常循环延长等待；完成时间仍取决于后续执行和服务器负载。修复后完整矩阵比较、RVV执行及硬件Dirty状态跟踪仍待验证。

### 第四次运行：单个向量矩阵测试通过（2026-10-18）

用户在600秒限时内完成运行，Agent经SSH只读核对 `_e01/rvv_fmatmul_04/exit.status` 为0，`simulate.log`包含如下实际输出：

```text
[UART] fmatmul kernel:
[UART] Calculating fmatmul on scalar core...
[UART] Calculating fmatmul on vector core...
[UART] The execution took 19883 cycles.
[UART] The performance is 3.296082 FLOP/cycle (82.402054% utilization).
[UART] Verifying result...
[UART] Passed.
[SLINK] SUCCESS
$finish at simulation time          26019135000
Time: 26019135000 ps
CPU Time: 402.720 seconds; Data structure size: 517.3Mb
```

输入记录与当前ELF匹配；simv与第三次相同，成功不依赖重新编译硬件：

| 输入 | SHA256 |
| --- | --- |
| simv（运行前记录） | `540e4f917be8bfd5db03239da35c3022e2408a882e894ed78dbf55c52b704920` |
| fmatmul.spm.elf（运行前记录及当前文件一致） | `4746bc7ebd17bae54adf2732e03720e385277ba92e88690474880b91152dc626` |
| 修订后的crt0.S（本轮读取） | `f173151553881fd6002b8a23108828fb3b38e585df46322abe07194e0f0a81d1` |

本次确认官方32×32测试在既定向量硬件配置、SPM布局、Serial Link preload路径下完成标量金值、向量内核及程序自带比较，FS显式设置的兼容修正通过该测试。19883为软件内核计时打印，402.720秒为VCS主机CPU Time，不等于墙钟时间或目标执行时间；性能输出不作为已校准指标。

完整报错、原因、修复代码、单ELF重编及重跑说明集中在[速查Q07](../planning/server_reference_rebuild_guide.md#q07)。本轮仅文档更新和远端只读复核；未代执行构建/仿真，未改共享状态。仍待：FS Dirty状态跟踪原因、测试比较器/输入局限及不同VL/尾部、访存原子、SPI自主启动、固定工程提取和独立性验收。前文“未通过/待运行”均为对应阶段历史，不覆盖本段结果。
