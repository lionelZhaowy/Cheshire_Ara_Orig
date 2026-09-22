# L01 交接：软件学习与使用手册

## 基本信息

- 日期：2026-09-20；任务：L01 软件学习文档。
- 用户授权：整理 sw 下 SDK/编译链接工具、嵌入式库原理功能、测试示例功能与流程，帮助初学者上手。
- 状态：文档完成；软件/硬件功能验证未执行。
- 输入提交：`379ae4544bc62e05a2736b11b33a3244181bba38`。
- 输入工作区已有 00/01 修改、AGENTS/02/共享文档/configuration/handoffs 未跟踪；保留全部已有内容。
- 负责路径：新建 `docs_codex/software/` 五篇 Markdown、本交接；串行增补 PROJECT_STATE、AGENT_TASKS、handoffs/README 与 01 的导航。不修改 sw/、RTL、依赖或构建脚本；不实施 S01 迁移。

## 本轮结果

- [软件导航](../software/README.md)：目录职责、学习顺序、软件分层与最小闭环。
- [工具链/SDK/构建](../software/BUILD_AND_SDK.md)：裸机与 Linux 入口、gcc/ar/ld/工具、flags、单目标和独立临时输出构建示例、SDK 镜像缺口。
- [链接/启动/调试](../software/RUNTIME_AND_DEBUG.md)：SPM/DRAM/ROM 的 VMA/LMA、crt0、退出/异常、仿真/JTAG/UART/GPT/ZSL。
- [库与 API](../software/LIBRARIES.md)：MMIO、printf/UART、CLINT、DMA、LLC、AXI RT、OpenTitan DIF、存储 HAL、GPT、RVV 辅助库。
- [示例流程](../software/EXAMPLES.md)：当前 tests 全部9个主源、Ara中2个应用和16个验证主源的索引、功能、流程、前置条件、判据与局限。

均为本地源码确认、只读工具查询与静态算术；示例命令未编译或运行。没有新增待执行测试源码。

## 重要源码事实与待核查项

1. 根 `sw/deps/cva6-sdk` 当前只有 install64 与备份，完整 SDK Makefile 入口在 Ara 的 cheshire/sw/cva6-sdk；不把已有镜像当完整离线 SDK。
2. 原 sw.mk 仅自动收集 tests，tests_wo_ara 是备份。其8个主源中6个与当前同名文件相同，HelloWorld/MNIST不同。
3. Ara chs-sw-all 会复制测试源进入根 tests，构建后删除复制的 C 源；保留 ELF 但找不到同名源有此机制依据。不能无检查覆盖当前同名文件。
4. AXI RT enable 是位图整体写，budget/isolate 示例连续调用会覆盖先前 CPU 位；manager编号假设Ara关闭。isolate示例阻塞等DMA后才检查隔离，存在等待/流程风险；poll无超时。
5. clint_sleep_until 对未来目标先返回，与函数意图不符；get_mtime 未做 high-low-high 重读。仅记录，未修复。
6. 当前 rvv_test.h 对缺失 stub/MMU寄存器offset补0，根生成头/HJSON缺这些字段，访问会落SCRATCH0；这些测试不能当普通SoC通用MMU回归。
7. Ara vector_helloworld 实际把向量 str_v 传给 %s；fmatmul有初始化/无符号减法/错误索引等注意点。根4×4测试失败未汇入main返回码，MNIST无自动精度断言。
8. Boot ROM被动启动实际用scratch0/1传64位入口、scratch2掩码2触发；应用退出另用scratch2编码结果。_exit实际ret，不是注释所暗示的永远等待。
9. 根sw/boot未见VCU118 DTS；flash_disk.sh长度单位/整倍数换算存在需要核查的差异。未构建Linux镜像或烧写。

对应源码链接与函数名均在专题文档中。上述是阅读时与使用相关的发现，不是完整代码审计或修复报告。

## 验证证据

工作目录：仓库根；工具：shell/rg/Python3、已安装交叉工具链只读查询。

- 执行 git status --short、git rev-parse HEAD；定向阅读 sw.mk、链接脚本、启动/库/9个主测试及Ara软件入口、验证公共正文和宏。
- command -v 定位 GCC/GDB/readelf/OpenOCD/dtc/bender；GCC --version 为15.2.0(g5115c7e44)，ld --version 为GNU Binutils 2.46。
- gcc -print-file-name=libc.a 返回工具链路径。liblto_plugin.so 查询只回显名字，另以 rg 定位实际文件在 libexec/gcc/riscv64-unknown-elf/15.2.0/。
- Python只读枚举：根tests 9个.c/.S、tests_wo_ara 8个、Ara src 2个应用、src/tests 16个测试；逐个与文档链接核对。
- DMA示例静态索引计算：源19 byte、gold38 byte、4段×15 byte、dst stride7/src stride1，Python字节数组重放结果等于gold。不是目标端DMA测试。
- 文档检查：五篇专题加本交接共107个相对链接路径存在、代码围栏成对、27/27主源链接覆盖、无新增行尾空白；7段Shell示例经bash -n语法检查通过，未执行命令；git diff --check通过，退出码均0。未用Markdown渲染器验证锚点，未执行文档内目标构建/加载命令。

可复核的只读命令：

```sh
rg --files sw/tests sw/tests_wo_ara -g '*.c' -g '*.S'
rg --files .bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/src -g '*.c'
riscv64-unknown-elf-gcc --version
riscv64-unknown-elf-ld --version
git diff --check
```

**未编译应用、未运行仿真、未综合、未连接板卡、未烧写。** 未执行全量make、依赖更新、清理或Git提交。

## 决策与下一步

- 学习先用HelloWorld/链接与启动/DMA，再按硬件条件学习RT/CLIC/RVV；Linux为独立进阶路线，不是裸机前置。
- 后续S01在独立目录冻结工具链、ISA/ABI、最小库与输出规则，处理实际需要的运行时缺口。
- V01按示例判据建立真实回归，先处理阻塞/错误码/stub匹配等必要问题，再记录性能。
- 最少输入：software/README、BUILD_AND_SDK、EXAMPLES，以及所选示例的实际源码/配置。
- 共享状态/任务/交接索引已串行同步，E01/S01/V01实施状态未标完成。
