# L01 / Ara Crossbar 可视化与 AXI RT 答疑

## 基本信息

- 日期：2026-10-06；任务 L01。
- 用户授权：解释带 Ara 的 Crossbar 结构、绘制图片、核查 RT 开关，并评估 NPU/ISP 场景是否需要 RT。
- 输入：分支 `mp/ara-pulp-v2`，HEAD `5ddec4fb4`，开始时 `git status --short` 无输出。
- 状态：源码答疑与图片完成；RT 实施和动态验证未开展。
- 写入范围：独立 `docs_codex/diagrams/2026-10-06_axi_crossbar_ara/` 与本交接；无生产代码或共享状态变更，未提交 Git。

## 源码确认

1. `target/sim/src/tb_cheshire_pkg.sv::gen_cheshire_ara_cfg()` 继承 `DefaultCfg`，只设置 Ara/2 lanes/VLEN 2048；`hw/cheshire_pkg.sv::DefaultCfg.AxiRt=0`。仿真 SELCFG=3 的 RT 关闭。
2. `hw/cheshire_pkg.sv::gen_axi_in()` 在此配置生成 7 个输入：CVA6、Debug SBA、Ara、DMA、Serial Link、VGA、USB。`gen_axi_out()` 生成 5 个输出：Debug、Regbus 分支、LLC/SPM、DMA 控制、Serial Link。LLC/SPM 共用编号；多个地址规则不等于多个输出端口。
3. `target/xilinx/src/cheshire_top_xilinx.sv::gen_cheshire_xilinx_cfg()` 关闭 SerialLink，按 USE_USB 决定 USB，按 ARA 启用 Ara，不覆盖 AxiRt。当前 `add_sources.vcu118.tcl` 定义 ARA/2 lanes/2048、未定义 USE_USB，对应 5 输入/4 输出、RT 关闭。这是当前源码与脚本推导，不是 bitstream 验收。
4. `hw/cheshire_soc.sv::i_ara_axi_inval_filter / i_ara_axi_dw_converter` 位于 Ara 访存输出与 Crossbar 之间；`AraDataWideWidth=32*Cfg.AraNrLanes`，本配置为 64 bit，与系统数据位宽相同。
5. 本地 `axi_xbar.sv::i_xbar_unmuxed / gen_mst_port_mux`、`axi_xbar_unmuxed.sv::gen_slv_port_demux` 为逐输入地址译码/demux、逐输出 mux 仲裁结构。`axi_mux.sv` 使用轮询仲裁和 W 来源 FIFO；事务级仲裁不等于字节带宽均分。
6. 本地 `axi_rt_unit.sv` 包含 burst splitter、write buffer、按 AR/AW 握手与 LEN/SIZE 统计的字节预算及隔离控制。`axi_rt_unit_counter.sv` 管理周期与预算。预算耗尽触发阻止新请求的机制，不能理解为终止已经接受的传输或固定时间超时；恢复与边界行为仍须实测。
7. `axi_rt_reg_pkg.sv` 固定 `NumMrg=6, NumSub=2, NumReg=12`，Ara 仿真配置需要核对/重新生成。`sw/tests/axirt_budget.spm.c` 的 DMA 编号 `num_int_harts+1` 未计入 Ara，套用到上述 7 输入配置会指向 Ara，而不是 DMA。

## 设计建议（尚未实施）

- NPU/ISP 共享 DDR 宜具备服务质量设计：ISP 以输入速率、FIFO 深度和最坏停顿约束服务；NPU 限制连续长突发/过量流量，CPU 保留响应机会。实际预算、周期与突发长度不能在缺少规格时冻结。
- 用户已要求 NPU/ISP 绕过 LLC，因此流量管理必须覆盖它们实际通往共享 DDR 的汇聚入口；仅启用原 SoC Crossbar 前的 RT 不会限制独立旁路。
- LLC 下游已汇合 CPU/Ara，按此入口管理不能区分两者，也不能按上游请求字节直接推导实际 DDR 流量。
- 建议先以 RT 关闭建立功能与竞争性能基线，再评估经过验证的 AXI RT、加速器自身限流和 DDR 控制器 QoS；并非默认启用当前 alpha IP。
- 官方 AXI-REALM 论文用于补充原理，不将论文测试数字或新版本能力归给本地快照。上游问题 #13（预算耗尽恢复）、#16（预算与突发组合的隔离）提示应做定向本地回归，不证明本地必现。

## 交付与验证

- `docs_codex/diagrams/2026-10-06_axi_crossbar_ara/crossbar_ara.svg`：当前仿真 Ara 配置，包含输入、译码/demux、连接矩阵、mux 仲裁、目标及 FPGA 差异。
- 同目录 `ddr_qos_proposal.svg`：标注“设计建议，尚未实现”的 DDR 旁路与流量管理位置。
- 同名 PNG 为 Chrome 本地渲染，分别 1680×1160 / 1680×620；人工查看，文字、连接和边界标签可见。
- 使用 `apply_patch` 创建 SVG。渲染命令采用临时 profile，`google-chrome --headless --no-sandbox --disable-gpu --disable-dev-shm-usage --disable-background-networking --no-first-run --no-default-browser-check --hide-scrollbars --user-data-dir=<mktemp目录> --window-size=<对应尺寸> --screenshot=<PNG绝对路径> file://<SVG绝对路径>`。
- 沙箱内 Chrome 首次运行因 socket `Operation not permitted` 退出 133；获执行权限后，两次本地渲染退出 0。未复跑既有教材检查或覆盖历史证据。
- 未 RTL 编译/展开/仿真、未软件构建、未板测、未实施 ASIC 提取或 RT 集成。

## 外部补充资料

- 本地 axi_rt 依赖 HEAD：`641ea950e24722af747033f2ab85f0e48ea8d7f8`；根 Bender.yml 声明 `0.0.0-alpha.9`，实际使用 Bender.local 的固定源码目录。
- [AXI-REALM 原论文](https://arxiv.org/abs/2311.09662)：周期预算、流量整形与突发干扰的原理。
- [上游 Issue #13](https://github.com/pulp-platform/axi_rt/issues/13)、[Issue #16](https://github.com/pulp-platform/axi_rt/issues/16)：仅作为验证输入。

## 最小下一步

1. M01 根据 ISP 帧格式/速率/FIFO、NPU 读写规模和供应商 DDR QoS 接口建立带宽及最坏服务时间预算。
2. V01 若验证 RT，先匹配生成寄存器尺寸和软件 manager 编号，再覆盖突发分片、预算耗尽/恢复、背压和 CPU/Ara/设备并发。
3. 本次仅新增答疑图片，没有已实施架构事实变化，无需合并共享状态或改变任务表状态。
