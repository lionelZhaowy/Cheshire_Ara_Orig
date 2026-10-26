<a id="常用配置入口和修改流程"></a>

# 常用配置与修改流程

> 2026-10-25正式工程入口：请先读[当前配置与电路关系](../engineering/Fixed_Vector_SoC_Resource_Guide.md#q1)。`~/CheshireAra`已使用统一 `cheshire_pkg::Cfg`，不使用旧SELCFG/TB四配置选择；本文旧路径、默认值和2026-10-19服务器表保留为其历史输入说明，不直接作为正式工程修改步骤。


返回 [配置导航](README.md)。本页的“已有”表示源码中有该组合/入口；“示例”表示可供实施讨论的修改方法；均不声称本轮运行通过。

<a id="server-config-trace"></a>

## 0. 当前服务器固定配置：逐层追踪（2026-10-19）

先读[上手指南第4章](../software/SERVER_SIMULATION_GUIDE.md#config)理解传递过程，再用本节查当前值；完整字段定义继续沿用[CVA6](CVA6.md)、[Cheshire](CHESHIRE.md)、[Ara](ARA.md)、[外设/VIP](PERIPHERALS.md)字典，不再复制一套字段全集。

**范围与证据：**本地输入`2f0f2d6f85979709fbc99dd4098447cb5587ce5f`；服务器基准Cheshire=`e040b7bbc…`、Ara=`2895ba907…`、CVA6=`99eac9a64…`。2026-10-19尝试SSH核对时握手超时，本节依据当前本地源码和2026-10-18已保存的[服务器核查](../maintenance/E01/reports/reference_rebuild_check.md)、[两端范围对比](../maintenance/E01/reports/local_server_build_comparison.md)，未新增构建/运行证据。

- **源码推导**：在指定profile＋配置3下，由定义、覆盖和实例连接得到的值，不等于本轮逐项读回展开数据库。
- **已有构建证据**：历史核查确认清单的profile/decoder/宏及展开`SelectedCfg=3`。716个直接编译源两端曾逐文件一致，但不自动覆盖全部include和工具输入。
- **已有运行证据**：2026-10-18的`rvv_fmatmul_04`通过单个32×32测试，使用服务器显式FS=Clean修正；不推及所有软件或完整回归。下表“基线使用值”不是每次运行都固定不变的全局默认。

<a id="config-file-map"></a>

### 0.1 配置文件地图：各pkg、TB和脚本分别负责什么

| 文件/对象 | 定义与作用 | 最终消费者 / 阅读方法 |
| --- | --- | --- |
| [cheshire_pkg.sv](../../hw/cheshire_pkg.sv) | `cheshire_cfg_t`定义字段，`DefaultCfg`给初值，`gen_axi_*`/`get_llc_size`计算端口、地址、容量，`gen_cva6_cfg`覆盖CPU配置 | SoC、fixture及各wrapper；先查字段，再查函数，不能把所有包常量都当用户选项 |
| [tb_cheshire_pkg.sv](../../target/sim/src/tb_cheshire_pkg.sv) | 由DefaultCfg构造4份配置；索引0默认、1 AXI RT、2 CLIC、3 Ara | fixture选择一份传给DUT；虽然文件名含tb，这部分确实决定被测硬件 |
| [tb_cheshire_soc.sv](../../target/sim/src/tb_cheshire_soc.sv) | 顶层`SelectedCfg/UseDramSys`参数；运行时读取4个plusargs | 前两者转交fixture；plusargs控制启动输入、装载及镜像，详见0.4 |
| [fixture_cheshire_soc.sv](../../target/sim/src/fixture_cheshire_soc.sv) | `DutCfg=TbCheshireConfigs[SelectedCfg]`；连接DUT/VIP | `.Cfg(DutCfg)`给SoC，`.DutCfg(DutCfg)`给VIP；对齐两端类型，不另外选择一份VIP硬件配置 |
| [cheshire/typedef.svh](../../hw/include/cheshire/typedef.svh) | `CHESHIRE_TYPEDEF_ALL`等宏根据Cfg生成地址、AXI/Reg结构体及位宽 | fixture/SoC/VIP端口；派生类型应跟随Cfg，不手动另设宽度 |
| CVA6 [config_pkg.sv](../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/include/config_pkg.sv) | 用户配置/最终配置的类型和枚举定义 | 描述“有哪些字段”，不单独选择CPU能力 |
| [cv64a6_imafdcv_sv39_config_pkg.sv](../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/include/cv64a6_imafdcv_sv39_config_pkg.sv) | 唯一选入的profile，定义`cva6_config_pkg::cva6_cfg` | `gen_cva6_cfg`以它为初值；不同profile通常定义同名包，不应同时编入 |
| [build_config_pkg.sv](../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/include/build_config_pkg.sv) | 从覆盖后的CPU用户配置派生内部配置 | CVA6与Ara的`Cva6Cfg`；如`EnableAccelerator=RVV`，不建议直接修改派生结果 |
| Ara [2_lanes.mk](../../.bender/git/checkouts/ara-2c7b103275a16c87/config/2_lanes.mk)及[集成Makefile](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/Makefile) | Make侧lane/VLEN、profile/decoder选择和编译宏 | 清单生成、相关软件入口；不会自动修改TB中写定的数值 |
| [ara_pkg.sv](../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/include/ara_pkg.sv) | 指令/请求类型、枚举和微架构常量 | Ara内部；顶层实际lane/VLEN还要看SoC的`i_ara`参数绑定，见[Ara字典](ARA.md) |
| [vip_cheshire_soc.sv](../../target/sim/src/vip_cheshire_soc.sv) | 模型、时钟、复位、协议驱动/监视及等待策略 | 仿真环境；具体值及是否可独立修改见0.4 |
| 生成寄存器包，如PLIC/CLINT/Serial Link包 | 根据生成输入定义地址、位域、源数量等 | 硬件实例和部分包级常量；不能靠覆盖Shell变量就改变已生成的文件 |
| [VCS启动脚本](../../target/sim/vcs/start.cheshire_soc.sh) | 将Shell变量转换成`vcs`选项和`simv`参数 | 变量是否有效取决于实际拼接代码；`VCSARGS`是当前未追加内容的反例 |

### 0.2 Cheshire与Ara：默认值、覆盖和硬件消费者

配置3执行`ret=DefaultCfg`后**显式赋值三个字段**：`Ara=1`、`AraNrLanes=2`、`AraVLEN=2048`。其中后两项与当前默认值相同，真正改变数值的是`Ara:0→1`；其余全部字段继承DefaultCfg。由此可将[Cheshire完整字段表](CHESHIRE.md#2-全部-soc-字段)作为当前组合的默认值来源，同时检查每个字段是否真正被消费者读取。

下列值均为源码推导；profile/宏/配置选择另有历史构建证据。硬件字段的修改默认需要RTL编译、重新展开与验证；若涉及选源或生成尺寸，还需先重生成相应输入。

| 字段 / 含义 | 默认 → 配置3 | 来源及消费者 | 关联约束 |
| --- | --- | --- | --- |
| `Ara` / 是否生成向量单元 | 0 → **1** | TB配置函数覆盖；SoC `gen_ara`及AXI入口生成 | 同时匹配向量CPU profile和真实decoder |
| `AraNrLanes` / lane数量 | 2 → 2 | TB显式赋值；`i_ara.NrLanes`及`AraDataWideWidth=32×lanes` | 当前Ara AXI数据宽度派生为64 bit；软件lane宏也需匹配 |
| `AraVLEN` / 向量寄存器位数 | 2048 → 2048 bit | TB显式赋值；`i_ara.VLEN`及VRF组织 | 不等于CPU的地址容器VLEN；软件宏不是硬件容量开关 |
| `NumCores` | 1 → 1 | DefaultCfg；CPU实例循环、hart/互连派生 | CLINT/PLIC生成尺寸不一定自动联动 |
| `AddrWidth/AxiDataWidth/AxiUserWidth` | 48/64/2 → 不变 | 类型宏、SoC总线及`gen_cva6_cfg` | 改宽度须贯穿DUT、VIP、子模块适配 |
| `AxiMstIdWidth` | 2 → 2 bit | AXI输入端口及ID转换 | 7个输入下，交叉开关下游ID派生为5 bit；LLC下游为6 bit，不单独手填 |
| `LlcNotBypass/LlcOutConnect` | 1/1 → 不变 | SoC `gen_llc`、外存与原子路径 | `LlcNotBypass=0`影响内部SPM；不能当作纯性能开关随意关闭 |
| `LlcSetAssoc/LlcNumLines/LlcNumBlocks` | 8/256/8 → 不变 | `i_llc`及`get_llc_size()` | 配合64-bit数据得到128 KiB；链接脚本仍单独限制64 KiB |
| `LlcOutRegionStart/End` | `[0x80000000,0x100000000)` → 不变 | 地址译码、LLC及CPU区域属性 | 是2 GiB路由区间，不证明仿真模型/物理DDR具备同等容量 |
| `Bootrom/Uart/I2c/SpiHost/Gpio/Dma/SerialLink/Vga/Usb/BusErr` | 均1 → 不变 | 各generate分支、地址图及接口 | 存在不等于板上接出或功能已测试；Serial Link还是当前加载路径 |
| `AxiRt/Clic/IrqRouter` | 均0 → 不变 | 对应硬件分支/CPU中断配置 | 配置3不叠加配置1/2；它们各自从DefaultCfg重新构造 |
| `RtcFreq` | 32768 Hz → 不变 | SoC只读频率信息、软件测频依据 | 不产生时钟；需与VIP的实际RTC周期对应 |
| `Cva6NrPMPEntries` | 0 → 0 | `gen_cva6_cfg`覆盖profile的8 | 最终CPU PMP条目为0，不是profile中的8 |
| `SlinkMaxClkDiv`字段 | 1024 → 1024 | **当前SoC/VIP实例读同名包级常量，未读Cfg字段** | 数字恰好相同不表示传递生效；不能只改此字段期待硬件改变 |

当前7个AXI输入由CPU、debug、Ara、DMA、Serial Link、VGA、USB构成；ID宽度公式在`cheshire/typedef.svh`。未设置的扩展字段由`DefaultCfg`的`default:'0`填零。外设开关裁切、地址重排或改变lane数不属于本轮文档授权。存储bank组织继续查[固定资源指南](../engineering/Fixed_Vector_SoC_Resource_Guide.md)。

### 0.3 CVA6：profile初值不总是最终值

链路为`profile::cva6_cfg → gen_cva6_cfg(Cfg) → build_config → Cva6Cfg → CPU/Ara`。字段全集和所有覆盖细节见[CVA6字典](CVA6.md)；下表突出容易读错的来源，均为该组合的源码推导。

| 字段/组 | profile → SoC覆盖/派生后 | 谁使用 / 修改时注意 |
| --- | --- | --- |
| `XLEN / VLEN` | 64 / 64 → 不变 | CPU数据通路/虚拟地址容器；这里VLEN不是Ara向量长度 |
| `RVF/RVD/RVV` | 1/1/1 → 不变 | CPU能力；`build_config`由RVV派生`EnableAccelerator=1`。`Cfg.Ara`不会替代RVV赋值 |
| `CvxifEn` | 0 → `gen_cva6_cfg`固定置0 | 当前Ara采用专用加速器接口；端口名含cvxif不表示开启通用CV-X-IF |
| `AxiAddrWidth/AxiDataWidth/AxiUserWidth` | 64/64/64 → **48/64/2** | 由SoC对应字段覆盖，供CPU总线及类型使用 |
| `AxiIdWidth` | 4 → 包常量4 | CPU原始ID；与SoC输入端口2-bit ID之间有适配，不能混为一个字段 |
| `NrPMPEntries` | 8 → **0** | 取`Cfg.Cva6NrPMPEntries`；profile原值被覆盖 |
| `RASDepth/BTBEntries/BHTEntries` | 2/32/128 → 同值覆盖 | 最后取SoC的Cva6对应字段；直接改profile可能再次被覆盖 |
| `RVSCLIC` | 0 → `Cfg.Clic=0` | 中断配置由SoC覆盖；相关源数量也在函数中计算 |
| `IcacheByteSize/DcacheByteSize/DCacheType` | 4096/8192/WT → 不变 | 当前L1缓存配置；影响容量、派生索引和存储组织 |
| `DebugEn`及debug地址 | SoC函数设置DebugEn=1，并指定调试地址 | 不能只看profile判断调试是否存在 |
| 缓存/执行/非幂等区域 | SoC函数重设规则数、起始地址与长度 | 来自SPM容量、外存窗口和CIE区间；改变映射需同步软件、译码与访问属性 |
| `FpPresent/FLen/EnableAccelerator` | `build_config`派生为1/64/1 | 内部实现消费；优先修改合法输入配置，避免直接改派生函数输出 |

改profile字段通常需要重新编译和展开；选另一个profile还需重新生成选源清单。CPU支持F/D/V与软件设置FS/VS是两个条件：后者在运行期开放已存在状态，不能生成硬件单元。服务器FS修正与旧ELF的差异见[Q07](../maintenance/E01/planning/server_reference_rebuild_guide.md#q07)，不能推断全部ELF已更新。

### 0.4 TB/VIP：参数、运行输入和派生类型

fixture只显式传入VIP的`DutCfg`、`UseDramSys`和AXI类型，未覆盖下表其余VIP可调参数，所以它们在这组源码中继承声明默认值。**下面的默认推导不是逐个波形实测。**

| 参数/输入 | 声明默认 / 当前基线 | 消费者及作用 | 修改后最小动作 |
| --- | --- | --- | --- |
| `SelectedCfg` | 0 / 历史展开记录为3 | TB→fixture→DutCfg→DUT，选择硬件组合 | 重新展开；若CPU/宏不匹配，先重新选源/编译 |
| `UseDramSys` | 0 / 基线0 | TB→fixture→VIP，选择外部内存模型；不是DDR控制器使能 | 重新展开；开启还需相应库和资源 |
| VIP `DutCfg`、AXI类型参数 | 声明为零/logic占位 / fixture传入有效配置及类型 | 与DUT接口匹配，不能采用VIP占位值独立运行 | 跟随DUT配置与类型重新构建 |
| `ClkPeriodSys/Jtag/Rtc` | 5ns/20ns/30518ns / 未覆盖 | VIP时钟发生器；5ns对应仿真200MHz，不是ASIC频率承诺 | 改SV默认值须重编/展开；参数覆盖至少重展开 |
| `RstCycles` | 5 / 未覆盖 | 各时钟域复位发生器，以各自周期计 | 同上；不能将5写成统一的5ns |
| `TAppl/TTest` | 0.1/0.9 / 未覆盖 | 协议驱动/采样相位占系统周期比例 | 同上；不是DUT综合时序约束 |
| `UartBaudRate/UartParityEna` | 115200/0 / 未覆盖 | UART对端模型 | 同上；软件UART设置也要匹配 |
| `UartBurstBytes/UartWaitCycles` | 256/60 / 未覆盖 | UART加载与等待控制 | 同上；不是硬件FIFO容量 |
| `SlinkMaxWaitAx/R/Resp` | 100/5/20 / 未覆盖 | Serial Link VIP等待参数 | 同上；不等于Shell墙钟超时 |
| `SlinkBurstBytes` | 1024 B / 未覆盖 | VIP装载分块 | 同上；不是SoC数据总线位宽 |
| `SlinkMaxTxns/SlinkMaxTxnsPerId` | 32/16 / 未覆盖 | VIP侧事务配置 | 同上；不能当作SoC同名事务限制 |
| `SlinkAxiDebug` | 0 / 未覆盖 | VIP额外打印 | 同上；不是运行plusarg，不能凭名字用`+SlinkAxiDebug=1`覆盖 |
| `AxiStrbWidth/AxiStrbBits` | 从DutCfg派生 / 8及3 | VIP协议类型和寻址辅助 | 不独立覆盖，跟随DUT宽度 |
| `BOOTMODE` | plusarg缺省0 / 通过单例为0 | TB读取并驱动DUT启动输入，改变现有逻辑的启动行为 | 重跑；模式1当前TB不支持 |
| `PRELMODE` | plusarg缺省0 / 通过单例为1 | TB选择JTAG(0)/Serial Link(1)/UART(2)装载任务 | 重跑；相关硬件接口须存在 |
| `BINARY/IMAGE` | 缺省空字符串 / 单例使用fmatmul.spm.elf、未指定IMAGE | ELF加载或外设镜像预置；不是RTL源文件 | 换有效输入后重跑；若改源码先构建软件/镜像 |

不要把仿真RTC周期与`Cfg.RtcFreq`混用：前者真的产生波形，后者向软件报告频率。30518ns约对应32768Hz，存在取整；两者改变时需检查一致性。`BOOTMODE`改变DUT输入，但不改变DUT结构；`UseDramSys`不改变SoC内部结构，却会改变整个仿真平台的展开结构。

### 0.5 脚本、宏与软件：追到实际使用位置

| 输入 | 当前设置/来源 | 实际生效位置 | 修改后的动作 |
| --- | --- | --- | --- |
| `ARA_CONFIGURATION` | 集成Make默认`2_lanes` | include相应`.mk`，取`nr_lanes=2/vlen=2048` | 若改变，重新核对TB常量、宏和软件，再导出/编译/展开；不能单改即认为生效 |
| `ARA/NR_LANES/VLEN` | 历史清单宏存在，2/2048 | 消费者因目标而异：FPGA wrapper、Ara独立TB读取；Cheshire TB以函数值为准 | 对照所选源的预处理引用；宏变化要重编受影响源码 |
| profile target / `exclude_first_pass_decoder` | 向量profile / 排除CVA6 stub | Bender按目标选文件，留下Ara decoder | 重新导出有序清单、编译、展开 |
| `SELCFG/USE_DRAMSYS` | 启动脚本无设置时不追加覆盖 | VCS脚本转成展开参数；Questa用`-G` | 对现有simv单纯export无效，须重新展开 |
| `VLOGAN_ARGS` | 生成清单时传入`-full64`等 | 成为生成脚本中的vlogan选项 | 想改变现有清单，须重新生成或审定适配；运行前export不自动改文件 |
| `VCSARGS` | 当前脚本仅判断是否为空 | 未追加字符串内容；非可靠调试选项入口 | 不能按名称猜测覆盖；调试适配见上手指南第7章 |
| `CXX_PATH` / `CHS_SW_GCC_BINROOT` | 本机G++路径 / RISC-V GCC路径 | 前者联编DPI，后者编译目标程序 | 分别影响主机联编或软件构建，不互换 |
| `CHS_SW_FLAGS`的ISA/ABI | 根默认不带V；Ara入口替换为`rv64gcv_zifencei`、`lp64d` | 目标软件代码生成/调用约定 | 重新构建所选软件；不会增加CPU硬件能力 |
| `eew/printf` | 服务器官方入口无默认值，本次显式64/1；本地有补默认值的修改 | 测试编译宏`EEW/PRINTF` | 重编软件；不修改Ara硬件ELEN/VLEN |
| FS/VS | crt0 / 测试运行代码设置 | `mstatus`状态；首条相关指令之前必须有效 | 改启动/软件后重编ELF，再运行验证；不必为此重编RTL |
| `-kdb/-debug_access` | 普通或调试构建选项 | 仿真数据库/调试可见性 | 新调试构建；不改变目标SoC功能配置 |
| UCLI记录范围/时间、Shell `timeout` | 按测试选择 | 前者控制信号采集；后者限制主机墙钟时间 | 已有可见性足够时只重跑；不更改硬件或目标时钟 |

详细跟踪任意新字段时，记录“**声明/单位 → 默认值 → 当前覆盖 → 最终消费者 → 作用类别 → 联动项 → 重做范围 → 证据状态**”。本节固定配置表是查询依据；未来简短脚本负责读取/校验和记录，当前尚未实施配置文件封装。

## 1. 当前配置矩阵

| 用途/入口 | CPU profile | SoC 配置来源 | Ara / 其他差异 | 证据与适用范围 |
| --- | --- | --- | --- | --- |
| 根 Make 默认 | cv64a6_imafdchsclic_sv39_wb | TB 默认 SelectedCfg=0 | Ara=0 | 现有标量构建默认；不是向量基线 |
| TB SELCFG=0 | 由编译清单决定 | DefaultCfg | Ara=0，RT=0，CLIC=0 | 选择配置不更换 CPU |
| TB SELCFG=1 | 同上 | DefaultCfg+AxiRt=1 | 仍 Ara=0 | RT 示例；需匹配生成寄存器 |
| TB SELCFG=2 | 同上 | DefaultCfg+Clic=1 | 仍 Ara=0 | CLIC 示例，非 Ara+CLIC |
| TB SELCFG=3 | 必须另选向量 profile | DefaultCfg+Ara=1 | 2 lanes，2048 bit | 服务器历史核查已对齐；旧本地生成脚本的差异另列第6节，不混用 |
| Ara 集成 Makefile | cv64a6_imafdcv_sv39 | 仿真仍需 SELCFG=3；FPGA 读宏 | 默认 ARA_CONFIGURATION=2_lanes | 带 exclude_first_pass_decoder/ARA 宏的来源 |
| 当前 VCU118 add_sources | cv64a6_imafdcv_sv39 | FPGA wrapper 派生 | Ara=1、2/2048，SerialLink=0、Usb=0、RTC=1 MHz | 清单源码确认；不证明现有 bitstream 与全部输入一致 |
| 建议首个 ASIC 固定基线 | cv64a6_imafdcv_sv39 | 新建独立固定包，取 TB Ara 快照 | 1 核、2/2048；其余先保留 | 02 文档的提取建议，目录尚未实施，非最终产品冻结 |

当前 VCU118 仍继承 `Vga=1/I2c=1` 等 DefaultCfg 字段，即使板级没有相应 IO 宏；不要把不引出接口等同于已经裁掉逻辑。

相关入口：[cheshire.mk](../../cheshire.mk)、[TB 配置数组](../../target/sim/src/tb_cheshire_pkg.sv)、[Ara 集成 Makefile](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/Makefile)、[FPGA wrapper](../../target/xilinx/src/cheshire_top_xilinx.sv)。

<a id="2-初学者常用场景"></a>

## 2. 典型配置组合与修改示例

<a id="21-重现标量-helloworld"></a>

### 2.1 标量 HelloWorld 配置

保留现有板级工程、启动方式和已使用软件，记录 CPU profile、SoC 配置、bitstream/ELF 来源和串口输出。HelloWorld 适合验证取指、部分存储和串口路径；它不覆盖向量计算、所有 DDR 地址或原子并发。

<a id="22-建立正确向量组合"></a>

### 2.2 CPU 与 Ara 向量配置

需要同时满足：

- 编译唯一 CPU profile：`cv64a6_imafdcv_sv39`，`RVV=1`。
- 只编译 Ara 的真实 `cva6_accel_first_pass_decoder.sv`，排除 CVA6 同名模块的 stub。
- 仿真选 `SelectedCfg=3`；FPGA wrapper 传 `ARA/NR_LANES=2/VLEN=2048`。
- 软件使用带 V 的 ISA，典型为当前入口的 `rv64gcv_zifencei`、`lp64d`；工具链确实支持所用指令。
- 启动设置 VS；浮点路径设置 FS；测试真正执行向量并比较结果。

现有 Ara 入口用于选源的关键字符串是：

```text
-t cv64a6_imafdcv_sv39 -t cva6 -t rtl -t exclude_first_pass_decoder
--define ARA --define NR_LANES=2 --define VLEN=2048
```

这是**源码选择说明**，不是本轮执行的构建命令。当前目标仍是后续 E01 形成固定配置+静态 filelist，无须为阅读本手册反复维护 Bender。

<a id="23-调整向量规模"></a>

### 2.3 向量规模调整

建议先只变一个因素，例如维持 VLEN=2048 比较 2/4 lanes，或维持 2 lanes 比较不同 VLEN；这类组合必须先展开和回归。若直接选择本地 `4_lanes.mk`，其 VLEN 也变成 4096，要在性能报告中明确两个变量都变了。

同时核对 TB 常量、FPGA 宏、软件宏、VRF bank 深度、Ara AXI 宽度转换、4 个 outstanding reads 限制和 DDR 实测带宽。不要把新的 lane 数写进软件宏就认为硬件改变。

<a id="24-增大-llcspm-容量"></a>

### 2.4 LLC/SPM 容量调整

仅作计算示例：在 `AxiDataWidth=64, LlcSetAssoc=8, LlcNumBlocks=8` 不变时，把 `LlcNumLines` 从 256 改为 512，总容量从 128 KiB 变为 256 KiB；默认 SPM 窗口长度也随之变化。

```systemverilog
// 供后续独立配置包采用的函数片段；本轮未应用或编译。
function automatic cheshire_cfg_t gen_team_cfg();
  cheshire_cfg_t ret = DefaultCfg;
  ret.Ara = 1;
  ret.AraNrLanes = 2;
  ret.AraVLEN = 2048;
  ret.LlcNumLines = 512; // 仅作容量计算例子
  return ret;
endfunction
```

需要检查 SRAM 形状、tag 地址、BIST、栈定位、SPM 别名和链接脚本。不要为了增大 LLC 把整个 AXI 数据宽度一并改大，因为那会触及大量接口。`sw/link/common.ldh` 当前 SPM 链接区只写 64 KiB、DRAM 链接区 8 MiB，这是软件可放置区域，不等于 128 KiB 硬件 SPM/2 GiB DDR 路由窗口。

<a id="25-减少外设"></a>

### 2.5 外设裁切

待产品保留表确认后，在独立配置里按需求设置 `Usb/Vga/SerialLink/I2c/SpiHost/Gpio` 等；调整端口绑值、启动介质、软件探测、AXI ID 和中断表。不要裁掉用于当前 ELF 加载或自主启动的接口。

DMA=0 会减少 AXI 发起者并移除控制窗口。LlcNotBypass=0 会失去内部启动 SPM，影响比关闭 UART/VGA 大得多。现阶段不因“裸机”就自动删除 MMU/PMP/Debug，也不把最终外设取舍当成已决定。

### 2.6 图像搬运和 NPU 接入

先用已存在的 2D iDMA 理解行长度、stride、帧缓冲和所有权交接。自定义 IP 的 MMIO 可接 Reg 扩展，DMA master 可接 AXI 扩展；图像带宽预算需要帧宽×帧高×每像素 byte×帧率，再加读写遍数与空隙开销。

若要求 ISP/NPU 绕过 LLC，须新增 DDR 侧连接设计，确定不缓存共享区或缓存维护流程、缓冲区所有权、中断通知及 LR/SC 边界。本仓库没有一个 `NpuBypassLlc` 开关可以完成这些工作。

## 3. 仿真与软件常用参数

来源：[start.cheshire_soc.tcl](../../target/sim/vsim/start.cheshire_soc.tcl)、[tb_cheshire_soc.sv](../../target/sim/src/tb_cheshire_soc.sv)、[Boot ROM C](../../hw/bootrom/cheshire_bootrom.c)。

| 参数 | 当前含义 | 注意 |
| --- | --- | --- |
| SELCFG | Questa Tcl转成-GSelectedCfg，VCS Shell转成-pvalue+SelectedCfg | 展开选 SoC，不能修改已编译 CPU profile |
| USE_DRAMSYS | 对应两种脚本的UseDramSys展开参数 | 需匹配 SystemC/DRAMSys 库和资源，不是 DDR 控制器开关 |
| BOOTMODE=0 | 被动加载 | 配合 PRELMODE/BINARY |
| BOOTMODE=1 | ROM 的 SPI SD 启动 | 当前 TB 明确 fatal 为未支持，不能照板级流程直接仿真 |
| BOOTMODE=2 | SPI NOR Flash 启动 | IMAGE 提供对应模型可读内容 |
| BOOTMODE=3 | I2C EEPROM 启动 | 同上，并核对设备容量 |
| PRELMODE=0/1/2 | JTAG / Serial Link / UART 调试加载 | 仅 BOOTMODE=0 分支使用；关闭链路后不能选它 |
| BINARY | ELF 文件路径 | 需与 ISA、链接地址和启动契约匹配 |
| IMAGE | 自主启动模型镜像路径 | 与 ELF 是不同格式/加载路径 |
| CHS_SW_FLAGS | 编译器架构、ABI、优化等 | 覆盖时保留所需原有选项，避免只传 -march 丢掉其余设置 |
| eew / printf（Ara 软件入口） | 本地修改补默认64/1；服务器官方版无默认，显式传64/1 | 测试数据元素宽度与打印开关，不改变 Ara ELEN；见[重建Q06](../maintenance/E01/planning/server_reference_rebuild_guide.md#q06) |

如果已有**重新编译且匹配的 work 库**，可按现有 ModelSim 入口采用以下 Tcl 片段；这是用法示例，本轮没有执行。应在原流程规定的 `target/sim/vsim` 工作目录运行，并把 ELF 占位路径换成实际文件：

```tcl
set SELCFG 3
set BOOTMODE 0
set PRELMODE 0
set BINARY /absolute/path/to/verified_vector_test.spm.elf
source start.cheshire_soc.tcl
run -all
```

示例依赖匹配的仿真编译清单；第6节记录旧本地checkout清单问题，服务器后续已按向量入口对齐，使用时要核对所在目录和输入版本。`BOOTMODE=0` 直接加载 ELF 不需要 GPT；自主启动解析仍可支持 GPT/raw，镜像构建规则与硬件启动能力要分别看。

<a id="4-每次改配置的建议顺序"></a>

## 4. 配置修改与验证流程

1. 记录 git HEAD、工作区变更、CPU profile、Cfg 取值、宏、软件 ISA/ABI；明确只改哪个目标配置。
2. 在独立配置包/wrapper 和独立输出目录实施，保护旧 FPGA 工程。不要在原 DefaultCfg 上顺手做产品裁切。
3. 检查字段实际消费者、派生位宽/容量/地址与生成包尺寸；核对单位是 bit、byte、项数还是 log2。
4. 同步必要的源码清单、typedef、生成 RTL、软件头文件/链接脚本与启动方式；将“声明默认值、目标覆盖值、派生结果、该次构建展开值”分列。没有该次展开记录时，只标为源码推导。
5. 先语法编译和展开，检查重复 package/module、无效范围、端口截断、断言。
6. 运行与改动相关的最小功能测试，再进行性能/面积比较；记录真实结果和失败输入，写独立交接。

## 5. 最小验证矩阵

| 改动 | 最少应验证的行为 | 通过证据 |
| --- | --- | --- |
| 切 CPU profile / RVV | 启动、标量 ISA、向量整数与浮点 | 指令实际执行、结果比对、异常信息 |
| Ara lanes/VLEN | 不同 vl/SEW、跨 lane、tail/mask、向量 load/store | 与标量参考值一致、无超时 |
| cache/PMA/LLC | miss/回写或写穿、SPM 边界、CPU/Ara 共享 | 内存数据一致、配置读回、相关波形 |
| AXI ID/事务深度/宽度 | 多 ID、反压、burst、读写同时发生 | 响应 ID/顺序/数据正确，无死锁 |
| DMA | 1D/2D、stride、未对齐、跨边界、完成通知 | 目标区与参考数据一致，周围哨兵未破坏 |
| 外设关闭/地址改变 | BootAddr、链接区、MMIO、IRQ 和错误地址 | 正常路径完成、非法路径响应符合设计 |
| DDR/旁路拓扑 | 并发普通访存、共享区可见性、AMO/LRSC | 设计契约对应测试逐项通过 |
| SRAM/时钟/ASIC 适配 | 读延迟、byte enable、复位、CDC、时序 | 对应仿真/形式/综合报告，不用 FPGA bitstream 替代 |

“编译通过”“仿真返回 0”“板上计算正确”“时序签核”分别记录，不能相互替代。测试矩阵是后续工作建议，本轮没有执行这些测试。

<a id="6-本轮静态发现与待验证项"></a>

## 6. 源码静态发现与待验证项

| 项目 | 源码证据 | 对配置使用的影响 |
| --- | --- | --- |
| 旧本地生成清单的profile/decoder未对齐向量（历史检查） | 当时compile.cheshire_soc.tcl同时含标量profile、decoder stub、真实Ara decoder | SELCFG=3不足以修复；2026-10-18服务器清单已对齐，不能将此历史问题泛化为服务器当前状态 |
| SlinkMaxClkDiv 字段未被当前实例消费 | SoC/VIP 用包级常量，不用 Cfg 字段；Cfg 是 16 位 shrt_bt，可保存 1024，指数 Log2MaxClkDiv=10 不是该字段位宽 | 单改字段无效 |
| SPM 执行规则未覆盖高地址非缓存别名 | ExecuteRegionLength=2×SizeSpm；别名间隔 0x04000000 | 不承诺从非缓存别名执行代码 |
| DMA Regbus/访问宽度未统一 | wrapper 默认 Reg64，生成前端固定 DW=32；HAL 以 uint64_t 指针访问 32 位 ID | 先验收 lane/访问宽度及单次提交；wrapper 无完成 IRQ，不能靠错误 IRQ 代替轮询 |
| DMA 1D 分支 busy 信号可疑 | wrapper 连接 idma_busy，但声明的是 busy | 不能列为已验证可切换的 1D 模式 |
| DMA 驱动 decouple 位号需核对 | 两个宏表达式均移到 DECOUPLE_AW_BIT，当前宏为 0 | 开启 decouple 之前先对照寄存器定义 |
| VGA 错误记录容量与读并发不同 | VgaMaxReadTxns=24，错误单元 NumOutstanding=CoreMaxTxns=8 | 更改吞吐参数时补充错误路径验证 |
| PLIC/CLINT/AXI RT 为生成尺寸 | 当前 58 sources/2 contexts/1 hart；RT 6 managers | 加核/加 IRQ/加 master 需联动生成包 |
| 许多配置合法性检查仍是 TODO | cheshire_soc.sv 末尾 | 未报错不能推导组合合法 |

这些记录是配置手册的使用边界，不是本轮修复报告；各实现任务按用户授权处理。

<a id="7-可复制的团队配置记录模板"></a>

## 7. 团队配置记录模板

```text
配置名称/用途：
源码 HEAD 与本地差异：
CPU profile 文件；唯一性：
CVA6 关键最终值（RVV/RVH/RVSCLIC/PMP/cache/MMU）：
SoC Cfg 定义文件与覆盖项：
Ara lanes/VLEN/浮点支持：
总线地址/数据/ID/USER；事务容量：
LLC 总容量；启动 SPM 分配；运行期分配：
DDR AXI 契约；地址窗口与实际容量：
外设保留表；外部端口/IRQ；生成包尺寸：
启动方式；RTC/SoC/设备时钟来源：
软件工具链、ISA/ABI、链接脚本、VS/FS：
源码清单/宏；构建输出目录：
已执行命令、结果和日志：
未验证项与下一步：
```

<a id="teaching-20261007"></a>

## 配置候选的推导与验收（2026-10-07）

配置组合的合法性分为四层：字段能表达该值；模块约束和位宽成立；系统启动及软件契约成立；目标环境已完成相应验证。第三层尤其容易被忽略：一个取消 LLC 的系统可能可以展开，却无法沿原 Boot ROM 使用 SPM 栈启动。本地 SoC 尚有配置校验 TODO，assertion 未报错也不能替代这四层判断。

以“RVV 数组计算 + 新增 NPU 控制口”为候选，先沿以下顺序推导，无需为每一步新建实验：

1. 用向量 profile、真实 first-pass decoder 和 `ARA` 宏形成一致的编译输入；TB 的 `SelectedCfg=3` 只选择 SoC 参数。
2. 确认 Ara 单核、lane/VLEN 的必要断言和本地选择。声明范围不等于所有组合已验证。
3. 为 NPU 的控制目标配置 Reg 窗口；若它还主动访问内存，再增加 AXI 发起端。两件事分别计算。
4. 核对 Crossbar 来源/ID、生成模块尺寸、中断编号和访问属性；当前没有自动完整重生成流程。
5. 按软件 ISA/ABI、VS/FS、SPM/DRAM 布局及缓冲区所有权选择程序；初期应明确现有 CPU/Ara 一致性机制不能覆盖任意 NPU。
6. 把编译、展开、正常事务、错误/背压/复位和数值结果作为不同证据，保留实际命令和输入哈希。

输出一行配置记录至少包括：profile 路径及内容版本、宏、最终 Cfg、生成文件版本、工具链/ISA/ABI、链接模式、装载方式、初始化责任、验证平台与结果。当前教材表中的组合属于静态候选，已有实验记录仍按其原日期解释。

官方概述的扩展端口“最多 16”与参数表的 0..15 存在措辞差异；本地字段为 4 bit，应按当前消费者审查。不要把概述数字直接写进 Cfg。更完整的约束表见[网页配置组合](../learning/configuration.html#legality-levels)。

<a id="review-cases-20261007"></a>

## AXI RT、CLIC 与 IRQ Router 的独立配置案例（2026-10-07 复审修正）

三个案例共同采用单核标量 profile `cv64a6_imafdchsclic_sv39_wb`、Ara=0、Bootrom=1、PlatformRom=0、内部 LLC 保留；软件为原 `rv64gc_zifencei/lp64d`、`spm.ld`、`crt0.S`。装载沿现有 JTAG 流程，先核对 profile/decoder 和可用栈。以下均为源码静态确认及待验证场景，本轮未编译或运行。

| 配置记录 | AXI RT 预算 | CLIC 门限/向量 | IRQ Router 目标屏蔽 |
| --- | --- | --- | --- |
| 相对 DefaultCfg | 仅 AxiRt=1，SELCFG=1 | 仅 Clic=1，SELCFG=2 | 仅 IrqRouter=1；须新建独立配置，现有 SELCFG 无此项 |
| CPU 有效 RVSCLIC | 0 | 1，由 gen_cva6_cfg 覆盖 | 0；Router 不改变 CPU 中断模式 |
| 尺寸与编号 | 6 manager、2 region；CPU=0、Debug=1、DMA=2；生成头与 RTL 一致 | N_SOURCE=16+58+0=74、INTCTLBITS=8；CPU 源数、向量表及 PLIC/CLINT 生成规模分别核对 | NumIntrSrc 取实际 packed 类型宽度，目标数为 2；bit0→PLIC、bit1→核0 CLIC 分支（本例关闭） |
| 软件输入 | sw/tests/axirt_budget.spm.c；claim、region/预算/周期、enable 后启动 DMA | sw/tests/clic_basic.spm.S；mtvec 模式3、mtvt、mintthresh、源31属性/pending/enable | 待编写测试；UART源1对应 0x02080004 掩码，配置普通 PLIC handler，读UART清源再 complete |
| 最小结果 | 128×8=1024字节逐项一致，读/写预算都减少1024且剩余相等，返回0 | 门限0xff期间不进入成功路径，降为0后进入源31向量路径并返回0；错误/未到返回1 | 清理旧事件后，掩码0阻止新事件到PLIC；清理后改1、再次注入应领取源1并服务；观察输入/输出与计数 |
| 阻塞与范围 | 现有 iDMA 位宽/ID访问问题；加Ara后7 manager且DMA=3，原例不能直接复用 | 尚无本轮目标运行；本地开发版CLIC语义；原例不证明一般ISR现场恢复/mret/嵌套 | 缺专用配置入口、受控UART激励和完整测试；掩码复位1是源码事实，不是通过记录 |

所有场景设置有界运行超时，保存配置、程序/ELF来源、关键状态、结果及退出码。AXI RT 例验证预算计账，不证明预算耗尽后的实时性；CLIC 的软件置 pending 验证不依赖 Router；Router 的掩码不能替代 PLIC 优先级和 claim/complete。

源码入口：`target/sim/src/tb_cheshire_pkg.sv`、`hw/cheshire_pkg.sv::gen_cva6_cfg`、`hw/cheshire_soc.sv::gen_axi_rt/gen_clic/gen_irq_router`、`cheshire.mk::AXIRT_NUM_MGRS/AXIRT_NUM_SUBS`。Router 目标掩码定义/复位见 `.bender/git/checkouts/irq_router-376b3d113c15d0ef/rtl/irq_router{,_reg_top}.sv`。详细过程及来源链接分别见 [AXI RT](../learning/configuration.html#case-axi-rt)、[CLIC](../learning/configuration.html#case-clic)、[IRQ Router](../learning/configuration.html#case-irq-router)。
