# Regbus 全路径与自有 IP 接入

2026-10-12，L01；输入提交 `c4162204cfee0c48b81158b4296860a678d92bec`。

本轮按用户新反馈，将接入所需知识集中到两张图。旧 A 区四张细节图保留作内部调试参考，不再作为接入 IP 的必读内容。未改 RTL、配置、地址图或 skill。

| 图 | 作用 | 预览 | 母版 | PDF |
| --- | --- | --- | --- | --- |
| ① Regbus 全路径 | 现有桥、两级选路、片内/错误/外部端口与新增边界 | [PNG](export/01_regbus_whole.png) | [SVG](01_regbus_whole.svg) | [PDF](export/01_regbus_whole.pdf) |
| ② IP 寄存器封装 | 地址译码、字节写入、读回、命令与状态职责 | [PNG](export/02_ip_register_contract.png) | [SVG](02_ip_register_contract.svg) | [PDF](export/02_ip_register_contract.pdf) |

[两页原生可编辑 PPTX](export/diagrams.pptx)。采用 publication-figures 后端；屏幕教学宽度 280 mm。第二图是建议接口结构，不是已有 NPU/ISP RTL。

图①边框限定的是 Cheshire 内部互连与寄存器目标，不是整个 SoC 边界；CVA6 CPU 本身也在 cheshire_soc 内，画在左侧是为了表示访问来源。蓝色双向线合并请求/响应两束信号，不表示 Regbus 可同时独立执行读写。数据/地址宽度按默认 AXI64、Reg32、地址48展开；其他配置须按类型核实。外部接口由现有 RTL 支持，但默认有效端口数为0；自有 IP 用虚线标为拟新增。reg_cdc 是异域接入时的可用适配器，不是现有公共路径中自动插入的单元。

## 1. 接入时需要理解的全路径

```text
CPU 的 MMIO load/store
  → 主 AXI Crossbar：决定进入 Regbus 窗口
  → 原子适配 / AXI cut / AXI-to-Reg 桥：使用现有实现
  → Regbus 地址解码 / demux：决定访问哪个寄存器目标
  → 外部 Regbus 端口 k
  → 自有 IP 寄存器封装
```

响应沿相反方向返回。桥对外提供单个 32-bit Regbus 请求/响应接口。两级地址路由由同一组外部 Reg 配置生成，不需要为每个 IP 重新实现桥。

本地官方文档明确把外部 Regbus subordinate 端口作为集成机制，并说明 Regbus 固定32-bit、不支持 AXI 式 burst/并行读写：[架构文档](../../../docs/um/arch.md) Interconnect；[集成文档](../../../docs/tg/integr.md) Instantiating Cheshire。这里采用官方提供的接口，自有寄存器布局、任务提交方式及 CDC 选择属于产品设计。

## 2. 实施工作集中在四处

### 2.1 当前平台配置中的 RegExt 参数

配置字段位于 [cheshire_pkg.sv](../../../hw/cheshire_pkg.sv) 118–122 行：

| 字段 | 含义 |
| --- | --- |
| RegExtNumSlv | 外部 Regbus 目标端口数 |
| RegExtNumRules | 地址规则数量，未必等于端口数 |
| RegExtRegionStart[j] | 第 j 条规则起始地址 |
| RegExtRegionEnd[j] | 结束地址，不包含这个地址 |
| RegExtRegionIdx[j] | 第 j 条规则映射到的外部端口编号 k |

在当前平台配置的派生函数中修改这些字段，保留已有 Ara、DDR、FPGA 等配置，不为扩展而盲目恢复 DefaultCfg。下面仅是“原来没有外部端口、增加一个 IP”的字段示意，不是已分配地址或可直接编译的完整配置：

```systemverilog
cfg.RegExtNumSlv         = 1;
cfg.RegExtNumRules       = 1;
cfg.RegExtRegionIdx[0]   = 0;
cfg.RegExtRegionStart[0] = IpBase;
cfg.RegExtRegionEnd[0]   = IpBase + IpWindowBytes;
```

规则需要满足 start < end、索引小于端口数、窗口不与已有规则冲突。采用 `[start,end)`；不是 end=start+size-1。

`gen_axi_out()` 381–384 行把外部 Reg 地址规则导向主 AXI 的 Regbus 出口；`gen_reg_out()` 438–444 行把同一窗口导向 `ext_base + k`。通常不需要手工修改两个函数，也不需要为它另开 `AxiExtNumSlv`。

地址能路由，不等于 CPU 属性正确。`gen_cva6_cfg()` 505–514 行生成非幂等、缓存及执行范围；新增窗口要核对为设备 MMIO。不要将控制寄存器放入普通可缓存/可投机读取区域后，只靠 volatile 解决。本文没有冻结任何新 IP 基址。

### 2.2 外层顶层实例和连线

现有连接见 [cheshire_soc.sv](../../../hw/cheshire_soc.sv) 431–436 行：

```systemverilog
assign reg_ext_slv_req_o = reg_out_req[RegOut.num_out-1:RegOut.ext_base];
assign reg_out_rsp[RegOut.num_out-1:RegOut.ext_base] = reg_ext_slv_rsp_i;
```

端口 k 的请求接到自有 IP 的 Regbus 从接口，请求对应的响应接回 k。当前 [FPGA 顶层](../../../target/xilinx/src/cheshire_top_xilinx.sv) 537–538 行仍将请求输出悬空、响应输入接零；[仿真 fixture](../../../target/sim/src/fixture_cheshire_soc.sv) 89–90 行也未使用。仅增加配置条目而不接线，会留下无法完成的访问。

外部类型应通过 `CHESHIRE_TYPEDEF_ALL` 或 `CHESHIRE_TYPEDEF_REG` 与当前 Cfg 保持一致；Reg 请求结构体宽度不能照搬64-bit AXI 数据类型。官方推荐在外层系统包派生配置和接口类型，见 docs/tg/integr.md；本轮未修改原有运行工程。

### 2.3 IP 寄存器封装

结构体定义依据 [register_interface/typedef.svh](../../../.bender/git/checkouts/register_interface-902ad5bfde7bb98c/include/register_interface/typedef.svh)，Cheshire固定Reg32的宏见 [cheshire/typedef.svh](../../../hw/include/cheshire/typedef.svh) 33–34 行。

| 信号 | 对 IP 的方向 | 使用约定 |
| --- | --- | --- |
| addr | 输入 | 完整系统地址；demux 不自动减基址 |
| write | 输入 | 1写、0读 |
| wdata[31:0] | 输入 | 32-bit 写数据 |
| wstrb[3:0] | 输入 | 逐字节写入使能，必须正确处理 |
| valid | 输入 | 当前请求有效 |
| rdata[31:0] | 输出 | 完成读访问时返回的数据 |
| error | 输出 | 完成访问时返回的错误状态 |
| ready | 输出 | 本次寄存器访问可完成 |

`valid && ready` 在时钟沿成立才产生一次访问。图② `wr_en=fire&&write` 是总写事件；每个寄存器实际写使能还必须经过地址命中、权限和字节掩码检查。非法写不能改状态。等待期间请求可能保持多拍，不能每拍重复启动 IP。

图②的 `offset=addr-BASE` 是建议封装方式，不表示现有 demux 已完成地址转换。对严格对齐且完整译码的窗口，可以按设计取低位；必须避免意外别名。

对简单组合读、时钟沿写的寄存器，可以像现有 `cheshire_reg_top.sv` 一样保持 ready=1；只有能在该沿真正完成访问时才这样做。不存在的寄存器应当结束访问并返回明确错误，避免永久拉低 ready。无请求时不要凭借 ready 产生副作用。

启动长任务建议使用参数寄存器 + START 门铃 + BUSY/DONE/ERROR。写 START 被接受后，立即完成这笔配置访问；等任务完成再置状态或中断，不把一次 Regbus 访问拖成整个推理/帧周期。配置寄存器宜使用 shadow/提交语义：软件可以先写宽地址的高低32位及其他参数，再由 START 一次锁存供硬件使用，避免撕裂配置。具体布局仍待 IP 规格。

优先参考本工程已有生成式寄存器路径：[hw/regs/cheshire_regs.hjson](../../../hw/regs/cheshire_regs.hjson)、[cheshire_reg_top.sv](../../../hw/regs/cheshire_reg_top.sv)、[依赖官方说明](../../../.bender/git/checkouts/register_interface-902ad5bfde7bb98c/README.md)。该依赖带本地适配过的 reggen，可生成 Regbus 寄存器接口；少量寄存器也可以手写。本轮没有运行生成器或建议重拉依赖/Bender迁移。

### 2.4 软件定义与功能检查

硬件寄存器表和软件头文件至少一致规定：基址、偏移、32-bit访问宽度、复位值、RO/RW/W1C、busy 时写入行为、启动条件和错误清除。首版用对齐32-bit MMIO访问，不使用普通64-bit结构体赋值、memcpy或原子指令访问设备寄存器。

若使用中断，需要另接 `intr_ext_i`、配置源数量/路由并定义清除机制；Regbus 本身不传中断。DMA 的物理地址和数据可见性、缓存维护属于数据通路契约，Regbus 配置成功不能替代这些要求。

## 3. 时钟与必须注意的访问行为

- 公共桥使用 SoC clk_i；Regbus 协议本身不自动分频。慢操作可以用 ready 等待，但这不改变时钟。
- 寄存器封装同域时直接接。如果整个寄存器从接口在异步时钟域，现有 [reg_cdc.sv](../../../.bender/git/checkouts/register_interface-902ad5bfde7bb98c/src/reg_cdc.sv) 274行起可适配完整事务；如果寄存器保留SoC域、IP核异域，则配置提交和状态返回仍需自己的跨域握手/快照。二者是不同边界选择。
- 需明确双方复位及目标时钟可用性；不能期待用一个已停钟、不可访问的寄存器接口来启动它自己的配置时钟。PLL/复位等启动关键控制尤其要提前确定可访问域。
- 当前桥 `HideStrb=0`，mem_to_banks 将64-bit访问拆成两路，外层只过滤零字节使能的写。读不会被这个过滤器屏蔽。因此即使软件使用32-bit读，也不能假定相邻32-bit寄存器绝不会被内部访问。首版建议状态读取无副作用，用W1C确认事件；读即清零或读出队的寄存器需要先定向验证/适配。该行为来自前轮静态源码核对，尚无本轮动态测试。
- 对齐32-bit访问只是软件使用约定，不能单独解决上面的窄读副作用问题。不要用“用户不必研究桥内部”掩盖这个接口层可见约束。

## 4. 哪些内部细节可以暂时不研究

| 对象 | 接入普通配置口时的处理 |
| --- | --- |
| AXI AR/AW/W 仲裁、burst展开、AXI ID恢复 | 使用现有桥，保留参数；只有出现协议问题再深入 |
| stream_fork、meta/sel FIFO、stream_to_mem计数器 | 不修改；理解对外握手和阻塞行为即可 |
| mem_to_banks内部请求/响应FIFO | 不修改；保留对窄访问/副作用的边界验证 |
| 原子适配器与AXI cut内部实现 | 保留现有配置；不据此允许软件对自有MMIO使用AMO |
| DDR/GB搬运调度 | 不属于寄存器接入本身，另走数据接口及M01契约 |

对 NPU、ISP、NPU 搬运器、图像帧 DMA，可以使用同一种 Regbus 配置接口，而数据接口按带宽和拓扑分别设计。这是新 IP 接入建议；当前 Cheshire iDMA 有自己的控制入口及已记录问题，不因本图而改成接公共 Regbus。

后续真正实施时，最小验证集是：窗口首尾/空洞和端口映射，复位值，普通读写与逐字节写，等待时不重复副作用，START只触发一次，运行中仍能读状态，中断清除；另对32-bit窄读、相邻寄存器和非法偏移做实际桥接测试。异步配置再增加CDC与复位测试。本轮未实施这些测试。

## 5. 图稿制作与证据

`build_figures.py` 复用前一图目录的基本 SVG 绘图函数，但不调用其四图生成入口、不修改旧文件。导出使用 publication-figures `scripts/run.py --width-mm 280 --min-font-pt 9 --render --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`；新导出应指定空目录。

见 [导出报告](export/export_report.json) 与 [检查报告](validation.json)。两张最终预览已查看；PPT文字/原生对象保存重读，PDF字体嵌入及无整图位图检查。Office未实测；图②不是已完成或已验证的IP设计。未运行RTL仿真、综合、板测，未修改共享项目状态或任务表。
