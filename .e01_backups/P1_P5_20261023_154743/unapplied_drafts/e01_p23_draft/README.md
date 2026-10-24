# P2/P3 定向用例草稿

状态：2026-10-23 本地草稿。只读了现有 `sw/tests/rvv_bounds.c` 和相关 `vmfpu.sv`，未编译、未运行，未修改服务器、共享文档或原 R/F。这两份文件供主 Agent 纳入已授权的隔离阶段 B；不构成通过证据。

沿用当前测试的 `cheshire_start/end`、整数 `printf`、VS 设置以及 SPM `0x100...` 加 `0x04000000` 到 `0x140...` 的无缓存别名。当前 `spm.ld`/`common.ldh` 将对象链接至 `0x10000000` 起的64 KiB；两个草稿先检查各自向量缓冲区完全位于该范围，否则打印 `P2/P3_PRECONDITION_FAIL` 并停止，不能用于 DRAM 链接。别名依赖当前地址映射及链接位置，不是通用运行约定。保留当前 CRT 的 FS 启动修正，只检查 FP 已启用，不断言 FS Dirty 行为。输入和期望值全部用整数位模式准备，不依赖编译器折叠浮点表达式；FP32/64 都使用 RNE。保存并恢复 frm，不新增公共测试框架。

## P2：p2_vmfpu_order.c

| case_id | 当前短 VL | 连续指令 | 检查内容 |
| --- | --- | --- | --- |
| 640 / 320 | e64 VL2 / e32 VL4，LMUL1 | `vfadd v8,v2,v4` → `vmfeq v10,v12,v14` | 两条没有数据依赖，vd 不重叠；加法各元素、比较有效 mask 位、popcount、mask 写入边界、五个 fflags 都为0 |
| 641 / 321 | 同上 | `vfadd v8,v2,v4` → `vfsgnj v10,v12,v14` | 两条没有数据依赖，vd 不重叠；两个向量结果和 fflags |
| 642 / 322 | 同上 | 两条均加 `v0.t` | v0=0x05；有效元素结果，mu 保留的无效元素和 fflags |
| 643 / 323 | 同上 | `vfadd v8,v2,v4` → `vfsgnj v10,v8,v14` | 第二条显式依赖第一条，作为有依赖的有限对照 |

两条主触发指令放在同一个 `asm volatile` 中，中间没有读回、CSR、fence 或函数调用。数据及目的初值先载入；主触发只含精确、有限加法/比较/符号注入，避免 P3 除法缺陷干扰。默认每种重复8次；重复是观察机会，不代表必然重叠。结果通过 `vmv.x.s`，比较结果通过 `vcpop.m` 建立向量到标量的依赖，之后 `fence`、读 fflags。内存结果由当前工程已有的无缓存别名/fence 约定检查。e32 的 `vmv.x.s` 符号扩展在 C 中转换回 uint32_t。

预期结束标记 `P2_DONE c=... e=0 repeat=8`，成功返回0，失败返回42。仍使用当前启动/仿真器结果检查入口，不能仅凭该标记或 simv 返回0认定通过。`p2_case_id` 可用于关联观察，写入发生在准备阶段，不作为精确发射时刻。

`vcpop.m` 也引入 mask 计数路径。若只有 lane=92 的 popcount 检查失败，而 `vsm` 有效 mask 位和加法结果正确，应单列为辅助检查失败，不能直接归因 #482。当前 VL2/4 的静态检查未发现该辅助路径的已知触发条件，但草稿尚未实测。

### P2 VMFPU 最小观察建议

普通运行不开波形。若已有临时文本观察手段，主 Agent 可在隔离候选的每个 lane 的 `vmfpu` 层级记录以下信息；层级以当前 elaboration 为准，不硬编码别的版本的 testbench 路径。不要把临时观察写回原 R/F。

1. `vinsn_issue_q_valid`、`vinsn_processing_q_valid`；两者的 `op/id/vd/vtype.vsew`；`issue_cnt_q`、`to_process_cnt_q`；输入 `vfpu_in_valid && vfpu_in_ready`，输出 `vfpu_out_valid && vfpu_out_ready`。
2. `vinsn_issue_lat_d`、`vinsn_processing_lat_d`、`latency_stall`、`operands_valid`、`result_queue_full`。旧版另有 `latency_problem_d/q`；候选按其实际 diff 对应，不能要求被移除寄存器继续存在。
3. `vfpu_result` / `vfpu_processed_result`、`unit_out_result`，以及入队时 `result_queue_d[result_queue_write_pnt_q].id/addr/wdata/mask/be`。当前入队 id/addr 来自 **processing** 指令，因此返回顺序错会把数据绑定到错误目的。`vfpu_tag_in/out` 在当前路径携带 mask，**不是指令 id**，不能用它证明高低延迟指令身份。

应分别记录以下证据，不能只写“连续汇编已覆盖”：

- 高延迟 `VFADD` 已发生输入握手，结果尚未被输出接受；低延迟 `VMFEQ` 或 `VFSGNJ` 已在 issue 端等待，两者 id 不同。e64/e32 当前 compute 延迟分别5/4，NonComp 为1；旧分类函数漏了 VMFEQ，不能拿旧函数给出的“比较延迟”当真实执行延迟。
- 低延迟指令的输入握手与高延迟输出握手的实际间隔、返回顺序、目的 id/addr；仅存在同时 pending，不足以证明抢先返回。`result_queue_full` 或缺少操作数造成等待时，不把它误计为 latency_stall 的效果。
- 候选在上述 hazard 条件下及时阻止低延迟握手，并在允许后正确处理两条结果。比较结果在当前代码通过 MaskUnit 分支处理，需检查 `mask` 路由及最终 v10 的有效 mask 位，不能只看一般向量寄存器写端口。
- 若旧版实际错误且候选通过，保留两边相同 ELF 的输入/输出与这些事件；若旧版通过、没有出现目标重叠或抢先返回，只能报告“功能回归通过；该触发尚未复现”。不得宣称旧版一定应失败或功能 PASS 已证明 #482 修复。

## P3：p3_div_flags.c

标量/向量分别覆盖 FP32、FP64：四种正负零的 0/0（NaN，**仅 NV=0x10**）；正负有限数/正负零（符号正确的 infinity，**仅 DZ=0x08**）；正常精确除法（flags=0）。向量 VL4、LMUL1，另有 mask=0x09：lane1 的 0/0 和 lane2 的 finite/0 不参与，只剩正常精确结果，flags=0，未激活目的保留1024。

向量混合激活的 NV/DZ lane 应得到0x18。标量和向量另各执行一次先 0/0、再 finite/0 的序列：第一条读0x10，第二条不清除后读0x18，验证累积。第二条操作数准备只用整数/搬运指令，不能插入会改 fflags 的 FP 运算。全部读取比较完整五位 fflags：NV/DZ 之外 OF/UF/NX 必须为0。

NaN 只检查 exponent 全1且 fraction 非0，不限定 payload/符号。Infinity 和正常精确结果逐位比较。每个单例在操作数准备完后清 fflags，标量先 `fmv.x.w/d` 取得依赖结果再读 CSR；向量先结果 store、`vmv.x.s` 依赖和 fence，再读 CSR。不要把它简化成紧跟 vfdiv 的独立 `csrr`。

预期结束标记 `P3_DONE c=... e=0`，成功返回0，失败返回43。标量 case_id 为10000+宽度×100+下标；向量为20000+宽度×100+下标。低版本按官方问题预期 0/0 会多 DZ，但是否在本工程重现，以主 Agent 的旧版实测为准。所有操作数均为零、正常有限数，不含 subnormal，因此本稿不验证另一个 MVP #16，也不验证 FS Dirty。

## 纳入阶段 B 前的检查

- 按现有独立软件入口/隔离参考入口编译；沿用当前工具链，不增加依赖。固定向量寄存器 clobber 写法与当前 `rvv_bounds.c` 相同，但本稿尚未确认汇编器诊断。
- 编译后人工核对反汇编：P2 主指令对相邻、寄存器不变；P3 设置/读取 fflags 与结果依赖顺序符合上述要求。防止编译器在汇编块之外引入未考虑的自动向量化；沿用当前已接受的测试编译选项。
- 同一候选前后使用同一测试 ELF、输入、配置和测试入口。P2/P3 分开执行，P3 建议记录标量/向量及 FP32/64 分项；失败记录不掩盖此前候选结论。
- 两个草稿只补当前具体缺口；不代替既有 HelloWorld、RVV bounds、fmatmul32 等受影响回归，不等于完整 ISA/ASIC 验收。不为了让旧版失败添加特例或扩大参数扫描。
