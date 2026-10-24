# 参考工程详细记录存档（精简前）

2026-10-20 保存，包含本轮对齐检查。后续不更新；历史“最新／待修复”语句只代表各次记录时点，当前结论以[主报告](../reference_rebuild_check.md)为准。正文内容保留，仅调整相对链接以适应存档位置。精简前原文 SHA256：`8ea1b2c7597f4d0d8133a4ab44d5f692a874ba5b3d42c485aaa0582adf87853c`。

---

# E01 / 参考工程检查与定向测试报告

**最新断言结果（2026-10-20）：**服务器 WT 读断言已按有效字节检查并打印采样值；54 项定向检查、长 DMA/HelloWorld/向量复制三项回归通过，原长 DMA 误报消失，三份 CPU trace 与修改前一致。准确修改行号及前后代码见[第 12 节](#read-assertion-fix-20261020)。下述第 11 节的 DMA/LLC 死锁仍未解决；旧断言记录保留作为修复前结果。

**最新复核（2026-10-20）：新旧死锁的直接原因不同。** 新失败发生在第 14 行分段后的首个写拍：需要 8 B，但只有 4 B，补足数据的读又被后续写挡住。原默认死锁则是读返回缓冲满、读挡写。新增 8 组单变量对照中 7 组通过、14 行组复现；通过组的内部采样也确认所需读先行后，数据可以补齐。**“非对齐、不同步长”不是充分触发规律。** 先看[第 11 节的对照表和原因](#dma-cause-confirmation)；下面保留上轮长度/场景表及历史记录。

<a id="dma-test-matrix"></a>

## 上轮实际测过的 DMA 长度与场景

**尚未测出“哪些长度/对齐/步长必然失败”的边界。** “非对齐、不同步长”是一个失败用例的参数描述，不是已经证明的失败规律。此前“9 项成功”还包含寄存器检查、HelloWorld 和向量复制，不能理解成 9 种 DMA 长度均已验证。

以下 DMA 均为 **SPM 源区 → SPM 目的区**，通过非缓存别名访问。步长指“下一行起点减当前行起点”，不是行尾之后的空隙；总请求字节数为行数×每行字节数。

| 场景 | 每行字节 × 行数＝每笔请求量 | 源/目的步长（字节） | AW 解耦 | 实际结果 |
| --- | --- | --- | --- | --- |
| 官方短测试及编号检查 | 15×4＝60 B | 1 / 7 | 关 | 两个用例均通过；各行有重叠，目的实际覆盖 36 B，另检查 2 B 末尾保护字符 |
| 原长测试，历史失败对照 | 256×32＝8192 B（8 KiB） | 256 / 256 | 关 | 首笔死锁；此前新、旧 RTL 均复现，本次未重复运行 |
| 同一原长测试，新 HAL | 256×32＝8192 B（8 KiB） | 256 / 256 | 开 | 连续 3 笔功能检查通过；保留 1 次已定位的 CVA6 断言 |
| 同 bank 内高地址向低地址搬运 | 128×32＝4096 B（4 KiB） | 128 / 128 | 开 | 连续 2 笔通过 |
| 跨 bank，搬运范围跨 4 KiB 边界 | 128×32＝4096 B（4 KiB） | 128 / 128 | 开 | 连续 2 笔通过 |
| 同上，同时 CPU 访问独立区域 | 128×32＝4096 B（4 KiB） | 128 / 128 | 开 | 连续 2 笔通过 |
| 非对齐起点＋非整拍行长＋不同步长 | 123×16＝1968 B | 139 / 149 | 开 | **首笔死锁，第二笔未执行** |

后三个通过的 4 KiB 用例及通过的 8 KiB 用例，源/目的起点均按 64 B 对齐，每行长度和步长也都是 64 B 的整数倍。它们只证明这些具体布局通过，不能推出“所有对齐搬运都安全”或“8 KiB 是安全上限”。本次没有做长度扫描。

失败用例具体是：

- 源起点 `0x14008043`，相对 8 B 数据拍偏移 **3 B**；目的起点 `0x14010045`，偏移 **5 B**。
- 每行复制 **123 B**；源步长 **139 B**，即行间留 **16 B**；目的步长 **149 B**，即行间留 **26 B**。
- 第 i 行的源/目的起点偏移分别为 `(3+3i) mod 8`、`(5+5i) mod 8`，因此每行对齐关系不断变化，读写的 64 B 分块边界也不能直接一一对应。
- 停住的描述符对应第 14 行（从 0 计为第 13 行）：当前写需要后续源读的数据，但该读请求被后续写描述符挡住。第 10.4 节给出实际地址及内部采样。

**上轮仅确认一条循环等待及一个具体触发组合，尚未分别对照各参数；本轮已完成第 11 节所列的 8 组单变量对照。** 官方短测试同样包含非整拍行长、不同步长和非对齐的后续行，却能通过，但它关闭了 AW 解耦，也不能代替 AW 开启时的单变量对照。因此，不能把当前结果总结成“非对齐就失败”“不同步长就失败”或“大于某个长度就失败”。当前仍未穷举参数范围；不能把有限对照推广成普遍安全或失败规则。

**2026-10-20 当前结果：**官方 DMA 按次配置接口已回移；原对齐长搬运及基本回归通过，非对齐/不同步长组合出现写挡读死锁，整体定向验收未通过。详见[第 10 节](#dma-aw-config-20261020)。以下第 1–9 节及旧“最新结果”段均保留为历史记录，不覆盖本段。

**2026-10-20 最新结果：**已实际执行 DMA 与向量 HelloWorld 定向测试。向量复制修正副本比较通过；DMA 原版小用例的数据比较通过，但内部信号与诊断用例确认控制寄存器的返回位置、64 位写入存在问题。此外，目标程序失败时，当前 VCS 进程仍可能退出 0。测试项、结果、原因和服务器产物见[第 7 节](#dma-vector-tests-20261020)。参考 RTL、驱动原件、配置及已有结果未改，stub 用例未运行，未开始提取。

日期：2026-10-18。参考工程：`zhaowy24@172.16.0.243:~/CheshireAraPULP`。本地输入：`2f0f2d6f85979709fbc99dd4098447cb5587ce5f`。

2026-10-19增量：用户按精简官方入口完成新一轮fmatmul；Agent只读确认`target/sim/vcs/simulate.log`中的Passed、SLINK SUCCESS及正常结束，主机退出状态**未取得**。随后按明确授权删除四个旧`rvv_fmatmul_01`～`04`目录、旧HelloWorld备份`vcs_before_wave`及空重建目录，保留最新完整产物及工具链证据；清理前后394个保留文件哈希一致。具体配置、输入哈希、警告、清理清单和边界见[E01交接最新检查节](../../../../handoffs/E01_fixed_vector_extraction.md#2026-10-19-最新普通仿真检查与清理已完成)。以下为2026-10-18历史检查，所引已删除服务器目录不再可直接访问，结论与已有本地证据仍保留；不把旧退出码用于新运行。

**历史结论（2026-10-18）：参考工程重建及单个32×32 fmatmul向量测试通过，启动FS兼容修正已在该测试中验证；完整RVV/独立提取验收仍未完成。** 速查第5步命令只构建软件，随后用户另行运行；第1—5节保留五步初查快照，第6节记录故障定位及最终成功，复现修复见[速查Q07](../../planning/server_reference_rebuild_guide.md#q07)。

本轮通过SSH只读核查Git、Python包、清单、日志、ELF及反汇编；未重跑编译、展开或仿真，未修改服务器文件、系统工具或TTY工程。详细命令、输出摘录、时间戳和哈希见[证据快照](../evidence/reference_check_2026-10-18.json)。

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

完整报错、原因、修复代码、单ELF重编及重跑说明集中在[速查Q07](../../planning/server_reference_rebuild_guide.md#q07)。本轮仅文档更新和远端只读复核；未代执行构建/仿真，未改共享状态。仍待：FS Dirty状态跟踪原因、测试比较器/输入局限及不同VL/尾部、访存原子、SPI自主启动、固定工程提取和独立性验收。前文“未通过/待运行”均为对应阶段历史，不覆盖本段结果。

<a id="dma-vector-tests-20261020"></a>

## 7. DMA 与向量 HelloWorld 服务器定向测试（2026-10-20）

用户授权本地 Agent 通过 SSH 执行前述疑点测试并报告原因。本节是实际构建、运行及信号采样结果；不沿用旧运行的退出码。stub 用例按用户决定全部排除。未委派服务器 Agent，未执行提取或整套回归。

### 7.1 实际输入与运行方式

| 项目 | 本次实际输入 |
| --- | --- |
| 服务器参考工程 | `zhaowy24@172.16.0.243:/home/zhaowy24/CheshireAraPULP` |
| Cheshire | `e040b7bbc7851a37faff3c4657ff8d656cc6e20a` |
| Ara / CVA6 | `2895ba907e9eb14b3464609dc791a969d159a7c3` / `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c` |
| iDMA / register_interface | `c12caf59bb482fe44b27361f6924ad346b2d22fe` / `ae616e5a1ec2b41e72d200e5ab09c65e94aebd3d` |
| 硬件配置 | `cv64a6_imafdcv_sv39`、Ara 真实 decoder、2 lanes、VLEN=2048、SelectedCfg=3、UseDramSys=0；未改变数值 |
| 启动和软件 | 保留已有 FS=Clean 启动修正，重新编译 `crt0.S`；SPM 链接；BOOTMODE=0、PRELMODE=1（Serial Link preload） |
| 工具 | `/opt/riscv/bin/riscv64-unknown-elf-gcc` 13.2.0；VCS W-2024.09-SP1；DPI 编译使用 GCC toolset13 G++ |
| 新产物根目录 | `/home/zhaowy24/CheshireAraPULP/_e01/dma_vector_check/`，下文简称 `$OUT` |

先复用现有 `simv`，只重编指定软件。软件采用该版本官方配方的 include、宏、`rv64gcv_zifencei/lp64d`、`-O2 -flto -mstrict-align`、`spm.ld`，复用原 `libcheshire.a`；直接执行相应编译/链接命令，输出全部指向 `$OUT`，避免官方全量目标收集 stub 或改写原产物。精确参数与退出状态保存在 `build_commands.json`、`diagnostic_build_commands.json`，五个软件用例编译、链接均退出 0。

现有 `simv` 限制了可读信号层次，首次 UCLI 内部采样失败。随后在 `$OUT/debug_build/` 从空输出目录执行原有 `compile.cheshire_soc.sh` 副本，并按相同配置重新展开；仅把调试选项改为 `-debug_access+r`、去掉顶层层次限制。编译和展开均退出 0（墙钟分别 20.494 s、33.368 s）。未调用 Bender，未复制旧编译库。这个构建仍读取参考工程源码，**不是独立提取验收**。

普通运行命令如下；每个用例使用独立工作目录，串行执行，墙钟上限 600 s，无波形导出。定位运行增加 `-ucli -i <该次 probe.tcl>`，只读采样 DMA 信号并保存在文本日志中，没有 force。

```sh
timeout -k 5s 600s <simv绝对路径> +BOOTMODE=0 +PRELMODE=1 +BINARY=<ELF绝对路径>
```

服务器现有 `start.cheshire_soc.sh` 的 PRELMODE 是 0；本轮未改该文件，上述命令显式选择 1。所有运行的完整命令、UTC 起止时间、墙钟时间、ELF SHA256、主机退出码见各 `run_*/command.json`、`result.json`、`exit.status`。`inputs.json` 保存原输入完整哈希；调试版另有 `debug_build/simv.sha256`。

| 本次二进制 | SHA256 前 12 位（完整值见上述文件） |
| --- | --- |
| 原 `target/sim/vcs/simv` | `42d3bac1f539` |
| 新 `debug_build/simv` | `65b5f56af5a1` |
| `dma_original.elf` | `78c8dc13545b` |
| `dma_checked.elf` | `74a20869cd48` |
| `dma_reg_readback.elf` | `98172e33df5e` |
| `vector_original.elf` | `a919487d354c` |
| `vector_fixed.elf` | `bbd711e99ba2` |

### 7.2 测试项与结果

“目标”是 RISC-V 程序返回值，“主机”是 `timeout/simv` 进程退出码；两者不能互相替代。目录均位于 `$OUT`，其中保存 `simulate.log` 和 CPU trace。

| 测试项 | 实际操作与结果 | 目标 / 主机 | 产物目录 |
| --- | --- | --- | --- |
| 原版二维 DMA | 原样复制、重编 `sw/tests/dma_2d.spm.c`。38 字节金值及结尾保护字符比较通过；原轮询读到的提交、完成 ID 均为 0 | 0 / 0 | `run_dma_original/` |
| DMA 编号检查 | 测试副本沿用原 HAL 提交，保存 ID，只增加有界轮询及非零 ID 检查，不额外读取 NEXT_ID。38 字节比较仍通过，但 ID=0，按诊断定义返回 64，**失败** | 64 / 0 | `run_dma_checked/` |
| DMA 64 位字段读回 | 使用原 HAL 指针向源地址字段写 `0x1122334455667788`，分别读 64 位、低/高 32 位。得到 `0x0000000055667788`、`0x55667788`、0，按诊断定义返回 67，**失败**。仅测试控制寄存器，未用此数值发起访存，随后写零 | 67 / 0 | `run_dma_reg_readback/` |
| 原版向量 HelloWorld | 原样复制、重编 Ara 集成用例；实际打印 `Hello Vector World!`，正常结束。原程序没有比较 `buf`，不能由打印成功推断目标缓冲区正确 | 0 / 0 | `run_vector_original/` |
| 修正向量 HelloWorld 副本 | 仅将打印参数改为 `buf`，增加与源字符串逐字节比较及错误返回。输出 `VECTOR_COPY errors=0 bytes=22`，**通过** | 0 / 0 | `run_vector_fixed/` |
| DMA 编号内部追踪 | 新调试版运行同一 `dma_original.elf`，在 504–507 μs 每 5 ns 采样一次。内部提交 ID=2、完成 ID 最终=2；返回位置错误见下节。原程序仍成功，结束时间与普通版同为 519430000 ps | 0 / 0 | `run_dma_control_debug/` |
| DMA 写入内部追踪 | 新调试版运行同一 `dma_reg_readback.elf`，在 503–504.5 μs 采样。确认外层收到完整 64 位写数据，内部只写低 32 位；高地址字段一直为 0，重现返回 67 | 67 / 0 | `run_dma_readback_debug/` |
| 首次内部追踪尝试 | 原 `simv` 在 504 μs 报 `UCLI-CMD-NODBG`，没有完成测试；保留日志，不计为通过。后由上述独立调试版完成定位 | 未到程序结束 / 0 | `run_dma_control_trace/` |

普通版五次完整运行的墙钟时间依次为：原 DMA 6.754 s、编号检查 7.137 s、字段读回 6.637 s、原向量 36.954 s、修正向量 73.044 s。它们是仿真主机耗时，不是目标程序性能比较。没有完整用例超时。

### 7.3 DMA 原因：确有宽度适配问题，不能仅解释为配套截位约定

**（1）提交、完成编号位于错误的数据半部。** 服务器 GCC 13.2.0 的实际 ELF 把 HAL 的 64 位 ID 指针读取拆为两次 `lw`：NEXT_ID 读 +0x44/+0x48，DONE_ID 读 +0x84/+0x88，再拼为 64 位。相邻项实际属于不同通道，不是同一编号的高低半部；当前未用通道为 0。

内部追踪与 CPU trace 给出如下对应关系（时间为仿真 ns）：

| 时刻 | 实际事件 |
| --- | --- |
| 506130 | AXI 读取 `0x01000044`，AR.size=2，即 4 字节 |
| 506135–506140 | 提交握手发生，内部 NEXT_ID 从 2 变为 3；该次返回 `RDATA=0x0000000000000002` |
| 506180 | CPU 的 `lw +0x44` 得到 0 |
| 506370–506375 | 搬运完成握手发生，内部 DONE_ID 从 1 变为 2 |
| 506405–506415 | AXI 读取 `0x01000084`，AR.size=2，返回仍为 `0x0000000000000002` |
| 506455 | CPU 的 `lw +0x84` 得到 0；相邻未用通道的读取也为 0 |

这两个有效寄存器地址在 8 字节拍内偏移为 4，32 位数据应位于 RDATA[63:32]，本次却位于 [31:0]。CVA6 `load_unit.sv:472` 按地址低位移位取值，所以读到 0。`hw/cheshire_idma_wrap.sv` 使用 64 位 Regbus；iDMA `target/rtl/idma_reg64_2d_reg_top.sv:30,58–60` 固定 DW=32，直接接入请求并把 32 位读值零扩展到外层；`register_interface/src/axi_lite_to_reg.sv:184` 直接转发，没有在此处补上半部定位。

**（2）64 位写没有拆成两个 32 位寄存器写。** 读回测试在 503455 ns 的外层请求为 WDATA=`0x1122334455667788`、WSTRB=`0xff`；内层 `reg_wdata=0x55667788`、`reg_be=0xf`。503460 ns 低地址字段变为 `0x55667788`，高字段仍为 0。64 位读回也只有低字段。这直接确认高半部丢失；与是否实际访问该数值所指的内存无关。

**（3）为什么原测试还能通过。** 原用例地址、长度、步长等数值都能放在低 32 位；小搬运在第一次完成寄存器读取前已经结束。CPU 随后比较 38 字节，结果确实正确。但原阻塞函数比较的是两个错误的 0，没有通过有效 ID 确认完成。本轮没有观察到该小用例提前返回后产生数据错误，也没有测试大传输；不能据此接受阻塞等待功能。

因此，本次既发现 HAL 访问粒度与寄存器定义不符，也确认了 RTL 控制接口的宽度/数据位置适配问题。**不能称“只是软件缺少安全处理，硬件没有问题”，也不能据此称 DMA 搬运核心已损坏。** 用户提出的截位解释说明了低地址小搬运为何可成功，但不能解释为正确的通用编号与 64 位字段访问约定。仅把 HAL 的 ID 指针改为 32 位不足以解决返回位置错误；当前 ELF 已经实际执行 32 位读取。

### 7.4 向量打印问题：原版可打印，但打印的不是 `buf`

固定 Ara 源码中的确是 `printf("%s", str_v)`；注释写“Print buf”，实际参数却是向量值。此次原版没有打印崩溃：反汇编显示编译器用 `vs1r.v` 把向量保存到临时栈区，并把该区地址放入 a1 传给 `printf_`；其中恰好含有完整字符串和终止符。因此看到了正常文字，不能把先前静态疑点写成“服务器已复现打印失败”。

测试副本改为 `printf("%s", buf)`，并在打印后比较 `sizeof(str)=22` 个字节，错误数为 0。实际 ELF 保留 `vsetivli ... 22,e8,m1`、`vle8.v`、`vse8.v`。结论是该配置下这次 22 字节向量复制正确；没有验证其他 VL、尾部保持、多组数据或完整 RVV。改动仅在 `$OUT/src/vector_fixed.c`，原 Ara 文件未改。

### 7.5 新发现：程序失败没有转成主机非零退出

编号检查和字段读回分别输出 `[SLINK] FAILED: return code 64/67`，三个失败的完整运行（包含调试重跑）主机退出码却都是 0。源码原因是 `vip_cheshire_soc.sv:949` 用 `$error` 打印程序错误，而 `tb_cheshire_soc.sv:68` 最后无条件 `$finish`；本次 VCS 默认行为没有把该错误转换为进程非零退出。首次 UCLI 采样错误也返回了主机 0。

本轮按“完成日志＋目标返回值＋主机退出状态”判定结果，没有把这些运行当成通过。后续自动回归必须使目标失败或运行未完成得到失败判定；可在独立平台中最小调整 TB 结束处理或现有运行入口检查。本轮未修改参考 TB/VIP，也未新增运行框架。

### 7.6 保留内容、未关闭项与下一步

- 前后检查的 15 项原输入（源码、启动文件、库、脚本、原 simv/共享库和已有日志）SHA256 全部一致；参考工程 `git status --short`、原 tracked diff 一致。Ara、CVA6、iDMA、register_interface 的 HEAD 一致，受跟踪源码无差异。原有 `.gitignore`、FS 启动修正、启动脚本及未跟踪 `wave.tcl` 均保留。
- 新软件副本、诊断用例、Tcl、RTL 编译库、完整日志和 CPU trace 均留在 `$OUT`；`summary.json` 汇总实测事件及结果。本地只更新现有报告、方案、交接、状态和任务表。未写 `~/CheshireAra`、TTY 工程或 `/opt`，未改本地 RTL/sw/依赖。
- 新调试构建仍有 245 条 SIOB、9 条 ENUMASSIGN；编译另有 IPDW、PHNE、SV-LCM-RIPI 各 1 条。本轮未逐条关闭。运行中 RT-NCMUCS 均仅在 0 ps 出现；部分 ELF 有零填充区不预载提示，部分链接有 RWX 段警告，未阻止本次已完成用例，不据此称所有警告已无害。
- **待单独实施的修复：**按当前版本适用的官方组件处理 DMA 64→32 位控制通路与 HAL 寄存器访问；保留地址、功能配置和提交副作用。修复后重跑原用例、有效 ID/完成等待、上下半部读写和必要长传输检查。向量打印修正副本可作为最小软件补丁输入；失败退出处理也需在后续平台中落实。这里说明修复方向，未改功能性 RTL、驱动原件或批准下一任务。
- 本轮疑点测试与原因定位完成，**DMA 功能修复尚未完成**。stub 继续勿用；完整参考验收、独立提取/搬迁、SPI 启动、DDR/原子等既有未测项没有被本轮结果替代。

<a id="dma-fix-20261020"></a>

## 8. DMA 控制接口局部修复与定向回归（2026-10-20）

本节接续第 7 节，用户明确授权实施已讨论方案，由本地 Agent 通过 SSH 完成。**控制接口的编号位置和高半部丢失已修复；较长二维搬运另出现停滞，不能宣称此次全部验收通过。** 信号链、逐层代码和位图见[DMA 控制通路说明](../../../../engineering/DMA_Control_Path_and_Fix.md)。

### 8.1 修改与实际输入

服务器仍为 `/home/zhaowy24/CheshireAraPULP`，Cheshire 和第 7.1 节四项依赖 HEAD、CPU/Ara/SoC 配置均保持。此次唯一的两个生产源码改动为：

| 文件 | 改动与来源 |
| --- | --- |
| `hw/cheshire_idma_wrap.sv` | 回移官方 `bca9aadb7588de7046460daf91b39fe863a7a9d1` 的 `axi_to_reg_v2`、`RegDataWidth=32`、`CutMemReqs=1` 局部改动，加上 `ef11799d00d9c7b19d042864529d03cbe41fac5b` 的空接 `reg_id_o`。未移植整个 PR、升级 iDMA 或修改依赖源码。 |
| `sw/include/dif/dma.h` | CONF、STATUS、NEXT_ID、DONE_ID 的四类指针及声明改为 `volatile uint32_t *`；成对 64 位字段及高层函数签名保持。此改动为本次独立的软件补丁。 |

新产物根目录为 `_e01/dma_vector_check/fix_validation_20261020/`，下文简称 `$FIX`。其中 `before/` 保存两文件原件，`before.diff/status` 保存进入时状态；`upstream-wrapper.patch`、`rtl.diff`、`hal.patch` 分开记录来源与实际改动。原失败目录未覆盖。

先修改 RTL，HAL 尚未修改时，从空的 `$FIX/rtl_build/` 目录编译和展开：分别退出 0，耗时 20.263 s、32.592 s。沿用之前已验证的官方编译脚本副本、VCS W-2024.09-SP1、GCC toolset13 G++、SelectedCfg=3；调试选项为 `-debug_access+r`。未调用 Bender、未复制旧编译库。完整命令保存在 `rtl_build/build_commands.json`。

随后单独修改 HAL，沿用第 7 节软件参数，重编五个 ELF，编译和链接均退出 0。复用原 FS=Clean 对应的 `crt0.o` 与原 `libcheshire.a`，源和链接命令见 `software_build_commands.json`；输出 ELF、map、dump 留在 `$FIX`。这不是独立软件构建或工程提取验收。

| 输入 | SHA256 |
| --- | --- |
| 修复后的 wrapper | `da0811e1199b2dadf6f2cdbea169987ceb2fb4a1d344e56ecdecf76f1e699546` |
| 修复 RTL 的 `rtl_build/simv` | `a81d6de9fd9a4f1da89bdcf9485234271688abd3a2148beb6db63063d7cc743f` |
| 修复后的 HAL | `609d5920339776c8c9b235ea6ed41a5a2856b8cd77b695512730ca7fb286caf3` |
| 新 `dma_checked.elf` | `0650ba3e74b52345837ba94cfc0a6e64ab196ae6e36d2924ad30b18c878e5366` |
| `dma_reg_lanes.elf` | `84fb9133523412a7843ccf9f1d54dd76ef527b9353c1dc8c978a3d1d1abf2298` |
| `dma_long_2d.elf` | `e1934c1f303a13cd1610ae856d18df2ac53e8b1d1ed6271601996be779802d24` |

每次运行的 `command.json`、`result.json`、`exit.status` 分别保存实际命令、ELF/simv 哈希、UTC 起止时间、墙钟耗时及主机状态。判断仍使用 SLINK 完成记录与目标结果，不将主机 0 单独视为通过。

### 8.2 仅修 RTL，同一批原 ELF 对照

| 用例 | 修复前 | 仅修 RTL 后 | 目标 / 主机 | 新目录 |
| --- | --- | --- | --- | --- |
| 原二维 DMA | 数据比较通过，但编号读成零 | 同一 ELF 通过；内部 next 从 2 变 3，done 从 1 变 2 | 0 / 0 | `rtl_only_dma_original/` |
| 原编号诊断 | 目标返回 64，失败 | 同一 ELF 检查有效编号和完成等待，通过 | 0 / 0 | `rtl_only_dma_checked/` |
| 原 64 位字段读回 | 高半部为零，目标返回 67 | 同一 ELF 完整读回 `1122334455667788`，通过 | 0 / 0 | `rtl_only_dma_reg_readback/` |

三个 ELF 的哈希与第 7.1 节一致，运行耗时分别为 16.129 s、8.174 s、7.603 s。第一个用例同时采样内部信号：next 在 506155 ns 变为 3，done 在 506380 ns 变为 2；原数据比较保持通过。由此可以把两个原失败项的消失归因于此次 RTL 局部改动，而非更换测试软件。

### 8.3 修 HAL 后的编号与字段访问

`dma_checked` 保留原数据比较、有界轮询和非零编号检查，增加观测变量；`dma_reg_lanes` 检查成对写、分别读低/高半部、分别写低/高半部且另一半保持、最后清零。全部通过，目标/主机均为 0/0。初次运行分别耗时 60.766 s、51.198 s。

初次内部采样误沿用较早的启动窗口，实际 MMIO 发生在 533–538 μs，窗口没有覆盖操作。没有把这两次空窗口当成内部验证；依据 CPU trace 在 `checked_internal/`、`lanes_internal/` 重新采样，目标和主机再次均为 0/0，耗时 54.207 s、42.976 s。

| 实际 CPU trace | 观测值与含义 |
| --- | --- |
| 537970 ns，读取 `0x01000044` | 一次 `c.lw` 得到提交编号 2；没有旧 HAL 的额外 `+0x48` 读取 |
| 538075 ns，读取 `0x01000084` | 完成编号仍为 1，进入等待 |
| 538245 ns，再读 `0x01000084` | 完成编号为 2，退出等待；没有额外 `+0x88` 读取 |
| 534335 / 534450 ns，分别读 `+0xd8/+0xdc` | `55667788 / 11223344` |
| 534565 ns，64 位读 `+0xd8` | `1122334455667788` |
| 534770 ns，写低半部后再完整读 | `11223344aabbccdd`，高半部保留 |
| 534985 ns，写高半部后再完整读 | `12345678aabbccdd`，低半部保留 |
| 535355 ns，清零后完整读 | 0 |

长用例的 `read_done_once` 反汇编也只有一次 `lw a0,132(a5)`，随后移位实现无符号零扩展；不是额外 MMIO 访问。`lw` 与 `lwu` 的符号扩展差别不改变读取宽度。

这些诊断副本没有配置 UART；其 `printf` 不作为判据或已打印结果。上述数值来自 CPU trace、内部采样及程序比较返回值；普通 HelloWorld/向量用例按各自原流程配置 UART。

内部采样还确认：537920 ns 只有一次 `issue_id=1`，NEXT_ID_0 的 Regbus 读取确实返回 2；字段图样在 533690/533695 ns 分别形成 `+0xd8=55667788`、`+0xdc=11223344` 两次写，两次内层写使能均为 `0xf`。分别修改低、高半部时只出现对应半部的有效写。寄存器测试没有产生提交请求。

修复后的 AXI 读返回也已直接观测：537930 ns 的 NEXT_ID_0 为 `00000002_00000000`；538035/538205 ns 的 DONE_ID_0 分别为 `00000001_00000000`、`00000002_00000000`。编号在高 32 位，与 CPU 对 `+0x44/+0x84` 的取值位置一致。

基本回归也已完成：

| 用例与目录 | 实际结果 | 目标 / 主机 | 墙钟耗时 |
| --- | --- | --- | --- |
| `hal_helloworld/` | 官方标量用例打印 `Hello World!`，SLINK SUCCESS | 0 / 0 | 33.791 s |
| `hal_vector_fixed/` | `Hello Vector World!`、`VECTOR_COPY errors=0 bytes=22`，SLINK SUCCESS | 0 / 0 | 82.618 s |

两个 ELF SHA256 分别为 `51a387f5e3a842af60424730a7089de76674605ec58fb45c5da621d280d85415`、`a99da940a5ba45c8ba90c6f34951b7a628d501a2b0e7f59c2c6e5d18cd71a5ce`。向量副本只是重新编译已有最小修正，不修改 Ara 原件或扩大为完整 RVV 验收。

### 8.4 长二维搬运：新发现的停滞

测试 `src/dma_long_2d.c` 使用 SPM 非缓存别名，两端各保留 64 字节保护区；计划每笔 32 行×256 字节、三笔顺序提交并等待，检查编号 2/3/4、等待次数及全部数据。源、目的步长均为 256，保持 HAL 默认 `DECOUPLE_AW=0`、`DECOUPLE_RW=0`。

`hal_dma_long_2d/` 在 600.045 s 被超时结束，主机 124，无目标完成结果，**失败**。不能用短传输成功替代这一项。

为判断是否为仿真器零延时循环，从新目录 `loop_build/` 编译同样源码和配置，只在 VCS 展开时增加本机手册列出的 `+vcs+loopreport+100000`。编译/展开均为 0，耗时 20.834 s、103.206 s；新 simv SHA256 为 `1ea5ad64230eb784a119718766248b1ae20bbef52657bf22a63e422dfb67b381`。同一 ELF 的诊断运行限时 120 s，同样未完成。

该诊断发出 `LOOP_NOTSUP`：当前模型含 specify/timing checks，循环报告可能不可靠。因此不能用“没报循环”证明没有循环。不过 UCLI 采样显示仿真时间确实从 1947000 ns 推进到 1959000 ns，期间任务已提交，next=3、done=1，后端持续忙，数据主口出现读响应和待发送写数据。这将后续定位重点放到 DMA 数据通路及握手，而非继续把它归因于编号读成零。

### 8.5 长搬运的对照定位与结论边界

新增两次限时内部观察，使用**同一 `dma_long_2d.elf`**，分别运行修复后的 simv 和第 7 节原始 `debug_build/simv`。两次均在仿真 2 ms 读取最终状态后由 UCLI 主动退出，主机 0，但目标未完成，**只是诊断，不计测试通过**。目录为 `long_bus_fixed/`、`long_bus_original/`，墙钟分别为 49.090 s、48.236 s。

两种 RTL 得到相同的停滞状态：

| 观察位置 | 实际值 | 直接说明什么 |
| --- | --- | --- |
| 任务编号 | next=3、done=1 | 第一笔编号 2 已提交，尚未退休 |
| AXI 读请求/响应 | ARVALID=1、ARREADY=0；RVALID=1、RREADY=0 | 新读请求和已有返回数据均不能继续握手 |
| AXI 写请求/数据 | AWVALID=0、AWREADY=1；WVALID=1、WREADY=0 | 下游可收写地址，但当前没有释放新 AW；写数据被反压 |
| R/AW 耦合模块 | 内部 AW 队列 valid=1，`aw_to_send_q=0`、`first=0`、`aw_sent=0` | 队列里还有写地址，当前无释放它所需的读首拍事件/信用 |

修复版在采样窗口内观察到 10 个 AR、1 个 AW、17 个 R、14 个 W 握手；最后 R/W 握手分别在 1948815/1948805 ns。仅在 1948735 ns 看到一次 `first=1` 并释放 AW，随后到 2 ms 仍没有完成。这些是 DMA 主口的采样统计，不替代下游 LLC 各级队列的完整计数。

再制作纯诊断副本 `src/dma_aw_debug.h` / `dma_long_aw_decoupled.c`，**只将测试使用的 `DMA_CONF_DECOUPLE_AW` 从 0 改为 1**，生产 `sw/include/dif/dma.h` 的标志保持 0。相同硬件和 3×8 KiB 数据检查在 `long_aw_decoupled/` 完成，目标/主机 0/0，耗时 241.918 s。ELF SHA256 为 `44a225c8f4c94c7b729c8219cbf3aaeef7e6f55533337526aa0013ba36c85168`。

两份 ELF 的反汇编差异已保存为 `long_aw_disassembly.diff`：除文件名外，只有 `0x10001452` 的一条指令从 `li a2,1024` 变成 `li a2,1025`，即 CONF 从 `0x400` 变成 `0x401`。地址、搬运尺寸、比较逻辑和缓冲区布局均未改变。

| 作业 | 提交 / 完成编号 | 等待次数 | 数据和保护区 |
| --- | --- | --- | --- |
| 0 | 2 / 2 | 19 | 无比较错误 |
| 1 | 3 / 3 | 30 | 无比较错误 |
| 2 | 4 / 4 | 30 | 无比较错误 |

编号和次数由三个观测数组的 CPU store trace 核对；UART 只完整输出前两行，不能将未完成发送的第三行冒称实际打印。最终程序返回 0 覆盖全部三笔数据、保护区和编号检查。

**仍有一条断言失败，不能把这个诊断副本称为无告警验收通过。** 在仿真 1957840 ns，CVA6 `core/cache_subsystem/wt_cache_subsystem.sv:288` 的 `gen_assertion[1].a_invalid_read_data` 报失败，消息为 port 1 读数据含无效值检查失败；随后打印的数据为 `0000000000000002`。单凭随后显示的稳定值不能否定断言曾失败，也不能断定它一定是无害的调度问题。原默认标志长测试因尚未走到同一完成读取，不能作为排除该警告的对照。

本次能确定：默认 R/AW 耦合开启时，这个工作负载在 DMA 与 SPM 数据通路之间停滞；原 RTL 同样如此，关闭该耦合后能完成数据搬运。**尚未确定是谁首先导致 WREADY 下降，以及是下游 LLC/SPM 的排序/背压约束、耦合控制实现，还是二者组合造成问题。** 下一步应沿最后一次 W/R 握手追踪 LLC 的读写描述符与返回缓冲，再检查断言时刻的有效信号和数据，不能仅凭耦合模块 busy 就认定该模块自身有错误。

官方另有 [iDMA #115](https://github.com/pulp-platform/iDMA/issues/115) / PR #80 处理耦合相关死锁，但记录的触发条件是 `decouple_rw=1`、非对齐地址和多 burst；本次为 `decouple_rw=0`、64 字节对齐缓冲区。尚无依据认定是同一缺陷，未移植该修复或升级依赖。PR #203 中另外的 1D 修复也仍在此次范围外。

### 8.6 保存、保护与后续

- 前后核对的 **81 项受保护文件哈希保持一致**，包括原源码/配置、FS 修正、原库、旧 simv 及原失败日志；允许变化的 wrapper/HAL 单独列出。四项依赖 HEAD 和 tracked diff 保持，根工程除这两个文件外的 tracked diff 与进入时完全一致。原 `.gitignore`、启动脚本差异和未跟踪 `wave.tcl` 保留。
- 原 `target/sim/vcs/simv`、原编译库没有更新；此次修复使用 `$FIX/rtl_build/simv` 验证。以后从原仿真入口继续时，需要重编修改后的 RTL，不能把旧 simv 当作已包含补丁。
- `final.patch` 保存此次两个生产文件的总差异；`final_summary.json` 汇总实际输入、所有运行、内部采样、断言及保护检查。全部完整日志、trace、编译库留服务器；本地仅接收必要摘要并更新文档，无 FSDB 导出。
- 主构建仍有 245 条 SIOB、9 条 ENUMASSIGN；编译有 IPDW、PHNE、SV-LCM-RIPI 各 1 条。基本运行的 RT-NCMUCS 仍存在；本次未逐项关闭这些历史警告。AW 诊断新增的读数据断言单独保留，不能混入“已知无害警告”。
- 已从官方 API 核对 main `6c6dd5e834347f72c7be31cd6c41021ec293c5b9`，其四类 HAL 指针仍为 64 位。`contribution/upstream-hal-width.patch` 是面向该输入的独立草案，已检查可应用，来源记录在同目录 `upstream-main.json`。未运行最新上游完整仿真，未 commit、push 或发布 PR；长测试和断言结果需在后续贡献说明中如实披露。
- **交付状态：说明文档、两项局部修复、规定测试的执行及原因分析已完成；默认配置的完整定向验收未通过。** 后续需另定数据通路/断言排障范围。本轮止于该范围，不改生产解耦标志、不改 iDMA/LLC/CVA6、不修 1D、不升级依赖，也不开始提取。

<a id="dma-stall-diagnosis-20261020"></a>

## 9. 长搬运死锁与读数据断言的继续排查（2026-10-20）

本节根据用户“继续排查并查找官方修复”的要求，补充第 8.5 节的两个未决原因。**默认长搬运已定位为 LLC 共同读写流水线的循环等待；解耦运行的那一次断言已定位为未使用的 32 位含 X，CPU 实际读取结果正确。** 没有修改生产源码、默认标志或依赖，也没有把默认模式改判为通过。

### 9.1 输入、运行方法与输出

服务器根目录仍为 `/home/zhaowy24/CheshireAraPULP`，HEAD `e040b7bbc7851a37faff3c4657ff8d656cc6e20a`。本轮使用第 8 节已编译的 `$FIX/rtl_build/simv`，没有重新构建硬件或软件：

| 输入 | SHA256 / 版本 |
| --- | --- |
| simv | `a81d6de9fd9a4f1da89bdcf9485234271688abd3a2148beb6db63063d7cc743f` |
| 默认长测试 ELF | `e1934c1f303a13cd1610ae856d18df2ac53e8b1d1ed6271601996be779802d24` |
| 仅 AW 解耦的 ELF | `44a225c8f4c94c7b729c8219cbf3aaeef7e6f55533337526aa0013ba36c85168` |
| LLC | `559bcbd09a5a884dbe31e2d72fd95d024e357f39` |
| CVA6 | `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c` |
| iDMA | `c12caf59bb482fe44b27361f6924ad346b2d22fe` |

这里 `$FIX=~/CheshireAraPULP/_e01/dma_vector_check/fix_validation_20261020`。新输出全部位于 `$FIX/followup_diagnosis_20261020/`，以下简记 `$DIAG`。

各例串行执行，命令形式为：

```sh
timeout -k 5s 600s <原 simv 绝对路径> \
  +BOOTMODE=0 +PRELMODE=1 +BINARY=<既有 ELF 绝对路径> \
  -ucli -i <本例 probe.tcl>
```

本轮都是限时段观测，最后由 UCLI 退出，**没有完整跑完三笔任务，不按目标程序返回 0 计通过**。完整三笔结果仍引用第 8.5 节。没有导出波形或强制改变信号。

| `$DIAG` 下的运行目录 | 主机状态 / 耗时 | 实际产物与结论 |
| --- | --- | --- |
| `llc_stall/` | 0 / 39.670 s | 默认 ELF；1948605–1949600 ns 每 5 ns 采样，2 ms 最终快照；确认 LLC 循环等待 |
| `cpu_assertion/` | 0 / 38.058 s | 首次脚本在采样标签中未转义 `[1]`，Tcl 报 `invalid command name "1"`；没有 CPU 样本，**诊断失败**，保留原日志 |
| `cpu_retry/cpu_assertion/` | 0 / 38.958 s | 修正标签转义后重跑；1957800.5–1957880 ns 每 0.5 ns 采样，复现同一断言 |
| `confirm/llc_aw_decoupled/` | 0 / 41.745 s | 解耦 ELF；与默认相同 LLC 采样窗口，写描述符提前进入；第一笔完成，亦复现原断言 |
| `confirm/load_result/` | 0 / 39.086 s | 增加 load_unit 偏移、操作和结果采样；直接确认所需高 32 位产生有效零结果 |

`command.json`、`result.json` 保存实际命令、输入哈希、开始时间、运行时长和主机状态。上述表格另按 `simulate.log` 核对 Tcl 错误和断言事件，明确区分首个失败诊断；初始 `diagnostic_errors` 字段没有捕获该 Tcl 错误，不能仅凭该字段为空或主机 0 判成功。完整日志、CPU trace 留服务器，本地仅接收必要摘要。

### 9.2 默认模式：读写请求的共同流水线堵塞

观测层次：

- DMA：`tb_cheshire_soc.fix.dut.gen_dma.i_idma`。
- LLC：`tb_cheshire_soc.fix.dut.gen_llc.i_llc.i_axi_llc_top_raw`。

共同仲裁器输出在 valid/ready 同为 1 时的顺序如下。时间是 UCLI 的周期采样标签，用于比较先后次序；没有把它另称为精确的事件区边沿时间。

| 默认模式采样时间 / ns | 被接收的描述符 |
| --- | --- |
| 1948690、1948695、1948700、1948710 | 读 `0x10003a80`、`0x10003ac0`、`0x10003b00`、`0x10003b40` |
| 1948750、1948790 | 读 `0x10003b80`、`0x10003bc0` |
| 1948830 | 第一条写 `0x10001a00` |

地址在 LLC 内已经从非缓存别名 `0x1400...` 映射回 `0x1000...`。默认模式的第一条 AW 虽已由 DMA 发出，但写描述符排在六个读描述符后面。

到 2 ms 的关键状态：

| 单元 | 实测状态 | 原因关系 |
| --- | --- | --- |
| read unit | `busy_q=1`，当前地址 `0x10003ba0`、len=3；`r_fifo_full=1`、`way_inp_ready_i=0` | 读返回缓冲满，当前读无法继续 |
| hit/miss unit | 读 `0x10003bc0`，`hit_valid=1/hit_ready=0` | 等 read unit 接收 |
| shared spill | 写 `0x10001a00`，valid=1/ready=0 | 被前面的读描述符挡住 |
| write unit | `busy_q=0`，`write_desc_ready=1`，却 `write_desc_valid=0`；W FIFO valid=1、内部 ready=0 | 写单元没有取得描述符，不能消费已缓冲的数据 |
| 行锁/计数 | `locked=0`、`cnt_stall=0`；读写 unlock grant 均为 1 | 排除本次停滞由行锁或请求计数阻塞造成 |
| DMA 主口 | R valid=1/ready=0，W valid=1/ready=0，next=3、done=1 | 写不动导致 DMA 缓冲满，继而停止收读数据，形成循环等待 |

这解释了先前只能看到的 WREADY 下降：写数据停在缓冲，写单元等描述符；写描述符又被前面的读请求阻挡。不能把“DMA 接受过 14 个 W beat”写成“已写入 SRAM 14 拍”。后续 AW 仍等读首拍是伴随现象，本例不是单凭 AW 信用计数为零就能归因于计数器错误。

在同一采样窗口中，AW 解耦副本的前三个描述符是：1948690 ns 读 `0x10003a80`、1948695 ns 读 `0x10003ac0`、1948700 ns 写 `0x10001a00`，之后读写继续交替。只改变一条配置立即数便使写请求提前进入，与前述等待链相符。原/修复 RTL 同样停滞的结果仍引用第 8.5 节；本轮没有重跑旧 RTL。

代码关系、连续等待图及固定版本行号见[说明第 7.1 节](../../../../engineering/DMA_Control_Path_and_Fix.md#dma-llc-deadlock)。**本例的阻塞原因已确定；生产修复未实施，默认测试仍失败。**

### 9.3 断言：栈上未使用的 32 位为 X，而实际 load 结果正确

原断言仍在 1957840 ns 复现。CPU trace 与细粒度采样对应如下：

| 时间 / ns | 实际事件 |
| --- | --- |
| 1634105 | `sw` 把零写入 `0x1001ff44`；在此前到本次读取的 trace 中，相邻低 32 位没有对应访问记录 |
| 1957775 | DONE_ID 的 `lw` 已正确读出 2；它早于断言 |
| 1957839.5 | cache 返回 `00000000_xxxxxxxx`，rvalid=1、kill=0；load_unit offset=4、valid=1、shifted_data=0、result=0 |
| 1957840 | 断言按时钟沿采样整个 64 位返回值，因此失败 |
| 1957840.5 | 通路已切换到下一条栈读取：offset=0、data/result=2；未用 `$sampled` 的 warning 因而打印 2 |
| 1957850 | 提交 `lwu a5,36(sp)`，PC=`0x100014b6`，地址=`0x1001ff44`，结果 a5=0 |
| 1957855 | 下一条 `ld a4,16(sp)` 提交，地址=`0x1001ff30`，结果 a4=2 |

本次 `lwu` 读取对齐 64 位字的高半部，低半部 X 不参与结果。`load_unit.sv:472` 的移位及结果选择对此有直接实现，采样也确认了有效结果为零；不是只根据程序最终返回 0 猜测告警无害。

检查第 8.5 节完整三笔运行的 `trace_hart_0.log`，未发现打印的寄存器操作数/结果含 X/Z；全部数据及保护区比较仍为零错误。由此可将**这一个断言事件**解释为检查范围超过指令访问范围，加上报错打印未取采样值。不能将该结论推广到所有 X 告警，也未修改断言或清空栈来消除它。

具体摘要位于 `confirm/load_result/selected_samples.json`、`cpu_retry/cpu_assertion/trace_check.json`、`stack_accesses.json`。

### 9.4 官方变更核对与下一步边界

2026-10-20 查询了 Cheshire 的 DMA 相关 issue/PR、iDMA #80/#204 的实际文件差异、LLC 默认分支提交记录、PULP CVA6 的 WT/standard cache 文件历史及相关断言讨论。

- **最接近的死锁记录是 [Cheshire #219](https://github.com/pulp-platform/cheshire/issues/219)**，仍 open；无公开复现正文和关联修复 PR，不能凭标题断言完全相同。LLC 后续的 flush/SPM 模式切换修复与本例持续处于 SPM 时的读写阻塞不同。
- [iDMA #80](https://github.com/pulp-platform/iDMA/pull/80)（`40fe6a67`，2026-08-12）和 [#204](https://github.com/pulp-platform/iDMA/pull/204)（`497c1f23`，2026-08-18）已合入 devel，分别调整 AW 释放依据、修正空队列释放及解耦信用处理。它们没有修改 LLC 共同流水线；本例已经看到第一条写请求排在 LLC 的读请求后，尚不能认定这些 PR 关闭了本次死锁。
- [Cheshire #294](https://github.com/pulp-platform/cheshire/pull/294) 是 iDMA 0.7.0 的较大集成改动，合入 **gwaihir**，不是 main 的现成小补丁；[#295](https://github.com/pulp-platform/cheshire/pull/295) 合入 main，增加默认关闭的 AXI cut，未声称修复 #219。此次没有套用任何一项或升级依赖。
- **断言有直接相关官方讨论和提交**：[Cheshire #274 维护者回复](https://github.com/pulp-platform/cheshire/issues/274#issuecomment-5253008526) 解释未使用字节中的 X 与采样打印问题；PULP CVA6 [`e606cdfe36b49d09c8f60975fd10f88948677c6d`](https://github.com/pulp-platform/cva6/commit/e606cdfe36b49d09c8f60975fd10f88948677c6d) 改用 `$sampled`、调整 X 检查，但仅涉及 standard/HPD cache，未改当前 WT cache，并明确保留整个字检查的限制。官方 API 没返回关联 PR；不能把它说成当前 WT 的完整修复。
- 更早 [CVA6 PR #664](https://github.com/openhwfoundation/cva6/pull/664) 的 `kill_req` 条件已在当前 WT 代码中；此次 kill=0，不适用。

完整适用性表见[说明第 7.3 节](../../../../engineering/DMA_Control_Path_and_Fix.md#dma-upstream-fixes)。后续可分别确定 LLC/DMA 死锁的最小修复，以及 WT/LSU 断言的采样与有效字节检查；两者不要混成一个 DMA 数据核心补丁。生产 AW 默认值保持 0，默认定向验收保持未通过。

### 9.5 保护检查与交付限制

- 进入时参考工程 HEAD、status、wrapper/HAL 哈希与第 8 节一致。每组诊断脚本结束时均核对 wrapper、HAL、`crt0.S`、`Bender.lock`、`Bender.yml` 五项哈希不变；后续只读核对 LLC/CVA6 的 HEAD 及 tracked diff，均与固定版本一致且无 tracked 差异。全部远端写入仅为 `$DIAG` 中的采样脚本、日志及摘要。
- 最后一次读取关键采样成功后，SSH 连续出现连接超时。收尾的全工程 diff、旧 81 项文件哈希汇总**未完成**，未取得 `report_summary.json`；不能把前次的 81 项检查复述成本轮新结果。诊断仿真此前均已结束，关键采样已返回，原因分析不依赖这次收尾连接。
- 本地更新五份既有 E01 文档，报告第 1–8 节字节保留；本地链接、显式锚点、围栏和范围内差异检查通过。没有改本地 RTL/sw、启动新子 Agent、修改依赖或重新运行完整回归，也没有提交/发布补丁。

<a id="dma-aw-config-20261020"></a>

## 10. 按次 AW 解耦接口回移与验证（2026-10-20）

### 10.1 实际改动与输入

用户选择方案一并授权实施。参考工程仍为 `~/CheshireAraPULP`、Cheshire `e040b7bbc7851a37faff3c4657ff8d656cc6e20a`，依赖和硬件配置沿用第 9 节；本地 HEAD 为 `c9abbb48946fe3a7244bfb3159919b7c9731cb59`。WSL SSH 间歇超时；用户允许 Windows SSH 后，使用 WSL 调用 Windows `ssh.exe` 完成部署和测试。VPN 重连后仍优先试过 WSL，曾连通一次，随后握手再次超时，继续使用可用的 Windows 通道。连接方式不改变目标工程及修改范围。

仅修改服务器以下四个生产文件：

| 文件 | 本次改动 |
| --- | --- |
| `sw/include/dif/dma.h` | 局部采用 Paul Scheffler 的官方 [`4c2390f25f250c9ea75d314dd107da11a52aa8fa`](https://github.com/pulp-platform/cheshire/commit/4c2390f25f250c9ea75d314dd107da11a52aa8fa)（[PR #189](https://github.com/pulp-platform/cheshire/pull/189)）HAL 改动，给四个 memcpy 接口增加 `conf` 参数及 NONE/AW/RW/ALL 标志；保留此前 CONF/STATUS/NEXT_ID/DONE_ID 的 32 位访问修正 |
| `sw/tests/dma_2d.spm.c` | 增加 `DMA_CONF_DECOUPLE_NONE` 实参，保持原短测试行为 |
| `sw/tests/axirt_budget.spm.c`、`axirt_budget_isolate.spm.c` | 同样显式传 NONE，使调用适配新接口；没有跟随上游将其模式改为 ALL |

测试副本通过 `DMA_CONF_DECOUPLE_AW` 逐笔选择 AW 解耦，RW 解耦仍关闭。二维 CONF 为 `0x401`；不是把整个工程的所有 DMA 调用默认改成解耦。没有修改 iDMA/LLC RTL、依赖、1D 行为、TB 退出机制或启动 FS 修正，也没有开展 Bender 剥离。

部署前逐文件核对预期哈希并保存原件。HAL 从 `609d5920…` 变为 `68083d32538d9f73c33232bda00d24c2d9236ac0f0c7cc438dff73d364921a8d`；四文件完整前后哈希及最小差异见[本地补丁目录](../evidence/dma_aw_config_20261020/README.md)。服务器输出统一放在：

```text
~/CheshireAraPULP/_e01/dma_vector_check/aw_config_20261020/
```

下文用 `$AW` 代指该目录。原失败记录、第 8/9 节产物均保留。

### 10.2 构建和运行方法

- 用服务器 `/opt/riscv/bin/riscv64-unknown-elf-gcc` 13.2.0，在 `$AW` 新建目标文件、ELF、map 和反汇编；复用第 8 节的软件构建参数、既有 FS 修正的启动对象和 `libcheshire.a`。已核对该库没有 `sys_dma_*` 实现，DMA 接口由本次头文件编入用例。
- 本次软件改动没有改变 RTL，复用第 8 节已构建的 `fix_validation_20261020/rtl_build/simv`，SHA256 为 `a81d6de9fd9a4f1da89bdcf9485234271688abd3a2148beb6db63063d7cc743f`。不称为本次重新构建 RTL，也不使用更早的旧 RTL simv。
- 每例独立目录，串行执行 `timeout -k 5s 600s <simv> +BOOTMODE=0 +PRELMODE=1 +BINARY=<本次ELF>`，普通运行不导出波形。记录 ELF/simv/HAL 哈希、命令、起止时间、主机状态、SLINK 完成及断言。
- `program_completed=true` 只表示主机退出 0、SLINK 报告目标成功且没有目标失败/工具 Error；仍另外检查断言，不能把它读成“无警告验收”。现有 VIP 的 `[SLINK] SUCCESS` 对应目标返回 0，失败时主机也可能为 0 的限制保持。

`build_commands.json` 记录六个运行用例及两个 AXI-RT 用例的编译/链接；后两项仅验证新接口能编译链接，没有运行 AXI-RT 功能回归。`layout_build_commands.json` 记录四个定向布局用例。12 个 ELF 均使用服务器工具链构建。

### 10.3 原用例与基本回归

| 测试 | 目标返回 / 主机退出 | 主机耗时 / 秒 | 结论 |
| --- | --- | --- | --- |
| `dma_long_aw_api`：原长搬运，AW 解耦，三次 32×256 字节 | 0 / 0 | 240.554 | 功能检查通过；1 次已定位断言仍保留 |
| `dma_original`：原短 DMA，NONE | 0 / 0 | 7.817 | 通过；无运行时断言 |
| `dma_checked`：编号及数据检查，NONE | 0 / 0 | 45.595 | 通过；无运行时断言 |
| `dma_reg_lanes`：64 位字段与上下半部读写 | 0 / 0 | 35.035 | 通过；无运行时断言 |
| `helloworld`：标量 HelloWorld | 0 / 0 | 33.438 | 通过；无运行时断言 |
| `vector_fixed`：已修正向量复制，22 字节 | 0 / 0 | 82.372 | 通过；无运行时断言 |


原长用例除增加 AW 实参外，保留三次 `32×256=8192` 字节、非缓存 SPM 别名、逐字节比较、保护区和等待检查。新 ELF `.text` 与第 8.5 节的 AW 解耦诊断 ELF **逐字节相同**，但本次确实从新 HAL 重新编译并运行；不是复制旧 ELF 当作新验证。新 ELF SHA256 为 `5f807e2b7cb3c80023cd4228df7559d572d74afc4625fb1efee8594c73b0d124`。

CPU trace 中提交编号和完成编号均为 `[2,3,4]`，未完成轮询次数为 `[19,30,30]`。 本次 trace 还确认三次 CONF 均由单个 `sw` 写入 `0x401`，每笔只执行一次 NEXT_ID 的 `lw`；32 位访问修正保持。程序返回 0 表明三笔数据和保护区检查均通过。UART 只完整输出前两笔，第三笔数值由全局数组的 store trace 核对，不冒称已经打印。短编号用例 `observed_submit=2`、`observed_done=2`、`observed_data_errors=0`。

长用例仍有一次 WT cache 断言，时间为 `1957840 ns`；不能列为“零断言通过”。本次 `.text`、断言时间及指令上下文均与第 9.3 节相同：`1957850 ns` 提交 PC=`0x100014b6` 的 `lwu`，读取 `0x1001ff44`，结果为 0；下一条 `ld` 结果为 2。结合第 9.3 节此前已经取得的内部采样，可判断此次是同一未使用低 32 位含 X 的事件。未重新声称本次采过内部信号，也没有关闭断言或清空栈掩盖它。

### 10.4 地址、步长及 CPU 并发定向测试

源码为 `$AW/src/dma_aw_layouts.c`，本地保留[同一源文件](../evidence/dma_aw_config_20261020/dma_aw_layouts.c)。每个用例两次传输，期望编号 2、3，并要求至少一次 DONE 尚未完成；比较所有目的字节、间隙和前后保护区，检查源区未改变。均采用 SPM 非缓存别名，源、目的不重叠。

| 用例 | 源 → 目的；行数×字节，源/目的步长 | 结果；主机耗时 |
| --- | --- | --- |
| `layout_reverse` | `0x1400a040 → 0x14008040`，同 16 KiB way/bank 2 内反向；32×128，128/128 | 目标/主机 0/0；58.458 秒；编号 2、3，轮询 11、34，数据/保护区零错误 |
| `layout_cross_bank` | `0x1400c040 → 0x14010040`，bank 3→4，覆盖 4 KiB 边界；32×128，128/128 | 目标/主机 0/0；58.416 秒；编号 2、3，轮询 10、19，零错误 |
| `layout_unaligned` | `0x14008043 → 0x14010045`；16×123，139/149 | **停滞，未通过**；215.048 秒后主动停止以进行内部诊断，主机返回 255，无目标返回；不是 600 秒超时 |
| `layout_cpu` | 同跨 bank 用例，同时 CPU 读写独立区域 | 目标/主机 0/0；59.864 秒；编号 2、3，每笔一次未完成轮询；CPU 共两轮读写，数据/保护区零错误 |

**非对齐组合未通过：AW 提前后出现“写等待读”的反向循环。** 原运行数分钟没有新指令提交，停止记录为 `$AW/run_layout_unaligned/diagnostic_stop.json`。随后复用同一 ELF，在 `diagnose_unaligned/` 运行至 2 ms，仅采样信号，不导出波形、不强制信号。诊断主机退出 0 只代表 Tcl 正常退出，不能计作程序成功。

600 μs、1 ms、2 ms 三次采样状态相同：

| 单元 | 实测状态 | 对应等待 |
| --- | --- | --- |
| DMA | `next_id=3, done_id=1`；RVALID=0/RREADY=1，WVALID=0/WREADY=1 | 首笔 ID=2 未完成；此时 DMA 愿意收 R，却没有读返回，也没有 W 数据可交付 |
| LLC write unit | busy=1，地址 `0x10010800`、len=7，`w_valid=0` | 当前 8 拍写描述符等待后续写数据 |
| hit/miss | 写 `0x10010840`，valid=1/ready=0 | 下一个写描述符等待 busy 的 write unit |
| shared spill | 读 `0x10008780`，valid=1/ready=0 | 所需读请求被前面的写描述符挡住 |
| read unit | busy=0，R FIFO 不满；最后描述符 `0x10008778`、len=0 | 读单元空闲，却收不到被挡住的读描述符 |
| 行锁/计数 | locked=0、cnt_stall=0，读写 unlock grant=1 | 本次没有行锁或计数阻塞 |

结合测试地址可进一步解释这一依赖：第 13 行（从 0 计）的源起点是 `0x14008752`，目的起点是 `0x140107d6`。目的 `0x14010800..0x1401083f` 对应源 `0x1400877c..0x140087bb`；最后已处理的 `0x10008778` 单拍读覆盖到 `0x1000877f`，后续源字节需要被挡住的 `0x10008780` 读请求。这里的映射是根据用例地址/步长与采样描述符推导，并非声称逐拍数据已另行采样。

等待链为：**当前写等 W → DMA 等源读返回 → 源读被后续写描述符挡住 → 后续写等当前写完成**。这与默认模式中“读返回满、读挡写”方向相反，说明只提前 AW 不能保证共同流水线对全部流量均能前进。没有把这组“非对齐＋不同步长”的失败推广成所有非对齐都失败；两项因素的独立影响尚未分别测试。

本次停止在已授权的按次配置接口与诊断范围，没有继续改 LLC/iDMA RTL、打开 RW 解耦或引入软件拆分搬运机制。下一步若要求支持该组合，应另行确定共享流水线防死锁修改及回归范围；不能把该用例静默移出验收。


固定测试区位于 SPM 的 `0x14008000` 至 `0x14016100` 范围内；CPU 并发区为 `0x14016000` 起 256 字节，与源/目的分开。运行前检查各 ELF 实际分配 section 的末端低于缓存地址 `0x10008000`；启动栈仍在 SPM 顶部，测试区不覆盖代码、全局数据或栈。

首轮布局脚本在运行前的地址检查中误把链接符号 `__base_dram=0x80000000` 当成实际占用内存，因此停止，尚未运行布局仿真。已改为检查 ELF 的 SHF_ALLOC section；原脚本与失败日志保留为 `layout_run_preflight_failed.py`、`layout_progress.log`、`layout_build_commands_preflight_failed.json`，重试输出为 `layout_progress_retry.log`。这是本次测试脚本检查错误，不是目标 DMA 故障。

### 10.5 结论、保护范围与图稿

**本次 10 个功能测试中，9 个目标返回 0；非对齐步长组合停滞，整体定向验收未通过。** AW 解耦使原对齐长搬运及已列出的三个布局通过，不能覆盖另一种“写挡读”循环。默认 NONE 模式的 RTL 死锁没有被消除；仍保留原失败结果，不将这次配置规避写成任意流量下的通用硬件修复。未验证 DDR/cache 模式、任意多主机流量、重叠复制、在线解锁、1D 功能及完整 RVV/ASIC 验收。

这是当前 DMA 与 LLC/SPM 组合的前进性缺陷：局部反压动作正确，但资源等待形成循环，正常请求不能完成。不能仅凭这一点认定独立 iDMA 某个模块违反 AXI；官方 #189 只是提供配置接口，也没有宣称修复 #219。详见[设计缺陷判断和结构图](../../../../engineering/DMA_Control_Path_and_Fix.md#dma-aw-implementation)。

服务器前后核对 83 项已有保护清单，除本次清单内改动外的 81 项哈希保持；另对四个授权文件检查预期修复后哈希。排除四个文件后，Git diff 与部署前一致；四项相关依赖 HEAD 与原记录一致且无 tracked 差异，`git diff --check` 通过。完整摘要见 [protection_result.json](../evidence/dma_aw_config_20261020/protection_result.json)。本地 25 项范围外文件哈希保持，未修改本地生产 RTL/sw、依赖、TTY 或 `/opt`，未 commit/push/发布 PR。

[汇报图](../../../../diagrams/2026-10-20_dma_llc_deadlock/README.md)提供 SVG、PNG、原生 PPTX。最终 SVG 的整图预览已实际查看；PPTX 保存重读、文字、102 个原生对象、24 个箭头端点和 3 个虚线轮廓检查通过，无整图位图。Office 显示/编辑未验证。报告第 1–9 节保留，不重新解释为本次测试。


<a id="dma-cause-confirmation"></a>

## 11. 新死锁原因复核与单变量对照（2026-10-20）

**结论：新旧死锁的直接原因不同。** 原默认模式是“读返回积满，读挡写”；本次 AW 解耦用例是“写数据不齐，写挡住所需读”。共同的结构条件是 LLC 读写描述符共用流水线，后面的请求不能越过堵住的描述符。不能把“非对齐、不同步长”当成充分触发条件；新增对照中，保留这些特征也有完整通过的用例。

### 11.1 实际对照结果：只对下列组合负责

固定 AW=1、RW=0，源/目的区域和验证方式沿用上轮失败用例。基准参数：源 `0x14008043`、目的 `0x14010045`，每行 123 B、16 行，源/目的步长 139/149 B。每个成功用例均连续执行两笔，并检查编号、等待、数据、行间隙、前后保护区和源区未改变。

| 相对基准只改变的参数 | 每笔请求量 | 实际结果 |
| --- | --- | --- |
| 不变，重新编译基准 | 123×16＝1968 B | 复现“写挡读”，首笔未完成 |
| 仅源起点 `…8043 → …8040` | 1968 B | **两笔通过**；后续行仍因 139 B 步长而改变对齐位置 |
| 仅目的起点 `…0045 → …0040` | 1968 B | **两笔通过**；后续行仍不是全部对齐 |
| 仅每行长度 `123 → 128 B` | 2048 B | **两笔通过**；起点及 139/149 B 步长保持 |
| 仅源步长 `139 → 149 B` | 1968 B | **两笔通过**；两侧步长变成 149/149 B |
| 仅目的步长 `149 → 139 B` | 1968 B | **两笔通过**；两侧步长变成 139/139 B |
| 仅行数 `16 → 1` | 123 B | **两笔通过** |
| 仅行数 `16 → 13` | 1599 B | **两笔通过** |
| 仅行数 `16 → 14` | 1722 B | 复现“写挡读”，首笔未完成 |

这是原失败基准加 **8 组单变量对照：新增 7 组通过、1 组失败**。13 行通过、14/16 行失败只适用于这组起点、长度、步长、配置及仿真环境；没有测试全部更大行数，也不能推广成“所有 14 行以上都死锁”。改变参数也会改变 burst 分割及请求时序，不能据此把任一通过参数宣布为全局安全规则。

新基准 ELF 的 `.text` 与上轮失败 ELF 逐字节相同，排除因诊断源码改写而更换复现程序。成功判据为目标返回 0 的 SLINK SUCCESS、主机退出 0、无目标/工具错误；这 7 组均无新增断言。两个失败组在 600 μs 与 2 ms 的内部状态保持同一循环，采样脚本随后退出，没有等满 600 秒；**主机退出 0 是诊断结束，不是目标通过**。

### 11.2 第 14 行具体发生了什么

1. **当前 iDMA 在 64 位通路使用 2 KiB 的分段边界。** 源码的分段粒度为 `min(256×8, 4096)=2048 B`；本例长度缩减配置为 0、RW 解耦为 0，读写按较近边界同步分段。这是当前实现的分段方式，不是把 AXI 的所有边界规则都说成 2 KiB。
2. 第 14 行（从 0 计为第 13 行）源为 `0x14008752`，目的为 `0x140107d6`。目的到 `0x14010800` 只剩 **42 B**，所以该行实际被分成 **42 B＋81 B**。分段器采样直接读到这两个数，不再仅凭地址推测。
3. 第二段从源 `0x1400877c` 搬到目的 `0x14010800`。iDMA 发出对齐后的 AR=`0x14008778`、AW=`0x14010800`，两者 LEN=10、SIZE=3，即各 11 拍、每拍 8 B；有效字节由移位及掩码处理。
4. LLC 再按 64 B 边界切分。第二段的首个 8 B 写拍需要源 `0x1400877c..0x14008783`：前 4 B 来自读描述符 `0x10008778`，后 4 B 来自后续读 `0x10008780`。这里 `0x140…` 是非缓存别名，LLC 入口已还原为 `0x100…`。
5. **后续写描述符 `0x10010840` 比所需读 `0x10008780` 更早进入共同流水线。** 它等当前写完成；当前写等后 4 B 数据；后 4 B 的读又被它挡住，循环成立。

关键实测值：在 600 μs 和 2 ms，写侧 `w_dp_valid_i=1`、所需字节掩码 `mask_out=0xff`、已有字节 `buffer_out_valid_i=0x0f`、`ready_to_write=0`。源码要求所有所需字节有效才发 WVALID，因此此时停发 W 是正确动作；不能丢掉后 4 B 强行完成写拍。DMA 的 **RREADY=1**，LLC read unit 空闲、R FIFO 不满；它愿意读，却拿不到被挡住的读描述符。

代码对应：

- [iDMA 分段器](../../../../../.bender/git/checkouts/idma-77bf7fa56d324e6a/target/rtl/idma_legalizer_rw_axi.sv)：79 行定义分段大小，164–184 行在 RW 耦合时取两侧较近边界；[page splitter](../../../../../.bender/git/checkouts/idma-77bf7fa56d324e6a/src/backend/idma_legalizer_page_splitter.sv)计算具体剩余字节。
- [iDMA 写数据单元](../../../../../.bender/git/checkouts/idma-77bf7fa56d324e6a/src/backend/idma_axi_write.sv)：159–160 行检查所需字节是否全部有效，177 行由此产生 WVALID。
- [LLC write unit](../../../../../.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/src/axi_llc_write_unit.sv)：157–166 行只有实际消费完描述符要求的 W 拍才释放 busy 并接下一条写。
- [LLC hit/miss](../../../../../.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/src/axi_llc_hit_miss.sv)：184–188 行等待下游 ready 后才能释放当前 hit 描述符；共同通路连接见 [LLC top](../../../../../.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/src/axi_llc_top.sv) 的仲裁、spill、hit/miss 和 merge unit。

### 11.3 用通过用例检验上述解释

只把源起点改成 `0x14008040`，其余参数保持，仍有非对齐行和不同步长。对这个完整运行已通过的 ELF 再做短窗口采样，得到：

| 观测 | 原失败用例 | 仅源起点改变的通过用例 |
| --- | --- | --- |
| 所需读与后续写的进入顺序 | 555140 ns：W `0x10010840`；555230 ns：R `0x10008780` | **555085 ns：R `0x10008780`；555095 ns：W `0x10010840`** |
| 当前写拍的数据是否齐全 | 所需 `0xff`，已有 `0x0f`，持续不变 | 555145 ns 已有 `0x7f`，暂时停写；555190 ns 变为 `0xff`，WVALID=1 |
| LLC 是否收到 W | 当前写持续等数据 | 555215 ns，LLC write unit 的 `w_valid=1`，搬运继续 |

因此，**短暂缺少字节本身不等于死锁**。失败的关键是提供缺失数据的读被前面的写挡住；通过用例将该读先放行，数据能够补到齐全。这是对具体因果链的对照支持，不是仅看“程序最终成功/失败”给参数贴标签。

### 11.4 与原死锁的区别、产物和边界

| 项目 | 第 9 节原默认模式 | 本次 AW 解耦失败组 |
| --- | --- | --- |
| DMA 当前状态 | 数据缓冲满，RREADY=0 | 写拍数据缺字节，RREADY=1、WVALID=0 |
| LLC 当前阻塞 | R 返回 FIFO 满，当前读不能完成 | 当前写等 W，read unit 空闲 |
| 关键被挡请求 | 写描述符被读挡住 | 源读描述符被后续写挡住 |
| 共性 | 共同描述符流水线与数据依赖构成循环 | 同左，但不是同一条直接等待链 |

本轮只做诊断和测试副本，没有修改生产 HAL、RTL、依赖或配置。服务器输出为 `$AW/cause_check_20261020/`；[本地摘要与用例](../evidence/dma_aw_config_20261020/cause_check/README.md)保存参数、构建命令、结果、分段/掩码/描述符采样摘要，完整日志、trace 和 ELF 留服务器。内部采样使用原失败 ELF 和已通过的源起点对照 ELF；不把 Tcl 主动退出计作功能通过。

结果解析已排除 UCLI 对 Tcl 命令的回显，只将单独输出的循环标记计作持续等待；早期含回显匹配的中间 JSON 和脚本在服务器保留，最终摘要已经纠正。没有因此改变目标程序或重写仿真结果。生产 Git diff 与执行前完全相同，83 项保护哈希保持；用于分析的源码已和服务器核对。仍未证明任何参数范围普遍无死锁，也没有执行 LLC/iDMA 防死锁结构修复。

<a id="read-assertion-fix-20261020"></a>

## 12. CVA6 读数据断言修正与验证（2026-10-20）

用户授权修改已定位的 `dma_long_aw_api` 断言问题并测试。本节只处理验证逻辑；第 11 节的 DMA/LLC 死锁结论及未完成项保持。服务器 Cheshire HEAD 仍为 `e040b7bbc7851a37faff3c4657ff8d656cc6e20a`，CVA6 为 `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c`。修改前该 CVA6 checkout 的 Git 状态干净；本地 HEAD 为 `c9abbb48946fe3a7244bfb3159919b7c9731cb59`。WSL SSH 握手超时后，沿用用户已允许的 Windows SSH。

### 12.1 修改哪个文件、哪一行

**只修改服务器参考工程的两份源码，本地 FPGA 对应源码未改。** 两个文件共同目录为：

```text
/home/zhaowy24/CheshireAraPULP/.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/cache_subsystem/
```

行号基于本节保存的修改前、修改后文件，不按上游最新分支计算。完整前后差异见 [assertion.patch](../evidence/read_assertion_20261020/assertion.patch)，输入及输出哈希见 [patch_inputs.json](../evidence/read_assertion_20261020/patch_inputs.json)。原件在服务器新输出目录的 `before/` 中。

| 文件 | 修改前位置 | 修改后位置 | 实际变化 |
| --- | --- | --- | --- |
| `wt_cache_subsystem.sv` | 286–297 行，原条件在 289 行 | 286–287 行 | 移除外层整字读数据检查，注明检查转移到已有读控制器；写数据断言保持 |
| `wt_dcache_ctrl.sv` | 原 291 行 `hot1` 检查之前，无按字节读数据检查 | 291–313 行；元信息断言 293–300 行、数据断言 302–313 行 | 利用已有 `address_off_q`、`data_size_q` 检查正确的返回字节，并打印采样值；原 `hot1` 等检查保留 |

**修改前：** 外层在返回有效且未取消时检查整个 64 位数据，打印当前信号值。

```systemverilog
assert property (
  @(posedge clk_i) disable iff (!rst_ni)
    dcache_req_ports_o[j].data_rvalid && ~dcache_req_ports_i[j].kill_req
    |-> (|dcache_req_ports_o[j].data_rdata) !== 1'hX)
else
  $warning(1, "[l1 dcache] reading invalid data on port %01d: data=%016X",
           j, dcache_req_ports_o[j].data_rdata);
```

这既会因未使用字节中的 X 误报，也可能因其他位为 1 使归约 OR 为 1 而漏报。报错打印未使用采样值，可能与触发断言的数据不同。

**修改后：** 断言放在真实 `wt_dcache_ctrl` 的现有仿真专用区域内。先检查保存的访问范围确定且不越过返回字边界，再检查该范围内的每个字节。

```systemverilog
  a_read_metadata_known :
  assert property (@(posedge clk_i) disable iff (!rst_ni)
    req_port_o.data_rvalid && !req_port_i.kill_req |->
      !$isunknown({address_off_q[CVA6Cfg.XLEN_ALIGN_BYTES-1:0], data_size_q}) &&
      ((int'(address_off_q[CVA6Cfg.XLEN_ALIGN_BYTES-1:0]) + (1 << data_size_q))
        <= CVA6Cfg.XLEN / 8))
  else $warning("READ_META_INVALID %m id=%h offset=%h size=%h",
      $sampled(id_q), $sampled(address_off_q), $sampled(data_size_q));

  for (genvar byte_idx = 0; byte_idx < CVA6Cfg.XLEN / 8; byte_idx++) begin : gen_read_data_check
    a_read_data_known :
    assert property (@(posedge clk_i) disable iff (!rst_ni)
      req_port_o.data_rvalid && !req_port_i.kill_req &&
      !$isunknown({address_off_q[CVA6Cfg.XLEN_ALIGN_BYTES-1:0], data_size_q}) &&
      (byte_idx >= int'(address_off_q[CVA6Cfg.XLEN_ALIGN_BYTES-1:0])) &&
      (byte_idx < int'(address_off_q[CVA6Cfg.XLEN_ALIGN_BYTES-1:0]) + (1 << data_size_q))
      |-> !$isunknown(req_port_o.data_rdata[byte_idx*8+:8]))
    else $warning("READ_DATA_X %m id=%h offset=%h size=%h byte=%0d data=%h",
        $sampled(id_q), $sampled(address_off_q), $sampled(data_size_q), byte_idx,
        $sampled(req_port_o.data_rdata));
  end
```

`address_off_q`、`data_size_q`、`id_q` 原本就在请求获准时保存，返回时尚未被同周期下一笔请求覆盖。没有用“当前请求”的字节使能代替返回对应的信息，也没有新增寄存器、接口或跟踪队列。当前配置的 PTW、标量 load、加速器读端口均由相应的 `wt_dcache_ctrl` 实例检查。

保留原来的 reset/kill 门控及 warning 严重度。两份文件的全部差异均位于既有 `//pragma translate_off` 区域且受 `ifndef VERILATOR` 保护；去掉该区域后，修改前后的功能源码文本完全一致。这是源码范围检查，不是另做过综合或形式等价验证。本次是项目局部修正，不冒称直接回移某个官方断言补丁。

### 12.2 实际构建与输出

新产物在服务器：

```text
~/CheshireAraPULP/_e01/dma_vector_check/read_assertion_20261020/
```

下文以 `$ASSERT` 表示。使用原有编译清单与构建参数，在空的 `$ASSERT/rtl_build/` 从源码重新编译和展开，未复制旧编译库或 simv。VCS 为 W-2024.09-SP1，SelectedCfg=3，硬件配置、FS、HAL、ELF 均保持。

编译退出 0、19.459 秒；展开退出 0、33.009 秒。新 simv SHA256：`f96fba4c7f1ccdb0755649770863fa6762b7cfa62b50647659c334128998556b`。命令和结果见本节 [证据目录](../evidence/read_assertion_20261020/README.md)，完整日志/编译库保留服务器。

### 12.3 定向检查：证明没有用取消检查来隐藏问题

[测试源](../evidence/read_assertion_20261020/tb_read_assertion.sv)实例化本次修改后的真实 `wt_dcache_ctrl`，通过请求、返回及 miss/replay 控制信号驱动；没有复制一份断言函数作为替代 DUT。使用当前 64 位返回数据配置，覆盖 byte/halfword/word/doubleword 和各自然对齐偏移。

| 内容 | 检查数 | 预期与实际 |
| --- | --- | --- |
| 有效字节为 0、范围外含 X | 15 | 均不报警，包含本例高 32 位读取 |
| 有效字节含 X，其他字节为 1 | 15 | 每例准确报 1 次数据警告，避免原归约 OR 漏检 |
| 有效字节含 Z | 15 | 每例准确报 1 次数据警告 |
| 取消请求，返回全 X | 1 | 不检查已取消结果 |
| 宽度未知、访问范围越界 | 2 | 每例报 1 次元信息警告，不因无法生成有效范围而静默跳过 |
| miss 等待、replay 重试 | 4 | 有效数据正常时不报；有效字节含 X 时各报 1 次 |
| 采样后立即改变数据 | 1 | 日志仍打印触发断言的 `ffffffxxffffffff`，没有误打印后来的 `deaddeaddeaddead` |
| 旧 32 位返回同时接收新 8 位请求 | 1 | 两笔按各自保存的范围检查，均不误报 |

**54 项均符合预期。** 其中 33 次数据警告、2 次元信息警告是主动注入的负例预期结果，逐例核对数量；这不是普通回归的告警豁免。19 个正例/取消场景无警告。定向仿真主机退出 0，`UNIT_DONE cases=54`，完整逐例摘要见 [unit_result.json](../evidence/read_assertion_20261020/unit_result.json)。

### 12.4 相同 ELF 的 SoC 回归

串行运行，每例主机上限 600 秒，不导出波形。新 simv 使用前次 `$AW` 的原 ELF，检查程序完成、主机状态和断言；未初始化整片栈、改程序或者关闭断言来消除告警。

| 用例 | 程序返回 / 主机退出 | 新断言告警 | 主机耗时 / 秒 |
| --- | --- | --- | --- |
| `dma_long_aw_api` | 0 / 0 | 0 | 241.185 |
| `helloworld` | 0 / 0 | 0 | 33.283 |
| `vector_fixed` | 0 / 0 | 0 | 81.746 |


三项均获得 `[SLINK] SUCCESS`，且 CPU trace 与修改前同一 ELF 的完整 trace **逐字节一致**，三个哈希均相同。长 DMA 的原告警消失，提交/完成编号仍为 2、3、4，等待次数仍为 19、30、30，数据和保护区检查通过；UART 仍只完整打印前两笔，第三笔由相同的完整 trace 与程序返回值确认。向量用例输出 `VECTOR_COPY errors=0 bytes=22`。具体哈希、命令和退出记录见 [soc_results.json](../evidence/read_assertion_20261020/soc_results.json)。这支持本次改动只改变验证行为，不将三个用例的轨迹一致扩大为全设计等价证明。

### 12.5 保护检查与结论

服务器 85 项保护哈希保持，根 Git diff 与实施前一致。四项相关依赖 HEAD 不变；其中 CVA6 仅上述两份断言源码存在差异，其他三项依赖无 tracked 差异。两份源码修复后哈希、实际行号、功能文本比较及范围检查见 [protection_result.json](../evidence/read_assertion_20261020/protection_result.json)；`git diff --check` 通过。本地 24 项范围外文件哈希保持，包括本地两份 CVA6 源码、HAL、wrapper。未修改 TTY 工程、工具安装、硬件配置、HAL、启动 FS 或已有失败产物。

结论：本节修复了 `dma_long_aw_api` 已定位的检查范围误报与打印采样问题，负例验证保留了实际有效数据的 X/Z 检测。它不修复第 11 节的 DMA/LLC 死锁，也不代表其他 CPU 配置、其他缓存实现、Verilator 或全部 ISA 验证已通过。未 commit、push 或发布 PR。

<a id="dma-alignment-check-20261020"></a>

## 13. 软件对齐粒度对照与断言修复复核（2026-10-20）

**结论：不能把 64 B 称为三个参数各自必需的最小粒度。** 8/16/32 B 统一规则均有实测死锁反例；64 B 是当前最简单的保守统一选择。单独缩短行长、或让源与目的保持相同的 64 B 块内偏移，也有通过用例。因此可另行验证更宽松的参数组合，但不能把任一小粒度成功组合推广为全范围支持。

### 13.1 输入、检查方法与实际结果

沿用第 11 节测试副本和构建命令，仅参数化地址、每行长度、两侧步长与行数；扩大初始化和逐字节校验范围以容纳更大步长。校验源区不变、目的数据、行间隙及前后保护区；两次顺序提交，检查编号 2/3、完成编号和非零轮询次数。测试区界限先核对，避开代码、栈和其他缓冲区。

使用第 12 节**已修断言**的现有 simv，SHA256=`f96fba4c7f1ccdb0755649770863fa6762b7cfa62b50647659c334128998556b`。硬件参数、HAL、FS 及依赖不变；本轮未重建 RTL。所有用例均 SPM 非缓存别名、源目的不重叠、AW=1/RW=0，每组连续两笔，串行运行、每例主机上限 600 秒、不导出波形。

| 用例 | 源地址 → 目的地址 | 每行 B × 行数 | 源/目的步长 B | 结果 | 主机秒 |
| --- | --- | --- | --- | --- | --- |
| `align32_phase_shift` | `0x14008060 → 0x14010040` | 128×16 | 160/192 | 首笔持续写挡读 | 19.073 |
| `align16_phase_shift` | `0x14008050 → 0x14010040` | 128×16 | 144/160 | 首笔持续写挡读 | 18.791 |
| `align8_phase_shift` | `0x14008048 → 0x14010040` | 128×16 | 136/144 | 首笔持续写挡读 | 18.473 |
| `align64_phase_shift` | `0x14008040 → 0x14010040` | 128×16 | 192/256 | 两笔通过 | 68.67 |
| `align64_boundary` | `0x140087c0 → 0x14010780` | 192×8 | 256/320 | 两笔通过 | 44.389 |
| `address32_only` | `0x14008060 → 0x14010040` | 128×16 | 192/256 | 首笔持续写挡读 | 19.523 |
| `stride32_only` | `0x14008040 → 0x14010040` | 128×16 | 160/256 | 首笔持续写挡读 | 19.653 |
| `length24_only` | `0x14008040 → 0x14010040` | 24×16 | 192/256 | 两笔通过 | 60.677 |
| `length120_only` | `0x14008040 → 0x14010040` | 120×16 | 192/256 | 两笔通过 | 66.829 |
| `address32_same_offset` | `0x14008060 → 0x14010060` | 128×16 | 192/256 | 两笔通过 | 68.424 |
| `address8_same_offset` | `0x14008048 → 0x14010048` | 128×16 | 192/256 | 两笔通过 | 68.448 |

成功行表示两笔目标检查全部通过、`[SLINK] SUCCESS` 且主机退出 0、无断言。失败行表示首笔仍未完成，在 600 μs 和 2 ms 采样到相同的“写等数据、后续写挡读”状态，诊断随后主动结束；**不是主机超时，也不能因为主机退出 0 计为通过**。所有测试均无新的 X/Z 告警。合计 **6 组通过、5 组持续循环**，不是“所有小粒度都失败”。

### 13.2 为什么连 32 B 对齐也会失败

以 `align32_phase_shift` 为例：源 `0x14008060`、目的 `0x14010040`、行长 128 B、步长 160/192 B、16 行，五个字节参数都满足 32 B 整数倍。

第 9 行（索引 8）源为 `0x14008560`，目的为 `0x14010640`。目的第一个 64 B 写块需要源 `…8560..859f`：前 32 B 属于读块 `…8540..857f`，后 32 B 属于读块 `…8580..85bf`。前 32 B 已写入后，当前写停在 `0x10010660`；后续写 `0x10010680` 挡住所需源读 `0x10008580`。

实测：当前写 busy=1、剩余 LEN=3（4 拍）；read unit 空闲；DMA RREADY=1，WVALID=0，`mask_out=ff`、`buffer_out_valid_i=00`、移位量=0。**这次不是“8 B 内还缺 4 B”，而是下一整拍根本没有到达。** 8 B 对齐只能消除拍内重排，不能消除一个 LLC 写块依赖两个源读块的情况。16/8 B 失败组也观察到同类循环。

64 B 起点及步长会使每一行的源/目的 LLC 分块边界对应；在 RW 耦合模式下，当前 2 KiB 分段边界也是 64 B 的倍数。行长不是 64 B 倍数时，只要起点关系保持，末尾的读写短块仍可对应。因此不应把行长 64 B 当成必需条件。

进一步放宽地址的一种几何条件是 `src % 64 == dst % 64`、`src_stride % 64 == dst_stride % 64`，从而每行源/目的保持相同块内偏移。本轮只验证表中相同偏移组合；**该等式说明分块关系，不是包含所有并发、反压和 cache 行为的无死锁证明。** 更小单位可以有可用组合，但不是简单把“64”全替换为“32/16/8”。

### 13.3 当前建议、保护与断言确认

- 默认软件采用地址 64 B 对齐、两侧步长及每行长度为正的 64 B 整数倍，AW=1/RW=0；称作**保守统一规则**，不称最优或硬件最小要求。若应用需要较短行长，或更小对齐，应按本节已测组合及具体布局另外确定支持范围，不擅自向上取整访问越界。本轮没有向 HAL 写入规则或自动 CPU 回退。
- 官方旧默认标志的对齐长搬运仍然死锁；不能只写对齐条件而省略 AW/RW 配置。未执行一般 cache/DDR、重叠复制、多主机压力或全部参数组合验证。
- 已只读复核另一位 Agent 的第 12 节交付：两份服务器 CVA6 文件及 simv 哈希一致；移除仿真专用区域后，功能源码与固定原版相同。54 项摘要全部符合预期，服务器定向日志含完成标记；三项原 ELF/成功日志/CPU trace 哈希匹配且无读断言。此处复核已有结果，未重复声称本轮重跑其三项回归。
- 新输出在服务器 `$AW/alignment_check_20261020/` 及其 `factor_checks/`，其中 `$AW=~/CheshireAraPULP/_e01/dma_vector_check/aw_config_20261020`。测试源、参数、命令、结果、状态摘要及断言复核结果见[本地必要摘要](../evidence/dma_aw_config_20261020/alignment_check/README.md)；完整日志、trace、ELF 留服务器。两组运行结束后分别确认根 Git diff 和 85 项输入哈希保持；CVA6 仍仅有第 12 节两份断言差异。本轮不修改生产 RTL/HAL、本地 FPGA 源码或依赖，不执行提取。
- 本地按用户要求精简 DMA 专题，保留控制/数据/完成链、错误位置、修复来源、两类死锁和有效链接。修改前全文保存在 `/tmp/e01-alignment-nooyxpcl/before/DMA_Control_Path_and_Fix.md`；原报告第 1–12 节和既有测试产物保留，没有因精简删除失败记录。
