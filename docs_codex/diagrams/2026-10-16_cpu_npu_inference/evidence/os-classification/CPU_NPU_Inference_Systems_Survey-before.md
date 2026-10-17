# CPU＋NPU 异构 SoC 的模型推理体系调研

返回[工程参考](README.md) · 关联[OS 选型](Edge_LLM_OS_Selection.md)、[缓存一致性综述](CPU_NPU_Cache_Coherence_Survey.md)、[DDR/GB 契约](IP_DDR_Interface_Contract.md)

2026-10-16，L01。工程输入：`mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`，含已有未提交文档。本文调研通用推理，重点讨论小型 LLM；属于应用、基础软件和软硬件接口分析，必要时对照 SoC 实现。分层沿用[层次与工具](../software/LAYERS_AND_TOOLS.md)，开发主机上的模型编译工具与目标端运行软件分别描述。

**CPU＋NPU 推理依靠一套匹配的编译、执行和数据交接体系。** 编译器确定哪些工作适合加速器，运行时组织模型和张量，驱动或指令接口启动硬件，存储与同步机制保证结果能被下一阶段使用。Linux、RTOS、裸机可以承载不同实现，但都不能替代这些职责。对本项目，值得借鉴的是这些职责如何划分，以及如何逐步验证，而非照搬某个平台的总线或软件包。

下文的“官方事实”来自所列版本的公开资料；“工程事实”来自本地源码；“建议”尚未成为选型决定。未执行外部 SDK、模型推理、工程构建、仿真或板测。完整来源身份见[资料记录](../diagrams/2026-10-16_cpu_npu_inference/evidence/sources.json)及[补充记录](../diagrams/2026-10-16_cpu_npu_inference/evidence/sources-extra.json)，访问日期均为 2026-10-16。

## 1. 先沿一次推理看完整链路

以一个包含卷积或矩阵乘、激活、后处理的模型为例。开发主机读取模型图和权重，结合校准数据、目标精度和输入形状，生成适合目标硬件的表示。随后完成算子选择与融合、张量布局变换、分块和内存安排。输出可能是设备命令包，也可能是调用算子库的 C 代码；“编译模型”与交叉编译 CPU 程序是相关但不同的步骤。

目标端加载产物，分配或绑定输入、输出和工作区。CPU 可以同时承担模型调度与部分数学计算：例如输入处理、尚未加速的算子以及结果排序。选入 NPU 的子图通过平台接口提交，设备读取对应张量并执行。最后，等待机制报告任务状态，平台保证输出可见，应用再消费结果。多个子图可重复经历这一过程；能否重叠计算与搬运，取决于依赖、缓冲资源和硬件能力。[NVDLA 编译手册](https://nvdla.org/sw/compilation_tool.html)、[运行时手册](https://nvdla.org/sw/runtime_environment.html)

![模型部署与设备任务全链路](../diagrams/2026-10-16_cpu_npu_inference/deployment-chain.png)

图 1：依据 NVDLA、Ethos-U、ExecuTorch 与 Deeploy 的公开流程归纳重绘；表达逻辑职责，不表示它们采用相同接口。CPU 与 NPU 共享张量需要平台兑现地址、所有权和同步条件。[SVG](../diagrams/2026-10-16_cpu_npu_inference/deployment-chain.svg) · [四页原生可编辑 PPTX](../diagrams/2026-10-16_cpu_npu_inference/export/diagrams.pptx)

需要分别回答三个“谁来调度”：模型运行时选择下一段计算，设备软件或固件安排硬件任务，OS 调度 CPU 线程。三者粒度不同。线程可抢占不意味着 NPU 可中途抢占，图节点提交成功也不意味着结果已经落入可消费的内存。

“CPU fallback”同样有条件。框架必须保留相应 CPU 算子实现，并正确衔接精度、布局和内存；有些编译器遇到不支持的节点会失败，有些允许混合执行。不能把“编译成功”“调用成功”“使用了 NPU”和“全图由 NPU 执行”视为同一状态。[Vela 的 CPU 操作说明](https://arm-software.github.io/CMSIS-Ethos-U/main/vela/index.html)

## 2. 四组工业方案

### 2.1 NVDLA：模型包、驱动与硬件层调度

参考 NVDLA 官方软件手册和 `nvdla/sw` 提交 `79538ba1b5`（2019-09-30）。这是理解开放 DLA 软件组织的历史实现，不代表当前 NVIDIA 全产品软件栈，也不把 Jetson GPU 推理路径与 NVDLA 混为一谈。[软件仓库](https://github.com/nvdla/sw/tree/79538ba1b52b040a4a4645f630e457fa01839e90)

官方基础流程从 Caffe 网络及权重开始。解析器形成图，编译器依据目标配置将操作映射到硬件功能块，必要时按缓冲大小拆分，再输出 **loadable**。它不只是权重文件，还携带硬件操作、张量缓冲及依赖信息。不同配置能否运行该产物，取决于功能与资源匹配；可解析格式不等于硬件能执行全部内容。[编译手册](https://nvdla.org/sw/compilation_tool.html)

以 headless Linux 为例：CPU 上的用户态运行时加载 loadable，绑定输入输出，提交 DLA task；内核驱动接收任务，engine scheduler 根据依赖配置功能块。硬件完成事件经中断处理推动后续操作，最终向调用方交付任务结果。计算功能块的数据读取由其 DMA 路径完成，CPU 不必逐个搬运元素。官方接口区分 CPU 可访问地址、设备可访问地址和内存句柄，并提供 DRAM/SRAM 内存类别。[运行时手册](https://nvdla.org/sw/runtime_environment.html)

工程启示是把图执行、设备调度和 OS 适配拆开。官方还讨论由伴随微控制器运行调度软件的 headed 组织，以及替换平台适配层的可能性；这不构成任意 FreeRTOS 平台已经移植通过的证据。[NVDLA Primer](https://nvdla.org/primer.html)

**适用边界：**该路线主要展示 CNN/DLA 部署。不能因存在矩阵相关计算，就声称原版编译器可直接接收任意 Transformer、动态序列或现代 LLM 量化格式。遇到不支持的操作，需要确认解析器、外层图划分和 CPU 实现，不能假设 KMD 自动补算。

### 2.2 Ethos-U：编译出的 NPU 子图嵌入轻量框架

参考 CMSIS-Ethos-U Cortex-M 集成文档，仓库身份为 `b2b641ee93`（2026-10-02）；实际芯片仍需绑定具体 Ethos-U 型号、Vela、驱动和内存配置。Vela 在开发主机上将量化模型转换为目标相关的命令流和编码常量。TFLite 路径中，可支持区域成为 Ethos-U custom operator，其余区域保留为 CPU 操作；TOSA 路径没有相同的 CPU fallback 机制。[Vela](https://arm-software.github.io/CMSIS-Ethos-U/main/vela/index.html)

目标端应用调用 TFLM 的模型执行入口。遇到普通节点时调用 CPU kernel，遇到 Ethos-U 节点时交给集成代码及 core driver。驱动接收命令数据和内存区域基址，启动设备并处理完成或故障通知。接口提供同步调用以及异步提交/等待；单线程裸机和 RTOS 对等待与锁的实现不同，不需要据此改变模型数学含义。[驱动接口](https://arm-software.github.io/CMSIS-Ethos-U/main/driver/index.html)

常量、tensor arena 和可选快速 scratch 的位置需要与 Vela 的 memory mode 一致。CPU 指针与 NPU 地址若不同，还需要平台地址转换；共享缓存数据则需实现相应维护钩子。编译器规划的 NPU SRAM 使用量不能直接当作全系统内存，因为 CPU 栈、应用和框架仍会占用空间。[集成说明](https://arm-software.github.io/CMSIS-Ethos-U/main/integration/index.html)

**适用边界：**这证明 MCU 环境可以组织完整的异构推理，并不证明任意 Ethos-U 型号支持本项目拟用的 LLM。需检查实际的 CPU 节点清单、算子形状、量化约束及峰值 arena；“使用 TFLite”也不自动满足这些条件。对本项目可借鉴的是自定义算子与设备适配边界，而不是直接复用其命令编码。

### 2.3 Rockchip：通用模型与 LLM 使用各自部署链

以 RK3588 所属支持平台为例，核对 RKNN-Toolkit2 `v2.5.0` README 所在提交 `2c723177a9`，以及 RKLLM `v1.3.1` README 所在提交 `f739053044`。二者是分别取证的软件版本，不能仅凭编号认定所有二进制、驱动与模型已相互兼容。[RKNN 仓库](https://github.com/airockchip/rknn-toolkit2/tree/2c723177a94fac65cbc036d722907ddbc91980cf)、[RKLLM 仓库](https://github.com/airockchip/rknn-llm/tree/f7390530443bf84f0394255a449d7cbe81e69d1c)

通用模型由主机 RKNN-Toolkit2 转换为 RKNN 模型，板端通过 Runtime C/C++ 接口或 Lite2 Python 接口使用；RKNPU 内核驱动负责与硬件交互。公开 C API 能看到初始化、输入绑定、运行、取得输出和销毁，以及内存绑定和同步相关接口。因此，“共享缓冲/减少复制”仍有格式和可见性契约，不能仅把已有指针传进去就视为零开销。[RKNN API 头文件](https://github.com/airockchip/rknn-toolkit2/blob/2c723177a94fac65cbc036d722907ddbc91980cf/rknpu2/runtime/Linux/librknn_api/include/rknn_api.h)

LLM 则通过 RKLLM-Toolkit 做转换与量化，生成 `.rkllm`，板端使用 RKLLM Runtime。其公开 API 包含 `rkllm_init`、`rkllm_run`、异步运行、结果回调、取消及 KV 管理。这表明接口面对的是带持续状态的生成任务，应用还要管理上下文和会话生命周期。官方多模态示例把视觉编码器的 `.rknn` 与语言部分的 `.rkllm` 组合，而非把所有模型统一交给一个通用入口。[RKLLM 部署示例](https://github.com/airockchip/rknn-llm/blob/f7390530443bf84f0394255a449d7cbe81e69d1c/README.md)、[RKLLM API](https://github.com/airockchip/rknn-llm/blob/f7390530443bf84f0394255a449d7cbe81e69d1c/rkllm-runtime/Linux/librkllm_api/include/rkllm.h)

**适用边界：**公开资料支持上述工具和调用链，却不足以完整确认每个模型内部的 CPU/NPU 分工、KV 物理布局及固件调度。应标为未公开或待核查。对本项目的启示是把“可部署模型范围、编译产物、板端运行库、驱动版本”作为一个组合验收，而非只有 NPU RTL 和几个寄存器。

### 2.4 Qualcomm QNN＋ExecuTorch：框架委派给厂商后端

采用 ExecuTorch **1.0** 文档和 `v1.0.0` 提交 `8c84780911`，避免把浮动的 stable 页面当固定版本。该文档采用 QNN 2.37.0 作为已验证建议组合，示例覆盖特定 Snapdragon 平台；这是外部参考版本，不是本项目升级要求。[Qualcomm 后端文档](https://docs.pytorch.org/executorch/1.0/backends-qualcomm.html)

开发主机通过 `torch.export` 捕获模型，按目标需要量化，并指定 SoC 与后端选项。QNN partitioner 判断节点支持情况，把可委派子图交给 QNN 编译路径，最终保存包含委派计算的 `.pte`。在目标端，ExecuTorch 加载程序，通过 Qualcomm backend 调用 QNN/HTP 运行库，把计算送往 Hexagon。这里的“后端”同时涉及编译时降低模型表示和运行时执行，两侧都要匹配。[部署与量化流程](https://docs.pytorch.org/executorch/1.0/backends-qualcomm.html)

源码中 `QnnOperatorSupport` 会使用节点转换器及 QNN 支持查询；`QnnPartitioner` 再为相应节点标记委派关系，并处理常量和可变缓冲。这与“遇到任何不支持节点就自动在 CPU 无缝完成”不同：剩余图还需有可执行 kernel，子图边界必须满足形状、布局和数值约束。KV 一类可变状态也不能按普通只读权重处理。[固定版本 partitioner](https://github.com/pytorch/executorch/blob/8c84780911e7f4e9eb19395181b04761392a4b56/backends/qualcomm/partition/qnn_partitioner.py)

**适用边界：**公开文档足以说明模型到委派运行的接口，但不能据其推断闭源 HTP 固件的全部任务队列、内部 SRAM 和抢占方式。CPU 承担框架、提交、输入输出及实际保留的计算；具体比例要测量。对本项目可借鉴框架后端的组织，不能把 QNN 二进制用于自有 NPU，也不能把增加 Linux 驱动等同于完成框架适配。

![NVDLA、Ethos-U 与 Gemmini 的调用路径](../diagrams/2026-10-16_cpu_npu_inference/invocation-paths.png)

图 2：依据 NVDLA 运行时手册、Ethos-U 驱动说明及 Gemmini README/C 库归纳重绘。三列分别表示设备驱动、轻量框架 custom op、自定义指令路径；省略 CPU 普通访存。Gemmini 详见下一节。[SVG](../diagrams/2026-10-16_cpu_npu_inference/invocation-paths.svg)

## 3. 三组学术与开源方案

### 3.1 Gemmini：可由软件安排搬运的矩阵加速器

Gemmini 是 Chipyard 生态的全系统研究平台，本文使用提交 `8c3f9923a4`。其软件提供矩阵、卷积等调用和裸机、Linux、proxy-kernel 程序构建路径；后者应按其实际系统调用能力理解，不能当作完整 Linux。官方区分 Spike 功能验证与周期级仿真，功能结果不等于性能证据。[Gemmini README](https://github.com/ucb-bar/gemmini/blob/8c3f9923a44a2fe2c7930587be297d6d4f8c09ca/README.md)

这里不强制先产生类似 NVDLA 的网络包。应用可直接调用 C 算子库，库根据硬件参数安排分块，宏发出 RISC-V 自定义指令，经 RoCC 进入 Gemmini。`mvin` 把主存数据搬入本地 scratchpad 或 accumulator，计算命令操作阵列，`mvout` 将结果写回。DMA 与 SoC 存储层次连接；控制指令和大块张量传输是两条不同职责的路径。[C 库源码](https://github.com/ucb-bar/gemmini-rocc-tests/blob/2b7cc09e7813518aa99c0d260e72fa526a892227/include/gemmini.h)

CPU 还负责程序控制、非阵列计算和必要同步。scratchpad 是显式管理的本地存储，软件须遵守容量、布局、分块和数据依赖。高层模型能覆盖到什么程度，取决于库和框架适配，不由脉动阵列自动保证。Gemmini 的硬件生成参数也会影响软件可用的尺寸和数据类型，编译程序时必须使用对应参数头文件。

**适用边界：**RoCC/TileLink 与本项目 CVA6/Ara/AXI 的接口不同。可以研究它的分块库、搬运与计算协同、测试组织；不能把现有 `cvxif` 命名端口当作可直接插入 Gemmini 的接口。其 CNN/矩阵测试也不能证明本工程已支持 LLM。

### 3.2 Deeploy＋Siracusa：把存储与异构调度编进程序

依据 Deeploy 论文 `arXiv:2408.04413v1`（2024-08-08）、Siracusa 硬件论文及作者代码。论文中的部署流程从量化 ONNX 出发：选择算子模板和执行资源，再联合安排分块与静态内存，生成含 DMA 与同步操作的 C 代码。目标端因而可以使用较少运行时支持，复杂决策更多发生在编译阶段。[Deeploy 论文 §III](https://arxiv.org/html/2408.04413v1)、[作者仓库](https://github.com/pulp-platform/Deeploy/tree/0d6d4e2ae1adebcf72ab5d0e2621b9f51e080718)

![Deeploy 与 Siracusa 的计算及存储协作](../diagrams/2026-10-16_cpu_npu_inference/deeploy-siracusa.png)

图 3：依据 Deeploy 论文 Fig. 1、Fig. 5 和 §V 归纳重绘。互连框合并表达 TCDM 访问与仲裁职责，省略端口细节；主控到集群为任务派发关系。NMS 是 Siracusa 的权重存储，不能直接等同于本项目 GB。[SVG](../diagrams/2026-10-16_cpu_npu_inference/deeploy-siracusa.svg)

Siracusa 包含主控核、8 核 RISC-V 计算集群、N-Eureka NPU、多 bank L1 TCDM、L2 和 NMS。CPU 集群与 NPU 可访问 TCDM，仲裁决定冲突访问的服务；DMA负责 L2/L1 搬运，NMS 为 NPU 提供单独的权重供给路径。这里的 L1/L2 是软件管理的存储层次，不能套用 CVA6 L1D/LLC 的透明缓存语义。[Siracusa 论文](https://arxiv.org/html/2312.14750v2)

在论文的 Transformer 部署中，编译期常量权重的线性层被改写为 N-Eureka 可执行的 1×1 卷积；其他计算由集群 kernels 承担。编译生成的分块代码组织激活与 KV 等数据的搬运，使用 NMS 的方案将相应线性层权重放入 NMS。这个映射有操作数和布局条件，不能推广成“所有动态矩阵乘都可以直接变成卷积”。[Deeploy 论文 §V-B、§V-C](https://arxiv.org/html/2408.04413v1)

**适用边界：**论文报告的是 Siracusa 原型上的特定 TinyStories 模型，给出的结构为 8 个 decoder 层、隐藏维度 64、FFN 中间维度 256，并采用整数化路径；它不是本项目假设的 0.5B～3B 模型。本文不引用其 tokens/s 预测本项目，也不把后续仓库 HEAD 当作论文测量时的代码。可借鉴的是算子模板、存储层级和调度共同建模，尤其适合进一步评估 Ara/NPU/GB 的分工。

### 3.3 llm.npu：围绕移动 NPU 约束优化 prefill

依据 *Fast On-device LLM Inference with NPUs*，`arXiv:2407.05858v2`（2024-12-15）。论文主要解决输入提示较长时的 **prefill** 延迟，并利用移动平台 CPU/GPU/NPU 协同；不是只含 CPU＋NPU 的硬件案例。其经验可用于思考异构划分，但移植到没有已确认 GPU 的本项目时，需要重新评价计算去向。[论文](https://arxiv.org/html/2407.05858v2)

它将可变长度 prompt 分成固定大小块，使用预先准备的子图，同时保持因果依赖，以降低不同输入长度带来的图准备成本。在张量层面，把对精度敏感的离群值相关计算分离给 CPU/GPU，其余适配整数计算交给 NPU；在块层面，依硬件适配性与精度需求调度。这里的乱序安排遵守依赖，不是改变自回归语义，也不是任意交换 Transformer 层。

这类切分增加了合并、同步和存储安排问题。CPU/GPU 算出的部分结果必须与 NPU 结果按正确精度和顺序合并；多份预编译图也可能增加模型相关内存。因而“更多计算卸载到 NPU”与“端到端更快”不是同义词，应同时观察图准备、额外副本和交接成本。

作者维护的 [mllm](https://github.com/UbiquitousLearning/mllm/tree/1d3c3d8e506e3d12e902af82866972623b240ce0) 提供移动模型运行实现和后端支持矩阵；本文记录的仓库提交为 2026 年快照，已晚于论文。复现实验必须另行固定论文对应代码与模型，不能混用最新版功能和旧论文数字。

**适用边界：**论文的 prefill 加速不能写成相同倍率的 decode 或整体对话加速。Ara 是否适合承担离群值、归一化、Softmax 或采样中的某一部分，是本项目的候选研究方向，当前证据不足以确认收益。

## 4. 横向比较：相同职责如何落到不同实现

| 方案 | 主要部署产物 | CPU 与 NPU 的交接方式 | 数据组织重点 | 主要适用边界 |
|---|---|---|---|---|
| NVDLA | loadable | UMD → KMD / engine scheduler → 功能块 | 张量地址、依赖与硬件层配置 | 历史 CNN/DLA 路径，LLM 需另证 |
| Ethos-U | 含 custom op 的 TFLite / 命令流 | TFLM → core driver → NPU | arena、常量、scratch 与 memory mode | 回退与算子覆盖依模型格式、型号 |
| Rockchip | `.rknn` / `.rkllm` | Runtime → RKNPU 驱动 | SDK 内存接口、模型与会话状态 | 工具、运行库、驱动须组合匹配 |
| Qualcomm | 含后端计算的 `.pte` | ExecuTorch delegate → QNN/HTP | 子图边界、量化、常量与可变缓冲 | 闭源内部调度不由公开 API 推断 |
| Gemmini | RISC-V 程序及模型数据 | C 库 → 自定义指令 / RoCC | 分块、scratchpad、accumulator、DMA | 不是 AXI 外设接口的直接替代品 |
| Deeploy | 生成的 C 程序与权重 | 生成代码 → CPU kernels / NPU 控制 | 静态分配、分块、显式搬运 | 需为目标建立模板与存储模型 |
| llm.npu | 分块模型图与运行软件 | CPU/GPU/NPU 协同 | 离群值、子图复用、依赖与合并 | 主要针对 prefill，平台含 GPU |

共同点是“把可执行的计算与数据安排一起交给目标”。差别主要在决策发生时间和控制接口：Deeploy 更强调提前生成程序，框架 delegate 保留图执行组织，Gemmini 向应用暴露较直接的指令与分块库。它们可以互相借鉴；采用一种 NPU 命令接口，并不要求同时采用同一个 OS 或高层模型框架。

## 5. 从视觉模型转到 LLM，还需解决什么

![LLM 阶段及异构分工](../diagrams/2026-10-16_cpu_npu_inference/llm-phases.png)

图 4：上部按自回归执行关系归纳，prefill 结果经采样得到首个输出，后续 token 进入 decode；下部根据 llm.npu §3 重绘其特有优化，省略详细子图调度。KV 箭头是算法数据读写，不是硬件缓存探测。[SVG](../diagrams/2026-10-16_cpu_npu_inference/llm-phases.svg)

**阶段与形状。** Prefill 可利用多个输入 token 的并行计算；decode 在低批量下每步工作形状不同，权重和历史 KV 读写可能成为主要开销。固定大小图、长度档位或分块都可以作为候选，但填充、额外图存储及切换有成本，必须测量。Deeploy 与 llm.npu 的案例分别说明了存储管理与图准备的重要性，不能仅以峰值 TOPS 判断能力。

**持久状态。** CNN 中间激活常可在最后一个消费者结束后释放；KV 跨生成步存活，须维护有效长度、会话归属和复用条件。算法 KV、CPU 硬件缓存和独立 GB 是不同对象。KV 可以存在 DDR，在需要时分块进入 GB；也可以部分驻留，具体取决于容量和使用模式。本项目尚未选择该方案，容量公式和假设算例见 [OS 专题 §3.2](Edge_LLM_OS_Selection.md#32-权重与-kv-内存预算)。

**精度与算子。** 低位宽权重文件并不保证 NPU 原生执行同位宽运算。解包、scale、累加位宽、反量化、转置及剩余算子都可能消耗 CPU/Ara 或额外存储。QNN 的支持检查、Vela 的 CPU 操作报告和 llm.npu 的离群值处理说明，应以具体后端的可执行组合为单位判断覆盖，而非只列出“支持 INT8/INT4”。

**分工代价。** 对一段原在 CPU 执行的子图，可用下式整理测量边界，而非直接预测速度：

```text
卸载收益 = 原 CPU 时间 − 新路径关键路径时间
新路径包含：准备/转换、提交、必要搬运、NPU 执行、同步及剩余 CPU 计算
```

存在重叠时应测关键路径，不能把所有活动时间机械相加。逐个小算子往返设备可能得不偿失；保留连续子图和中间结果驻留通常值得评估，但不支持的操作不能为减少交接而被忽略。排序、采样是否交给 CPU，也应结合结果大小判断。近期讨论的“设备先缩减候选、CPU 再排序”可作为具体测量场景，见 [GB/CPU 访问专题](Global_Buffer_CPU_Access.md)。

**正确性与异常。** 发布输入必须先满足可见性和顺序，再启动设备；完成必须包含所需写回和同步，才允许消费或回收缓冲。硬件一致性不会自动完成张量布局变换，也不会使独立 GB 快照随 DDR 修改而更新。取消或进程退出时仍须处理在途 DMA，避免迟到写污染已复用内存；这些职责在裸机、RTOS、Linux 下都存在。[Linux 6.5 DMA API](https://docs.kernel.org/6.5/core-api/dma-api-howto.html)、[本项目一致性条件](Cache_Coherence_Architecture.md)

## 6. 映射到 Cheshire＋CVA6＋Ara

本地源码身份来自 [.bender 快照清单](../../.bender/SNAPSHOT.tsv)：Ara `2895ba907e`、CVA6 `99eac9a649`，目录后缀不是提交号；还须考虑本地差异。本文只核对涉及职责，不重复建立地址图或重跑历史实验。

| 外部机制 | 本工程已有基础与源码依据 | 候选新增职责 | 待验证事项 |
|---|---|---|---|
| CPU 执行模型控制 | [向量 profile](../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/include/cv64a6_imafdcv_sv39_config_pkg.sv) 含 MMU、S/U/V；[软件构建](../../sw/sw.mk)与[启动代码](../../sw/lib/crt0.S)存在 | 选定运行时、模型加载与应用生命周期 | 实际 profile、算子结果、内存峰值；不能用配置存在代替运行 |
| 向量算子后端 | [SoC](../../hw/cheshire_soc.sv) 的 `gen_ara/i_ara` 接收 CVA6 加速器请求；普通向量访存经过失效过滤、宽度转换接主 Xbar | 按当前 RVV 工具链实现和选择 Ara kernels | 数值、指令覆盖、FS/VS 与任务上下文；Ara 不是 MMIO 启动的 NPU |
| NPU 设备提交 | SoC 有外部 AXI master/slave、Regbus 扩展连接；[配置包](../../hw/cheshire_pkg.sv) 中 `CvxifEn=0` | NPU 命令生成、驱动、完成/错误与模型后端 | 扩展端口不等于 NPU 已接入；不直接套用 RoCC 或 QNN |
| 共享片上存储与显式搬运 | [契约 §12](IP_DDR_Interface_Contract.md#12-独立global-buffer与ddr需求更新)要求独立 GB、主 Xbar 64-bit 及设备 DDR 旁路；当前 Ara 代码仍接主 Xbar | GB 分块、共享数据代理、DDR–GB 搬运及同步契约 | 容量、bank、仲裁、地址、错误；现有 iDMA 不直接等同于新搬运器 |
| OS 与平台适配 | [Ara SDK 规则](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/cva6-sdk.mk)有 `RVV_LINUX=1`、Linux 应用和镜像入口 | Linux 驱动、缓冲映射与用户态接口；裸机诊断适配 | Linux 启动、镜像溯源、RVV 抢占和 NPU 推理均未由本轮验收 |

**最新需求与旧图的关系：**2026-10-16 的[一致性专题及交接](../handoffs/L01_cache_coherence_architecture.md)明确 Ara 访问 GB 应经过也服务 NPU/ISP 的共享数据代理，且该代理与 DDR–GB 搬运器是不同职责。本文映射采用这一更新，不将旧契约示意中的简化连接解释为最终直连，也不把另一对话提出的一致性候选当作已选方案。当前源码仍没有这一 GB 分支，需求与实现必须分列。

官方 Linux 路线提供平台起点，并未交付面向新增 NPU 的编译器、模型运行时或驱动。现有 `i_ara_axi_inval_filter` 也不是面向任意设备的完整一致性系统。外购 DDR、共享代理、设备旁路和缓存协调仍需按契约实现并验证；用户报告的 VCU118 HelloWorld 不扩大解释为这些功能验收。

## 7. 建议的落地顺序与最小验证

**设计建议：先选代表工作负载，再形成能贯通的最小软件链。** 模型结构、精度、最大上下文、质量底线、首 token/逐 token 目标和 DDR/GB 预算未定时，不冻结框架或算子分工。延续 [OS 专题](Edge_LLM_OS_Selection.md) 的建议，保留裸机验证基线，评估精简 Linux 承载完整应用；RTOS 是否更合适仍由产品约束决定。

第一步，用 CPU 参考实现和固定输入建立结果基准，再验证一个代表性矩阵/卷积算子。检查权重打包、scale、布局、对齐和尾块，不只选完全匹配阵列大小的输入。Ara 与候选 NPU 分别比对，避免在全模型失败时无法区分数学和设备交接问题。

第二步，贯通“分配与地址准备—发布—搬运/计算—完成—消费—回收”，验证 DDR/GB 边界、CPU 介入、超时、错误与重复提交。接口应表达缓冲生命周期、任务身份和有效结果范围；本次只提出职责，不定义寄存器、ioctl 或新的 C ABI。

第三步，再接连续子图与完整模型，分别测冷加载、图准备、prefill、decode、后处理。记录峰值内存、CPU/Ara/NPU 时间、DDR 有效字节、GB 复用、质量变化及失败恢复。若端到端收益不足，先缩小卸载范围或改变分块，保留已验证 CPU 路径作为对照；不能通过隐藏同步或放宽正确性制造加速结果。

| 最小场景 | 判据与应记录的数据 |
|---|---|
| 支持/不支持算子混合 | 明确分配、CPU 实现或清楚报错；不能静默丢失节点 |
| 非整块尺寸与上下文边界 | 尾块/填充正确；最大长度处无越界，KV 有效范围正确 |
| CPU ↔ NPU/Ara 数据交接 | 缓存开启及不同交接顺序下结果可靠；不凭 IRQ 推定可见 |
| 输入和模型重复使用 | 生命周期、工作区复用与会话隔离正确；不污染历史 KV |
| 设备失败或取消 | 错误可上报；确认迟到访问停止后才回收缓冲，恢复后新任务正确 |
| 性能与质量比较 | 固定模型、精度、输入、频率和测量边界，同时报告质量、延迟与内存 |

以上是 S01/I01/M01/V01 后续评估输入，不是已执行结果。本文不指定采购 IP、不升级 `.bender`，也不改变固定配置与静态清单迁移方向。实际文档、来源与图稿检查见[主题交接](../handoffs/L01_cpu_npu_inference_survey.md)；四张图均为资料归纳重绘，编辑与复现入口见[图稿说明](../diagrams/2026-10-16_cpu_npu_inference/README.md)。
