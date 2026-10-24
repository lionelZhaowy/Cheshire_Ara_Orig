# 图稿目录索引

更新：2026-10-18。按内容查图；“正式配图”表示文档正在使用，不表示对应硬件已经实现或验证。**文件夹没有被正文直接链接，也可能是生成依赖或用户单独使用的 PPT。**

## 常用入口

- **当前 SoC 架构 v1**：[第9页预览](2026-10-16_soc_landscape_m5_gb/soc-architecture-v1.png) · [九页主PPT](2026-10-16_soc_landscape_m5_gb/soc_landscape_m5_gb.pptx) · [实施总纲](../engineering/SoC_Architecture_v1_Master_Plan.md)。
- **RTL 模块内部机制**：[A 图总览](2026-10-13_rtl_module_comparison/index.html) · [21篇正文](../rtl_modules/README.md)。
- **软件栈**：[全组件软件栈](2026-10-13_complete_software_stack/README.md) · [软硬件分层](2026-10-09_software_hardware_layers/README.md)。
- **DDR–GB 同步**：[v1 当前图稿](2026-10-20_ddr_gb_coherence_v1/README.md) · [说明正文](../engineering/DDR_GB_Coherence_Design.md)。
- **实施难点**：[13幅图](2026-10-18_implementation_challenges/README.md) · [专题正文](../engineering/Implementation_Challenges_and_Open_Questions.md)。

## 主目录：正文配图、独立交付及依赖

| 文件夹 | 用途 | 图片内容与保留原因 |
| --- | --- | --- |
| [2026-10-09_software_hardware_layers](2026-10-09_software_hardware_layers/README.md) | 正式配图 | 软硬件分层、源码与工具对应；LAYERS_AND_TOOLS 正文使用。 |
| [2026-10-11_native_reconstruction](2026-10-11_native_reconstruction/README.md) | 共享来源 / 独立图集 | 37 张教材结构图、8 张独立图的原生重建，另有完整 SoC 图；工业版的输入来源。 |
| [2026-10-12_axi_to_detailed_mem](2026-10-12_axi_to_detailed_mem/README.md) | 生成依赖 | AXI→详细存储接口的请求、fork/metadata、stream_to_mem、bank/port；A 图经 Regbus 脚本导入其绘图工具。 |
| [2026-10-12_industrial_redraw](2026-10-12_industrial_redraw/README.md) | 共享来源 / 独立图集 | 9 张工业风格图：Crossbar、DDR、初始化、程序执行、软硬件层次、LLC/SPM、完整 SoC 等。后续一致性图复用底图。 |
| [2026-10-12_regbus_ip_integration](2026-10-12_regbus_ip_integration/README.md) | 生成依赖 | Regbus 全路径与自有 IP 寄存器封装两图；正式 A 图复用布局。 |
| [2026-10-12_rtl_modules](2026-10-12_rtl_modules/README.md) | 生成依赖 / 前版 | 原 17 章、20 图版本；正式 A 图仍导入其布局脚本，不能因正文改用 A 而整目录归档。 |
| [2026-10-13_complete_software_stack](2026-10-13_complete_software_stack/README.md) | 正式配图 | 全组件软件栈、裸机/主机工具/可选 Linux 分路，39 类组件；软件接口教材使用。 |
| [2026-10-13_foundation_software](2026-10-13_foundation_software/README.md) | 正式配图 | 基础软件/BSP、HAL/DIF、驱动及主机工具；软件接口教材使用。 |
| [2026-10-13_nonvolatile_storage](2026-10-13_nonvolatile_storage/README.md) | 独立交付 | eMMC 与 SPI NAND 选型汇报；当前为 revision_03（3.3 V PAD），保留早期修订用于追溯。 |
| [2026-10-13_rtl_module_comparison](2026-10-13_rtl_module_comparison/README.md) | 正式配图 | 21 篇 RTL 指南的 24 张 A 连续走线图、213 条连接；SVG/PNG/PDF/24 页原生 PPTX。B/C 已退出正式流程。 |
| [2026-10-13_software_hardware_interfaces](2026-10-13_software_hardware_interfaces/README.md) | 正式配图 | 启动/装载、UART、DMA、Ara 四个软硬件接口案例。 |
| [2026-10-15_edge_llm_os](2026-10-15_edge_llm_os/README.md) | 正式配图 | 裸机/RTOS/Linux 软件栈及一次边缘推理任务的软硬件协作。 |
| [2026-10-15_global_buffer_cpu_access](2026-10-15_global_buffer_cpu_access/README.md) | 正文比较参考 | CPU 不直达 GB 与 CPU 可达 GB 两种方案；正文仍引用作历史比较，现行 v1 采用共享 M5。 |
| [2026-10-16_cache_coherence](2026-10-16_cache_coherence/README.md) | 生成依赖 / 前版 | 早期逐行协调图及 industrial-base 底图；当前 hybrid、DDR–GB 说明等生成器仍读取。 |
| [2026-10-16_coherence_comparison](2026-10-16_coherence_comparison/README.md) | 生成依赖 / 前版 | A～F 一致性方案的统一布局比较；hybrid 生成器仍复用其代码，旧推荐状态已被替代。 |
| [2026-10-16_coherence_hybrid](2026-10-16_coherence_hybrid/README.md) | 前版 / 生成依赖 | 10月16日维护与分类图；当前专题采用10月20日v1版，原件和生成依赖保留。 |
| [2026-10-16_coherence_survey](2026-10-16_coherence_survey/README.md) | 正式引用 / 外部原图 | Cohmeleon、NVDLA、Gemmini 等四张来源图及出处；综述仍使用，保留来源与证据。 |
| [2026-10-16_cpu_npu_inference](2026-10-16_cpu_npu_inference/README.md) | 正式配图 | 模型部署全链、CPU/NPU 分工、运行时提交及异构推理系统。 |
| [2026-10-16_ddr_gb_coherence_design](2026-10-16_ddr_gb_coherence_design/README.md) | 前版 / 校验输入 | DDR–GB 同步说明的系统、版本快照、时间线三图；后续 review 版本引用其证据和前版校验输入，保留。 |
| [2026-10-16_ddr_gb_coherence_review](2026-10-16_ddr_gb_coherence_review/README.md) | 前版 / 生成依赖 | 10月16日评审输入及三图；旧三口系统图由v1专题替代，原件/预览/证据保留。 |
| [2026-10-20_ddr_gb_coherence_v1](2026-10-20_ddr_gb_coherence_v1/README.md) | 当前一致性配图 | v1共享M5与四口前端专题图、16步时序、生命周期/路径比较；主说明三页和规划/综述六页原生PPTX。 |
| [2026-10-16_global_buffer_shared_xbar](2026-10-16_global_buffer_shared_xbar/README.md) | 正式配图 | CPU/Ara 独立 master 经主 Xbar 共用 GB 出口；Global_Buffer_CPU_Access 正文采用。 |
| [2026-10-16_soc_landscape_m5_gb](2026-10-16_soc_landscape_m5_gb/README.md) | 当前架构图 | 用户手调的九页主 PPT；显示顺序第 9 页为 SoC 架构(v1)，使用 soc-architecture-v1.png/svg 预览。旧页与修订证据保留。 |
| [2026-10-18_implementation_challenges](2026-10-18_implementation_challenges/README.md) | 正式配图 | SoC v1 十三类实施难点，13 张 SVG/PNG 与13页原生 PPT；对应实施难点专题。 |

根目录的 [soc_landscape.pptx](soc_landscape.pptx) 是用户提供的原始全景 PPT 输入，保留；当前 v1 主文件见上方入口。

## backup_no_use：历史备份与少量历史来源

**此目录不是可直接删除的缓存。**仍有历史说明、对照页、原始哈希和重建输入引用其中材料；下面逐项标出。正式正文直接嵌图的三组目录及 A 图绘图依赖已移回主目录。本次只迁移/修复路径，没有重新绘图、裁切 PPT 页面或删除图片。

| 备份子目录 | 内容及当前身份 |
| --- | --- |
| [2026-10-06_axi_crossbar_ara](backup_no_use/2026-10-06_axi_crossbar_ara/) | 早期 AXI Crossbar 与 DDR 多端口建议；历史重建仍读取其中母版，不能删除。 |
| [2026-10-06_svg_pptx_skill_validation](backup_no_use/2026-10-06_svg_pptx_skill_validation/) | 旧 SVG→PPTX 转换试验、Office 检查截图和格式验证。 |
| [2026-10-08_boot_initialization](backup_no_use/2026-10-08_boot_initialization/README.md) | 旧版初始化硬件/软件对应与程序执行图；仍是历史重建输入。 |
| [2026-10-10_ddr_lvds_isp_gb](backup_no_use/2026-10-10_ddr_lvds_isp_gb/) | 早期 DDR/LVDS/ISP/GB 拓扑；历史重建输入，不代表当前 v1。 |
| [2026-10-10_llc_cache_spm](backup_no_use/2026-10-10_llc_cache_spm/README.md) | 旧 LLC/Cache/SPM 母版与导出；历史重建输入。 |
| [2026-10-10_publication_figure_research](backup_no_use/2026-10-10_publication_figure_research/README.md) | 出版图稿方案调研与来源记录，没有当前正文配图。 |
| [2026-10-11_native_pptx_validation](backup_no_use/2026-10-11_native_pptx_validation/README.md) | 原生箭头/虚线/PPTX 后端试验与 skill 源码快照；历史验证读取其原始哈希。 |
| [2026-10-12_regbus_rtl](backup_no_use/2026-10-12_regbus_rtl/README.md) | Regbus bridge/译码深图与原生合辑；指南已使用 A，但旧分析可追溯。 |
| [2026-10-12_regbus_structure](backup_no_use/2026-10-12_regbus_structure/README.md) | 早期 Regbus 结构分析图，后续接入说明和 A 图已承接正式阅读职责。 |
| [2026-10-12_soc_landscape](backup_no_use/2026-10-12_soc_landscape/README.md) | 早期 SoC 全景及 C1～C9 控制窗说明；软件教材仍链接它解释旧规划编号，已迁移链接。 |
| [2026-10-13_rtl_modules_native_c](backup_no_use/2026-10-13_rtl_modules_native_c/README.md) | C 试绘的迁移提示与原验证证据；图稿实体已在10月13日集中压缩归档。 |
| [2026-10-14_software_stack_industrial](backup_no_use/2026-10-14_software_stack_industrial/README.md) | 本次归档：工业风格软件栈候选；正文仍采用10月13日全组件版本，未宣称用户否定此候选。 |
| [2026-10-15_cache_coherence](backup_no_use/2026-10-15_cache_coherence/README.md) | 本次归档：早期 DDR–GB 一致性三图；正文已改用10月16日方案图。 |
| [2026-10-16_soc_landscape_shared_gb](backup_no_use/2026-10-16_soc_landscape_shared_gb/README.md) | 本次归档：两页共享 GB 全景修订；后续主 PPT 已发展为 m5_gb 九页版本。 |
| [backup_skill_publication](backup_no_use/backup_skill_publication/) | 旧 publication-figures 试绘：Crossbar、启动、软件层次、DDR/GB、LLC/SPM 和可搬迁 skill 快照。 |

备份中的旧生成/检查脚本按当时目录布局和输入编写，是历史快照；不作为当前默认工作流。需复核时在独立临时目录恢复相应布局，不能重跑旧脚本覆盖当前手调 PPT。主目录的原生重建入口已支持归档路径解析，源码哈希不刷新。

当前路径见 [path_migrations.json](path_migrations.json)；原始日志/清单中的旧路径保持原样，通过映射追溯。`evidence/`、旧页及逐轮检查预览保留在各自图稿目录，避免破坏输入身份；当前图不因目录含大量过程图片而整批归档。整理范围、备份与检查见[既有主题交接](../handoffs/L01_documentation_organization.md)。
