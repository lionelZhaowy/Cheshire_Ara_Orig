# E01 / 本地与服务器重建范围对比

## 修改记录

| 日期 | 角色 | 输入版本 | 修改与验证摘要 |
| --- | --- | --- | --- |
| 2026-10-18 | E01 调查／文档，结合 S01/V01 | 本地 `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`；服务器 Cheshire `e040b7bbc…`、Ara `2895ba907…`、CVA6 `99eac9a64…` | 只读核对两端、静态追踪 Make，新增范围对比报告；未安装、获取工程依赖、构建、仿真或修复 |

## 基本信息

- 本轮授权：只读调查与两份指定文档编写。交付为调查结果和建议，不是补齐工程授权。
- 状态：调查与文档完成；完整工程复现、回归、Linux/FPGA重建和独立提取未完成。
- 本地原有共享状态、工程专题、软件索引及 E01 文件等修改保持；不代写 PROJECT_STATE/AGENT_TASKS。
- 负责路径：[专题报告](../maintenance/E01/reports/local_server_build_comparison.md)及本交接。无生产接口、配置、地址、RTL、工具或服务器文件变更，未提交 Git。

## 本轮结果

- **源码／只读核查：**两端26项硬件依赖HEAD逐一相同；按服务器VCS清单核对716个直接编译源，本地均存在且hash相同。不能扩大为宏、全部include、软件、工具或全工程等价。
- **SDK：**两端根SDK gitlink为`55c137…`且未初始化；本地只有镜像输出／备份。Ara内SDK实际为`44fdb08…`、服务器嵌套源码已初始化但未构建Linux。根SDK空不妨碍当前裸机GCC路线。
- **本地Linux历史证据：**Buildroot GCC13.2、Linux6.5输出、构建时间日志、rootfs存在；两处install64的9文件逐一相同且非符号链接。符合`linux-img`复制规则，但具体历史命令及Linux启动仍未确认。
- **入口分工：**Cheshire `all`聚合SW/HW/仿真输入；Ara根`all`重建工具；SDK `all`是Linux GCC＋Spike，`images`才构建镜像。五步未省略当前VCS单例所需的LLVM/Verilator/Linux步骤，因为该路线不用它们。
- **已有运行证据重新核对：**服务器run_04的scalar/vector/compare、Passed、SUCCESS、退出0均在；当前ELF/simv hash与输入记录相同。本轮没有重新运行。FS显式Clean修正保留，Dirty根因、S01-T01及完整验收仍开放。
- **纠正历史文件状态：**服务器`sw/tests/fmatmul.c`当前已恢复，hash与Ara原源相同；现有`vector_helloworld.spm.elf`在`0x1000010a`仍为旧FS清位指令。因此不能声称所有向量ELF已随fmatmul一起修正，换测试前须检查所选ELF。
- **新静态缺口：**本地uImage为11,986,507B，根固定GPT内核分区只有8,388,608B；未来默认打包会越过内核分区。Ara根`riscv_tests`引用的`hardware riscv_tests_simc`在所读固定Makefile无定义。`linux-img`增量依赖未自动覆盖所有rootfs应用变化。均未修复、未动态复现。

## 验证证据与边界

- 查询：`git rev-parse/status/ls-tree/submodule status/diff/show`，文件／目录读取、SHA-256、已安装编译器版本和库路径；无 Make/Bender 执行。
- 18项生成文件差异中17项两端相同；AXI-RT hjson仅注释的生成器路径不同。完整26项版本表、工具路径／版本、主要Make目标、五步对应与5条最小路线见报告。
- 服务器运行证据仍在`/home/zhaowy24/CheshireAraPULP/_e01/rvv_fmatmul_04/`；报告附录记录关键hash和复核方法，不复制大trace。
- 文档检查：相对链接、表格列数、空白与范围保护；写入前保存204个已有修改／未跟踪文件hash，交付前复核。临时查询输出仅在本机`/tmp`，不是新增工程框架或交付依赖。
- 未编译／未展开／未仿真／未板测；没有确认LLVM/Verilator历史源码构建命令、完整Linux启动或所有回归。厂商安装只记录路径／版本，不保存受限正文、许可证或凭据。

## 下一步

1. 当前裸机基线不必为“目录齐全”补建根SDK或整套工具；由用户选择扩大验证还是转Linux／FPGA用途。
2. S01/V01接收报告§6：FS Dirty、S01-T01、回归缺口；Linux路线先审镜像分区容量及rootfs增量打包，工具路线先审原recipe的reset/clean/下载副作用。
3. 用户如能提供旧LLVM/Verilator构建目录或日志，再定向补充历史来源；不扫描无关历史。
4. C00如需合并共享状态，仅引用本报告的调查边界和新静态问题，不把文档交付写成重建／回归完成。本轮未修改共享状态。

接手最少阅读：[本报告](../maintenance/E01/reports/local_server_build_comparison.md)、[既有E01主交接](E01_fixed_vector_extraction.md)、[五步核查](../maintenance/E01/reports/reference_rebuild_check.md)。
