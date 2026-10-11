# L01 / 软硬件分层图的工具与脚本映射

> 记录日期：2026-10-11。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-11；用户请求：按既有分层图，以表格列出当前开源工程各层对应的工具或脚本。
- 状态：完成（静态清单与答疑）。输入 HEAD `eaf55be17`，开始时 `git status --short` 无输出。
- 本轮仅新增本交接；未修改图稿、生产源码、共享状态和任务表。

## 本轮结果

- 区分目标代码与开发主机工具：HAL/DIF/MMIO 主要是编入目标程序的代码；Make、交叉编译器、生成器、仿真器、调试器及 FPGA 工具运行于主机。
- 应用/基础软件：`sw/tests`、`sw/lib/{hal,dif}`、`sw/include`、`sw/deps/printf`，由 `sw/sw.mk` 编译/归档/链接；Ara 向量入口为 `.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/Makefile`，会设置 V 扩展、lane/VLEN 宏，并执行复制/清理步骤，不能视作只读包装器。
- 工程构建：根 `Makefile` 包含 `cheshire.mk`，后者包含 `sw/sw.mk` 与 `target/xilinx/xilinx.mk`；Bender 清单来源为 `Bender.yml/Bender.lock/Bender.local`，当前依赖是本地受版本管理的快照。
- 接口生成：`REGTOOL` 来自 register_interface 的 vendored OpenTitan `util/regtool.py`；`cheshire.mk` 生成 SV 寄存器文件，`sw/sw.mk` 用 `--cdefines` 生成 C 头。
- 启动：`hw/bootrom`、`util/gen_bootrom.py`、`sw/lib/crt0.S`、`sw/link`；ROM 生成目标独立，不是每次 all 自动重建。
- 仿真：`target/sim/vsim/compile.cheshire_soc.tcl`、`start.cheshire_soc.tcl`，VCS 启动脚本及生成规则，`tb/fixture/vip_cheshire_soc.sv`、`elfloader.cpp`；工具为 Questa/ModelSim、VCS、C++ 编译器，DRAMSys 是可选模型。
- FPGA：`impl_ip.tcl`、`impl_sys.tcl`、`add_sources.vcu118.tcl`、约束与 `program.tcl/flash.tcl`，由 Vivado 执行；不是全开源工具链。
- 下载与调试：`util/openocd.*.tcl`、`flash_disk.sh`、`flash_disk.gdb`；后者将 `flash.spm.elf` 与镜像加载到目标，再调用目标端 `sw/boot/flash.c` 完成介质写入。UART 协议的仿真客户端在 VIP，本轮未发现并宣称通用板级 Python 下载器。
- OS：Ara 的 `cheshire/sw/cva6-sdk.mk` 调用 CVA6 SDK / Buildroot 等；根 `sw/sw.mk` 的 Linux GPT 规则仍存在，消费外部 SDK 镜像并使用 dtc/sgdisk/dd。通用 GPT 测试规则被注释，两者不能混淆。
- ASIC、NPU/ISP/LVDS 等沿共享状态标为待实施，不虚构可用脚本。独立 `cheshire_ara_asic/` 本次检查仍不存在。

## 验证证据

- `git status --short`、`git rev-parse --short HEAD`；读取共享状态、任务表、2026-10-11 文档重构交接。
- 使用 `rg --files`、`rg -n`、`sed` 定向核对上述 Makefile、脚本与源码路径，没有执行 make、下载、烧写、构建或仿真。
- 若干历史候选文档名和目录通配未匹配，改用当前存在的文件核对，不以缺失的历史路径作证据。
- 本轮未检查主机工具安装版本，不声称脚本引用的工具均已可用；现有 ELF/bitstream 不作为新测试证据。
- 未提交；无生产接口、地址、配置或验证状态变化。

## 下一步

- 按具体任务进入相应脚本；真正执行前核对 CPU profile、Ara 配置、软件 ISA、板型和工具路径。
- 如后续把表加入正式教材，按当前 HTML/Markdown 同步维护规则处理；本轮未扩大为教材或图稿修改。
