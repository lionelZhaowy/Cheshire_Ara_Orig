# 交接：L01 / 全书审查、外设与Ara教学重组

## 基本信息

- 日期：2026-10-08；单对话执行，未启动其他Agent。
- 授权：初始全书审查/03–08条件评估/后续Prompt；用户追加外设和Ara/RVV正文实施、正常教学与诊断分离。生产RTL/sw/依赖/地址图/工程构建只读，不运行大型验证。
- 状态：授权文档分析与局部实施完成，文档检查通过；待独立教学复审，目标工程验证仍待完成。
- 输入：mp/ara-pulp-v2 / 459f9d6f5748e39063f7bb67e959c2f27859915d。
- 输入已有修改：learning/figures/20261007/editable/diagrams.pptx，保护未写；输入快照记录其哈希。
- 拥有范围：本轮报告、外设18–23/Ara24–26及必要入口、生成页面、导航/检查最小同步、software路线短注、独立证据/交接、共享状态简短汇总。

## 本轮结果

- 完整审读30主章及首页/实验/来源页；寄存器索引仅入口/分组及相关字段抽查，不宣称429项事实全审计。
- 已交付全章节表、锚点问题/处方、全书路线及两种改写样例、分阶段读者验收。
- 外设采用UART文本、GPIO位操作/事件、EEPROM/NOR只读、DMA三行机制、Link写读/VGA彩条/USB控制传输的正常任务；保留无驱动/无模型/未接线条件。
- Ara先讲137元素与RVV状态，再讲真实接口、内部结构、容量、协作及结果交接。保留本地限制与执行前提。
- 新增peripheral-debug与vector-debug参考章；旧锚点保留。七篇/30主章不变，主页面由34增36。
- 03/04建议整合现有资料；05/06/08限定范围文档可立即写；07待OS目标输入。5个完整新对话Prompt按所有权拆分。
- 未实施：其余全书重排、S01-B01修复、iDMA修复、工程提取/依赖升级/模型完善/OS移植。
- 证据等级：技术实现为定向源码确认；VCU118 HelloWorld为用户报告；历史ELF/dump/小单元运行仍为已有产物；本轮运行只产生文档/浏览器实测；全书路线和候选工程契约为建议。

## 改动与接口

- 全书审查：../L01_Teaching_Quality_Review_2026-10-08.md。
- 外设对照：../L01_Peripherals_Revision_2026-10-08.md。
- Ara对照：../L01_Ara_RVV_Revision_2026-10-08.md。
- 条件评估：../03-08_Topic_Readiness_2026-10-08.md。
- 后续任务：../L01_Next_Tasks_Prompts_2026-10-08.md。
- 内容源：learning/content/uart-gpio、interrupts、i2c、spi、dma、stream-io、ara、vector、sharing；cva6/configuration仅增定向阅读提示；index/evidence增入口。
- pages.json新增两个reference；check_structure总数36；preview_structure增加相关截图。build_site更新36主页及20兼容页导航。未改图/可编辑源。
- software/README增加历史dma_2d路线的当前门槛说明。
- 本轮证据目录：learning/evidence/peripheral-20261008，包含before-content/input及检查记录；目录名沿用最初外设范围，含Ara补充。教材本体可独立阅读，源码链接需完整仓库。
- 生产配置/profile/宏/地址/IRQ/位宽变化：无。
- 未提交git commit。E01/S01/V01/M01/I01/P01只接收文档建议，不因此获得实施授权。

## 验证证据

工作目录为仓库根；Python 3.13.5、Google Chrome 151.0.7922.108。源码输入为上述HEAD加input.json所记工作区；本轮无生产配置变化。

|实际命令/检查|退出码与结果|新证据|
|---|---|---|
|git status --short；git branch --show-current；git rev-parse HEAD|0；记录原有PPTX修改与本轮路径|input.json|
|python3 docs_codex/learning/scripts/build_site.py|0；36主页面、20兼容入口|生成页面与后续被测哈希|
|python3 docs_codex/learning/scripts/check_structure.py --check-generated --out-dir docs_codex/learning/evidence/peripheral-20261008/generated-check|1；临时副本WaveDrom所需Chrome未启动、缺DevToolsActivePort|generated-check/checks.txt，失败保留|
|同上，输出改为release-generated，在允许的沙箱外执行|0；56 HTML、3137本地链接/资源、703 Markdown链接、373迁移；128生成产物一致，37结构SVG临时重生一致|[生成检查](../learning/evidence/peripheral-20261008/release-generated/checks.txt)|
|python3 docs_codex/learning/scripts/preview_structure_site.py --out-dir docs_codex/learning/evidence/peripheral-20261008/release-browser（沙箱外）|0；36页桌面/手机、7无脚本页、199跨页书签、导航/交互/图像加载通过|[浏览器报告](../learning/evidence/peripheral-20261008/release-browser/browser.txt)及run.json/截图|
|定向SHA256/旧id/容量与分块算式检查|0；162资产含用户PPTX未变；34原正文快照未变且旧id全部保留；58来源哈希未变|protection-and-task-checks.txt、release-protection.txt、sources.json|
|git diff --check；check_site.py（交接收尾后）|0；无空白错误，本地文档链接检查通过|documentation-final.txt|

前后检查独立保存，未覆盖历史。875历史证据/示例/资产、728旧站文件保护检查通过。Chrome沙箱失败是运行环境限制，不是页面通过；沙箱外重试才产生浏览器/临时生成通过证据，没有自动审批拒绝或待用户确认事项。run.json记录各轮被测HTML集合与哈希；release-*为最终正文结果。

人工实看I2C桌面、SPI手机、Ara内部图与相邻解释、RVV手机及两个诊断入口截图。自动遍历全站不等于人工逐屏检查所有页面，寄存器字典仍是定向抽查。新图数量为0；复用已有结构图与WaveDrom，原可编辑PPTX哈希与输入相同。

未软件构建、未生产RTL编译/仿真、未综合/板测/性能或ASIC签核。未对所有寄存器和所有RTL重新审计；未做真人试读。外设连接示例、RVV容量推导与命令预期不代表目标运行通过。

## 决策与下一步

- 用户本轮已明确正常教学与故障诊断分离、授权外设/Ara实际优化；未授权生产工程变更。
- 未决：DDR/IP/工艺/OS选择和运行模型；不得补成已冻结参数。PlatformRom非零返回缺口、iDMA宽度/ID门槛、Ara目标执行及总线错误缺口继续开放。
- 最小下一步：
  1. 独立L01-R复审本轮正常链与诊断定位。
  2. L01-S重组软件13–16，首个程序先走到main。
  3. M01-D/P01-D可并行写各自限定接口/适配手册。
  4. L01-O串行汇总路线/索引，E01/S01/V01工程工作另行授权。
- 最少输入：根AGENTS、PROJECT_STATE/AGENT_TASKS、本交接、全书审查、条件评估、相关任务Prompt。
- 共享状态由本轮单一协调对话简短更新；历史结果不改写，待目标验证状态不关闭。
