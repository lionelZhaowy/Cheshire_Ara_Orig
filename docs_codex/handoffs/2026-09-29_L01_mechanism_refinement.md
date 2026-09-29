# L01 / 重点机制、启动模式与维护安全完善

## 基本信息

- 日期：2026-09-29；授权：根据结构修订复审继续优化教材。
- 输入：`mp/ara-pulp-v2`，HEAD `69fabdd227e225bf9f5f0b9ec5fe9d056999fea6` 加上一轮未提交的七篇/30章成果；本轮不是从 HEAD 的16章重写。
- 原有工作区改动、三份结构相关记录和最新复审原文保留；未执行 git 提交或生产工程操作。
- 完成范围：重点教材内容、五张结构图、报告目录与只读检查工具、入口/状态/交接。框架仍为七篇/30章、34主页面。

## 本轮结果

逐项对应 F1–F6 见 [REFINEMENT.md](../learning/REFINEMENT.md)。

1. 修正 iDMA、DDR旁路、Serial Link 启动和模型数组语境；普通章号引用改为可点击目标，检查编号与清单一致，保留历史文档原有日期与编号。
2. Crossbar 2×2 同组请求：译码竞争、AW仲裁预留、W来源与目标、WLAST局部释放、B/R计数及同ID先慢后快。映射到本地 mux/demux 符号；特别指出 W FIFO 可能早于 AW 握手预留，spill使内部释放和外部完成分离。
3. DDR 解释 AR→队列/地址映射→行状态与命令调度→PHY→返回缓冲→R，区分行命中/冲突、刷新、训练和背压。PLL 两域例子和 done 隔离/保持例子均标为教学/候选，不假设 ASIC 实现。
4. Boot 在原页内增加 Serial Link、UART、GPT/raw、SD、NOR、EEPROM 的 H3；每一路说明选择、格式、搬运、目的/入口及验证边界。Debug 先定义传输和模块，再列寄存器并串起 ELF 装载；去掉重复偏移。
5. CVA6 增加功能图及资源术语；电源术语先定义，时钟约束概念补释；新增五个因果自测，统一几处口语标题。
6. `report_run.py` 为两检查入口分配全新目录，默认 `/tmp/l01-*`，指定路径已存在则拒绝，包括空目录。记录实际时间、HEAD、工作区状态、输入哈希、输出位置。`check_structure.py` 默认只读；显式 `--check-generated` 在临时副本运行生成器，比较后删除副本。`build_registers.py` 不再写固定日期来源报告。

## 文件与来源

- 重点 `learning/content/{interconnect,ddr,clocks,power,cva6,boot,boot-debug}.html`；主题引用相关正文及生成页。
- `build_mechanism_diagrams.py` 和五张 `assets/mechanism-*.svg`；六张已有 WaveDrom JSON/SVG 均未改动。
- `report_run.py`、`check_structure.py`、`preview_structure_site.py`、`check_site.py` 与寄存器生成器；维护说明区分读取与写入。
- 本轮输入快照为 `evidence/refinement-20260929-input.json`；发布证据在 `evidence/refinement-20260929/`，旧 `structure-*` 等原件不变。
- 定向本地来源见 [sources.json](../learning/evidence/refinement-20260929/sources.json)；公开原理资料的范围、查阅及部分直连限制见修订说明。未全文认证供应商规范，也未引入私有寄存器值。

## 验证命令与结果

在仓库根；Python 标准库和本地 Chrome。实际时间、浏览器版本和输入快照以各目录的 `run.json` 为准。

```bash
python3 docs_codex/learning/scripts/build_mechanism_diagrams.py
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/preview_structure_site.py --out-dir docs_codex/learning/evidence/refinement-20260929/browser
python3 docs_codex/learning/scripts/check_structure.py --check-generated --out-dir docs_codex/learning/evidence/refinement-20260929/checks
```

以上输出目录用于本次发布，后续执行必须换新路径或省略 `--out-dir`；不能原样重跑后覆盖快照。

- [结构检查](../learning/evidence/refinement-20260929/checks/checks.txt)：旧证据/示例/资产875文件、旧站728文件、373迁移、章号目的/启动结构、54 HTML 链接/导航；临时生成123个产物比较；工作区检查前后哈希不变。
- [浏览器检查](../learning/evidence/refinement-20260929/browser/browser.txt)：34主页面桌面/手机、7页无脚本、199条跨页迁移、图像/索引/计算器交互及5张机制图边界；检查期间原有证据和教材输入哈希不变。
- [拒绝覆盖检查](../learning/evidence/refinement-20260929/output-protection.json)：两个入口遇到已有输出目录均返回2，已有运行的文件哈希未变。
- 内容源变化以本次 checks/content-changes.json 记录；旧逐块内容审计仍属于上一轮，不复用其固定段落序号认证新的改写。
- 初次检查发现备份包含历史 Python 缓存，已修正备份集合检查而未删除文件；初次浏览器重定向遇到 CDP 上下文切换，现只对导航期间上下文失效重试，其他异常仍失败。最终报告记录实际成功结果；未伪造 RTL 波形或日志。

无软件构建、RTL编译/展开/仿真、板测、性能、综合或ASIC提取。本轮没有改生产 RTL/sw/target/.bender 或依赖清单。

## 最小继续步骤

1. 阅读 `learning/README.md`，检查选新输出目录；编辑后才显式生成网站。
2. 内容审阅优先从 Crossbar 推演、DDR读路径、Boot模式入口开始；当前框架无需再拆站。
3. 目标执行另交 V01/S01，既有 JTAG段尾/继承栈、DMA宽度、Ara总线错误与器件镜像缺口保留；本文不授权实施这些工程修改。

共享状态与任务索引更新为本轮文档成果，原评审和旧交接保留历史身份。
