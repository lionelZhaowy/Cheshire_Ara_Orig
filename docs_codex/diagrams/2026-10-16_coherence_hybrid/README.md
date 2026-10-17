# 软硬件协同缓存维护：正式图稿

2026-10-16，L01。[规划正文](../../engineering/Cache_Coherence_Architecture.md) · [综述正文](../../engineering/CPU_NPU_Cache_Coherence_Survey.md) · [规划阅读预览](architecture-preview.html) · [综述阅读预览](survey-preview.html) · [六页原生 PPTX](export/diagrams.pptx)。

当前规划采用软件交接、L1D／LLC 硬件范围维护和统一经 DDR 的数据路径。本目录替代此前图稿中的“逐事务 I/O 一致性优先推荐”状态，原目录、原始图与验证证据保留。

| 页 | 用途 | SVG 母版 | PNG 预览 |
|---|---|---|---|
| 1 | 系统图：原布局与三口 DDR，更新范围维护职责 | [system](figures/system.svg) | [system](previews/system.png) |
| 2 | 交接流程：提交前维护、设备持有、消费前同步 | [ownership](figures/ownership.svg) | [ownership](previews/ownership.png) |
| 3 | 经 DDR 与缓存直供成本比较；本方案采用左侧 | [data-paths](figures/data-paths.svg) | [data-paths](previews/data-paths.png) |
| 4 | A/B：软件维护与软件触发的硬件范围维护 | [handover](figures/handover.svg) | [handover](previews/handover.png) |
| 5 | C/D：文献中的 LLC 局部协调与 I/O 一致性 | [coverage](figures/coverage.svg) | [coverage](previews/coverage.png) |
| 6 | E/F：分配策略与设备缓存代理；F 为文献背景 | [agent-types](figures/agent-types.svg) | [agent-types](previews/agent-types.png) |

## 布局与技术范围

系统图唯一底图仍是用户认可的 [2026-10-12 工业版](../2026-10-12_industrial_redraw/ddr_interconnect.svg)。本轮复用此前最小增补生成器，仅调整已新增维护模块及控制标签；底图的模块坐标、尺寸、数据连线和 S0/S1/S2 均保留。Ara、NPU、ISP 和搬运器到 GB 的路径经过共享数据代理，LLC 经 S0 到 DDR。

图 2 的箭头表示逻辑阶段依赖，图 3 表示数据通路。图 4–6 采用通用缓存层次解释文献分类，CPU 私有缓存的实际层数以具体平台为准。图 6 中 F 的必要条件是设备缓存参与探测，Gemmini 的 L2 接入位置本身不足以归入 F。

图 3 右侧为接口成本比较；当前方案全部缓存／GB 数据交换经 DDR。软件保持交接范围所有权，硬件负责维护及 DMA 准入；自动阻挡 CPU 违规访问需要额外覆盖 L1 命中路径。原子域接口在系统图中保留为评审项。

机制依据：[RISC-V CMO v1.0](https://docs.riscv.org/reference/isa/v20240411/unpriv/cmo.html)、[Linux 6.5 DMA API](https://docs.kernel.org/6.5/core-api/dma-api-howto.html)、[Cohmeleon v1 §2](https://arxiv.org/html/2109.06382v1#S2)、[AMD PG201](https://docs.amd.com/r/en-US/pg201-zynq-ultrascale-plus-processing-system/Slave-Interface)。项目源码和适用条件集中在规划正文第 5 节。

## 生成与验证

使用 `industrial-svg-pptx` 及其 `svg-pptx-diagrams-native` 后端，无新增依赖。[build.py](build.py)读取已有绘图类和唯一批准底图，输出到新目录。复现示例：

```sh
python3 docs_codex/diagrams/2026-10-16_coherence_hybrid/build.py --out-dir /tmp/coherence-hybrid-svg
python3 docs_codex/diagrams/2026-10-16_cache_coherence/render.py --source-dir /tmp/coherence-hybrid-svg --out-dir /tmp/coherence-hybrid-png
python3 /home/zhaowenyao/.codex/skills/svg-pptx-diagrams-native/scripts/run.py --input /tmp/coherence-hybrid-svg/system.svg /tmp/coherence-hybrid-svg/ownership.svg /tmp/coherence-hybrid-svg/data-paths.svg /tmp/coherence-hybrid-svg/handover.svg /tmp/coherence-hybrid-svg/coverage.svg /tmp/coherence-hybrid-svg/agent-types.svg --out-dir /tmp/coherence-hybrid-pptx --aspect source --font 'Microsoft YaHei' --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc
python3 docs_codex/diagrams/2026-10-16_coherence_hybrid/render_documents.py
python3 docs_codex/diagrams/2026-10-16_coherence_hybrid/validate.py
```

Chrome 检查六图无文字越界、框内溢出、文本重叠或连线穿字，已逐张查看 PNG。[图稿记录](previews/browser.json) · [两份正文预览记录](evidence/document-browser.json) · [最终检查](evidence/validation.json)。修订前文件与输入哈希保存在 `evidence/before/` 和 [input.json](evidence/input.json)。

六页 PPTX 含 270 个原生文本对象、119 条原生箭头和 9 个原生虚线形状，无整图栅格化。连线端点未绑定形状，移动模块后需调整连接。Office 显示／编辑尚未实测；图稿检查与硬件仿真、板测分别记录。
