# L01 / 深度扩充后的篇章结构修订

## 基本信息

- 日期：2026-09-29；任务 L01。
- 授权：根据另一评审 Agent 的结构审查实际修改教材；保留已有内容、证据及 WaveDrom，不再次建立多套并列主线。
- 状态：教材结构修订完成；目标 SoC 执行仍未验证。
- 输入分支 `mp/ara-pulp-v2`，HEAD `69fabdd227e225bf9f5f0b9ec5fe9d056999fea6`。
- 开始时已有 `handoffs/README.md` 修改及未跟踪的 `2026-09-29_L01_structure_review.md`，属于审查结果；原文保留，仅追加本次索引。
- 范围：`learning/` 正文/网站/生成及验证脚本/新证据、外层入口和共享状态、独立交接。无生产接口、缓存机制、NPU 或 FPGA 修改；未提交 git。

## 反思与落实

上一轮扩充以知识点覆盖为主，没有同步调整章节职责、前置关系和导航。H2-only 目录让新内容继续堆在长页面末尾，链接存在性检查也不能发现语义错位。此次把内容归属、章节层次、导航生成及证据范围一起调整，具体逐项回应见[修订说明](../learning/STRUCTURE_REVISION.md)。

- 七篇、30 个正文章，另有首页/实验合册/寄存器/证据，共 34 主页面；20 个更早的兼容页保留。
- 正文共 112 个 H2、129 个 H3。侧栏仅展开当前篇，当前章显示节；页内目录含节/小节，原生可折叠；面包屑、编号、上下章同源。首页先提供 C 程序短路线。
- LLC/SPM、DDR、DMA/流量管理、共享数据分别为 11/12/22/26；Ara 硬件、RVV、模型案例为 24/25/29。CVA6、时钟、复位、电源独立为 02/04/05/06。
- 地址与协议先于 Crossbar；UART/GPIO、CLINT、I2C、SPI 的复位/字段在操作之前；实验 E 扩充归入 H3。12 组/429 项寄存器不改数据，回链直达设备字段/初始化。
- 373 条旧 URL 映射指向真实新节；脚本关闭时有静态迁移说明。原 148 个 H2 逐项记录归属；示例、来源、原图继续可达。原架构中的时钟/复位/电源混合节拆入 04/05/06，其旧组合锚点落到 06。

## 定向技术核对

1. 配置真实字段为 `Cfg.Ara`、`Cfg.AraNrLanes`、`Cfg.AraVLEN`，修正未说明的 `EnAra`。`Cfg.NumCores` 派生 `NumIntHarts`；Ara 单核约束在 SoC 消费者处核对。资源原值与平台覆盖分列。
2. `target/sim/src/vip_cheshire_soc.sv` 的 `jtag_elf_halt_load` 在 `DutCfg.LlcNotBypass` 条件下只轮询 `CFG_SPM_LOW.bit0`，然后 halt 并等待 `DMSTATUS.allhalted`；没有等待 ROM C 测频。`hw/bootrom/cheshire_bootrom.S` 在写配置/COMMIT 后继续扩展 sp，故不能从该位推断栈与全部初始化完成。
3. 启动流程图及 WaveDrom `boot-phases.json` 同步修订，不再把 BIST/SPM/stack 合成一项完成状态；时序明确为教学事件，非真实仿真采样。
4. `sw/lib/dif/uart.c::uart_init` 等使用 `reg8`，槽间距 4 字节与 C 字节访问分开；补初始化调用、IER/DLAB/DLL/DLM/LCR/FCR/MCR 顺序，并将超时伪代码改为字节访问。

[本次 9 个定向来源快照](../learning/evidence/structure-20260929-sources.json)用于定位以上核对；此前 94 个来源哈希另行校验仍匹配。不把哈希一致解释为本次逐条重新认证全部技术结论；官方资料沿用原查阅日期，未重新核验上游网页。

## 改动与维护入口

- `scripts/pages.json`：由旧三元组列表改为显式 `parts/pages` 对象。
- `build_site.py`、`assets/site.css/js`：分组导航、H2/H3 编号、当前章节、离线旧锚点迁移。
- `anchor_migrations.json`：373 项当前迁移；旧 `legacy_links.json` 保留作历史输入。
- `build_registers.py`：精准回链，新的来源报告写 `structure-*`，不覆盖前轮记录。
- `check_site.py`：检查多层目录；新增 `check_structure.py`、`preview_structure_site.py`。
- `content/*.html` 与生成的主/兼容页；两张启动图及对应生成源。
- `README.md`、`STRUCTURE_REVISION.md`、`00_README.md`、项目状态和任务表；新证据统一 `structure-20260929-*`。

旧 `check_depth.py` / `preview_depth_site.py` 等属于旧格式与历史日期，不再作为当前维护入口；需要重现时在独立旧版本副本中执行。

## 实际验证

工作目录为仓库根；Python 标准库；Google Chrome 151.0.7922.108，`file://` 离线。

```bash
python3 docs_codex/learning/scripts/build_registers.py
python3 docs_codex/learning/scripts/build_diagrams.py
python3 docs_codex/learning/scripts/build_waves.py
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/preview_structure_site.py
python3 docs_codex/learning/scripts/check_structure.py
```

结果退出码均为 0，详见[结构报告](../learning/evidence/structure-20260929-checks.txt)、[浏览器报告](../learning/evidence/structure-20260929-browser.txt)、[内容比对](../learning/evidence/structure-20260929-content-audit.json)。

- 原 148 个 H2 源块哈希与归属核对；466 个正文/代码/表格/图块中 423 个在去标签/空白/单章号后保留，43 个改写逐一说明原因。首页/寄存器/证据页采用专项检查。这是内容保留检查，不是技术正确性认证。
- 旧站 728 文件、66,754,766 字节不变；输入时已有证据和示例 783 文件不变；未修订的 71 个资产不变。评审原文哈希不变。
- 429 寄存器行逐字相同，各组目的节按设备核对；生成 57 个 HTML/SVG/索引产物可重复。
- 全部 54 HTML 的本地链接/锚点、标题、导航、上下章、层级、63 SVG XML 及离线资源检查；最终链接计数以报告为准。
- 34 主页面 × 桌面 1440×1100 / 手机 390×844；7 页禁用脚本；199 条跨页旧 URL 实际跳转；静态旧书签回退、目录展开、图像缩放、寄存器搜索与迁移后的模型计算器均通过。
- 两张修订 SVG 文本在 viewBox 内；人工查看桌面向量页、手机首页、Ara/DDR 页面及启动图截图。未见页面级横向溢出、JS 异常或 HTTP(S) 页面请求。

检查过程中修复寄存器回链生成时对 `i2c` 的匹配漏项、列表重复编号、首页目录占屏和末尾空白；最终报告只列最终成功检查。未重新构建软件或运行 RTL/板测/性能/综合/ASIC 提取；历史 ELF 和运行记录没有转写为本次结果。

## 决策与最小下一步

- 用户已授权按照结构评审修改，已实现七篇/30 章；原审查报告仍保留其当时“建议、未实施”的历史身份。
- 读者从首页短路线开始，源码查阅按具体章跳转；后续修改同时维护正文锚点及映射。
- 如开展目标执行，先另行进入 V01/S01：唯一 profile/decoder 编译展开 → 标量及注错 → RVV 动态/数值证据；JTAG 段尾、继承栈、DMA 控制位宽、Ara 访存错误仍是既有验证门槛。
- 最少读取本交接、`learning/README.md`、对应正文与 `evidence.html#structure`。本轮不以新文档自动授权其他工程任务。
- `PROJECT_STATE.md`、`AGENT_TASKS.md` 已更新本次文档状态；无待协调合并的生产接口变更。
