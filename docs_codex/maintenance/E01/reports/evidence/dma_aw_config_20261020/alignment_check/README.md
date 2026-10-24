# DMA 软件对齐粒度检查

2026-10-20；完整参数表及结论见[对齐粒度检查](../../../reference_rebuild_check.md#dma-alignment-check-20261020)。11 组中 6 组连续两笔通过、5 组持续写挡读；诊断退出不算通过。

- `case.c`、`variants.json`：同一测试副本与各组参数，含数据、源区、行间隙和保护区检查。
- `build_commands.json`、`results.json`：实际软件构建、运行命令、ELF/simv 哈希、目标结果、主机退出及内部状态。未重建 RTL。
- `input_hashes.json`、`protection.json`：两组运行的根 Git diff、85 项输入保持；包含已修断言的 CVA6 文件。
- `assertion_review.json`：另一位 Agent 的断言修复复核；现有文件、日志、ELF 和 trace 匹配。不是本轮重新运行其三项回归。

服务器完整产物在 `~/CheshireAraPULP/_e01/dma_vector_check/aw_config_20261020/alignment_check_20261020/`，后六组在 `factor_checks/`。同目录的 `window_probe.tcl` 与每个运行目录的 `probe.tcl` 保存诊断方法，600 μs/2 ms 状态不变且满足写挡读条件才标记持续循环；否则继续等待程序完成。每例主机上限 600 秒。日志、trace、ELF 留服务器。
