<a id="cheshireara-软件学习与使用手册"></a>

# Cheshire/CVA6/Ara 软件参考手册

本手册说明 `sw/` 软件目录、工具链、链接布局、程序启动、库接口及示例执行流程。

基准日期：2026-09-20；输入提交：`379ae4544bc62e05a2736b11b33a3244181bba38`。依据当前本地源码和工具查询整理；**本轮未编译应用、未运行仿真、未连接板卡、未烧写存储器**。命令标为使用示例，不代表已经跑通。硬件配置另见 [配置手册](../configuration/README.md)。

## 1. 阅读路线

| 顺序 | 文档 | 学习目标 |
| --- | --- | --- |
| 1 | [工具链、SDK 与编译](BUILD_AND_SDK.md) | 分清裸机/Linux 软件；理解 gcc、ar、链接器、ELF，选择单个构建目标 |
| 2 | [链接、启动、加载与调试](RUNTIME_AND_DEBUG.md) | 追踪 reset→Boot ROM→应用 _start→main→退出码；会查链接地址与异常 |
| 3 | [嵌入式库原理与 API](LIBRARIES.md) | 理解 MMIO、UART/printf、CLINT、DMA、LLC、AXI RT、HAL 与 GPT |
| 4 | [示例程序逐项导读](EXAMPLES.md) | 当前 9 个主测试源码逐项流程、前置配置、预期结果和局限；Ara 源码索引 |

第一次动手按 `helloworld → ELF/链接布局 → dma_2d → DRAM 程序 → 正确向量组合` 的顺序。AXI RT、CLIC、MMU stub 测试各有专门硬件条件，不应一开始执行全目录。

<a id="2-当前目录的职责"></a>

## 2. 软件目录与职责

| 路径 | 当前内容 | 初学者怎么用 |
| --- | --- | --- |
| [sw.mk](../../sw/sw.mk) | 软件编译、库归档、链接与镜像规则 | 从这里查实际参数和目标 |
| [include](../../sw/include) | util/params/smp、DIF/HAL 头文件、生成寄存器定义 | 区分地址、寄存器偏移与 API |
| [lib](../../sw/lib) | crt0、UART/CLINT、器件 HAL、GPT；已有 .o/.a | 阅读源码，旧产物不作为当前编译证据 |
| [link](../../sw/link) | common.ldh 与 spm/dram/rom 三种脚本 | 选择放置区域；名字后缀有实际含义 |
| [tests](../../sw/tests) | 9 个当前 .c/.S 主程序、RVV 辅助头/body、Python 数据脚本、大量旧产物 | 按本手册逐项选一个学习 |
| [tests_wo_ara](../../sw/tests_wo_ara) | 8 个备份主程序及旧产物 | 不在 sw.mk 自动测试扫描目录中；不是当前构建开关 |
| [boot](../../sw/boot) | zsl/flash、设备树源码及旧 flash ELF | 理解多阶段启动；不是所有文件都是普通应用 |
| [deps/printf](../../sw/deps/printf) | 小型格式化输出库 | 通过 _putchar 接 UART |
| [deps/cva6-sdk](../../sw/deps/cva6-sdk) | 当前仅 install64 与备份目录 | 当前主要是已有 Linux 镜像；这里没有完整 SDK Makefile |
| [Ara 软件入口](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw) | RVV 裸机源、Linux SDK 源码入口、benchmark 规则 | 进阶使用，注意复制/删除测试源的既有行为 |
| [util](../../util) | OpenOCD、GDB、烧写脚本 | 主机端辅助工具；不运行在 CVA6 上 |

`sw/tests_wo_ara` 中 AXI RT 三例、CLIC 两例、DMA 一例与 `sw/tests` 对应源码相同；HelloWorld 和 MNIST 源码不同。目录名不能替代源码比较，复制旧目录并不会自动改变硬件是否有 Ara。

<a id="3-从-mips-工程迁移过来的概念对照"></a>

## 3. MIPS 与 RISC-V 软件环境对照

| 熟悉的概念 | 这里的对应物 | 需要特别注意 |
| --- | --- | --- |
| 交叉编译器与 ABI | riscv64-unknown-elf-gcc；-march/-mabi | RV64 不表示一定有 V；lp64d 要求双精度浮点调用约定 |
| 启动汇编 | Boot ROM 汇编 + 应用 crt0.S | 两个 _start 属于两个不同程序，不可混连 |
| 链接地址 | common.ldh + 三种 .ld | SPM 默认只链接 64 KiB，硬件阵列默认 128 KiB |
| CP0/异常寄存器 | mstatus/mtvec/mcause/mepc/mtval 等 CSR | 中断开关、浮点 FS、向量 VS 都要符合实际硬件 |
| 自定义总线寄存器 | 地址符号 + 生成 offset + volatile load/store | AXI/Reg 桥不会自动纠正错地址或错访问宽度 |
| DMA 完成 | 读取任务 ID、等待 DONE_ID | volatile/fence 不等于自动缓存一致 |
| 串口日志 | printf_→_putchar→uart_write | 不依赖 Linux 控制台，可能阻塞并影响计时 |
| 程序结束 | main 返回→_exit→SCRATCH2 | 没有操作系统进程退出，调试器不会必然自动停止 |

<a id="4-最小实践闭环"></a>

## 4. 程序构建、运行与验证流程

1. 记录当前 CPU profile、SoC 使能和 bitstream/仿真库来源；确定 SPM 已由 Boot ROM 初始化。
2. 查工具链路径和版本，阅读 [单目标构建](BUILD_AND_SDK.md)；先编 HelloWorld，避免混用不同 ISA/ABI 的旧 .o/.a。
3. 用 readelf/objdump 确认 `_start`、入口地址、代码和数据位置；对照 SPM/DDR 实体。
4. 仿真通过匹配的 loader 加载 ELF；板级通过团队已确认的 JTAG/UART 路径加载。烧录 FPGA bitstream 和下载 ELF 是两步。
5. 保存 UART 输出、程序返回码和实际输入版本；出现异常先看 mepc/mcause/mtval，再扩展程序。

[示例导读](EXAMPLES.md)列出每个程序的退出判据。有些程序只打印结果而始终返回 0，有些例程依赖专用验证硬件，不能统一把“退出 0”或“有 ELF”记成测试通过。

## 5. 与工程任务的关系

本轮是 L01 软件学习文档，不实施 S01 软件迁移、E01 独立工程提取或 V01 回归。项目状态见 [PROJECT_STATE](../PROJECT_STATE.md)，本轮检查与源码缺口见 [交接记录](../handoffs/2026-09-20_L01_software_guide.md)。后续迁移时保留当前软件作为对照，建立独立输出目录和明确的工具链版本。
