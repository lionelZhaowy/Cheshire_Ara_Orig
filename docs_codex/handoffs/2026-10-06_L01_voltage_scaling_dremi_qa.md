# L01 / Dremi 固定板级供电与电压调整答疑

## 基本信息

- 日期：2026-10-06；任务 L01；用户要求确认 Dremi 固定板级 LDO 与片上调压能力，并介绍行业实现。
- Cheshire HEAD `5ddec4fb4`；上轮 AGENTS.md、状态、任务表、索引及 Platform ROM 专题文档变更保留。本轮仅新建本交接。
- Dremi 只读输入 `/mnt/d/Personal_Files/ServerSyn/dremi_ding_aps_mipi`，无 Git。前轮已读取该工程 AGENTS/context/sync 约定；未修改已流片 RTL、未访问远程或同步。
- 状态：答疑与静态核查完成；板级电源事实仍需原理图/型号，电压调整未实现。

## 结论及证据边界

- 用户报告：Dremi 由板级 LDO 输出固定电压供电。若 LDO 输出固定，或其反馈由固定电阻设置且没有控制入口，软件不能通过 PLL 寄存器改变该供电电压。降低时钟可以是 DFS，不因此具备 DVFS。
- 当前芯片接口/配置模块/MPU 软件未发现核心供电电压控制、PMIC/DVS 目标配置或内部可编程核心稳压器的管理实现；不能据此对所有未检查的模拟 IP 宣称绝无内部 LDO。
- `src/design_core/out_wrapper_top.sv:33` 起包含复位、参考时钟、数据、消息、I2C 和 QSPI PAD。已有 SCL/SDA 名称不证明有 PMIC 接入或软件调压功能。
- `out_wrapper_top.sv:208` 的系统 PLL 接收频率配置字并输出 SocClk，仿真电源端口以逻辑 1/0 表示；它们不是实测电压或板级稳压模型。真实供电网络通常不由这种数字 RTL 完整呈现。
- `io_interface/PLLConfig.sv:20` 只把有效输入锁存到 PLL 配置输出；本轮不能把 PLL 控制字等同核心 VDD 控制。
- 定向检查 doc、design_core/io_interface/off_src、MPU main 与两个 API 头文件，没有发现电源调压相关实现；工程内未找到可供本次核对的板级原理图/电源器件资料。因此实际 LDO 型号、反馈及外部控制仍是证据缺口。
- Cheshire 教材 `learning/content/power.html:6` 标明候选多电源域未实现。`cheshire_soc.sv:1713` 的 Link isolate/clock-enable 输出未连接完整电源管理；本地尚无已验证的调压系统。

## 官方补充资料

- [TI SLVA646](https://www.ti.com/lit/an/slva646/slva646.pdf)，第 4 节：SoC 与供电系统必须共同支持电压调整；外部 PMIC 可经 I2C/SPI/GPIO 管理。通常片内负责策略/命令，板级器件实际改变供电。
- [NXP PCA9460 datasheet](https://www.nxp.com/docs/en/data-sheet/PCA9460.pdf)，7.6.1.2：buck 的 DVS 可由 MODE/待机请求脚选择，且有寄存器/I2C 控制配置。作为接口实例，不作为本项目选型。
- [TI TIDA-00531](https://www.ti.com/tool/TIDA-00531)：可调 LDO 配合 I2C 数字电位器的 DVS 参考设计。说明 LDO 不必天然是固定输出；能否动态调整取决于器件和实际反馈电路，不能直接套用现有板卡。
- [ST STM32U5 电源管理培训](https://www.st.com/content/ccc/resource/training/technical/product_training/group1/95/38/81/9b/cb/0d/43/89/STM32U5-System-Power-management_PWRMNGMNT/files/STM32U5-System-Power-management_PWRMNGMNT.pdf/_jcr_content/translations/en.STM32U5-System-Power-management_PWRMNGMNT.pdf)：内部 LDO/SMPS 支持电压档位，说明片上调压也是另一种实现；不代表当前 Dremi/Cheshire 或具体 55 nm 工艺已有这些 IP。
- [Linux OPP 文档](https://cdn.kernel.org/doc/html/latest/power/opp.html)：工作点是域所支持的频率/电压组合。仅用于解释合法工作点，不声称已移植 Linux DVFS。

## 工程建议，尚未冻结

- 当前设计若维持固定供电，可优先支持该电压允许范围内的调频/时钟门控；不能承诺降频自动降压，或在未验证的高频下运行。
- 若后续需要 DVFS，优先评估板级可编程 PMIC/buck 与芯片控制接口；片上 LDO/DC-DC 是额外模拟 IP 及电源完整性工作，非 DVFS 必需条件。
- 独立时钟域不自动成为独立电压域。独立调压需要独立的有效供电网络（外部 rail 或片上调节器）、宏/库电压范围及跨域电平转换；同电压可关断域又是不同能力，电源开关本身不产生可调稳定电压。
- 通常升频需要先达到所需电压并确认稳定，降压前先将频率降至目标电压允许范围；电压未改变的调频不必强行执行升降压步骤。工作点、SRAM/PLL/PHY限制、斜率/稳态与负载瞬态必须验证，PGOOD语义按实际器件确认。
- 共享 rail 的 CPU/Ara/互连/SRAM 电压须满足所有活跃消费者；不能仅凭 CPU 降频就给全域降压。PAD/PLL/PHY/DDR 供电不可随核心工作点任意变化。

## 验证与下一步

- 命令：Git 状态/HEAD 只读检查，rg 文件与相关符号定向搜索，nl/sed 检查 top/PLLConfig/教材和 SoC Link 边界，sha256sum 记录小型输入，浏览厂商官方资料。
- Dremi top SHA-256：`bc2cddeef62de720a1cdcbfbb1ad46933c64c0d550078ad6e52a1e7bfbe0a376`；wrapper：`0fe31fc9f5dae432a62f8abb8186317be276dd9e2ff0300227fc7bcd2c778ce5`；MPU main：`8bf7b2a8b273690a14a488446160b726e8748159fbdb898b4b539dd19975c138`。
- 未编译、未仿真、未板测、未测电压、未改变供电或频率，未修改共享状态/任务决定。既有 Platform ROM 配置约定未被扩展成已决定 DVFS。
- 最小下一步：用实际板级原理图/BOM 确认 LDO、反馈、使能/控制及各 rail；若需求需要，再由 P01 核对 55 nm 库/宏和芯片 PAD/电源网络，确定 DFS 或 DVFS 边界。
- 未提交 Git。
