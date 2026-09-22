# Ara 配置参数手册

返回 [配置导航](README.md)。基于仓库内 `ara-2c7b103275a16c87` 快照；参数存在与特性开启均为源码事实，不代表本轮通过了对应指令测试。

## 1. 先理解四个不同的“宽度/长度”

| 名称 | 当前向量基准 | 含义 |
| --- | --- | --- |
| CVA6 XLEN | 64 bit | 标量整数寄存器宽度 |
| CVA6 配置中的 VLEN | 64 bit | CPU 虚拟地址容器宽度 |
| Ara VLEN / Cfg.AraVLEN | 2048 bit | 每个架构向量寄存器的存储容量 |
| Ara ELEN | 64 bit | 最大向量元素宽度，定义在 ara_pkg |
| NrLanes / Cfg.AraNrLanes | 2 | 并行执行 lane 数 |
| vl | 软件运行时确定 | 当前指令处理的元素数量，不是 bit 数 |
| SEW / LMUL | 由 vtype 设置 | 单元素宽度 / 寄存器分组倍率 |

以 `VLEN=2048, SEW=32, LMUL=1` 为例，一个向量寄存器最多容纳 64 个元素；`vl` 可以少于 64。向量寄存器容量较大也不表示一个周期能算完所有元素。增加 lane 数影响并行度，增加 VLEN 影响每次可处理的数据量，两者是独立选择。

架构寄存器共 32 个：总有效数据容量 `32×VLEN/8`，当前为 8192 byte；2 lanes 时每 lane 分摊 4096 byte。公式不包含队列、状态、算术单元与布线面积。

## 2. 模块参数与 Cheshire 实际连接

来源：[ara.sv](../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/ara.sv)、[ara_pkg.sv](../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/include/ara_pkg.sv)、[SoC 的 gen_ara](../../hw/cheshire_soc.sv)。模块声明中的 0/logic 通常是占位默认值，不能独立直接实例化。

| 参数 | ara 模块默认 | Cheshire 中实际取值/来源 | 含义与修改影响 |
| --- | --- | --- | --- |
| NrLanes | 0 | Cfg.AraNrLanes，2 | lane 数；改变 VRF 分布、shuffle 和访存带宽 |
| VLEN | 0 | Cfg.AraVLEN，2048 | 每个向量寄存器 bit 数 |
| OSSupport | 1 | 显式固定 1 | OS/地址转换相关支持；不代表已运行操作系统 |
| FPUSupport | FPUSupportHalfSingleDouble | 未覆盖，沿用默认 | 半精度/单精度/双精度向量浮点支持 |
| FPExtSupport | FPExtSupportEnable | 未覆盖 | vfrec7、vfrsqrt7、round-toward-odd 相关支持 |
| FixPtSupport | FixedPointEnable | 未覆盖 | 向量定点相关操作支持 |
| SegSupport | SegSupportEnable | 未覆盖 | 分段访存支持 |
| CVA6Cfg | 声明引用 cva6_config_pkg | 显式连接 build_config 后的 Cva6Cfg | 必须与宿主 CPU 配置一致；不要依赖 Ara 声明占位默认 |
| AxiDataWidth | 0 | 32×AraNrLanes，当前 64 | Ara 本地访存 AXI 位宽，不是 64×lanes |
| AxiAddrWidth | 0 | Cfg.AddrWidth，48 | 与 SoC 地址位宽一致 |
| exception_t | logic | SoC 派生异常类型 | 异常回传结构，不能用占位 logic |
| accelerator_req_t / accelerator_resp_t | logic | SoC/CVA6 派生类型 | 加速器请求/响应 |
| acc_mmu_req_t / acc_mmu_resp_t | logic | 同上 | 地址转换请求/响应 |
| cva6_to_acc_t / acc_to_cva6_t | logic | 同上 | 组合宿主接口结构 |
| axi_ar_t / axi_r_t / axi_aw_t / axi_w_t / axi_b_t | logic | Ara 宽数据通路各通道类型 | 位宽须匹配 AxiDataWidth、地址和 ID |
| axi_req_t / axi_resp_t | logic | Ara 宽数据请求/响应类型 | 不能拿窄 SoC 类型直接替代 |
| NrPEs（localparam） | NrLanes+4 | 6 | lane + load/store/slide/mask；附近注释曾写 +3，以表达式为准 |
| VLENB（localparam） | VLEN/8 | 256 | 每向量寄存器 byte 数 |
| vlen_t（localparam type） | clog2(VLEN+1) 位 | 12 bit | 元素/长度相关计数容器，勿手动缩减 |

`FPUSupport` 的枚举包括 None、Half、Single、HalfSingle、Double、SingleDouble、HalfSingleDouble、All。`All=6'b111111` 还包含额外格式位，并非只是标准 FP16/32/64 的别名。若产品要裁掉浮点，需改 SoC 对 Ara 的参数传递或建立独立配置，再验证 decoder、软件 ISA 和异常行为；当前 `cheshire_cfg_t` 没暴露这些开关。

## 3. 当前连接中容易漏掉的固定参数

| 位置 | 当前参数/行为 | 意义 |
| --- | --- | --- |
| Ara 写入到 CPU L1D 的 invalidation filter | MaxTxns=4；L1LineWidth=Cva6Cfg.DCACHE_LINE_WIDTH/8 | L1 cache line 改动会影响过滤器；不能把它当成全系统一致性网络 |
| invalidation filter 使能 | acc_cons_en | 来自 CPU 自定义 CSR_ACC_CONS；CPU 开加速器时复位值为开，软件可以改变 |
| Ara 到 SoC 数据宽度转换器 | AxiMaxReads=4 | 增加 lanes 后读事务容量不会自动增长 |
| Ara AXI ID 类型 | Cfg.AxiMstIdWidth | 与 CPU 内部 4 位 ID 不同 |
| scan_enable_i / scan_data_i | 固定 0，scan_data_o 未使用 | 现有接线不构成 ASIC DFT 集成 |
| Ara 时钟/复位 | 与 SoC clk_i/rst_ni 相连 | 不是独立频率的向量时钟域 |

`CvxifEn=0` 与 `RVV=1` 可以同时成立：本组合启用专用 accelerator 接口；不能只根据端口中的 cvxif 字样把它认成通用 NPU 插槽。CPU/Ara 之间有特定的一致性配合，新增 ISP/NPU DMA 不会自动加入这套配合。CSR 实现见 [csr_regfile.sv](../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/csr_regfile.sv)。

## 4. 约束与已有示例配置

Ara 顶层明确检查：`NrLanes>0`、lane 数为 2 的幂且不超过 `MaxNrLanes=16`；`VLEN>0`、`VLEN>=ELEN`、VLEN 为 2 的幂。shuffle 实现提供 1/2/4/8/16 lanes 分支。

这些检查**不是整个集成的完整合法范围**。config Makefile 注释还写 `VLEN>128`；VRF 的每 bank 深度由 `32×VLEN/NrLanes/(8×64)` 派生，过小组合还可能产生无效地址切片。`rvv_pkg` 中最大 VLEN 常量为 65536 bit。不要把“满足顶层几条检查”当成任意组合均可用的结论。

下面四组来自本地 [config 目录](../../.bender/git/checkouts/ara-2c7b103275a16c87/config)，后两列是按 SoC 公式计算，非性能测量：

| Ara 配置文件 | lanes | VLEN bit | 总 VRF 数据容量 | 当前 Cheshire Ara 本地 AXI bit |
| --- | --- | --- | --- | --- |
| 2_lanes.mk | 2 | 2048 | 8 KiB | 64 |
| 4_lanes.mk | 4 | 4096 | 16 KiB | 128 |
| 8_lanes.mk | 8 | 8192 | 32 KiB | 256 |
| 16_lanes.mk | 16 | 16384 | 64 KiB | 512 |

这些例子都使每 lane VRF 有效容量为 4 KiB；并不要求 lanes 增加时 VLEN 必须同比增加。保持 SoC 总线为 64 bit 时，更宽 Ara AXI 仍经过宽度转换，DDR 带宽不会按 lane 数线性增长。首个提取建议继续冻结 2/2048，其他组合需单独展开与向量回归。

**仿真/FPGA 差异**：Ara Makefile 中 `ARA_CONFIGURATION` 会读取 `nr_lanes/vlen` 并形成宏；FPGA wrapper 读取宏。但当前仿真 `gen_cheshire_ara_cfg()` 明写 2/2048，修改宏不改变它。软件宏也必须与最终硬件一致。

## 5. 包内常量：属于微架构，不建议初学者随意改

| 常量 | 当前值 | 作用 |
| --- | --- | --- |
| ELEN / ELENB | 64 / 8 | lane 元素/数据宽度基础 |
| NrVInsn | 8 | 可并行跟踪的向量指令数量 |
| MaxNrLanes | 16 | shuffle 等实现支持上限 |
| NrVRFBanksPerLane | 8 | 每 lane 的 VRF bank 数 |
| NrOperandQueues | 9 | 操作数队列类别数量 |
| MaxVInsnQueueDepth | 4 | 指令队列最大深度常量 |
| MfpuInsnQueueDepth / ValuInsnQueueDepth | 4 / 4 | 浮点乘法/整数 ALU 队列 |
| VlduInsnQueueDepth / VstuInsnQueueDepth / VaddrgenInsnQueueDepth | 4 / 4 / 4 | load/store/address 队列 |
| SlduInsnQueueDepth / NoneInsnQueueDepth | 2 / 1 | slide / 占位类别队列 |
| MaskuInsnQueueDepth | 1 | 源码明确仅支持 1 |
| LatMultiplierEW64/32/16/8 | 1/1/1/0 | 乘法流水配置 |
| LatFCompEW64/32/16/8 | 5/4/3/2 | 浮点计算流水配置 |
| LatFCompEW16Alt / LatFCompEW8Alt | 3 / 2 | 替代格式计算流水 |
| LatFDivSqrt / LatFNonComp / LatFConv / LatFDotp | 3/1/2/0 | 对应单元流水配置；不能直接等同于所有指令端到端完成周期 |
| LatFMax | LatFCompEW64=5 | 调度相关最大流水常量 |

VRF 实现见 [vector_regfile.sv](../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/lane/vector_regfile.sv)：8 个单端口 `tc_sram` bank/lane，数据宽度 64 bit；基准每 bank 64 words。换 SRAM 宏需要保持读延迟、byte enable、时钟门控与访问仲裁契约。

## 6. 软件匹配

硬件 profile 要 RVV=1，SoC 要 Ara=1，源码清单要真实 `cva6_accel_first_pass_decoder.sv` 并排除 stub。软件 `-march` 要包含 V，启动代码在首条向量指令前设置 `mstatus.VS`，涉及浮点还要设置 FS。

根 [sw.mk](../../sw/sw.mk) 默认 `rv64gc_zifencei/lp64d`；[Ara 软件入口](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/Makefile) 将它改为 `rv64gcv_zifencei` 并加入 `NR_LANES/VLEN/ARA_NR_LANES/EEW/PRINTF` 宏。根 [crt0.S](../../sw/lib/crt0.S) 可见 FS 初始化，不能因此假定任意程序已设置 VS，应检查实际启动代码和测试程序。

通用程序优先按实际 `vl` 循环处理数据；专门按 VLEN/lane 编译的 benchmark 必须匹配硬件。验收应包含整数向量加法、load/store、尾部元素、非整倍长度、浮点结果比较和 CPU/Ara 共享数据可见性；看到 ELF 中有 RVV 指令只是静态证据。
