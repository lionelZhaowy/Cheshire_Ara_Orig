# SoC 全景图修正：下侧 M5 → GB

2026-10-16，L01。按用户确认的计划修改上一版两页 PPT 的第 2 页，输入 HEAD `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`，分支 `mp/ara-pulp-v2`。GB 子系统保留上方位置，下侧新增 GB AXI 接口目标框。仅图稿修订，未改 RTL 或工程配置。

**[下载两页原生可编辑 PPTX](soc_landscape_m5_gb.pptx)**

| 页码 | 内容 | PNG | SVG |
|---|---|---|---|
| 1 | 原始全景图，完整保留 | [预览](slide-01.png) | [矢量预览](slide-01.svg) |
| 2 | 下侧 M5 → GB，7×6 基础端口＋扩展 | [预览](slide-02.png) | [矢量预览](slide-02.svg) |

![修正后的第 2 页](slide-02.png)

## 已落实的修改

- 下侧目标顺序为 **M0、M1、M2、M3、M4、M5、M_EXT**。M4 接 Serial Link TX，M5 接 GB AXI 接口，M_EXT 保留为可选外部目标。局部重排右侧目标框，M0～M3 不动。
- 删除上侧 `M_GB` 及其旧连线/标签；CPU S0 和 Ara S2 保持独立。Ara 仍为 2 lanes / AXI64，经失效过滤和等宽透传进入 Crossbar。
- M5 向下连接 GB AXI 接口，标注“CPU / Ara 共用”“64-bit 数据窗口”；再从接口框右侧，经 Crossbar 外侧连续绕回现有 GB 访问适配器。M_EXT 分支与 ISP→GB 交叉处有跳线，不代表连接。
- 下侧接口框是上方 GB 控制器的 AXI 前端表示，不是第二块 SRAM，也不是搬运引擎。GB SRAM 仍只有一个实例，NPU、ISP、搬运器及 DDR 连接关系保留。
- 第 2 页说明改为 `7 × 6 基础端口 + 扩展 | 64 bit 数据 / 48 bit 地址 | 地址译码 / 各目标仲裁`。7×6 是本规划中的七个内部发起端与六个固定目标，扩展端另计；不表示当前生产 RTL 已增加第六个目标。

本次沿用 `industrial-svg-pptx` 工业风格，新增对象由 `svg-pptx-diagrams-native` 后端生成。保留原有字号尺度，通过框宽、文字位置及走线调整容纳 M5。原 PPT、上一版两页 PPT 和旧证据均未覆盖。

## 验证与边界

[验证报告](evidence/validation.json) · [编辑清单](evidence/build-01/edit_report.json) · [输入快照](evidence/input.json) · [检查迭代](evidence/check_iterations.json)

- 输出仍为两页。ZIP 中仅 `ppt/slides/slide2.xml` 内容改变，第 1 页及全部依赖保持原始字节；第 1 页 PNG/SVG 与上一版一致。
- 第 2 页 365 个原对象未改，删除 5 个旧出口对象，局部修改 13 个对象，新增 8 个原生对象。最终为 386 对象、196 个文本、71 个原生箭头。
- 端口顺序、上下位置、7×6 标签、GB 唯一实例、CPU/Ara 独立输入检查通过；新增路径连续、端点落在边界、不穿过 IP/Crossbar 本体或文字。修改区文字无越框或相互重叠。
- ZIP 关系与对象 ID 检查、保存重读、原生箭头/虚线及文本检查通过；无整图图片替代。输入保护覆盖 50 个既有文件。
- 实际查看两页及 [M4/M5/M_EXT 局部](evidence/preview-01/m4-m5-ext-detail.png)、[上方回接路径](evidence/preview-01/gb-route-detail.png)。

**Office 显示/编辑未实测。** PNG/SVG 由 PPT 显式 DrawingML 几何和文本在本地渲染，采用文泉驿替代字体，不是 Office 截图；PPTX 是主交付文件。原生箭头没有绑定模块端口，移动模块后可能需要手动调整连线。本次没有硬件编译、仿真或板测。

## 复现

当前输入：[上一版两页 PPT](../2026-10-16_soc_landscape_shared_gb/soc_landscape_shared_gb.pptx)，SHA-256 `9080ab142e19910ba0d2bc50298d9fb66800aeceefec28bb7382e6250e73f8a0`。`build.py` 直接修改此文件的第 2 页，仅写到新目录。以下是实际命令；复跑时使用不存在的输出目录，保留已生成证据。`native_skill_root` 指向安装的原生 SVG/PPTX skill。

```sh
python3 -B docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/build.py \
  --input docs_codex/diagrams/2026-10-16_soc_landscape_shared_gb/soc_landscape_shared_gb.pptx \
  --out-dir docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/evidence/build-01 \
  --native-skill-root "$native_skill_root"

"$native_skill_root/.venv/bin/python" -B \
  docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/preview_deck.py \
  --deck docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/evidence/build-01/soc_landscape_m5_gb.pptx \
  --out-dir docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/evidence/preview-01

"$native_skill_root/.venv/bin/python" -B \
  docs_codex/diagrams/2026-10-16_soc_landscape_m5_gb/validate.py
```

PNG 使用已安装的 CairoSVG 2.9.1：`cairosvg.svg2png(url=svg_path, write_to=png_path)`，渲染解释器来自 `publication-figures/.venv`，仅复用依赖。将构建的 PPTX 和渲染的两页 SVG/PNG 复制至本目录后验证。最终检查报告已存在时脚本拒绝覆盖；复查应另存证据。主题记录见 [L01 交接](../../handoffs/L01_global_buffer_cpu_access.md)。
