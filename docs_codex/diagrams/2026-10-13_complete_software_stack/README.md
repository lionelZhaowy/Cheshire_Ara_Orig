# 当前工程全组件软件栈

2026-10-13，L01。输入：`mp/ara-pulp-v2` / `bf1b4198dfd74cc78291c152b8b682d523e785c5` 加已有文档修改。按功能组件覆盖当前裸机 BSP、Ara、主机工具和可选 Linux/SDK 分路；不逐一罗列每个 API、benchmark 或可选第三方软件包。

- [SVG 母版](complete-software-stack.svg) · [PNG 阅读版](complete-software-stack.png) · [原生可编辑 PPTX](export/diagrams.pptx)
- [正文与源码索引](../../software/interfaces/foundation-software.html#complete-stack) · [Markdown](../../software/interfaces/markdown/foundation-software.md#complete-stack)
- [39 类组件清单](components.json) · [图稿生成脚本](build_figure.py) · [布局与连续箭头](layout.json)
- [导出结构检查](export/export_report.json) · [视觉查看记录](visual_review.json) · [本批次证据](../../software/interfaces/evidence/complete-stack-20261013/validation.json)

原有 [UART / GPT Flash 调用链图](../2026-10-13_foundation_software/README.md)保留。新图按五条功能分路组织，并把启动支持放在旁侧。蓝色为调用，绿色为寄存器访问，紫色为指令操作，橙色为主机构建/装载，灰蓝色为启动，橄榄色为 OS 服务。普通代码也由 CPU 取指执行；图只突出关键跨层关系，不枚举每条机器指令。

虚线框圈定基础支持代码区域，旁注说明 C/S 对象归档与头文件内联的区别；不是精确的归档成员边界，也不是目标运行时多出一层。`crt0.S` 虽画在启动侧，仍属于 `sw.mk` 的库源清单；Boot ROM 固件单独构建。CSR 辅助和 RVV 的两条箭头表示同一内核可能使用的两种操作，不是二选一。

Linux 分路区分主机构建工具、目标用户空间、内核、SBI 服务和启动程序。SDK 的 `fw_payload` 将 U-Boot 作为 OpenSBI payload；U-Boot 的 `mkimage` 是主机程序。图中启动箭头依据源码与配方，当前镜像、DTS、介质和向量上下文未运行验收。RTOS 仅标待移植；新 IP 的未来软件不画成现有组件。VGA/Serial Link、USB/CLIC 的支持范围见正文索引。

使用 `svg-pptx-diagrams-native` 的原生形状导出方法；图稿脚本本身只依赖 Python 标准库。正式交付只有此版本，调整过程保存在独立 evidence 中。PPTX 为原生形状、独立文本和完整箭头对象，无整图栅格嵌入；移动方框不保证箭头自动跟随。Office 显示/编辑未验证。

复现 SVG（仓库根执行）：

```sh
python3 docs_codex/diagrams/2026-10-13_complete_software_stack/build_figure.py
```

PPTX 使用技能目录的 `scripts/run.py --input 母版SVG --out-dir 新目录 --slide-width-in 32` 导出，输出目录须为空或不存在。PNG 来自本批次 Chrome 的 SVG 实际渲染。页面检查脚本按章节清单检查桌面/手机页面，并按 SVG viewBox 渲染所有配图；重跑必须指定新的证据目录。
