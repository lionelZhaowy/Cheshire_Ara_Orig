# DMA 新死锁原因复核（2026-10-20）

结果及解释见[原反例与单变量对照](../../../reference_rebuild_check.md#dma-cause-confirmation)。服务器目录为 `~/CheshireAraPULP/_e01/dma_vector_check/aw_config_20261020/cause_check_20261020/`。

- `case.c`、`variants.json`、`build_commands.json`：原失败用例的参数化副本和实际构建输入；基准 `.text` 与旧失败 ELF 一致，见 `input_summary.json`。
- `results.json`：原失败内部诊断及 9 组参数运行。基准和 14 行组持续循环；其余 7 组目标返回成功。`cycle` 已排除 UCLI 命令回显；诊断主机退出 0 不表示目标成功。
- `detailed_summary.json`：失败组描述符先后顺序及字节掩码；`burst_summary.json`、`legalizer_summary.json`：2 KiB 分段、实际 AXI/LLC burst。
- `passing_burst_summary.json`、`passing_masks.json`：源起点单变量通过组的读写顺序和 `0x7f → 0xff` 数据有效掩码变化。
- `protection.json`、`rtl_hashes.json`：生产 Git diff/83 项哈希不变，六份原因分析源码与现场一致。

完整日志、CPU trace、ELF 和诊断脚本留服务器。没有修改生产 RTL/HAL，也没有验证通用修复。
