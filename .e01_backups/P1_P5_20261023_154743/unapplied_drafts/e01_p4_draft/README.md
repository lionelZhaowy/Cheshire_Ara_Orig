# P4 最小真实 ELF 输入草稿

2026-10-23：仅在本地 `/tmp/e01_p4_draft` 准备。未写服务器、未编译/链接、未生成 ELF、未构建 RTL、未运行测试。以下是交主 Agent 的阶段 B 草稿，不能记为已验证输入。P2/P3 草稿不变。

## 已只读核实的入口

- 当前 `src/tb/src/elfloader.cpp` 的 `load_elf` 按 **program header 顺序** 遍历，不按 ELF section 表重新排序。`PT_LOAD && p_memsz!=0` 后，只有 `p_filesz!=0` 才加入 `sections`；VIP 得到的地址是 `p_paddr`，长度是 `p_memsz`。只复制 `p_filesz` 实际文件字节；文件尾之外的 NOBITS 并非 loader 主动清零的证明。
- 当前 `slink_elf_preload` 是 1024 B burst、8 B beat，并仍有 `i<=sec_len`。`slink_write_beats` 检测到空队列会在发 AW 前 `$fatal("[SLINK] Zero-length write requested!")`。AXI `AWLEN=0` 是 **1 beat**，不能把它当空写错误。
- 第一拍的 WSTRB 从未对齐 AW 地址对应字节开始，前面的字节不写；尾拍超出 payload 的位置补零并写入。后续段可能覆盖前段的尾部 padding，所以不能承诺任意邻区 guard 不变。
- 当前 `sw/link/spm.ld` 包含原 `common.ldh`，后者给软件 0x10000000 起的64 KiB链接区；物理 LLC SPM 当前为128 KiB。原 Boot ROM 从 LLC_SIZE 把栈调整到 SPM 顶部，已有记录为0x1001fff8；应用 CRT 默认继承传入 SP，并只清自己的 BSS。草稿不修改 CRT/Boot ROM 或栈初始化。

## 六个有目的的输入

| P4_CASE | 数据 PT_LOAD 地址 | p_filesz=p_memsz | 用途 | 链接布局 |
| --- | --- | --- | --- | --- |
| 1 | 0x10000000 | 1024 | 一次整 burst 后的空尾写 | p4_single.ld |
| 2 | 0x10000000 | 2048 | 两次整 burst 后的空尾写 | p4_single.ld |
| 3 | 0x10000000 | 1031 | 非1024倍、非8倍尾长；正常对照 | p4_single.ld |
| 4 | 0x10000001 | 1024 | #191 单独 `<` 的截尾反例，缺失最后有效字节位于0x10000400 | p4_single.ld |
| 5 | 0x10000ff8 | 16 | 8 B对齐但单 burst 跨4 KiB；修复后应是两个1-beat burst | p4_single.ld |
| 6 | A=0x10002000；B=0x1000200d | A=13；B=9 | 两个逻辑范围相邻、不重叠的段，均有尾字节；第一段尾拍与第二段首拍共用一个beat | p4_multi.ld |

六个 ELF 分开保存，使旧版 case1/2 的预加载 fatal 不掩盖其他输入。三个 VIP 版本复用这同一批 ELF，不为某个版本重编数据或改变输入。

`p4_preload_bytes.c` 通过顶层 GNU assembler `.rept/.byte` 产生 `.p4_a/.p4_b` **真实 PROGBITS 文件内容**，不是 C 在启动后填入。A每字节为 `1+((37*i+17)%251)`，B为 `1+((37*i+101)%251)`，全部非零、随位置变化。C 使用 volatile 字节读，经当前 SPM `+0x04000000` 无缓存别名检查每个加载字节，未向 payload 写入。C 编译只选择 `-DP4_CASE=N`；所需绝对地址/长度同时作为汇编绝对符号交给链接脚本，不需要另一份配置表或输入生成器。

共用程序从0x10004000开始，和低地址测试数据独立 PT_LOAD；继承现有 HelloWorld CRT、库和 UART 初始化。脚本限制程序到0x1000c000以下，保留其上的地址区给栈。应用段末尾加入 PROGBITS 字节，使其期望总长度 `%8==1`，避免应用段自身触发1024倍数错误。六个输入均不另加空 PT_LOAD；本轮空 burst 来自旧循环处理1024整倍长段的多余迭代。loader跳过零长度PT_LOAD只保留已有静态结论，不为它增加测试段。

**上述 PHDR 形状是链接意图，尚未经过链接证明。** 尤其未对齐 payload 的 p_offset/p_vaddr，以及孤立 ALLOC section 的归属必须按下节实际检查；不能用 section 长度替代 PT_LOAD 长度。

## 纳入现有编译命令的最小改动

不新增 Makefile/自动生成平台。沿主 Agent 已在隔离参考副本使用的 HelloWorld 软件编译/链接命令，保留同一工具链、ISA/ABI、include、原 CRT0 和当前 `libcheshire.a`。六次只改变：

1. 源文件换成本目录 `p4_preload_bytes.c`，增加 `-DP4_CASE=1` 至 `6`；建议沿现有定向测试保留 `-fno-tree-vectorize -fno-strict-aliasing`，本用例不需要 RVV。
2. 原 `-T.../spm.ld` **替换** 为本目录 `p4_single.ld`（1–5）或 `p4_multi.ld`（6），不要同时传两个主布局。保留 `-Wl,-L<隔离参考副本的 sw/link>`，让 `INCLUDE common.ldh` 仍解析当前原件对应副本。
3. 输出到该轮新目录的 `p4_01.elf` 至 `p4_06.elf`，另存各自 map。单独编译、再链接的入口在编译这份 C 时传 `P4_CASE`；一条命令编译链接的入口在同一命令传它。保留原有 CRT 的显式提取方式，不能因更换源文件漏 `_start`。

这是一次性输入生成说明，未执行。无需 objcopy 改写 ELF、改 ELF program headers、手改测试地址或重生成 ROM。若链接器对 top-level asm 或布局诊断，先记录并只修测试布局，不能在输入不符合下述检查时开始宣称复现结果。

## 链接后、运行前的只读检查

对每个 ELF 使用既有 `readelf -hW -lW -SW`、map 和必要的 `objdump -s -j .p4_a`；case6再读 `.p4_b`。保存六个 ELF 哈希。至少确认：

- ELF 为当前 RISC-V 架构/ABI，入口是原 `_start` 在0x10004000；程序头表在文件内。所有非空 PT_LOAD 的 `p_paddr==p_vaddr`；按 vaddr 升序；`p_filesz<=p_memsz`，文件范围有效且 `p_offset`/`p_vaddr` 满足 `p_align` 同余。
- 数据 PT_LOAD 精确等于表中地址与长度，不含 ELF headers、对齐前缀、程序代码、BSS或额外 section。尤其 case4 是 **0x10000001/1024**，case5是 **0x10000ff8/16**，case6两个段的范围不重叠且分别为13/9 B。只看到 `.p4_a` 长度正确不足以开始测试。
- 1–5各只有数据/app两个预期 PT_LOAD，6有A/B/app三个；没有人为增加的空段。发现额外段先检查归属，不把纯BSS或孤立section混入已定义边界。
- app 段从0x10004000开始，所有实际加载内容位于0x1000c000以下，最终 **p_memsz 非1024倍**。预期最后PROGBITS使 filesz=memsz；若不是，应记录并调整测试布局，避免把未装载 NOBITS 当本候选缺陷。检查 section-to-segment mapping，防止脚本后出现的 orphan ALLOC 节绕过位置 ASSERT、改变 memsz 或进入测试数据段。
- payload 对应文件中的每一字节与固定公式一致，case4最后字节应为0xdb。main没有存 payload 的代码；`.bss` 位于 app 区，不会在 CRT 中清掉测试数据。实际 SP应在保留的高地址区；草稿main会检查0x1000c000≤SP<0x10020000。

## 三个版本的判定

| 输入 | 原 VIP 的静态预期 | 仅 #191 的静态预期 | #191后再采用 #192 的要求 |
| --- | --- | --- | --- |
| 1、2 | 实发完数据后因空队列fatal，可能尚未装载app | 消除空写，正确启动并读回全部数据 | 同样通过 |
| 3 | 正常对照 | 正常对照 | 完整数据及最终尾部补零通过 |
| 4 | 最后一轮补最后字节 | 少装0x10000400的最后字节；可能导致数据检查或未知值诊断失败 | 1024字节全正确，不能只看没有空写 |
| 5 | 尝试一个跨页burst；是否实际报错须看协议证据 | 与原版相同 | 两个合法1-beat burst，完整16字节 |
| 6 | 检查当前相邻段行为 | 同样检查 | A/B全部字节正确，最后B之后的定义padding为零 |

这些是源码推导，不是预定测试结论。case4未装载字节的初值可能碰巧等于期望，因此还须保留实际写入范围；不能只凭“C没有失败”抹去缺失写。case5即使旧版数据读回正确，也不能把跨页AXI请求视为合法。

若使用已有 SLINK 调试文本或在隔离TB中增加必要的临时文本观察，只记录预加载相关 AW/W/B 和 section边界，不改生产SLINK接口、不默认导波形。对每次AW握手记录 addr/size/len；beat数为 `AWLEN+1`。检查4KiB边界时，对未对齐首拍使用 `aligned_start=addr&~((1<<AWSIZE)-1)`，最后可能写字节为 `aligned_start+(AWLEN+1)*(1<<AWSIZE)-1`，与首地址应同页；不要用包含未对齐偏移的过宽公式误报。结合WSTRB记录真正写入的payload范围。

主 Agent 串行、每例默认600秒，R显式使用 `BOOTMODE=0/PRELMODE=1` 的实际SLINK ELF入口；最终以当前入口的目标返回值、仿真器结果和错误分类共同判定。C成功打印 `P4_DONE case=N c=... e=0` 并返回0，失败返回44；原版加载fatal时不会有该标记，是预加载失败，不伪装成C已运行。

C仍核对全部目标字节并累计错误，UART只在末尾输出首条 `P4_FAIL g/i/v/e`（若有）和一条DONE；删除START和单独的PRECONDITION提示。前置检查失败时group=0，跳过危险读回，统一DONE后返回44；group=1/2是A/B数据，group=3是最后一段的定义padding。详细布局由运行前readelf保存，不在UART重复输出。

case6中 A结束于0x1000200d，A尾拍的补零可能先覆盖后续B位置，随后按升序加载B恢复其真实数据；最终只检查A/B完整内容，以及最后B结束0x10002016至拍末0x10002018的两字节补零。其他任意邻区/leading guard没有保持不变的契约，不据此要求重构VIP strobes。

P4a 是已授权逐步对照的中间版本；case4若复现截尾，记录其不能独立采用，再按已授权范围继续P4b。最终P4b出现新的相邻段覆盖、布局或协议问题时停止，保留输入和日志，不扩为SLINK生产总线改造。结束后再由主 Agent 运行计划内适用既有回归；原ROM padding限定告警、FS/libgcc及LLC既有结论不随本测试改写。

## 默认关闭的实际 AXI 观察片段

`p4_slink_observe.svh` 放入隔离候选 TB 的 `tb_cheshire_soc` 模块内部、`endmodule` 前，可直接粘贴或用候选目录内的include。默认不开启；P4运行时额外传 **`+P4_SLINK_OBSERVE +P4_CASE=N`**，N必须与该ELF编译的P4_CASE相同。这不是新的仿真入口，原BOOTMODE/PRELMODE/BINARY和现行结果检查保持。

已通过SSH只读核实真实层级：`tb_cheshire_soc.fix.vip.slink_mst_vip_dv` 是 `AXI_BUS_DV`，具有 `aw_addr/aw_len/aw_size/aw_burst/aw_valid/aw_ready`、`w_data/w_strb/w_last/w_valid/w_ready`、`b_resp/b_valid/b_ready`；时钟为 `fix.vip.clk`。片段只在实际握手采样，不force、不驱动接口、不调用DPI、不改传输或插入延迟。当前VIP函数严格send_aw→发送所有W→等待B，片段因此只保存一个在途写，不伪装成通用AXI检查器。

- 每个AW输出地址、AWLEN、beat数、AWSIZE和burst，区分DATA/APP/OTHER；核对正确的4KiB边界、完整W握手数、WLAST和BRESP。每burst仅打印首/末W内容及B摘要，均是主机文本，不增加目标UART输出。
- 对数据保留区记录所有真实WSTRB为1的字节，保存其**最后一次写入值**。结束时检查全部固定payload及最后段padding；因此#191漏写最后字节即使SPM旧值碰巧相同，也会被记为missing。该观察证明VIP发送的数据和地址；C经SPM实际读回仍不可省略。
- case6不在A段结束时把临时零padding与B期望值比较；待所有段结束才检查最终A/B。现有 `[SLINK] Preloading section at ...` 文本给出段顺序；A/B共用一个beat，不能只按AW所在beat判断所属段。
- DATA地址低于0x10003000，APP从0x10004000开始；低区与app之间有明确间隔。**app PT_LOAD跨页不等于它的burst跨页**：readelf确认app首地址0x10004000且长度非1024倍后，旧VIP的1024步长只在页内0/0x400/0x800/0xc00开始；满burst至页尾，末burst更短，本应不触发P4两类错误。app协议错误须单列，不能用它替代目标data case的复现。
- `[P4_OBS_DONE]` 给出AW/W/B数量、data/app burst数、missing/bad/errors及launch。最后的launch来自真实SCRATCH2写2及OKAY响应。有效修复至少要求errors=missing=bad=0、launch=1，且有正确的C DONE/目标退出/现行日志检查；该摘要不是单独PASS。观测错误只记录，不主动中止旧版，便于保存对照；现行检查必须把非零errors作为失败证据。若仿真被外部超时终止而没有final摘要，结论是观察未完成。

**空队列没有AW握手，纯总线观察无法看到它。** 保留当前VIP真实 `beats.size()==0` 的fatal作为空突发证据；AWLEN=0仍是合法1 beat，片段不据此虚构empty计数。若主Agent需要统一观察前缀，可仅在隔离VIP的 `slink_write_beats` 原空队列判断之前加入以下只读标记，并在三个版本保持一致；原fatal和控制流不能改：

```systemverilog
if ($test$plusargs("P4_SLINK_OBSERVE") && beats.size()==0)
  $display("[P4_OBS_EMPTY] addr=%h size=%0d queued_beats=0", addr, size);
```

原版case1/2可能显示payload全部已写、errors=0但launch=0，然后因真实空队列fatal结束；这仍是预加载失败。该标记只读取真实函数参数，不构造空段、替换loader或强制总线。

## 静态评审

另一本地子 Agent 已只读快评 C、GNU assembler和链接布局，未发现明确语法错误；同时明确：未对齐PT_LOAD范围、orphan ALLOC和最终app memsz都必须链接后核对。随后按主Agent要求移除了空PHDR并精简UART。观察片段仍为未编译草稿；真实层级已经只读核实，不等于VCS语法及动态行为已验证。
