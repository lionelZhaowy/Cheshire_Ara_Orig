# L01 / 官方 Platform ROM 路线与本地返回缺陷核查

## 基本信息

- 日期：2026-10-06；任务 L01。
- 用户授权：分析官方 Platform ROM 初始化路线，纠正此前方案比较的遗漏；只读分析，不修复 RTL/启动源码。
- 输入分支/提交：`mp/ara-pulp-v2`，HEAD `5ddec4fb4`；已有未跟踪图、tools/ 和同日交接全部保留。
- 状态：分析完成；Platform ROM 集成及目标运行未验证。
- 本轮写入：仅此交接和独立 /tmp 诊断工具/二进制；未改生产代码、教材或共享状态，未提交 Git。

## 已确认事实

1. 官方 `docs/tg/integr.md:78` 与在线 [SoC Integration / Platform ROM](https://pulp-platform.github.io/cheshire/tg/integr/#platform-rom) 提供启动关键平台资源设置钩子，列举 clock sources、IO pads、memories、PHYs，也允许自定义引导流程。不是已交付 PLL/DDR 驱动或保证全套初始化都在该阶段的固定流程。
2. `hw/cheshire_pkg.sv:126` 定义 PlatformRom；DefaultCfg 未赋值，通过 653 行 default:'0 得到 0。当前仿真/FPGA 配置未发现覆盖，因而默认跳过。
3. `hw/cheshire_soc.sv:1139` 将 Cfg.PlatformRom 提供给只读 SoC PLATFORM_ROM 寄存器；地址不是软件写该寄存器设定。外部平台需要实现可执行映射、ROM 实体及控制寄存器接口。
4. `cheshire_bootrom.S:59` 先处理 LLC BIST/SPM/栈，80 行再调用 Platform ROM。它由同一个 CVA6 执行，不是独立 RefClk 初始化处理器；需要先提供有效系统启动时钟及可用的 CPU/互连/ROM/LLC，必要时采用 RefClk 旁路。
5. `cheshire_soc.sv:564` 在关闭 Cfg.Bootrom 时允许从 Cfg.PlatformRom 直接复位启动；这是更换引导入口的另一分支，需要平台自己承担运行环境，不能与“内置 ROM 调用平台钩子”混同。
6. `docs/um/sw.md:42` 说明硬件 Boot ROM immutable；平台 ROM 若用 mask ROM 同样不可更新。多次写/等待/轮询与流片后修改算法是不同能力，后者需可更新载荷或显式补丁机制。
7. 当前 `gpt.c:73` 加载介质载荷到 SPM 再执行；`sw/boot/zsl.c:76` 先加载 payload/DTB 到 DRAM，再跳转固件。`sw/include/params.h:43` DTB 为 0x80800000，FW 为 0x80000000。因此图中 DRAM 不能排在 OpenSBI/U-Boot 运行之后才首次就绪，必须在加载之前可用。

## 本轮新发现：Platform ROM 返回路径缺陷

- 当前 `hw/bootrom/cheshire_bootrom.S:86` 为 `jalr t0`，紧接 89 行 `boot_next_stage`；`_boot` 在 112 行。普通 ret 返回后会进入使用 a0 作为下一阶段入口的代码，而非介质启动的 `_boot/main`。
- 仓库已有上游历史提交 `9b4c222df72f74f90ab9f36d80ba7b527f92e62b`，2025-03-31，标题 `hw/bootrom: Fix platform ROM fallthrough to boot (#187)`。提交说明指出 boot_next_stage 插入后破坏平台 ROM 重入；补丁把 _boot/_exit 移到调用之后、boot_next_stage 移到后面。`git merge-base --is-ancestor <该提交> HEAD` 返回 1，当前未包含该修复；不据此自动升级依赖或 cherry-pick。
- [当前上游启动源码](https://github.com/pulp-platform/cheshire/blob/main/hw/bootrom/cheshire_bootrom.S) 也显示 jalr 后紧接 _boot，符合修复后的返回流程。本地版本结论不能套用该最新版。
- 本轮从已纳管 `cheshire_bootrom.sv` 精确抽取 2048 个 32-bit word 为小端二进制，仅作反汇编，没有编译源码。GNU objdump 2.46 确认：

```text
0x020000ae  lw t0,72(t0)       # PLATFORM_ROM
0x020000b2  beqz t0,0x02000154 # 无平台 ROM 时直接到 _boot
0x020000b6  jalr t0            # 普通返回地址为 0x020000b8
0x020000b8  auipc t0,0x1000    # boot_next_stage
0x020000c0  sw a0,16(t0)       # 将 a0 保存为下一阶段地址低字
0x0200014e  jalr t0            # 跳转该下一阶段入口
0x02000154  li t0,0            # _boot
0x02000160  jal 0x020014c0     # C main
```

- 这是源码/已生成指令确认，未做 Platform ROM 目标仿真。默认地址为 0 时绕过该路径，不宣称所有已有启动失败。已有 PLL 答疑只检查钩子，没有核对返回控制流，现明确补充并修正。
- 输入 SHA-256：S 为 `6641c387c8a3d77235bf7aa2617874a205d7fc5abdb5d52cf63b05c7abc078d0`；SV 为 `c6a8f134c290ae8d2da3a0d9ac8c89cb231909f3db3adcb1b6ded40e5da8aa9d`。

## 方案比较的修正与建议

- Platform ROM 是 CPU 软件初始化的早期落点，属于此前方案 2 的一种安排；它与“Flash 加载 SPM 固件后初始化”区别主要在执行时机、代码存储和可更新性，而不是是否需要系统启动时钟或安全 PLL 切换。
- 此前答疑提到 PlatformRom，但随后因偏重用户的流片后更新需求而优先讲 Flash/SPM 路线，未把官方前介质启动路线充分比较，这是分析遗漏；不能声称官方已交付了 PLL/DDR 初始化实现。
- 建议平台 ROM 放进入可靠介质读取之前必须完成的最小平台设置，如必要 PAD、PLL/安全切钟、必要启动检查；复杂可变的 PHY/DDR 配置可由 SPM 中可更新固件承担，但必须在第一次使用相关资源前完成。
- DDR controller/PHY training 可以在平台 ROM 或早期 SPM 固件执行，实际控制和训练通常需配合 IP 硬件及其规定固件/序列；本轮没有供应商资料，未确认具体实现。
- 不建议因为图里列了 DDR 就强制把 DDR 整套训练固化进 mask ROM；也不应推迟启动介质可访问性的必要 PAD/clock 配置到介质加载之后。

## 命令与验证边界

- 只读：git status/rev-parse/log/show/merge-base、rg、nl/sed、sha256sum；读取官方文档和上游启动源码。
- 临时目录 `/tmp/cheshire_prom_review_BVss7T/`，含 apply_patch 创建的提取器。初试 Node 提取器因 node 不在 PATH 返回 127；随后 Python 标准库提取器成功，输出二进制用于 objdump。没有使用提取文件替换生产 ROM。
- 重现：`python3 /tmp/cheshire_prom_review_BVss7T/extract_rom.py hw/bootrom/cheshire_bootrom.sv /tmp/cheshire_prom_review_BVss7T/cheshire_bootrom.bin`；随后 `riscv64-unknown-elf-objdump -D -b binary -m riscv:rv64 --adjust-vma=0x02000000 --start-address=0x020000a4 --stop-address=0x02000164 /tmp/cheshire_prom_review_BVss7T/cheshire_bootrom.bin`。两者退出 0；未重新编译 ROM。
- 部分 GitHub PR/commit 网页返回 cache miss；修复提交说明及补丁直接从本地 Git 历史读取，在线 main 文件用于交叉对照。
- 未 RTL 编译/仿真、未板测、未实施 PLL/DDR，也未修改生产代码。

## 下一步与协调

1. E01/S01 启用 PlatformRom 前，单独授权修复并重新生成启动 ROM，验证“空钩子正常返回”和错误/超时分支；不能只改 S 而保留旧 SV。
2. P01 明确 RefClk 启动、配置银行/PAD、PLL 与 DDR IP 依赖；划分不可修改平台代码与可更新 SPM 代码的职责。
3. C00 可将 Platform ROM 返回缺陷及上游修复依据合并到共享技术缺口；本轮独立记录，不把方案当已实施事实，也不覆盖共享状态。
