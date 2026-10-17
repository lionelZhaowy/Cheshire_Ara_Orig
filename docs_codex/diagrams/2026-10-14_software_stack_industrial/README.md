# 软件栈工业风格版

2026-10-14，L01；输入分支`mp/ara-pulp-v2`，HEAD `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`，开始时工作区干净。用户明确要求使用`industrial-svg-pptx`重绘，供汇报版本选择；本图为新增候选，不替换正文中的原版。

- [新旧对照页](index.html)
- [工业版SVG](software-stack-industrial.svg) · [PNG](software-stack-industrial.png) · [原生可编辑PPTX](export/diagrams.pptx)
- [原版图稿](../2026-10-13_complete_software_stack/README.md) · [39类组件源码索引](../../software/interfaces/foundation-software.html#component-index)
- [生成脚本](build_figure.py) · [原生导出报告](export/export_report.json) · [验证记录](evidence/validation.json)

## 改绘范围

采用2880×1620的16:9横向画布、白底、方角、统一深色细边框和低饱和嵌套区域。应用/向量计算为淡粉，BSP与驱动为淡蓝，访问辅助与启动支持用淡紫，接口契约用淡杏，SoC存储与可选OS分路用淡绿。线色仍区分函数调用、构建/装载、寄存器访问、指令执行、启动及OS服务；不以配对编号替代真实连接。

沿用原图34个组件分组和35条关系箭头，另有6条图例箭头。图内缩短了少量说明文字；器件HAL、DIF、MMIO/CSR辅助、Ara入口、主机工具、Boot ROM/crt0/ZSL、libgcc/libc及Linux/SDK分路均保留。组件完整含义继续使用原正文索引，不重新建立另一套软件分类。虚线表示可选Linux分路或尚缺平台实现；BSP代码区用实线边界，避免将库归档范围误读为可选功能。

`libcheshire.a`仍是归档组织形式；头文件内联由调用者编译，crt0也参与归档。Ara执行RVV指令；Linux系统调用、SBI服务、OpenSBI→U-Boot→Linux启动关系分别表示。图不证明DDR初始化、设备驱动、Linux或RTOS已运行验收。

本轮核对旧批次157个非文档源码引用，哈希均未改变，详见[输入记录](evidence/input.json)。这只是图稿内容延续的证据，不是重新执行功能测试。旧图、原PPTX、正文和历史证据不改动。

## 导出与阅读

PPTX由同级`svg-pptx-diagrams-native`后端生成，为单页16:9原生形状、文本、完整箭头和虚线对象；不嵌入整图图片。SVG字体为Microsoft YaHei，浏览器使用WenQuanYi Zen Hei/sans-serif回退；PPTX不嵌入字体。Office显示/编辑未验证，移动方框不保证箭头自动跟随。

在仓库根重建SVG：

```sh
python3 docs_codex/diagrams/2026-10-14_software_stack_industrial/build_figure.py
```

导出后端通过已安装`industrial-svg-pptx`目录的父目录定位同级`svg-pptx-diagrams-native/scripts/run.py`；传入`--input`母版SVG、`--out-dir`新目录、`--aspect source --slide-width-in 16`。PNG由本机Chrome实际渲染。`preview.py --out-dir 新目录`检查文字边界、正交路径、文字/连线遮挡、所属块边界，并保存1920×1080汇报预览和新旧对照页的桌面/手机截图。

全组件图信息密集，建议通过原尺寸SVG/PNG查看细节；原有UART/Flash案例图仍适用于逐条讲解。当前两版供用户选择，尚无新的采用决定。
