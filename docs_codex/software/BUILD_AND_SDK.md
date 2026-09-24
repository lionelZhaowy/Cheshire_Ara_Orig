# 工具链、SDK 与软件编译

返回 [软件导航](README.md)。以下以当前 [sw.mk](../../sw/sw.mk)、[根 Makefile](../../Makefile) 和 [cheshire.mk](../../cheshire.mk) 为准；命令示例未在本轮执行构建。

<a id="1-三套东西不要混用"></a>

## 1. 裸机工具链、Ara 环境与 Linux SDK

| 类别 | 当前入口 | 输出/运行环境 |
| --- | --- | --- |
| Cheshire 裸机软件 | 根 make + sw/sw.mk | libcheshire.a、测试 ELF；无 Linux，直接访问 MMIO |
| Ara 裸机扩展 | Ara/cheshire/sw/Makefile | 带 V 的程序、测试辅助头和源码；仍用 Cheshire 启动/链接 |
| CVA6 Linux SDK | Ara/cheshire/sw/cva6-sdk/Makefile | Buildroot 工具链、Linux、OpenSBI、U-Boot、rootfs 与镜像 |

裸机 HelloWorld 不要求先编 Linux。SDK 也不是编译器可执行文件的别名；它集合工具链、系统软件、配置和镜像流程。

当前根 `sw/deps/cva6-sdk` 仅见 `install64/`、`install64.bak_20260410_194946/`；镜像包括 `fw_payload.bin/.elf/.dump`、`u-boot/.bin/.dump`、`uImage`、`vmlinux`、`Image.gz`。这些已有产物不能证明本机具备完整重建环境或已经在板上运行。根 `.gitmodules` 记录该 SDK 与 printf 为子模块，依赖快照的搬迁边界见 [.bender/README](../../.bender/README.md)。

<a id="2-每个工具做什么"></a>

## 2. 工具职责与输入输出

| 工具 | 角色 | 常用检查/操作 |
| --- | --- | --- |
| riscv64-unknown-elf-gcc | 裸机交叉编译驱动，可调用 assembler/linker | --version、-c、-T、-march、-mabi |
| riscv64-unknown-elf-as | 汇编器 | 通常由 gcc 调用；.S 先经过预处理 |
| riscv64-unknown-elf-ld | 链接器 | 地址分配、符号解析、段布局；本工程实际用 gcc 驱动链接 |
| riscv64-unknown-elf-ar | 静态库归档 | ar t 查看成员；ar rcs 建归档 |
| objdump / readelf / nm / size | 检查产物 | 反汇编、ELF 入口/段、符号、容量 |
| objcopy | 转换格式 | ELF→binary / Verilog hex；不执行程序 |
| riscv64-unknown-elf-gdb | 主机端目标调试器 | 连接 OpenOCD、装载、断点、读寄存器 |
| make | 按依赖执行构建规则 | 不是编译器，也不自动检测所有参数变化 |
| Python + regtool.py | 从 HJSON 生成寄存器定义 | 依赖环境需单独准备 |
| dtc | 设备树编译器 | .dts→.dtb，主要用于系统启动 |
| OpenOCD | JTAG 调试服务 | GDB 与实际硬件之间的接口 |
| Buildroot 的 riscv64-buildroot-linux-gnu-gcc | Linux 交叉工具链 | 面向 Linux 用户态/系统构建，不能无条件替代裸机工具链 |

本轮只读查询：PATH 中裸机 GCC 在 `/home/zhaowenyao/riscv_toolchain/bin/`，版本 `15.2.0 (g5115c7e44)`；GNU ld 为 `2.46`；GDB/readelf/OpenOCD/dtc/bender 可定位。这是本机快照，不是项目规定的最低版本或新环境保证。`gcc -print-file-name=libc.a` 返回了工具链库路径；不代表本工程已实现完整 libc 系统调用适配。

在自己的主机可先检查（不编译应用）：

```sh
command -v riscv64-unknown-elf-gcc riscv64-unknown-elf-ar
command -v riscv64-unknown-elf-gdb riscv64-unknown-elf-readelf
riscv64-unknown-elf-gcc --version
riscv64-unknown-elf-gcc -dumpmachine
riscv64-unknown-elf-gcc -print-multi-lib
riscv64-unknown-elf-gcc -print-file-name=libc.a
```

`CHS_SW_GCC_BINROOT` 指向含 `riscv64-unknown-elf-gcc` 等工具的 **bin 目录**，不是 SDK 根目录。未找到 gcc 时，默认路径推导可能失败；应先显式确认工具位置。

<a id="3-当前编译参数逐项解释"></a>

## 3. 软件编译参数

| 参数 | 当前默认/位置 | 用途与联动 |
| --- | --- | --- |
| CHS_SW_FLAGS | 共享基础选项 | 同时进入编译和链接；覆盖整个变量会替换默认列表 |
| -march=rv64gc_zifencei | 根默认 | RV64 的 G/C 与 fence.i；没有 V |
| -march=rv64gcv_zifencei | Ara 入口替换后 | 允许生成 RVV；还需硬件向量 profile 和 Ara=1 |
| -mabi=lp64d | 默认 | long/指针 64 位、双精度硬浮点 ABI；不是数据总线位宽 |
| -DOT_PLATFORM_RV32 | 默认 | OpenTitan 库使用的平台宏；不把目标改成 RV32，架构仍由 -march/-mabi 决定 |
| -mstrict-align | 默认 | 编译器避免随意生成不满足对齐条件的访存 |
| -O2 | 默认 | 优化；源码调试可能跳行、变量被消除 |
| -Wall -Wextra | 默认 | 常见告警 |
| -static | 默认 | 静态链接；不表示完全没有 libc |
| -ffunction-sections -fdata-sections | 默认 | 每函数/数据独立 section，配合 gc-sections 裁掉未用部分 |
| -flto -fuse-linker-plugin | 默认 | 链接期优化，需要一致的工具链/插件/对象文件 |
| -frandom-seed=cheshire | 默认 | 固定编译器相关随机种子，不固定所有外部构建输入 |
| -ggdb | CCFLAGS | GDB 调试信息 |
| -mcmodel=medany -mexplicit-relocs | CCFLAGS | 代码寻址模型及显式重定位；迁移链接地址时保持一致 |
| -fno-builtin | CCFLAGS | 不把普通函数名随意视作编译器内建实现 |
| -fverbose-asm -pipe | CCFLAGS | 汇编注释/编译器子进程管道 |
| -nostartfiles | LDFLAGS | 不采用工具链默认 crt0，由 libcheshire 的启动代码接管；不同于 -nostdlib |
| -Wl,--gc-sections | LDFLAGS | 丢弃不可达 section；不是删除源码 |
| -Wl,-L…/sw/link | LDFLAGS | 供 INCLUDE common.ldh 搜索 |
| -T…/spm.ld 等 | 链接规则 | 选择存储布局 |

`CHS_SW_CCFLAGS`、`CHS_SW_LDFLAGS` 可分别覆盖，但 ISA/ABI 必须一致。`CHS_SW_ARFLAGS` 当前传 LTO plugin。Makefile 在工具链 `libexec/gcc/riscv64-unknown-elf/<版本>/liblto_plugin.so` 下找它；本机路径存在。`gcc -print-file-name=liblto_plugin.so` 本机只回显名字，不能仅凭这条查询断言插件缺失，也不能把回显名字当成已解析绝对路径。

### 3.1 常用 Make 变量

| 变量 | 当前默认/用途 |
| --- | --- |
| CHS_SW_DIR / CHS_SW_LD_DIR | CHS_ROOT/sw 与其 link 子目录；改前者会改变源/产物收集位置 |
| CHS_SW_INCLUDES | 项目 include、printf、LLC、AXI RT、OpenTitan 的头搜索路径 |
| CHS_SW_LINK_MODES | 从 link/*.ld 收集，当前 dram/rom/spm；不是运行时选择 |
| CHS_SW_DTC | dtc，用于设备树编译 |
| CHS_CVA6_SDK_IMGS | 根 SDK install64 下 fw_payload.bin 和 uImage；用于Linux镜像打包 |
| CHS_SW_DISK_SIZE | 16M，根Linux磁盘镜像的默认文件容量 |
| CHS_SW_ZSL_TGUID / CHS_SW_DTB_TGUID / CHS_SW_FW_TGUID | 不同payload的分区类型GUID，与启动解析匹配；不是文件名 |

原 CHS_SW_FLAGS 还带 `-Wl,-flto`；这是当前脚本传给链接器的选项写法，应随原工具链组合核对，不把参数清单当成任意版本都适用的通用模板。

## 4. 构建依赖与命名规则

```text
HJSON / 已生成寄存器头
        ↓
应用 .c 或 .S → 应用 .o ──────────────────────┐
库 .c/.S + 第三方库源码 → 多个 .o → libcheshire.a ├→ gcc -T*.ld → ELF
                                            ┘                 ├→ dump
                                                              ├→ bin
                                                              └→ memh
```

库归档除 `sw/lib` 外，还包含 printf、LLC 驱动、AXI RT 驱动及 OpenTitan base/DIF/autogen 源码。因此只复制 `sw/` 并不足以直接用原规则编完整 libcheshire.a；需要对应 `.bender` 软件依赖或后续显式提取它们。

| 源文件名 | 自动收集的链接模式 | 解释 |
| --- | --- | --- |
| helloworld.c | .spm/.dram/.rom | 无模式后缀，自动按三种 .ld 生成目标 |
| dma_2d.spm.c | 只 .spm | 程序依赖 SPM 别名 |
| mnist_mlp_cpu.dram.c | 只 .dram | 数据规模大、需要 DDR |
| clic_basic.spm.S | 只 .spm | .S 是可预处理汇编 |
| fmatmul.c.h | 不作为主 .c 编译 | 由源程序 include，避免误当主程序 |
| *.c.body | 不独立构建 | RVV 变体共用的正文 |
| *.py | 不进 RISC-V 编译 | 主机数据生成脚本 |

根 `make chs-sw-all`（别名 `make sw-all`）生成软件库、头、测试 dump/memh 和烧写工具，不运行测试。根 `make all` 还涉及硬件生成/仿真输入；首次学习不必使用它。单目标链接规则含 `%.o` 与 `%.$mode.o` 两种形式，对应上述两种命名。

原规则会在源码附近写 `.o/.a/.elf`，包括部分依赖源码目录；`tests_wo_ara/` 不在自动扫描列表中。

## 5. 原工程的单目标使用方法

已具备本地依赖、生成器和一致工具链时，在仓库根执行以下示例。它们会写构建产物，本轮未执行：

```sh
CHS_SW_ROOT_DIR=$(pwd)
CHS_SW_TOOL_BIN=$(dirname "$(command -v riscv64-unknown-elf-gcc)")
make "$CHS_SW_ROOT_DIR/sw/tests/helloworld.spm.elf" \
  CHS_SW_GCC_BINROOT="$CHS_SW_TOOL_BIN"
make "$CHS_SW_ROOT_DIR/sw/tests/helloworld.spm.dump" \
  CHS_SW_GCC_BINROOT="$CHS_SW_TOOL_BIN"
```

使用绝对目标路径与当前 `CHS_SW_DIR` 保持一致。编好后检查，不直接启动板卡：

```sh
riscv64-unknown-elf-readelf -h -l sw/tests/helloworld.spm.elf
riscv64-unknown-elf-objdump -h sw/tests/helloworld.spm.elf
riscv64-unknown-elf-objdump -d -S sw/tests/helloworld.spm.elf
riscv64-unknown-elf-nm -n sw/tests/helloworld.spm.elf
riscv64-unknown-elf-size sw/tests/helloworld.spm.elf
riscv64-unknown-elf-ar t sw/lib/libcheshire.a
```

原规则明确留有 `TODO: track headers with gcc -MM`，没有完整头依赖跟踪；改变编译选项也不一定让现有对象过期。遇到“改了头/ISA 却没重编”，应在独立工作副本或明确的输出清单内重建相关对象/归档，不清理 `.bender/` 或批量删除他人的产物。`make -n` 也会解析 Makefile 中的 `$(shell ...)` 和 include，不把它视作完全无副作用的环境探测器。

### 5.1 无 Bender 的最小学习构建示例

以下为 **Bash 示例，未执行**：只将当前 HelloWorld、crt0、UART/CLINT 和 printf 编到新建临时目录，不是完整 SDK/ASIC 提取脚本。它刻意不使用 LTO，便于看懂归档和链接；产物不应与原 LTO 基线做未经控制的性能比较。要求当前生成头已存在、工具链可用，运行仍须匹配硬件和启动环境。

```bash
CHS_SW_ROOT_DIR=$(pwd)                 # 在仓库根执行
CHS_SW_LEARN_OUT=$(mktemp -d /tmp/cheshire-sw-learn.XXXXXX)
CHS_SW_CC=riscv64-unknown-elf-gcc
CHS_SW_AR=riscv64-unknown-elf-ar
CHS_SW_LEARN_FLAGS=(-march=rv64gc_zifencei -mabi=lp64d -mcmodel=medany
  -O2 -ggdb -mstrict-align -fno-builtin -ffunction-sections -fdata-sections
  -I"$CHS_SW_ROOT_DIR/sw/include" -I"$CHS_SW_ROOT_DIR/sw/deps/printf")
for src in sw/lib/dif/uart.c sw/lib/dif/clint.c sw/deps/printf/printf.c; do
  name=$(basename "${src%.c}")
  "$CHS_SW_CC" "${CHS_SW_LEARN_FLAGS[@]}" -c "$CHS_SW_ROOT_DIR/$src" \
    -o "$CHS_SW_LEARN_OUT/$name.o"
done
"$CHS_SW_AR" rcs "$CHS_SW_LEARN_OUT/libsupport.a" \
  "$CHS_SW_LEARN_OUT/uart.o" "$CHS_SW_LEARN_OUT/clint.o" "$CHS_SW_LEARN_OUT/printf.o"
"$CHS_SW_CC" "${CHS_SW_LEARN_FLAGS[@]}" -c sw/lib/crt0.S -o "$CHS_SW_LEARN_OUT/crt0.o"
"$CHS_SW_CC" "${CHS_SW_LEARN_FLAGS[@]}" -c sw/tests/helloworld.c -o "$CHS_SW_LEARN_OUT/main.o"
"$CHS_SW_CC" "${CHS_SW_LEARN_FLAGS[@]}" -nostartfiles -static \
  -T sw/link/spm.ld -Wl,-L"$CHS_SW_ROOT_DIR/sw/link" -Wl,--gc-sections \
  -Wl,-Map,"$CHS_SW_LEARN_OUT/hello.map" \
  "$CHS_SW_LEARN_OUT/crt0.o" "$CHS_SW_LEARN_OUT/main.o" "$CHS_SW_LEARN_OUT/libsupport.a" \
  -o "$CHS_SW_LEARN_OUT/hello.spm.elf"
```

crt0 单独列出，支持库放在使用它的对象后面。此例不包含 DMA/LLC/RT/HAL；扩展应用时需补对应源码和头，不把 `-I` 当成“已经链接实现”。

<a id="6-ara-软件入口与当前注意点"></a>

## 6. Ara 软件入口与配置约束

入口：[Ara 软件 Makefile](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/Makefile)。

- `ARA_CONFIGURATION=2_lanes` 默认选 2/2048；可选本地 4/8/16 lane 配置。
- 将根 `rv64gc` 替换为 `rv64gcv`，加入 `CHESHIRE/NR_LANES/VLEN/ARA_NR_LANES/EEW/PRINTF` 宏；当前 `eew=64, printf=1`。
- `chs-sw-all` 先复制 `src/*.c`、`src/tests/*.c`、body 和 include 文件到根 `sw/tests`，再转调根构建；成功后删除那些复制的 C 源。
- 因而旧 ELF 可以仍在 tests，原 C 源却在依赖目录。该目标会覆盖同名文件，**不要在正在编辑的 tests 上把它当无害的快捷编译命令**。先检查同名文件与输出范围，宜在独立副本中使用。

单独构建向量程序时，保持根 `CHS_SW_FLAGS` 其余选项，替换 ISA 并补齐该程序需要的宏；相关库对象也要来自同一套配置。当前 `fmatmul_test_4x4.c` 可直接在根找到，其他向量源看 [示例索引](EXAMPLES.md)。`<riscv_vector.h>` 与 intrinsic 接口受工具链版本影响，本地 vector_util 注释要求 GCC>=13；版本号只是必要线索，具体代码仍需实际编译核验。

## 7. Linux SDK 的组成与构建入口

源码入口：[cva6-sdk/Makefile](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/cva6-sdk/Makefile)，桥接规则：[cva6-sdk.mk](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/cva6-sdk.mk)。

| 部分 | 功能 | 与裸机的区别 |
| --- | --- | --- |
| Buildroot | 构建 Linux 工具链、rootfs 和内核相关输出 | 会需要主机依赖、下载与大量构建资源 |
| OpenSBI | M-mode 固件服务 | Linux 通过 SBI 使用平台服务，不是 libcheshire |
| U-Boot | 后续加载/启动 Linux | 当前 fw_payload.bin 将它作为 OpenSBI payload |
| Linux / rootfs | 内核与用户态环境 | 程序面向 Linux ABI/系统调用 |
| riscv-isa-sim / riscv-tests | ISA 模拟/测试组件 | 不是 Cheshire AXI/UART/DDR 的完整 SoC 仿真 |
| device tree | 描述地址、设备和中断等 | 必须与实际 SoC 配置匹配 |

当前 SDK `XLEN=64`；`RVV=1` 会选择 `_V_defconfig`。桥接文件 `RVV_LINUX:=1`，Linux compiler 路径是 `buildroot/output/host/bin/riscv64-buildroot-linux-gnu-gcc`。仅更改 RVV 并不替代 Linux 上下文切换/固件/硬件一致性的验收。

若后续明确需要 Linux，并准备好完整依赖，可从 Ara 的 `cheshire/sw` 目录使用已有 `make fmatmul-linux`、`make linux-img` 等入口；这是入口说明，不是本轮已执行步骤。源码支持 `HOST_TOOLCHAIN_SUFFIX`，README 中另出现 `TOOLCHAIN_SUFFIX` 拼写，应以 Makefile 为准。规则写“曾在 host GCC/G++ 11.2.0 工作”是历史记录，不是唯一支持版本。

`linux-img` 会备份根 SDK install64 后复制新镜像；可能触发子模块更新和大型 Buildroot 编译。SDK 快照不含所有下载缓存/工具链，不能宣称完整离线可重建。

<a id="8-镜像规则与当前板型缺口"></a>

## 8. 镜像构建规则与平台支持范围

根 Linux 镜像规则仍在：`sw/boot/linux.<board>.gpt.bin` 将 ZSL、DTB、fw_payload.bin、uImage 放入 GPT 分区。通用裸机 `%.gpt.bin` / `%.gpt.memh` 规则则已注释。**“裸机不必用 GPT”和“Boot ROM 仍支持 GPT/raw”可以同时成立。**

当前根 `sw/boot` 提供 Genesys2、Genesys2 VGA、VCU128 DTS，未见 `cheshire.vcu118.dts`。因此不能直接承诺 `linux.vcu118.gpt.bin` 规则可完成；也不应把 VCU128 的设备树重命名后当作已适配 VCU118。

SDK 自带的 `flash-sdcard/format-sd` 与 Cheshire 根镜像规则使用不同布局；烧写工具见启动篇。首次学习以 ELF 直载为主，制作或写入启动介质需先明确实际板卡、设备与镜像格式。
