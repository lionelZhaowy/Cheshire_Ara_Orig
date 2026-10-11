# L01 / AXI Crossbar 数据与地址位宽答疑

> 记录日期：2026-10-09。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-09；用户要求根据架构图和当前源码确认 Data Width / Address Width 配置。
- 输入 HEAD：`278434024`；已有启动/时钟/DDR等未跟踪交接与图原样保留。
- 状态：静态分析完成；只新增本交接，未改生产代码或配置，未提交。

## 结论与证据

1. `hw/cheshire_pkg.sv::DefaultCfg` 的当前基线为 DW=64、AW=48。`cheshire_soc.sv::AxiXbarCfg` 直接消费 `Cfg.AxiDataWidth` 和 `Cfg.AddrWidth`。`hw/include/cheshire/typedef.svh` 据此生成数据、WSTRB、AWADDR/ARADDR类型，Xbar 没有写死 64/48。
2. AXI规范的 DW 为 8/16/32/64/128/256/512/1024。当前 RV64/64-bit AMO 路径不能据此选择32或更小：`axi_riscv_amos.sv:1078` 要求 RISCV_WORD_WIDTH <= AXI_DATA_WIDTH，SoC 实例传64；WT CPU也要求 AxiDataWidth>=XLEN。
3. Cheshire配置类型 `dw_bt=bit[9:0]`、`aw_bt=bit[5:0]`：可表示上限分别1023、63。结合标准DW和当前RV64路径，字段级候选是64/128/256/512；1024和AW64均会截断为0。候选不是整套SoC验收通过清单。
4. 本地官方 `docs/um/arch.md:148` 声明 AW=32..64，且其他宽度字段写shrt_bt；与当前配置类型不一致。本轮按源码判定AW64不能直接设置。地址宽度不要求2的幂，但窗口、CPU和目标端的限制仍要核对。
5. 默认外存窗口排他终点4GiB、SerialLink终点8GiB会转换为addr_t（`cheshire_soc.sv::gen_axi_map`）。保持默认LLC窗口需要至少33位以表示终点；保持默认SerialLink窗口需至少34位。AW32不能仅改字段而沿用整张默认地址图。
6. CPU 的 `gen_cva6_cfg()` 会将两项宽度同步覆盖到CVA6，当前CPU入口没有一段固定64-bit到系统宽度的dw_converter。因此修改SoC DW也会影响CPU缓存适配。
7. Ara向量profile `cv64a6_imafdcv_sv39` 是WT、IcacheLineWidth=128、DcacheLineWidth=256；wt_axi_adapter显式有Icache单beat等宽分支，64/128可作为不改变cacheline时进一步验证的候选；DW256/512会让现有Icache line/DW比值为0，不能直接视为可用。未展开或运行128配置，不声称其整机通过。
8. 标量默认 `cv64a6_imafdchsclic_sv39_wb` 是WB、I/D line=128。std_nbdcache要求DcacheLineWidth/DW属于{2,4,8,16}；DW128时比值1，直接违反断言。不能把Ara的候选范围套给标量WB profile。
9. Ara自身DW=32*NrLanes；2 lanes为64，经现有axi_dw_converter适配到系统DW。改变系统DW不自动改变Ara lane数量或CPU XLEN。
10. `get_llc_size()` 包含DW/8；默认geometry不变，DW128会使LLC/SPM容量从128KiB变成256KiB。普通Reg接口仍32-bit，由axi_to_reg_v2适配。iDMA旧桥/生成reg32消费者已有位宽缺口，不能因backend参数化就保证控制接口支持加宽。
11. LLC顶层DW断言明列64/128/256/512，但尾项为1028。相同依赖提交官方源码也存在此异常，不能将其当作标准1024支持；本地10-bit字段原本也无法设置1024。本轮不修复、不升级。
12. 当前VCU118 wrapper 的SoC出口DW64/AW48，在dram_wrapper_xilinx里转换到MIG DW512、地址低31位。MIG 512-bit接口不代表主Xbar已经512-bit；主Xbar也不必与DDR端口同宽。

## 验证边界与资料

- AXI依赖提交：`39f5f2d51c5e524f6fc5cf8b6e901f7dcc5622d7`；LLC：`559bcbd09a5a884dbe31e2d72fd95d024e357f39`。
- 使用rg/nl/sed读取定义、实际传参、profile消费者和断言；取回相同提交官方AXI/LLC资料，核对AXI规范的数据位宽清单。
- 官方AXI文档：https://raw.githubusercontent.com/pulp-platform/axi/39f5f2d51c5e524f6fc5cf8b6e901f7dcc5622d7/doc/axi_xbar.md
- 官方LLC源码：https://raw.githubusercontent.com/pulp-platform/axi_llc/559bcbd09a5a884dbe31e2d72fd95d024e357f39/src/axi_llc_top.sv
- 未RTL编译/展开/仿真/板测；参数表示范围、静态候选、已验证配置分开报告。

## 下一步

- 用户若要求加宽，再明确目标profile/DW/AW/地址图/LLC容量，定向验收CPU refill、窄访问、Ara、DMA控制/数据和DDR适配；不凭架构图直接改共享配置。
- 本次无实现状态改变，不更新共享任务状态；原ASIC固定基线不因本答疑自动调整。
