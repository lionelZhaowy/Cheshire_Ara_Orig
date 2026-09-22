# L01 交接：中文离线入门教材与独立学习实验

## 基本信息

- 日期/对话标识：2026-09-22 / L01 learning site。
- 任务 ID / 授权：L01；基于当前仓库制作中文图文入门网站，允许教材内独立示例、轻量脚本及检查；不修改生产 RTL、原 sw、共享 filelist，不执行大型仿真/综合/板测/ASIC 提取，不启动子 Agent。
- 状态：教材网站实现完成；软件轻量构建完成；Questa/VCS 实际编译展开与运行待验证。
- 输入分支/提交：mp/ara-pulp-v2 / `379ae4544bc62e05a2736b11b33a3244181bba38`。
- 初始已有变更：00_README.md、01_Cheshire_Ara_Quick_Start.md 已修改；AGENTS.md、02、PROJECT_STATE、AGENT_TASKS、HANDOFF_TEMPLATE、configuration/software/handoffs 已存在但未跟踪。本轮保留原内容，不清理、不覆盖。
- 负责路径：新增 `docs_codex/learning/`，本独立交接；串行增补 PROJECT_STATE、AGENT_TASKS、handoffs/README。原 RTL/sw/依赖/FPGA/清单只读。

## 本轮结果

- 新增入口 [learning/index.html](../learning/index.html)，10 个离线页面：路线、架构、必要基础、配置、C/ELF/启动、仿真、访存/DMA/RVV、实验、ASIC/AI 导读、证据索引。
- 10 张 SVG：路线、Cheshire/CVA6/Ara、配置、C→ELF→运行、JTAG 启动时序、地址/LLC/SPM、AXI 握手、CPU/Ara/DMA 一致性、排错、未来 NPU/ISP/LVDS/AXI4 DDR。
- 原生 HTML/CSS/JS，无 CDN/后端。步骤切换、折叠自测、离线 AI 权重/KV/激活容量与简化带宽计算器。正文不依赖 JS 或网络。
- 一个独立 lesson.c 串联 Hello→数组→MMIO→timer→DMA→RVV，默认 137 项，总和 28085；错误进入 return，支持故障注入。RVV 汇编单独编译，C/CRT/库保持标量 ISA，进入向量函数前启用 VS。
- 本轮未完成：任何目标 CPU 实际执行、RTL 编译展开、DMA/RVV 功能运行、中断 handler 回归、真实 DDR/板级操作、ASIC 提取。

新结论及等级：

1. **本轮实测**：GCC 15.2.0、Questa 2024.1 可调用；VCS/vlogan 不在 PATH；许可证未检查。
2. **本轮实测（仅软件构建）**：六个 SPM 阶段、array DRAM、错误注入 array 共 8 次最终构建退出 0；SPM entry=0x10000000、DRAM entry=0x80000000；RVV 反汇编出现 vsetvli、两条 vle32.v、vadd.vv、vse32.v。没有向量执行证据。
3. **源码确认 + 本轮独立导出**：旧仿真清单仍为标量 profile，stub/真实 decoder 共存；SELCFG=3 不切 profile。教材 prepare_sim.sh 本地导出唯一向量 profile/真实 decoder 到全新教材输出目录，未改旧清单。输出有 W28 .svh 类型告警，未靠实际 RTL 编译消除疑问。
4. **源码确认**：JTAG 启动等 SPM 配置标志，halt/SBA 写入/DPC resume；serial link 另走 scratch[1:0] 入口与 scratch2 掩码 2。crt0 清 BSS、初始化 FS，不初始化 VS，_exit 实际 ret。
5. **源码确认的新待核查项**：VIP jtag_elf_preload 以 i<=sec_len、步进 8 读写，段尾有额外写/越界索引风险；未动态验证影响、未修复。
6. **本轮构建告警**：旧 MMIO `extern void *` 基址声明触发 GCC -Warray-bounds，原布局产生 RWX LOAD 告警；保留完整日志，没有改旧接口或隐去告警。
7. **教学设计，功能待验证**：DMA/RVV 仅在单核全 128 KiB SPM 条件下，预约物理 [0x10010000,0x10011000)，仅经高别名访问；应用低 64 KiB，栈必须高于保留区。此约定仅属于独立实验，不是未来 DDR 共享区或生产地址图变更。

## 改动与接口

- `learning/content/*.html` 为正文维护源，根 HTML 为生成结果；`scripts/build_site.py` 统一导航。
- `assets/*.svg` 由 `scripts/build_figures.py` 生成；CSS/JS 为本地资源。
- `examples/lesson.c`、`rvv_add.S`；`scripts/build_example.sh` 最小交叉构建，派生自 sw.mk，不调用根 make、不使用 LTO。
- `scripts/prepare_sim.sh` 仅 Bender --local 导出，复制原 start 与 DPI 到新目录，引用原仓库源码，不是独立 ASIC 提取。
- `scripts/check_run.py` 检查实际日志；`check_site.py` 静态检查网站；可选 `preview_site.py` 使用本机 Chrome/CDP 预览，只依赖 Python 标准库。
- 日志/报告：`learning/evidence/environment.txt`、`builds.txt`、`build_logs/*.log`、`prepare.txt`、`checks.txt`、`browser.txt`、`source_manifest.json`、`preview-*.png`。
- 随机命名的 ELF/对象/清单输出目录保留在 evidence 下，以教材局部 .gitignore 排除；未清理旧产物。文本报告记有真实路径/哈希，重新构建产生新目录。
- 网站本体可离线搬迁；源码相对链接需完整仓库。独立仿真导出的绝对路径要在目标机器重新导出。
- 生产配置/profile/宏/地址/中断/位宽：无修改。E01/S01/V01/M01 可使用教材与缺口表，但对应实施状态不改为完成。
- 未创建 Git 提交。

## 验证证据

工作目录：仓库根。主要命令：

```sh
bash docs_codex/learning/scripts/build_example.sh hello spm
bash docs_codex/learning/scripts/build_example.sh array spm
bash docs_codex/learning/scripts/build_example.sh mmio spm
bash docs_codex/learning/scripts/build_example.sh timer spm
bash docs_codex/learning/scripts/build_example.sh dma spm
bash docs_codex/learning/scripts/build_example.sh rvv spm
bash docs_codex/learning/scripts/build_example.sh array dram
INJECT_ERROR=1 bash docs_codex/learning/scripts/build_example.sh array spm
bash docs_codex/learning/scripts/prepare_sim.sh
python3 docs_codex/learning/scripts/build_figures.py
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/check_site.py
python3 -m py_compile docs_codex/learning/scripts/*.py
git diff --check
```

- 最终 8 次软件构建均退出 0；完整 flags/告警见 build_logs，ELF 哈希和入口见 builds.txt。早期构建发现独立 ticks 函数在其他阶段未用，改为仅 timer 编译后完成最终全阶段轻量构建。
- 网站最终检查通过：10 HTML、10 SVG、全部站内链接/锚点/资源/alt 与无外部渲染依赖；准确链接计数见 checks.txt。13 段教学 shell 命令通过 bash -n，仅语法检查，不代表仿真运行。
- 31 个定向读取的原始源码/脚本 SHA-256 前后相同；git diff --check 退出 0。
- check_run 用四个人工字符串检查正常/错误结果/缺少结束/工具错误的接受拒绝行为；这些是**检查器测试输入，不是 DUT 日志**，未作为运行证据保存或展示。
- Chrome 151.0.7922.108：全部 10 页桌面 1440×1100、手机 390×844 实际加载；图像加载/导航/无整页横向溢出通过；步骤按钮、折叠、自主改变上下文触发预算重算通过；无 JS 异常、无 HTTP(S) 页面资源请求；关闭 JS 的生命周期正文存在。
- 实际浏览器检查最初运行于 `/tmp/l01_preview.py`，已将相同行为的可迁移版本保存为 `learning/scripts/preview_site.py`，并在最终内容生成后再次执行该交付脚本通过。初次 Chrome 在沙箱内因本地 socket setsockopt 限制失败，经工具授权在沙箱外仅访问本地页面后成功；没有自动审批拒绝。
- 初版预览检查器错误地要求至少 7 个 h2，实际该章为 6 个；修正检查后重跑通过。网站并无因此产生的空白章节。
- 已人工查看入口、架构、启动时序、AXI 表、预算计算器、手机截图；其他页面完成浏览器 DOM/资源/布局检查，不宣称每个浏览器或每个像素均验收。

**没有执行 RTL 编译、展开或仿真；没有综合、板测或提取。** 目标程序预期输出均标为待验证。Questa 功能与许可未验收；VCS 服务器版本/许可/主机 C++/SV 兼容性未验收。

## 决策与下一步

- 本轮用户决定：优先完整学习教材；后续工程提取与 AI 系统只是导读。本轮未改变固定配置提取建议或冻结产品架构。
- 下一位最小步骤：
  1. 阅读 learning/lifecycle.html、simulation.html 与实验 0～3，使用全新目录导出固定向量清单。
  2. 在有许可的 Questa/目标 VCS 环境真实编译展开；先解决首错、W28 涉及输入和 DPI/C++ 组合，记录实际版本。
  3. 运行 array 正常与注入错误两份 ELF，回传完整构建/展开/运行日志与退出状态；再推进 DMA/RVV，并补退休/PC 路径证据。
  4. V01 单独处理加载段尾测试；S01 单独处理 CRT/CLINT/MMIO 表达和原示例错误返回；这些是建议，不自动授权改原工程。
- 最少输入：learning/README、evidence 页、相关实验、当前实际源码；无需通读所有第三方依赖。
- 已串行向 PROJECT_STATE、AGENT_TASKS、handoffs/README 增补网站导航和证据状态，未改 E01 等任务状态。
