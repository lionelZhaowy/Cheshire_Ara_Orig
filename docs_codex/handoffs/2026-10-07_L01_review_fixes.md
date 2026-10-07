# L01 / 官方资料教学扩充评审 R1、R2 定向修正

## 基本信息

- 日期：2026-10-07；任务 L01；角色为修改者。
- 用户授权：修复独立评审的两项 P2 文档问题；不修改生产代码或执行目标仿真。
- 状态：两项修改及文档检查完成，待独立评审确认。
- 输入 HEAD：`f01487c2f3c3e990b515bff813227b97049976a3`。开始仅有未跟踪的独立评审记录和 `review-teaching-20261007/independent-checks.json`，均原样保留。
- 负责范围：相关 HTML 正文/生成页、既有 Markdown、浏览器检查入口的小幅扩展、独立证据和必要进度索引。

## 本轮结果

### R1：Platform ROM 的栈前提

- [boot#platform-rom](../learning/boot.html#platform-rom) 的分支表改为条件保证，补充 `la sp, __stack_pointer$` 只是赋值；`HW_FEATURES.llc=0` 会直接到 `_prom_check_run`，跳过 BIST、内部 SPM 和按容量调整栈。
- 明确 `LlcOutConnect=1、LlcNotBypass=0` 时平台的责任：在首次栈访问前提供替代可写存储和有效 sp；可以提前提供存储，或先由不依赖栈的早期汇编建立存储/栈，再调用需要栈的 C 程序。
- 三种情况可分别推演：保留 LLC 时 ROM 负责内部 SPM/栈调整；无 LLC 时平台负责替代存储；Bootrom=0 时平台直接承担第一阶段。PlatformRom=0 进入通用 ROM C 之前也须满足可用栈条件。
- 同步 clocks/runtime/reset、`software/RUNTIME_AND_DEBUG.md`、`03_Platform_ROM_Clock_IP_Configuration.md` 中相同的泛化表述；正常返回缺陷 S01-B01 仍保留，未修生产 ROM。
- 依据：`hw/bootrom/cheshire_bootrom.S::_start/_prom_check_run`、`cheshire_bootrom.ld::__stack_pointer$`、`hw/cheshire_soc.sv::gen_llc/gen_llc_bypass/reg_hw2reg.hw_features`。等级：源码静态确认。

### R2：三个独立配置案例

[configuration#case-baseline](../learning/configuration.html#case-baseline) 给出共同 profile、单核/无 Ara、启动、LLC、ISA/ABI、链接及装载前提；原合并行拆成三个链接行，并各增加独立小节：

| 案例 | 完整记录与验收要点 |
| --- | --- |
| [AXI RT](../learning/configuration.html#case-axi-rt) | SELCFG=1 只开 AxiRt，CPU RVSCLIC=0；6 manager/2 region、DMA=2；参考 axirt_budget.spm.c，1024 字节逐项相等、读写预算各减1024且剩余相同、返回0。iDMA 控制位宽/ID问题继续阻塞动态验收；Ara+RT 必须调整生成规模和软件编号。 |
| [CLIC](../learning/configuration.html#case-clic) | SELCFG=2 只开 Clic，CPU RVSCLIC=1；默认74源、8控制位；参考 clic_basic.spm.S 的 mtvec/mtvt/mintthresh 与源31，检查高门限抑制、低门限触发及返回码。明确原例不证明一般 ISR 的上下文恢复/mret/嵌套。 |
| [IRQ Router](../learning/configuration.html#case-irq-router) | DefaultCfg 只加 IrqRouter 的待建配置，没有现成 SELCFG；RVSCLIC=0；明确源/目标尺寸、UART源1、掩码地址0x02080004、目标bit0为PLIC；给出屏蔽/放行两阶段受控事件验收、清理旧pending和handler职责。缺专用入口/程序/激励继续标明。 |

- 同步 [RECIPES](../configuration/RECIPES.md#review-cases-20261007) 的三案例矩阵；不增加 Lab、不编造 runnable 命令或通过记录。
- 依据：`tb_cheshire_pkg` 配置函数、`gen_cva6_cfg`、`gen_axi_rt/gen_clic/gen_irq_router`、`cheshire.mk` 的 AXIRT 生成变量、两个现有测试源、Router RTL/寄存器复位及 CLIC 随附官方说明。等级：源码静态确认；三个案例均待动态验证。
- 非阻断的 SRAM 本地实例建议没有纳入本轮两项定向修正，原通用推演和边界保持。

## 改动与接口

- HTML 正文：boot、clocks、runtime、reset、configuration、evidence；对应根 HTML 用原 build_site.py 更新，锚点保留。
- Markdown：`software/RUNTIME_AND_DEBUG.md`、`configuration/RECIPES.md`、平台 ROM 专题和学习目录 README。
- 浏览器脚本追加三个配置案例的桌面/手机截图；截图名加 anchor，避免同一 configuration 页三个截图相互覆盖。
- 证据目录：[review-fixes-20261007](../learning/evidence/review-fixes-20261007/)；input.json 为输入保护快照，sources.json 为14项定向源码哈希。
- 无硬件配置/profile/地址/中断/位宽变更；原 sw、RTL、依赖、filelist、旧图和历史证据未改。未提交/推送。
- 同步 L01 任务进度、项目简短进度和交接索引，独立评审原件保留。

## 验证证据

工作目录为仓库根；浏览器 Google Chrome 151.0.7922.108。命令如下，重复检查须使用新的输出目录：

```bash
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/check_structure.py --out-dir docs_codex/learning/evidence/review-fixes-20261007/structure
python3 docs_codex/learning/scripts/preview_structure_site.py --out-dir docs_codex/learning/evidence/review-fixes-20261007/browser
git diff --check
```

- [结构报告](../learning/evidence/review-fixes-20261007/structure/checks.txt)：退出0，54 HTML、2833 本地链接/资源、71 SVG XML、613 Markdown链接/锚点；标题/TOC/sidebar/上下章、373项迁移、875历史文件、728备份保护通过。
- [临时生成与保护比较](../learning/evidence/review-fixes-20261007/generation-protection.json)：复制 scripts/content 到新临时目录，运行副本 build_site.py，54 HTML 与工作区逐字节一致；本轮未变更图表，因此未重跑全部 SVG 生成器。14项源码哈希一致。该保护快照在必要共享索引更新前记录，最终保护复核另见 protection-final.json。
- [浏览器报告](../learning/evidence/review-fixes-20261007/browser/browser.txt)：退出0，34主页面桌面/手机，7页禁用脚本，199旧书签，新增三配置案例双尺寸检查；无页面级溢出、资源加载失败或JS异常，54 HTML哈希结束时未变。
- 人工查看当前桌面 Platform ROM 表、手机 AXI RT 小节、桌面 Router 小节截图；所看范围无明显文字遮挡或布局异常。
- 收尾再执行 read-only 结构检查，结果见 `structure-final/checks.txt`；其 Markdown 数量可因交接/索引链接增加而变化。
- 未执行软件构建、RTL 编译/仿真、综合、板测或 ASIC 实施。本轮网页通过不替代三个案例的目标运行。

## 决策与下一步

1. 评审者只需对照 R1 三种栈责任和 R2 三个独立场景复核，原已通过机制无需全量重审。
2. 后续 V01/S01 在实际环境处理已有启动/清单/iDMA缺口，再按案例记录输入、超时、状态及结果。
3. Router 的独立配置、测试程序与激励仍是后续实施项，不将静态方案记为已实现。

最少输入：本交接、独立评审记录、boot/configuration 正文及 sources.json 中的定向源码。共享索引记录本轮文档修正，不关闭 S01-B01 或其他硬件验证待办。
