# P1–P7 修复：官方 PR 来源、问题处理与本地代码审查

**2026-10-26 [P7已同步正式工程并验证，参考工程已提交GitHub](#p7-reference-formal-sync-20261026)：F自身重建RTL及14 ELF后，17次串行仿真全部PASS；P7共68组/13416项0错，归档原LLVM向量及两标量均未重编即465/0、复制22字节0错，12回归通过。F保留既有布局，维护目标29→31，日常7/Ara11保持；其余1046原输入及R全部4394输入内容/权限保持。随后仅R四份P7源码提交并推送`4e30feec`，两处诊断修改保留；两地前后恢复/归档核对完成。默认仍GCC13.2，LLVM构建规则尚未重新适配、迁移验收未完成；未综合/板测/公开上游PR。下方仅R、未提交及F未同步均为前阶段历史。**

**2026-10-26 P7已在R修复并通过验收：**原定重排条件/目的EMUL分类之外，按用户继续修复授权追加多寄存器重排等待及VID无用输出本地退休，2 RTL共32增4删。最终68组/13416项0错，原LLVM失败ELF未重编即465/0、复制22字节0错，两标量及12回归全部PASS。共22次实际运行，旧版及中间4次TARGET_FAIL如实保留；4318其他跟踪输入和原两处诊断修改保持，两地备份及实际恢复检查通过。R保留未提交修复，F未同步、LLVM迁移未恢复，无提交推送。完整分类、逐项结果、覆盖和回退见[13.5](#p7-emul-local-fix-20261025)。下段及13.4为前轮失败回退历史。

**2026-10-25 P7候选未通过，R已回退：**固定[Ara #483](https://github.com/pulp-platform/ara/pull/483)的7增1删候选成功编译，初版同ELF两次诊断显示加法组合改善，但第51组e32/m2 VMACC仍从索引64出错；当前OPMVV保留EMUL=1的源码链及字节模型精确解释首错，超出本次固定补丁范围。初版非零vstart算术控制还触及当前实现支持边界，用户已批准替换为部分VL乘加；修订版构建后未继续仿真。17项修订验收均未执行，原LLVM失败ELF及其余回归未新运行，P7未验收。R的4321项原输入、原Git状态/差异已恢复，F未写、LLVM迁移未恢复、未提交推送；详见[第13.4节](#p7-implementation-result-20261025)。

**2026-10-25 P6已提交并同步两工程：**R的6份P6文件已单独提交并推送[GitHub `cb20a03c`](https://github.com/lionelZhaowy/CheshireAraPULP/commit/cb20a03c063d208d17eef024a1f6491152d509e8)，远端main已读回确认。F按自身目录和Make组织同步，独立重建后11次仿真全部PASS；五个P6目标508组/38452项、0错，P2三项及vector/RVV/fmatmul复跑通过。当前修改范围见[统一总表](#formal-p1-p5-files)，本次具体结果见[第12节](#p6-reference-formal-sync-20261025)。下面第9–11节“仅R/未提交/F未同步”是同步前的阶段记录；本轮未综合、板测或发布上游PR。

**2026-10-25 P6实施完成（仅R）：**已将3份RTL修改写入参考工程 `CheshireAraPULP`，新增2份C测试及5个显式Make目标。采用#475/#480相关局部，并自行修正MASKU数据接收归属和compress结束逻辑。本轮17次串行仿真为16 PASS＋1预期旧版停滞；其中生产源码重建后的8次全部PASS，5个P6软件目标合计508组/38452项检查、0错。具体文件见[第1节](#formal-p1-p5-files)，代码、结果与回退见[第11节](#p6-fix-20261025)。F未同步，未提交或推送。下面第9、10节保留此前测试/候选阶段的历史状态，以本节及第11节为当前结论。

**2026-10-25 P6候选检查：**后续授权的21次仿真确认#475、#469局部和#480可分别复用部分修复，但组合仍有历史数据归属错误及compress全不选/跨字停滞。仅修改独立源码副本，R/F生产源码保持；P6未验收。见[第10节](#p6-candidate-check-20261025)。#479按用户决定暂不继续处理。

**2026-10-25 后续授权的 R 定向测试：**已在 `CheshireAraPULP` 实际复现 Ara #475；#479 的两组各120次比较序列通过，但未进入冲突接收窗口。另复现 #450 所述 compress 终止停滞，并保留一例延迟标量提取错误值，见[第9节](#ara-maskb-tests-20261025)。仅新增测试与观察代码，未应用RTL修复、修改F或发布PR。下方“本轮未重新测试”属于此前独立复审记录。

记录日期：2026-10-23。完整运行记录见[官方维护评估](../planning/official_upstream_maintenance_assessment.md)。

**2026-10-25正式工程独立复审：**已只读核对F当前P2/P3生产源码、上下游握手、实际历史补丁及F五项原始测试日志。在所查路径内未确认新的RTL缺陷；本地修改与原错误原因相符。明确保留一项覆盖缺口：P3向量测试固定VL=4，尚未证明非整拍尾部异常屏蔽。见[本次逻辑与证据](#formal-review-20261025)。本轮未重新测试或综合，未改服务器代码。

阅读顺序：第1节看P1–P6文件及修复来源总表；第2节查P1–P5官方SHA；第3–5节看原三处自行修改；第8节看P2/P3剩余边界；第11节看P6初次R实现与验证，第12节看R提交及F同步验证。

2026-10-24 同步结果：重建参考工程R已按下述局部差异同步、完成48次验证并推送GitHub `5986ba02`；正式工程F随后同步并独立完成41次运行（38 PASS、原ROM限定告警1、预期负例2），39项共同用例与R一致，前后版本备份及恢复核对完成。详见[当前结果与回退](../planning/official_upstream_maintenance_assessment.md#reference-formal-sync-20261024)。下文未另标F的代码位置与修复前后结果继续指原候选C；源码差异未改变，未进行综合。

**2026-10-23整理时状态（历史）：所有“通过”仅指隔离候选 C 的已执行仿真。修复未写回重建参考工程 `~/CheshireAraPULP`，也未同步正式工程 `~/CheshireAra`。没有进行综合、布局布线或板测。** 本次文档整理只读核查源码和历史结果，没有重新构建或运行测试。

服务器：`zhaowy24@172.16.0.243`。C 的路径：

```text
/home/zhaowy24/CheshireAra_maintenance/P1_P5_20261023_154743/candidate
```

当前 HEAD/通过标签：`p1-p5-pass = 5e0f973c090ee26ba18ce520bc61beebe584e929`。本次 SSH 核查 C 工作区干净，下面三份自行修复文件均与该标签一致。代码差异取自实际提交，行号按最终标签；未另标F的源码路径均相对于 C。配置保持 WT D-cache、2 lanes、VLEN=2048。

<a id="formal-p1-p5-files"></a>

## 1. 修复文件与来源总表

2026-10-25更新。P1、P2至P7及后续P编号统一追加到本表，不按修复批次另建修改表。目前保留P1–P5的10份修复文件，以及P6的3份RTL、2份测试和1份Make入口；P7第二次实施已在R修复并通过最终17个正例，原LLVM/两标量/12回归均PASS；前轮失败回退保留在13.4，第二次实施详见13.5。P1–P5的配套测试、入口及来源记录未在此穷举。

文件路径统一相对正式工程F `/home/zhaowy24/CheshireAra`，同一修复也已保存在参考工程R。P1–P5历史复验见[同步记录](../planning/official_upstream_maintenance_assessment.md#reference-formal-sync-20261024)；P6已按[两工程同步规范](../planning/server_reference_rebuild_guide.md#cross-project-sync-rules)映射同步并完成F独立验证，详见[第12节](#p6-reference-formal-sync-20261025)。各行“已实施工程”记录当前范围，后续P编号仍追加本表。

“官方PR局部”表示只采用固定SHA的相关修改，不表示整包升级或整PR合入。P1–P5完整来源见[第2节](#2-官方局部修复来源不重复列代码)，P6来源、代码及验证见[第11节](#p6-fix-20261025)和[R初次差异](../../../../.e01_backups/p6_fix_20261025/production_changes.patch)及[F同步差异](../../../../.e01_backups/p6_sync_20261025_sf0kdpzo/formal_changes.patch)。Ara #469的未合并状态为此前2026-10-25查询快照，采用范围以固定SHA和实际差异为准。

| 修复编号 | 修改文件 | 修复来源 | 问题与修复作用 | 已实施工程 |
| --- | --- | --- | --- | --- |
| P1 | `src/cheshire_soc/ara/hardware/src/vlsu/vstu.sv`<br>生产RTL | [Ara #481](https://github.com/pulp-platform/ara/pull/481)，局部回移 | 改用计数判断待完成存储，避免队列绕回后指针相等被误判为空，导致存储无法完成。 | R、F已验证 |
| P2 | `src/cheshire_soc/ara/hardware/src/lane/vmfpu.sv`<br>生产RTL | [Ara #482](https://github.com/pulp-platform/ara/pull/482)，局部回移 | 补全浮点延迟分类并修正停顿判断时机，避免短延迟结果抢先写入错误目标寄存器。 | R、F已验证 |
| P2 | `src/cheshire_soc/ara/hardware/src/masku/masku.sv`<br>生产RTL | [Ara #469](https://github.com/pulp-platform/ara/pull/469)，仅VL尾位屏蔽局部；PR未合并 | 排除VL之外的mask尾位，修正有效范围内的计数/查找；不是采用该PR的全部mask修复。 | R、F已验证 |
| P2 | `src/cheshire_soc/ara/hardware/src/ara_sequencer.sv`<br>生产RTL | **本地修复**，见[第3节](#local-p2-scalar) | 标量提取等待共享队列释放，避免返回旧值；保留VCPOP/VFIRST专用返回，排除存储误入标量响应分支。 | R、F已验证 |
| P3 | `src/cheshire_soc/fpu_div_sqrt_mvp/hdl/norm_div_sqrt_mvp.sv`<br>生产RTL | [fpu_div_sqrt_mvp #18](https://github.com/pulp-platform/fpu_div_sqrt_mvp/pull/18)，局部回移 | 取消0/0错误附带的DZ（除零）标志，保留应有的NV（无效运算）标志。 | R、F已验证 |
| P3 | `src/cheshire_soc/fpnew/src/fpnew_opgroup_multifmt_slice.sv`<br>生产RTL | **本地修复**，见[第4节](#local-p3-mask) | 修正除法/平方根的SIMD mask索引，屏蔽当前格式未使用或被mask关闭元素的异常贡献；保持子单元同步启动。 | R、F已验证 |
| P4 | `src/tb/src/vip_cheshire_soc.sv`<br>仿真VIP | [Cheshire #191](https://github.com/pulp-platform/cheshire/pull/191)、[#192](https://github.com/pulp-platform/cheshire/pull/192)＋**本地修复**，见[第5节](#local-p4-preload) | 官方修改处理空突发、4 KiB跨页及非对齐装载；本地修正首拍地址，防止覆盖相邻前段。仅影响ELF预加载，不改变芯片RTL。 | R、F已验证 |
| P5 | `src/cheshire_soc/idma/target/rtl/idma_generated.sv`<br>派生生产RTL | [iDMA #66](https://github.com/pulp-platform/iDMA/pull/66)，仅重复次数局部 | 将关闭相应ND维度时的重复次数设为1，避免一维传输不搬运数据却推进完成ID。 | R、F已验证 |
| P5 | `provenance/generation/idma/src/frontend/reg/tpl/idma_reg.sv.tpl`<br>生成模板，不直接综合 | [iDMA #66](https://github.com/pulp-platform/iDMA/pull/66)，与派生RTL同一局部修复 | 同步重复次数修正，保持模板与已有派生RTL一致，避免以后生成时恢复旧错误；本次未全量重生成。 | R、F已验证 |
| P5 | `sw/include/dif/dma.h`<br>软件HAL | [Cheshire #203](https://github.com/pulp-platform/cheshire/pull/203)，仅一维HAL对应局部 | 删除一维搬运中多余的重复次数寄存器清零，配合RTL归一化处理；保留既有32位MMIO指针及CONF修正。 | R、F已验证 |
| P6 | `src/cheshire_soc/ara/hardware/src/lane/lane_sequencer.sv`<br>生产RTL | [Ara #475](https://github.com/pulp-platform/ara/pull/475)相关局部 | 记录仍在运行的gather/compress；它们释放共享MaskB前，阻止标量提取抢先进入，解除VL=1循环等待。 | R、F已验证 |
| P6 | `src/cheshire_soc/ara/hardware/src/masku/masku.sv`<br>生产RTL | [Ara #480](https://github.com/pulp-platform/ara/pull/480)相关局部＋本地compress修复 | 广播按valid/ready真实握手逐lane记忆，全部接收后才出队；compress保留最近选中索引、扫描完再发最终标记，全不选直接完成，修正末尾未选及跨选择字停滞；连接下面的数据归属有效信号。 | R、F已验证 |
| P6 | `src/cheshire_soc/ara/hardware/src/masku/masku_operands.sv`<br>生产RTL | **本地修复** | 新增当前issue有效输入；仅MASKU有效指令且确实使用该通路时，允许vd缓冲接收及返回ready，避免空闲MASKU把CPU标量数据留给下一条gather。 | R、F已验证 |
| P6 | `sw/tests/regressions/p6_maskb.c`（新增） | 复用此前v4定向测试，执行及判据保持 | KIND=0/1/2/3分别检查延迟提取、即时整数提取、FP32提取、全选compress后提取；各120组/7800项。 | R、F已验证 |
| P6 | `sw/tests/regressions/p6_compress.c`（新增） | 针对已确认结束缺口补充 | e8/m1检查VL=0/1/2/128/130/256，全不选、首/末选、127/128跨字、交替和全选；恢复VLMAX存出，检查选中结果及整个目的寄存器尾部保持。28组/7252项。 | R、F已验证 |
| P6 | `sw/Makefile` | 复用现有`direct_test`宏 | 将5个目标合入F已有`regressions`，维护项24→29；日常7项、可选Ara 11项保持。R继续使用原`p6-regressions`入口。 | R、F已验证 |
| P7 | `src/cheshire_soc/ara/hardware/src/ara_dispatcher.sv` | [Ara #483](https://github.com/pulp-platform/ara/pull/483)固定`6b664a2c…`局部＋本地分类/等待；R提交`4e30feec` | 25增2删；旧目的仍作为源时重排、OPMVV目的EMUL分类、实际多寄存器重排完成等待；邻近in_lane_op及重排计数结构保持。 | R、F均通过；F独立17次PASS，见[13.6](#p7-reference-formal-sync-20261026) |
| P7 | `src/cheshire_soc/ara/hardware/src/lane/valu.sv` | 本地VID无用输出退休；R提交`4e30feec` | 7增2删；阻止VID零载荷留在mask spill，保留原队列计数、指针及done；非VID逻辑等价。 | R、F均通过，VID→compress有效95项及保留尾部33项正确 |
| P7 | F `sw/tests/regressions/p7_reshuffle.c`、`sw/Makefile`；R `sw/tests/p7_reshuffle.c`及原Make | 同一569行C＋既有direct_test；R提交`4e30feec` | F Make仅加4行，两个目标加入现有regressions；7/31/11构建组。R保留显式P7目标及默认all/P6。 | F重建54＋14组、13416项0错；RVV序列196/100条与R编码一致 |

**验证边界：**生产RTL属于可综合写法，但尚未实际综合；VIP不参与芯片综合，模板不直接综合，HAL为软件。P5汇总RTL内未启用的3D部分只核对源码一致性，不能宣称动态验证；正式工程没有另增独立的 `idma_reg64_2d_top.sv` / `idma_reg32_3d_top.sv`。P3非整拍VL尾部仍缺动态覆盖，见[第8节](#formal-review-20261025)；原ROM padding限定告警、共享LLC、FS/libgcc等既有限制不因本表撤销。

<details>
<summary>历史候选的错误后果与修复前后结果（展开查阅）</summary>

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

</details>

## 2. 官方局部修复来源（不重复列代码）

以下均为固定提交的选定修改，没有整包升级。P1–P5官方修改之外的三处本地差异在第3–5节列出；P6另见第11节。

| 项目 | 官方提交 | 实际采用范围 | 综合属性 |
| --- | --- | --- | --- |
| P1 / Ara #481 | [ae8297af0af38b52136826e591782042025725da](https://github.com/pulp-platform/ara/commit/ae8297af0af38b52136826e591782042025725da) | `hardware/src/vlsu/vstu.sv`存储队列计数判断 | 生产RTL，可综合逻辑；未跑综合 |
| P2 / Ara #482 | [a987112abed1339ecc9723555759be79427224bf](https://github.com/pulp-platform/ara/commit/a987112abed1339ecc9723555759be79427224bf) | `hardware/src/lane/vmfpu.sv`延迟分类和停顿判断 | 同上 |
| P2 / Ara #469局部 | [2ce6c2cc976b3dea5f52858e3b9cea8d4779e033](https://github.com/pulp-platform/ara/commit/2ce6c2cc976b3dea5f52858e3b9cea8d4779e033) | `hardware/src/masku/masku.sv`的VL尾位屏蔽；不含PR其余修改。2026-10-23实施调查时PR未合并 | 同上 |
| P3 / fpu_div_sqrt_mvp #18 | [2ec0514c1d538781a26df23fb8a947a60fcdccfc](https://github.com/pulp-platform/fpu_div_sqrt_mvp/commit/2ec0514c1d538781a26df23fb8a947a60fcdccfc) | `hdl/norm_div_sqrt_mvp.sv`中0/0分支1行；不含#16 | 同上 |
| P4 / Cheshire #191、#192 | [1b893efc6ee520be7d135a1adda397af94fa1c45](https://github.com/pulp-platform/cheshire/commit/1b893efc6ee520be7d135a1adda397af94fa1c45)、[ae5795dfdb177a8dc3ef2f43dcc7ceaa36fd9238](https://github.com/pulp-platform/cheshire/commit/ae5795dfdb177a8dc3ef2f43dcc7ceaa36fd9238) | `target/sim/src/vip_cheshire_soc.sv`的ELF加载循环/分段；两个官方中间版均不作为最终接受版本 | 仿真VIP，不纳入综合 |
| P5 / iDMA #66 | [92799c5fabcf2cd1f224f970bbb040b290d08fd5](https://github.com/pulp-platform/iDMA/commit/92799c5fabcf2cd1f224f970bbb040b290d08fd5) | `idma_reg.sv.tpl`及已有`idma_reg64_2d_top.sv`、`idma_reg32_3d_top.sv`、`idma_generated.sv`的reps赋值；没有重生成RTL | 模板不直接综合；派生RTL可综合，未跑综合；未启用3D仅静态核对 |
| P5 / Cheshire #203 | [bca9aadb7588de7046460daf91b39fe863a7a9d1](https://github.com/pulp-platform/cheshire/commit/bca9aadb7588de7046460daf91b39fe863a7a9d1) | `sw/include/dif/dma.h`删除1D清reps的1行，保留本地MMIO/CONF修正 | C软件，综合不适用；重编及运行通过 |

<a id="local-p2-scalar"></a>

## 3. 自行修改一：P2标量返回条件

**目的：结果真正可以交给CPU时才回应，避免读到旧值；存储仍等待原地址响应。**

- 正式F文件：`src/cheshire_soc/ara/hardware/src/ara_sequencer.sv`；历史C对应 `.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/ara_sequencer.sv`。
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

<a id="local-p3-mask"></a>

## 4. 自行修改二：P3浮点子单元异常屏蔽

**目的：只汇总当前浮点格式实际使用且未被mask关闭的元素所产生的异常。**

- 正式F文件：`src/cheshire_soc/fpnew/src/fpnew_opgroup_multifmt_slice.sv`；历史C对应 `.bender/git/checkouts/fpnew-ed006ec0a4178e29/src/fpnew_opgroup_multifmt_slice.sv`。
- 位置：`fpnew_opgroup_multifmt_slice`模块的`gen_pulp_divsqrt`分支；最终第392–398行新增mask计算，第414行修改实例端口连接。
- 本地提交：`d38bcf6925077593e6b766154d6fda205a532ed7`。

当前每个Ara lane内的相关64-bit FPnew切片有4个内部子单元（不是整个Ara共4个），FP32实际用2个，FP64用1个。其余子单元为保持同步仍启动，补零0/0产生的NV不应参与汇总。mask以最小16位元素为粒度，FP32第二个元素应取bit2，不能直接取bit1。这解释了正常除法多报NV以及mask关闭后仍报异常。

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

**可综合性：可综合的组合选择/索引逻辑。** `LANE`和`Width/NUM_SIMD_LANES`是展开常量，当前Ara路径后者为16（CPU标量路径为64）；`fp_width`查固定格式编码表计算位宽。表达式中为常量除法，可由综合工具优化，没有新增时钟或状态。已通过VCS编译/展开及仿真；实际综合映射、面积和关键路径未验证。

**验证：**官方#18之后，同一177项6错→0；FP32/FP64除法和平方根、四元素全部16种mask组合的补充753项28错→0，覆盖应保留/应屏蔽的NV/DZ、结果及保护区。标量基础测试、RVV及fmatmul通过。FP16只有静态索引核对，未动态验证；其他配置不能直接沿用通过结论。

<a id="local-p4-preload"></a>

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

**2026-10-23历史结论：**当时只有隔离候选通过。R/F写回及独立复验已在2026-10-24完成，不能再将它们列为当前未同步；综合及ASIC验收仍未完成。


<a id="formal-review-20261025"></a>

## 8. 正式工程P2/P3独立复审（2026-10-25）

F=`/home/zhaowy24/CheshireAra`，下列路径相对F；正式目录没有Git元数据，以[实际文件哈希及结束复查](evidence/abc_review_20261025.json)为依据。当前 `ara_sequencer.sv`及 `fpnew_opgroup_multifmt_slice.sv`完整文件与历史C标签 `5e0f973c090ee26ba18ce520bc61beebe584e929`一致；第3/4节代码仍适用，正式行号分别为564–569和392–398/414。这个比较只覆盖所述文件，不意味着两工程全量一致。

### 8.1 P2：为什么三条返回通路不能共用一个条件

对照实际官方patch，Ara #482（`a987112…`）只处理VMFPU延迟分类和stall，未改sequencer或masku；后两处错误来自旧逻辑，不是该补丁新引入。VL尾位过滤仍是#469的固定局部hunk（`2ce6c2c…`），本轮不重新查询PR合并状态，完整SHA见第2节。

下表路径前缀为 `src/cheshire_soc/ara/hardware/src/`。

| 返回对象 | 实际生产者/消费者 | 本地条件解决什么 |
| --- | --- | --- |
| VMVXS/VFMVFS | `ara.sv:304–305/319`使用lane0共享MaskB数据及ready；`lane/operand_queue.sv:495–501/530–535`在有效且ready时弹出 | MaskB有数据不等于属于当前标量提取。等 `running_mask_insn_q=0`再应答和消费，避免取走旧mask字 |
| VCPOP/VFIRST | `masku/masku.sv:1386–1389/1491–1496`产生专用结果脉冲，下一拍自动清valid，没有结果ready输入 | 不能等running位清零，否则会漏接当拍结果。保留独立的枚举分支，而不是统一加“mask已结束”条件 |
| 存储 | `ara_sequencer.sv:554–562`用addrgen_ack应答并携带异常字段 | 旧 `!use_vd`也包含store；显式枚举将其排除，防止旁路MaskB valid误触发地址完成 |

mask完成的当拍，sequencer仍使用旧 `running_mask_insn_q`，标量提取保守等待到下一拍；队列在未ready时保留有效数据，未见由此引入丢响应的路径（`ara_sequencer.sv:628–634`）。成功接收后回IDLE并消费队列；专用MASKU结果下一拍清valid，未发现新增重复响应机制。

这里有两个适用前提：`ara_pkg.sv:112–113`的MASKU指令队列深度为1；CPU `src/cheshire_soc/cva6/core/acc_dispatcher.sv:293–294`将返回ready常置1。F历史 `p2_mask/simulate.log`的60个样本在mask完成、busy仍为1且scalar_ready为0时正确回应VCPOP/VFIRST，支持专用通路不靠该ready消费。未来增加MASKU在途数或CPU返回反压时必须重新检查，不能直接推广本结论。

### 8.2 P3：为什么保留同步启动，只屏蔽异常贡献

MVP #18（`2ec0514…`）只清0/0分支的DZ，不处理SIMD汇总；本地修复针对旧有的无效子单元NV及mask索引错误。当前SoC未覆盖Ara默认 `FPUSupportHalfSingleDouble`，每个Ara lane的VMFPU为64 bit，内部最小元素粒度16 bit：

| 当前格式 | 实际元素/内部子单元 | 读取的 `simd_mask`位 | 其他内部子单元 |
| --- | --- | --- | --- |
| FP16 | 0、1、2、3 | 0、1、2、3 | 无；本轮仅静态核对，未动态验证FP16 |
| FP32 | 0、1 | 0、2 | 子单元2/3的mask置0 |
| FP64 | 0 | 0 | 子单元1/2/3的mask置0 |

依据为 `ara/hardware/src/lane/vmfpu.sv:846–852/1075–1085`与 `fpnew/src/fpnew_opgroup_multifmt_slice.sv:179–202/392–414`（均在 `src/cheshire_soc/`下）。这里的内部子单元不是Ara lane。CPU标量FPU虽然复用该文件，但正式profile的 `XFVec=0/FLen=64`，只实例化lane0，`NUM_SIMD_LANES=1`，不能套用上表的四子单元说明。

- **不会改变同步参与者：**slice的DIVSQRT仍启动全部内部子单元，并等待ready/done归约（217–219、638–639）。只改mask使无效结果不能贡献异常；若改成不启动无用子单元，反而需要重做同步协议。
- **不会用下一条指令格式屏蔽上一条结果：**`fpnew_divsqrt_multi.sv:105–132`将格式、mask及valid随同一事务传递，197行在 `op_starting`锁存result_mask，339–362随结果输出；HOLD状态保留未被接收的结果和对应mask。
- **异常只在对应输出mask下汇总：**slice第664–669行按lane_masks屏蔽后OR。真实有效元素的NV/DZ保留，补零子单元即使产生NV也不贡献。

源码中VMFPU还按剩余元素数生成issue_be（`vmfpu.sv:1543–1552`），存在VL尾部过滤路径；但Ara dispatcher第421/450行的跨lane异常OR没有逐项按lane valid屏蔽。**不能仅凭此判定缺陷**：还需证明无效lane确有非零旧标志被消费。已有监视在所测输入上为0，未覆盖下述不均匀lane条件。

### 8.3 正式工程历史测试及剩余缺口

已实际读取F的 `sim/work/p1_p5_20261024/runs/` 下列目录中的 `simulate.log`和 `result.json`，不是只检查候选C。五项均为PASS，目标、simv和入口返回均0，错误列表为空；具体ELF及历史清单哈希存入本次来源快照，避免在正文铺满哈希。

| F运行目录 | 原始日志中的检查结果 | 证明的范围 |
| --- | --- | --- |
| `p2_order` | 835项、0错；两lane错绑及提前/存储误响应均0 | 所测浮点排序与辅助返回序列 |
| `p2_mask` | 124项、0错 | 所测VL边界；包括上述60次专用返回同拍样本 |
| `p2_scalar` | 483项、0错 | 所测标量提取重叠；不等于所有交叠序列穷举 |
| `p3_flags` | 177项、0错 | 标量/向量除法及五位异常检查 |
| `p3_matrix` | 753项、0错 | FP32/64除法、平方根、4元素全部16种mask及相关结果/保护区 |

当前测试源已归入 `sw/tests/regressions/`。P3基础和矩阵向量部分均固定 `VL=4`：在当前2 Ara lanes下，FP32恰好填满一轮、FP64填满两轮。保护区未改写只能证明写界，**不能证明非整拍尾部的异常屏蔽或不均匀lane有效事件正确**。

后续若授权补测，直接在原 `p3_div_flags.c`增加FP32/64的VL=1和3：先用较长VL装入含异常触发值的完整操作数，再缩短到VL=1/3并清fflags；使活动元素得到精确正常结果、VL外元素若被错误计算会触发NV，检查fflags=0与尾部不写；再将活动元素置为NV/DZ作必须保留的对照。沿用原flags观察器，不新建框架。本轮未实施，也不将缺口写成已知失败。

原FP16动态、VL=0/长VFIRST、更多舍入/次正规及UF/NX等边界保持。HOLD路径已静态检查，没有新证据要求本轮增加随机背压测试。第3/4节修改仍属于可综合RTL写法；实际目标库综合、时序、面积和功耗均未验证。

若后续更新服务器随工程说明，可在现有修复来源摘要中补充“P2依赖当前MASKU深度/CPU返回契约；P3依赖格式及mask粒度；P3非整拍VL仍待补测”三点即可，无需另建报告。本轮未写服务器。


<a id="ara-maskb-tests-20261025"></a>

## 9. Ara #475/#479：参考工程实际测试（2026-10-25）

### 9.1 范围、输入和方法

用户本轮授权“进行测试，先在CheshireAraPULP工程上测试”。本地主Agent经既有Windows SSH执行；只在R新增测试源、只读观察模块和新输出目录，没有应用修复、修改生产RTL/依赖/配置或操作正式工程F，没有调用Bender、提交、推送或创建公开issue/PR。

- R：`/home/zhaowy24/CheshireAraPULP`，HEAD保持 `5986ba021e1a0d30dbdb5ecb2cfa230a2c35947c`。VCS `W-2024.09-SP1`，GCC `13.2.0`；`SelectedCfg=3`、真实Ara、2 lanes/VLEN2048、WT D-cache；软件定向使用e32/m1。
- 来源：[#475](https://github.com/pulp-platform/ara/pull/475) head `5737c311…`、[#479](https://github.com/pulp-platform/ara/pull/479) head `38ade6c0…`；配套说明查[#469](https://github.com/pulp-platform/ara/pull/469) head `aee901c7…`。完整SHA和查询状态在备份的 `upstream_snapshot.json`。**用例依据PR描述自行构造，没有取得/重放作者的完整随机测试程序或seed环境。**
- 最终源：R `_e01/pr475_479_20261025/v4/{maskb_repro.c,maskb_observer.sv}`。通过既有 `sw/Makefile` 的 `direct_test` 宏构建，未改Makefile；硬件沿既有静态VCS清单，在新目录分析/展开，加一个只读观察顶层，无force、DUT输入驱动或stub。
- 普通运行无波形、串行，沿既有 `run.py` 判定目标/仿真器/入口。最终矩阵VL为1/2/3/4/5/7/8/15/16/17/31/32/33/63/64，间隔0/1/2/4条nop、重复2次，每个完整矩阵120组。初始化在producer之前等待，紧邻producer/consumer之间不加等待；另有128条nop的延迟提取对照。
- 观察器记录lane的valid/ready接收、MaskB请求及指令完成。相关事务连续20001周期无进展时打印现场并 `$finish`；这些运行的原始分类为 **INCOMPLETE、目标未结束、simv=0、入口=4**，不记作PASS，也不是等满主机600秒后的TIMEOUT。死锁判断同时依据请求依赖及匹配的内部状态。

### 9.2 实际结果

下表运行名均位于R `work/runs/`，前缀省略 `pr475479_20261025_`。数字是检查次数或每lane窗口次数，不是缺陷数量。

| 运行 | 操作及实际结果 | 结论/退出状态 |
| --- | --- | --- |
| `v4_k7` | gather→存储，120组/7800检查，0错 | PASS，0/0/0 |
| `v4_k8` | 全选compress→存储，120组/7800检查，0错 | PASS，0/0/0 |
| `v3_k1`、`v4_k1` | `vrgather.vx→vmv.x.s`，VL=1；两lane各捕获1次#475窗口，随后20001周期无进展 | #475复现，入口4；v4为重复确认 |
| `v3_k2` | `vrgather.vx→vfmv.f.s`，VL=1；相同窗口与停滞 | #475复现，入口4 |
| `v3_k3` | 全选`vcompress→vmv.x.s`，VL=1；相同窗口与停滞 | #475复现，入口4 |
| `v4_k4` | gather→`vmslt.vx`，120组/8056检查，0错；每lane接收120次旧vd读取，#479窗口0次 | PASS，0/0/0；未触发目标窗口 |
| `v4_k5` | 全选compress→`vmslt.vx`，同样120组/8056检查、0错、每lane#479窗口0次 | PASS，0/0/0；未触发目标窗口 |
| `v4_k9` | 仅部分选择compress→存储；到VL=2、有效选择位`01`时停滞，无后续比较指令 | 与#450终止问题一致，入口4 |
| `v4_k6` | 相同部分选择compress后接比较；在相同VL=2处先停滞，新比较尚未进入冲突接收窗口 | 同一前置终止问题，不能记为#479复现，入口4 |
| `v4_p2_regression` | 原R `p2_scalar_overlap.elf`，483项、0错；原提前返回/存储误回应计数均0 | PASS，0/0/0 |

**#475的具体等待链。** 例如 `v4_k1` 的gather于cycle203734进入lane，标量提取于203736被接收；此时gather仍运行、状态机尚为IDLE、请求valid仍0，标量源`v8`的hazard为`01`。后续gather读取源`v2`的MaskB命令停在valid=1/ready=0，标量请求又等待gather写回`v8`；cycle223742仍无进展，MASKU的issue/commit有效位均为1。与PR描述的循环等待相符；本地P2-3的CPU返回条件没有解除lane内部这个等待链。

**#479的证明边界。** 两个完整矩阵中每lane均记录120次需要旧vd的mask指令接收，但在REQUESTING阶段向lane提出/接收此类请求均为0；顶层等待且lane仍在REQUESTING的采样各为13848次。因此已测试这些序列且功能通过，但**尚未验证冲突窗口到达后的行为，不能据此宣布#479不存在或PR误报**。尚未应用其所述#469配套修改，也没有复现作者随机seed的原环境。

### 9.3 相关终止问题与额外标量失败样本

**部分选择compress。** `VL=2`、选择位`01`意味着最后输入元素不选中。独立compress对照和后接比较两种程序均在此处停滞：lane状态为REQUESTING，最后请求的`is_last_req=0`，请求/命令队列已无推进，MASKU仍未完成。与官方[issue #450](https://github.com/pulp-platform/ara/issues/450)描述的“末尾未选中，结束标记没有进入FIFO”一致；#469包含相应修改，而此前P2只采用了VL尾位过滤。没有进行该终止补丁的修复前后对照，本轮不称已修复。

**延迟标量提取仍有错误值。** `v2_k0` 在gather后等待128条nop，VL=4时首次失败：scalar实际值 `0x3f8020003f800000`，期望 `0x000000003f803000`；同时向量存储的首元素正确为 `0x3f803000`。585项检查中1错，目标47/simv0/入口1，无#475窗口。实际值与源向量旧MaskB字相符；失败详情通过C的 `maskb_failure[]` 和CPU trace同时保存。**根因尚未完整定位，不能认定#475或#479补丁会修复它。** 原483项回归本轮再次通过，不覆盖这个新gather序列；未在F重跑该反例。

### 9.4 测试自身修正及保留的早期记录

- v1观察器用接收后已更新的 `vinsn_running_d` 过滤，漏计非标量接收；v2改为真实valid/ready握手。v1混合初始化下的旧值失败未单独定因，不能按其“gather计数0”判断未执行；原源/ELF/日志保留，随后简化初始化。v1/k1在该诊断期间主动停止，未当作PASS或PR死锁。
- v3/k4功能检查0错，但CPU读取包含无效尾位的整个mask字节时出现 `READ_DATA_X`，原入口2不改写。v4只读取完整有效字节，其余有效位继续由 `vcpop` 检查；**未屏蔽断言、未降低期望值**，两组完整矩阵重新运行均PASS。早期失败没有删除。

### 9.5 保存位置、保护核对及最小继续步骤

- 全部17份运行记录（含早期错误/中止）及CPU trace留在R `work/runs/pr475479_20261025_*`。构建命令及软件Make输入在 `work/pr475_479_20261025/v4/commands.json`；新硬件输出在该目录，软件输出在 `sw/build/pr475_479_20261025/v4/`。
- 本轮前后4302份R已跟踪文件的SHA256/权限、HEAD和Git状态全部保持；原有两份未提交诊断也保持。这里只报告已核对范围，不把历史4390文件恢复检查当作本轮执行。F和本地FPGA未操作。
- 服务器归档：`~/CheshireAra_maintenance/pr475_479_20261025/pr475_479_evidence.tar.gz`；[本地同份归档](../../../../.e01_backups/pr475_479_20261025/pr475_479_evidence.tar.gz)、[结构化结果](../../../../.e01_backups/pr475_479_20261025/summary.json)、[最终测试源](../../../../.e01_backups/pr475_479_20261025/maskb_repro.c)、[只读观察器](../../../../.e01_backups/pr475_479_20261025/maskb_observer.sv)。两地归档SHA256一致，161份数据成员内容/权限及清单重读校验通过；完整大体积trace留服务器，哈希已记录。共享文档原未提交版本另存同目录 `docs_before/`。

重跑已有#475用例的例子（沿用既有VCS环境，运行名须尚未存在）：

```bash
cd /home/zhaowy24/CheshireAraPULP
E01_SIMV="$PWD/work/pr475_479_20261025/v4/simv" \
  /usr/bin/python3.9 _e01/remaining_acceptance_20261021/run.py \
  pr475_replay_01 elf sw/build/pr475_479_20261025/v4/maskb_k1.elf \
  +MASKB_OBSERVE +MASKB_STALL_CYCLES=20000 +P2_SCALAR_MONITOR
```

本轮授权测试已完成，**没有实施RTL修复**。建议下一步先评审已复现#475的最小回移；compress终止问题和延迟提取错误值分别处理，#479在必要配套修改或作者触发环境明确后再测试。是否实施这些修改需用户另行决定；不因此自动扩展到其他开放PR、F同步、综合或上游发布。


<a id="p6-candidate-check-20261025"></a>

## 10. P6候选：共享MaskB通道与compress结束条件（2026-10-25）

### 10.1 授权、采用范围与结论

用户在第9节测试之后授权检查现有PR并仿真确认，不能解决时给出修改方案；确认#479暂不继续处理。本轮将这些问题命名为 **P6候选**，只在参考工程R的独立源码副本应用PR，不写入R生产源码或正式工程F，不升级依赖、不调用Bender，不提交或推送。第1节的10份已接受P1–P5文件保持；**P6尚未完成修复或验收。**

输入L保持 `ca8395677691ba8d9d226ce4b5b5b49192b90f1c` 及原有文档修改；R保持 `5986ba021e1a0d30dbdb5ecb2cfa230a2c35947c` 及两份原诊断文件修改。当前配置仍为SelectedCfg=3、2 lanes/VLEN2048、WT，VCS W-2024.09-SP1、GCC13.2。

查询时以下PR均开放、未合并。只采用表列局部，不将它们记为自行开发的修复：

| 来源与固定head | 副本中的改动 | 本轮结论 |
| --- | --- | --- |
| Ara [#475](https://github.com/pulp-platform/ara/pull/475)，`5737c311892e3ed2a61181efd46c6c74489863ef` | `lane/lane_sequencer.sv`：记录正在执行的gather/compress，在其释放MaskB前阻止标量提取进入 | 已验证可消除原VL1循环等待；不能修复全部数据错误 |
| Ara [#469](https://github.com/pulp-platform/ara/pull/469)，`aee901c70f9eb9be644da556dc4a2ddd0de48661` | `masku/masku.sv`：仅#450相关的“最后选中元素”标记；既有P2 VL过滤不重复应用，VID修改未采用 | 部分选择矩阵通过；全不选和超过一个选择字仍停滞，不能整段视为完整compress修复 |
| Ara [#480](https://github.com/pulp-platform/ara/pull/480)，`74560f5302990f5a235292067b060b1eef545e93` | `masku/masku.sv`：广播接收掩码只记录真实valid/ready握手，并保持至全部lane接收 | 后续检索发现与多余请求直接相关，追加独立对照；修复原VL4错误点，但同程序继续运行仍有历史依赖错误 |

#479没有应用或追加定向测试；未改变其GitHub状态。另查到的#467标量源hazard、#502 VFIRST结束等PR没有证据可替代本轮数据归属修复，没有扩大回移。

### 10.2 仿真方法与实际结果

保留R底库，在 `_e01/p6_20261025/` 复制当前RTL，原样应用上述相关hunk。通过既有静态VCS脚本的独立副本，仅替换这两份RTL的读取路径；其他源码与参数相同。输出位于 `work/p6_20261025/{pr475,pr475_450,diagnostic,ownership,pr475_450_480}/`。后两个诊断顶层只观察请求/缓冲/响应，没有force或DUT驱动。

软件复用原 `direct_test` 和 `run.py`，不改Makefile或运行器。旧失败ELF用于原版/两PR/三PR对照；针对已确认缺口，在本轮测试副本中增加VL1、单独VL4、全不选及跨128位选择字的检查。全部仿真串行，保留原断言，无综合、板测或ASIC验收。

运行名均在R `work/runs/`，下表省略前缀 `p6_20261025_`：

| 运行/比较 | 实际结果 | 能证明什么 |
| --- | --- | --- |
| `baseline_scalar1` → `scalar1_int` | 同一VL1 ELF：原版停滞、每lane #475窗口1次；#475副本8组/520项0错、PASS | 请求端互斥修复原触发 |
| `scalar1_float`、`scalar1_compress` | #475副本，各8组/520项0错、PASS | 浮点提取、compress后提取也通过VL1定向检查 |
| `pr475_k9` → `combined_k9` | 同一部分选择ELF：仅#475在VL2停滞；再加#469相关段后，120组/7800项0错、PASS | #469对已测e32/m1/VL1–64末尾未选场景有效 |
| `compress_none`、`compress130` | 两PR副本：e8/m1/VL2全不选；e8/m1/VL130交替选择、最后元素未选；两项均20001周期无推进、INCOMPLETE/入口4 | #469仍缺全不选路径；VL130超过2×64位选择字，相关补丁条件不成立，仍保留旧终止缺陷 |
| `baseline_delayed_history` → `delayed_history` | **同一原v2/k0 ELF**：原版与两PR副本均585项/1错、TARGET_FAIL/目标47；首次错误在第一轮VL4 | #475＋#469没有修复原延迟提取反例 |
| `three_prs_history` | 再加#480：原VL4点通过，第一轮全部28组通过；第二轮VL1/gap0首次失败，累计1885项/2错、目标47 | #480修复部分多余请求，但数据归属问题仍存在。两个错误数的测试进度不同，不能按“1→2”比较收益 |
| `scalar4_delay`、`scalar4_now` | 两PR副本，单独VL4，各65项0错、PASS | VL4本身不足以触发，指令历史有影响；等待128条nop不是完整修复 |
| `history_vl3`、`three_prs_vl3` | 包含VL1/2/3历史的原v4源码ELF：两PR、三PR均在VL3返回X，由只读观察器结束，INCOMPLETE/入口4 | 未知值仍存在，不能记PASS；该观察器用于在错误返回时停止，不屏蔽断言 |
| `p2_regression` | **两PR副本**既有P2标量回归483项0错、PASS；early=0、store_without_addrack=0 | 保留原P2回归；这不覆盖新的历史依赖错误，也不代表三PR版本已完成回归 |

总计21份原始运行记录：7 PASS、6 INCOMPLETE、4 ASSERTION_OR_SIM_ERROR、1 SIM_ERROR、3 TARGET_FAIL。它们包含诊断与停止记录，**不是“21项回归均通过”**，也不是缺陷数量。完整表在[结构化运行记录](../../../../.e01_backups/p6_20261025/run_summary.json)。

保留的非最终记录：

- `pr475_k1/k2/k0` 完整历史矩阵出现CPU未知操作数断言后主动停止，原入口2/仿真器255保持；`pr475_k3` 跑到目标47，7800项/1853错并有READ_DATA_X，原入口2保持。后来用VL1窄范围单独确认死锁修复，未把完整矩阵改记通过。
- `compress_cross` 初始扫描128/129/130：VL128已完成257项0错、进入VL129后主动停止，原SIM_ERROR/入口3保持；不能称整个扫描通过，也不能据此判定VL129失败。停止说明中先前基于较早日志的“仍在VL128”判断已追加更正；之后单独`compress130`确认VL130停滞。
- 新compress测试首次生成C字符串时有换行语法错误，编译失败版本和日志保留；修正后重建才运行，未把编译失败当硬件缺陷。

### 10.3 已定位的数据串入与#480作用

两PR副本、同一历史ELF的只读记录提供了两个直接现场：

1. cycle216357：CPU正确收到 `0x000000003f800000`，但MASKU的issue/commit都为0时，它的vd缓冲也接收了该标量值；下一条gather在cycle219804实际消耗这份残留值。当前 `masku_operands.sv` 无条件把MaskB valid送入vd spill，没有区分空闲时的CPU标量返回。
2. cycle243475：CPU收到旧gather字 `0x3f8020003f800000`。此刻队列头还是conv=0的gather命令，本次标量的conv=2命令要到243476才入队，正确v8数据要到243478才返回。仅判断MASKU已空闲，不能证明队列头属于当前标量请求。

追加#480后，原VL4点lane0的MaskB源请求从 **6次变为应有的4次**，响应恢复为 `0x000000003f803000`；说明广播重复接收是原错误点的一部分。但同一ELF第二轮VL1记录：scalar实际 `0x000000003f83c000`、期望 `0x000000003f800000`，存出的向量首元素也为前者。CPU详细trace中的8个失败字段已保存于 `three_prs_failure_trace.txt`；这次向量值已错，不能都归为最后一级CPU写回错误。

因此，**#475请求互斥、#480广播握手、MASKU缓冲/CPU返回归属是相邻但不同的条件**。本轮确认空闲MASKU误收及后续消耗、旧命令被当标量返回；还没有通过自定义RTL前后对照证明一个局部条件能消除全部历史错误，不能宣布根因已全部修完。

### 10.4 P6建议修改方案：尚未实施

建议P6保留三个问题的独立检查，不整包采用所有开放PR：

- **P6-1，请求与广播。** 以#475作为标量进入MaskB的互斥基础；#480对已观察的重复请求有直接收益，可作为配套候选。保留两者来源，最终必须与下面的数据归属修改组合验证，不能按VL1通过直接写入已接受版本。
- **P6-2，compress完整结束。** #469只能作为局部参考。可在 `masku.sv` 暂存最近一个选中索引：出现下一个选中项时，把前一个按非末项发出；扫描全部VL结束后，再把暂存项携带两个结束标记发出。一个都没选中时单独完成、不读取伪造源数据、不写目的；扫描结束后停止再生成请求，并等待已有数据/结果排空。这样不依赖“最后输入恰好选中”或“选择位只占一个字”。这是状态逻辑方案，需核对背压、计数、尾部保持和全不选完成路径，尚无实现/仿真通过结论。
- **P6-3，数据归属。** 优先检查 `masku_operands.sv` vd缓冲的valid/ready，依据当前MASKU有效指令和实际数据用途接收，避免空闲时收走CPU标量数据；同时在 `ara.sv`/sequencer的返回路径确认本次标量命令已实际发出且当前数据属于它，并检查gather结束时的剩余请求/数据。若现有控制信号无法无歧义区分，再沿命令保存归属标记；不靠固定nop或无条件清空共享队列处理。具体最小diff需下一步实现并用本轮历史序列验证。

验收至少重跑本轮原失败ELF（含第二轮VL1、非整拍VL3）、即时/延迟整数与浮点提取、compress全选/末尾不选/全不选/跨选择字，以及既有P2回归；不能以旧483项通过替代新失败样本。#479继续不纳入；F同步、综合、上游PR准备/发布不属于本轮。

### 10.5 产物、保护与重跑

- R新增源/差异：`_e01/p6_20261025/`；软件输出：`sw/build/p6_20261025/`；5个独立硬件输出及每步 `commands.json`：`work/p6_20261025/`；21份日志：`work/runs/p6_20261025_*`。原源码、断言与已有日志没有覆盖。
- 结束核对：4241份**非符号链接的已跟踪常规文件**内容/权限、HEAD及原Git状态与本轮输入相同（本轮计数排除符号链接，与第9节4302的口径不同）；两份原诊断修改保持，无遗留本轮simv进程。F与本地FPGA未操作。
- 工程外归档：`~/CheshireAra_maintenance/p6_20261025/p6_evidence.tar.gz`；[本地同份归档](../../../../.e01_backups/p6_20261025/p6_evidence.tar.gz)，SHA256 `4bd0b539c91fa615c81f41dd1ffd126aaedf93600d32f0974822fe2098963244`。146个成员，145份数据成员逐一校验内容、长度、权限；完整CPU trace和构建simv留服务器，其哈希在归档的 `external_traces.json`。共享文档原未提交状态另存本地 `docs_before/`。

已有产物的最小重跑示例（运行名须尚未存在）：

```bash
cd /home/zhaowy24/CheshireAraPULP
E01_SIMV="$PWD/work/p6_20261025/pr475_450_480/simv" \
  /usr/bin/python3.9 _e01/remaining_acceptance_20261021/run.py \
  p6_history_replay_01 elf sw/build/pr475_479_20261025/v2/maskb_k0.elf \
  +MASKB_OBSERVE +MASKB_STALL_CYCLES=20000 +P2_SCALAR_MONITOR +P6_SCALAR_DEBUG
```

该命令预期重现三PR副本的历史依赖错误，**不是通过示例**。重新构建时使用对应输出目录保存的 `commands.json` 和本轮固定输入；没有新建通用测试框架。当前交付是P6候选检查及修改方案，生产修复、F同步和验收尚未完成。


<a id="p6-fix-20261025"></a>

## 11. P6实施及仿真结果（2026-10-25，仅R）

### 11.1 范围与实际实现

用户授权实施后续P6、仿真并更新修改表及相关文档。本地主Agent通过Windows SSH操作R；本地子Agent参与局部实现及独立静态复核，没有启动服务器Agent。R输入及完成后HEAD均为 `5986ba021e1a0d30dbdb5ecb2cfa230a2c35947c`，P6保存在工作区，**未提交、未推送，F未同步**。沿用SelectedCfg=3、WT、2 lanes、VLEN2048、MASKU指令队列深度1，以及现有VCS静态入口、GCC13.2/VCS W-2024.09-SP1；未调用Bender或升级依赖。

采用固定PR来源如下，只取相关代码，不声称上游当前分支已验证：

| 来源 | 固定head SHA | 实际采用 |
| --- | --- | --- |
| Ara #475 | `5737c311892e3ed2a61181efd46c6c74489863ef` | lane中gather/compress运行位图及标量进入互斥，约在`lane_sequencer.sv:248/323/379`。 |
| Ara #480 | `74560f5302990f5a235292067b060b1eef545e93` | `masku.sv:564`附近的广播握手及保持逻辑。 |
| 本地P6-2 | 无提交 | `masku.sv:517/1146/1526`附近的pending索引、跨字扫描、最终请求及空输出完成路径。 |
| 本地P6-3 | 无提交 | `masku_operands.sv:34/85/169/262`的指令有效输入及vd输入valid/ready资格；`masku.sv`连接新端口。 |

**数据归属。** 当前接收条件为：

```systemverilog
assign masku_owns_vd = vinsn_issue_valid_i && (vinsn_issue_i.vfu == VFU_MaskUnit) &&
    (vinsn_issue_i.use_vd_op || (vinsn_issue_i.op inside {[VRGATHER:VCOMPRESS]}));
```

该条件同时门控vd缓冲输入valid及返回lane的ready。只门控ready仍可能让spill缓冲采样；只门控valid仍可能确认并弹出数据。`VFU_MaskUnit`限定排除masked FMA等虽有`use_vd_op`、但旧vd实际来自其他通路的指令；gather/compress临时源读取仍允许。此次组合已使原失败ELF及连续矩阵通过，因此没有再改`ara.sv`/`ara_sequencer.sv`、增加tag或改变CPU返回协议；原P2标量条件保留。这不构成任意队列深度/接口配置的数据归属证明。

**compress结束。** 保留最近选中的一个索引；遇到下一个选中项时，把前一个按非末项送入索引FIFO及请求FIFO，只有两者均可写才推进。扫完VL后，将保留的最终索引同时带`vcompress_last_idx`和`is_last_req`发出，随后不再扫描或重复发送。未选位无需FIFO空间，pending索引可跨128选择位字保留。有输出仍等待原结果队列和最终VRF写入确认；全不选则清零剩余计数并从空输出路径完成，不伪造索引。新增一个索引寄存器及3个控制位，没有新FIFO或整向量组合查找。

没有采用第10节尝试的#469 compress单字向后查找局部，因为它不能解决已确认的全不选及VL130跨字问题；**原P2采用的#469 VL尾位过滤仍保留**。#479按用户决定不应用、不追加测试，也未改变其GitHub状态。

### 11.2 本轮实际运行

先用独立候选源码运行，再将同SHA的3份RTL写回R，从实际生产路径重新分析、展开并运行。运行目录均为R `work/runs/`；下表省略前缀 `p6fix_20261025_`。PASS均为目标/仿真器/入口返回码0，原断言保持。

| 阶段及运行后缀 | 实际检查 | 结果 |
| --- | --- | --- |
| `v1_history` | **原v2/k0失败ELF未重编**，56组/3640项；此前第一轮VL4及第二轮VL1错误点均经过 | PASS，0错 |
| `v1_int`、`v1_float`、`v1_compress_scalar` | 现有v4 KIND1/2/3 ELF，各120组/7800项，含VL1/3及重复历史 | 3 PASS，0错 |
| `v1_compress` | 新边界ELF，28组/7252项 | PASS，0错 |
| `v1_p2_order`、`v1_p2_bound`、`v1_p2_scalar` | 既有P2测试，分别835、124、483项 | 3 PASS，0错 |
| `v1_baseline_boundary` | **同一新compress ELF**在未修复旧simv上执行，VL1全不选处停滞20001周期 | 预期负例：INCOMPLETE、入口4，保持原结果 |
| `accepted_delay`、`accepted_int`、`accepted_float`、`accepted_compress_scalar` | 由永久Make目标重建；各120组/7800项 | 4 PASS，0错 |
| `accepted_compress` | 永久Make目标重建，28组/7252项，含两次VL0 | PASS，0错 |
| `accepted_vector` | 既有`vector_fixed.elf`，22字节复制，0错 | PASS |
| `accepted_rvv` | 既有`rvv_bounds.spm.elf`，5976项，0错 | PASS |
| `accepted_fmatmul` | 既有`fmatmul.spm.elf` | PASS |

合计 **17次运行：16 PASS＋1预期旧版停滞**；其中生产路径8次全部PASS。永久5目标合计 **508组、38452项检查、0错**，不把候选重复运行或其他回归加入该软件检查总数。原始返回码、UART和统计见[结构化结果](../../../../.e01_backups/p6_fix_20261025/summary.json)。

只读统计模块无force、DUT输入驱动或主动finish。生产四个MaskB用例的`idle_vd_captures`均为0；`accepted_compress_scalar`记录120次接受/完成/最终索引，扫描FIFO等待9968周期、最终索引发送等待488周期、最终写回等待120周期，说明本轮实际经过这些等待路径。compress边界记录：`[P6_FIX_SUMMARY] lanes=2 vd_captures=2344 idle_vd_captures=0 compress_accepts=26 compress_commits=26 empty_done=6 final_idx_pushes=20 scan_fifo_wait=5512 flush_fifo_wait=38 final_gnt_wait=20`。VL0的两次操作由前端处理，不要求进入MASKU。计数为整次运行、双lane聚合，不能证明所有指令归属或所有背压组合。

首次生产展开因只读统计模块使用跨层`$bits`作为localparam，被VCS拒绝；改为当前工程明确的2 lane常量后分析/展开成功，生产RTL未因此改变。初次日志及统计模块原版保留，未改记成功。

### 11.3 覆盖范围与限制

**P6修复确认：**在当前R配置及已测场景下，本次已复现的VL=1死锁、延迟/连续标量提取错误，以及compress末尾未选、全不选和跨选择字停滞，均已通过修复后对应检查，当前没有尚未解决的已复现P6失败项。2026-10-25再次只读核对服务器6份最终文件、17份结果记录及通过运行所用ELF/simv，均与已验证版本一致；本次确认未重新构建或仿真。该结论不表示所有RVV指令、配置和程序均已无错；下列未测项属于覆盖限制，不是已确认的剩余缺陷。#479按此前决定未纳入P6，F仍未同步。

标量矩阵使用e32/m1，VL集合为1/2/3/4/5/7/8/15/16/17/31/32/33/63/64，4种间隔×2轮；gather索引为VL−1，检查整数和FP32提取及全选compress后的提取。沿用旧用例的初始化等待，KIND0保留producer后128条nop来重放“延迟也读错”的原例；没有靠增加nop修改旧失败条件。没有动态验证vrgather.vv、vrgatherei16、负整数扩展或其他SEW/LMUL组合。

新compress为e8/m1、tu/mu、vstart=0，无插入nop。14种布局×2轮，在当前VLMAX=256初始化完整目的寄存器为非零变化值；压缩后恢复VLMAX并检查全部256元素，所以验证了选中结果及`[选中数,256)`的目的尾部保持。选择位内存的VL外设为1，其中加载末字节内的VL外位可实际进入；不能称所有VL外寄存器位都已加载1。该测试不等同于任意RVV程序、配置或vstart验收；原MaskB矩阵的内存保护检查也不等同于完整寄存器尾部检查。

本轮仅仿真当前R配置，未综合、FPGA板测或ASIC验收，也未在F或上游当前版本运行。没有面积/时序/功耗结论；P3非整拍VL异常屏蔽等原缺口不因P6通过而消失。

### 11.4 构建、证据与局部恢复

永久软件入口（沿用现有工具环境）：

```bash
cd /home/zhaowy24/CheshireAraPULP
make -C sw OUT="$PWD/sw/build/p6_fix_20261025/accepted" p6-regressions
```

五个目标为`p6_scalar_delay`、`p6_scalar_int`、`p6_scalar_fp`、`p6_compress_scalar`、`p6_compress`。默认`all`的64项依赖（31 ELF＋31 dump＋库＋SPI）前后相同，P6由上述显式组运行；未新增通用测试框架。硬件分析/展开的实际命令及初次失败/重试保存在R `work/p6_fix_20261025/{candidate_v1,accepted}/commands.json`，使用现有静态脚本，未改原构建入口。

重跑已构建的compress例（运行名须未存在）：

```bash
E01_SIMV="$PWD/work/p6_fix_20261025/accepted/simv"   /usr/bin/python3.9 _e01/remaining_acceptance_20261021/run.py   p6_replay_01 elf sw/build/p6_fix_20261025/accepted/p6_compress.elf   +MASKB_OBSERVE +MASKB_STALL_CYCLES=20000 +P6_FIX_MONITOR
```

R修改前4302份跟踪输入中，只有3RTL及`sw/Makefile`这4个原文件改变，另外新增2个C；其余4298份内容/权限和61个符号链接属性保持，原两处诊断修改及HEAD保持。F、本地FPGA、原配置/wrapper、其他依赖及历史产物未改。详见归档中的`protection_check.json`。

服务器工程外备份位于 `~/CheshireAra_maintenance/p6_fix_20261025/`，本地副本位于[本轮备份目录](../../../../.e01_backups/p6_fix_20261025/)。`before.tar.gz`含4份原文件、两份新增文件原本不存在的记录；`after.tar.gz`含6份最终文件及最小差异。两版均已在独立目录实际恢复并比较内容/权限，生产源码未回退。初次默认tarfile解包去掉组写权限的验证失败有单独记录，显式恢复归档权限后通过；回退时须按`rollback.md`比较当前文件与after清单，保护后续修改，不能整包覆盖或reset/clean。

完整小型证据[归档](../../../../.e01_backups/p6_fix_20261025/p6_fix_evidence.tar.gz)含184份数据成员及清单；服务器、本地SHA256均为 `036aa84592e62f0cc772c10a0b49af38c4594ec51bd7c3b2706cca4c4e38d3bb`，成员内容/长度/权限重读核对通过。大体积CPU trace及simv留服务器，位置与SHA记录于`summary.json`。本地5份文档修改前版本保存在`docs_before/`。静态复核记录见[compress](../../../../.e01_backups/p6_fix_20261025/compress_review.md)、[数据归属](../../../../.e01_backups/p6_fix_20261025/scalar_review.md)、[软件入口](../../../../.e01_backups/p6_fix_20261025/software_review.md)；这些复核不计作额外仿真。

本轮P6在R实施和仿真完成；没有进行F同步、Git提交/推送或公开上游操作。


<a id="p6-reference-formal-sync-20261025"></a>

## 12. P6提交GitHub及正式工程同步验证（2026-10-25）

### 12.1 授权、版本和目录映射

用户明确授权先将R的P6提交GitHub，再同步F并按其目录构建、仿真。R提交/推送依据本轮开头明确授权；所引用Prompt末尾“不提交/推送”用于F同步阶段。本轮由本地主Agent经既有Windows SSH执行，没有委派服务器Agent，也没有新增同步框架。

R输入HEAD `5986ba021e1a0d30dbdb5ecb2cfa230a2c35947c`，6份P6工作区文件均与第11节验收归档哈希一致。已单独提交为 `cb20a03c063d208d17eef024a1f6491152d509e8`，仅含3份RTL、`sw/Makefile`及2份C；dry-run、正常快进push及`ls-remote`读回均成功，个人私有仓库main为同一提交。两处原诊断修改继续保留，未混入提交。R此次没有重新仿真，沿用相同源码的第11节结果。

F没有`.git`，以实施前1051份非输出输入的内容/权限快照固定版本；没有初始化仓库或为F提交/推送。三份目标RTL与R父提交逐字一致后，才应用P6，配套端口连接和原P1–P5修复保留。文件映射为：

| R路径 | F路径 | 本次处理 |
| --- | --- | --- |
| `.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/lane/lane_sequencer.sv` | `src/cheshire_soc/ara/hardware/src/lane/lane_sequencer.sv` | 请求互斥；最终内容与R提交一致 |
| 同组件`masku/masku.sv` | `src/cheshire_soc/ara/hardware/src/masku/masku.sv` | 广播、compress及端口连接；最终内容与R提交一致 |
| 同组件`masku/masku_operands.sv` | `src/cheshire_soc/ara/hardware/src/masku/masku_operands.sv` | 数据归属；最终内容与R提交一致 |
| `sw/tests/p6_maskb.c`、`sw/tests/p6_compress.c` | `sw/tests/regressions/`下同名文件 | 两份源内容不改，F沿现有维护目录放置 |
| `sw/Makefile`五条测试规则 | F `sw/Makefile` | 仅增加7行，沿用`direct_test`、本地库/头/链接及OUT机制，合入已有regressions |

Make数据库对照确认：默认`all`仍7个ELF，可选Ara仍11个，维护组24→29；总计47个ELF，日常＋维护为36个。F不增加`p6-regressions`分组或新的仿真TARGET。P6保留原ELF名，四个MaskB目标固定KIND=0/1/2/3；全部采用SPM、相同编译宏语义和`-fno-tree-vectorize -fno-strict-aliasing`。运行用F `TARGET=soc`，P6五项无附加参数，没有移入R实验观察器。

`provenance/source_manifest.json`复用原来源、revision和维护记录，更新7个原条目、新增2份C条目；其余979条目保持，合计988条。3份RTL与2份C的最终哈希等于R提交内容；Make保留F组织。8份历史patch、`p1_p5_sync_20261024.json`等原始快照保持。更新F现有README及两份用户指南，ELF/TARGET表已列出五项P6的编译选项、运行参数、用途和本次结果。

### 12.2 F自身构建与实际仿真

软件使用F `sw/Makefile`在新OUT `sw/build/p6_sync_20261025/`构建11个指定ELF及dump、map和本地库；返回0。硬件用未改的`sim/scripts/compile.cheshire_soc.sh`，`TARGET=soc`、新`BUILD_DIR=sim/work/p6_sync_20261025`；返回0。每例均由F原`start.cheshire_soc.sh`展开并运行，独立`RUN_DIR=BUILD_DIR/<ELF基本名>`，串行、无波形、`SIM_TIMEOUT=600`，默认Serial Link ELF装载。compile/start/check_result及集中配置、wrapper、TB均保持。

下表三返回值顺序为目标/simv/入口；耗时含本例start的展开与运行，不是硬件执行周期。P2附加参数沿F指南，原监视器保留。

| ELF | 本次实际检查 | 结果及返回值 | 主机总耗时/s |
| --- | --- | --- | --- |
| `p6_scalar_delay.elf` | 延迟标量提取，120组/7800项、0错 | PASS，0/0/0 | 126.459 |
| `p6_scalar_int.elf` | 即时整数提取，120组/7800项、0错 | PASS，0/0/0 | 118.070 |
| `p6_scalar_fp.elf` | FP32提取，120组/7800项、0错 | PASS，0/0/0 | 117.815 |
| `p6_compress_scalar.elf` | 全选compress后提取，120组/7800项、0错 | PASS，0/0/0 | 119.884 |
| `p6_compress.elf` | 全不选/跨字/尾部保持，28组/7252项、0错 | PASS，0/0/0 | 215.625 |
| `p2_vmfpu_order.elf` | 835项、0错；原VMFPU/mask/scalar监测开启 | PASS，0/0/0 | 91.948 |
| `p2_vcpop_boundaries.elf` | 124项、0错；原mask/scalar监测开启 | PASS，0/0/0 | 85.891 |
| `p2_scalar_overlap.elf` | 483项、0错；原scalar监测开启 | PASS，0/0/0 | 94.151 |
| `vector_fixed.elf` | 22字节复制、0错 | PASS，0/0/0 | 110.073 |
| `rvv_bounds.spm.elf` | 5976项、0错 | PASS，0/0/0 | 298.311 |
| `fmatmul.spm.elf` | 结果校验Passed. | PASS，0/0/0 | 490.094 |

**F本次11次运行全部PASS。** P6五项共508组/38452项、0错，与R基准一致；P2三项共1442项、0错，RVV 5976项、0错，向量复制和fmatmul校验也通过。软件输出、UART、入口JSON、断言/超时均实际检查，不只依据simv返回0。P6测试内容与R相同，覆盖及未测范围继承第11.3节；没有因F通过扩大为任意RVV程序、lane/VLEN/队列/SEW/LMUL、综合或ASIC验收。#479未纳入，原ROM/SPI、LLC、FS/libgcc及P3非整拍尾部等限制保持。

编译来源快照在BUILD_DIR保存；测试结果均记录同一快照哈希。本次运行结束后只更新了3份用户文档及其来源维护项，最终清单哈希因此变化；6份P6代码/Make文件与编译快照一致，无RTL变化，未为文档更新重复编译或仿真。

### 12.3 保护检查、备份和重跑

F实施前1051份非输出输入中，最终仅8个原文件变化（3RTL、Make、来源清单及3文档），其余1043份内容/权限/符号链接属性保持；新增2份C，未覆盖未跟踪文件。R原4302份跟踪输入按P6已验收内容重查通过，两处原诊断修改和P6内容均保持。本地FPGA工程、其他依赖、配置/wrapper、脚本、历史产物和来源历史未清理或升级；未调用Bender、重生成Boot ROM、综合、板测或公开上游操作。

服务器备份及证据：`/home/zhaowy24/CheshireAra_maintenance/p6_sync_20261025_054434/`；本地[同份目录](../../../../.e01_backups/p6_sync_20261025_sf0kdpzo/)及[完整归档](../../../../.e01_backups/p6_sync_20261025_sf0kdpzo/p6_sync_evidence.tar.gz)。归档含123份数据成员及清单，SHA256为 `f956dbe06ef06426b3a3d92beb173d1fe4a138dbc69dddd80b16787d91dfad7b`；服务器和本地重读核对内容/长度/权限一致。前后局部源码包均在独立目录实际恢复校验，生产工程未回退；恢复时先按`formal_after.json`核对后续修改，再仅处理8个变化原文件和2个新增文件，不能整包覆盖。详见备份的`rollback.md`。

R增量`p6_commit.bundle`在两地保存并验证哈希，要求已有父提交5986ba02，不是可独立重建全仓库的完整bundle。CPU trace及最终VCS仿真器留服务器，位置与SHA在[结构化结果](../../../../.e01_backups/p6_sync_20261025_sf0kdpzo/summary.json)；11份独立result/log、展开日志、构建命令、映射、前后源码和来源检查已归档。本地本轮6份文档输入（含已有修改）在备份`docs_before/`保存，本次只更新其中5份进展文档，AGENTS约束保持。

沿F入口重跑compress例（新RUN_DIR以保护本次产物，先按需重新Make/compile）：

```bash
cd /home/zhaowy24/CheshireAra
TARGET=soc BUILD_DIR=sim/work/p6_sync_20261025 \
  RUN_DIR=sim/work/p6_replay_01 \
  BINARY=sw/build/p6_sync_20261025/p6_compress.elf \
  ./sim/scripts/start.cheshire_soc.sh
```

本轮R提交/推送、F映射同步、独立验证及文档更新完成；两工程保留各自目录和入口。

<a id="p7-reshuffle-assessment-20261025"></a>

## 13. P7：同源目的重排、目的EMUL与VID输出修复

2026-10-26，当前状态为**第二次实施在R修复并验证通过，F未同步、LLVM迁移未恢复**，详见[13.5](#p7-emul-local-fix-20261025)。13.1–13.3保留实施前评估，13.4保留第一次候选不足及回退历史。无提交推送或上游发布。

实施前评估输入为R `cb20a03c063d208d17eef024a1f6491152d509e8`及原两处诊断修改，本地HEAD `ca8395677691ba8d9d226ce4b5b5b49192b90f1c`。评估时SSH确认R/F的`ara_dispatcher.sv`内容相同，SHA256均为`f5108be10340ca3b6d1090ba343152e88f9214364ac14b0e9ec50a062954d0c1`；当时两工程都尚无本修复。LLVM失败、单变量对照、GCC/LLVM标量控制和257项字节模型沿用[迁移计划第10节](../planning/llvm_toolchain_migration_plan.md#llvm-vector-failure-analysis-20261025)，评估阶段未重新仿真。

### 13.1 上游已有同题候选，预计只改一个RTL模块

本轮通过GitHub只读接口确认[Ara PR #483](https://github.com/pulp-platform/ara/pull/483)为open、未合并，head为`6b664a2c7437b4b2bea51af17b8a26a20b6d38e7`。其描述正是“完整覆盖省去目的重排、同寄存器又省去源重排，最终都未重排”；示例为whole-load后原地FP减法，与本次原地整数加法属于同一控制条件。

该PR修改`hardware/src/ara_dispatcher.sv`新增7行、删除1行，另外一行CHANGELOG；没有附带测试文件。主要是明确`full_vd_overwrite`和`old_vd_is_source`，将目的重排条件改为`!full_vd_overwrite || old_vd_is_source`。其中旧目的参与计算包括显式vs1/vs2与vd相同，以及`use_vd_op`表示的隐式旧目的操作数。优先采用这个局部修复方向，保留来源，不升级Ara、不照搬PR基线的其他变化；PR勾选测试通过不替代本工程验证。

| 对象 | P7预计修改 | 估计规模 |
| --- | --- | --- |
| `ara_dispatcher.sv` | 修正旧目的仍被读取时的重排省略条件；复用现有重排状态机 | 约8行RTL差异，计注释/排版约10–20行 |
| VLSU、lane/VRF、SLDU、MASKU | 检查关联行为，初始方案不修改 | 0行；若验证证明需改数据通路，重新评估范围 |
| 一份P7 C测试 | 显式RVV汇编，GCC/Clang均可编译，避免依赖编译器是否选择原地分配；在同一文件容纳组合 | 预计约150–300行，以可读的输入、参考值及汇总检查为主 |
| 已有`sw/Makefile` | 复用测试宏增加一个显式维护目标 | 约2–5行；保持各工程分组和目录，不改默认日常目标 |

RTL预计仅增加组合判断，没有新增端口、状态寄存器或存储器。必要重排会消耗原本被错误省掉的执行周期，这是正确执行所需；未做综合，不能据行数估计面积、时序或PPA。

### 13.2 验证预算：约54组定向组合，R首轮约17次运行

一个P7测试ELF的核心矩阵为 **3种SEW（16/32/64）×2种LMUL（1/2）×4种寄存器关系（vd仅等于vs1、仅等于vs2、三者相同、目的与源分离）×2种VL（VLMAX、VLMAX−1）=48组**。先用EW8布局初始化，再切换计算宽度；全长检查有效数据，部分长度以tu检查保留尾部，不能要求ta尾部保持某个确定值。初稿额外6组包含非零vstart算术控制，实施时发现超出当前源码注明的支持范围；用户已批准将该两组替换为部分VL的VMACC/VMADD尾部检查，见13.4。每组有多个数据及保护检查，54组不等于54次仿真或只有54个数值比较。

| 执行组 | 预计新仿真次数 | 判据 |
| --- | ---: | --- |
| 同一P7定向ELF在旧RTL/候选RTL各一次 | 2 | 旧版应在已定位组合复现，候选消除错误；控制组结果保持 |
| 归档原LLVM自动向量ELF、原LLVM标量及原GCC标量ELF，在候选RTL各一次 | 3 | 不重编掩盖失败；原465项由256错变0，标量及手写复制保持0错 |
| 既有12个回归目标 | 12 | `p1_vstu_wrap`、P2三项、`p3_div_flags`、P6五项、`rvv_bounds.spm`、`fmatmul.spm`；按原比较数/完成标志/入口结果/断言检查 |
| **R首轮合计** | **约17** | 预计1–2小时串行主机仿真预算，另加一次候选RTL编译、测试编写与定位；不是承诺工期 |

预算参考本机已有每例约2分钟、RVV约5分钟、fmatmul约8分钟的历史记录，不把它当硬件性能；每例默认600秒，无波形。只有出现新的停滞、错误或无法定位的行为才追加诊断运行，不预先新增框架。旧/新输出各用新目录，实际原件、局部差异及恢复检查在实施时保存；不覆盖现有产物，不通过清理依赖解决问题。

如果17次通过，再按用户确认的实施范围决定F映射同步及独立验证；这些未计入17次。本次仅证明当前2 lanes/VLEN2048基线的P7覆盖，不能宣称所有RVV指令、配置或自动向量化程序正确；GCC对相同显式RVV序列的测试不等于已验证GCC自动向量器。更换/升级GCC版本不属于P7，LLVM原38项迁移验收也不能由这17次替代。相关掩码/归约/宽度不一致的其他上游问题不顺带纳入；若碰到则保存并区分原问题与新增回归。

### 13.3 建议与上游贡献

**建议作为P7修复。**本例是符合ISA的普通原地计算，依赖编译器始终避开它会使软件正确性取决于寄存器分配；自动向量化会频繁生成这类组合。修改小而验证范围明确，值得先在R验证#483局部补丁。

已有同题PR #483，成功后优先准备独立的最小复现、当前提交/配置、修复前后结果及回归用例，供该PR作者/维护者使用；不把重复补丁作为新发现提交。只有发现现有PR未覆盖且独立成立的差异，才评估补充PR。本轮没有发评论、提交、推送或创建PR。

以上评估阶段只更新本地报告、LLVM计划导航及主题交接；修改前文档保存在`.e01_backups/llvm_migration_20261025/p7_assessment_before/`，上游候选和当时输入摘要见同目录上层`p7_upstream_assessment.json`。该阶段服务器源码、工具链和历史产物保持；后续实施见下文。

<a id="p7-implementation-result-20261025"></a>

### 13.4 实施结果：固定候选不足以通过，已保护后回退

**实际范围。**用户随后批准详细计划，仅在R实施。输入HEAD仍为`cb20a03c063d208d17eef024a1f6491152d509e8`，WT、2 lanes、VLEN2048保持。只临时修改dispatcher、`sw/Makefile`并新增`sw/tests/p7_reshuffle.c`；局部补丁来源固定为Ara #483提交`6b664a2c7437b4b2bea51af17b8a26a20b6d38e7`，7增1删。没有照搬上游邻近`in_lane_op`差异，没有修改重排状态机、EMUL或EEW记录。GCC13.2构建定向ELF及dump，静态脚本重新分析/展开候选RTL；复用原P6观察模块和现有`run.py`，不调用Bender。Make候选将P7设为显式目标并从`all`排除，默认ELFS、P6组及原编译选项比对保持。

**测试修订。**初版仍包含第53/54组非零vstart加法。实际R的`hardware/src/lane/operand_requester.sv:317–319`注明架构非零vstart只支持内存操作；将它用于加法是本次规划疏漏。初版出现X/断言，不能作为合格的旧版数据错误复现，也没有关闭断言继续判PASS。用户明确批准“替换两组并继续P7”，于是仅将这两个调用改为e32/m2、VL=127（VLMAX−1）的VMACC/VMADD，使用`tu`检查第127项旧D保持。独立检查确认仍为54组、6144数据、4224保护区、109 CSR检查；新OUT构建成功。该修订版未运行，因为当时仍在结束的初版候选诊断另有第51组失败。

实际完成的是下列两次**初版诊断**，不是修订后的合格验收对照。两次使用完全相同ELF，SHA256为`ba36801aa752bcf6f21047975da33fb56cf236711ed26190468dfbace30522e3`。

| 初版诊断 | UART计数（组/数据/保护/CSR） | 数据等软件检查错误/失败组 | 运行判定及主机耗时 |
| --- | --- | --- | --- |
| 原P6 RTL | 54 / 6144 / 4224 / 109 | 2273 / 22；mask `003c151515151515`，含指定第27组 | `ASSERTION_OR_SIM_ERROR`；target=1、入口=2、simv=0；544.333秒 |
| #483局部候选RTL | 54 / 6144 / 4224 / 109 | 257 / 4；mask `003c000000000000`，即51–54组 | `ASSERTION_OR_SIM_ERROR`；target=1、入口=2、simv=0；545.873秒 |

候选的前50组软件检查未置失败位，包含48组核心加法矩阵和两组控制；不能据此称54组或P7通过。第51组为`vmacc.vv v24,v8,v16`、e32/m2、VL=128，第一个数据错误在索引64：实测`0xdc5bd2b9`，期望`0x09aa53b9`。它早于后面两个非零vstart控制，替换53/54不能消除这个失败。

**定位到的独立EMUL问题。**以下行号来自归档中的实际候选dispatcher，非本地旧依赖：

1. `ara_dispatcher.sv:1434–1435`在OPMVV入口将`ara_req.emul`默认设为`LMUL_1`，注释说明用于mask操作；`:1719–1733`的普通VMADD/VMACC没有恢复当前`csr_vtype_q.vlmul`。
2. `:3663–3668`用该EMUL设置重排次数，`:485–509`每个微操作只重排一个物理寄存器。因此m2旧目的`v24/v25`只处理`v24`，后64个e32元素所在的`v25`保持EW8布局。
3. `:3681–3694`的结果EEW记录同样按EMUL=1，仅更新`v24`。后面的`vs2r.v`使用EW8，发现两个寄存器的EEW标签不同而整理源；`:559–587`会跳过标签已是EW8的`v25`，但其中算术结果已经按EW32写入，最终存出的字节顺序也错。
4. 使用本轮SSH读取的R `hardware/include/ara_pkg.sv`（SHA256 `1db38551089ae654f7c0e20410ad05fc39a73a135d7d6d4344d7581ef14cff3d`）的2-lane EW8/EW32表建立独立字节模型，精确得到索引64实测值`dc5bd2b9`；模型预测前64项正确、后64项错误。内部EMUL/EEW信号及完整128项运行输出未逐项动态观测，后续三项预测值未与trace比对，不把模型当RTL验证。

这个VMACC场景在旧、新代码中的`full_vd_overwrite`都为假，原版也已请求目的重排；#483局部补丁没有改变该场景的分支。因此当前证据支持**已有的独立EMUL重排/记录缺口**，不支持称其为#483新引入的回归。继续修复需要改变此次明确保持的译码/EMUL或相关记录逻辑，已超出固定7增1删范围；没有扩大修改或更改期望值规避失败。

**17项修订验收逐项状态。**所有后续运行停止；原LLVM失败ELF已从失败归档提取并冻结（SHA256 `287c24efc299d167e972aeec5288188df1240d7004c099cae8605038bd5579de`），没有重编或拿活动目录同名文件代替，但本轮没有运行它，不能声称465项由256错变0。两标量及12份旧回归也只完成历史哈希核对/复制，没有新PASS。

| 序号 | 修订验收目标 | 本轮结果 |
| ---: | --- | --- |
| 1 | 修订P7 ELF / 旧RTL | 未运行；初版带断言诊断不替代此项 |
| 2 | 同一修订P7 ELF / 候选RTL | 未运行；初版候选51组失败后停止 |
| 3 | 归档原LLVM自动向量ELF | 未运行 |
| 4 | LLVM标量ELF | 未运行 |
| 5 | GCC标量ELF | 未运行 |
| 6 | P1 `p1_vstu_wrap` | 未运行 |
| 7 | P2 `p2_vmfpu_order` | 未运行 |
| 8 | P2 `p2_vcpop_boundaries` | 未运行 |
| 9 | P2 `p2_scalar_overlap` | 未运行 |
| 10 | P3 `p3_div_flags` | 未运行 |
| 11 | P6 `p6_scalar_delay` | 未运行 |
| 12 | P6 `p6_scalar_int` | 未运行 |
| 13 | P6 `p6_scalar_fp` | 未运行 |
| 14 | P6 `p6_compress_scalar` | 未运行 |
| 15 | P6 `p6_compress` | 未运行 |
| 16 | `rvv_bounds.spm` | 未运行 |
| 17 | `fmatmul.spm` | 未运行 |

**保护与实际回退。**服务器工程外目录为`/home/zhaowy24/CheshireAra_maintenance/p7_fix_20261025_205414/`；本地第二份为[本轮备份目录](../../../../.e01_backups/p7_fix_20261025/)。原件4份（两个本轮目标原件＋原两处诊断文件）在服务器及本地实际展开，内容/权限匹配；初版和修订后的3份候选文件也分别实际展开核对。回退前再次核对HEAD、4321项原跟踪输入和精确after哈希，仅两个预期原件发生变化；保存实际候选差异后，只恢复dispatcher与Make，将新C移动到`failed_sources/p7_reshuffle.revised.c`，未覆盖并行修改或删除证据。回退后4321项内容/权限、原Git状态、完整原Git差异全部匹配；F所查4项相关输入保持，未向F写入任何文件。

原件归档`before/before.tar.gz` SHA256为`4ec3ce4db9d5c98de40a1390c08aa48c0828316a9ad2207e26757cf0ccfb83d8`；本地准备包为`8966d0303a745cabe7bd3da7ea6a1fe9eb479f498e55574e5c5fdc0e4cfcdaa5`；修订after归档为`84dcdd139d70a68520f2d5676b0fff4181fe86493ddb0b58db3c7b8a54c49385`。修订ELF SHA256为`a4ac932e6551808145880047eb3ec25d490e3b48d49e039c151bfd92b8bf10ca`，已保存但未仿真。

候选旧/新simv、两次原始运行目录及trace继续保留在R的`work/`；逐文件哈希见本轮`evidence/diagnostic_results.json`。实际补丁、两版C/ELF/dump、原始结果/日志、上游快照、字节模型和回退结果均保存。[最终失败证据包](../../../../.e01_backups/p7_fix_20261025/failure_bundle.tar.gz)在服务器及本地各一份，SHA256 `b85d22b0ecae273ba440ccea74e4166e07d2fd437b5f7a2e517409200a6038b3`；服务器归档重读、本地实际展开108项内容/权限/大小全部匹配，见[本地恢复检查](../../../../.e01_backups/p7_fix_20261025/failure_bundle_local_check.json)。大trace不重复装包，保留原目录并记录哈希。当前R恢复到原GCC/P6基线；**P7未完成验收，LLVM迁移仍停止，F未同步，未提交、推送或对上游发表评论/创建PR**。LMUL4/8、非零算术vstart、其他指令/配置、GCC自动向量器及PPA均不在本轮验证结论内。

<a id="p7-emul-local-fix-20261025"></a>

### 13.5 第二次实施通过：目的EMUL分类、多寄存器等待与VID输出退休

输入和仿真记录为2026-10-25；2026-10-26完成结果核对及交付。

**授权及版本。**用户批准在R实施完整OPMVV目的EMUL分类，随后明确要求遇到相关新错误继续尝试最小、可综合的局部修复，取代原计划“非预期失败即停止”的限制。范围仍仅`/home/zhaowy24/CheshireAraPULP`；R HEAD `cb20a03c063d208d17eef024a1f6491152d509e8`、WT、2 lanes、VLEN2048保持，原两处诊断修改受保护。未向正式工程F同步、恢复LLVM迁移、提交推送或对上游发言。13.4保留第一次候选失败和回退历史，不代表当前R状态。

**最终修改。**P7沿用#483固定提交`6b664a2c7437b4b2bea51af17b8a26a20b6d38e7`的7增1删；本地修复分别补充目的EMUL分类、重排等待和VID载荷退休。dispatcher相对原件25增2删，VALU 7增2删，合计32增4删；没有新增端口、类型、硬件参数、状态寄存器或存储器。组合默认赋值、原状态及队列记账已独立复核；实际仅执行VCS编译和仿真，未执行综合、STA或PPA评估。

目的EMUL分类置于OPMVV原func6译码之后、寄存器对齐检查之前；默认分支不覆盖原赋值，非法编码/vtype/功能禁用仍由原异常路径处理：

| OPMVV类别 | func6/子编码 | 目的EMUL |
| --- | --- | --- |
| 平均加减 | `001000`–`001011` | 当前LMUL |
| 乘除余数 | `100000`–`100111` | 当前LMUL |
| 四种乘加 | `101001/101011/101101/101111` | 当前LMUL |
| 扩展 | `010010`，合法子编码2–7 | 当前LMUL；六种静态核对，仅VF2动态覆盖 |
| compress | `010111` | 当前LMUL |
| VIOTA、VID | `010100`的子编码16、17 | 当前LMUL |
| 普通整数归约、掩码、标量返回 | 保留各原译码 | 原单寄存器默认 |
| 合法扩宽分支 | 保留各原译码 | 原`next_lmul(...)`赋值 |

**两项进一步发现的错误及修复。**

1. 第10组`vwmaccu.vv`的源为e16/m1，目的为e32/EMUL2。仅#483候选会按EMUL2安排v24、v25重排，但退出只看CSR LMUL=m1而跳过WAIT_IDLE，可能使后续乘加与末次重排交错。旧#483候选中仅索引125、127错误：`32379ef1/898b3e1a`，期望`89d7a555/89d5e723`。本地在原条件追加`rs_lmul_cnt_limit_q != 0`，以实际已枚举的多寄存器组决定是否等待，复用原状态；同一控制ELF在中间候选中128项已全部正确。该等待可能减少与其他在途指令的执行重叠，未测性能影响。
2. 旧#483候选与中间候选的第14组输出相同，均为VL127/tu压缩的95项有效输出全部仍是旧D，33项尾部保持；中间候选前13组均正确。trace确认VL127、vstart0及CPU最后写入的mask首字`eeeeeeeeeeeeeeee`。开启已有P6只读监测后，同一ELF再次95错，`compress_accepts=1/commits=1/empty_done=1/final_idx_pushes=0/vd_captures=0`，说明走了空选择完成路径。结合源码，原因指向VID零载荷残留：实际VALU把包含VID的操作范围全部接收，SIMD ALU对VID默认输出0；该结果进入mask spill，而MASKU自己生成VID且不给此ALU载荷ready，下一条compress便可能误用残留零字。本地仅门控VALU的两处组合赋值：VID载荷不写mask spill，在原结果队列中本地退休，保留计数、指针和done；非VID逻辑与原逻辑等价。

上述内部链由实际源码、CPU输出与既有监测计数支持；未采内部波形，不能把未观测的逐拍顺序写成已测时序。

**测试入口及冻结输入。**新增同一份569行`sw/tests/p7_reshuffle.c`；Make仅7增1删，复用`direct_test`产生显式`p7_reshuffle.elf`和`p7_emul_controls.elf`，从默认all排除并读取各自.d，GCC13.2及P6分组/原编译选项保持。测试另关自动向量化与严格别名优化。两份ELF各构建一次，此后全部对照复用，不改变参考值：

- main SHA256 `fec0f4a7c96045abb6b118d2861fd765721d9306aac06e920ca51a6e9834b368`：54组、6144数据、4224保护区、109 CSR。
- controls SHA256 `66800815ef1279c88904959c6e856e29dc59b39d5afb6f2a140a62503efbea6e`：14组、1984数据、926保护区、29 CSR。
- 原LLVM失败ELF SHA256 `287c24efc299d167e972aeec5288188df1240d7004c099cae8605038bd5579de`，来自失败归档，不取活动目录、不重编。
- 旧P6 simv `b1b5afd70504fd9cdb4c67b319b5652b6bccbdfa802d46520d0a0f557de0e33f`；旧#483 simv `2c3ade0cc117d6dd02084c45e5afd442d42a86ea6dd474e9ca7e0bec2dd8cb49`，完整哈希及编译来源已记录。

**逐项运行。**串行、每例600秒、无波形，复用静态清单、已有监测和`run.py`；正例同时检查目标/入口返回、完成标志、UART检查及断言。旧控制的原预期掩码`3c1f`和实际`3e1f`都保留，没有改期望把额外失败判成合格负例。最终19个验收位置之外，保留中间候选2次和监测诊断1次，共22次实际运行。

| 实际顺序 | 原验收位置 | 用例/RTL | 实际结果 | 主机秒 |
| ---: | --- | --- | --- | ---: |
| 1 | 1 | 旧P6 / main54 | TARGET_FAIL；2272数据错、控制0错，第27组复现 | 564.576 |
| 2 | 2 | 旧#483 / controls14 | TARGET_FAIL；609错、mask=3e1f；原预期3c1f，额外第10组2错 | 352.643 |
| 3 | 附加A | 中间候选 / main54 | PASS；54组全部0错 | 453.381 |
| 4 | 附加B | 中间候选 / controls14 | TARGET_FAIL；仅第14组95错，控制0错 | 351.036 |
| 5 | 附加C | 中间候选 / 同ELF监测诊断 | TARGET_FAIL；95错；empty_done=1、final_idx_pushes=0 | 352.911 |
| 6 | 3 | 最终候选 / main54 | PASS；54/6144/4224/109全部0错 | 454.282 |
| 7 | 4 | 最终候选 / controls14 | PASS；14/1984/926/29全部0错；empty_done=0、final_idx_pushes=1 | 240.421 |
| 8 | 5 | 原LLVM自动向量ELF，未重编 | PASS；465/0，复制22字节0错 | 125.032 |
| 9 | 6 | LLVM标量对照 | PASS；465/0，复制22字节0错 | 125.189 |
| 10 | 7 | GCC标量对照 | PASS；465/0，复制22字节0错 | 141.675 |
| 11 | 8 | P1 VSTU wrap | PASS；4次store、64字节0错 | 156.753 |
| 12 | 9 | P2 VMFPU顺序 | PASS；835/0 | 64.625 |
| 13 | 10 | P2 mask边界 | PASS；124/0 | 58.510 |
| 14 | 11 | P2标量重叠 | PASS；483/0 | 66.182 |
| 15 | 12 | P3基础flags | PASS；177/0，污染计数0 | 44.488 |
| 16 | 13 | P6延迟提取 | PASS；7800/0 | 91.940 |
| 17 | 14 | P6整数提取 | PASS；7800/0 | 90.268 |
| 18 | 15 | P6浮点提取 | PASS；7800/0 | 90.523 |
| 19 | 16 | P6 compress后提取 | PASS；7800/0 | 93.076 |
| 20 | 17 | P6 compress边界 | PASS；28组/7252项0错 | 187.135 |
| 21 | 18 | RVV边界 | PASS；5976/0 | 270.934 |
| 22 | 19 | fmatmul | PASS；结果校验Passed | 462.535 |

最终候选17个正例全部PASS，其中原归档LLVM向量ELF的465项由256错变为0错，手写复制22字节0错；两标量各465/0，12项既有回归保持通过。两份定向测试共68组、8128数据＋5150保护＋138 CSR＝13416项检查0错。全部22次实际运行无断言记录：18 PASS（含中间候选main一次）及4次旧版/中间TARGET_FAIL，不能写成22次全PASS或原旧控制符合预期。合计约80.6分钟主机仿真耗时，不含构建和定位，不用于推断硬件性能。最终simv SHA256为`df3c05da06e9d394faf9a4afeaf5726cfb4b730bf907f2e54dac281da7d60845`；完整命令、ELF哈希、UART、断言与trace清单见证据包。

**保护、恢复与交付。**服务器工程外证据根为`/home/zhaowy24/CheshireAra_maintenance/p7_emul_fix_20261025_220012/`，本地为`.e01_backups/p7_emul_fix_20261025_220012/`。原dispatcher/Make/两处诊断原件，以及追加VALU原件，分别保存权限、哈希和Git差异，两地均实际展开；最终四份源码包两地恢复检查通过，SHA256 `d564d594856d925e96e29d0ec0c2392a075d055b374c137b7ff3b23c6aa00b3b`。旧失败源码、ELF、日志、trace及前轮备份未删除。回退只恢复三个原文件、将本轮新增C移入证据目录，须先确认after哈希未被后续修改；不得整树还原。

结束逐项检查4321项原跟踪输入，仅dispatcher、VALU、Make三项授权变化，其余4318项（含两处原诊断修改）内容/权限保持，HEAD仍为`cb20a03c`；新增C单独保留。F本轮未写，四项直接相关输入的结束哈希保持。完整[交付证据包](../../../../.e01_backups/p7_emul_fix_20261025_220012/p7_evidence_bundle.tar.gz)两地SHA256一致：`8811010b757e44a2210f91b5f867114614a3e538658f9af2b960f69537b8dc6d`。服务器重读及[本地实际展开检查](../../../../.e01_backups/p7_emul_fix_20261025_220012/bundle_local_check.json)共203数据成员/204总成员的内容、大小和权限匹配；大trace留原运行目录并记录SHA。可直接查看[完整源码差异](../../../../.e01_backups/p7_emul_fix_20261025_220012/final_evidence/production_changes.patch)及[结束保护检查](../../../../.e01_backups/p7_emul_fix_20261025_220012/final_evidence/final_check.json)。本轮保留R修复，不提交、不推送；LLVM迁移仍未恢复，F未同步。

**覆盖限制。**本轮动态结论限于所列SEW16/32/64、LMUL1/2矩阵及实际回归；扩宽控制为源m1/目的m2，扩展仅VF2动态覆盖。未执行LMUL4/8及VF4/VF8的P7定向矩阵、非零算术vstart、所有宽度/重叠关系或GCC自动向量器验收；实际operand_requester注明非零vstart只支持memory操作；完整分类不等于修复OPMVV所有功能。满VL compress尾部、源操作数分别计数和对齐、P3非整拍VL异常屏蔽、ROM限定告警、共享LLC旧失败和FS/libgcc边界不因本结果关闭。原LLVM特定程序通过也不能替代整套LLVM迁移验收。

<a id="p7-reference-formal-sync-20261026"></a>

### 13.6 P7同步正式工程、独立验证及参考工程GitHub提交（2026-10-26）

**结果。**按用户确认顺序，先将已验收P7从R映射到F，完成F独立构建及17项串行正例，再提交和推送R。R父提交`cb20a03c063d208d17eef024a1f6491152d509e8`，新提交[`4e30feec288f0157f2ae6c0fb9ea736314de902e`](https://github.com/lionelZhaowy/CheshireAraPULP/commit/4e30feec288f0157f2ae6c0fb9ea736314de902e)；personal/main重新读回一致，未推官方origin或创建上游PR。仅4份P7源码入提交，两处原诊断修改保持且未暂存；F无Git，未初始化或提交。LLVM迁移不在本轮实施范围，默认编译器仍为GCC13.2。

**实际同步。**两个Ara RTL在F与P7前原件逐字一致，按对应局部差异同步；dispatcher25增2删、VALU7增2删，没有配置/端口变化。C映射到`sw/tests/regressions/p7_reshuffle.c`，内容SHA256 `2655b406f7a9e15073c430c6bafb065432e1067c8f3b2f87120700c06817ed4a`与R相同。F Make仅增加4行、复用direct_test，维护目标29→31，默认7项/Ara11项和原flags保持；配置/wrapper/静态清单/已有TB不改。正式三份指南与现有来源清单同步更新。manifest988→989，仅6个原条目改变并新增C，其他982原条目保持；原source/source_sha256/revision及维护历史前缀保留，Ara revision仍是锁定上游版本，新增reference_commit记录本次R提交。

**构建与输入。**F使用自身`sw/Makefile`、`sim/scripts/compile.cheshire_soc.sh`与`start.cheshire_soc.sh`。新软件输出`sw/build/p7_sync_20261026_085142/`，硬件输出`sim/work/p7_sync_20261026_085142/`，没有调用Bender。14份ELF/dump重新构建：两P7及12回归；三归档ELF以普通文件复制到新OUT/frozen且核对原SHA，不从活动目录取同名文件、不重编。F两P7 ELF的哈希分别为`4df4cac5e1e9da6c16dda24fbda4073558e68d9a2e542e174d2df22420075ed9`及`75fb38454c060af58557840ac8c640929955d31a81713a13bc5afbf43558640e`，与R ELF整文件哈希不同；196/100条RVV编码及顺序逐条一致，不能称作同一份ELF。原LLVM向量ELF仍为`287c24efc299d167e972aeec5288188df1240d7004c099cae8605038bd5579de`。

**17次实际运行。**均为TARGET=soc、BOOTMODE=0、PRELMODE=1，每例600秒、无波形、串行且独立RUN_DIR。表中PASS同时满足target/simv/entry=0、status=PASS、errors空、正常完成及UART检查；P1/P2/P3另检查原监测。P1要求实际4存储及队列清空；P2 order要求两lane inputs=outputs>0、pair_pending_cycles>0、noncomp错绑0，三项标量监测rows>0/early=0/store_without_addrack=0；P3污染计数0。

| 次序 | F运行用例 | 实际检查 | 结果 | 主机秒 |
| ---: | --- | --- | --- | ---: |
| 1 | `p7_reshuffle` | 54组/6144数据/4224保护/109 CSR，全部0错 | PASS | 450.247 |
| 2 | `p7_emul_controls` | 14组/1984数据/926保护/29 CSR，全部0错 | PASS | 238.961 |
| 3 | `original_llvm_vector` | 465/0，复制22字节0错 | PASS | 124.974 |
| 4 | `clang_scalar` | 465/0，复制22字节0错 | PASS | 125.861 |
| 5 | `gcc_scalar` | 465/0，复制22字节0错 | PASS | 141.912 |
| 6 | `p1_vstu_wrap` | 4存储/64字节，协议计数及队列正确 | PASS | 155.937 |
| 7 | `p2_vmfpu_order` | 835/0，双lane真实重叠及监测0错 | PASS | 64.217 |
| 8 | `p2_vcpop_boundaries` | 124/0，监测0错 | PASS | 58.576 |
| 9 | `p2_scalar_overlap` | 483/0，监测0错 | PASS | 65.615 |
| 10 | `p3_div_flags` | 177/0，fflags污染0 | PASS | 44.727 |
| 11 | `p6_scalar_delay` | KIND0，120组/7800项0错 | PASS | 91.537 |
| 12 | `p6_scalar_int` | KIND1，120组/7800项0错 | PASS | 89.117 |
| 13 | `p6_scalar_fp` | KIND2，120组/7800项0错 | PASS | 90.095 |
| 14 | `p6_compress_scalar` | KIND3，120组/7800项0错 | PASS | 92.347 |
| 15 | `p6_compress` | 28组/7252项0错 | PASS | 185.851 |
| 16 | `rvv_bounds.spm` | 5976项0错 | PASS | 269.456 |
| 17 | `fmatmul.spm` | 矩阵结果Passed | PASS | 461.062 |

主机仿真耗时合计45.8分钟，不含构建/展开，不用于推断硬件性能。完整命令、ELF/entry/parser/simv哈希、UART及专用监测保存在[逐项结果](../../../../.e01_backups/p7_sync_20261026_085142/final_evidence/evidence/formal_runs.json)。start逐例重新展开，逐例simv哈希按实际记录，不强行假定相同。测试时manifest快照与最终活动清单不同，结束后仅补入三文档及实际commit元数据；编译RTL、软件和入口保持，见delivery_summary.json。R本轮未重跑仿真，使用13.5的相同源码既有验证。

**保护和恢复。**服务器备份`/home/zhaowy24/CheshireAra_maintenance/p7_sync_20261026_085142/`，本地`.e01_backups/p7_sync_20261026_085142/`。F修改前7原件、新C原先不存在，修改后8文件；R前后6文件（4P7及2诊断），均保存内容/权限，并在两地实际展开比较。F全部1053份非输出原输入中仅7份变化、其他1046份保持；新增C1份。R全部4394输入（4393跟踪项＋原未跟踪P7 C；共4244个常规文件、149个符号链接及1个未初始化SDK空子模块目录）内容/权限/链接目标保持，Git提交只改变版本记录。全程未删除历史产物。

[两地交付包](../../../../.e01_backups/p7_sync_20261026_085142/p7_sync_evidence_bundle.tar.gz) SHA256 `3313efa092859b6a324a16544cc10e0113f8bc3dc6fb6a0a29e538650e555a7f`，176个成员的内容、大小和权限重读一致，见[本地展开检查](../../../../.e01_backups/p7_sync_20261026_085142/delivery_bundle_check.json)。R增量bundle需已有父基线`cb20a03c`，服务器git bundle verify通过、本地已保存。完整trace保留F运行目录并在run_files.json记录哈希，不为归档重复拷贝。回退F前先核对本轮after哈希及后续修改，仅合并恢复7原文件、将新增C移入证据目录；R已发布提交不能以reset/强推撤销，若需撤销另做反向提交并保留诊断修改。

**准备阶段记录。**首次候选上传被系统安全解包清除组写权限，第二次只读Make变量比较受到stdin临时路径影响，两次均在生产写入前停止检查；恢复候选清单权限、为只读变量比较显式指定SW_ROOT后继续，记录保留。两次不是RTL或仿真失败。提交前检查另修正了未初始化SDK空子模块目录的文件类型处理；git add因.bender父目录忽略提示返回非零，但实际只暂存了4份目标文件，逐份核对blob哈希后仅对这4个路径显式add -f继续。原脚本和说明保留，未改变RTL、ELF或17次仿真结果。

**范围。**本轮验证仍限WT、2 lanes、Ara VLEN2048及本矩阵；LMUL4/8、VF4/8、非零算术vstart、满VL compress尾部、按操作数计数/对齐、P3非整拍尾部、ROM padding限定告警、共享LLC及FS/libgcc边界保持。没有综合、PPA、板测、LLVM新构建或GCC自动向量器整体验收。
