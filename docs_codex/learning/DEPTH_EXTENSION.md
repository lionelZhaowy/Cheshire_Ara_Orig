# L01 深度扩充：章节职责与验收

2026-09-29，沿用 16 章、6 项实验和 2 页参考。前一轮旧站 728 文件备份保留；本轮不另建并行教材主线。修改入口是 `content/*.html`，运行 `scripts/build_site.py` 更新发布 HTML。

| 阅读问题 | 正文章节 | 深度与独立交付 |
| --- | --- | --- |
| 系统里有哪些请求者、存储和平台边界？ | 01、03 | 完整 SoC/AXI/Reg 图、默认地址范围/实际容量/CPU 属性；本地代码与官方预留图差异 |
| 哪些参数互相约束？ | 02、05 | SoC / CVA6 / 软件组合表；本地 GCC 宏、三个向量入口及对象能力边界 |
| 时钟、复位、电源如何落实到 ASIC？ | 01、16 | 当前域表与未来分域分图；PLL/DDR 放行 WaveDrom；UPF/库/DFT 等待条件 |
| 程序如何从文件变成运行状态？ | 04～07 | 存储生命周期、JTAG 事件波形、逐介质启动对照、真实向量取证点 |
| 设备怎样由寄存器走到动作和完成？ | 08～12、14 | UART/GPIO/CLINT/PLIC/I2C/SPI/SD/Link/VGA/USB 的访问、复位、步骤、结果和错误边界；DDR/Debug/iDMA 深化 |
| CVA6 与 Ara 的接受、应答、提交和完成有何区别？ | 13 | 专用接口、scoreboard/pending、MMU、VRF/VLSU；算术/load 两张 WaveDrom；AXI 错误缺口 |
| CPU/Ara/NPU 如何交接数据？ | 12 | 当前 WT/pending/invalidation、候选路径、所有权状态与交接 WaveDrom；旁路副本/原子问题 |
| 怎样编写和验证 RVV？ | 13、实验 E | 同一数组，汇编/intrinsics/自动向量化，6 种长度、环绕输入、归约、独立参考和守卫；FP32 编译探针 |
| Ara 与未来 NPU 如何协作模型片段？ | 13、15 | 137×64 int8 全连接候选案例、int32 输出、布局/流量/精度/调度成本；未来 API 伪代码 |
| NPU/ISP/LVDS/DDR 怎么接？ | 15、16 | 旁路拓扑、接口资料、带宽与 FIFO 算例、阶段验收，未修改生产设计 |

图形约定：13 张新结构/状态 SVG 由 `build_depth_diagrams.py` 生成；6 张时序 SVG 由 `build_waves.py` 使用本地 WaveDrom 3.5.0 生成，JSON 在 `assets/waves/`。旧通道流程图已改正“时序图”的误称。浏览器只读取 SVG，断网和禁用 JS 仍能看波形。生成器使用本机 Chrome，不需要 npm/Node 或在线 CDN。

轻量验证分层记录：

- 主机构建：标量、RVV 汇编、intrinsics、自动向量化及汇编注错版本；FP32 仅对象编译。
- 静态指令：向量 load/add/store/reduction 实际出现在 ELF，主程序参考对象没有 V。
- 日志工具：人工构造正反日志仅测试检查器，不产生目标执行证据。
- 网站：本地链接/锚点、图 XML、可重建性、历史证据/备份保护、桌面/手机及禁用 JS 预览。
- 待验证：生产 RTL 编译展开、全部目标数值/故障/性能、真实波形、板测、NPU 接入与 ASIC 实现。

资料版本和取得失败项见 [官方资料表](OFFICIAL_SOURCES.md)，执行结果以 [证据页](evidence.html#depth) 和独立交接为准。
