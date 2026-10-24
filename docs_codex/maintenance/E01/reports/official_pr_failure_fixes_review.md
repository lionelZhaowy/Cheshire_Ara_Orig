# P1–P5 官方 PR 同步测试：问题处理与本地代码审查

记录日期：2026-10-23。完整运行记录见[官方维护评估](../planning/official_upstream_maintenance_assessment.md)。

2026-10-24 同步结果：重建参考工程R已按下述局部差异同步、完成48次验证并推送GitHub `5986ba02`；正式工程F随后同步并独立完成41次运行（38 PASS、原ROM限定告警1、预期负例2），39项共同用例与R一致，前后版本备份及恢复核对完成。详见[当前结果与回退](../planning/official_upstream_maintenance_assessment.md#reference-formal-sync-20261024)。下文代码位置与修复前后结果继续指原候选C；源码差异未改变，未进行综合。

**2026-10-23整理时状态（历史）：所有“通过”仅指隔离候选 C 的已执行仿真。修复未写回重建参考工程 `~/CheshireAraPULP`，也未同步正式工程 `~/CheshireAra`。没有进行综合、布局布线或板测。** 本次文档整理只读核查源码和历史结果，没有重新构建或运行测试。

服务器：`zhaowy24@172.16.0.243`。C 的路径：

```text
/home/zhaowy24/CheshireAra_maintenance/P1_P5_20261023_154743/candidate
```

当前 HEAD/通过标签：`p1-p5-pass = 5e0f973c090ee26ba18ce520bc61beebe584e929`。本次 SSH 核查 C 工作区干净，下面三份自行修复文件均与该标签一致。代码差异取自实际提交，行号按最终标签；所有源码路径均相对于 C。配置保持 WT D-cache、2 lanes、VLEN=2048。

## 1. 问题与解决方案

失败项数是检查失败次数，不是独立缺陷数量。P2/P3剩余问题来自旧代码；P4两个反例证明了所选官方修改在当前工程中的回归。

| 项目 | 问题与后果 | 解决方案及来源 | 隔离候选验证结果 |
| --- | --- | --- | --- |
| P1 | 存储队列绕回后指针相等，被误当作没有待完成存储；响应已返回却不能完成 | 官方Ara #481，改用计数判断 | 旧版4个B响应、0完成；修复后4完成、队列清空，数据及回归通过 |
| P2原目标 | 不同延迟浮点指令的结果写错目标寄存器 | 官方Ara #482，修正延迟分类和停顿判断 | 每lane观察到的15次错绑变为0；辅助检查仍有31错，需下面两项修复 |
| P2额外问题① | VL外mask尾位被计数，`vcpop`应为1却返回15 | 官方PR #469的6行局部修改；调查时PR未合并 | 同一835项测试31错→15错；mask补充124项32错→0 |
| P2额外问题② | 标量提取在共享队列仍忙时提前返回旧值，存储误入标量返回分支 | **本地修复**返回条件，见§3 | 同一835项剩余15错→0；标量补充483项通过，无原FIFO满断言 |
| P3原目标 | 0/0应报无效运算NV，却同时多报除零DZ | 官方MVP #18，只取消0/0分支的DZ | 同一177项20错→6错；剩余6项旧版也失败 |
| P3额外问题 | 未使用子单元的NV被汇总，错误mask索引使关闭的元素仍贡献异常 | **本地修复**子单元参与条件及mask索引，见§4 | 原177项剩余6错→0；补充753项28错→0 |
| P4 | 原版空突发/跨4 KiB；仅#191导致非对齐1024 B段漏尾字节；#192又覆盖相邻前段5字节 | 官方#191→#192，再加**本地首拍地址修正**，见§5 | 同六个ELF逐版比较，最终5195项及正常HelloWorld加载通过 |
| P5 | 1D重复次数为0，后端不搬运，但完成ID仍推进 | 官方iDMA #66的reps修改＋Cheshire #203删除HAL多余清零 | 旧版18 B全错、后端0次；修复后实际搬运18 B；2D→1D→2D及既有DMA回归通过 |

## 2. 官方局部修复来源（不重复列代码）

以下均为固定提交的选定修改，没有整包升级。官方修改之外的三处本地差异在后文列出。

| 项目 | 官方提交 | 实际采用范围 | 综合属性 |
| --- | --- | --- | --- |
| P1 / Ara #481 | [ae8297af0af38b52136826e591782042025725da](https://github.com/pulp-platform/ara/commit/ae8297af0af38b52136826e591782042025725da) | `hardware/src/vlsu/vstu.sv`存储队列计数判断 | 生产RTL，可综合逻辑；未跑综合 |
| P2 / Ara #482 | [a987112abed1339ecc9723555759be79427224bf](https://github.com/pulp-platform/ara/commit/a987112abed1339ecc9723555759be79427224bf) | `hardware/src/lane/vmfpu.sv`延迟分类和停顿判断 | 同上 |
| P2 / Ara #469局部 | [2ce6c2cc976b3dea5f52858e3b9cea8d4779e033](https://github.com/pulp-platform/ara/commit/2ce6c2cc976b3dea5f52858e3b9cea8d4779e033) | `hardware/src/masku/masku.sv`的VL尾位屏蔽；不含PR其余修改。2026-10-23实施调查时PR未合并 | 同上 |
| P3 / fpu_div_sqrt_mvp #18 | [2ec0514c1d538781a26df23fb8a947a60fcdccfc](https://github.com/pulp-platform/fpu_div_sqrt_mvp/commit/2ec0514c1d538781a26df23fb8a947a60fcdccfc) | `hdl/norm_div_sqrt_mvp.sv`中0/0分支1行；不含#16 | 同上 |
| P4 / Cheshire #191、#192 | [1b893efc6ee520be7d135a1adda397af94fa1c45](https://github.com/pulp-platform/cheshire/commit/1b893efc6ee520be7d135a1adda397af94fa1c45)、[ae5795dfdb177a8dc3ef2f43dcc7ceaa36fd9238](https://github.com/pulp-platform/cheshire/commit/ae5795dfdb177a8dc3ef2f43dcc7ceaa36fd9238) | `target/sim/src/vip_cheshire_soc.sv`的ELF加载循环/分段；两个官方中间版均不作为最终接受版本 | 仿真VIP，不纳入综合 |
| P5 / iDMA #66 | [92799c5fabcf2cd1f224f970bbb040b290d08fd5](https://github.com/pulp-platform/iDMA/commit/92799c5fabcf2cd1f224f970bbb040b290d08fd5) | `idma_reg.sv.tpl`及已有`idma_reg64_2d_top.sv`、`idma_reg32_3d_top.sv`、`idma_generated.sv`的reps赋值；没有重生成RTL | 模板不直接综合；派生RTL可综合，未跑综合；未启用3D仅静态核对 |
| P5 / Cheshire #203 | [bca9aadb7588de7046460daf91b39fe863a7a9d1](https://github.com/pulp-platform/cheshire/commit/bca9aadb7588de7046460daf91b39fe863a7a9d1) | `sw/include/dif/dma.h`删除1D清reps的1行，保留本地MMIO/CONF修正 | C软件，综合不适用；重编及运行通过 |

## 3. 自行修改一：P2标量返回条件

**目的：结果真正可以交给CPU时才回应，避免读到旧值；存储仍等待原地址响应。**

- 文件：`.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/ara_sequencer.sv`。
- 位置：`ara_sequencer`模块，`p_sequencer`组合过程的`WAIT`分支；最终第564–569行。原地址响应在554–562行，原ready表达式在575行，均未改。
- 本地提交：`6382e4214100c0e0de56dcd7190941cbaeebae0e`。

旧条件`!use_vd`范围过宽。VMVXS/VFMVFS是向量到标量的提取，必须等mask指令释放共享MaskB队列；VCPOP/VFIRST有专用结果通路，不能一起用“mask未结束”挡住，否则可能漏掉当拍完成响应。存储不应进入该分支。

```diff
@@ -561,8 +561,12 @@ module ara_sequencer import ara_pkg::*; import rvv_pkg::*; import cf_math_pkg::i
           ara_resp_o.fof_exception = addrgen_fof_exception_i;
         end
 
-        // Wait for the scalar result
-        if (!ara_req_i.use_vd && pe_scalar_resp_valid_i) begin
+        // MaskB is shared with MASKU: scalar moves must wait for its release.
+        // VCPOP/VFIRST return through a dedicated result path. Stores must only
+        // acknowledge address translation, even when they do not write vd.
+        if (pe_scalar_resp_valid_i &&
+            (((ara_req_i.op inside {VMVXS, VFMVFS}) && !running_mask_insn_q) ||
+             (ara_req_i.op inside {VCPOP, VFIRST}))) begin
           // Acknowledge the request
           state_d                = IDLE;
           ara_req_ready_o        = 1'b1;
```

**可综合性：可综合的组合控制逻辑。** 只增加指令枚举比较及布尔条件，没有增加寄存器、时钟、延时或仿真系统任务。已通过VCS编译/展开及仿真；未跑综合，实际工具支持、面积和时序未验收。

**验证：**同一835项测试在mask已修复的条件下15错→0；观察到的15次标量提前返回和37次存储误响应均消失。补充用例旧版FIFO满断言，修复版483项通过；实际覆盖VMVXS/VFMVFS各56个队列忙且结果有效的等待采样。mask、RVV、fmatmul、向量复制、非stub CSR及P1回归通过。未穷举所有标量/mask交叠情况。

## 4. 自行修改二：P3浮点子单元异常屏蔽

**目的：只汇总当前浮点格式实际使用且未被mask关闭的元素所产生的异常。**

- 文件：`.bender/git/checkouts/fpnew-ed006ec0a4178e29/src/fpnew_opgroup_multifmt_slice.sv`。
- 位置：`fpnew_opgroup_multifmt_slice`模块的`gen_pulp_divsqrt`分支；最终第392–398行新增mask计算，第414行修改实例端口连接。
- 本地提交：`d38bcf6925077593e6b766154d6fda205a532ed7`。

当前每个相关FPnew切片有4个内部子单元，FP32实际用2个，FP64用1个。其余子单元为保持同步仍启动，补零0/0产生的NV不应参与汇总。mask以最小16位元素为粒度，FP32第二个元素应取bit2，不能直接取bit1。这解释了正常除法多报NV以及mask关闭后仍报异常。

```diff
@@ -389,6 +389,13 @@ or on 16b inputs producing 32b outputs");
             .busy_o           ( lane_busy[lane]     )
           );
         end else begin : gen_pulp_divsqrt
+          // All subunits participate in PULP synchronization, including formats
+          // with fewer elements. Only real, unmasked elements may raise flags.
+          // SIMD mask bits are indexed at the narrowest supported granularity.
+          logic divsqrt_mask;
+          assign divsqrt_mask = LANE_FORMATS[dst_fmt_i]
+              ? simd_mask_i[(LANE * fpnew_pkg::fp_width(dst_fmt_i)) /
+                            (Width / NUM_SIMD_LANES)] : 1'b0;
           fpnew_divsqrt_multi #(
             .FpFmtConfig ( LANE_FORMATS         ),
             .NumPipeRegs ( NumPipeRegs          ),
@@ -404,7 +411,7 @@ or on 16b inputs producing 32b outputs");
             .op_i,
             .dst_fmt_i,
             .tag_i,
-            .mask_i           ( simd_mask_i[lane]   ),
+            .mask_i           ( divsqrt_mask        ),
             .aux_i            ( aux_data            ),
             .vectorial_op_i   ( vectorial_op        ), // synchronize only vectorial operations
             .in_valid_i       ( in_valid            ),
```

`LANE_FORMATS[dst_fmt_i]`判断本子单元是否参与当前格式；索引将元素编号换算成最小元素粒度的mask位。同步启动、握手、CPU CSR及Ara dispatcher保持原样；没有通过停止未用子单元来破坏同步。

**可综合性：可综合的组合选择/索引逻辑。** `LANE`和`Width/NUM_SIMD_LANES`是展开常量，当前后者为16；`fp_width`查固定格式编码表计算位宽。表达式中为常量除法，可由综合工具优化，没有新增时钟或状态。已通过VCS编译/展开及仿真；实际综合映射、面积和关键路径未验证。

**验证：**官方#18之后，同一177项6错→0；FP32/FP64除法和平方根、四元素全部16种mask组合的补充753项28错→0，覆盖应保留/应屏蔽的NV/DZ、结果及保护区。标量基础测试、RVV及fmatmul通过。FP16只有静态索引核对，未动态验证；其他配置不能直接沿用通过结论。

## 5. 自行修改三：P4相邻ELF段保护

**目的：保留首拍真实字节偏移，防止加载后一段时覆盖前一段。此处只修仿真加载器。**

- 文件：`target/sim/src/vip_cheshire_soc.sv`。
- 位置：`vip_cheshire_soc`模块的`slink_elf_preload`任务；最终第923–924行。
- 本地提交：`ac5d74a3f32d682fe6ce73186479e1d5a564b479`。

反例：A从`0x10002000`开始、长13 B；B从`0x1000200d`开始、长9 B。原版及仅#191均通过；#192把B地址向下对齐到`0x10002008`，首拍WSTRB=`ff`，前置填充零覆盖A末5字节。现有`slink_write_beats`本来能根据非对齐地址屏蔽首拍前导字节，因此只需保留`addr_cur`。

```diff
@@ -920,8 +920,8 @@ module vip_cheshire_soc import cheshire_pkg::*; #(
               beat[8*e +: 8] = bf[sec_offs + b + e];
           beats.push_back(beat);
         end
-        // Address must be beat‑aligned for slink_write_beats
-        slink_write_beats(addr_cur - bus_offs, AxiStrbBits, beats);
+        // Keep the original offset so slink_write_beats masks the leading bytes.
+        slink_write_beats(addr_cur, AxiStrbBits, beats);
       end
     end
     void'(get_entry(entry));
```

**可综合性：不适用，这是不可作为芯片逻辑综合的仿真VIP任务。** 使用动态队列、仿真驱动及ELF读取，仅参与测试；没有改生产AXI路径、硬件接口或Boot ROM。

**验证：**同六个ELF逐版比较，覆盖1024/2048 B、非整倍长度、非拍对齐、跨4 KiB及相邻多段；最终5195项全部通过，真实SLINK观察缺字节/错字节/协议检查错误均为0，正常HelloWorld加载通过。#191漏尾字节及纯#192覆盖5字节的失败证据保留。未穷举所有ELF布局。

## 6. 测试配套及其自身错误

以下用于复现和观测，不是额外的芯片修复。自编测试也保存在同一标签，可按位置审查；不将测试观察器加入生产综合清单。

| 内容 | C内位置 | 用途及结果 |
| --- | --- | --- |
| P2用例 | `sw/tests/p2_vcpop_boundaries.c`（main第120行）、`sw/tests/p2_scalar_overlap.c`（main第96行）、`sw/tests/p2_vmfpu_order.c` | VL边界、标量重叠、原浮点排序；124/483/835项通过 |
| P3用例 | `sw/tests/p3_div_flags.c`（main第209行） | 原177项/扩充753项；清标志、等结果依赖，再检查全部五个标志 |
| P4用例/布局 | `sw/tests/p4_preload_bytes.c`（main第113行）、`sw/link/p4_single.ld`、`sw/link/p4_multi.ld` | 真实ELF加载后逐字节检查；六例最终通过 |
| 默认关闭的只读TB诊断 | `target/sim/src/tb_cheshire_soc.sv`：P2开关第230/400/448行，P3第509行，P4第630行 | P3最初因VCS不接受所用层级参数引用而编译失败；改用本配置常量边界并检查实际内部单元数后通过，生产参数未改 |
| P1/P5配套 | 同TB：P1开关第96行、P5第765行；`sw/tests/p1_vstu_wrap.c`、`sw/tests/p5_dma_1d.spm.c` | P1仅开启时门控真实内部B通道触发绕回；P5只读观察真实搬运。均非stub，定向通过 |

P4测试首次漏包含`printf.h`，链接拉入newlib导致超出预留区，修正测试头文件后解决；另一次预建输出目录被入口拒绝，改用尚不存在的新输出目录。这些是测试编写/调用错误，不是官方PR引入的设计缺陷。实际前后比较使用修正后的相同输入，没有降低检查条件。

## 7. 验证结论与审查入口

历史验证使用候选内源码、库及新输出目录，串行、默认600秒、普通运行无波形。联合检查目标结果、仿真器结果、入口返回、完成标志及断言，不能只看`simv=0`。

最终累计版本的HelloWorld、非stub CSR、向量复制、RVV 5976项、访存原子572项及fmatmul通过；同最终版本三项DMA回归通过。ROM/SPI仅按既定padding告警限定接受功能，入口仍为2，没有改记为无告警PASS。共享LLC已知失败、FS边界及libgcc限制保持。

在服务器C中只读审查三项本地修复：

```bash
cd /home/zhaowy24/CheshireAra_maintenance/P1_P5_20261023_154743/candidate
git show 6382e4214100c0e0de56dcd7190941cbaeebae0e -- .bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/ara_sequencer.sv
git show d38bcf6925077593e6b766154d6fda205a532ed7 -- .bender/git/checkouts/fpnew-ed006ec0a4178e29/src/fpnew_opgroup_multifmt_slice.sv
git show ac5d74a3f32d682fe6ce73186479e1d5a564b479 -- target/sim/src/vip_cheshire_soc.sv
```

逐项提交、通过标签、失败源码/日志，以及目录外和本地双份累计bundle均已保留。恢复方法和运行目录见[维护评估的恢复章节](../planning/official_upstream_maintenance_assessment.md#恢复方法与阶段c边界)。本地备份：`.e01_backups/P1_P5_20261023_154743/`；服务器备份：C的同级`backups/`。

**已确认的是固定配置隔离候选中列出的仿真通过；重建参考工程/正式工程的写回与复验、综合及ASIC验收均未完成。**
