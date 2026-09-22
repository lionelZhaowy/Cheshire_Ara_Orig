# CVA6 配置参数手册

返回 [配置导航](README.md)。本页逐项覆盖当前快照的 `cva6_user_cfg_t`，以 `cv64a6_imafdcv_sv39` 为向量基准。不是所有上游 CVA6 版本的通用参数承诺。

## 1. 参数生效顺序

```text
源码清单选择一个 cv*_config_pkg.sv（共同定义 cva6_config_pkg）
    → cva6_config_pkg::cva6_cfg（cva6_user_cfg_t）
    → cheshire_pkg::gen_cva6_cfg(Cfg) 覆盖 SoC 相关字段
    → build_config_pkg::build_config() 计算 cva6_cfg_t
    → cva6 实例与 Ara 实例使用同一份 Cva6Cfg
```

主要源码：[字段类型](../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/include/config_pkg.sv)、[向量 profile](../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/include/cv64a6_imafdcv_sv39_config_pkg.sv)、[派生函数](../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/include/build_config_pkg.sv)、[SoC 覆盖函数](../../hw/cheshire_pkg.sv)。`CVA6Config*` 局部常量主要是填写结构体的辅助名称；硬件最终读的是结构体和派生配置。不能只搜索一个 localparam 就认定最终值。

名称 `cv64a6_imafdcv_sv39` 表示这个 profile 的 RV64、I/M/A/F/D/C/V 组合与 Sv39 翻译配置。不是可以任意拼字母的配置生成器。当前 I/M 并没有在该 user 结构体中提供独立 `RVI`/`RVM` 字段。

## 2. 两个重要 profile 的实际差异

| 项目 | 根构建默认 cv64a6_imafdchsclic_sv39_wb | Ara 入口 cv64a6_imafdcv_sv39 |
| --- | --- | --- |
| RVV / RVH | 0 / 1 | 1 / 0 |
| RVSCLIC（profile 原值） | 1 | 0 |
| RVSCLIC（DefaultCfg 覆盖后） | 0 | 0 |
| RVZCB / RVZiCond | 1 / 1 | 0 / 0 |
| I-cache | 16 KiB，4 way，16 byte/line | 4 KiB，4 way，16 byte/line |
| D-cache | 32 KiB，8 way，16 byte/line，WB | 8 KiB，4 way，32 byte/line，WT |
| DcacheFlushOnFence | 1 | 0 |
| NrPMPEntries 原值 → SoC 默认 | 8 → 0 | 8 → 0 |

根 profile 来源：[标量配置包](../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/include/cv64a6_imafdchsclic_sv39_wb_config_pkg.sv)。WB=写回，WT=写穿；WT 也有写缓冲，不意味着与所有 DMA 自动一致。切 profile 会同时改变多项硬件，不只是开关 V。

## 3. 全部用户配置字段

“集成后”中的 `cfg.*` 指 Cheshire 配置字段；“同左”表示 gen_cva6_cfg 没覆盖它。表中数值是当前向量 profile 的源码值；数组用紧凑表达。

| 字段 | 向量 profile 原值 | 集成后来源/覆盖 | 含义与注意点 |
| --- | --- | --- | --- |
| `XLEN` | `64` | `同左` | 整数寄存器位宽，当前 RV64；改为 RV32 涉及 profile、软件 ABI、总线和 Ara 集成，不是一个局部优化。 |
| `VLEN` | `64` | `同左` | CPU 虚拟地址容器位宽，当前 64；Sv39 有效虚拟地址模式由 build_config 派生。不是 Ara 向量长度。 |
| `RVA` | `1` | `同左` | 原子指令扩展 A；主存通路依赖原子适配器。 |
| `RVB` | `0` | `同左` | 位操作扩展总开关；具体子扩展支持还需看 decoder。 |
| `ZKN` | `0` | `同左` | 标量密码指令开关；当前关闭。 |
| `RVV` | `1` | `同左` | 向量扩展 V；派生 EnableAccelerator，是 Ara 工作必要条件。 |
| `RVC` | `1` | `同左` | 压缩指令 C；影响取指与解码，对软件 -march 有约束。 |
| `RVH` | `0` | `同左` | Hypervisor 扩展 H；向量 profile 关闭，根标量默认 profile 开启。 |
| `RVZCB` | `0` | `同左` | Zcb 压缩子扩展；当前关闭。 |
| `RVZCMP` | `0` | `同左` | Zcmp 压缩栈操作子扩展；当前关闭。 |
| `RVZCMT` | `0` | `同左` | Zcmt 压缩表跳转子扩展；当前关闭。 |
| `RVSCLIC` | `0` | `cfg.Clic` | CLIC 扩展支持；最终被 Cfg.Clic 覆盖。 |
| `RVZiCond` | `0` | `同左` | 条件操作扩展；当前关闭。 |
| `RVZicntr` | `1` | `同左` | 基础计数器扩展；不要与 PerfCounterEn 的性能事件使能混为一谈。 |
| `RVZihpm` | `1` | `同左` | 硬件性能监视计数器扩展。 |
| `RVF` | `1` | `同左` | 标量单精度浮点；软件 ABI lp64d 还需要 D。 |
| `RVD` | `1` | `同左` | 标量双精度浮点；当前由 profile 的同一个 CVA6ConfigRVF 常量赋值。 |
| `XF16` | `0` | `同左` | 非标准半精度浮点选项；不控制 Ara 的 FPUSupport。 |
| `XF16ALT` | `0` | `同左` | 非标准替代 16 位浮点选项。 |
| `XF8` | `0` | `同左` | 非标准 8 位浮点选项。 |
| `XF8ALT` | `0` | `同左` | 非标准替代 8 位浮点选项。 |
| `XFVec` | `0` | `同左` | 标量 FPU 内的非标准 packed SIMD；不是 RVV/Ara 开关。 |
| `PerfCounterEn` | `1` | `同左` | 微架构性能计数逻辑使能；用于性能分析时保留并核对事件定义。 |
| `MmuPresent` | `1` | `同左` | 地址转换 MMU 硬件；不等于软件已经启用分页。 |
| `RVS` | `1` | `同左` | Supervisor 特权模式支持。 |
| `RVU` | `1` | `同左` | User 特权模式支持。 |
| `SoftwareInterruptEn` | `1` | `同左` | 软件中断支持；配合 CLINT/MSIP。 |
| `DebugEn` | `1` | `1` | CPU debug 支持；Cheshire 强制为 1。 |
| `DmBaseAddress` | `64'h0` | `AmDbg` | Debug Module 基址；由 Cheshire AmDbg 覆盖为 0。 |
| `HaltAddress` | `64'h800` | `'h800` | debug halt 入口偏移；Cheshire 强制 0x800。 |
| `ExceptionAddress` | `64'h808` | `'h810` | debug 异常入口偏移，不是普通 mtvec；profile 的 0x808 被改成 0x810。 |
| `TvalEn` | `1` | `同左` | trap value 寄存器信息支持，例如异常关联地址/值。 |
| `DirectVecOnly` | `0` | `同左` | mtvec 是否只支持 direct 模式；不控制 RVV 向量运算。 |
| `NrPMPEntries` | `8` | `cfg.Cva6NrPMPEntries` | PMP 表项数量；profile 为 8，但 Cheshire 默认覆盖为 0。 |
| `PMPCfgRstVal` | `{64{64'h0}}` | `同左` | PMP 配置复位值数组；生效项受 NrPMPEntries 限制。 |
| `PMPAddrRstVal` | `{64{64'h0}}` | `同左` | PMP 地址寄存器复位值数组；与权限/范围编码一起设置。 |
| `PMPEntryReadOnly` | `64'd0` | `同左` | PMP 项只读属性位图；须结合保护模型设计。 |
| `PMPNapotEn` | `1` | `同左` | PMP NA4/NAPOT 地址匹配支持开关。 |
| `NrNonIdempotentRules` | `2` | `2` | 非幂等物理区域规则数；Cheshire 覆盖为 2。 |
| `NonIdempotentAddrBase` | `见 profile 区域数组（集成时被覆盖）` | `gen_cva6_cfg() 重建，见第 4 节` | 非幂等区域基址数组；Cheshire 重建，避免对有副作用的设备按普通内存处理。 |
| `NonIdempotentLength` | `见 profile 区域数组（集成时被覆盖）` | `gen_cva6_cfg() 重建，见第 4 节` | 非幂等区域长度数组，byte；不是结束地址。 |
| `NrExecuteRegionRules` | `3` | `5` | 可取指区域规则数；Cheshire 覆盖为 5。 |
| `ExecuteRegionAddrBase` | `见 profile 区域数组（集成时被覆盖）` | `gen_cva6_cfg() 重建，见第 4 节` | 可取指物理区域基址数组；Cheshire 重建。 |
| `ExecuteRegionLength` | `见 profile 区域数组（集成时被覆盖）` | `gen_cva6_cfg() 重建，见第 4 节` | 可取指物理区域长度数组，byte；SPM 别名存在注释/实现差异，见 SoC 篇。 |
| `NrCachedRegionRules` | `1` | `3` | 可缓存物理区域规则数；Cheshire 覆盖为 3。 |
| `CachedRegionAddrBase` | `见 profile 区域数组（集成时被覆盖）` | `gen_cva6_cfg() 重建，见第 4 节` | CPU 可缓存区域起点数组；并不配置 LLC 或 DMA snoop。 |
| `CachedRegionLength` | `见 profile 区域数组（集成时被覆盖）` | `gen_cva6_cfg() 重建，见第 4 节` | CPU 可缓存区域长度数组；改变共享区时必须分别考虑 L1、LLC、设备路径。 |
| `CvxifEn` | `0` | `0` | 通用 CV-X-IF 使能；Cheshire 强制为 0，Ara 通过专用 accelerator/MMU 通路集成。 |
| `CoproType` | `config_pkg::COPRO_NONE` | `同左` | 通用 coprocessor 类型；当前 COPRO_NONE，不能因此推断 Ara 不存在。 |
| `NOCType` | `config_pkg::NOC_TYPE_AXI4_ATOP` | `config_pkg::NOC_TYPE_AXI4_ATOP` | CPU 外部互连类型；Cheshire 固定 NOC_TYPE_AXI4_ATOP。 |
| `CLICNumInterruptSrc` | `256` | `NumCoreIrqs + NumIntIntrs + cfg.NumExtClicIntrs` | CPU CLIC 中断源数量；Cheshire 用 16+内部源数+NumExtClicIntrs 覆盖。 |
| `AxiAddrWidth` | `64` | `cfg.AddrWidth` | CPU AXI 地址位宽，profile 为 64，SoC 默认覆盖为 48。 |
| `AxiDataWidth` | `64` | `cfg.AxiDataWidth` | CPU AXI 数据位宽，由 SoC AxiDataWidth 覆盖。 |
| `AxiIdWidth` | `4` | `Cva6IdWidth` | CPU 原生 AXI ID 位宽，Cheshire 固定 4；后续 serializer 可压缩。 |
| `AxiUserWidth` | `CVA6ConfigXlen` | `cfg.AxiUserWidth` | CPU AXI USER 位宽，由 SoC AxiUserWidth 覆盖；不是 FetchUserWidth。 |
| `AxiBurstWriteEn` | `0` | `同左` | CPU AXI burst 写支持选项；cache 类型和总线实现共同决定事务行为。 |
| `MemTidWidth` | `2` | `同左` | cache 内存事务标签位宽；派生 DCACHE_MAX_TX=2^MemTidWidth。 |
| `IcacheByteSize` | `4096` | `同左` | I-cache 总数据容量，byte；默认向量 profile 为 4 KiB。 |
| `IcacheSetAssoc` | `4` | `同左` | I-cache way 数，默认 4。 |
| `IcacheLineWidth` | `128` | `同左` | I-cache line 位宽，bit；128 bit=16 byte，别按 128 byte 算。 |
| `DCacheType` | `config_pkg::WT` | `同左` | D-cache 实现类型枚举；当前向量 profile 是 WT（写穿）。 |
| `DcacheIdWidth` | `1` | `同左` | cache 内部数据请求标识宽度；不等于 AXI ID 宽度。 |
| `DcacheByteSize` | `8192` | `同左` | D-cache 总数据容量，byte；默认向量 profile 为 8 KiB。 |
| `DcacheSetAssoc` | `4` | `同左` | D-cache way 数，默认 4。 |
| `DcacheLineWidth` | `256` | `同左` | D-cache line 位宽，bit；256 bit=32 byte，Ara invalidation 过滤器使用它。 |
| `DcacheFlushOnFence` | `1'b0` | `同左` | 实现是否把 fence 与 D-cache flush 关联；向量 profile 为 0，不能假定 fence 自动清 cache。 |
| `DcacheInvalidateOnFlush` | `1'b0` | `同左` | flush 后是否 invalidate 的实现选项；不等于全系统 cache coherence。 |
| `DataUserEn` | `0` | `同左` | CPU 数据附带 USER 信息的功能开关；SoC 仍会在外层写 AXI USER 原子标识。 |
| `WtDcacheWbufDepth` | `8` | `同左` | WT D-cache 写缓冲深度；WT 仍可能有未完成的缓冲写。 |
| `FetchUserEn` | `0` | `同左` | 取指附带 USER 信息的功能开关。 |
| `FetchUserWidth` | `1` | `同左` | 取指 USER 信息位宽；关功能时仍保留非零占位宽度。 |
| `FpgaEn` | `0` | `同左` | CPU 局部 FPGA 优化选项；profile 为 0，不等于工程没有 FPGA 技术单元。 |
| `FpgaAlteraEn` | `0` | `同左` | Altera 专用优化选择；不是所有 FPGA 的开关。 |
| `TechnoCut` | `0` | `同左` | CPU 技术相关切分选项；需核对目标实现路径，不作为初学者常改项。 |
| `SuperscalarEn` | `0` | `同左` | 双发射选择；当前 0，开启还会强制提交口数为 2，属于微架构变更。 |
| `NrCommitPorts` | `2` | `同左` | 提交端口数；当前 2 不表示每周期双发射。 |
| `NrLoadPipeRegs` | `1` | `同左` | load 结果通路流水寄存器数量；改变时需要检查延迟契约。 |
| `NrStorePipeRegs` | `0` | `同左` | store 通路流水寄存器数量。 |
| `NrScoreboardEntries` | `8` | `同左` | scoreboard 可跟踪的指令项数；派生事务 tag 位宽，非 cache 在途数。 |
| `NrLoadBufEntries` | `2` | `同左` | load buffer 项数；性能受存储延迟与依赖共同影响。 |
| `MaxOutstandingStores` | `7` | `同左` | 可挂起 store 数量；不要与 SoC AXI MaxTxns 简单相等。 |
| `RASDepth` | `2` | `cfg.Cva6RASDepth` | 返回地址预测栈深度；由 Cfg.Cva6RASDepth 覆盖。 |
| `BTBEntries` | `32` | `cfg.Cva6BTBEntries` | 分支目标缓冲项数；由 Cfg.Cva6BTBEntries 覆盖。 |
| `BHTEntries` | `128` | `cfg.Cva6BHTEntries` | 分支历史表项数；由 Cfg.Cva6BHTEntries 覆盖。 |
| `InstrTlbEntries` | `16` | `同左` | 指令 TLB 项数；只影响转换缓存，不改变页表模式。 |
| `DataTlbEntries` | `16` | `同左` | 数据 TLB 项数。 |
| `UseSharedTlb` | `0` | `同左` | 是否使用共享 TLB；当前关闭。 |
| `SharedTlbDepth` | `64` | `同左` | 共享 TLB 深度；UseSharedTlb=0 时不是启用的容量。 |

## 4. CPU 物理地址属性与 SoC 地址地图

默认 `Cva6ExtCieLength=0x20000000`、`Cva6ExtCieOnTop=0`：

| 属性 | gen_cva6_cfg 生成的默认区域（排他终点） |
| --- | --- |
| 非幂等 | [0,0x10000000)、[0x40000000,0x80000000) |
| 可缓存 | SPM [0x10000000,0x10020000)、DDR [0x80000000,0x100000000)、扩展 [0x20000000,0x40000000) |
| 可执行 | Debug [0,0x40000)、Boot ROM [0x02000000,0x02040000)、SPM 规则 [0x10000000,0x10040000)、DDR 和上述扩展区 |

“幂等”指重复访问不会造成新的设备副作用，典型反例是读取即出队的 FIFO 寄存器。这些 PMA 属性不是 AXI 路由表、不是 PMP 权限表，也不是页表。设置可缓存属性不会创建 RAM；扩展 slave 地址规则也不会自动使 CPU 采用正确属性。

`NrMaxRules=16` 是数组槽位上限，实际生效条数由 `Nr*Rules` 控制。区域数组使用基址+长度；Cheshire 地址路由数组则使用起点+排他终点，修改时不要混用。

## 5. 常见派生字段：读懂即可，通常不直接改

| 派生字段 | 当前向量基准 | 计算/意义 |
| --- | --- | --- |
| EnableAccelerator | 1 | 来自 RVV，驱动 Ara 专用交互 |
| NrIssuePorts / NrCommitPorts | 1 / 2 | 单发射，最多两个提交口 |
| NrWbPorts / NrRgprPorts | 5 / 2 | 回写口/整数寄存器读口，按加速器与发射模式派生 |
| TRANS_ID_BITS | 3 | clog2(8 项 scoreboard) |
| FpPresent / FLen | 1 / 64 | 由浮点格式开关派生 |
| PLEN / VLEN / SV | 56 / 64 / 39 | CPU 内部物理地址容器/虚拟地址容器/翻译有效模式；SoC AXI 地址仍为 48 |
| MODE_SV / PtLevels | ModeSv39 / 3 | 本地 build_config 对 RV64 的派生，不能只把 VLEN 改 48 就得到 Sv48 |
| ICACHE_INDEX_WIDTH / TAG_WIDTH | 10 / 46 | clog2(4096/4)；56−10 |
| DCACHE_INDEX_WIDTH / OFFSET_WIDTH / TAG_WIDTH | 11 / 5 / 45 | clog2(8192/4)、clog2(32)、56−11 |
| DCACHE_NUM_WORDS | 64 | 源码名称如此：2^(11−5)，对应每 way 的 line 索引规模 |
| DCACHE_MAX_TX | 4 | 2^MemTidWidth，不是 xbar 最大事务数 |
| FETCH_WIDTH / INSTR_PER_FETCH | 32 / 2 | 开 RVC 后每次最多容纳两个 16 位指令片段，不表示双发射 |

## 6. 常改与慎改项

- 初学者先冻结 profile 和 ISA；优先学习 `RASDepth/BTBEntries/BHTEntries`、cache 容量/way/line 的关系以及地址属性。改变预测器尺寸需检查数组索引和实现对 0/2 的幂的假设。
- 改 cache 容量后，应同时检查 bank 形状、索引/标签位宽、SRAM 宏、miss/eviction 测试；本轮没有给任意 cache 组合背书。
- 开 PMP 必须设计复位与软件配置，包含权限异常测试；不能照搬其他系统的 PMP reset 值。
- 切换 WT/WB/HPDCACHE 需要配套源码清单和一致性机制。当前向量基线是 WT，不应为了性能直接换 WB。
- `FpgaEn=0` 不能证明 ASIC 就绪；技术 cell、SRAM 和 clock gating 的源码选择仍要独立核对。

当前结构体没有简单的 `NumCores`、CPU 主频、LLC 容量或 Ara lane 数字段：这些分别归 SoC、时钟实现、LLC、Ara 管理。profile 中 `CVA6ConfigRvfiTrace` 也没有同名 user 字段，不能把一个未接入的 localparam 当成已经生效的 trace 开关。
