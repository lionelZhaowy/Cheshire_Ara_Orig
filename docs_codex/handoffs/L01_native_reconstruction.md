# L01 / 原版图稿集中重建为原生 PPT 对象

> 记录日期：2026-10-11。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 修改记录

| 日期 | 角色 / 输入 | 修改与验证摘要 |
| --- | --- | --- |
| 2026-10-12 | L01 skill 归档与风格选择；`c4162204c` | 按用户要求归档并移除非 native skill 及发现链接；1820 项清单核对一致，native 工业模板导出通过；细化硬件互连与软硬件分层图的不同风格偏好 |
| 2026-10-12 | L01 非教程图工业重绘；`c4162204c` | `industrial-svg-pptx` 批量应用，交付 9 图及 9 页合辑；37 张教程图不重绘，182 个既有文件保护核对通过 |
| 2026-10-12 | L01 Regbus 图稿；`c4162204c` | 根据当前 RTL 新增公共 Regbus 工业风格结构图，SVG/PNG/原生 PPTX 交付；源码与图稿静态检查通过，Office 未实测 |
| 2026-10-12 | L01 工业风格 skill；`c4162204c` | 用户选定工业风格，新增并安装 `industrial-svg-pptx`；模板原生导出与 skill 检查通过，既有图稿/转换器不变 |
| 2026-10-12 | L01 横向双版；`c4162204c`；主 Agent + 布局子 Agent | 用户确认按日期归档；新增参考风格版、原版重排版及两页合辑；旧目录改名由用户完成，本轮只读保护，见本节 |
| 2026-10-12 | L01 图稿；`mp/ara-pulp-v2` / `c4162204c` | 根据用户授权新增完整 SoC 架构图，使用 `svg-pptx-diagrams-native`；新增原生 SVG/PPTX/PNG，保留原 45 张及用户修改的合辑，检查结果见下 |

## 旧 skill 归档与按图意选择风格（2026-10-12）

- 用户明确要求归档删除非 native `svg-pptx-diagrams`，保留 native 与工业版；偏好工业版的 SoC 布局和深色模块边框，同时偏好 native 软硬件分层图的浅色背景、标题层级和协调的彩色框线。这次细化取代早先笼统的“工程架构图优先工业版”；已写入根 `AGENTS.md`，默认按图意生成单版，比较请求再生成多版。
- 输入 HEAD `c4162204c`；未启动子 Agent。依照 `skill-creator` 的调用关系检查要求，确认 native 有独立导出器，industrial 调用 native，publication-figures 的旧版来源仅为历史快照说明、并无运行依赖；工程内 Python/shell 搜索未发现旧 skill 名称调用。
- 经工具权限批准，将完整旧目录（含虚拟环境）移至 [归档与恢复说明](/home/zhaowenyao/.codex/skill-archives/2026-10-12_svg-pptx-diagrams/README.md)，并将 `~/.agents/skills/svg-pptx-diagrams` 发现链接移入归档。1820 项文件 SHA-256、目录和符号链接清单前后一致；旧安装目录与发现链接均已移除。归档不在 active skills 目录内，当前会话已加载的目录描述可能仍显示旧条目。
- 仅同步 native 的 `references/platform-install.md`，去掉“调用旧版”的现行指引，记录归档位置；原说明已备份至归档。未修改任何导出器代码、其他 skill 设计规则或旧图稿。仓库修改限于 `AGENTS.md` 和本主题交接，保留其他对话记录。
- 归档后验证：native `scripts/run.py` 导出工业模板到 `/tmp/diagram-skill-retirement-20261012-native`，成功生成 100 对象 / 47 文本 / 23 原生箭头 / 1 虚线的 PPTX；native 的 `quick_validate.py` 通过；publication `scripts/run.py --help` 退出 0（仅启动检查，未重新验证其整条导出流程）。Office 未实测；未改 RTL/配置，未运行构建或仿真。
- 后续：硬件框图选 industrial，层次/概念图选 native；论文插图可选独立 publication-figures，位图插画可选 imagegen。两类主风格可按图意组合，使用同一个 native 导出后端，无需常规双份生成。

## 公共 Regbus 结构图（2026-10-12）

- 授权/输入：用户显式调用 `industrial-svg-pptx`，要求按 RTL 绘制 Regbus；HEAD `c4162204cfee0c48b81158b4296860a678d92bec`。未启动子 Agent，仅负责新图目录与本主题交接，保留用户已有修改和旧图目录改名。
- 交付：[图稿说明与源码依据](../diagrams/backup_no_use/2026-10-12_regbus_structure/README.md)、[SVG](../diagrams/backup_no_use/2026-10-12_regbus_structure/regbus_structure.svg)、[PNG](../diagrams/backup_no_use/2026-10-12_regbus_structure/regbus_structure.png)、[原生 PPTX](../diagrams/backup_no_use/2026-10-12_regbus_structure/regbus_structure.pptx)。包含生成/检查脚本、导出报告及输入源码哈希。
- 内容：公共原子适配→切片→AXI/Reg 转换→解码/分发；16 类正常目标、错误响应与 RegExt，重复组按类别合并。明确 `clk_i` 同域、组合解码/分发、固定 32-bit Reg 数据、可选目标与 iDMA 独立路径边界；不加入尚未实施的 CDC 或新增 IP。
- 实际验证：`build_regbus.py`、native `run.py --aspect source --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`、CairoSVG 渲染、`verify_regbus.py` 最终均退出 0。135 原生对象、77 文本、28 原生箭头、15 虚线；保存重读文字一致，无栅格媒体；字体度量无文本互相重叠/画布越界；最终 PNG 已目视检查。检查脚本初版将空文本框计入，修正为仅比较非空文本后通过，不涉及图稿内容差异。
- 保护/边界：开始保存 189 个输入哈希及交接临时备份；除本交接获授权追加外核对保持不变。未改 RTL/sw、Cfg、地址或旧图；未提交，未编译/仿真/板测。Office 显示/编辑未实测；字体未嵌入，箭头不保证端口跟随。
- 最小下一步：用户在 PowerPoint 中核对字体、显示与编辑；按具体反馈修订本图。工程事实与主线任务状态未变化，不扩写共享状态页。

## 非教程独立图的工业风格重绘（2026-10-12）

- 用户授权：用新 skill 重绘 `2026-10-11_native_reconstruction` 下非 `learn` 前缀的有效图片，教程图不重绘。清单为 9 个独立 SVG（含 `example` 和后加完整 SoC 图），排除 37 个 `learning_*` 与旧 5 张 contact 辅助拼图；合辑、脚本、报告、锁文件不当独立图。
- 输入：`mp/ara-pulp-v2` / `c4162204cfee0c48b81158b4296860a678d92bec`。使用 `industrial-svg-pptx` 及其 native 导出后端，未使用子 Agent。产物在 [2026-10-12_industrial_redraw](../diagrams/2026-10-12_industrial_redraw/README.md)，日期目录平铺；新建图稿/脚本/说明，更新本交接及 `AGENT_TASKS.md` 导航，保留并行 Regbus 图任务的交接记录。未改 RTL、sw、地址、Cfg、依赖、现有图稿或全局 skill，未提交。
- [新旧对照入口](../diagrams/2026-10-12_industrial_redraw/index.html)、[9 页原生合辑](../diagrams/2026-10-12_industrial_redraw/all_industrial.pptx)。全部 16:9，每图独立 SVG/PNG/PPTX；附 3 张新预览拼图、来源/布局/导出/检查 JSON、生成与渲染/图库/验证脚本。
- 8 图按内容重排，Crossbar 保留 35 条可达矩阵线，启动图采用职责/阶段分区，LLC 保留阵列与方式切换；完整 SoC 使用用户刚认可的工业布局冻结副本 `soc_layout.py` 再生成，SVG 与上轮认可版逐字节一致。图内长说明迁到[图意与版本说明](../diagrams/2026-10-12_industrial_redraw/figure_notes.md)，来源清单保留原始文本和哈希。
- 技术版本边界：旧 QoS 图 S1=ISP/S2=NPU 标为历史独立主口方案，DDR/GB 图仍为 S1=NPU/GB/S2=帧写入；没有借重绘统一端口或冻结地址/接口。旧静态快照、ROM 返回缺口、GB/旁路待实现与 Office 未验证状态保留。
- 实测：native skill Python 执行 `build_industrial.py --out-dir /tmp/industrial-redraw-delivery`；CairoSVG 2.9.1 环境执行 `render_previews.py --directory ...`；native Python 执行 `verify_outputs.py --directory ... --report .../validation.json`；Python 执行 `write_gallery.py --directory ...`，全部退出 0。非覆盖复制至正式目录。
- [验证结果](../diagrams/2026-10-12_industrial_redraw/validation.json)：9 图共 1296 个原生对象、696 个文本、178 个箭头对象、42 个原生虚线对象；257 个关键对象覆盖通过。单图与合辑重读文字一致，无 `ppt/media/`，字体度量无文字重叠/越界。实际逐张看 PNG，修正穿字走线、跨线、标签留白与省略号缺字；HTML 链接检查通过，未进行浏览器 UI/Office 实测。
- 保护核对：快照 `/tmp/industrial-redraw-source-hashes.json` 覆盖两个既有日期图目录共 182 文件，全部哈希不变，包括教程图、用户合辑及锁文件。证据见[交付检查](../diagrams/2026-10-12_industrial_redraw/delivery_checks.json)。没有编译/仿真/板测或新增 ASIC 验收结论。
- 最小下一步：用户在新旧对照页审图并在 PowerPoint 中核对字体/编辑；按具体图反馈微调。新风格并未替换教程/工程文档的既有引用，不触发批量迁移。

## 工业风格复用 skill（2026-10-12）

- 用户授权：偏好工业风格版，要求新建 skill 供后续绘图复用。输入 `mp/ara-pulp-v2` / `c4162204c`；本轮未使用子 Agent。使用 `skill-creator`，安装至 [industrial-svg-pptx/SKILL.md](/home/zhaowenyao/.codex/skills/industrial-svg-pptx/SKILL.md)，默认允许正常自动选择，也可显式 `$industrial-svg-pptx` 调用。
- 新增 6 个 skill 文件：入口、`agents/openai.yaml`、`references/visual-rules.md`、通用 `industrial_starter.svg`、认可版本的 SVG/PNG 快照。固化配色/线宽/文字层次/嵌套分区/正交走线，按新内容调整布局；不把参考图的 Cheshire 参数与候选连接当成普适硬件事实。PPTX 复用同级 `svg-pptx-diagrams-native` 后端，未复制或修改转换器。
- 工程内只更新根 `AGENTS.md` 的绘图风格偏好及本交接；既有 RTL、工程配置、图稿和 skill 保持不变。新 skill 位于用户级目录，不属于仓库文件；目录写入经工具权限边界批准后完成，无覆盖已有目标。
- 验证：`skill-creator/scripts/quick_validate.py` 通过；native 后端 `scripts/run.py --input .../industrial_starter.svg --out-dir /tmp/industrial-svg-pptx-starter-check --aspect source --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc` 通过。模板为 2400×1350，100 个原生 PPT 对象、47 个文本、23 个原生箭头、1 个虚线对象；保存重读文字相同、无 `ppt/media/`、字体度量无重叠/越界、全部本地引用有效，实际查看 PNG 预览。6 个安装文件逐项 SHA-256 与暂存源一致。
- 保护检查：原 native skill（排除环境/字节码）与上轮横向图目录合计 37 个输入文件哈希不变。临时制作与测试目录在 `/tmp/industrial-svg-pptx-skill-20261012`、`/tmp/industrial-svg-pptx-starter-check`；不把模板测试当新 SoC 架构交付。
- 边界：Office 显示/编辑未实测；新 skill 自动选择效果尚待后续真实调用。最小下一步是用 `$industrial-svg-pptx` 绘制下一个工程图，按实际反馈微调风格规范。未增加生产构建/仿真/板测证据。

## 横向双版本与日期归档（2026-10-12）

- 用户决定：后续图稿使用 `docs_codex/diagrams/YYYY-MM-DD_<主题>/`；已由用户将旧目录改名为 `2026-10-11_native_reconstruction`。本轮新增 `2026-10-12_soc_landscape`，并将日期规则写入根 `AGENTS.md`。本交接的旧图链接已跟随改名；下方历史命令/原授权文字保留当时路径，不恢复旧目录。
- 输入：`mp/ara-pulp-v2` / `c4162204cfee0c48b81158b4296860a678d92bec`。按 `svg-pptx-diagrams-native` 绘制；主 Agent 负责原版重排与汇总，`soc_reference_style` 子 Agent 只负责同目录的参考风格图及自身脚本/报告，之后相互审图。未修改 RTL、软件、地址/Cfg、filelist 或依赖，未提交。
- [本轮预览入口](../diagrams/backup_no_use/2026-10-12_soc_landscape/index.html)、[图稿说明](../diagrams/backup_no_use/2026-10-12_soc_landscape/README.md)、[两页原生 PPTX 合辑](../diagrams/backup_no_use/2026-10-12_soc_landscape/soc_landscape_comparison.pptx)。每版分别交付 SVG、PNG、单页 PPTX、layout/export/验证 JSON，附两个生成脚本、合辑导出脚本和统一检查脚本。
- 版本 1：3600×2025、16:9，参考工业芯片框图的细深色边框与柔和嵌套分区；版本 2：3400×1850，保留原蓝/绿/橙/紫和圆角风格。两版均将 CVA6–Ara/NPU/ISP 上置、AXI/Regbus/DDR 横置；合辑统一 16:9 按比例居中。
- 范围：7 个 AXI 发起端 + 扩展、5 类 AXI 目标 + 扩展、18 个 Regbus 外设 + error/RegExt、C1–C9 配置端、DDR S0/S1/S2。Ara GB 分流、独立 GB、统一 S1 搬运前提、RAW/ISP 帧边界选择均保留为候选，未冻结地址与接口参数。
- 命令/结果：native skill Python 运行两份 `build_*.py`（版本 1 由布局子 Agent 生成；版本 2 导出至 `/tmp/cheshire-soc-landscape-v2-final`）；CairoSVG 2.9.1 渲染 PNG；`verify_landscape.py --stem soc_reference_style` 与 `--stem soc_rearranged` 均 PASS；`export_comparison.py --out-dir /tmp/cheshire-soc-landscape-comparison-final` PASS。图稿由非覆盖复制进入正式目录。
- 实际验证：两版人工查看并独立交叉审图；修正 Ara GB 线穿标题、C 标号留白、ISP 副标题越界，以及三 DDR 口统一进入 QoS 的表示。版本 1 为 386 对象 / 198 文本 / 71 原生箭头 / 28 原生虚线，版本 2 为 370 / 185 / 72 / 24；文字逐项与 SVG 一致、字体度量无重叠/越界、单页及两页 PPTX 无栅格媒体。
- 保护：输入 163 个文件 SHA-256 快照位于 `/tmp/soc_landscape_input_hashes.json`；包含用户改名后的旧图目录、用户修改的合辑及锁文件、三篇已有修改文档。交付时全部保持不变，详见[交付检查](../diagrams/backup_no_use/2026-10-12_soc_landscape/delivery_checks.json)。本轮只新增当天图目录、更新本主题交接与根 `AGENTS.md` 的图稿归档规则。
- 边界/下一步：Office 显示/编辑仍未实测，字体未嵌入，箭头未绑定模块端口；未编译/仿真/板测。用户可比较两版并选后续主版，在 PowerPoint 中核对显示与编辑。无 RTL 工程事实变化，不扩大更新共享状态页。

## 完整 SoC 架构图补充（2026-10-12）

- 授权/范围：用户要求在 `native_reconstruction` 新增 SoC 完整框图，展开参考 Crossbar 图的所有主从端口、Regbus 所有外设、DDR 图的三 AXI 端口；补充三张芯片框图作视觉参考。仅绘图和相关导航/交接，未修改 RTL/sw、Cfg、地址、中断、filelist、依赖或旧 FPGA 工程，未提交。未启动子 Agent。
- 输入工作区已有 `01_Cheshire_Ara_Quick_Start.md`、`configuration/CVA6.md`、`handoffs/L01_interface_reference.md`、`all_diagrams.pptx` 修改及 `~$all_diagrams.pptx` 锁文件；全部保护。工作前对本目录原有文件及上述三篇文档保存 155 个 SHA-256 快照，位置 `/tmp/soc_architecture_protection.json`；临时快照仅作本轮核对。
- 交付：[SVG](../diagrams/2026-10-11_native_reconstruction/soc_full_architecture.svg)、[PNG](../diagrams/2026-10-11_native_reconstruction/soc_full_architecture.png)、[PPTX](../diagrams/2026-10-11_native_reconstruction/soc_full_architecture.pptx)。本目录继续平铺；不追加、覆盖用户在编辑的 45 页合辑。更新 README 与 index 入口，旧 45 图报告/母版/合辑保留其历史范围。
- 结构与依据：[图稿说明及复现](../diagrams/2026-10-11_native_reconstruction/README.md#新增完整-soc-架构图2026-10-12)。已核对 `gen_axi_in/gen_axi_out/gen_reg_out`、`cheshire_soc` 的 Ara filter/width converter/LLC/iDMA 路径，以及 `cheshire_idma_wrap` 内部 AXI→Reg。7 个内部发起端、5 类目标、AXI 扩展口、18 个 Regbus 外设目标与 error/extension、9 组新 IP 配置端、DDR 三口均独立标示。可选灰框、新增彩色虚线、C1–C9 配置端身份均有说明。
- 候选拓扑沿 M01 §12 和 DDR 参考图：S1 统一搬运前提、Ara 宽侧新增分流、GB 独立 SRAM、RAW/ISP 二选一保持。没有冻结新地址、GB 参数、lane/VLEN、实际 DDR 端口/频率、时钟域或新增中断。部分局部适配、CDC、逐源中断和 AXI 返回通道采用总览抽象，不能当连接级网表。
- 复现脚本：新增 `build_soc_full_architecture.py`（调用指定 native skill 后端，拒绝覆盖非空目录）、`verify_soc_full_architecture.py`；另附布局、导出和验证 JSON。SVG 是可编辑母版，PPTX 为一页原生形状/文本，PNG 是 CairoSVG 渲染而非 Office 截图。
- 实测命令：native skill Python 执行生成脚本 `--out-dir /tmp/cheshire-soc-architecture-final`；CairoSVG 2.9.1 生成同名 PNG；native skill Python 执行检查脚本并写入 `soc_full_architecture.validation.json`，均退出 0。初稿曾因不支持 round join 和一次不完整路径语法被导出器拒绝，已修正；草稿留在 `/tmp/cheshire-soc-architecture-v1` 至 `v4`，交付仅使用 final 结果。
- 结果：[结构报告](../diagrams/2026-10-11_native_reconstruction/soc_full_architecture.export.json)、[验证报告](../diagrams/2026-10-11_native_reconstruction/soc_full_architecture.validation.json)：3400×2440，386 对象、206 文本、73 原生箭头、26 原生虚线对象；保存重读文字和端点/虚线属性一致，ZIP 无整图图片，字体度量下文本越界/互相重叠为 0。已人工查看全图和 Ara/DDR/GB/图像局部，修正跨线经过标题、分流线和 RAW/GB 交叉的表示。
- 验证边界：Office 显示/编辑未验证；字体未嵌入，箭头未绑定模块端口。原 `verify_outputs.py` 数量断言适用于 45 张历史集合，不用它宣称新增图通过或用户合辑通过。本轮未编译、未仿真、未板测或进行性能/ASIC 验收。
- 最小下一步：在用户 PowerPoint 中核对中文字体与编辑；按用户审图反馈修改本图；M01/I01 后续确认接口时再修订候选连线。无工程事实/任务主线状态变化，本图子任务保存在本主题交接，不扩写共享状态页。

## 基本信息

- 日期：2026-10-11；输入 HEAD `2784340240915fe4338ec54bfd613723b127d62e`。
- 用户授权：使用新建的 `svg-pptx-diagrams-native` 重建旧 skill 生成的全部图片；产物集中到 `native_reconstruction` 单个新目录，不建下级目录、不覆盖原文件。
- 状态：45 张图的 SVG、PNG、单页 PPTX 和 45 页合辑完成；结构验收通过，Office 实际显示/编辑未验证。
- 本轮负责路径：`docs_codex/diagrams/native_reconstruction/` 与本交接。未启动子 Agent。
- 起始已有 M01 接口文档修改及多个图目录/交接未跟踪；全部保留。`backup_new` 中的 publication 版未移动或改写。

## 本轮结果

- [图稿入口](../diagrams/2026-10-11_native_reconstruction/index.html)、[说明与完整列表](../diagrams/2026-10-11_native_reconstruction/README.md)、[45 页合辑](../diagrams/2026-10-11_native_reconstruction/all_diagrams.pptx)。
- 范围：diagrams 下 8 张不同的正式图稿，加教材当前 37 张结构图。重复导出/历史修订按正式最终版重建一份；100 个相关原 SVG 的覆盖关系见 `source_inventory.json`。旧 DDR `before_datasheet` 草案保留原件和来源记录，不作为当前方案重发。
- 排除 WaveDrom、已撤回的 6 张手工波形、publication 版以及 native skill 自测示例。这些不属于本次旧 skill 的当前结构图集合。
- 固定原图布局、配色、文字和 viewBox，按已核对的线身/端点关系重建 306 个完整箭头，其中 18 个双向，共 324 个端点；4 处曲线附加短线合并到原曲线，136 条虚线碎片合并为 4 个完整矩形边框。
- 3618 个旧对象变为 3154 个对象，1653 个文本对象全部保留。24 个早期图中与线身不同色的箭头端点归一为线身颜色；箭头形状采用 native skill 的中号端点，记录视觉差异，不声称逐像素一致。
- 新目录内 SVG/PNG/PPTX、预览索引、接触图、映射、复现脚本和报告全部平铺，没有子目录。没有修改或新建任何全局 skill。

## 验证证据

工作目录为仓库根目录。主要命令：

```sh
~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/native_reconstruction/rebuild.py \
  --out-dir /tmp/cheshire-native-reconstruction-export

~/.codex/skills/publication-figures/.venv/bin/python -B \
  docs_codex/diagrams/native_reconstruction/render_previews.py \
  --directory docs_codex/diagrams/native_reconstruction

~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  docs_codex/diagrams/native_reconstruction/verify_outputs.py \
  --report docs_codex/diagrams/native_reconstruction/validation.json
```

- 全部退出 0。正式目录先保存固定映射/复现脚本；导出在临时目录执行，逐文件确认目标不存在后复制到正式目录。
- 导出后重新读取各 PPTX，校验文字、对象数、原生箭头与虚线属性及 ZIP 完整性，无整图图片嵌入。所有未参与迁移的 SVG 对象和文本对象逐项比较相等。
- PNG 使用 CairoSVG 2.9.1，复用已安装的渲染环境，不采用 publication skill 的设计规则。查看 5 张总览中的全部 45 张图，并放大检查示例、DDR 双向路径、软硬件分层虚线框、教材 Crossbar 曲线。
- 程序化修改四个代表 PPT 的箭头线宽/边框宽度，在临时目录保存重读，原生属性和对象数保持。此结果不是 Office UI 验证。
- 验收报告：45 个输入 SHA-256 保持不变，旧 skill 的 12 个源文件与上轮留存哈希一致；45 SVG、45 图稿 PNG、5 总览 PNG、45 单图 PPTX、1 合辑 PPTX；索引链接有效，目录平铺。
- 当前 PNG 是 SVG 渲染，不是 PPT 截图；字体不嵌入。Office 显示、实际编辑和端口跟随未验证；当前连接器未绑定模块端口。
- 未改 RTL/sw、工程配置、原图、教材页面引用或旧 skill；未编译/未仿真/未板测；未 Git 提交。

## 决策与下一步

- 本次是原版图稿的对象语义迁移，保留原图技术快照与候选/待验证说明，不改变项目实现结论。
- 最小下一步：用户查看 `index.html`，在允许的 Office 环境打开合辑或单图文件确认显示和编辑体验；如需调整箭头大小/图中文字，另行按具体图稿修改新目录内母版。
- 共享项目状态/任务表没有工程事实变化；本次图稿子任务由本独立交接留档。
