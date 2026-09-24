<a id="已有嵌入式库原理功能和使用入口"></a>

# 嵌入式库原理与接口参考

返回 [软件导航](README.md)。库源码由 [sw.mk](../../sw/sw.mk) 归档进 `libcheshire.a`；头文件中的 inline/宏则可能直接进入应用对象。以下按调用层次解释，API 以当前本地版本为准。

## 1. 四层软件接口

```text
应用：main / 算法 / 测试判据
  ↓
HAL：SD、SPI Flash、I2C EEPROM、UART debug 等设备/协议
  ↓
DIF：UART、CLINT、DMA 或 OpenTitan I2C/SPI/GPIO 等 IP 接口
  ↓
MMIO：地址符号 + 寄存器 offset + volatile load/store
```

HAL 负责“向某种器件发什么协议”，DIF 负责“怎样操作这个控制器”，`regs/*.h` 只定义寄存器位置与位字段，本身不会初始化设备。UART/CLINT 是本项目本地驱动，I2C/SPI 等依赖 OpenTitan DIF；不要按同名函数推断来自同一 IP。

## 2. 基础工具与地址

来源：[util.h](../../sw/include/util.h)、[params.h](../../sw/include/params.h)、[smp.h](../../sw/include/smp.h)。

| 接口 | 原理/功能 | 使用提醒 |
| --- | --- | --- |
| reg8(base,offs) / reg32(base,offs) | 先按 byte 加偏移，再转为 volatile 指针 | offs 单位是 byte；*reg32 才执行访问 |
| fence() | 带编译器 memory clobber 的 RISC-V fence | 约束顺序，不是通用 cache flush |
| fencei() | fence.i | 修改/装载指令后同步取指；不能替代 DMA 数据可见性设计 |
| wfi() | 等待中断指令 | 无合适唤醒条件会一直等 |
| set_mtie / set_mie | 操作 mie 定时器使能 / mstatus 全局使能 | handler 与中断源必须先准备好 |
| get_mcycle() | 读 CPU cycle 计数 | 不是微秒；需知道频率 |
| invoke(code) | fence.i 后按函数指针调用 | 调用地址/ABI/栈必须有效 |
| gprw(gp) | 读或切换 global pointer | 用于跨阶段代码回调，不是普通变量赋值接口 |
| CHECK_CALL(call) | 调用非零返回就直接返回错误码 | 只适合相同错误返回约定 |
| CHECK_ASSERT(code,cond) | 条件失败就从当前函数返回 code | 不是会打印信息的 libc assert |
| BIT / BIT_MASK | 构造位和低位掩码 | n 要在目标整型位宽内 |
| chs_hw_feature_present(bit) | 读 SoC HW_FEATURES 位图 | 仅包含该寄存器实际定义的特性，不自动覆盖所有 CPU ISA |
| smp_pause/resume | 汇编宏，配合 hartid/CLINT MSIP 管理启动 | 普通 crt0 仍停住非零 hart；不是 pthread/多核调度库 |

例：`*reg32(&__base_regs, CHESHIRE_RTC_FREQ_REG_OFFSET)` 是一次 MMIO 读。`volatile` 限制编译器省略/合并访问，不保证多核原子性、跨主设备顺序或 cache coherence。

## 3. UART 与 printf

来源：[UART 头](../../sw/include/dif/uart.h)、[UART 实现](../../sw/lib/dif/uart.c)、[printf 头](../../sw/deps/printf/printf.h)、[printf 实现](../../sw/deps/printf/printf.c)。

| API | 行为 |
| --- | --- |
| uart_init(base,freq,baud) | 分频值=freq/(16×baud)，关闭 UART 中断，设 8N1、清/开 FIFO，并写 modem 控制 |
| uart_write / uart_read | 轮询状态后收发一个 byte，阻塞式 |
| uart_read_ready | 查询 RX 是否有数据 |
| uart_write_str / uart_read_str | 按传入 len 收发固定 byte 数，不自动 strlen |
| uart_write_flush | fence 后等待发送寄存器/移位器空 |
| _putchar / _getchar | 默认绑定 `__base_uart` 的单字符接口 |

printf 调用链：`#include "printf.h"` 将 `printf` 宏映射为 `printf_`→格式解析/数字转文本→`_putchar`→UART。`snprintf_` 输出到内存缓冲区，`fctprintf` 可使用自定义字符回调。它不依赖 Linux 文件描述符，也不需要 heap 来格式化。

常用格式：`%d/%u/%x/%s/%p/%f`；64 位计数可用 `%llu` 并显式转为 `unsigned long long`。字符串传 `char*`；RVV 向量类型不能直接传给 `%s`。`uart_write_str(str,sizeof(str))` 对数组会连结尾 `\0` 一起发出，若不要结尾应按正确文本长度发送。

printf 的编译宏可裁掉浮点、指数、long long、ptrdiff 支持：`PRINTF_DISABLE_SUPPORT_FLOAT/EXPONENTIAL/LONG_LONG/PTRDIFF_T`；还可设置格式转换缓冲区与默认精度。它们必须作用于 **printf.c 的编译**，仅在应用里定义不会重配已编好的库。

先初始化 UART 再打印，退出前 flush。算法性能测量把串口打印放到计时区外；库的可重入格式转换不保证多 hart/中断同时向同一个 UART 输出时不会交错。

## 4. CLINT：计时、测频与唤醒

来源：[clint.h](../../sw/include/dif/clint.h)、[clint.c](../../sw/lib/dif/clint.c)。

| API | 功能 | 单位 |
| --- | --- | --- |
| clint_get_mtime() | 合并高/低 32 位寄存器为 mtime | RTC ticks |
| clint_spin_until(t) | 轮询直到绝对时刻 t | RTC ticks |
| clint_spin_ticks(n) | 从当前值起忙等 n ticks | RTC ticks |
| clint_get_core_freq(ref_freq,ref_time_inv) | 跨 RTC tick 测量 Δmcycle，计算 Δcycle×ref_freq/Δmtime | 返回 Hz；2500 是测量时窗倒数参数，不是 2500 ticks |
| clint_set_mtimecmpx(idx,value) | 写指定 hart/timer 的比较阈值 | 绝对 RTC ticks |
| clint_sleep_until / clint_sleep_ticks | 设计意图为设置 timer、开中断、wfi | 必须先建立正确中断处理 |

本地 `clint_sleep_until()` 当前开头是 `if (clint_get_mtime() < tgt_mtime) return;`，未来时刻反而提前返回，与睡眠意图不符。`clint_get_mtime()` 也只读 high→low，未见高位重读以处理低位回卷。**本轮未修复；初学者先学已使用的测频/忙等路径，睡眠与极限时间边界另做验证。**

`ref_freq/ref_time_inv` 太小会使测量 ticks 为 0；RTC 不动则轮询卡住。定时中断触发后要处理比较值/使能和返回，单调用 wfi 不构成通用延时函数。

<a id="5-idma提交任务和等待完成"></a>

## 5. iDMA 任务提交与完成查询

来源：[dif/dma.h](../../sw/include/dif/dma.h)，硬件配置说明见 [DMA 参数](../configuration/PERIPHERALS.md)。头文件用宏 `X(sys,&__base_dma)` 展开 `sys_dma_*` 函数。

| API | 行为 |
| --- | --- |
| sys_dma_memcpy(dst,src,size) | 设置地址/长度等并读 NEXT_ID 提交，返回任务 ID |
| sys_dma_blk_memcpy | 提交后轮询 DONE_ID，阻塞到完成 |
| sys_dma_2d_memcpy(dst,src,size,dst_stride,src_stride,num_reps) | 开启 ND，配置每行长度、起点步进和重复次数 |
| sys_dma_2d_blk_memcpy | 二维提交+阻塞等待 |
| sys_dma_get_status | 读状态 |
| sys_dma_*_ptr | 返回对应寄存器指针，访问可能有副作用 |

地址/长度/stride 按 byte，不按 C 元素数。`memcpy` 在这里是硬件 DMA，和 libc 的 CPU 逐字节/逐块复制不同。既有驱动使用 reg64_2d 寄存器布局，切硬件 1D 前端后不能原样复用。

典型流程：分配可达缓冲区→通过约定方式让 DMA 看见源数据→设置/提交任务→等待→按缓存协议取得目的数据→比较结果。默认 SPM 的 `0x14000000` 非缓存入口与 `0x10000000` 入口映射同一阵列；例程通过加 `0x04000000` 使用该别名。此技巧只适合对应的 SPM 地址，不能给任意 DDR 指针都加这个值。

阻塞函数没有超时，DMA 被隔离/无响应时可能不返回。驱动中两个 decouple 配置表达式均使用 AW 位号，当前宏为 0；若要启用这些选项，先核对字段并验证。

## 6. LLC 与 AXI RT 库

| 库 | 常用 API | 原理/适用边界 |
| --- | --- | --- |
| [axi_llc_reg32](../../.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/sw/include/axi_llc_reg32.h) | get_set_asso/num_lines/num_blocks/version/bist_out | 通过 32 位 MMIO 读 LLC 信息 |
| 同上 | set_spm、set_flush、get_flushed | 写低/高配置再 COMMIT；查询完成状态 |
| 同上 | all_cache、all_spm、flush_all | 便利封装；flush_all 只是发起配置，不自动完成所有等待/所有权管理 |
| [axirt](../../.bender/git/checkouts/axi_rt-7cef46f372eaf0fb/sw/lib/axirt.h) | claim/release | 访问寄存器 guard，管理配置权限 |
| 同上 | set_region、set_budget、set_period | 为 manager/region 设置范围、读写预算/周期 |
| 同上 | set_len_limit_group | 一次配置一组 manager 的 burst 限制字段 |
| 同上 | enable/disable | 写 RT 与 IMTU 使能位图 |
| 同上 | poll_isolate | 等待隔离状态；当前无超时 |

LLC way 分配变化会改变 SPM 容量。当前代码/栈仍在 SPM 时不要调用 all_cache 把自身存储回收；库不替应用迁移栈。更多容量关系见 [配置手册](../configuration/CHESHIRE.md)。

AXI RT 的 manager 编号是 xbar 发起者位置，不是 AXI transaction ID。现有测试按 CPU0=0、Debug=1、DMA=2 的无 Ara 组合编写；开启 Ara 会在 DMA 前新增位置。`__axirt_enable(mask)` 实现是**写入整个位图，不是 OR 累加**，连续 enable 两次可能覆盖前一次。`poll_isolate` 用右移结果比较 1，未先按 bit0 掩码；多个高位 manager 同时隔离时需另查其判据。

## 7. OpenTitan base/DIF

源码位于 [OpenTitan 软件库目录](../../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/device/lib)。根构建把 base、dif、dif/autogen 的 C 源编进库。

- base 的 `mmio_region_t` 等封装 MMIO 基址与访问；bitfield 等工具拆装字段。
- DIF 用 `dif_i2c_t`、`dif_spi_host_t` 等 handle 标识 IP，提供初始化、配置、FIFO、事务和 IRQ 接口。
- autogen 部分来自寄存器描述，减少手写 offset；外部 `.hjson`、RTL 与软件头必须同版本。
- 这些 API 不自动完成板级 PAD、上拉、时钟或实际器件初始化；通常由 HAL 再封装。

初期按已有 HAL 的 include 和 handle 初始化方式使用，不用另起一套重复寄存器定义。导入旧 OpenTitan 示例时核对平台宏、MMIO 位宽和本工程生成版本。

## 8. 外部存储 HAL 与 GPT

| 模块 | 功能/API | 工作流程与限制 |
| --- | --- | --- |
| [i2c_24fc1025](../../sw/include/hal/i2c_24fc1025.h) | init/read/write | 配置 I2C timing/FIFO→发送器件控制与地址→分块读写；当前设计面向 24FC1025，并非通用 I2C 驱动 |
| [spi_sdcard](../../sw/include/hal/spi_sdcard.h) | init、read_checkcrc/ignorecrc、write_blocks | 低速初始化 SD SPI 模式→命令/响应→512-byte block 传输与 CRC；不是原生 SDIO 模式 |
| [spi_s25fs512s](../../sw/include/hal/spi_s25fs512s.h) | init、single_read、single_flash | SPI 命令读取；烧写按 256 KiB sector 擦写、分块编程、轮询 WIP；不适用于未知 Flash 直接套用 |
| [uart_debug](../../sw/include/hal/uart_debug.h) | init/check/serve | 二进制 READ/WRITE/EXEC 协议，供被动下载/执行 |
| [gpt](../../sw/include/gpt.h) | check_signature/find_partition/boot_part_else_raw | 使用 read 回调从任意支持的介质读分区表与 payload |

HAL 使用 `priv/buf/addr/len` 形式方便 GPT 统一调用。`addr/len` 通常是 byte；`write_blocks` 是 SD block 数，`single_flash` 是 256 KiB sector 数，不能互换。

GPT 代码先检查 LBA1 的签名，读取分区项，根据 GUID/大小挑选；找不到匹配项时有首分区回退，没有 GPT 则走 raw。这里不是 FAT/ext 文件系统，也没有展示完整可信启动/签名认证实现。GPT 分区 LBA end 是**包含端点**，所以长度为 `(end−begin+1)×512`，不同于 AXI 地址规则的排他终点。

I2C/SPI HAL 多用轮询，部分路径无统一超时。现有函数存在不等于所有对齐、边界、写入和器件型号都已验收；以最小读测试和独立设备验证为后续起点，本轮没有执行外设测试。

## 9. Ara 测试辅助库与通用 libc 的边界

| 文件 | 作用 | 注意 |
| --- | --- | --- |
| [cheshire_util.h](../../sw/tests/cheshire_util.h) | cheshire_start/end 初始化 UART/flush | 依赖调用方先 include 所需头；在头内定义普通函数，多编译单元使用需处理重复定义 |
| [vector_util.h](../../sw/tests/vector_util.h) | enable_rvv、计时、浮点近似比较 | timer 当前为 unsigned int，长运行计数会受 32 位范围限制；内联汇编约束需审核 |
| [encoding.h](../../sw/tests/encoding.h) | CSR/ISA 编码常量与宏 | 测试辅助定义，不是完整硬件能力检测 |
| [rvv_test.h](../../sw/tests/rvv_test.h) | RVV 状态、断言、异常/内存测试、stub 配置 | 专用验证代码；缺失的 stub 寄存器 offset 被补成 0，不是“功能自动关闭” |
| [fmatmul.c.h](../../sw/tests/fmatmul.c.h) / [fmatmul.h](../../sw/tests/fmatmul.h) | 向量矩阵核实现/接口 | include 式组织，核参数与 lane/VLEN/内存容量匹配 |

裸机 GCC 可能附带 newlib/libgcc 等；原链接规则也未禁用全部默认库。但当前工程没有因此获得 POSIX 文件系统、Linux syscall、线程或任意 malloc 支持。先使用已接通的静态缓冲、显式 MMIO 和本库接口；需要额外运行时能力时，检查缺失符号与启动/堆/锁/系统调用适配。
