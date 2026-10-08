# L01-ASIC：系统教材机制深化与 P01 工程手册实施

日期：2026-10-08。授权：用户要求多个子 Agent 实施，主管分配本任务；仅改教材/文档，生产 RTL、软件、依赖和工程配置只读。输入为 `mp/ara-pulp-v2`，HEAD `459f9d6f5748e39063f7bb67e959c2f27859915d`。已有全部修改作为输入保护，包含用户 PPTX 和上轮正文/证据。本报告是作者自查；主管的独立验收和发布证据另记。

## 1. 修改前问题与实际动作

| 章节 | 原问题或保留理由 | 实际修改/去向 |
|---|---|---|
| clocks | PLL 原理与共享输出影响解释正确；开头列时钟来源，未先说明谁给 CPU 第一个时钟 | 以安全取指→软件配置 PLL 开头；新增完整串口支路调频过程，区分接受/稳定/完成、全局影响与分频更新；原 PLL 图、公式和共享 M/N 条件保留 |
| reset | 复位源/里程碑有效；正常启动与故障恢复交错，释放机制未落到单元 | 改为复位起点→本地四级 rstgen→ROM/SPM/栈→外部 ready→排空后重启；严重边界仅短提示链接系统诊断 |
| power | isolation/retention/level shifter 和原图连贯，保留 | 加入一帧结束后的状态/内存所有权与下一帧恢复；epoch 明确为候选，不冒充实现；不指定电压/域/收益 |
| future | 原资源表是入口，单独 k+1/k+2 太抽象 | 改为固定输入→资源职责图→真实 VRF 链接→同一接口的验证层次→任务准入；旧 sram-example 保留为机制入口 |
| asic-memory（新增） | 缺真实存储消费者实例 | 操作数请求→bank 仲裁→tc_sram→延迟 valid/queue→操作数队列；尺寸复算、局部写、竞争、k+2 错配、宏拼接、视图/初始化/测试 |
| cdc-rdc（新增） | “有同步器”不足以解释事件/配置/AXI 与独立复位 | 从一笔多位配置握手讲起，再解释各信号类与 Gray FIFO、真实 DDR CDC 和 warm reset 限制 |
| physical-interfaces（新增） | 数字端口与物理层缺连续过程 | 用 I2C 第九拍 ACK 解释输出/OE/输入、FPGA IOBUF、PAD/封装/PCB/器件；不猜上拉/电压/LVDS参数 |
| timing-physical（新增） | SDC/STA 仅作为名词/清单 | 用 operand_requester→VRF bank 地址和返回路径解释 setup/hold、时钟/例外、宏摆放与时序反馈 |
| manufacturing-test（新增） | scan/MBIST 容易被端口/BIST 名称掩盖 | 正常 shift/capture/移出与 bank 遍历读写，测试交接、内容影响、当前 scan 绑值和 LLC tag BIST 范围 |
| silicon-bringup（新增） | 首硅只有抽象阶段名 | 连续计划：版本/供电→有效时钟/复位→ROM/SPM→标量/UART→DDR→Ara/系统；明确观察和测量边界 |

六个新页均为完整正文，不是占位；九主题中的 DDR/多主/论文测量由主管负责，本任务提供最小解释与回链。所有旧四页语义 ID 保留，旧图与 WaveDrom 不改，未触碰可编辑 PPTX、旧站和历史证据。公共导航、章号、生成页由主管统一。

## 2. 关键源码核对与保留限制

- `lane.sv::VRFSizePerLane`、`ara_pkg::NrVRFBanksPerLane/ELEN` 和 `vector_regfile::NumWords`：2 lanes / VLEN 2048 对应总 8192 byte、每 lane 4096 byte、每 bank 512 byte，即 64×64-bit 1RW；十六个 bank。
- `vector_regfile::p_rdata_valid`：req/read 有效及目标队列延迟一拍；`operand_requester` 请求直接 grant，返回 mux ready 固定有效；增加宏延迟不能只换实例名。
- generic `tc_sram` 默认 `Latency=1、ByteWidth=8、SimInit="none"`；Xilinx 版本固定零初始化。两种 target 的初值不能混用，更不能据 FPGA 上电零值声称 ASIC VRF 复位清零。
- `rstgen_bypass` 默认四级同步释放；普通 `cdc_2phase/cdc_fifo_gray` 明示两端 POR/warm reset 限制，clearable 也不能自动终止 AXI 已接受事务。
- `cheshire_top_xilinx::i_clkwiz.locked()` 和 `dram_wrapper_xilinx` 两种 MIG 的 calibration 完成输出未接；`cheshire_soc::i_dbg_dm_top.ndmreset_o()` 未使用。诊断交给主管 `system-debug#platform-readiness`，没有把未接等同实测启动失败。
- Ara scan 输入绑 0/输出未用，VRF 门控 `test_en_i=0`；LLC 文档仅 tag-store BIST，不能推导 DFT/全芯片 MBIST 已完成。
- 原有 S01-B01、iDMA、Ara 运行/写响应缺口均未关闭。

源码输入 SHA-256 及依赖路径见 [input.json](learning/evidence/system-implementation-20261008/asic/input.json)。Bender.lock 对这些项是本地 Path，revision/version 为 null；目录后缀不被冒充上游 commit。在线资料用于机制，不能覆盖这些本地快照。

## 3. 官方资料使用范围

本地随附官方资料优先：tech_cells_generic README/API/实现、Ara lane 文档及消费者、common_cells 跨域/复位头部契约、LLC BIST 文档。在线 2026-10-08 定向核对：

| 官方资料 | 本轮用途/版本边界 |
|---|---|
| [Cheshire Integration](https://pulp-platform.github.io/cheshire/tg/integr/) | SoC/平台责任和 Platform ROM 钩子；具体本地执行顺序回到 S 源 |
| [NXP UM10204](https://www.nxp.com/docs/en/user-guide/UM10204.pdf) | Rev.7.0，2021-10-01；普通双向 I2C 的 ACK/开漏/上拉，不扩为所有模式本地支持 |
| [OpenSTA 说明](https://openroad.readthedocs.io/en/latest/main/src/sta/README.html)、[示例](https://openroad.readthedocs.io/en/latest/main/src/sta/doc/Examples.html) | latest 查阅时的分析输入/时钟/例外/角概念；不指定项目 EDA 工具或写可用签核 SDC |
| [OpenROAD CTS](https://openroad.readthedocs.io/en/latest/main/src/cts/README.html) | 宏和时钟树进入布局反馈的职责 |
| [Siemens Tessent 2024.1 方法课程](https://training.plm.automation.siemens.com/ilt/iltdescription.cfm?pID=276866-US_____EDA__2024.1_1199)、[MemoryBIST](https://www.siemens.com/en-gb/products/ic/tessent/test/memorybist/) | scan/ATPG/ATE 与存储测试/修复范围；非产品选型或本地工具可用证明 |

没有复制受限供应商交付，也没有选择工艺宏、PLL/PAD、频率、电压、域数或测试工具。

## 4. 读者任务验收：作者回答及定位

| 任务 | 应能复述的答案与正文定位 |
|---|---|
| PLL 由软件配置，CPU 第一条指令的时钟从哪来？ | 硬件先给安全时钟/复位和取指条件，再由同一 CPU 的平台代码配置；clocks#clocks |
| 串口调频什么时候可以继续发送？ | 停新任务、等 FIFO/移位器和相关事务排空、按 IP 切换稳定、更新分频/软件时间、开放；clocks#normal-frequency-change |
| reset 撤销是否等于 C 可运行？ | 本域同步释放后还需存储/栈/入口和应用初始化；reset#readiness |
| 关计算域后上一帧结果属于谁？ | 结果是否保留取决于存储域；完成与所有权先交常开/CPU，计算配置保持/重建另定；power#shutdown/#wake |
| 同容量 SRAM 多一拍哪里出错？ | k+1 valid/queue 身份与 k+2 数据错配；请求 grant、队列预留和门控也须一起评估；asic-memory#k-plus-two |
| 多位配置为何不逐位同步？ | 各位可能来自不同快照；锁存整组并握手，接收完成不等于配置完成；cdc-rdc#handshake |
| I2C 释放 SDA 后输入为什么仍能低？ | OE 关只释放本端，目标 ACK 经线路/PAD反馈；physical-interfaces#ack-path/#open-drain |
| hold 违例为什么不能一律降频解决？ | 关注同边沿最早新值和时钟偏斜，不由周期增大保证；timing-physical#setup-hold |
| 已有 BIST/scan 为什么不等于量产测试完成？ | 测试对象、接管、故障模型/覆盖与访问链不同；manufacturing-test#local-scope |
| 第一个 DDR 测试代码/栈放哪里？ | 已验证片上存储，避免先依赖待测外存；silicon-bringup#staged-run |
| 一份 RTL 仿真通过报告证明什么？ | 同一输入/模型范围内的行为；不替代物理、电气、制造或更大系统证据；future#verification-layers |

这些是作者基于正文的任务回答，不是假称真实读者试读通过；主管可据此独立复述验收。

## 5. 后续追加：P01 工程手册

主管追加授权后，已创建 [P01_ASIC_Adaptation_and_Evidence.md](P01_ASIC_Adaptation_and_Evidence.md)：定向资源清单、SRAM 适配记录字段、生命周期配置契约、验证矩阵、输入负责人和解锁条件。它引用 HTML 机制，不重复02提取规格；盘点包括 XPM/MIG/MMCM、通用/CPU/Ara/LLC存储入口、ROM、时钟/复位/CDC、USB/DDR PHY、PAD、scan/MBIST。没有声称完成全设计展开/存储数量审计。

P01 具体映射等待工艺宏/PLL/PAD/PHY/EDA/DFT资料；E01 提供固定展开基线，M01/I01提供接口与流量，S01提供初始化软件，V01提供实际回归。文档与条件实验计划可做；实际工程和目标运行不在本轮授权。

## 6. 只读交叉复审与检查

完整读了 software Agent 本轮 `traps/boot/boot-debug`，审查限定为时钟复位、启动栈、调试停止和平台钩子的相互一致。没有发现该边界内的阻塞矛盾：正常前提与已知缺口分开，SPM配置位不扩大成栈完成，halt不冻结整个SoC，trap要求有效栈。向主管提供一项可选导航建议：boot#default-path 回链 clocks#clocks 或 reset#readiness。未修改这些他人文件，也未将这次定向复审冒充全书技术审计。

本任务检查见 [final-checks.txt](learning/evidence/system-implementation-20261008/asic/final-checks.txt)：十页 ID 唯一、H2/H3 有语义锚点、旧四页 35 个 ID 全保留；111 个本地 HTML 链接/资源和三份 Markdown 的 37 个本地链接通过；21个首批生产/依赖文件哈希不变；两组 VRF 尺寸复算；git diff --check 退出0。可重现命令为 `python3 docs_codex/learning/evidence/system-implementation-20261008/asic/check_asic_docs.py`。learning 文件在 2026-10-08 03:17:52 UTC 冻结交主管发布。生成、全站结构/链接、桌面/手机浏览器和最终保护由主管统一执行，不能把主管尚未完成的检查写成本任务通过。

未运行任何目标构建、RTL仿真、综合、CDC/RDC/STA、DFT、物理实现或板/首硅测试。图稿、脚本、生成页与共享状态均不属于本任务写入范围；没有 Git 提交。
