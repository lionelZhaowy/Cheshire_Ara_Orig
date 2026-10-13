# L01 / 文档目录分类与精简

## 修改记录

| 日期 | 输入 / 角色 | 修改 |
| --- | --- | --- |
| 2026-10-13 | `5a1338e0a0bf115ddd54c19e0ae367ac2d541892` / `mp/ara-pulp-v2`，L01 文档整理 root；无子 Agent | 正式入口收敛到 A；归档224个B/C产物及脚本，删除2个字节码缓存；共享状态精简，修复28项历史路径映射，活动文档检查通过 |
| 2026-10-11 | eaf55be17，L01 本对话；保留前轮命名迁移及用户未提交文档 | 用户要求解释并归类顶层 L01 文件；13 份过程资料迁到 maintenance/L01，收敛用户入口，更新 AGENTS 存放规则 |
| 2026-10-11 | 同 HEAD 与本对话变更 | 用户补充要求 M/P 统一处理及新 Agent 历史定位：两份现行工程参考迁入 engineering，新增 Agent 定位指南并接入 AGENTS/00/状态 |
| 2026-10-11 | 同 HEAD 与本对话变更 | 用户授权删除 learning_backup 及独占资源；728 文件移出仓库，移除现行页面备份入口并同步生成，保留共享资源和独立证据 |

## 当前结果（2026-10-13）

- 正式入口：[文档总览](../00_README.md)、[RTL模块指南](../rtl_modules/README.md)、[工程契约](../engineering/README.md)。A 连续走线是最终决定；B 弃用、C 未采用，均已退出正文与默认维护流程。
- 共享状态从145行收敛至89行，任务表从92行收敛至68行；历史过程与旧任务Prompt保存在整理前快照，日期/输入/失败及未关闭项继续由原主题交接和证据承担。没有合并或改写不同轮次的验证。
- 清出展开工作树并压缩归档 **224文件**：B图稿/导出124、C图稿/导出98、C历史生成/验证脚本2；另删除 **2个**已备份的无独有内容Python字节码缓存。没有不可恢复地删除独有图稿。
- 集中备份：[归档与恢复说明](../maintenance/L01/archive/documentation_organization/README.md)、[机器清单](../maintenance/L01/archive/documentation_organization/manifest.json)。主归档273成员，补充链接修复备份15成员；包括未跟踪/忽略文件。原始C验证/视觉/渲染清单和evidence留在原处，B对应的原记录也不改字节。
- 21篇正文仅替换24处图览链接及24处查线说明；所有技术段落、213条连接表、源码链接和A图像保持不变。新增A独立检查；原verify_comparison命令转调A，不刷新历史报告。已移除不可达的B生成代码；C旧脚本仅在归档中。
- 两个早期布局目录完整保留；正式A目录124个静态文件、engineering四文件、本次前已有2632个evidence文件均按起始哈希保持不变。provisional A/B导出、早期可编辑图稿及PPT锁文件未操作：前两类可能含修订/人工编辑，锁文件为外部Office占用状态，不作为静态产物清理。
- 额外修复28项不同的旧链接映射：01任务表拼写、native_reconstruction改名、publication图稿归档增加目录层级；同步旧图入口中的当前复现命令。未重建旧目录或learning_backup。旧已知断链列表清空，原列表保存于补充备份。

## 本次检查、失败修正与边界

输入开始时Git仅有 `docs_codex/diagrams/2026-10-12_rtl_modules/export/~$diagrams.pptx` 未跟踪；未发现需要覆盖的并行文本修改。写入仅限 `docs_codex/` 的文档、图稿导航/维护脚本、归档和清单。没有使用git clean/reset、切换分支、提交、修改RTL/sw/配置/依赖/工程构建脚本或执行硬件构建。

- `python3 -B docs_codex/learning/scripts/check_site.py`：通过71 HTML页面、5078本地HTML链接/资源、108 SVG XML、51份Markdown与源一致性及全部Markdown链接/锚点。最终确切计数见[检查结果](../maintenance/L01/archive/documentation_organization/validation.json)。
- publication-figures已有venv运行 `verify_a.py --output <新报告路径>`：21章、24图、213连接、78项源码哈希、176源码行号、24份矢量PDF、24页PPT/1548原生对象通过，几何发现0。24张PNG与历史实际看图哈希一致；**本次未重新人工看图或复核RTL功能**。
- `build_comparison.py --navigation-only`：正文导航和A图览生成幂等；图源未重新批量生成。定向读取早期布局并重建24组节点/边清单，与现清单一致；仅在/tmp生成Regbus及DDR/LVDS两份SVG，逐字节等于现有A母版。五份活动Python脚本语法通过。
- 归档逐成员解读并核对哈希；技术正文与清理前备份比较，只允许上述两类文字替换；历史验证/证据哈希不变。新检查将B/C残留路径限于原始快照、归档映射和禁止项检查，不留活动依赖。
- 首轮A检查把Serial Link正文的 `AW/W/B/AR/R` 误认为B路径，已缩小为实际图稿目录匹配；该失败报告保存在本次检查结果中。全站首轮发现旧断链及三处本地官方Markdown源码的 `#L` 被误判为标题，已修复导航并让检查器验证实际行号。链接批处理首轮重复替换了同一目标，导致多一级 `../`，已从备份按唯一映射修正并复查通过，未掩盖为原检查通过。
- `git diff --check`通过；除文档目录外无Git差异。Office显示/编辑、浏览器交互、生产仿真、板测、签核均未执行。下文10月11日失败和未关闭记录保留为当时结果；本次链接修复只关闭导航问题，不替代历史结构检查或生产验证。

收尾观察到外部锁文件变化：初始旧RTL图目录的锁文件消失，正式A目录出现新锁文件；本任务未操作锁文件，已从静态保护断言中排除。最终PPT本体哈希仍一致。归档检查首轮还将26个已归档JSON误列为须原地保留，已按操作清单改为校验其归档成员；首轮失败条目保存在本次检查结果中。

最小下一步：阅读正式入口即可；后续维护用A独立检查。独有旧图/原生导出如需进一步删减，先核实用户编辑情况；不因本次归档自动获得绘图、源码修复或提取授权。

## 2026-10-11 交付与范围（历史）

- [维护索引](../maintenance/L01/README.md) 是统一入口，分类为 planning/reviews/reports；12 份 L01 文件加 03–08 专题条件评估迁入，原日期保留正文，名称改为稳定主题。
- 旧 Prompt 是已执行历史任务定义，不是新任务授权；报告是教材修改和文档检查，不是新增用户教程或生产 SoC 验证。
- 根 AGENTS、00_README、PROJECT_STATE、AGENT_TASKS、handoffs/README 更新职责/入口。其他受影响 Markdown/HTML 仅迁移链接/路径；搬迁文件内部相对链接重算。
- M01/P01 是现行工程契约/适配参考；首轮保留，后续按用户要求迁至 engineering（非历史归档）。用户 01 正文仅在有旧路径引用时作机械替换，不删除其其他修改。
- 唯一 evidence 内编辑为 title-style-20261008/README.md 的报告导航链接；原日志/哈希/截图和内容快照未改。历史原始快照中旧路径可结合 [迁移表](../maintenance/L01/path_migrations.json) 追溯。
- 迁移前 37 份受影响文件备份：`/tmp/cheshire-report-classification-27cq7z3m`，仅临时恢复用途；旧正文未做语义删减。没有在顶层留下兼容副本，最终实数核对顶层 Markdown 从 23 份降为 10 份（纠正过程更新中 24→11 的计数）。

## 2026-10-11 检查与剩余事项（历史）

- 命令：git status/rev-parse，rg/head/cat 定向审读，python3 /tmp/cheshire_classify_reports.py --apply（批量机械迁移），git diff --check，既有 check_site.py。
- 迁移前备份与现文件对照：13 份正文除链接、路径名和迁移说明外一致；旧路径文件均已迁出。`git diff --check` 退出 0。
- `python3 docs_codex/learning/scripts/check_site.py` 退出 1：仍为此前 17 条缺失（16 条旧图稿归档链接及 01 的 AGENT_TASK S.md 拼写），没有本次迁移新增缺失或 HTML/Markdown 漂移；不能声称全站检查通过。
- 无 RTL/sw/依赖修改，无目标编译/仿真/板测，也没有 Git 提交。
- 下一位从当前状态及维护索引开始；小型维护只更新主题交接，复杂报告按任务目录收录，不在根目录每轮再建一份。

### 工程参考与检索指南补充验收

- M/P 迁移前受影响 29 份文件备份在 `/tmp/cheshire-report-classification-ro2z9qes`。两份正文与备份对照，除路径/链接及分类提示外保持一致，未删除条款。旧顶层实体已移入 engineering，旧名见其 path_migrations.json。
- AGENT_DOCUMENTATION_GUIDE 与 engineering/README 的本地链接检查通过；git diff --check 退出 0。全站 check_site 仍为同样 17 条旧断链，未新增本轮链接错误或生成漂移。
- 新 Agent 从 AGENTS 链接进入定位指南，按“当前状态→任务主题→正式参考→必要的历史报告/原始证据”检索；无需通读所有记录。未新增独立答疑日志。

### 旧站清理范围与恢复

- 删除范围精确为 `docs_codex/learning_backup/`，728 文件、66,754,766 字节，包括目录内旧图片、示例及证据副本。目录外链接的现存目标是工程源码/现行文档，没有发现独占外部图片；未扩大删除范围。原目录 git status 无修改。
- 采用移出仓库的可恢复方式，完整目录位于 `/tmp/cheshire-retired-learning-z3xmiopj/learning_backup`；同级 manifest.json 记录所有文件哈希，移动后逐个校验通过。/tmp 可被系统清理，不作为长期备份承诺；已跟踪部分仍可由 Git 历史恢复。
- 当前 build_site 模板去掉侧栏/兼容跳转页的旧站链接；content/index、content/evidence 改为说明旧站已移除并链接维护资料；重建 51 对 HTML/Markdown 与 20 个旧地址跳转页。跳转仍保留当前章节目标和锚点迁移。
- check_structure 只将旧站存在/哈希断言改为已退休目录不存在的断言；其他历史资产检查不放宽。旧 restructure-backup.json 清单和独立 evidence 保留原样。
- 入口、README、状态/任务及 AGENTS 更新删除范围。历史叙述保留原时间身份，原始日志不改写。未删除任何其他文档或图片目录。
- build_site 退出 0；check_site 仍只有既有 17 条断链，无本次旧站删除造成的新缺失；git diff --check 退出 0。未运行浏览器或目标 RTL。
- 定向检查通过：旧站目录不存在，当前 HTML/Markdown/content 无指向旧站的 href/src/Markdown 链接。`check_structure.py` 退出 1（`/tmp/l01-checks-r89a7zfb`）：先在历史 `L01_structure_revision_review.md` 与早期 review_sha256 比较处失败，该文件此前命名迁移已加头部说明；未抵达后续结构断言，不声称完整结构通过，不放宽该历史检查。
