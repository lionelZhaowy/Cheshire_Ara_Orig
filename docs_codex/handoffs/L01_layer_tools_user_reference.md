# L01 / 分层与工具用户参考页

> 记录日期：2026-10-11。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-11；任务 L01，用户要求将层次和工具映射写入正式学习文档，而非仅存交接。
- 状态：用户参考页与入口完成；全局文档检查有既有归档断链，未修改历史文件。
- 输入 HEAD `eaf55be17`；开始时仅有本对话上一轮未跟踪的工具映射交接，保留。

## 本轮结果与文件

- 新增 [software/LAYERS_AND_TOOLS.md](../software/LAYERS_AND_TOOLS.md)：分层图与职责表、15 项模块映射、15 项主机流程映射、启动/OS/实现平台表、按任务查入口及配置条件。
- 在 `00_README.md`、`software/README.md`、`software/LIBRARIES.md` 增加正式阅读链接。此页承担源码/工具查询，主要原理继续指向现有 runtime 主教材。
- `PROJECT_STATE.md` 仅增加文档导航；`AGENT_TASKS.md` 的 L01 行补充参考页交付，不改变生产任务状态。
- 保留现有图源、PNG/PPTX、主教材 content/HTML/同步 Markdown，未运行生成器。无 RTL/sw/构建脚本修改。

## 验证证据

- `git status --short`、`git rev-parse --short HEAD`，读取现行软件导航、库接口正文、教材维护说明和入口。
- `python3 docs_codex/learning/scripts/check_site.py` 退出 1：16 次 missing 报错均在 `diagrams/backup_skill_publication/*/README.md`。原 `known_link_gaps.json` 仍登记 `diagrams/backup_new/` 路径，故当前目录下的既有问题未命中旧名单。本轮不改归档或放宽检查规则。
- 定向复用检查器的链接/锚点检查函数，检查本次参考页、入口和状态/交接；同时确认全局错误仅来自上述未改归档。`git diff --quiet HEAD --` 核对归档、检查器和已知缺口清单未改。
- `git diff --check` 检查格式；本轮没有浏览器渲染、目标编译、仿真、板测或烧写。Markdown 已接入已有阅读入口，HTML/Markdown 生成内容未变。
- 未提交，无地址、配置、接口或目标验证状态变化。

## 下一步

- 用户从软件手册第一项或文档总入口打开新参考页。
- 历史图稿目录迁移的断链及名单路径差异由对应归档维护任务处理；不将全局检查记为通过。
