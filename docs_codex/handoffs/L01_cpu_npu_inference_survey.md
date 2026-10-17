# L01 / CPU＋NPU 模型推理体系调研

## 修改记录

| 日期 | 角色 / 输入版本 | 修改与验证摘要 |
|---|---|---|
| 2026-10-16 | L01 文档与图稿作者；`mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8` | 按用户确认计划交付七组案例、LLM 分析、当前工程映射、四图及原生 PPTX；仅文档/图稿验证 |
| 2026-10-16 | L01 系统环境补充；同一分支与 HEAD，以上交付未提交 | 按用户反馈增加裸机/RTOS/Linux 与推理软件的职责区分、七组实际环境归类；纠正 llm.npu 实测范围 |

## 结果与范围

- 正式专题：[CPU＋NPU 模型推理体系调研](../engineering/CPU_NPU_Inference_Systems_Survey.md)，初次交付约 6200 个中文字，系统环境补充后约 7600 字；[图稿与复现入口](../diagrams/2026-10-16_cpu_npu_inference/README.md)。状态：文档与图稿交付，硬件和软件实施未启动。
- 按授权新增专题、图稿目录和本交接，工程索引仅增加一行；没有更改既有 OS/一致性/GB 专题、RTL/sw、配置、地址、IRQ、filelist 或依赖，未提交 Git。
- 初始工作区已有工程索引/软件接口交接修改及多组未跟踪文档和图稿；[输入快照](../diagrams/2026-10-16_cpu_npu_inference/evidence/input.json)记录 288 个既有文件及相关源码哈希。未启动子 Agent。

## 结论等级与接口

- **官方资料确认**：七组案例分别说明模型产物、调用链和数据管理；来源版本、访问日期与证据缺口在正文和来源清单中。不把浮动主线版本当成历史论文测量版本，不把 prefill 结果当成 decode 性能。
- **本地源码确认**：Ara 经现有失效过滤、宽度转换接主 Xbar；向量 profile 和 Linux SDK 规则存在。现有源码不是新增 NPU/GB 或 Linux 运行验收。
- **现行需求对照**：采用 2026-10-16 共享数据代理要求，与 DDR–GB 搬运职责分开；未重绘项目拓扑、冻结一致性选择或设备参数。
- **设计建议**：先固定代表模型及质量/资源目标，再贯通 CPU 参考、单算子、数据交接与完整模型；不定义新 C ABI、寄存器或 ioctl。供 S01/I01/M01/V01 评估，不作为实施授权。

## 初次交付验证证据

工作目录为仓库根。只使用 Python、现有 Chrome 及已安装绘图 skill，不安装模型 SDK、不执行工程构建。

| 检查 | 实际结果与记录 |
|---|---|
| `build_figures.py --out-dir …/evidence/source-03` | 退出 0，生成四张 SVG、46 条连续箭头及布局清单；正式母版与其一致 |
| `render.py --source-dir …/evidence/source-03 --out-dir …/evidence/render-05` | 退出 0；[记录](../diagrams/2026-10-16_cpu_npu_inference/evidence/render-05/browser.json)：无文字越界、框内溢出、文本重叠或文字/连线交叉 |
| 作者逐张查看 PNG | [视觉记录](../diagrams/2026-10-16_cpu_npu_inference/evidence/visual-review.json)：四图连线、中文和语义检查；最终 PNG 与已查看图逐字节一致 |
| 原生导出器 `run.py … --aspect source` | 退出 0，保存后重读；四页、156 个文本对象、46 条原生箭头、1 个虚线对象；[报告](../diagrams/2026-10-16_cpu_npu_inference/export/export_report.json) |
| 来源与链接 | [来源主记录](../diagrams/2026-10-16_cpu_npu_inference/evidence/sources.json)、[补充记录](../diagrams/2026-10-16_cpu_npu_inference/evidence/sources-extra.json)、[外链实际响应](../diagrams/2026-10-16_cpu_npu_inference/evidence/external-links.json)；22 个正文外链全部 HTTP 200，技术结论只使用成功获取且核对过的来源 |
| 正文、SVG/PPTX 结构、相对链接与输入保护 | `validate.py --out-file …/evidence/validation.json` 退出 0，47 项全部通过；除索引外 287 个输入文件哈希一致，索引逐字保留原内容、仅追加一行；[最终检查](../diagrams/2026-10-16_cpu_npu_inference/evidence/validation.json)记录逐项判据与结果 |

过程失败如实保留：首次 Chrome 被沙箱限制，后经自动审批本机渲染；初稿三处连线压字已调整；首次 PPTX 导出发现 SVG ID 重名，已修复；一次 Chrome 端口文件写入竞争已修正。外部资料初次出现限流/404，换用可访问的官方资料，不据失败页面补写事实。

**结构检查通过，Office 显示与编辑未验证。** 未运行 Office、外部模型 SDK、目标模型、RTL 仿真或板测；没有新增性能或硬件一致性验收结论。

## 系统环境补充与纠错

- 授权范围：用户要求补充七组工作的裸机、RTOS、Linux 分类。只修改正式专题与本交接，增加本次证据；工程索引、既有专题、SVG/PNG/PPTX 和生成脚本保持原样。
- 交付：正文 §1.1–§1.3 补充承载环境、Runtime/TFLM、UMD/KMD 和设备固件的层次关系，逐项列出七组案例的实际路径，并对照一次 NPU 提交在三类环境中的责任落点。Android 与普通 Embedded Linux、开发主机与目标端、proxy kernel 均单独界定。
- 纠错：正文 §3.3、§4 与图 4 图注以 llm.npu 论文 §4/§4.1/§4.6/§5 为准，替代初版“实际 CPU/GPU/NPU 协同”的表述。实测为 Android 13 上 CPU＋NPU、CPU decode；GPU 协同仅模拟，图 4 下半仍表示设计归纳。
- 来源：[系统环境核对](../diagrams/2026-10-16_cpu_npu_inference/evidence/os-classification/sources.json)。本次四个新增外部链接经网页工具打开并核对正文；未将网页读取成功记作目标环境实测。
- 输入与保护：[修订前快照](../diagrams/2026-10-16_cpu_npu_inference/evidence/os-classification/input.json)记录 337 个文件哈希，并保存两份被改文档的原文；[本次检查](../diagrams/2026-10-16_cpu_npu_inference/evidence/os-classification/validation.json)记录本地链接、锚点、修改范围和图稿哈希。上节 47 项为初次交付的历史记录，本次未重渲染或重导出图稿，未新增 Office/SDK/工程测试。

## 未关闭项与最小下一步

1. 用户/I01/S01 确认代表模型、精度、上下文、质量、延迟和资源预算，再选择后端；当前建议不是 OS/IP 选型决定。
2. 对闭源方案内部调度、真实 CPU 回退及 KV 布局，仍需对应版本资料或实测；本次资料不足处已注明。
3. 由后续实施任务验证 Ara 上下文、NPU 命令/完成、GB 所有权、缓存和失败恢复。新任务从正式专题 §6–§7 与现行 IP/DDR 契约继续，无需重跑历史实验。

没有应据此更新为“工程已实现”的共享事实，未改写 `PROJECT_STATE.md` 或 `AGENT_TASKS.md`。
