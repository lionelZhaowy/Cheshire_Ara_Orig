# M01/I01/S01/P01-AR / Cheshire扩展架构审查

## 基本信息

- 日期：2026-10-11。用户授权：依据当前源码/配置/架构图和外购IP资料完成架构审查，新增报告、图、可复算脚本；不改功能源码、不跑大型构建、不提交推送。
- 状态：**审查交付完成；建议方案未实现，目标动态验证待执行，产品参数待输入。**
- 输入分支 `mp/ara-pulp-v2`，HEAD `2784340240915fe4338ec54bfd613723b127d62e`。初始已有大量教程/M01文档修改及未跟踪图；独立保护记录包含533个既有文件。
- 本轮负责：`docs_codex/reviews/2026-10-11_architecture/`及本交接。主Agent汇总；子Agent分别只读核缓存/启动ASIC，并在独立子路径开发预算工具，无生产文件编辑。

## 本轮结果

- [完整报告](../reviews/2026-10-11_architecture/Architecture_Review_Report.md)及[离线HTML](../reviews/2026-10-11_architecture/Architecture_Review_Report.html)，覆盖五条端到端链路、接口/配置、数据所有权、GB/DDR预算、17项分级风险和13组待执行验证、首版取舍。
- 源码确认：当前向量profile为WT L1D，LLC按地址/ways决定旁路，不使用AxCACHE；本地官方架构文档相应说法与依赖实现不同。仅fence或CPU不缓存不能使LLC共享数据自动可见。
- 方案建议：普通RAM继续经LLC；缩短正常LLC/PMA窗口，尾部NC保留池经独立外部AXI从口在DDR侧合流，同PA单一路由、禁止缓存别名/共享原子对象。未冻结地址/容量，未改配置。
- 方案建议：GB仍为独立SRAM，首版用系统external slave64 + NPU本地bank仲裁，使CPU/Ara/iDMA可达；Ara4/128独立分流和ISP全面共享GB先延期。当前2lane出口本来64。
- 源码/生成指令确认：Platform ROM普通返回缺陷仍在；iDMA Reg64/32适配与HAL宽读缺陷、Ara写B错误TODO仍开放；另外确认ZSL忽略载荷读取返回值。报告区分真实缺陷、条件风险与信息缺口。
- 原始资料确认：本轮只读受控Windows DDR PDF/三版Word，通用系列有AXI4/混宽能力，但实际交付RTL/PHY/模型/manifest未取得；AXI/APB不同草案必须统一。没有上传/复制受限原文。
- 量化结论：12000²×30×16-bit一次DDR写8.64 GB/s，一写一读17.28 GB/s，已超过单通道x64 DDR3-2133理论17.064 GB/s。用户未新增确认其为硬指标，仍是压力场景；不将其判为当前功能P0。
- 未完成：RTL集成、Platform ROM/iDMA修复、真实DDR初始化、目标仿真/Linux/板测、55nm工艺映射或签核。本次没有将建议升级为用户决定。

## 改动与接口

- 新增报告MD/HTML、两张SVG+PNG、原生可编辑PPTX、计算JSON输入和Python脚本、验证日志/哈希。完整清单由新目录自身保留。
- [推荐关系图](../reviews/2026-10-11_architecture/figures/recommended_integration.png)及[SVG](../reviews/2026-10-11_architecture/figures/recommended_integration.svg)；[当前图](../reviews/2026-10-11_architecture/figures/current_implementation.png)。图用实线/虚线区分当前和待实现。
- [计算脚本](../reviews/2026-10-11_architecture/scripts/budget.py)、[可配置输入](../reviews/2026-10-11_architecture/inputs/budget_inputs.json)、[预算结果](../reviews/2026-10-11_architecture/results/final/budget.md)。数值来源分资料/假设/实测；当前无目标吞吐实测值。
- 配置/profile/RTL/寄存器/地址图/filelist/驱动/供应商资料变更：无。未提交、未推送。
- 依赖接收：E01/V01/S01/M01/I01/P01；C00汇总本审查进展，不将工程实施状态改为完成。

## 验证证据

- 详见[执行记录](../reviews/2026-10-11_architecture/evidence/validation.md)及[源码快照](../reviews/2026-10-11_architecture/evidence/source_snapshot.json)。定向rg/nl/sed和官方页面核对；生成ROM重抽取2048字/8192B，objdump退出0。
- `PYTHONDONTWRITEBYTECODE=1 python3 docs_codex/reviews/2026-10-11_architecture/scripts/test_budget.py`：**11项通过**；确定性逐字复算通过、已有结果拒绝覆盖通过，见`results/self_check.json`。
- `python3 docs_codex/reviews/2026-10-11_architecture/tools/render_report.py`及`tools/check_artifacts.py`：HTML生成、49个本地链接/锚点、两组SVG/PNG等检查；最终数值以`evidence/artifact_checks.json`为准。
- 采用[svg-pptx-diagrams-native技能](/home/zhaowenyao/.codex/skills/svg-pptx-diagrams-native/SKILL.md)生成原生箭头/虚线与可编辑文字。SVG/PPTX结构检查通过，PNG视觉查看，HTML桌面/窄屏首屏预览；Office实际编辑未验证。
- 当前PATH有Questa2024.1，无vcs/vlogan；这不表示目标服务器未安装或VCS2018必不能运行。没有生产compile/elaborate/sim/板测/综合/STA结果。
- **并行边界：** 首次输入保护检查发现其他对话修改教程/旧图及新增其他交接，已保留原观察记录，未回滚/覆盖；因此不报告“全部既有文件字节不变”。本轮受审的32个关键源码哈希保持、生产hw/sw/target/.bender无tracked diff；最终观察见artifact_checks。共享PROJECT_STATE/AGENT_TASKS/交接索引留给协调者合并，避免在活跃文档重构期间覆盖。

## 决策与下一步

- 本次继承：DDR目标AXI4、55nm、CentOS/VCS2018、保留FPGA与静态清单迁移方向、Linux硬件条件；本轮没有新冻结性能/GB/DDR端口参数。
- 待用户/IP方输入：首版硬负载、Dremi/NPU包含关系与已有DMA/端口、ISP算法与LVDS峰值/反压、供应商实际交付manifest、55nm宏/PHY/PAD视图。
- 最小继续步骤：
  1. E01固定向量配置/清单，V01在目标VCS2018做分层小探针；S01处理已授权后才可实施的ROM/iDMA定向修复。
  2. I01/算法填写真实tensor与接口，M01/S01冻结NC池/GB/PMA/完成错误契约；供应商对齐AXI4/APB实际版本。
  3. 新建代理master验证NC数据交接、错误/复位与GB争用，再接真实IP；执行报告V01–V13，不把本轮计算当性能验收。
  4. 用真实负载重跑budget并选择减少落帧/分块驻留/ROI或DDR组织；宏/PHY资料齐后推进ASIC适配与物理验证。
- 最少阅读：主报告§1、§4.3、§6、§7、§8，以及inputs/README；无需重读整套教程。
- C00待合并：联合架构审查交付完成；LLC AxCACHE文档差异、NC同PA池/GB slave64为本轮建议；DDR实际交付仍待输入；11项仅公式测试、硬件验证均未新增。原E01/S01-B01/M01/I01/P01工程状态保持。
