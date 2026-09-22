# 交接：L01 / 进阶全外设与系统执行教材

## 基本信息

- 日期/对话：2026-09-22，本轮进阶扩充。
- 授权：延续L01教材，覆盖全部可用/可选外设的寄存器、驱动与硬件结构，细化系统、时钟复位/电源边界及软件→硬件流程。用户明确同时加入CPU/Ara内部与中断/DMA/所有权/超时综合案例。
- 状态：教材实现完成；目标RTL编译、展开、运行均待验证。未启动子Agent。
- 输入：分支`mp/ara-pulp-v2`，HEAD `379ae4544bc62e05a2736b11b33a3244181bba38`。开始时00/01文档已修改，AGENTS、共享状态、专题、handoffs、learning等已未跟踪；全部保留，不提交/清理/切换分支。
- 负责范围：`docs_codex/learning/`；串行增补PROJECT_STATE、AGENT_TASKS、00_README、handoffs索引。本轮未改01历史教程和原RTL/sw/地址图/filelist/FPGA/.bender。

## 本轮结果

- 新增14页，现全站24页：进阶路线/完整支持矩阵、完整系统/时钟复位/电源证据、CVA6/Ara执行、寄存器驱动方法、UART/GPIO、I2C/EEPROM、SPI/NOR/SD、CLINT/PLIC/CLIC/Router、iDMA/LLC/AXI RT/Bus error、Link/VGA/USB、Boot/Debug/系统寄存器、综合实验、寄存器索引、进阶证据。
- 新增8张SVG，现18张。完整SoC连接图、时钟复位边界、软件→硬件流程、CPU/Ara内部、低速外设内部、中断、所有权与隔离、Link/VGA/USB分层；均标教学示意，箭头有控制/数据/IRQ/clock含义。电源域无完整源码证据，明确未描述，不虚构已实现的UPF或断电域。
- 12个头文件、429个寄存器偏移与字段常量离线检索；关闭JS仍可读。UART别名/CLIC/USB/Router/Debug在正文手工核对表说明，不强套通用头。
- 独立C示例：GPIO软件注入→PLIC ISR、加入CLINT timer、条件DMA/逐元素/守卫/超时隔离；EEPROM/NOR只读16字节0x9a；旧HAL与单32bit DMA ID访问汇编对照。
- 本轮未完成：任何RTL运行、引脚GPIO/SD/VGA/USB端到端测试、生产代码修复、ASIC提取。未将编译或用户历史板测当作本轮运行。

## 新结论与依据

1. **iDMA控制接口强静态不匹配证据，目标故障尚未动态复现。** `hw/cheshire_idma_wrap.sv`的`dma_regs`/`axi_to_reg`保持64位；`.bender/git/checkouts/idma-77bf7fa56d324e6a/target/rtl/idma_reg64_2d_reg_top.sv`固定DW=32并直接截取data/strb。deprecated axi_to_reg→axi_lite_to_reg未显示addr[2]对应的lane搬移。原`sw/include/dif/dma.h`对+0x44 NEXT_ID/+0x84 DONE_ID使用uint64_t*，本机GCC实测拆成相邻两次32bit读取，见`evidence/advanced-dma-access.s`的legacy_next/single_next。
2. 新综合例默认`adv_allow_dma=0`，输出BLOCKED并返回16，不提交DMA；`DMA_INTERFACE_VALIDATED=1`只是将来接口验收后的编译选择，不修复硬件。明确32位ID、高低地址写、非零ID检查；任何超时/零ID都隔离buffer。旧入门memory/labs增加相同前置门槛，历史构建记录保留。
3. DMA wrapper没有完成IRQ，bus_err.dma是错误中断；backend为NO_ERROR_HANDLING。综合例ISR是GPIO和CLINT，DMA由前台查ID，未编造IRQ号。
4. GPIO输入=0、VGA输出悬空、USB PHY clock=0：`target/sim/src/fixture_cheshire_soc.sv`。VIP有EEPROM/NOR/Serial Link对端，SD BOOTMODE1在tb中fatal。VCU118宏没有USE_I2C/SD/VGA/USB；Link引脚未接。
5. Serial Link `clk_ena_o/reset_no/isolate_o`在SoC悬空，isolated_i绑0；IP寄存器存在不代表集成门控/隔离生效。clk_i/clk_sl_i/clk_reg_i都接系统时钟，仍有物理源同步域。
6. HAL静态审读：I2C短未对齐首块未对len裁剪、写分支STOP与递归偏移疑点；NOR CR3V写命令却构造Rx段；CLINT sleep_until判断方向/计数回卷读；AXI RT隔离轮询未掩码/无超时及6manager生成物与Ara7manager联动。全部独立建议，未改生产代码。
7. FPGA locked/MIG校准完成未纳入当前放行路径、USB复位直连主域；当前目录未发现完整UPF/CPF，不能宣布电源分区/CDC/RDC签核。VGA clk_div是FSM使能，RTC是同步边沿tick，不把它们画成所有逻辑另一个clock。

各结论有正文源码路径/符号；81份来源文件哈希在`learning/evidence/advanced-source-manifest.json`，寄存器来源另有JSON。

## 改动与接口

- 手写正文：`learning/content/advanced*.html`及system/execution/register-driver/uart-gpio/i2c/spi/interrupts/dma-llc/stream-io/boot-debug/capstone；registers由脚本生成。
- 图：`scripts/build_advanced_figures.py`→8个新SVG；统一build_site导航分入门/进阶，所有root HTML重生成。
- 示例：`examples/advanced.c`、`storage_read.c`、`dma_access_audit.c`；脚本`build_advanced.sh`、`check_advanced_run.py`、`validate_advanced.py`、`build_registers.py`。
- 样式/交互：离线寄存器搜索、进阶步骤切换、长导航/移动布局；preview_site新增`--advanced`，旧报告不覆盖。
- 无生产配置/profile/宏/地址/IRQ/位宽变更。只修改文档与教材独立示例。S01/V01需接收DMA/驱动验证建议；M01/P01接收一致性/时钟复位/电源证据边界。
- 未提交。独立构建目录被learning/.gitignore排除，摘要/完整编译日志/PNG与来源JSON可审阅；完整搬迁仓库保留源码链接，单搬learning可离线阅读但源码链接失效。

## 验证证据

工作目录仓库根。GCC15.2.0、binutils2.46、Chrome151.0.7922.108；vsim只查询版本得到Questa2024.1，VCS/vlogan不在PATH，许可证未检查。

```sh
python3 docs_codex/learning/scripts/build_advanced_figures.py
python3 docs_codex/learning/scripts/build_registers.py
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/check_site.py
python3 docs_codex/learning/scripts/validate_advanced.py
python3 docs_codex/learning/scripts/preview_site.py --advanced
git diff --check
```

- build/check脚本exit0：24页、18 SVG、站内链接/锚点/alt/离线资源/脚本语法/空白检查；最终计数见`advanced-site-checks.txt`。
- 8个最终软件版本exit0；entry=0x10000000、BSS在低64KiB、trap强符号与ISR整数指令检查；12个人工日志判据用例通过。**没有目标运行日志**。GCC对象边界/原代码/RWX等警告保留（26～99条），见`advanced-builds.txt`与`advanced_build_logs/`。
- 31项上轮受保护输入hash仍一致。DMA对照仅编译生成汇编，无MMIO操作。
- 实际Chrome file://预览全24页桌面1440×1100/手机390×844；图片、导航、无整页横向溢出；搜索唯一项/无匹配/清空、步骤、details、旧预算计算器；禁JS读正文与429项；无HTTP(S)请求/JS异常；8新SVG文字未越viewBox。另人工查看完整系统/时钟图、搜索和手机截图。修过预览脚本对无figure页面的截图选择并重跑，未掩盖失败。
- 本轮未RTL编译/展开/仿真/板测；未验证VCS版本/兼容性/许可证。SVG为教学图，截图是页面显示。

## 决策与下一步

- 用户已确认：同时扩充CPU/Ara内部与综合驱动两条线，篇幅可增加；全部外设纳入教学。普通排版无重复确认，无子Agent。
- 最小后续步骤：
  1. 读`learning/advanced-evidence.html`和第15章lane证据；S01/V01在独立任务确定32位桥/寄存器/HAL一致方案并验证+0/+4偏移、WSTRB、一次提交一次请求。
  2. 在有许可证的Questa或实际VCS环境，先编译/展开正确独立清单，验证ELF段尾、Hello/array；再跑gpio/timer与EEPROM/NOR只读。
  3. DMA接口验收后运行条件capstone正常/注错/超时，不允许超时后复用buffer；保存完整命令、ELF SHA、UART、退出码/波形。
  4. 分别补GPIO引脚激励、VGA帧观察、USB时钟/设备模型/驱动栈、SD模型；当前默认fixture无法替代这些环境。
- 最少阅读：本交接、learning/README.md、advanced-evidence.html、dma-llc.html、capstone.html；按具体外设再定向读源码。
- 共享索引已串行同步PROJECT_STATE/AGENT_TASKS/00_README/handoffs；不把这些建议自动升级为RTL修复授权。
