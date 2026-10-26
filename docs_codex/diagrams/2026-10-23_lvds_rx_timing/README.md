# LVDS RX 像素与帧时序示意

> **历史图稿提示（2026-10-26）：**本目录图稿及以下算例保留 2026-10-23 的 128 数据＋8 时钟、96 批/行输入。当前 RX 已改为 **64 数据＋4 时钟、1C16D**，若保持相邻像素分配则为 192 批/行；500 Mbit/s 时纯像素需 66.060288 ms/帧，不能达到既定 30 FPS。当前值见[资源预算 v1.7](../../engineering/SoC_Resource_and_Packaging_Plan.md#lvds-rx-timing)。本轮只标注 Markdown，图稿源和产物未重绘；下述图内“当前”均指原绘图版本。

2026-10-23。仅说明“图像发送端 → SoC RX”；不含 TX。技术正文见[资源与封装专题](../../engineering/SoC_Resource_and_Packaging_Plan.md)。

| 图 | 编辑源 | 矢量图 | 预览 | 离线编辑与预览 |
| --- | --- | --- | --- | --- |
| 连续串行接收与并行输出流水 | [JSON5](lvds_rx_pixel_timing.json5) | [SVG](lvds_rx_pixel_timing.svg) | [PNG](lvds_rx_pixel_timing.png) | [HTML](lvds_rx_pixel_timing.html) |
| 行与整帧的逻辑组织 | [JSON5](lvds_rx_frame_timing.json5) | [SVG](lvds_rx_frame_timing.svg) | [PNG](lvds_rx_frame_timing.png) | [HTML](lvds_rx_frame_timing.html) |

项目预算输入为 **12288×12288 灰度、14 bit/像素、30 FPS、128 个数据差分对、500 Mbit/s/数据对；合作方确认 RX 至少 8 个时钟差分对，物理分组按 8 组、每组 16 数据对＋1 时钟对计**。像素图采用相对周期，不固定上述线速对应的频率；下方数值预算保留为独立算例，帧图只展示接收后的数据批次与索引。SDR 上升沿采样、LSB→MSB 是用户指定的时序假设，不是传感器官方协议或 IP 时序保证。按该 8 时钟条件计算，RX 数据/时钟共 136 对、272 个信号端；额外控制端未定，不因图中省略而宣称实际无需控制。

像素图不固定时钟频率，以 `T_LVDS` 为位周期，`T_RX＝14×T_LVDS`。完整显示 CLK_LVDS[0] 下的 DATA[0…15]，追加 CLK_LVDS[1]、DATA[16]、DATA[17]，省略 DATA[18…126] 和 CLK_LVDS[2…7] 后显示 DATA[127]；最后一条属于 CLK_LVDS[7]。共显示两个 LVDS 时钟、19 条数据 lane；逻辑字位置一致不代表物理时钟同相。`Pc[b]` 表示第 0 行像素 P[0,c] 的 bit b，每框是一位串行数据；lane j 完整展开的前三次像素为 P[0,j]、P[0,128+j]、P[0,256+j]。不同像素的数值可以相同，P/N 仅以差分逻辑值表达。

CLK_RX 周期为14个 T_LVDS。DATA_RX 表示完成解串及组间对齐后的128×14-bit逻辑聚合，首批收齐前为未定义；本图仅显示在示意 CLK_RX 上升沿后更新的前两组输出：`{P0, P1, P2, ..., P127}`、`{P128, P129, P130, ..., P255}`，分别与第二、第三批串行输入重叠。前三批串行字区间分别在14、28、42个 T_LVDS结束；图到第三批输入结束为止，不保留第四批空间，不展示第三批DATA_RX输出。这只是观察窗口裁剪，不表示接收器丢弃第三批数据或停止时钟。

图上沿后小间隔仅说明先后，不量化实际延迟。CLK_RX相位、解串和组间对齐延迟均待确认，不能据此认为简单分频即可跨组接收；1792-bit聚合不是已实现RTL接口。第14/28/42个输入上升沿采完各lane的bit 13，不表示解串器立即输出；当前用户精简版已移除a/b/c可见标记。SDR、位序和理想采样相位仍为绘图约定，不规定建立/保持时间；DATA_RX初始阴影表示未定义。

帧图只保留`FRAME_CNT`、`ROW_CNT`、`COL_CNT`和`DATA_RX`四条轨迹。每批`DATA_RX`包含128个完整的14-bit像素；计数器是当前批次的索引，均从0开始。`COL_CNT`为起始列，以`0*128、1*128、2*128、…、95*128`显示，批次索引`i=0…95`，共96批；末批完成后列显示`0*128`、行加1。末行12287结束时，列／行同时归0，`FRAME_CNT`从0加到1。它们仅为图稿中的逻辑计数，不定义RTL寄存器、计数器位宽或接口。

帧内采用连续像素编号，每帧12288×12288＝150994944个像素，下一帧重新从P0开始，用`FRAME_CNT`区分：

```text
COL_CNT = i × 128，i=0…95
首像素编号 = ROW_CNT × 12288 + i × 128
DATA_RX = {P首编号, P(首编号+1), P(首编号+2), ..., P(首编号+127)}
```

| FRAME_CNT | ROW_CNT | COL_CNT显示 | DATA_RX像素范围 |
| --- | --- | --- | --- |
| 0 | 0 | 0*128 | P0…P127 |
| 0 | 0 | 1*128 | P128…P255 |
| 0 | 0 | 2*128 | P256…P383 |
| 0 | 0 | 95*128 | P12160…P12287 |
| 0 | 1 | 0*128 | P12288…P12415 |
| 0 | 1 | 2*128 | P12544…P12671 |
| 0 | 12287 | 2*128 | P150982912…P150983039 |
| 0 | 12287 | 95*128 | P150994816…P150994943 |
| 1 | 0 | 0*128 | P0…P127 |

帧图保留行0、行1、末行12287及下一帧首批，各行显示前三批（i=0/1/2）和第96批（i=95）。四条轨迹的断口同步：第三批后省略i=3…94（92批），另省略行2…12286（12285行）。只展示数据批次，未定的行／帧间隔未展示，不表示实际间隔为零；压缩横轴不按时间比例。旧图8条Group/B轨迹已被本图替代，物理8时钟／128数据对分组及下方预算保持。

配色按轨迹类别固定：`FRAME_CNT`蓝色、`ROW_CNT`紫色、`COL_CNT`绿色、`DATA_RX`白色，不再用相同黄／橙色同时表达不同尺度。每批DATA_RX上层的`F/R/i`明确所属帧／行／批，例如`F0/R1/i2`是帧0、行1、索引2（第3批）；下层用`{P首…P末}`表示同一批128个连续编号像素，不是只输出首末两个像素。颜色不代替索引编号。

像素图取第0行，完整展开前三批输入；lane 0…17及127的相邻串行字列号增加128，接收后的前两批与帧图的头两批DATA_RX相同。物理lane编号及正式采样／同步协议仍待确认。

| 纯像素预算 | 结果 |
| --- | --- |
| 每 lane 每行 | 96 像素 × 14 bit ÷ 500 Mbit/s＝2.688 μs |
| 一帧纯像素时间 | 12288 × 2.688 μs＝33.030144 ms |
| 30 FPS 的周期 | 33.333333… ms |
| 一帧全部非像素时间上限 | 303.189333… μs；含实际控制、训练、消隐等，不重复计费，也不强制全部放在帧末 |

图稿以本轮用户输入和上述明确假设绘制，不复制某款传感器的帧协议。WaveJSON 语法使用[官方 WaveDrom 教程](https://wavedrom.com/tutorial.html)和本机 `wavedrom@3.6.2` 引擎，按 [wavedrom-gen skill](/home/zhaowenyao/.agents/skills/wavedrom-gen/SKILL.md) 生成。未安装依赖或注册 MCP。

在仓库根目录重新生成（复用已安装的本地依赖）：

```sh
lvds_skill_dir=/home/zhaowenyao/.agents/skills/wavedrom-gen
lvds_diagram_dir=docs_codex/diagrams/2026-10-23_lvds_rx_timing
for lvds_stem in lvds_rx_pixel_timing lvds_rx_frame_timing; do
  node "$lvds_skill_dir/scripts/validate-wavejson.mjs" \
    --input "$lvds_diagram_dir/$lvds_stem.json5"
  node "$lvds_skill_dir/scripts/render-wavedrom.mjs" \
    --input "$lvds_diagram_dir/$lvds_stem.json5" \
    --svg "$lvds_diagram_dir/$lvds_stem.svg" \
    --png "$lvds_diagram_dir/$lvds_stem.png" \
    --html "$lvds_diagram_dir/$lvds_stem.html"
done
```

初版两源均通过 `--strict`：0 errors、0 warnings（当前人工精简版的校验状态见文末）；SVG/PNG/自包含 HTML 由相同最终源生成。已实际查看最终两张整图，以及像素字边界/最后位、帧末局部；未做器件测试、RTL 仿真、IP/封装时序签核。主 Agent 已用 headless Chrome 在禁用外网解析条件下实测两张 HTML：修改 JSON5 标题后点击 Render，均生成含新标题的 SVG。检查结果保存在 `/tmp/cheshire_lvds_rx_timing_20261023_ddswtjwd/offline_html_validation.json`；未安装浏览器或新增运行框架。

2026-10-23 像素图局部修订：完整展开16条数据lane并采用Pc[b]标注；上述首/末lane旧图已被替代。最终像素源通过严格校验，已查看整图、首末lane和换字位置，并重新实测离线HTML编辑渲染；本轮行／帧图四份产物哈希保持。检查与修改前副本见 `/tmp/lvds_pixel_16lane_jrf6e_7y/`。

2026-10-23 后续修订：像素图改用相对周期，增加分组省略与CLK_RX/DATA_RX；上段16-lane版本记录保留为历史。当前19条数据lane、532个位标签及两组聚合数据已核对，严格校验、最终预览和离线HTML编辑重渲染通过；帧图四份产物未改。修改前副本及检查结果见 `/tmp/lvds_rx_output_myop4vee/`。

2026-10-23 流水示例修订（历史，已由下段裁剪替代）：当时完整展开前三批输入并显示三批DATA_RX输出；下一批输入合并位标签、保持连续接收，替代上段两批示例。严格校验、最终整图/第三批边界预览及离线HTML重渲染通过；帧图未修改。修改前副本及检查结果见 `/tmp/lvds_rx_pipeline_zolq4jyc/`。

2026-10-23 按用户要求裁剪：当前像素图只保留三批完整串行输入与前两批DATA_RX输出，删除第四批空间；图末为观察窗口结束。三批期间时钟持续运行，第三批输出仅不展示。最终源严格校验、整图及末端检查、离线HTML重渲染通过；帧图未改。副本及检查结果：`/tmp/lvds_rx_three_groups_oam8sa5x/`。

2026-10-23 用户人工精简版：按所提供附件逐字节保存像素JSON5，并重新生成同名SVG、PNG与离线HTML。保留原文中的3条指向已移除a/b/c标记的edge，官方引擎成功渲染，校验0 errors、3 warnings，因此本版不使用`--strict`；这些箭头不显示。已查看最终整图、换字边界和CLK_RX/DATA_RX区域，离线HTML编辑标题后重渲染正常（状态为`Rendered with warnings`）。帧图四份文件哈希保持；修改前副本与检查记录：`/tmp/lvds_pixel_user_simplified_nl4ztjsq`。

2026-10-23 信号分组：按用户要求将像素图`signal`组织为`LVDS`与`RX`两个WaveDrom分组，前者包含接收输入及并行传输区间，后者包含`CLK_RX`和`DATA_RX`。波形、数据、相位和周期逐项保持，重生成SVG/PNG/HTML并查看最终整图与分组局部；原3条缺失节点警告保持，帧图产物哈希不变。修改前副本：`/tmp/lvds_signal_groups_rt9h7_jq`。

2026-10-23 帧图改为RX批次与计数：按已批准计划移除旧Group/B轨迹及G0/G1/Gf区段，保留四轨并同步标记省略。帧内连续像素编号、每行96批、列／行／帧切换已核对；WaveDrom严格校验0 errors/0 warnings，最终整图、长编号、行与帧边界及图注均已查看，离线HTML编辑重渲染通过。像素图四份文件及资源预算专题哈希保持。修改前六份文件、输入哈希及检查结果位于`/tmp/lvds_frame_rx_counters_0qj9g5y1`。

2026-10-23 帧图前三批与尺度配色修订：每行展开前三批再接第96批（中间92批省略），共显示13批；COL_CNT改为i*128表达式。固定帧蓝／行紫／列绿／数据白，并在DATA_RX标明F/R/i。严格校验零错误零警告，逐项核对编号/边界/配色并查看最终图片；HTML离线编辑重渲染通过，13个标签最大宽491.52、单批框宽520，长标签不重叠。像素图及预算专题哈希保持。修改前副本与结果：`/tmp/lvds_frame_batch_colors_sjc4pwg6`。

2026-10-23 帧图紧凑排版：批次标签改为两层，上层F/R/i、下层{P首…P末}，保留全部13批范围、计数关系、配色和省略；仅在COL与DATA之间增加无名留白容纳上层标签，仍为4条命名轨迹。hscale从13减为5，SVG宽度8980→3540（约缩短61%），PNG宽17960→7080，默认字号保持。最终整图及首／末行、两种切换边界已查看；严格校验零错误／零警告，HTML离线编辑重渲染及上下标签居中/间距检查通过，范围文字最大宽190.82、单批宽200。像素图及预算专题哈希保持；副本及结果：`/tmp/lvds_frame_compact_vm9426um`。
