# L01 / CPU 与 Global Buffer 接入比较

## 修改记录

| 日期 | 角色 / 输入 | 修改与验证摘要 |
|---|---|---|
| 2026-10-16 | L01 全景 PPT 修订；用户 `soc_landscape.pptx` / 同 HEAD | 保留原页并复制为第 2 页，定向改为共享 GB 出口；交付独立两页原生 PPTX 与配套 SVG/PNG，原输入未覆盖 |
| 2026-10-16 | L01 架构决策与图稿作者；同分支/HEAD | 用户选定 Ara2 / CPU 与 Ara 共享主 Xbar64 的 GB 目标出口；更新正式文档，新增单图 SVG/PNG/原生 PPTX，保留旧图及修改前备份；未改生产代码 |
| 2026-10-15 | L01 分析与图稿作者；`mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8` | 按用户确认计划及追加 Markdown 要求，交付正式分析和两张工业风格 SVG/PNG、两页原生 PPTX；仅文档与图稿 |

## 当前结果：2026-10-16 已确认拓扑

- 用户选择 CPU 接入 GB，Ara 保持 2 lanes，并取消规划中的 Ara 独立 GB 分流。CPU/Ara 保留独立 Xbar 输入，共用一个 64-bit GB 目标出口。本选择替代下文历史记录的“CPU 未定 / Ara 独立支路”，不冻结 GB 容量、地址、频率或仲裁。
- [正式文档](../engineering/Global_Buffer_CPU_Access.md)新增当前方案、收益/竞争与跨文档同步边界；[新图稿与复现](../diagrams/2026-10-16_global_buffer_shared_xbar/README.md)交付一张已选拓扑，旧两图完整保留。
- 源码确认 `AraDataWideWidth = 32 * Cfg.AraNrLanes`，默认与 VCU118 加源脚本为 2 lanes；当前 `filter→axi_dw_converter→axi_in_req[AxiIn.ara]` 可复用。AXI `gen_no_dw_conversion` 在 64→64 时直接透传，无需为省转换删除实例。未改变 VLEN 或 profile。
- 2-lane/64-bit 接口匹配已确认，负载是否够用仍待测；CPU/Ara 同 GB 目标共享出口吞吐，不把主 Xbar 描述为全部目标串行，也不承诺两个独享 64-bit GB 口。
- 负责修改仅正式文档、本稳定 handoff，以及 `diagrams/2026-10-16_global_buffer_shared_xbar/`。输入与旧文件备份见[快照](../diagrams/2026-10-16_global_buffer_shared_xbar/evidence/input.json)。无生产 RTL/sw、依赖、FPGA 工程和共享状态修改。

### 本次验证

具体命令见新图稿 README。`build_figures.py …/source-01` 成功；`render-01` 因 Chrome 本地 socket 的沙箱限制退出 1。经环境审批的 `render-02` 生成预览，但 GB 适配框副标题溢出，布局检查退出 1。缩短文字后 `source-02`、`render-03` 退出 0，作者实际查看 PNG，无文字遮挡或越界。原生后端导出退出 0，1 页、60 文本、23 原生箭头；保存重读与文档/拓扑检查见[最终报告](../diagrams/2026-10-16_global_buffer_shared_xbar/evidence/validation.json)。

验证保护 42 个既有文件（含旧图稿全部文件及其他对话文档）与 6 个源码输入，核对修改前备份、图形端点、连续路径、独立输入/共享出口、文本/箭头、链接及 `git diff --check`。Office 显示/编辑未实测；未运行软件/RTL 或板测，未验证吞吐/有界服务。

### 协调同步与最小下一步

1. M01/协调者将契约 §12 的“Ara4/宽侧分流候选、CPU 待定”更新为本次近期选择，保留原始输入和 DDR 需求；不将 4-lane 宽支路候选当作当前要求。
2. 软件接口导航仍有 CPU 待定描述，应从 HTML 内容源同步生成页；本轮不单独改 `integration.md`。DDR–GB 同步设计/一致性图的 Ara 独立分支亦待所属对话同步，不改变其已确认的范围维护/握手/DDR 端口职责。
3. `PROJECT_STATE.md`、`AGENT_TASKS.md` 及工程索引已有其他对话未提交修改，本轮保持原样，由协调者汇总该拓扑决策和新图稿入口。
4. 后续实施需明确 GB 窗口及缓存/权限、扩展 ID、字节写、原子拒绝行为和服务界限。最小验证覆盖 CPU/Ara 同 GB 目标与不同目标并发、NPU/搬运器竞争、响应/顺序/错误闭环，并测量端到端后处理性能。既有 Ara B 错误与 iDMA 控制缺口未关闭。

### 全景 PPT 增量交付（2026-10-16）

用户随后明确要求以 `docs_codex/diagrams/soc_landscape.pptx` 的第 1 页复制出第 2 页，再修改 Ara/GB 互联。本轮新增 [SoC 全景图目录](../diagrams/2026-10-16_soc_landscape_shared_gb/README.md)，只更新本 handoff，不改正式分析和其他对话文件。输入 SHA-256 `ec43b6e1b645ff379865d518ac3b20dc32c078c02bca1eca52428a49cca4db4b`，原 PPT 与本交接修改前版本均备份。

输出第 1 页 XML/依赖完整保留；第 2 页删除地址分流及 Ara 独立 GB 线，保留 CPU S0、Ara S2，新增连续 `M_GB→GB 访问适配` 路径，标注 Ara2/AXI64，清除 ISP 线在旧 Ara 分支处已失去用途的跳线。新图 368 个原对象未变；仅删除 7、修改 9、新增 6 个原生对象。

实际 `edit_deck.py …/build-02`、`preview_deck.py …/preview-03`、`validate.py` 最终退出 0；[验证报告](../diagrams/2026-10-16_soc_landscape_shared_gb/evidence/validation.json)记录两页、原文件/原页保护、关系检查、原生文本/箭头/虚线保存重读及新增路径端点和避字。两次先前检查失败是 M_GB 端点附近的字形/平头线帽边界计算问题，修正检查后通过；没有据此修改或删减图形内容，迭代记录保留。

作者实际查看原页与最终第 2 页的本地 SVG 渲染。无连接的 Office 会话，Office 显示/编辑未实测，配套预览不冒充 PowerPoint 截图。最小后续检查是用户在目标 Office 打开两页核对字体和编辑行为；不扩展为硬件实施。

## 历史记录：2026-10-15 结果与负责范围

以下保留当时输入、命令、验证及待办；其中 CPU 是否接入和 Ara 独立支路选择已由上述 2026-10-16 决策取代。旧验证报告对应旧文档快照，不能用来证明当前正文。

- 正式内容：[CPU 接入 GB](../engineering/Global_Buffer_CPU_Access.md)；[图稿与复现](../diagrams/2026-10-15_global_buffer_cpu_access/README.md)。状态：文档与图稿交付完成，硬件方案未冻结、未实施、未验证。
- 用户选择的分析输入是“小结果、灵活处理”；建议保留 64-bit 主机入口，反复排序时复制到 CPU 私有工作区。此建议不是用户已经冻结 CPU 接入的决定。
- 用户本轮追加明确要求独立 Markdown；因此新增正式工程参考页。原 `integration.md`、现行 IP/DDR 契约、已有一致性文档及图稿均未修改。
- 本轮只新增上述正式文档、`diagrams/2026-10-15_global_buffer_cpu_access/` 和本交接。生产 RTL/sw、地址、IRQ、profile、清单、依赖和 FPGA 工程无改动；未提交 Git。
- 工作区原有工程索引、软件接口交接修改，以及软件栈/一致性图稿和文档等未跟踪文件全部保护；[输入快照](../diagrams/2026-10-15_global_buffer_cpu_access/evidence/input.json)记录初始状态和哈希。

### 2026-10-15 依据与验证

源码核对沿主 Xbar 外部从设备、Ara filter→converter、LLC 前原子适配、CVA6 PMA 消费链进行。依赖源标识为 Ara `2895ba90`、CVA6 `99eac9a6`、AXI `39f5f2d5`，本地文件哈希才是此次实际输入。官方资料和具体源码入口见正式文档，不重复复制论证。

工作目录为仓库根。实际生成、渲染、导出命令完整保存在图稿 README，检查入口及结果如下：

- `build_figures.py --out-dir …/evidence/source-01` 退出 0；初次 `render.py …/render-01` 退出 1，Chrome 本地 socket 受沙箱限制，日志保留。
- 经环境审批执行本地 Chrome 到 `render-02`，布局检查退出 1，发现 NPU→GB 连线穿过分区标题；没有把该批次标为通过。
- 定向修正后 `build_figures.py …/source-02`、`render.py …/render-03` 均退出 0；逐张实际查看两张 PNG，无文本越界、遮挡、连线穿字或端点悬空。
- 原生后端 `run.py --input cpu-isolated.svg cpu-accessible.svg --out-dir export --aspect source`（完整字体选项见 README）退出 0；两页、125 文本、48 原生箭头，保存重读通过。
- `validate.py --out-file …/evidence/validation.json` 的最终结果见[验证报告](../diagrams/2026-10-15_global_buffer_cpu_access/evidence/validation.json)：链接、图形连接、两方案公共布局、PPTX 对象、67 个既有文件及 15 个输入保护；`git diff --check` 一并检查。

Office 显示/编辑未实测，原生箭头未绑定模块端口；不承诺拖动模块自动重连。未执行目标软件/RTL 编译、展开、仿真、综合、板测或 ASIC 验收。

### 2026-10-15 当时未关闭项与下一步

1. 用户/M01/I01 评审 CPU 是否接入，再提供候选表规模、GB 组织和接口、地址与仲裁目标；图稿不冻结容量、频率或 SRAM 端口。
2. S01/V01 按正式文档比较 Ara→SPM 与 CPU 直访/私有复制，验证所有权、错误、迟到写和并发干扰；Ara B 错误与 iDMA 控制接口缺口保持开放。
3. GB 非缓存直访与 DDR 旁路一致性分别评审；不把另一对话的硬件一致性建议视为已实现能力。

共享状态、任务表和已有未提交工程索引本轮保持不动，没有工程实现状态变化。若协调者汇总导航，可增加正式文档入口；本交接已保存本次文档进展和输入身份。
