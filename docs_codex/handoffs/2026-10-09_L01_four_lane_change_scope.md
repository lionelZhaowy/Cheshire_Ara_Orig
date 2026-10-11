# L01 / 4-lane 修改范围答疑

## 基本信息

- 日期：2026-10-09；分支mp/ara-pulp-v2，输入HEAD `278434024`。
- 授权：仅分析改为4-lane需要修改的部分；未授权实施。
- 状态：静态范围分析完成；仅新增本交接，未提交，已有未跟踪文件保留。

## 本轮结果

- 最小候选：Ara=1、NrLanes=4、VLEN仍2048、系统DW64/AW48。需区分本地依赖`config/4_lanes.mk:22`的预设：nr_lanes=4、vlen=4096；选择该预设会同时改变VLEN，不能声称只改lane。
- 仿真：`target/sim/src/tb_cheshire_pkg.sv:30`当前配置3硬编码lane=2。应在获授权后新增隔离4-lane配置或修改选中配置，并保持SELCFG索引一致；仅改NR_LANES宏不会覆盖该字段。
- FPGA：`target/xilinx/src/cheshire_top_xilinx.sv:125`使用ARA/NR_LANES/VLEN宏。`ara/cheshire/Makefile:26`选择ARA_CONFIGURATION；4_lanes预设为4/4096，若只增lane须显式覆盖vlen=2048。当前加源脚本宏仍2/2048，未来生成清单应使用隔离输出保护旧工程，不执行会覆盖现有脚本的规则。
- CPU仍需向量profile和真实decoder；无需因为4-lane修改CPU XLEN或CVA6Cfg.VLEN。
- `hw/cheshire_soc.sv:606,861`自动形成Ara128→系统64转换，无需手改lane实例、VLSU、slide/mask或转换器逻辑。此为现有适配路径，不是编译或动态通过。
- 系统DW64/AW48不变时，本次没有改变CPU缓存参数、LLC/SPM容量、地址图或MIG位宽的必要；若另选DW128，则是扩大范围的系统位宽分析。
- VRF核算：`lane/lane.sv:30`容量公式，ara_pkg的NrVRFBanksPerLane=8、ELEN=64，vector_regfile的NumWords=VRFSize/8/64。4/2048每lane2KiB，每bank32个64-bit字，总8KiB；4/4096每lane4KiB，每bank64字，总16KiB。静态整除与非零成立，不代表完整组合合法或时序通过。
- 软件：`ara/cheshire/sw/Makefile:23,33,35`独立选择配置并传NR_LANES、VLEN、ARA_NR_LANES。fmatmul用lane数控制对齐和利用率分母；`cheshire/sw/include/rvv_test.h:197`仍按1024×lane派生VLMAX，未直接使用VLEN。4/2048不能只重编译就假定测试的硬件长度假设正确，需按各用例复核有效vl、期望值和边界覆盖；其宏名不应直接等同RVV体系结构VLMAX。

## 验证证据

- 本轮运行git status/rev-parse，cat两份lane配置，rg/sed读取硬件/软件消费者；未改生产RTL/sw或配置，未编译/展开/仿真/板测/综合。
- 官方固定提交的4_lanes.mk raw与GitHub页面均尝试获取，工具返回Cache miss；本轮预设取值以当前本地vendor文件为证，不声称线上再次核验成功。来源提交沿用SNAPSHOT.tsv的Ara `2895ba907e9eb14b3464609dc791a969d159a7c3`。

## 决策与下一步

- 用户尚未选择VLEN2048或4096、实施平台或系统加宽；固定ASIC提取基线未改变，共享状态不更新。
- 实施前选择候选，列隔离配置/清单/软件产物路径；验收实际展开4-lane、128→64转换、vlenb及向量结果、mask/尾部/跨lane、背压和共享数据。已有错误处理缺口保持开放。
