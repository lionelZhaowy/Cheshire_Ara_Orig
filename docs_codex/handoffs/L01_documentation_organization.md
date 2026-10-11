# L01 / 文档目录分类与精简

## 修改记录

| 日期 | 输入 / 角色 | 修改 |
| --- | --- | --- |
| 2026-10-11 | eaf55be17，L01 本对话；保留前轮命名迁移及用户未提交文档 | 用户要求解释并归类顶层 L01 文件；13 份过程资料迁到 maintenance/L01，收敛用户入口，更新 AGENTS 存放规则 |
| 2026-10-11 | 同 HEAD 与本对话变更 | 用户补充要求 M/P 统一处理及新 Agent 历史定位：两份现行工程参考迁入 engineering，新增 Agent 定位指南并接入 AGENTS/00/状态 |
| 2026-10-11 | 同 HEAD 与本对话变更 | 用户授权删除 learning_backup 及独占资源；728 文件移出仓库，移除现行页面备份入口并同步生成，保留共享资源和独立证据 |

## 交付与范围

- [维护索引](../maintenance/L01/README.md) 是统一入口，分类为 planning/reviews/reports；12 份 L01 文件加 03–08 专题条件评估迁入，原日期保留正文，名称改为稳定主题。
- 旧 Prompt 是已执行历史任务定义，不是新任务授权；报告是教材修改和文档检查，不是新增用户教程或生产 SoC 验证。
- 根 AGENTS、00_README、PROJECT_STATE、AGENT_TASKS、handoffs/README 更新职责/入口。其他受影响 Markdown/HTML 仅迁移链接/路径；搬迁文件内部相对链接重算。
- M01/P01 是现行工程契约/适配参考；首轮保留，后续按用户要求迁至 engineering（非历史归档）。用户 01 正文仅在有旧路径引用时作机械替换，不删除其其他修改。
- 唯一 evidence 内编辑为 title-style-20261008/README.md 的报告导航链接；原日志/哈希/截图和内容快照未改。历史原始快照中旧路径可结合 [迁移表](../maintenance/L01/path_migrations.json) 追溯。
- 迁移前 37 份受影响文件备份：`/tmp/cheshire-report-classification-27cq7z3m`，仅临时恢复用途；旧正文未做语义删减。没有在顶层留下兼容副本，最终实数核对顶层 Markdown 从 23 份降为 10 份（纠正过程更新中 24→11 的计数）。

## 检查与剩余事项

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
