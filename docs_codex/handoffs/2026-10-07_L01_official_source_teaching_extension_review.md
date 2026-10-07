# L01 / 官方资料与源码教学扩充独立评审

## 基本信息

- 日期：2026-10-07；角色：独立评审者。
- 用户授权范围：了解工程上下文，按 `2026-10-07_L01_official_source_teaching_extension.md` 审查新 HTML 教材。只读教材及生产实现，新增本记录与独立检查证据。
- 状态：评审完成；建议定向修改后复审，不将本轮教学要求标为全部闭环。
- 开始 HEAD：`5ddec4fb4e982b460b12c3f3587523807602d5d4`，分支 `mp/ara-pulp-v2`；工作区已有实施交接列出的文档修改及未跟踪文件。
- 评审过程中，其他操作将 HEAD 推进到 `f01487c2f3c3e990b515bff813227b97049976a3`（“结合官方文档进行更新”）。本评审未执行提交、切换分支或还原。收尾核对原浏览器报告的 152 项输入、54 个 HTML 和 48 项来源哈希全部一致，因此下述结论仍针对同一内容。新提交也纳入了本轮先生成的 structure 检查目录；此事实不改变检查的执行主体和证据等级。
- 负责路径：本交接及 `learning/evidence/review-teaching-20261007/`。共享状态、任务表和索引交 C00 串行汇总。

## 本轮结果

整体上，新增内容已经将配置、互连、软件分层及 ASIC 责任从资料索引扩充为因果解释；没有发现把网页检查冒充 RTL/板测通过的表述。核心机制多数与当前源码一致。保留以下两个 P2 项，其中 R1 是新增说明的技术前提遗漏，R2 是上一轮明确教学要求尚未完成；不是要求重写整站。

### R1 / P2：Platform ROM 分支表遗漏“内部 LLC 存在”的前提

- 位置：`learning/content/boot.html:12`（`boot.html#platform-rom`）；关联 `content/clocks.html:28`。
- 问题：表格只以 `Bootrom=1, PlatformRom≠0` 为条件，便断言“自带 ROM 建立 SPM/栈后……调用”。实际上这两个字段不保证内部 SPM 存在。对于 `LlcOutConnect=1, LlcNotBypass=0` 的旁路组合，ROM 仍可调用非零平台入口，但不会建立内部 LLC/SPM。
- 源码证据：`hw/bootrom/cheshire_bootrom.S:59–63` 检查 `HW_FEATURES.llc`，为零直接跳到 `_prom_check_run`；`:82` 明确指出只有存在 LLC 才有内部 SPM。`:53` 加载链接栈指针只是写寄存器，不能证明指针所指存储可写。`hw/cheshire_soc.sv:496` 的 LLC 实例条件为 `LlcOutConnect && LlcNotBypass`；`:543` 是旁路分支。`hw/bootrom/cheshire_bootrom.ld:12` 提供默认栈地址。
- 影响：读者按表格裁掉 LLC 后，可能直接在平台入口调用依赖栈的 C 初始化程序，首次保存返回地址/局部变量时就访问不存在或未就绪的存储。另一个方向的误读是认为 Platform ROM 必须依赖内部 LLC，而忽略平台可提供替代存储的契约。
- 最小修改：给表格的 SPM/栈保证加上默认保留 LLC 的适用条件，并明确无内部 LLC 时 ROM 跳过该初始化，平台须提供可用存储/栈，或先执行不依赖栈的早期代码。clocks 章的 LLC/SPM 描述也限定为当前保留 LLC 的启动基线。不要把 `Bootrom=0` 分支的责任说明当成对 `Bootrom=1`、无 LLC 分支的替代。
- 验收：读者分别推演保留 LLC、旁路 LLC、关闭内置 Boot ROM 三种情况，能指出谁保证第一次栈访问安全；不需要本轮修改生产 ROM 或实现新启动机制。

### R2 / P2：AXI RT、CLIC、Router 配置案例仍未按上一轮要求拆开

- 位置：`learning/content/configuration.html:38–40`（`configuration.html#configuration-candidates`）。
- 问题：新增“合法性分层”解释有效，但用途表仍把 `AXI RT / CLIC / Router` 合为一行，仅写“可选 SoC 分支 + CPU 能力 + 生成尺寸”。读者仍无法从这一行选择其中一个用途并说明完整配置、启动软件及验收差异。这是原有缺口延续，不是新增技术错误。
- 需求依据：前序 `2026-10-07_L01_configuration_teaching_depth_review.md` 第 3 节明确要求拆开这些场景，给出 profile、SoC 差异、生成规模、启动/软件及最小验证；不要求穷举或运行所有组合。新增段落建议读者保留配置记录，但没有代替教材提供至少一份完整示范记录。
- 实现依据：`target/sim/src/tb_cheshire_pkg.sv::gen_cheshire_rt_cfg` 只设 `AxiRt=1`，`gen_cheshire_clic_cfg` 只设 `Clic=1`，四项选择中没有专用 Router 配置。`hw/cheshire_pkg.sv::gen_cva6_cfg` 将 CPU `RVSCLIC` 覆盖为 `Cfg.Clic`。三者既不是同一入口，也不是相同软件契约。`configuration/RECIPES.md` 的入口矩阵已有部分数据，但尚不能使这一 HTML 用途行独立完成教学任务。
- 最小修改：拆成三个简短案例，每个写明相对 DefaultCfg 的差异、CPU 有效配置是否受影响、生成 IP/软件编号的依赖、启动或 handler/驱动要求、当前阻塞及一个最小验收场景。对未知条件明确留待验证，不虚构完整合法配置；可复用现有事实及专章链接，无需增加 Lab。
- 验收：读者能解释“选择 SELCFG=1 不等于启用 CLIC”“SELCFG=2 不等于启用 Router”“Ara+RT 不是两个现有测试结果的简单合并”。

### 非阻断建议：给 SRAM 推演增加一个实际消费者落点

`future.html#sram-example` 的 k+1/k+2、写掩码和碰撞说明正确，也明确标为通用假设。作为 ASIC 入门解释可接受。不过，相比其他新增节，这里仍缺一条可跟读的本地实例路径。后续可从 LLC 数据阵列或 Ara VRF 任选一处，列出实例、存储抽象及读数据有效周期的消费者，再与假设宏比较。无需选定供应商或实现适配；本项不作为当前技术错误。

## 按交接要求复述五条过程

| 读者任务 | 本轮独立核对与评价 |
| --- | --- |
| CPU 配置到实例 | 唯一 profile 的 `cva6_cfg` → `gen_cva6_cfg` 平台覆盖 → `build_config` 派生 → CVA6/SoC generate。PMP 原值 8 被默认覆盖为 0，CLIC 由 Cfg 覆盖；本地 `EnableAccelerator=RVV`。`Cfg.Ara` 另行控制 Ara 实例，软件还需 VS/FS。新增表可解释原值与有效值，不把 RV32 文件存在等同于 Cheshire 支持。通过；配置用途闭环仍见 R2。 |
| UART 地址到设备 | `0x03002014` 是 UART 基址加 LSR 偏移 20；CPU 属性决定 MMIO 行为，第一层 AXI 规则送 Reg 桥，第二层选 UART，再按偏移访问。核对 `gen_axi_out/gen_reg_out` 和 `sw/include/dif/uart.h`、`sw/lib/dif/uart.c`；本地驱动使用 reg8。PMA/PMP/MMU 与路由职责没有混同。通过。 |
| LLC 缺失到外存 | 默认 64 B/行、16 KiB/way、128 KiB 总容量正确；按行拆分 → 查标签 → 必要时旧地址写回 → refill → 原访问。额外查看 `src/eviction_refill/axi_llc_w_master.sv`，其确实等待 B 握手才继续送描述符；SPM 直接寻址与全 SPM 时外存旁路分开。这里不能由握手推出所有错误路径已验证，教材未作此承诺。通过。 |
| ROM 到 main | 分清复位 ROM、NOR 镜像、SPM 执行位置；JTAG 的 ELF 段/DPC 路径与介质 raw/GPT 路径分别解释。应用 crt0 清 BSS、设置 FS 并执行浮点初始化，VS 由向量入口另设；JTAG 的 SPM 标志不保证继承栈已经建立。非零平台钩子的返回缺陷及上游修复边界记录正确。默认保留 LLC 路径通过；泛化到无 LLC 时须修 R1。 |
| SRAM 宏替换 | 从端口、深度、宽度扩展到延迟、掩码、冲突和测试脚，说明多一拍数据会错配当前请求，整字写宏可能需要受控读改写。正确区分通用推演和实际工艺交付。概念通过；本地跟读例子可增强。 |

另外核对了 `AxiMap` 为常量、7→9 发起者导致来源位 3→4、输入 ID=2 时目标 ID=6，以及扩展 master/slave 端口的请求方向；未发现新增说明与源码不符。DDR 初始化代码/栈必须先有可用存储、VRF 不属于 NPU 可寻址共享窗口、未来旁路并非自动一致等边界保留。

## 官方来源与版本核对

本轮实际打开了 [Cheshire Architecture](https://pulp-platform.github.io/cheshire/um/arch/)、[SoC Integration](https://pulp-platform.github.io/cheshire/tg/integr/)、[Software Stack](https://pulp-platform.github.io/cheshire/um/sw/)、[CVA6 Parameters](https://cva6.readthedocs.io/en/latest/01_cva6_user/Parameters_Configuration.html) 和 [CVA6 PMA](https://cva6.readthedocs.io/en/latest/01_cva6_user/PMA.html)。在线资料持续更新，不作为本地版本替代。

Cfg 派生方式和未用输入绑值与官方集成说明一致；在线扩展数量概述与参数表的差异确实存在。PMA 的静态属性与核内访问行为相符。具体 LLC 机制以随依赖保存的官方设计说明及 RTL 为准。Platform ROM 修复提交用本地 `git show` 确认，未执行 cherry-pick 或 ROM 重生成。

## 验证证据

工作目录为仓库根。本轮重新执行：

```bash
python3 docs_codex/learning/scripts/check_structure.py --out-dir docs_codex/learning/evidence/review-teaching-20261007/structure
git diff --check
```

- 两项退出码均为 0。[结构日志](../learning/evidence/review-teaching-20261007/structure/checks.txt)：54 HTML、2805 本地链接/资源、71 SVG XML、602 Markdown 链接/锚点；373 项迁移、875 历史文件及 728 备份保护通过。
- 本轮结构命令未请求 `--check-generated`。另用 Python 标准库在新临时目录复制 scripts/content，仅运行该副本的 `build_site.py`，生成 34 主页面+20 兼容页；54 个 HTML 与当前工作区逐字节一致。没有在原站执行生成器，也没有重生成全部 SVG。[独立比较结果](../learning/evidence/review-teaching-20261007/independent-checks.json)。
- 原 browser-final 的 152 项输入、54 HTML，以及 sources.json 的 48 来源文件，经 SHA-256 复核均未漂移。原浏览器检查可追溯至当前内容；本轮没有重新运行 Chrome 自动检查。
- 人工查看留存截图：三张 `teaching-*.svg`、390 宽集成接口表、1440 宽 Platform ROM 表。所看范围未发现文字遮挡或明显溢出；不声称人工审读了全部页面截图。
- 未执行软件构建、RTL 编译/仿真、板测、综合、ASIC 提取或实现。

## 改动与接口

- 新增本独立评审及 `review-teaching-20261007/` 检查产物；未修改正文、生成 HTML、SVG、生产 RTL/sw、配置或接口。
- 未由本评审执行 Git 提交或推送。工作区中的外部提交变化见基本信息。
- 既有 S01-B01、DMA 控制位宽和 Ara 错误处理等待办不因本次网页审查而关闭。

## 决策与下一步

1. L01 修改者定向处理 R1、R2，并同步由正文生成的 HTML；不在本次评审中改生产实现。
2. 用新的输出目录检查结构/生成一致性，必要时只补受影响页面浏览器检查；保留本次与原有证据。
3. 复审对照两项验收条件闭环；无需重做已通过的五条机制说明。
4. C00 可汇总“官方来源教学扩充独立评审完成，有两项定向待改”；不能将其记为硬件验证完成。

最少继续输入：本记录、受影响的 `content/boot.html`、`content/clocks.html`、`content/configuration.html`，及上述定向源码/前序教学要求记录。
