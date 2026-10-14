# L01 / 非易失参数存储方案 PPT 交接

## 修改记录

| 日期 | 对话/角色 | 输入版本 | 修改与验证摘要 |
|---|---|---|---|
| 2026-10-13 | L01 图文作者，root Agent | `bf1b4198dfd74cc78291c152b8b682d523e785c5` / `mp/ara-pulp-v2` | 新增 eMMC/SPI NAND 两页可编辑 PPT、连续连接配图、预览及来源；原生结构和 SVG 预览检查通过 |
| 2026-10-13 | L01 图文作者，root Agent，修订 2 | 同上；工作区另有软件教材未提交修改，原样保留 | 用户要求紧凑汇报版；补充协议、器件候选、eMMC 50 MHz/SPI 100 MHz评估点与PHY/PAD约束；旧稿保留 |

## 当前交付：修订 2

- [新版两页 PPTX](../diagrams/2026-10-13_nonvolatile_storage/revision_02/nonvolatile_storage_options_v2.pptx)取代第一版作为本主题阅读入口；旧文件及其检查记录保留，不覆盖。
- 用户要求提高单页信息密度；本次仍为两页，正文约16–18 pt，统一建议配置、结构图、协议和选型表格、性能比较。配图补齐工艺相关 I/O PAD/收发时序层，连续连接仍采用既定表达。
- 内容更新：eMMC建议1-bit/≤400kHz初始化，8-bit High Speed SDR/50MHz读取；候选Kingston E04GS14DXI 4GB及EMMC08G-WV28 8GB。SPI NAND候选W25N08MW，10MHz初次联调、100MHz Quad SDR条件性评估。以上为建议，用户未冻结料号/频率/IP或采购。
- 源码确认：现有SPI Host SCK由`clk_i/[2×(CLKDIV+1)]`产生；100MHz需输入至少200MHz并满足分频及物理采样条件，不表示当前SoC已有该时钟。没有修改主频、控制器或驱动。
- “纯数字接口不等于仅需RTL”：本版说明PAD及采样要求，区分SDR实现与HS200/HS400常见DLL/延迟线PHY。没有将具体厂商PHY视为必购。
- 新增`build_report_v2.py`与`revision_02/`；更新主题README和本交接，修改前备份见`evidence/before_revision_02/`。未修改共享状态、软件教材或生产源码，无子Agent，未提交。

修订2验证：仓库根执行`/home/zhaowenyao/.codex/skills/publication-figures/.venv/bin/python docs_codex/diagrams/2026-10-13_nonvolatile_storage/build_report_v2.py`退出0。两页88/96个原生对象、5/7个箭头、7个正确的官方超链接；测宽、对象边界、原生媒体检查通过。初稿发现标签列过窄后扩宽；视觉检查修正图标题/总线标签边界及负号字体回退。最终两页均view_image检查，[证据](../diagrams/2026-10-13_nonvolatile_storage/revision_02/visual_review.json)保留PNG哈希；[自动报告](../diagrams/2026-10-13_nonvolatile_storage/revision_02/validation.json)记录完整结果。第一版9项产物哈希保持一致。PNG为同源SVG渲染，Office显示/编辑仍未实测；未编译、未仿真、未板测、未测真实吞吐。

以下保留第一版过程及证据快照，其中“开始时工作区干净”仅描述第一版输入；修订2没有覆盖其他对话的教材修改。

## 基本信息与本轮结果

- 用户明确授权实施两页 PPT 计划，范围仅演示材料及主题交接。已完成文档交付；没有子 Agent。
- 开始时 `git status --short` 无输出。负责路径为 [2026-10-13_nonvolatile_storage](../diagrams/2026-10-13_nonvolatile_storage/README.md)及本文件；未覆盖旧图、源码和共享状态。
- 用户确认（2026-10-13）：约 500 MiB 校正参数开机完整加载 DDR、运行时从 DDR 读取，30 秒加载可接受。
- 建议而非冻结决策：eMMC 4/8 GB 优先评估，SPI NAND 作为吞吐达标后的备选；有效搬运目标 25 MiB/s；A/B 更新、具体器件/主机 IP 未确定。
- 将 30 秒暂按“存储初始化至参数加载并校验完成”预算是本次材料假设，不扩展成系统启动时间验收承诺。

## 交付与改动

- [正式两页 PPTX](../diagrams/2026-10-13_nonvolatile_storage/output/nonvolatile_storage_options.pptx)，含可编辑原生图、正文、比较表、2 个官方超链接及技术备注。
- [说明与复现入口](../diagrams/2026-10-13_nonvolatile_storage/README.md)链接 SVG、PNG、纯配图 PPTX、源码哈希和检查结果；独立复制该图稿目录即可阅读产物，源码链接需仓库。
- 使用 `svg-pptx-diagrams-native` 生成配图，`python-pptx` 组版；未创建或修改 skill。
- 生产 RTL、软件、配置、profile、宏、地址、IRQ、DDR 拓扑和依赖版本变化：无。未提交 Git commit。

## 验证证据

- 仓库根执行：`/home/zhaowenyao/.codex/skills/publication-figures/.venv/bin/python docs_codex/diagrams/2026-10-13_nonvolatile_storage/build.py`，退出 0。临时初稿先在 `/tmp/nonvolatile_storage_draft1` 验证，正式目录未覆盖旧产物。
- [validation.json](../diagrams/2026-10-13_nonvolatile_storage/output/validation.json)：2 页，59/57 个原生对象，5/6 个原生箭头，2 个正确的外部超链接、完整备注；无整图媒体、无越界对象，正文测宽通过。
- [visual_review.json](../diagrams/2026-10-13_nonvolatile_storage/visual_review.json)：两页 PNG 均实际查看，保留最终预览哈希。预览为同源 SVG 渲染，不是 PowerPoint 截图。
- `git diff --stat -- hw sw .bender target` 无输出。未编译、未仿真、未板测；本机没有可用 Office/LibreOffice，Office 显示及交互编辑未实测。未测量存储加载性能。

## 后续最小步骤

1. 用户先用 PPT 讨论两种方案；源材料和依据从图稿 README 进入。
2. 真正选型前确认具体容量、温度/保存年限、更新频率、主机 IP 及可达时钟；本 PPT 不构成采购或集成授权。
3. 硬件接入后测量初始化、完整参数搬运和校验总耗时，验证不可纠错读错误与更新中掉电；没有这些证据不能宣称达到 30 秒。

共享状态与任务表本次不修改；后续协调者需要时可合并上述用户需求与材料入口，不将方案建议写成工程完成状态。
