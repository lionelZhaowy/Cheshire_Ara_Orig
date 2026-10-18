# SoC v1 实施难点图稿

2026-10-18；输入 `09798c1ded457e423b927844f66faae87583a20c` 及当时未提交的 v1/GB/团队文档。对应[正式专题](../../engineering/Implementation_Challenges_and_Open_Questions.md)与[交接](../../handoffs/L01_implementation_challenges.md)。

采用用户指定的 `svg-pptx-diagrams-native` skill。中文、1600×900 自由编辑画布；按问题使用结构、流程、依赖和反馈关系，连续连线保留实际方向。所有图都是待实施机制的解释，不是现有 RTL 网表。无旧图/PPT 作为生成输入，也未修改旧手调 PPT。

[下载 13 页原生 PPTX](export/diagrams.pptx) · [导出结构报告](export/export_report.json) · [检查记录](evidence/README.md)

## 页面与源文件

| 页码 | 主题 | 母版 / 阅读预览 / 最终 PPTX 本地预览 |
| --- | --- | --- |
| 01 | GB：所有权、权限与仲裁 | [SVG](masters/01_gb_ownership.svg) · [PNG](png/01_gb_ownership.png) · [PPT 页预览](evidence/final-ppt-preview/slide-01.png) |
| 02 | DDR–GB：跨层数据同步 | [SVG](masters/02_cache_sync.svg) · [PNG](png/02_cache_sync.png) · [PPT 页预览](evidence/final-ppt-preview/slide-02.png) |
| 03 | 设备地址体系：先定义地址，再选择翻译机制 | [SVG](masters/03_address_spaces.svg) · [PNG](png/03_address_spaces.png) · [PPT 页预览](evidence/final-ppt-preview/slide-03.png) |
| 04 | 配置寄存器：数量来自行为契约 | [SVG](masters/04_register_commit.svg) · [PNG](png/04_register_commit.png) · [PPT 页预览](evidence/final-ppt-preview/slide-04.png) |
| 05 | 四口 DDR：独立入口，共享物理存储 | [SVG](masters/05_ddr_ports.svg) · [PNG](png/05_ddr_ports.png) · [PPT 页预览](evidence/final-ppt-preview/slide-05.png) |
| 06 | 共享压缩前端：算法之外的事务系统 | [SVG](masters/06_compression.svg) · [PNG](png/06_compression.png) · [PPT 页预览](evidence/final-ppt-preview/slide-06.png) |
| 07 | 完成与回收：区分五个时间点 | [SVG](masters/07_completion_recovery.svg) · [PNG](png/07_completion_recovery.png) · [PPT 页预览](evidence/final-ppt-preview/slide-07.png) |
| 08 | AXI 适配：五个通道分别保持语义 | [SVG](masters/08_axi_adaptation.svg) · [PNG](png/08_axi_adaptation.png) · [PPT 页预览](evidence/final-ppt-preview/slide-08.png) |
| 09 | 实时预算：平均吞吐之外还要保证最长等待 | [SVG](masters/09_bandwidth.svg) · [PNG](png/09_bandwidth.png) · [PPT 页预览](evidence/final-ppt-preview/slide-09.png) |
| 10 | 算法与布局：计算正确和搬得动必须同时满足 | [SVG](masters/10_algorithm_layout.svg) · [PNG](png/10_algorithm_layout.png) · [PPT 页预览](evidence/final-ppt-preview/slide-10.png) |
| 11 | 启动、时钟、复位与 CDC：先建立可执行条件 | [SVG](masters/11_boot_clock_reset.svg) · [PNG](png/11_boot_clock_reset.png) · [PPT 页预览](evidence/final-ppt-preview/slide-11.png) |
| 12 | 真实工艺：宏语义、测试接管与物理签核 | [SVG](masters/12_asic_dft.svg) · [PNG](png/12_asic_dft.png) · [PPT 页预览](evidence/final-ppt-preview/slide-12.png) |
| 13 | 验证与调试：从故障触发到可追溯证据 | [SVG](masters/13_verification.svg) · [PNG](png/13_verification.png) · [PPT 页预览](evidence/final-ppt-preview/slide-13.png) |

`masters/` 为 13 幅编辑母版；`export/*.editable.svg` 是同一批图的规范化副本，不是另外 13 个主题。`png/` 为 Markdown 使用的 13 张阅读预览。`evidence/` 保留首轮及修订检查，不能拿中间稿代替正式交付。

## 视觉与语义约定

**2026-10-18 用户澄清：图 01 的 eMMC/S7→M5→GB 表示硬件可达性，不是当前软件参数加载流程。** 实际规划为上电复位、DDR 就绪后软件先 eMMC→DDR，ISP 工作时才 DDR→GB。图 01 下方的 GB 写入/交接阶段由 DDR→GB 搬运及实际 GB 使用者承担；图 03 的设备地址必须按实际目的地配置。连通图和 PPT 原件保留，图注与[正式专题第 01 节](../../engineering/Implementation_Challenges_and_Open_Questions.md#challenge-01)纠正软件含义；首次交付的检查报告仅对当时文档快照有效。

蓝：数据/请求；紫：配置/控制；绿：完成/交接/响应；红：故障/恢复。双向连线可以汇总请求与返回，不增加帧写 DMA 的读能力或帧读 DMA 的写能力；具体 AXI 通道见图 08。可选 IOMMU 边界用完整虚线矩形，其他边框实线不表示已经实现。

图 02 使用 CPU L1D/写缓冲→主 Xbar→LLC→F0 的层次；Ara 为独立 Xbar 输入；M5 GB 路径见图 01。F1 搬运走共享前端，不绕到 Controller 后面；完整四口见图 05。图 06 的 AR/AW 地址控制、数据编解码及 R/B 返回分开，旁路 R 与解压后的 R 都有连续返回通路。

图 07 的错误分支覆盖未释放阶段；“隔离→排空/受控恢复”是资源回收前提，换 token 不是阻止旧写的手段。图 03 的 IOMMU 是可选机制，尚未选定。图 04 的 pending/active 配置是待细化建议。详细来源、状态和验收条件统一维护在正式专题。

## 生成和检查

生成器 [build_figures.py](build_figures.py) 仅依赖 Python 标准库；[render_previews.py](render_previews.py) 需要 CairoSVG，PPTX 模式只解析本导出器生成的原生 DrawingML 子集，遇到不支持对象会报错。预览解析器读取**最终 PPTX**，不拿源 SVG 冒充 PPT 导出图。

在本目录运行，使用新的空输出目录：

```sh
python3 build_figures.py --out-dir candidate/masters
python3 /home/zhaowenyao/.codex/skills/svg-pptx-diagrams-native/scripts/run.py \
  --input candidate/masters/*.svg --out-dir candidate/export --aspect source \
  --font 'Microsoft YaHei' --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc
python3 render_previews.py --svg-dir candidate/masters --out-dir candidate/png
python3 render_previews.py --pptx candidate/export/diagrams.pptx \
  --out-dir candidate/ppt-preview --crops
```

本机导出器使用 skill 的 Python 环境（python-pptx 1.0.2）；渲染使用已有 `/home/zhaowenyao/.codex/skills/publication-figures/.venv/bin/python` 内的 CairoSVG 2.9.1，仅复用本地渲染环境，未使用其图稿风格或安装依赖。上述 `python3` 渲染命令需替换为装有 CairoSVG 的解释器。脚本没有硬编码该环境路径，可在其他本地环境复现。

最终验证命令：

```sh
/home/zhaowenyao/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python validate.py --out evidence/validation.json
```

字体声明为 Microsoft YaHei，本地渲染/测量回退至文泉驿正黑；PPTX 未嵌入字体。PPT 直线为原生连接线，折线为一个原生自定义几何对象，箭头是对象属性；虚线为完整边框属性。没有整页位图，文本可编辑；未绑定模块端口，不保证移动模块自动重连或 Office 自动路由。**Office 显示/编辑未实测。**
