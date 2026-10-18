# L01 / 新 publication-figures skill 与 diagrams 重绘

> 2026-10-13 仅修复归档后的导航路径；下文验证记录仍对应原日期与输入，未重新验收图稿。

> 记录日期：2026-10-10。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-10。
- 本轮授权：用户在调研规划后明确要求“新建skill，并重新生成docs_codex/diagrams下子文件夹，新文件夹名称在原名基础上添加后缀_new”。此前仅规划的边界由本轮实施授权更新。
- 状态：新 skill、图稿与配套导出已交付；Office 外观与用户审美评价待实际检查。
- 输入 HEAD：`2784340240915fe4338ec54bfd613723b127d62e`。起始存在 M01 契约修改、多份图和交接未跟踪；保留。未启动子 Agent。
- 范围：7 个新 `_new` 目录、个人新技能目录和本交接；不改原图、旧 skill、RTL/sw、工程配置与共享状态。

## 本轮结果

- 新技能安装到 `/home/zhaowenyao/.codex/skills/publication-figures/`，含独立 `.venv`；[仓库快照](../diagrams/backup_no_use/backup_skill_publication/2026-10-10_publication_figure_research_new/skill/publication-figures/SKILL.md)可供审阅和搬迁。使用了 svg-pptx-diagrams 的旧后端快照与 skill-creator 指导，旧技能保留。
- 6 个有图目录重绘为 15 页（13 张不同图，验证组复用 2 张），输出 6 份 PPTX、15 份 PDF、源/规范化 SVG、彩色/灰度 PNG、中文图注和内容映射。调研目录对应 `_new` 保存总交付、生成器、skill 快照和对照页。
- [总交付与新旧对照入口](../diagrams/backup_no_use/backup_skill_publication/2026-10-10_publication_figure_research_new/README.md)。只重绘旧目录的正式母版，不复制历次中间导出；原教材引用未替换。
- 主要优化：说明移出图面，英文短标签/中文图注；DDR/LLC/软件层次拆图；矩阵、阵列、地址字段、mux 与阶段对应；物理宽182 mm、最小9.315 pt、原生虚线、PDF字体嵌入。不是严格同语言/同总面积A/B对照。
- 原有技术结论不变：DDR/GB为候选，LLC转换完成与COMMIT接受分开，ROM返回缺陷保留，既有板测/OS/ASIC缺口未关闭。

## 验证证据

- [validation.json](../diagrams/backup_no_use/backup_skill_publication/2026-10-10_publication_figure_research_new/validation.json)：逐图输入哈希、原生对象/文字保留、最终字号、PDF字体与尺寸、旧文件保护及安装版一致性。
- [preservation.json](../diagrams/backup_no_use/backup_skill_publication/2026-10-10_publication_figure_research_new/preservation.json)：97 个原图/旧 skill 文件起始哈希，结束时一致。旧 .venv/自动缓存未纳入。
- 运行 `build_figures.py --out-root <新临时目录>`、`export_all.py`、`check_delivery.py`；源码及导出保存在对应 `_new` 中。单图导出和批量导出均用新后端，旧脚本未改。
- `quick_validate.py <新 skill>` 通过；`test_export.py` 两个行为测试通过；安装后 `scripts/run.py` 实测输出到 `/tmp/publication-installed-smoke` 成功。
- 依赖：Python 3.13、python-pptx 1.0.2、Pillow 12.3.0、CairoSVG 2.9.1、PyMuPDF 1.28.2；本机 Cairo/fontconfig/Liberation Sans。依赖在独立环境安装，未改仓库依赖清单。首次沙箱网络安装失败后按授权提权安装成功。
- 全部不同图稿彩色预览与灰度总览已查看；文字包围盒及正交线段交叠辅助检查。修正了 ROM 返回节点、LLC Block/Byte 输入、mux 朝向，并删除转换图外围重复解释。
- Chrome 初次被沙箱 socket 限制阻止；授权的本地只读截图执行退出0，已查看对照页桌面截图。没有上传或发布页面。
- Office 未运行：既有交接记录本机脚本签名策略曾阻止验证，本轮没有改策略或将 SVG/PDF 渲染说成 Office 实测。PPT 用 Liberation Sans，目标系统缺字体时需检查替代布局。没有真实打印/用户盲测/目标投稿合规验收。
- 未编译/未仿真/未板测，未 Git 提交。

## 最小下一步

1. 用户从新旧对照页评审图面和图注；如有偏好，仅改新 skill/新目录，继续保留旧版。
2. 在装有匹配字体且允许验证的 Office 环境实测显示与编辑；此前结构检查不等于通过此项。
3. 确定具体投稿场所/年份后重新核对对应模板；照片/混合面板、分组与自动重连属于后续能力，不宣称本版已实现。

无需 C00 更新 RTL/启动/提取实现事实；如汇总方法工具进展，可记录“publication-figures 已创建并完成 diagrams 独立重绘，Office 实测未完成”。本轮不并发修改 PROJECT_STATE.md / AGENT_TASKS.md。
