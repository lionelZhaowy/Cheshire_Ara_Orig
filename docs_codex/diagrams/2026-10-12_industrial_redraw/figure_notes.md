# 工业风格重绘 · 图意、版本与阅读边界

本轮是视觉重绘，沿用输入图稿的技术内容。原图中较长的阅读说明、依据与验证边界整理到这里；原始全部文本和 SVG 哈希保存在 [来源清单](source_inventory.json)，原图文件不变。没有重新验证原图所述全部 RTL 行为，也没有集成新 IP。

## 1. crossbar_ara

- 对应原图的 `tb_cheshire_pkg::gen_cheshire_ara_cfg()` / SELCFG=3 静态快照（原标注 HEAD `5ddec4fb4`）。Ara=1，2 lanes / VLEN 2048，主 AXI 数据 64 bit，`Cfg.AxiRt=0`，输入直接接 Crossbar。
- 7 个发起端、7 个输入 DEMUX、5 个目标 MUX、5 类目标全部保留；35 条灰线表示可达关系，彩线表示请求示例。内部矩阵保留斜线，避免把全连接关系画成一条实际共享导线；矩阵以外为正交连接。
- 每个输入按 AR/AW 地址选择目标；每个输出独立仲裁。不同目标可并行，访问同一目标才在该处竞争。图中通道组概括 AR/AW/W 请求及 R/B 返回；未映射请求进入各输入错误响应单元，局部缓冲/适配及错误单元未展开。
- S/M 是 Crossbar 端口视角：S 接系统 master，M 接系统 slave。Debug/SBA 发起端和 Debug 目标窗口分开；iDMA 数据 master 和控制 slave 也分开。
- Ara 经过失效过滤与位宽适配，本配置 64→64 bit；其 CVA6 专用指令/MMU 接口不属于主 AXI 矩阵。
- M2 是 LLC/SPM 共用目标；原子适配、cut、地址重映射后进入 LLC。SPM 128 KiB，存在 cached/uncached 别名；外存窗口是 `[0x8000_0000, 0x1_0000_0000)`。SPM/cache 命中可在片内完成，其他外存访问由 LLC 下游接平台 DDR。
- M3 iDMA 控制从 `0x0100_0000` 起。M4 Slink TX 窗口是 `[0x1_0000_0000, 0x2_0000_0000)`。
- 原图注明 VCU118 加源脚本关闭 SerialLink/USB、开启 Ara，因此是 5×4、RT 同样关闭；本图继续采用仿真配置 7×5，不把两者混为同一实例。

## 2. ddr_qos_proposal

- 保留原独立主口候选：S0=SoC/LLC，S1=ISP，S2=NPU。原图早于共享 GB/统一搬运方案，重绘标题下标明其历史方案身份；**不把它的 S1/S2 与第 7、9 图交换或混用**。
- SoC 经 Crossbar、原子适配和 LLC；SPM 可留在片内。ISP/NPU 数据绕过主 Crossbar/LLC，分别到 DDR 端口。各端口请求进入共同仲裁，再进入控制器核心，不代表多口各自独占带宽。
- 原图使用 DDR Controller V2.1 的接口摘要：p8 最多 8 个 AXI 端口；p10 仲裁特性；p13 每口 QoS；p17–18 内部结构与命令调度。重绘保留可配置优先级、轮询、页命中限制、命令队列、FR-FCFS 和 DRAM 时序约束；本轮未重新调阅或导入供应商受限材料。
- 原摘要注明 p14 不支持独立 AXI Urgent 接口。具体优先级/QoS 寄存器与映射、带宽保底、最坏延迟仍待用户手册确认。是否额外加 RT 需结合控制器能力评估。
- 多端口不能自动解决共享缓存一致性或旁路写入的 AMO/LRSC 观察范围。当前 RTL 未因此完成供应商 IP 集成。

## 3. example

保留输入→处理→输出、输出反馈到输入的机制，改为工业风格方角块与完整曲线箭头。它是通用图形示例，不是工程 IP。旧图关于“圆角框/椭圆”的外观说明随重绘失去适用性，改为原生矢量对象说明；未保留无技术含义的装饰椭圆。

## 4. initialization_hw_sw

- 原静态快照为 Bootrom=1、PlatformRom=0、内部 LLC、根 SDK 载荷入口（HEAD `278434024`，2026-10-08）。左侧是硬件职责，右侧是同一个 CVA6 执行的软件阶段，不是另外三个处理器。
- 有效 `clk_i/rst_ni` 来自外围平台。LLC tag BIST 在复位后自主测试；ROM 汇编轮询 DONE 并通过 CFG_SPM/COMMIT 配置 SPM。**DONE 只表示完成，不等于 BIST_OUT 无错误。** tag BIST 不测试 LLC 数据阵列，SRAM 制造测试另行设计。
- ROM 位于 `0x02000000`，S/C 预编译到 `cheshire_bootrom.sv`。ROM 汇编建立整数环境、sp/gp 和早期栈，调用 ROM C main；C 代码测频、读取 boot_mode、选驱动、装载载荷并交接入口。
- 自主介质 SPI NOR/SD/EEPROM 与 UART/JTAG/Link 等装载路径各有契约，需分别验收。设备驱动搬运字节到 LLC 数据/SPM；图中的绿色入口连线表示镜像机器指令与执行阶段的对应关系。
- 载荷 `sw/lib/crt0.S` 初始化自己的 sp/gp、mtvec、BSS、FP，再进入自己的 main；main 返回发布 scratch2 后 ret。应用 BSS 不是靠 LLC tag BIST 清零。
- 原图列明 Platform ROM 非零返回路径待 S01-B01 修复。重绘没有关闭该缺口；根 SDK/ROM 的其他已登记问题仍按工程交接处理。
- 原依据：`hw/cheshire_soc.sv`、`hw/bootrom/`、`sw/lib/crt0.S`、`axi_llc_hit_miss/tag_store/tag_pattern_gen`。无新增目标仿真或板测证据。

## 5. program_execution_flow

- 保留 SPI NOR 自主启动示例：boot_mode=2、PlatformRom=0、根 SDK CRT0；原快照 HEAD `278434024` / 2026-10-08。
- ROM `_start` → 早期环境/LLC 初始化 → ROM C main → SPI 初始化与 `gpt_boot_part_else_raw` → 镜像写入 SPM `code_buf` → `boot_next_stage` 的 `jalr ra, 0(t0)` → 载荷 `_start`。
- 载荷 CRT0 保存来时 ra、建立自己的运行环境，call 自己的 main。main 不返回时继续应用逻辑；正常返回时 `_exit` 写 `scratch2 = (返回值 << 1) | 1`，恢复 sp/gp/ra，再 ret。
- 保留原源码推导的返回缺口：`boot_next_stage` 的 jalr 后是 ret、未保存上一层 ra，可形成 ret 自循环，并非按设计进入 ROM `_exit`。这不是本轮新做的动态复现，也没有修复源码。
- 外部仿真/调试器可以观察 scratch2，TB 可以结束仿真进程；完成通知、CPU 自动停机、复位、断电、权限切换是不同事件。
- JTAG 直接设 PC、UART invoke、OS 程序退出不等于本调用链。原依据：Boot ROM S/C、gpt.c、crt0.S、rom.ld。

## 6. cheshire_software_hardware

- 沿用原图的裸机职责分层（原 HEAD `278434024` / 2026-10-09）。应用按需直接调用相关接口；这些区域不表示每次指令执行都必须穿过所有软件层。
- printf→UART DIF、GPT 经 read 回调访问介质、存储 HAL→SPI/I²C/GPIO DIF、UART debug HAL→UART DIF 是代表性调用。MMIO 工具按基址、偏移和访问位宽访问寄存器，regs 头文件提供偏移/位字段。
- LLC、AXI RT 等还有专用库；`libcheshire.a` 是代码归档组织方式，跨多个职责，不单独等同一个抽象层。
- 构建支持在开发主机生成 ELF/布局；Boot ROM/crt0 建立运行环境，异常处理与必要配置也可在运行期使用。启动交接不等于普通函数调用，启动支持不是每次设备调用的必经层。
- 指令执行、CSR/特权、内存/MMIO、异常/中断是不同的软件可见契约。CVA6 与 Ara 的专用请求/响应接口和主 AXI 数据访问分开。
- SPM 复用 LLC 数据阵列。片外 DDR 经控制器/PHY，Flash/SD/EEPROM 经 SPI/I²C，规划图像传感器经 LVDS。NPU/ISP 接入与 DDR 旁路仍待实现；图中虚线只是规划路径，不冻结新 IP 实现。
- RTOS/Linux 分别建立其任务/内核/驱动路径，不假定直接复用整套裸机 HAL。FPGA 为现有 VCU118 工程，ASIC 宏/时钟/PAD 等仍需适配；已有结构不表示全部功能已仿真或板测。

## 7. ddr_interconnect

- 保留 2026-10-10 候选结构：CVA6→主 AXI→原子适配→LLC/SPM→S0；Ara 单一出口在失效过滤之后新增地址分流，普通地址经原位宽适配进入主 64-bit AXI，GB 地址走宽侧局部分支。
- GB 是新增独立片上分 bank SRAM，不等于 LLC/SPM。NPU 计算与 DDR 搬运分开，NPU/GB 搬运器也是 GB 访问者；局部适配协调 Ara、NPU、ISP 与搬运器，处理 bank 冲突。
- GB 的 ISP 工作区、NPU–Ara 活跃区、搬运双缓冲仅为分区示意；容量/bank/位宽/频率待定，并行能力依赖真实 SRAM 带宽与分区。
- LVDS→CDC/FIFO→ISP→帧边界选择→帧 DMA；RAW 可绕过 ISP，ISP 可与 GB 交换中间数据。帧写入器负责地址、stride、像素打包并产生 AXI 写事务；本方案 RAW/ISP 暂不同时录制。
- **三口成立条件：S1 由 NPU 与 GB 共用统一搬运出口，S2 接帧写入。若保留独立 NPU master 和 GB DMA，需评估 S3，不能以绘图方式强行串行化。** 原 DDR IP 摘要允许最多 8 个 AXI slave；并未冻结最终使用数。
- 端口合流是控制器内部共享仲裁的逻辑示意，不是把独立 AXI 通道电气短接。多口共享同一 DDR 带宽。
- 控制寄存器/中断、缓存维护、完整 CDC 和 AXI 返回通道没有逐项展开；GB 不自动一致。图中新增分流、局部访问适配与旁路未因此实现。

## 8. llc_cache_spm

- 保留 DefaultCfg 8 way × 256 行/way × 8 个 64-bit 块/行 = 128 KiB；每 way 16 KiB，每缓存行 64 B。地址划分：Tag [47:14]、Set [13:6]、Block [5:3]、Byte [2:0]。
- Cache 按 Set 选组、各 way 并行比 Tag/Valid；示例命中组42的Way6，Way 不是 Cache 地址字段。未命中在 Cache way 内替换/回填，Dirty 决定回写。图是逻辑行对应，Tag SRAM 与 Data SRAM 是不同阵列。
- CFG_SPM 位图 1=SPM、0=Cache：0x00 全 Cache；0x0F 为 64 KiB SPM + 64 KiB Cache；0xFF 全 SPM 时 DDR 访问走旁路，SPM 仍在阵列内。
- SPM 固定槽 `base + way × 0x4000`；Way2 范围 `0x10008000–0x1000BFFF`，`0x10008AAB` 对应 Way2 / 组42 / 块5 / 字节3。直接寻址、不比 Tag；未设为 SPM 的 way 槽访问报错，用途改变不压缩地址槽。
- 转换前停止相关访问、迁移代码/栈/保留数据并协调缓冲/在途事务；写 CFG_SPM、COMMIT，由配置 FSM 协调请求和必要 flush/Dirty 回写，再按寄存器契约确认完成。
- SPM→Cache 前保存要保留的内容；转换不复制到另一块 RAM，原内容失去固定驻留保证。SPM 绕过 LLC Tag 管理，不保证 CPU L1 一定不缓存；`0x14000000` 别名映射同一 SPM 阵列。
- 原依据：cheshire_pkg/soc、axi_llc_burst_cutter/hit_miss/config、Boot ROM；HEAD `278434024` / 2026-10-10。无新增目标运行证据。

## 9. soc_full_architecture

本图沿用用户已选定的 [工业版布局](../backup_no_use/2026-10-12_soc_landscape/soc_reference_style.svg)，用其冻结脚本副本 `soc_layout.py` 重新导出，不重新发明用户已确认的分区。与旧完整图对应：7 个 AXI 发起端及扩展、5 类目标及扩展、18 个 Regbus 目标及 error/RegExt、C1–C9、GB/NPU/LVDS/ISP/帧写入、DDR 三端口都保留。

详见 [原工业版说明](../backup_no_use/2026-10-12_soc_landscape/README.md)。特别保留 iDMA 控制 slave→wrapper 内 AXI→Reg，与 iDMA 数据 master 分离；新 IP 的 RegExt 配置端是候选。原完整图的 NPU 搬运 256 bit 是需求候选，不是供应商接口冻结值；图内简写为统一 AXI 主口，条件仍保留在此。地址、GB 参数、lane/VLEN、DDR 实际位宽/频率、时钟域、IRQ 均未因重绘冻结。
