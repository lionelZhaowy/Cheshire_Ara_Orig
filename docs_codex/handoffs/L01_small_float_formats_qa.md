# L01 / CVA6 小位宽浮点格式答疑

> 记录日期：2026-10-09。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-09；授权范围：解释 XF16/XF8 与 ALT 格式、定位 RTL。
- 输入：mp/ara-pulp-v2，HEAD 2784340240915fe4338ec54bfd613723b127d62e。
- 现有 engineering/IP_DDR_Interface_Contract.md 修改及未跟踪交接/图目录保留。
- 状态：源码答疑完成，非功能验证；仅新增本交接，未提交。

## 本轮结果（源码确认）

- `.bender/git/checkouts/fpnew-ed006ec0a4178e29/src/fpnew_pkg.sv:21` 定义 FP16=1/5/10、FP16ALT=1/8/7、FP8=1/5/2、FP8ALT=1/4/3（符号/指数/显式尾数）。ALT 是格式区别，不是替代微架构。
- CVA6 `core/include/cv64a6_imafdcv_sv39_config_pkg.sv:18` 四项全为0；`hw/cheshire_pkg.sv:489` 的 gen_cva6_cfg 不覆盖这些项。
- CVA6 `core/include/build_config_pkg.sv` 派生 FpPresent、FLen、非标准向量标志，复制四个配置位。
- `core/decoder.sv:1087`起控制小宽度浮点访存；1164、1174 等位置检查运算格式与替代半精度编码。
- `core/ex_stage.sv:429` 实例化 fpu_wrap；`core/fpu_wrap.sv:63` 组装 FPU_FEATURES.FpFmtMask；536 实例化 fpnew_top。
- FPnew `src/fpnew_opgroup_block.sv:97` 根据格式掩码生成运算 slice；`fpnew_opgroup_fmt_slice.sv:119` 实例化 fpnew_fma；`fpnew_fma.sv:59` 按 FpFormat 推导指数/尾数宽度。转换位于 fpnew_cast_multi。
- 发现边界：XF8ALT 进入格式掩码和延迟配置，但当前 decoder 无 XF8ALT 消费，fpu_wrap 格式选择与转换源选择没有 FP8ALT 分支。不能把设1解释为 CPU 已有可用 FP8ALT 指令入口；底层能力与 CPU 集成不等价。
- XFVec 为 CPU FPU 的 packed SIMD；Ara 独立 FPUSupport/FPExtSupport，不能混为 RVV 开关。

## 版本和官方依据

- `.bender/SNAPSHOT.tsv`：CVA6 来源99eac9a649001bdf5b8f9da52e0ca73d5c48db1c；FPnew 来源e5aa6a01b5bbe1675c3aa8872e1203413ded83d1；vendor有本地差异。
- Bender.local:19 与 target/xilinx/scripts/add_sources.vcu118.tcl:201 指向独立 fpnew checkout，不能只看 CVA6 内嵌副本。
- 官方 https://github.com/openhwfoundation/cvfpu 的 README 用于解释可参数化格式、格式转换和 packed SIMD；当前网页不作为本地版本指令支持证据。固定来源提交 raw URL 本次 web 返回 Cache miss，具体位宽及集成结论以本地源码为依据。

## 验证证据与下一步

- 仓库根执行 git status --short、git rev-parse HEAD、git branch --show-current，以及定向 rg/sed/cat；静态追踪配置→译码→wrapper→运算模块。
- 未编译、未仿真、未板测；未修改生产 RTL、软件、配置或共享状态。
- 如后续要求启用，先确定需要的格式及工具链指令编码，再验证译码、格式转换、舍入和特殊值；XF8ALT 需先处理 CPU 格式入口缺口。
- 当前没有项目实施状态变化，无需 C00 合并共享状态。
