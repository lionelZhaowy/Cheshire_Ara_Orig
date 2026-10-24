# DMA–LLC/SPM 死锁结构与过程

2026-10-20，使用 `svg-pptx-diagrams-native` skill 制作。

- [PNG 预览](dma_llc_deadlock.png)
- [SVG 母版](dma_llc_deadlock.svg)
- [可编辑 PowerPoint](export/diagrams.pptx)

上半部分表示同一 SPM 中源、目的不重叠的 DMA 搬运。紫色为地址/描述符，蓝色为数据方向，红色虚线表示阻塞关系；中间互连和缓冲合并表示。下半部分依次展示循环等待的形成，以及按次启用 `DECOUPLE_AW=1` 在原对齐用例中提前发送写地址的位置。新发现的非对齐/不同步长“写挡读”死锁记录在报告第 10.4 节，未画入本图；绿色条不能解释为所有布局均已修好。

第一条 AW 已发出，但写描述符进入 LLC 共同流水线太晚，被前面的读描述符挡住。图中并非“DMA 从未发送 AW”，也并非“LLC 不支持交替读写”。FIFO 满时反压正确；问题是反压形成循环后，没有任何一方能释放资源。

固定源码、信号采样和局限见 [DMA 信号链说明](../../engineering/DMA_Control_Path_and_Fix.md#dma-llc-deadlock)，本次实现与测试见 [DMA 长度与布局测试](../../maintenance/E01/reports/reference_rebuild_check.md#dma-aw-config-20261020)。图表示已观察到的等待关系，不是逐周期波形，也不证明 AW 解耦对所有流量均能避免死锁。

检查：从最终 SVG 生成并查看整图 PNG，核对数据方向、控制连接及循环箭头；PPTX 保存后重读，文字与 SVG 一致，包含 102 个原生对象、57 个文本对象、24 个原生箭头端点、3 个原生虚线轮廓，无整图位图。结构检查通过，Office 显示/编辑未验证。连线未绑定模块端口，移动模块不保证自动随动；字体未嵌入。
