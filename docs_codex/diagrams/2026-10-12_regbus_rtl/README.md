# Regbus RTL 逻辑实现图

2026-10-12；L01；输入 HEAD `c4162204cfee0c48b81158b4296860a678d92bec`。用户要求先交付本轮 RTL 分析图片，再决定是否封装 skill。本轮使用现有 industrial-svg-pptx 和 svg-pptx-diagrams-native；未创建或修改 skill。

| 图 | PNG | SVG | 原生 PPTX |
| --- | --- | --- | --- |
| AXI→Regbus 桥内部 | [预览](regbus_bridge_rtl.png) | [母版](regbus_bridge_rtl.svg) | [单页](regbus_bridge_rtl.pptx) |
| 地址解码、请求分发、响应选择 | [预览](regbus_decode_rtl.png) | [母版](regbus_decode_rtl.svg) | [单页](regbus_decode_rtl.pptx) |

[两页 PPTX 合辑](regbus_rtl_analysis.pptx) · [检查报告](validation.json) · [输入源码哈希](source_hashes.json)

## 图稿层次与参数

这是 RTL 推导的逻辑实现示意，不是综合后的门级网表。第一图保留模块/功能边界，展开宽度拆分、请求缓冲、握手选择、过滤和响应寄存器；第二图进一步画出范围比较、选择、门控和 MUX 的组合等价关系。没有重新列一遍 SoC 外设清单。

以 `DefaultCfg` 的 AXI 数据 64 bit、地址 48 bit、`RegAdaptMemCut=1` 作静态参数代入；公共 Reg 数据为 32 bit，因此 `NumBanks=2`。这是阅读基准，不是某个目标平台 elaboration 通过报告。AXI ID 宽度仍由具体主设备数量派生，没有写死。`CutMemRsps` 在当前 SoC 实例未覆盖，使用桥默认值 0；`CutMemReqs` 由 `Cfg.RegAdaptMemCut` 传入。

两个子通路是宽度拆分，不是两块 SRAM，也不是两个独立外部 Regbus 端口。图中地址为 `align8(addr)+4*i`，字段和握手沿本地实现追踪，不据名称假设只访问 AXI size 对应的单一路径。

## 第一图的连接与源码对应

| 图中对象 | RTL 依据 |
| --- | --- |
| SoC 接入与参数 | [cheshire_soc.sv](../../../hw/cheshire_soc.sv) 的 `i_axi_to_reg_v2`；[cheshire_pkg.sv](../../../hw/cheshire_pkg.sv) 的 `DefaultCfg` |
| 桥 A/B 层级、子通路、过滤、汇合 | [axi_to_reg_v2.sv](../../../.bender/git/checkouts/register_interface-902ad5bfde7bb98c/src/axi_to_reg_v2.sv)，`NumBanks`、`gen_tcdm_to_reg`、`i_mem_req_spill`、`i_mem_rsp_spill`、`i_reg_mux` |
| 读写地址/计数、选择锁定、元数据与 R/B 返回 | [axi_to_detailed_mem.sv](../../../.bender/git/checkouts/axi-ecdc900686449c15/src/axi_to_detailed_mem.sv)，`rd_meta_q/r_cnt_q`、`wr_meta_q/w_cnt_q`、`meta_sel_q/sel_lock_q`、`i_fork`、`i_meta_buf`、`i_sel_buf`、`i_join`、`i_fork_dynamic` |
| 两路数据切片、地址、请求/响应缓冲 | [mem_to_banks_detailed.sv](../../../.bender/git/checkouts/common_cells-7f7ae0f5e6bf7fb5/src/mem_to_banks_detailed.sv)，`gen_reqs`、`gen_resp_regs`；桥使用 `HideStrb=0`、`MaxTrans=1`、`FifoDepth=1` |
| 在途限制与响应缓冲 | [stream_to_mem.sv](../../../.bender/git/checkouts/common_cells-7f7ae0f5e6bf7fb5/src/stream_to_mem.sv)，`BufDepth=1` |
| Reg 子通路轮询仲裁、响应回送 | [reg_mux.sv](../../../.bender/git/checkouts/register_interface-902ad5bfde7bb98c/src/reg_mux.sv) 及 [stream_arbiter.sv](../../../.bender/git/checkouts/common_cells-7f7ae0f5e6bf7fb5/src/stream_arbiter.sv) |
| 响应寄存器、请求直通 | [periph_to_reg.sv](../../../.bender/git/checkouts/register_interface-902ad5bfde7bb98c/src/periph_to_reg.sv)，`gnt_o`、`r_valid_q`、`r_rdata_q`、`r_opc_q` |

连接点解释：

- `P0/1` 对应两路 `mem_qvalid/qready/addr/wdata/strb/we/id`，B 区以 P0、P1 分别展开。
- `T0/1` 对应两路 `mem_pvalid/rdata/err`；A 中的 T 入口与 D 中的 T 输入是同一返回路径的层次展开，不是重复执行两次收集。
- `R0/1` 对应 `reg_mux` 给过滤器正常分支的 `valid_rsp[0/1]`；`rdata/error` 广播，`ready` 只回到获选路。该行为由 reg_mux/stream_arbiter 完成，图中以 R 标签连接，不是绕过仲裁直接广播 ready。
- `META` 为元数据 FIFO 输出；`RB` 为响应类型 FIFO 输出。后者存储 `{sel_b,sel_r}`，不是 Reg 响应数组。
- `F0/F1` 仅表示 `i_fork` 到两个 FIFO 的握手关系。`stream_fork` 不搬运 payload；FIFO 数据来自 `meta` 或由它组合生成的选择位。主数据线的 `meta + W.data/W.strb` 表示 `m2s_req` 的组合装配，W 数据来自 AXI W 通道，不经过元数据选择器存储。
- 正向请求箭头合并 payload/valid；多数反压线未逐根展开，关键的 `reg_rsp.ready → gnt_o → r_valid_q` 在 C 区明确表达。该图不是逐端口完整接线图。

前端读写选择不是单纯轮询：双方有效时先比较 QoS，同 QoS 再结合单次写、正在进行的 burst 等条件，最后轮询；被背压时保持选择。B 区 `reg_mux` 的两路仲裁是另一个仲裁层次，不能将两者混为一个模块。

`spill_register` 是具有握手的弹性缓冲，不等价于单个 DFF；图中双竖线表示缓冲对象，不规定它内部只含一个寄存器。C 区才明确画出 `periph_to_reg` 的响应 DFF。该模块每拍采样数据/错误；`r_valid_q` 表示有效性，没有凭空加入 gnt 数据使能。实际 RTL 另有 ID 返回寄存器，但此桥将该适配器的 `id_i` 接零、`r_id_o` 不使用；AXI ID 通过元数据路径保留，图 C 因而未画未使用 ID 支路。

图 D 是图 A 内部响应逻辑的放大说明。`i_join` 配对内存响应与元数据，`i_fork_dynamic` 控制 R/B 的 valid/ready 分发；R/B payload 由旁侧组合逻辑产生，不把握手模块说成数据存储器。写错误有跨拍累积状态。

## 第二图的组合等价关系

依据 [addr_decode_dync.sv](../../../.bender/git/checkouts/common_cells-7f7ae0f5e6bf7fb5/src/addr_decode_dync.sv)、[reg_demux.sv](../../../.bender/git/checkouts/register_interface-902ad5bfde7bb98c/src/reg_demux.sv)、[reg_err_slv.sv](../../../.bender/git/checkouts/register_interface-902ad5bfde7bb98c/src/reg_err_slv.sv)。

当前实例 `Napot=0`、`config_ongoing_i=0`、`en_default_idx_i=1`，规则命中为：

```text
match[j] = (addr >= start[j]) && ((addr < end[j]) || end[j] == 0)
select   = 最高命中规则的 idx；无命中则 RegOut.err
sel_p    = (select == p)
out_req[p].valid   = sel_p && in_req.valid
out_req[p].payload = sel_p ? in_req.payload : 0
in_rsp             = out_rsp[select]
```

请求门控图是正常有效索引下的 RTL 组合等价表达，不声称综合工具必然保留逐端口比较器和相同门数。`payload` 是图中对 addr/write/wdata/wstrb 的组合简称，不是源码中另建的字段。响应字段合计 34 bit（32-bit rdata + error + ready）。图 C 的其他目标表示除代表端口 p 与 error 外的其余输入，不新增端口或错误模块。

`RegMap` 是参数展开生成的常量，不是软件可写寄存器。解码器与 demux 内无状态存储；后者虽然声明 clk_i/rst_ni，当前内部逻辑不使用。错误从设备没有时钟端口，常量输出 ready=1/error=1/rdata=BADCAB1E。

## 静态事务追踪

以下只核对源码关系，没有新增仿真或逐周期波形证据。

1. **合法、对齐的 64-bit 读**：假设所涉及的两个 32-bit 寄存器都可安全读取。AR 形成元数据和内存请求；拆成地址 A 与 A+4 的两路；各自经过请求缓冲和 periph_to_reg。读不命中零写过滤，两路由 reg_mux 逐次访问公共 Regbus；两路返回经响应寄存器和收集逻辑重组为 R 数据，ID/LAST 取自配对元数据。不能据此推广为所有窄读/MMIO 副作用均安全。
2. **仅低四字节有效的写**：在对齐 64-bit 数据拍中假设 WSTRB=0x0f。低路 WSTRB=0xf 访问目标；高路 WSTRB=0 命中零写过滤，在本地成功应答，不访问高路对应寄存器。零写响应和正常响应都经 periph_to_reg 返回。全部写拍处理后构造 B；发生有效字节对应错误时进入写错误累积路径。
3. **Regbus 二级空洞**：地址规则无命中，默认选 error 端口；选中的 ready/error/rdata 返回桥。该路径不是一级 AXI 无映射时的 DECERR 处理路径。

## 生成、检查与边界

从仓库根目录执行。生成器与导出后端均要求新输出；不覆盖旧图。

```sh
python3 docs_codex/diagrams/2026-10-12_regbus_rtl/build_figures.py --out-dir /tmp/regbus-rtl-rebuild
native_skill_root="$HOME/.codex/skills/svg-pptx-diagrams-native"
python3 "$native_skill_root/scripts/run.py" --input /tmp/regbus-rtl-rebuild/regbus_bridge_rtl.svg /tmp/regbus-rtl-rebuild/regbus_decode_rtl.svg --out-dir /tmp/regbus-rtl-rebuild-export --aspect source --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc
"$native_skill_root/.venv/bin/python" docs_codex/diagrams/2026-10-12_regbus_rtl/verify_figures.py
```

单图分别以相同命令、单个 `--input` 导出。PNG 使用 CairoSVG 2.9.1 渲染。第一图为 2400×1860，第二图为 2400×1570；合辑统一第一图画布，第二图等比例居中。

最终两图已实际查看。保存重读检查：第一图 212 个原生对象、105 个文本、48 个原生箭头；第二图 101 个原生对象、53 个文本、21 个原生箭头；文本与 SVG 一致、无栅格媒体，文泉驿字体度量无文本互相重叠及画布越界。检查不构成逻辑等价形式证明。

Office 显示/编辑未实测；字体未嵌入、连线未绑定模块端口。保留旧 Regbus 图与 SoC 全景图，供用户比较层次与表达；未修改 RTL、配置、地址、软件或 skill，未运行生产编译/仿真/板测。下一步根据用户对本轮图片的反馈确定展开深度和是否封装 skill。
