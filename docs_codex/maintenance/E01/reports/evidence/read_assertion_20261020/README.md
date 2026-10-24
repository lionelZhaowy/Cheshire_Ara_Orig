# CVA6 读返回断言修正与验证

2026-10-20，服务器参考工程 CVA6 `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c` 的局部修正。完整说明、前后代码与行号见[断言修复与测试](../../reference_rebuild_check.md#read-assertion-fix-20261020)。

- [assertion.patch](assertion.patch)：两份源码的完整前后差异。只修改服务器的 `wt_cache_subsystem.sv` 和 `wt_dcache_ctrl.sv`，本地对应生产源码保持原样。
- [patch_inputs.json](patch_inputs.json)：修改前后 SHA256。复用补丁前须核对实际输入，不覆盖未知差异。
- [tb_read_assertion.sv](tb_read_assertion.sv)：实例化实际读控制器的定向测试，不复制判断逻辑充当 DUT。
- [unit_result.json](unit_result.json)：54 项检查逐项记录，包括 33 次预期数据警告、2 次预期元信息警告；负例是否符合预期按每项核对，不按全局忽略警告判定。
- `build_commands.json`、`unit_build_commands.json`、`soc_results.json`：新 RTL 构建和相同 ELF 的实际回归命令、输入哈希与结果。
- `protection_result.json`、[functional_text_check.json](functional_text_check.json)：保护检查与移除 translate_off 区域后的源码一致性检查；后者不是综合/形式等价证明。

服务器完整产物：`~/CheshireAraPULP/_e01/dma_vector_check/read_assertion_20261020/`。原件位于 `before/`，构建日志及 simv 位于 `rtl_build/`，定向日志位于 `unit_run/`，三项 SoC 日志和 CPU trace 位于 `run_*/`。日志、编译库、ELF 不拷回本地。没有提交或发布上游 PR。
