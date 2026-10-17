# L01 / CPU 与 Global Buffer 接入比较

## 修改记录

| 日期 | 角色 / 输入 | 修改与验证摘要 |
|---|---|---|
| 2026-10-17 | L01 第 6 页 F3 样式补修；六页 PPT `0dcb46b4…` / 同 HEAD | 用户指出遗漏并授权修改；仅为 F3↔帧输出 VDMA 增加与 F1/F2 一致的深蓝双向虚线属性，前五页及其余对象不变；最终 PPT 重读预览与局部检查 |
| 2026-10-17 | L01 第 6 页限定样式修复；五页 PPT `3f100763…` / 同 HEAD | 规划后收到“开始实施”；直接复制第 5 页，恢复 ISP/GB、F1/F2、S_EXT/M_EXT 五条虚线并补图例；前五页及主题依赖原字节保留；纠正第 5 页曾将规划误当实施的记录 |
| 2026-10-17 | L01 第 5 页规划与图稿；四页 PPT `24427f14…` / 同 HEAD | 追加第 5 页，F0～F3 及四条下游 DDR 接口双向表达请求/响应；C1～C8 / C9～C16 移到 Regbus 下方两行，与 PLL 底边对齐；复用第 3 页标题并下移主体；前四页及主题依赖原字节保留 |
| 2026-10-17 | L01 第 4 页配置与通道修订；四页 PPT `92c80e25…` / 同 HEAD | 底部统一 C1～C16，删除 Regbus 内重复配置；F3 仅保留 VDMA→F3 AXI 请求接口；分离 AR/AW、W/R 编解码、旁路、元数据及 B 匹配；最终 PPT 重读预览，前三页及主题依赖不变 |
| 2026-10-16 | L01 第 4 页布局与配色纠正；四页 PPT / 同 HEAD | 删除标题栏及外引 IRQ/配置长线，恢复底部 C1～C9/PLL 位置，右侧竖排 ROI/LVDS 输出；67 个原有框继承第 3 页填充；仅 slide4.xml 改变，最终文件重新渲染检查 |
| 2026-10-16 | L01 全景 PPT 第 4 页；当前 M5 三页 PPT / 同 HEAD | 同目录追加 eMMC 内置 DMA、≤256 ROI 裁切与四口共享压缩前端；前三页原字节保留，四页原生 PPT/SVG/PNG 及检查交付；未改 RTL 或正式契约 |
| 2026-10-16 | L01 全景 PPT 第 3 页布局；当前 M5 两页 PPT / 同 HEAD | 按用户要求在同目录追加第 3 页，前两页完整保留；等距排列目标端口，互换 GB 适配下方 M5/ISP 入口，删除两者之间的跳线 |
| 2026-10-16 | L01 全景 PPT 布局纠正；上一版两页 PPT / 同 HEAD | 用户要求下侧新增 M5，保持 GB 子系统上方；第 2 页更新为 M4—M5—M_EXT 和 7×6，保留第 1 页、原输入与上一版 |
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

### 全景 PPT 首版交付（2026-10-16；布局已被下文修正替代）

用户随后明确要求以 `docs_codex/diagrams/soc_landscape.pptx` 的第 1 页复制出第 2 页，再修改 Ara/GB 互联。本轮新增 [SoC 全景图目录](../diagrams/2026-10-16_soc_landscape_shared_gb/README.md)，只更新本 handoff，不改正式分析和其他对话文件。输入 SHA-256 `ec43b6e1b645ff379865d518ac3b20dc32c078c02bca1eca52428a49cca4db4b`，原 PPT 与本交接修改前版本均备份。

输出第 1 页 XML/依赖完整保留；第 2 页删除地址分流及 Ara 独立 GB 线，保留 CPU S0、Ara S2，新增连续 `M_GB→GB 访问适配` 路径，标注 Ara2/AXI64，清除 ISP 线在旧 Ara 分支处已失去用途的跳线。新图 368 个原对象未变；仅删除 7、修改 9、新增 6 个原生对象。

实际 `edit_deck.py …/build-02`、`preview_deck.py …/preview-03`、`validate.py` 最终退出 0；[验证报告](../diagrams/2026-10-16_soc_landscape_shared_gb/evidence/validation.json)记录两页、原文件/原页保护、关系检查、原生文本/箭头/虚线保存重读及新增路径端点和避字。两次先前检查失败是 M_GB 端点附近的字形/平头线帽边界计算问题，修正检查后通过；没有据此修改或删减图形内容，迭代记录保留。

作者实际查看原页与最终第 2 页的本地 SVG 渲染。无连接的 Office 会话，Office 显示/编辑未实测，配套预览不冒充 PowerPoint 截图。最小后续检查是用户在目标 Office 打开两页核对字体和编辑行为；不扩展为硬件实施。

### 全景 PPT 布局纠正（2026-10-16；保留为第 2 页）

用户明确指出首版上侧 `M_GB` 违背“上侧发起端、下侧目标端”的图形约定，且端口计数未正确更新；要求在 M4 与 M_EXT 之间增加 M5，将计数改为 7×6。用户随后确认 GB 子系统保留上方位置，下侧新增其 AXI 接口框。本次按该计划实施，不再采用首版的上侧出口布局和 7×5 标签；首版证据保留为历史。

输入是上一版两页 `soc_landscape_shared_gb.pptx`，SHA-256 `9080ab142e19910ba0d2bc50298d9fb66800aeceefec28bb7382e6250e73f8a0`。新增 [M5 修正图稿目录](../diagrams/2026-10-16_soc_landscape_m5_gb/README.md)，仅更新本稳定 handoff，正式分析、共享状态与其他对话文档保持不变；本交接修改前版本已备份。

交付仍为两页原生 PPTX 及 SVG/PNG：第 1 页和所有依赖部件原样保留，仅第 2 页 XML 改变。移除上侧出口，局部重排下侧 M4/M5/M_EXT；M5 向下接 GB AXI 接口，再沿 Crossbar 外侧连续回到上方现有 GB 访问适配器。CPU S0、Ara S2、Ara2/AXI64、NPU/ISP/搬运与 DDR 关系保留；GB SRAM 没有重复实例。

实际 `build.py …/build-01`、`preview_deck.py …/preview-01` 退出 0。`validate.py` 前两次因检查器混入 DDR 同名端口及侧边标签而退出 1，收紧到主 Crossbar 边界后退出 0，图稿内容未因此改变。[最终报告](../diagrams/2026-10-16_soc_landscape_m5_gb/evidence/validation.json)确认下侧 M0～M5/M_EXT 顺序、7×6 标签、端点/避让、文字/原生箭头保存重读及 50 个既有文件保护；第 2 页 365 个原对象不变，最终 386 对象、196 文本、71 原生箭头。

作者已查看两页和 M5/回接路径局部预览。Office 显示/编辑未实测，没有 RTL/配置变更或硬件验证；后续仅需在目标 Office 核对字体与编辑显示。7×6 是图中的规划拓扑计数，不是当前生产 RTL 已增加目标端口的声明。

### 全景 PPT 第 3 页布局优化（2026-10-16；保留为第 3 页）

用户要求保留前两页，在当前 `2026-10-16_soc_landscape_m5_gb/` 目录追加第 3 页，不另建图稿目录。输入两页 PPT 的 SHA-256 为 `3aeb085a47c843dbaa101d5e4dc85abb8b52d15c135402468c0cdb0b13608a57`；修改前 PPT、README、本交接已备份到该目录 `evidence/page3-before/`。负责范围仅当前图稿目录及本稳定 handoff，未改变正式分析、共享状态、源码或配置。

[三页 PPT 与预览](../diagrams/2026-10-16_soc_landscape_m5_gb/README.md)的第 3 页将下侧 M0～M5、M_EXT 等距排列，目标框随端口居中；保留全部文字与字号，并同步调整 Regbus 下接线及 LLC→DDR 起点。GB 适配器下方改为左侧 M5、右侧 ISP，删除这两条线之间的跳线，保留各自与 M_EXT/DDR 旁路线交叉所需的跳线。CPU/Ara 独立输入、Ara2/AXI64、单个 GB SRAM 及其他连接关系保持。

`append_uniform_page.py …/page3-build-02`、`preview_deck.py …/page3-preview-01`、`validate_page3.py` 最终退出 0；实际命令见图稿 README。[检查报告](../diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page3-validation.json)确认第 1、2 页及全部依赖原字节保留，预览也相同；第 3 页沿用 386 对象，其中 331 个未改，196 文本、71 原生箭头、26 原生虚线对象保留。端口间距、框内文字、连线避让、包关系与保存重读检查通过，32 个受保护既有文件未改。

第一次检查因原始导入坐标相对设计坐标约 0.005 px 的差异失败，将端点/边界比较容差改为 0.01 px 后通过；等距误差要求仍为 0.001 px，图稿未因此改动。`page3-build-02` 相比 `page3-build-01` 只更新新增备注页的页码域，三页绘图 XML 相同。作者已实际查看整页及两个修改区局部预览。Office 显示/编辑未实测；最小下一步仍是在目标 Office 打开检查字体和编辑显示，不扩展为硬件实施。

### 全景 PPT 第 4 页系统扩展（2026-10-16；初版，布局已由下文替代）

用户确认 eMMC Host 内置 DMA、每帧至多 256 个矩形 ROI 纯裁切，以及按地址区域启用、保留普通旁路的四口共享无损压缩/解压；前端位于采购 DDR Controller 外部。本轮仅实施图稿和配套说明，不授权硬件实施，也不冻结 IP、地址、IRQ、容量、速率或算法。

输入为当前三页 `soc_landscape_m5_gb.pptx`，SHA-256 `8522fffd3d4b36412d72da427866e59ebe67252b497913d9cd8298ed1a2bdeeb`，HEAD/分支仍为上述基线。修改前 PPT、README 和本交接已备份至原图稿目录 `evidence/page4-before/`；负责文件仅该目录的主 PPT、README、新增第 4 页 SVG/PNG、生成/检查脚本及证据，以及本 handoff。未新建图稿目录。

[四页交付与接口说明](../diagrams/2026-10-16_soc_landscape_m5_gb/README.md)保留前三页，复制第 3 页框架并重排第 4 页。新增 eMMC→Host/DMA→S7→M5→GB、ROI 调度→单个二维读 VDMA→FIFO→LVDS TX，以及四个独立 F0～F3→DDR S0～S3 通路。Crossbar 改为 8×6 固定端口加扩展；上下端口等距，Ara2/AXI64、CPU/Ara 独立输入及单个 GB 保持。前端内部压缩器和解压器分别绘制，普通旁路和元数据管理可见；新增 C10～C12 配置与独立 IRQ 向量连续接入 RegExt/外部 IRQ/PLIC。详细条件及后续硬件验证只写入图稿 README，不复制成另一份工程契约。

实际 `build_page4.py …/page4-build-04`、`preview_deck.py …/page4-preview-04`、CairoSVG 渲染及 `validate_page4.py` 最终退出 0，完整命令见 README。[检查报告](../diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page4-validation.json)确认前三页 XML/关系/备注/共享依赖、原 SVG/PNG 均保持原字节；第 4 页 461 个原生对象、192 个文本、96 个原生箭头、16 个虚线对象，112 条路径连续且端点正确，51 处显式跳线。文字边界/重叠、连线避让、S7/M5、四口映射、包关系与保存重读检查通过，66 个受保护文件未改。[交付检查](../diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page4-delivery.json)记录发布文件及链接/保护核对。

首版局部检查发现 ROI/压缩模块文字偏上与 PHY 标记重叠，第二版修正；第三版明确“四口共享”和“独立 IRQ 向量”语义；最终版修正 Regbus 首列分支 2 px 边界差异。先前证据保留，不冒充已通过结果。作者实际查看最终整页及 eMMC/ROI、压缩/DDR、Regbus/IRQ、GB 入口局部。Office 显示/编辑未实测；没有 RTL 编译、仿真、板测或吞吐验证。

跨对话待同步：当前正式 DDR 文档仍有三口快照，本页第四口及 eMMC/ROI/压缩需求由协调者后续对照用户决定汇总；本轮未修改这些契约、`PROJECT_STATE.md` 或任务表。最小后续动作是在目标 Office 核对字体/编辑显示；若另行进入硬件设计，再按 README 落实区域格式、元数据更新、部分写/跨块、四口可见性、缓存维护、帧/参数所有权与错误排空，不把本交接当作实施授权。

### 第 4 页布局与配色纠正（2026-10-16；历史交付，配置与通道表达由下节替代）

用户指出初版的配置/IRQ 长线杂乱、PLL/扩展寄存器位置改变、LVDS 对端表达不对称及继承模块配色变化。本轮按反馈修订同一主 PPT 的第 4 页：去掉标题栏；C1～C9 扩展寄存器和 PLL 框恢复第 3 页原位置；新增 C10～C12 配置集中在 Regbus；删除红色 IRQ 及向远端 IP 引出的配置长线；Regbus 与压缩前端靠近，右侧竖排 ROI→VDMA→FIFO→LVDS TX；统一省略 LVDS 片外发送端和接收端。中断和配置硬件需求并未取消，仅简化绘图。

输入 SHA-256 `4574947a4d716530021dd0735c6affdfe525202dd82ee246ae8e4ea2a5d51c98`；输出 `92c80e25bc9bb5d444dfa3269997e1b0c78168885ac4d627fd92e9cebaa9dc8b`。负责范围仍为原 `2026-10-16_soc_landscape_m5_gb/` 图稿目录和本 handoff；旧主 PPT、第 4 页 SVG/PNG、README 与本交接均备份至 `evidence/page4-layout-before/`。未修改 RTL、工程契约、共享状态或其他对话文件。

配色缺陷证据：第 3 页 Crossbar 填充为 `accent1` 加 `lumMod=20000/lumOff=80000`，旧预览器遗漏亮度变换，初版重绘误把深色固定写入第 4 页；两个外部扩展框亦未继承原填充。当前 67 个既有框/分区直接复用第 3 页填充定义；Crossbar 解析为 `#DAE3F3`，S_EXT/M_EXT 外部模块为 `#F5F5F7`。输出包只修改 `ppt/slides/slide4.xml`，前三页及全部主题/母版/布局/关系部件原字节保留。原 slide-01～03 SVG/PNG 不覆盖；修正颜色解析后的第 3 页预览放新 evidence 中用于对照。

`revise_page4_layout.py …/page4-layout-build-03`、`preview_deck_colours.py`、`validate_page4_layout.py` 最终退出 0；[README](../diagrams/2026-10-16_soc_landscape_m5_gb/README.md)记录命令、颜色说明和接口边界。[当前检查](../diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page4-layout-validation.json)确认填充一致、C1～C9/PLL 位置、等距端口、S7/M5、四口 DDR、单个 GB、竖向链及配置目标位置。第 4 页 487 个原生对象、222 文本、91 原生箭头、25 虚线对象；108 条连续路径、11 处跳线，文字/端点/避让/关系/保存重读检查通过。构建 01 因 C 标记重复 SVG ID 退出 1，构建 02 修正后通过布局检查；构建 03 进一步去除底部配置线重叠并对齐端点。

发布后从最终主 PPT 重新生成预览，与检查版本 SVG/PNG 字节一致；作者实际查看最终整页、存储/ROI、扩展/PLL、Crossbar 及 Regbus 局部。[最终交付检查](../diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page4-layout-delivery.json)记录哈希、144 个既有文件保护及文档链接核对。Office 应用显示/编辑仍未实测；没有硬件测试。后续只需按目标 Office 显示检查字体，不据本次修图推进硬件实施。

### 第 4 页配置与通道修订（2026-10-17；历史交付，第 4 页继续保留）

用户明确授权仅修订现有主 PPT 第 4 页，使用 `industrial-svg-pptx`，同目录先备份，不修改前三页、主题、母版、布局、RTL 或其他契约。输入 HEAD 仍为 `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`，分支 `mp/ara-pulp-v2`；PPT 输入 SHA-256 `92c80e25bc9bb5d444dfa3269997e1b0c78168885ac4d627fd92e9cebaa9dc8b`，输出 `24427f14665215fbef05494c4b28175ea2222c73631fd23267ca5a687dc0b890`。主 PPT、第 4 页 SVG/PNG、README 与本交接修改前内容已备份至原图稿目录 `evidence/page4-controls-before/`。

负责文件为 `diagrams/2026-10-16_soc_landscape_m5_gb/` 下主 PPT、`slide-04.svg/png`、README、新增 `revise_page4_controls.py` / `validate_page4_controls.py` 及本轮 evidence，以及本稳定 handoff。C1～C9 含义/顺序保留；C10 eMMC、C11 ROI、C12 前端公共控制、C13 输出 VDMA、C14 LVDS TX、C15 压缩器、C16 解压器统一在底部 RegExt 主线下，各自匹配模块 C 标识。Regbus 内旧 C10～C12 汇总框删除，不增加远端配置长线或红色 IRQ 线。配置组不冻结地址或寄存器文件数量。

F3 外部只保留深蓝 VDMA→F3 请求接口；R 响应沿原接口返回，绿色限定 GB 局部读写。前端重排为公共四口适配、独立 AR/AW 地址/事务路径、共享 W 压缩/R 解压/普通数据旁路、元数据管理及下游 R/B 响应匹配；B 独立返回，不通过编解码器。四个独立下游接口标为 DDR.S0～DDR.S3，与主 Crossbar S 口区分。PLL、CPU/Ara、S7/M5、单个 GB、RAW/ISP 选择、四路 DDR 及右侧 ROI 纵向链保留。完整接口条件和 C1～C16 参数归属只写入[图稿 README](../diagrams/2026-10-16_soc_landscape_m5_gb/README.md)。

最终 `revise_page4_controls.py …/page4-controls-build-04`、`preview_deck_colours.py`、`validate_page4_controls.py …/page4-controls-validation-final.json` 均退出 0，命令见 README。[最终检查](../diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page4-controls-validation-final.json)确认仅 `ppt/slides/slide4.xml` 改变，其他包部件原字节保留；67 个继承框填充与第 3 页一致，203 个受保护文件及备份未变。4 页、541 个第 4 页原生对象、240 文本、98 原生箭头、29 虚线对象；114 条连续路径、9 处显式跳线，文字/框/端点/关系/保存重读检查通过。

初次预览误用系统 Python，缺少 Pillow，改用既有 skill 环境。构建 01 发现 F 端口文字贴边，02 修正；实际查看整页和局部后发现 C 标识框压到标题，03 增加留白并补充框/文字交叠检查，04 再修正旧 eMMC/PHY 说明贴住 C10/C3 框。中间通过的报告只对应当时检查范围，未充作最终验收。最终发布后从主 PPT 重新生成 `evidence/page4-controls-final-preview-04/`，作者实际查看整页、存储/ROI、配置行、PLL、Crossbar、Regbus、GB/图像输入局部，并沿 eMMC 加载、帧写与 ROI 读三个场景复核方向和共享关系。[交付检查](../diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page4-controls-delivery.json)记录最终哈希、文件保护、链接和检查范围。

Office 显示/编辑未实测；预览为原生 DrawingML 解析与本地替代字体渲染，非 Office 截图。未运行硬件编译、仿真、板测或性能验证，未修改工程契约和共享状态。后续如需继续，最小动作是在目标 Office 核对字体/编辑显示；硬件接口、寄存器、IRQ、压缩格式和服务保证仍须另行设计验证，本记录不授权实施。

### 第 5 页：双向接口与两行配置（2026-10-17；历史交付）

**2026-10-17 授权范围纠正：**用户随后明确指出本轮只要求规划，Agent 却实施了第 5 页，且遗漏了应继承的虚线样式。下段是当时记录，不能作为本轮已获实施授权的依据；保留原文件与原验证证据。第 6 页已先只读规划，直到用户明确“开始实施”才执行。

用户要求规划修改并创建第 5 页。本轮先说明单箭头“请求方向”与双箭头“请求/响应”的区别及两行布局方案，再实施同目录追加页。输入仍为 `mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`；四页 PPT SHA-256 `24427f14665215fbef05494c4b28175ea2222c73631fd23267ca5a687dc0b890`，五页输出 `3f100763d6bd76966b2e7b9ee6773735e716aebfd349a6034f444f842d4a8887`。主 PPT、README、第 4 页 SVG/PNG、本交接已备份到原目录 `evidence/page5-before/`。

负责文件仅原 `2026-10-16_soc_landscape_m5_gb/` 的主 PPT、README、新增第 5 页 SVG/PNG、生成/检查脚本及证据，以及本 handoff。前四页 XML/关系/备注及已有 SVG/PNG 保留；不修改 RTL、地址配置、正式契约或共享状态。配置组数量与含义不变：C1～C8 第一行、C9～C16 第二行，位于 Regbus 下方，两行并列挂接同一 RegExt 主干，第二行底边与 PLL 框底边对齐。Regbus 内只压紧空隙，保留文字尺寸；主体整体下移约 158.095 设计单位，第 3 页标题两个原生对象完整复制，主题、母版、布局不变。

F0～F3 外部接口及前端→DDR.S0～DDR.S3 共八条连接改为原生双端箭头。F2 返回方向表示写响应 B，F3 返回方向表示读数据 R，不能据此增加 DMA 读写能力或改变主从角色；内部 AR/AW、W 压缩、R 解压、B 响应匹配方向保留。既有 Crossbar 单箭头仍只画请求，新增双/单箭头图例明确区别。CPU/Ara、S7/M5、单个 GB、RAW/ISP 选择和竖向 ROI 输出链保持。[README](../diagrams/2026-10-16_soc_landscape_m5_gb/README.md)记录规划、具体变化及语义边界。

`build_page5.py …/page5-build-02`、`preview_deck_colours.py …/page5-preview-02`、`validate_page5.py …/page5-validation.json` 退出 0。构建 01 常规检查通过，实际局部预览发现下游短接口双箭头太近，02 上移前端返回路由并整理元数据框留白后通过。[检查报告](../diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page5-validation.json)确认前四页及依赖不变，329 个受保护文件未改；新增第 5 页 547 个原生对象、242 文本、99 原生箭头、29 虚线对象、116 条连续路径，端点/文字/标识框/原配色与字号/关系/保存重读检查通过。

发布后从最终主 PPT 重新生成 `evidence/page5-final-preview/`，实际查看整页及配置行、PLL 对齐、存储/ROI 局部，确认双向接口与内部定向通道未混淆。[交付检查](../diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page5-delivery.json)记录最终文件哈希、前四页/备份保护与文档链接。Office 显示/编辑未实测；无硬件测试。最小后续动作仍是目标 Office 显示/编辑核对，不因图稿完成推进 RTL 或接口选型。

### 第 6 页：恢复虚线并保留第 5 页布局（2026-10-17；首版，F3 已由下文补修）

任务 L01，输入 `mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`。用户先要求第 6 页规划，随后明确“开始实施”。负责文件限既有 `diagrams/2026-10-16_soc_landscape_m5_gb/` 的主 PPT、README、新增 `slide-06.svg/png`、第 6 页生成/检查脚本及 evidence，以及本 handoff。修改前主 PPT、README、第 5 页 SVG/PNG、本交接备份至 `evidence/page6-before/`；未改 RTL、地址配置、驱动、正式工程契约或共享状态。

五页输入 SHA-256 `3f100763d6bd76966b2e7b9ee6773735e716aebfd349a6034f444f842d4a8887`，六页输出 `0dcb46b4fdce907ff32e75ca59d932b414ec053d3b07c5e2abe5dd1386f9cdf9`。直接复制第 5 页原生对象：ISP↔GB、搬运器↔F1、帧写入 DMA↔F2 恢复原第 4 页备份的虚线参数；S_EXT/M_EXT 恢复第 3 页外部扩展的灰色虚线。保持第 5 页双/单箭头、线宽与几何，不恢复旧 DDR 拓扑。仅图例新增虚线样例并调整内部留白；标题、C1～C16 两行、PLL 对齐、填充/字号和其余连接完全保留。详细边界与样式来源见[README 第 6 页](../diagrams/2026-10-16_soc_landscape_m5_gb/README.md)。

`build_page6.py …/page6-build-02`、`preview_deck_colours.py …/page6-preview-02`、`validate_page6.py …/page6-validation-final.json` 均退出 0。[最终检查](../diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page6-validation-final.json)确认前五页及依赖原字节保留、391 个受保护文件未变；新页 528 个继承对象完全不变，改动仅五条线及 14 个图例对象，新增两个图例对象。最终 549 个原生对象、243 文本、100 箭头、35 虚线对象；保存重读、包关系、线端点、方向、文字和线框避让通过。构建 01 已通过结构检查，实际预览发现图例说明被 F2 走线分隔，02 仅整理图例间距。

发布后从最终主 PPT 生成 `evidence/page6-final-preview/`，实际检查整页、GB/ISP、扩展口与图例、存储/ROI、配置/PLL 局部，确认原有方向及共享通路未改变；[交付检查](../diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page6-delivery.json)记录最终哈希、保护和预览范围。Office 显示/编辑未实测，无硬件测试。最小后续为目标 Office 字体/显示/编辑核对；本次不授权继续硬件实现或扩大改图范围。

### 第 6 页 F3 样式补修（2026-10-17；当前交付）

用户指出 LVDS TX 输出链遗漏，核查确认 F3↔帧输出 VDMA 仍为实线；随后明确“实施修改”。此前首版检查仅覆盖五条连线和几何保护，没有充分检查新增同类通路的样式一致性；旧报告保留为历史证据，不作为 F3 样式正确的证明。

输入分支/HEAD 不变，六页主 PPT 输入 `0dcb46b4fdce907ff32e75ca59d932b414ec053d3b07c5e2abe5dd1386f9cdf9`，补修输出 `7330221874eb045d9fd2511a834d64c6ba45b98e5c7fb7014c67dee088277f31`。先备份主 PPT、README、slide-06.svg/png、本交接到同目录 `evidence/page6-f3-before/`。负责范围仅上述图稿/说明/本交接、新增 `fix_page6_f3.py` 及本次 evidence；不加页，不改 RTL、地址、工程契约或共享状态。

只为 `roi-f3-request` 增加与 F1/F2 完全相同的原生虚线参数。去掉新增的 `a:custDash` 后，整页与输入完全一致；PPT 包只有 `ppt/slides/slide6.xml` 改变，前五页、依赖、端点、路径、双箭头、颜色、字号、框边和布局不变。图像裁切输出的外层虚线及内部实线功能框继续保留。

`fix_page6_f3.py` 和最终主 PPT 的 `preview_deck_colours.py` 均退出 0；[原生差异与保存重读](../diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page6-f3-build/native-check.json)通过。实际查看最终整页与存储/ROI 局部，F1/F2/F3 同为深蓝双向虚线；SVG 也仅 F3 路径增加虚线属性。最终保护/哈希/预览记录见[交付检查](../diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page6-f3-delivery.json)，复现与当前边界见[README](../diagrams/2026-10-16_soc_landscape_m5_gb/README.md)。Office 显示/编辑未实测，无硬件测试。最小后续仍为目标 Office 核对，本记录不授权其他修改。

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
