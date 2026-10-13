# L01 / 软硬件接口源码教程

## 修改记录

| 日期 | 角色 | 输入版本 | 修改与验证摘要 |
|---|---|---|---|
| 2026-10-13 | 专题作者 | `mp/ara-pulp-v2` / `c4162204cfee0c48b81158b4296860a678d92bec`；既有未提交状态见输入记录 | 新增8页HTML/Markdown、4张可编辑案例图；独立重编标量/RVV/HelloWorld及DMA编译探针；文档验证见下方证据 |

## 基本信息

- 任务沿用 **L01**。用户附件明确授权软硬件接口分析、连续教程编写、必要配图及复用最小案例验证；功能修复留待后续。未新建任务ID，未启动子Agent。
- 状态：教程与配图已交付；软件编译完成；目标运行及功能缺陷仍待验证。
- 输入与保护：[input.json](../software/interfaces/evidence/input.json)记录分支、HEAD、原始status及关键既有文档哈希。其他对话已有文档修改、图稿迁移删除和未跟踪模块指南，未覆盖或清理。
- 负责路径：`docs_codex/software/interfaces/`、`docs_codex/diagrams/2026-10-13_software_hardware_interfaces/`、本交接；仅在`software/README.md`补充专题导航及范围说明。

## 本轮结果

正式说明见[HTML入口](../software/interfaces/index.html)／[Markdown入口](../software/interfaces/markdown/index.md)，顺序为构建启动、指令/Ara/CSR、内存/MMIO、异常中断、五案例、IP/Linux修改导航、最小实践。详细技术内容不在本交接重复。

| 结论/问题 | 等级与依据 | 边界/接收任务 |
|---|---|---|
| 根规则默认标量profile，VCU118清单选择向量profile/2 lanes/VLEN2048，保存的仿真清单仍有profile/decoder匹配问题 | 当前源码；[基线](../software/interfaces/index.html#baseline) | `SELCFG=3`不能替代重新编译正确CPU；V01验收输入身份 |
| UART真实访问为LSR的`lbu`与THR的`sb`，追到Reg/APB译码、FIFO和UART_TX | 本轮HelloWorld重编反汇编+静态RTL；[案例](../software/interfaces/cases.html#uart) | 不是本轮串口运行/板测 |
| DMA内部Reg DW64与生成DW32不一致，ID指针为uint64_t而地址仅4字节对齐 | 源码与本轮`probe_next/probe_done`的两次`lwu`；[DMA案例](../software/interfaces/cases.html#dma) | 延续既有门槛；S01/V01观察双读与副作用，另行修复 |
| 普通`sys_dma_memcpy()`的reps=0在当前2D前端/ND midend中可能无搬运却退休ID | **新增静态风险**：`sw/include/dif/dma.h`；`target/rtl/idma_reg64_2d_top.sv::enable_nd/reps`；`idma_nd_midend.sv::zero/burst_req_valid/ND_MIDEND`；`cheshire_idma_wrap.sv::nd_rsp_o()/idma_nd_rsp_valid` | 未仿真；错误内容未回传而DONE_ID依据响应握手推进。不能把普通1D API当作当前2D问题的替代方案；S01/V01最小波形确认 |
| GPIO INTR_TEST→PLIC→CVA6→trap→清源/complete→mret可静态追踪，但没有可直接运行的完整默认PLIC示例 | [中断案例](../software/interfaces/cases.html#gpio-irq)，含GPIO[0]当前源20的推导 | 本轮未新增ISR；CLIC例是另一配置，不能拼接为默认路径 |
| CPU/Ara有WT、acc一致性CSR、pending/barrier和写失效协作；不覆盖任意DMA/NPU | [内存章](../software/interfaces/memory-mmio.html)与[Ara章](../software/interfaces/instructions.html) | 尚未验证并发/错误响应；主交叉开关、LLC不能单独证明系统一致性 |
| 当前DTS与RTL配置有资源差异，内核配方和源码存在不证明Linux运行 | [集成章](../software/interfaces/integration.html)：PLIC数量、LLC窗口、ISA描述、SerialLink名称等 | S01核对选定DTS/内核/固件；无新Linux驱动、OS或地址决策 |
| Platform ROM返回、Boot ROM C栈对齐、CLINT sleep/read/compare、Reg桥窄读副作用 | 复核/引用已有分析；[缺口表](../software/interfaces/labs.html#gaps) | 功能修复未实施；源事实与动态后果分开 |

修改导航沿用最新[IP/DDR契约](../engineering/IP_DDR_Interface_Contract.md)：新增GB是独立存储体；NPU/GB搬运统一逻辑、DDR多个slave端口/位宽和Ara支路仍依赖确认与实施。C1–C9仅列建议的软件可见字段类别，未冻结地址、偏移、IRQ、频率、容量或OS。

## 改动与接口

- HTML正文是唯一编辑源；复用主教材标题/目录、Markdown导出器和CSS/JS，生成8对阅读页；未重建原51页主教材。
- [四张图](../diagrams/2026-10-13_software_hardware_interfaces/README.md)保存结构化SVG、生成脚本、原生PPTX、预览及检查记录。使用`svg-pptx-diagrams-native`技能；未调用外部消息工具。
- 无RTL、生产软件、依赖、filelist、地址、寄存器、中断、位宽或启动配置改动；无`.bender`升级/清理；未提交Git。
- 输出需保留仓库相对目录才能完整离线浏览源码链接；独立软件构建位于专题`evidence/`，不覆盖`sw/`旧产物。局部`.gitignore`保留日志、反汇编和ELF证据，临时对象/支持归档不入库。

## 验证证据

工作目录为仓库根；GCC为`riscv64-unknown-elf-gcc (g5115c7e44) 15.2.0`，完整flags/警告和产物哈希见[builds.json](../software/interfaces/evidence/builds.json)。三个构建命令实际退出0：

```sh
JOURNEY_OUT="$PWD/docs_codex/software/interfaces/evidence/scalar-build" bash docs_codex/learning/scripts/build_journey.sh scalar spm
JOURNEY_OUT="$PWD/docs_codex/software/interfaces/evidence/rvv-build" JOURNEY_DEPTH=1 bash docs_codex/learning/scripts/build_journey.sh rvv spm
bash docs_codex/software/interfaces/scripts/compile_probes.sh "$PWD/docs_codex/software/interfaces/evidence/hello-build" "$PWD/docs_codex/software/interfaces/evidence/scalar-build"
```

以上目录已含证据；复跑必须用新目录。HelloWorld链接本轮新编最小支持库，不是完整`libcheshire.a`重建。标量/RVV的text/data/bss分别为5328/796/548与6092/908/548 byte；SPM入口0x10000000，栈符号0表示继承。MMIO链接符号的`-Warray-bounds`与LD的RWX告警保留，不能称零警告。

```sh
python3 docs_codex/software/interfaces/scripts/build.py
python3 docs_codex/software/interfaces/scripts/check.py
python3 docs_codex/software/interfaces/scripts/preview.py --out-dir 新证据目录
```

- [源码身份](../software/interfaces/evidence/sources.json)：119个被引用文件及复用工具，不是全仓扫描或仿真结果。
- [定向文档检查](../software/interfaces/evidence/validation.json)：双格式生成一致性、链接/锚点、图片、源码/产物哈希和关键既有输入保护。
- [最终浏览器检查](../software/interfaces/evidence/browser-review/browser.json)：8页×1440/390宽度；4张SVG预览；作者逐图查看。PPTX只有结构检查，未执行Office显示/编辑验收。
- 首次Chrome受沙箱本机套接字限制退出，自动审批放行本机预览后继续；首次页面检查发现未套figure样式导致宽图溢出，已修复。`browser/`、`browser-pass/`保留失败证据，`browser-final/`、`browser-verified/`及中间export保存修正过程；最终记录以以上链接为准。
- **未执行SoC仿真、FPGA板测、Linux启动或ASIC验证**。未把用户历史VCU118 HelloWorld扩大为本轮验收。

## 决策与下一步

1. 用户先读构建启动与UART案例，用已有可靠平台运行独立SPM程序并保存实际输出、返回码和输入身份。
2. S01/V01先以最小波形确认DMA DW/ID拆读及reps=0路径；再决定修复，不直接运行完整DMA回归当作已可靠路径。
3. 在匹配默认PLIC硬件上补最小强`trap_vector`示例；CLINT、Platform ROM和窄读问题分别验收。
4. M01/P01按现行契约补IP端口manifest、初始化/错误恢复和所有权协议，地址/IRQ/OS等由用户后续确认。

共享`AGENT_TASKS.md`已有其他对话修改，本轮仅写独立交接；请C00按需在L01下合并“软硬件接口教程已交付、目标运行未验收”，并将上述DMA新增静态风险转给S01/V01。无新增用户架构决策需要冻结进共享状态。

终检观察到`AGENTS.md`、`L01_rtl_module_guide.md`及`maintenance/L01/planning/rtl_module_figures.md`在本轮期间出现外部修改；已重新读取AGENTS新增的RTL指南A版走线偏好，其明确不要求重绘其他系列。本轮未写这三个文件，保留输入哈希和终检差异，不恢复、不刷新原基线。

另核对实际清单选择的`idma_generated.sv`：其中`idma_reg64_2d`和`idma_backend_rw_axi`模块正文，与教程引用的独立top/backend文件逐字相同；确认以上DMA静态结论适用于清单中的拼接文件。首次文档检查发现Markdown导出器引用`scripts/pages.json`而专题尚缺该元数据，已补齐并作为唯一页面清单；失败记录保存在`evidence/validation-initial.json`。
