# L01 / 系统教材独立复审交接

## 基本信息

- 日期/对话：2026-10-08，主管 `/root` 下 `/root/software`。
- 任务：在已完成L01-S作者实施后，独立只读复审OS、measurement和保留外设/Ara，向主管提问题及复核修正。
- 状态：17页源正文完整复审完成；五项发现均经主管修改、审读者只读复核；最终站点验收由主管进行。
- 输入：`mp/ara-pulp-v2` / `459f9d6f5748e39063f7bb67e959c2f27859915d`，叠加此前及并行文档修改；保护原图稿/PPTX、生产源码与旧证据。未提交。
- 本任务仅新增独立报告、reviews快照、本交接；不替主管修改共享状态或生成物。

## 本轮结果

- 完整审读17页：rtos、virtual-memory、linux、os-devices、os-debug、measurement、uart-gpio、interrupts、i2c、spi、dma、stream-io、ara、vector、sharing、peripheral-debug、vector-debug。
- 五项发现：vector构建目录错误；UART初始化/完成重复；sharing与vector强前置循环；sharing图注不匹配及隔离诊断入口；OS诊断缺软件入口。各项位置、影响、建议与关闭依据见报告第3节。
- 正常链、独立诊断、可执行条件均按读者任务复审。图文部分只抽核9个SVG标签/结构与3个WaveDrom JSON，不声称全图视觉检查。
- 定向核对DTS、Linux版本/配置/FP与V状态路径、CVA6计数器、SPI HAL。明确源码/已有产物/文档推演与目标执行不同。
- SPI复核触发本人boot页一处影响范围自纠：CR3V问题仅写擦路径，不扩大成所有NOR读启动阻塞。经主管授权修正并再次冻结，另在作者报告记录，不计本人章节独立通过。

## 改动与接口

- [独立复审报告](../L01_System_Independent_Review_2026-10-08.md)：完整覆盖、五项发现及验收边界。
- [独立快照](../reviews/2026-10-08_L01_independent_system_review/source-snapshot.json)：17页、9SVG、3时序及定向源码哈希。
- 本记录；补充作者报告最终release2检查链接。
- 无配置/profile/宏/地址/中断/位宽变化，无生产文件修改。所有正文公共修正由主管完成。
- learning已按主管要求完全冻结，本轮收尾证据写在docs_codex/reviews，未再写learning。

## 验证证据

- 工作目录：`/home/zhaowenyao/RISC_CVA6_prj/cheshire_ara`，上述提交；使用Python 3.13.5只读采样。
- 源阅读：逐页完整读取；修正后以 `sed -n '1,40p' docs_codex/learning/content/uart-gpio.html`、`rg -n 'build_journey|new-ownership|frames|software-debug|前置' docs_codex/learning/content/{vector,sharing,os-debug}.html`复核修改，人工比对完整正常链。
- JSON快照脚本读各路径并执行SHA-256，17页/9图/3时序齐全，定向源码无缺失。可通过Python读取JSON并逐路径重算sha256；内容以后续主管修改为准。
- `git diff --check`退出0。新增报告、快照README、交接3文件另以Python检查：11个本地目标存在，无尾随空白；快照全部路径重算SHA-256一致，脚本退出0。该检查没有代替全站锚点或浏览器检查。
- 未运行build_site、浏览器、目标编译、仿真、板测、OS或Ara。本文仅源正文与定向事实复核；最终生成/全站链接/浏览器由主管统一。

## 决策与下一步

- 用户已明确授权多Agent实施教材；没有授权本任务工程修复。文档审查未关闭Platform ROM、iDMA、Ara等验证缺口。
- 最小下一步：主管完成全站生成/结构/链接及桌面手机浏览器；把本报告纳入总报告/共享索引；后续S01/V01以具体目标环境验证标量、OS、向量和交接，不从教材检查推导实测结论。
- 最少读取：本独立报告、软件作者实施报告、主管总实施报告及各自证据。
- 共享状态由主管汇总：可记录“17页源正文独立复审、5项修正关闭”；不可写成“全站技术事实/实机独立验收通过”。
