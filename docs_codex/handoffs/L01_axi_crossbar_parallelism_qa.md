# L01 / AXI Crossbar 双发起者并行答疑

> 记录日期：2026-10-09。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-09；用户要求结合源码解释两个 Master 同时访问两个不同 Slave 的并行性。
- 输入 HEAD：`278434024`；已存在启动/时钟相关未跟踪图与交接，未覆盖。
- 状态：源码分析完成；仅新增本记录，无 RTL/软件/配置改动，未提交。

## 源码确认与结论

- 本地 AXI 依赖 HEAD：`39f5f2d51c5e524f6fc5cf8b6e901f7dcc5622d7`。其 doc/axi_xbar.md 与同提交官方资料均说明全连接结构；多个地址规则可以指向同一输出。
- hw/cheshire_soc.sv:231–275：NoSlvPorts=AxiIn.num_in、NoMstPorts=AxiOut.num_out、Connectivity='1、LatencyMode=CUT_ALL_PORTS；没有配置成全局共享单发起通路。
- axi_xbar_unmuxed.sv::gen_slv_port_demux（108 起）：逐输入实例化 AW/AR 地址译码与 demux。gen_xbar_slv_cross/gen_xbar_mst_cross（232 起）按输入 i、输出 j 独立连接 slv_reqs[i][j] → mst_ports_req_o[j][i]。
- axi_xbar.sv::gen_mst_port_mux（131 起）：逐输出 i 实例化 axi_mux，读取 mst_reqs[i]，输出 mst_ports_req_o[i]；generate for 代表并存的硬件实例，并非轮流执行的软件循环。
- axi_mux.sv::i_aw_arbiter（264 起）和 i_ar_arbiter（409 起）为每个输出各自的写地址/读地址仲裁；W 来源 FIFO 也随各输出实例独立存在。
- 因此，两独立输入访问两独立输出，在各通路可接收、无跟踪/容量约束阻挡时，可并行接受和传输。同一输出的同一地址通道每次只仲裁出一路；多笔已接受事务仍可在途重叠，不必等待第一笔完整响应后才仲裁下一笔。
- 同输出读/写使用独立 AR/AW 仲裁，互连允许重叠，最终并行执行程度由目标实现决定。
- hw/cheshire_pkg.sv::gen_axi_out：SPM 与外存窗共用 llc 端口；UART/GPIO 等在主 Crossbar 看都是 reg_demux 端口。逻辑地址或外设名不同不保证独立输出。

## 证据与边界

- 通过 git status、rev-parse、nl/sed/rg 定向检查源码与本地官方 IP 文档；官方相同提交文档：
  https://raw.githubusercontent.com/pulp-platform/axi/39f5f2d51c5e524f6fc5cf8b6e901f7dcc5622d7/doc/axi_xbar.md
- 当前 CUT_ALL_PORTS 有通道流水线切分；可并行不等于输入提出请求当拍就穿透到目标，VALID/READY 握手仍由通路缓冲和背压决定。
- 未编译、未仿真、未板测；没有新增动态验收结果。已有教材事务模型不是本轮生产 RTL 验证。

## 最小下一步

- 如后续用户要求动态展示，针对不同输出/同输出同方向/同输出读写设置独立小型 Crossbar 测试，记录输入和输出握手、数据拍及响应；无需启动完整生产 SoC 构建。
- 本次结论是既有结构的进一步解释，无共享实现状态变化，不修改 PROJECT_STATE/任务表。
