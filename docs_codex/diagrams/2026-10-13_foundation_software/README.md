# Cheshire 基础软件栈

2026-10-13，L01；源码输入`bf1b4198dfd74cc78291c152b8b682d523e785c5`。本图配合[基础软件与BSP正文](../../software/interfaces/foundation-software.html#stack)，是软件关系示意，不是RTL物理拓扑或运行波形。

- [SVG母版](software-stack.svg)／[PNG阅读版](software-stack.png)
- [原生可编辑PPTX](export/diagrams.pptx)／[导出结构检查](export/export_report.json)
- [图稿生成脚本](build_figure.py)／[视觉查看记录](visual_review.json)

图中蓝色为软件调用与初始化支持，绿色为驱动/访问辅助代码，紫色为接口契约与指令/硬件行为，橙色为主机工具及平台连接。箭头均连续画出并标注语义。左侧生成宏箭头表示构建时提供访问所需定义，不是程序运行时调用regtool。当前例子中的HAL为Flash器件HAL；UART路径直接从公共库进入本地DIF。图不要求其他应用一律经过GPT、HAL或MMIO；RVV单独进入指令接口。

使用`svg-pptx-diagrams-native`，仅制作一个正式版本。SVG保留text和完整marker箭头，PPTX以原生形状、文本和线端点导出；移动模块不保证连接器自动跟随。已用Chrome查看实际PNG；结构验证不等于Office显示/编辑验收，本轮未运行Office。

在仓库根重新生成SVG：

```sh
python3 docs_codex/diagrams/2026-10-13_foundation_software/build_figure.py
```

导出器位于已安装技能`/home/zhaowenyao/.codex/skills/svg-pptx-diagrams-native/scripts/run.py`；传入`--input`母版路径和`--out-dir`新目录，不能覆盖已有非空导出。PNG来自[本轮浏览器证据](../../software/interfaces/evidence/foundation-20261013/browser-final/browser.json)中的`figure-software-stack.png`，不是由另一份绘图数据重画。
