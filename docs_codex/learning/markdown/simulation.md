# 41 · Questa/VCS 仿真与结果验证

仿真输入、目标运行、结果数据与退出判据。

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/simulation.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../simulation.html) · [阅读路线](index.md)

- [41.1 仿真运行的输入组成](#flow)
- [41.2 独立清单与工作目录](#prepare)
- [41.3 QuestaSim / ModelSim 的入口](#questa)
- [41.4 VCS 的入口差异](#vcs)
- [41.5 输出、退出与独立结果校验](#judgement)
- [41.6 执行条件与独立诊断入口](#debug)
- [41.7 向量实验的动态验证证据](#vector-trace)

**本章任务**

按阶段检查输入、运行、数值和退出。 前置：[04 · 工具链、链接与 ELF](build.md)、[15 · JTAG 与程序加载调试](boot-debug.md)。

<a id="pieces"></a>

<a id="exercise"></a>

<a id="flow"></a>

## 41.1 仿真运行的输入组成

仿真需要目标软件、硬件模型、主机加载器和外部环境。RISC-V GCC 生成应用 ELF；RTL 编译器处理模块和类型；展开器按 SelectedCfg 建立实例层级；主机 C++ 编译器生成 DPI 加载器。运行时再由 TB 提供复位、器件响应和程序加载。软件构建成功可以推进到后面阶段，不能跳过这些输入检查。

教材先使用 UseDramSys=0 的 AXI 行为内存，不依赖额外 SystemC/DRAMSys 库。它适合检查地址和总线行为；真实 DDR 的 PHY、校准、刷新和板级时序属于另外的验证对象。当前默认 fixture 有 UART 接收、NOR 和 EEPROM 模型，也有未接出的外设观测点。

| 共同阶段 | 输入与输出 | 首先定位的失败 |
| --- | --- | --- |
| 软件构建 | journey.c / 库 / 链接脚本 → ELF、map、dump | 编译或链接的首条错误 |
| RTL 编译 | 有序清单 / 宏 / package → 工具工作库 | 缺文件、重复定义、类型或顺序错误 |
| 展开及 DPI | SelectedCfg / C++ loader → 可运行设计 | 实例参数、库、主机 ABI、许可证 |
| 装载与执行 | BINARY / boot mode → 内存、PC、UART、退出码 | 最早没有达到的目标状态 |

<a id="prepare"></a>

## 41.2 独立清单与工作目录

[prepare\_sim.sh](../scripts/prepare_sim.sh) 只调用 Bender 本地导出，选择向量 profile、真实 decoder、ARA 宏及 2/2048，并复制启动脚本与 ELF loader 到新目录。它检查现成 NOR/EEPROM 模型，缺输入时退出。导出仍引用本仓库源码绝对路径，作用是隔离本次模拟器工作库；独立 ASIC 源码提取属于后续任务。

```
# Bash，仓库根；只准备输入，不运行 RTL
bash docs_codex/learning/scripts/prepare_sim.sh
# 将上一命令打印的绝对路径填入 LEARN_SIM
LEARN_SIM='/实际输出目录/evidence/sim.XXXXXX'
LEARN_REPO="$PWD"
# LEARN_OUT 是实验 A 打印并检查过的本次构建目录
LEARN_ELF="$LEARN_OUT/journey.spm.elf"
test -s "$LEARN_ELF"
rg -n 'config_pkg.sv|first_pass_decoder' "$LEARN_SIM/vsim/compile.cheshire_soc.tcl"
```

接受条件为唯一 cv64a6\_imafdcv\_sv39\_config\_pkg、唯一真实 decoder、没有 scalar profile 或 decoder stub。历史导出记录有 .svh 类型 W28 告警，实际编译仍需确认 include 输入。`make sim-all` 的职责是准备仿真输入；它没有代替下面的运行步骤。

<a id="questa"></a>

## 41.3 QuestaSim / ModelSim 的入口

Questa 用 vlog 建库，Tcl 中的 vsim 负责展开与运行。原 start.cheshire\_soc.tcl 把 SELCFG 转为 `-GSelectedCfg`，把 BINARY/BOOTMODE/PRELMODE 转为 TB plusargs；这些是工程定义的参数。ModelSim 要具有当前设计需要的 SystemVerilog、优化和 DPI 能力，具体版本须在目标环境验收。

以下命令是**待目标环境验证的 SoC 操作**，本次教材重构未运行。先完成编译并检查退出码和首错，再执行加载运行；路径建议不含空格，变量沿用上一节。

```
(
  cd "$LEARN_SIM/vsim" || exit 1
  timeout 300 vsim -c -do 'onerror {quit -code 2 -f}; set r [source compile.cheshire_soc.tcl]; if {$r eq "1"} {quit -code 2 -f}; quit -f' > compile.log 2>&1
)
# 确认 compile.log 和退出码后，另执行：
(
  cd "$LEARN_SIM/vsim" || exit 1
  timeout 300 vsim -c -do "onerror {quit -code 2 -f}; set SELCFG 3; set BOOTMODE 0; set PRELMODE 0; set BINARY {$LEARN_ELF}; source start.cheshire_soc.tcl; run 100 ms; quit -f" > simulate.log 2>&1
)
python3 "$LEARN_REPO/docs_codex/learning/scripts/check_run.py" "$LEARN_SIM/vsim/simulate.log" --stage array
```

100 ms 是目标仿真时间，timeout 300 是主机墙钟秒数。主机可能花很久才模拟少量目标时间。退出码 124 表示墙钟超时，应记录最后进展；compile 清单 catch 后可能返回 1，所以外层显式检查 Tcl 返回值。展开信息位于 simulate.log 前部。

<a id="vcs"></a>

## 41.4 VCS 的入口差异

VCS 先由 vlogan 处理 RTL，再由 vcs 展开并编译链接 elfloader.cpp，生成 simv。SelectedCfg 在展开时传入；BINARY 是 simv 运行时参数。原 start shell 的 shebang 被注释且管道错误传播有限，教材按原参数拆成顺序执行的步骤，以便把首错和阶段对应起来。

```
# 在装有 VCS/vlogan 的服务器重新导出当地绝对路径
(
  set -e
  cd "$LEARN_SIM/vcs"
  timeout 300 bash compile.cheshire_soc.sh > compile.log 2>&1
  timeout 300 vcs -full64 -kdb -O2 -debug_access=r     -debug_region=1,tb_cheshire_soc -cpp "$(command -v g++)"     -pvalue+SelectedCfg=3 ../src/elfloader.cpp tb_cheshire_soc > elaborate.log 2>&1
  timeout 300 ./simv +BOOTMODE=0 +PRELMODE=0 +BINARY="$LEARN_ELF" > simulate.log 2>&1
)
python3 "$LEARN_REPO/docs_codex/learning/scripts/check_run.py" "$LEARN_SIM/vcs/simulate.log" --stage array
```

参数来自当前本地入口，目标 VCS 对它们的支持仍需实测。本组命令仅设置墙钟限制；需要统一目标周期 watchdog 时应由独立验证任务在 TB 中定义。此前环境探测见[2026-09-28 记录](evidence.md#current)；本次结构检查见[结构修订记录](evidence.md#structure)，历史版本号不作为兼容性保证。

<a id="judgement"></a>

## 41.5 输出、退出与独立结果校验

贯穿例按独立公式逐个比较 `result[i] == 3*i+1`，同时计算总和。N=137 时总和为 28085，正常日志应含 `LEARN stage=1 Hello Cheshire!` 和 `LEARN sum=28085 errors=0`，并以 \[JTAG\] SUCCESS 结束。新例另报告初态检查；初态错误会进入同一个 errors 和返回码。

注错构建翻转 result\[5\] 的低位，从 16 变为 17，预期总和 28086、errors=1、程序返回 1。检查器应拒绝该日志。这个对照验证了“数据差异 → 错误计数 → main 返回 → scratch2 → VIP → 主机检查器”的传播链。手工日志只能检验检查器规则，真正的运行证据需要目标日志。

UART 是程序进度证据，scratch2 是结束协议，逐元素比较是算法证据，模拟器错误日志是硬件/工具故障证据。进程正常退出仍应检查四者；已有矩阵示例存在最终总是 return 0 的路径，因而本书采用独立错误计数。

<a id="debug"></a>

## 41.6 执行条件与独立诊断入口

正常实验仍需记录装载、main、逐项校验和结束协议。没有达到预期进度时，进入[目标运行阶段诊断](system-debug.md#simulation)；原PC/CSR、测频/UART、结果和结束定位要求已迁移，生产缺口没有关闭。

<a id="vector-trace"></a>

## 41.7 向量实验的动态验证证据

目标仿真首先要保存实际展开的 profile/Cfg.Ara/Cfg.AraNrLanes/Cfg.AraVLEN、decoder 源清单和 ELF 哈希，再按符号地址定位 learn\_vadd/learn\_sum。波形观察依次取 CPU PC/scoreboard trans\_id、acc\_dispatcher req\_valid/ready 与 insn、Ara resp\_valid/exception、sequencer running、VLSU AR/R/AW/W/B 及 load\_complete/store\_complete。层次路径以本次展开为准，不复制另一配置的固定 dut 路径。

一条教学 WaveDrom 只说明应该追踪什么关系，真实波形需保存 simulator 数据库及导出的时间区间、时钟尺度、信号层次与工具版本。把请求接受、应答、CPU 提交、内部完成和结果读取标在同一事务上。先确认选中了真实 Ara 路径，再用逐项参考及故障注入验证数据，最后才进入性能计时。

这些观察点定义应收集的正常因果链，本轮没有新的生产RTL仿真数据库。真实波形需由V01在匹配配置的目标上取得，相关故障定位见[独立入口](system-debug.md#simulation)。

**源码与进一步阅读**

[Questa 启动](../../../target/sim/vsim/start.cheshire_soc.tcl)；[VCS 启动](../../../target/sim/vcs/start.cheshire_soc.sh)；[plusargs 与结束](../../../target/sim/src/tb_cheshire_soc.sv)；[UART 与退出检查](../../../target/sim/src/vip_cheshire_soc.sv)

**只换 BINARY，要重编译 RTL 吗？**

软件字节变化通常只需重新装载运行；profile、宏或生成输入变化要重编译，SelectedCfg 变化要重新展开。按变化发生的阶段处理。

---

[上一页：固定配置工程与 ASIC 集成验收](future.md) · [下一页：正确性、性能与论文实验记录](measurement.md)
