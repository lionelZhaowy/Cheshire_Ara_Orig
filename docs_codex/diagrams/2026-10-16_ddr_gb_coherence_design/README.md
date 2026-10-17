# DDR–GB 数据同步设计配图

2026-10-16，L01。[正文](../../engineering/DDR_GB_Coherence_Design.md) · [HTML 阅读预览](design-preview.html) · [三页原生可编辑 PPTX](export/diagrams.pptx)

| 图 | 内容 | SVG 母版 | PNG 预览 |
|---|---|---|---|
| 1 | 系统连接与范围维护控制 | [system.svg](figures/system.svg) | [system.png](previews/system.png) |
| 2 | 三个缺少同步时的数据版本场景 | [versions.svg](figures/versions.svg) | [versions.png](previews/versions.png) |
| 3 | 裸机调用与硬件动作时序 | [timeline.svg](figures/timeline.svg) | [timeline.png](previews/timeline.png) |

系统图采用用户认可的 [2026-10-12 工业底图](../2026-10-12_industrial_redraw/ddr_interconnect.svg)，保留原模块坐标、尺寸、数据线和 S0/S1/S2 三口；范围维护模块沿用此前已增补位置。生成器只调用该底图的扩展入口，未采用其他重布局版本。图 2 和图 3 为本文新绘，采用 `industrial-svg-pptx` 风格及 `svg-pptx-diagrams-native` 原生导出后端。

图 2 是数据状态快照，实线表示已发生的数据传递，虚线表示待推进写入。第一个场景按当前 CVA6 写缓冲实现绘制：CPU 可以通过前递读取 2，写应答返回前 L1D 阵列仍可为 1；LLC 与 DDR 此时也为 1。后两个场景分别展示干净旧副本和迟到脏写回。设备搬运经过共享数据代理，图中用连续箭头合并表示。

图 3 按时间向下展开。L1D、LLC 的细部应答由维护引擎汇合；输入与输出准备合并成前半段，输出交还 CPU 的维护单独放在后半段。硬件同步和裸机接口均为规划中的职责，证据与条件见正文。

## 生成与检查

[build.py](build.py)复用已有绘图类和认可底图；[render_document.py](render_document.py)生成阅读预览；[validate.py](validate.py)检查链接、图稿、PPTX 和已有内容保护。使用已安装的 Chrome、Python 和原生导出环境，没有新增依赖。以下命令从仓库根运行，输出目录应为空：

```sh
python3 docs_codex/diagrams/2026-10-16_ddr_gb_coherence_design/build.py --out-dir /tmp/ddr-gb-design-svg
python3 docs_codex/diagrams/2026-10-16_cache_coherence/render.py --source-dir /tmp/ddr-gb-design-svg --out-dir /tmp/ddr-gb-design-png
python3 /home/zhaowenyao/.codex/skills/svg-pptx-diagrams-native/scripts/run.py --input /tmp/ddr-gb-design-svg/system.svg /tmp/ddr-gb-design-svg/versions.svg /tmp/ddr-gb-design-svg/timeline.svg --out-dir /tmp/ddr-gb-design-pptx --aspect source --font 'Microsoft YaHei' --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc
python3 docs_codex/diagrams/2026-10-16_ddr_gb_coherence_design/render_document.py
python3 docs_codex/diagrams/2026-10-16_ddr_gb_coherence_design/validate.py
```

Chrome 首次启动受沙箱 socket 限制，日志保存在 `evidence/render-01/`；取得本机执行权限后完成渲染。排版检查与逐张预览记录见 [browser.json](previews/browser.json)，正文显示记录见 [document-browser.json](evidence/document-browser.json)。中间源稿与渲染保留在 `evidence/source-*/`、`evidence/render-*/`，当前入口使用上表文件。

三页 PPTX 包含 154 个原生文字对象、54 条原生箭头、12 个原生虚线对象，未嵌入整图位图。[导出报告](export/export_report.json) · [最终检查](evidence/validation.json)。PPTX 字体为 Microsoft YaHei，本机预览使用文泉驿字体；箭头端点保留原生属性，移动模块后需相应调整连线。Office 显示及编辑尚未实测。

本轮输入哈希、已有三文件的可恢复备份见 [input.json](evidence/input.json) 和 `evidence/before/`。文档中的硬件正确性、性能与错误恢复用例留待实现后验证，本次没有运行 RTL 编译、仿真或板测。
