# L01 / 教材结构与写作风格整理

## 基本信息

- 日期：2026-09-23；任务：L01。
- 授权范围：对全部教程 HTML、README 和相关 Markdown 进行章节组织、标题、导航与正文风格优化；保留技术内容与证据，不实施技术修复。
- 状态：文档整理完成；生产 SoC 的运行验证状态没有变化。
- 输入：分支 `mp/ara-pulp-v2`，HEAD `ae2b69fe0640e57c89dfc6bcc9404bfd5008e1a5`，以及开始时已有的未提交硬件主线、图表、示例和索引。未跟踪的 M01 DDR 交接保留。
- 负责路径：`docs_codex/learning/` 的正文、生成页、既有生成/检查脚本；00/01/02 文档、配置与软件参考手册；本记录及必要共享索引。

## 本轮结果

- 统一 35 个页面的标题、H1、H2/H3、页内目录、侧边栏和上下章导航；同步整理 15 篇 Markdown 教材/参考中的 115 处标题。
- 正式标题使用陈述性、名词性技术主题；问题保留在正文、自测与实验。三条主线分别承担概念与基本实验、设备使用与执行分析、硬件结构与集成原理。
- 页面顺序与文件名不变。局部结构调整：配置章按配置层次→硬件基线与覆盖→软件与运行时状态→联动→实验组织；程序生命周期先解释复位启动条件，再解释 ELF 装载；参数化 RTL 先解释数组/位宽再追踪 UART；I2C target 模式独立于 EEPROM 只读实验；硬件外设章先讲寄存器实现，再讲设备结构和中断。
- 入口和章节增加必要的范围说明与跨章节引用，减少概览、驱动用法与硬件实现之间的职责重叠；未新增教程页面，未重写 CSS/JS 或网站框架。
- 所有原 HTML ID 保留；改名的 Markdown 标题保留旧锚点。证据、技术表格数据、命令、图表与自测答案经快照比较保留。
- 未发现需要在本次编辑中改写的已证实技术错误。iDMA 控制接口位宽、profile/decoder 匹配、VCS/模型环境、缓存一致性等既有缺口继续保留。首页将旧许可证查询描述明确归属 2026-09-22，与后续独立单元记录区分。

## 改动与接口

- 正文：`learning/content/*.html`；生成输出：`learning/*.html`。
- 页面标题唯一来源：`learning/scripts/build_site.py` 的 `PAGES`；寄存器索引标题同步修改 `build_registers.py`，429 项数据不变。
- `check_site.py` 增加 H1/title/导航/目录/上下章一致性、标题层级和 Markdown 链接锚点检查；`preview_site.py --editorial` 使用独立证据名称，复用现有浏览器检查流程。
- 新证据：`learning/evidence/editorial-checks.txt`、`editorial-browser.txt` 与三张 `editorial-preview-*.png`。未覆盖既有证据。
- 配置、profile、宏、地址、中断号、位宽和生产接口变化：无。原 RTL、sw、共享清单、FPGA 工程和 `.bender/` 未修改。
- 未执行 Git 提交或推送；本工作区还包含上一轮硬件教材的未提交内容，不应把全部 diff 误记为本轮改动。

## 验证证据

工作目录为仓库根。文档工具为 Python 3 标准库；实际 Chrome 版本记录在 `editorial-browser.txt` 首行。

```sh
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/check_site.py
python3 docs_codex/learning/scripts/preview_site.py --editorial --advanced --hardware
```

- 上述命令退出码均为 0。静态检查覆盖全站 35 页、28 张 SVG、站内资源、HTML/Markdown 锚点、标题/目录/导航和上下章一致性。
- Chrome 使用 `file://` 实际预览全部页面：桌面 1440×1100、手机 390×844；图片正常、无页面横向溢出，无 JavaScript 异常或 HTTP(S) 渲染依赖。寄存器搜索、步骤切换、折叠答案、图表缩放和预算计算检查通过；另检查禁用脚本后的核心内容。
- 与本轮编辑前本机快照比较：634 个既有证据/图片资源/示例/交接文件 SHA256 不变；51 个代码块、27 个源码依据块、30 个图表块、101 个自测/步骤解释、77 张技术表格数据保留。导航表标题和技术表表头允许编辑，技术单元格不变。
- 15 篇 Markdown 的原命令块、表格和旧标题锚点保留；页面顺序不变。寄存器生成器输出与正文一致。快照比较脚本和输入位于本机 `/tmp/cheshire_editorial_audit.py` 与 `/tmp/cheshire-editorial-gcw3hyjt`，不作为可搬迁依赖；结果保存在独立证据文件。
- 本次未重新构建示例、编译 RTL、运行仿真、综合或板测；以往独立单元通过不扩大为生产 SoC 通过。

## 决策与下一步

- 用户已确认本轮优先优化表达与结构，保留技术结论与验证边界，不新增无必要的文档实体。
- 后续维护在 `content/` 与 `PAGES` 修改后再生成，保留已有 ID；Markdown 改标题需保留旧锚点或同步所有引用。
- 最小继续步骤：阅读网站目录与本记录；按新结构开展教学；技术修复仍由 S01/V01 等任务取得实施授权后处理。
- 最少输入：`learning/README.md`、`learning/scripts/build_site.py`、本记录。
- 已串行同步 `PROJECT_STATE.md`、`AGENT_TASKS.md` 与交接索引，仅更新 L01 文档进展。
