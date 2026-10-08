# L01-S 软件主线与 trap 教材实施

2026-10-08；输入 `mp/ara-pulp-v2` / `459f9d6f5748e39063f7bb67e959c2f27859915d`。本轮用户授权多个子 Agent 实施教材，主管统一导航、生成与验收；本记录只说明 L01-S 的实际正文修改，不把规划或文档通过当作目标执行。

## 1. 修改范围与保护

完整审读并修改 `learning/content/{architecture,cva6,configuration,runtime,build,boot,boot-debug}.html`，新增 `traps.html` 和 `software-debug.html`。同步 `software/README.md` 当前连续阅读入口。未修改生产 RTL/sw、依赖、配置、地址、链接脚本、工程构建入口或教材示例。未改图稿、可编辑 PPTX、历史证据或旧站；未自行改公共清单、生成页或维护脚本。

开始时上述多数正文和整个站点已有未提交工作，属于输入基线。本任务七个输入正文的原样副本及哈希保存在 [software/before](learning/evidence/system-implementation-20261008/software/before/)，总输入保护由主管统一执行。图引用保留原集合（九个引用），只按讲述顺序调整位置。

## 2. 修改前后与旧链接

|页/锚点|修改前的具体问题|已实施的改变|读者任务|
|---|---|---|---|
|architecture#requests / #port-roles|模块接口表与完整图先于具体过程，第三个故事是调试装载，缺事件关系|数组取指/数据、UART字符、GPIO事件连续展开；详细图/端口表后置；补功能、事务、地址、实现四视角|给同一连线说明谁发起、传什么、怎样完成，区分事件与数据搬运|
|cva6#functional-units / #configuration-families|软件使用模型被CPU资源和配置族打断|先PC/整数与CSR/MMIO、M/S/U、trap/内存/Ara职责；配置族/覆盖/scoreboard/分支资源保留在可选回查|核程序所需能力与状态，不要求先解释流水资源|
|configuration#first-program-contract|从展开机制和Ara组合开始，读者不知为何配置|用同一标量SPM/UART任务先配齐CPU/SoC/平台/软件；软件契约前移，Ara和RT/CLIC案例明确为后续回查|解释为什么整数数组仍需当前crt0的F/D，为什么链接地址不建立存储|
|runtime#software-stack|将构成、构建、启动混列为printf层级，原句称最后BootROM/loader层才访问MMIO|从137个对象开始，四种关系分别用连续段落解释；增加真实main→printf→_putchar→uart_write→MMIO→引脚与flush|复述每一步执行者、输入/输出和完成，指出UART路径没有器件HAL|
|build#software-options|Make变量表早于翻译单元、对象、库和ELF|先完整生成过程/段与节/布局，再回查变量；构建失败详述进入诊断|从seed/result追到文件字节、RAM与BSS责任，不把dump当加载文件|
|boot#default-path / #crt|平台钩子/各介质和OS早于应用完整初始化|默认ROM→SPM/JTAG→crt0→main→UART/退出先连续讲完，再讲PlatformROM、被动/自主介质和ZSL|解释不同装载者交接到同一应用环境的前提|
|boot-debug#debug-workflow / #observe-program|调试主要是DMI枚举与VIP内部动作|加入GDB/服务器/传输/DM职责、同一ELF断点/寄存器/反汇编观察；DMI细节后置|分清主机符号、目标字节、运行PC，说明halt没有冻结全部SoC|
|traps（新）|通用trap与上下文前置散在CPU和设备章|调用→同步异常/异步中断→硬件CSR→整数包装→服务/返回→委托/调度|说明硬件保存与软件保存的分工；ret、mret、PLIC complete不混同|
|software-debug（新）|启动/构建/loader/平台缺口穿插正常路径|按最后完成的责任交接定位；集中段尾、继承栈、PlatformROM、介质与输出诊断|正文能独立读完；出现症状能从明确入口找到证据|

七个已有页面共 **84 个原 ID 全部保留**，不用新增跨页强制重定向。语义迁移采用原位置保留最小条件及直达链接：

|原入口|详细内容的新位置|原入口仍保留什么|
|---|---|---|
|boot#platform-rom|software-debug#platform-rom-return|正常平台责任、栈条件、非零钩子未修复的短阻塞提示|
|boot-debug#loader-limits|software-debug#loader-tail|文件字节/BSS责任和段尾风险短提示|
|boot#gpt-raw及各介质节|software-debug#media-start|镜像/入口、绝对等待语义及可执行边界|
|build#build-practice|software-debug#build-errors|实验前提、产物与判据|
|boot#crt / cva6#csr-trap|traps#software-context 与 software-debug#trap-stop|进入C与弱handler适用范围、正常机制/诊断各自入口|

`software-stack` 不再是错误的垂直调用栈，锚点现在解释同一概念的四种关系。CVA6 的旧资源锚点仍精确落在对应参考内容，未将字段事实删除。

## 3. 源码与官方资料核查

定向来源见 [sources.json](learning/evidence/system-implementation-20261008/software/sources.json)，记录37个本地文件哈希和对应符号/主题；不是对37份文件全部逐行审计的声明。

- 先采用随附 `docs/um/sw.md`、`docs/tg/integr.md` 及 CVA6 programmer/trap 文档，再核当前消费者。随附软件文档的被动请求 bit0、EEPROM 重复模式值等旧描述不覆盖当前表达式；正文继续按 scratch2 掩码2/mode3，并在诊断记录版本差异。
- `crt0.S` 确认BSS、FS、调用main、返回scratch协议和128字节整数包装；`csr_regfile.sv` 对照trap入口/MRET状态更新；advanced.c用于完整正常服务。原包装不扩写成FP/RVV、嵌套或OS上下文切换已支持。
- UART源码确认初始化无返回值、8位MMIO、THR_EMPTY与TMIT_EMPTY、printf出口；CLINT确认测频前提与绝对等待。函数返回、控制器空闲、远端接收正确继续分开。
- VIP/ELF loader确认p_paddr、p_filesz/p_memsz、SPM位轮询、halt、DPC、退出码与段尾问题；OpenOCD真实公共脚本是 `util/openocd.common.tcl`，没有以猜测的脚本名生成命令。
- 在线查阅RISC-V psABI（当时1.1预发布，仅采用既有LP64D/栈规则）与GDB官方文件/符号说明。ISA官方网页尝试返回错误，trap以随附官方文档加当前源码核对，不声称读到失败页面。在线新版内容不升级成本地能力。

没有形成新的工程修复结论；Platform ROM S01-B01、iDMA、Ara及已知介质/loader验证缺口全部保留。

## 4. 本任务实际检查与教学验收

独立证据目录：[software](learning/evidence/system-implementation-20261008/software/README.md)。使用Python 3.13.5执行只读正文检查，最终结果 [content-check-release2.json](learning/evidence/system-implementation-20261008/software/content-check-release2.json)：9页、84旧锚点、189个本地目标/锚点检查通过，标题ID唯一，九个原图引用保留；构建/默认启动/CVA6/trap顺序符合预定依赖。独立复算137项总和为28085；这不是目标程序执行。

`git diff --check` 退出0。没有运行 build_site、浏览器或大型工程检查；主管将统一生成、链接/迁移检查、桌面/手机预览及最终保护核对。源HTML检查不替代生成后的阅读布局。

作者任务验收已逐段核对：

1. 不打开诊断可复述数组对象→编译链接→ELF→ROM/SPM→装载→crt0→main→库/DIF/MMIO→UART→退出，列出每处执行者和地址意义。
2. 可在main前区分seed初值与result零初始化；能分别解释编译成功、入口交接、数组正确、UART空闲与VIP返回码。
3. 可解释同一CPU上的M/S/U、CSR与MMIO、ABI保存与异步包装、trap与任务切换关系。
4. 保留了继承栈、loader段尾、弱handler、非零PlatformROM和介质边界，不通过移走诊断隐藏阻塞条件。
5. CVA6主线以正确使用为限；配置规模与高级模式是回查，不成为首个程序的前置。

以上是**作者审读**，不是本人对自己章节的独立复审，也没有真人试读或新增软件构建/仿真/板测。主管与其他审读者仍可据完整过程提问题。

## 5. 交给主管与OS的接口

新增主章 `traps`，建议标题“异常、上下文与特权返回”；新增参考 `software-debug`，建议标题“软件、启动与调试诊断”。推荐中断页 `#trap` 回链 `traps#software-context`，首页/来源页增加软件诊断入口；公共文件均由主管处理。

L01-OS可引用 `runtime#abi`、`boot#crt`、`boot#later-stages`、`traps#call-versus-trap/#trap-entry/#software-context/#trap-return/#syscall-scheduling/#local-handler`。OS页职责是A→B→A、虚拟内存与Linux/驱动，避免重复展开裸机crt0。仍未选择具体产品OS/版本，未移植port/BSP或修改工程。

## 6. 收尾定向自查修正

审读外设保留章时，重新核对 spi_s25fs512s.c，确认CR3V的Rx方向缺陷仅在single_flash写擦函数，init/single_read不经过它。已修正boot#nor-boot曾过度扩大的阻塞提示，保留真实模式/镜像/目标验收条件。此项为作者自查修正，不计入对本人软件章的独立通过。修正后正文再次冻结，最新源检查为content-check-release2.json。
