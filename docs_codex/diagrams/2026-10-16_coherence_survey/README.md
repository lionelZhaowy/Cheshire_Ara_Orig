# CPU–NPU 一致性综述：原图与资料

2026-10-16，L01。正文：[CPU–NPU 缓存一致性](../../engineering/CPU_NPU_Cache_Coherence_Survey.md)；[含当前规划的最新阅读预览](../2026-10-16_coherence_hybrid/survey-preview.html)；[原始四图版预览](preview.html)。当前示意图及可编辑文件见[软硬件协同维护图稿](../2026-10-16_coherence_hybrid/README.md)，本目录继续保存四张原图与原交付证据。

## 四张原图

| 图 | 作者、资料与版本 | 原始文件 | 阅读预览 |
|---|---|---|---|
| 1：四种存储访问模式 | Joseph Zuckerman、Davide Giri、Jihye Kwon、Paolo Mantovani、Luca P. Carloni，*Cohmeleon: Learning-Based Orchestration of Accelerator Coherence in Heterogeneous SoCs*，MICRO 2021；arXiv 2109.06382v1，Fig. 1 | [SVG](originals/cohmeleon-modes.svg) | [PNG](previews/cohmeleon-modes.png) |
| 2：NVDLA 接口 | NVIDIA，NVDLA v2 *Integrator’s Manual*，System Diagram，2026-10-16 获取 | [PNG](originals/nvdla-system.png) | [PNG](previews/nvdla-system.png) |
| 3：Gemmini 架构 | Hasan Genc 等，*Gemmini: An Agile Systolic Array Generator Enabling Systematic Evaluations of Deep-Learning Architectures*；arXiv 1911.09925v2，Fig. 1 | [SVG](originals/gemmini-system.svg) | [PNG](previews/gemmini-system.png) |
| 4：并发实验 | Zuckerman 等，Cohmeleon，同上，Fig. 3 | [SVG](originals/cohmeleon-concurrency.svg) | [PNG](previews/cohmeleon-concurrency.png) |

来源页面：[Cohmeleon v1](https://arxiv.org/html/2109.06382v1)、[NVDLA 手册](https://nvdla.org/hw/v2/integration_guide.html#system-diagram)、[Gemmini v2](https://arxiv.org/html/1911.09925v2)。下载 URL、原图大小与 SHA-256 见 [sources.json](sources.json)。

`originals/` 保存获取的原始字节。PNG 预览由 Chrome 在白底按原比例渲染，保持原图连线、标签、坐标轴及数据；中文解释放在正文图注中。三张 SVG 预览宽 1800 px，NVDLA 保留 1076×519 原始分辨率。正文未使用重新绘制的项目拓扑。

用途为本地学习、比较与评审中的文献引用；各图版权归原作者／权利人。Cohmeleon 出版版版权页标注作者持有版权、出版权许可给 ACM，DOI：[10.1145/3466752.3480065](https://doi.org/10.1145/3466752.3480065)；arXiv 页面列出的存储许可不作为开放再许可。Gemmini 的版本与许可入口见[论文记录](https://arxiv.org/abs/1911.09925v2)，NVDLA 条款见[官方许可](https://nvdla.org/license.html)。进一步使用按各来源条款处理。

## 核对口径

| 对象 | 采用的版本／证据 | 本文使用范围 |
|---|---|---|
| Linux DMA API | [Linux 6.5](https://docs.kernel.org/6.5/core-api/dma-api-howto.html) | DMA 映射、同步及发布顺序的职责 |
| Arm AXI／ACE | [IHI 0022H，2020](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf)，D3／D6／D11 | I/O 一致性事务语义 |
| Ethos-U | [固定提交 9a825eec770d](https://github.com/ARM-software/CMSIS-Ethos-U/blob/9a825eec770dac8987ffb7703aadc34753720f2d/source/README.md#data-caching)；[版本证据](evidence/ethos-source.json) | 驱动 clean／invalidate 契约，旧 flush 钩子状态 |
| Ethos-N | [2020 系列简报](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/AI-ML%20Datasheet%20and%20briefs/Arm%20Ethos-N%20Product%20Brief%20-%20May%202020.pdf) | ACE-Lite／ACE-5 Lite 接口方向；具体分配策略待型号手册 |
| AMD Zynq UltraScale+ | [PG201 v3.5](https://docs.amd.com/r/en-US/pg201-zynq-ultrascale-plus-processing-system/Slave-Interface)；[官方配置示例](https://xilinx-wiki.atlassian.net/wiki/spaces/A/pages/18842098/Zynq+UltraScale+MPSoC+Cache+Coherency) | HP／HPC／ACP／ACE 范围和 L2 分配；使用需满足属性与 snoop 配置 |
| NVDLA | v2 集成手册；[v1 BDMA 描述](https://nvdla.org/hw/v1/ias/unit_description.html#bridge-dma) | 双内存接口、可选 SRAM 与包含 BDMA 的配置；SoC 负责一致性集成 |
| Gemmini | 论文 v2；[README 固定提交](evidence/gemmini-source.json)；[Chipyard 1.11.0 及子模块](evidence/chipyard-source.json) | 默认路径和具体配置静态核对，未展开／运行参考 SoC |
| ESP | [Giri 等，NOCS 2018](https://www.cs.columbia.edu/~davide_giri/pdf/giri_nocs18.pdf) | 三种模式的运行时选择、缓存容量与访问复用取舍 |
| Cohmeleon | 2109.06382v1，§2–4 | 四模式、按调用选择；Fig. 3 基准按单实例非一致性 DMA 归一化 |
| Spandex／FCS | [Alsop 等，2104.11678v1，2021](https://arxiv.org/html/2104.11678v1) | CPU–GPU 模拟、访问级选择、自失效／写直达及同步前提 |
| 当前工程 | [8 个源码哈希核对](evidence/local-source-check.json) | 沿用现有专题的源码结论；无新增硬件运行证据 |

## 预览与检查

利用已安装 Python Markdown 和 Chrome，运行：

```sh
python3 docs_codex/diagrams/2026-10-16_coherence_survey/render.py
```

脚本只从原图生成 PNG 和正文 HTML 预览。[浏览器记录](evidence/browser.json)检查图片加载与页面横向溢出；四张 PNG 已逐张查看，页面截图保存在 `previews/document-*.png`。输入保护见 [input.json](evidence/input.json)，最终链接和差异检查见 [validation.json](evidence/validation.json)。
