# L01 / 4-lane与主Xbar128位联动范围

> 记录日期：2026-10-09。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期2026-10-09，输入分支mp/ara-pulp-v2，HEAD `278434024`。
- 用户授权仅答疑：解释共享访存通路，并分析Xbar128需要修改的部分。
- 本轮仅新增本交接，未提交；已有未跟踪文件原样保留。共享状态、生产源码和固定提取基线不变。

## 本轮结果（静态源码确认）

- 前答“共享访存通路64-bit”指主Xbar到原子适配器、LLC及SoC外存出口的系统侧AXI R/W数据宽度，不是VCU118 MIG的512-bit AXI接口，更不是DDR物理DQ宽度；也不意味着Xbar所有独立目的端口合计只能传64-bit。
- `hw/cheshire_soc.sv:606`只令Ara端口DW=32×lane；主Xbar取Cfg.AxiDataWidth，两者独立。4-lane/DW64是128→64→LLC64→DDR wrapper64→512；4-lane/DW128是128→128→LLC128→wrapper128→512（外存流量路径）。
- 配置入口：仿真选中配置或隔离新增配置需显式AxiDataWidth=128、AraNrLanes=4，VLEN单独决定。FPGA的gen_cheshire_xilinx_cfg也需显式系统DW128；NR_LANES宏不修改它。所有类型应由同一Cfg生成，不能只改AxiXbarCfg字面参数。
- 自动消费者：`hw/include/cheshire/typedef.svh:19`生成128-bit数据/16-bit strobe；`cheshire_pkg.sv:497`覆盖CVA6 AXI配置；`cheshire_soc.sv:454,513`原子/LLC；`dram_wrapper_xilinx.sv:99,138`从端口类型取输入宽度，保留MIG512。
- 向量WT profile Icache line128/Dcache line256；wt_axi_adapter.sv:62,65,450,485存在Icache line=AXI DW的单beat分支，128下I/D refill分别1/2拍，具备静态适配路径。不是已展开通过；不能套用标量WB profile。
- LLC容量get_llc_size=ways×lines×blocks×DW/8；默认8×256×8在DW128为256KiB，line128B（DW64时128KiB、line64B）。如保留原容量和line字节数，NumBlocks=4是可进一步验证的几何候选，不是已选方案；NumLines减半虽保容量但不保line字节数。官方固定版本LLC定义也明确block宽等于AXI宽，且支持128。
- 普通外设桥cheshire_soc.sv:369的axi_to_reg_v2仍RegDataWidth32；无需把MMIO寄存器改128，但必须验证16字节beat内不同偏移的窄访问。
- iDMA需特别限定：cheshire_idma_wrap.sv:46,65内部Regbus跟随AxiDataWidth，并非固有固定64（64是当前配置值）；:125旧axi_to_reg同样接系统DW。既有生成reg32消费者缺口在128下继续存在，不能声称DMA控制已适配。修复/局部定宽桥方案须进一步定向设计和授权，不能仅以backend参数化判定可用。
- 软件无需因系统DW128改成128位ISA/ABI；sw/link/common.ldh保守SPM64K并非等于硬件全部容量，不能机械改成256K。bootrom.S:76读取LLC_SIZE；启动与链接、栈/堆/共享缓冲区仍需一致性验收。

## 验证证据

- 执行git status/rev-parse及定向sed/rg，检查配置、SoC、CPU WT adapter、LLC、DDR wrapper、iDMA、链接文件。初始软件路径查找失败后定位到实际路径重新读取。
- 官方固定提交LLC源码在线读取成功：https://raw.githubusercontent.com/pulp-platform/axi_llc/559bcbd09a5a884dbe31e2d72fd95d024e357f39/src/axi_llc_top.sv
- CVA6固定提交WT adapter线上请求失败；CPU分析以本地99eac9a来源快照为证，不声称线上复核成功。
- 未修改参数、未编译/展开/仿真/板测/综合。来源与本地差异边界沿用前交接。

## 下一步

- 先确定4-lane的VLEN以及LLC是保持容量/line还是接受增大，再定隔离配置与构建输出。
- 最小验收含CPU启动/refill/窄访问、Ara结果与背压、LLC/SPM边界和flush、AMO/LRSC、MMIO各byte lane、DMA控制/搬运及平台128→512转换。
- 生产实施需授权；已有Ara写响应错误、iDMA和启动缺口不因128位静态分析关闭。
