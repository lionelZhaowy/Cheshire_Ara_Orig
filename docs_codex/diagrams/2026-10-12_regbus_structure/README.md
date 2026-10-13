# Cheshire 公共 Regbus 结构

2026-10-12；L01 图稿。输入 HEAD：`c4162204cfee0c48b81158b4296860a678d92bec`。按当前 RTL 绘制，使用 `industrial-svg-pptx` 风格与 `svg-pptx-diagrams-native` 原生导出后端。

- [PNG 预览](regbus_structure.png)
- [SVG 母版](regbus_structure.svg)
- [原生可编辑 PPTX](regbus_structure.pptx)
- [导出报告](export_report.json)、[检查结果](validation.json)、[输入源码哈希](source_hashes.json)

## 范围与读图

公共配置路径为主 AXI Crossbar 的 `AxiOut.reg_demux` → `i_reg_atomics` → `i_reg_atomics_cut` → `i_axi_to_reg_v2` → `i_reg_demux`。`addr_decode` 读取 `reg_in_req.addr` 和静态 `RegMap`，输出 `reg_select`，控制请求分发与响应选择。解码器不是串在数据通路中的寄存器桥。

紫色和蓝色双向箭头分别合并表示 Regbus、AXI 请求与响应；不表示一根双向电气导线，也不表示 Regbus 可并发读写。每个目标有独立请求/响应结构体，横向 demux 长条不是把所有从设备输出短接在一起。绿色单向线表示地址或选择控制，`RegMap` 方块表示 elaboration 时生成的静态规则，不是运行期可编程硬件寄存器。

目标按 `gen_reg_out()` 的 16 类正常功能，加错误响应与外部扩展展开；CLIC 和 Bus-error 的重复实例合并表示。单核且对应功能均开启时，16 类对应 18 个正常目标（Bus-error 展开为 3 个）。虚线表示映射或扩展端口受 `Cfg` 控制，不代表当前平台已全部启用。Bus-error 单元实际实例化还受对应 VGA/iDMA/CPU、BusErr 等条件约束。

公共桥的数据宽度固定为 32 bit，地址宽度随 `Cfg.AddrWidth`，默认 48 bit；主 AXI 数据宽度随 `Cfg.AxiDataWidth`，默认 64 bit。`RegAmoPostCut` 控制切片旁路，`RegAdaptMemCut` 控制桥内部请求切片。两者均不分频。

此公共桥及内部寄存器访问使用 SoC `clk_i`；`addr_decode` 和 `reg_demux` 为组合逻辑。时钟域边界指寄存器访问路径，不声称 USB、Serial Link 等外设的全部功能电路都只有一个时钟。外部 RegExt 端口属于系统接口时序域，外部 IP 使用其他时钟时需要适配；本图没有加入尚未实施的 `reg_cdc` 或供应商 APB 桥。

一级原 Regbus 窗口为 `[0x0200_0000, 0x0c00_0000)`，扩展 `RegExtRegion*` 也会进入 AXI 地址表并指向该分支；二级未匹配请求默认转向 `RegOut.err`，由 `reg_err_slv` 返回错误。iDMA 配置使用独立 AXI 目标及自身 wrapper 内的转换，不在图示公共分支中。NPU/ISP/PLL/DDR/LVDS 的候选配置银行尚未接入，故未画成已有外设。

## RTL 依据

| 图中对象 | 本地源码与符号 |
| --- | --- |
| 公共 AXI→Reg 路径、解码、demux、error、扩展口 | [cheshire_soc.sv](../../../hw/cheshire_soc.sv)，约 295–440 行 |
| 地址规则与目标类别 | [cheshire_pkg.sv](../../../hw/cheshire_pkg.sv)，`gen_axi_out()`、`gen_reg_out()` |
| 公共数据/选通宽度 | [typedef.svh](../../../hw/include/cheshire/typedef.svh)，Reg 类型生成宏 |
| 协议、桥、组合分发 | [register_interface](../../../.bender/git/checkouts/register_interface-902ad5bfde7bb98c/README.md)，`include/register_interface/typedef.svh`、`src/axi_to_reg_v2.sv`、`src/reg_demux.sv`、`src/reg_err_slv.sv` |
| 地址选择与默认目标 | [addr_decode.sv](../../../.bender/git/checkouts/common_cells-7f7ae0f5e6bf7fb5/src/addr_decode.sv) |

## 复现与验证

从仓库根目录执行，SVG 和导出目录必须是新的位置。`build_regbus.py` 拒绝覆盖已有 SVG；后端拒绝覆盖非空输出目录。

```sh
python3 docs_codex/diagrams/2026-10-12_regbus_structure/build_regbus.py --output /tmp/regbus-rebuild.svg
native_skill_root="$HOME/.codex/skills/svg-pptx-diagrams-native"
python3 "$native_skill_root/scripts/run.py" --input /tmp/regbus-rebuild.svg --out-dir /tmp/regbus-rebuild-export --aspect source --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc
"$native_skill_root/.venv/bin/python" docs_codex/diagrams/2026-10-12_regbus_structure/verify_regbus.py
```

PNG 使用本地 CairoSVG 2.9.1 从 SVG 渲染，画布为 2400×1350（16:9）。PPTX 保存重读检查通过：135 个原生对象、77 个文本、28 个原生箭头对象、15 个虚线对象，无 `ppt/media/` 栅格图片。SVG/PPTX 文字一致；文泉驿字体度量下文本互相重叠及画布越界为 0。已查看最终 PNG，移开了端口连线上的文字；自动几何检查不替代目视布局检查。

PPTX 字体为 Microsoft YaHei，未嵌入；本机 PNG 字体回退为文泉驿。Office 显示/编辑未实测，箭头未绑定模块端口，移动模块不保证连线自动跟随。仅完成图稿与静态检查，未修改生产 RTL、未编译/仿真/板测，不新增频率或功能验收结论。
