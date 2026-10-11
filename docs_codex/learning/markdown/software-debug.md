# 启动与软件故障诊断

装载、初始化与软件运行问题的阶段定位。

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/software-debug.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../software-debug.html) · [阅读路线](index.md)

- [软件构建、装载与运行的分层诊断](#locate-stage)
- [构建错误与告警](#build-errors)
- [JTAG 装载停顿与阶段完成条件](#load-stop)
  - [应用入口的栈有效性与对齐条件](#stack-handoff)
  - [本地 ELF/JTAG 段尾与补零责任](#loader-tail)
- [trap 停顿的原因记录与恢复条件](#trap-stop)
- [main 运行期间的 UART 无输出与乱码诊断](#no-output)
- [应用数据、日志与退出码的一致性检查](#wrong-result)
- [替代装载路径的协议与观察边界](#alternate-loaders)
- [Platform ROM 的正常返回缺口](#platform-rom-return)
- [介质启动的已有局限](#media-start)
- [已知软件问题的证据与验证状态](#known-issues)

**诊断入口**

正常构建、启动、调试与 trap 原理分别见[构建](build.md)、[启动](boot.md)、[调试](boot-debug.md)和[异常与上下文](traps.md)。本页集中已有证据支持的症状、局限和后续验证，不把“已记录”写成“已修复”。

<a id="locate-stage"></a>

## 软件构建、装载与运行的分层诊断

没有 UART 文本可能发生在构建、装载、应用启动或设备输出中的任何一层。先保存同一轮输入：完整 HEAD/本地差异、硬件配置或 bitstream 标识、ELF 哈希、工具/运行命令和日志，再寻找最后一个已完成的动作。沿“主机文件 → 目标段字节 → 恢复 PC → crt0/main → 库/DIF → MMIO → UART 引脚/接收”逐步缩小，避免只凭终端空白就改 UART 分频。

| 实际症状 | 最先要区分的事实 | 入口 |
| --- | --- | --- |
| 没有新 ELF / 链接失败 | 头文件声明、对象实现、链接顺序和脚本布局 | [构建错误](#build-errors) |
| 停在等待 LLC / halt / SBA | 目标是否执行 ROM、存储是否可写、调试传输是否响应 | [装载停顿](#load-stop) |
| 已 resume 但未进入 main | DPC/入口、sp、BSS 区与 FS/指令条件 | [入口与栈](#stack-handoff)、[trap](#trap-stop) |
| main 已进入但无输出或乱码 | 测频轮询、UART 状态/配置、引脚及接收端 | [输出路径](#no-output) |
| 输出了但结果/退出码不对 | 初值、数组数据、结束通知、日志所对应 ELF | [结果检查](#wrong-result) |
| 替代介质或平台钩子启动失败 | 是否满足该路径自己的镜像和控制流契约 | [Platform ROM](#platform-rom-return)、[介质启动](#media-start) |

<a id="build-errors"></a>

## 构建错误与告警

`undefined reference` 表示链接器未能满足某个符号引用。先看报错函数在哪个对象中调用、实现是否进入支持库、该库是否参与当前 ELF 的链接。头文件能让 C 编译通过，却不能提供 uart\_init 的机器码。涉及 LTO 时同时记录编译器、归档工具和插件版本；不要把一个旧 .a 的存在当作本轮生成成功。

地址重定位溢出时，把报错重定位、寻址选项和 map 中的目标地址一起看；重新链接到 DRAM 不会初始化 DDR。ELF 丢弃 .riscv.attributes 的本地规则也使“最后 ELF 无属性”不能单独判定 ISA，应核对象属性、命令和反汇编。原 MMIO 声明可能引发对象边界告警，原链接布局可能引发 RWX 段告警：记录来源和影响，不靠静默关告警验收，不在文档任务中修改生产实现。

<a id="load-stop"></a>

## JTAG 装载停顿与阶段完成条件

若日志停在 `Wait for LLC configuration`，看复位后 PC 是否沿 ROM 到 BIST/SPM 配置处，LLC 是否存在、BIST 是否完成以及配置位是否已写。若停在 halt，检查 JTAG/DTM/DMI 活性、DMCONTROL 和 DMSTATUS.allhalted；若停在写内存，检查 SBA 的 busy/error 与实际目标地址、写响应。DM 已响应不表示目标存储一定可访问，SPM 配置位也不表示所有 ROM 初始化已结束。

本地 jtag\_write 对部分命令和 SBA 操作检查 busy、cmderr、sberror/sbbusyerror；调查时保存第一次错误的地址、操作宽度和返回状态，避免重复写把线索覆盖。DMI 是调试寄存器编号，SBA 地址是系统物理地址；两者混用会使观察完全指向另一对象。SBDATA 的 read-on-data 可让读取触发下一次总线访问，自动刷新设备窗口须考虑该副作用。

<a id="stack-handoff"></a>

### 应用入口的栈有效性与对齐条件

`jtag_elf_halt_load` 在 LlcNotBypass 为真时只等 CFG\_SPM\_LOW.bit0，然后 halt；`cheshire_bootrom.S` 在配置写之后还会按 LLC\_SIZE 扩展 sp。当前 spm.ld 的 \_\_stack\_pointer$ 为 0，应用继承进入时栈。应把实际暂停 DPC、sp、所用链接符号与栈覆盖的可写范围记录在一起；不能依据配置位推断栈已位于 SPM 高端。

原应用 crt0 在进入 main 前保存 24 字节上下文，默认高端初始 sp 与这个动作共同影响调用边界的 16 字节对齐。应在实际 C 调用边界观察 sp，并检查栈与代码/数组区间不相交。无内部 LLC 时，默认链接值本身不会建立可写存储；平台须先提供替代栈，详见[正常平台责任](boot.md#platform-rom)。本轮不通过改 PC、改栈或改生产链接脚本掩盖这一契约。

**ROM 自己的 C 入口需单独检查：**当前源汇编在默认内部 SPM 路径设置 `sp=__base_spm+LLC_SIZE-8`，PlatformRom=0 时随后直接到 `_boot: call main`，中间没有应用 crt0 那样的 24 字节调整。默认 128 KiB 情形得到 `sp=0x1001fff8`，余数 `sp % 16 = 8`，未满足前述常规 ABI 的 16 字节对齐。这里确认的是源代码调用边界问题；本轮没有用目标波形复现异常或判断现有 ROM 编译结果是否受影响。非零 Platform ROM 钩子也继承该初始 sp，若用标准 ABI 的 C 实现同样需要核对；不能用应用 crt0 的对齐结果替 ROM 路径结案，应由启动任务结合实际 ROM 指令和 C 调用验证。

<a id="loader-tail"></a>

### 本地 ELF/JTAG 段尾与补零责任

当前 `elfloader.cpp::load_elf` 以 p\_paddr 作为地址，保存 p\_filesz 文件字节，并把 p\_memsz 作为段长度交给 VIP；p\_memsz 大于 p\_filesz 时会打印未补零提示。应用 .bss 仍由 crt0 清零。这个源文件叫 get\_section 的接口实际迭代 ELF PT\_LOAD 段，名称不能用来推断其按 section header 装载。

`vip_cheshire_soc.sv::jtag_elf_preload` 按 8 字节打包写入，循环条件为 `i <= sec_len`，并读取 bf\[i\]…bf\[i+7\]。段恰为 8 字节整倍数时仍会多进入一轮，非整倍数的末轮也缺逐字节边界限制，构成源码确认的越界风险。尚未动态复现或修复，不能将任意 ELF 安全装载作为既定能力。

后续独立 V01/S01 验证应覆盖 1/7/8/9 字节段、相邻段和守卫区，检查目标读回、BSS 初值与段外字节；保留工具版本、ELF 各长度及总线写轨迹。UART/Link 的分段循环另有逐字节边界判断，不应把 JTAG 的缺口无依据地推广到所有装载路径。

<a id="trap-stop"></a>

## trap 停顿的原因记录与恢复条件

当前 journey 未覆盖弱 trap\_vector，默认入口在 `j trap_vector` 自循环。已进入 main 或还在 crt0，都可能因不满足指令/地址条件转到这里。先保存 mepc、mcause、mtval、mstatus、入口附近反汇编与 sp；mtval 为 0 不代表“没有异常”，其内容受原因和实现配置影响。具体指令位置比“看起来卡死”更能区分问题。

若发生在 crt0 浮点初始化，检查所选 CPU F/D 能力及 FS；若发生在向量入口，按[Ara/RVV 诊断](vector-debug.md)核 profile、decoder、VS/FS 和指令本身。若为访问异常，先把有效地址、物理目标、权限与实际存储范围对上，不从一次错误就改全局缓存配置。

若 handler 返回后反复进入，要先区分设备原因没有清除、timer compare 仍已到期，还是同步异常被原样重试。清 PLIC complete 不能代替消除外设原因；对所有 mepc 加 4 也不是通用恢复方法。正常入口、整数保存和 mret 见[trap 章](traps.md)。现有包装不提供完整 FP/RVV 或嵌套上下文，涉及它们的运行需要对应 port/入口和专项验证。

<a id="no-output"></a>

## main 运行期间的 UART 无输出与乱码诊断

journey 在 UART 初始化前调用 clint\_get\_core\_freq。它等待 RTC tick 推进并测 mcycle，因此先检查 RTC\_FREQ 声明与实际 rtc\_i，以及 mtime 是否变化；RTC\_FREQ 非零不会创造一个输入时钟。随后查 uart\_init 的 freq/baud 单位及分频，再看 LINE\_STATUS、THR 写、TX 引脚和接收端。printf 符号存在与函数已执行是不同证据。

若卡在 uart\_write 或 uart\_write\_flush，记录轮询的状态位与当时控制器/引脚条件；这些 API 没有内建超时。乱码优先比较目标实际协议时钟、波特率、帧格式及接收端配置；不把控制器时钟直接当串行比特时钟。具体连线和寄存器诊断沿[UART 专项入口](peripheral-debug.md#uart)。本地 uart\_write\_flush 还保留访存顺序 TODO，它的存在不等于已证实或修复某个平台错误。

<a id="wrong-result"></a>

## 应用数据、日志与退出码的一致性检查

先核 INIT 行：seed 不为 1 指向装载初值或对象布局，result 初值不为零指向 crt0/BSS 或内存覆盖；随后核首个不匹配项、总和和 errors。保留真正使用的 ELF 与 map，避免看旧符号调试新文件。检查静态区不重叠，只覆盖链接器已知对象；运行栈和约定地址的共享缓冲区还需单独排除冲突。

本例正常是 137 项均等于 3\*i+1，总和 28085，errors=0，SCRATCH2 编码返回 0。JTAG 的 Preload complete、Resumed 和 SUCCESS 是三种不同阶段；只有最后一项也不能证明当前程序执行了你所期待的算法。向量正确性及 CPU/Ara 交接沿[向量诊断](vector-debug.md)，DMA 条件沿[DMA 诊断](peripheral-debug.md#dma)。

<a id="alternate-loaders"></a>

## 替代装载路径的协议与观察边界

Serial Link 先把数据写完并满足可见性约定，再写 scratch0/1 的 64 位入口，最后以 scratch2 掩码 2 通知 ROM。当前源码按 bit1 判断，旧注释/随附软件文档有 bit0/bit2 表述差异；应以表达式和阶段协议为准。应用退出则改用同一 scratch2 的 bit0 与返回码。当前日志检查器主要识别 JTAG，不能把它原样用于 \[SLINK\] 成功判定；VCU118 Link 尚无已建立的板端闭环。

UART 服务需 ACK=0x06 握手，READ/WRITE/EXEC 命令携带小端 addr64/len64 字段；终端直接发送 ELF 字节不构成该协议。WRITE 首次 ACK 不是数据写完，EOT 才是该传输阶段结束，EXEC 返回 EOC=0x14 及 32 位返回码。服务对输入目标地址没有完整白名单，也不验证 ELF；主机须限定合法 RAM 范围、长度和超时，不能对未知地址试探写入。

<a id="platform-rom-return"></a>

## Platform ROM 的正常返回缺口

官方 Platform ROM 契约允许初始化后返回通用启动；本地 `_prom_check_run` 的 `jalr t0` 后紧邻 `boot_next_stage`，普通 ret 返回会落入下一阶段跳转逻辑，而非 \_boot。已有审查同时检查了源汇编与已生成 ROM 指令；上游修复提交 `9b4c222df72f74f90ab9f36d80ba7b527f92e62b`（PR #187）未纳入当前 HEAD。详细证据见[独立核查](../../handoffs/L01_platform_rom_boot_review.md)与[平台决策专题](../../03_Platform_ROM_Clock_IP_Configuration.md)。

影响范围是启用非零 PlatformRom 并期望正常返回的路径；默认 0 绕过该调用，不据此判定全部既有启动失败。修复与重新生成 ROM 属于 S01-B01 工程任务，本轮未实施。后续须同时验收空钩子返回、实际初始化及默认启动；只更新源 S、保留旧 ROM RTL 不能完成修复。

<a id="media-start"></a>

## 介质启动的已有局限

先确定镜像含的是符合本地 raw/GPT 契约的连续载荷，而非误把 ELF header 放到 SPM 执行入口。默认最多 96 个 512 字节 LBA，即 48 KiB；GPT 简化回退不等于完整分区校验或认证。ROM 从 code\_buf 起点调用，因此 entry 的布置与 JTAG 直接取 e\_entry 的规则不同。

SD 当前 TB 拒绝 BOOTMODE=1，没有该模型闭环；NOR 的 CR3V 写方向、EEPROM HAL 跨界及递归问题按[SPI](peripheral-debug.md#spi)和[I2C](peripheral-debug.md#i2c)证据继续保留。少量模型预填数据、驱动函数存在或有旧镜像，均不能替代完整自主启动结果。

ROM 的 SD/NOR 初始化等待调用 `clint_spin_until`，对应绝对 mtime 阈值：阈值已过去即返回，尚未到则仅等剩余量。它不保证从初始化结束起额外等待 1 ms/350 μs。器件规范若要求从上电、复位或命令完成开始计时，后续须记录参考事件和实际波形核实。此处只解释既有实现差异，不修改驱动、不授权介质擦写。

<a id="known-issues"></a>

## 已知软件问题的证据与验证状态

| 问题/边界 | 证据与影响 | 当前状态 |
| --- | --- | --- |
| Platform ROM 返回 S01-B01 | 源汇编及既有生成指令；非零平台钩子 | 未修复，未目标回归 |
| JTAG 继承栈接管 | VIP 等待位与 ROM 后续指令顺序；spm.ld 继承 sp | 真实暂停位置/栈仍需记录，不能泛化失败 |
| 默认 ROM C 调用栈对齐 | 源汇编 SPM 顶端−8 后直接 call main；默认 sp 模 16 为 8 | 源码边界确认；实际 ROM 指令、影响及目标验证待启动任务处理 |
| JTAG 段尾 | i&lt;=sec\_len 与无末字节边界；任意长度 PT\_LOAD | 源码风险确认，未动态复现/修复 |
| 默认 handler / 整数包装范围 | crt0 的弱自循环、128 B整数保存；未包含完整 FP/RVV/嵌套 | 当前接口边界；不能当 OS port |
| CLINT/UART、SPI/I2C 实现问题 | 已有驱动源码与外设诊断；影响计时/完成/介质事务 | 对应问题仍开放，本页只回链 |
| Ara/iDMA 和目标场景 | 向量/外设诊断中的接口与完成限制 | 未因文档重组关闭，不新增目标通过记录 |

本页以 [VIP](../../../target/sim/src/vip_cheshire_soc.sv)、[ELF loader](../../../target/sim/src/elfloader.cpp)、[ROM](../../../hw/bootrom/cheshire_bootrom.S)、[crt0](../../../sw/lib/crt0.S)、[CLINT](../../../sw/lib/dif/clint.c)和[UART](../../../sw/lib/dif/uart.c)为当前源码依据；历史证据保留原日期。正文生成/链接检查只验证教材产物，不能替代目标执行、介质读取或修复验收。

---

[上一页：参考 · 来源与验证记录](evidence.md) · [下一页：外设调试与故障诊断](peripheral-debug.md)
