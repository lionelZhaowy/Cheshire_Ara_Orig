# 教材插图母版与可编辑导出

当前七篇/30章使用 **37 张重绘结构图 + 6 张 WaveDrom 教学时序图**。2026-10-07 用户明确要求波形继续使用 WaveDrom，已恢复原有生成路径，撤回上一轮手工绘制的6张波形。未被当前正文引用的历史资产、旧站备份和历史证据保持原样。

- [新旧图对照页](figures/20261007/index.html)：逐图查看，并返回对应教材章节。
- [37 页结构图原生可编辑 PPTX](figures/20261007/editable/diagrams.pptx)：每图一页；文本、框、曲线和箭头为独立对象；不包含手工重绘波形。
- [新版母版清单](assets/figures-20261007/manifest.json)：图名、来源说明、状态、哈希和替换路径。
- [旧图归档清单](figure_archive/20261007/manifest.json)：旧图哈希和原章节引用；原 `assets/*.svg` 也保留，兼容旧生成器与历史检查。
- [SVG 实际渲染证据](evidence/figures-20261007/svg-browser-final/report.json)与[PPTX 导出报告](figures/20261007/editable/export_report.json)。浏览器 SVG 渲染不等于 Office 测试。

## 图的表达规则

以具体对象和连接关系选择图形结构。Crossbar 展开输入译码、连接矩阵、逐目标仲裁与二级 Reg 译码；存储用地址与物理阵列映射；控制与数据面分别绘制；时钟、电源画域边界；软件与启动用主机/目标泳道；时序图以 WaveDrom JSON 表达信号和时序，由 WaveDrom 渲染。流程型内容仍可使用顺序箭头，但需说明传递的产物、状态或接口。

图内写明当前源码结构、教学示意或未来方案。7×5 Crossbar 是 **DefaultCfg + Ara=1、单核、无外部扩展端口** 的展开，不是所有配置的固定拓扑。S 为 Crossbar 接收请求的一侧，M 为发送请求的一侧；Debug、iDMA、Link 的发起角色与可寻址目标角色分别标注。SPM 两个别名仍映射同一阵列。Platform ROM/栈条件、S01-B01、iDMA 和 Ara 错误处理缺口不因插图更新而关闭。

37张结构图的 SVG 使用显式坐标和呈现属性，不含外部字体、图片、CSS、marker、滤镜或文字轮廓。文本保持 `text`；箭头用线和独立三角形，曲线用可编辑 Bézier。统一画布 1800×1125；颜色同时配合标签和布局表达角色，不以颜色作为唯一信息载体。字体为本地已安装的 WenQuanYi Zen Hei；跨机器无此字体时可能回退，PPTX 不嵌入字体，目标 Office 仍需检查外观。

## 维护与生成

母版定义：[build_research_figures.py](scripts/build_research_figures.py)；绘图原语：[figure_primitives.py](scripts/figure_primitives.py)。六张时序图的唯一母版为 `assets/waves/*.json`，由既有 `scripts/build_waves.py` 调用本地 WaveDrom 3.5.0 渲染到 `assets/depth-*.svg`。网页引用这些 WaveDrom 生成文件。不得用自写SVG波形绘制器替代 WaveDrom；SVG只是它的离线显示产物。

在仓库根执行，输出路径必须尚不存在：

```bash
python3 docs_codex/learning/scripts/build_research_figures.py --out-dir /tmp/l01-figures-new
python3 docs_codex/learning/scripts/preview_research_figures.py --input-dir /tmp/l01-figures-new --out-dir /tmp/l01-figures-preview-new
```

确认新目录的图与检查结果后，再有选择地安装到 `assets/figures-20261007/`。结构图使用新版生成器；波形仍使用既有 `build_waves.py`。新图定义变更时同时重新导出 PPTX，更新母版哈希及独立证据；不覆盖旧检查目录。生成器不默认覆盖已有输出。

PPTX 使用 `svg-pptx-diagrams` skill 的 `scripts/run.py`，只传入本批37张结构图 SVG、全新导出目录和用于测量的本地字体文件。导出器逐项验证源文本与 PPTX 文本一致、对象数一致及不存在整图图片。字体与文本对象保持可编辑。本轮检测到 PowerPoint 注册，但实际调用验证脚本被 Windows 的脚本签名策略阻止，未能打开文稿或导出 Office 预览；未修改系统执行策略。也未测试 Office 的“SVG 转换为形状”。

对照页生成器为 [build_figure_gallery.py](scripts/build_figure_gallery.py)，输出新目录后将 `index.html` 安装到 `figures/20261007/`。对照页中的相对链接按该安装位置编排，可与整个 `learning/` 一起离线搬迁。

修改配图引用仍编辑 `content/*.html`，然后运行 `build_site.py`。当前 `check_structure.py --check-generated` 还会在临时副本生成新图，比较37张结构图母版与清单，并通过既有WaveDrom生成器比较6张波形；其他旧生成器校验历史资产。`check_site.py` 递归检查新旧 SVG XML；`preview_structure_site.py` 检查当前新版图及桌面/手机网页。

## 验证等级

37张结构图与上一轮逐字节一致，沿用对应SVG渲染与文字边界检查。恢复后的6张WaveDrom波形按其原始JSON和生成器验证，不能套用结构图导出器。最新网页与生成一致性证据见 `evidence/wavedrom-restoration-20261007/`。PPTX 仅有结构/文本检查，不能据此声称 Office 显示已通过。

所有图均为教学图，未新增软件构建、生产 RTL 编译/仿真、综合、板测或 ASIC 实施证据。图中的未来 NPU/ISP、DDR 旁路、工艺宏、时钟及电源域仍需后续设计与验收。

上一轮手工波形、包含它们的43页PPTX及生成输入保存在 `figure_archive/20261007-withdrawn-manual-waves/`，仅用于历史追溯。当前图集与PPTX入口均已更新。
