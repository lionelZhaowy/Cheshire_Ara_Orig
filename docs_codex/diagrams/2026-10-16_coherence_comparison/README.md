# 一致性方案：统一布局对比图

2026-10-16，L01。配套[综述正文](../../engineering/CPU_NPU_Cache_Coherence_Survey.md) · [完整阅读预览](preview.html) · [四页原生可编辑 PPTX](export/diagrams.pptx)。

本目录为此前方案比较的历史快照，以下 E 优先推荐状态已由软件触发范围维护取代。现行图稿、完整预览和 PPTX 见[软硬件协同维护](../2026-10-16_coherence_hybrid/README.md)。本组为工程解释图，由本项目绘制；依据公开机制归纳，不复制论文图形。对比图使用通用 CPU 私有缓存／LLC 分层，项目实际互连继续采用[工业底图版](../2026-10-16_cache_coherence/industrial-base/system.png)。

| 页 | 比较内容 | SVG | PNG |
|---|---|---|---|
| 1 | A 软件维护、B 搬运边界硬件维护 | [源图](figures/handover.svg) | [预览](previews/handover.png) |
| 2 | C LLC-coherent DMA、D 含分配的 I/O 一致性 | [源图](figures/coverage.svg) | [预览](previews/coverage.png) |
| 3 | E 不分配 LLC 的 I/O 一致性、F 完整缓存代理 | [源图](figures/recommended.svg) | [预览](previews/recommended.png) |
| 4 | E1 清理到 DDR 后读取、E2 缓存直接供数 | [源图](figures/recommended-data.svg) | [预览](previews/recommended-data.png) |

E 是项目优先评估方向，B 是较低成本候选；E2 数据响应路径仍待评审。D／E 属于同一一致性类别，区别在分配策略；F 的关键是设备缓存也参与探测。图中的双向紫线合并表示请求与确认，绿线表示设备访问／数据。虚线框表示项目候选新增职责。

## 依据与解释范围

- [Cohmeleon v1 §2](https://arxiv.org/html/2109.06382v1#S2)：四种模式及 LLC-coherent 与 coherent DMA 的覆盖区别。
- [AMD PG201 v3.5 端口表](https://docs.amd.com/r/en-US/pg201-zynq-ultrascale-plus-processing-system/Slave-Interface)：HPC 不分配 L2、ACP 分配 L2、ACE 双向一致性，用于能力对照。
- [Arm IHI0022H](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf)：I/O 一致性事务语义；实际集成需满足互连与缓存响应条件。
- [项目方案](../../engineering/Cache_Coherence_Architecture.md)：B、E、F 的工程评估位置，独立 GB、共享数据代理和设备旁路要求。

图 4 以 LLC 持有最新脏行的读操作比较供数路径；下方列出设备写的共同逻辑职责。具体流水、事务编码、控制器端口映射与错误恢复由后续设计细化。E1 要求探测至访问完成受保护；一次性范围维护加整块排他对应 B。

## 生成与检查

使用 `industrial-svg-pptx` 风格和 `svg-pptx-diagrams-native` 原生导出后端。[build.py](build.py)仅复用已有 `Figure` 绘图类，不载入或重排项目完整拓扑；所有新图采用连续正交线。复现时使用新的输出目录：

```sh
python3 docs_codex/diagrams/2026-10-16_coherence_comparison/build.py --out-dir /tmp/coherence-comparison-svg
python3 docs_codex/diagrams/2026-10-16_cache_coherence/render.py --source-dir /tmp/coherence-comparison-svg --out-dir /tmp/coherence-comparison-png
python3 /home/zhaowenyao/.codex/skills/svg-pptx-diagrams-native/scripts/run.py --input /tmp/coherence-comparison-svg/handover.svg /tmp/coherence-comparison-svg/coverage.svg /tmp/coherence-comparison-svg/recommended.svg /tmp/coherence-comparison-svg/recommended-data.svg --out-dir /tmp/coherence-comparison-pptx --aspect source --font 'Microsoft YaHei' --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc
python3 docs_codex/diagrams/2026-10-16_coherence_comparison/render_document.py
```

Chrome 检查见[图稿记录](previews/browser.json)和[正文记录](evidence/browser.json)；四图逐张查看。PPTX 包含 146 个原生文字对象、71 条原生箭头及原生框形，无整图栅格化；连线端点未绑定形状，移动模块后需自行调整连线。Office 显示和编辑尚未实测。链接、输入保护及 PPTX 重读结果见[验收记录](evidence/validation.json)。
