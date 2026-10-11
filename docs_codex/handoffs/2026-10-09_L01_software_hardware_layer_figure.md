# L01 / Cheshire 软硬件分层图交付

## 基本信息

- 日期：2026-10-09；任务 L01，用户在方案复核后明确授权“开始绘制”，使用 svg-pptx 技能。
- 状态：图稿及结构导出完成；Office 实际显示/编辑待验证。
- 输入：`mp/ara-pulp-v2`，HEAD `278434024`。已有 M01 文档及其他交接/图示文件保留。
- 负责路径：新建 `docs_codex/diagrams/2026-10-09_software_hardware_layers/` 与本交接；未修改生产源码、共享任务表或教程正文。

## 本轮结果

- 交付一张 2000×1500 分层图：应用软件、基础软件、接口契约、SoC 硬件、片外器件；侧栏包含构建、启动支持、可选 OS、实现平台及图例。
- 保留真实代表性调用链、CVA6–Ara 专用接口和独立 AXI 访存路径；lib 作为归档注记。NPU/ISP 等采用规划虚线框。
- 文件入口：[图稿说明](../diagrams/2026-10-09_software_hardware_layers/README.md)、[SVG](../diagrams/2026-10-09_software_hardware_layers/cheshire_software_hardware.svg)、[PPTX](../diagrams/2026-10-09_software_hardware_layers/export_final/diagrams.pptx)、[PNG](../diagrams/2026-10-09_software_hardware_layers/export_final/cheshire_software_hardware.png)。
- 本轮证据为源码复核和图稿检查，未新增硬件能力或产品配置决策。

## 验证证据

- 仓库根运行 `git status --short`、`git rev-parse --short HEAD`，技能主文件和 SVG 子集说明已读取。
- 技能隔离 Python 运行 `build_figure.py`：修正初次参数语法和过长副标题后退出 0，检查中文字体测量与文字画布边界。
- `python3 /home/zhaowenyao/.codex/skills/svg-pptx-diagrams/scripts/run.py --input docs_codex/diagrams/2026-10-09_software_hardware_layers/cheshire_software_hardware.svg --out-dir docs_codex/diagrams/2026-10-09_software_hardware_layers/export_final --font-file /mnt/c/Windows/Fonts/msyh.ttc`：退出 0。
- 导出报告确认 334 个对象、108 个文本对象，重读文字及对象数相同，无 `ppt/media/` 整图图片。报告保存输入 SHA-256。
- 生成器在新临时目录复现 SVG，统一文件尾换行后与正式母版逐字节比较通过；字体回退和底部留白已同步到生成器。
- Chrome 初次无法创建默认 headless 配置目录；经授权使用 `/tmp/l01-layers-*` 隔离配置后，本地离线渲染退出 0。最终 PNG 全图人工检查通过，保留字体回退和底部留白调整前的 `export/` 中间版本。
- PowerPoint `verify_powerpoint.ps1 -Presentation .../export_final/diagrams.pptx -OutDirectory .../export_final` 被 Windows 数字签名/执行策略拒绝（UnauthorizedAccess），退出 1；未打开文稿、未改变策略。Office 验证不通过不能被 SVG 截图替代。
- 无生产构建、RTL 仿真或板测；无配置、地址、中断或位宽改动；未提交。

## 下一步

- 用户可直接查看正式 PNG，编辑 SVG 母版或 PPTX 原生对象。
- 若需 Office 外观验收，在允许执行已审阅验证脚本的环境中只读打开并导出检查，不覆盖现有产物。
- 本轮独立图稿不改变生产工程事实；需要协调者汇总时仅追加文档交付记录，不关闭任何原有验证缺口。
