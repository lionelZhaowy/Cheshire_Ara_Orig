# 原版图稿的原生对象重建

> 2026-10-13 仅修复归档后的导航路径；下文验证记录仍对应原日期与输入，未重新验收图稿。

使用 `svg-pptx-diagrams-native`，共 **45 张图：diagrams 下 8 张，教材结构图 37 张**。所有图稿和配套文件平铺在本目录，没有下级目录；原文件和旧 skill 保留。

直接打开 [图稿总览](index.html)，或下载 [45 页可编辑 PPT 合辑](all_diagrams.pptx)。每张另有同名 `.svg` 母版、原尺寸 `.png` 预览和单页 `.pptx`。`learning_` 前缀表示教材图。

## 新增完整 SoC 架构图（2026-10-12）

[SVG 母版](soc_full_architecture.svg) · [PNG 预览](soc_full_architecture.png) · [单页原生 PPTX](soc_full_architecture.pptx) · [检查报告](soc_full_architecture.validation.json)。本图独立新增，未加入用户正在编辑的 `all_diagrams.pptx`；上方“45 张”及旧报告仍指原重建集合。

本图将现有 `crossbar_ara.png` 与 `ddr_interconnect.png` 合为系统总览，并参考用户提供的三张芯片框图组织总线和子系统。输入为 `mp/ara-pulp-v2` / `c4162204cfee0c48b81158b4296860a678d92bec`；依据 `hw/cheshire_pkg.sv::gen_axi_in/gen_axi_out/gen_reg_out`、`hw/cheshire_soc.sv`、`hw/cheshire_idma_wrap.sv`、`target/sim/src/tb_cheshire_pkg.sv` 和 [M01 契约第 12 节](../../engineering/IP_DDR_Interface_Contract.md#12-独立global-buffer与ddr需求更新)。这是一张现有接口加扩展候选的框图，不是新的固定配置或已实现网表。

- 主 Xbar 的 S0–S6 是接受 7 个 AXI master 的入口，M0–M4 是通向 5 类 AXI slave 的出口。编号沿单核 Ara 仿真配置；额外标出可选 AXI 扩展入口/目标。多个地址规则可共用 M2（LLC/SPM），不把 SPM 另算一个目标端口。图示省略逐通道返回线、部分局部适配和 cut。
- Regbus 展开 18 个外设/配置目标（单核，含三个 Bus-error 单元），另列 `reg_err_slv` 和 RegExt。IRQ router、AXI RT、CLIC 在参考 Ara 仿真配置中关闭，灰虚线仅展示其可选位置；其他模块也受各自 Cfg 使能控制，完整图不表示所有平台启用它们。
- iDMA 数据 master 和独立 AXI 配置 slave 分开。其配置仅在自身 wrapper 内转 Regbus，不挂在公共 Regbus 分支；原控制位宽验证缺口保持开放。
- DDR S0 为 LLC 出口，S1 为 NPU/GB 共用搬运出口，S2 为帧写入器。DDR 端口的 S 编号与主 Xbar S 编号独立。三口成立以统一 S1 为条件；若保留独立 NPU DDR master 与 GB DMA，须重新评估 S3/合流，不用此图冻结三口。多端口共享 DDR 带宽，实际控制器端口宽度与适配/CDC待定。
- 彩色虚线为新增候选：Ara 宽侧分流、独立 GB、NPU/搬运器、LVDS/ISP/帧 DMA、PLL 和 ASIC DDR/PHY。GB 容量、bank、lane/VLEN、CPU 直访路径和地址未冻结。ISP 与 NPU 可独立工作；RAW/ISP 图像录制按帧边界二选一。GB 与 LLC/SPM 是不同存储；旁路不自动建立缓存一致性或原子观察域。
- C1–C9 为同一 IP 的配置寄存器与功能块的对应标号，不是第二套 IP，也不是寄存器地址。这里采用 RegExt 配置候选；供应商 APB/AXI-Lite 接口需适配，未来可改独立 AXI 配置口。图中 PLL 的系统分发线不是时钟域冻结方案；早期启动、局部复位与 CDC 契约仍须落实。中断控制器已画出，逐源中断线及新 IRQ 编号未展开/冻结。

画布 3400×2440；PPT 编辑画布宽 28 in，保持原比例。386 个原生对象，其中 206 个文本对象、73 个完整箭头、26 个带原生虚线属性的对象；不含整图图片。字体使用 Microsoft YaHei，本机 PNG/度量使用 WenQuanYi Zen Hei 回退。已查看全图及 Ara、DDR、GB/图像通路局部，文字边界与重叠检查通过；**Office 显示/编辑未验证**。连接线未绑定模块端口，移动方框不保证连线自动跟随。

复现时输出到全新目录（运行原 45 张重建脚本不会重建本图）：

```sh
~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/2026-10-11_native_reconstruction/build_soc_full_architecture.py \
  --out-dir /tmp/soc-overview-new

~/.codex/skills/publication-figures/.venv/bin/python -c \
  "import cairosvg; cairosvg.svg2png(url='/tmp/soc-overview-new/soc_full_architecture.svg', write_to='/tmp/soc-overview-new/soc_full_architecture.png')"

~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/2026-10-11_native_reconstruction/verify_soc_full_architecture.py \
  --directory /tmp/soc-overview-new \
  --report /tmp/soc-overview-new/soc_full_architecture.validation.json
```

渲染仅复用现有 CairoSVG 环境，不采用 publication skill 的排版约束。原 `verify_outputs.py` 的全目录数量检查绑定历史 45 张快照；本次新增图使用上述独立检查，未重写历史报告。技术范围和保护核对见 [主题交接](../../handoffs/L01_native_reconstruction.md)。

## 重建内容

保留原版颜色、文字、布局和 SVG viewBox，没有按论文栏宽缩放，也没有添加外围说明框。将有明确对应关系的线/路径与三角形重建为单个带端点属性的对象：**306 个完整箭头，包含 18 个双向箭头，共 324 个端点**。4 处曲线附加短线合入原曲线；136 条虚线碎片重建为 **4 个完整矩形边框**。SVG 对象总数从 3618 降为 3154，1653 个文本对象原样保留。PPTX 另省略 45 个画布背景矩形，实际共 3109 个对象。

箭头尖端保留原坐标；箭头大小统一为新 skill 支持的中号三角端点，不承诺逐像素一致。Crossbar/DDR 早期图中 24 个原本与线身颜色不同的箭头端点统一使用线身颜色；虚线改为连续轮廓后，角点处的虚线相位可能与逐边拼接版本不同。

直线箭头为 PPT 原生连接线；曲线、折线为带原生端点属性的单个自定义几何对象。虚线为矩形的线属性。文字保持独立可编辑。连接线未绑定模块端口，移动模块不会自动保证连线追随；不承诺折线自动路由。

## PPTX 背景修正（2026-10-11）

45 张图的单页 PPTX 和合辑已更新。最底层、恰好铺满画布、无圆角和无异色边框的矩形不再作为图形导出：42 张白底图使用 PPT 默认背景，3 张浅色底图使用 PPT 页面背景填充。图内普通白色模块、有边框的矩形与圆角框保留。SVG、PNG 保持不变。

逐页比较更新前后的 46 个 PPTX（共 90 页）：除背景矩形及重新编号的对象 ID 外，其他图形 XML 完全相同。箭头、虚线、文字和布局保持；报告新增 `omitted_canvas_background_ids`。

## 来源与覆盖

[重建映射](reconstruction_plan.json) 固定 45 个输入文件的 SHA-256、每个箭头线身/端点 ID、原坐标和对应虚线段；执行脚本按映射重放，不使用距离推测任意旧图的关联。对应关系依据原图预览、端点方向和现有生成代码核对，尤其包括教材 `figure_primitives.py::arrow/curve` 和分层图 `build_figure.py::arrow/planned`。

[来源清单](source_inventory.json) 列出所有相关原版 SVG：同一图的初稿、v2、final、editable 和验证副本映射到一份新稿，优先采用正式最终版。旧 `before_datasheet` DDR 草案只保留来源记录，不冒充当前方案重新发布。教材以现存 37 张 editable SVG 为输入；已撤回的 6 张手工波形、WaveDrom 图、`backup_new` 中的 publication 版本及 native skill 自测图均不在本次原版结构图集合内。

本次重建不更新历史图中的技术快照。原图注明的候选方案/待验证状态继续有效。

## 验证及显示边界

- 每张 SVG 校验并导出，保存后重新读取 PPTX，核对对象、文字、箭头端点与虚线属性；没有整图图片嵌入。
- 45 张 PNG 已生成并逐张查看总览；对双向路径、曲线箭头和虚线框另作大图检查。PNG 是 CairoSVG 渲染，**不是 Office 截图**。
- [结构报告](export_report.json) 与 [验收报告](validation.json) 记录结果；程序化修改 4 个代表图的箭头线宽/虚线框宽度，再保存重读，完整对象属性保持。
- 没有执行 Office 打开、显示或 UI 编辑验收。字体不嵌入；本机中文预览使用 WenQuanYi Zen Hei 回退，目标 PowerPoint 的字体替换可能影响排版。
- 单图 PPT 保持各自比例；合辑采用统一 4:3 编辑页面并居中容纳各图，不拉伸。默认页面宽 14 in 是 PPT 编辑画布设置，不是论文尺寸限制。

## 复现

在仓库根目录执行，输出目录必须为空或不存在。脚本拒绝覆盖已有产物。

```sh
~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/2026-10-11_native_reconstruction/rebuild.py \
  --out-dir /tmp/native-reconstruction-repeat
```

`--skill` 可指定另一安装位置；`--repo` 可指定仓库位置。PNG 渲染用含 `cairosvg`、`Pillow` 的 Python 环境调用 `render_previews.py --directory <新输出目录>`。当前渲染环境是本机既有 publication-figures 的 Python，仅复用 CairoSVG/Pillow，不应用其排版规则。

本目录的验收命令：

```sh
~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/2026-10-11_native_reconstruction/verify_outputs.py
```

## 图稿列表

| 页 | 图稿 | SVG | PNG | PPTX |
| --- | --- | --- | --- | --- |
| 1 | Cheshire + CVA6 + Ara：AXI Crossbar 的实际结构 | [SVG](crossbar_ara.svg) | [PNG](crossbar_ara.png) | [PPTX](crossbar_ara.pptx) |
| 2 | 参考 DDR Controller V2.1 的多端口接入建议 | [SVG](ddr_qos_proposal.svg) | [PNG](ddr_qos_proposal.png) | [PPTX](ddr_qos_proposal.pptx) |
| 3 | 数据处理与反馈：可编辑矢量示例 | [SVG](example.svg) | [PNG](example.png) | [PPTX](example.pptx) |
| 4 | 启动初始化的软硬件对应关系 | [SVG](initialization_hw_sw.svg) | [PNG](initialization_hw_sw.png) | [PPTX](initialization_hw_sw.pptx) |
| 5 | 从复位到应用返回的程序执行流程 | [SVG](program_execution_flow.svg) | [PNG](program_execution_flow.png) | [PPTX](program_execution_flow.pptx) |
| 6 | Cheshire SoC 软硬件分层结构 | [SVG](cheshire_software_hardware.svg) | [PNG](cheshire_software_hardware.png) | [PPTX](cheshire_software_hardware.pptx) |
| 7 | DDR 互联候选结构：LVDS / ISP 旁路 + 共享 Global Buffer | [SVG](ddr_interconnect.svg) | [PNG](ddr_interconnect.png) | [PPTX](ddr_interconnect.pptx) |
| 8 | LLC 多路组相联 Cache 与按 way 切换 SPM | [SVG](llc_cache_spm.svg) | [PNG](llc_cache_spm.png) | [PPTX](llc_cache_spm.pptx) |
| 9 | 地址路由窗口与物理资源的映射 | [SVG](learning_depth-address-map.svg) | [PNG](learning_depth-address-map.png) | [PPTX](learning_depth-address-map.pptx) |
| 10 | Ara 内部：向量元素分散到 lanes，再重排回内存 | [SVG](learning_depth-ara-internals.svg) | [PNG](learning_depth-ara-internals.png) | [PPTX](learning_depth-ara-internals.pptx) |
| 11 | 当前时钟与事件：SoC 主域、异步入口、FPGA DDR 域 | [SVG](learning_depth-clocks-current.svg) | [PNG](learning_depth-clocks-current.png) | [PPTX](learning_depth-clocks-current.pptx) |
| 12 | 未来 ASIC：时钟、复位、电源分别划分责任 | [SVG](learning_depth-clocks-future.svg) | [PNG](learning_depth-clocks-future.png) | [PPTX](learning_depth-clocks-future.pptx) |
| 13 | CVA6–Ara：控制协议与 AXI 数据通路分离 | [SVG](learning_depth-cva6-ara.svg) | [PNG](learning_depth-cva6-ara.png) | [PPTX](learning_depth-cva6-ara.pptx) |
| 14 | DDR 子系统：AXI 事务、控制器、PHY 与器件引脚 | [SVG](learning_depth-ddr.svg) | [PNG](learning_depth-ddr.png) | [PPTX](learning_depth-ddr.pptx) |
| 15 | 未来 DDR 旁路：数据汇合不等于一致性自动成立 | [SVG](learning_depth-npu-bypass.svg) | [PNG](learning_depth-npu-bypass.png) | [PPTX](learning_depth-npu-bypass.pptx) |
| 16 | 未来异构任务：所有权状态与异常回收 | [SVG](learning_depth-ownership.svg) | [PNG](learning_depth-ownership.png) | [PPTX](learning_depth-ownership.pptx) |
| 17 | 当前共享数据：Ara 的失效协作有明确参与者 | [SVG](learning_depth-shared-current.svg) | [PNG](learning_depth-shared-current.png) | [PPTX](learning_depth-shared-current.pptx) |
| 18 | 未来共享存储：资源位置、访问路径与协议职责 | [SVG](learning_depth-shared-future.svg) | [PNG](learning_depth-shared-future.png) | [PPTX](learning_depth-shared-future.pptx) |
| 19 | Cheshire / CVA6 / Ara：计算、控制与存储边界 | [SVG](learning_depth-system-full.svg) | [PNG](learning_depth-system-full.png) | [PPTX](learning_depth-system-full.pptx) |
| 20 | 向量访存：地址翻译与数据搬运是两条路径 | [SVG](learning_depth-vector-memory.svg) | [PNG](learning_depth-vector-memory.png) | [PPTX](learning_depth-vector-memory.pptx) |
| 21 | AXI Crossbar：7 个发起端、5 个目标与两级译码 | [SVG](learning_depth-xbar-full.svg) | [PNG](learning_depth-xbar-full.png) | [PPTX](learning_depth-xbar-full.pptx) |
| 22 | PLL、分频与门控：时钟生成和事务跨域分别设计 | [SVG](learning_mechanism-clocks.svg) | [PNG](learning_mechanism-clocks.png) | [PPTX](learning_mechanism-clocks.pptx) |
| 23 | CVA6 功能层次：发射、执行、提交与系统接口 | [SVG](learning_mechanism-cva6.svg) | [PNG](learning_mechanism-cva6.png) | [PPTX](learning_mechanism-cva6.pptx) |
| 24 | 一次 DDR 读：请求调度与返回数据分别穿过控制器 | [SVG](learning_mechanism-ddr.svg) | [PNG](learning_mechanism-ddr.png) | [PPTX](learning_mechanism-ddr.pptx) |
| 25 | 关电域与常开域：隔离、保持、电平转换各有职责 | [SVG](learning_mechanism-power.svg) | [PNG](learning_mechanism-power.png) | [PPTX](learning_mechanism-power.pptx) |
| 26 | Crossbar 内部：选择目标、预留 W、归还 ID | [SVG](learning_mechanism-xbar.svg) | [PNG](learning_mechanism-xbar.png) | [PPTX](learning_mechanism-xbar.pptx) |
| 27 | JTAG 直接装载：主机与目标两条时间线如何汇合 | [SVG](learning_new-boot.svg) | [PNG](learning_new-boot.png) | [PPTX](learning_new-boot.pptx) |
| 28 | 主机上的构建产物：每个文件回答不同问题 | [SVG](learning_new-build.svg) | [PNG](learning_new-build.png) | [PPTX](learning_new-build.pptx) |
| 29 | 配置何时生效：源码选择、展开结构与运行状态 | [SVG](learning_new-configuration.svg) | [PNG](learning_new-configuration.png) | [PPTX](learning_new-configuration.pptx) |
| 30 | 一次 UART 寄存器访问：地址、寄存器副作用与引脚 | [SVG](learning_new-device.svg) | [PNG](learning_new-device.png) | [PPTX](learning_new-device.pptx) |
| 31 | 未来图像系统：流数据、帧缓冲与控制路径分层 | [SVG](learning_new-future.svg) | [PNG](learning_new-future.png) | [PPTX](learning_new-future.pptx) |
| 32 | 新增 IP：控制面、主动数据面与完成事件独立定义 | [SVG](learning_new-integration.svg) | [PNG](learning_new-integration.png) | [PPTX](learning_new-integration.pptx) |
| 33 | 外设事件进入 CPU：设备状态、PLIC 与 trap 服务闭环 | [SVG](learning_new-interrupt.svg) | [PNG](learning_new-interrupt.png) | [PPTX](learning_new-interrupt.pptx) |
| 34 | 64 位 AXI 数据拍中的 32 位寄存器访问 | [SVG](learning_new-lanes.svg) | [PNG](learning_new-lanes.png) | [PPTX](learning_new-lanes.pptx) |
| 35 | LLC / SPM：两个别名如何访问同一组 ways | [SVG](learning_new-memory.svg) | [PNG](learning_new-memory.png) | [PPTX](learning_new-memory.pptx) |
| 36 | 缓冲区交接：地址相同还需要所有权与可见性 | [SVG](learning_new-ownership.svg) | [PNG](learning_new-ownership.png) | [PPTX](learning_new-ownership.pptx) |
| 37 | 七篇、30 章：由系统概念进入实现与验证 | [SVG](learning_new-route.svg) | [PNG](learning_new-route.png) | [PPTX](learning_new-route.pptx) |
| 38 | C 对象与运行内存：指令、初值、零初始化与栈 | [SVG](learning_new-runtime.svg) | [PNG](learning_new-runtime.png) | [PPTX](learning_new-runtime.pptx) |
| 39 | I2C EEPROM 与 SPI NOR：控制器动作映射到器件协议 | [SVG](learning_new-serial.svg) | [PNG](learning_new-serial.png) | [PPTX](learning_new-serial.pptx) |
| 40 | 三种访问辨认 SoC：字符输出、数组计算、调试装载 | [SVG](learning_new-system.svg) | [PNG](learning_new-system.png) | [PPTX](learning_new-system.pptx) |
| 41 | AXI 写事务：地址、数据与响应三条独立通道 | [SVG](learning_new-transaction.svg) | [PNG](learning_new-transaction.png) | [PPTX](learning_new-transaction.pptx) |
| 42 | 137 个 e32 元素：按实际 vl 分批执行 | [SVG](learning_new-vector.svg) | [PNG](learning_new-vector.png) | [PPTX](learning_new-vector.pptx) |
| 43 | ASIC 交付边界：数字逻辑消费什么，工艺平台提供什么 | [SVG](learning_teaching-asic-responsibilities.svg) | [PNG](learning_teaching-asic-responsibilities.png) | [PPTX](learning_teaching-asic-responsibilities.pptx) |
| 44 | 从 C 到执行：主机产物如何变成目标内存与 CPU 状态 | [SVG](learning_teaching-code-to-execution.svg) | [PNG](learning_teaching-code-to-execution.png) | [PPTX](learning_teaching-code-to-execution.pptx) |
| 45 | 配置契约：profile、SoC Cfg、软件与运行状态共同约束 | [SVG](learning_teaching-config-contract.svg) | [PNG](learning_teaching-config-contract.png) | [PPTX](learning_teaching-config-contract.pptx) |
