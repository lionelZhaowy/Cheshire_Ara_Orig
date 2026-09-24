<a id="cheshire-实验课堂l01"></a>

# Cheshire/CVA6/Ara 教材阅读与维护说明

在浏览器直接打开 [index.html](index.html)，无需安装依赖、联网或启动后端。入门顺序：01 系统架构 → 02 RISC-V 与 SoC 基础 → 03 硬件与软件配置体系 → 04 C 程序的编译、加载与启动（配合实验 0～3）→ 05 软件仿真流程与故障定位 → 06 访存、DMA 与 RVV（配合实验 4～7）。07 为 ASIC 迁移与 AI 系统规划导读。

## 教材组织与阅读路线

入门主线建立概念并完成程序运行闭环；进阶剖析按设备组织寄存器、驱动与执行验证；硬件主线解释配置展开、互连实现与系统集成。参数全集由 [配置参考](../configuration/README.md) 提供，软件入口与 API 由 [软件参考](../software/README.md) 提供；历史入门分析与提取交接书保留原有依据和范围。

进阶主线从 [advanced.html](advanced.html) 开始：08 完整系统/时钟复位 → 09 CPU/Ara 执行 → 10 驱动方法 → 11～16 全外设 → 17 启动调试 → 18 综合实验。2026-09-22 进阶版本为 24 页、18 张 SVG；新增 14 页、8 张细化图、429 项可离线搜索的寄存器索引。内容包括 CPU/Ara 执行机制和中断/DMA 综合案例。

这里的完整范围包括 SoC regs、Boot ROM、Debug、CLINT、PLIC、可选 CLIC/IRQ Router、UART、GPIO、I2C/EEPROM、SPI/NOR/SD、iDMA、LLC/SPM、AXI RT、Bus error、Serial Link、VGA、USB，以及外部 AXI/DDR 边界。各项明确区分默认 RTL、仿真模型和 FPGA 接出状态。电源域没有完整源码证据，图中如实标未描述；未来 ASIC 电源分区未伪装为现有实现。

页面中的 Markdown 参考文档可在 IDE 打开。完整仓库一起搬迁可保留源码链接；只搬迁 learning/ 可以看全部网页、图、交互与示例，但不能跟到原仓库源码。浏览器直接打开源代码可能下载而非显示，这是 MIME/浏览器行为，不是链接失效。

<a id="硬件学习主线2026-09-23"></a>

## 硬件主线与验证记录（2026-09-23）

新增 [hardware.html](hardware.html) 及 H01～H09/硬件实验，共11页、10张SVG；当前全站35页、28张SVG。推荐先读 H01参数化RTL → H02 CPU功能配置 → H03 SoC结构生成 → H04 Crossbar → H05接口适配，再读存储/DMA、外设、中断、平台和自定义IP。CVA6不深入流水线电路，重点讲配置消费者及对外行为。

硬件主线编写时的输入提交 `ae2b69fe0640e57c89dfc6bcc9404bfd5008e1a5`。生产RTL、sw、旧清单、FPGA和.bender不变；未跟踪的M01交接保留。模型/单元/SoC证据分层，见 [hardware-labs.html](hardware-labs.html)。独立Reg加法示例不是AXI设备，也未接入SoC。Questa 2024.1实际编译运行该两文件单元，35项检查通过；注错时模拟器原始退出码为0，日志检查器正确返回1。因此不能只凭工具进程码判断通过。该轮未运行生产 SoC 和 VCS。

```sh
python3 docs_codex/learning/scripts/build_hardware_figures.py
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/hardware_lab.py self-test
bash docs_codex/learning/scripts/run_hw_unit.sh
python3 docs_codex/learning/scripts/check_site.py
python3 docs_codex/learning/scripts/preview_site.py --hardware
```

`hardware_lab.py`只做有限单核场景计算、lane示例与人工握手trace检查，不是SV展开器。`hardware-model-baseline.json`锁定三个已审查生产文件；哈希变化须人工重审，不能自动更新后宣称模型仍正确。`record_hardware_sources.py`记录新增章节引用来源；它只记录哈希，不证明硬件行为。

`run_hw_unit.sh`使用vlib/vmap/vlog/vsim和timeout，在新的`/tmp/cheshire-hw-unit.XXXXXX`写setup/compile/run/injected日志，不写旧work库；脚本60秒限制单次编译/运行，缺工具返回2。完整日志为本机临时文件，摘要保存在`evidence/hardware-unit.txt`。`--hardware`浏览器检查使用独立证据文件，不覆盖先前两轮报告。

<a id="基准与边界"></a>

## 入门与进阶版本基准

以下为2026-09-22原入门/进阶版本的基准；新增硬件主线的基准与实测范围见上一节。

- 任务：L01；日期：2026-09-22；输入分支 `mp/ara-pulp-v2`，HEAD `379ae4544bc62e05a2736b11b33a3244181bba38`。
- 基于当前工作区已有文档与定向源码核对；未改原 RTL、sw、共享 filelist、FPGA 或依赖。现有未提交内容保持原样，只有本任务必要共享索引增补。
- [证据页](evidence.html)区分本轮实测、源码静态确认、用户历史报告、待验证示例、未来方案。
- 本轮的交叉编译和反汇编不等于目标程序运行；未进行大型 RTL 仿真、综合或板级操作。源码和文档清单见 [source_manifest.json](evidence/source_manifest.json)。

<a id="维护方法"></a>

## 内容维护与页面生成

### 标题与章节编排

页面标题统一使用技术主题名称；H2 按概念、结构、操作和验证组织，H3 从属于对应主题。问题与场景保留在正文、FAQ、自测或实验中。三条主线分别承担概览、设备使用与硬件实现职责，交叉内容用范围说明和链接衔接，不重复铺陈。

页面文件名及原有 HTML `id` 保持稳定。Markdown 标题改名时保留旧标题的显式锚点，兼容历史交接和外部书签。页面标题与章节顺序只在 `build_site.py` 的 `PAGES` 中维护；正文 H2 自动生成页内目录，侧边栏与上下章共用 `PAGES`。

### 页面生成与检查

手写正文在 `content/*.html`，统一导航/布局由 `scripts/build_site.py` 生成根目录各 HTML。修改正文后在仓库根运行：

```sh
python3 docs_codex/learning/scripts/build_figures.py
python3 docs_codex/learning/scripts/build_advanced_figures.py
python3 docs_codex/learning/scripts/build_registers.py
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/check_site.py
```

以上文档脚本只使用 Python 标准库。可选进阶浏览器回归：`python3 docs_codex/learning/scripts/preview_site.py --advanced`，需要本机 `google-chrome` 和允许本地套接字的环境，使用临时用户配置与 file://，覆盖 `evidence/advanced-browser.txt` 和 `advanced-*.png`；不带参数时使用旧报告命名。不要只改生成页面。图输入在 build_figures.py、build_advanced_figures.py 与 build_hardware_figures.py，输出为 assets/*.svg，没有 Mermaid/CDN、远程字体、图片请求或后端。JavaScript 增强图表适应宽度/放大阅读、步骤切换、寄存器过滤、表格容器与 AI 预算计算；关闭脚本仍可阅读正文、429项寄存器、图和折叠答案。

`content/registers.html` 由 build_registers.py 从明确列出的12个本地头文件生成，不手工修改；正文其余页面仍由人维护。索引只提取偏移/字段常量，不推断访问权限，也不会读写 MMIO。源码改变后重新生成并重审访问语义与哈希，不能自动沿用当前结论。

所有图用文字标明含义和证据边界。SVG 属代码维护的原生图形，不需要 AI 位图生成。在线官方资料链接是可选延伸阅读，不是页面渲染依赖；本地实现仍以版本冻结的源码为准。

## 独立软件和仿真辅助脚本

```sh
bash docs_codex/learning/scripts/build_example.sh array spm
bash docs_codex/learning/scripts/build_example.sh rvv spm
bash docs_codex/learning/scripts/prepare_sim.sh
bash docs_codex/learning/scripts/build_advanced.sh timer
python3 docs_codex/learning/scripts/validate_advanced.py
```

`build_example.sh` 派生自 `sw/sw.mk` 的最小构建方法，不调用根 make；每次新建教材 evidence 内目录。支持 hello/array/mmio/timer/dma/rvv，array 也可以 dram 链接。DMA/RVV 固定只允许 spm，并有严格的 128 KiB SPM/保留缓冲/栈前提，详见网站，不能用来推导 DRAM 一致性。

进阶复核发现 iDMA 控制桥64位/生成寄存器32位的lane适配缺口，旧HAL还用64位指针访问32位ID；旧入门dma例也增加此运行门槛，见 [第15章](dma-llc.html#lanes)。`build_advanced.sh` 支持 gpio/timer/capstone/eeprom/flash；capstone默认输出BLOCKED/rc16并不提交DMA。`DMA_INTERFACE_VALIDATED=1` 只表示将来接口独立验收后选择条件路径，不会修复硬件。原RTL/sw未改。

`validate_advanced.py` 构建8个版本，检查entry/BSS/trap符号/ISR指令、12个人工日志验收用例、DMA访问汇编以及31个受保护源码哈希，写 `advanced-builds.txt` 与 `advanced_build_logs/`。它不运行RTL；重复会新建编译产物并更新该摘要。实际目标日志用 `check_advanced_run.py <log> --stage gpio|timer|capstone|eeprom|flash`，当前只支持JTAG完成标记。GPIO引脚层、VGA帧、USB枚举、SD设备、AXI RT等的环境缺口见 [进阶证据](advanced-evidence.html)。

`prepare_sim.sh` 只调用 Bender 的本地导出，引用已有输入、复制原启动脚本和 DPI 到全新目录；不运行模拟器、下载模型或覆盖旧 filelist。实际运行命令与先决条件见 [仿真章](simulation.html)。当前独立清单只证明选择正确，仍待真实编译展开。

运行产物目录被本目录 `.gitignore` 排除；可审阅的本轮文本证据与浏览器预览保存在 evidence 下的独立命名文件。重新运行不会覆盖前次产物。应用日志用 `scripts/check_run.py <log> --stage <阶段>` 检查；默认固定 N=137，不适合未经同步修改的用例。

## 结构与写作整理记录（2026-09-23）

本次在已有 35 页网站与 15 篇 Markdown 教材/参考中统一标题和正文语气；页面顺序、文件名、技术表格数据、命令、源码引用和验证状态保持。配置、启动流程、参数化 RTL、I2C 和硬件外设章调整了内部层次。详见 [独立交接](../handoffs/2026-09-23_L01_editorial_revision.md)。

仅修改正文与标题时，依次运行 `python3 docs_codex/learning/scripts/build_site.py`、`python3 docs_codex/learning/scripts/check_site.py`。本次实际离线浏览器检查命令为 `python3 docs_codex/learning/scripts/preview_site.py --editorial --advanced --hardware`；需要本机 Chrome 与本地套接字。`--editorial` 使用独立报告和截图前缀，避免覆盖既有预览证据；后两项启用原有交互检查。

[内容保留检查](evidence/editorial-checks.txt)记录编辑前后比较范围；[浏览器记录](evidence/editorial-browser.txt)记录桌面/手机全站预览与交互检查。本次未重新构建软件、编译 RTL、仿真或板测，既有技术缺口仍保留。

<a id="验收与更新"></a>

## 验证要求与交接规则

更新技术结论时同时更新来源路径/符号和证据状态；源码 hash 改变后重新复核，不能自动沿用测试结论。`check_site.py` 检查本地资源、HTML/Markdown 锚点、标题与导航一致性、标题层级、SVG/XML、主要页面教学结构及外部渲染依赖；它不代替浏览器预览或 RTL 仿真。浏览器实测细节见 [checks.txt](evidence/checks.txt)和证据页。

最后按仓库 HANDOFF_TEMPLATE 写独立交接，串行增补 PROJECT_STATE、AGENT_TASKS 和 handoffs 索引；不因教材中的修复建议自动认领 E01/S01/V01 实施。
