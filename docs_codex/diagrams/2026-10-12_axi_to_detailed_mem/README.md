# i_axi_to_detailed_mem：按信号拆解的教学图

2026-10-12，L01；输入 HEAD `c4162204cfee0c48b81158b4296860a678d92bec`。

用户指出上一版 A 区混合数据流、握手与放大视图，不能帮助理解电路。本版只重绘这一主题，改用 publication-figures 的结构化 SVG / 原生对象导出。旧图保留，不改 RTL 或 skill。

## 图稿

| 图 | 要回答的问题 | 预览 | 可编辑源 | 矢量 PDF |
| --- | --- | --- | --- | --- |
| ① 请求内容 | 为什么 AR 和 AW/W 要二选一？W 数据从哪里走？ | [PNG](export/01_request_payload.png) | [SVG](01_request_payload.svg) | [PDF](export/01_request_payload.pdf) |
| ② 三路握手 | fork 到底分发什么？两个 FIFO 存什么？ | [PNG](export/02_fork_and_metadata.png) | [SVG](02_fork_and_metadata.svg) | [PDF](export/02_fork_and_metadata.pdf) |
| ③ 接口适配 | stream_to_mem 怎样转换握手？ | [PNG](export/03_stream_to_mem.png) | [SVG](03_stream_to_mem.svg) | [PDF](export/03_stream_to_mem.pdf) |
| ④ 宽度与端口 | 两路 32-bit 请求及返回究竟是什么？ | [PNG](export/04_banks_and_ports.png) | [SVG](04_banks_and_ports.svg) | [PDF](export/04_banks_and_ports.pdf) |

[四页可编辑 PPTX](export/diagrams.pptx)。实线表示字段连线；虚线表示 valid/ready 或选择控制。FIFO 内小格表示存储容量，不表示固定延迟。图采用屏幕教学宽度 260 mm，最小字号约 10.1 pt，不声称符合某投稿模板。

这些图各自是同一模块的一个信号视图，不能把跨图重复出现的实例当成新增硬件。图①只画请求字段；图②只展开 fork 三路握手和两个 FIFO 的输入侧，FIFO 的读出握手在正文解释；图③展开 stream_to_mem 的门控、状态与响应缓冲；图④展开切片/拼接及逐路 FIFO，集中用公式表达收齐条件。它们不是完整端口网表或综合门级网表。

默认参数：AXI 数据 64 bit、Reg 数据 32 bit、地址 48 bit；`NumBanks=2`。`axi_to_reg_v2` 实例明确设置 `BufDepth=1`、`HideStrb=0`、`OutFifoDepth=1`，故元数据 FIFO 和选择 FIFO 均深度 2，其余图中相关 FIFO 深度 1。

## 1. 读写二选一的原因

“一个事务是读或写”不等于“同一接口任意时刻只存在读或写之一”。AR 与 AW/W 是独立通道，可以同时有效，也可以在一笔读尚未返回时出现写请求。这里的内部执行入口只有一组 `m2s_req/m2s_req_valid/m2s_req_ready`，所以必须将两个来源串行调度。

`i_ax_mux` 选择的是 `rd_meta` 与 `wr_meta`，产生 `meta`。它不是在 AR、AW、W 三个通道中挑一个。写前端先处理 AW 与 W 的关联，再形成写候选。新写需要 `aw_valid && w_valid`；已开始的 burst 使用保存的 AW 信息，逐拍等待 W。

例如 AW 先到、W 晚到：该模块不会提前完成这笔新 AW 的握手，上游保持 AW；等 W 到达且内部获准推进后才完成握手。这个等待发生在写前端和握手保持机制，不靠 i_meta_buf 存写数据。W.data 由当前 W 通道直接进入请求结构体。

当前仲裁优先考虑 QoS，再考虑 burst 属性，最后轮换；请求未完成输入握手时保持选择。这是当前实现策略，不是 AXI 协议规定读写一定以这种优先级执行。

源码：[读前端](../../../.bender/git/checkouts/axi-ecdc900686449c15/src/axi_to_detailed_mem.sv) 175–217 行，写前端 220–268 行，选择器与仲裁 270–325 行，请求组装 378–392 行。

## 2. 旧黑线与 fork 的区别

旧图直达 i_stream_to_mem 的黑色主线没有明确标明字段/握手，这正是歧义来源。它代表组装后的 `m2s_req`，主要字段是：

```systemverilog
addr  = meta.addr;
we    = meta.write;
id    = meta.id;
wdata = axi_req_i.w.data;
strb  = axi_req_i.w.strb;
```

该数据不经过 fork。fork 只有 valid/ready 及内部状态，不含 payload 端口，也不是两个 FIFO 的容器。

实际连接是：

```systemverilog
.valid_i (arb_valid),
.ready_o (arb_ready),
.valid_o ({sel_valid, meta_valid, m2s_req_valid}),
.ready_i ({sel_ready, meta_ready, m2s_req_ready})
```

同一项访问必须完成三件事：执行支路接收请求、meta FIFO 接收描述信息、sel FIFO 接收返回选择位。fork 允许三个接收事件分不同周期发生，但每路必须恰好一次，全部完成后才允许上游换成下一项。

以下是源码可推导的教学例子，不是仿真波形；假设初始没有未完成的 fork 项，arb_valid 持续有效：

| 时钟沿 | meta 支路 | sel 支路 | 执行支路 | 上游 |
| --- | --- | --- | --- | --- |
| E0 | ready=1，接收一次 | ready=1，接收一次 | ready=0，未接收 | arb_ready=0，保持当前项 |
| E1 | fork 将其 valid 压低，不再入队 | fork 将其 valid 压低，不再入队 | 仍 ready=0 | 继续保持 |
| E2 | 不重复接收 | 不重复接收 | ready=1，接收一次 | arb_ready=1，整项完成 |

因此这里只要求“同一访问的三个分支一一对应”，不要求同一拍入队。此前如果把它说成必须同周期同步，应以本次说明为准。

源码：[stream_fork.sv](../../../.bender/git/checkouts/common_cells-7f7ae0f5e6bf7fb5/src/stream_fork.sv) 的头部契约、输入 READY/WAIT 状态机及 `gen_oup_state`；顶层接线见 axi_to_detailed_mem 327–337 行。

## 3. 两个旁路 FIFO 的必要性

### i_meta_buf

它存完整 `meta_t`：addr、atop、lock、strb、id、last、qos、size、write、user、cache、prot、region；没有 wdata。

访问下游要花时间，而当前 AXI 输入以后会变成下一项。返回时仍需要原始 ID、LAST，以及错误处理所需的读写/地址/size/strb 等信息，所以要按顺序保存。输出的真实名字是 `meta_buf`；旧图 META 是绘图连接标签。

### i_sel_buf

它每项只存 2 bit：

```systemverilog
sel_b = meta.write & meta.last;
sel_r = ~meta.write | meta.atop[5];
```

普通读保存 `(B,R)=(0,1)`；普通写中间拍保存 `(0,0)`；普通写最后一拍保存 `(1,0)`。普通写每个内部拍仍有完成响应，但只有最后一拍产生 AXI B，中间拍的完成被内部消费并累积错误。ATOP 项是通用模块的额外条件，此处不展开，不据此宣称 Regbus 支持原子寄存器访问。

输出真实名字是 `sel_buf_b/sel_buf_r`；旧图 RB 是两位选择信号的绘图标签，不是读写数据总线。

### 返回时如何配对

```text
m2s_resp.data  ─────────────────────────→ AXI R.data
meta_buf.id / last ─────────────────────→ AXI R.id / R.last、B.id
m2s_resp.err + meta_buf 属性 ─────────────→ 错误筛选 / 写错误累积 / RRESP、BRESP

m2s_resp_valid ─┐
               ├─ i_join ─ mem_join_valid ─ i_fork_dynamic ─ RVALID / BVALID
meta_buf_valid ┘                              ↑
                                    sel_buf_b / sel_buf_r
```

`i_join` 只同步响应与元数据的握手；数据在其旁边直接连到响应构造逻辑。`i_fork_dynamic` 再结合选择 FIFO 和 RREADY/BREADY 控制何时消费。三个 FIFO/响应序列按顺序推进，不靠搜索 ID 在队列中随机匹配。

之所以是两个独立 FIFO，是当前 RTL 把“响应字段”与“响应通道控制”做成两个独立 stream，分别交给 join 和 dynamic fork。逻辑上可以设计成另一种合并队列，但那会是另一套 RTL；这里没有提出修改。

两个 FIFO 都是 `FALL_THROUGH=1`、`DEPTH=1+BufDepth=2`。深度表示可容纳两项，不表示数据必须延迟两个周期。

源码：axi_to_detailed_mem 的 `meta_t` 定义 121–135 行、选择位/FIFO 339–376 行、join/dynamic fork 495–519 行、错误与 AXI 字段构造 523–579 行。

## 4. stream_to_mem 的转换机制

这里的 stream 是通用 valid/ready 接口，不是 AXI-Stream 协议。转换前已经不是 AXI 五通道；AXI 请求已由前端整理成结构体。

| 方向 | 上游 stream 侧 | 下游 memory 侧 |
| --- | --- | --- |
| 请求字段 | req_i | mem_req_o，直接透传 |
| 请求握手 | req_valid_i / req_ready_o | mem_req_valid_o / mem_req_ready_i，受容量门控 |
| 响应字段 | resp_o | mem_resp_i |
| 响应握手 | resp_valid_o / resp_ready_i | 只有 mem_resp_valid_i，没有响应 ready |

下游不能被响应 ready 暂停。它一旦返回，上游必须有地方接。因此模块用计数器限制请求发出，用 FIFO 保留返回结果。

```systemverilog
assign mem_req_o = req_i;
assign req_ready = (cnt_q < BufDepth) | (resp_valid_o & resp_ready_i);
assign req_ready_o = mem_req_ready_i & req_ready;
assign mem_req_valid_o = req_valid_i & req_ready;
```

`req_ready` 是模块内部的容量允许信号，区别于输出端口 `req_ready_o`。`cnt_q` 统计已接收请求但尚未向上游交付响应的数量；下游响应到达 FIFO 时不减计数，响应被上游接收才减计数。

在 BufDepth=1 下：

1. cnt=0，可以在下游请求 ready 时发出一项。
2. 请求握手后 cnt=1，停止发新项。
3. 下游返回，但上游 resp_ready=0，响应保存在 FIFO，cnt 仍为 1。
4. 上游消费响应，cnt 减一；源码也允许同周期发出下一项，此时加减抵消。

源码：[stream_to_mem.sv](../../../.bender/git/checkouts/common_cells-7f7ae0f5e6bf7fb5/src/stream_to_mem.sv) 63–103 行及 115–116 行。时序举例假设每个已接收请求返回一次响应，符合该接口契约。

## 5. 两路 32-bit 端口与返回

`mem_to_banks_detailed` 不仅切开数据，还为两路分别保存请求和响应。

```text
A = align8(mem_req.addr)

lane 0: addr=A,   wdata=原[31:0],  strb=原[3:0]
lane 1: addr=A+4, wdata=原[63:32], strb=原[7:4]
```

两路都是 48-bit 地址、32-bit 数据、4-bit 字节使能。每路 req/gnt 独立，因而可以在不同周期被外层适配器接收。下游仍会由外层 reg_mux 汇到一个公共 Regbus；本模块不代表两个独立外设总线，也不是把 AXI 地址截成 32 bit。

旧图 P0/1 与 T0/1 均为人工标签，现按实际端口解释：

| 旧标签 | i_axi_to_detailed_mem 端口 | 外层 axi_to_reg_v2 信号 | 意义 |
| --- | --- | --- | --- |
| P[i] 正向请求 | mem_req_o[i] | mem_qvalid[i] | 请求有效 |
| P[i] 反向握手 | mem_gnt_i[i] | mem_qready[i] | 下游可以接收请求 |
| P[i] 请求内容 | mem_addr_o、mem_wdata_o、mem_strb_o、mem_we_o、mem_id_o | mem_addr、mem_wdata、mem_strb、mem_we、mem_id | 地址、数据、使能和属性 |
| T[i] 返回有效 | mem_rvalid_i[i] | mem_pvalid[i] | 这一子请求完成，读写都需要 |
| T[i] 返回内容 | mem_rdata_i[i]、mem_err_i[i] | mem_rdata[i]、mem_err[i] | 读数据和完成状态 |

`mem_exokay_i` 在这个桥实例中接零；通用模块还具有其他属性端口，其中部分在外层未连接。

由于 HideStrb=0，本模块不会过滤零 strobe 写；过滤发生在外层后续 `reg_demux`。不能根据这张图推断窄读只访问一个 lane。

两路响应分别进入各自 FIFO。当前参数下：

```text
mem_rvalid = resp_valid[0] & resp_valid[1]
返回 64-bit 数据 = {lane1_data, lane0_data}
```

先返回的一路在自己的 FIFO 中等待，直到另一条也有效；整拍交付时一起弹出。错误位和 exclusive 状态先逐路保留，后续 AXI 响应构造再处理。

输入请求的总 gnt 还受两路请求 FIFO 和响应 FIFO 可用空间共同限制：`gnt_o = (&req_ready) & (&resp_ready) & !dead_write_fifo_full`。这里 HideStrb=0，因此 dead_write_fifo_full 恒为 0。图④没有把每根 FIFO 空间反馈线展开，以上公式给出当前接收条件。

源码：[mem_to_banks_detailed.sv](../../../.bender/git/checkouts/common_cells-7f7ae0f5e6bf7fb5/src/mem_to_banks_detailed.sv) 115–163 行、188–208 行；端口映射见 [axi_to_detailed_mem.sv](../../../.bender/git/checkouts/axi-ecdc900686449c15/src/axi_to_detailed_mem.sv) 460–493 行和 [axi_to_reg_v2.sv](../../../.bender/git/checkouts/register_interface-902ad5bfde7bb98c/src/axi_to_reg_v2.sv) 72–107 行。

## 旧图内容去向与验证

| 旧图元素 | 本次去向 |
| --- | --- |
| AR / AW+W 与 i_ax_mux | 图①；正文第 1 节解释独立通道与共享资源 |
| 黑色 meta+W 主线 | 图①显式 m2s_req 组装；正文第 2 节 |
| i_fork / F0 / F1 | 图②使用三组真实 valid/ready，不保留自定义 F 标签 |
| 下方 i_meta_buf / i_sel_buf、META / RB | 图②输入字段、容量与真实输出名；正文第 3 节返回配对 |
| i_stream_to_mem | 图③内部逻辑和公式；正文第 4 节 |
| i_mem_to_banks / P0/1 / T0/1 | 图④；正文第 5 节逐端口映射 |
| 原图 A 外部的 Regbus 适配和外设解码 | 不属本次展开范围，旧图保留 |

生成入口为 `build_figures.py`，原生导出使用 publication-figures `scripts/run.py`：

```sh
python3 docs_codex/diagrams/2026-10-12_axi_to_detailed_mem/build_figures.py
```

导出参数：四张 SVG、`--width-mm 260 --min-font-pt 9 --render --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`，输出到新的空目录。当前导出结果位于 export；重新导出需另选空目录。

实际检查见 [export_report.json](export/export_report.json) 与 [validation.json](validation.json)，包含原生对象/文字保留、字体与矢量 PDF 检查、输入源码哈希。预览已逐张检查。Office 未实测；PPTX 字体未嵌入、连线未绑定对象端口。没有运行 RTL 仿真、综合、板测，教学时序表不是动态验证结果。
