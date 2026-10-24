# DMA 地址、行长、步长联合验证

2026-10-20，完整参数表、实际结果和原因见[主报告](../../../reference_rebuild_check.md#dma-joint-alignment-check-20261020)。首批 17 组为 14 通过、3 失败；`lock_checks/` 三次为 2 通过、1 失败复现。20 次运行不是 20 个不同用例。

- `case.c`、`variants.json`、`build_commands.json`：测试源码、实际参数和软件构建命令。每组两笔；逐字节检查目的区及空隙/保护区，源区未修改，编号推进并实际等待。
- `results.json`、`log_summary.json`：命令、实际 ELF/simv 哈希、运行时间、主机状态、完成日志、内部采样。`success=false` 不因主机退出 0 而计通过。
- `window_probe.tcl`：只读 UCLI 采样，无 force 或波形。首次 `dense_rows` 到 20 ms 仿真时间仍未完成；行锁复跑在 600 μs/2 ms 持续相同条件后诊断退出。
- `input_hashes.json`、`protection.json`：各批运行前后根 Git diff 和 85 项输入保持。
- `lock_checks/source_confirmation.json`：原因分析涉及的六份源文件与本地哈希一致，失败复跑 `.text` 与首次完全一致。ELF 含不同构建路径信息，不声称 ELF 整文件相同。
- `lock_checks/bloom_check.py/json`：按实际 16 bit 输入、6 bit 哈希、一轮置换/异或及固定种子复算两个锁键；源查询位图 `0x11`、目的占用位图 `0x20011` 与实际 RTL 采样一致。此计算解释本次反例，不是独立的 RTL 正确性测试。

服务器根：`~/CheshireAraPULP/_e01/dma_vector_check/aw_config_20261020/joint_alignment_check_20261020/`；完整日志、trace、ELF、编译产物留服务器。复用已修断言的 simv，未重建或修改 RTL/HAL。每例串行、主机上限 600 秒，无波形。
