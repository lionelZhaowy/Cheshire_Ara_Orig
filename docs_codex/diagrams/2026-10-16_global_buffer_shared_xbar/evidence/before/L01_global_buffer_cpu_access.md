# L01 / CPU 与 Global Buffer 接入比较

## 修改记录

| 日期 | 角色 / 输入 | 修改与验证摘要 |
|---|---|---|
| 2026-10-15 | L01 分析与图稿作者；`mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8` | 按用户确认计划及追加 Markdown 要求，交付正式分析和两张工业风格 SVG/PNG、两页原生 PPTX；仅文档与图稿 |

## 结果与负责范围

- 正式内容：[CPU 接入 GB](../engineering/Global_Buffer_CPU_Access.md)；[图稿与复现](../diagrams/2026-10-15_global_buffer_cpu_access/README.md)。状态：文档与图稿交付完成，硬件方案未冻结、未实施、未验证。
- 用户选择的分析输入是“小结果、灵活处理”；建议保留 64-bit 主机入口，反复排序时复制到 CPU 私有工作区。此建议不是用户已经冻结 CPU 接入的决定。
- 用户本轮追加明确要求独立 Markdown；因此新增正式工程参考页。原 `integration.md`、现行 IP/DDR 契约、已有一致性文档及图稿均未修改。
- 本轮只新增上述正式文档、`diagrams/2026-10-15_global_buffer_cpu_access/` 和本交接。生产 RTL/sw、地址、IRQ、profile、清单、依赖和 FPGA 工程无改动；未提交 Git。
- 工作区原有工程索引、软件接口交接修改，以及软件栈/一致性图稿和文档等未跟踪文件全部保护；[输入快照](../diagrams/2026-10-15_global_buffer_cpu_access/evidence/input.json)记录初始状态和哈希。

## 依据与验证

源码核对沿主 Xbar 外部从设备、Ara filter→converter、LLC 前原子适配、CVA6 PMA 消费链进行。依赖源标识为 Ara `2895ba90`、CVA6 `99eac9a6`、AXI `39f5f2d5`，本地文件哈希才是此次实际输入。官方资料和具体源码入口见正式文档，不重复复制论证。

工作目录为仓库根。实际生成、渲染、导出命令完整保存在图稿 README，检查入口及结果如下：

- `build_figures.py --out-dir …/evidence/source-01` 退出 0；初次 `render.py …/render-01` 退出 1，Chrome 本地 socket 受沙箱限制，日志保留。
- 经环境审批执行本地 Chrome 到 `render-02`，布局检查退出 1，发现 NPU→GB 连线穿过分区标题；没有把该批次标为通过。
- 定向修正后 `build_figures.py …/source-02`、`render.py …/render-03` 均退出 0；逐张实际查看两张 PNG，无文本越界、遮挡、连线穿字或端点悬空。
- 原生后端 `run.py --input cpu-isolated.svg cpu-accessible.svg --out-dir export --aspect source`（完整字体选项见 README）退出 0；两页、125 文本、48 原生箭头，保存重读通过。
- `validate.py --out-file …/evidence/validation.json` 的最终结果见[验证报告](../diagrams/2026-10-15_global_buffer_cpu_access/evidence/validation.json)：链接、图形连接、两方案公共布局、PPTX 对象、67 个既有文件及 15 个输入保护；`git diff --check` 一并检查。

Office 显示/编辑未实测，原生箭头未绑定模块端口；不承诺拖动模块自动重连。未执行目标软件/RTL 编译、展开、仿真、综合、板测或 ASIC 验收。

## 未关闭项与下一步

1. 用户/M01/I01 评审 CPU 是否接入，再提供候选表规模、GB 组织和接口、地址与仲裁目标；图稿不冻结容量、频率或 SRAM 端口。
2. S01/V01 按正式文档比较 Ara→SPM 与 CPU 直访/私有复制，验证所有权、错误、迟到写和并发干扰；Ara B 错误与 iDMA 控制接口缺口保持开放。
3. GB 非缓存直访与 DDR 旁路一致性分别评审；不把另一对话的硬件一致性建议视为已实现能力。

共享状态、任务表和已有未提交工程索引本轮保持不动，没有工程实现状态变化。若协调者汇总导航，可增加正式文档入口；本交接已保存本次文档进展和输入身份。
