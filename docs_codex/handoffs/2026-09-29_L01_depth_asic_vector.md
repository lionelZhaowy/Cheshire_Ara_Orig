# L01 / 教材深度扩充、CVA6–Ara 与 ASIC 集成教学

## 基本信息

- 日期：2026-09-29；任务 L01。
- 授权范围：在上一轮新版 HTML 上扩充技术深度、配图与必要独立教学示例；用户进一步要求时序图使用 WaveDrom 等工具，不能用 0/1 表格拼接。
- 状态：文档及轻量构建交付完成；生产 SoC 动态验证待执行。
- 输入：`mp/ara-pulp-v2`，HEAD `4f240258ca683913b7e17949aff23139bff981f1`。开始时已有上一轮教材重构的大量未提交改动和 ENV01 交接，均不清理、不覆盖历史证据。
- 负责路径：`docs_codex/learning/`、独立交接及必要共享索引。未启用子 Agent，未修改生产 RTL/sw/依赖/清单/平台。

## 本轮结果

- 保持 16 章、6 项实验、2 页参考，在原页面增量扩充；[章节职责表](../learning/DEPTH_EXTENSION.md)记录分工。
- 系统总图、AXI/Reg 拓扑、实际地址范围与 CPU 属性、配置组合、时钟/复位/电源边界、各介质启动、Debug、外设、DMA 与 DDR 接入深化。
- CVA6 初译码/scoreboard/非推测发出、专用加速接口、Ara 早应答/实际完成、MMU/VLSU、VRF 与缓存边界、软件 ISA/ABI/VS/FS、RVV 三入口及归约。
- 当前 CPU/Ara 可见性与未来 NPU 方案分开；共享路径、所有权状态、Ara→NPU→Ara 时序、DDR 旁路副本与 AMO/LRSC 问题、137×64 int8 模型片段成本和伪代码。
- 13 张新结构/状态 SVG + 6 张 WaveDrom 教学时序，保留 JSON、固定版本离线 renderer、许可证与来源。旧通道流程图已纠正“时序”称呼。
- 独立示例沿用 journey：汇编/intrinsics/自动向量化，长度 0/1/63/64/65/137，uint32 环绕输入、逐项独立参考、输入保持/守卫和整数归约；FP32 为编译探针。

新结论为源码确认或本轮主机构建，不是目标执行证明：

1. 本地 `CvxifEn=0`，`cvxif` 名称承载专用 `cva6_to_acc_t/acc_to_cva6_t`，消费者为 acc_dispatcher/Ara，不能解释为通用 XIF 插槽。
2. `acc_commit` 的非推测发出许可、CPU 最终提交、Ara 内部运行完成和 load/store complete 是不同事件。
3. `vstu.sv` 对 B 通道错误留有 TODO，vldu 也没有完整的 RRESP 错误闭环；完成通知不能单独证明成功。官方 main dispatcher 文档不覆盖本地事实。
4. 当前默认 SPM 译码各 128 KiB；低执行属性覆盖 2×SizeSpm 而实际窗口只有 SizeSpm，高别名不在该执行规则内。历史官方图的预留范围不能当实际容量。
5. GCC 15.2 固定手册的 intrinsic 0.11 文字与本地宏 `12000` 分开记录；具体 API 通过实际编译和 dump 验证。自动向量化实际产生 V 指令，但仍需目标运行。

## 改动与接口

- 正文 `content/*.html` 与生成 HTML；新增 `DEPTH_EXTENSION.md`、`OFFICIAL_SOURCES.md`。
- `assets/depth-*.svg`、`assets/waves/*.json`；固定 WaveDrom 3.5.0 仅用于文档生成，阅读使用静态 SVG，无 CDN/Node/npm 要求。
- `examples/rvv_reduce.S`、`rvv_intrinsics.c`、`rvv_auto.c`、`rvv_fp_probe.c`；扩展 journey/build_journey 与 check_run 的 `--depth`。
- 新 `build_depth_diagrams.py`、`build_waves.py`、`browser_cdp.py`、`preview_depth_site.py`、`record_depth_sources.py`、`check_depth.py`；旧快照脚本保留，README 明确当前维护入口。
- 生产配置/profile/地址/中断/接口变化：无。未实施 NPU、一致性或缓存机制改造。
- 未 git commit/push。部分临时 ELF 目录被既有规则忽略；精选完整构建日志和 ELF 哈希另存于本轮 evidence。

## 验证证据

工作目录为仓库根；GCC 15.2.0，Chrome 版本及离线模式见浏览器报告。

```bash
JOURNEY_DEPTH=1 timeout 60 bash docs_codex/learning/scripts/build_journey.sh scalar spm
JOURNEY_DEPTH=1 timeout 60 bash docs_codex/learning/scripts/build_journey.sh rvv spm
JOURNEY_DEPTH=1 timeout 60 bash docs_codex/learning/scripts/build_journey.sh rvv-intrinsics spm
JOURNEY_DEPTH=1 timeout 60 bash docs_codex/learning/scripts/build_journey.sh rvv-auto spm
JOURNEY_DEPTH=1 INJECT_ERROR=1 timeout 60 bash docs_codex/learning/scripts/build_journey.sh rvv spm
python3 docs_codex/learning/scripts/build_depth_diagrams.py
python3 docs_codex/learning/scripts/build_waves.py
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/preview_depth_site.py
python3 docs_codex/learning/scripts/check_depth.py
```

- [构建/指令/宏报告](../learning/evidence/depth-20260929-builds.txt)：五个整数 ELF，FP32 对象，均退出 0；三种向量入口有 load/add/store/reduction，标量 main/参考对象无 V。完整命令日志 `depth-20260929-build-*.txt` 保留既有 MMIO 符号/RWX 告警。
- [静态与保护报告](../learning/evidence/depth-20260929-checks.txt)：728 个旧站文件、66,754,766 字节保持一致；670 个开始前 evidence 文件保持哈希；来源清单、59 个生成 HTML/SVG 可重复，链接/锚点/脚本与 diff 检查通过。
- 检查器 8 个合成日志正反例通过，仅证明日志工具。WaveDrom 背压内容稳定性做了简单可执行检查，不是生产协议验证。
- [浏览器报告](../learning/evidence/depth-20260929-browser.txt)：20 主页面桌面/手机、5 页禁用脚本、寄存器搜索/缩放/计算器、35 张当前图的文本边界、20 旧页跳转；无外网渲染请求或 JS 错误。目视检查向量算术波形与完整系统图。
- [官方资料与版本差异](../learning/OFFICIAL_SOURCES.md)记录实际读取及在线取得失败项；[来源哈希](../learning/evidence/depth-20260929-sources.json)记录本地快照。
- 未执行生产 RTL 编译/展开/仿真、历史 Reg 单元重跑、板测、性能测量、综合、IP 集成或 ASIC 提取。所有新增时序都是教学图，非真实波形。

## 决策与下一步

用户已确认继续单线教材、保留可运行 FPGA 工程、NPU/ISP 绕过 LLC 的规划和 AXI4 DDR 方向。本轮将 WaveDrom JSON + 静态 SVG 作为教学时序维护方式。

1. V01：用冻结向量组合实际编译展开，运行标量正常/注错，再运行实验 E 三入口及尾部归约，保存 PC/trans_id/Ara/VLSU 波形和数值日志。
2. V01/S01：复现 Ara R/B 错误边界和 DMA 控制宽度问题，另行授权修复生产代码；不得把本轮源码告警当动态复现。
3. A01/DDR/NPU：取得供应商接口资料后，确定旁路地址/缓存属性/所有权与原子控制区、时钟复位和取消协议，再建立集成验收。
4. 后续教材维护先读本交接、`learning/README.md` 和对应章节；当前校验器为 `check_depth.py`，不要运行旧快照写入器覆盖历史证据。

共享状态和任务表已增加本轮完成范围及目标验证缺口；未将其他实施任务升级为已授权。
