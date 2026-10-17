# L01 / 边缘大模型推理的 OS 选择

## 修改记录

| 日期 | 角色 / 输入 | 修改与验证摘要 |
|---|---|---|
| 2026-10-15 | L01 文档与图稿作者；`mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8` | 按用户确认计划整理 OS 比较专题、两张图及原生 PPTX；文档/图稿检查见下文，不新增目标运行证据 |

## 结果与范围

- 正式内容：[边缘大模型推理的操作系统选择](../engineering/Edge_LLM_OS_Selection.md)；图稿和复现入口：[说明](../diagrams/2026-10-15_edge_llm_os/README.md)。状态：文档与图稿交付。
- 使用 `svg-pptx-diagrams-native` 和 `industrial-svg-pptx`，两图分别为三种执行环境的软件栈与候选 NPU/GB 任务协作；不创建新任务 ID，不启动子 Agent。
- 负责文件：新专题、新图稿目录、本交接；现有 `engineering/README.md` 只增补一行入口。现有一致性文档、图稿、生产 RTL/sw、地址、配置、filelist 和依赖未修改；未提交 Git。
- 初始工作区已有工程索引/接口交接修改，以及软件栈、一致性、GB 访问图稿等未跟踪内容，均保留；[输入快照](../diagrams/2026-10-15_edge_llm_os/evidence/input.json)保存身份和哈希。

## 结论等级与接口

- **源码确认**：本地向量 profile 含 MMU/S/U/V 配置；Ara 官方文档及 SDK 提供 Linux 路线，普通/V 配方分别请求 v5.10.7/v6.5。它们不是当前镜像或运行验收。
- **官方资料对照**：Gemmini、Ethos-U、Jetson 展示不同的软件组织；来源在专题各节，不将外部平台能力直接套到本工程。
- **设计建议**：保留裸机基线，优先评估精简 Linux 应用；模型固定、资源与实时约束明确时优先考虑 RTOS。产品 OS/模型/运行时仍未由用户选定。
- **数学算例**：1B 4-bit 理想权重载荷 500 MB；假设配置 KV 为 192 MiB。两例不是同一个已选模型，不作为产品容量决定。
- 无新增 C API、寄存器、IRQ 或硬件连接契约；供 S01/I01/M01/V01 后续评估。

## 验证证据

工作目录为仓库根；完整产物与输入哈希见图稿目录。实际命令及结果：

| 检查 | 结果 |
|---|---|
| `build_figures.py --out-dir evidence/source-01` | 退出 0；2 张 SVG、28 条连续箭头 |
| `render.py --source-dir evidence/source-01 --out-dir evidence/render-01` | 退出 1；Chrome 本地套接字被沙箱限制，日志保留 |
| 同输入渲染至 `evidence/render-02` | 经环境审批在沙箱外执行，退出 0；两图排版检查通过，作者逐张查看实际 PNG |
| 原生导出 `run.py --input software-stacks.svg inference-flow.svg --out-dir export --aspect source …` | 退出 0；2 页、119 文本、28 原生箭头、8 虚线对象；保存重读及 XML 核对 |
| `validate.py --out-file evidence/validation.json` | 退出 1；文档/图稿检查通过，检测到本任务未写入的独立 GB 图稿脚本变化；原始[报告](../diagrams/2026-10-15_edge_llm_os/evidence/validation.json)保留 |
| `validate.py --out-file evidence/validation-final.json` | 结果见[最终报告](../diagrams/2026-10-15_edge_llm_os/evidence/validation-final.json)：产物检查通过，既有输入全一致为 false；仅将已记录的外部变化单独分类，不替换原输入基线 |

SVG/PNG 使用文泉驿正黑；PPTX 使用 Microsoft YaHei，并用本机字体测量。原生连接器未绑定模块端口，不承诺移动模块自动跟随。**Office 显示与编辑未验证。** 文档检查不能解释为模型运行或硬件验收；未编译应用、未构建 OS、未仿真、未板测。

并行变化：`docs_codex/diagrams/2026-10-15_global_buffer_cpu_access/build_figures.py` 的输入哈希与结束哈希不同，作者身份未判断；本任务的写入操作未涉及该路径。[变化记录](../diagrams/2026-10-15_edge_llm_os/evidence/external_change.json)保留观察，不回滚、不重设快照。工程索引则通过删除本任务新增一行后与原文逐字一致的检查。

## 未关闭项与最小下一步

1. 用户/S01/I01 明确代表模型、精度、上下文、并发、更新频率和时延约束，再比较完整内存预算与运行时适配。
2. 按既有官方路径验证 OS/RVV，按现行契约独立验证 DDR/GB/NPU 和缓存交接；不因本篇交付关闭 Platform ROM、iDMA 或向量上下文缺口。
3. 若后续授权实施，V01 采用同模型/同硬件基线，记录质量、首 token/逐 token/尾延迟、内存、流量、能耗和失败恢复。本文仅给出验收需求。

本轮不改变生产事实和任务实施状态，不重复修改共享状态/任务表；本主题交接与工程索引承担文档导航。
