# L01 教材维护资料

返回[用户文档入口](../../00_README.md) · [当前项目状态](../../PROJECT_STATE.md) · [任务表](../../AGENT_TASKS.md)

这里保存“教材如何被规划、修改、评审和验收”的资料，不是用户学习课程。`L01` 是学习/教材任务编号，不是章号。2026-10-08 系统教材扩充涉及软件、OS、ASIC、外设和 Ara 的分工，因此产生了多份作者报告、主管验收和评审文件；它们原先混在 docs_codex 顶层，现在统一归类。

## 应该读什么

- **学习工程**：直接读[主教材 Markdown](../../learning/markdown/index.md)、[配置参考](../../configuration/README.md)、[软件参考](../../software/README.md)、[器件接口参考](../../EXTERNAL_DEVICES_AND_INTERFACES.md)，不必读本目录。
- **Agent 接手维护**：先读当前状态和对应主题 handoff；仅需追溯某次教材修改时，再从本索引选择报告。不能把历史 Prompt 当新授权。
- **追溯 10 月 8 日成果**：从[主管验收](reports/system_acceptance.md)看交付与缺口，再按需读具体作者/评审报告；之后的标题修改由标题报告说明。历史测试计数和截图对应原输入，不代表当前重新通过。

[文档与图稿整理归档](archive/documentation_organization/README.md)保存2026-10-13清理前原件、迁移清单与恢复办法；不进入学习路线。

## 分类索引

| 类别 | 文件 | 用途与当前身份 |
| --- | --- | --- |
| 历史规划 | [旧任务 Prompt](planning/historical_prompts.md) | 原 L01_Next_Tasks_Prompts，给不同 Agent 分配范围/文件/验收的指令草案；相关文档任务已执行，不再作为可直接启动入口 |
| 历史规划 | [系统教材深化规划](planning/system_revision_plan.md) | 软件→OS→ASIC 的内容与分工方案，已有后续实施 |
| 历史规划 | [03–08 专题条件评估](planning/topic_readiness.md) | 解释旧编号专题为什么整合进教材/M01/P01；不是缺少六篇教程的待办 |
| 审查 | [教学质量审查](reviews/teaching_quality.md) | 修改前的问题、改进依据及边界 |
| 审查 | [系统独立复审](reviews/system_independent.md) | 独立审读范围和问题；保留作者自查与独立评审的区分 |
| 实施 | [主管验收](reports/system_acceptance.md) | 汇总分工、修改、实际网页验证及尚未执行的目标验证 |
| 实施 | [软件与 trap](reports/software.md) | 软件章节作者实施与检查 |
| 实施 | [RTOS/Linux](reports/os.md) | OS 教学实施，不等于 OS 移植完成 |
| 实施 | [ASIC 机制](reports/asic.md) | 教材/P01 文档实施，不等于工艺适配完成 |
| 实施 | [外设章节](reports/peripherals.md) | 外设教学调整与范围 |
| 实施 | [Ara/RVV 章节](reports/ara_rvv.md) | 向量教学调整与范围 |
| 实施 | [标题规范修订](reports/title_style.md) | 系统扩充后的标题修改及对应检查 |
| 实施 | [标题润色收尾](reports/title_polish.md) | 后续定向润色，不能回填成前一轮输入的验证 |

## 维护规则与本次精简

2026-10-11：将顶层 12 份 L01 报告和 1 份专题评估迁入 planning/reviews/reports，文件名采用稳定主题，日期保留在内容中；迁移对应见 [path_migrations.json](path_migrations.json)。顶层入口只保留一个维护资料链接。正文、历史输入/结果、未关闭问题保留；仅调整路径和添加历史身份说明。

后续小幅改动只更新主题 handoff，不再同时新建一份顶层实施报告。只有需要承载详细审查、复杂修改对照或独立验收时才在本目录增加/更新专题报告，并从 handoff 链接；不复制报告正文。普通问答进入正式参考文档，需要新增教程时依据用户路线命名，不按 Agent ID 堆到根目录。

原始日志和哈希快照保留在原 evidence/reviews 目录，不是本次清理对象。历史 Prompt 中的“先读”“拥有”“现在实施”等句子属于旧输入，不能覆盖现行 AGENTS、任务状态或用户请求。
