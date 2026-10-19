# E01 / 第 1 步工具链最小验证

日期：2026-10-18。用户已明确“开始第1步”。输入：`mp/ara-pulp-v2` / `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`；未修改原 RTL、软件、依赖或 FPGA 工程。

**第 1 步检查已完成，结论为有条件可继续，不是所有项目通过。** 现有工具链能够编译和链接本次 RV64/RVV 1.0 小程序；SPM 地址测试通过。发现现有 libgcc 的特定高地址重定位限制，完整 runtime/目标执行仍待后续验证。未调用 VCS，未测试许可证，未执行任何 RISC-V 程序。

## 1. 执行范围与证据

服务器：`zhaowy24@172.16.0.243`。

唯一服务器写入根：`/home/zhaowy24/CheshireAraPULP/_e01/preflight/`：

```text
inputs/             原始探针、原样 elfloader.cpp、许可证、来源记录
run_001/            首轮 45 条命令，保留两项 DRAM 地址链接失败
diagnostic_inputs/  隔离探针、原样 crt0.S/common.ldh/spm.ld/dram.ld
run_002/            29 条隔离/补充命令；不覆盖首轮证据
run_003_metadata/   3 条工具路径查询、输入 SHA256、目录边界记录
```

本地镜像：[证据目录](evidence/preflight_2026-10-18/)。两个执行批次分别保存 `commands.jsonl`、`logs/*.stdout`、`logs/*.stderr`、`summary.json`、ELF/map/object 及 `artifact_hashes.json`。每条执行命令有 argv、cwd、60 秒超时、耗时和退出码；全部串行。

- [首轮结果](evidence/preflight_2026-10-18/run_001/summary.json)：45 条命令中 43 条退出 0，两个高地址链接命令退出 1；脚本总退出 1。
- [隔离结果](evidence/preflight_2026-10-18/run_002/summary.json)：29 条命令均退出 0；脚本退出 0。此结果不关闭首轮失败。
- [工具路径与输入校验](evidence/preflight_2026-10-18/run_003_metadata/verification.json)：查询退出 0；16 个输入文件在本地与服务器 SHA256 一致。
- 已核对取回的两个批次共 183 个产物/日志的归档校验和。原传输归档 `server_results.tar` 保留；它只包含 run_001/run_002。

`~/CheshireAra` 仍为空；`~/CheshireAraPULP` 仅新增 `_e01`。TTY 未写入；此前记录的 filelist、TB/DPI/fixture、SoC 包及主体共 7 个文件 SHA256 与阶段 0 相同。本地原有 9 个未提交/未跟踪文档不属于此次修改范围；共享状态文件保持原状，待协调者合并。

## 2. 工具与实际结果

| 项目 | 实测结果 | 证据边界 |
| --- | --- | --- |
| RISC-V GCC | `/opt/riscv/bin/riscv64-unknown-elf-gcc` 13.2.0，target `riscv64-unknown-elf` | 本次使用此现有安装，未升级 |
| GNU as/ld/ar/objdump/readelf/nm | 2.43.1；版本查询、汇编、链接、反汇编均实际执行 | GCC 实际 as/ld 路径另存 metadata |
| ISA/ABI | 标量 `rv64gc_zifencei`，向量 `rv64gcv_zifencei`；均 `lp64d`、`medany` | ELF64、RISC-V、double-float ABI 核对通过；vector `.o` 标记 `v1p0` |
| SPM 小程序 | 两组 ISA 在 `0x10000000` 编译/链接通过，无未定义符号 | 实际链接 libc 的 memcpy、libgcc 的 128-bit 除法辅助函数，不是只接受 -march |
| RVV/浮点/原子 | 反汇编含 vsetvli/vsetivli、vle32/vse32、vadd、vfmacc、F/D、AMO/LRSC、fence.i | 指令编码生成通过；未验证硬件执行或计算结果 |
| FS/VS | 自建探针反汇编确认先设置 mstatus，再执行 FP/RVV | 原版 crt0 没有统一开 VS 的问题仍保留；没有修改它 |
| LTO | 标量/向量 C 的 `-flto` 编译及 SPM 链接通过，使用 `-fuse-linker-plugin -Wl,-flto` | 不等于完整 libcheshire 构建通过 |
| 原版 crt0.S | 两组 ISA 汇编通过，保存反汇编 | 仅 object 检查，未与完整工程 runtime 链接或运行 |
| 原版链接脚本 | libc-only 隔离程序用未修改 common.ldh/spm.ld/dram.ld，在 SPM/DRAM 均链接通过 | 使用探针自己的 _start；并非完整官方启动软件验收 |
| 本机 C++ | `/opt/rh/gcc-toolset-13/root/usr/bin/g++` 13.3.1；C++11 STL 小程序编译、链接、实际运行退出 0 | 输出 `E01_NATIVE_CXX_PASS sum=10`，仅 x86_64 主机运行 |
| ELF loader | 当前本地 `target/sim/src/elfloader.cpp` 原样复制，使用 VCS 安装中的 svdpi.h，编译退出 0 | object 为 x86_64，四个 C API 导出存在；svGetArrayPtr 等须由后续模拟器链接提供，未进行 VCS 联编/运行 |

单一 multilib `.;` 在两组 ISA 下选择相同的 libc/libgcc。运行库路径：

```text
/opt/riscv/riscv64-unknown-elf/lib/libc.a
/opt/riscv/lib/gcc/riscv64-unknown-elf/13.2.0/libgcc.a
/opt/riscv/libexec/gcc/riscv64-unknown-elf/13.2.0/liblto_plugin.so
```

`gcc -print-file-name=liblto_plugin.so` 只返回裸文件名，不能据此判定插件不存在；实际 LTO 链接成功，再从 `-print-prog-name=lto-wrapper` 定位并确认了上述文件。后续归档工具需要插件时应使用实际路径。

## 3. 未关闭问题：libgcc 高地址重定位

首轮用同一组对象和同一探针 linker script，仅将 `PROBE_BASE` 从 `0x10000000` 改为 `0x80000000`，标量和 RVV 均失败：

```text
libgcc.a(_divdi3.o): in function __udivmodti4:
relocation truncated to fit: R_RISCV_HI20 against symbol __clz_tab
```

原始日志：[标量](evidence/preflight_2026-10-18/run_001/logs/scalar_dram_link.stderr)、[向量](evidence/preflight_2026-10-18/run_001/logs/vector_dram_link.stderr)。

隔离证据：

1. 探针使用 volatile `__int128` 除法，确保从现有 `libgcc.a` 实际拉入相关成员。
2. 将该 archive 中 `_divdi3.o` 只读提取到本次证据目录，反汇编发现 `lui` 配合 `R_RISCV_HI20/LO12_I` 对 `__clz_tab` 的绝对引用，见[重定位记录](evidence/preflight_2026-10-18/run_002/logs/libgcc_relocations.stdout)。未修改该 archive。
3. libc-only 变体仍实际调用 memcpy，但不含 128-bit 除法；配合原版 `dram.ld` 在 `0x80000000` 链接通过。因此不能把失败泛化为“工具链不支持 RVV”或“所有 DRAM 程序都不能链接”。

诊断：相关预编译库对象的地址生成方式存在 medlow 型限制；应用的 `-mcmodel=medany` 不会重编译已安装的 archive。GCC 对两种 code model 的地址限制见 [GCC 13.2 官方说明](https://gcc.gnu.org/onlinedocs/gcc-13.2.0/gcc/RISC-V-Options.html)。本次只确认所用成员，未审计所有 libc/libgcc 成员。

最小处理建议（尚未实施）：

- 首个验证程序继续放现行 SPM 区；从 SPM 执行代码访问原有 DDR 模型地址，仍可覆盖基础 DDR 访存，保持地址图及配置不变。这不关闭通用 DRAM 驻留软件的运行库限制。
- 若后续实际 DRAM 程序需要这些辅助函数，准备同源/同版本、`lp64d` 且按 medany 构建的必要运行库，装入用户独立目录并显式选择；先核对精确工具源码及构建配置，再提出具体构建动作。无需据此直接升级 GCC 或覆盖 `/opt`，本轮也未重建运行库。
- 不把强制挪动 `__clz_tab`、改 DDR 地址、删掉真实应用所需运算作为通用修复。待完整软件闭包链接后，以实际拉入的 archive 成员确定影响范围。

## 4. 告警与未验证项

- ELF loader 用 `-Wall -Wextra` 产生 22 条告警（含模板重复）：格式符与实参类型、signed/unsigned 比较、未使用变量等。原源码保留；编译成功不说明其错误路径行为正确。
- 原版 SPM/DRAM linker script 的四次隔离链接各有一条 RWX LOAD segment 告警，退出均为 0；这来自当前脚本的段组织，本轮未重写它。
- 首次 tar 传输观察到源 mtime 比服务器时钟领先约 351–390 秒。未修改服务器时间；补充传输使用 `tar -m` 不保留源 mtime。第 2 步应避免未来时间戳触发 make 误判，仍以 SHA256 校验源码内容。
- 没有执行 VCS/vlogan、许可证 checkout、DPI 模拟器联编、任何 RISC-V ELF、Boot ROM 启动、LLC/SPM 初始化或 RVV 结果测试。
- 完整 libcheshire、实际 printf/HAL、生成头文件依赖及 Python 包仍待第 2/3 步；最小 libc/libgcc 探针不能代替完整软件构建。未重生成 Boot ROM。

## 5. 可复现命令与下一步

原始命令逐条见两批 `commands.jsonl`，没有 shell 管道吞掉被测工具退出码。首轮脚本可用一个**不存在的新输出目录**重跑：

```sh
cd /home/zhaowy24/CheshireAraPULP/_e01/preflight
python3 inputs/run_preflight.py --out "$PWD/run_recheck_001"
```

当前安装下预计仍会在两项高地址完整探针链接失败并返回 1；不要通过覆盖 run_001 或删掉失败项把结果改成通过。隔离脚本当次入口是 `python3 diagnostic_inputs/diagnose.py`，固定输出 run_002 且拒绝覆盖；源码、输入和每条命令已保存，后续重跑应分配新输出。

**第 1 步结束，未进入第 2 步。** 建议第 2 步保持原规划：冻结当前源码、复制到参考根、离线导出正确向量清单、准备完整软件小测试；首次以 SPM 软件闭环推进，保留 libgcc 高地址问题。第 2 步不修改 `/opt` 或 TTY，不编译完整 SoC；取得用户确认后执行。
