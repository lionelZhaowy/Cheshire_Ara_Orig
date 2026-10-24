# 自定义 IP 与 Linux 修改导航

生成源、扩展接口和跨层契约

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/integration.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../integration.html) · [阅读路线](index.md)

- [寄存器、地址和生成文件同步](#register-change)
- [完成、错误和裸机 API](#driver-irq)
- [NPU、Global Buffer 与图像收发的连接](#accelerators)
- [v1 C1–C16 的软件可见职责](#c1-c9)
- [DDR 初始化与平台启动](#ddr)
- [裸机与 Linux 的接口对照](#linux)

本章是修改导航和设计建议，不是本轮RTL实施记录。优先复用本地官方[SoC集成文档](../../../../docs/tg/integr.md)、[架构文档](../../../../docs/um/arch.md)与现有扩展端口；新增IP内部协议、缓冲所有权和DDR旁路属于产品需求带来的定制部分。

<a id="register-change"></a>

## 寄存器、地址和生成文件同步

新增寄存器应先定义软件承诺：合法访问宽度、reset值、RW/RO/W1C语义、提交时刻、忙时行为、错误、清除与并发优先级，再写HJSON和功能RTL。下面路径均是当前可参考的源头，新IP文件名/地址尚未分配。

| 修改 | 改哪些源 → 同步哪些输出 | 最小验证与失败处理 |
| --- | --- | --- |
| 增/改字段 | 现有 `hw/regs/cheshire_regs.hjson` 或新IP自己的HJSON → reg\_pkg/reg\_top + C宏 → wrapper中的reg2hw/hw2reg消费者 | 生成差异审查、reset/readback、每byte strobe、RO/W1C/忙时提交；非法写返回定义错误，不默默启动 |
| 扩展Reg窗口 | 固定配置中 `RegExtNumSlv/NumRules/RegionStart/End/Idx` → `gen_axi_out()`把新增范围指向Reg出口，`gen_reg_out()`分配外部目标 → 顶层RegExt连接 | 首尾地址、end越界、重叠和洞测试；同域访问/背压；异域另加经验证CDC |
| 扩展AXI存储目标 | `AxiExtNumSlv/NumRules/Region*` → `gen_axi_out` → `axi_ext_slv_req_o/rsp_i` | 每个master的可达性、ID和响应、非法地址；SRAM模型先验读写再接宏 |
| 同步软件地址 | `sw/link/common.ldh`、`sw/include/params.h`、驱动base；必要时DTS `reg/ranges` | 从同一配置导出或自动对比基址/size，链接map与实际译码一致 |
| 改缓存/执行属性 | `gen_cva6_cfg`区域定义、页表/权限、cache策略、DMA契约 | 不能只改窗口不改属性；分别验证普通数据、MMIO、取指和别名 |

下面是现有**生成方式**，示例输出指向新临时目录；本轮未覆盖生产生成文件：

```
REGTOOL_PATH=.bender/git/checkouts/register_interface-902ad5bfde7bb98c/vendor/lowrisc_opentitan/util/regtool.py
REG_OUT=$(mktemp -d /tmp/cheshire-reg-review.XXXXXX)
python3 "$REGTOOL_PATH" -r hw/regs/cheshire_regs.hjson --outdir "$REG_OUT"
python3 "$REGTOOL_PATH" --cdefines hw/regs/cheshire_regs.hjson > "$REG_OUT/cheshire.h"
```

此命令需当前regtool的Python依赖可用；实际规则见 [cheshire.mk](../../../../cheshire.mk)/[sw.mk](../../../../sw/sw.mk)。单改生成头或生成RTL会在下一次生成时丢失。IRQ Router、CLIC、PLIC和各IP有自己的生成参数/模板，不能用一个SoC HJSON代替全部设备的源。

官方建议从DefaultCfg派生配置并复用外部端口；本项目已确认迁移方向仍是独立 `cheshire_ara_asic/`固定配置/静态清单，不因官方示例使用Bender而改回长期Bender管理。新wrapper/寄存器package须按编译先后加入将来的静态清单；旧FPGA脚本保持保护边界。

<a id="driver-irq"></a>

## 完成、错误和裸机 API

新增完成IRQ与错误IRQ先定义源端锁存状态，再决定共用一根线加原因位还是两根源。沿现有 `intr_ext_i` 和 `NumExtInIntrs/NumExtPlicIntrs/NumExtClicIntrs`检查可用源、同步和目标截断；内部新增源涉及 `cheshire_int_intr_t`时还会改变packed编号，需同步DIF常量、PLIC生成配置和DTS，不能只在top多拉一根线。

裸机API可以仿照现有DIF接受base句柄，但应为新引擎明确定义 `configure → submit → poll/wait → get_result → acknowledge → recover` 的职责。名称是建议，仓库尚无这些NPU函数。配置成功表示参数被接受，任务成功还要检查ID/错误/传输排空，API不能只返回一个DONE布尔值。

最小验收依次用软件INTR\_TEST或模块激励注入完成与错误，确认源pending、控制器claim/complete、ISR计数和返回主循环；再加入忙时重提、完成/清除同拍、IRQ屏蔽期间事件保持、超时和复位后的旧令牌。失败时先停新提交并保存错误信息；是否可取消、如何排空及何时允许重用缓冲必须由IP协议保证。

<a id="accelerators"></a>

## NPU、Global Buffer 与图像收发的连接

| 需求与未决输入 | 可复用机制与建议新增部分 | 跨层契约、最小验证及恢复 |
| --- | --- | --- |
| NPU/GB搬运器的控制+AXI master | RegExt承接控制；v1的GB搬运器DDR主口经F1接共享压缩前端，绕过LLC | 当前需求NPU DDR数据绕过LLC，不能为方便而接回会污染LLC的主存路径；定义设备地址/位宽/ID/在途、错误状态/IRQ、fence/缓存与所有权。先存储模型小块读写和R/B错误注入；超时隔离缓冲/排空 |
| CPU或Ara访问GB | GB独立SRAM；CPU/Ara2独立进入主Xbar64，经共享M5目标接GB适配/仲裁 | CPU直访已确认；GB不经过LLC，非缓存/权限需实际配置。验证双master同地址/不同bank冲突、byte写、边界与权限，失败不交付半写结果 |
| LVDS接收 | 控制端参考RegExt；数据经过接收、对齐、解包、跨域、FIFO | 输入规格、lane映射/速率/训练/帧格式由传感器与IP方提供。记录锁定/失锁、FIFO溢出、帧ID；先器件模型/回环，失锁丢帧/重同步策略待确认 |
| ISP与帧写入DMA | ISP配置、流通道背压；独立AXI帧写master经F2→DDR.S2 | 定义stride单位、像素打包、裁剪/色彩格式、有效长度、帧末与错误；DONE应对应定义的写排空点。验证短帧/坏帧/背压/地址越界；不把坏帧标成可消费 |
| NPU计算与Ara后处理 | 复用CPU任务调度与Ara指令入口，新增张量/任务描述和GB所有权 | layout/精度/量化、tile范围、epoch和顺序；验证小张量golden及守卫。IRQ只通知，结果交接仍需可见性保证 |

eMMC参数在DDR就绪后先加载到DDR，运行时再由F1搬入GB；Host DMA走主Xbar/M2/LLC/F0，不直接等同于GB搬运器。GB本地非缓存访问主要管理使用权和写入完成，不套用DDR往返维护。

GB容量、bank数、端口、字节写/ECC、时钟、仲裁公平性均待定。M5的64-bit与设备256-bit接口标称位宽不能直接相加成SRAM带宽；CPU/Ara/搬运器是否访问同一bank需要仲裁预算。DDR与GB显式搬运是用户需求，GB不是DDR别名，也不是自动一致缓存。

<a id="c1-c9"></a>

## v1 C1–C16 的软件可见职责

沿用原锚点以保留链接；标号按[v1 总纲](../../../engineering/SoC_Architecture_v1_Master_Plan.md#65-c1c16-配置组与软件交付)。C编号是图中的配置组，不是寄存器地址或独立slave数量；范围维护服务的控制归属仍待设计，本页不增编号。以下仅为接口职责，硬件与驱动待实现。

| 配置组 | 功能 | 软件需要观察/配置 |
| --- | --- | --- |
| C1 | PLL/时钟复位 | 安全频点、lock、切换/复位状态 |
| C2 | DDR Controller | 初始化、ready、四口配置及错误 |
| C3 | DDR PHY | 训练、校准、状态与失败 |
| C4 | LVDS RX | 接收格式、对齐、启停及错误 |
| C5 | LVDS TX | 发送格式、FIFO欠载、发送完成 |
| C6 | 帧写入 DMA | 帧地址/stride、写及元数据发布完成 |
| C7 | 帧输出 DMA | 二维读取、源帧范围、读完与错误 |
| C8 | ROI 任务/调度 | 最多256个矩形、顺序、帧身份与提交 |
| C9 | ISP | 参数位置/版本、帧边界生效及状态 |
| C10 | NPU 计算 | 操作数/结果GB位置、计算完成及错误 |
| C11 | GB 搬运 | DDR/GB地址、长度/stride、传输完成及排空 |
| C12 | GB 管理 | 容量/bank能力、就绪、分块使用及错误 |
| C13 | eMMC Host/DMA | Host命令、DDR加载、完成及错误 |
| C14 | 压缩公共控制 | 区域/元数据、初始化、排空与公共错误 |
| C15 | 共享压缩器 | 模式、能力、状态与统计 |
| C16 | 共享解压器 | 模式、能力、状态与统计 |

ROI读取经F3→共享前端→DDR.S3，R返回像素后进入FIFO/LVDS TX；不增加写能力。软件分别检查源帧生产完成、DMA读完和TX发完，源帧等待全部相关读取结束再复用。CPU改帧后需要输入同步；设备写帧后需跨口可见，CPU后续读取才执行所需失效。详见[DDR–GB同步设计](../../../engineering/DDR_GB_Coherence_Design.md)。

<a id="ddr"></a>

## DDR 初始化与平台启动

2026-10-20 按v1同步：F0（LLC）、F1（GB搬运）、F2（帧写）、F3（ROI帧读）经共享压缩前端接一个Controller的DDR.S0–S3；四口共享物理带宽。压缩区成功需包含数据和元数据发布，普通区域原样旁路；Controller本身的保证由供应商确认，项目另外验证前端/CDC/通知。供应商手册最多8口的能力不等于四口实例已交付。见[当前契约](../../../engineering/IP_DDR_Interface_Contract.md)。

可复用官方Platform ROM钩子，修复并验收S01-B01后，在片内可执行环境中按供应商流程配置安全时钟、复位、Controller/PHY、训练，再经定义的就绪检查开放DDR。具体先后依赖供应商时序，不能一概规定先Controller或先PHY。DDR不可用前，代码/栈/训练参数必须放在独立可用的片内资源；失败保留片内诊断/被动加载恢复入口，不搬应用到坏DDR。

供应商至少需提供版本manifest、AXI端口数/宽度/ID/在途和支持子集、地址语义、时钟复位/CDC边界、初始化寄存器与训练执行者、ready/error条件、模型/约束及授权范围。验收先做可控模型中的寄存器/复位/超时，再做首尾地址、byte mask、burst、并发和错误注入，最后真实训练/压力。不能以FPGA MIG HelloWorld代替这些验收。

运行中调频要阻止新提交、排空相关master、按IP约定进入安全状态/自刷新、切换并确认稳定、更新软件时基后恢复；具体机制尚未实现。保留运行软件可重复配置接口是用户已确认方向，不授权现在改PLL/DDR或升级依赖。

<a id="linux"></a>

## 裸机与 Linux 的接口对照

| 项目 | 当前裸机路径 | Linux通用机制及本项目缺口 |
| --- | --- | --- |
| 寄存器访问 | reg8/reg32、DIF直接操作平台地址 | 驱动从资源取得映射，使用readl/writel等IO访问器；用户态经系统调用，不能直接照搬裸机指针 |
| 地址描述 | common.ldh、params.h与RTL配置手工同步 | DTS的reg/ranges/interrupts和binding；驱动映射不改变RTL译码 |
| DMA缓冲 | 独占物理区/已验证别名，调用方承担同步 | 使用dma\_alloc\_coherent或dma\_map/sync/unmap，设备使用dma\_addr\_t；平台cache维护和地址转换必须真正支持 |
| 中断 | mtvec包装+应用trap\_vector+PLIC DIF | 驱动注册IRQ，内核irqchip层负责控制器流程，设备驱动处理源状态；不能在普通设备ISR再自己重复claim/complete |
| 完成/错误 | 轮询ID或自定义ISR，需补超时/恢复 | completion/wait queue等机制，返回错误并保留生命周期；睡眠操作不能随意放硬中断上下文 |
| 启动/初始化 | Boot ROM/Platform ROM/应用驱动 | 固件准备启动关键资源，Linux按设备依赖probe并管理资源；不能在probe之前就依赖尚未工作的DDR承载内核 |

Linux部分依据当前仓库存在的Linux6.5方向与官方[DMA API](https://docs.kernel.org/6.5/core-api/dma-api-howto.html)、[设备I/O访问](https://docs.kernel.org/6.5/driver-api/device-io.html)。DMA地址不同于CPU指针，coherent分配也不取消必要的排序；平台没有实现正确cache维护时，调用API名称不会自动补齐硬件/内核缺口。

当前 [sw/boot/cheshire.dtsi](../../../../sw/boot/cheshire.dtsi)及板级DTS是历史平台描述，**不能直接复制成VCU118或新ASIC定版**：ISA字符串`rv64imafdc`不声明V，PLIC ndev=51而本地生成NumSrc=58（还包括保留源0），`axi_llc@3001000`长度0x5000超过当前4KiB窗口，`memory-controller@3006000`标成ddr-link但当前该地址为Serial Link配置窗口。UART节点用reg-shift=2、reg-io-width=4，裸机UART使用reg8；必须各自核对硬件支持和桥副作用。这里只指出静态差异，不擅自改DTS或推断旧镜像必然失败。

新IP Linux资源至少列出compatible与binding、reg/reg-names、interrupt-parent/interrupts、clocks/clock-names、resets/reset-names、DMA mask/地址翻译；reserved-memory/memory-region、dma-ranges或IOMMU只有实际设计需要且硬件/内核支持才添加。**不要在DTS随意加dma-coherent来掩盖不一致硬件。** 新的clock/reset provider、IRQ描述和缓存维护是跨S01/M01/P01的实施工作，当前不存在已验收的新IP驱动。

---

[上一页：五条软件到 RTL 案例](cases.md) · [下一页：最小实践与验证记录](labs.md)
