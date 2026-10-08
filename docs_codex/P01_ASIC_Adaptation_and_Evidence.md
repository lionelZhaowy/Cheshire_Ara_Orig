# P01：ASIC 技术适配与验收证据手册

日期：2026-10-08。状态：**文档盘点完成；技术替换、源码提取与工程验证未实施。** 输入分支 `mp/ara-pulp-v2`，HEAD `459f9d6f5748e39063f7bb67e959c2f27859915d`；工作区带已有教材/图稿修改。本手册是定向接口盘点，不宣称已展开完整设计或穷举全部存储实例。

[02 提取交接书](02_Cheshire_Ara_ASIC_Extraction_Handoff.md)继续负责唯一配置、源码闭包、静态清单和阶段规格。本手册负责替换时要保持的语义、缺失资料及验收责任；原理教学在 [ASIC HTML 入口](learning/future.html)。现有 [03 平台约定](03_Platform_ROM_Clock_IP_Configuration.md)的职责和文件名保持不变。原计划 08 无需再创建同内容正文。

## 1. 当前可交付范围与证据等级

- **用户确认**：迁移为独立静态清单工程；DDR 可提供 AXI4；NPU/ISP 要求绕过 LLC；沿 Platform ROM 钩子完成安全启动配置并保留运行时配置接口。具体工艺、宏、PLL/PAD、频率与域划分未冻结。
- **源码确认**：以下路径、端口、参数消费者和绑值；只对当前快照负责。
- **用户历史报告/已有产物**：VCU118 HelloWorld、既有 ELF 与图形证据按原报告保留，不计为本次新执行。
- **本轮实测**：文档结构、链接、哈希保护和尺寸复算。未编译/未仿真/未综合/未板测/未做 STA、DFT 或物理签核。
- **方案建议**：接口表、模型测试与准入条件；不产生生产修改授权。

## 2. 先识别资源，不按模块名决定替换

| 当前资源/来源 | 本地可确认内容 | 替换时必须保持/明确 | 所需资料与责任人 |
|---|---|---|---|
| Ara VRF：[vector_regfile](../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/lane/vector_regfile.sv)、[lane](../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/lane/lane.sv) | 2/2048 快照为 16 个 64×64-bit 1RW bank；一拍有效位/目标队列；8-bit 字节使能 | 端口、延迟、掩码和消费者身份；控制复位与数据初始化分开；测试/保持脚 | P01/宏供应商：宏清单与各视图；V01：接口与消费者回归 |
| LLC data：[axi_llc_data_way](../.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/src/axi_llc_data_way.sv)；tag：[tag_store](../.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/src/hit_miss_detect/axi_llc_tag_store.sv) | data 与 tag 是不同消费者；tag 有上电 BIST/初始化 | way/line/block 组织、读写时序、tag 比较与 BIST；SPM 同时服务启动代码/栈 | E01 冻结组织；P01 提供两类宏；S01 明确启动容量；不能只替 data 宣称完成 |
| CVA6 cache：[icache](../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/cache_subsystem/cva6_icache.sv)、[wt_dcache_mem](../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/cache_subsystem/wt_dcache_mem.sv)等 | 本地有 sram_cache 路径，也有其他 cache 实现 | 先按冻结 profile 展开确定实际消费者，再逐实例填写端口/深宽/读延迟/掩码/碰撞 | E01 给唯一展开基线；P01 定向完成其余存储账本；本文不凭文件存在判定全部实例同时启用 |
| XPM：[tc_sram_xilinx](../.bender/git/checkouts/tech_cells_generic-223c43ccbeb688f9/src/fpga/tc_sram_xilinx.sv) | 1-port 用 xpm_memory_spram，2-port 用 tdpram；READ_LATENCY 传参，no_change，固定零初始化 | 与行为 tc_sram 的默认 SimInit="none" 有区别；不能把 FPGA 初始化特性带入 ASIC 假设 | P01/E01 选择唯一实现；供应商给 ASIC 上电/复位/碰撞语义 |
| Boot ROM：[S 源](../hw/bootrom/cheshire_bootrom.S)、[生成 SV](../hw/bootrom/cheshire_bootrom.sv) | 指令内容、取指接口和生成产物成套 | 内容一致、复位入口/地址映射、访问时序；常量逻辑或真实 ROM 宏；制造后不可更新边界 | S01 管内容和生成对应；P01 管实现；S01-B01 修复另有授权门槛 |
| clock gating / mux：[tc_clk](../.bender/git/checkouts/tech_cells_generic-223c43ccbeb688f9/src/rtl/tc_clk.sv) | 行为 ICG 在低电平锁存使能；普通 mux 明示不保证无毛刺动态切换 | 极性、最小脉冲、门控检查、测试旁路、切换协议；不能把行为 assign 当工艺时钟单元 | PLL/库供应商交可用单元与约束，P01 设计平台协议 |
| MMCM/clkwiz：[FPGA top](../target/xilinx/src/cheshire_top_xilinx.sv) | clkwiz 输出系统/USB 等时钟；locked 未参与当前连接的启动放行 | ASIC 使用真实参考源、PLL/安全旁路，CPU 最早取指不能依赖尚未执行的 PLL 软件 | P01/IP 供参考范围、稳定/锁定/切换协议；S01 使用可持续访问配置接口 |
| reset / CDC：[rstgen_bypass](../.bender/git/checkouts/common_cells-7f7ae0f5e6bf7fb5/src/rstgen_bypass.sv)、[cdc_2phase](../.bender/git/checkouts/common_cells-7f7ae0f5e6bf7fb5/src/cdc_2phase.sv) | 同步释放；普通 CDC 有明确两端复位和路径约束 | 复位源/极性/作用域、时钟有效条件、排空与重新就绪；clearable 不自动解决 AXI 取消 | P01 域表/复位规范；V01 结构和协议验收 |
| MIG/DDR：[dram_wrapper_xilinx](../target/xilinx/src/dram_wrapper_xilinx.sv) | 位宽/ID 适配，可选 AXI CDC，MIG UI 域；calib 完成输出未参与完整放行 | AXI4、初始化/训练/响应、位宽/ID/地址、控制器/PHY/器件责任；保留训练前可执行存储 | M01+DDR 供应商交授权接口/模型；P01 电源/时钟/PAD；S01 早期固件 |
| USB：[SoC gen_usb](../hw/cheshire_soc.sv) | OHCI 控制/DMA/IRQ；独立 usb_clk_i、usb_rst_ni；DP/DM 输入/输出/OE | 数字端与实际收发电气、PHY/时钟/复位以及模式责任，不能开配置位就称可用 | 若用户保留 USB，由 P01/IP/板级负责人给 PHY/PAD 与目标验证环境；保留决策未冻结 |
| PAD / IOBUF：[FPGA top](../target/xilinx/src/cheshire_top_xilinx.sv) | I2C IOBUF 的 T=~en；GPIO/其他 IO 按实际 wrapper 接线 | IO/OE 极性、输入反馈、开漏/三态、上电默认、I/O 电压、封装/板负载 | P01/PAD 供应商+封装/板级团队；I01 给传感器/外设完整接口 |
| scan / MBIST：[SoC Ara 连接](../hw/cheshire_soc.sv)、[LLC 文档](../.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/doc/axi_llc.md) | Ara scan 输入绑 0、输出未用；VRF 门控 test_en 绑 0；LLC BIST 针对 tag | 测试接管、时钟复位控制、链/阵列覆盖、宏修复与测试退出；现有端口不等于实现完成 | P01/DFT 负责人供策略、工具和故障模型；供应商供测试/修复接口 |

这张表是定向资源入口。完整生产清单还要在 E01 固定实例后列出 debug 存储、FIFO、寄存器阵列与其他技术单元，确认哪些映射为触发器、哪些映射为宏；不能仅搜索 tc_sram 就宣布全部工艺依赖已覆盖。

## 3. 每个 SRAM/ROM 的最小适配记录

每项记录保留：**逻辑实例路径 → 消费者符号 → 抽象 wrapper → 所选物理宏 → 视图版本**。接收者应能据此回答：

1. 地址单位、深度/宽度、端口类型和可并发访问是什么？
2. 请求在哪个边沿接收，何时给有效数据，是否允许背压？
3. 片选/写使能/字节掩码的有效极性与未选字节行为是什么？
4. 同址访问允许哪些组合，读数据定义如何？复位/上电/休眠是否保持内容？
5. 功能模型、Liberty、LEF/版图、测试/修复、低功耗资料是否属于同一版本？

真实 VRF 例见 [asic-memory#bank-contract](learning/asic-memory.html#bank-contract)。k+2 宏不能直接接到 k+1 有效位上；如改变延迟，必须重新设计有效位、目标队列、空间预留和门控周期，参见 [具体消费者推演](learning/asic-memory.html#k-plus-two)。本文没有指定宏拼接方式或写真实适配 RTL。

## 4. 正常配置与平台生命周期契约

平台硬件先建立安全时钟/复位和可取指路径；保留 LLC 时 Boot ROM 准备 SPM/栈；Platform ROM 才能配置依赖这些资源的 IP。运行时同一控制口需要支持再次配置，但任意参数重写是否允许、作用范围和完成状态必须由 IP 规定。详细教学在 [正常调频](learning/clocks.html#normal-frequency-change)与 [域重启](learning/reset.html#transaction-reset)。

配置契约至少包含请求拥有者、允许状态、参数合法集合、接收/生效/完成的区别、受影响时钟域、排空条件、配置通路自身时钟、实际频率发布和外设分频更新。若涉及电压、DDR 变频或掉电，另需供应商规定的状态转换与数据保持条件。具体初始频率、独立域、DVFS 表均未冻结。

当前接线的三个边界必须保留：[FPGA top](../target/xilinx/src/cheshire_top_xilinx.sv) 的 `i_clkwiz.locked()` 未接；[DDR wrapper](../target/xilinx/src/dram_wrapper_xilinx.sv) 的两种 MIG `init_calib_complete()` 输出未接；[SoC](../hw/cheshire_soc.sv) 的 `i_dbg_dm_top.ndmreset_o()` 未用。它们说明尚无相应完整控制闭环证据，**不是本轮观测到启动必然失败**。非零 Platform ROM 返回问题继续引用 [S01-B01](03_Platform_ROM_Clock_IP_Configuration.md#s01-b01)。

## 5. 验证矩阵：保持什么，在哪里观察

| 对象 | 功能/消费者验证 | CDC/RDC/等价 | 时序/物理/制造证据 |
|---|---|---|---|
| VRF SRAM | 连续读、局部写、竞争后重试，数据/valid/队列身份一致；使用前初始化 | 变更前后按明确复位/初始化约束比较；同域不编造 CDC | 宏输入/输出路径、门控时序；实际宏/版图；bank 测试覆盖 |
| ROM/启动存储 | 指令字节、复位入口、栈与默认/非零平台钩子（修复后） | 地址/实现变更的行为对应；复位与接口结构 | ROM/SRAM 时序、初始化/制造不可更新责任 |
| PLL/复位/电源 | 安全启动、合法重配、排空、释放和软件频率一致 | 跨域配置、复位断言/释放、掉电隔离；各模式前后行为 | 时钟约束、脉冲/门控、低功耗库与物理/测试模式 |
| DDR/PHY | 初始化先于使用，地址/宽度/响应、并发和数据结果 | 两侧时钟/复位与在途事务；新互连接口检查 | PHY/PAD/器件时序与板条件；供应商验收和系统回归 |
| PAD/USB/图像输入 | 真实方向/OE、上电状态和正常事务；完整设备条件 | 进入数字域的采样和复位协议 | 电气/ESD、封装/PCB、输入输出预算；工具/实验各有边界 |
| DFT/MBIST | 功能模式不被破坏，测试接管与退出正确 | 插入后的功能模式等价/回归 | scan/ATPG/MBIST 范围、故障模型/排除项、测试时序/功耗与 ATE 数据 |

编译展开只证明结构可接受；功能模型结果不证明物理实现；STA 不证明数据算法正确；DFT 覆盖不等于系统回归通过。每份报告必须对应同一配置/源码/库版本，标实际命令、工具、输入、退出码、排除范围和原始产物。没有运行不填“通过”。

## 6. 输入缺口与解锁条件

| 提供者 | 具体输入 | 现在可做 | 解锁的工程步骤 |
|---|---|---|---|
| 用户/系统负责人 | 最终保留设备、频率/性能/功耗范围、启动介质、复位/低功耗要求 | 整理候选接口与依赖 | 冻结产品配置和接受标准 |
| 工艺方/P01 | PDK/库版本、合法工作角、允许发布的宏/PLL/PAD 摘要及受控资料位置 | 说明所需视图、极性与周期 | 真实宏映射、时钟/IO 实现、物理签核 |
| DDR 供应商/M01 | AXI4/控制器/PHY/器件、初始化、训练状态、模型与工具授权 | 与当前 LLC 出口建立契约 | 控制器替换、初始化软件、真实 DDR 验证 |
| E01 | 唯一 profile/源码清单、实际展开实例、第三方差异 | 当前源码定向教学与盘点 | 完整资源数量/尺寸账本和可搬迁验证基线 |
| S01/V01 | 启动修复/软件约定、工具许可/模型、预期输出和回归环境 | 写带条件的测试计划 | 平台软件运行、消费者回归及错误场景 |
| DFT/封装/板级团队 | 测试策略/ATE、封装/板/测试点与供电测量条件 | 制造测试及首硅路线设计 | 测试插入与制造交付、样片启动/功耗测量 |

受限资料不复制进仓库，只记授权接口摘要与受控位置。资料缺失影响具体工程步骤，不阻止完整解释机制；RTOS/Linux 不是这份裸机 ASIC 适配清单的强制前置。

## 7. 接收与后续分工

E01 接收实例/唯一实现选择要求；P01 落实工艺资源与约束；M01 接收 DDR 及多主接口；S01 接收初始化/重复配置和状态交还；V01 接收各层验证判据；I01 提供新增 IP 的流量与物理接口。公共状态/索引由协调者串行汇总。下一步最小工程工作需另行明确授权，不能从本次文档实施推导允许修改生产 RTL、升级依赖、提取源码或启动大型验证。

来源版本和检查记录见 [本轮 ASIC 证据](learning/evidence/system-implementation-20261008/asic/README.md)与 [实施报告](L01_ASIC_Implementation_2026-10-08.md)。官方概念与本地实现分别在 HTML 源节引用；在线 latest 只作机制资料，不取代当前消费者快照。
