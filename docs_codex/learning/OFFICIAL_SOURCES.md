# 本轮官方资料与本地版本的对应关系

核对日期：2026-09-29。阅读原理以官方资料为补充，实现结论以当前本地消费者为准。网站正文及配图离线自足，下面的外部链接只用于进一步追溯。

| 官方资料 | 本轮实际阅读及用途 | 版本边界 |
| --- | --- | --- |
| [Cheshire Architecture](https://pulp-platform.github.io/cheshire/um/arch/) | 系统层次、地址区域和启动说明 | 在线文档没有绑定本地 HEAD；大区域常表示预留空间，实际窗口按 `gen_axi_out/gen_reg_out` 重算 |
| [Cheshire SoC Integration](https://pulp-platform.github.io/cheshire/tg/integr/) | 配置结构、扩展接口、VIP 与 Platform ROM 的前置条件 | 官方建议的 Bender 流程是参考，用户独立固定配置/静态清单方向继续有效 |
| [Ara dispatcher 官方说明](https://github.com/pulp-platform/ara/blob/main/docs/source/modules/ara_dispatcher.md) | 算术早应答、load/store 等待地址与异常的概念 | main 文档不能证明冻结版本的总线错误支持；本地 vstu 明确仍有 B 错误 TODO |
| [RVV 官方归档 v1.0](https://github.com/riscvarchive/riscv-v-spec/blob/v1.0/v-spec.adoc) | 分组、mask/tail、按 vl 分块、访存与归约语义 | 使用明确的 v1.0 标签；不是硬件支持矩阵 |
| [RISC-V 20240411 V 页面](https://docs.riscv.org/reference/isa/v20240411/unpriv/v-st-ext.html) | 对照术语及章节 | 本次页面标题为 Version 1.0，导言却含 1.1-draft 字样；不静默抹去差异，冻结语义另交叉查 v1.0 归档 |
| [GCC 15.2.0 RVV intrinsics](https://gcc.gnu.org/onlinedocs/gcc-15.2.0/gcc/RISC-V-Vector-Intrinsics.html) | 头文件入口及该版手册声明的 intrinsic 0.11 | 本地 GCC 实际宏为 `__riscv_v_intrinsic=12000`，以本轮具体函数编译和 dump 验证可用性，不将不同网页/API 版本混同 |
| [GCC 15.2.0 RISC-V options](https://gcc.gnu.org/onlinedocs/gcc-15.2.0/gcc/RISC-V-Options.html) | ISA、ABI 和代码模型选项 | 参数只声明编译目标；不能改变 RTL profile 或 VS/FS |
| [Arm AMBA AXI/ACE IHI0022H PDF](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf?revision=71bd7c57-2ed7-487b-bc3e-68c4ab56fa5f&la=en&hash=6325311012DDADF238C35A6C0FD734E520754F82) | A3 握手依赖、通道与 AXI4 事务规则 | PDF 同时包含 AXI/ACE 多种协议；本工程普通 AXI4 不因此自动实现 ACE 或全部新扩展。网页入口重定向无正文，实际读取了官方 PDF |
| [pulp-platform riscv-dbg README](https://github.com/pulp-platform/riscv-dbg/blob/master/README.md) | DTM/DM、abstract/progbuf/SBA 功能边界 | 具体 DMI 字段及 0.13.1 声明核对本地 README/dm_pkg；不把在线 master 当当前 RTL |
| [WaveDrom 官方项目](https://github.com/wavedrom/wavedrom) | 标准波形描述和 SVG 输出 | 离线渲染固定 3.5.0；来源、包哈希、许可证保存在 `assets/vendor/wavedrom-3.5.0/` |

本地根 HEAD 为 `4f240258ca683913b7e17949aff23139bff981f1`。`Bender.yml` 指定 CVA6 `pulp-v2.0.0-alpha.1`、Ara `2895ba907e9eb14b3464609dc791a969d159a7c3`，但本地依赖和修改纳入主仓库，不能用上游标签替代内容哈希。固定版本 Ara/CVA6 在线路径本轮读取失败，CVA6 在线手册也未取得有效正文；改读本地随依赖提供的 README、FUNCTIONALITIES、lane 文档和实际 RTL，未声称成功取得这些失败的网页。

本地证据入口：

- [本地来源哈希](evidence/depth-20260929-sources.json)
- [工具链/构建实测](evidence/depth-20260929-builds.txt)
- [扩充章节与证据分工](DEPTH_EXTENSION.md)

配图不得复制厂商受限数据手册。新架构图为按本地连接重绘的教学抽象；新时序图全部保留 WaveDrom JSON 与离线 SVG，明确标注教学时序。真实波形应额外标明运行配置、信号层次、时间单位及仿真产物，不能用教学图冒充。
