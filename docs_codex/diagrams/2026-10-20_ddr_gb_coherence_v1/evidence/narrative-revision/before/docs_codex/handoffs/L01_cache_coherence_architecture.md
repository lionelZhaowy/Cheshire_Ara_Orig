# L01 / DDR–GB 缓存一致性审查与图稿

当前版本入口：[2026-10-20 SoC v1 同步](#2026-10-20-soc-v1-文档与图稿同步)。此前各节保留当时输入、选择与验证结论；旧三口和 Ara 独立支路不再作为当前方案。

## 修改记录

| 日期 | 角色 / 输入 | 内容 |
|---|---|---|
| 2026-10-20 | L01 文档实施；`mp/ara-pulp-v2` / `c9abbb48` | 按批准计划同步共享 M5、四口前端、LVDS 交接及两套专题图集；保护九页主 PPT 和 E01 已有修改 |
| 2026-10-15 | L01 文档作者；`mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8` | 按用户确认计划新增一致性条件审查、三类架构比较及三张可编辑图；只交付文档与图稿 |
| 2026-10-16 | L01 文档修订；同分支 / HEAD | 按用户要求润色正文与三图；按新增更正重画图 1 的共享代理、LLC–DDR 路径及一致性接口；沿用方案比较状态 |
| 2026-10-16 | L01 图 1 再修正；同分支 / HEAD | 用户否定上轮重布局，明确只在 10 月 12 日工业版底图上最小增补；原位保留 S0/S1/S2，新增协调模块与控制线 |
| 2026-10-16 | L01 评审反馈落实；同分支 / HEAD | 修订独立说明第 3–7 章，区分既有可靠性缺口与新增能力，补齐排空、软件等待／恢复及评审 Prompt |
| 2026-10-16 | L01 文档维护；用户转交独立评审，同分支 / HEAD | 完成评审答疑后的 Markdown 修订，新增 Q&A 与供应商会议问题；握手职责待实现，未改 RTL |
| 2026-10-16 | L01 Datasheet 对照；同分支 / HEAD | 根据用户提供 V2.1 手册更新会议问题与 Q&A，记录已知能力、页码和文档疑点；未取得供应商补充答复 |
| 2026-10-16 | L01 时序答疑整理；同分支 / HEAD | 在主说明图 3 后补充应用流程、九项硬件动作与 16 个箭头的对应表，明确输出准备在图中提前执行 |

当前接手入口为[主说明](../engineering/DDR_GB_Coherence_Design.md)及本文件末尾“Datasheet 核对与供应商问题收窄”“时序图与应用流程对应”。下方早期“尚未选型／待评审”等措辞保留当时状态，当前采用的软件交接与硬件范围维护方向见后续用户决策记录。

## 结果与范围

- 正式技术内容：[DDR–GB 缓存一致性](../engineering/Cache_Coherence_Architecture.md)。状态：文档与图稿完成；硬件方案未选型、未实现、未验证。
- 用户选择“先比较，暂不选型”。逐行 I/O 一致性是不分配 LLC 行的长期优先评估建议；缓存直接供数、协议选型及接口改造不是用户已确认决策。
- 本轮改动：上述正式文档、`engineering/README.md` 入口、[新图稿目录](../diagrams/backup_no_use/2026-10-15_cache_coherence/README.md)、本交接。
- 保留 `IP_DDR_Interface_Contract.md` 的用户需求及现有建议。未改 RTL、sw、地址、位宽、CSR、IRQ、启动、filelist 或依赖；未提交 Git。共享状态与任务状态没有工程进展变化，不改写。
- 输入已有 `L01_software_hardware_interfaces.md` 未提交修改与 `2026-10-14_software_stack_industrial/` 未跟踪目录，未覆盖；[input.json](../diagrams/backup_no_use/2026-10-15_cache_coherence/evidence/input.json)保存这些文件、现行契约/共享文档及源码哈希。

## 证据与检查

工作目录为仓库根。源码检查覆盖 WT profile、写缓冲、Ara 失效/pending、LLC way 维护和原子适配前提；外部规范采用 Arm IHI 0022H D3.1/D6.7/D11。依赖上游 HEAD 仅作来源标识，实际输入由主仓库版本及文件哈希约束。

下列命令结果均为本轮实际执行；输出目录相对图稿目录：

| 命令 / 检查 | 结果 |
|---|---|
| `build_figures.py --out-dir evidence/source-01` | 退出 0，3 张 SVG、29 条连续箭头 |
| `render.py --source-dir evidence/source-01 --out-dir evidence/render-01` | 退出 1；Chrome socket 被沙箱拒绝，原始日志保留 |
| 同输入渲染到 `evidence/render-02` | 经环境审批在沙箱外运行，退出 0；首次预览通过 |
| `build_figures.py --out-dir evidence/source-02`，再渲染到 `evidence/render-03` | 各退出 0；最终三图无文字越界、框内溢出、文本重叠或连线穿字；逐张人工查看 PNG |
| 原生后端 `run.py --input system.svg read-to-gb.svg write-to-ddr.svg --out-dir export --aspect source --font 'Microsoft YaHei' --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc` | 退出 0；3 页、119 文本、29 原生箭头；保存重读检查通过 |
| `validate.py --out-file evidence/validation.json`，`git diff --check` | 结果见[验证报告](../diagrams/backup_no_use/2026-10-15_cache_coherence/evidence/validation.json)；检查正文/图稿链接、SVG/PPTX一致性、原生对象、输入保护与空白错误 |

字体、重现命令和完整产物导航见[图稿说明](../diagrams/backup_no_use/2026-10-15_cache_coherence/README.md)。PNG 的布局检查不是 Office 检查；Office 显示与编辑未实测。未编译、未展开、未仿真、未板测，也没有运行新硬件一致性协议。

## 未关闭项与下一步

- M01/I01 评审共享粒度、是否允许缓存直接供数、GB/搬运器实际接口、共享原子域与成本；本轮没有冻结接口编码或配置。
- 现有 L1D 外部失效不能未经并发重审直接拓展；LLC 的逐行探测、数据响应和完整确认服务仍是新增工作。
- 将正文验收场景交 V01/S01；重点验证旧回填/脏行不能覆盖新写、部分字节不丢失、完成与超时恢复可追溯。已有 Ara B 错误处理等生产缺口不因本次文档交付关闭。
- 最小下一步：用户/M01 先选需要的共享能力及是否允许缓存供数，再形成实现规格；无需为阅读本文重跑历史实验。

## 2026-10-16 文字与图 1 互连修订（图 1 布局已被下节替代）

### 用户要求及处理

- 正文和三张图一起润色：以机制、原因和结果组织叙述，减少重复否定句与授权提醒，保留技术条件和证据。正文仍为五部分，约 2750 个汉字。
- 用户随后明确：Ara 访问 GB 应经过共享数据代理，代理也服务 NPU/ISP；图 1 应清楚呈现 LLC 到 DDR Controller 的通路。本次将旧图的 Ara→GB 直连更正为 Ara→过滤/分流→共享代理→GB，并分开画出共享代理与 DDR–GB 搬运器。
- 用户提供 10 月 11 日参考图，随后指定更清楚的[10 月 12 日工业版](../diagrams/2026-10-12_industrial_redraw/ddr_interconnect.pptx)。两版均已读取 PPTX 文字并查看配套 PNG。新版沿用工业分区与连续连线，DDR 端口数量、宽度和 IP 组织保持待评审。
- 同步补出 LLC 的回填/写回/透传路径、图像帧写入独立事务、CVA6–Ara 既有协作，以及写缓冲、原子观察点、LLC、设备入口和 DDR 在途事务的协调职责。图 2/3 也标明通过共享代理访问 GB。

### 修改范围与证据

修改正式正文、本交接，新增[2026-10-16 图稿目录](../diagrams/2026-10-16_cache_coherence/README.md)。旧图保留；正文与交接的修订前版本存于新目录 `evidence/before/`。工程参考索引、其他专题、共享状态、RTL/sw 及依赖均保留输入内容。

本次定向复核 `cheshire_soc.sv` 的 Ara 失效过滤→位宽转换→主 Xbar，以及 LLC 的 `axi_llc_mst_req_o / axi_llc_mst_rsp_i` 外存连接；8 个原分析源码哈希与 10 月 15 日输入相同。新图表示架构评审用的职责与逻辑连接，实际生产源码尚无 GB 分流或通用一致性服务。现行契约与其他专题由其负责对话后续汇总本次图 1 更正；本轮只修改上述负责文件。

| 本轮命令 / 检查 | 结果 |
|---|---|
| `build_figures.py --out-dir evidence/source-04` | 退出 0；3 张 SVG、43 条连续箭头，图 1 有 25 条 |
| `render.py`：`source-01` → `render-01` | 退出 1；Chrome socket 被沙箱禁止，日志保留 |
| 经环境审批：`source-01/02` → `render-02/03` | 发现并修正图 1 标签重叠/穿线；原始检查结果保留 |
| `source-03/04` → `render-04/05` | 均退出 0；最终三图无文字越界、框内溢出、文本重叠或连线穿字，逐张查看 PNG |
| 原生后端 `run.py`，三 SVG → `export/` | 退出 0；3 页、145 文本、43 原生箭头、7 原生虚线形状 |
| `validate.py --out-file evidence/validation.json` | [报告](../diagrams/2026-10-16_cache_coherence/evidence/validation.json)：检查链接、PPTX 原生对象、连线端点、输入保护与空白错误 |

原生导出的完整参数见[图稿说明](../diagrams/2026-10-16_cache_coherence/README.md)。Office 显示和编辑未实测；本轮执行范围为文档与图稿检查。原有硬件并发、错误恢复和性能验收项继续开放，方案选型与接口实施仍由 M01/I01 后续评审。

## 2026-10-16 工业底图最小增补（当前采用）

用户明确否定上节重新安排整个图 1 布局的做法，并要求排除 10 月 11 日参考图的影响。当前唯一绘图基准是 `2026-10-12_industrial_redraw/ddr_interconnect.svg` 及其原生 PPTX；生成器直接载入该 SVG，保留所有原有模块、尺寸、坐标、数据线和三口 DDR 分组。

仅在原空白处增加一个缓存一致性协调模块及六条控制连线，分别涉及 CVA6 L1D/写缓冲、原子适配、LLC、S1、S2 和 DDR 在途管理；另补一个紫色图例。原位保留 S0←SoC/LLC、S1←NPU/GB 搬运、S2←帧 DMA。三处局部标签调整为“L1D / 写缓冲”“共享数据代理”“WB 缓存 / 片上 SPM”；既有数据连线完全保留。图 2/3 的 SVG 与上一版相同。

正式入口改为[工业底图版](../diagrams/2026-10-16_cache_coherence/industrial-base/system.png)及[三页 PPTX](../diagrams/2026-10-16_cache_coherence/industrial-base/export/diagrams.pptx)，正文图注解释 S0/S1/S2 和新增控制接口。根级重布局稿只作历史证据，已在图稿 README 标为被否定；旧输入、图片和导出保留。当前源脚本只依赖 10 月 12 日底图。

本次输入、修订前备份及结果分别见 `evidence/minimal-input.json`、`evidence/before-minimal/`、[最小修改检查](../diagrams/2026-10-16_cache_coherence/evidence/minimal-validation.json)。执行记录：

| 命令 / 检查 | 结果 |
|---|---|
| `build_figures.py --out-dir evidence/minimal-source-01` | 退出 0；图 1 原画布 2800×1575，新增模块及控制线 |
| Chrome：`minimal-source-01` → `minimal-render-01` | 经本地环境审批执行，退出 0；无文字越界、重叠、框内溢出或连线穿字，已查看图 1 PNG |
| 原生导出：三 SVG → `industrial-base/export/` | 退出 0；3 页、149 文本、51 原生箭头、5 原生虚线形状 |
| `validate.py --out-file evidence/minimal-validation.json` | 核对唯一底图的原对象几何/样式、三口连接、图 2/3 一致性、链接、原生 PPTX 与输入保护 |

绘图约束的更正已落实；缓存供数、硬件协议选型及 RTL 验收继续按原未决项评审。Office 显示和编辑仍未实测。

## 2026-10-16 CPU–NPU 工业与学术方案综述

用户确认工程综述深度：4000–6000 字、七组案例、四张原文配图。输入仍为 `mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`。由 L01 完成资料研究，供 M01/I01/S01/V01 评审；沿用现有架构建议状态。

交付[CPU–NPU 缓存一致性综述](../engineering/CPU_NPU_Cache_Coherence_Survey.md)，约 4000 汉字，另含英文术语与引用。比较 Ethos-U、Ethos-N、AMD Zynq UltraScale+、NVDLA、Gemmini、ESP/Cohmeleon、Spandex/FCS。统一区分硬件覆盖范围、缓存分配和独立 SRAM 生命周期。重点核实：HPC 支持 I/O 一致性且不分配 L2；ESP 的 LLC-coherent 模式仍需维护 CPU 私有缓存；Gemmini 具体参照 Chipyard 1.11.0 配置及其固定子模块；Cohmeleon Fig. 3 是混合加速器竞争实验，Spandex/FCS 是 CPU–GPU 模拟研究。

修改范围：新增综述与[原图资料目录](../diagrams/2026-10-16_coherence_survey/README.md)，在工程索引追加一行，本主题交接追加本节。现有缓存一致性正文、工业底图和其他主题保留输入内容；源码、配置与依赖未修改。工程索引将项目方案和外部综述并列导航，新综述链接既有条件审查和源码依据。

资料目录保留四张原图（3 SVG、1 PNG）、Chrome PNG 预览、中文图注、来源版本／URL／哈希、HTML 阅读预览及渲染脚本。Ethos-U 固定提交 `9a825eec770d`，Gemmini README 固定提交 `2c98ce3ec634`；Chipyard 1.11.0 的 Gemmini 子模块为 `8c8b38b9dea3`。全部使用已有环境，无新增依赖。

| 检查 | 证据与范围 |
|---|---|
| 当前工程源码 | 8 个相关文件哈希与上一专题证据一致，见[源码核对](../diagrams/2026-10-16_coherence_survey/evidence/local-source-check.json) |
| `python3 docs_codex/diagrams/2026-10-16_coherence_survey/render.py` | 已安装 Chrome 渲染四图及 Markdown HTML；图片全部加载、页面无横向溢出，见[浏览器记录](../diagrams/2026-10-16_coherence_survey/evidence/browser.json) |
| 原图／阅读检查 | 四张 PNG 逐张查看，核对路径、标签、图例与轴；保留原图内容，中文说明置于图注 |
| 链接／空白／输入保护 | [最终检查](../diagrams/2026-10-16_coherence_survey/evidence/validation.json)记录正文结构、相对链接、原图哈希、已有工作区保护及 `git diff --check` |

正文 16 个独立外部资料 URL 中，14 个直接 HEAD 返回 200；两份 Arm PDF 的直接请求返回 403，已通过 web 工具打开并读取官方原文，记录于图稿目录 `evidence/source-links.json`。

验证范围为资料、源码静态对照及文档显示；未运行 Chipyard／当前 SoC 仿真或板测。供应商具体探测服务、Ethos-N 的缓存分配细节、当前工程缓存供数与协议实现仍待评审。最小下一步：M01/I01 依据共享负载和旁路要求选择待测候选，以软件维护为成本基线制定硬件验证与性能实验。

## 2026-10-16 综述补充：项目建议归类与统一布局对比

用户指出综述缺少项目建议的明确位置，并要求用示意图直观比较。输入仍为 `mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`，L01 文档职责；本次更新综述、原图目录 README 导航及本交接，新增[统一布局图稿目录](../diagrams/2026-10-16_coherence_comparison/README.md)。现有架构正文、工业底图三口 DDR 互连、原文图片及其他主题保留。

正文明确：项目优先评估的是 E“不分配 LLC 行的逐行 I/O 一致性”，与 D 同类而采用不同分配策略；B“搬运边界硬件维护”以块／任务为交接单位。三张对比图展示 A/B、C/D、E/F，第四张展开 E1 清理到 DDR 后读取与 E2 缓存直接供数。E2 仍待评审；E1 保持事务级分类的前提是探测至访问完成受保护。图稿属于机制解释，不替代实际 SoC 端口图。AMD HPC 的 L2 分配行为只作为能力参照，项目通用服务仍待设计。

采用 `industrial-svg-pptx`，输出四张 SVG、四张 PNG、四页原生 PPTX及生成源。第一轮 Chrome 检查发现第四图五处文字穿线，已调整标签；最终四图无文字越界、溢出、重叠或连线穿字，并逐张查看。原生导出重读核对 146 个文字对象、71 条箭头，未嵌入整图位图；Office 实机显示／编辑未测试。更新后的 HTML 预览加载八张图片，页面无横向溢出。

执行入口与证据：`build.py`、既有 Chrome `render.py`、原生后端 `run.py`、新增 `render_document.py`；[图稿检查](../diagrams/2026-10-16_coherence_comparison/previews/browser.json)、[正文检查](../diagrams/2026-10-16_coherence_comparison/evidence/browser.json)、[最终检查](../diagrams/2026-10-16_coherence_comparison/evidence/validation.json)。修订前文件备份和受保护文件哈希位于新目录 `evidence/before/` 与 `evidence/input.json`。

本轮验证限于技术表达、链接、图稿及输入保护，未实施或运行硬件。原有协议选型、缓存供数、原子域和性能验证事项继续开放。

## 2026-10-16 用户收敛方向：软件交接与硬件范围维护

输入仍为 `mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`。用户本轮要求给出方案，允许推理前后显式存储同步，要求 L1D 也纳入硬件探测；本项目保留设备绕过 LLC 的 DDR 接入和独立 GB，排除 F 类设备私有一致性缓存；倾向统一通过 DDR 交换缓存与 GB 数据，要求比较直接供数的代价，不采用 LLC→GB 新数据口。具体指令、协议和硬件实现尚未冻结。

原综述的 E/F 图同时呈现了接入位置和缓存代理属性，容易混淆。F 的分类依据是设备存在参与探测的同地址私有缓存，接入 L2 本身并不足以归入 F。综述所用 Gemmini 固定版本以 DMA 显式搬运 Scratchpad，其连接 L2 的事实与上述 F 定义应分开理解。此处记录纠正；当前文档与图稿仍为上一轮比较快照，后续修订应优先采用本节用户方向。

本轮建议：保留 E 所示旁路数据拓扑，将维护策略收敛到软件触发的缓冲区／分块交接，硬件负责 L1D／写缓冲、LLC 范围操作和 DDR 跨端口完成确认。该维护方式更接近 B 的批量交接；软件保证交接区所有权，DMA 准入等待维护完成。输入 clean 到 DDR，输出写前处理旧脏数据、写后 invalidate 排除期间重新取得的旧副本。采用清理后失效的保守输出准备方式，完整覆盖省略旧数据回写作为后续独立优化。若要硬件阻止 CPU 违规访问，还需在 L1 命中路径覆盖范围检查，不能只在 LLC 后阻挡。

静态复核：向量 profile 的 L1D 为 8 KiB、4 路、32 B 行、WT，`DcacheFlushOnFence=0`；`wt_axi_adapter.sv` 外部失效设置 `inv.all`，`wt_dcache_missunit.sv` 清除索引对应全部 way，`wt_dcache_mem.sv` 的行写／失效占用会阻塞读授权。LLC 现有 `axi_llc_config.sv` 按 way 维护并隔离入口；按范围维护及独立完成语义需要扩展。现有 FENCE 不能作为完成 LLC→DDR 清理的依据。标准语义参照 [RISC-V CMO v1.0，20240411 规范](https://docs.riscv.org/reference/isa/v20240411/unpriv/cmo.html)；软件交接参照 [Linux 6.5 DMA API](https://docs.kernel.org/6.5/core-api/dma-api-howto.html)。本地 Zicbom 实现与平台传播路径尚未具备已验收证据，建议先评审范围维护引擎及 HAL／驱动封装。

开销评估重点为 tag 端口竞争、失效后重填、LLC 脏写回、维护期间入口隔离及同步频率；面积、周期、CPU 性能比例需 RTL／综合与负载测量。最小后续评审对象：范围维护与并发回填的协议、三 DDR 端口的跨口可见性、软件所有权及 LR/SC/AMO 域、超时排空和迟到写。验证应包含部分行保护、写缓冲未排空、写后旧副本重取及缓存行大小不同的情况。

本轮仅追加本节交接，保留正文、图稿、契约与其他工作区修改；未运行构建、仿真或板测。

## 2026-10-16 软硬件协同维护：正式规划与图文更新

用户要求将上节方案详细写入现有规划并同步图文。输入仍为 `mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`，L01 负责文档，供 M01/I01/S01/V01 后续实现评审。当前方向为软件交接、L1D／LLC 硬件范围维护、统一经 DDR 的缓存／GB 数据交换；此前逐事务 I/O 一致性优先推荐状态由本节取代，F 为文献背景，缓存直供为成本比较项。

正式更新[规划正文](../engineering/Cache_Coherence_Architecture.md)五部分：定位与数据连接、输入输出交接、接口与完成协议、维护开销与数据路径比较、源码及验收。明确输入 clean、输出写前 clean＋invalidate／写后 invalidate、旧回填处理、部分行保护、DDR 跨口可见、错误隔离和软件所有权；按实际数据交接设置同步点。补充当前 8 KiB WT L1D 的索引全 way 失效、端口竞争及 LLC way 维护隔离的成本。具体 CSR、指令形式、接口粒度和硬件实现仍待评审。

同步[综述](../engineering/CPU_NPU_Cache_Coherence_Survey.md)开篇、分类图注和项目启示，保留七组案例、原文图片与外部来源；工程索引更新方案状态。旧图稿目录 README 增加现行入口，其图像、PPTX 和证据均保留。`CPU_NPU_Inference_Systems_Survey.md`、GB/OS 专题、IP/DDR 契约及其他工作区内容保持输入版本。

新增[2026-10-16_coherence_hybrid](../diagrams/2026-10-16_coherence_hybrid/README.md)：六张 SVG/PNG、六页原生 PPTX、生成源、两份 HTML 阅读预览和检查证据。前三张用于规划，其余为综述分类对比。系统图继续只采用 10 月 12 日工业底图，保留所有原模块几何、数据线路及 S0/S1/S2；仅更新已新增的维护模块与控制标签。图 2 新增完整交接过程；图 3 比较经 DDR 与缓存直供，后者标明本方案不采用。

| 本轮检查 | 结果与证据 |
|---|---|
| 生成与 Chrome 布局 | `build.py` 与既有 `render.py`；首轮发现系统图一个标签穿线并修正，最终六图无文字越界、框内溢出、文本重叠或连线穿字；逐张查看 PNG |
| 原生导出与重读 | 六页、270 文本、119 原生箭头、9 原生虚线形状；核对 SVG 文本与 PPTX，未嵌入整图位图 |
| 文档显示 | `render_documents.py`；规划 3 图、综述 8 图全部加载，页面无横向溢出 |
| 输入与拓扑保护 | [input.json](../diagrams/2026-10-16_coherence_hybrid/evidence/input.json)保存已有文件哈希、9 个源码哈希及允许修改列表；原文修订前内容备份在 `evidence/before/` |
| 链接、差异与范围 | [validate.py](../diagrams/2026-10-16_coherence_hybrid/validate.py)与[最终检查](../diagrams/2026-10-16_coherence_hybrid/evidence/validation.json)，包含底图几何及真实连接核对、源码哈希、已有文件保护和空白检查 |

Office 显示／编辑尚未实测。硬件维护、DMA、CPU 性能和错误恢复用例列为后续验收，本轮未编译、仿真或板测。最小下一步为 M01/I01/S01 评审范围维护完成语义、DDR 多口可见性、HAL 入口与原子域，再制定针对性 RTL 和驱动实现计划。

## 2026-10-16 独立说明：从裸机推理到缓存维护

用户审核通过八章独立说明计划后授权实施。L01 本轮输入为 `mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`，工作区已有文档和图稿修改保留；状态为文档与图稿交付完成，硬件仍待实现。

新增主阅读入口[《DDR–GB 数据同步设计：从裸机推理到缓存维护》](../engineering/DDR_GB_Coherence_Design.md)：八章按一次裸机推理展开，先解释数据版本与错误原因，再说明输入／输出维护、31 行 HAL 伪代码、硬件接口职责及开销。正文约 5100 汉字，全文约 5300 汉字；章节使用陈述句，主线独立于综述中的字母分类。既定的软件交接、L1D／LLC 硬件维护、设备旁路和统一经 DDR 交换方向保持原样。

源码复核进一步校准 WT 示例：`wt_dcache_wbuffer.sv` 开头说明及应答处理显示，写缓冲可向 CPU 读取前递新值，返回写应答后再按命中状态更新 L1D；图 2 因此分别标示 L1D 阵列值和 CPU 可获得的值。这是源码时序说明，未复现硬件异常。保留部分行保护、32/64 B 粒度差异、冲突回填／替换、跨口可见、原子域及迟到写恢复等验收条件。

修改范围：新增正文及[配套图稿目录](../diagrams/2026-10-16_ddr_gb_coherence_design/README.md)；旧规划仅在开头增加新入口，原正文完整保留；工程索引增加主阅读入口；本交接追加记录。综述、推理系统、GB、OS、现行 IP 契约及源码保持输入版本。未提交 Git commit。

三张 SVG／PNG、三页原生 PPTX、生成源和 HTML 阅读预览位于 `2026-10-16_ddr_gb_coherence_design/`。图 1 只沿用 10 月 12 日工业底图的增补入口，123 个原始带 ID 对象的几何及数据线保持一致；图 2 展示三种数据版本错误，图 3 把裸机调用与硬件动作放在同一时间线上。

| 检查 | 命令与结果 |
|---|---|
| 图稿生成与 Chrome | `build.py --out-dir …/figures`；既有 `render.py --source-dir …/figures --out-dir …/previews`，退出 0。首轮 Chrome 受沙箱 socket 限制，经本机执行审批后完成；逐张查看 PNG，修订前后证据均保留 |
| 原生导出与重读 | 已安装 skill 的 `scripts/run.py`，退出 0；3 页、154 个文字对象、54 条原生箭头、12 个虚线对象，无整图位图 |
| 正文显示 | `render_document.py`，退出 0；八章标题和三图加载正常，页面无横向溢出；已查看正文及图注阅读预览 |
| 链接、拓扑与保护 | `validate.py`，检查正文链接、PPTX 文字／箭头、三口与代理路径、旧规划原文保留、源码哈希及空白错误；[最终记录](../diagrams/2026-10-16_ddr_gb_coherence_design/evidence/validation.json) |

[输入清单](../diagrams/2026-10-16_ddr_gb_coherence_design/evidence/input.json)保存 428 个已有文件及 14 个源码／依据文件的哈希；三份允许修改的已有文件另有可恢复备份，其他 425 个已有文件通过保护检查。Office 显示与编辑未实测；本轮未执行 RTL 编译、仿真、板测或性能测量。最小下一步是人工通读独立说明，再由 M01/I01/S01 评审范围维护和 DDR 跨端口完成语义；接口编码、地址与实现参数仍待确定。

## 2026-10-16 缓冲区术语澄清

用户要求将答疑中的概念区分补入独立说明。输入 HEAD 仍为 `322bd6ce9`。修改正文开篇及第 1–3 章：用表格区分 DDR 软件输入／输出缓冲区、WT L1D 内部写缓冲和独立 GB；补充 `wt_dcache.sv` 中的 `i_wt_dcache_wbuffer`、八条目配置及 `wbuffer_q` 时序状态的源码入口；说明软件范围交接、写缓冲排空和 DDR→GB 搬运的不同职责。既定维护流程与硬件方案保持原样。

同步刷新配套 HTML 阅读预览与检查记录，原文、交接及旧预览保存在 `2026-10-16_ddr_gb_coherence_design/evidence/buffer-terminology/before/`。`render_document.py` 和 `validate.py` 均退出 0，检查新增表格的页面布局、相对链接及已有内容保护；全文约 5800 汉字，八章和三图结构保持。SVG／PNG 图稿、PPTX 及 RTL 未修改，未执行硬件构建或运行验证。

## 2026-10-16 评审反馈落实：事务排空与软件恢复

输入：`mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`。用户批准本轮文档修订计划；L01 仅修改[独立说明](../engineering/DDR_GB_Coherence_Design.md)、配套图文及本交接，新增[下一轮评审 Prompt](../maintenance/L01/reviews/ddr_gb_coherence_review_prompt.md)，供用户转交；尚未执行独立评审。综述、旧规划、工程索引、契约及 RTL／软件保持输入版本。

正文保留八章及缓冲区术语，约 6400 汉字、27 行概念伪代码。第 3–5 章明确软件停止范围访问、硬件处理已接受事务及受保护维护窗口，补充迟到读响应的条件性时序；该交错尚未在当前路径复现。第 6 章在首次维护前建立上下文，列出六个等待点的成功条件与错误出口，说明未知接受状态、超时隔离、迟到写、资源复用及 SPM／CPU 停顿对超时检测的影响。第 7 章把既有可靠性缺口、新增同步能力、供应商集成契约分开，按 way 与按范围的差异归入实现工作。

本轮源码确认：`axi_llc_w_master.sv` 未使用 B 响应载荷，收到握手即继续；flush 通知进入 config 计数完成链，普通替换也经过该写回路径。该事实支持“引入 GB 前已存在的写回错误处理缺口”，系统级报告／恢复和实际错误影响仍待核查，未进行故障注入。WT missunit 的 DRAIN 屏蔽读 miss、推进写并等待写缓冲空及 MSHR 空，再经 FLUSH 返回确认，可作为排空再失效的参考。FENCE 提交等待链包含 WT 写缓冲空，LLC clean 仍由平台服务负责。LLC 隔离可能影响 SPM 访问；维护应自主推进，上游写排空应在隔离 LLC 之前完成。

本轮[图稿目录](../diagrams/2026-10-16_ddr_gb_coherence_review/README.md)保存三张 SVG／PNG、三页原生 PPTX、生成源与阅读预览。图 1、图 2 与上版 SVG 逐字节相同；图 3 新增上下文、冲突请求限制、排空确认、写响应错误判断及最终失效说明。原图稿和全部历史证据保留，修订前正文与交接备份在 `evidence/before/`。

| 检查 | 命令、结果及证据 |
|---|---|
| SVG 生成与 Chrome 布局 | 新目录 `build.py --out-dir …/figures`；既有 `2026-10-16_cache_coherence/render.py`，三图通过，逐张查看 PNG；沙箱内 Chrome 首次启动失败日志保留，经本机执行审批后完成 |
| 原生 PPTX | 已安装 skill 的 `scripts/run.py --aspect 16:9`；3 页、156 个文本、55 条原生箭头、12 个虚线对象，无整图位图；重读比对 SVG 文本及对象属性 |
| 正文预览 | 新目录 `render_document.py`；八章与三图加载正常，无页面横向溢出 |
| 链接与保护 | 新目录 `validate.py`；[最终检查](../diagrams/2026-10-16_ddr_gb_coherence_review/evidence/validation.json)核对链接、123 个底图对象、既有文件及源码哈希、空白错误；[输入清单](../diagrams/2026-10-16_ddr_gb_coherence_review/evidence/input.json)记录 174 个已有文件和 17 个源码输入 |

Office 显示／编辑未实测，未执行 RTL 构建、仿真、板测、错误注入或性能测量。最小下一步：用户转交评审 Prompt，由独立评审核对目标维护窗口、错误观察点、软件前进性及恢复契约；具体修复位置、CSR／指令形式与超时值留待实现评审。本记录补充前文“现有 FENCE 不能完成 LLC 清理”的结论，明确其已有写缓冲排空作用。

## 2026-10-16 独立评审答疑与供应商会议准备

**输入与授权。** L01 文档维护，`mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`。用户转交新一轮独立评审，要求先分析答疑，随后明确授权修改 Markdown、记录供应商会议问题，并保存评审及答疑 Q&A。被评审主文 SHA-256 为 `487683bb133ddcf10584c1123baec3620910e64a5f6a4eddc0690f67e0cf1373`，作者接收时重新核对一致。本轮未启动其他 Agent，未提交 Git commit。

**本轮交付。** [主说明](../engineering/DDR_GB_Coherence_Design.md)保留八章、三图和概念伪代码；补历史错误跨命令影响、等待／报错／重试区别、五阶段握手职责，以及任务 A 超时后仍写 P 的恢复例子。SPM 说明改为具体入口路径，区分正常有限等待与故障挂起。输入输出按取整后的维护范围隔离。图注解释逻辑完成条件和 Ara 接收握手；SVG、PNG、PPTX 与旧 HTML 预览均保留原件，旧预览仍是修订前快照。

新增[供应商会议问题](../engineering/DDR_Supplier_Coherence_Questions.md)，按 S0 写成功后 S1 读的具体时序询问可见性，再询问错误、部分写入、排空和复位覆盖，附答复／版本／依据栏。新增[评审与答疑 Q&A](../maintenance/L01/reviews/ddr_gb_coherence_review_qa.md)，保存完整独立评审原文、作者判断、五项追问与更正、采纳／暂缓表及可转交反馈。原附件字节保存在本轮证据目录，Markdown 原文仅调整链接和标题以便搬迁。

**决策与事实边界。** 用户确认维护窗口和握手需要实现，本轮只登记职责，没有实施 RTL/HAL。“新同步清除历史错误”被明确更正为未来应避免的设计风险，当前写回路径未记录该错误。LLC 写回不检查 BRESP、回填不使用 RRESP、tag 先于写回成功更新等属于静态源码核查；不据此宣称故障已复现。透明重试、故障硬时限／监控主体、CSR 和额外 DDR 接口尚未冻结。供应商问题尚未发送或取得答复。

**负责文件。** 主说明、供应商问题、Q&A、原评审 Prompt 的状态、工程索引、L01 维护索引、本交接；共享状态／任务表仅增加本主题进展与链接。保留其他对话已有工程索引内容、`L01_software_hardware_interfaces.md` 修改及全部原图稿。旧 Prompt 的待评审状态被当前记录替代，原指令与原始检查证据仍保留。

**检查与证据。** 修订前 7 份已有 Markdown 已可恢复备份；输入状态、附件哈希及 137 个源码／图稿／范围外文件哈希见[输入清单](../maintenance/L01/reports/ddr_gb_coherence_revision/evidence/2026-10-16_qa_update/input.json)。执行 `python docs_codex/maintenance/L01/reports/ddr_gb_coherence_revision/evidence/2026-10-16_qa_update/validate.py`，检查本轮文件的本地链接、主文结构、完整评审保留、保护哈希及 `git diff --check`；实际结果见同目录 [validation.json](../maintenance/L01/reports/ddr_gb_coherence_revision/evidence/2026-10-16_qa_update/validation.json)。最终退出 0：193 项本地链接、137 个保护文件、7 份备份、八章／三图／27 行未改伪代码及完整评审保留检查通过。首轮仅因报告自链接在报告生成前尚不存在而失败，原结果保存在 `validation_initial.json`；报告生成后复核通过。本次未运行浏览器／Office 检查、RTL 构建、仿真、板测、错误注入或性能测量，旧图文验证仅对原版本有效。

**最小下一步。** 用户审阅修订后的主说明和 Q&A；开会时使用供应商问题表并记录依据；再按用户授权细化握手接口和恢复目标。下一轮独立复审须使用本轮修改后的 Markdown，而非旧 HTML 预览或旧主文哈希。

## 2026-10-16 Datasheet 核对与供应商问题收窄

输入：`mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`。用户先提供 DDR Controller Datasheet，要求阅读核对，再明确授权更新 Markdown。沿用 L01，仅负责供应商问题、主说明、Q&A、本交接及共享状态／任务表的主题摘要；未改生产 RTL、软件、原契约或图稿，未提交 Git。

[会议问题](../engineering/DDR_Supplier_Coherence_Questions.md)保留 Q1–Q7 编号，记录 V2.1（September 2024）、61 页和原资料位置。将手册明确的 AXI4／多端口／独立时钟、错误中断、上电复位，与仍待补充的跨口完成、属性行为、错误事务关联、运行中排空／复位分开。记录功能表与信号表的 AxCACHE／AxPROT 差异，以及 bid／bresp／rdata 方向疑似笔误；没有把文档问题判为 RTL 缺陷。

[主说明](../engineering/DDR_GB_Coherence_Design.md)仅补手册依据和未决边界；[Q&A 第 6.1 节](../maintenance/L01/reviews/ddr_gb_coherence_review_qa.md)保存资料核对后的问法调整，独立评审原文不变。Coherency 不支持的作用范围待澄清，不能直接推断跨口读写失效；低功耗确认和上电复位不能直接代替运行中排空契约；DFI 更新超时不能直接代替一般 AXI 事务超时。现有拓扑及维护方向不变。

来源核对在上一答疑轮通过本机临时 PDF 读取库完成，查看了相关表格及架构／复位图原页。本轮依据该核对结果修改文档。只保存授权范围内的接口摘要、页码及原文件哈希，不复制供应商全文、截图或新建手册副本；资料未上传。会议答复、实际交付配置、受控详细指南和控制器动态验证均未取得。

本轮修订前六份 Markdown 已备份，原手册、源码／图稿、范围外修改及上一轮证据共 153 个文件纳入保护哈希，见[输入清单](../maintenance/L01/reports/ddr_gb_coherence_revision/evidence/2026-10-16_datasheet_update/input.json)。本轮检查命令：`python docs_codex/maintenance/L01/reports/ddr_gb_coherence_revision/evidence/2026-10-16_datasheet_update/validate.py`；结果见[validation.json](../maintenance/L01/reports/ddr_gb_coherence_revision/evidence/2026-10-16_datasheet_update/validation.json)。检查本地链接、八章／三图／伪代码与评审原文保留、源文件保护及空白错误。未执行 RTL 构建、仿真、板测、故障注入、浏览器或 Office 检查。上一轮验证报告保持原样，不回填本轮结果。

最小下一步：会议优先确认 Q1/Q2 的跨口时序保证、Coherency 术语和实际属性行为；索取匹配交付版本的 Databook、Integration Guide、Application Guide、寄存器表；再明确错误／排空／局部复位流程并制定验证用例。

## 2026-10-16 时序图与应用流程对应

L01 文档维护；输入 `mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`，含已有未提交文档。用户授权将本轮答疑中的对应关系写入主说明 timeline 部分。仅修改[主说明](../engineering/DDR_GB_Coherence_Design.md)第 6 章图 3 后的说明与本主题交接。

新增应用流程、九项硬件动作与 16 个箭头的对应表；明确输入／输出是 DDR 地址用途，输入同步本身只需覆盖输入，输出准备在设备写入前完成，现图将其提前与输入同步合并展示。图像未标数字，表中按箭头自上而下编号；计算框及图后 CPU 读取另作说明。原图稿、HTML 预览、源码、共享状态与其他文件均未修改。

验证：执行临时 Python 文本／SVG 检查，确认 16 个箭头顺序及编号覆盖、表格三列、八章结构及新增段落之外的主文逐字保留；新增内容无链接及行尾空白，`git diff --check` 通过。修订前两份文件备份位于本机 `/tmp/l01-timeline-bqiyfe_m/`（临时恢复用途）。未运行浏览器、Office 或硬件验证。原硬件实现、DDR 契约和恢复未决项保持；最小下一步为用户按对应表阅读图 3。

## 2026-10-20 SoC v1 文档与图稿同步

**输入与范围。** 用户明确要求实施已审核的 DDR–GB 一致性同步计划；实施前确认分支 `mp/ara-pulp-v2`、HEAD `c9abbb48946fe3a7244bfb3159919b7c9731cb59`。沿用 L01，未启动其他 Agent。已有 AGENTS、共享状态／任务表、E01 交接／计划／检查报告、服务器仿真指南和未跟踪图稿均保留；本轮不写 PROJECT_STATE／AGENT_TASKS，不提交 Git。

**文档修改。** [主说明](../engineering/DDR_GB_Coherence_Design.md)保留八章、三图、27 行原伪代码及 16 步对应表。同步 CPU/Ara2 独立输入共享 M5→GB、M2→LLC→F0，以及 F1 GB 搬运、F2 帧写、F3 ROI 帧读经共享前端到 DDR.S0–S3。增加 LVDS 三类交接，分别说明源帧读完、TX 发完和 CPU 再访问。维护仍针对软件可见的 DDR 逻辑物理范围；缓存行保护与前端压缩块处理分别负责，N＋D 仅表示上游逻辑数据量。

架构规划、IP/DDR 契约、供应商 Q1–Q7、两份综述、GB CPU 专题、软件接口 HTML 内容源及对应生成页同步上述边界。规划说明同时对齐排空顺序、条件性旧回填、冲突脏数据错误出口和 SPM 前进性。总纲／实施难点及两个索引只更新相关完成状态与链接。Q&A／旧 Prompt 各增加当前入口，历史正文保持原文。外部研究案例、论文原图与供应商已有摘要保持原来源，本轮没有重读受控 Datasheet 或取得新答复。

**配图。** 新目录：[2026-10-20_ddr_gb_coherence_v1](../diagrams/2026-10-20_ddr_gb_coherence_v1/README.md)。新作一张一致性专题系统图；16 步时序保留箭头几何与次序，更新编号和 F0/F1／前端完成语义；生命周期和路径比较局部修订。数据版本及三张通用分类 SVG 与原图逐字节相同，图注解释抽象层次。两套原生 PPTX 分别为三页主说明和六页规划／综述，第 1 页共用同一系统图。九页 SoC 主 PPT、全部旧图和旧验证记录保持原件。

**检查与证据。** [输入清单](../diagrams/2026-10-20_ddr_gb_coherence_v1/evidence/input.json)记录 6306 个既有文件哈希，17 个允许修改文件另有修订前备份。命令与预览方式见新图稿 README；[最终结果](../diagrams/2026-10-20_ddr_gb_coherence_v1/evidence/validation.json)包含文件保护、本地链接、原伪代码／评审正文保留、16 箭头及生成页一致性、PPTX 保存重读和 `git diff --check`。

三页 PPTX 含 136 个文本、49 条原生箭头、8 个虚线对象；六页含 250 个文本、113 条原生箭头、5 个虚线对象，均无整图位图。最终 SVG 的 Chrome 整页、最终 PPTX 重读后的整页及系统／时序局部已实际查看；正文浏览器检查覆盖主说明、架构规划、供应商问题和 integration 页面。PPTX 预览是 DrawingML 对象与本地字体近似，不是 Office；Office 显示／编辑未实测。保留首版控制线穿字及 Chrome 沙箱失败记录；随后修正连线并经本机审批渲染成功。系统 Python 缺少 PIL，PPTX 重读改用已安装 skill 环境，未安装依赖。

**待实现与最小下一步。** 本轮完成文档和图稿同步，未修改 RTL、驱动、地址配置或压缩算法，未执行构建、仿真、板测、故障注入或性能测量。供应商四口交付／可见性答复、前端数据与元数据聚合完成／错误、通用范围维护、GB 非缓存配置及恢复协议仍待实现评审。下一轮独立评审使用本次主说明和图稿入口，重点检查 F0→F1/F3、F1→F0/F3、F2→F3 交接以及部分行／部分压缩块、迟到事务和源帧释放；由用户转交，不自动启动评审。
