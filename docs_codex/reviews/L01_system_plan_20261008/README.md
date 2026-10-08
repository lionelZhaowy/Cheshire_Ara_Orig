# L01 系统教材规划检查记录

本目录仅记录 2026-10-08 评审对话汇总和修改规划；上轮正文与网页证据仍在 learning/evidence/peripheral-20261008/，不在这里重写。

- input.json：本轮开始的分支、完整 HEAD、Git 状态、439个输入文件哈希；附件1168行及SHA-256。
- check_protection.py：只读保护检查，5个已明确更新的文档作为允许差异，其他输入均要求字节不变；新文件范围另记于日志。
- checks.txt：检查命令、退出码、输出，含文档链接/静态页面检查、git diff --check、输入保护和本轮文件清单。

本轮未编辑 learning/content、生成页、脚本、图源或生产工程，没有重新运行生成器或浏览器。网页静态链接检查不等于新的浏览器/目标运行结果。没有目标编译、仿真、板测或OS/ASIC实现。

复查命令（在仓库根；若工作区已继续修改，哈希差异应视为版本变化，不重写 input.json）：

~~~sh
python3 docs_codex/learning/scripts/check_site.py
git diff --check
python3 docs_codex/reviews/L01_system_plan_20261008/check_protection.py
~~~

规划与结果见 [修改规划](../../L01_System_Textbook_Revision_Plan_2026-10-08.md) 和 [独立交接](../../handoffs/2026-10-08_L01_system_curriculum_plan.md)。
