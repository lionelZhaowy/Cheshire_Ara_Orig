# SoC 全景图：共享 GB 目标与端口布局

2026-10-16，L01。输入 HEAD `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`，分支 `mp/ara-pulp-v2`。按用户最新要求，在当前目录的两页 PPT 后追加第 3 页，保留第 1、2 页；不另建图稿目录。仅图稿修订，未改 RTL 或工程配置。

**[下载三页原生可编辑 PPTX](soc_landscape_m5_gb.pptx)**

| 页码 | 内容 | PNG | SVG |
|---|---|---|---|
| 1 | 原始全景图，完整保留 | [预览](slide-01.png) | [矢量预览](slide-01.svg) |
| 2 | 下侧 M5 → GB；上一轮布局，完整保留 | [预览](slide-02.png) | [矢量预览](slide-02.svg) |
| 3 | 下侧目标端口等距排列；交换 GB 下方 M5、ISP 入口 | [预览](slide-03.png) | [矢量预览](slide-03.svg) |

![第 3 页：等距目标端口和调整后的 GB 入口](slide-03.png)

## 第 3 页的修改

- M0、M1、M2、M3、M4、M5、M_EXT 沿 Crossbar 下侧等距排列，首尾留白一致。3600 宽画布中的中心间距约为 404.286；对应目标框居中对齐。
- 保持原有文字、字号、颜色和箭头样式。多数目标框采用相同宽度；主存目标略宽，以容纳原子适配与 LLC/SPM 两个内部块。同步移动 AXI→Regbus 的下接线和 LLC→DDR 连线起点，连接关系保持。
- GB 访问适配器下方改为 **左侧 M5、右侧 ISP**。M5 回接线与 ISP 线不再交叉，删除两者之间原有的跳线；保留 ISP 跨 DDR 旁路线、M5 跨 M_EXT 下接线所需的跳线。
- CPU S0、Ara S2 仍为独立输入；Ara 保持 2 lanes / AXI64，通过失效过滤、等宽透传进入 Crossbar。GB SRAM 仍只有一个实例，下侧 GB AXI 接口框代表上方 GB 控制器的 AXI 前端。NPU、ISP、搬运引擎及 DDR 拓扑保持。

第 2、3 页均保留 `7 × 6 基础端口 + 扩展 | 64 bit 数据 / 48 bit 地址 | 地址译码 / 各目标仲裁`。7×6 是规划中的七个内部发起端与六个固定目标，S_EXT、M_EXT 另计；不是生产 RTL 已增加第六个目标的声明。

本次沿用 `industrial-svg-pptx` 工业风格，重建的路径由 `svg-pptx-diagrams-native` 后端生成，再与原生 PPT 对象合并。主 PPT 为权威输入/交付；配套 SVG 保留矢量形状和文字，供查看与后续编辑。

## 本次验证与保护

[第 3 页检查报告](evidence/page3-validation.json) · [编辑清单](evidence/page3-build-02/edit_report.json) · [输入及保护快照](evidence/page3-input.json) · [交付检查](evidence/page3-delivery.json)

- 输出三页。原第 1、2 页的 XML、关系、备注及共享依赖保持原始字节；两页 PNG/SVG 也与输入完全一致。新增第 3 页及其备注/关系，仅更新全局页数、页面列表与内容类型等必要包信息。
- 第 3 页沿用第 2 页的全部 386 个对象；其中 331 个对象未改，55 个对象调整位置、尺寸、对齐或路径。196 个文本、71 个原生箭头、26 个原生虚线对象均保留；文字内容、字号与原生线条样式未变。
- 端口等距、目标对齐、GB 两入口互换、两条路径不相交检查通过。修改区文字落在框内、互不遮挡；修改的连线连续且避开模块和文字。
- ZIP 关系、保存重读检查通过，无整图图片替代。保护快照中的 32 个既有文件未改变。
- 已实际查看第 3 页整页、[目标行局部](evidence/page3-preview-01/target-row-detail.png)和 [GB 下方入口局部](evidence/page3-preview-01/gb-input-detail.png)。前两页预览与已检查的原图字节一致。

**Office 显示/编辑未实测。** PNG/SVG 是依据显式 DrawingML 几何与文本的本地预览，采用文泉驿替代字体，不是 Office 截图。原生箭头没有绑定模块端口，移动模块后可能需要调整连线。本次没有硬件编译、仿真或板测。

## 输入和复现

本次输入为当前目录原两页 PPT，SHA-256 `3aeb085a47c843dbaa101d5e4dc85abb8b52d15c135402468c0cdb0b13608a57`。修改前版本保存在 [两页 PPT 备份](evidence/page3-before/soc_landscape_m5_gb.pptx)，同目录也保留 README 和主题 handoff 的修改前备份。先前图稿目录、原始 `soc_landscape.pptx` 和本目录第 1、2 页 SVG/PNG 均未覆盖。

以下为实际使用的最终构建与检查命令；`native_skill_root` 指向安装的原生 SVG/PPTX skill。复跑请使用尚不存在的输出目录和报告文件，保留已有证据。

```sh
python3 -B docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/append_uniform_page.py \
  --input docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page3-before/soc_landscape_m5_gb.pptx \
  --out-dir docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page3-build-02 \
  --native-skill-root "$native_skill_root"

"$native_skill_root/.venv/bin/python" -B \
  docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/preview_deck.py \
  --deck docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page3-build-01/soc_landscape_m5_gb.pptx \
  --out-dir docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page3-preview-01

"$native_skill_root/.venv/bin/python" -B \
  docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/validate_page3.py \
  --deck docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page3-build-02/soc_landscape_m5_gb.pptx \
  --preview docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page3-preview-01 \
  --report docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/evidence/page3-validation.json
```

`page3-build-01` 与 `page3-build-02` 的三页绘图 XML 完全相同；后者只把新增备注页的页码域更新为 3。PNG 由已安装的 CairoSVG 2.9.1 渲染（`publication-figures/.venv`，仅复用依赖）。首次检查遇到原始导入坐标与一位小数设计坐标约 0.005 px 的差异，将坐标比较容差设为 0.01 px 后通过；未因此修改图稿。端口间距一致性另以 0.001 px 检查。

## 第 2 页历史修订

上一轮以 [共享 GB 出口初版](../2026-10-16_soc_landscape_shared_gb/soc_landscape_shared_gb.pptx) 为输入，删除上侧 M_GB，增加下侧 M5→GB AXI 接口，局部排列 M4/M5/M_EXT，并将说明改为 7×6。该页本轮完整保留，便于对比。

[上一轮 README](evidence/page3-before/README.md)、[上一轮检查报告](evidence/validation.json)、[上一轮编辑清单](evidence/build-01/edit_report.json)与 `build.py`、`validate.py` 保留为两页版本的历史证据；其“输出两页”结论对应当时文件，不用于验证现在的三页主 PPT。主题记录见 [L01 交接](../../handoffs/L01_global_buffer_cpu_access.md)。
