# eMMC 与 SPI NAND 非易失存储方案

日期：2026-10-13。L01；输入版本 `bf1b4198dfd74cc78291c152b8b682d523e785c5`，分支 `mp/ara-pulp-v2`。这是选型说明材料，不是新增存储接口的实现或性能验收报告。

## 当前版本：修订 2，紧凑技术汇报版

用户要求补齐频率、协议、器件选型和 PHY 条件，并减少零散排版。本版保留两页，将字号调整至正文约 16–18 pt，按“建议配置 → 连续连接图 → 协议 / 实现表格 → 带宽比较”组织。

- **[新版两页 PPTX](revision_02/nonvolatile_storage_options_v2.pptx)**。
- PNG 预览：[eMMC](revision_02/slide_01.png) · [SPI NAND](revision_02/slide_02.png)。
- 配图 SVG：[eMMC](revision_02/emmc_v2.svg) · [SPI NAND](revision_02/spi_nand_v2.svg)；[原生图合辑](revision_02/diagrams.pptx)。
- [结构与测宽检查](revision_02/validation.json)、[逐页视觉检查](revision_02/visual_review.json)、[输入源码哈希](revision_02/source_manifest.json)。

修订 2 的配置建议和约束：

| 项目 | eMMC | SPI NAND |
|---|---|---|
| 器件候选 | Kingston E04GS14DXI，4 GB MLC、-40～85°C；8 GB 候选 EMMC08G-WV28 | Winbond W25N08MW 系列，8 Gbit / 1 GiB、1.8 V；后缀待确认 |
| 初始化 / 联调 | 1-bit、≤400 kHz 初始化，再按器件能力切换总线/模式 | 首次联调建议 10 MHz，并非协议强制要求 |
| 批量读取评估点 | 8-bit High Speed SDR、50 MHz；模式规格上限为 52 MHz | Quad STR/SDR、100 MHz，属于有条件评估值 |
| 理论线速 | 50 MB/s ≈47.7 MiB/s | 50 MB/s ≈47.7 MiB/s |
| 前提 | 新增主机 / DMA、收发时序与适配 PAD；核对 VCCQ，评估 1.8 V I/O | 当前 SCK=clk_i/[2×(CLKDIV+1)]；100 MHz 需输入至少200 MHz且整比分频匹配，另须验证采样及软件吞吐 |

50 MHz eMMC 是本轮提出的评估工作点，不是正式时钟冻结；不能把此前讨论的 52 MHz 模式上限当作已选时钟。候选器件支持 HS400 不代表本方案需要 HS400。电气层必须实现 I/O PAD、采样和驱动时序；数字接口不等于只需 RTL，也不意味着所有模式都强制购买数模混合 PHY。高速 PHY 的 DLL/延迟线可参考官方实现。

当前 SPI Host 和公共 Regbus 共用 SoC `clk_i`；不因为提出100 MHz SCK便自行提高 SoC 时钟或添加时钟域。100 MHz只是必要的频率预算，页读取等待、命令、FIFO和CPU搬运还会降低有效吞吐。Quad 50 MHz 理论约23.8 MiB/s虽低于25 MiB/s建议目标，但不单独证明一定超过30秒，仍以完整加载测量为准。

新加入的官方链接：[Kingston 工业级选型表](https://media.kingston.com/pdfs/emmc/itemp-emmc_flyer_en.pdf?_=v1)、[JEDEC 5.1 标准（TI 托管）](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/791/JESD84_2D00_B51-_2800_1_2900_.pdf)、[Synopsys PHY 实现](https://www.synopsys.com/designware-ip/interface-ip/mobile-storage/sd-emmc-phy.html)、[W25N08MW 型号入口](https://www.winbond.com/hq/new-online-purchasing-guide/?__locale=en&pLine=%2Fproduct%2Fcode-storage-flash%2Fqspi-nand%2F&pNo=W25N08MW)。系列参数与具体料号供电/封装/温度/供货仍须分开确认。

修订 2 可复现命令（输出非空时拒绝覆盖）：

```sh
/home/zhaowenyao/.codex/skills/publication-figures/.venv/bin/python \
  docs_codex/diagrams/2026-10-13_nonvolatile_storage/build_report_v2.py \
  --out-dir /tmp/nonvolatile_storage_v2_rebuild
```

两页分别88/96个原生对象，5/7个原生箭头，7个官方超链接，备注保留协议及计算依据。已检查测宽、对象边界、链接与最终PNG；Office实际显示/编辑未验证，PNG仍为同源SVG渲染。旧稿9项产物哈希全部保持；修改前说明与交接已备份于 `evidence/before_revision_02/`。下方保留第一版依据及其验证快照。

## 第一版阅读与下载（历史保留）

- **[第一版两页可编辑 PPTX](output/nonvolatile_storage_options.pptx)**：第 1 页 eMMC；第 2 页 SPI NAND、对比与加载预算。每页页脚有可点击的官方链接，备注包含来源、源码依据和适用条件。
- PNG 预览：[第 1 页](output/slide_01.png) · [第 2 页](output/slide_02.png)。这些是与 PPT 共用布局的 SVG 渲染，不是 Office 截图。
- 原始配图：[eMMC SVG](output/emmc.svg) · [SPI NAND SVG](output/spi_nand.svg)；[纯配图原生 PPTX](output/diagrams.pptx)。
- 完整页面 SVG：[第 1 页](output/slide_01.svg) · [第 2 页](output/slide_02.svg)。
- [自动检查](output/validation.json) · [逐页查看记录](visual_review.json) · [源码哈希](output/source_manifest.json)。

## 内容与适用条件

用户确认：约 500 MiB 的盲元补偿、非均匀性校正参数开机完整加载到 DDR，运行时从 DDR 读取；允许 30 秒加载。本材料暂将 30 秒定义为存储初始化至加载并校验完成的预算，不等同于完整系统上电时间要求。

`500 / 30 = 16.67 MiB/s` 是纯数据带宽下限，约 `17.48 MB/s`。建议有效搬运目标为至少 `25 MiB/s`，对应约 20 秒传输，并预留约 10 秒给初始化、校验；这是预算建议，需端到端测量。若校验等工作超时，应重新分配预算。

eMMC 建议评估 4 GB/8 GB 工业级器件、带 DMA 的主机控制器和对应驱动；现有工程未集成该通路。保留 NOR 启动，由后续加载程序在 DDR ready 后读取 eMMC。SPI NAND 方案评估复用 SPI Host，必须新增 NAND 驱动并验证实际 Quad、FIFO 和软件搬运性能。当前 SPI Host 不应直接画成已能 DMA 写 DDR。

W25N-MW 仅是官方可查的系列示例，非采购决定。8 Gbit 对应 1 GiB；两份 500 MiB 参数仅余约 24 MiB，另有坏块、预留块、元数据和增长要求，不应据此认定单颗 1 GiB 足够稳妥实现双副本。A/B 参数更新是建议，用户尚未冻结；完整方案还需数据落盘、冗余版本记录和更新中掉电恢复验证。

SPI NAND 图是读取功能链示意，ECC 与页缓存的物理实现次序由具体器件决定。带器件内纠错功能不等于具有 eMMC 的完整介质管理。固件仍需处理页读命令、纠错状态、不可纠错错误和坏块映射等。

例如 Quad STR 50 MHz 的纯线速只有 25 MB/s（约 23.84 MiB/s），不计其他开销也达不到 25 MiB/s 建议目标。Winbond 标称 83 MB/s 不能作为当前工程性能；本地 SD-SPI 驱动的 25 MHz 限制也不是所有 SPI NAND 的通用频率上限。

## 官方依据

以下均于 2026-10-13 查阅；只引用公开资料，没有复制供应商受限内容或整段产品说明。

| 官方来源 | 本材料使用的依据 |
|---|---|
| [Micron eMMC 产品页](https://www.micron.com/products/storage/managed-nand/emmc) | 器件分类与官方资料入口 |
| [Micron FAQ](https://www.micron.com/sales-support/sales/faqs) | 全管理型 eMMC 的内部介质管理与纠错职责 |
| [Micron NAND 选型说明](https://www.micron.com/products/storage/nand-flash/choosing-the-right-nand) | NAND 控制器、ECC、坏块与磨损管理职责 |
| [Micron eMMC 容量与型号交叉查询](https://www.micron.com/sales-support/design-tools/cross-reference-tools/emmc-cross-reference-tool) | 4 GB/8 GB 等容量档位；不构成供货承诺 |
| [Winbond W25N-MW](https://www.winbond.com/hq/product/code-storage-flash/qspi-nand/w25n-mw/index.html?__locale=en) | 2/4/8 Gbit、SPI/Dual/Quad、页组织与 BBM LUT |
| [W25N02MW 官方详情](https://www.winbond.com/hq/product/code-storage-flash/qspi-nand/w25n-mw/?__locale=ja&partNo=W25N02MWTBIG) | 系列器件内 ECC 的具体示例；未将该料号位数泛化为所有器件规格 |

本地对应：[SPI Host 接线](../../../hw/cheshire_soc.sv)、[Boot ROM 启动介质](../../../hw/bootrom/cheshire_bootrom.c)、[SD-SPI 软件搬运](../../../sw/lib/hal/spi_sdcard.c)、[NOR HAL](../../../sw/lib/hal/spi_s25fs512s.c)、[官方启动说明](../../../docs/um/sw.md)。具体输入哈希见上方清单。

## 复现与检查

使用 `svg-pptx-diagrams-native` 的原生图导出后端生成两张图，再通过 `python-pptx` 将原生对象加入两页演示稿，补充正文、比较表、备注和超链接。没有栅格化结构图。所用字体为 Microsoft YaHei；本机 PNG 渲染使用可用的中文字体回退，PPT 不嵌入字体。

```sh
/home/zhaowenyao/.codex/skills/publication-figures/.venv/bin/python \
  docs_codex/diagrams/2026-10-13_nonvolatile_storage/build.py \
  --out-dir /tmp/nonvolatile_storage_rebuild
```

脚本依赖 `python-pptx`、Pillow、CairoSVG，支持 `--skill-dir` 指定 skill 位置。输出目录非空时拒绝覆盖。复现需已安装 skill；阅读和编辑最终 PPT 不依赖它。重新选定输出目录后可安全重建，不运行旧图生成器。

自动检查包含：2 页/16:9、原生对象、整体无栅格媒体、对象 ID 唯一、对象不越界、正文测宽、2 个官方超链接、备注存在、原生箭头及文件哈希。逐页查看 PNG 后未发现文字遮挡、错向箭头或截断。第 1 页 59 个原生对象，第 2 页 57 个；箭头分别 5/6 个。

**验证边界：**结构与同源 SVG 预览检查通过；本机没有可用的 Office/LibreOffice，Microsoft Office 显示和交互编辑未验证。移动模块时连线端点不保证自动跟随。未修改生产源码，未编译、未仿真、未板测，未测量真实存储吞吐。
