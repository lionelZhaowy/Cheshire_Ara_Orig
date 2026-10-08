# L01 外设教材优化：审查、改动与验收

日期：2026-10-08。输入 `mp/ara-pulp-v2` / `459f9d6f5748e39063f7bb67e959c2f27859915d`。本文件在修改正文前建立；实施结果及检查在收尾追加。原有 `learning/figures/20261007/editable/diagrams.pptx` 修改归用户，保护不动。

用户补充授权外设正文重组与补写；此前全书审查及 03–08 评估继续交付，非外设主章节不实施改写。只改文档及其生成页面，不改生产 RTL/sw/依赖/配置/地址图，不新增驱动或目标运行。未启动子 Agent。

## 修改前逐章问题与实施清单

以下正文均已完整审读；相关源码为定向核对，非全仓库审计。

| 章节/模块 | 最小教学任务 | 修改前问题 | 本轮动作与保留内容 |
| --- | --- | --- | --- |
| 18 UART | 输出 `ready` 并确认最后字符离开移位器 | 从 MMIO 属性立即跳到实例；连接、支持层次及重复初始化不足 | 先讲终端/帧/连接，再解释现有 reg8、DLAB 和 flush；保留正确初始化顺序、GPIO 掩码例 |
| 18 GPIO | 解释 GPIO3 输出及 GPIO0 软件注入事件 | 输出示例与引脚输入限制脱节 | 补 SoC in/out/oe、fixture 绑零及板级未接；完整解释掩码、方向、输入与清源 |
| 19 CLINT/PLIC/Router/CLIC | 服务一次 GPIO0 事件和至少两次 timer | 两段 compare 更新顺序不同，PLIC 内容插入 timer；特殊控制器过早 | 合并 timer 解释；以事件闭环串起门控/claim/清源/complete；特殊控制器后置；保留整数现场边界 |
| 20 I2C/EEPROM | 读模型地址 0 的 16 字节 | FMT/ACQ/寄存器先于器件读操作，target 模式和 HAL 缺口打断 | 先用途、24FC1025 依据、两线连接和事务，再映射 HAL/DIF/寄存器；集中缺口；保留 STOP→START 本地差异 |
| 21 SPI/NOR/SD | CS1 读取模型 16 字节 | FIFO 数量/复位字段先于片选内事务，缺连续 API 例 | NOR 主线完整后再讲 SD；区分控制器基址、Flash 地址、RAM 地址；保留只读、不擦写 |
| 22 iDMA | 推演三行 16 字节搬运，识别为何当前不能运行 | 寄存器、2D、桥缺口、RT、BusErr 快速切换 | 先一次搬运与所有权；寄存器提交后集中阻塞；RT/错误独立进阶任务，保留 BLOCKED/rc16 |
| 23 Serial Link | 远端写读与被动装载交接 | 先 network/data_link 参数，缺端到端地址例和连接解释 | 补两端发送/接收时钟与数据、窗口映射、VIP 任务；未接板端明确 |
| 23 VGA | 从 RGB565 帧缓冲连续输出两帧 | 从 fetcher/credit 起步，缺显示接口用途及最小连线 | 先帧/行/像素，再配置与主动读，给待模型验收全过程；不编造显示器型号 |
| 23 USB OHCI | 解释一次控制传输及 TD 回收 | HCCA/ED/TD 未由具体任务引出；流程表替代解释 | 先 host/device/PHY 及连接，再以控制传输引出描述符；现无完整枚举栈，明确伪代码层次 |
| 10 Regbus、16 Debug | 公共访问契约与调试加载 | 已有握手/主机目标时间线较完整 | 不重写；外设入口给准确引用，避免把 DMI 当 MMIO |
| 实验/参考 | 能选择可构建、待运行、阻塞任务 | 分组链接与支持等级分散 | 补共同支持导航与任务前置，保留六实验及 429 行索引数据 |

## 事实依据与范围

官方先查 Cheshire Software Stack / SoC Integration；器件类别查 Microchip 24FC1025 与 Infineon S25FS512S 官方页/数据手册，再对照本地 HAL、DIF、SoC、fixture/VIP、FPGA wrapper。在线资料查阅日为 2026-10-08，不代替本地快照；完整订货型号及板载身份不由 HAL 名称推出。

本轮复核路径：`hw/cheshire_soc.sv` 外设 generate、`target/sim/src/{fixture_cheshire_soc,vip_cheshire_soc}.sv`、`target/xilinx/src/cheshire_top_xilinx.sv`、`sw/lib/dif/{uart,clint}.c`、`sw/lib/hal/{i2c_24fc1025,spi_s25fs512s}.c`、依赖中对应 DIF/寄存器/RTL、教材 `journey.c/storage_read.c/advanced.c`。原教学图能够表达任务关系，本轮复用并逐步解读，不修改图稿、PPTX、WaveDrom 或生成器。

修改前快照：[input.json](learning/evidence/peripheral-20261008/input.json)；逐章原文保存在同目录 `before-content/`。旧教材备份和旧证据原样保留。

## 最终修改前后与逐项验收

|范围|修改前→修改后|无需诊断即可回答的任务|执行等级/未解决输入|
|---|---|---|---|
|UART/GPIO|寄存器/复位开篇→终端文本/引脚任务→MMIO→初始化→flush/观察|TX/RX和流控方向、baud与系统clk；GPIO先数据后OE、掩码与DATA_IN|UART有用户历史HelloWorld；本例未目标运行。GPIO无板端回环，实际电平/PAD待板级资料|
|timer/PLIC|CLIC提前、compare写法分散→GPIO注入/定时计数闭环→扩展|源、PLIC领取、清源、complete、CSR门；RTC与系统clk|实验C已有源码，正常/遗漏触发的SoC结果待V01；CLIC/Router条件另查|
|I2C|FMT/ACQ和缺陷先行→EEPROM地址0的16字节读→寄存器/API→target扩展|器件控制字/内部地址/RAM/MMIO；开漏和ACK、CLK到400kHz计数、read返回后比对|VIP M24FC1025/0x9a；当前板未启用I2C。短未对齐/写/等待缺口未修复|
|SPI/NOR/SD|资源枚举→完整片选内0x13/地址/RX任务→SD支线|SCK/CS/数据方向、三个地址空间、初始化与共享host、READY/ACTIVE/WIP|VIP S25FS512S；VCU118有QSPI路由但实际芯片型号/电气待确认。SD缺模型/板宏；未写介质|
|DMA/RT/BusErr|搬运/缺陷/错误混合→三行正常搬运机制、阻塞短提示、错误详情独立|stride为行起点增量、NEXT读触发、DONE与数据正确分开|当前DMA不可提交，rc16保持；RT预算实验同受阻，S01/V01门槛未关闭|
|Link/VGA/USB|模块名→每项具体任务并连续解释|Link远端响应；VGA按帧取数/时序；USB描述符/TD结果|机制步骤例；板Link未接、VGA无输出模型、USB缺时钟/PHY模型/host栈。无虚构器件兼容列表|

以上是本轮逐段任务审读结果，不是目标运行验收，也没有真人受试者测试。外设正常正文保留配置、初始化、访问副作用、返回与完成条件；症状、恢复和已知缺陷集中到peripheral-debug。旧uart-recovery、i2c limits、dma lanes/errors等入口保留，可到新诊断目的地。中断、DMA、target/SD正常扩展仍在正文。

支持层不再混写：IP/驱动存在、模型连接、板级宏/引脚、已有构建、用户报告和本轮实测分别说明。两个有依据的器件系列是24FC1025和S25FS512S；没有将其补成板载完整订货型号。寄存器429项未改，USB没有生成索引组，明确链接实际RTL译码。

检查产物写入同一新证据目录，最终生成/浏览器命令和退出码见独立交接。未编译软件、未运行生产RTL/板测、未修复驱动或拓扑；所有未解决问题迁移保留。
