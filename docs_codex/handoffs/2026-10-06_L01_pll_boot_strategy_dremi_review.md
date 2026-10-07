# L01 / Dremi 初始化限制与 Cheshire PLL 启动方案选择

## 基本信息

- 日期：2026-10-06；任务 L01。
- 用户授权：比较 RefClk 硬件初始化与参考时钟启动后软件初始化，结合指定 Dremi 工程提出建议；不包含 RTL 实施。
- Cheshire 输入：`mp/ara-pulp-v2`，HEAD `5ddec4fb4`。已有未跟踪文档、图和 tools/ 保留。
- Dremi 输入：`D:/Personal_Files/ServerSyn/dremi_ding_aps_mipi`，本轮经 `/mnt/d/Personal_Files/ServerSyn/dremi_ding_aps_mipi` 只读访问；无 .git，未连接服务器、未同步、未修改该工程。
- 已阅读 Dremi AGENTS.md、doc/AI_PROJECT_CONTEXT.md 和 doc/SYNC_WORKFLOW.md；遵守已流片 design_core/ip/debug_core 的禁止修改边界。
- 状态：源码核查及建议完成；方案未冻结、未实现、未动态验证。

## 当前源码证据

### Dremi

- 主 TB `sim/tb_sim_core.sv:339` 实例化 `out_wrapper_top`，该 top 在 615 行实例化 `dremi_soc_wrapper`；原编译脚本通过 design_core/off_src/io_interface 库目录解析这些模块。
- `dremi_soc_wrapper.sv:627` 实例化 `RegInitialConfig`，时钟为 FlashClk；801 行实例化 FrequencyCut。已沿实际赋值确认 `io_interface/FrequencyCut.sv:29` 为 `assign FlashClk = RefClk`，虽然端口注释写着 40M→10M，但本版本 FlashClk 实际直接沿用 RefClk；单独 clk10M 输出才由计数器生成。PLLConfig 与 MipiInterfaceRx 配置寄存器分别接 RefClk、由 RefClk 连接的 TxEscClk，与用户所述参考域初始化一致。
- `off_src/RegInitialConfig.sv:48` ConfigStart 只在复位后置位，进入 SocPllConfig 后清零；149 行起每个 RX 配置项处理一个有效数据字，243 行 ConfigEnd 永久自环，未有软件重启入口。
- `io_interface/PLLConfig.sv:20`、`io_interface/MipiInterfaceRx.sv:117` 的锁存器在有效写事件时更新，无内部一次性写锁；wrapper 的输入为启动配置数据与对应配置标志。本次核对的通路没有提供给软件的独立寄存器重写接口。
- 所以当前痛点来自固定的启动调度/后续写入口缺失，不是硬件初始化 FSM 或模拟配置寄存器必然只能写一次。可重复命令状态机或硬件启动后软件访问同一配置银行都可解决架构上的限制；不代表已有硅片可以无条件修复。
- 用户提供 PD_BG 必须先 1 后 0 的要求；本轮未核对供应商位号、电气含义或等待时间，未把该语义当作已由本地源码独立确认的事实。
- 小型输入身份 SHA-256：
  - RegInitialConfig.sv：`01b7ab4b4e95f1997f51bc852e4948fa820820b62805e0dd7c6f72363c03c958`
  - PLLConfig.sv：`a2287e805029a9d306143847cee8bf9c99faef32db7d038531530c259d8fe5f3`
  - MipiInterfaceRx.sv：`2eca94402436d3f133d03326173cb0cd91c0e58615d01dc3a84f8cd1ac7ee738`

### Cheshire

- `hw/cheshire_pkg.sv:118`、`hw/cheshire_soc.sv:432` 提供通用外部 Regbus 扩展，未自带 PLL/MIPI 管理器或配置跨域桥。
- `hw/bootrom/cheshire_bootrom.S:59` LLC BIST/SPM 先于 80 行 Platform ROM 钩子；RefClk 启动需 CPU/互连/ROM/LLC 具备有效时钟及复位、可访问宏。
- `docs/um/sw.md:42` 明确硬件 Boot ROM immutable；90 行描述 ZSL mutable。使用 Boot ROM 执行多次寄存器写不等于流片后可以修改 ROM 算法。
- `hw/bootrom/cheshire_bootrom.c:50` SPI NOR 选择与 core_freq 相关的读取速率；SD 路径固定目标 24 MHz，并由 HAL 检查目标速率不高于 core_freq。RefClk 低频启动应逐个核对引导介质和驱动，不能泛称所有入口原样可用。
- `target/xilinx/src/cheshire_top_xilinx.sv:445` 当前 RTC 来自系统时钟分频；ASIC 采用频率切换时应另设稳定 RTC/超时基准，或严格维护实际频率一致性。
- 本地 `common_cells/src/clk_mux_glitch_free.sv` 明确要求切换时两源稳定，会短暂停止输出，使用 tech clock cells 并要求工艺映射/综合保护；复位时旁路不提供常规滤毛刺，选择需保持稳定。该模块无完整 PLL 就绪检测、软件请求完成接口或死时钟恢复协议，不能单独当完整时钟控制器。

## 建议，尚未实施

- 优先采用方案 2 的参考时钟启动结构，外加最小 RefClk 常开硬件管理器：保证默认安全旁路、POR 安全值、复位/时钟切换、独立超时与故障恢复。CPU/固件决定配置值和重复操作顺序，硬件负责边沿、执行握手及失效处理。
- Boot ROM 只保留足以进入 SPM、读取可靠引导介质及进入恢复路径的最小固定代码。Flash 加载到 SPM 的可更新早期固件配置 PLL、申请切换，再初始化 DDR/MIPI/其他外设；不要求以 Linux/OpenSBI 为前置，现有 ZSL 是软件分层参考而非已实现的硬件管理程序。
- 如果引导介质必须依赖 PLL，可采用小型可恢复的 ROM 初始 PLL 步骤，再由可更新固件管理后续 IP；不要把全套模拟 IP 的复杂初始化都固定在 ROM。
- 常开域保留 PLL/PHY 配置银行、功能复位控制和 RTC/超时；配置访问跨域应有完整多位数据及请求/应答协议，不能只对写脉冲加同步器。保持可读写、读回及明确错误响应，局部功能复位不应无意销毁配置或令配置接口无法访问。
- 按用户提供序列，PD_BG 可通过写 1、等待或状态轮询、写 0、再等待并释放 RX 的固件流程实现；POR 所需安全默认值须由硬件提供，实际时长、位号和允许重配置条件以供应商资料为准。
- 第一次 RefClk→PLL 切换尽量在 SPM 执行、DDR/MIPI/DMA 未开始工作时完成。常开管理器先接收请求、确保寄存器总线事务不会因切换悬挂，再在两源稳定下完成安全切换并反馈状态。主域暂停能否保持 SRAM/接口状态需验证，正常切换不能清除配置及复位全部执行状态。
- PLL 运行时重配必须先返回有效安全时钟，再按 IP 要求改变 PLL；PLL 不锁保持 RefClk。真正失锁/时钟停止不是普通 mux 两稳定时钟的切换问题，需硬件故障响应及受控恢复，首版可选择复位恢复而非无损续跑。
- 方案 1 加软件接管同样可以支持重复 PHY 配置，且省去首次 CPU 运行中的时钟切换；当 RefClk 无法支撑最小启动或无法取得可验证的切换实现时，这是合理备选。选择方案 2 不是由 PD_BG 单项要求逻辑上必然推出的。

## 验证与最小下一步

- 仅执行 Git 状态/版本检查、rg 搜索、定向 nl/sed 阅读与小文件 sha256sum，并访问 Cheshire 官方集成/启动文档。没有编译、仿真、综合、STA、板测、远程操作或 Dremi 修改。
- [Cheshire Platform ROM](https://pulp-platform.github.io/cheshire/tg/integr/#platform-rom)、[Cheshire Boot Flow](https://pulp-platform.github.io/cheshire/um/sw/#boot-flow) 与本地分层一致。尝试在线读取匹配 common_cells 版本的时钟 mux 文件返回 cache miss，具体判断以本地快照为据。
- 最小下一步：提供具体 PLL/PHY 的启动、锁定、重配和配置接口契约；先验证 RefClk 下 SPM/Boot/Flash，再验证寄存器 CDC 重复写/局部复位，再验证 RefClk↔PLL 切换及失败留在安全时钟。生产 RTL 实施需要另行授权。
- 本轮不把建议写成用户已冻结决策，不修改共享状态或任务表。
