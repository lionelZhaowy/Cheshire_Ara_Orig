# M01 DDR与独立GB需求更新交接

> 记录日期：2026-10-09。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-09；任务M01 DDR需求与接口文档整理。
- 授权：源码分析、需求整理和文档更新；不改生产RTL/sw、配置、filelist、地址图或DDR拓扑，不升级依赖，不运行大型构建。
- 状态：需求文档更新完成；参数待输入，方案未实现、待验证。
- 输入分支：mp/ara-pulp-v2；HEAD `2784340240915fe4338ec54bfd613723b127d62e`。
- 开始git status仅有18条既有未跟踪文档/目录，无tracked diff；保留全部既有文件。其中L01 GB/AXI128交接及4份M01当日交接均为输入。
- 负责路径：本仓库M01契约、本独立交接，及Windows DDR资料主指南。共享状态、任务表、02提取书、AGENTS和地址/配置由协调者合并，本轮不写。

## 本轮结果

- 用户确认：近期主Xbar64以控制适配/验证工作量；接受容量增长、功能优先；NPU256 DDR旁路；GB为独立片上SRAM、NPU/Ara共享中间数据。
- 源码确认：Ara端口32×lane，当前VCU118仍2/2048；filter→converter→Xbar现有路径，普通路径原子位于LLC前；4_lanes预设4096；Debug128功能不兼容、iDMA控制DW缺口、Ara B错误TODO保持开放。
- 设计候选：Ara4的单AXI128出口在收窄前分流，普通路径保持64 Xbar/LLC，GB直达SRAM；优先保留公共filter。NPU在LLC下游合流，Controller实际端口与GB宏组织待定；不是官方完整参考方案。
- 已完成：修订旧CPU/Ara均走LLC概括；新增三类带宽账本、工作负载最小输入、GB资源及所有权/通知/地址/错误契约、G01—G07验收要求；核对三版Word磁盘正文并在主指南§19.9列逐项差异。
- Word发现：V2.0缺独立GB/分流及三类预算；INNO…20260416d仍AXI3/APB2且颗粒/Rank/总容量表内不一致，需供应商澄清。原件未写、锁未动。SHA256及精确字段在Windows主指南§19.9.2。
- 未完成：未生成新Word版本、未做Word布局验收，未实施GB/分流/旁路或选型冻结。

## 改动与接口

- `docs_codex/engineering/IP_DDR_Interface_Contract.md`：开篇更新基线，§1/§2修订路径，新增§12需求/源码/候选/输入/验收。
- Windows `D:/Personal_Files/科研任务/5.3-项目-大面阵短波红外视觉芯片/20260428-DDR PHY/docs_codex/DDR3控制器IP接口梳理与CVA6集成指南.md`：v2.4，修正开篇和历史候选适用范围，新增§19.9及Word差异；Windows资料不复制到源码仓库。
- 本交接独立新增；旧交接原样保留。配置/profile/宏/地址/中断/位宽实际改动：无。
- 文档供C00/E01/I01/S01/V01/P01接收；GB01—06、DDR01—03是待填写的契约，非现有端口声明。
- 未提交；仓库相对链接可随仓库搬迁，受控Windows资料需保留原位置或重新定位。

## 验证证据

- 工具：Windows PowerShell只读OOXML及WSL Git 2.43.0、Python 3.12.3轻量文档处理。
- 工作目录：`/home/zhaowenyao/RISC_CVA6_prj/cheshire_ara`。执行 `git status --short`、`git branch --show-current`、`git rev-parse HEAD`；读取根AGENTS、PROJECT_STATE、AGENT_TASKS、HANDOFF_TEMPLATE、M01契约及指定L01交接；未审计全仓库。
- 定向源码命令示例：`sed -n '602,610p;815,891p' hw/cheshire_soc.sv`；`sed -n '417,438p' .bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/vlsu/vstu.sv`；`cat .bender/git/checkouts/ara-2c7b103275a16c87/config/4_lanes.mk`。另核Debug CSR/SBA、iDMA wrapper/reg顶层和VCU118加源宏。
- 默认沙箱进程启动失败，改经批准的受限目的命令访问成功；WSL无rg，改用cat/sed限定读取。一批含rg的命令退出1，后续重读成功。
- Word初始OpenRead受在用共享模式阻止，改FileAccess.Read+FileShare.ReadWrite读取内存快照成功；未结束Word进程、未删锁、未写Word。结果不包含用户未保存编辑。
- 写入前哈希保护：M01契约 `1a9a7b4ce735bf73e98dda5566603fb1a277a7a3e044ea92cec863c440cdf731`；Windows主指南 `ee61657d15243410e9b2f27bba3f28a216c863ee169f260299d24aabb4b3e1ef`；不一致即拒绝覆盖。
- 写入后 `git diff --check` 退出0；`git diff --name-only` 仅M01契约；新增仅本交接。25个可直接解析的本地链接目标存在，三份文档UTF-8/代码围栏和新增需求/验收ID检查通过；HEAD未变，既有18条未跟踪项保留。此为文档检查，不是硬件测试。
- 原Word和V2.0的收尾SHA256与读取前一致。INNO…20260416d在其他进程编辑期间从76cf…变为547c…，随后重新只读完整表格，协议与容量问题仍存在；最终快照和边界已同步主指南。本轮未覆盖或撤回该外部变更。
- 未编译、未展开、未仿真、未板测、未综合或ASIC签核；源代码条件代入不是运行结果。未重查厂家PDF全文，既有速率/混合能力仍按前次资料证据，不增厂商承诺。

## 决策与下一步

- 用户已确认的最新决定来自2026-10-09本轮指令及L01 GB交接；主Xbar64不因Ara4候选自动改变，VLEN和固定提取基线不变更。
- 尚待输入：模型与算子/tensor、GB容量/bank/端口/时钟、搬运引擎、计算搬运重叠、CPU是否直访、DDR流量及供应商manifest。最终速度/通道/容量/频率不冻结。
- 下一步最多四项：I01/算法填写§12.5最小输入；M01按三账本预算并询厂商真实组合；S01/P01/V01填写GB可见性/错误/时钟和验收；参数与Word编辑版本协调后另存新Word并列差异。
- 最少读取：M01契约§12、本交接、L01 GB与AXI128交接；Windows需求表审阅用主指南§19.9。
- 需C00合并：PROJECT_STATE/AGENT_TASKS中CPU/Ara概括细化、近期主Xbar64及独立GB确认、4-lane/VLEN尚未冻结、Debug128与iDMA/Ara错误边界；AGENTS/02的旧概括按相同规则解释，但不能将原提取基线改4-lane或把方案标已实现。
