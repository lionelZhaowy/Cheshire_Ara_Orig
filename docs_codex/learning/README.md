# Cheshire / CVA6 / Ara 中文工程教材

直接用浏览器打开 [index.html](index.html)。20 页课程与参考可用 `file://` 离线阅读；没有服务器、CDN、字体下载或前端安装步骤。页面文字、SVG、目录和表格在关闭 JavaScript 时仍可阅读；脚本只增强图像缩放、寄存器搜索和容量计算。

2026-09-28 重构为 **16 章单线课程 + 6 项实验 + 2 页参考**。面向已有处理器/RTL 经验、刚开始学习 RISC-V 嵌入式软件的读者，从硬件职责推进到配置与互连，再建立运行模型，完成构建、加载和仿真，最后学习设备、共享存储、向量与系统扩展。

- [2026-09-29 深度扩充](DEPTH_EXTENSION.md)：CVA6–Ara/RVV、共享存储、系统与 ASIC 集成；[官方来源及版本边界](OFFICIAL_SOURCES.md)。
- [编排设计与旧内容去向](CONTENT_REDESIGN.md)：知识依赖、章节目标和实验取舍。
- [实验手册](labs.html)：前置、输入、工作目录、命令、产物、判据和失败首查。
- [来源与验证记录](evidence.html)：区分当前静态检查、软件构建、历史单元运行和待执行的目标仿真。
- [旧站完整备份](../learning_backup/index.html)：重写前逐文件复制并校验的 728 个文件，含图、脚本、示例及历史证据；[备份清单](evidence/restructure-backup.json) 保存每个文件的哈希与字节数。备份内保留原日期，不参与新站生成。

## 维护入口

在仓库根执行，Python 仅用标准库；WaveDrom 生成和浏览器预览需要本地 `google-chrome`：

```bash
python3 docs_codex/learning/scripts/build_depth_diagrams.py
python3 docs_codex/learning/scripts/build_waves.py
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/preview_depth_site.py
python3 docs_codex/learning/scripts/check_depth.py
```

正文编辑 `content/*.html`；目录在 `scripts/pages.json`；渲染壳由 `build_site.py` 生成。原 16 张图仍由 `build_diagrams.py` 维护。本轮新增 13 张结构/状态图由 `build_depth_diagrams.py` 生成；6 张时序图源文件在 `assets/waves/*.json`，`build_waves.py` 使用本地 WaveDrom 3.5.0 导出 `assets/depth-*.svg`。厂商包保留许可证与来源哈希；页面阅读不执行 WaveDrom，也不联网。

`preview_depth_site.py` 检查桌面/手机、交互、禁用脚本和 SVG 文字边界，写 `evidence/depth-20260929-browser.txt`。`check_depth.py` 验证备份、670 个本轮开始前证据文件、来源哈希、可重复生成、链接/锚点、合成日志检查器和部分波形握手语义。不调用生产 RTL 工具。

`record_depth_sources.py` 只在完成有依据的来源审阅后更新本轮来源快照，不能用于掩盖源码漂移。旧 `record_sources.py`、`preview_site.py`、`check_integrity.py` 属于 2026-09-28 重构记录，会写 `restructure-*`，不能作为本轮维护入口。寄存器索引仍为 12 组/429 项；未改其来源时无须重新运行 `build_registers.py`。以后改变寄存器来源应另建日期记录，保留旧证据。

## 示例与证据

`examples/journey.c` 是第 04～07、13 章贯穿示例。`build_journey.sh scalar spm`、`scalar dram`、`rvv spm` 分别形成标量 SPM、仅用于布局对照的 DRAM、显式 RVV 版本。`JOURNEY_DEPTH=1` 启用六组长度、环绕输入和归约检查；`rvv-intrinsics`、`rvv-auto` 使用同一主程序。`INJECT_ERROR=1` 构建负例。每次输出到新目录；可设置 `JOURNEY_OUT` 为事先创建的空目录，已有内容时拒绝覆盖。工具链前缀由 `CROSS_COMPILE` 设置。

实验 C、D 复用 `advanced.c` 和 `storage_read.c`，实验 F 复用独立 Reg 单元。原 `lesson.c`、原构建器、硬件教学模型及旧图生成器保留供历史证据追溯；它们不定义新课程顺序，旧页面重建请在独立旧站副本中进行。日常维护使用上面的本轮入口。

本轮报告统一 `evidence/depth-20260929-*`；2026-09-28 的 `restructure-*` 保留为历史。历史 `builds.txt`、`advanced-*`、`hardware-*`、`editorial-*` 及其产物保持原内容。临时软件输出目录不纳入版本管理，精选编译日志及 ELF 哈希已存入本轮报告；不能把哈希或 ELF 当成执行成功证据。

复制 `learning/` 即可阅读课程内容；正文里的 `../../hw/…` 等链接用于在完整仓库内查源码，独立搬走教材后需同时携带仓库才能打开这些源码链接。备份入口同理需要相邻 `learning_backup/`。
