# L01 / 器件接口参考与交接整理

## 修改记录

| 日期 | 角色 / 输入 | 内容 |
| --- | --- | --- |
| 2026-10-11 | 本对话 L01；mp/ara-pulp-v2，eaf55be17 | 静态核对 DDR 模型、存储器及其他接口；原三份答疑记录的技术内容合并到正式参考文档 |
| 2026-10-11 | 本对话 L01；同 HEAD，保留已有未提交文档 | 新增正式参考及导航；按用户要求修改 AGENTS/模板/任务表的交接规则，历史日期前缀日志改为任务主题命名并迁移引用 |

## 当前结果与负责文件

- 正式技术内容：[EXTERNAL_DEVICES_AND_INTERFACES.md](../EXTERNAL_DEVICES_AND_INTERFACES.md)，包含型号、模块/实例、模型抽象层、驱动/主机工具、平台接线、DDR IP 未到位的推进建议及原答疑纠错。
- 入口：00_README、software/README、software/LAYERS_AND_TOOLS；未改用户编辑中的 01 正文（若含旧交接路径，仅机械迁移路径）。
- 约定：根 AGENTS.md、HANDOFF_TEMPLATE、AGENT_TASKS、handoffs/README。纯答疑不单独记；变更、决策、缺陷、验证和阻塞记入任务主题；日期置于文件头。
- 历史改名映射见 [name_migrations.json](name_migrations.json)；改名保留内容，不合并其他对话未经审读的历史结论，不修改原始验证日志/证据快照。
- 本对话原 ddr_asic_model_qa、storage_device_mapping、external_interfaces_qa 三份文件合并移除，内容已进入正式参考。85 份迁移前原文备份在 `/tmp/cheshire-handoff-backup-3ui3_3yt`；/tmp 是临时恢复手段，不是长期证据库。82 份历史日志改名，三份合并；三条归档页面仍使用的旧路径保留符号链接，实际内容只维护新文件。

## 事实、纠错及剩余项

- Serial Link 对端为 axi_rand_slave 代理，不将其直接称为 RAM；EEPROM 启动按源码 case3，不采用 docs/um/sw.md 中误写的 0b10。
- 默认 TB 明确拒绝 SD 启动；GPIO/VGA/USB 没有有效默认外部交互场景；有驱动/RTL 不等于运行通过。
- DDR 模型不提供采购 ASIC Controller/PHY；Platform ROM 返回和栈对齐、iDMA/Ara 等原验证缺口均保持。
- 本轮无 RTL/sw 配置、接口或地址变化；未提交。状态是文档交付，不是硬件验收。

## 检查与继续步骤

- 已静态执行 git status/rev-parse、rg/sed，核对模型、VIP/TB/fixture、SoC、FPGA top、HAL/DIF 与构建规则；官方资料链接保留在正式参考。
- `python3 docs_codex/learning/scripts/check_site.py`：退出 1，共 17 条缺失链接，16 条为既有 diagrams/backup_skill_publication 归档链接，1 条是用户未提交的 01 中 `AGENT_TASK S.md` 拼写；未扩大修改这些内容。未报告 HTML/Markdown 漂移或本次新文档/迁移链接错误。
- `python3 /tmp/cheshire_verify_handoffs.py` 退出 0：82 份历史正文除路径替换/头部说明外一致，85 个迁移目标存在，189 条定向本地链接有效，三份合并原文可恢复；`git diff --check` 退出 0。全站检查不能记为通过。
- 未运行目标编译/仿真/板测或 DRAMSys 构建；未升级依赖。
- 下一位先读正式参考及本交接；新增实际测试时保留配置/命令/日志；其他历史 handoff 的内容精简应按主题审读后实施，保留重要决策和缺陷证据。
