# L01 / Ara2 TC'24 的 lane 数与 AXI 数据位宽

> 记录日期：2026-10-09。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

- 日期：2026-10-09；输入 HEAD `278434024`。用户要求核对论文8-lane配置是否对应256-bit AXI。本轮仅新增交接，不改 RTL/配置，不提交；已有未跟踪交接/图保留。
- 已确认：论文为 Ara2: Exploring Single- and Multi-Core Vector Processing With an Efficient RVV 1.0 Compliant Open-Source Processor，DOI 10.1109/TC.2024.3388896。作者稿 https://arxiv.org/pdf/2311.07493 为2024-06-17 v2，封面DOI与本地Ara README引用一致。
- 论文第4节、PDF第5页脚注3声明SRAM word为4×L bytes；第5.1节说明lane加倍时AXI数据位宽也加倍。因此8 lanes对应32 bytes/word=256 bits。论文评估2/4/8/16 lanes，不仅8 lanes。
- 本地Ara依赖 `hardware/src/ara_soc.sv:23` 默认 AxiDataWidth=32*NrLanes；其Xbar使用AxiWideDataWidth，CPU接口固定64-bit，由ara_system.sv里的dw_converter向宽总线适配。这是依赖自带独立参考SoC，不是Cheshire当前顶层；不认定当前依赖提交与论文实验RTL完全相同。
- 当前 `hw/cheshire_soc.sv:606` 的 AraDataWideWidth=32*Cfg.AraNrLanes，818传入Ara。若仅将AraNrLanes改为8，Ara接口为256-bit，但 `Cfg.AxiDataWidth` 仍可保持64-bit，由861起的dw_converter变为256→64后接主Xbar。增加lane不自动加宽主Xbar。
- Ara顶层ara.sv把NrLanes与AxiDataWidth定义为独立参数；32×lane是参考集成/实验的带宽配置，并非RVV协议要求，亦非lane计算位宽或VLEN。论文描述lane的64-bit元素数据通路，不能把系数32解释为lane只有32-bit计算能力。
- 论文访存实验使用SRAM，不能将其直接视为当前DDR/LLC配置或本工程实测性能。
- 证据：静态读取上述本地模块、ara_soc/ara_system、README；读取论文原文第4/5.1节。未编译、未仿真、未板测，也未更改ASIC提取基线。
- 最小下一步：如用户要实施8-lane配置，先确定系统互连位宽和内存带宽契约，再对当前组合展开与动态验收；本问题不授予实施权限。不修改共享状态。
