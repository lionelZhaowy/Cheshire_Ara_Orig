<a id="示例程序导读功能执行流程与前置条件"></a>

# 示例程序与验证条件

返回 [软件导航](README.md)。本页覆盖 `sw/tests` 当前全部 **9 个 .c/.S 主程序**，另说明辅助文件、`tests_wo_ara` 和 Ara 依赖中的 **2 个应用、16 个验证程序**。功能说明依据源码，未在本轮执行这些目标程序。

<a id="1-先用这张表选程序"></a>

## 1. 示例分类与硬件要求

| 当前主程序 | 功能 | 典型硬件配置/存储 | 判据与学习顺序 |
| --- | --- | --- | --- |
| [helloworld.c](../../sw/tests/helloworld.c) | UART 格式化输出 | 普通配置、UART/CLINT；先 .spm | 观察两行输出+返回 0；第一步 |
| [dma_2d.spm.c](../../sw/tests/dma_2d.spm.c) | 二维 DMA、stride 与 SPM 别名 | Dma=1；仅 SPM | 返回不匹配 byte 数；第二步 |
| [axirt_hello.spm.c](../../sw/tests/axirt_hello.spm.c) | AXI RT 配置后串口输出 | SELCFG=1、DMA/UART；无 Ara 编号假设 | 特性检查+输出；进阶 |
| [axirt_budget.spm.c](../../sw/tests/axirt_budget.spm.c) | DMA 预算按传输 byte 计数 | SELCFG=1、64-bit AXI、SPM | 数据比较+读写预算差；进阶 |
| [axirt_budget_isolate.spm.c](../../sw/tests/axirt_budget_isolate.spm.c) | 超预算隔离意图 | 同上；当前阻塞流程需检查 | 不宜直接作为首个自动回归 |
| [clic_basic.spm.S](../../sw/tests/clic_basic.spm.S) | 单中断阈值/向量入口 | SELCFG=2，CPU CLIC 支持 | 0 成功，1 失败 |
| [clic_multiple.spm.S](../../sw/tests/clic_multiple.spm.S) | 两中断不同等级与阈值 | 同上 | 30 先、31 后；0 成功 |
| [fmatmul_test_4x4.c](../../sw/tests/fmatmul_test_4x4.c) | 标量与 RVV FP64 矩阵乘 | 向量 CPU+SELCFG=3 或匹配 FPGA；先 .spm | 对照数值；当前失败未汇入退出码 |
| [mnist_mlp_cpu.dram.c](../../sw/tests/mnist_mlp_cpu.dram.c) | CPU 量化 MLP 推理示范 | DDR 可用；.dram | 输出结果/周期；不是精度自动验收 |

所有应用均依赖当前 crt0 的 RV64/D 浮点初始化。`SELCFG` 只选 SoC，不替换 CPU profile 或软件 ISA。默认板级没有 AXI RT/CLIC 时，不能因板上 HelloWorld 已跑通就直接运行对应测试。

<a id="2-helloworld一条-printf-如何到串口"></a>

## 2. HelloWorld 初始化与 UART 输出

当前流程：设置 mstatus.VS→读 RTC_FREQ→用 CLINT/mcycle 测核频→UART 设 115200/8N1→printf 输出问候与 `1024/0x400`→等待 TX 空→返回 0。

两个核心调用：`clint_get_core_freq(rtc_freq,2500)` 为 UART 分频取得频率；`printf` 经 `_putchar` 最终进入轮询 UART 写。设置 VS 没有执行向量计算，不能用该程序证明 Ara 工作。

可做的最小练习：改打印整数、用 snprintf 格式化到静态数组、读一个只读 SoC 配置寄存器并打印。只在应用变更时重编/重载 ELF，不需要因此重建 FPGA bitstream。

`tests_wo_ara/helloworld.c` 是更早的直接 `uart_write_str("Hello World!…")` 版本，无 VS 设置和格式化输出；它不在默认自动测试列表。

<a id="3-dma-2d从重叠字符串看-stride"></a>

## 3. 二维 DMA 的长度、步长与数据布局

流程：

1. 检查 DMA feature；不存在返回 −1。
2. 在栈上建立源字符串、参考字符串和目的缓冲。
3. 用 `+0x04000000` 得到 SPM 非缓存别名，并把源内容显式写到 DMA 可见入口。
4. 在目的缓冲尾部写 `!` 和 `\0`，作为越界哨兵。
5. 调用 `sys_dma_2d_blk_memcpy(dst,src,15,7,1,4)`；源码长度表达式为 `sizeof(src_cached)-4`。
6. 等待任务完成，逐 byte 比较 gold，返回不匹配数量。

源数组含终止符共 19 byte；目的/gold 共 38 byte。4 段起点与覆盖区间如下（byte 索引，右端不含）：

| 段 | 源区间 | 目的区间 |
| --- | --- | --- |
| 0 | [0,15) | [0,15) |
| 1 | [1,16) | [7,22) |
| 2 | [2,17) | [14,29) |
| 3 | [3,18) | [21,36) |

后段覆盖前段尾部，结果为 `This ishis is is is as is a DMA test!`。本轮只用主机 Python 对上述索引计算复核了 gold，并未运行 DMA 硬件。尾部索引 36/37 应保留 `!/\0`。

这比二维图像更小，但机制相同：每行长度和行起点间隔可不同。图像例子中常让 dst_stride 等于目标帧 pitch；本例特意用小 stride 产生重叠。不要把这段加别名偏移的代码改成 .dram 链接后原样使用。

<a id="4-axi-rt-三个程序先理解-manager-编号"></a>

## 4. AXI RT 测试与发起端编号

共同前提：有 AXI RT、DMA，至少 2 个 subordinate region，通常运行 `SELCFG=1`。CPU0 manager=0、Debug=1、DMA=`NumIntHarts+1` 是这些例程的无 Ara 假设。Ara 加入后 DMA 位置变化，同时需检查生成 RT 寄存器的 manager 数。

### 4.1 axirt_hello.spm.c

检查 AXI RT/DMA/UART 特性与区域数→取得核频→claim 配置 guard→设置 burst 限制→给 CPU0 设置两个地址 region、预算 8/周期 100→给 DMA 设置大预算/周期→`enable(0x5)` 同时打开 manager0/2→初始化 UART→打印→flush→返回 0。

它主要展示配置顺序与受限 CPU 流量仍可输出；虽然配置 DMA，却没有实际发起 DMA 搬运。缺失 feature/region 时返回 −1/−2/−3/−4。不能把它的通过解释成预算计数和隔离都已测试。

### 4.2 axirt_budget.spm.c

检查特性→分配 128 个 uint64_t 源/目的数组与 gold→通过非缓存 SPM 别名访问→为 CPU/DMA 配置大预算 `0x10000000` 与长周期→设 burst fragmentation 字段→初始化递增图样→fence→DMA 搬 1024 byte→逐项比较→读 DMA 读/写剩余预算→检查各扣 1024 且读写一致。

数据错返回 `20+i`；预算结果返回三项布尔差异之和，0 表示源码判据满足。`DMA_NUM_BEATS=128` 明确假设 64-bit AXI，不是任意位宽通用常量。frag 值 0 是 AXI 长度字段式的最大碎片化配置，不代表允许零字节传输。

**当前实现细节**：测试先 `__axirt_enable(CPU位图)`，再 `__axirt_enable(DMA位)`；库是整寄存器写而非 OR，因此最终使能不自动包含第一次的 CPU 位。它仍可用于阅读 DMA 预算流程，但不能声称“CPU 和 DMA 同时受控”已经由这段调用保证。

### 4.3 axirt_budget_isolate.spm.c

初始化 32 个 uint64_t（256 byte）源/目的数组→配置 CPU 大预算→DMA 总请求设计为 8 次×256=2048 byte，而预算只给一半 1024 byte→调用 stride=0 的二维传输，反复访问相同区域→检查 manager 隔离→隔离时返回 0。

**关键执行顺序问题**：源码使用阻塞 `sys_dma_2d_blk_memcpy`，等待全部任务完成之后才 `__axirt_poll_isolate`。若隔离使任务不能完成，就到不了检查语句；若等待周期补充预算后完成，又需确认隔离状态是否还满足判据。加上 poll 无超时，此例可能长时间不退出，不能直接作为初学者的一键成功示例。

后续验收需要把提交、观察隔离、解除/补充预算、任务完成分别设计，并加超时；本轮仅说明，未改程序。它也有上一例连续 enable 覆盖和 manager 编号的限制。

## 5. CLIC 两个汇编示例

这些示例直接写 `0x08000000` 的 CLIC，`CLICINT(id)=base+0x1000+4×id`；`mtvt` CSR=0x307、`mintthresh`=0x347。开启 mstatus.MIE、设置 mtvec 低位为 3 进入本实现 CLIC 模式，配置 SHV、edge trigger、pending、enable、level/priority。阈值与 level 位数一起决定是否可响应。

它们使用 `.option norvc` 保持指定指令长度，并有对齐的跳转表。不同版本 CLIC 的表格式/CSR 细节可能不同，必须以本工程 CPU/CLIC 实现为准，不能当成所有 RISC-V 平台都支持的通用代码。

### 5.1 clic_basic.spm.S

保存旧 mtvec→设置异常失败入口和 mtvt 表→配置 IRQ31（control=0xaa）并置 pending→配置 level 编码→mintthresh=0xff，保持屏蔽→等待500次循环→置 a0=0，阈值降到0→期待进入 IRQ31 对应入口→恢复 mtvec→返回0；提前触发/未触发/走错误入口返回1。

`thirtyone` 附近注释与分支不一致：实际 `beqz a0, pass_restore` 表示 **a0=0 时通过**。这是以寄存器作测试阶段标志的验证写法，不是生产中断 handler 模板。

### 5.2 clic_multiple.spm.S

阈值0xff屏蔽全部→先挂 IRQ31/0xaa，再挂 IRQ30/0xcc→降低阈值至0xbb→只期待 IRQ30→handler 检查 a0=30 并 mret→回到主流程→把阈值降0并置 a0=31→IRQ31 handler 检查后转 pass→恢复 mtvec并返回0。

期望顺序是 **等级更高的 IRQ30 先响应，随后才是 IRQ31**，不是 pending 的先来先服务。源码最终 handler 部分以 ret/跳转直接收束测试，未完整恢复所有 CLIC/CSR/通用寄存器状态；不建议不复位连续串接这些例程当作通用 ISR。

## 6. fmatmul_test_4x4：CPU 与 Ara 的实际运算

数据：三个 4×4 double 数组 A/B/gold、两个结果数组，32-byte 对齐；gold 来自 [Python 脚本](../../sw/tests/fmatmul_test_4x4.py)。

流程：设置 VS/FS 为 3（Dirty）→测频/初始化 UART→读 instret/cycle→普通三重循环矩阵乘→再次计数→配置 RVV `e64,m4`→四个向量寄存器组清零→交替加载 B 行并用 `vfmacc.vf` 累加 A 的标量元素→`vse64.v` 写四行结果→读计数→打印周期/指令数与比值→按绝对误差0.001比较 scalar/vector 与 gold。

`VLEN=2048` 并不表示这次一定处理2048 bit；程序根据 P=4 设置实际 vl。LMUL=m4 对寄存器分组，不是“四个 lane”。每条向量指令的退休也不能按元素数当作 CPU 指令数。

当前限制必须保留：

- verify_result 失败会打印并返回−1，但 main 最后仍返回0；因此退出码不能独立判定通过。
- 内联汇编对隐式向量寄存器/内存副作用的约束需要审核，计时结尾也需确认 Ara 存储完成；本轮不认可输出比值为已验收性能。
- 以带 V 的编译选项编译时，名为 scalar 的 C 循环仍需反汇编确认是否被自动向量化。
- 此核只按当前4×4案例学习，不把内部展开循环当成任意奇数维度/余数维度均支持。
- `main` 没有显式 uart_write_flush；若返回路径/仿真结束很快，最后输出完整性需确认。

Python 脚本需要 NumPy，固定 seed=42，生成 A/B 与 `np.dot` gold，只打印 C 初始化文本，不自动改源码。输出保留6位小数，因此粘贴后的输入存在舍入，比较使用容差；不要手动改 A/B 却保留旧 gold。

## 7. mnist_mlp_cpu.dram.c：量化算法参考

先跳过大段权重/图像常量，按 `main → init_padding_arrays → linear1_normal…linear5_normal` 阅读。逻辑网络为 `784→64→64→32→16→10`，批大小32，按32元素块补齐；一个32位 int 打包四个8位有符号值。

每层流程：从 bias 初始化 int32 累加器→拆出输入和四个权重 byte→整数乘累加→用 int64 中间结果乘量化系数并右移→按开关做 ReLU→饱和到[−128,127]→重新打包写出。它是普通 CPU C 循环参考，不驱动独立 NPU/脉动阵列。

main 在栈上初始化输入，设置 VS 并初始化 UART→准备 padding 权重/bias、清中间数组→测量5层推理→解包32个样本的10类结果并找最大项→打印指令/周期→返回0。开启 VS 本身不表示算法使用 RVV；以最终指令为准。

注意：没有标签/golden 自动断言，不能从返回0推导分类精度达标；`max_val` 初值为0，对所有分数都为负的情况不能作为通用 argmax 实现。输入常量、栈和中间数组规模较大，按 .dram 链接；阅读/改网络时同步检查打包、补齐、量化系数和溢出范围。

## 8. 辅助文件和 tests_wo_ara

| 文件/目录 | 用途 | 构建关系 |
| --- | --- | --- |
| fmatmul_test_4x4.py | 生成矩阵数据/gold | 主机运行，非测试 ELF |
| fmatmul.c.h / fmatmul.h | 较完整矩阵核实现与接口 | 由 Ara fmatmul.c include |
| cheshire_util.h / vector_util.h | UART 入口、RVV/计时辅助 | 当前头里有函数定义，注意多编译单元重复符号 |
| rvv_test.h / encoding.h | CSR/断言/异常、stub测试辅助 | 与对应验证 RTL 配套 |
| *.c.body | 多个 RVV 变体共享正文 | 经 include 编译，不能单独当主程序 |
| tests_wo_ara | 8个备份主程序 | 自动扫描只看 tests；不会自动根据 Ara=0 选择这个目录 |

存在 .elf/.dump/.o 不说明这些文件与今天的 .c、flags、libcheshire.a 相匹配。源文件缺失时应追踪来源，而不是用旧 ELF 证明现在能重建。

## 9. Ara 依赖中的两种应用

源目录：[Ara Cheshire src](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src)。根 tests 中已有同名 ELF，当前 C 源在此处。

| 程序 | 功能与流程 | 当前源码注意点 |
| --- | --- | --- |
| [vector_helloworld.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/vector_helloworld.c) | UART init→enable_rvv→intrinsic vle8 读字符串→汇编 vse8 写 buf→打印→flush | 实际 `printf("%s", str_v)` 把向量值传给字符串格式，未使用已写好的 buf；不能直接作为正确 RVV 入门样例 |
| [fmatmul.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/fmatmul.c) | 默认32×32矩阵→CPU算gold→向量核→计时/FLOP估算→逐项比较 | 首次 printf 在 cheshire_start 之前；`k-j` 是无符号减法；verify首项失败返回−1后打印 c[error] 会使用负索引，需后续审核 |

`fmatmul` 四个 double 矩阵默认约32 KiB，不含代码/栈；扩大 `_MM_SIZE_` 时容量按平方增长。此处只是源码学习入口，不把内核注释里的最大矩阵尺寸当作 SPM 保证。

<a id="10-ara-专用验证测试先确认配套寄存器"></a>

## 10. Ara 专用验证测试与配套寄存器

当前 [rvv_test.h](../../sw/tests/rvv_test.h) 在没有 `CHESHIRE_STUB_EX_EN_REG_OFFSET` 时，把多个 stub/MMU/debug offset 全部补成0；当前根 `regs/cheshire.h` 和 HJSON 没有这些字段。于是对“多个不同测试寄存器”的访问实际上都落到 SoC base+0，即 SCRATCH0。**能编译不表示 stub 硬件存在；这些测试不能直接作为当前标准 SoC 的 MMU 回归。**

公共流程是：初始化 UART/RVV→准备专用寄存器和异常状态→设置 vl/vstart、访存数据和模拟应答延迟→执行向量访存/CSR 指令→捕获异常并检查 mcause/mtval/vstart 或数据→清理测试寄存器→返回判据。`page_fault` 是注入异常场景，不等价于软件已建立完整 Sv39 页表。变体 `.c` 常只定义宏再 include `.body`，应把二者一起读。

下表逐个索引16个验证主源，名字中的 `var_lat` 指测试控制的应答延迟变化，`var_ex` 指异常控制的进一步变化；具体循环范围由 EEW/VLEN/ARA_NR_LANES/EXTENSIVE_TEST 等决定。

| 源文件 | 功能与程序流程 |
| --- | --- |
| [regfile_text_stub_regs.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/regfile_text_stub_regs.c) | 向四个专用stub寄存器写不同字符→读回逐项比较→清理；当前offset回退为0时不成立。 |
| [rvv_test_exceptions.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/rvv_test_exceptions.c) | 设置不同向量指令/CSR状态→执行可能异常的操作→核对异常标志与状态；先检查测试寄存器和trap约定。 |
| [rvv_test_mmu_stub_idx_ld_comprehensive_page_fault_var_lat_var_ex.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/rvv_test_mmu_stub_idx_ld_comprehensive_page_fault_var_lat_var_ex.c) | 索引load正文；异常控制2、延迟变化→按索引地址访存并核对异常/数据。 |
| [rvv_test_mmu_stub_unit_stride_comprehensive_page_fault_var_lat.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/rvv_test_mmu_stub_unit_stride_comprehensive_page_fault_var_lat.c) | 同一正文；异常控制1→加入page fault，检查恢复状态和数据。 |
| [rvv_test_mmu_stub_unit_stride_comprehensive_page_fault_var_lat_var_ex.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/rvv_test_mmu_stub_unit_stride_comprehensive_page_fault_var_lat_var_ex.c) | 同一正文；异常控制2→进一步变化异常注入条件。 |
| [rvv_test_mmu_stub_unit_stride_comprehensive_var_lat.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/rvv_test_mmu_stub_unit_stride_comprehensive_var_lat.c) | 共用连续load/store正文；异常控制0、延迟控制1、初值10→遍历vl/vstart与应答延迟。 |
| [rvv_test_mmu_stub_unit_stride_corner_cases.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/rvv_test_mmu_stub_unit_stride_corner_cases.c) | 对连续访存的边界场景设置数据和vl/vstart→执行load/store→检查异常/结果；不是DDR全范围测试。 |
| [rvv_test_mmu_stub_unit_stride_ld_comprehensive_page_fault_var_lat.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/rvv_test_mmu_stub_unit_stride_ld_comprehensive_page_fault_var_lat.c) | load专用正文；异常控制1→注入page fault并检查状态。 |
| [rvv_test_mmu_stub_unit_stride_ld_comprehensive_page_fault_var_lat_var_ex.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/rvv_test_mmu_stub_unit_stride_ld_comprehensive_page_fault_var_lat_var_ex.c) | load专用正文；异常控制2→变化异常条件并检查加载/异常行为。 |
| [rvv_test_mmu_stub_unit_stride_ld_comprehensive_var_lat.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/rvv_test_mmu_stub_unit_stride_ld_comprehensive_var_lat.c) | load专用正文；异常控制0→遍历vl/vstart与变化延迟，检查加载结果。 |
| [rvv_test_mmu_stub_unit_stride_reshuffle.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/rvv_test_mmu_stub_unit_stride_reshuffle.c) | 改变元素宽度/向量状态并连续访存→核对VRF数据重排与部分更新。 |
| [rvv_test_mmu_stub_unit_stride_st_reshuffle.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/rvv_test_mmu_stub_unit_stride_st_reshuffle.c) | 用不同源/目的元素宽度执行store→按byte检查vstart前保留区与有效写入区。 |
| [rvv_test_vstart_csrs.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/rvv_test_vstart_csrs.c) | 设置/读取vstart及向量CSR→执行CSR与向量操作→检查状态变化；仍使用本套测试辅助环境。 |
| [rvv_test_vstart_unit_stride_mmu_stub_page_fault_var_lat.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/rvv_test_vstart_unit_stride_mmu_stub_page_fault_var_lat.c) | vstart page-fault正文→检查异常发生后的部分进度/重启状态。 |
| [rvv_test_vstart_unit_stride_mmu_stub_page_fault_var_lat_mmu_req_gen.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/rvv_test_vstart_unit_stride_mmu_stub_page_fault_var_lat_mmu_req_gen.c) | 前一正文另启MMU请求生成器，间隔参数1→覆盖额外请求交互。 |
| [rvv_test_vstart_unit_stride_mmu_stub_var_lat.c](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/tests/rvv_test_vstart_unit_stride_mmu_stub_var_lat.c) | vstart连续访存正文；启用模拟虚拟访存、变化延迟→检查非零vstart处理。 |


<a id="11-从示例到团队可复用程序"></a>

## 11. 示例复用与验收要求

保留库初始化、寄存器来源和明确返回码，替换算法/数据；不要连带复制原测试的私有假设（固定manager编号、模拟stub寄存器、ret收束中断等）。

一个可验收用例至少记录：源程序与输入数据、CPU/SoC配置、工具链/flags、链接模式、加载方式、预期输出、失败判据、超时与日志。对矩阵/MLP等性能程序先确认数值正确，再报告周期；对MMIO/DMA程序先确认缓存/所有权与完成顺序，再比较吞吐。

已有示例是学习材料与测试起点，不是全部可直接复制为产品驱动的实现。本轮新增文档没有修复上述代码问题，也未改变旧测试的行为。
