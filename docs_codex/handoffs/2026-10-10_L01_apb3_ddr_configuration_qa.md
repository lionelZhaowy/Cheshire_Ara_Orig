# L01 / APB3 DDR 配置接口兼容性与频率答疑

## 基本信息

- 日期：2026-10-10；授权范围：确认现有 APB 版本、分析 Regbus→APB3 可行性和供应商所述 100 MHz 限制。
- 输入：`mp/ara-pulp-v2`，HEAD `2784340240915fe4338ec54bfd613723b127d62e`。
- 保留既有 M01 契约修改及未跟踪图、交接。本轮仅新增此记录，未提交；分析完成，集成待验证。

## 本轮结果与依据

- 源码确认：本地 APB README 声明 APB4；`register_interface/src/reg_to_apb.sv:35` 起透传地址/数据/选通，含 PSTRB、固定 PPROT=010；47–70 行 SETUP/ACCESS 状态机支持 PREADY 等待并返回 PSLVERR。单 clk_i，无分频或 CDC。
- 版本：`.bender/UPSTREAM.lock` 记录 register_interface 0.4.4 / ae616e5a1ec2b41e72d200e5ab09c65e94aebd3d，apb 0.2.4 / 77ddf073f194d44b9119949d2421be59789e69ae，apb_uart 0.2.1 / 6c7dde3d749ac8274377745c105da8c8b8cd27c6。实际由 Bender.local 的本地快照覆盖；上述为来源记录，不宣称工作区与上游零差异。
- 实际例子：`hw/cheshire_soc.sv:1347` 实例化 reg_uart_wrap；`.bender/git/checkouts/apb_uart-38dcfab592cbc1a1/src/reg_uart_wrap.sv:62` 实例化 reg_to_apb，76 行起连接 apb_uart，只使用 APB3 共有信号，未连接 PSTRB/PPROT。这证明现有连接方式，不证明新 DDR 接口已验证。
- SoC 主外设互连是 Regbus：`hw/cheshire_soc.sv:369` 的 axi_to_reg_v2 固定 RegDataWidth=32，407 行分流，432 行导出外部 Regbus 从设备口；不能把整个 Cheshire 描述为 APB4 总线系统。
- 官方规范：Arm IHI0024E 前言版本沿革、3.2.1/Table 3-1、3.5.1/Table 3-3 说明 APB3 的等待/错误，APB4 新增选通/保护；有 PSTRB 主端接无 PSTRB 从端可兼容但不支持稀疏写，有 PPROT 主端接无保护从端可忽略该输出。参考 https://documentation-service.arm.com/static/63fe2c1356ea36189d4e79f3 。本轮只引用 APB3/4 相关规则，不把 APB5 特性套入本地。
- 官方模块路径亦核查：https://github.com/pulp-platform/register_interface/blob/master/src/reg_to_apb.sv 和 https://github.com/pulp-platform/register_interface/blob/master/src/reg_cdc.sv ；实现结论以本地固定快照为准。

## 建议及接口条件（未实施）

- 可以接受供应商 APB3：保留桥内部 APB4 struct，在边界仅连接 APB3 共有端口；桥内仍引用 pstrb/pprot，不能直接传入缺字段 struct。
- 若供应商寄存器为32位，约定32位对齐全字访问，写请求 wstrb=1111。建议新增窄范围检查，对部分写/全零选通写拒绝且不发下游 PSEL；不默默忽略选通。不使用通用自动读改写替代选通，因为 W1C/读清零/硬件更新等寄存器语义可能破坏数据。
- PPROT 在现桥固定010，不透传 CPU 权限；需要访问保护时单独设计上游权限控制。地址是字节还是字索引、局部偏移、数据宽度需核对供应商。
- PREADY/PSLVERR按IP实际契约连接。只有确认永不等待才可将PREADY绑1；无错误输出时可按契约绑PSLVERR=0，但会缺失该级错误报告。现桥无超时，永久PREADY=0会挂住请求，CPU软件超时不能保证从阻塞load中恢复。

## 时钟分析

- 当前 VCU118：`target/xilinx/scripts/impl_ip.tcl:106` 请求50 MHz；`target/xilinx/src/cheshire_top_xilinx.sv:156,526` 接 soc_clk 至 SoC；UART桥与IP共用clk_i。为源码配置证据，未测量板上频率，也没有供应商DDR APB已集成的证据。
- 100 MHz是用户转述的供应商限制，不是APB3/4协议固定频率。PCLK需满足供应商、桥、适配逻辑和实现STA限制；100 MHz对应10 ns，50 MHz对应20 ns。
- 候选：外部32位Regbus→reg_cdc→在PCLK运行的reg_to_apb→APB3 DDR配置口。可先评估50 MHz，供应商需确认最低频率、初始化时间及相对其他时钟约束；100 MHz工作点以IP条件和STA为准，不冻结频率。
- `register_interface/src/reg_cdc.sv:274`提供双时钟域；默认cdc_2phase的复位限制见`common_cells/src/cdc_2phase.sv:16`：POR同时断言、各域同步释放，不能任意独立热复位；还需按其注释落实CDC物理约束。此处只是候选，尚未验收。
- 仅给从设备分频不成立，桥和下游APB需要同PCLK；同PLL分频也需明确跨域实现与时序约束。PREADY等待不降低时钟频率，APB至少两拍亦不把100MHz许可变成200MHz。
- APB段理想每笔时间=(2+W)/fPCLK；50/100 MHz零等待分别40/20 ns、25/50百万笔每秒，32位等效100/200 MB/s。只为总线理论上限，未含AXI、CDC、软件和DDR内部初始化/训练耗时；APB配置时钟不等于DDR AXI时钟或存储器速率。

## 验证证据及下一步

- 执行git status/rev-parse/branch、rg/nl/cat定向源码检查、官方网页规范检索；git diff --check在新增记录前通过。早期两条带不存在glob的rg被zsh拒绝，随后改用明确路径完成相关定位。
- 未编译、未仿真、未板测、未综合或STA；没有修改生产RTL或共享状态。结论是协议和源码层面可行，不是供应商对接通过。
- 下一步：供应商确认APB3端口/寄存器访问规则、PCLK范围与复位/就绪关系、等待上限和错误响应；M01/E01再设计外部Regbus支路与适配；V01验证等待、连续访问、非法写、错误、CDC与复位。共享工程状态未发生变化，无需关闭既有任务。
