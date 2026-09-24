<a id="常用配置入口和修改流程"></a>

# 常用配置与修改流程

返回 [配置导航](README.md)。本页的“已有”表示源码中有该组合/入口；“示例”表示可供实施讨论的修改方法；均不声称本轮运行通过。

## 1. 当前配置矩阵

| 用途/入口 | CPU profile | SoC 配置来源 | Ara / 其他差异 | 证据与适用范围 |
| --- | --- | --- | --- | --- |
| 根 Make 默认 | cv64a6_imafdchsclic_sv39_wb | TB 默认 SelectedCfg=0 | Ara=0 | 现有标量构建默认；不是向量基线 |
| TB SELCFG=0 | 由编译清单决定 | DefaultCfg | Ara=0，RT=0，CLIC=0 | 选择配置不更换 CPU |
| TB SELCFG=1 | 同上 | DefaultCfg+AxiRt=1 | 仍 Ara=0 | RT 示例；需匹配生成寄存器 |
| TB SELCFG=2 | 同上 | DefaultCfg+Clic=1 | 仍 Ara=0 | CLIC 示例，非 Ara+CLIC |
| TB SELCFG=3 | 必须另选向量 profile | DefaultCfg+Ara=1 | 2 lanes，2048 bit | 可作为提取取值基准；当前生成仿真脚本未对齐 |
| Ara 集成 Makefile | cv64a6_imafdcv_sv39 | 仿真仍需 SELCFG=3；FPGA 读宏 | 默认 ARA_CONFIGURATION=2_lanes | 带 exclude_first_pass_decoder/ARA 宏的来源 |
| 当前 VCU118 add_sources | cv64a6_imafdcv_sv39 | FPGA wrapper 派生 | Ara=1、2/2048，SerialLink=0、Usb=0、RTC=1 MHz | 清单源码确认；不证明现有 bitstream 与全部输入一致 |
| 建议首个 ASIC 固定基线 | cv64a6_imafdcv_sv39 | 新建独立固定包，取 TB Ara 快照 | 1 核、2/2048；其余先保留 | 02 文档的提取建议，目录尚未实施，非最终产品冻结 |

当前 VCU118 仍继承 `Vga=1/I2c=1` 等 DefaultCfg 字段，即使板级没有相应 IO 宏；不要把不引出接口等同于已经裁掉逻辑。

相关入口：[cheshire.mk](../../cheshire.mk)、[TB 配置数组](../../target/sim/src/tb_cheshire_pkg.sv)、[Ara 集成 Makefile](../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/Makefile)、[FPGA wrapper](../../target/xilinx/src/cheshire_top_xilinx.sv)。

<a id="2-初学者常用场景"></a>

## 2. 典型配置组合与修改示例

<a id="21-重现标量-helloworld"></a>

### 2.1 标量 HelloWorld 配置

保留现有板级工程、启动方式和已使用软件，记录 CPU profile、SoC 配置、bitstream/ELF 来源和串口输出。HelloWorld 适合验证取指、部分存储和串口路径；它不覆盖向量计算、所有 DDR 地址或原子并发。

<a id="22-建立正确向量组合"></a>

### 2.2 CPU 与 Ara 向量配置

需要同时满足：

- 编译唯一 CPU profile：`cv64a6_imafdcv_sv39`，`RVV=1`。
- 只编译 Ara 的真实 `cva6_accel_first_pass_decoder.sv`，排除 CVA6 同名模块的 stub。
- 仿真选 `SelectedCfg=3`；FPGA wrapper 传 `ARA/NR_LANES=2/VLEN=2048`。
- 软件使用带 V 的 ISA，典型为当前入口的 `rv64gcv_zifencei`、`lp64d`；工具链确实支持所用指令。
- 启动设置 VS；浮点路径设置 FS；测试真正执行向量并比较结果。

现有 Ara 入口用于选源的关键字符串是：

```text
-t cv64a6_imafdcv_sv39 -t cva6 -t rtl -t exclude_first_pass_decoder
--define ARA --define NR_LANES=2 --define VLEN=2048
```

这是**源码选择说明**，不是本轮执行的构建命令。当前目标仍是后续 E01 形成固定配置+静态 filelist，无须为阅读本手册反复维护 Bender。

<a id="23-调整向量规模"></a>

### 2.3 向量规模调整

建议先只变一个因素，例如维持 VLEN=2048 比较 2/4 lanes，或维持 2 lanes 比较不同 VLEN；这类组合必须先展开和回归。若直接选择本地 `4_lanes.mk`，其 VLEN 也变成 4096，要在性能报告中明确两个变量都变了。

同时核对 TB 常量、FPGA 宏、软件宏、VRF bank 深度、Ara AXI 宽度转换、4 个 outstanding reads 限制和 DDR 实测带宽。不要把新的 lane 数写进软件宏就认为硬件改变。

<a id="24-增大-llcspm-容量"></a>

### 2.4 LLC/SPM 容量调整

仅作计算示例：在 `AxiDataWidth=64, LlcSetAssoc=8, LlcNumBlocks=8` 不变时，把 `LlcNumLines` 从 256 改为 512，总容量从 128 KiB 变为 256 KiB；默认 SPM 窗口长度也随之变化。

```systemverilog
// 供后续独立配置包采用的函数片段；本轮未应用或编译。
function automatic cheshire_cfg_t gen_team_cfg();
  cheshire_cfg_t ret = DefaultCfg;
  ret.Ara = 1;
  ret.AraNrLanes = 2;
  ret.AraVLEN = 2048;
  ret.LlcNumLines = 512; // 仅作容量计算例子
  return ret;
endfunction
```

需要检查 SRAM 形状、tag 地址、BIST、栈定位、SPM 别名和链接脚本。不要为了增大 LLC 把整个 AXI 数据宽度一并改大，因为那会触及大量接口。`sw/link/common.ldh` 当前 SPM 链接区只写 64 KiB、DRAM 链接区 8 MiB，这是软件可放置区域，不等于 128 KiB 硬件 SPM/2 GiB DDR 路由窗口。

<a id="25-减少外设"></a>

### 2.5 外设裁切

待产品保留表确认后，在独立配置里按需求设置 `Usb/Vga/SerialLink/I2c/SpiHost/Gpio` 等；调整端口绑值、启动介质、软件探测、AXI ID 和中断表。不要裁掉用于当前 ELF 加载或自主启动的接口。

DMA=0 会减少 AXI 发起者并移除控制窗口。LlcNotBypass=0 会失去内部启动 SPM，影响比关闭 UART/VGA 大得多。现阶段不因“裸机”就自动删除 MMU/PMP/Debug，也不把最终外设取舍当成已决定。

### 2.6 图像搬运和 NPU 接入

先用已存在的 2D iDMA 理解行长度、stride、帧缓冲和所有权交接。自定义 IP 的 MMIO 可接 Reg 扩展，DMA master 可接 AXI 扩展；图像带宽预算需要帧宽×帧高×每像素 byte×帧率，再加读写遍数与空隙开销。

若要求 ISP/NPU 绕过 LLC，须新增 DDR 侧连接设计，确定不缓存共享区或缓存维护流程、缓冲区所有权、中断通知及 LR/SC 边界。本仓库没有一个 `NpuBypassLlc` 开关可以完成这些工作。

## 3. 仿真与软件常用参数

来源：[start.cheshire_soc.tcl](../../target/sim/vsim/start.cheshire_soc.tcl)、[tb_cheshire_soc.sv](../../target/sim/src/tb_cheshire_soc.sv)、[Boot ROM C](../../hw/bootrom/cheshire_bootrom.c)。

| 参数 | 当前含义 | 注意 |
| --- | --- | --- |
| SELCFG | Tcl 转成 -GSelectedCfg=0/1/2/3 | 展开选 SoC，不能修改已编译 CPU profile |
| USE_DRAMSYS | -GUseDramSys | 需匹配 SystemC/DRAMSys 库和资源，不是 DDR 控制器开关 |
| BOOTMODE=0 | 被动加载 | 配合 PRELMODE/BINARY |
| BOOTMODE=1 | ROM 的 SPI SD 启动 | 当前 TB 明确 fatal 为未支持，不能照板级流程直接仿真 |
| BOOTMODE=2 | SPI NOR Flash 启动 | IMAGE 提供对应模型可读内容 |
| BOOTMODE=3 | I2C EEPROM 启动 | 同上，并核对设备容量 |
| PRELMODE=0/1/2 | JTAG / Serial Link / UART 调试加载 | 仅 BOOTMODE=0 分支使用；关闭链路后不能选它 |
| BINARY | ELF 文件路径 | 需与 ISA、链接地址和启动契约匹配 |
| IMAGE | 自主启动模型镜像路径 | 与 ELF 是不同格式/加载路径 |
| CHS_SW_FLAGS | 编译器架构、ABI、优化等 | 覆盖时保留所需原有选项，避免只传 -march 丢掉其余设置 |
| eew / printf（Ara 软件入口） | 默认 64 / 1 | 测试数据元素宽度与打印开关，不改变 Ara ELEN |

如果已有**重新编译且匹配的 work 库**，可按现有 ModelSim 入口采用以下 Tcl 片段；这是用法示例，本轮没有执行。应在原流程规定的 `target/sim/vsim` 工作目录运行，并把 ELF 占位路径换成实际文件：

```tcl
set SELCFG 3
set BOOTMODE 0
set PRELMODE 0
set BINARY /absolute/path/to/verified_vector_test.spm.elf
source start.cheshire_soc.tcl
run -all
```

示例依赖匹配的仿真编译清单；当前 checkout 的清单存在第 6 节所述问题，不能跳过编译输入核对。`BOOTMODE=0` 直接加载 ELF 不需要 GPT；自主启动解析仍可支持 GPT/raw，镜像构建规则与硬件启动能力要分别看。

<a id="4-每次改配置的建议顺序"></a>

## 4. 配置修改与验证流程

1. 记录 git HEAD、工作区变更、CPU profile、Cfg 取值、宏、软件 ISA/ABI；明确只改哪个目标配置。
2. 在独立配置包/wrapper 和独立输出目录实施，保护旧 FPGA 工程。不要在原 DefaultCfg 上顺手做产品裁切。
3. 检查字段实际消费者、派生位宽/容量/地址与生成包尺寸；核对单位是 bit、byte、项数还是 log2。
4. 同步必要的源码清单、typedef、生成 RTL、软件头文件/链接脚本与启动方式。
5. 先语法编译和展开，检查重复 package/module、无效范围、端口截断、断言。
6. 运行与改动相关的最小功能测试，再进行性能/面积比较；记录真实结果和失败输入，写独立交接。

## 5. 最小验证矩阵

| 改动 | 最少应验证的行为 | 通过证据 |
| --- | --- | --- |
| 切 CPU profile / RVV | 启动、标量 ISA、向量整数与浮点 | 指令实际执行、结果比对、异常信息 |
| Ara lanes/VLEN | 不同 vl/SEW、跨 lane、tail/mask、向量 load/store | 与标量参考值一致、无超时 |
| cache/PMA/LLC | miss/回写或写穿、SPM 边界、CPU/Ara 共享 | 内存数据一致、配置读回、相关波形 |
| AXI ID/事务深度/宽度 | 多 ID、反压、burst、读写同时发生 | 响应 ID/顺序/数据正确，无死锁 |
| DMA | 1D/2D、stride、未对齐、跨边界、完成通知 | 目标区与参考数据一致，周围哨兵未破坏 |
| 外设关闭/地址改变 | BootAddr、链接区、MMIO、IRQ 和错误地址 | 正常路径完成、非法路径响应符合设计 |
| DDR/旁路拓扑 | 并发普通访存、共享区可见性、AMO/LRSC | 设计契约对应测试逐项通过 |
| SRAM/时钟/ASIC 适配 | 读延迟、byte enable、复位、CDC、时序 | 对应仿真/形式/综合报告，不用 FPGA bitstream 替代 |

“编译通过”“仿真返回 0”“板上计算正确”“时序签核”分别记录，不能相互替代。测试矩阵是后续工作建议，本轮没有执行这些测试。

<a id="6-本轮静态发现与待验证项"></a>

## 6. 源码静态发现与待验证项

| 项目 | 源码证据 | 对配置使用的影响 |
| --- | --- | --- |
| 当前仿真 profile/decoder 未对齐向量 | compile.cheshire_soc.tcl 同时含标量 profile、decoder stub、真实 Ara decoder | SELCFG=3 不足以修复；需后续修正独立清单并重新编译 |
| SlinkMaxClkDiv 字段未被当前实例消费 | SoC/VIP 用包级常量，不用 Cfg 字段；10 位字段赋 1024 截为 0 | 单改字段无效 |
| SPM 执行规则未覆盖高地址非缓存别名 | ExecuteRegionLength=2×SizeSpm；别名间隔 0x04000000 | 不承诺从非缓存别名执行代码 |
| DMA 1D 分支 busy 信号可疑 | wrapper 连接 idma_busy，但声明的是 busy | 不能列为已验证可切换的 1D 模式 |
| DMA 驱动 decouple 位号需核对 | 两个宏表达式均移到 DECOUPLE_AW_BIT，当前宏为 0 | 开启 decouple 之前先对照寄存器定义 |
| VGA 错误记录容量与读并发不同 | VgaMaxReadTxns=24，错误单元 NumOutstanding=CoreMaxTxns=8 | 更改吞吐参数时补充错误路径验证 |
| PLIC/CLINT/AXI RT 为生成尺寸 | 当前 58 sources/2 contexts/1 hart；RT 6 managers | 加核/加 IRQ/加 master 需联动生成包 |
| 许多配置合法性检查仍是 TODO | cheshire_soc.sv 末尾 | 未报错不能推导组合合法 |

这些记录是配置手册的使用边界，不是本轮修复报告；各实现任务按用户授权处理。

<a id="7-可复制的团队配置记录模板"></a>

## 7. 团队配置记录模板

```text
配置名称/用途：
源码 HEAD 与本地差异：
CPU profile 文件；唯一性：
CVA6 关键最终值（RVV/RVH/RVSCLIC/PMP/cache/MMU）：
SoC Cfg 定义文件与覆盖项：
Ara lanes/VLEN/浮点支持：
总线地址/数据/ID/USER；事务容量：
LLC 总容量；启动 SPM 分配；运行期分配：
DDR AXI 契约；地址窗口与实际容量：
外设保留表；外部端口/IRQ；生成包尺寸：
启动方式；RTC/SoC/设备时钟来源：
软件工具链、ISA/ABI、链接脚本、VS/FS：
源码清单/宏；构建输出目录：
已执行命令、结果和日志：
未验证项与下一步：
```
