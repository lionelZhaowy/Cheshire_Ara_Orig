# 仿真测试平台结构与验证流程

生成日期：2026-10-19。输入 HEAD：`c9abbb48946fe3a7244bfb3159919b7c9731cb59`。两图介绍 Serial Link 加载 SPM 程序、CPU/Ara 执行和软件自检；是源码核对与图稿交付，不是一次新的工程验证。

| 风格 | 可编辑文件 | 整页预览 |
| --- | --- | --- |
| 工业框图 | [PPTX](industrial.pptx) · [SVG](industrial.svg) | [PNG](industrial.png) |
| 教学层次 | [PPTX](teaching.pptx) · [SVG](teaching.svg) | [PNG](teaching.png) |

**本次汇报采用第 1 版的纵向工业图：**[可编辑 PPTX](industrial_portrait.pptx) · [SVG](industrial_portrait.svg) · [PNG](industrial_portrait.png)。1500×1870 纵向画布，输入为 `industrial.svg` 的单页完整图：上部输入和 TB、中部 fixture 内的 VIP/DUT、下部软件自检与主机观察/结果。保留主结构和真实通路，仅将 VIP 独立打印框并入日志输出、检查职责框改成页脚，缩短重复文字。下面的极简版保留作历史候选，当前选择以此纵向版为准。源码和证据边界共用下文。

**汇报插图（工业风精简版）：**[可编辑 PPTX](industrial_compact.pptx) · [SVG](industrial_compact.svg) · [PNG](industrial_compact.png)。画布为 1200×1010，适配所提供汇报页的空白区域；只保留 ELF→TB/VIP→Serial Link 装载、CPU/Ara→AXI→SPM、软件自检及 UART/SLINK 两路输出。TB/fixture 层次、配置差异、波形和断言细节见完整版及下文；精简不改变结果含义或证据边界。原两版文件保留，本次选择工业风用于该汇报插图。

两版均为单页 16:9；工业版先看硬件层次，教学版先看软件步骤。对象、连接方向和结果含义相同。本次风格比较不改变 RTL 模块指南采用 A 版连续走线的既定决定。

## 阅读顺序

1. **准备输入。** 场景取自[服务器指南](../../software/SERVER_SIMULATION_GUIDE.md)：`BINARY="../../../sw/tests/fmatmul.spm.elf"`、`BOOTMODE=0`、`PRELMODE=1`、`SELCFG=3`。前三项成为运行 plusargs；SELCFG 变为展开参数 `SelectedCfg`，不是 DUT 引脚。
2. **复位、装载、启动。** `fix` 同时容纳 `vip` 与 `dut`。VIP 产生时钟、复位和启动模式；复位释放后 CPU 先运行 ROM，配置 LLC 为 SPM。VIP 轮询 SPM 配置位，随后调用 DPI 取得 ELF 段地址、数据和入口，经 Serial Link→AXI→SPM 写入程序，再写 `SCRATCH[1:0]=入口`、`SCRATCH[2]=2`。ROM 检查的是 bit 1，随后清标志并跳入应用。
3. **执行与自检。** 应用 crt0 清 BSS；main 生成 A/B，CPU 标量循环得到 G，RVV 内核经 CPU→Ara 请求计算 C，Ara 经独立 AXI 入口读写 SPM。CPU 执行 `verify_matrix`，逐项调用绝对差阈值为 `0.001` 的比较。图中的软件框是执行步骤，不是新增硬件，也没有 TB scoreboard 或独立 golden model。
4. **报告与结束。** `Verifying result...` 只是比较开始；`Passed.` 是软件比较分支的输出，两者经 UART TX→VIP 监视打印。main 返回后，crt0 写 `SCRATCH[2]=(rc<<1)|1`；VIP 经同一 Serial Link 通路轮询 bit 0，右移取 rc，零值打印 `[SLINK] SUCCESS`，非零执行 `$error` 打印 FAILED。TB 等返回以及 UART 当前字节读完后执行无参数 `$finish`；没有把目标 rc 直接作为主机退出码传出。`[ELF]` 来自 DPI 的主机 printf，`[SLINK]` 来自 VIP，自检文本才经过 UART。
5. **辅助观察。** 普通日志说明进度和错误；软件自检检查本用例数值；局部断言/响应检查约束具体接口行为。FSDB/Verdi 只辅助定位，不替代这些判据。官方 `tee` 保存 stdout，stderr 及主机退出状态仍需单独核对。

实线双向箭头合并表示请求与返回；紫色虚线表示软件步骤/任务返回，绿色虚线表示 DPI 数据交接，灰线表示观察/日志。折线跨越处使用跳线，不表示电气连接。CPU/Ara 的总线适配、缓存、原子处理和 Regbus 分发作了归并；软件写完成寄存器仍由 CPU 经互连执行。SPM 使用 LLC 阵列，装载入口和 CPU/Ara 运行访存入口不同。

## 源码定位

路径均指本地输入版本，行号便于定位；目录中的依赖源码保持原版权与许可证。

| 图中对象或连接 | 对应源码位置 |
| --- | --- |
| compile / start、参数与日志 | [compile](../../../target/sim/vcs/compile.cheshire_soc.sh)：vlogan 组、620 行 CPU profile；[start](../../../target/sim/vcs/start.cheshire_soc.sh)：29–39 行参数转换、57–61 行展开/运行；[Ara 官方集成入口](../../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/Makefile)：29 行及 `update_vsim_src` |
| TB→fixture→VIP/DUT、结束条件 | [tb_cheshire_soc](../../../target/sim/src/tb_cheshire_soc.sv)：8–74 行；[fixture](../../../target/sim/src/fixture_cheshire_soc.sv)：20、77、170 行；[配置 3](../../../target/sim/src/tb_cheshire_pkg.sv)：29–48 行 |
| 时钟复位、Serial Link、UART 监视 | [vip_cheshire_soc](../../../target/sim/src/vip_cheshire_soc.sv)：162–194 行时钟/模式，466–493 行 UART，797–950 行读写、预加载、启动及结束任务 |
| ELF 文件→DPI→SV 缓冲区 | [elfloader.cpp](../../../target/sim/src/elfloader.cpp)：`read_elf`、`load_elf`、`get_section`、`read_section`、`get_entry`；处理 PT_LOAD 的物理地址与入口，不是 RAM 后门直写 |
| ROM 初始化 SPM、等待 launch | [ROM 汇编](../../../hw/bootrom/cheshire_bootrom.S)：63–106 行；[ROM C](../../../hw/bootrom/cheshire_bootrom.c)：23–34 行 `boot_passive`。C 注释的“bit 2”与实际 `& 2` 不符，以代码的 bit 1 为准 |
| CPU/Ara→互连→SPM/外设 | [cheshire_soc](../../../hw/cheshire_soc.sv)：265 行 Xbar、512 行 LLC、635–889 行 CPU/Ara 和适配、1295 行起 ROM/UART、1695 行 Serial Link。完整实例为 `gen_cva6_cores[0].i_core_cva6` 与 `gen_cva6_cores[0].gen_ara.i_ara` |
| SPM 链接、BSS、返回码 | [spm.ld](../../../sw/link/spm.ld)、[common.ldh](../../../sw/link/common.ldh)：SPM 起址 `0x10000000`；[crt0.S](../../../sw/lib/crt0.S)：46–69 行 BSS，116–131 行 main/退出。写完成码后实际执行 `ret`，不能照注释理解为永久等待 |
| A/B、参考 G、C 比较及 Passed | [fmatmul.c](../../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src/fmatmul.c)：默认 32×32、40 行比较、53 行 main、74 行标量 G、88 行向量调用、102–110 行报告；[vector_util.h](../../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/include/vector_util.h)：44 行 `similarity_check` |
| RVV 内核与 UART 输出 | [fmatmul.c.h](../../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/include/fmatmul.c.h)：`vsetvli`、`vle64.v`、`vfmacc.vf`、向量 store；[cheshire_util.h](../../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/include/cheshire_util.h)：UART 初始化/flush；[uart.c](../../../sw/lib/dif/uart.c)：67 行 `_putchar` |
| 局部检查，不是数值参考模型 | VIP 829、860 行检查 AXI B/R 响应；[axi_xbar](../../../.bender/git/checkouts/axi-ecdc900686449c15/src/axi_xbar.sv)：166–179 行 ID 宽度断言；[axi_demux_simple](../../../.bender/git/checkouts/axi-ecdc900686449c15/src/axi_demux_simple.sv)：462–505 行有效位、通道稳定性与选择范围检查 |

## 配置差异与未核实事项

- **不能直接用本地图证明本地脚本可跑向量。** 本地 start 尚未写入上述四项值，也没有指南中的 `set -e -o pipefail`；本地生成 compile 选 `cv64a6_imafdchsclic_sv39_wb`（V=0），不是指南记录的 `cv64a6_imafdcv_sv39`（V=1）。配置 3 只明确 Ara=1、2 lanes、VLEN=2048。图按指南的学习场景说明机制，不把本地清单与服务器构建混为一份配置。
- 本地现有 ELF 的 `readelf -h -l` 确认入口/LOAD 地址均为 `0x10000000`；SHA256 为 `9b1c771c38b6a69b614276a60c59acb4d1fbc47adc4ecb0b0a8f2e19e722335e`，不同于交接中的服务器 ELF。没有重新生成或执行它，也没有据其存在推断 FS 修正或程序通过。本地 crt0 仍有旧 FS 清位写法；服务器 FS=Clean 修正仅沿用交接记录。
- [E01 交接](../../handoffs/E01_fixed_vector_extraction.md)记录了 2026-10-19 普通 32×32 fmatmul 的 Passed/SUCCESS/正常 finish，但未取得该次主机退出状态；20 μs 波形短测与前 10 μs FSDB 读取是另一项历史证据。本轮未访问这些服务器产物；当前服务器配置、完整波形版运行、GUI及全部断言启用/触发情况仍未核实。
- 本地 VCS 清单包含 `-assert svaext`，上述 AXI 检查受 `VERILATOR/XSIM` 等条件控制；这是静态入口与源码证据，不是断言运行覆盖报告。VIP 的外部内存模型和返回端模型存在，但本例 ELF/矩阵主路径在 SPM，故主图不展开 DRAMSys、外部 DRAM 或随机返回端；没有新增随机矩阵激励、UVM、覆盖率平台。单例不能代表完整 RVV、DDR 或 ASIC 验收。

## 图稿检查范围

已读取并采用 `industrial-svg-pptx`、`svg-pptx-diagrams-native` 的规则和后端。两份 PPTX 各含 **153 个原生对象、94 个文本对象、30 条完整箭头、16 个虚线对象**，无整页图片；紫色软件区仍是可编辑图形与文字。

使用 Python `python-pptx`/ZIP XML 保存重读，并在临时副本修改文字、模块位置及箭头线宽后再次保存重读。对两版对象/边语义和方向逐一核对；用本地 Chrome/CDP 渲染最终 SVG，并复用仓库现有 DrawingML 子集预览器从**最终 PPTX**读取对象重新渲染。已实际查看两版整页、连线区和自检区；文字越界、文字互叠及箭头穿字检查未发现问题。检查记录与最终 PPTX 整页/局部预览在 [checks](checks/validation.json)。

**Office 显示/编辑未实测。** PPTX 指定 Microsoft YaHei，本机预览回退到文泉驿正黑；本地 DrawingML 预览不等同于 PowerPoint 排版。箭头是完整可编辑对象，但未绑定模块端口，移动模块不保证自动跟随。未修改 RTL、软件、启动脚本或配置，未构建、仿真、连接服务器或新增工程验证结论。

精简版另以 `python-pptx`/ZIP XML 保存重读检查：59 个原生对象、34 个文本对象、13 条完整箭头、3 个虚线对象，无嵌入图片；临时副本文字、框位置及箭头线宽修改后重读通过。从最终 PPTX 重建的整页和 DUT/自检/报告局部预览已实际查看，Chrome/CDP 文字与连线检查未发现问题。记录见 [compact-validation.json](checks/compact-validation.json)，预览见[整页](checks/industrial_compact-pptx.png)与[局部](checks/industrial_compact-detail.png)。同样未在 Office 中实测，未新增仿真证据。

所提供汇报页的 EEPROM 启动编码重复写作 `2’b10`；当前 `cheshire_bootrom.c` 的 EEPROM 分支为 `case 3`，应标 `2’b11`。原汇报文件未提供，本次未修改该页。

纵向版检查：141 个原生对象、86 个文本、28 条完整箭头、14 个虚线对象，无嵌入图片。`python-pptx`/ZIP XML 保存重读及临时副本编辑检查通过；与第 1 版逐项核对保留连接的方向/线型，省并的两个框和两条内部日志连接见 [portrait-validation.json](checks/portrait-validation.json)。使用 Chrome/CDP 查看最终 SVG，以及从最终 PPTX DrawingML 重建的[整页](checks/industrial_portrait-pptx.png)、[VIP/DUT 连线局部](checks/industrial_portrait-connections.png)、[自检与结果局部](checks/industrial_portrait-results.png)。Office 未实测；图稿修订不构成工程验证。
