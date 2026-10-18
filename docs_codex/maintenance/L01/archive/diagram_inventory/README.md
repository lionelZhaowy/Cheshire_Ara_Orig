# 图稿目录检索与 backup_no_use 整理

2026-10-18；L01；输入 `aa5716464a8869b91212cba9fa31deb1e41ebcf5`，分支 `mp/ara-pulp-v2`。用户已将16个目录移入 backup_no_use；本次以该工作区为输入，没有把Git中的337项删除当作待清除文件。

正式入口：[图稿索引](../../../../diagrams/README.md)。范围与结果见[主题交接](../../../../handoffs/L01_documentation_organization.md)。

- [manifest.json](manifest.json)：初始引用审查、用户已移动目录、本次4个移回/3个归档目录、每个文件前后路径与起始哈希、112处导航变更。
- [before_inventory.tar.gz](before_inventory.tar.gz)：201个操作前文件。包括7个本次迁移目录的完整原件，以及将修改的文档/脚本；归档内路径相对仓库根，先在独立空目录恢复，不覆盖当前工作区。
- [validation.json](validation.json)：本次实际检查、命令与限制。原始图稿验证报告及输入哈希不重写。
- [verify_inventory.py](verify_inventory.py)：检查现行图稿导航、正式文档的链接/锚点、初始文件去向、图片/PPT/PDF及证据保护、9对软件专题HTML/Markdown同步；`--output`只允许新报告路径。历史evidence/before/skill快照不当作现行导航；不重新渲染图片。

本次不删除任何图像、PPT、PDF或独立证据。迁移原件可在backup_no_use中直接访问；静态图稿未被重新布局或生成，未做Office/硬件运行验证。目录外旧原始记录仍可能保存迁移前路径，使用[路径映射](../../../../diagrams/path_migrations.json)追溯。
