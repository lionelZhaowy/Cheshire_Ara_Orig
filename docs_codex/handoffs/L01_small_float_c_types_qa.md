# L01 / 小位宽浮点 C 类型与当前软件支持

> 记录日期：2026-10-09。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-09；任务：源码答疑与轻量编译探针。
- 输入：HEAD 2784340240915fe4338ec54bfd613723b127d62e，mp/ara-pulp-v2；已有 M01 文档修改及未跟踪交接保留。
- 状态：答疑完成；仅新增本交接，未提交，无生产配置变更。

## 结果与证据

- 本机 riscv64-unknown-elf-gcc (g5115c7e44) 15.2.0 接受 `_Float16` 和 `__bf16`，sizeof 均为2。
- 根 sw/sw.mk:26 默认 `-march=rv64gc_zifencei -mabi=lp64d`。相同 ISA 下非恒定输入加法探针生成：半精度 `__extendhfsf2`→`fadd.s`→`__truncsfhf2`；BF16 `__extendbfsf2`→`fadd.s`→`__truncsfbf2`。不是直接半精度/BF16 运算指令。
- 两种探针均完成编译汇编及 `-nostdlib -Wl,-e,add -lgcc` 最小链接；该 ELF 不含平台启动，不是可直接运行的 Cheshire 程序。未仿真/板测。
- `_Float8` 和 `__fp8` 的语法探针均报 unknown type name；不能推导其他所有编译器都不支持 FP8。
- Ara apps/fdotproduct/kernel/fdotproduct.c:170 有 `_Float16` 点积，含旧版 RVV intrinsic 和内联汇编两条分支；apps/dtype-matmul/kernel/hp-fmatmul.c 有半精度矩阵乘法。存在源码不代表当前工具链完整构建或目标运行通过。
- 定向检索根 sw 和 Ara apps 未找到 __bf16/__fp8/_Float8/float8_t/bfloat16_t 应用类型使用；未声称扫描所有 SDK/vendor 后得出全仓库绝对不存在。
- FPnew tb/flexfloat/examples/example01.c:38 有 `{5,10}` 和 `{8,7}` 的 C 软件模型示例；flexfloat_t/ff_add 属测试参考计算，不是 CPU XF* 指令封装。
- 继承上一交接：当前向量 CPU profile 四个 XF* 均关；XF8ALT 的 CPU 格式入口缺口仍在。`__bf16` 类型存在不等于匹配本地 XF16ALT 非标准编码。

## 可复核命令与产物

临时目录 `/tmp/cheshire-fptypes-pv6zHU`（临时证据，非仓库长期资产）：probe.c、half.s、bfloat.s、half.elf、bfloat.elf。

probe.c 核心为 `typedef FP_TYPE scalar_t; _Static_assert(sizeof(scalar_t)==2, "expected 16-bit type"); scalar_t add(scalar_t a,scalar_t b){return a+b;} scalar_t from_float(float a){return (scalar_t)a;}`，默认 FP_TYPE=_Float16。

编译：`riscv64-unknown-elf-gcc -O2 -march=rv64gc_zifencei -mabi=lp64d -S probe.c -o half.s`，BF16 加 `-DFP_TYPE=__bf16`；最小链接将 `-S` 替换为 `-nostdlib -Wl,-e,add` 并加 `-lgcc`。编译及链接无错误输出。

官方补充：https://gcc.gnu.org/pipermail/gcc-patches/2022-July/597965.html ，https://gcc.gnu.org/onlinedocs/gcc/RISC-V-Options.html 。当前网页只解释类型/ISA层次，本地版本行为由实测确定。

## 下一步

- 若启用硬件低精度，分别确认 CPU 标量指令与 Ara 向量路径，核查生成指令、工具链版本和运行时转换库。
- FP8 若只作为缓冲区编码，可用 uint8_t 保存位模式，但需显式转换/运算函数；这不是浮点 C 原生类型。
- 无共享实施状态变化，无需更新 PROJECT_STATE/AGENT_TASKS。
