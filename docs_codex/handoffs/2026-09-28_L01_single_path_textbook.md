# 交接：L01 / 单线中文离线教材重构

## 基本信息

- 日期：2026-09-28；任务 L01。
- 授权：基于当前源码重新组织并编写教材、完整旧站备份、必要独立示例和轻量脚本、网页检查及交接索引；禁止生产 RTL/sw/地址图/filelist/FPGA/依赖修改、大型仿真、提取、发布及 Git 提交。
- 状态：教材实现完成；目标 SoC 动态验收待验证。
- 输入：分支 `mp/ara-pulp-v2`，HEAD `4f240258ca683913b7e17949aff23139bff981f1`。开始时仅有未跟踪 `2026-09-27_ENV01_codex_gpu_auth.md`，未修改。
- 负责：`docs_codex/learning/`、新增 `learning_backup/`，本交接及必要项目/参考入口。未启动子 Agent。

## 本轮结果

- 先完整复制旧站到 [learning_backup](../learning_backup/index.html)，728 文件、66,754,766 字节；写入前后按 SHA-256 核对。备份含 HTML、资源、维护脚本、示例、历史日志和原有本地构建产物。
- 新站 [index](../learning/index.html) 为 16 章连续课程、6 项实验、2 页参考（共 20 页主页面），另保留 20 个旧 URL 迁移页。取消原入门/进阶/硬件并列目录。
- 原理顺序：系统职责 → 配置展开 → 互连与适配 → 裸机运行模型 → 构建 → 加载复位启动 → 仿真 → 设备协同 → 存储/向量 → 系统扩展。内容分析、逐章依赖和全部旧内容去向见 [重构设计](../learning/CONTENT_REDESIGN.md)。
- 新写 `journey.c` 贯穿全局/局部对象、初始化、编译链接、装载、结果输出及 RVV。用 137 项结果和独立公式校验；标量/向量同一任务，尾部守卫和注错路径服务关键概念。
- 六实验分别为对象布局、装载/错误传播、中断协同、EEPROM/NOR 只读对照、RVV 同任务对照、独立 Reg 设备。简单环境/Hello/MMIO/轮询/模型推导并入正文。DMA/capstone 数据运行因既有控制接口缺口退出主线，历史代码和证据保留。
- 16 张新 SVG 按新版依赖设计；复用基础样式和离线增强交互。429 个寄存器条目保留，回链当前设备章。
- 事实等级：技术结论为当前本地源码静态确认；四种软件构建和浏览器为本轮实测；旧单元/模型结果为标明日期的历史实测；SoC/板级/ASIC 为待验证或规划。

## 改动与接口

- `content/*.html` 是新正文源；`scripts/pages.json` 是唯一目录顺序；`build_site.py` 生成页面，`legacy_links.json` 保留旧书签。
- `build_diagrams.py` 生成 `assets/new-*.svg`；旧图仅供历史追溯，不用于新主线图表编排。
- 新 `examples/journey.c`、`scripts/build_journey.sh`；复用原 `rvv_add.S` 和生产库的只读输入。输出到唯一新目录；`JOURNEY_OUT` 指定非空目录时拒绝覆盖。
- `build_registers.py` 改写本轮 `restructure-register-sources.json`，保护原 `advanced-register-sources.json`。`record_sources.py` 记录 70 个当前源码/参考/示例输入哈希。
- 更新 `README.md`、`check_site.py`、`preview_site.py`；根目录旧 URL 为迁移入口，无旧课程导航。旧备份独立可读，不作为新站生成输入。
- 更新项目状态/任务表/总索引、配置/软件手册的阅读入口和交接索引，历史正文/结论保留。
- 生产配置/profile/宏/地址/IRQ/位宽：**无修改**。DMA 风险仍由 S01/V01 接收；固定配置和独立工程由 E01/C00 接收。
- 未 Git 提交、推送或发布。普通 `git diff --stat` 不包含新增备份与新文件，审阅时结合 `git status --short`。

## 验证证据

工作目录为仓库根。全部本轮报告位于 [evidence](../learning/evidence.html#current)，文件名前缀 `restructure-`，不改历史日期。

1. **软件构建：** GCC 15.2.0（g5115c7e44）。实际执行 `timeout 60 bash docs_codex/learning/scripts/build_journey.sh scalar spm`、`scalar dram`、`INJECT_ERROR=1 … scalar spm`、`rvv spm`，四次退出 0。检查 `.i/.s/.o`、548 字节 BSS、seed/greeting 节归属、入口/栈符号、标量调用及 RVV 指令。完整日志、哈希、产物路径见 [构建报告](../learning/evidence/restructure-builds.txt) 和 `restructure-build-logs/*.txt`。每次保留 24/25 条编译/链接告警，包括原 MMIO 对象边界与 RWX 段；未静默屏蔽。
2. **离线网站：** `python3 docs_codex/learning/scripts/check_site.py` 检查 40 个 HTML（20 主页面 + 20 迁移）、本地链接/锚点、标题/H1/目录/相邻章、44 个 SVG XML（16 新图 + 28 历史图）、Shell 语法及 Markdown 链接。
3. **实际浏览器：** `python3 docs_codex/learning/scripts/preview_site.py`。Chrome 版本见 [报告](../learning/evidence/restructure-browser.txt)；20 页分别在 1440×1100 与 390×844 的 `file://` 环境检查图片、导航、页面溢出；测试寄存器筛选/清空、容量计算与非法输入、图缩放、自测展开、关闭脚本的运行模型/启动/429 条索引、16 张新 SVG 文字边界及 20 个迁移入口。无 JS 异常、资源失败或 HTTP(S) 页面请求。首页、运行模型、启动、手机与图像截图保存在本轮 evidence；人工查看发现并修正 LLC 下游连接和向量尾部文字布局。
4. **完整性：** 备份逐文件哈希、主站历史 evidence 内容、重复生成一致性、来源哈希、受保护目录未改变及 `git diff --check` 结果见 [检查报告](../learning/evidence/restructure-checks.txt)。

重生成命令：

```bash
python3 docs_codex/learning/scripts/build_diagrams.py
python3 docs_codex/learning/scripts/build_registers.py
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/check_site.py
python3 docs_codex/learning/scripts/preview_site.py
python3 docs_codex/learning/scripts/check_integrity.py
```

未执行生产 RTL 编译/展开/仿真、综合、板测、ASIC 提取。未重新导出生产清单，保留既有独立 `prepare_sim.sh` 的目标操作；未重跑未修改的历史 Reg 单元（2026-09-23 的 35 项结果不冒充本轮）。本轮软件编译不能证明 UART、退出状态、IRQ、器件读取或 Ara 动态行为正确。

## 决策与下一步

- 用户 2026-09-28 明确要求重新写作、取消三条路线、完整备份和直接实施；据此重写，无待排版审批。
- 后续最小动作：
  1. V01 在目标许可环境按 [第 07 章](../learning/simulation.html) 导出当地清单，核对唯一向量 profile/decoder，实际编译、SelectedCfg=3 展开和 DPI/模型链接。
  2. 运行实验 B 正常/注错，保存工具版本、HEAD、ELF 哈希、compile/elaborate/simulate 全日志、结果与 PC/CSR；单独检查 JTAG 段尾边界。
  3. 依次执行 C/D/E，分别观察 IRQ 清源、EEPROM/NOR 协议、RVV 动态握手和数据结果；有首次失败就停在该层定位。
  4. S01/V01 统一并验证 DMA 64/32 位控制桥、lane 和 HAL 访问后，再决定恢复 DMA 数据实验；VGA/USB/SD/真实 GPIO 引脚需补模型/激励。
- 最少阅读：新站 README、CONTENT_REDESIGN、第 07 章、实验手册和证据页。跨任务事实仍参照 PROJECT_STATE。
- 共享状态已同步；不要求其他对话合并新的生产实现结论。
