# 本轮官方资料与本地版本的对应关系

核对日期：2026-09-29。阅读原理以官方资料为补充，实现结论以当前本地消费者为准。网站正文及配图离线自足，下面的外部链接只用于进一步追溯。

| 官方资料 | 本轮实际阅读及用途 | 版本边界 |
| --- | --- | --- |
| [Cheshire Architecture](https://pulp-platform.github.io/cheshire/um/arch/) | 系统层次、地址区域和启动说明 | 在线文档没有绑定本地 HEAD；大区域常表示预留空间，实际窗口按 `gen_axi_out/gen_reg_out` 重算 |
| [Cheshire SoC Integration](https://pulp-platform.github.io/cheshire/tg/integr/) | 配置结构、扩展接口、VIP 与 Platform ROM 的前置条件 | 官方建议的 Bender 流程是参考，用户独立固定配置/静态清单方向继续有效 |
| [Ara dispatcher 官方说明](https://github.com/pulp-platform/ara/blob/main/docs/source/modules/ara_dispatcher.md) | 算术早应答、load/store 等待地址与异常的概念 | main 文档不能证明冻结版本的总线错误支持；本地 vstu 明确仍有 B 错误 TODO |
| [RVV 官方归档 v1.0](https://github.com/riscvarchive/riscv-v-spec/blob/v1.0/v-spec.adoc) | 分组、mask/tail、按 vl 分块、访存与归约语义 | 使用明确的 v1.0 标签；不是硬件支持矩阵 |
| [RISC-V 20240411 V 页面](https://docs.riscv.org/reference/isa/v20240411/unpriv/v-st-ext.html) | 对照术语及章节 | 本次页面标题为 Version 1.0，导言却含 1.1-draft 字样；不静默抹去差异，冻结语义另交叉查 v1.0 归档 |
| [GCC 15.2.0 RVV intrinsics](https://gcc.gnu.org/onlinedocs/gcc-15.2.0/gcc/RISC-V-Vector-Intrinsics.html) | 头文件入口及该版手册声明的 intrinsic 0.11 | 本地 GCC 实际宏为 `__riscv_v_intrinsic=12000`，以本轮具体函数编译和 dump 验证可用性，不将不同网页/API 版本混同 |
| [GCC 15.2.0 RISC-V options](https://gcc.gnu.org/onlinedocs/gcc-15.2.0/gcc/RISC-V-Options.html) | ISA、ABI 和代码模型选项 | 参数只声明编译目标；不能改变 RTL profile 或 VS/FS |
| [Arm AMBA AXI/ACE IHI0022H PDF](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf?revision=71bd7c57-2ed7-487b-bc3e-68c4ab56fa5f&la=en&hash=6325311012DDADF238C35A6C0FD734E520754F82) | A3 握手依赖、通道与 AXI4 事务规则 | PDF 同时包含 AXI/ACE 多种协议；本工程普通 AXI4 不因此自动实现 ACE 或全部新扩展。网页入口重定向无正文，实际读取了官方 PDF |
| [pulp-platform riscv-dbg README](https://github.com/pulp-platform/riscv-dbg/blob/master/README.md) | DTM/DM、abstract/progbuf/SBA 功能边界 | 具体 DMI 字段及 0.13.1 声明核对本地 README/dm_pkg；不把在线 master 当当前 RTL |
| [WaveDrom 官方项目](https://github.com/wavedrom/wavedrom) | 标准波形描述和 SVG 输出 | 离线渲染固定 3.5.0；来源、包哈希、许可证保存在 `assets/vendor/wavedrom-3.5.0/` |

本地根 HEAD 为 `4f240258ca683913b7e17949aff23139bff981f1`。`Bender.yml` 指定 CVA6 `pulp-v2.0.0-alpha.1`、Ara `2895ba907e9eb14b3464609dc791a969d159a7c3`，但本地依赖和修改纳入主仓库，不能用上游标签替代内容哈希。固定版本 Ara/CVA6 在线路径本轮读取失败，CVA6 在线手册也未取得有效正文；改读本地随依赖提供的 README、FUNCTIONALITIES、lane 文档和实际 RTL，未声称成功取得这些失败的网页。

本地证据入口：

- [本地来源哈希](evidence/depth-20260929-sources.json)
- [工具链/构建实测](evidence/depth-20260929-builds.txt)
- [扩充章节与证据分工](DEPTH_EXTENSION.md)

配图不得复制厂商受限数据手册。新架构图为按本地连接重绘的教学抽象；新时序图全部保留 WaveDrom JSON 与离线 SVG，明确标注教学时序。真实波形应额外标明运行配置、信号层次、时间单位及仿真产物，不能用教学图冒充。

<a id="teaching-20261007"></a>

## 2026-10-07：官方章节拆解与本地消费者核对

本节是新一轮记录，不改写上文 09-29 的访问结果。输入 HEAD 为 `5ddec4fb4e982b460b12c3f3587523807602d5d4`。本次成功读取 Cheshire 在线架构、集成、软件页及 CVA6 Parameters/PMA 页；在线网页属于持续更新版本。教学正文以概念解释和本地实现推演为主，第三方参数全集仍在现有配置字典中。

| 官方章节或随附官方说明 | 融入的教学内容 | 本地依据与适用边界 |
| --- | --- | --- |
| [Cheshire Architecture](https://pulp-platform.github.io/cheshire/um/arch/)：Components / Interconnect | [模块的多种接口角色](architecture.html#port-roles)、[结构配置与运行时控制](interconnect.html#configuration-versus-registers) | `cheshire_soc` 的实际端口/实例与 `gen_axi_in/out`；外设是否存在由有效 Cfg 决定 |
| 同页 Memory Map / LLC | [地址逐层解释](address-map.html#address-translation-example)、[LLC/SPM 请求推演](memory.html#llc-transaction) | 区别路由窗口、物理容量、PMA 与链接预算；官方 SPM 预留区不当作本地容量 |
| 同页配置表；[CVA6 Parameters](https://cva6.readthedocs.io/en/latest/01_cva6_user/Parameters_Configuration.html) | [CPU 可选配置族](cva6.html#configuration-families)、[有效值](cva6.html#profile-effective-values)、[组合约束](configuration.html#legality-levels) | 本地 88 个 CPU 用户字段、113 个 SoC 字段；profile → gen_cva6_cfg → build_config → RTL。在线新增字段不反填本地结构 |
| [CVA6 PMA](https://cva6.readthedocs.io/en/latest/01_cva6_user/PMA.html) | [PMA/PMP/MMU 职责](address-map.html#address-translation-example) | `gen_cva6_cfg` 的静态属性与核内消费者；普通独立核的概念描述不替代本地 Ara 专用协作实现 |
| [本地 AXI Crossbar 说明](../../.bender/git/checkouts/axi-ecdc900686449c15/doc/axi_xbar.md) | [地址规则、来源 ID、顺序与修改边界](interconnect.html) | 文档与 `axi_xbar_unmuxed/axi_mux/axi_demux_simple` 交叉阅读；本地 `AxiMap` 是常量，通用 IP 的动态输入能力未成为 SoC MMIO 功能 |
| [本地 LLC 设计说明](../../.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/doc/axi_llc.md) | [按行拆分、脏行写回、填充和 SPM](memory.html#llc-transaction) | `axi_llc_hit_miss/evict_unit/refill_unit` 与 Cheshire Reg32 wrapper；文档的通用 AXI-Lite 包装不替代当前寄存器偏移 |
| [SoC Integration](https://pulp-platform.github.io/cheshire/tg/integr/)：Instantiating | [Cfg 与接口类型、各扩展端口方向](integration.html#official-instantiation)、[DDR 平台契约](ddr.html#platform-contract) | `CHESHIRE_TYPEDEF_ALL`、SoC 顶层及平台 wrapper；固定配置/静态清单仍为用户确认方向 |
| 同页 Platform ROM；[Architecture Boot ROM](https://pulp-platform.github.io/cheshire/um/arch/#boot-rom) | [平台钩子三种配置情况](boot.html#platform-rom)、[PLL 启动与运行时设置](clocks.html#boot-and-runtime-frequency) | `BootAddr`、只读 PLATFORM_ROM、`_prom_check_run`、生成 ROM；正常返回缺口见下表 |
| [Software Stack](https://pulp-platform.github.io/cheshire/um/sw/) | [软件职责分层](runtime.html#software-stack)、[Make 配置](build.html#software-options)、[ZSL 后续阶段](boot.html#later-stages) | `sw/sw.mk`、crt0、链接脚本、DIF/HAL、zsl；裸机与 Linux 层次分开，本地寄存器生成流程按 HJSON |
| [tech_cells_generic 随附说明](../../.bender/git/checkouts/tech_cells_generic-223c43ccbeb688f9/README.md) | [工艺资源映射与 SRAM 时序推演](future.html#resource-mapping)、[时钟/复位/电源边界](power.html#domain-orthogonality) | 抽象层需要平台实现；未假定选定宏、频率、电源域或供应商寄存器 |
| Ara 本地 [FUNCTIONALITIES](../../.bender/git/checkouts/ara-2c7b103275a16c87/FUNCTIONALITIES.md) 与 [lane 说明](../../.bender/git/checkouts/ara-2c7b103275a16c87/docs/source/lane.rst) | 既有 [专用接口](ara.html#interface)、新增 [VRF 与共享张量](sharing.html#vrf-versus-shared-memory) | `ara.sv`、dispatcher、VLSU、失效过滤与 CVA6 acc_dispatcher；NPU 共享协议为未来方案 |

版本差异与未验证条件：

| 项目 | 当前核对结果 | 教材处理 |
| --- | --- | --- |
| Platform ROM 正常返回 | 本地 jalr 后落入 boot_next_stage；本地 git 对象中可读上游修复 `9b4c222df72f74f90ab9f36d80ba7b527f92e62b`，但它不是当前 HEAD 祖先 | 说明官方契约和本地缺口，独立修复/ROM 重生成/返回回归；不修改生产代码。在线 commit 页本轮抓取失败，修复依据为本地 git 对象 |
| 扩展端口上限 | 官方概述写最多 16，同页参数表为 0..15，本地计数字段为 4 bit | 不以概述证明值 16 可用，按本地字段与消费者审查 |
| 寄存器头生成 | 在线软件页使用 RDL/PeakRDL；本地 Make 使用 HJSON/REGTOOL | 用当前规则解释编译，不要求升级生成器 |
| EEPROM boot mode | 随附旧说明存在编码笔误，本地 C switch 使用 3 | 正文使用源码模式 3，保留历史差异记录 |
| CPU cache 字段名称 | 本地用户字段 `DCacheType`，辅助 localparam `CVA6ConfigDcacheType` | 修正网页两处字段大小写，不改变 cache 选择结论 |
| ASIC 资料 | Cheshire 提供系统数字接口与平台钩子；未提供本项目选定工艺的完整 PLL/DDR/低功耗交付 | 按职责、依赖和验收解释未来方案，不编造寄存器及频率 |

源文件哈希见 [sources.json](evidence/teaching-20261007/sources.json)。HTML 与 Markdown 采用相同概念和当前源码结论，原有表格、命令、实验和动态验证记录保留。
