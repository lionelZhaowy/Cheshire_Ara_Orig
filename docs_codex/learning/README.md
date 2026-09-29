# Cheshire / CVA6 / Ara 中文工程教材

用浏览器打开 [index.html](index.html)：**七篇、30 章，另有首页、六项实验合册和两页参考，共 34 个主页面**。正文、导航和静态 SVG 可用 `file://` 离线阅读，无服务器或 CDN。当前篇默认展开；H2/H3 页内目录可折叠；手机可收起全书目录。关闭 JavaScript 仍能阅读并使用原生目录。

- [本次机制与维护完善](REFINEMENT.md)：重点章节、启动模式与独立证据输出。
- [此前结构修订](STRUCTURE_REVISION.md)：审查回应、当前职责、旧页迁移和内容保护。
- [实验手册](labs.html)：命令、输入、产物、结果判据和失败首查；贯穿同一个数组示例。
- [来源与验证](evidence.html#refinement)：结构检查、此前软件构建和目标环境缺口分开。
- [旧站备份](../learning_backup/index.html)：728 文件原样保留；[哈希清单](evidence/restructure-backup.json)。
- [此前深度扩充](DEPTH_EXTENSION.md)、[09-28 编排设计](CONTENT_REDESIGN.md)为历史范围说明；其中 16 章编号不再定义当前目录。[官方来源](OFFICIAL_SOURCES.md)保留原查阅日期。

## 当前维护入口

在仓库根执行；Python 仅需标准库，浏览器检查与 WaveDrom 生成还需本地 `google-chrome`。只检查现有网页时：

```bash
python3 docs_codex/learning/scripts/check_structure.py
python3 docs_codex/learning/scripts/preview_structure_site.py
```

这两个命令只读教材与历史记录，默认各创建一个随机命名的 `/tmp/l01-*` 新目录并打印路径。`run.json` 保存实际时间、HEAD、工作区状态、输入哈希和输出位置；成功或失败报告留在本次目录。需要保存证据时，以 `--out-dir 新目录路径` 指定位置，目录已存在（即使为空）也拒绝执行，不提供覆盖旧证据的选项。

需要比较生成一致性时显式执行：

```bash
python3 docs_codex/learning/scripts/check_structure.py --check-generated
```

它在临时副本运行生成器，并比较 HTML、SVG、寄存器索引；工作区不会被重新生成。仅当实际修改正文/导航后，才执行下面的**写入操作**更新网页：

```bash
python3 docs_codex/learning/scripts/build_site.py
```

正文编辑 `content/*.html`。`scripts/pages.json` 显式定义 `parts` 和 `pages`：页包含 slug、title、subtitle、kind；正文另含 part 与连续 number。目录、面包屑、节号和上下章均由同一清单生成。H2/H3 必须带唯一语义 id，章号不要写死在标题里；完整层次见生成后的页内目录。

移动旧节时更新 `scripts/anchor_migrations.json`，旧 URL 指向真实新正文锚点。跨页迁移具有脚本跳转和禁用脚本静态链接两种形式；同页别名直接落在对应内容前。`legacy_links.json` 留作历史输入，新生成器使用新迁移表。修改后同时检查目的语义和链接是否有效。

需要修改图或寄存器索引时再运行相应生成器；这些命令明确写入教材资产/内容，不是只读检查：

```bash
python3 docs_codex/learning/scripts/build_diagrams.py
python3 docs_codex/learning/scripts/build_depth_diagrams.py
python3 docs_codex/learning/scripts/build_mechanism_diagrams.py
python3 docs_codex/learning/scripts/build_waves.py
python3 docs_codex/learning/scripts/build_registers.py
```

前两个脚本分别维护 16 张原重构结构图与 13 张深度扩充结构/状态图。新增五张机制结构图由 `build_mechanism_diagrams.py` 维护。6 张时序图编辑 `assets/waves/*.json`，使用本地保留许可证的 WaveDrom 3.5.0 导出 SVG；阅读网页不用加载 WaveDrom。时序图必须标明教学示意或真实运行依据。寄存器索引仍为 12 组/429 项，各组直达关键语义与初始化节；宏不代表读写属性或实际实例数量。

`check_structure.py` 核对备份与本轮修改前的证据/示例/资产哈希、七篇/30章、旧锚点、章号与目标、启动目录、导航/链接；`--check-generated` 另查临时生成一致性。`preview_structure_site.py` 检查桌面/手机、无脚本、迁移与交互。过去 `structure-20260929-*`、`depth-*`、`restructure-*` 保持原样；本次发布证据见 `evidence/refinement-20260929/`，日后检查须使用另一个新目录。

寄存器生成器现在只更新索引，不再写固定日期来源报告；本次检查的 `run.json` 保存教材输入快照，定向 RTL/软件来源另记本次 sources.json。旧内容逐块审计仍保留在此前报告，新检查不再用旧轮次的固定段落序号约束后续教学扩充。

旧 `preview_depth_site.py`、`check_depth.py`、`preview_site.py`、`check_integrity.py`、`record_*sources.py` 属于其日期的历史流程，不作为当前入口，其中部分仍使用旧目录格式。需要重现旧版时在独立旧版本副本中执行，不能用旧记录器覆盖当前证据。更新源码后应另建日期记录，并解释漂移，不改旧哈希掩盖变化。

## 示例与验证边界

`examples/journey.c` 贯穿 13–17、25 章。原 `build_journey.sh scalar spm`、`scalar dram`、`rvv spm` 保留；`JOURNEY_DEPTH=1` 启用尾部/归约输入，`rvv-intrinsics`、`rvv-auto` 比较编程入口，`INJECT_ERROR=1` 生成负例。每次输出到新的目录，已有内容拒绝覆盖。详细环境、命令和验收见实验手册，不为结构修订重复运行构建。

实验 C/D/F 继续复用此前独立示例。原 `lesson.c`、历史模型和生成器保留用于追溯。静态指令、目标执行、数值结果和性能是独立证据；本次只运行文档生成及网页检查，没有软件构建、生产 RTL 仿真或板测。

复制 `learning/` 可阅读教材；源码链接 `../../hw/...` 等需要完整仓库，备份入口需要相邻 `learning_backup/`。生产 RTL、软件、工具链及 FPGA 工程的维护不属于教材生成流程。

报告的 `run.json` 将 `inputs`（内容源、脚本、资产）与 `tested_html`（根目录主页面及兼容 HTML 的 SHA-256）分开记录。浏览器结束前检查被测 HTML 的文件集合和字节哈希未变；历史报告不回填新字段。
