# DMA 按次配置补丁与验证记录

状态：已部署服务器并重新构建、运行测试；9 个用例目标返回 0，非对齐/不同步长用例停滞，整体定向验收未通过。实际结果和适用范围见[DMA 长度与布局测试](../../reference_rebuild_check.md#dma-aw-config-20261020)。最初连接超时时仅完成本地编译，此后经 Windows SSH 继续实施。

- `backport.patch`：四个文件的局部差异。HAL 配置接口来自 Paul Scheffler 的 Cheshire `4c2390f25f250c9ea75d314dd107da11a52aa8fa`（PR #189），保留前次四类 32 位 MMIO 指针修正。原三个测试只增加 `DMA_CONF_DECOUPLE_NONE` 参数，保持原配置行为；不同于上游 AXI-RT 测试改用 ALL，本次不扩展其运行模式。
- `official_hal.diff`：官方提交中的 HAL 原始差异，供比对来源。
- `patch_inputs.json`：各文件预期修复前后 SHA256。HAL 修复前为之前服务器实测版本；三个测试的修复前为 Cheshire `e040b7bbc` 的 Git 内容。本次部署前已再次核对现场文件；后续使用仍需检查实际输入，不能据此覆盖未知修改。
- `dma_long_aw_api.c`：原长搬运测试仅增加 AW 配置参数，三次 32×256 字节、编号/等待/数据/保护区检查保留。服务器已重新构建并运行三笔；本地编译记录作为前期检查保留。
- `hal_api_check.c`、`mmio_disassembly.txt`：接口编译与访问宽度检查；四个 memcpy 接口均编译，CONF 为单次 `sw` 写 0x401，NEXT_ID/DONE_ID 各一次 `lw` 后零扩展，地址/长度仍为 `sd`。
- 两份 `*_compile_results.json`：本地命令及退出状态。使用 GCC 15.2.0；服务器原环境是 GCC 13.2.0，结果不可替代服务器构建。严格 -Werror 首次因既有链接符号 `__base_dma` 声明导致 array-bounds 诊断失败；只把该类降为 warning 后，修复前后均为 61 条，编译退出 0，未改链接符号声明或关闭全部警告。

本地 FPGA 的 `sw/`、RTL 和依赖未修改。详细状态及后续测试项见[DMA 长度与布局测试](../../reference_rebuild_check.md#dma-aw-config-20261020)。

- `dma_aw_layouts.c`：同 bank 反向、跨 bank/4 KiB、非对齐不同步长、CPU 并发的定向用例；`CASE=0..3` 分别构建，各执行两次搬运。
- `run_summary.json`、`protection_result.json`、`server_build_commands.json`、`server_layout_build_commands.json`：服务器实际结果摘要、保护检查和软件构建命令。详细日志、trace 和 ELF 留在服务器 `$AW`（路径见报告）。

- `unaligned_diagnosis.json`、`unaligned_stop.json`：失败运行的主动停止记录及 600 μs/1 ms/2 ms 内部采样；诊断退出 0 不表示程序通过。
