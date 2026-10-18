# Publication figures：新 skill 与重绘交付

> 2026-10-13 仅修复归档后的导航路径；下文验证记录仍对应原日期与输入，未重新验收图稿。

2026-10-10。用户在调研完成后明确授权创建新 skill，并按原子目录名加 `_new` 保存重绘结果。旧 skill、原图和历史导出保持原样；不修改 RTL、软件、配置、依赖清单或现有教材引用。

## 查看与使用

- [新旧对照页](index.html)：同显示宽度查看原图与重绘图，可调宽度、切换灰度，并查看图注与内容映射。
- 已安装 skill：[publication-figures](/home/zhaowenyao/.codex/skills/publication-figures/SKILL.md)。可用 `$publication-figures` 调用；本次安装位于 Linux/WSL 用户技能目录，未另外部署 Windows 用户目录。
- [可搬迁的 skill 源码快照](skill/publication-figures/SKILL.md)：包含入口、领域图式、图面内容规则、场所资料、导出说明、审查规则与独立后端。和安装版内容一致，不依赖旧 skill。
- [上一轮调研](../../2026-10-10_publication_figure_research/README.md)仍保留为当时的规划记录；其中“尚未实施”描述的是上一轮状态，本轮实施结果以本文为准。

## 目录和内容

| 新目录 | 页数 | 重绘内容 |
| --- | ---: | --- |
| [2026-10-06_axi_crossbar_ara_new](../2026-10-06_axi_crossbar_ara_new/README.md) | 2 | 7×5 Crossbar 可达矩阵与独立仲裁；历史 DDR 三端口建议 |
| [2026-10-06_svg_pptx_skill_validation_new](../2026-10-06_svg_pptx_skill_validation_new/README.md) | 3 | 处理/反馈示例；复用新版 Crossbar 与 DDR 图检验批量导出 |
| [2026-10-08_boot_initialization_new](../2026-10-08_boot_initialization_new/README.md) | 2 | 软硬件初始化对应关系；ROM/载荷控制流与返回缺陷 |
| [2026-10-09_software_hardware_layers_new](../2026-10-09_software_hardware_layers_new/README.md) | 3 | 调用关系、硬件执行/访存、构建与执行环境分别表达 |
| [2026-10-10_ddr_lvds_isp_gb_new](../2026-10-10_ddr_lvds_isp_gb_new/README.md) | 2 | 系统/GB/DDR 拓扑；RAW/ISP 与 GB 数据流 |
| [2026-10-10_llc_cache_spm_new](../2026-10-10_llc_cache_spm_new/README.md) | 3 | Cache 地址/阵列/选择；SPM 用途与寻址；软件/硬件切换次序 |
| 当前 `2026-10-10_publication_figure_research_new` | — | 新 skill 快照、生成器、对照入口及验收记录；原目录是调研文档，没有待重绘的图稿 |

合计 15 页（13 张不同的图，其中 2 张在验证组复用），6 份原生可编辑 PPTX、15 份矢量 PDF；每页同时提供源 SVG、规范化 SVG、300 dpi PNG、灰度 PNG 和图注。仅重绘正式母版，不重复生成旧 `export/`、`v2/`、`before_datasheet` 等历史中间版。

## 已落实的设计变化

1. 图面只保留对象、端口、字段、关系、必要状态与局部标签。大标题、背景说明、阅读指南、来源和验证条移出画布。技术前提没有丢弃，按图保存在 README 的图注和补充条件中。
2. 使用有含义的图式：Crossbar 用可达矩阵与仲裁器，LLC 用 tag/data 分立阵列、地址字段和选择器，SPM 用 way 位图，启动按软件阶段与硬件资源对应。不是简单把彩色圆角框改成黑色直角框。
3. 复杂主题拆图，不用不断缩小文字维持一页。DDR 拆成 2 图，LLC/SPM 拆成 3 图，软硬件总览拆成 3 图。
4. 白底、深色线字，以蓝色/浅蓝填充表达少量重点；规划模块使用虚线，Cache/SPM 同时用 C/S 字母编码，灰度不依赖色相。
5. 按 182 mm 宽导出，最小文字约 9.315 pt（不是旧版 14 英寸 PPT 中的字号）；最细线约 0.573 pt。182 mm / 9 pt 是这次工作规格，不宣称适用于所有刊会。

本轮图面采用英文短标签、中文图注，使用 Liberation Sans；PDF 已嵌入字体。PPTX 字体未嵌入，目标电脑需有该字体才能保持同样度量，字体替换后的外观仍须检查。本次同时改变了语言、内容分工与拆图方式，所以对照页不构成严格控制变量的读者 A/B 实验，也不声称客观消除了所有“AI 味”。

## 导出能力与证据

新后端由旧导出器独立复制并审计修改：增加显式物理宽度、导出前最小字号拒绝检查、原生虚线、保留源对象 ID、PDF/PNG/灰度输出。PDF 检查实际页面尺寸、字体嵌入和纯矢量结构。旧后端没有修改。

- [完整验收记录](validation.json)：逐页源哈希、字号、原生对象数与文本数；6 份 PPTX 重新读取与 ZIP 检查通过，文字逐项一致，无整图位图/SVG 嵌入。
- [原文件保护记录](preservation.json)：本轮开始时记录的 97 个旧图稿/旧 skill 文件哈希，结束时一致；旧环境 `.venv` 和 Python 自动缓存不在此清单中。
- 已实际查看全部不同图稿的彩色预览与灰度总览，检查标签/走线/裁切；生成时进行文字宽度/画布边界和文字对文字的包围盒检查，另检查正交线段与文字的交叠。几何检查不是电气语义证明。
- 新 skill 的 frontmatter/目录校验通过；两个行为测试覆盖物理尺寸、原生虚线、文本保留、PDF 字体、拒绝覆盖、拒绝过小字号与拒绝不支持的 image 元素。安装后入口实测导出成功。
- Chrome 已只读渲染本地对照页并查看桌面截图。首次受沙箱 socket 限制失败，在获准的本地浏览器进程中成功；未上传文件或发布网页。

**Office 实际打开、编辑和渲染未验证。** 本轮没有重复运行此前被数字签名策略拒绝的 PowerPoint 脚本，也没有修改执行策略。SVG/PDF 预览不能替代 Office 外观验收。未做真实纸张打印、用户盲测或任一目标稿件的完整合规验收；未重新编译/仿真/板测。

第一版支持纯结构/机制图，不支持照片/实验结果混合面板、PPT 语义分组、移动后自动重连或 SVG↔PPT 双向同步。AI 方法结构图可使用同一规则；实测曲线和视觉结果应使用有来源的数据/图像流程，不能凭空生成结果。

## 复现

本地安装环境是 `/home/zhaowenyao/.codex/skills/publication-figures/.venv`。主要实测版本：Python 3.13、python-pptx 1.0.2、Pillow 12.3.0、CairoSVG 2.9.1、PyMuPDF 1.28.2。Cairo/fontconfig 与 Liberation Sans 为系统渲染依赖。新机器按 skill 中 `requirements.txt` 创建自己的隔离环境，不复制跨平台 `.venv`。

在本目录运行；将 `<python>` 换成装有上述依赖的 Python：

```sh
<python> build_figures.py --out-root /tmp/publication-redraw-reproduce
<python> export_all.py --root /tmp/publication-redraw-reproduce
<python> skill/publication-figures/scripts/test_export.py
<python> check_delivery.py
```

`build_figures.py` 和导出器均拒绝覆盖已有输出。`export_all.py` 默认使用本目录的 skill 快照，按 `manifest.json` 顺序输出每组 PPT。生成器当前按本机 Liberation Sans 字体文件度量；其他系统需要配置对应字体路径。`check_delivery.py` 检查当前交付和本机原始输入，故其完整保护检查要求原仓库与技能目录仍在。

`build_index.py` 根据 manifest 重建本地对照页。源事实、旧图到新图/图注的映射均随各组 README 提供；原有教程没有自动替换为新图，便于先对照评审。
