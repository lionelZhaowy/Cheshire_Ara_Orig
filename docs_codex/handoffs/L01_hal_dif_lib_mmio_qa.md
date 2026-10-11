# L01 / HAL、DIF、lib 与 MMIO 软件接口答疑

> 记录日期：2026-10-09。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-09；任务：L01，只读源码分析与学习答疑。
- 状态：完成（解释与静态核对）；输入分支 `mp/ara-pulp-v2`，HEAD `278434024`。
- 开始时已有 M01 接口契约修改、多份未跟踪交接及图示目录，原样保留。
- 本轮负责路径：仅新增本记录；无生产源码或共享状态修改。

## 本轮结果

- 源码确认：软件手册对应缩写为 DIF（Device Interface Functions）；本次未调查 DDR 控制器/PHY 的 DFI 接口。
- 源码确认：HAL 封装器件/协议，DIF 封装控制器/IP 操作，MMIO 执行寄存器地址访问。层次表示责任与调用关系，不要求每条路径逐层经过。
- 源码确认：`lib` 表示库源码组织或库产物，不是 HAL 与 DIF 之间的独立层。`sw/sw.mk:44-64` 将本地库与 printf、LLC、AXI RT、OpenTitan base/DIF 等对象归档为 `libcheshire.a`，108-112 行定义应用链接。
- SPI 实例：`sw/lib/hal/spi_s25fs512s.c:40-65` 组织读命令 0x13、4-byte 地址和接收段，再调用 `dif_spi_host_transaction()`。
- DIF 实现：`.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/device/lib/dif/dif_spi_host.c:398-459` 操作 CSID、COMMAND、FIFO；同依赖 `sw/device/lib/base/mmio.h:143-145` 使用 volatile 32-bit 写。
- MMIO 实例：`sw/include/util.h:16-22` 的 reg8/reg32 仅返回指针；`sw/lib/dif/uart.c:38-41` 轮询状态并解引用写 THR，实际执行访问。
- 可直接调用 DIF：`sw/tests/helloworld.c:35-45` 直接初始化 UART；`sw/lib/dif/uart.c:67-68` 将 printf 的字符输出接到 UART。
- SPI Flash 烧写入口：`sw/boot/flash.c:38-48` 调用器件 HAL。
- 官方补充：[OpenTitan DIF 说明](https://opentitan.org/book/doc/contributing/sw/device_interface_functions.html)用于确认术语、MMIO 依赖及职责分离，不把当前 master API 套用为本地版本。`Bender.lock:173-177` 使用本地 Path，revision/version 为 null；本轮函数行为以受版本管理的本地快照为准。

## 验证证据与边界

- 仓库根执行 `git status --short`、`git rev-parse --short HEAD`、`git branch --show-current`；以 `rg`、`nl -ba`、`sed` 定向读取上述文件及软件手册、项目状态、任务表和最新教材交接。
- 首次通配路径 `sw/README*` 无匹配，改为现存文件定向检查；依赖 DIF README 不存在，以实际 C/H 实现及官方资料核对。
- 本轮仅静态阅读；未编译、未仿真、未板测。无配置、地址、接口或中断变化；未提交。

## 决策与下一步

- 对后续自定义 IP 的分层讨论属于设计建议，不表示已有 NPU/ISP 软件实现。
- 无新项目决策或任务状态变化，无需 C00 合并共享状态。
- 后续按具体器件/IP 选择一条实际调用链继续阅读；无需扩大为全库审计。
