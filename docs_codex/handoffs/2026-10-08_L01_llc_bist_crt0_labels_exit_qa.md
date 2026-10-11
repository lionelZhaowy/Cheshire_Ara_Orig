# L01 / LLC BIST、CRT0 入口、数字标签与返回流程

## 基本信息

- 日期：2026-10-08；任务 L01；用户要求解释四个源码问题，不包含修复实施。
- 输入：`mp/ara-pulp-v2`，HEAD `278434024`；开始时仅上轮 bootrom_crt0_execution_qa.md 未跟踪，保留。
- 负责：只读硬件/软件/既有 ELF 与官方资料，仅新增本交接，未提交 Git。
- 状态：静态核查及既有产物反汇编完成；未编译/未仿真/未板测。

## LLC BIST 的定义、启动与范围

- `hw/cheshire_soc.sv:496` 在 LlcOutConnect && LlcNotBypass 时实例化 `axi_llc_reg_wrap i_llc`。
- 当前依赖为 Bender.local 的 `.bender/git/checkouts/axi_llc-5fb8850caad4fcfa`，SNAPSHOT.tsv 来源 commit `559bcbd09a5a884dbe31e2d72fd95d024e357f39`；具体实现以本地快照为准。
- 实例链：`cheshire_soc.gen_llc.i_llc` → `axi_llc_reg_wrap.i_axi_llc_top_raw` → `axi_llc_top.i_hit_miss_unit` → `axi_llc_hit_miss.i_tag_store` → `axi_llc_tag_store.i_tag_pattern_gen`。
- `src/axi_llc_hit_miss.sv:402` 的 init_q 复位为 0；319 行未初始化分支主动发出 mode=Bist、all-way indicator、store_req_valid=1。握手后该请求进入 tag store，tag_store.sv:239 驱动 gen_valid，再启动 pattern_gen，不需要软件 start 写操作。
- `hit_miss_detect/axi_llc_tag_pattern_gen.sv` 执行 WZEROUP/RZEROUP/WONEUP/RONEDOWN/WZERODOWN/RZERODOWN；193 行结束置 eoc。tag_store:337 的 bist_valid_o 来自 gen_eoc，config:370 映射为 BIST_STATUS.done。
- 测试对象是 tag SRAM（包括 tag/valid/dirty 元数据），不是 axi_llc_data_way 的数据 SRAM，不能据此声称全 LLC 数据阵列 MBIST/工艺 DFT 已覆盖。tag store 265 行起每 way 实例化 tc_sram；真实宏必须保持规定延迟、使能等语义。
- 当前 Boot ROM S:65 轮询配置基址+0x48 的 DONE，随后写 all-way SPM 配置并 commit。它没有读取 +0x20/+0x24 BIST_OUT 判断错误；DONE 表示结束，不是错误位全零证明。BIST 后硬件设置的初始 way 用途会覆盖过程中提前提交的配置，官方建议等待结束再配置。
- 本地 `doc/axi_llc.md:91` 和[上游对应说明](https://github.com/pulp-platform/axi_llc/blob/master/doc/axi_llc.md)描述自动 tag-store 自测。Cheshire 开源组合包含该逻辑，ASIC 宏适配/制造测试仍待 P01/V01。

## CRT0 入口及既有 ELF 证据

- gpt.c:89 调用 boot_next_stage(code_buf)，code_buf 为 SPM 起点。ROM 汇编将地址保存在 scratch4/5，并在107行 `jalr ra,0(t0)` 跳到该地址。
- `common.ldh:11` 为 ENTRY(_start)，spm.ld:13 和 rom.ld:14 都把 .text._start 放在载荷最前。标准 SDK 载荷此节来自 crt0.S，故地址跳转自然进入该镜像的 _start；没有源码级 call crt0。raw 路径不解析 ELF，正确镜像布局是前提。
- 已有 sw/tests/helloworld.spm.elf 的 readelf/nm：ELF64/RISC-V，entry=_start=0x10000000，main=0x100012a2，_exit=0x10000116。开头反汇编与 crt0 的中断/ hart 检查相符。仅作为旧产物地址示例，不证明当前源重新编译或目标通过。
- ELF SHA-256 `619a03ebcc13a8b9a7cc5052c4c2e6d066f6253554edc48b83a5f242c0c9f970`。

## 数字局部标签

- GNU 数字局部标签可重复定义；Nb 指前方最近的 N:，Nf 指后方下一个 N:，汇编器内部区分符号，非普通重名标签。
- crt0.S：19行2f→23行2:；22行1b→20行1:；27行1f→29行1:；32行1f→34行1:。
- 官方定义：[GNU as Numeric Local Labels](https://sourceware.org/binutils/docs/as/Symbol-Names.html#Local-Labels)。

## main 返回与两层 _exit

- crt0.S:116 的 call main 建立指向随后机器指令的 ra，紧接的120行是 _exit；标签/注释/汇编指示不占运行指令位置。C main 的正常函数返回因此先进入应用 _exit，无须显式 call _exit。
- 已有 ELF：0x10000112 为 jal main，下一地址0x10000116即应用_exit；该段写scratch2后0x10000130 ret。源码125行的 wait forever 注释不等同实际指令。
- crt0 在启动时将进入应用的 ra 存栈；应用_exit恢复该 ra 后 ret。UART EXEC 的 invoke 路径与 JTAG 直接改 PC 的返回契约不同，不能混同。
- **新增静态返回链缺口**：ROM boot_next_stage 在107行 jalr 之后是109行 ret，但没有保存原调用者 ra。按普通载荷 crt0 保留并恢复入口 ra 的条件，应用返回后到达 ROM 这条 ret，此时 ra 仍指向该 ret，造成自返回循环；不能承诺继续返回 gpt → ROM C main → ROM _exit。注释本身也写“下一阶段不应返回”。未运行目标验证，未改代码。
- ROM `_boot` 调用 ROM C main 后紧接的 `_exit` 则是另一个符号，执行 ebreak/wfi。只有真正从 ROM C main 返回才到此处，不能把应用和 ROM 的两个 _exit 视为同一入口。

## 验证与后续

- 读取当前状态/任务和上轮交接，rg/nl 定向核查，readelf -h、nm -n、objdump -d 读取既有 ELF，并访问官方 LLC/GNU/RISC-V 汇编资料；没有执行编译或目标运行。
- ROM S SHA-256 `6641c387c8a3d77235bf7aa2617874a205d7fc5abdb5d52cf63b05c7abc078d0`；crt0 S `b6b305f14dc866903fb9d0c0dee51a0758141b6742b793bf265776f19c2ef7f7`。
- 下一步：V01/P01 核对真实 SRAM BIST 语义与错误注入/数据阵列测试覆盖；S01 若需要可返回载荷，明确其 ABI 与 boot_next_stage 返回链，独立授权后修复并验收，不在答疑中修改。
- 已有 S01-B01（Platform ROM 返回）与本次载荷返回问题不是同一条控制流，不能以修复其中一个声称另一个已通过。C00 可将新返回链缺口及 tag-only BIST 证据边界合并到共享状态，本轮只写独立记录。
