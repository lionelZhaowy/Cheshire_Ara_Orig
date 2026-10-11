# LLC 组相联结构与 Cache/SPM 转换图

日期：2026-10-10；输入：`mp/ara-pulp-v2`，HEAD `278434024`。按用户指定 svg-pptx-diagrams skill 绘制；没有实施任何 LLC 配置变更。

## 最终文件

- [PNG 预览](export_final/llc_cache_spm.png)
- [可编辑 SVG](export_final/llc_cache_spm.editable.svg)
- [原生可编辑 PPTX](export_final/diagrams.pptx)：一页，保持源图 3:2 比例，文字/矩形/连接独立，不是整图图片。
- [导出报告](export_final/export_report.json)
- 最终母版：[source_final/llc_cache_spm.svg](source_final/llc_cache_spm.svg)；生成源：[build_figure.py](build_figure.py)。根目录早期 SVG 与 export/ 为中间版本，保留但不作为最终交付。

## 图中包含的关系

1. 左侧展示全 Cache 的逻辑基线：8 way、256 组，每组在 8 个 way 中各有一个候选行；Tag/V/D 与数据行分属不同 SRAM 阵列。图中的组 42 / Way 6 命中是教学举例，不是运行波形。
2. Cache 地址分解来自当前 48-bit AXI 地址与 64-bit 数据配置：Tag[47:14]、Set[13:6]、Block[5:3]、Byte[2:0]。Way 由 Tag/Valid 命中或替换选择，不是请求中的独立 Cache 地址字段。
3. 每行 8×8B=64B，每 way 256×64B=16KiB；总数据阵列 128KiB，不把 tag 存储计入此数据容量。
4. CFG_SPM 的有效位每位对应一个 way，1 为 SPM，0 为 Cache。0x00 为全 Cache，0x0F 为教学混合示例，0xFF 为 Boot ROM 等待 BIST 后提交的全 SPM 用途。
5. SPM 直接按固定地址槽选择 way，不做 LLC Tag 命中比较；仍需该 way 已配置为 SPM。槽大小16KiB，槽不会因位图稀疏而紧凑重排。Way2为[0x10008000,0x1000C000)，示例0x10008AAB对应Way2/组42/块5/字节3。
6. 全 SPM 并完成提交后，DDR 地址流量走 LLC 旁路，SPM 地址仍访问本阵列。SPM 不代表所有上游缓存都被禁用；当前0x14000000未缓存别名在SoC内重映射到同一SPM，CPU L1属性及共享协议还需核对。
7. 切换由软件写位图/提交与硬件FSM协调完成。转换不是把数据复制到新增RAM；必须先保护相关代码、栈和数据，并处理在途事务与缓存副本。反向SPM→Cache后，原SPM内容不再受固定驻留保护。

官方历史 LLC 文档部分将 way 称为 set；本图采用常见 Cache 术语：`LlcSetAssoc=8` 是8个way，`LlcNumLines=256` 对应256组/每way256行，不把它误解释成只有8组。

## 源码依据

- `hw/cheshire_pkg.sv`：DefaultCfg 的 AXI地址/数据宽度及 LLC 参数、`spm_size()`、SPM别名。
- `hw/cheshire_soc.sv:501`：别名重映射；`gen_llc.i_llc`：实例与控制连接。
- `.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/src/axi_llc_top.sv:252`：Tag/Index/Block/Byte字段与容量。
- `axi_llc_burst_cutter.sv:68`：固定per-way SPM地址槽与way_ind译码。
- `axi_llc_hit_miss.sv`、`hit_miss_detect/axi_llc_tag_store.sv`：SPM/Cache用途检查、Tag+Valid比较及错误响应。
- `axi_llc_data_way.sv:119`：每way数据SRAM；`axi_llc_config.sv:408`：提交、隔离/等待、刷新及旁路控制。
- `hw/bootrom/cheshire_bootrom.S:65`：BIST后提交全SPM。
- [官方 LLC 文档](https://github.com/pulp-platform/axi_llc/blob/master/doc/axi_llc.md)：补充说明；实际实现以本地固定源码为准，未升级依赖。

## 检查边界

技能导出器重新读取 PPTX，确认297个原生对象、177个文本对象逐项保留，最小文字10.2pt；ZIP完整，无ppt/media/整图。使用Microsoft YaHei字体度量，母版提供浏览器字体回退。最终PNG为Chrome本地渲染，已人工核对矩阵行间距、标题、地址与流程。

尝试运行本机PowerPoint只读验证脚本时被数字签名策略拒绝，未打开文稿；**Office实际显示/编辑尚未验证**，SVG预览不能替代此项。没有改变执行策略。

静态算术检查确认64B/行、16KiB/way、128KiB总数据容量及地址示例。没有编译/仿真/板测，没有声称Cache/SPM动态转换已经验收。
