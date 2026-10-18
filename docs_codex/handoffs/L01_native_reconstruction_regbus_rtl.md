# L01 / Regbus RTL 细节图独立交接

## 修改记录

| 日期 | 角色 / 输入 | 修改与验证摘要 |
| --- | --- | --- |
| 2026-10-12 | L01 Regbus RTL 绘图；`c4162204c` | 交付桥内部与解码/分发两张逻辑图；原生导出及静态检查通过，未封装新 skill |
| 2026-10-12 | L01 A 区教学重绘；`c4162204c` | 用户否定旧图可读性；改用 publication-figures 分离请求字段、三路握手、stream_to_mem 内部与 bank 接口，新增四图及逐问题说明；旧图保留 |
| 2026-10-12 | L01 接入视角收敛；`c4162204c` | 用户要求全 Regbus 限一到两张图；新增全路径与 IP 寄存器封装两图，明确 RegExt 配置/接线/寄存器契约与可直接复用的内部模块 |

## 基本信息

- 用户授权：先生成本次 RTL 分析图片，再根据图片反馈决定是否封装 skill。
- 输入 HEAD：`c4162204cfee0c48b81158b4296860a678d92bec`。使用既有 industrial-svg-pptx / svg-pptx-diagrams-native，无子 Agent。
- 负责文件：新增 `docs_codex/diagrams/2026-10-12_regbus_rtl/` 与本独立交接；未改生产源码、配置、地址、软件或 skill，未提交。
- 并行保护：拟向 `L01_native_reconstruction.md` 追加前，字节比较发现该文件被非教程工业重绘任务更新。本轮没有写入该共享交接；按仓库独立子任务后缀规则创建本文件，由协调者后续合并链接。

## 本轮结果

- [图稿入口、源码依据及静态读写追踪](../diagrams/backup_no_use/2026-10-12_regbus_rtl/README.md)、[两页原生 PPTX](../diagrams/backup_no_use/2026-10-12_regbus_rtl/regbus_rtl_analysis.pptx)。两图分别交付 SVG、PNG、单页 PPTX，并提供生成/验证脚本、源码哈希与报告。
- 桥图按默认 AXI64/Reg32 展开两路、请求弹性缓冲、零写过滤、内部仲裁，放大 periph_to_reg 响应 DFF；解码图展开范围比较/优先选择、valid 门控/payload MUX、34-bit 响应 MUX 及常量错误目标。
- 明确时序缓冲与组合逻辑的区别；使用同名连接点及必要的局部抽象，不称为逐端口完整接线图、综合网表或已仿真时序。
- 保留旧 Regbus 结构图和 SoC 全景图；没有自动封装新技能。

## 验证证据

- `build_figures.py`、native `run.py --aspect source --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`、CairoSVG 2.9.1 渲染、`verify_figures.py` 最终均退出 0；实际 PNG 已查看，修正握手 fork 与数据旁路的区分、过滤响应连接和跨线表达。
- 第一图：212 原生对象 / 105 文本 / 48 箭头；第二图：101 / 53 / 21。单页与合辑文字一致、无栅格媒体，字体度量无文字互相重叠/画布越界，输入源码哈希一致。
- 35 个输入快照存于 `/tmp/regbus_rtl_before.json`；34 个源码/旧图文件保持不变，共享交接的另一任务变更已识别且未覆盖。交付检查见图目录的 `protection_checks.json`。
- 初次共享交接更新脚本在内容一致性检查处主动停止，没有写入；改用本独立交接完成记录。
- Office 显示/编辑未实测，字体未嵌入，连线未绑定模块端口。未编译/仿真/板测；静态事务追踪不是动态验收。

## 下一步

1. 用户评审本轮图片的展开深度、符号和可读性，再决定是否调整图片及封装 skill。
2. 协调者需要时将本交接链接并入原图稿主题交接；不覆盖非教程工业重绘任务内容。
3. 工程事实与主线状态不变，不扩写共享状态页。

## 2026-10-12 用户反馈后的 A 区重绘

- 用户指出旧图混合不同层次、人工标签 P/T/META/RB 不便理解，并明确要求针对 i_axi_to_detailed_mem 四个问题解释和重绘。上文的导出/静态检查通过不代表用户认可旧图可读性；本节作为该部分教学表达的后续版本。
- 新交付：[四图、代码对应和教学例子](../diagrams/2026-10-12_axi_to_detailed_mem/README.md)，含 SVG/PNG/PDF/[四页原生 PPTX](../diagrams/2026-10-12_axi_to_detailed_mem/export/diagrams.pptx)。使用 publication-figures，未创建或修改 skill；没有启动子 Agent。
- 负责文件：新增 `docs_codex/diagrams/2026-10-12_axi_to_detailed_mem/`，更新本主题交接。没有修改前轮图稿、共享项目状态、任务表、生产源码或配置。
- 核实机制：AXI 读写可并发提出请求，二选一来自内部单请求通路；fork 没有 payload 端口，三个分支允许不同周期握手且各恰好一次；meta/sel FIFO 保存返回所需字段和通道选择，非 AW/W 数据对齐缓存；stream_to_mem 请求透传、容量门控、在途计数和无 ready 返回缓冲；bank 接口用真实端口命名。
- 检查：`build_figures.py`、publication-figures `scripts/run.py --width-mm 260 --min-font-pt 9 --render`、`verify_figures.py` 均最终退出 0。四页共 288 原生对象、152 文本对象，保存重读文字一致、无 PPT 栅格媒体；最小字体约 10.1 pt，字体度量检查无文字越界/互相重叠；四张最终 PNG 已实际查看，修正 FIFO 容量格、控制线交叉和缺失减号字形。PDF 为矢量，字体嵌入检查通过。
- 检查脚本首跑仅因 README 链接到尚待本脚本生成的 validation.json 停止；修正自引用检查后通过。输入源码哈希与结果在图目录 validation.json。涉及生产源码的最终 `git diff --stat` 无输出。
- 边界：时钟沿例子来自静态推导，不是仿真波形；未运行 RTL 仿真/综合/板测或 Office。PPTX 端点未绑定、字体未嵌入；源码行为不等于综合网表形状。
- 待办：用户检查本次分视图是否满足电路学习需求；仍由用户决定下一步展开和是否封装 skill。

## 2026-10-12 收敛为两张接入视图

- 最新用户反馈：A 区拆四图太细碎，要求整个 Regbus 用一到两张图，并区分接入自有 IP 的必需知识和可直接使用的模块。因此上节四图作为内部调试参考保留，不再作为接入学习的主入口。
- 新入口：[Regbus 全路径与 IP 接入](../diagrams/2026-10-12_regbus_ip_integration/README.md)。交付两张 SVG/PNG/PDF 与两页原生 PPTX，继续使用 publication-figures，不修改 skill。
- 内容边界：图①依据现有 RTL 表达两级选路、完整桥模块次序、片内/错误/外部端口；新增 IP 显式标记待实现。图②是建议寄存器封装，非既有 IP 电路。说明聚焦当前平台 RegExt 参数、外层接线、寄存器握手/字节使能/偏移、软件表与时钟中断；地址数值未冻结。
- 本地官方路径已对照 docs/um/arch.md、docs/tg/integr.md、register_interface README 及当前源码。RegExt 规则由 gen_axi_out/gen_reg_out 同时生成两级映射；当前 FPGA/仿真顶层未使用外部 Regbus 端口，不能只改参数即认为已接通。
- 保留接口层重要约束：公共路径无自动降频/CDC；START访问完成与长任务完成分开；桥当前窄读可能触及相邻32-bit寄存器，建议无读副作用状态与W1C，实施时需专项测试。无需为普通配置口研究或重写 fork/FIFO/AXI ID 恢复逻辑。
- 修改范围：新增 `docs_codex/diagrams/2026-10-12_regbus_ip_integration/`、更新本交接；无生产源码、配置、原图、共享状态/任务表修改。
- 实际检查：生成、原生导出及 verify_figures.py 最终退出0；两页138原生对象、76文本对象，PPT文字保存重读一致且无媒体图片；字体度量无文字越界或互相重叠；两张最终PNG已查看，PDF字体嵌入/矢量检查通过。首轮导出因空文本被严格拒绝，修正后成功。Office未测试，未进行RTL构建/仿真/板测。
- 后续按用户具体IP规格确定窗口、寄存器表、时钟复位及验收，不因本次绘图而自动实施RTL或封装skill。
