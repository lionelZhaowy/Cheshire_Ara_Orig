# Cheshire 实验课堂（L01）

在浏览器直接打开 [index.html](index.html)，无需安装依赖、联网或启动后端。建议顺序：01 架构 → 03 配置 → 04 C 程序生命周期 + 实验 0～3 → 05 仿真 → 06 访存与实验 4～7；02 作为基础解释，07 为进阶导读。

进阶扩充从 [advanced.html](advanced.html) 开始：08 完整系统/时钟复位 → 09 CPU/Ara 执行 → 10 驱动方法 → 11～16 全外设 → 17 启动调试 → 18 综合实验。现有站点共 24 页、18 张 SVG；新增 14 页、8 张细化图、429 项可离线搜索的寄存器索引。用户同时选择了执行内部与中断/DMA综合案例两条扩充路线。

这里的完整范围包括 SoC regs、Boot ROM、Debug、CLINT、PLIC、可选 CLIC/IRQ Router、UART、GPIO、I2C/EEPROM、SPI/NOR/SD、iDMA、LLC/SPM、AXI RT、Bus error、Serial Link、VGA、USB，以及外部 AXI/DDR 边界。各项明确区分默认 RTL、仿真模型和 FPGA 接出状态。电源域没有完整源码证据，图中如实标未描述；未来 ASIC 电源分区未伪装为现有实现。

页面中的 Markdown 参考文档可在 IDE 打开。完整仓库一起搬迁可保留源码链接；只搬迁 learning/ 可以看全部网页、图、交互与示例，但不能跟到原仓库源码。浏览器直接打开源代码可能下载而非显示，这是 MIME/浏览器行为，不是链接失效。

## 基准与边界

- 任务：L01；日期：2026-09-22；输入分支 `mp/ara-pulp-v2`，HEAD `379ae4544bc62e05a2736b11b33a3244181bba38`。
- 基于当前工作区已有文档与定向源码核对；未改原 RTL、sw、共享 filelist、FPGA 或依赖。现有未提交内容保持原样，只有本任务必要共享索引增补。
- [证据页](evidence.html)区分本轮实测、源码静态确认、用户历史报告、待验证示例、未来方案。
- 本轮的交叉编译和反汇编不等于目标程序运行；未进行大型 RTL 仿真、综合或板级操作。源码和文档清单见 [source_manifest.json](evidence/source_manifest.json)。

## 维护方法

手写正文在 `content/*.html`，统一导航/布局由 `scripts/build_site.py` 生成根目录各 HTML。修改正文后在仓库根运行：

```sh
python3 docs_codex/learning/scripts/build_figures.py
python3 docs_codex/learning/scripts/build_advanced_figures.py
python3 docs_codex/learning/scripts/build_registers.py
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/check_site.py
```

以上文档脚本只使用 Python 标准库。可选进阶浏览器回归：`python3 docs_codex/learning/scripts/preview_site.py --advanced`，需要本机 `google-chrome` 和允许本地套接字的环境，使用临时用户配置与 file://，覆盖 `evidence/advanced-browser.txt` 和 `advanced-*.png`；不带参数时使用旧报告命名。不要只改生成页面。图输入在两个 build_*figures.py，输出为 assets/*.svg，没有 Mermaid/CDN、远程字体、图片请求或后端。JavaScript 增强图表适应宽度/放大阅读、步骤切换、寄存器过滤、表格容器与 AI 预算计算；关闭脚本仍可阅读正文、429项寄存器、图和折叠答案。

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

## 验收与更新

更新技术结论时同时更新来源路径/符号和证据状态；源码 hash 改变后重新复核，不能自动沿用测试结论。`check_site.py` 检查本地资源、站内锚点、SVG/XML、主要页面教学结构及外部渲染依赖；它不代替浏览器预览或 RTL 仿真。浏览器实测细节见 [checks.txt](evidence/checks.txt)和证据页。

最后按仓库 HANDOFF_TEMPLATE 写独立交接，串行增补 PROJECT_STATE、AGENT_TASKS 和 handoffs 索引；不因教材中的修复建议自动认领 E01/S01/V01 实施。
