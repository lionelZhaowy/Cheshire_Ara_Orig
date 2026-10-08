# 交接：L01-ASIC / ASIC 机制教学与 P01 文档实施

## 基本信息

- 日期/对话：2026-10-08，主管 `/root` 明确分配子任务；用户授权多个子 Agent 实施教材，主管协调验收。
- 任务 ID/范围：L01-ASIC；后续追加 P01-D 文档。正文、独立报告/证据/交接；生产只读，不运行大型工程验证。
- 状态：**负责的十页正文和 P01 手册完成；待主管统一生成/发布验收。** 技术适配和源码提取未实施。
- 输入：`mp/ara-pulp-v2`，HEAD `459f9d6f5748e39063f7bb67e959c2f27859915d`；已有上轮正文/生成页/报告/PPTX 等未提交修改全部保护。
- 独占：content/clocks、reset、power、future；新增 asic-memory、cdc-rdc、physical-interfaces、timing-physical、manufacturing-test、silicon-bringup；独立报告/P01手册/本目录。导航/脚本/生成页/共享状态由主管统一。

## 本轮结果

- 修改四页、新增六个完整教学页，正常链与诊断分开；旧四页全部语义锚点保留，图/PPTX/WaveDrom不改。
- SRAM以真实Ara VRF实例说明1RW、64×64bit、16bank、一拍数据/valid/queue、k+2错配、局部写与初始化，另区分XPM零初始化。
- 时钟复位电源以安全取指/受控调频/排空重启/一帧关电恢复串联；CDC按传递对象并解释两端复位；I2C ACK贯穿PAD/封装/板；实际VRF路径贯穿STA/物理；scan/MBIST与首硅均明确对象和过程。
- P01手册交资源入口、替换语义、输入责任和验证矩阵，02继续负责提取规格；未穷举全设计实例。
- 交叉完整读新traps/boot/boot-debug，限定时钟复位/栈/调试前提，没有发现阻塞矛盾；可选回链建议已交主管。
- 新结论等级：现有源码确认、公式复算和文档检查；候选ASIC过程是方案建议。所有目标运行缺口保留。
- 依据：本地Ara/tech_cells/common_cells/LLC官方随附资料和消费者；官方在线I2C Rev7、OpenSTA/CTS与Siemens测试概念，版本适用范围见实施报告。

## 改动与接口

- [实施报告](../L01_ASIC_Implementation_2026-10-08.md)记录前后映射、来源和读者任务答案。
- [P01工程手册](../P01_ASIC_Adaptation_and_Evidence.md)记录待资料和接口验收。
- [证据](../learning/evidence/system-implementation-20261008/asic/README.md)独立可读；需要源码链接时保留完整仓库路径。
- 新slug/title/ID见page-manifest；推荐标题已发送主管，编号/篇章顺序由主管编排。正文新链接包括主管拥有的measurement与system-debug#platform-readiness。
- 诊断需主管保留：FPGA `i_clkwiz.locked()`未接，DDR wrapper两种MIG calibration完成输出未接，SoC `i_dbg_dm_top.ndmreset_o()`未用。不是实测启动必败。S01-B01仍按现有03专题登记，未修复。
- 配置/profile/宏/地址/中断/位宽变化：无。生产源码/软件/依赖/工程入口：未修改。未提交Git。

## 验证证据

- 仓库根；Python静态脚本读取HTML/链接/源哈希，公式复算；输入版本如上。
- 第一轮：10页ID唯一/H2H3有ID，旧四页ID全部保留；110个本地链接/资源无缺失；21个首批生产/依赖哈希保持；VLEN2048/4096的容量/bank公式通过；负责正文git diff --check退出0。XPM说明加入后再做最终检查，见final-checks。
- 最终命令：`python3 docs_codex/learning/evidence/system-implementation-20261008/asic/check_asic_docs.py`，退出0。10页/35个旧ID、111个HTML本地链接、3份Markdown的37个本地链接、21个源哈希、两组尺寸复算和diff检查均通过；记录final-checks.txt。learning于2026-10-08 03:17:52 UTC冻结交主管。
- 链接检查按生成页面的learning根目录解析content相对路径，对新主页面转查content；Markdown按各文件位置解析。不是HTML浏览器渲染。
- 生成/全站浏览器由主管执行；本子任务不写脚本/生成页，未冒称通过这些检查。
- 未编译/未仿真/未综合/未板测/未做CDC/RDC/STA/DFT或物理签核；未提取或映射真实宏；没有真人试读。

## 决策与下一步

- 用户确认范围按本轮多Agent实施与原保护边界；ASIC教学立即实施，具体资源和工程选择仍待输入。
- 缺失：工艺/宏/PLL/PAD/DDR/PHY/DFT/EDA/封装/板资料，最终设备与性能指标；具体提供者及阻塞步骤在P01表。
- 最小继续：
  1. 主管集成十页导航/生成页，完成浏览器、全站链接/锚点、源和旧资产保护验收。
  2. 主管独立用实施报告任务题复述正常过程，汇总共享状态；不把作者自查当真实读者试读。
  3. P01/M01/I01获得资料后补契约；E01固定实例后补完整技术资源账本，真实适配/运行另授权。
- C00合并建议：L01-ASIC正文与P01限定范围文档完成；工程提取、OS移植、平台修复和目标验证状态不变。旧07/08规划由主管按实际载体更新，不新增数字08占位正文。
