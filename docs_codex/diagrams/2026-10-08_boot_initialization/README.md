# 初始化对应关系与程序执行流程图

日期：2026-10-08；输入：`mp/ara-pulp-v2`，HEAD `278434024`。当前源码关系及控制流推导，不是新增运行验收。

## 最终交付

| 内容 | SVG | PNG |
| --- | --- | --- |
| 初始化软硬件对应关系 | [结构化 SVG](export_final/initialization_hw_sw.editable.svg) | [预览](export_final/initialization_hw_sw.png) |
| 从复位到应用返回的程序流程 | [结构化 SVG](export_final/program_execution_flow.editable.svg) | [预览](export_final/program_execution_flow.png) |

- [两页原生可编辑 PowerPoint](export_final/diagrams.pptx)：图形、连线、箭头和文字分别为原生对象，非整图图片。
- [导出检查报告](export_final/export_report.json)：85/83 个对象，50/47 个文本对象；保存后重新读取，文字与对象数量一致，无内嵌整图 SVG/位图。
- 根目录两份 SVG 是最终母版；`export/` 是留白调整前的中间版本，保留但不作为最终交付。

## 技术范围

第一图对应启用内部 LLC、Bootrom=1、PlatformRom=0 的结构。所有软件阶段由同一个 CVA6 执行；LLC 的 tag BIST 是硬件自主执行。SPM 使用 LLC 数据阵列；tag BIST 不覆盖该数据阵列，DONE 不代表所有错误位为零。

第二图以 boot_mode=2 的 SPI NOR 自主启动为代表：ROM S → ROM C → gpt 装载 → boot_next_stage 地址调用 → 载荷 CRT0 → main → 应用_exit。main 正常返回不自动停机、换权限、复位或断电。scratch2 是完成通知，仿真 TB 可以据此终止仿真。

当前 ROM 的 boot_next_stage 未保存上一层 ra；普通载荷恢复入口 ra 后返回时，按源码可形成尾部 ret 自返回循环。图中已标为源码推导，未声称目标仿真通过。JTAG 直接改 PC、UART invoke、OS 用户程序退出是不同返回契约，不直接套用本图。

Platform ROM 非零普通返回另有已登记的 S01-B01 缺陷，图中默认跳过它，不将未修复路径画成正常返回。

## 来源与检查

- `hw/cheshire_soc.sv`、`hw/bootrom/cheshire_bootrom.S/.c`、`sw/lib/crt0.S`、`sw/lib/gpt.c`、`sw/link/rom.ld`。
- `.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/src/{axi_llc_hit_miss.sv,axi_llc_config.sv}`、`hit_miss_detect/{axi_llc_tag_store.sv,axi_llc_tag_pattern_gen.sv}`；来源 commit `559bcbd09a5a884dbe31e2d72fd95d024e357f39`。
- 使用用户指定的 svg-pptx-diagrams skill：SVG 保留 text；导出脚本生成原生 PPTX，未把文字转路径或栅格化。
- 最终 SVG 已用本地 Chrome 渲染并人工检查两张 1600×900 预览。PPTX ZIP 完整，无 ppt/media/。
- Windows PowerPoint 验证脚本被当前脚本签名策略拒绝，未打开文稿，因此 **Office 实际打开/编辑/导出未验证**。未修改执行策略，SVG 预览不能代替 PPTX 在 Office 的外观验证。
- 未编译生产软件或 RTL，未运行 SoC/板级测试；本轮没有修改生产代码。
