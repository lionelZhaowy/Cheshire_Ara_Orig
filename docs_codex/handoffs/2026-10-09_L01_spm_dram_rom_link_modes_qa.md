# L01 / SPM、DRAM、ROM 链接模式答疑

## 基本信息

- 日期：2026-10-09；任务 L01；用户要求详细解释三种链接模式的区别和联系。
- 输入：`mp/ara-pulp-v2`，HEAD `278434024`；已有 M01_IP_DDR_Interface_Contract.md 未提交修改，以及图/交接未跟踪文件保留。本轮仅新增本交接，未提交 Git。
- 状态：源码、官方资料和既有 ELF 静态核查完成；未构建、未运行目标。

## 当前实现

- `sw/sw.mk:115` 从 sw/link/*.ld 生成链接模式，108 行起 gcc -T 对应脚本。模式是构建阶段的地址/镜像布局选择，不是运行时 boot_mode、CPU profile 或硬件配置。
- `common.ldh` 声明 ENTRY(_start)；spm基址0x10000000/链接预算64KiB，dram基址0x80000000/8MiB，extrom从0/48KiB，bootrom从0x02000000/16KiB。这些预算不是实际物理容量验收。
- spm.ld：.text/.misc/.bss/.bulk在SPM，通常VMA=LMA；栈符号继承common的0，由CRT0保留进入时sp。
- dram.ld：同类节在DRAM，VMA=LMA；显式__stack_pointer$=ORIGIN(dram)+LENGTH(dram)-8=0x807ffff8。代码、数据、BSS、栈需DDR可用，脚本不会初始化控制器/PHY。
- rom.ld：所有需加载字节合入连续.misc，`>spm AT>extrom`；执行地址SPM、装载地址从0；BSS在SPM不占镜像字节，CRT0清零，栈继承。不是XIP，也不替换硬件Boot ROM。
- `hw/bootrom/cheshire_bootrom.ld` 才把启动源码链接到片上bootrom区并用于生成ROM RTL。
- ROM镜像读取路径：Boot ROM设备函数→gpt_boot_part_else_raw，读取GPT分区或raw介质字节到SPM，再boot_next_stage(code_buf)。默认最多读取48KiB；不能仅将dram.bin改名烧入介质就期待该ROM装载器迁移到DDR执行。
- `crt0.S`不实现通用LMA→VMA数据复制，依赖加载器放置代码/初值，随后清BSS；新增不同执行/存放区域需实现实际搬运，不能仅改ld。
- 当前通用测试GPT打包规则在sw.mk:135起被注释，ROM的GPT/raw解析仍在；Linux镜像规则另有ZSL/DTB/FW分区，不把停用通用打包扩大成GPT能力不存在。

## 既有 ELF 核对

readelf -h、objdump -h、nm -n 验证已有三份 sw/tests/helloworld.*.elf：

| 模式 | entry/_start | 代码VMA | 代码LMA | 栈符号 |
| --- | --- | --- | --- | --- |
| spm | 0x10000000 | .text=0x10000000 | 同VMA | 0（继承） |
| dram | 0x80000000 | .text=0x80000000 | 同VMA | 0x807ffff8 |
| rom | 0x10000000 | .misc=0x10000000 | 0 | 0（继承） |

这些是旧产物证据，不是本轮重新编译或板测；ROM main偏移等具体布局还会随代码及工具链变化。

ROM ELF 的readelf -l还确认LOAD VirtAddr=0x10000000、PhysAddr=0。`target/sim/src/elfloader.cpp:239` 基于p_paddr记录/写入可加载段；故不能把.rom.elf无条件交给当前DPI ELF预加载器，它可能向0写入代码而PC入口仍在SPM。应选匹配加载器的.spm/.dram ELF，或使用.rom.bin的介质装载流程。

LMA=0是外部镜像装载布局坐标，不证明SPI Flash被CPU映射在0地址；ELF文件内部偏移又是独立字段。GPT打包可把同一镜像放在非零分区偏移，运行地址仍不变。

## 官方依据与验证边界

- [Cheshire软件栈](https://pulp-platform.github.io/cheshire/um/sw/)将SPM/DRAM裸机执行及ROM镜像介质装载分开；[GNU ld LMA说明](https://sourceware.org/binutils/docs/ld/Output-Section-LMA.html)定义AT/AT>及VMA/LMA关系。此处VMA是链接器运行地址术语，不意味着本地裸机启用了MMU。
- 仓库根运行git状态/HEAD、rg、nl/sed，读取三脚本/CRT0/构建及GPT/DPI加载代码；readelf、objdump、nm读取已有ELF，sha256sum记录身份。未编译/未仿真/未板测、未改源码或其他文档。
- 已有ELF SHA-256：spm `619a03ebcc13a8b9a7cc5052c4c2e6d066f6253554edc48b83a5f242c0c9f970`；其余两份身份可按本轮只读命令重新取得，不能将文件名当运行证据。

## 最小下一步

后续具体程序先选装载者/启动介质，再选匹配脚本；检查readelf -h -l与objdump -h、栈/BSS布局及可用存储。需要把大程序从Flash装入DDR时采用独立SPM loader并初始化DDR；不在本轮实施。无已实施架构或任务状态变化，不更新共享状态/任务表。
