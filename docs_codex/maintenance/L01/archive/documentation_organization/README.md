# 文档与 RTL 试绘整理归档

2026-10-13；L01；输入 `mp/ara-pulp-v2` / `5a1338e0a0bf115ddd54c19e0ae367ac2d541892`。当前结果与验证见[组织交接](../../../../handoffs/L01_documentation_organization.md)，正式资料由[模块指南](../../../../rtl_modules/README.md)和[项目状态](../../../../PROJECT_STATE.md)承担。

## 内容与恢复

[before_cleanup.tar.gz](before_cleanup.tar.gz) 是集中可恢复备份，273 个原路径成员；补充导航修复备份 [before_link_repairs.tar.gz](before_link_repairs.tar.gz) 保存另外15个文件；[manifest.json](manifest.json) 记录每个成员的 SHA-256、字节数、分类、操作及输入版本。归档已经逐文件读取校验后才清理原路径。B 被弃用、C 未采用，但原始 SVG、PPTX 与全部导出格式仍可完整恢复；未以“脚本能生成”为理由丢弃可编辑成果。

| 处理 | 数量 | 当前职责 |
| --- | ---: | --- |
| B 全套图稿与导出归档 | 124 文件 | 仅供历史追溯，正式图由 A 承担 |
| C 图稿与导出归档 | 98 文件 | 仅供历史追溯，正式图由 A 承担 |
| C 生成/验证脚本归档 | 2 文件 | 历史输入快照；活动检查改用 verify_a.py |
| Python 字节码缓存清理 | 2 文件 | 无独有内容；删除前已备份 |
| 修改前导航/脚本/状态及保留资料备份 | 47 文件 | 完整旧输入，包括旧 A/B checker、旧状态全文和任务 Prompt |

解包至**独立空目录**，不要覆盖当前工作区：

```sh
mkdir -p /tmp/rtl-style-history
tar -xzf docs_codex/maintenance/L01/archive/documentation_organization/before_cleanup.tar.gz -C /tmp/rtl-style-history
```

成员路径以仓库根为基准。归档中的脚本依赖当时布局、文档和原 A 图，不能仅解包一份脚本就当作当前可运行工具；复核历史时还应结合输入提交和原证据备份。不要在当前目录重新生成 B/C，或把旧报告改成新目录结构已通过。

检查结果见 [validation.json](validation.json)；可用已有 publication-figures venv 执行 [verify_organization.py](verify_organization.py) 复核归档成员、保留文件、正文及链接，使用 `--output` 指定新的报告路径。补充备份的成员和哈希也记录在同一清单；恢复时可按需解包对应归档。

## 保留与替代关系

- A 全部交付格式、78 项源码哈希、21 篇正文及213条连接保留；新检查不刷新原技术哈希。
- A/B 和 C 原 `validation.json`、视觉/渲染/源码清单及 `evidence/` 保持原字节。其中 B/C 资产路径为归档成员路径，属于允许保留的历史引用。
- C 原 README/比较页存入备份，原位置只留下简短迁移说明和24个旧图锚点。正式文档不再跳转 C。
- 两个早期布局目录、Regbus 早期图稿、provisional A/B 原生导出和PPT 锁文件未操作。前两类存在生成依赖；其他材料有独立编辑/修订或占用状态疑点，不能认定无用。
- 共享状态中的旧教材阶段记录收敛为当前结论和主题链接，原全文存于本归档，详细日期/输入/命令与失败记录继续保留在原 handoff/证据中。

本归档不含新的硬件测试结论，不进入正式学习导航。未修改生产实现、依赖或工程构建脚本。
