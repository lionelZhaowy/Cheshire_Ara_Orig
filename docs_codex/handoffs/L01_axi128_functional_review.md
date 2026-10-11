# L01 / 系统AXI128位功能风险定向审查

> 记录日期：2026-10-09。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-09；任务L01；授权仅源码分析、官方核对及验证评估，未授权生产修改或大型构建。
- 用户最新确认：接受位宽联动引起的缓存容量等增长，优先保证功能正确；不再把保持128KiB作为本轮目标。
- 输入分支mp/ara-pulp-v2，HEAD `2784340240915fe4338ec54bfd613723b127d62e`；已有未跟踪文件保留。
- 分析对象：Ara4-lane、系统AXI DW64→128、AW48不变、向量WT profile；VLEN仍未单独冻结，2/4-lane软件配置问题沿用前交接。
- 状态：定向静态审查完成；确认Debug新阻塞项，深化既有iDMA证据。没有完整SoC功能通过结论。

## 结论修正

此前“主要改配置及必要接口修复”的说法需明确收紧：**当前Cheshire直接把系统DW128传给Debug Module，存在具体功能不兼容，不能原样只改参数就认定整机可用。** iDMA控制桥既有问题也必须处理。Xbar/LLC支持128不代表外围所有消费者支持。

## 确认问题：Debug随系统加宽到128不成立

- `hw/cheshire_soc.sv:1034` dm_top.BusWidth=Cfg.AxiDataWidth；两侧axi_to_mem_interleaved与axi_from_mem也直接使用系统DW，当前没有独立Debug DW隔离。
- `.bender/git/checkouts/riscv-dbg-1a98531d53bb4602/src/dm_csrs.sv:171` sbaddr_q/sbdata_q固定64-bit；:191按BusWidth选取，在128下取[127:0]越界。工具可能报错/告警或产生未知高位，未实测具体工具行为。
- `src/dm_sba.sv:74`的byte enable：32-bit访问只有BusWidth==64才选择4个字节，否则全置1；64-bit访问直接全置1。BusWidth128下分别得到16'hffff，而非正确4/8字节掩码。对于16字节对齐基址的32位写，本应000f，实际ffff。此为源码条件代入，不是波形实测。
- `src/dm_mem.sv:218`仅有64分支和32分支，128进入32分支；返回低32位零扩展，不能组成CPU需要的128位debug取指/数据返回。:64 MaxAar也只区分64与其他。
- 功能影响：JTAG SBA可能多写相邻数据；debug park ROM/progbuf/abstract command执行不可靠；程序加载、暂停恢复、寄存器调试可能受损。正常启动未执行Debug路径不代表Debug正确。Debug当前无简单Cfg禁用开关。
- 官方当前README明确Debug bus/SBA支持32/64，master dm_sba保留相同32/64掩码分支。未发现可直接引用的128支持修复，不能声称全上游历史已穷尽检索。
- 设计建议（未实现）：DM和其mem桥维持64；SBA主端经64→128、Debug从端经128→64。两方向都需处理；原子处理仍在适当的系统側，不把ATOP问题转嫁给不支持的窄桥。地址64→SoC48的既有裁剪规则也须保留。优先复用已有axi_dw_converter，不扩大DM协议实现。

## 确认既有问题：iDMA控制Regbus

- `hw/cheshire_idma_wrap.sv:46,65,125`的data_t、Regbus及旧axi_to_reg都跟随系统宽度。
- register_interface的`src/deprecated/axi_to_reg.sv`保留AXI同宽转换到AXI-Lite/Regbus；`src/axi_lite_to_reg.sv:214`直接转发wdata/wstrb、:184直接返回rdata，无宽到32的lane选择。
- idma `target/rtl/idma_reg64_2d_reg_top.sv:32`固定DW32，:58截取低32-bit wdata及低4-bit wstrb，:60把32位读返回零扩展。
- 128-bit下对base+4/+8/+12的32位写会在高byte lane，低4-bit strobe为0；读返回又未摆放到对应lane。与CPU正常WSTRB生成矛盾。该问题在DW64已存在，128扩大偏移覆盖，非本轮新引入才有。
- 设计建议：数据backend维持128；控制侧采用系统128→固定Reg32的合法适配，评估已有axi_to_reg_v2。保持寄存器地址与单次读副作用，HAL按生成寄存器粒度访问。不能因模块名reg64推断其总线DW64。

## 有静态适配证据的路径（均未动态通过）

1. Xbar：cheshire_soc.sv:203,242与typedef.svh:19统一生成数据/字节使能；128在dw_bt表示范围内。必须改同一Cfg，不能仅改Xbar参数常数。
2. CPU：gen_cva6_cfg:497覆盖AXI位宽；当前向量WT Iline128/Dline256。wt_axi_adapter:65,485明确1拍I refill和2拍D refill；:142复制XLEN64写数据、:208按地址低4位选WSTRB。wt_dcache_mem:274按AXI偏移选择uncached读64位字，:377等断言满足256>=128>=64；wt_dcache_missunit:286有AXI>64的AMO返回字选择。不是标量WB结论；该WB约束前交接已说明。
3. 原子：axi_riscv_amos.sv:1020起有AXI/ALU比大于1的word选择，1030使用地址选择64位操作数，1078要求CPU字宽<=AXI宽。128/64=2具备适配路径；需要AMO.W/D及LRSC各半字位置和竞争写验证。
4. Ara：4-lane端口128；axi_dw_converter等宽；invalidation filter由CPU Dline32字节及AW.len/size计算覆盖，不使用LLC行字节数。CPU/Ara共享数据、跨L1行和背压需验收。vstu.sv:425 B响应错误TODO保持开放。
5. LLC：默认8×256×8×16=256KiB，line128B。get_llc_size、地址图、CPU可缓存/可执行范围及LLC_SIZE寄存器消费同一公式；Boot ROM :76读取LLC_SIZE设置栈。SPM范围0x10000000..0x10040000，uncached别名0x14000000..0x14040000，当前映射无因此新增碰撞。BIST/flush/边界/栈仍需动态验收。
6. 软件链接：sw/link/common.ldh仍保守SPM64KiB，不自动使用整个硬件容量，但不能据此认为容量增长功能错误；不可机械扩展而不预留栈/堆。
7. 普通MMIO：cheshire_soc.sv:369使用axi_to_reg_v2(RegDataWidth32)，内部NumBanks=128/32=4，有拆分、返回拼接路径。需验证UART等带读副作用寄存器没有额外访问，及0/4/8/12偏移。
8. FPGA DDR：dram_wrapper_xilinx.sv:99从端口类型得到128输入，转换到既有MIG512；不改DQ/DDR地址拓扑。需128→512的窄访问、尾拍、WSTRB、burst/4KiB、CDC和背压验证。
9. 其他启用模块：默认仿真Dma/SerialLink/Vga/Usb均开；FPGA关闭SerialLink，USB依宏。USB已有32→系统宽度转换(hw/future/spinal_usb_ohci.sv:117)；VGA RGB565要求总线宽度是16倍数，128满足；SerialLink按通道类型位数计算packet宽度，但对端必须匹配，尚未完整协议验证。不能把未接引脚/未运行外设列为通过。

## 建议验收门槛（未执行）

- 隔离128配置与输出，先展开/lint；确认正确向量profile、decoder、所有端口类型、无Debug越界/截断，不能忽略功能性width告警。
- Debug单元：SBA 8/16/32/64访问所有自然对齐偏移，周围保护字不变，正确错误响应；halt/resume、abstract GPR、progbuf和JTAG加载。
- DMA控制：寄存器0/4/8/12偏移、地址高低字、NEXT_ID读副作用；数据：1/3/4/8/15/16/17/31/32等长度及非对齐、guard区和错误/背压。
- SoC：Boot ROM/BIST/SPM首尾、CPU I/D refill、全部窄访问；AMO.W/D和LRSC；Ara跨lane/mask/tail以及共享数据；LLC miss/evict/flush/SPM模式；所有路径精确比对，不以无挂死替代结果正确。
- FPGA：额外MIG模型或板测、时序/CDC、复位；ASIC实现仍需宏/工艺及签核。理想内存仿真不证明真实DDR通过。

## 证据与交接

- 命令：git status --short、git rev-parse HEAD、定向rg/sed读取上述文件；若搜索初始路径不存在，定位后重读，不作为通过证据。
- 官方源：https://raw.githubusercontent.com/pulp-platform/riscv-dbg/master/README.md （明确32/64支持），https://raw.githubusercontent.com/pulp-platform/riscv-dbg/master/src/dm_sba.sv （相同掩码分支）。master仅用于当前官方能力核对，不替代本地版本。
- 本地Debug来源SNAPSHOT.tsv提交358f90110220adf7a083f8b65d157e836d706236；固定提交在线文件请求Cache miss。LLC对应版本官方来源见前交接，已读取。
- 本轮未编译、未展开、未仿真、未板测、未综合，无新动态证据。源码算术示例不是测试通过。
- 本轮仅写独立记录；需要C00合并的事实：用户接受容量增长；DW128新增Debug明确阻塞，iDMA缺口持续。应修正此前DW128为候选时未列出的Debug限制，不覆盖原历史记录。
- 最小下一步：先定Debug64隔离和DMA Reg32桥的详细接口及单元验收，再由用户授权实施隔离128配置；不要先跑整机长仿真绕过这两项问题。
