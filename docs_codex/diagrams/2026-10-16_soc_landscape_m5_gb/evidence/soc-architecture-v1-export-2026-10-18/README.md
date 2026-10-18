# v1 第九页只读导出与总纲整合证据

日期：2026-10-18。L01 文档整合；输入分支 `mp/ara-pulp-v2`，HEAD `09798c1ded457e423b927844f66faae87583a20c`。用户授权总纲、当前 PPT 导出及最小导航/交接更新，不授权工程实施。没有启动子 Agent。

## 输入与保护

- [输入状态及 632 个既有文件哈希](input.json)；其中四个允许修改的文档已完整备份到 [before](before/)，其余纳入保护核对。
- 主 PPT：`../../soc_landscape_m5_gb.pptx`，SHA-256 `b19710ba3cf23a34c93745c381051c4da5b03cae735f9d2e895416120cf05e3a`，共九页。[演示顺序](presentation-order.json)由 `presentation.xml` 的 `sldIdLst` 与关系文件解析；标题“SoC架构(v1)”唯一落在显示顺序第 9 页，本次对应 `ppt/slides/slide9.xml`。
- 用户手调的分区上边界和标题直接来自当前保存的 PPT。没有运行旧页面生成器，没有写回/保存主 PPT，没有覆盖原 SVG/PNG。同名 v1 SVG/PNG 在开始时不存在。
- [文件索引](markdown-file-index.txt)是 `docs_codex/` Markdown 路径索引；[主题索引](topic-index.txt)是限定主题的检索命中，不表示全部文件全文已读。实际阅读范围列在[总纲 §9.2](../../../../engineering/SoC_Architecture_v1_Master_Plan.md#92-主要来源与实际追溯范围)。
- [定向源码哈希](source-check.json)用于防止把历史快照当本轮动态验证，收尾再次比对。未扫描完整 `.bender/` 或全仓 RTL。

## 导出与复现

[export_v1.py](export_v1.py)基于原目录已有 `preview_deck_colours.py` 的只读解析器，改为按实际演示关系选第 9 页并断言 v1 标题；复用原 `revise_page4_layout.py` 中主题亮度颜色解析函数，未修改这两个原脚本。只解析绘图对象，没有调用修改 PPT 的生成函数。使用 industrial-svg-pptx 的对象/语义/预览检查流程和现有 native skill 环境；不执行反向生成 PPT。

实际执行（在仓库根目录，路径变量仅为复现方便）：

```sh
V1_EVIDENCE=docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/evidence/soc-architecture-v1-export-2026-10-18
V1_DECK=docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/soc_landscape_m5_gb.pptx
/home/zhaowenyao/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  "$V1_EVIDENCE/export_v1.py" --deck "$V1_DECK" --out-dir "$V1_EVIDENCE/preview"
```

退出 0，生成 [PPT 派生 SVG](preview/slide-09.svg) 与对象/文字坐标记录。随后以 Python `shutil.copy2` 在检查目标不存在后复制为 `soc-architecture-v1.svg`；使用已有 publication-figures 环境的 CairoSVG 2.9.1 栅格化为同名 PNG，并从同一 SVG 的 viewBox 生成下列五处局部，退出 0。系统 Python 与 native skill 环境没有 CairoSVG，探测返回 ModuleNotFoundError；改用已有环境完成，没有安装依赖。

上述栅格化步骤已整理成 [raster_v1.py](raster_v1.py)，并在独立目录实际重跑核对最终 PNG/局部逐字节一致：

```sh
/home/zhaowenyao/.codex/skills/publication-figures/.venv/bin/python -B \
  "$V1_EVIDENCE/raster_v1.py" --svg "$V1_EVIDENCE/preview/slide-09.svg" \
  --out-dir "$V1_EVIDENCE/raster-recheck"
/home/zhaowenyao/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -B \
  "$V1_EVIDENCE/validate.py"
```

复现时输出目录必须不存在；不要覆盖这些已交付证据。验证脚本不修改主 PPT，报告写入本证据目录。

## 实际查看与语义核对

从本次最终源 PPT 导出的[整页 PNG](../../soc-architecture-v1.png)和以下局部均已实际查看：

| 局部 | 实际检查范围 |
|---|---|
| [标题与核心区](title-core.png) | v1 标题、三个分区的上边界留白、CPU/Ara2/GB/采集布局、中文 |
| [GB与采集](gb-capture.png) | M5回接、GB局部共享、ISP交互、RAW绕行、F1/F2走线和跳线 |
| [Xbar与eMMC](xbar-emmc.png) | CPU S0/Ara S2独立输入、eMMC S7、共享M5、物理eMMC连线 |
| [存储与ROI](storage-roi.png) | 四F口/DDR.S口、共享编解码/旁路/响应、F1～F3虚线、ROI纵向读出链 |
| [配置区](controls.png) | 当前C1～C16名称和分组、PLL及RegExt布局 |

作者沿上电、参数加载、RAW/ISP帧写、ROI输出、DDR↔GB与CPU后处理的文图对应进行自查；维护/启动/恢复等图中省略项以总纲明确补足。脚本另对 C 组文字、PPT/SVG文字完整性和八条 DDR 接口的双端箭头/虚实做限定检查。`native-page-check.json` 保留早期原始 XML 比较输出：PowerPoint 复制/保存会改变对象标识或元数据，该文件中的 raw changed-name 列表**不是几何变化判据或验收结论**；其按对象名称去重的557也不是实际对象数，两个继承对象同名。最终按唯一对象ID核得 **558 个原生对象**，无整页图片；有效检查以 `validation.json` 为准。

保留源几何、主题解析颜色和原生线型；本地字体为 WenQuanYi Zen Hei，布局近似不保证与 Microsoft YaHei/Office 逐像素一致。**Office 显示/编辑未实测**，本次未对 PPT 做修改后保存重读；仅只读解析/重读，并确认整包哈希未变。检查覆盖当前 v1 与明确列出的路径，不宣称全部历史页面审图通过。

## 收尾结果与恢复

[validation.json](validation.json)记录 Markdown本地链接/锚点、主PPT页序/标题、当前配置组、关键接口样式、SVG文字、PNG重现、既有文件与源码保护、Git差异范围、章节/表格及空白检查。检查失败时保留报告并修正新交付，不改旧证据。本轮最终仅四份既有文档与新总纲/导出资产发生预期变化，其他初始未提交/未跟踪内容保留，HEAD/分支未切换，未提交Git。

首次验证脚本有一处括号笔误，修正后首轮报告保留在 [validation-first.json](validation-first.json)：发现模块表分隔行多一列、对象数误沿用旧页557，以及报告自身尚未写出时的链接检查。修正表格与计数依据后再次运行退出0；没有因此修改PPT或放宽对象ID唯一性/输入保护要求。最终既有文件保护628项、源码哈希19项、16个配置组、8条DDR接口样式及新链接/表格检查通过；范围不包含Office与硬件运行。

恢复四份导航/交接文档时，先比较当前内容与本次输出，确认无后续编辑，再从 `before/` 的对应路径定向取回；不得批量还原工作区。旧主PPT从未写入，不需要由本轮备份覆盖。

本证据不包含软件/RTL编译、展开、仿真、板测、性能、错误注入、综合、STA/DFT或物理签核结果。供应商受控PDF/Word、实际交付与目标Office未重新实测。
