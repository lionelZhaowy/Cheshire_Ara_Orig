# 软硬件接口案例图

2026-10-13，L01；输入主仓库 `c4162204c`。本轮使用 `svg-pptx-diagrams-native`，按教学分层使用浅色区、彩色边框和带标签的完整箭头。静态关系图不代表目标运行波形。

| 图 | SVG母版 | 解释位置 |
|---|---|---|
| 启动和装载责任 | [boot.svg](boot.svg) | [构建启动](../../software/interfaces/build-boot.html#boot) |
| 字符输出逐层对应 | [uart.svg](uart.svg) | [UART案例](../../software/interfaces/cases.html#uart) |
| DMA配置、传输和取回 | [dma.svg](dma.svg) | [DMA案例](../../software/interfaces/cases.html#dma) |
| Ara专用请求和数据通路 | [ara.svg](ara.svg) | [指令接口](../../software/interfaces/instructions.html#ara-path) |

[四页原生可编辑PPTX](export-reviewed/diagrams.pptx) · [导出结构报告](export-reviewed/export_report.json)。单线/折线箭头作为一个原生对象导出，文字仍可编辑；连接器未绑定模块，移动模块不保证线条自动跟随；未实际运行Office。

源码是[build_figures.py](build_figures.py)及生成SVG。生成母版：

```sh
python3 docs_codex/diagrams/2026-10-13_software_hardware_interfaces/build_figures.py
```

导出使用已安装技能的 `scripts/run.py --input boot.svg uart.svg dma.svg ara.svg --out-dir 新目录`（在本图目录或使用完整路径），脚本位于 `/home/zhaowenyao/.codex/skills/svg-pptx-diagrams-native/scripts/run.py`。导出工具拒绝覆盖非空目录；当前 `export-reviewed/`为最终交付，`export/`及`export-final/`保留中间导出供追溯，修改后先导出到新目录再核对。

实际Chrome逐图预览保存在[专题浏览器证据](../../software/interfaces/evidence/browser-review/browser.json)及相邻 `figure-*.png`；[视觉记录](visual_review.json)记录作者查看与输入哈希。结构检查不能代替Office显示/编辑验收。
