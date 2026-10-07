# L01 / 官方资料与本地源码的教学解读扩充

## 基本信息

- 日期/对话标识：2026-10-07；L01 修改者对话。
- 用户授权：用户明确同意从评审者转为修改者；提供的网页版问答只作为解释深度示例，要求扩展到硬件架构、ASIC 集成等官方章节，并结合源码解读。
- 状态：文档实施与轻量验证完成，交独立评审；生产缺口修复和目标运行不在本轮范围。
- 输入分支/提交：`mp/ara-pulp-v2`，`5ddec4fb4e982b460b12c3f3587523807602d5d4`。
- 输入工作区：`AGENTS.md`、`PROJECT_STATE.md`、`AGENT_TASKS.md`、`handoffs/README.md` 已修改；Platform ROM 专题、其他交接/图表/tools 等未跟踪。均保留，输入状态和 1084 项哈希见 [input.json](../learning/evidence/teaching-20261007/input.json)。
- 负责范围：`learning/` 正文、生成 HTML、三张新 SVG、维护说明、现有检查脚本的最小扩展；配置/软件 Markdown 追加解释；本独立交接。不修改生产 RTL/sw、依赖、filelist、地址图或用户原有协作记录。不启动子 Agent。

## 本轮结果

已扩充 17 个教学章节及首页/证据页，共 19 个 HTML 正文源，正文净增约 1.83 万文本字符（去 HTML 标签的粗计，不作为质量验收）。保留七篇/30 章、34 个主页面、20 个兼容页面、六项实验和现有 UI。

| 教学范围 | 新增解释与具体推演 | 入口 |
| --- | --- | --- |
| 系统架构 | 同一模块的控制、主动数据、事件三类接口；Crossbar 端口名与对端角色；SoC IP 与完整芯片的责任 | [architecture](../learning/architecture.html#port-roles) |
| CVA6 / SoC / 软件配置 | CPU 配置族、两 profile 原值/有效值；类型范围、结构约束、启动契约和动态验证四层；端口/ID/生成器的联动 | [cva6](../learning/cva6.html#configuration-families)、[configuration](../learning/configuration.html#legality-levels) |
| 地址与互连 | UART 地址逐层解释；PMA/PMP/MMU；常量 AxiMap 与运行时控制区别；新增两个发起者和一个 Reg 控制口的推导 | [address-map](../learning/address-map.html#address-translation-example)、[interconnect](../learning/interconnect.html#configuration-versus-registers) |
| 存储与 DDR | LLC 按行拆分、标签、脏行替换和填充；SPM 直接寻址；回收栈所在 way 的风险；DDR 出口/控制器/PHY 分工与初始化依赖环 | [memory](../learning/memory.html#llc-transaction)、[ddr](../learning/ddr.html#platform-contract) |
| ASIC 平台 | 启动安全时钟、Platform ROM 与运行时调频；时钟/复位/电源域分别划分；SRAM 延迟与字节写适配；PAD/PLL/ROM/DDR/DFT 交付 | [clocks](../learning/clocks.html#boot-and-runtime-frequency)、[future](../learning/future.html#resource-mapping) |
| 软件与启动 | 应用/库/DIF/HAL/启动职责；分节原因；原 Make 选项；C→ELF→装载→执行；ROM/介质/SPM、平台钩子三分支、ZSL/OpenSBI/DTB | [runtime](../learning/runtime.html#software-stack)、[build](../learning/build.html#software-options)、[boot](../learning/boot.html#platform-rom) |
| 系统扩展 | 官方 Cfg/type 宏与扩展端口方向；VRF 与共享张量区别；LVDS→ISP→NPU/Ara→回收的一次任务推演 | [integration](../learning/integration.html#official-instantiation)、[sharing](../learning/sharing.html#vrf-versus-shared-memory)、[accelerators](../learning/accelerators.html#frame-walkthrough) |

同步追加 7 个现有 Markdown：`configuration/{README,CVA6,CHESHIRE,RECIPES}.md`，`software/{README,BUILD_AND_SDK,RUNTIME_AND_DEBUG}.md`。保留历史正文作为前缀，各新增节有独立日期/锚点。`learning/README.md` 和 `OFFICIAL_SOURCES.md` 记录维护方法及官方章节落点。

新增 SVG：`teaching-config-contract.svg`、`teaching-code-to-execution.svg`、`teaching-asic-responsibilities.svg`。均为原生可编辑 SVG/text，标注教学示意，独立维护，不改旧图或生成器。不使用外部 CDN。

解释方法为“定义职责 → 解释原因 → 推演过程 → 对照配置/源码 → 给出验证条件”。加入 8 个折叠自测，不新增重复 Lab。已有外设寄存器章节、RVV 编程实验和数值/失败判据保留。

### 技术结论与证据等级

- **源码静态确认**：当前 CPU 88 用户字段、SoC 113 字段；`DCacheType` 大小写据 `config_pkg.sv` 修正网页原拼写；字段枚举不等于所有组合已验证。
- **源码静态确认**：`gen_cva6_cfg` 的 PMP/CLIC/接口覆盖，`build_config` 的派生；`AxiMap` 为常量；7→9 发起者使来源位从 3→4，原输入 ID=2 时 Crossbar 目标侧由 5→6。
- **官方契约与本地差异**：非零 Platform ROM 正常返回落入 `boot_next_stage` 的缺口继续保留。`git show 9b4c222...` 可读上游修复（PR #187），`git merge-base --is-ancestor ... HEAD` 返回 1；不在当前祖先链。在线 commit 页抓取失败，修复依据来自本地 git 对象，未擅自 cherry-pick/重生成生产 ROM。
- **官方与本地版本边界**：在线扩展端口概述 16 与表格 0..15、本地 4 bit 字段；在线 RDL/PeakRDL 与本地 HJSON/REGTOOL。当前实现以本地消费者为准。
- **未来方案**：ASIC 宏、PLL、低功耗、NPU/ISP/LVDS、DDR 适配。没有编造供应商寄存器、合法频率、电源域或动态通过记录。
- 本轮定向来源文件及哈希见 [sources.json](../learning/evidence/teaching-20261007/sources.json)，48 项；官方来源及对应网页节见 [OFFICIAL_SOURCES](../learning/OFFICIAL_SOURCES.md#teaching-20261007)。

## 改动与接口

- 正文源：`learning/content/{architecture,cva6,configuration,clocks,reset,power,address-map,interconnect,memory,ddr,runtime,build,boot,sharing,integration,accelerators,future,index,evidence}.html`。
- 根 HTML 由原 `build_site.py` 生成。该脚本只调整当前证据锚点和页脚日期，目录元数据/旧锚点迁移表不变。
- `preview_structure_site.py` 增加 `teaching-*.svg` 检查及四个新增重点小节的桌面/手机截图；不改 CSS/JS 或网站框架。
- 产物/报告：`learning/evidence/teaching-20261007/`。`input.json`/`sources.json` 是独立快照，浏览器报告包含所测 54 HTML 的哈希，结束时核对未变化。
- 本轮未修改任何硬件配置、profile、宏、地址、中断、位宽或软件可执行代码；未提交 Git、未推送。
- 教材可离线阅读；源码链接需要完整仓库。新 ASIC 图是规划关系，不是实际电源意图/物理设计。

## 验证证据

工作目录为仓库根；Python 使用当前环境，浏览器为 **Google Chrome 151.0.7922.108**。

最终可重现命令（再次执行时换用不存在的新输出目录）：

```bash
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/check_structure.py --check-generated --out-dir docs_codex/learning/evidence/teaching-20261007/structure-final
python3 docs_codex/learning/scripts/preview_structure_site.py --out-dir docs_codex/learning/evidence/teaching-20261007/browser-final
git diff --check
```

- 构建器退出 0：34 主页面、7 篇、20 兼容页。
- [最终结构检查](../learning/evidence/teaching-20261007/structure-final/checks.txt)退出 0：54 HTML，2805 项本地链接/资源，71 SVG XML，581 Markdown 链接/锚点；页面标题/H1/TOC/sidebar/上下章一致；373 项迁移；临时副本生成的 126 个产物与当前一致。
- [最终浏览器检查](../learning/evidence/teaching-20261007/browser-final/browser.txt)退出 0：34 主页面在 1440×1100 / 390×844；7 页禁用脚本；199 条跨页旧书签；图表交互、寄存器查询、模型计算器；新旧重点 SVG 边界；4 个新增节的两种尺寸截图。无页面级横向溢出、加载失败、JS 异常或 HTTP(S) 资源请求；54 HTML 哈希前后相同。
- 人工实际查看三张新增 SVG、桌面 CVA6 页、手机首页、桌面 Platform ROM 表、手机集成接口表。初看 ASIC 图箭头标签过近，调整后再次查看最终图；执行流程图补充继承栈前提。最终截图留在 browser-final，未将仅自动检查的全部页面称为逐页人工审读。
- [内容保护检查](../learning/evidence/teaching-20261007/preservation.json)：全部原代码块、表格、图、Quiz、source 块保留（仅规范化 DcacheType 字段拼写）；配置/软件 Markdown 历史正文保留；输入中旧资产、证据、原协作文件、源码没有越界变化。主检查另确认 875 个历史证据/示例/资产、728 个备份文件未变。
- `git diff --check` 退出 0。48 项定向源码哈希未变。
- 第一次 `structure-1` 的 `--check-generated` 在沙箱启动 Chrome 时缺少 DevToolsActivePort 而失败；记录保留，未伪装通过。自动批准沙箱外的同一文档检查后，structure-2 与 structure-final 通过。browser-1 为图表微调前的成功记录，browser-final 为最终版本。
- **未执行**：软件构建、RTL 编译/仿真、综合、板测、性能测试、ASIC 提取/实现。

## 决策与下一步

用户已确认：由本对话实施，另一对话独立评审；从示例问答所体现的解释深度扩展到官方硬件/ASIC 章节。此前确认的 Platform ROM 早期平台初始化方向、固定配置和静态清单方向保留。

后续仍需真实 IP/平台输入：PLL 安全切换和寄存器、工艺 SRAM/ROM 语义、DDR 控制器/PHY 初始化与就绪、完整低功耗/测试约束。现有 Questa/VCS profile/decoder、生成器尺寸及启动/HAL 缺口不因文档扩充而消失。

评审 Agent 最小步骤：

1. 阅读本文和 `OFFICIAL_SOURCES.md#teaching-20261007`，定向审读配置、互连、存储及 ASIC 章节，避免仅按字数/目录评价。
2. 用 `sources.json` 中本地路径核对有效配置、端口方向、LLC 和 Platform ROM 的解释，重点检查是否把必要条件写成充分条件。
3. 按读者任务复述一次“CPU 配置到实例”“UART 地址到设备”“LLC 缺失到外存”“ROM 到 main”“SRAM 宏替换”过程，指出仍缺的定义、因果或前提。
4. 查阅最终浏览器截图/报告；如需复跑，用全新输出目录，不覆盖历史证据。问题交独立评审记录，不同时覆盖实施文件。

需要 C00 合并到共享索引：L01 本轮完成的 17 章解释扩充、7 个 Markdown 和最终文档检查；链接本交接；保留生产验证缺口与原角色/范围边界。共享状态/任务表/交接 README 在开始时已有其他对话修改，本轮未覆盖。
