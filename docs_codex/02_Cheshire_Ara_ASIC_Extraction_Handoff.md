<a id="cheshire--cva6--ara-固定配置剥离后续-agent-执行交接书"></a>

# Cheshire/CVA6/Ara 固定配置提取交接书

编写日期：2026-09-20。

本文是实施规格，不是迁移完成报告。本轮只创建本文；没有创建 ASIC RTL、修改原工程、重新编译或验证芯片功能。

## 1. 用户目标与执行边界

用户希望把当前本地工程中正确的 Cheshire + CVA6 + Ara 组合，提取到独立的 `cheshire_ara_asic/` 目录，后续由团队自己的 EDA 脚本管理。**不要把学习、修补或长期维护 Bender 变成前置项目。**

后续 Agent 获得实施授权后，默认在原仓库内新建 `cheshire_ara_asic/`，以便不修改旧工程、也不写入未授权的同级目录。该目录必须能够单独复制到 EDA 服务器或新仓库使用，不能依赖父目录。若用户指定其他位置，以用户为准。

交付目标：

1. 一个固定的向量 CPU + Ara 硬件配置，而非通用多板卡/多 profile 构建平台。
2. 本地完整的必要 RTL、头文件、软件和验证依赖；有序的静态编译清单。
3. 日常编译、仿真、软件构建不调用 Bender，不访问 GitHub，不引用旧 `.bender` 目录。
4. 保留工艺无关 SoC 和明确的工艺适配边界，供后续接 SRAM、时钟单元、DDR 控制器/PHY、PAD 与 DFT。
5. 先验证提取正确，再裁切外设、添加 NPU/ISP、改变 DDR 拓扑；这些变更分开验收。

不属于首次提取的工作：重新下载/升级第三方 IP；修复原工程所有入口；搭建通用依赖管理系统；集成 Linux 全套 SDK；直接完成流片签核；在无 IP 交付资料时虚构 DDR/PHY 或 SRAM 实现。

“去掉 Bender”不等于不要编译清单、配置和工具脚本。用静态 filelist、一个固定配置包和少量团队脚本替代即可。

## 2. 已核对的本地事实

执行时先重新检查工作区；下列提交号只是本文编写时的定位信息。

| 对象 | 本地事实 |
| --- | --- |
| 根仓库 HEAD | `379ae4544bc62e05a2736b11b33a3244181bba38` |
| CVA6 源码 | `.bender/git/checkouts/cva6-20c9d7cbe0dd6995/` |
| Ara 源码 | `.bender/git/checkouts/ara-2c7b103275a16c87/` |
| 依赖管理状态 | `Bender.local` 指向版本管理中的本地源码快照；不是可以随意删除的临时缓存 |
| 依赖溯源 | `.bender/SNAPSHOT.tsv`、`.bender/UPSTREAM.lock`，以及根仓库历史 |
| 根构建默认 profile | `cv64a6_imafdchsclic_sv39_wb`，不启用 RVV，不作为目标 CPU 配置 |
| 目标 CPU profile | `cv64a6_imafdcv_sv39`，启用 RVV；L1 D-cache 为 WT |
| 现有仿真生成脚本 | 使用标量 profile，且同时列出 CVA6 decoder stub 和 Ara 真实 decoder；不能直接作为正确清单 |
| 现有 VCU118 加源脚本 | 使用向量 profile、`ARA`、`NR_LANES=2`、`VLEN=2048`，可交叉核对，但包含 FPGA 专用实现 |
| DDR 采购方向 | 供应商已可提供 AXI4 控制器；不要继续把 AXI4→AXI3 桥作为既定需求 |

关键入口：

- [Ara 集成入口](../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/Makefile)：`COMMON_CUSTOM_TARGETS` 给出正确 profile 和 decoder 选择。
- [SoC 配置/派生函数](../hw/cheshire_pkg.sv)：`DefaultCfg`、`gen_cva6_cfg()` 和 AXI 类型/地址派生。
- [SoC 本体](../hw/cheshire_soc.sv)：CPU、Ara、原子适配器、LLC 和外设连接。
- [Ara 仿真配置](../target/sim/src/tb_cheshire_pkg.sv)：`gen_cheshire_ara_cfg()`。
- [VCU118 源清单](../target/xilinx/scripts/add_sources.vcu118.tcl)：只用于交叉检查。
- [VCU118 顶层](../target/xilinx/src/cheshire_top_xilinx.sv)：板级适配参考，不作为 ASIC 顶层直接复制。

本地可能有未跟踪的测试和已有产物，必须记录。旧 ELF/bitstream 不构成当前提取结果的通过证据。

<a id="3-固定哪一个配置"></a>

## 3. 固定配置基线

### 3.1 首次提取的唯一基线

用本地 `gen_cheshire_ara_cfg()` 的**实际取值快照**作为首次通用 SoC 基线，而不是继承会变化的外部默认值：

| 项目 | 基线 |
| --- | --- |
| CVA6 | 只保留 `cv64a6_imafdcv_sv39_config_pkg.sv` 这一 profile 定义 |
| SoC | 复制当前 `DefaultCfg` 的全部字段，显式设 `Ara=1` |
| Ara | `AraNrLanes=2`、`AraVLEN=2048` |
| decoder | Ara 的 `hardware/src/cva6_accel_first_pass_decoder.sv`；排除 CVA6 stub |
| LLC/SPM | 保留当前 LLC、原子适配器、Boot ROM 初始化路径及容量 |
| 地址/中断/外设 | 首次保持上述配置快照，不顺手重排地址或裁切启动依赖 |
| 平台 | 通用仿真/ASIC 子系统；不带 VCU118 MIG、XPM、MMCM、板级 PAD |

这是一份提取验证基线，不是已经确定的最终产品外设清单。它与 VCU118 顶层存在已知平台差异，例如 RTC 频率、SerialLink/USB 的设置；执行 Agent 必须在配置说明中列出差异，不能声称是板上 bitstream 的完全等价复刻。

在新目录内建立 `cheshire_ara_asic_cfg_pkg.sv`，只导出一个最终配置常量。仿真和综合实例化同一个固定 SoC wrapper，不再用 `SELCFG` 选择不同 SoC。不要求重写底层所有参数化模块，也不要机械删除参数和 generate；固定顶层实参即可固定硬件。

为避免第二套手抄配置漂移，必须统一导出外部 AXI 类型、派生位宽和配置常量，沿用 `CHESHIRE_TYPEDEF_ALL` 等派生机制。不能把 LLC 输出 ID 宽度直接当成 CPU 原始 AXI ID 宽度。

注意：CVA6 配置结构中的 `VLEN` 和 Ara 的向量寄存器长度不是可以凭名字互换的字段；本地 CPU profile 中存在 `VLEN=64`，不要为了与 Ara 的 2048 对齐而修改它。按字段实际用途追踪。

### 3.2 必须检查的配置一致性

- 所有配置包/模块同名定义唯一；尤其是 `cva6_config_pkg` 和 first-pass decoder。
- CPU 最终构建配置 `RVV=1`，SoC `Ara=1`，lane/VLEN 一致。
- 保留当前 CVA6/Ara 指令、MMU、异常和一致性交互。不因为端口名带 `cvxif` 就改成其他通用 CV-X-IF 模块；当前集成中 `CvxifEn=0` 并不代表 Ara 关闭。
- 仿真和综合的差异只允许是验证代码、断言设置及明确的技术单元替换，不允许悄悄切换 CPU profile、cache 类型或 SoC 外设。
- 软件向量 ISA 与硬件相符；VS/FS 初始化由软件负责，不以 HelloWorld 输出作为向量验收。

<a id="4-获取源码闭包只借用-bender-一次"></a>

## 4. 源码依赖闭包与一次性清单解析

“源码闭包”指：不仅有实例化的 RTL，还包含解析这些 RTL 所需的 package、include、宏、生成文件和技术单元。

<a id="41-推荐操作"></a>

### 4.1 清单解析与源码核对步骤

1. 记录当前根提交、工作区变更、依赖快照和工具版本。不要运行依赖更新、清理或下载命令。
2. 使用已安装 Bender 的本地模式，离线解析**固定向量配置**，将导出结果收集到新的 staging/provenance 目录；不要覆盖原 `compile.cheshire_soc.tcl`。
3. 提取有序文件、include 目录、宏、源文件分组/编译单元约定和语言类型；保持相对顺序。
4. 从当前磁盘复制实际源码和必要头文件到新目录，重写所有路径为新目录内部路径。
5. 新目录中的静态清单成为后续维护入口，Bender 输出仅归档为溯源材料。

本机 `bender script --help` 已确认有 `flist-plus`、`template-json`、`--no-default-target` 和 `--local`。下例是**待执行的提取命令示意，不是已经验收的最终 filelist**：

```sh
bender --local script flist-plus --no-default-target \
  -t rtl -t cva6 -t cv64a6_imafdcv_sv39 \
  -t exclude_first_pass_decoder \
  --define ARA --define NR_LANES=2 --define VLEN=2048
```

先用非 FPGA 的通用目标获取参考 RTL 闭包；测试平台需要的 `sim`/`test` 文件另外识别、放入验证清单。用 `template-json` 或对应模拟器输出交叉核对分组宏/include 作用域，不假定平铺的 flist 能表达所有编译单元语义。

不要把示例直接加 `-t asic` 就当作 ASIC 就绪：当前 `tech_cells_generic/Bender.yml` 在 ASIC target 下会排除部分通用技术单元，若没有工艺替代会留下缺失模块。必须先把技术单元边界列清楚。

如果本地 Bender 无法离线解析：只做有限的本地路径检查；不要升级 Bender/依赖或修复整个旧构建体系。用现有正确的 Vivado 向量清单作为参考，加上依赖 `Bender.yml` 的条件选择信息，人工/脚本生成通用静态清单。该回退必须逐项替换 FPGA 单元，并靠实际编译展开验证，不能简单删除名字带 xilinx 的几行即宣告成功。

<a id="42-必须保存但常被漏掉的内容"></a>

### 4.2 依赖来源、许可证与本地差异

- AXI、common_cells、CVA6、Cheshire、寄存器接口等 `.svh`/`.vh` 及所有间接 include。
- FPU/fpnew、divider、debug、timer/interrupt、寄存器与总线等传递依赖。
- Boot ROM 的现有生成 RTL，以及其 C/汇编/链接源和生成工具。
- 寄存器的现有生成 RTL、软件头文件和原始描述；首次可以不重生成，但必须能追溯。
- 被未实例化模块的类型声明引用的 package。模块没有综合进网表，不代表解析阶段不需要它的 package。
- 仿真的 ELF loader C++、DPI 声明、必要验证包和 AXI memory model。
- 每个实际复制组件的许可证、版权声明、来源版本和本地差异。对外部存储器仿真模型单独确认可用性，不随意再分发。

允许对必要组件先保留完整 include 子树，再逐步收敛；不要求一开始把文件数量压到理论最小。不要复制整套 Linux SDK、Vivado 工程产物和所有其他 profile。

不要按字母排序 filelist；不要用全目录递归通配符把 stub、替代实现、测试模块一起编进去；不要把所有源文件拼成一个巨型 SV 文件；不要只拷综合网表。

## 5. 新目录的最小组织

```text
cheshire_ara_asic/
  README.md
  rtl/
    config/cheshire_ara_asic_cfg_pkg.sv
    top/cheshire_ara_asic_soc.sv
    cheshire/                     # 本地 SoC 必要源码，保留原相对 include 关系
    vendor/<component>/           # 实际需要的第三方 RTL/头文件
  tech/
    sim/                          # 通用 SRAM、时钟等仿真实现
    asic/                         # 工艺适配边界；未交付则明确标记未实现
  filelists/
    rtl.f                         # 共同功能 RTL，包含固定配置
    sim.f                         # rtl.f + 仿真技术单元 + TB/DPI 所需 SV
    synth.f                       # rtl.f + 指定的工艺实现/声明
  verification/
    tb/                           # 固定 wrapper 的 TB、VIP
    models/                       # AXI RAM 等
    dpi/                          # elfloader.cpp 等
  sw/
    startup/ link/ lib/ tests/ bootrom/
  scripts/                        # 团队使用的简单 compile/run/build 脚本
  constraints/                    # 真实约束；未知时列问题，不编造数字
  provenance/
    source_manifest.tsv           # 新路径、原路径、组件、版本、SHA256、用途
    configuration.md              # 完整配置快照、平台差异、已裁切项
    extraction_notes.md           # 导出参数、宏/分组、改动理由、未完成项
    original_manifests/           # Bender/锁文件等归档；不参与日常构建
  LICENSES/
```

文件名可按团队习惯调整，但必须保留上述职责分离。每个 filelist 明确相对路径基准；工具脚本统一从新目录根部执行或解析根路径。不要假设各工具对嵌套 `-f` 的相对路径规则相同。

不新增泛化配置生成框架、复杂插件系统或自制包管理器。至多建立一个简单 manifest/check 脚本做路径存在、重复定义和校验和检查。

## 6. 顶层与工艺边界

<a id="61-首次交付的是-soc-子系统不是已完成的芯片顶层"></a>

### 6.1 SoC 子系统的交付范围

`cheshire_ara_asic_soc.sv` 应实例化固定配置的 `cheshire_soc`，暴露：

- SoC 时钟/复位、RTC、启动模式、测试模式。
- DDR 侧 AXI 主接口（来自 `axi_llc_mst_req_o`/响应端口）。
- JTAG、UART 和当前保留的必要外设接口。
- 后续自定义 IP 用的控制/中断/AXI 扩展边界；没有启用的输入按协议安全绑值。

不复制 VCU118 顶层的 MMCM、IBUF/OBUF、MIG、风扇、板级约束和 PCIe/板卡相关对象。不把 `dram_wrapper_xilinx.sv` 改名字后冒充 ASIC DDR wrapper。

PLL、PAD、DDR PHY、芯片电源/复位、scan 等放在后续 chip-level 集成层。DDR 初始化完成前不得无条件允许软件依赖 DDR；首次验证可用 AXI RAM 替代控制器，明确这不验证 PHY 和真实初始化流程。

<a id="62-技术单元必须单独跟踪"></a>

### 6.2 工艺相关单元与替换记录

至少盘点 LLC data/tag、CVA6 cache、Ara 寄存器文件/存储结构、debug RAM、各级 FIFO、clock gating/reset/CDC 单元。不能只寻找一个 `tc_sram` 就声称所有存储器已完成工艺映射。

每个 SRAM/ROM 适配项记录：深度、位宽、端口数、读延迟、byte enable、read-during-write 行为、初始化/X 行为、低功耗/测试接口。先保持功能时序语义，再做宏拼接或 banking。

仿真模型和 ASIC 实现同名时只能选一份。工艺库未到位时允许完成通用 RTL 仿真和已标注的综合前检查，但 `synth.f`/流程必须明确报出缺失映射，不能静默把行为 SRAM 当作最终宏实现，或以未解析黑盒宣告完成。

<a id="7-软件与验证脱离旧仓库也必须能运行"></a>

## 7. 独立软件环境与验证要求

最小软件集合：启动汇编、链接脚本、串口/计时/退出支持、必要寄存器头文件、标量 HelloWorld、一个可判定结果的 RVV 测试、原子与访存测试。

- 向量测试使用包含 V 的 ISA 编译选项，例如本地 Ara 入口使用的 `rv64gcv_zifencei`，ABI 保持与运行库一致；记录编译器版本。
- 在第一条可能的向量指令之前设置 `mstatus.VS`；向量浮点还要考虑 FS。若只在 `main` 中启用，必须确认此前的启动代码/库没有自动生成向量指令；更稳妥的是在新启动路径中明确处理。
- `vsetvli` 的 strip-mining 测试覆盖小于/大于 VLMAX 和尾部情况，不只固定长度一次运算。
- 继承现有 Boot ROM 全 SPM 初始化语义。直接预加载 ELF 不应掩盖 Boot ROM/LLC 初始化错误；另外保留从复位执行 Boot ROM 的测试。
- 原 `sw/sw.mk` 的裸机 GPT 生成规则被注释，不将它当成首次仿真前置条件。若交付自主 Flash/SD 启动，再单独恢复正确镜像构建和测试。
- 文件来源完整：`crt0.S`、`common.ldh`、各链接布局、printf/OpenTitan 引用和 LLC 软件接口不能依赖父目录。
- 旧 `vip_cheshire_soc.sv` 若沿用，检查层次路径与新 wrapper 是否一致；其 ELF DPI 对应 C++ 也必须编译链接。

首次闭环建议：在修正后的向量参考配置与新固定 wrapper 上运行相同最小程序，比较退出码、关键计算结果和必要总线行为。不要为了建立参考而覆盖旧生成脚本，可将参考构建产物放独立 staging 目录。

## 8. NPU/ISP 绕过 LLC 的架构契约（后续阶段，不混入首次提取）

<a id="81-允许旁路但必须把两个问题分开"></a>

### 8.1 缓存一致性与原子操作可见性

**原子性**：一个读-改-写不能被其他相关访问破坏。

**缓存一致性/可见性**：CPU/Ara/LLC 中的副本与 DDR 中的数据何时一致。

NPU/ISP 仅使用普通 AXI4 DMA 时不必支持 AMO/ATOP。它们可以绕过 LLC，接到 DDR 前的第二级互连：

```text
CVA6/Ara → 原 SoC 互连 → 原子适配器 → LLC ─┐
NPU DMA ──────────────────────────────────┼→ DDR AXI4 互连 → 控制器/PHY
ISP DMA ──────────────────────────────────┘
```

这是拟议拓扑，不是当前工程已经存在的连接。新的互连需要处理 ID 唯一性/响应路由、位宽、并发、回压、公平性、跨时钟及复位，不是把请求线直接并接。绕过 LLC 消除的是该路径对 LLC 的分配/替换压力，不会消除 DDR 带宽争用；CPU 自己访问同一缓冲区仍可能污染缓存。

<a id="82-第一版推荐的存储使用规则"></a>

### 8.2 初始方案的存储使用约定

| 数据 | 建议管理方式 |
| --- | --- |
| CPU 常规代码、堆栈、私有数据 | 维持原 CPU/Ara 存储路径 |
| 图像帧、tensor 大缓冲区 | 独立 DDR 物理区间，CPU/Ara 访问时保证相关缓存层均不缓存，或用已验证的缓存维护协议 |
| 命令/完成通知 | MMIO doorbell/状态寄存器和中断，定义发布与完成顺序 |
| 必须由 CPU 与设备共同原子修改的锁/计数器 | 不走未经设计的旁路；另设真正共享的原子访问域/专用同步模块 |

首选“明确的缓冲区所有权 + 不缓存的共享 DMA 区 + MMIO 通知”。性能需求明确后再优化 CPU 缓存共享缓冲区。

**“不缓存”是待实现和验证的系统属性，不是写个 C 指针修饰符就成立。**必须检查 CVA6 的可缓存范围/属性产生、Ara 路径、LLC 地址规则和新 DDR 路由。Linux 以后也不能只设置 PTE 或 `volatile` 就默认整个系统都不缓存。

本地 LLC 通过 `cached_start_addr_i`/`cached_end_addr_i` 等规则控制路径；不能凭 AXI 名称假定只改 `AxCACHE` 就可选择性旁路。`Cfg.LlcOutRegionStart/End` 同时涉及 SoC 派生映射，若缩小范围必须检查 CPU 对 DMA 区的请求是否还能路由到 DDR，而非变成 decode error。必要时为 DMA 区添加显式旁路地址路由。本文不预定 DMA 区的具体地址和大小。

避免同一物理页存在一条可缓存别名和一条不缓存别名；共享区按实际 cache line 边界隔离，不能让设备缓冲区与 CPU 锁/普通变量共用一个可能被写回的 cache line。

<a id="83-上游原子适配器不能替旁路提供的保证"></a>

### 8.3 旁路路径的原子可见性边界

- CPU 在某地址执行 AMO，设备旁路普通写同一地址：适配器看不到该写，不能宣称系统级原子性仍成立。
- CPU 执行 LR 后，设备通过旁路写 reservation 相关位置：上游 reservation 监视器可能不知道，SC 成功/失败语义不能按完整共享域来保证。
- 即使设备从不发 AMO，其普通写也可能破坏上述保证。
- 若设备只操作隔离的数据区，且 ownership 期间 CPU 不并发访问，CPU 在其他不受旁路影响的内存上的原子操作并不会因此一概失效。

不能简单把原子适配器移到 LLC 后面解决问题：本地 LLC 不支持直接处理上游原子事务，而且 cache hit 可能根本不访问下游。DDR 前加第二个原子单元同样不能修复 CPU cache 的旧副本。若确实需要设备/CPU 共同原子访问，必须让该地址的全部相关访问在无缓存旁路或真正一致的路径上汇合，再确定原子适配器位置和请求者 ID 规则。

原子适配器官方使用说明要求下游对对应内存位置具备所有权/一致性保障，见 [axi_riscv_atomics](https://github.com/pulp-platform/axi_riscv_atomics)。

<a id="84-必须定义的生产者消费者时序"></a>

### 8.4 生产者与消费者的交接时序

CPU 生产、NPU 消费：CPU 写输入 → 必要的 cache clean/写缓冲排空与屏障 → 确认数据到达共享可见点 → 写 doorbell → NPU 读。

ISP/NPU 生产、CPU 消费：CPU 交出缓冲区前处理旧缓存状态 → 设备写数据 → 等待所需 AXI 写响应并按控制器契约确认可见性 → 发布完成状态/中断 → CPU 执行必要的屏障和 invalidate → CPU 读。

`fence` 解决排序，不自动等同于清空所有 cache；本地向量 profile 的 L1 WT 也不意味着 LLC 是 WT。LLC 仍可能保有脏数据。不得依靠 `fence.i`、`volatile` 或中断到达本身替代完整协议。

若没有可用且已验证的分级 cache 维护机制，第一版应采用全路径不缓存的 DMA 共享区。不要先实现有缓存的共享缓冲区、再假设后续补一条 flush 即可。

## 9. 执行顺序与验收门槛

### 阶段 A：只提取并固定配置

交付：源码闭包、唯一固定配置/顶层、静态清单、最小软件/TB、来源清单、可执行构建入口。

通过标准：

- 新目录复制到另一位置后，所有实际构建输入都在新目录或显式工具/工艺库路径下。
- 实际编译展开无重复 package/module、无缺失 include、无意外 FPGA primitive、无旧路径引用。
- 无 Bender/联网步骤；归档文档可以提及 Bender，但执行路径不能依赖它。
- 从复位完成 Boot ROM/LLC 初始化；标量、向量、基本 DDR 模型访存、AMO/LRSC 测试有确定通过判据。
- 记录实际命令、工具版本、日志和失败项。没有仿真许可证时只交付静态检查结果并注明未验证，不伪造通过。

### 阶段 B：裁切产品不需要的模块

用户尚未给出完整外设保留表，不由 Agent 擅自决定所有删除项。先提供很短的保留/关闭表；明确无关的 FPGA 包装可在阶段 A 去除。

每个裁切项：先用配置禁用并编译展开/回归，核对地址/中断/Boot ROM/软件依赖，再从新目录文件清单移除无用源码。若类型引用使少量 package 必须保留，记录原因，不把它误认为硬件仍存在。

不要因“不需要 Cache”就删 LLC：它还提供 Boot 栈和 SPM；若真删，必须先实现独立片上 SRAM 并修改启动与链接布局。

只保留一个日常可构建的产品配置；阶段 A 的结果可作为提交/报告留档，不建立多套长期目标矩阵。

### 阶段 C：DDR 旁路与自定义 IP

先用 AXI master BFM 代替 NPU/ISP，验证第二级 DDR 互连和共享区协议，再接真实 IP。

至少覆盖：CPU 写→设备读、设备写→CPU 读、回压/多 ID/突发/字节写、CPU 与设备并发访问不同区域、共享区 ownership 交接、脏缓存行覆盖风险、复位/超时/错误响应、持续图像流下 CPU 服务延迟。对禁止的跨域原子共享明确测试/约束，不默认为支持。

### 阶段 D：工艺 IP 和流片流程

待 SRAM/DDR/PHY/标准单元等资料明确后替换技术模型，重新验证语义与时序，开展综合、CDC/RDC、DFT/MBIST、约束审查、等价、STA 和物理实现。目录名称含 `asic` 不代表这些已完成。

<a id="10-给后续-agent-的可直接使用任务摘要"></a>

## 10. 后续实施任务摘要

> 在保留当前工程不变的前提下，按本文在仓库内创建可独立搬迁的 `cheshire_ara_asic/`。第一阶段只实现固定 `cv64a6_imafdcv_sv39` + Ara 2 lanes / VLEN 2048 的源码剥离、静态 filelist、通用 SoC wrapper、最小软件与仿真闭环。允许把本地 Bender 当作一次性离线依赖解析器，不要升级依赖、修复旧工程所有脚本或新建包管理框架。保留来源/许可证/头文件/DPI/生成 RTL。不要把 VCU118 专用器件带进 ASIC RTL。不要同时改变 CPU profile、内存映射、缓存拓扑和启动协议。先给出新目录的实际编译/仿真结果，再进行用户确认的外设裁切与 NPU/ISP DDR 旁路改造；明确所有未验证项。

交接报告只需回答：新目录在哪里、固定配置是什么、怎么构建运行、哪些测试通过、还缺什么。不要再要求用户系统学习 Bender。
