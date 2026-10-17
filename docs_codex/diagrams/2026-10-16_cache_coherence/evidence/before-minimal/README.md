# DDR–GB 一致性图稿：文字与互连修订

2026-10-16，L01。配套正文：[缓存一致性：条件审查与架构比较](../../engineering/Cache_Coherence_Architecture.md)。

| 图 | SVG 母版 | PNG 预览 |
|---|---|---|
| 数据存储互连与一致性协调 | [system.svg](system.svg) | [system.png](system.png) |
| DDR 地址数据搬入 GB | [read-to-gb.svg](read-to-gb.svg) | [read-to-gb.png](read-to-gb.png) |
| GB 数据写入 DDR | [write-to-ddr.svg](write-to-ddr.svg) | [write-to-ddr.png](write-to-ddr.png) |

[三页原生可编辑 PPTX](export/diagrams.pptx) · [导出报告](export/export_report.json) · [检查结果](evidence/validation.json)

## 图意与本次修订

正文与三图改用直接说明动作、原因和结果的表述。图 1 按用户更正和[工业版 DDR 互连图](../2026-10-12_industrial_redraw/ddr_interconnect.pptx)重排；[较早参考图](../2026-10-11_native_reconstruction/ddr_interconnect.pptx)用于对照连接关系。

- Ara 普通地址经失效过滤、分流和位宽适配进入主 Xbar；GB 地址经共享数据代理访问 SRAM。NPU、ISP 和搬运器也使用该代理。
- GB 代理负责适配、仲裁和 bank 访问，DDR–GB 搬运器负责显式复制。图中分别画出两者。
- LLC 的回填、写回和透传请求有完整的 DDR 路径；设备搬运与图像帧写入从各自入口合流。DDR 合流画在控制器区域中作为逻辑示意，实际可由外部互连或控制器端口实现。
- 一致性协调覆盖 L1D/写缓冲、LLC、原子观察点、设备请求和 DDR 在途事务。图中另画候选缓存供数数据线，便于区分供数和探测控制。

图 1 聚焦数据存储互连；I-cache、Boot ROM、外设寄存器与像素接收流水线由对应专题展开。CPU 的 GB 标量入口仍由[CPU 接入方案](../../engineering/Global_Buffer_CPU_Access.md)单独评审。具体 IP 划分、DDR 端口数、GB 组织与缓存供数保持待评审状态。

采用 `industrial-svg-pptx` 及 `svg-pptx-diagrams-native` 后端。图 1 为 2400×1350，图 2/3 为 1920×1080，均为 16:9。连续正交线保留实际连接，跳线表示独立路径交叉。系统图双向线合并请求/返回或协作握手；图 2 展示供数过程，图 3 展示逻辑处理阶段。

## 生成与验证

SVG/PNG 使用本机文泉驿正黑，PPTX 指定 Microsoft YaHei。已逐张检查 PNG，并保存重读 PPTX：3 页、145 个文本对象、43 个原生箭头、7 个原生虚线形状，文字与 SVG 一致。Office 显示与编辑尚未实测；模块与线条为独立对象，移动模块后需相应调整连线。

生成脚本为 [build_figures.py](build_figures.py)，Chrome 渲染脚本为 [render.py](render.py)。在仓库根运行，使用新的输出目录保存每次结果：

```sh
python3 docs_codex/diagrams/2026-10-16_cache_coherence/build_figures.py --out-dir /tmp/coherence-source-new
python3 docs_codex/diagrams/2026-10-16_cache_coherence/render.py --source-dir /tmp/coherence-source-new --out-dir /tmp/coherence-render-new
```

PPTX 由已安装 skill 的 `svg-pptx-diagrams-native/scripts/run.py` 导出；依次传入三张 SVG，参数为 `--aspect source --font 'Microsoft YaHei' --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`。导出环境沿用已有安装。

本次检查入口：[validate.py](validate.py)。命令：

```sh
python3 docs_codex/diagrams/2026-10-16_cache_coherence/validate.py --out-file /tmp/coherence-validation-new.json
```

证据保存在 `evidence/`：

- [input.json](evidence/input.json) 记录 HEAD、131 个受保护文件、8 个源码输入及参考图哈希；`before/` 保存修订前正文和交接，便于恢复与对照。
- `render-01` 记录 Chrome 沙箱 socket 限制；经环境审批后，`render-02/03` 用于发现并修正标签遮挡，`render-04` 为首次排版通过结果。
- [source-04](evidence/source-04/layout.json) 与 [render-05](evidence/render-05/browser.json) 是正式输入和最终预览；根目录 SVG/PNG 与之相同。`export-01` 保留最后一次措辞微调前的导出。
- [主题交接](../../handoffs/L01_cache_coherence_architecture.md)记录文档修订、用户的图 1 更正及后续评审事项。旧图与原验证记录保留在各自日期目录。
