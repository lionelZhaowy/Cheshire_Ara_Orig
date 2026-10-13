# Agent 文档定位与历史检索指南

本页用于快速找到有效结论和历史依据，不替代[根 AGENTS](../AGENTS.md)、源码或测试。更新：2026-10-13。

## 1. 最短接手路线

1. 读 [PROJECT_STATE](PROJECT_STATE.md)：当前方向、已确认需求、未验证项。
2. 读 [AGENT_TASKS](AGENT_TASKS.md) 对应任务行及其主题交接，确定本次范围；任务表不是授权或文件锁。
3. 根据下表只读需要的正式文档，再定位定义、实例及消费者；执行前核对 HEAD、git status 和涉及文件。
4. 只有缺少决策依据或需要复核过去结果时，继续追溯交接、维护报告和原始证据。不要默认通读 handoffs、扫描整个 .bender 或重跑旧 Prompt。

## 2. 问题到入口

| 要找什么 | 首选入口 | 必要时追溯 |
| --- | --- | --- |
| 学习顺序、教程 | [00_README](00_README.md)、[Markdown 教材](learning/markdown/index.md) | [教材维护说明](learning/README.md)，了解源文件与生成关系 |
| RTL 模块内部机制、信号与源码 | [21篇模块指南](rtl_modules/README.md) → 对应章节 | [主题交接](handoffs/L01_rtl_module_guide.md)；正式采用 A，B/C 不进入阅读路线 |
| 参数和配置 | [配置参考](configuration/README.md) | 当前 package、选中的 CPU profile、目标构建覆盖 |
| 软件/工具/API | [软件参考](software/README.md)、[层次工具索引](software/LAYERS_AND_TOOLS.md) | HAL/DIF、sw.mk、crt0、链接脚本 |
| 器件、接口、仿真对端 | [接口实现参考](EXTERNAL_DEVICES_AND_INTERFACES.md) | SoC、VIP、fixture、TB、FPGA top，避免把模型存在当通过 |
| ASIC 提取 | [02 提取规格](02_Cheshire_Ara_ASIC_Extraction_Handoff.md) | E01 交接、最新实际输出目录 |
| 启动、PLL、Platform ROM | [03 平台约定](03_Platform_ROM_Clock_IP_Configuration.md) | S01-B01 任务、Platform ROM 缺陷与用户决策交接 |
| DDR/GB/新增 IP 契约 | [工程参考索引](engineering/README.md) → IP/DDR | M01 需求更新、接口可行性记录；区分用户决定与建议 |
| SRAM/PHY/PAD/DFT | [ASIC 适配参考](engineering/ASIC_Adaptation_and_Evidence.md) | P01 输入和供应商授权资料位置 |
| 上个 Agent 改了什么 | [handoffs 索引](handoffs/README.md)，再按任务/主题搜 | 主题文件头修改记录、输入版本、改动路径、未关闭项 |
| 教材为什么这样改 | [maintenance/L01](maintenance/L01/README.md) | planning / reviews / reports；原 Prompt 是历史，不是现授权 |
| 某次测试到底通过什么 | handoff/报告引用的具体 evidence 或 reviews 文件 | 命令、退出码、输入哈希、工具和日志；本轮没跑不能记为重新通过 |

## 3. 有限范围检索示例

在仓库根执行，只读查询：

```sh
# 先找任务主题，而不是把所有日志全文读入上下文
rg --files docs_codex/handoffs | rg '/(M01|P01|S01|V01|E01)_'

# 定位某个决策/缺陷的记录，再打开命中章节及其引用
rg -n 'S01-B01|Platform ROM|返回路径' docs_codex/PROJECT_STATE.md docs_codex/AGENT_TASKS.md docs_codex/handoffs
rg -n 'GB|主Xbar|256|用户确认' docs_codex/engineering/IP_DDR_Interface_Contract.md docs_codex/handoffs/M01_*.md

# 查看当前版本和待修改文件；不要用还原/清理消除已有改动
git rev-parse HEAD
git status --short
```

文件名改过时先查映射：

- [handoff 名称迁移](handoffs/name_migrations.json)：日期前缀 → 任务主题名。
- [教材维护报告迁移](maintenance/L01/path_migrations.json)：原顶层 L01/03–08 文件 → 分类目录。
- [本次图稿与入口精简](maintenance/L01/archive/documentation_organization/manifest.json)：B/C 资产的原路径、哈希、归档成员和恢复来源。原始检查中的路径通过该清单追溯。
- [工程参考迁移](engineering/path_migrations.json)：原 M01/P01 顶层文件 → engineering。

原始日志/哈希快照里的旧路径是当时记录，不能为匹配新目录而改写验证输入。映射只解释“今天文件在哪里”，不证明当前内容仍等于历史被测版本。三个 handoff 旧名符号链接仅为归档导航兼容，新文档不要继续引用旧名。

## 4. 怎样判断结论是否仍有效

- 优先当前明确需求；实现事实以当前源码和匹配配置的测试为准。正式文档是检索入口，不天然比旧记录更正确。
- 对照记录的输入 HEAD、未提交变更、配置、日期及作者/独立评审身份。文件名新旧、修改时间或“完成”二字都不能代替核实。
- 作者实施报告、独立评审、主管验收分别说明各自范围；不能将作者自查当独立通过，或把网页检查当 RTL/板测。
- 遇到冲突，记录两边来源、当前源码证据和仍缺的测试；已修正的结论标明替代关系，不为一致而删除原失败日志。
- 只读需要的片段和直连证据；确认版本差异后再做定向复核，不重复全仓审计。

## 5. 新内容写在哪里

| 内容 | 位置与规则 |
| --- | --- |
| 用户需要长期查阅的解释 | 正式教程/参考文档，同主题更新，保持单一主要说明 |
| 接口条件、设计约束和实施输入 | engineering 或现有 02/03 专题，保留任务归属与未决状态 |
| 变更、决策、缺陷、验证、阻塞 | handoffs/<任务ID>_<主题>.md；头部追加修改记录，不逐轮新建 |
| 复杂教材规划/评审/实施对照 | maintenance/<任务ID>/planning、reviews、reports；handoff 只链接 |
| 原始验证产物 | 对应 evidence/reviews 的独立输出，保留输入身份，不覆盖旧证据 |
| 纯重复解释 | 无需新增 handoff；若纠正事实，更新正式说明及必要的主题记录 |

共享状态只概述重要变化并给链接，不再复制整份报告。历史 Prompt 和任务表中的待办不能自动转化成执行授权。
