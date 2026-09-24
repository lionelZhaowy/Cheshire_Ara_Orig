# 交接：L01 / 硬件原理、结构生成与互连主线

## 基本信息

- 日期：2026-09-23。用户确认先前两轮分析方案后明确“开始实施”。不启动子Agent。
- 范围：CVA6理解功能/接口与配置，不深究流水线电路；Crossbar、协议适配、存储/DMA、外设/中断、平台及自定义IP深入到结构和验证。
- 输入分支 `mp/ara-pulp-v2`，HEAD `ae2b69fe0640e57c89dfc6bcc9404bfd5008e1a5`。
- 开始唯一未跟踪文件：`2026-09-22_M01_DDR_interface_feasibility.md`，未读写、移动或提交；不接手M01实施。
- 状态：教材实现与轻量验证完成。只编译/仿真教材独立双文件单元，没有生产SoC/AXI/IP回归。
- 默认工具沙箱因WSL `/mnt/wslg/distro`挂载错误无法启动，改用获准的沙箱外定向读写与轻量验证；无生产配置修改。

## 本轮结果

- 新增11页：hardware、rtl-elaboration、cpu-config、soc-topology、axi-crossbar、axi-adapters、hardware-memory、hardware-devices、hardware-platform、ip-integration、hardware-labs。
- 新增10张原生SVG：路线、配置汇合、结构前后对照、crossbar分流/汇聚、AW/W/B阶段、lane/适配、存储、外设事件链、平台契约、自定义IP。
- 全站35页、28图。CVA6章节追profile→gen_cva6_cfg→build_config→消费者；H03手算UART/Ara/LLC；H04剖析decode/demux/mux、ID、W选择队列、顺序与背压；H05解释lane/ID/cut/CDC。
- 交互复用离线图片缩放、折叠答案，新增写事务步骤演示，标记非真实波形。
- 独立`lesson_reg_adder.sv` + TB：32位Reg样式控制、字节写、START、BUSY、DONE/W1C、IRQ、错误响应；未分配生产地址或接入SoC。
- `hardware_lab.py`：有限单核拓扑计算、+0/+4 lane示例、人工握手trace检查；不是SV求值/展开器或AXI仿真器。基准JSON锁定3个相关生产文件，源码变化需人工重审。

## 新结论与证据等级

1. 源码静态确认：`cheshire_pkg.gen_axi_in/gen_axi_out/gen_reg_out`分别生成发起端、AXI目标和Reg目标。UART关闭压紧内部索引，I2C仍在0x03003000；第一层Reg大窗口不消失。
2. 源码静态确认：默认6发起者→Ara7发起者，`AxiSlvIdWidth=2+ceil(log2(N))`均为5；Ara+2外部master=9时为6。不是LLC输出ID宽。
3. 本地AXI设计文档与RTL并列记录：同输入同ID同方向跨目标需等待，未使用响应重排缓冲；PipelineStages参数存在，但文档有内部切分造成W循环等待的风险说明，当前SoC为0，未验证非零值。
4. 本轮实测：Questa 2024.1可编译运行本教材独立单元；35项检查通过。`+INJECT_FAIL`触发$fatal后原始进程码仍为0，需日志检查器拒绝，最终检查器exit1。不能扩展成完整SoC许可/仿真通过。
5. 原iDMA控制口位宽与HAL缺口保持未解决状态，本轮不修复、不运行DMA。

源码路径/符号在正文，24个直接引用源码哈希见`learning/evidence/hardware-source-manifest.json`；原31+81条来源记录复核一致。

## 改动与接口

- 仅`docs_codex/learning/`教材正文、生成页面、SVG、脚本、独立示例和证据；旧正文增加硬件入口。
- 同步00/01阅读入口、configuration/README、learning/README、PROJECT_STATE、AGENT_TASKS与本交接索引。
- 生产RTL、sw、地址图、profile、宏、filelist、FPGA、.bender均无修改。未清理旧产物。
- 自定义IP接入、AXI数据引擎、NPU/ISP/DDR方案仍是教学规划；独立加法例不是AXI从设备，没有通用CDC/队列/缓存一致性。
- 本轮未提交或推送；此前GitHub发布授权已在此前任务完成，本轮不自动重复发布。

## 验证证据

工作目录仓库根，命令：

```sh
python3 docs_codex/learning/scripts/build_hardware_figures.py
python3 docs_codex/learning/scripts/record_hardware_sources.py
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/hardware_lab.py self-test
bash docs_codex/learning/scripts/run_hw_unit.sh
python3 docs_codex/learning/scripts/check_site.py
python3 docs_codex/learning/scripts/preview_site.py --hardware
git diff --check
```

- 18项教学模型检查exit0：数量/ID边界、UART/I2C索引、SPM、lane、握手稳定/注错、地址区间/重叠；不声称覆盖完整AXI。
- 单元最终目录`/tmp/cheshire-hw-unit.WkvQee`：vlog exit0且0 errors/0 warnings；正常35检查、630ns完成；注错raw rc0，检查器正确exit1，wrapper exit0。原始日志在临时目录，可重跑；摘要`hardware-unit.txt`保留失败修复经过。
- 首次wrapper错误要求注错raw rc非零，exit1；修正为正常与注错使用同一`check_hw_unit.py`日志判据后重跑通过。没有删除失败记录。
- 网站检查35 HTML / 28 SVG、本地资源/锚点/图片alt/离线依赖/脚本语法；精确链接计数见`hardware-checks.txt`。
- Chrome实际file://桌面1440×1100、手机390×844逐页预览；完整导航、图片加载、无整页横向溢出；新增步骤按钮、折叠、图片fit/full；禁JS可读正文；10新SVG文字未超viewBox；无JS异常或HTTP(S)页面请求。结果`hardware-browser.txt`，截图`hardware-*.png`。
- 人工查看crossbar与AW/W/B图，修正交叉线遮挡标签；配置图改成真实多输入汇合，随后重跑浏览器检查。
- 未运行生产SoC的编译/展开/仿真，未运行VCS/综合/板级操作或ASIC提取；未做CDC/RDC或性能签核。

## 决策与下一步

- 用户已确认本次层次与深度；普通排版和独立教学单元在授权范围内。
- 下一步1：从hardware→H01/H02/H03/H04/H05学习，先交手算结构表和事务路径。
- 下一步2：V01在独立配置/工作库验证真实crossbar同ID跨目标、AW/W错开、背压与错误响应；不能拿教学模型替代。
- 下一步3：S01/V01先验收DMA控制lane/访问宽度，再运行已有综合DMA实验；生产修改需另任务授权。
- 最少读取：本交接、learning/README、hardware-labs、对应硬件章节。共享索引串行同步，不改M01任务状态。
