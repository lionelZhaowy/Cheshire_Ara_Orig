# L01 / CLIC 功能与硬件问答

## 基本信息

- 日期：2026-10-09；范围：解释 CLIC 可选性、功能、当前 RTL 和配置影响。
- 输入：分支 `mp/ara-pulp-v2`，HEAD `2784340240915fe4338ec54bfd613723b127d62e`。
- 工作区已有 M01 文档修改及多份未跟踪交接/图目录，未触碰。
- 状态：完成静态分析；只新增本交接，无生产代码或共享状态修改、无提交。

## 本轮结果与依据

- `hw/cheshire_pkg.sv`：DefaultCfg.Clic=0；gen_cva6_cfg 覆盖 RVSCLIC=cfg.Clic；启用时添加每核 MMIO 窗口，基址 0x08000000、步长 0x40000。
- `hw/cheshire_soc.sv::gen_clic`：每核可选实例，SSCLIC=1/USCLIC=0；PLIC/CLINT 实例不受 Clic 开关控制；系统源既可直接进 CLIC，也可经 PLIC 汇总进 CLIC 的 MEIP/SEIP 槽位，需软件避免重复使能。
- 当前默认尺寸 16 个 core 槽位 + 58 个内部源 + 0 外部源 = 74；UART 的 PLIC 编号 1 对应 CLIC 直接源 17。
- 本地 clic 的 src/clic_gateway.sv：正沿检测、软件 pending、单 pending 位、接受后内部 claim 清边沿请求；电平请求跟随源。src/clic_reg_adapter.sv 明确只实现正沿/高电平。
- src/clic_target.sv：IP & IE 过滤，二叉比较树按 mode、ctl 仲裁，完全相同选较低 ID；IDLE/ACK/CLAIM 和 kill 握手。74 源树展开为 128 叶、7 层比较；这不是 7 个时钟周期或实测时延。
- CVA6 core/cva6_clic_controller.sv：同特权级比较新 level 与 max(intthresh, intstatus 当前 level)，并由 CSR/decoder 配合处理中断许可。
- 本地 clic/doc/clic.adoc 为 2021-07-20、0.9 Development 快照；Bender.yml 声明 2.0.0，但 Bender.local/lock 使用路径快照，不能据目录后缀推断 Git commit。
- CLIC README 的“CVA6 Not supported yet”与本工程 CVA6 专用控制器/端口和测试冲突，应以当前实现为准；不代表完整规范符合性。
- CVA6 core/csr_regfile.sv:2589 起明确有意偏离规范：SHV 直接执行表项，不加载表项内地址；实际入口替换地址 [7:2] 为 cause[5:0]。高于 63 的 ID 存在入口别名风险（静态推断），IRQ31 测试未覆盖。
- sw/tests/clic_basic.spm.S：mtvec 模式3、mtvt 跳转表、IRQ31 软件 pending、nlbits=4、ctl=0xaa、门限 ff/00；示例以 ret 返回，不是完整嵌套 ISR/mret 验证。

## 验证证据

- 仓库根执行 git status --short、git rev-parse HEAD、git branch --show-current；用 rg/sed/cat 定向读取以上源码、PROJECT_STATE、AGENT_TASKS、最新关联交接和模板。
- 联网读取官方 https://pulp-platform.github.io/cheshire/um/arch/ ，并检索 https://github.com/pulp-platform/clic 与 https://github.com/riscv/riscv-fast-interrupt 。部分 raw URL 读取失败，具体旧版实现结论取本地快照。
- 未编译、未仿真、未综合、未板测；面积/延迟无测量结果。

## 决策与下一步

- 用户未决定启用 CLIC，也未授权修改 RTL；普通 NPU/ISP 完成通知不单独构成启用必要性。
- 若要启用，先使用现有 SELCFG=2 标量示例验证，再增加外设电平清源、完整现场/mret、嵌套和高编号入口用例；Ara+CLIC 不由现有 SELCFG=3 自动启用。
- 最少续读：hw/cheshire_soc.sv、clic/src/{clic,clic_gateway,clic_target}.sv、CVA6 core/{cva6_clic_controller,csr_regfile}.sv、sw/tests/clic_basic.spm.S。
- 共享状态无需因本次问答改写；高编号向量入口限制供后续 V01 验证参考。
