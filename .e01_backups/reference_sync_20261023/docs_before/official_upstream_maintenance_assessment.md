# E01 / Cheshire + Ara 开发基线与官方维护评估

2026-10-23 云端基线已同步：R的`main`及`rebuild-baseline-20261023`已推送至个人仓库，云端提交与R均为`424e4d2cd9f7e129bbda7e595504a48952b150e9`，工作区干净。**本次仅上传修复前基线，P1–P5仍只在C；未构建或修改F。** 见[同步实测记录](server_reference_rebuild_guide.md#github-cloud-baseline-20261023)。下方等待仓库/SSH设置的描述保留为历史。

2026-10-23 最新托管状态：R实际源码及已有修正已保存为个人Git基线`424e4d2c…`，待创建私有GitHub仓库和授权SSH后上传。用户已要求**先基线上云，再分项同步P1–P5到R并复验**；当前未push、未同步修复，F不动。见[配置结果与用户操作](server_reference_rebuild_guide.md#github-personal-baseline-20261023)。下方“R/F未写回”指P1–P5修复；本轮R的Git元数据和管理文档已更新。

用户审查摘要：[PR同步测试问题与本地代码修改](../reports/official_pr_failure_fixes_review.md)（官方局部修复来源、三处自行修改的实际diff/位置、可综合性与验证范围）。**通过仅指隔离候选C；重建参考原件R和正式工程F尚未写回，未进行综合。**

<a id="p3-p5-repair-20261023"></a>

## 2026-10-23 P3–P5局部修复及累计回归完成

用户在“继续P3–P5”后明确要求失败应先定位并尝试修复。本轮从隔离候选C的`p3-stopped=7b1c13feb4323be10450ec1e4e47f344cba8bc63`恢复，保留P1/P2与MVP #18。**普通测试失败不再机械触发整项停止：先保留证据、诊断并在当前候选范围内最小修复，再用相同输入复验；涉及接口/架构、其他功能、受保护工程或无法消解的冲突才暂停。** 这取代下方历史“未解释失败即停止”的执行方式，不授权FS、MVP #16、LLC扩展、依赖升级或参考/正式工程同步。

当前仅C发生修改；R=`~/CheshireAraPULP`、F=`~/CheshireAra`未写回。C=`/home/zhaowy24/CheshireAra_maintenance/P1_P5_20261023_154743/candidate`，其父目录记为B。沿原配置和离线构建入口，本地Agent经WSL SSH执行，没有服务器Agent或本轮子Agent。**P3、P4、P5定向、受影响回归及最终累计检查已完成；最终标签`p1-p5-pass=5e0f973c090ee26ba18ce520bc61beebe584e929`。ROM/SPI沿用原限定告警接受，原始入口返回2不改写。阶段B在C完成并停止，未同步R/F。**

| 候选 | 当前状态 | 通过版本 | 采用范围 |
| --- | --- | --- | --- |
| P1 | 已验证，未同步 | `p1-pass=9fe3cd5…` | 保留此前存储队列修复及验证 |
| P2 | 已验证，未同步 | `p2-pass=7ac2e12…` | 保留此前官方排序补丁、mask及标量回应局部修复 |
| P3 | 已验证，未同步 | `p3-pass=a7e837d…` | MVP #18＋本地FPnew SIMD mask修复 |
| P4 | 已验证，未同步 | `p4-pass=2736992…` | #191/#192＋本地相邻段首拍地址修正 |
| P5 | 已验证，未同步 | `p5-pass=fe8d8cd…` | 仅reps模板/派生RTL hunk及HAL删除1行 |

### P3：官方0/0补丁之外的SIMD异常标志修复

此前177项中残留6错已经定位并消除。默认关闭的只读观察覆盖CPU清零/读取、Ara逐lane valid/fflags及FPnew内部子单元；实测排除了此前怀疑的无valid Ara lane污染，未修改dispatcher或CSR。

当前FPnew的PULP除法/平方根分支按最小格式实例化4个内部子单元，FP32只用2个、FP64只用1个，但为同步仍启动全部子单元。旧代码直接连接`simd_mask_i[lane]`：一是未使用子单元的补零0/0贡献NV；二是FP32元素1应取最小16位粒度的mask bit2，旧代码却取bit1。实测FP32内部状态为`[NV,NV,DZ,DZ]`，旧mask1111汇总0x18；修复后mask0011仅汇总DZ。FP64正常除法的三个未使用子单元同样多报NV。

生产提交`d38bcf6925077593e6b766154d6fda205a532ed7`只在`fpnew_opgroup_multifmt_slice.sv`的`gen_pulp_divsqrt`中按`LANE_FORMATS[dst_fmt_i]`屏蔽不存在的元素，并以`LANE*fp_width(dst_fmt_i)/(Width/NUM_SIMD_LANES)`选取对应mask位；不改变同步、接口、参数、FS或其他运算组。**这是本地修复，不是官方回移。** 2026-10-23核对[官方pulp分支682f31e376ad796e2fea2eecfdaa2ef0141b2ca9](https://github.com/pulp-platform/fpnew/blob/682f31e376ad796e2fea2eecfdaa2ef0141b2ca9/src/fpnew_opgroup_multifmt_slice.sv)、fix/vec_div的`19a570de3f56b03de079527aafea5e0be8424fbd`及fix/lane_valid的`62c063155508d60f9ced41f15672770c635ca508`，未找到覆盖此PULP路径的相同修正。MVP #18的一行修复仍保留，不加入#16。

| 运行（C/work/runs/） | 检查/失败 | 目标/simv/入口 | 结论 |
| --- | --- | --- | --- |
| `p3_simd_before` | 177/6 | 43/0/1 | 官方#18之后、局部修复之前 |
| `p3_simd_after` | 177/0 | 0/0/0 | 原同一ELF通过 |
| `p3_matrix_before` | 753/28 | 43/0/1 | 新增完整mask矩阵复现错误 |
| `p3_matrix_after` | 753/0 | 0/0/0 | 同一补充ELF通过 |
| `p3_reg_rvv` | 5976/0 | 0/0/0 | RVV及精确浮点回归通过 |
| `p3_reg_fmatmul` | 32×32结果比较通过 | 0/0/0 | fmatmul回归通过，主机459.309秒 |

补充测试在既有`p3_div_flags.c`中增加FP32/FP64、除法/平方根、四元素全部16种mask组合，检查结果、未启用元素与保护区、五个fflags；包含屏蔽NV/DZ及应当保留的NV/DZ，未靠清零源操作数规避问题。标量基础测试仍在。动态结论限本配置FP32/FP64；FP16只有索引不变的静态核对，不能宣称已动态验证。

原ELF SHA256 `f7e7ff0664f70ef1fa7c4ccc7f2e78bc5de722eb66c6cda7df0582040f28362e`；补充ELF `fb6989b8730231b8f0ef9844a352ae50ea78e1174e318da9051760ccd7aa5d64`。修复前后simv分别为`work/p3_simd_before_v2/simv`（`51680b7fd489d1958ff8cb875e00eb0fbef8c4ea1c3829a41cb792a7cade7cf9`）和`work/p3_simd_after/simv`（`eff13726e7ac294cf1c1db71cf5bca1c66423b6ff5b538a344fb567bca19dd88`）。CPU trace解析确认全部原177次检查；补充版本369次函数调用含28个旧错误，另384个数据/保护检查被编译器内联，753总数来自实际UART，不伪称全部由函数入口解析。

`p3-pass=a7e837d2bb2a2ddf0f33a24cc6d8adbd2a180f20`。累计bundle SHA256为`8ed02b14d3801fce269603b2b5ee43c0029f6811c329b358fa4b24ccbc0ee275`，`p3_repair_evidence.tar.gz`为`89383aab69f200ee3cd3576c321c7a37b3cd6d628dbf1d3ee13cdf509bdc7066`（48数据成员＋manifest）。两者均在服务器B/backups与本地`.e01_backups/P1_P5_20261023_154743/`，双份哈希及逐成员检查通过。旧`p3-stopped`、失败日志、观察器首次VCS层级参数编译失败记录均保留；已改为当前配置常量观察边界后重新构建，无生产参数改变。完整trace保留原运行目录。

### P4：预加载边界及相邻段保护

使用同一批六个真实ELF，对照原版、#191、纯#192和最终局部适配版。六个输入在运行前核对ELF64/RISC-V入口、PT_LOAD地址/长度、filesz=memsz、对齐同余、所有ALLOC节归属及逐字节payload。程序从0x10004000执行，数据在低SPM，继承现有ROM栈；没有DPI替代、运行时填入payload或重生成ROM。

| 数据PT_LOAD | 原版 | 仅#191 | 纯#192 | 最终适配 |
| --- | --- | --- | --- | --- |
| 0x10000000 / 1024 B | 空写fatal，未启动 | 通过 | 通过 | 通过，1027项 |
| 0x10000000 / 2048 B | 空写fatal，未启动 | 通过 | 通过 | 通过，2051项 |
| 0x10000000 / 1031 B | 通过 | 通过 | 通过 | 通过，1035项 |
| 0x10000001 / 1024 B | 通过 | 缺最后有效字节；X断言，未完成 | 通过 | 通过，1034项 |
| 0x10000ff8 / 16 B | 数据正确但跨4KiB断言 | 同左 | 拆成两突发通过 | 通过，19项 |
| 相邻A=0x10002000/13 B，B=0x1000200d/9 B | 通过 | 通过 | A末5字节被清零，目标44 | 通过，29项 |

#191为[1b893efc6ee520be7d135a1adda397af94fa1c45](https://github.com/pulp-platform/cheshire/commit/1b893efc6ee520be7d135a1adda397af94fa1c45)，C提交`4d1c46e3c2ecfd884202c3e86af85a2542897d93`、标签`p4a-intermediate`；#192为[ae5795dfdb177a8dc3ef2f43dcc7ceaa36fd9238](https://github.com/pulp-platform/cheshire/commit/ae5795dfdb177a8dc3ef2f43dcc7ceaa36fd9238)，C提交`857992bfd32a6a565d16a3b615e901f3edc6d0da`、标签`p4b-official`。两者均只改VIP加载函数，不改生产RTL。

纯#192把B的AW地址对齐至0x10002008，首拍WSTRB=ff，填充零覆盖了已装载A的5个有效字节。**本地适配**`ac5d74a3f32d682fe6ce73186479e1d5a564b479`仅将调用改为`slink_write_beats(addr_cur,...)`并修正注释，保留原非对齐地址，复用现有writer首拍掩码保护前段。不修改writer接口或AXI生产路径。2026-10-23查询的[官方6c6dd5e834347f72c7be31cd6c41021ec293c5b9](https://github.com/pulp-platform/cheshire/blob/6c6dd5e834347f72c7be31cd6c41021ec293c5b9/target/sim/src/vip_cheshire_soc.sv)仍保留对齐调用，不能称这项适配为官方回移。

最终六项均目标/simv/入口=0/0/0，真实SLINK观察`missing=bad=errors=0, launch=1`，应用逐字节读回一致；另`p4_reg_helloworld`正常加载通过。检查范围含首/末拍、实际WSTRB、BRESP、完整拍数、4KiB边界及最终各段内容，不以AWLEN=0误判空突发（它表示合法一拍）。旧空写fatal来自真实空队列；fatal时被动观察器可能尚未采到最后B，不能把其unfinished摘要额外解释成新的总线缺陷。

#191非对齐反例在167.917主机秒时保留未知值/操作数断言及实际AW证据，核对进程确属该候选后主动结束。唯一DATA AW从0x10000001发128拍，证明0x10000400的最后有效字节未写；没有P4_DONE，不称死锁或软件通过。该预定中间失败后继续#192；纯#192相邻段失败进一步定位并局部修复。首次测试链接因漏`printf.h`拉入newlib超出保留区，已只修测试头文件；首次入口调用因预建输出目录未启动仿真，两次失败记录保留，实际动态版本均使用修正后的相同输入。

通过标签`p4-pass=273699230f6a820f4350e21d0315d4c029e4ce75`；累计bundle SHA256 `a41eb41bfe6f881c46d9a1974703f49e58f6eaf374a6ce7d9d75222bfc10f780`，`p4_evidence.tar.gz`为`b875e7b2b72a29914b01aa5fad7ce6df092b02d9fd2e21d4e11e6030f89894e7`（129数据成员＋manifest），双份哈希及成员检查通过。输入哈希、实际源版本、命令、四组simv哈希及25次运行结果在C的`provenance/p4_preload/results.json`与`work/p4_elf_validation.json`；运行目录为`p4_before_v2_01..06`、`p4a_01..06`、`p4b_official_01..06`、`p4_final_01..06`和`p4_reg_helloworld`，完整CPU trace留原目录。

### P5：一维模式实际搬运与HAL清理

只采用[iDMA #66 / 92799c5fabcf2cd1f224f970bbb040b290d08fd5](https://github.com/pulp-platform/iDMA/commit/92799c5fabcf2cd1f224f970bbb040b290d08fd5)的reps hunk，再采用[Cheshire #203 / bca9aadb7588de7046460daf91b39fe863a7a9d1](https://github.com/pulp-platform/cheshire/commit/bca9aadb7588de7046460daf91b39fe863a7a9d1)删除1D清reps写入的hunk，不迁入两PR的其他修改。实际wrapper、32位控制寄存器指针、逐次CONF、#80/#204、当前地址图和API保持；当前2D API是**7个参数（含CONF）**。

旧版1D请求的ND reps被置0，`idma_nd_midend`因此关闭后端valid并合成ND_MIDEND错误响应；wrapper未使用该错误载荷，仍推进DONE ID。实测ND请求18 B、reps0，ID2完成，但后端/AXI读写均0，18个目标字节全部错误。被动观察的errors计数只针对后端/AXI响应，不包括wrapper未连接的ND错误载荷；其旧版errors=0不表示搬运成功。

| 阶段/运行 | 目标/simv/入口 | 实际结果 |
| --- | --- | --- |
| 旧RTL＋旧HAL `p5_before` | 65/0/1 | ID2完成，backend=0，写0 B，18字节错 |
| 仅RTL修复＋相同旧HAL ELF `p5_rtl_after` | 0/0/0 | backend=1，1次AR/1次AW、3个R/W拍，18 B实际写入，数据/保护区全对 |
| 删除HAL清零、重编 `p5_hal_1d` | 0/0/0 | 同样正确完成18 B一维搬运 |
| 新HAL顺序 `p5_hal_sequence` | 0/0/0 | 2D→1D→2D，ND reps4→1→4；3请求、9后端提交/响应、138 B实际写入、ID2/3/4完成，全部数据与保护区通过 |
| `p5_reg_original` / `p5_reg_registers` | 均0/0/0 | 原小二维、寄存器访问通过 |
| `p5_reg_long_aw` | 0/0/0 | 原3笔各8192 B、AW解耦长搬运通过，ID2/3/4、非零pending、全部数据及保护区符合期望 |

顺序测试中，一维仍保留二维留下的src_stride=1、dst_stride=7和寄存器reps=4；前端只将有效reps归一为1。软件验证1D前后reps寄存器仍为4，第三笔2D再次正确。当前配置的真实ND、后端、AXI及完成通路由默认关闭的`+P5_DMA_MONITOR`只读观察，不force或使用stub。原长搬运测试没有flush最后一条UART行：实际只收到job0/1的完整打印，另从CPU trace核对`submitted_ids`及`completed_ids`均为[2,3,4]、pending=[19,30,30]；目标返回0与既有源码的累计字节/guard检查联合判定，没有虚构第三行打印。

生产RTL提交`4c0429ef96cedefc68c01ee7b88c03bab029cea7`，同时为`p5-rtl-pass`；修改现有`idma_reg.sv.tpl`、`idma_reg64_2d_top.sv`、`idma_reg32_3d_top.sv`及汇总`idma_generated.sv`。两份独立模块与汇总中的完整模块内容（忽略注释/空白）一致；**未执行RTL生成，未启用3D只做静态一致性检查。** HAL提交`4e2ebd52cf5206291fd088f70aeb3a198df0bec2`只删除1行；保留旧HAL ELF验证后才重建新软件和候选内库。

旧HAL同输入ELF SHA256 `e87884dad3d65b1a8b3cf0272f0383a5440541737726a0a78e1fa5bfec1c731e`；新HAL一维`66528b6a73a74ba8d984b509c58a70a097da1e0e6699966109ee58b9bccd4d7c`、顺序测试`af46f5e86868be3007b106b9938522a538d966fa382d02283d7064ad4b1bb11c`。旧/修复simv分别`4b6c1fb5f8c506ab2f87d97bcfbdb06601578d61fc2b91b4cd5023f683f8c02c`、`ece037df6623e91824c1993745c3df4f31385aa0188234d41a53292c247d5631`。HAL不改变硬件，后续沿用后一simv，不能把重编软件记成再次硬件构建。

`p5-pass=fe8d8cd031a0d73e676a7cc1f01aaf99bd1dae66`。累计bundle SHA256 `51e2a6ebbd30ffaca8e9b6daa1277ba92673d7a1811f1fafba5a74505471e60b`，`p5_evidence.tar.gz`为`f4ac3665be1df0638ec1a4f254f0253509dd5282a38fdb443e3a9648f25c9bee`（50数据成员＋manifest），均已双份核对。固定来源、局部补丁、实际提交、ELF/库构建命令、运行记录及派生一致性见C的`provenance/p5_1d/results.json`；未重新测试或修复共享LLC旧失败，不把1D修复推广为一般无死锁结论。

### 最终累计回归、保护与交付

| 本轮新增运行（C/work/runs/） | 结果 | 目标/simv/入口 | 主机秒 |
| --- | --- | --- | --- |
| `final_helloworld` | HelloWorld通过 | 0/0/0 | 33.396 |
| `final_csr` | 非stub CSR通过；trace恰好3次预期Illegal Instruction、mcause=2 | 0/0/0 | 34.317 |
| `final_vector` | 22 B向量复制零错误 | 0/0/0 | 82.606 |
| `final_rvv` | 整数/边界/保护区/精确浮点5976项零错误 | 0/0/0 | 270.035 |
| `final_memory` | SPM/DDR私有区访存原子572项零错误；实际16条AMO/LR/SC | 0/0/0 | 190.762 |
| `final_fmatmul` | 32×32标量/向量结果比较通过 | 0/0/0 | 459.973 |
| `final_spi` | 原ROM自主SPI搬运、HelloWorld、JTAG SUCCESS；仅原padding限定告警 | 0/0/2 | 460.322 |

P5的`p5_reg_original`、`p5_reg_registers`、`p5_reg_long_aw`已使用相同最终硬件和新HAL通过，累计汇总引用这三份记录，**没有重复执行或计作新运行**。本轮累计阶段为7次新运行（6 PASS＋1限定功能接受），并复用3项DMA回归。所有仿真串行、无波形、每例默认600秒；未用stub。主机耗时不作为硬件性能收益，未进行频率/面积/功耗评估。

最终硬件为`work/p5_rtl_after/simv`，实际构建源码`4c0429ef…`、SHA256 `ece037df6623e91824c1993745c3df4f31385aa0188234d41a53292c247d5631`；其后HAL提交`4e2ebd52…`只影响软件，再后的提交仅记录结果。各ELF/镜像的实际哈希及命令由`provenance/p1_p5_final.json`绑定，未把记录提交误写成硬件构建提交。

SPI使用原生成Boot ROM，Flash应用仍847 B、填充至49152 B，memh SHA256 `045d9d5d9b67adc379b5c366716dd4df5c9216f32459041b6ad956a66c6dd28b`与原验收镜像一致。执行trace中12288次store重建的49152 B在应用入口前与镜像全部相同；这是CPU已执行写入证据，不冒充独立读出SPM模型。实际仅4个断言事件：读检查byte6/7、写检查byte6/7；原ROM PC `0x02001708/0x0200170a`写入六个有效配置字节，`0x02001710`从`0x1001ff90`读出`xxxx0000000f0f0f`，`0x020004a0`保存到栈，与原padding根因一致。保留原`ASSERTION_OR_SIM_ERROR`及入口2，只按用户既定限定条件接受功能；未关闭断言、修改ROM或扩大豁免。

最终保护核对：R根HEAD/status/完整diff、26依赖HEAD/diff、1084原输入，以及F的962活动目标均匹配初始快照；C Git干净。相对`p2-pass`只有8份预定生产相关文件变化（MVP、FPnew、iDMA模板/三份派生文件、HAL、VIP）；其余为定向测试、默认关闭的只读观察、链接布局及来源/结果记录。本地HEAD仍`c9abbb489…`，未修改本地FPGA/RTL/sw；没有Bender调用、依赖下载/升级、RTL重生成、产物清理或受保护工程写入。核查记录为B/backups/`p3_p5_final_protection.json`。

最终`p1-p5-pass`累计bundle SHA256 `2dd0354914c3916664430df3043ed12c5df309e80d35f62967c4e81a2d31dac1`；`p1_p5_final_evidence.tar.gz`为`5de8267f47ef11bc275012c8c4dcf056aeb3115c92e943e7a0c2b86ca345f245`（40数据成员＋manifest）。服务器B/backups与本地`.e01_backups/P1_P5_20261023_154743/`双份哈希、全部归档成员和完整Git bundle检查通过；最初baseline实际恢复1084文件的记录继续保留。完整CPU trace及全部旧失败输出留C原运行目录，未删除。五份本地E01文档写前核对哈希，其他专题修改保留。

### 恢复方法与阶段C边界

本轮没有执行回退。C包含逐项提交及`baseline`、`p1-pass`至`p5-pass`、`p4a-intermediate`、`p4b-official`、`p5-rtl-pass`和最终`p1-p5-pass`标签。需要回退时先保存当时代码/日志，确认C干净且没有后续并发修改；发现变化先核对，不能直接覆盖。以下只撤销P3–P5生产修改，保留测试与失败记录：

```bash
cd /home/zhaowy24/CheshireAra_maintenance/P1_P5_20261023_154743/candidate
git status --short
git log --oneline p2-pass..HEAD
# 只退P5：执行下面前两条，生产内容回到p4-pass。
git revert --no-edit 4e2ebd52cf5206291fd088f70aeb3a198df0bec2
git revert --no-edit 4c0429ef96cedefc68c01ee7b88c03bab029cea7
# 再退P4：生产内容回到p3-pass。
git revert --no-edit ac5d74a3f32d682fe6ce73186479e1d5a564b479
git revert --no-edit 857992bfd32a6a565d16a3b615e901f3edc6d0da
git revert --no-edit 4d1c46e3c2ecfd884202c3e86af85a2542897d93
# 再退P3：生产内容回到p2-pass。
git revert --no-edit d38bcf6925077593e6b766154d6fda205a532ed7
git revert --no-edit fa7baaa3a830f0460fecdc1c0ebf2dd444d43bda
git diff --exit-code p2-pass -- .bender hw sw/include sw/lib target/sim/src/vip_cheshire_soc.sv
```

选择只退P5或P4时，将最后比较标签相应换成`p4-pass`或`p3-pass`，在对应位置停止；不用`reset --hard`。上面恢复命令本轮未实际执行，初始bundle恢复实测与本轮完整bundle/双份哈希检查是已有恢复证据。

若需要完整旧源码快照，可从累计bundle克隆到**尚不存在**的新目录，再选择标签，不覆盖C/R/F：

```bash
git clone --no-checkout ../backups/p1-p5-pass.bundle ../recover_p2_source
git -C ../recover_p2_source checkout p2-pass
```

这只恢复源码。新目录要运行构建时，须按既有入口做自身绝对路径适配并重新核对输入，不能直接沿用指向C的路径或旧产物；不恢复Bender。

**阶段B完成并停止。** 真正待用户决定的是阶段C同步范围与授权；C通过不代表R原件或F已更新。正式同步须按实际源码映射保留F后续配置/wrapper/静态清单/软件入口，先备份涉及文件，再逐项迁入已验证的官方hunk与明确标识的本地适配，在F新输出目录复验。是否写回R须另行明确，默认保持R原件。原ROM padding限定告警、FS/libgcc限制及共享LLC已知失败继续保留；当前仿真结果不等于ASIC或流片验收。

---

<a id="p3-stop-20261023"></a>

## 2026-10-23 历史停止记录：P3曾剩余6项标志失败（已由上方修复取代）

用户授权“继续P3–P5”。本次从已通过的`p2-pass`继续，只在原隔离候选C实施P3；**P3官方目标错误已消失，但完整定向未通过，不能标为已验证或直接同步项。P4/P5未迁入，受影响回归和全组累计回归未继续。** 以下保留当时事实；最新状态以上方P3–P5修复记录为准。

### 修改与同输入结果

C仍为`/home/zhaowy24/CheshireAra_maintenance/P1_P5_20261023_154743/candidate`。进入时Git干净，输入为`p2-pass` / `7ac2e12b4bdfcf65d91ef5962439e4b0f13bdd6c`，保留全部P1/P2及原有修正。2026-10-23重新读取官方[提交2ec0514c1d538781a26df23fb8a947a60fcdccfc](https://github.com/pulp-platform/fpu_div_sqrt_mvp/commit/2ec0514c1d538781a26df23fb8a947a60fcdccfc)：仅将`norm_div_sqrt_mvp.sv`的`Zero_a && Zero_b`分支中`Div_Zero_S`由1改为0，NV保持1。原始补丁及来源JSON保存在C的`provenance/official_patches/`；只有checkout路径前缀适配，未包含#16、FS或其他生产改动。

测试单独提交，覆盖标量/向量FP32、FP64：四种符号组合的0/0、非零数/±0、精确有限除法、屏蔽异常lane、标志累积、结果及保护元素。先准备操作数再清fflags，向量通过结果依赖后读全五个标志；反汇编与CPU trace确认实际执行顺序。两个版本使用**同一ELF**，SHA256为`f7e7ff0664f70ef1fa7c4ccc7f2e78bc5de722eb66c6cda7df0582040f28362e`。NaN检查覆盖指数/非零尾数，不声称完整NaN编码或全部浮点ISA验收。

| C/work/runs下的运行 | 检查 / 失败 | 目标 / simv / 入口 | 主机秒 | 结论 |
| --- | --- | --- | --- | --- |
| `p3_before` | 177 / 20 | 43 / 0 / 1 | 139.530 | 复现0/0多报DZ及其他向量标志不符 |
| `p3_after` | 177 / 6 | 43 / 0 / 1 | 137.735 | 消除14项0/0标志错误；完整定向仍失败 |

14项消失的错误为10项标量、4项向量0/0检查（含累积测试的首步重复）。全部20项原始错误均为fflags；结果数据、标量读回及保护元素在前后两版均符合期望。剩余6项在旧版同样失败，**不能说是P3补丁新引入**：

| case | 向量操作 | 实际fflags | 期望fflags |
| --- | --- | --- | --- |
| 23201 | FP32非零数/零 | `0x18`：NV＋DZ | `0x08`：DZ |
| 23202 | FP32精确有限除法 | `0x10`：NV | 0 |
| 23203 | FP32屏蔽异常lane | `0x18`：NV＋DZ | 0 |
| 26401 | FP64非零数/零 | `0x18`：NV＋DZ | `0x08`：DZ |
| 26402 | FP64精确有限除法 | `0x10`：NV | 0 |
| 26403 | FP64屏蔽异常lane | `0x10`：NV | 0 |

两次运行串行、无波形、600秒上限，未超时或触发RTL断言。VIP的`SLINK FAILED / $error`来自目标返回43；不能以simv返回0视为通过。软件库从C输入重建；硬件在`work/p3_after/`新建输出，源提交、命令及两步构建日志均保留；没有调用Bender或下载构建依赖。主机秒数不解释为硬件性能变化。

### 剩余问题与停止点

实际trace确认177次检查与UART的20/6项错误一致，且失败用例执行了fflags清零、向量结果依赖和标志读取。尚未确定剩余错误的具体根因，不能通过删去mask/普通除法检查将P3改判通过。

只读检查得到的线索是：`ara_dispatcher.sv:421/450`不逐lane按valid门控而直接OR全部异常标志；`vmfpu.sv:1332/2383`也在无输出握手时寄存异常数据。**这些只是待验证线索，未证明就是此次6项失败原因。** 后续应在现有TB增加默认关闭的只读观察，关联各lane的FPnew异常数据/valid、mask、dispatcher汇总及CVA6清零/更新时序，区分旧标志残留、mask过滤和CSR时序；只有确定根因后再决定最小修改。不扩展到FS、除法器#16或一般性浮点重构。

按既定“新错误/未解释结果即停止”要求，本次未进一步改RTL，未运行RVV/fmatmul回归，未开始P4/P5。P4仅阅读#191/#192及既有草稿，注意到对齐后整拍写入须检查相邻段是否保留；**没有P4动态结论，也未改VIP或编译P4 ELF**。P5仍未实施。下一步建议先授权定位并尝试修复上述6项，再按原顺序继续；阶段C仍未授权。

### 版本、备份与恢复

| 提交/标签 | 内容 |
| --- | --- |
| `95beade7f1ad238493bdaf46de40c7cfed412c84` | P3定向源码与现有Make目标，未混入生产修复 |
| `fa7baaa3a830f0460fecdc1c0ebf2dd444d43bda` | P3官方一行修复及来源记录；实际构建版本 |
| `p3-stopped` / `7b1c13feb4323be10450ec1e4e47f344cba8bc63` | 停止说明；**不是p3-pass**，已通过回退点仍为p2-pass |

修复前simv为`work/p2_scalar_after/simv`，SHA256 `58a95809e0ee638308de55a0f21abefaec3e5cc51b24f71b9852798e6322e9f0`；修复后为`work/p3_after/simv`，SHA256 `ec4cf83523e943be4cd1f7104651ab8b52352085e9ab77fe7f2ca9428fdd45bd`。日志/产物不纳入源码Git；全部检查分类及关键CSR trace位于`work/p3_analysis/`，两个完整CPU trace保留在各原运行目录。

累计`p3-stopped.bundle`、`p3_evidence.tar.gz`、清单/备份记录及`p3_p5_before.json`/`p3_p5_after.json`分别保存于服务器`.../P1_P5_20261023_154743/backups/`与本地`.e01_backups/P1_P5_20261023_154743/`。bundle SHA256为`7a88b2d3a3316c7da306ad466cdc34da0aa97054b55bbf88ef14f644696ac2d8`；证据归档SHA256为`54b0cc023cd40dd328c4f8e8f77aadb1a1bebdc02e0f4206f2898eb2d37ed3f3`，包含17份数据成员及其清单。双份哈希、完整bundle及归档成员检查见`p3_backup.json`和本地核查记录；首次baseline实际恢复1084文件匹配的记录继续保留。

**本次没有回退。** 如需仅撤销P3生产修改，先确认C干净且无后续并发改动，再执行：

```bash
cd /home/zhaowy24/CheshireAra_maintenance/P1_P5_20261023_154743/candidate
git status --short
git log --oneline p2-pass..HEAD
git revert --no-edit fa7baaa3a830f0460fecdc1c0ebf2dd444d43bda
git diff --exit-code p2-pass -- .bender hw sw/include sw/lib
```

这保留测试、停止记录及失败输出。若需完整旧源码快照，从累计bundle克隆到尚不存在的新目录，再checkout `p2-pass`，不覆盖R/F，不使用`reset --hard`。结束时R的HEAD/status/完整根diff、26依赖HEAD/diff、1084原输入与F的962活动目标均匹配保护快照，C Git干净；配置/接口/ABI、wrapper、既有#80/#204、原ROM padding告警、FS/libgcc及共享LLC限制保持。五份本地E01文档写前均匹配本轮备份，未覆盖其他专题修改。

---

<a id="p2-repair-20261023"></a>

## 2026-10-23 P2失败定位与局部修复

**用户明确授权“定位P2失败，找到问题原因并尝试修复”，并在调整审批模式后要求继续。本次只在既有隔离候选C处理P2，未写回R参考原件或F正式工程，未继续P3–P5。** P2官方修复之外，已分别修复两个实际触发的问题；最终状态与回归结果见下表。此前“P2剩余31项原因未明、等待定位授权”是历史停止记录，已由本节取代。

### 原因、最小修改与来源

原始输入为`p2-stopped` / `5a92bd47c7be608341c7adcef4dc97a60d88285f`，包含已验证P1与P2官方`a987112abed1339ecc9723555759be79427224bf`。查询日期为2026-10-23；当前配置仍为WT D-cache、2 lanes/VLEN2048。首先按原ELF的实际反汇编解析CPU trace，835次检查与31次失败完全对应，未降低期望或删去辅助检查。

| 问题 | 为什么错、实际后果 | 本次局部修复 | 来源与状态 |
| --- | --- | --- | --- |
| 16项`vcpop`错误 | `masku.sv`把VL之外的mask尾部位送入16位计数slice。VL=2时有效1位加14个尾部1返回15；VL=4时有效2位加12个尾部1返回14 | 在当前word中将有效VL之外的位清零，再送popcount/首位查找；仅6行，不改参数/接口 | [Ara提交2ce6c2cc976b3dea5f52858e3b9cea8d4779e033](https://github.com/pulp-platform/ara/commit/2ce6c2cc976b3dea5f52858e3b9cea8d4779e033)，属于[PR #469](https://github.com/pulp-platform/ara/pull/469)，查询时**开放、未合并**；仅选该hunk，未迁入PR其他修复。C生产提交`2b36bfcc68b2f2cf4b67a190804a1872262a392d` |
| 15项向量读回标量错误，以及存储误响应 | `ara_sequencer.sv`用`!use_vd`认定标量响应，既包含存储，又未在mask仍占用MaskB时阻止完成返回。实测15次`busy=1/valid=1/ready=0`却返回CPU，读到旧值；另有37次存储未收到addrgen ack却被该分支回应 | 明确只处理VMVXS/VFMVFS及VCPOP/VFIRST；前两者等待mask释放共享队列，后两者沿专用结果通路返回；存储继续等待原地址响应。只改WAIT条件及注释，原ready表达式不变 | **本地修复，不冒充官方回移**。查询的[官方main `34bd3bc152421b4601a7bf3d6e8e91ffb545c99e`](https://github.com/pulp-platform/ara/blob/34bd3bc152421b4601a7bf3d6e8e91ffb545c99e/hardware/src/ara_sequencer.sv#L564-L572)仍含原逻辑，未找到相应官方补丁。C生产提交`6382e4214100c0e0de56dcd7190941cbaeebae0e` |

这两个问题不能解释成P2官方补丁新引入的31项错误：相应错误逻辑原本就在旧基底中。官方P2只改`vmfpu.sv`，已经消除了观察到的浮点返回错绑；本次另两处修复后，才完成当前定向验收。不可把未合并的mask补丁描述为官方主线已修复。

不能统一用`!running_mask_insn_q`挡住所有标量结果：VCPOP/VFIRST的专用结果valid与完成通知同拍出现时，该位仍为1，统一门控会漏响应。补充测试实际覆盖VMVXS/VFMVFS各56个`busy=1、valid=1`的等待采样，CPU回应保持0，释放后正确返回；并非靠未触发重叠取得通过。原P2的store等待也得到修正，其后VMVXS不再重复撞到占用窗口，两种情况分别记录。

### 串行实测

所有运行沿C现有`_e01/remaining_acceptance_20261021/run.py`，默认600秒、无波形、无stub；保留目标、simv、入口、完成标志及断言联合判定。以下目录均在`C/work/runs/`。硬件每一步从新输出构建；软件和库来自C，无Bender或下载依赖参与构建。主机耗时缩短主要受错误打印减少影响，**不作为硬件性能收益**。

| 运行 | 检查结果 | 目标 / simv / 入口 | 主机秒 |
| --- | --- | --- | --- |
| `p2_diag_original` | 官方P2后旧状态复现：835项31错，16计数＋15标量；15提前响应/37存储误响应 | 42 / 0 / 1 | 155.704 |
| `p2_mask_before` | 新增定向：124项32错 | 44 / 0 / 1 | 110.377 |
| `p2_scalar_before` | 新增标量定向：已发现3次提前响应/5次存储误响应，随后MaskB命令FIFO满断言；未完成 | 未结束 / 0 / 2 | 111.466 |
| `p2_mask_only_original` | 只加mask修复：835项15错，全部为标量读回；计数错误已消失 | 42 / 0 / 1 | 155.168 |
| `p2_mask_after` | 124项全部通过 | 0 / 0 / 0 | 58.096 |
| `p2_scalar_fixed_original` | 再加标量条件修复：835项全部通过；提前响应/存储误响应均0，两lane浮点错绑均0 | 0 / 0 / 0 | 64.181 |
| `p2_scalar_after` | 同一补充ELF：483项全部通过、无FIFO断言 | 0 / 0 / 0 | 65.538 |
| `p2_mask_final` | 累计版本复验124项全部通过 | 0 / 0 / 0 | 58.117 |
| `p2_reg_rvv` | RVV/精确浮点5976项通过 | 0 / 0 / 0 | 268.014 |
| `p2_reg_fmatmul` | 32×32标量金值/向量计算/比较通过 | 0 / 0 / 0 | 458.345 |
| `p2_reg_vector` | 向量复制通过 | 0 / 0 / 0 | 82.022 |
| `p2_reg_csr` | 非stub CSR通过 | 0 / 0 / 0 | 34.154 |
| `p2_reg_p1` | 真实B门控绕回再次触发，B=4/完成=4/队列空，数据通过 | 0 / 0 / 0 | 156.133 |

mask定向覆盖非零VL=1/2/4/8/15/16/17/127/128/129、已知非零尾部、masked/unmasked以及短VL的VFIRST；测试跨当前128位word边界。VL=0及VFIRST长序列未纳入本轮动态验证，本补丁不据此关闭这些范围的未验证问题，也不扩大为完整mask ISA验收。新标量定向覆盖FP32/FP64、正负结果、VMVXS符号扩展、VFMVFS NaN boxing、依赖对照、存储结果/有效mask/保护字节/五个fflags。旧版断言时尚未执行VFMVFS，VL/地址/指令均合法，不能归咎于新增浮点检查。

本轮没有重设计MaskB spill的所有权逻辑；上述通过只证明列出的触发与回归，不声称覆盖所有scalar/mask交错。ROM padding限定告警、FS/libgcc边界、共享LLC旧失败及P3除法标志问题保持原状态；未新增FS修复、性能优化、ROM生成、依赖/工具升级或LLC扩展排查。

### 版本、备份与恢复

C仍为`/home/zhaowy24/CheshireAra_maintenance/P1_P5_20261023_154743/candidate`，单一Git仓库。旧`baseline`、`baseline-ready`、`p1-pass`、`p2-stopped`保留，测试观察与生产修改分开提交，失败输出未删除。

| 标签/提交 | 含义 |
| --- | --- |
| `530d771b362a39c5a5d0a2c4367b910beece9771` | 新监视及两个定向测试；默认关闭的监视不驱动RTL |
| `p2-mask-pass` / `4b681ea94f16cb71148efba9b69c8a2417fdb3e5` | 仅mask子修复通过；当时P2整体仍15错，不误称全部通过 |
| `p2-pass` / `7ac2e12b4bdfcf65d91ef5962439e4b0f13bdd6c` | 官方P2＋两项补充局部修复的定向及五项回归通过；**已验证、未同步** |

新增备份同存于服务器`.../P1_P5_20261023_154743/backups/`及本地`.e01_backups/P1_P5_20261023_154743/`。`p2-mask-pass.bundle` SHA256为`38dab45ce8d8d2444a1c5c29b79ec44d16fdf94775e87845b77ca88b8fbdea0a`。最终`p2-pass.bundle` SHA256为`c586c07f274b3fd85e24c803a2d8a9b618522c3b0ccb8326e5ab444680c7300f`；`p2_repair_evidence.tar.gz` SHA256为`032b078fe575f1a3efad7995545651cf2d48e75cb100b198d2046856c47d9a6f`，含50份成员（关键ELF、13次运行日志/结果、构建命令/日志和保护记录等）。服务器与本地SHA一致，bundle完整历史验证通过，归档49份数据成员逐项哈希一致；另1份为其清单。大体积CPU trace仍保存在C的原输出中。最终记录提交另清理两个测试文件中过时的“未编译/未运行”注释，无可执行语句变化，最后实际构建源提交仍为`6382e42…`。

关键ELF始终不变：原P2为`b6f19fac138bf3c4e46a4c2db4dc9e3174014fd8890d7e82dcc19767fb7089e3`；mask边界为`953d67c3b9f9078ee0c7e20d19dfb1b2065d62a6aa6f2a57ce2242dc3446fa16`；scalar补充为`9d599c5492258c07c4b3adf7f09d38a739a9c32be527c46cc4e36d987d980eed`。三个诊断硬件版本分别为`work/p2_diag_before`、`work/p2_mask_after`、`work/p2_scalar_after`，各有实际源提交、命令和构建日志。最后simv SHA256为`58a95809e0ee638308de55a0f21abefaec3e5cc51b24f71b9852798e6322e9f0`。

**下列是恢复说明，本次未执行回退。** 确认候选Git干净、没有后续并发修改且备份已就绪后，可逆序撤销本次两项生产修复，保留测试、诊断和失败记录：

```bash
cd /home/zhaowy24/CheshireAra_maintenance/P1_P5_20261023_154743/candidate
git status --short
git log --oneline p2-stopped..HEAD
git revert --no-edit 6382e4214100c0e0de56dcd7190941cbaeebae0e
git revert --no-edit 2b36bfcc68b2f2cf4b67a190804a1872262a392d
git diff --exit-code p2-stopped -- .bender hw sw/include sw/lib
```

上述生产提交也包含各自来源说明；revert会将对应文件从工作树移除，原补丁和适配说明仍保存在Git历史及bundle中，测试与仿真日志不删除。若候选目录损坏，从累计bundle克隆到一个尚不存在的新目录，核对所需标签/源哈希；禁止覆盖R/F或删除失败证据。首份bundle实际恢复、1084份输入哈希一致的记录仍有效，本次新增bundle的完整历史与双份哈希校验也已通过。

结束核对R的HEAD/status/完整根diff、26依赖HEAD/diff、1084份原输入以及F的962条活动目标，全部与原保护快照一致；见两地备份中的`p2_diagnose_before.json`/`p2_diagnose_after.json`。C当前Git干净。本地HEAD仍为`c9abbb48946fe3a7244bfb3159919b7c9731cb59`，仅更新现有五份E01文档及持久备份，未改本地RTL/sw/FPGA。五份文档写前哈希均与本轮备份一致，保留并行A/B基线评估和用户选择A的记录。

本轮交付后停止。P3–P5及P1–P5最终累计回归未执行；参考原件未更新，正式同步仍需阶段C授权。F对应源码为`src/cheshire_soc/ara/hardware/src/lane/vmfpu.sv`、`masku/masku.sv`和`ara_sequencer.sv`（后两者沿同一`hardware/src/`根）。阶段C还须重新核对现行来源映射/后续改动，并用正式入口验证，不能由C通过代替F验收。

---


<a id="p1-p5-stage-b-stop-20261023"></a>

## 2026-10-23 阶段B历史实测：P1通过，P2未通过并停止

**本节保留当时停止事实；后续定位与修复已完成，当前状态见[文首P2记录](#p2-repair-20261023)。**

**用户已明确授权实施P1–P5计划。本轮实际执行了隔离副本、备份、构建和串行仿真；在P2遇到未解释的检查失败后，按计划停止。P3–P5未实施，累计回归未执行，R参考原件与F正式工程均未修改，阶段C未授权。** 下方A/B基线比较及阶段A正文中的“本轮未构建”“候选未实施”等，均为各自历史轮次，该轮修复状态以本节为准，后续结果见文首。

### 实际版本、修改和状态

候选根目录：`/home/zhaowy24/CheshireAra_maintenance/P1_P5_20261023_154743/candidate`，下文简称C。源输入来自R的**实际磁盘文件**，不是纯`e040b7bbc…`导出；保留FS启动、DMA wrapper/32位MMIO/HAL/CONF、iDMA #80/#204、WT读断言等既有修正。当前配置仍为WT D-cache、2 lanes/VLEN2048，未改接口、地址图、ABI、队列/LLC参数或依赖版本。

| 项目 | 本轮实际状态 | 修改与证据 | 是否可直接同步 |
| --- | --- | --- | --- |
| 基准 | 已重建、已验证基本入口 | 新输出中重建库/ELF和VCS；HelloWorld、向量复制、RVV通过 | 仅供隔离对照 |
| P1 / Ara [ae8297af0af38b52136826e591782042025725da](https://github.com/pulp-platform/ara/commit/ae8297af0af38b52136826e591782042025725da) | **已验证，未同步** | 只改`vstu.sv`的`issue_pnt != commit_pnt`为计数比较；同ELF旧版复现，新版完成，向量复制/RVV回归通过 | 可作为后续阶段C候选；仍须正式工程复验 |
| P2 / Ara [a987112abed1339ecc9723555759be79427224bf](https://github.com/pulp-platform/ara/commit/a987112abed1339ecc9723555759be79427224bf) | **已应用到C，但验证未通过** | `vmfpu.sv`原始官方patch直接适用，10增/11删，无额外生产适配；错绑观察消失，但完整定向仍失败 | **不可列为通过项，不同步** |
| P3 / MVP #18 | 已调查、待验证；本轮未实施 | 只有未编译的本地测试草稿 | 否 |
| P4a/#191、P4b/#192 | 已调查、待验证；本轮未实施 | 只有未编译的测试/链接布局草稿；未修改VIP | 否 |
| P5 RTL/HAL | 已调查、待验证；本轮未实施 | 已核对模板/派生映射并准备草稿，未应用、未运行 | 否 |

P1生产提交为`26637be97e731a98ae0fd220b61f814f6a703409`；P2生产提交为`7a7075a71386027b1da630bf2d8268b561957654`。测试及入口适配单独提交。没有FS新修复、除法器#16、性能优化、共享LLC扩展排查、ROM重生成、Bender调用或工具升级。

### 前后实测与停止原因

测试仍使用参考工程既有`_e01/remaining_acceptance_20261021/run.py`判定逻辑，仅将simv及输出绑定到C。保留目标/仿真器/入口三层结果；普通运行无波形、串行、600秒上限。各目录位于`C/work/runs/`。

| 运行目录 | 实际结果 | 目标 / simv / 入口 | 用时 |
| --- | --- | --- | --- |
| `baseline_hello` / `baseline_vector` / `baseline_rvv` | 三项PASS；RVV为既有5976项用例 | 均0/0/0 | 33.643 / 82.378 / 270.590秒 |
| `p1_before` | 达到完整触发后B=4、完成=0，队列未清空；定向观察器在100000周期限值报告失败 | 未结束/0/2 | 71.855秒 |
| `p1_after` | 同触发B=4、完成=4、队列清空；全部数据/保护区通过 | 0/0/0 | 156.558秒 |
| `p1_vector` / `p1_rvv` | 两项PASS，门控默认关闭 | 均0/0/0 | 81.582 / 267.480秒 |
| `p2_before` | 已观察错绑及目标错误；大量UART明细导致未在600秒内结束，trace持续执行发送等待 | 未结束/124/124 | 600.015秒 |
| `p2_before_compact` | 保持全部检查/8次重复，仅缩短打印；835项中92项不符 | 42/0/1 | 155.413秒 |
| `p2_after_compact` | 相同ELF；835项中仍31项不符 | 42/0/1 | 154.673秒 |

**P1证明范围。** 默认关闭的`+P1_VSTU_GATE`在真实VLSU的B缓冲与VSTU之间同时门控valid/ready。四条存储已接收并发出（AW=4、W=8、WLAST=4）、无B握手/完成、`issue_cnt=0/commit_cnt=4`且指针相等后释放。旧版接收4个B却不完成；一行修复后4次完成且队列清空。没有以DDR延迟代替真实内部通道，没有改变生产队列/其他AXI通道或使用stub。前后ELF SHA256均为`13a14532c332603e01b81873675ec7f8e153fd75b2d45efc0080ddc766f8be89`。

**P2已证明的现象与未关闭项。** 固定汇编覆盖FP32/FP64的`vfadd→vmfeq`、`vfadd→vfsgnj`、mask和依赖对照，不含除法；反汇编核对主指令相邻。观察真实FPnew返回组而非把mask tag当指令ID。旧版明确出现NONCOMP的比较结果1/0写入加法v8，以及ADDMUL的3.0/6.0被当作比较结果送往v10。压缩输出版本每个lane记录15次该错绑；补丁后同ELF每lane为0，低延迟指令在加法未完成时的输入握手由15降为0，输入/输出均为136次。

然而修复版仍失败：首条`case=640/lane=92`为`vcpop`返回15、预期1；这条异常在旧版也存在。静态检查未发现明显的C/寄存器约束错误，但尚未确认其实际执行时VL、完整源mask及内部计数；**不能断言具体新RTL缺陷，不能将全部31项归为popcount，也不能说是P2引入。** 本次只可说“相同输入下未再观察到#482错绑”，不可说“P2完整验证通过”。没有删除辅助检查、改低期望值或继续迁入P3–P5。P2受影响的fmatmul等回归及最终累计回归也未执行。

正式前后对照使用相同ELF SHA256 `b6f19fac138bf3c4e46a4c2db4dc9e3174014fd8890d7e82dcc19767fb7089e3`；旧/新simv分别为`71c7f6099a241ff6345d031d54f93b0612612a5b28fe3f3df024cdb242c542ef`、`50847102a8422add48fef698d676ce205ac8cfd557ba73eaf46a810599cde246`。最初冗长输出的ELF和超时记录另存，未混作同ELF对照；压缩打印改变了指令位置，首次执行不重叠，但后续重复的实际握手已确认触发。UART轮询超时没有被称为死锁。

### 可恢复版本、备份和入口

C使用单一Git仓库，分支`maintenance-p1-p5`，没有嵌套Git/gitlink。首批1084份实际输入共14,455,906字节；`.bender`所需源码按普通文件保存，历史输出/嵌套仓库元数据不复制。当前iDMA的36项本地差异中，23份活动/所需文件已逐字保存，另13份未编译的独立生成变体/job由`provenance/reference_idma_existing.patch`保留完整差异，不能称为全部变体已复制或动态验证。

参考成功VCS脚本保持原分组/宏，只适配C路径和新输出；编译日志的1181条源/include访问均落在C。软件复用F现行显式Make配方，按来源映射回R实际源；库在C内重建。初次缺`vector_util.h`、第二次缺`encoding.h`的编译记录保留，加入原有`sw/tests`及Ara `apps/common` include后通过；没有复制旧库冒充重建或改第三方代码解决入口缺项。

| 标签 | 完整提交 | 含义 |
| --- | --- | --- |
| `baseline` | `043633d2e108a8f6b56e91d1a29063bc23c5fbc4` | 未适配的实际输入快照，含原本未提交修正 |
| `baseline-ready` | `88568a5eaafc0e71f074f75f7b4d06d0d5d144b6` | 入口已适配、三项基准通过；可运行回退点 |
| `p1-pass` | `9fe3cd5e7f1ad03ef82ed4fa85b360da251b7e6e` | P1定向及受影响回归通过 |
| `p2-stopped` | `5a92bd47c7be608341c7adcef4dc97a60d88285f` | 当前失败候选及停止记录；**不是p2-pass** |

目录外服务器备份为`/home/zhaowy24/CheshireAra_maintenance/P1_P5_20261023_154743/backups/`；本地持久备份为仓库内[.e01_backups/P1_P5_20261023_154743/](../../../../.e01_backups/P1_P5_20261023_154743/)，未纳入本地源码提交。两处均保存累计`baseline.bundle`、`baseline-ready.bundle`、`p1-pass.bundle`、`p2-stopped.bundle`；停止版本还保存`stage_b_evidence.tar.gz`（共49份文件，含所用ELF、结果、日志/命令及保护记录）。大体积CPU trace及全部原输出留在C，未删除。未应用P3–P5草稿另存本地备份，明确未编译/未运行，不代表已实施。

首次`baseline.bundle`已实际克隆到服务器`backups/restore_check`，恢复HEAD匹配，1084份文件哈希全部一致；不是仅执行`bundle verify`。记录为`backups/restore_verification.json`。其后各bundle复制到本地并比对SHA256，停止bundle本地`git bundle verify`也通过。

| 备份 | SHA256 |
| --- | --- |
| `baseline.bundle` | `3a055862e016113d14b535f75e128961ade053912a078b705724985e48dbc492` |
| `baseline-ready.bundle` | `8b20402f07c52cee1472ade5eb4503e57559454385de947c91d8c908854f2308` |
| `p1-pass.bundle` | `12cbc8a43ba2f62df1026c63bc8e5a949f2f721877c13b914cd4ac0c7e0dd7e7` |
| `p2-stopped.bundle` | `3d8de1f893b82391eed22075337e72b2ecdf673ec16e0f44fff6652a8c067183` |
| `stage_b_evidence.tar.gz` | `a12d88c278645d400bcb7f7e9f03975adcdbe4f287f69ba9069ee8f34416e691` |

**当前没有执行回退，保留失败代码供查看；下列命令仅为恢复说明，本轮不执行。** 如后续需要把C的生产源码退回P1，在确认没有新的未提交/后续并发修改、且停止bundle已备份后执行下列命令；测试观察与失败输出保留。若需撤销多项生产修复，先列明目标版本和提交，再按逆序逐项revert，不使用`reset --hard`或删除日志。

```bash
cd /home/zhaowy24/CheshireAra_maintenance/P1_P5_20261023_154743/candidate
git status --short
git log --oneline p1-pass..HEAD
git revert --no-edit 7a7075a71386027b1da630bf2d8268b561957654
git diff --exit-code p1-pass -- .bender hw sw/include sw/lib
```

如候选目录损坏，在一个**尚不存在的新目录**从备份恢复：`git clone -b maintenance-p1-p5 /完整备份路径/p2-stopped.bundle /新的恢复目录`，再核对上述标签及所选源哈希；不要覆盖R/F。工具仍使用现有`/opt/riscv`与VCS安装，恢复源码不等于已经恢复或重新运行旧产物。

### 保护检查与下一步

实施结束核对R的HEAD/status/完整根diff、26依赖HEAD/diff哈希、1084份原输入，以及F的962条活动目标哈希，**全部与实施前一致**，见备份中的`protection_before.json`/`protection_after.json`。未写R/F、旧归档、FPGA、TTY、其他工程或EDA安装；没有运行清理。ROM padding限定告警、FS/libgcc边界及共享LLC旧失败保持，不因P1通过改变既有结论。

**本轮停止点已执行。** 下一步需先决定是否授权定位P2剩余检查失败（先核对实际VL/mask/计数和测试假设，再决定是否需要另一个局部修复）；这不自动授权新补丁、删除检查或继续P3–P5。P1可以单独提交阶段C选择，但当前未同步，正式工程必须另行备份、最小映射和复验。阶段A时“尚未选择候选/等待B授权”的条目已由本次明确授权取代；main迁移未启动。

---


<a id="main-baseline-decision-20261023"></a>

## 本轮结论：现在选 A，保留现有已验证组合

**评估日期：2026-10-23（Asia/Shanghai）。推荐继续维护现有工程，日常开发以服务器正式工程 `~/CheshireAra` 的实际源码与既有修正为基准；本地 VCU118 工程继续保留。现在不启动迁移到官方 `main`。** 这不是认定 `main` 无法集成 Ara：源码比较支持其可行性，而且优先候选可以使用 `main` 锁定的 CVA6 `pulp-v2.0.0`，不必先换成 `pulp-v3`，也没有发现必须退回旧 CPU 的依据。但候选尚未编译、展开或运行，不能称为可替换的向量基线。

最关键的三项依据：

1. **迁移不能消除当前最优先的向量/浮点维护。** `main` 没有 Ara；其 MVP 除法器仍为原版本；iDMA 0.6.4 还缺服务器已回移的 #80/#204。Ara #481/#482、MVP #18、加速器取消边界等仍需单独处理。B 的真实收益主要是 Cheshire 启动/预加载、一维 DMA、CPU FS/MMU及部分 LLC 修复。
2. **B 增加了当前并不需要的配套改造。** 主线引入 SystemRDL/APB、Serial Link 2.0、CLINT 0.3、新 UART 包装和软件地址/寄存器头变更；沿团队要求还要重新形成集中配置、静态清单及软件入口。当前目标不是采用这些新接口，近期少量局部补丁更容易限定影响范围。
3. **A 已有真实向量及独立重建证据，B 只有本轮静态兼容性证据。** 现有验证并非完整正确性保证，但足以作为受控修复的比较基准；B 必须重新验证向量分派、访存、CSR/异常、启动、外设和板级流程。新增 NPU/ISP/LVDS/ASIC DDR 尚未实现，两方案都要做这些工作，不能把它们算作迁移收益。

**置信度：对“现在选 A”为较高；对“B 使用主线锁定 CPU 可集成旧 Ara”为中等，只到源码层；对工期、性能和 Linux 可用性不作已验证判断。** 若近期明确需要主线平台能力，或隔离候选证明可用且剩余维护差异显著减少，应重新评估，条件见后文。

本次用户授权调查及必要小规模隔离验证；已完成源码/历史核对、服务器只读查询和临时 Git 合并试验。未修改生产 RTL、依赖、配置、软件、现有编译入口或服务器文件，未进行全量迁移、构建、目标仿真或板测。同日此前“仅局部修复”的决定约束生产维护；本次对 B 的调查不表示已经选择整包升级。后半部保留此前局部维护候选及验证细则。

## 可复现的版本和环境

### 三套工程及官方历史

| 对象 | 本轮核实的版本与关系 | 使用边界 |
| --- | --- | --- |
| 本地 **L** | 分支 `mp/ara-pulp-v2`，HEAD `c9abbb48946fe3a7244bfb3159919b7c9731cb59`；`origin=https://github.com/pulp-platform/cheshire.git`；`personal=git@github.com:lionelZhaowy/Cheshire_Ara_Orig.git` | `personal/main` 是团队 fork，未用作官方 main。L 在官方向量基底后有 19 个团队提交；主要代码改动集中于 `4175f4401…` 的 VCU118/软件，以及 `379ae4544…` 的依赖固定与保护，其余主要是文档 |
| 服务器参考 **R** | `/home/zhaowy24/CheshireAraPULP`，HEAD `e040b7bbc7851a37faff3c4657ff8d656cc6e20a` **加实际补丁** | 本轮 SSH 重新读取 HEAD/status；FS Clean、DMA wrapper/HAL、WT 断言、iDMA #80/#204 等不在该 HEAD 内，不能用纯 Git archive 代替 |
| 服务器正式 **F** | `/home/zhaowy24/CheshireAra`，无 `.git`；来源为 R 加提取、集中配置和入口适配 | 本轮读到 `reference.json`、`source_manifest.json`、`cheshire_pkg.sv` 哈希与同日此前快照一致；发现外部备份活动后，结束前重新核对F的962条活动来源目标哈希，**0不匹配**；R/F的VSTU/VMFPU也与旧版源相同。R的26依赖差异全集沿同日此前阶段A记录，不冒充本轮重算 |
| [官方向量分支](https://github.com/pulp-platform/cheshire/tree/e040b7bbc7851a37faff3c4657ff8d656cc6e20a) | 实际名称 `mp/ara-pulp-v2`，最新可获取 HEAD `e040b7bbc7851a37faff3c4657ff8d656cc6e20a`，提交日期 2025-07-09 | L 的祖先、R 的基底；不是官方默认分支 |
| [官方 main](https://github.com/pulp-platform/cheshire/tree/6c6dd5e834347f72c7be31cd6c41021ec293c5b9) | 最新可获取 HEAD `6c6dd5e834347f72c7be31cd6c41021ec293c5b9`，提交日期 2026-10-14；本轮 GitHub API 与隔离 Git 获取相互确认 | 与向量分支共同祖先 `68a7836c0f8998581808efb561bd2fc275a95323`；向量分支独有17、main独有64提交。L 对 main 为36/64，不能把差异当线性升级 |

进入时的未提交文件属于 AGENTS、已有工程文档、图稿、交接和原始证据；`hw/`、`sw/`、`target/`、Bender 配置及 vendored 源码相对 L 的根 HEAD 没有本轮新增差异。嵌套依赖相对其上游的手工修改则仍存在，不能由根 `git status` 干净推断依赖未改。全部进入时路径状态保存在本轮[原始证据目录](../reports/evidence/main_baseline_20261023/)；旧未提交评估正文在修改前已备份，本报告保留它。本轮观察到 `.e01_backups/P1_P5_20261023_154743/` 内一个旧bundle变化、三个新备份文件出现，均非本轮写入，未改动或清理；因此不宣称整个工作区在期间静止。四份本轮文档写入前均与自身输入备份一致。

### 实际生效的依赖，而非只看声明

L 的 [Bender.yml](../../../../Bender.yml) 是声明；[Bender.local](../../../../Bender.local) 用26项路径覆盖；[Bender.lock](../../../../Bender.lock) 全部是 `Path`，`revision/version=null`。本轮逐项读取 checkout Git HEAD 和差异，26项均与 [.bender/UPSTREAM.lock](../../../../.bender/UPSTREAM.lock) 一致。配合 `SNAPSHOT.tsv` 才能恢复来源；不能把这些路径锁当成没有版本，也不能运行清理/更新来“修复”它们。

R/F 使用相同历史源版本，但补丁不同。下表旧 SHA 指源版本；**L 的 CVA6/iDMA 无本地补丁，R/F 有 WT 断言及 #80/#204**。L 的 Ara 有8份 Makefile/软件/旧 stub 测试改动，RTL 无差异；R/F 的 Ara 无该组本地差异。两边 CLINT、PLIC、AXI-RT、Serial Link 有配置生成差异，完整旧锁与 R/F 差异见文末既有附录，本轮 L 原始记录见 `local_dependencies.json`。

| 组件 | 现有源版本 | main `6c6dd5e…` 实际锁 | 判断 |
| --- | --- | --- | --- |
| CVA6 | `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c` | `4c02b24fe7c04690f626776a92274da24f80d1da`，`pulp-v2.0.0` | 同属 PULP v2，后续37提交；**不是 pulp-v3** |
| Ara | `2895ba907e9eb14b3464609dc791a969d159a7c3` | **没有** | B 必须补入并固定；不能假称主线锁已验证 Ara |
| AXI | `39f5f2d51c5e524f6fc5cf8b6e901f7dcc5622d7` /0.39.6 | `78831b6feba265d5ee2683bbf42b4150f8a35c43` /0.39.8 | 不是最新 master，也未跨 common_cells v2 |
| common_cells | `13f28aa0021fc22c0d01a12d618fda58d2c93239` /1.33.0 | `9afda9abb565971649c2aa0985639c096f351171` /1.38.0 | 需按实际消费者核验；不能套用最新 v2 的迁移成本 |
| iDMA | `c12caf59bb482fe44b27361f6924ad346b2d22fe` /0.6.3 | `ff5d56fffb3767814db88d6bf8f381974ea33aa5` /0.6.4 | main 仍缺 R/F 后来局部回移的修复 |
| LLC | `559bcbd09a5a884dbe31e2d72fd95d024e357f39` /0.2.1 | `cb9a8a14a68ec89e17ef59ae30de2044a743f665` /0.3.0 | 部分配置/flush修复，不等于系统无死锁 |
| FPnew / MVP | `e5aa6a01b5bbe1675c3aa8872e1203413ded83d1` / `86e1f558b3c95e91577c41b2fc452c86b04e85ac` | 两者不变 | CPU/Ara 的 PULP 除法器问题不自动消失 |
| atomics / riscv-dbg | `0ac3a78fe342c5a5b9b10bff49d58897f773059e` / `358f90110220adf7a083f8b65d157e836d706236` | 两者不变 | LRSC/调试后续修复仍需筛选 |
| register_interface | `ae616e5a1ec2b41e72d200e5ab09c65e94aebd3d` /0.4.4 | `5daa85d164cf6b54ad061ea1e4c6f3624556e467` /0.4.5 | 不含 `reg_to_axi` #54 |
| Serial Link | `5a25f5a71074f1ebb6de7b5280f2b16924bcc666` /1.1.1 | `d4e513aebd368d77808c5e6629a1e2729c16eba0` /2.0.0 | 控制接口/生成/PHY配套变更 |
| CLINT | `d5390a805c20f9226758a152ba1645f61da73349` /0.2.0 | `fc7a1ae5ddbbbc76e5c71c3b184e50162b07d5ac` /0.3.0 | SystemRDL/APB配套变更 |
| UART | `6c7dde3d749ac8274377745c105da8c8b8cd27c6` /0.2.1 | `8182a85d234417db46fe833533f8536644d3bee3` /0.2.3 | 新 OBI 包装及 `obi_peripherals` 依赖 |

完整比较见 [lock_comparison.json](../reports/evidence/main_baseline_20261023/lock_comparison.json)，每项含源仓库URL和SHA；[官方锁文件](https://github.com/pulp-platform/cheshire/blob/6c6dd5e834347f72c7be31cd6c41021ec293c5b9/Bender.lock)本身有26项，移除Ara并新增 `obi_peripherals`，不能据总数相同认为组合不变。没有在 L/R/F 运行 Bender，也没有把实验用锁写回。

根子模块 `printf` gitlink/实际 HEAD 为 `0dd4b64bc778bf55229428cefccba4c0a81f384b` 且干净；根 `cva6-sdk` 的 gitlink 为 `55c137141b62d4b84722d08e0f5d2b9a5af1e77f`，未初始化。Ara 嵌套 SDK 是另一版本 `44fdb08ea0d44563ebfc2d5447c5b7e03ea5ea68`。main 根 SDK 改为 `df31dbe3c18f06027e07ba654ba7bbf861c63be3`，不能把不同 SDK 的产物混为同一次 OS 验证。

### 工具、清单和已经验证到哪里

- **现场工具约束已更新：**本轮只读 SSH 确认 Rocky Linux **8.10**、`/eda/synopsys/vcs/W-2024.09-SP1/bin/vcs`，`vcs -full64 -ID` 返回 **W-2024.09-SP1_Full64**。CentOS/VCS 2018 是早期目标，未找到当前仍强制使用2018或已完成2018兼容验证的证据。官方此版本与 main 的[仿真说明](https://github.com/pulp-platform/cheshire/blob/6c6dd5e834347f72c7be31cd6c41021ec293c5b9/docs/tg/sim.md#L8)均列出已支持的 VCS≥2024.09 环境，并非本轮证明更早版本必然不能运行。若以后必须2018，两方案另验，不能把假设中的2018改写作为当前迁移成本。
- **本地实际清单有区别：**`target/xilinx/scripts/add_sources.vcu118.tcl:256,455,482,785` 是向量 profile、真实 Ara decoder，宏为 `ARA/NR_LANES=2/VLEN=2048`，605个唯一源均存在。现存 VCS/Questa 清单各718源虽都存在，却选标量 `cv64a6_imafdchsclic_sv39_wb`，同时列入 stub 和 Ara decoder，缺 `ARA` 宏；不能用于证明当前向量仿真。正确选源依据是 Ara `cheshire/Makefile:25–31,56–62`，F 则已固化正确有序清单。
- **F 的实际功能基准：**1核、`cv64a6_imafdcv_sv39`、WT cache、RVV/MMU=1、RVH=0、SharedTLB=0、提交口2、Ara 2 lanes/VLEN2048、AXI地址48/数据64，LLC128 KiB。CPU配置中的 `VLEN=64` 是虚拟地址宽度字段，不是Ara向量长度。软件 ISA/ABI为 `rv64gcv_zifencei/lp64d`；已有主机GCC13.3.1、交叉GCC13.2.0/binutils2.43.1/newlib4.4.0记录，见[参考重建记录](../reports/reference_rebuild_check.md)。
- **历史执行证据：**HelloWorld、32×32 fmatmul标量金值比较、非stub CSR、5976项RVV边界/精确浮点、572项SPM/DDR模型访存原子，以及提取/异路径重建和配置合并对照。原ROM/SPI仅限定padding告警被接受；共享LLC三类DMA失败保留。这些都是2026-10-18至22的已有结果，**本轮未重新运行**。VCU118只有用户报告的HelloWorld板测，不能转移成新CPU/Ara组合板测或ASIC DDR验收。
- Linux是后续需求，但具体版本/验收组合未冻结，也不是当前裸机提取的前置。F没有Linux SDK流程；本地已有内核镜像或ELF不证明启动。高地址libgcc限制、页错/中断下向量恢复、OS上下文切换仍须单列。

## main 集成 Ara 是否可行、最少要改什么

### 原 issue 与当前判断

找到与用户描述吻合的 [Cheshire #206](https://github.com/pulp-platform/cheshire/issues/206#issuecomment-2891515252)：维护者于 **2025-05-19 15:51 UTC** 明确说明主线当时不支持Ara及其编译器。讨论没有固定SHA，也不能确认这就是用户当时看过的页面；按当日历史查询最近main提交为 `ae5795df…`。它是当时支持范围的说明，不是永久禁止集成。另有 [Ara #393](https://github.com/pulp-platform/ara/issues/393#issuecomment-2733125915) 推荐 `mp/ara-pulp-v2` 并遵循成套Bender依赖，曾记录随意替换Ara提交造成头文件/类型缺失。

当前main的判断直接来自 `Bender.yml`、`hw/cheshire_pkg.sv` 和 `hw/cheshire_soc.sv`：**没有Ara依赖、配置字段、AXI manager槽位、实例或连线；CPU `cvxif`输出不接、输入置0。属于尚未集成，而不只是开关默认关闭。** 但其锁定CVA6仍含Ara使用的专用加速器/翻译协议和向量profile，所以可从官方向量分支移入集成实现。

比较以下两个明确组合，均只作为候选，尚未形成新的实际filelist：

| 候选组合 | 源码依据 | 额外成本与收益变化 |
| --- | --- | --- |
| **B0：main + 旧CPU `99eac9a6` + 旧Ara `2895ba90`** | 保留现有已验证CPU/Ara内部组合；旧配置缺main新增 `RVXHCLIC` 字段，CPU缺 `clic_irq_v_i/vsid_i` 端口 | 主线 `gen_cva6_cfg`/CPU实例须适配，不能因为当前Clic=0就认为未声明字段/端口能通过编译；丢掉main CPU FS/MMU等修复，必须带回显式FS Clean。是可研究的保守组合，**不是更省工作且未验证** |
| **B1：main + 原锁CPU `4c02b24f` + 旧Ara `2895ba90`** | 本轮逐文件/代码块比较：`acc_dispatcher.sv`全文件、CPU accelerator实例、decoder加速器实例、LSU共享MMU仲裁块与旧CPU一致；向量profile保留RVV/WT/2提交/SharedTLB0 | **若以后试迁，优先B1。** 保留主线CPU修复与实例接口；仍须验证37个CPU提交带来的发射/MMU/前端变化。旧Ara仍需自身修复。没有发现必须退AXI/CC或升pulp-v3/最新Ara的依据 |

这只证明接口及依赖有可行基础。Ara原 `Bender.yml` 已依赖PULP `pulp-v2`，AXI/CC声明与旧工程曾统一解析；main仍使用同代AXI/CC，所用 `axi_dw_converter`、`counter`、`spill_register`源码一致。本轮**未执行合成候选的依赖解析或编译**，不由这些比较宣称完整版本兼容。接口比较输出在 [interface_check.json](../reports/evidence/main_baseline_20261023/interface_check.json)。

### 必需的源码与接口改动集合

移植对象来自向量分支 `f93cb310e…`、`4e8145dcd…`、`80f216ed0…`、`f0cede011…` 等提交，不能原样覆盖main对应文件。最低集合如下，路径以官方/本地完整工程为准；F中分别映射到 `src/config/`、`src/cheshire_soc/`、`src/tb/` 和现有静态入口。

| 文件/模块 | 必须移入或保留的内容 | 与main合并时的检查 |
| --- | --- | --- |
| `Bender.yml/lock`、Ara `cheshire/Makefile`、`cheshire.mk`；F静态compile | 固定Ara源；向量CPU profile；`exclude_first_pass_decoder`；唯一真实 `cva6_accel_first_pass_decoder`；Ara pkg/type/include和分组顺序；`ARA`及lane/VLEN配置入口 | main默认标量WB profile不可沿用；不能同时编入同名stub作为有效实现；沿F集中配置，不能新建重复参数系统 |
| `hw/cheshire_pkg.sv` | `Ara/AraNrLanes/AraVLEN`、`axi_in_t.ara`、`gen_axi_in` manager计数、默认值；沿用 `CvxifEn=0` | main已改用地址包、APB mask和新增CLIC字段；加入Ara后重新核Xbar宽度/ID以及相关生成配置，不能覆盖整个旧包 |
| `hw/cheshire_soc.sv:596–624,674–689,801–897` | 恢复 `Cva6UsrCfg → build_config → Cva6Cfg` 两层配置，再用完整派生配置建立 `CVA6_TYPEDEF_EXCEPTION`、ACC/MMU及聚合类型；CPU类型参数/端口；Ara、invalidation filter、宽度转换、关闭时安全连接和单核约束 | main的局部 `Cva6Cfg` 原是user配置、在CPU实例内调用build_config；Ara类型宏需要完整配置的TRANS_ID_BITS/PPNW等，不能只搬宏。这些端口虽名为 `cvxif`，实际是专用协议，**不是通用CV-X-IF**。CPU/Ara同clk/rst，Ara scan输入保持绑0 |
| CVA6 `decoder`、`acc_dispatcher`、`commit_stage`、`csr_regfile`、`load_store_unit`、`cva6_mmu`；Ara `ara_dispatcher`、`ctrl_registers`、`vlsu` | 分派指令/操作数/transaction ID；commit/flush与响应异常；向量CSR、FS/VS/fflags；共享MMU的翻译请求/响应及异常；vstart处理 | B1接口保留，但FS/MMU/发射实现改变。必须测投机取消/ID复用和异常归属，不能只接AXI；现有问题#3310等不因主线CPU版本更新而关闭 |
| `axi_inval_filter`、`axi_dw_converter`、CPU `dcache_inval` 与ACC同步字段 | Ara写地址使标量WT D-cache失效；标量store待处理状态与向量load/store完成状态协调；Ara宽口→SoC口→Xbar→LLC/外部存储 | 2 lanes时Ara数据宽 `32×2=64`，与SoC64相同；增加lane后涉及转换。CPU/Ara各自本地ID经SoC映射/manager前缀区分，不能复用同一manager编号。该机制不是NPU/ISP/DDR全系统硬件一致性 |
| `target/sim/src/tb_cheshire_pkg.sv`、fixture/VIP/TB；`target/xilinx/src/cheshire_top_xilinx.sv` | Ara专用配置、仿真选择和FPGA Ara配置；同一有效类型/参数传递 | main仍无对应向量配置；新SLINK/APB、ROM地址头必须配套；B1重新展开并检查真实Ara层次 |
| `sw/`、Ara测试、启动/ISA配置 | 向量ISA工具链、VS/FS正确初始化、原有效测试与金值、原子/访存/CSR边界、目标与主机退出状态 | 普通 `rv64gc` 默认不能生成RVV；main新链接符号/寄存器结构体与旧软件不能混搭；已有32位DMA控制语义需保留。B1同样保留R/F显式FS Clean，不能因#2936自动删除；删除须另有验证与决定。禁用stub不计功能覆盖 |

接口细节：[Ara类型定义](https://github.com/pulp-platform/ara/blob/2895ba907e9eb14b3464609dc791a969d159a7c3/hardware/include/ara/intf_typedef.svh)包含 `req_valid/resp_ready/insn/rs1/rs2/frm/trans_id/store_pending/acc_cons_en/inval_ready`；返回 `result/trans_id/exception/fflags/store_pending/complete/inval`，外层另带MMU请求/响应。CVA6只将到达scoreboard顶的非推测请求送出，`fence/fence.i`等待加速器待完成store；consistent模式同时协调标量待写数据、向量访存和WT L1D逐行失效，不能省略这些连线。

当前Ara manager ID宽2，CPU原4位ID先经serialize映射，Xbar输出ID宽为 `2+$clog2(AxiIn.num_in)`；加入Ara必须重算manager数和相关type。主Xbar最大事务配置24；Ara失效filter `MaxTxns=4`、L1行32B，宽度转换器 `AxiMaxReads=4`。CPU写缓冲8项、DMA在途16是另两个不同层次的限制，不应混用。依据为本地 `hw/cheshire_soc.sv:204,603,801–889`、`hw/cheshire_pkg.sv:300–325,454–483` 及向量CPU profile。

SoC外部DDR窗口仍以 `0x80000000–0x100000000` 为当前LLC出接口范围，SPM为 `0x10000000`、uncached别名 `0x14000000`；不能把main RDL中用于生成的最小保留尺寸直接当成实际LLC/DDR容量。main将地址常量、SV包、C头、链接片段关联到 `hw/cheshire.rdl`，新地址分配须保持这套对应关系。

现有路径具备向量MMU请求、异常返回与CSR接口，但**拥有接口不等于Linux精确异常/恢复已验证**。后续OS验收至少要覆盖S/U态页表与PMP实际配置、跨页向量访存/故障恢复、`vstart`、异步中断、FS/VS/SD及向量上下文保存恢复、OpenSBI/设备树/内核用户态RVV。裸机CSR检查和未启用页表的DDR模型测试均不能代替。Linux配套不会随切换Cheshire分支自动完成。

已有与缺失必须分开：当前Ara已继承 [#386](https://github.com/pulp-platform/ara/pull/386)（`15b426587cdf1431055248d76569f338b7986f4f`）和 [#388](https://github.com/pulp-platform/ara/pull/388)（`66317bcec616aaae392fdb9eb662846831c93f78`）。源码含异常写`vstart`、FOF更新`vl`、等待idle/flush和partial load结果写回VRF；`addrgen`中indexed未支持的旧注释不能代替实现判断。另一方面，默认启用segment支持时，`hardware/src/segment_sequencer.sv:170–181`在micro-op阶段压低响应valid，异常分支为空，drain阶段也未收集异常。开放 [Ara #490](https://github.com/pulp-platform/ara/pull/490)（head `e225d8a641f479bf53b3b0f66d921fa456123250`）针对该路径，查询日仍未合并；**A和B1都缺此修复**。若要求segment页异常可靠恢复，应把它列入该功能验收，而不是把所有开放异常PR一律变成当前裸机必修。

OS软件方面，main新增VCU118 DTS可复用，但公共 `.dtsi` 仍写 `rv64imafdc`；main SDK与Ara SDK分支的内容不同，前者没有后者的 `RVV`选择器及 `buildroot64_V_defconfig/linux64_V_defconfig`。这不表示main曾删除Ara支持，也不表示通用Linux不可能支持V，只说明没有自动继承本工程现用的向量OS配方。main `sw/sw.mk` 的内核GPT分区仍8MiB，既有本地约11.99MB uImage超分区问题也不会自动解决；参见[原本地/服务器比较](../reports/local_server_build_comparison.md)。

## 迁移究竟省下哪些修复

表内“当前”默认指日常开发目标R/F；L差异单列。B状态以 **B1（main原锁CPU + 补入旧Ara）** 为准，“含”仅表示在确切源码/依赖锁中完整或注明的局部语义存在，**不表示候选已经通过运行**。本轮同时查看PR状态、提交历史及代码，不以SHA不同或关键词相似判定覆盖。

| PR/提交及所属仓库 | 问题与适用配置 | 当前工程状态 | B1候选状态 | 前置依赖与剩余工作 |
| --- | --- | --- | --- | --- |
| Cheshire [#191](https://github.com/pulp-platform/cheshire/pull/191)/[#192](https://github.com/pulp-platform/cheshire/pull/192)，`1b893efc`/`ae5795df` | SLINK预加载空burst、4KiB边界、非拍对齐，F默认入口适用 | 未修 | **含完整最终函数** | 检查 `sec_offs<sec_len`、页剩余量限制、`b=-bus_offs`；仍需边界ELF及SLINK2验证；是TB收益，不是芯片缺陷修复 |
| Cheshire [#203](https://github.com/pulp-platform/cheshire/pull/203)及`ef11799d`、[AW CONF `4c2390f2`](https://github.com/pulp-platform/cheshire/commit/4c2390f25f250c9ea75d314dd107da11a52aa8fa) | DMA AXI64→reg32/编号读回、按次解耦配置 | R/F局部已修＋四类控制指针uint32；L仍旧 | 官方#203及CONF含；**指针仍uint64** | R/F只回移#203部分；main虽含官方#203，仍不含本地额外uint32控制指针修正。需适配main `dma.h:41–51`新static-inline头，不整份覆盖 |
| iDMA [#66 reps hunk](https://github.com/pulp-platform/iDMA/commit/92799c5fabcf2cd1f224f970bbb040b290d08fd5)＋Cheshire #203 HAL | 2D前端1D模式reps=0，不发起搬运 | 未修；#80/#204无关 | **含**：ND关闭时reps=1，HAL不再清0 | 模板/生成RTL/HAL成对，验证18B一维、ID/保护区及2D→1D→2D |
| iDMA [#80](https://github.com/pulp-platform/iDMA/pull/80)/[#204](https://github.com/pulp-platform/iDMA/pull/204)，`40fe6a67`/`497c1f23` | AW写首拍驱动、反压/空队列/许可计数 | **R/F已回移36文件并有定向证据**；L未修 | **都缺** | main锁定2025年的0.6.4，coupler仍读首拍驱动；需再迁已有修复及生成配套，避免迁移引入退步 |
| Cheshire [#219](https://github.com/pulp-platform/cheshire/issues/219)、iDMA [#227](https://github.com/pulp-platform/iDMA/pull/227)/[#273](https://github.com/pulp-platform/iDMA/pull/273) | 共享LLC读挡写/写挡读/Bloom行锁；大重构候选 | 已复现限制保留，用户暂停扩排 | **无自动解决证据**；后两PR仍未合并 | #227/#273有前置链与字段/生成修改，不能视为所有当前配置必需；按既定新设备绕LLC路线实现后另验 |
| Ara [#481](https://github.com/pulp-platform/ara/pull/481)/[#482](https://github.com/pulp-platform/ara/pull/482)，`ae8297af`/`a987112a` | store队列绕回停滞、FP混合延迟写错vd；当前启用 | 未修，优先候选 | **缺** | main不含Ara；加旧Ara后仍需各自小补丁与定向回归，不用更换lane/FPnew |
| Ara [#432](https://github.com/pulp-platform/ara/pull/432)/[#433](https://github.com/pulp-platform/ara/pull/433)/[#439](https://github.com/pulp-platform/ara/pull/439)/[#440](https://github.com/pulp-platform/ara/pull/440) | 源EMUL、跨SEW提取、归约提交、slide计数；条件候选 | 未修 | **缺** | #432两提交、#440跨模块配套；按工作负载筛选。开放mask/异常/性能PR不一律当必修 |
| MVP [#18](https://github.com/pulp-platform/fpu_div_sqrt_mvp/pull/18)/[#16](https://github.com/pulp-platform/fpu_div_sqrt_mvp/pull/16) | 0/0错误DZ；UF/OF标志；CPU和Ara都用PULP除法器 | 未修；#18优先，#16有后续风险 | **均缺，锁未变** | #18不需要#16；#16须考虑[#29](https://github.com/pulp-platform/fpu_div_sqrt_mvp/issues/29)精确次正规结果多报NX，不整包带入 |
| CVA6 [#2936 / `ecb13801`](https://github.com/pulp-platform/cva6/commit/ecb138010de2868532f43131697e38231162ddb5) | fld/FPR写FS Dirty表达式 | 旧CPU未修；启动显式Clean不是等价硬件修复 | **含该项** | `commit_stage`表达式＋`ariane_pkg`操作筛选成对；[#3173](https://github.com/openhwfoundation/cva6/issues/3173)F2I→fflags不置FS及SD残留仍在，不能称FS完全修好 |
| CVA6 MMU `8a6028b6`/`5576a226`/[`b56fbbb9`](https://github.com/pulp-platform/cva6/commit/b56fbbb9bda82bd217c28b9338904e31ab4cd134)，#2798/#2802/#2976；另有[#2989请求门控hunk](https://github.com/pulp-platform/cva6/commit/00d8acf4f82a4d30c4a22e24682dad84860989ce) | 非对齐异常与请求错拍，MMU1/RVH0适用 | 未修 | **三项配套及后续门控均含** | 三项修异常采样/请求有效性及非RVH更新；拒绝misaligned DTLB请求是#2989的额外hunk，不误归给前三项。需页错/非对齐trap归属和恢复测试 |
| CVA6 [#3310](https://github.com/openhwfoundation/cva6/commit/a31b556c30d5f71be9124b0f910ebce3f5c34514) | flush+acc_commit后ID复用误送向量 | 仍旧 | **仍旧** | `acc_dispatcher`清pending后仍可设ready；需定向修复/取消验证，不被普通RVV测试覆盖 |
| CVA6 [#2881](https://github.com/pulp-platform/cva6/commit/dcd5de6016f8643f431d5baa480549585632de31)/[#3009](https://github.com/pulp-platform/cva6/commit/197f371c72d883ec6452809d82fb4299d8b5a939)；sharedTLB #2945 | RAW/WAW发射优化；sharedTLB配置修复 | 未采用；前者暂缓性能项，后者当前关闭 | main CPU含 | 新`raw_checker`与发射行为增加回归；没有本工程性能收益测量。SharedTLB=0不能计作当前必需收益 |
| LLC `d410d306`/`0c581eda`/`08fef39c`＋[#44](https://github.com/pulp-platform/axi_llc/pull/44) | 在途重配/合并flush/完成状态/请求快照 | 未修；运行时切换才优先 | **前三项含，#44缺** | 0.3.0仍读实时cfg；需处理忙时配置快照，不能孤立迁中间补丁或宣称修复DMA系统循环 |
| LLC [BIST `06a4020d`](https://github.com/pulp-platform/axi_llc/commit/06a4020d135de5d6c13b8dbcebfcfa2937e8239d) | 特定VCS packed struct比较 | 未修，本工程未复现 | **含逐字段比较** | 属工具条件收益，不是已证实当前故障 |
| Cheshire [#187](https://github.com/pulp-platform/cheshire/pull/187)/[#189](https://github.com/pulp-platform/cheshire/pull/189)/[#252](https://github.com/pulp-platform/cheshire/pull/252) | Platform ROM返回、uncached SPM执行区、CLINT sleep | 对应hunk未修；按功能启用才触发 | **含** | main新ROM/地址包/CLINT头配套；A可裁取所需hunk。#189的另一HAL hunk已经局部回移，不代表执行区也修了 |
| atomics [#35](https://github.com/pulp-platform/axi_riscv_atomics/pull/35)、register_interface [#54](https://github.com/pulp-platform/register_interface/pull/54)、dbg [#206](https://github.com/pulp-platform/riscv-dbg/pull/206) | LRSC FF竞态、USB控制error反义、cmderr后的command | 未修，条件候选 | **均缺** | atomics/debug锁不变；reg0.4.5仍 `error==RESP_OKAY`；按使用路径验证，不因缺失一律阻塞 |
| AXI [#409](https://github.com/pulp-platform/axi/pull/409)/[#440](https://github.com/pulp-platform/axi/pull/440)、CC FIFO `c777d27e` | TX并发优化、容量语义、FIFO合法握手 | 未采用，性能/条件项 | **均缺** | 主线锁仍旧语义；当前DMA未发现相应FIFO非法握手触发，不扩大成整包升级 |

**B 能消除的工作：**上述已含的Cheshire补丁、1D前端/HAL、CPU FS/MMU组、部分LLC修改不再手工回移；官方VCU118基础也可直接复用。**仍存在的工作：**Ara/MVP/加速器边界、iDMA本地补丁、WT断言、DMA控制软件、系统共享LLC限制及产品新IP一致性。**转为新适配的工作：**寄存器生成/地址包/启动与HAL、SLINK/CLINT/UART、向量选源及重新静态提取。

若采用B0回退CPU，必须从B收益中扣除FS/MMU/RAW-WAW等，并保留显式FS Clean启动修正；若再回退CLINT/SLINK等以避免APB，需反向修改main实例、类型、软件头和生成入口，已是另一套混合平台，不能继续称“直接继承main整套维护”。本轮没有证据要求这些回退。

## 团队定制与两种方案的完整成本

| 已实现内容/需求 | A的投入 | B的投入、可复用部分及已有证据 |
| --- | --- | --- |
| Ara分派/翻译/一致性交互 | 保留，局部补丁加对应回归 | 移入上述接口和配置；B1无需重做CPU加速器协议，但CPU37提交和新SoC必须重新组合验证 |
| VCU118/MIG/时钟/XDC | 保留旧可运行原型；变更涉及板级时重验 | main [#240](https://github.com/pulp-platform/cheshire/pull/240)已有支持；本轮比较VCU118 XDC、时钟/MIG分支及DDR配置块字节一致，**不能算重新开发**。仍要保留Ara FPGA选择、核对main新SSI策略、工具参数、完整时序/bitstream并板测 |
| FS、DMA、iDMA、WT断言的R/F补丁 | 已实施，只对新增修复及受影响路径回归 | 按上表去掉已等价部分、保留缺失语义；不能用较新官方文件覆盖掉已修内容。WT有效读字节断言仍需适配 |
| CLINT/PLIC/SLINK/AXI-RT生成定制 | 沿现参数和生成物配对 | 单核CLINT、PLIC58源/2targets、SerialLink8bit等需在新生成/端口体系中重核；AXI-RT当前关闭，不为它增加功能验收 |
| 软件和测试 | 保留有效非stub测试、ISA/启动/链接和结果判定 | 新地址常量/struct头/链接符号适配；保留fmatmul/CSR/访存/负例判定。L中关闭的GPT规则、调试器速度和Ara软件修正按必要性迁入，不盲目复制旧绕过 |
| 静态独立工程、集中配置、Bash入口 | F已完成，无需重建管理机制 | 新来源/生成物/分组再提取并完成一次异路径重建；仍以静态清单日常开发，不恢复长期Bender维护 |
| 工具环境 | 当前VCS2024已能运行既有组合 | 没有已知必须换VCS的证据；main新增Python≥3.11、uv/pip与PeakRDL配套，首次生成/以后维护生成物时需匹配工具环境；固定生成SV后的日常静态编译不当然要引入Python管理。系统默认Python3.6不代表工程已满足生成要求 |
| NPU/ISP/LVDS/GB/外购AXI4 DDR、ASIC SRAM/PLL/PAD/DFT | **均为后续实现/集成任务** | 同样必须做；当前RTL只有Xilinx DDR4原型，未实现四入口DDR、GB或新增图像IP。方案B不会自动实现LLC旁路/缓存交接/工艺替换 |
| Linux/OS | 现组合还需完整OS验证与已知异常/状态问题处理 | main scalar SDK/VCU118 DTS可参考，但不等价Ara OS配套；必须选定内核/OpenSBI/SDK/向量上下文并实测，不能直接沿用旧镜像 |

两方案采用相同标准：保留当前裸机功能和已知限定结果，新增修复有定向前后对照；涉及的CPU/Ara/LLC/SLINK路径运行既有回归；FPGA保留目标则重新生成与板测；Linux被纳入当期目标后单独验收；ASIC综合、宏/PHY、DFT及物理签核不由任何一项仿真代替。

**A＝选择当前必需补丁＋对应回归＋持续跟踪，B＝Ara集成＋尚需保留的补丁＋平台/软件适配＋新静态提取＋全部受影响回归＋后续跟踪。** B不会长期免除Ara分支、团队IP和静态提取差异；A的代价是随着主线接口演进，未来大功能回移越来越难。当前没有必须立即采用主线新平台功能的需求，优先修复集中在少数文件，因此A近期投入更小；这不是永久冻结依赖的建议。

不提供无测量依据的精确天数。可比较的工作量单位是：A的独立小补丁/确实不可拆依赖组；B至少增加SoC+CPU/Ara组合、寄存器/软件、静态构建三个适配面，以及仿真/FPGA/OS各自验收。最大未知项是B1在新CPU/MMU时序和新SLINK下的实际运行结果、OS异常恢复和应用缓存交接；本轮没有PPA或性能数据。

### 补充：把main合并进现有派生分支

在 `/tmp` 独立bare库执行 `git merge-tree --write-tree`，没有修改现有index/分支/文件：

- 官方 `e040b7bb… + main`：退出1，**11个冲突文件**，包括Bender两文件、`cheshire.mk`、SoC/pkg、TB配置、FPGA顶层与CI。
- 本地 `c9abbb48… + main`：退出1，**14个冲突文件**，另含HelloWorld、DDR wrapper、PHY定义。命令与全部结果见 [upstream合并日志](../reports/evidence/main_baseline_20261023/merge_upstream_ara.txt)、[本地合并日志](../reports/evidence/main_baseline_20261023/merge_local_head.txt)。

合并可保留历史、复用main已有VCU118代码，若以后迁移，值得作为实现方式比较；**当前未显示明显更省功能适配/验证成本**。原始三方合并还会保留L的26项 `Bender.local` 路径覆盖，即便修完文本冲突，也可能仍编旧依赖而误称main组合。F无Git且包含不同补丁，L的合并结果不能直接替换F。此次没有解决冲突或生成可运行迁移分支。

## 验证状态、下一步与改变结论的条件

| 项目 | 本轮状态 | 能证明与不能证明的内容 |
| --- | --- | --- |
| 官方版本/共同祖先/锁、本地26实际HEAD、嵌套改动及现存清单 | **已执行通过** | 来源及静态输入明确；清单文件存在不等于可编译 |
| R/F版本、来源元数据、现用OS/VCS；结束前F的962条目标哈希 | **已执行通过（只读）** | 当前版本/环境与记录衔接、F目标全匹配；R/F两份Ara候选源仍旧。不是重新构建/仿真，也未重算R所有依赖差异 |
| main CPU/Ara关键协议及类型消费者比较 | **仅完成静态分析** | 支持B1可行性；不是整个依赖组合编译或elaboration |
| Git隔离合并试验 | **已执行，自动合并失败（11/14冲突）** | 证明不能直接无冲突合并；不是硬件编译失败或不可迁移证明 |
| B0/B1依赖实际解析、生成源码列表、编译/elaboration | **尚未验证** | 本轮未形成改完的候选设计；本地未发现VCS/Verilator/iverilog，服务器VCS可用，但构造并构建整个新平台不是此次小试验 |
| B标量/RVV/共享数据/MMU/中断、FPGA/Linux | **尚未验证** | 没有任何main候选的动态PASS；未以已有ELF/bitstream代替运行 |

本轮隔离Git获取曾在沙箱内遇代理/DNS不可达，正常联网获取后成功；首个只读服务器查询脚本用了系统Python3.6不支持的 `text` 参数，改成兼容写法后成功。这些是调查工具问题，未记成SoC失败。原始历史、锁、依赖差异、接口比较、进入时状态和环境摘要保存在本轮证据目录；没有新增工程运行框架。

**接下来优先做：**沿F/R已有入口，一次选择一个已确认命中路径的局部修复（先Ara #481；浮点正确性随后#482、MVP #18；需要1D API时处理iDMA reps＋HAL），以现有测试加该缺陷的必要边界检查验证，再同步正式源。SLINK预加载按#191/#192最终函数成套评估。本文不表示这些补丁已经实施，也不自动恢复被暂停的LLC大范围排查。

出现以下任一变化，重开B评估：

1. 官方Cheshire提供受维护的Ara集成分支/主线入口和固定锁，并有匹配当前WT、2 lanes/VLEN2048、启动与向量访存的回归；或团队实际获得同等可追溯的B1结果。
2. 产品当期确实需要主线的SLINK2、SystemRDL/APB、vCLIC或其他现有平台没有的能力，局部回移已接近重做其前置平台；此时B额外适配转为必需工作。
3. 以真实任务记录比较后，多组必需修复的回移/回归工作持续超过一次B适配与回归，且B实际锁包含这些修复。不能只数主线提交或开放PR数量。
4. 当前组合暴露阻断目标应用、且不能局部修复的CPU/Ara/OS问题，而主线的确切候选已有对应通过证据；反过来，如果B1必须回退CPU/互连或改用pulp-v3，先重算收益，不继续沿旧预算推进。

**迁移启动条件与试验顺序：**明确需要上述收益，固定B1的SHA/配置与必保留补丁后，在独立源码/依赖/输出中先解析并检查实际清单、编译/展开及真实Ara层次，再跑标量启动/内存/外设；接着复用非stub CSR、RVV整数/浮点/向量访存与fmatmul金值；最后按改动测标量store→向量load、向量store→标量cache读、反压/复位、中断、MMU/异常归属与恢复。只有出现具体覆盖缺口才补检查，不预设大量新测试文件。FPGA和Linux各自追加其独立验收。

**停止条件与回退点：**依赖/真实选源与记录不符、需要未纳入收益计算的依赖回退或大接口改写、已有通过项出现未解释失败、系统关键路径仍没有所需测试条件时，停在该隔离阶段；保留失败源码/配置/日志，生产继续用未变的F及原L。不能以HelloWorld、无文本冲突或只编译成功解除这些条件。新的可替换基线形成前不覆盖F，不升级L的FPGA依赖，不删除原记录或 `.bender`。

---

## 同日此前的局部维护调查（保留原候选和实施细则）

以下为本次基线比较之前完成的阶段A记录；其中“本轮”“当前需要用户决定”指此前局部维护任务，不限制上方本次已获授权的调查和隔离Git试验。当时修复候选尚未实施；当前进展见上方阶段B停止记录，原阶段B/C步骤用于后续具体修复，不应与本报告的“方案B迁移”混为一谈。


查询与现场核查日期：**2026-10-23（Asia/Shanghai）**。输入本地 HEAD：`c9abbb48946fe3a7244bfb3159919b7c9731cb59`，保留进入时的未提交文档、图稿及未跟踪文件。主 Agent 汇总，三个本地子 Agent 分查 CPU/Ara、互连/DMA、启动/软件，并复查重要候选的后续问题。

**状态：阶段 A，已调查、待验证。未修改服务器源码/依赖，未构建、仿真、生成 RTL 或清理产物。本文不授权阶段 B/C。** 既有修正的“已验证、已同步”仅指此前记录，不是本轮重新运行结果。

**2026-10-23 用户确认：仅进行局部代码修复，不整包升级组件或依赖。** 后续只评估选定修复及确有必要的前置修改；此确认限定维护范围，不等于已选择候选或授权阶段B实施。

## 1. 建议先看什么

建议先从 **Ara #481（store 队列绕回停滞）、Ara #482（不同延迟浮点结果写错目标寄存器）、MVP #18（0/0 多报除零标志）** 中选择一个小修复验证。另有 **iDMA一维提交修复**值得优先：当前2D前端在关闭ND时仍把reps强制为0，既有wrapper及#80/#204没有修这一点。四项都命中当前启用路径，实际文件仍有旧逻辑；逐项选择和验证，不一起迁入后只测一次。

验证入口另有 **Cheshire #191/#192**：正式工程默认 Serial Link ELF 预加载仍有空 burst 和跨 4 KiB 边界风险。若选择维护预加载，先记录 #191 的中间对照，再单独验证 #192 完整函数；静态复核发现 #191 单独使用可能截断非拍对齐整倍长输入，不能先承诺独立采用。

**不建议直接采用“最新版本”。** Cheshire 主线与向量分支、CVA6 pulp-v3 与当前 PULP 版本均有分叉。FS Dirty 修复也不能按标题直接采用：#2936 修正 `fld`，但开放 #3173 记录了 `fcvt` 修改 `fflags` 后未置 Dirty；MVP #16 则有精确次正规结果多报 NX 的后续报告。下面分别列出条件与停止点。

## 2. 两工程的实际输入

简称 **R**＝`/home/zhaowy24/CheshireAraPULP`，**F**＝`/home/zhaowy24/CheshireAra`，服务器 `zhaowy24@172.16.0.243`。

### 2.1 本轮核对结果

- R 的 HEAD 仍为 `e040b7bbc7851a37faff3c4657ff8d656cc6e20a`。根差异含 `.gitignore`、DMA wrapper/HAL、`crt0.S`、三个 DMA 调用点、VCS start 和未跟踪 `wave.tcl`。它不是纯上游提交。
- 读取 R 的 `Bender.lock`，并逐项读取 26 个依赖的真实 HEAD、`git status --short`、`git diff --binary`；HEAD 和差异哈希均匹配 F 的 `provenance/reference.json`。未运行 Bender。
- F 没有 `.git`。按现有 `provenance/source_manifest.json` 逐项读取 **962 条记录**的目标文件并计算 SHA256，全部匹配记录；这些记录包含源、头、软件、文档等，不是“962 个 RTL”。对可对应到现存 R 文件的记录做字节哈希比较，差异仅为下述十项；`source=new` 等无原文件的新增集成对象不计入此比较。
- 十项差异：`src/config/cheshire_pkg.sv`、fixture、SoC TB、Serial RX 回归 TB、LLC `probe.tcl`、两份外设模型许可证摘录、`sw/tests/regressions/dma_long_2d.c`、`check_result.py`、`start.cheshire_soc.sh`。这些是已有配置/层次/入口适配；所选 CPU/Ara/浮点/总线候选文件及原 ROM 在 R/F 一致。
- **配置合并已实施**：F 只有 `src/config/{cheshire_pkg.sv,cv64a6_imafdcv_sv39_config_pkg.sv}` 两个活动输入，`Cfg=DefaultCfg`，由同一包派生 CPU 配置及接口类型。`DefaultCfg.Ara` 原默认 0→1，原有效值已是 1。不能重新创建旧独立 cfg 包。
- **入口简化已实施**：`sim/scripts/compile.cheshire_soc.sh` 编译；`start.cheshire_soc.sh` 展开/运行；`check_result.py` 解析；`sw/Makefile` 单独构建软件。F 没有活动 `run.py`。日常允许复用输出并打印 WARNING；本次候选比较仍拟显式指定新输出，以保存前后结果。

来源记录本身不替代源码；以上哈希检查后，又沿候选调用路径核对了配置、实例和具体旧代码。没有据哈希一致宣称生成差异语义等价或动态测试通过。临时读取摘要保存在本地 `/tmp/e01_maintenance_stage_a/`；长期事实与官方链接汇入本文，不新增维护脚本或证据平台。

### 2.2 当前版本、修正及启用情况

下表路径相对 F；完整 26 项锁定 SHA 见附录。R 的依赖路径来自现有 `provenance/reference.json`，不使用本地 FPGA 工作区代替。

| 组件 / 官方仓库 | 锁定 SHA / 来源 | 实际本地修正与 F 路径 | 当前相关配置 |
| --- | --- | --- | --- |
| [Cheshire](https://github.com/pulp-platform/cheshire) | `e040b7bbc7851a37faff3c4657ff8d656cc6e20a`，`mp/ara-pulp-v2` | `src/cheshire_soc/cheshire_top`、`src/config`、`sw`；DMA wrapper/HAL、FS Clean；F 另有共同 wrapper、配置合并、静态清单和软件入口 | 1 核；地址48/data64；Ara/DMA/SerialLink/Bootrom=1；AXI最大事务24；AxiRt/Clic/IrqRouter=0 |
| [CVA6 PULP](https://github.com/pulp-platform/cva6) | `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c` | `src/cheshire_soc/cva6`；仅两份 WT 读断言局部修正 | `cv64a6_imafdcv_sv39`、WT；RVF/D/A/V=1，RVH=0，MMU=1，UseSharedTlb=0，非超标量，提交口2；PMP实际0；Data/FetchUser=0 |
| [Ara](https://github.com/pulp-platform/ara) | `2895ba907e9eb14b3464609dc791a969d159a7c3` | `src/cheshire_soc/ara`；依赖无本地差异 | 真实 decoder，2 lanes/VLEN2048；CPU profile VLEN64是另一字段；Half/Single/Double、FP扩展及定点默认启用 |
| [FPnew / CVFPU PULP](https://github.com/pulp-platform/cvfpu) | `e5aa6a01b5bbe1675c3aa8872e1203413ded83d1`，0.2.3 | `src/cheshire_soc/fpnew`；无本地差异 | CPU `fpu_wrap` 与 Ara `vmfpu` 均选 `DivSqrtSel=PULP` |
| [MVP div/sqrt](https://github.com/pulp-platform/fpu_div_sqrt_mvp) | `86e1f558b3c95e91577c41b2fc452c86b04e85ac`，1.0.4 | `src/cheshire_soc/fpu_div_sqrt_mvp`；无本地差异 | 实际经 `fpnew_divsqrt_multi` 实例化，结果及 fflags 回传 |
| [AXI](https://github.com/pulp-platform/axi) | `39f5f2d51c5e524f6fc5cf8b6e901f7dcc5622d7`，0.39.6 | `src/cheshire_soc/axi`；无本地差异 | Xbar、串行链路和各适配器；不能把目录内所有模块视为已实例化 |
| [原子适配](https://github.com/pulp-platform/axi_riscv_atomics) | `0ac3a78fe342c5a5b9b10bff49d58897f773059e`，0.8.2 | `src/cheshire_soc/axi_riscv_atomics`；无本地差异 | 实际 LLC/寄存器等路径，RVA=1；LRSC FF仍为阻塞赋值 |
| [iDMA](https://github.com/pulp-platform/iDMA) | `c12caf59bb482fe44b27361f6924ad346b2d22fe`，0.6.3 | `src/cheshire_soc/idma`；#80+#204，含模板/生成器/生成 RTL | AXI64、2D、在途16、MemSysDepth8；共享LLC三类已知失败保留 |
| [LLC](https://github.com/pulp-platform/axi_llc) | `559bcbd09a5a884dbe31e2d72fd95d024e357f39`，0.2.1 | `src/cheshire_soc/axi_llc`；无本地差异 | 非旁路、128 KiB（8 ways×256 lines×8 blocks×8 B）；读写各16；DDR范围0x80000000–0x100000000 |
| [common_cells](https://github.com/pulp-platform/common_cells) / [register_interface](https://github.com/pulp-platform/register_interface) | `13f28aa0021fc22c0d01a12d618fda58d2c93239` / `ae616e5a1ec2b41e72d200e5ab09c65e94aebd3d` | 同名 `src/cheshire_soc/`；无本地差异 | FIFO/仲裁/CDC、旧regbus及`axi_to_reg_v2`实际消费者；不迁SystemRDL/APB体系 |
| [Serial Link](https://github.com/pulp-platform/serial_link) | `5a25f5a71074f1ebb6de7b5280f2b16924bcc666`，1.1.1 | `src/cheshire_soc/serial_link`；单通道寄存器HJSON/生成RTL已有差异 | SerialLink=1；**F默认**ELF使用BOOTMODE0/PRELMODE1；R当前start实际PRELMODE0（JTAG）；SlinkBurstBytes1024；RX已验范围不等于TX |
| [riscv-dbg](https://github.com/pulp-platform/riscv-dbg) | `358f90110220adf7a083f8b65d157e836d706236`，0.8.1 | `src/cheshire_soc/riscv-dbg`；无本地差异 | DebugEn=1；F默认预加载不是JTAG，R当前start默认是JTAG |
| CLINT / OpenTitan外设 / AXI-RT | 完整SHA见附录 | 同名源目录；已有CLINT、PLIC及AXI-RT寄存器源/生成物差异，差异哈希本轮保持 | CLINT及UART/I2C/SPI/GPIO等配置启用；AxiRt=0。启用不表示I2C/GPIO等外部功能已验收 |

已有修正明确保留：FS 清位后显式设 Clean；DMA wrapper 32/64位转换及编号读回、HAL四类32位指针/按次CONF；iDMA #80+#204；WT按有效读字节检查。它们与后续官方候选不是整包覆盖关系。原生成 ROM、已有 HJSON/RTL 本地差异、版权与来源也必须保留。

## 3. 官方变更概览与调查范围

下表是 **2026-10-23 查询到的分支快照**，不是推荐升级版本。提交链接内的完整SHA固定查询对象；PR是否合并另查 `merged`，不以 `closed` 代替。

| 组件 / 查询分支 | 确切 head | 与现版本的关系及主要变化 |
| --- | --- | --- |
| Cheshire `mp/ara-pulp-v2` / `main` | `e040b7bbc7851a37faff3c4657ff8d656cc6e20a` / `6c6dd5e834347f72c7be31cd6c41021ec293c5b9` | [比较](https://github.com/pulp-platform/cheshire/compare/e040b7bbc7851a37faff3c4657ff8d656cc6e20a...6c6dd5e834347f72c7be31cd6c41021ec293c5b9)：分叉，main多64/少17，merge-base `68a7836c0f8998581808efb561bd2fc275a95323`。启动/VIP/地址区域修复、DMA接口、RDL/APB迁移、工具和平台变化；不整树覆盖向量分支 |
| CVA6 `pulp-v2` | `4c02b24fe7c04690f626776a92274da24f80d1da` | [比较](https://github.com/pulp-platform/cva6/compare/99eac9a649001bdf5b8f9da52e0ca73d5c48db1c...4c02b24fe7c04690f626776a92274da24f80d1da)：后续37提交，含FS/MMU正确性、RAW/WAW发射优化及不同cache/profile修复 |
| CVA6 默认 `pulp-v3` | `a0501599ea9e9741f76d34a9377272f23921fdbf` | 分叉，多318/少11，merge-base `2d411b2dc85abe00398e7d404542f0bf1b96f648`；重基于OpenHW `81245a47fad8fe1a5d562d953ef2662e099def76`，更换CVFPU并更新AXI/common_cells等。[PULP变更说明](https://github.com/pulp-platform/cva6/blob/a0501599ea9e9741f76d34a9377272f23921fdbf/CHANGELOG-PULP.md)。另外沿当前WT/加速器路径查OpenHW后续修复；没有声称穷尽其所有profile |
| Ara `main` | `34bd3bc152421b4601a7bf3d6e8e91ffb545c99e` | [比较](https://github.com/pulp-platform/ara/compare/2895ba907e9eb14b3464609dc791a969d159a7c3...34bd3bc152421b4601a7bf3d6e8e91ffb545c99e)：后续18提交，六组/七项功能修复、工具适配，Bender.yml未变；另有未合并mask/reshuffle/归约/异常等PR |
| CVFPU `pulp` | `682f31e376ad796e2fea2eecfdaa2ef0141b2ca9` | 后续13提交主要MXDOTP、低精度FP4/6/8、PACE及流水线可配置化；不是当前传统FPU的必需维护包 |
| MVP `master` | `917dd79cb2dc1a8f43df1a84e0e4231508a980e9` | 1.0.4之后#16/#18两个修复；已读后续#29/#30，不能称master已消除所有浮点错误 |
| AXI `master` | `70b8e54fd460e3308e58be596ceb3566a6e3576e` | 后续154提交；含remap并发、counter语义、适配器修复，以及common_cells v2/模块名/端口变更。后者不适合整包回移 |
| axi_riscv_atomics `master` | `97a1dd2ac643c276880420a0cf8eea697f228aa9` | 后续30提交；LRSC赋值竞态小修、reservation容量/PLRU新功能及工具变化；新PLRU仍有开放问题 |
| axi_llc `master` | `31059c4be62985f81bc46138f09e442d996aa3f3` | 运行时SPM/cache转换、合并flush及配置快照修复，另有生成/依赖调整；不等同DMA系统死锁修复 |
| iDMA `master/devel` | `a6b1d6657c03998b6df0baf905d7babd006ba614` | v0.7.4；后续正确性、compute/transpose/多head、SystemRDL、common_cells v2、生成目录变化并存；不能只按版本号同步 |
| common_cells `master` | `e73baaec2ca665cd80c3c384e9258e35242b829c` | 后续138提交；按FIFO/计数消费者筛选；v2命名/接口变化不作为默认维护 |
| register_interface `master` | `d6e1d4cdaab7870f4faf3f88a1c788eaf5ac129d` | v0.4.7，后续10提交；含reg_to_axi错误标志及工具/lint维护 |
| riscv-dbg `master` | `643607e19df3435cfd77cc56143e2637f5900a6e` | command错误屏蔽、总线位宽、多hart/debug支持；区分当前64位单hart路径 |
| serial_link `main` | `521908b92919ac143cbc489623d2300f17589c52` | 后续32提交；SDR/serializer新功能、v2寄存器与接口重构、common_cells v2；无当前必须整升证据 |

## 4. 候选分类与适用性

所有新增候选均为 **已调查、待验证，未同步**。这里的“适用”指当前代码和配置具备触发条件，不等于本轮已经复现。只把有原测试记录的既有修正列为已验证/已同步。

### 4.1 优先验证的局部候选与入口候选

| 候选 / 官方链接与提交 | 类别 | 当前是否适用 | 已有修正是否覆盖 | 前置依赖及移植范围 | 预期收益 | 验证方法 | 建议 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **P1 Ara #481** [PR](https://github.com/pulp-platform/ara/pull/481) / [ae8297af0af38b52136826e591782042025725da](https://github.com/pulp-platform/ara/commit/ae8297af0af38b52136826e591782042025725da)，已合并 | 停滞修复：队列全部store已issue而未commit，环指针绕回相等，被误判无待提交项 | 是；`vstu.sv`仍比较`issue_pnt!=commit_pnt`；与lane数无此排除条件 | 未覆盖；不是DMA/LLC的等待链 | 仅`ara/hardware/src/vlsu/vstu.sv`，改比较计数；不改变队列深度、接口/配置/ISA或清单 | 消除这一种向量store停滞 | 见§5：控制B返回时机、数据/提交计数及向量回归 | **优先验证，建议首个** |
| **P2 Ara #482** [PR](https://github.com/pulp-platform/ara/pull/482) / [a987112abed1339ecc9723555759be79427224bf](https://github.com/pulp-platform/ara/commit/a987112abed1339ecc9723555759be79427224bf)，已合并 | 正确性：低延迟FP结果抢在高延迟结果前写错vd | 是；VMFPU启用，缺比较操作延迟分类且判断晚一拍 | 未覆盖；原精确浮点加法/矩阵乘不证明混合延迟次序 | 仅`ara/hardware/src/lane/vmfpu.sv`；补延迟分类及及时组合判定，不升级FPnew | 正确排序；可能增加必要等待，**不称性能提升** | FP32/64比较/转换/算术混排，独立与依赖vd、mask；结果及fflags检查 | **优先验证** |
| **P3 MVP #18** [PR](https://github.com/pulp-platform/fpu_div_sqrt_mvp/pull/18) / [2ec0514c1d538781a26df23fb8a947a60fcdccfc](https://github.com/pulp-platform/fpu_div_sqrt_mvp/commit/2ec0514c1d538781a26df23fb8a947a60fcdccfc)，已合并 | 正确性：0/0应NV，却同时置DZ | 是；CPU/Ara均PULP除法器，`norm_div_sqrt_mvp.sv`旧分支仍置DZ | 未覆盖 | 仅`hdl/norm_div_sqrt_mvp.sv`一行；**不需要先迁#16**，不升级FPnew/生成RTL | 修正标量及向量0/0异常标志 | ±0/±0与非零/0对照，NaN/NV/DZ、mask及fflags累积；精确正常算例回归 | **优先验证**；不扩大成完整IEEE浮点验收 |
| **P4a Cheshire #191** [PR](https://github.com/pulp-platform/cheshire/pull/191) / [1b893efc6ee520be7d135a1adda397af94fa1c45](https://github.com/pulp-platform/cheshire/commit/1b893efc6ee520be7d135a1adda397af94fa1c45)，已合并 | 正确性/协议（验证平台）：预加载末尾多发空burst | 是；F默认PRELMODE1，实际VIP仍`i<=sec_len`；R验证时显式选1 | 未覆盖；旧ELF通过不覆盖所有section长度 | R `target/sim/src/vip_cheshire_soc.sv` → F `src/tb/src/vip_cheshire_soc.sv`，`<=`→`<`一行 | 可消除拍对齐整倍长的空写，但非拍对齐有截断风险 | 1024倍数/非整倍数、非拍对齐、loader跳过空PT_LOAD；核对全部字节 | **有条件入口维护**；先作中间对照，未过边界不独立同步 |
| **P4b Cheshire #192** [PR](https://github.com/pulp-platform/cheshire/pull/192) / [ae5795dfdb177a8dc3ef2f43dcc7ceaa36fd9238](https://github.com/pulp-platform/cheshire/commit/ae5795dfdb177a8dc3ef2f43dcc7ceaa36fd9238)，已合并 | 协议（验证平台）：单burst跨4KiB，并重新处理非对齐beat | 是；1024 B最大长度不能避免非页对齐起点跨页；VIP尚无页边界切分 | 未覆盖；RX专项不是该ELF加载过程 | 与P4a同一task；在记录#191中间结果后，单独比较完整函数；不改SLINK生产接口 | 避免非法边界，保留完整加载 | 页尾起点、多section、非拍对齐整倍长、尾字节/邻区；与原版和P4a分别比较 | **有条件采用**，不能用P4a的局部通过替代最终装载边界验收 |
| **P5 iDMA 1D-in-ND修复** [#66 / 92799c5fabcf2cd1f224f970bbb040b290d08fd5](https://github.com/pulp-platform/iDMA/commit/92799c5fabcf2cd1f224f970bbb040b290d08fd5)的reps hunk＋[Cheshire #203 / bca9aadb7588de7046460daf91b39fe863a7a9d1](https://github.com/pulp-platform/cheshire/commit/bca9aadb7588de7046460daf91b39fe863a7a9d1)的HAL对应hunk | 正确性；启用2D前端、用1D API令ENABLE_ND=0时前端仍强制reps0，midend拒绝传输/合成错误响应 | **适用**：DmaConfEnableTwoD1、当前reg64_2d及汇总均旧值，HAL1D另清reps0；机制已静态核实，未动态复现 | wrapper/HAL宽度、#80/#204均未覆盖；不能把#203整体标已回移 | 仅ND关闭时reps归一hunk、对应模板/派生RTL及HAL删1D清reps行；不用#66新协议字段/后端工具改动，不升依赖 | 使当前1D API真正发起一维搬运；不改变2D API或宣称通用无死锁 | 官方`dma_1d.spm.c`的18 B小搬运＋保护字符、ID与实际请求；2D→1D→2D顺序及原小DMA回归，见§5 | **优先验证**，与LLC长搬运排查分开 |

以上候选不要求改变寄存器/地址图、软件ABI、cache类型、lane数、生成工具或依赖锁。P5必须同步所涉模板和已有派生RTL，但不需重生成全IP。P4只修验证平台，不宣称修复芯片硬件行为。

P4静态反例：`sec_addr=0x10000001, sec_len=1024`时，旧首轮只装`bf[0..1022]`，最后一次`i=1024`装`bf[1023]`；单改`<`删除该轮。#192的`b=-bus_offs`重新计算beat覆盖。**这是源码推导，未仿真**；把它列为必测，不靠当前17个对齐ELF掩盖。若阶段B只授权P4a，遇此失败即报告停止；若明确授权P4a/P4b分步评估，可保留该预期中间失败后继续验证P4b，最终通过前不写回原件。

### 4.2 有条件、暂缓及不适用候选

#### CPU、Ara及浮点

| 候选 / 官方链接与提交 | 类别 | 当前是否适用 | 已有修正是否覆盖 | 前置依赖及移植范围 | 预期收益 | 验证方法 | 建议 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **C1 FS Dirty #2936** [PULP ecb138010de2868532f43131697e38231162ddb5](https://github.com/pulp-platform/cva6/commit/ecb138010de2868532f43131697e38231162ddb5)，原OpenHW merge `2700d14471963909923bdcfa1b013b4d1b30e567` | 正确性；括号/优先级使`fld`等未置FS Dirty，并增加不写FPR操作筛选 | 是；当前`commit_stage`仍旧表达式 | **FS=Clean启动修正未覆盖硬件状态跟踪** | `core/commit_stage.sv`＋`core/include/ariane_pkg.sv` helper，无接口升级 | 能修fld路径；与历史FS保持Initial现象相符，但尚未本工程复现确认 | Initial/Clean→fld/fadd，F2I触发NX/NV，读FPR操作、flush、FS/SD分别检查；见下文风险 | **有条件验证，不直接采用**：#3173仍开放，失败停止，不宣称完整FS修复 |
| **C2 加速器取消 #3310** [a31b556c30d5f71be9124b0f910ebce3f5c34514](https://github.com/openhwfoundation/cva6/commit/a31b556c30d5f71be9124b0f910ebce3f5c34514)，已合并 | 正确性；同拍flush和acc_commit留下ready，ID复用后误送投机向量指令 | 当前acc_dispatcher清pending后又设ready；非超标量不自动排除此时序 | 未覆盖 | 仅`core/acc_dispatcher.sv`，flush优先并清pending/ready | 防错误发送/副作用 | 异常＋待提交向量＋trans_id复用；核对取消指令不进入Ara，正常向量回归 | 有条件采用；优先于大版本升级，但需定向取消时序证据 |
| Ara #433 [e970f7736cde544eb2a44c6a44ad7eb0f8789f1a](https://github.com/pulp-platform/ara/commit/e970f7736cde544eb2a44c6a44ad7eb0f8789f1a) | 正确性；SEW改变后标量提取缺reshuffle | 旧dispatcher在用 | 未覆盖 | `ara_dispatcher.sv`一行；无依赖升级 | 修`vmv.x.s/vfmv.f.s`读值 | SEW A写入→SEW B提取，整数/FP/符号；现有固定SEW加法不足 | 有条件采用：内核使用该模式时 |
| Ara #432 [0bfbcfca0ad2eaf6a7e6fd38ff5edd7f1208c2d1](https://github.com/pulp-platform/ara/commit/0bfbcfca0ad2eaf6a7e6fd38ff5edd7f1208c2d1)＋[7ab0206a258e2dbbd00935cd88656a66ef9ebf84](https://github.com/pulp-platform/ara/commit/7ab0206a258e2dbbd00935cd88656a66ef9ebf84) | 正确性；整数扩展源EMUL误按LMUL检查，合法指令误trap | 当前缺两处检查修正；如m2的`vzext.vf2 v2,v1` | 未覆盖 | **同PR两提交为配套组**：dispatcher及`vsext.c/vzext.c`新增CASE7 | 正确区分源/目的EMUL与非法目的 | m2/4/8、vf2/4/8、合法/非法寄存器；对照官方新增用例 | 有条件采用；维护者明确一般src/dst重叠检查仍不完整 |
| Ara #439 [4f876b5948aebd53dd948dce52f4aae244cfe574](https://github.com/pulp-platform/ara/commit/4f876b5948aebd53dd948dce52f4aae244cfe574) | 正确性；背靠背整数归约在VRF真正提交前清计数 | 当前`lane/valu.sv`为旧逻辑 | 未覆盖 | 仅VALU提交状态/计数 | 防归约次序错误 | 连续/依赖归约、VRF反压、各整数归约操作 | 有条件采用；不覆盖开放#470的其他问题 |
| Ara #440 [ce6a67427eb9b1ee7d89cf9d682cb801714b77cf](https://github.com/pulp-platform/ara/commit/ce6a67427eb9b1ee7d89cf9d682cb801714b77cf) | 正确性；slide1up误按stride减少提交数 | 2lane在用 | 未覆盖 | `masku.sv`和`sldu.sv`两处一起 | 正确计数/完成 | VL0/1/2、lane边界、mask/tail及标量插入 | 有条件验证；含该补丁的main仍有[#508](https://github.com/pulp-platform/ara/issues/508)边界问题，不能承诺完整slide支持 |
| CVA6 MMU #2798/#2802/#2976，[8a6028b646e649b811854ba27e9f2d0e39f612a8](https://github.com/pulp-platform/cva6/commit/8a6028b646e649b811854ba27e9f2d0e39f612a8)、[5576a2267f1a53ccc4e753ae61e7092c37f77786](https://github.com/pulp-platform/cva6/commit/5576a2267f1a53ccc4e753ae61e7092c37f77786)、[b56fbbb9bda82bd217c28b9338904e31ab4cd134](https://github.com/pulp-platform/cva6/commit/b56fbbb9bda82bd217c28b9338904e31ab4cd134) | 正确性；非对齐异常与请求错拍 | MMU=1/RVH=0，仍直通misaligned_ex；裸机也不能完全排除 | 未覆盖 | `cva6_mmu.sv`；**不能孤立#2798**，其RVH=0锁存回归需#2976纠正，#2802选正确有效信号；[#2989/00d8acf4f82a4d30c4a22e24682dad84860989ce](https://github.com/pulp-platform/cva6/commit/00d8acf4f82a4d30c4a22e24682dad84860989ce)的阻止错误DTLB请求hunk另注明，不搬无关Python部分 | 异常归属及请求时序正确 | 连续对齐/非对齐访存、mcause/mepc/mtval、无额外请求；Sv39与trap后恢复 | 有条件采用；不是运行既有572项即可证明 |
| CVA6 shared TLB #2945 [407787890aea1d1c91d2ac219bd82e9b815a4bd1](https://github.com/pulp-platform/cva6/commit/407787890aea1d1c91d2ac219bd82e9b815a4bd1) | 正确性；逐way比较ASID/VMID漏`[i]` | **当前UseSharedTlb=0**，错误分支不执行；仅MMU=1或启用Sv39不使其适用 | 未回移但当前无须 | `cva6/core/cva6_mmu/cva6_shared_tlb.sv` | 对其他配置修多way匹配 | 只有将来明确启用shared TLB后才做多ASID/替换/flush验证 | **当前不适用** |
| **MVP #16** [0d7807af3a1822f9c932dbcd3c8e33f90697ff6e](https://github.com/pulp-platform/fpu_div_sqrt_mvp/commit/0d7807af3a1822f9c932dbcd3c8e33f90697ff6e) | 正确性；UF/OF漏NX | 当前PULP路径适用 | 未覆盖 | 同norm文件一行，逻辑独立于P3；不能因此自动合并 | 修部分标志，但有后续反例 | OF/总下溢＋精确次正规对照，FP32/64和舍入模式 | **暂缓原样回移**；[#29](https://github.com/pulp-platform/fpu_div_sqrt_mvp/issues/29)报告新增精确次正规NX误报 |

**C1不能被简化为“已有官方完整FS补丁”。** 本轮实际读取 `csr_regfile.sv`：显式CSR写会置Dirty，但硬件`csr_write_fflags_i`分支只累积标志，没有独立置Dirty路径。[开放 #3173](https://github.com/openhwfoundation/cva6/issues/3173)给出F2I修改fcsr但FS仍Clean的复现。已合并[#3469 / 6ee41edb289f9480282493388ae39693df69f76d](https://github.com/openhwfoundation/cva6/pull/3469)另修SD摘要使用旧FS值晚一拍，**不修F2I→FS**；开放[#3638](https://github.com/openhwfoundation/cva6/pull/3638)还涉及VS→SD。若选择C1，只承诺验证fld收益和这些边界；F2I/SD检查失败时停止，不能现场扩大为自研CSR修复或删除FS=Clean。

**MVP后续报告是风险证据，不冒充本工程复现。** #29报告 `0x00800000 / 0x40000000` 的精确FP32次正规结果，原版已有多报UF，#16还多报NX；同时报告1 ulp、NX和无穷特殊值等剩余问题。#18仅消除0/0的DZ，与这些错误分开。即使P3通过，也不关闭整个除法器正确性限制。

#### Cheshire启动、软件与配置

| 候选 / 官方链接与提交 | 类别 | 当前是否适用 | 已有修正是否覆盖 | 前置依赖及移植范围 | 预期收益 | 验证方法 | 建议 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **C3 uncached SPM执行 #189** [7ecb93a324aee8d1562a8ea347cfb714abe837e9](https://github.com/pulp-platform/cheshire/commit/7ecb93a324aee8d1562a8ea347cfb714abe837e9) 的执行区域hunk | 正确性；0x14000000别名取指未纳入可执行区 | 当前128KiB，旧`AmSpm+2*SizeSpm`不包含相隔64MiB的别名；普通访存通过不等于可执行 | 同PR的HAL能力已回移，**执行区未覆盖** | 仅当前`src/config/cheshire_pkg.sv::gen_cva6_cfg`规则数、基址/长度；不覆盖已合并Cfg/类型，也不重复迁HAL | 允许既有非缓存SPM别名执行，不新增地址窗口 | 官方`spm_uncached.spm.c`思路＋最小别名取指；cached正常、非法区仍拒绝 | 有条件采用：需要别名执行时；若官方DMA用例触发旧LLC限制则停止，不扩排查 |
| **C4 Platform ROM返回 #187** [9b4c222df72f74f90ab9f36d80ba7b527f92e62b](https://github.com/pulp-platform/cheshire/commit/9b4c222df72f74f90ab9f36d80ba7b527f92e62b) | 启动正确性；非零PlatformRom钩子ret落错路径 | 原S/SV仍有旧布局；**默认PlatformRom=0，当前普通启动不触发** | 未覆盖；原SPI padding豁免无关 | 源`.S`与生成SV成对；精确裁取启动布局/必要对齐，保留FS；同提交sw.mk flash改动不相关 | 平台初始化返回后继续内置启动 | 可返回的最小平台钩子、默认0、原ROM/SPI完整启动；源/反汇编/SV对应 | 有条件采用，沿S01-B01；**单列重生成ROM授权**，不顺手重生成 |
| **C5 CLINT sleep条件 #252** [6234e9e9898951e7b6ab818f4e699831eb76d74e](https://github.com/pulp-platform/cheshire/commit/6234e9e9898951e7b6ab818f4e699831eb76d74e) 中一行 | 软件正确性；未来deadline反而提前return | 两边`sw/lib/dif/clint.c`仍`now < target`；所选应用未调用该sleep API | 未覆盖 | 只将`<`改`>=`，**无需同PR的CLINT/APB/SystemRDL迁移** | 正确等待未来deadline | 当前CLINT、真实timer中断、会返回的handler：未来/过期/相等deadline；默认trap自循环不能作通过测试 | 有条件采用：使用sleep API时 |

#### 互连、原子、DMA及LLC

| 候选 / 官方链接与提交 | 类别 | 当前是否适用 | 已有修正是否覆盖 | 前置依赖及移植范围 | 预期收益 | 验证方法 | 建议 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **C6 LRSC FF #35** [PR](https://github.com/pulp-platform/axi_riscv_atomics/pull/35) / code [1ad48f389da7cef3d4b5169baeb214febe02a0ba](https://github.com/pulp-platform/axi_riscv_atomics/commit/1ad48f389da7cef3d4b5169baeb214febe02a0ba)，merge `3617819b8f0d9283b9122e4cef690bcfc7c1df4d` | 正确性/仿真竞态；连续burst令clr_len误取下一笔0而下溢、多等AW_BURST | 当前真实LRSC FF仍阻塞赋值；官方在Verilator发现，VCS是否出现待验证 | 未覆盖 | 仅`axi_riscv_atomics/src/axi_riscv_lrsc.sv`的7项复位/更新`=`→`<=`；不升级0.8.3 | 消除该竞态；“10×simulation speed”不是本工程硬件收益 | 连续不同len AW、LR/SC＋普通写清reservation、数据/握手及572项；旧新版VCS都过则明示未复现 | **有条件采用，小范围次优先**；不增加首批任务数量 |
| **C7 LLC配置/flush链** [d410d306abafe4d242c702336d6a1a8cf4e2c753](https://github.com/pulp-platform/axi_llc/commit/d410d306abafe4d242c702336d6a1a8cf4e2c753)、[0c581edae31996bf4190af9350952648f553adfa](https://github.com/pulp-platform/axi_llc/commit/0c581edae31996bf4190af9350952648f553adfa)、[08fef39c1cc473669f03231d93b2c9a2da804002](https://github.com/pulp-platform/axi_llc/commit/08fef39c1cc473669f03231d93b2c9a2da804002)、[#44/f8ca916a53d9c0ecea68acbddcd90c2275816817](https://github.com/pulp-platform/axi_llc/pull/44) | 正确性/停滞；在途事务时重配、SPM→cache同时flush、busy时改配置 | 当前`spm_lock=cfg_spm`立即生效，flush/SPM二选一；配置代码未修；启动全SPM不证明运行时转换触发 | 未覆盖；**不修DMA三类循环** | 主要`axi_llc_config.sv`：寄存SPM锁→合并flush→修合并算法flushed更新→快照请求；不能孤立迁0c58而遗漏08fe；完整最终语义须核对这一依赖链 | 正确转换/排空、不会因忙时配置变化无限flush；最终flush多一周期，不是加速 | 借官方[#32/dee54d390784aa04ce62b288a0bd09851a68a5a4](https://github.com/pulp-platform/axi_llc/commit/dee54d390784aa04ce62b288a0bd09851a68a5a4)场景，dirty写回/way属性/命中计数/数据；从DDR执行，避免重配自身SPM栈 | **有条件采用**：近期确需运行时cache/SPM/flush；否则暂缓。旧平台直接复制新TB有时序差异，见下文 |
| **C8 reg_to_axi #54** [78547839e3036eb1585966137a1096974fc54124](https://github.com/pulp-platform/register_interface/commit/78547839e3036eb1585966137a1096974fc54124) | 正确性；OKAY被映为error=1 | Usb=1，OHCI控制路径实例化；当前仍旧比较 | 未覆盖；其他外设通过不证明USB此路径 | `register_interface/src/reg_to_axi.sv`一处`==RESP_OKAY`→`!=RESP_OKAY`，无接口/前置 | 正确响应成功/错误 | Regbus→AXI读写OKAY/SLVERR/DECERR，rdata/error/ready；复用相关CSR检查 | 有条件采用：使用USB控制口前；非图像通路首要任务 |
| AXI id_remap #409 [e11c4f9ff48f2c5dfd15a6dbe31404908df7c34b](https://github.com/pulp-platform/axi/commit/e11c4f9ff48f2c5dfd15a6dbe31404908df7c34b) | 等待/并发改善，可产生性能收益 | 当前HoldAR阻AW/反向，**SerialLink TX**实际实例化；RX回归不能证明TX收益 | 未覆盖 | 仅`axi_id_remap.sv`；保留ATOP双向ID规则/公平性，无参数变化 | 解除独立读写通道不必要互挡 | 双向TX、独立ARREADY/AWREADY反压；校验ID/顺序/ATOP后看目标事务周期与握手数 | 有条件验证，性能细则见§6；不是共享LLC修复 |
| AXI counter #440 [da8793b0e3f14c9186c94fac9ed6ec06375c254e](https://github.com/pulp-platform/axi/commit/da8793b0e3f14c9186c94fac9ed6ec06375c254e) | 配置语义/容量行为改变；2幂少1、非2幂超上限 | 主Xbar MaxTrans24旧可至31，新严格24；其他4/8路径另核 | 未覆盖 | 新上游拆出`axi_demux_id_counters`并用cc v2；旧版应仅适配`axi_demux_simple`语义，不能孤立复制新文件 | 精确容量边界，**不保证吞吐提升** | 4/8/24无返回压力、ATOP同拍加2、正确顺序/反压；官方声称测试但merge只带2个RTL文件 | **暂缓，单列配置行为变更** |
| LLC BIST比较 [06a4020d135de5d6c13b8dbcebfcfa2937e8239d](https://github.com/pulp-platform/axi_llc/commit/06a4020d135de5d6c13b8dbcebfcfa2937e8239d) | 工具兼容/比较正确性，packed struct XNOR改逐字段 | 官方特定VCS/Simon路径错误；当前BIST已有通过记录，未见同样触发 | 未覆盖，但不等于当前失效 | 单`axi_llc_tag_store.sv` | 避免特定编译器错误比较 | 相同工具/参数下BIST pattern/way比较，不仅看编译成功 | 暂缓，出现具体工具证据再选 |
| riscv-dbg #206 [643607e19df3435cfd77cc56143e2637f5900a6e](https://github.com/pulp-platform/riscv-dbg/commit/643607e19df3435cfd77cc56143e2637f5900a6e)，code `b1fd38ad58e564e45611f85c7e425594bddd7cdc` | Debug规范正确性；cmderr非0仍触发command/autoexec | 当前单hart也可能适用；未证明现有调试流程触发 | 未覆盖 | `dm_csrs.sv`命令与4个autoexec点，无需多hart更新 | 错误未清时正确拒绝新命令 | 注入cmderr、各autoexec读写、清错恢复及busy状态；官方未随PR加新测试源码 | 有条件采用：JTAG/调试器验收时 |
| iDMA零尺寸 #247 [892434bd794e55e9c918c6bcba20a0e494a0e955](https://github.com/pulp-platform/iDMA/commit/892434bd794e55e9c918c6bcba20a0e494a0e955) / #267 [6d640580919b96d3b63c6c4e615b7c6abe22b34a](https://github.com/pulp-platform/iDMA/commit/6d640580919b96d3b63c6c4e615b7c6abe22b34a) | 正确性；零长/零reps反压及后续地址污染 | ND/RejectZeroTransfers启用，但nd_rsp_ready固定1排除部分响应反压；backend被挡的零reps仍待验证 | #80/#204不覆盖 | #247模板及所用rw_axi生成/汇总成对，需保留已有模板改动；#267 ND midend及directed TB；不迁compute字段 | 零尺寸响应及后续strided地址正确 | 官方zero_transfer_busy/NDZ按当前可达条件裁取，不为未启用反压造框架 | 暂缓/有条件验证；无当前零尺寸工作负载依据 |
| common_cells FIFO [c777d27e5aa585f6c53cc68fbbcae6a542d9b1c1](https://github.com/pulp-platform/common_cells/commit/c777d27e5aa585f6c53cc68fbbcae6a542d9b1c1) | 正确性；full/empty握手与pointer更新 | iDMA使用passthrough_stream_fifo，但当前读push已含ready、写pop已含有效mask；所查路径未找到对应非法推进 | 未覆盖，但不能称当前DMA数据损坏 | v1单文件条件适配，不能整升v2 | 对其他消费者防无效推进 | 消费者确需时借官方[a49dc11f1b2360accea6b567a8d7aa36512c0f77](https://github.com/pulp-platform/common_cells/commit/a49dc11f1b2360accea6b567a8d7aa36512c0f77)反压测试 | 暂缓 |

LLC #44与原子#35后续问题也做了复查：LLC [#47](https://github.com/pulp-platform/axi_llc/issues/47)涉及借用#32计数TB的时序及DPLLC，不能把完整新TB照搬；partitioned分支[#49](https://github.com/pulp-platform/axi_llc/issues/49)不用于当前主线。atomics新limited-PLRU的[#43](https://github.com/pulp-platform/axi_riscv_atomics/pull/43)（head `481df4a253d75a9a8a2ffd669e81fad12667195a`）/[#46](https://github.com/pulp-platform/axi_riscv_atomics/issues/46)不在当前旧实现，进一步反对整包升级；旧实现还有开放[#32](https://github.com/pulp-platform/axi_riscv_atomics/issues/32)失败SC不清reservation、[#44](https://github.com/pulp-platform/axi_riscv_atomics/pull/44)（head `b8e3c184f72cdfcdd195bc2d822f3f6ad3306c8a`）冲突写时LR误回EXOKAY，**#35不覆盖这些边界**。以上均未在本工程运行验证。

### 4.3 已覆盖修正、开放候选与当前不适用项

| 对象 | 本轮核实的状态与采用判断 |
| --- | --- |
| 既有DMA wrapper/HAL | [bca9aadb7588de7046460daf91b39fe863a7a9d1](https://github.com/pulp-platform/cheshire/commit/bca9aadb7588de7046460daf91b39fe863a7a9d1)的宽度转换hunk＋[ef11799d00d9c7b19d042864529d03cbe41fac5b](https://github.com/pulp-platform/cheshire/commit/ef11799d00d9c7b19d042864529d03cbe41fac5b)端口、[4c2390f25f250c9ea75d314dd107da11a52aa8fa](https://github.com/pulp-platform/cheshire/commit/4c2390f25f250c9ea75d314dd107da11a52aa8fa)按次CONF及本地32位控制指针：此前已验证、已同步R/F。**只覆盖这些hunk，不是整个#203已覆盖** |
| 既有iDMA #80/#204 | [40fe6a67b6d734b6d75409803af5eea9d0eb51c8](https://github.com/pulp-platform/iDMA/commit/40fe6a67b6d734b6d75409803af5eea9d0eb51c8)＋[497c1f2300091121d5de9344f3a9e5e501af44c5](https://github.com/pulp-platform/iDMA/commit/497c1f2300091121d5de9344f3a9e5e501af44c5)均已合并；当前36文件本地回移与生成物仍在，此前已验证、已同步。#80写首拍驱动AW、#204空队列保护/按任务标志及许可计数共同保留；不重复实施 |
| 既有WT读断言 | 本地按有效字节适配已验证、已同步；官方[e606cdfe36b49d09c8f60975fd10f88948677c6d](https://github.com/pulp-platform/cva6/commit/e606cdfe36b49d09c8f60975fd10f88948677c6d)改的是HPD/std，仍整字检查，不是WT替代方案 |
| Cheshire FS #201 / #202 | [#201](https://github.com/pulp-platform/cheshire/pull/201) `closed`但`merged=false`，head `d9c413fa65559234aaddc31b14fb816ff857b9b6`；不是官方已合并启动修复。[#202](https://github.com/pulp-platform/cheshire/issues/202)关闭并指向CPU修复，也不能覆盖C1的残留或取代本地Clean |
| DMA共享LLC | [Cheshire #219](https://github.com/pulp-platform/cheshire/issues/219)查询时仍open、无修复提交。本工程三类循环由既有实际记录支持，暂缓扩展排查决定不变 |
| iDMA [#227](https://github.com/pulp-platform/iDMA/pull/227) | **open、未合并**，head `ac6a0d088904264fa5be17bd6d774e9c935d1d68`，base devel `a6b1d6657c03998b6df0baf905d7babd006ba614`；说明依赖仍开放的[#161](https://github.com/pulp-platform/iDMA/pull/161)，head `5fb2a81c4d0b462a87e55ede6f1a464124ce8324`。39文件：每byte lane为读返回预留容量、新deadlock_free字段贯穿请求/寄存器/生成层；当前BufferDepth3会使读burst限到2拍，可能降吞吐。admission不使用同周期pop以防组合环。**不是保行为小修，也不保证LLC写依赖/Bloom锁无环**；暂缓，不启动试验 |
| iDMA [#273](https://github.com/pulp-platform/iDMA/pull/273) | **open、未合并**，head `728e7330ecc45c2f0849e74e60535a8d1cb27788`，base同上；声明依赖#227/#228/#272，60文件、删除decouple_rw语义并把旧位保留reserved、读写始终独立legalize。架构/行为重构，不能替换现有HAL/#80/#204；暂缓 |
| iDMA [#221](https://github.com/pulp-platform/iDMA/issues/221) | open，ErrorHandling=1＋读错误场景，官方根因未定；当前**NO_ERROR_HANDLING**，不列当前已知可触发缺陷。#67 `d77382f069df9043a86bb78ba25ff53d149e2b7b`多协议read mux、#53 `ea201b0d62324d71668481bbe78790d754f3f1d3` no_burst/page_burst不属于当前单rw_axi/pow2分割路径 |
| Ara开放mask/reshuffle/定点修复 | [#469](https://github.com/pulp-platform/ara/pull/469) head `aee901c70f9eb9be644da556dc4a2ddd0de48661`；[#502](https://github.com/pulp-platform/ara/pull/502) `16edd3ba8a734b7cc52dee124bd86adb53fa66ff`；[#483](https://github.com/pulp-platform/ara/pull/483) `6b664a2c7437b4b2bea51af17b8a26a20b6d38e7`；[#503](https://github.com/pulp-platform/ara/pull/503) `8581df7d40f5041e1d8478a29e7751c82bbb83cf`。**均未合并**。#469有4个reproducer；#502虽报告2lane/VLEN2048，但基于含#469等额外补丁的树，去早退也可能增加周期；#483与已合并#433不是同问题；#503是SEW16 vsmul移位，定点虽启用但工作负载未定。暂缓，需求命中后固定依赖再选；不把开放PR称为main能力 |
| CVA6其他cache/profile修复 | WB fence.i `ad1c5e902ea87ef59db30293bbdeea07a7e5a8f6`、HPD refill `5d59eaed64a64b0bbfc5a50938c0c5ee2344533c`当前WT不适用；DTLB ASID `bb11e1d826ad1e219784fd0d1ecd86094bc1e0ce`在RVH0两选择相同；WT user切片 `2272df3e0339247a6e9718551eef6d819ec9b1a2`的DataUserEn=0；WT data_error `e978838530c1117e8df7457b184460d95f5d3313`针对后续新接口，当前load_unit无该字段消费者。均不为回移而引入新接口 |
| 其他基础IP边界 | common_cells delta_counter新修复针对后续引入的问题，当前v1.33复位已有正确`~rst_ni`；stream_join_dynamic在所查DMA/AXI/Cheshire/SLINK链未实例化，未推定所有其他消费者无问题。AXI HideStrb修复在已查debug adapter的HideStrb0不触发；dbg总线/抽象寄存器位宽修复在当前64/64无差异。GPIO/I2C/USB/板级PHY未因源码调查获得功能验收 |

### 4.4 新功能、重构与工具变化：不混入保行为维护

| 官方变化 / 提交 | 为什么暂缓或不适用 |
| --- | --- |
| Cheshire SystemRDL/APB [#260 / 519464ed4c123888c20dff53d2e9309d3e469ce6](https://github.com/pulp-platform/cheshire/pull/260)，首生成改动 `3aed98131242eac999219602c7397892946dda6c`；CLINT #252；SLINK [#253 / 79a5f5c477241ea515ad5ba1cf55b550382ad950](https://github.com/pulp-platform/cheshire/pull/253) | HJSON/regbus→SystemRDL/PeakRDL/APB，连同RTL/头/链接地址/ROM/生成工具变化；需配套新IP。当前集中配置/静态清单已完成，不为维护引入整套迁移。只摘C5一行不要求这套前置 |
| Cheshire UART [#225 / f6096ff2ac42db7a3f3f5374770947932b45f587](https://github.com/pulp-platform/cheshire/pull/225) | apb_uart0.2.3 `8182a85d234417db46fe833533f8536644d3bee3`改为obi_uart包装、增加obi_peripherals并升相关库；与旧UART分支无共同祖先，新实现的修复不代表原UART同病。暂缓 |
| AXI/common_cells v2，[aa799ec1b11e0ffc4d975938e1b3ea66a89c6f71](https://github.com/pulp-platform/axi/commit/aa799ec1b11e0ffc4d975938e1b3ea66a89c6f71)与[d4114f691b172ec1970165f1b5e63e6269a71836](https://github.com/pulp-platform/axi/commit/d4114f691b172ec1970165f1b5e63e6269a71836) | cc_重命名、test_i删除及版本不兼容；#409等局部改动不需要整升。iDMA/SerialLink同步迁v2、compute/SDR/新serializer也无当前必需收益依据 |
| Cheshire SD启动频率 [#197 / 5c63c992c827d6ed4b8daaf0e6818c78ac709d16](https://github.com/pulp-platform/cheshire/pull/197) | SD SPI频率取min(24MHz,core/2)，适用于低于48MHz核心的SD启动；当前验的是SPI NOR raw，非SD，无SD验收。当前不适用，涉及C与生成ROM不能顺手替换 |
| Cheshire [#246 / fcf135015e1a26ea4a2ad74c4c071f5a8fa645fa](https://github.com/pulp-platform/cheshire/pull/246)；Ara [e561b79de74daa38351b68ddd5559dc78c3af36e](https://github.com/pulp-platform/ara/commit/e561b79de74daa38351b68ddd5559dc78c3af36e) | 前者数组初始化语法工具兼容；后者“Update verilator”还含simd_mul四处默认赋值和C++修改。不是只读标题认定无RTL影响；当前VCS无对应故障，暂缓，必要时只取相关hunk |
| Cheshire MEMH [#263](https://github.com/pulp-platform/cheshire/pull/263)，`c60404ad7a3c1840235495ec3d67757604da6101`＋`2a77a408a1c5cf1babb23514d12f40865b830607` | 新直接内存加载/启动模式，改VIP/TB/DPI，减少主机加载时间；当前无此需求，不新增模式或替代原SLINK/ROM验收 |
| Cheshire [#290 / faa7d15287e1f491d38a7f1f77ca52210e6b77a7](https://github.com/pulp-platform/cheshire/pull/290)、[#284 / a315a828abb61cf3cb9f4419b910ebe6739b90bf](https://github.com/pulp-platform/cheshire/pull/284) | 修迁移后的APB禁用端口/配置，还改ID默认/LLC；当前未引入apb_mask，不能说修当前同一缺陷 |
| Python uv/pip [#261 / a4fa6988e9b6fe52aab3edbaac62399f369462c9](https://github.com/pulp-platform/cheshire/pull/261)、[#291 / 78e0181615b56135d8b867d405b65d5fb0216080](https://github.com/pulp-platform/cheshire/pull/291)；Questa/DRAMSys [#267 / 703de67b50d2fc53fe833eb18a9269058b39dd46](https://github.com/pulp-platform/cheshire/pull/267) | 当前工具环境已用、日常不生成RTL/装包；UseDramSys0＋VCS/GCC13不受GCC8 stdc++fs问题影响，不升级环境 |
| SDK [#256 / 4a3932e1bfb8ab72b2d934d65667caefbe2884fc](https://github.com/pulp-platform/cheshire/pull/256)；FPGA/新板卡/Verilator路线 | 固定裸机Make不等于SDK；没有针对当前libgcc编译模式的修复证据。保护本地FPGA，不改板卡/工具。开放[#306](https://github.com/pulp-platform/cheshire/pull/306)/[#259](https://github.com/pulp-platform/cheshire/pull/259)的pulp-v3/HPD/CMO方案属于架构迁移，开放[#230](https://github.com/pulp-platform/cheshire/pull/230)/[#307](https://github.com/pulp-platform/cheshire/pull/307)的主机仿真速度不是硬件性能 |

## 5. 最小验证范围与停止点

本节是拟执行的检查，**本轮一项也未运行**。优先复用已有非stub CSR、RVV 5976项、访存原子572项、22 B向量复制、32×32 fmatmul、HelloWorld、DMA及Serial RX用例；不是把它们全部套在每个补丁上。

| 候选 | 最小改动 / 对照单位 | 已发现的测试缺口与最小补充 | 受影响既有回归 | 候选特有停止点 |
| --- | --- | --- | --- | --- |
| P1 | 一份VSTU源码；其余源/配置/ELF相同 | 现有复制/尾部检查未强制“整队列先issue、B返回尚未commit”。在现有Ara测试平台控制返回/反压，提交恰好队列深度的store，随后释放B；检查每项提交、AW/W/B数量、数据及保护区。若SoC软件无法自然构造，报告定向单元证据，另跑SoC正常回归 | 22 B向量复制、RVV边界/存储；HelloWorld仅作基本启动 | 新增丢写/重复完成/通道不稳定，或需改变队列/LLC参数才能运行即停止。旧/新均超时须先辨别推进/异常/停滞，不能直接称补丁无效或死锁 |
| P2 | 一份VMFPU源码；保留当前FPnew与延迟参数 | 5976项含精确浮点加法，未覆盖相邻不同延迟结果竞争。优先复用官方blackscholes/现有Ara FP测试输入；不足时在既有RVV用例追加短混排序列，FP32/64、比较/转换/乘加/除法、独立vd及依赖vd、mask，核对每个目标寄存器与fflags。除法固有数值边界单列 | 原精确FP、32×32 fmatmul、非stub CSR；不把完整blackscholes成功当全部数值空间 | 新错误或未解释数值差异停止；等待周期变化先按正确性需要解释，不预先宣称加速；不为通过改FPU延迟或替换除法器 |
| P3 | norm一行；单独验证#18，不引#16 | 既有精确算例未测异常标志。最小补充标量fdiv.s/d与向量vfdiv：±0/±0、非零/±0、正常精确除法、被mask掉的异常lane及fflags累积。每项先准备操作数和清fflags，再设所需FS并执行/读取，防准备动作污染结果 | 精确FP及fmatmul；非stub CSR确认标志读取 | P3定向仍错或正常路径新增异常则停止；#29所述已有1ulp/UF/NX等问题保留，不把它们临时混为本补丁扩展范围 |
| P4a | VIP一行；相同测试ELF跑旧/新，作为中间对照 | 已静态读17个现有ELF：均单PT_LOAD、4KiB对齐、memsz非1024倍数，**不覆盖空尾burst**。复用HelloWorld源，仅在候选测试输出调整link布局产生1024/2048 B实载入段及非整倍数对照；**加0x10000001起1024 B截断反例**；先readelf确认。空PT_LOAD应由loader跳过，不伪造DPI/stub | F默认HelloWorld、原RVV ELF；R测试显式PRELMODE1；核对全部装载字节 | 无空burst不足以通过，还须完整装载；预期截断若复现，记P4a不能独立采用。是否继续P4b依该次授权，不自扩范围 |
| P4b | P4a实测中间结果＋VIP页切分；对原版和P4a分别比较 | 现有17ELF虽可跨多页，但1024 B burst均由页内0/0x400/0x800/0xc00开始，不能触发跨页。加合法第二PT_LOAD：页内0xff8起16 B，另测P4a截断反例、非8倍尾部、多/相邻段。核对每个burst不跨4KiB、全部字节和最终入口 | P4a输入、HelloWorld/RVV/fmatmul；SPI默认启动只作不受影响对照，不冒充该预加载路径 | 官方VIP仍按整beat补零；只检查定义允许的padding与邻段最终内容，不承诺任意guard不变。新的覆盖相邻段错误即停，不扩为SLINK接口重构 |
| P5 | 先固定旧HAL/同一ELF验证reps RTL修复，再单独去HAL多余清reps写并重建软件，明确两类变化的贡献 | 历史已有2D及wrapper检查不覆盖正常1D API。采用公开`dma_1d.spm.c`18 B搬运及`!\0`保护，源/目的初始化为不同值，核对完成ID、一次ND→backend传输提交且有实际读写、每字节和保护区；再检查不同残留reps状态下1D及2D→1D→2D顺序 | 原小2D、编号/上下半部访问、原通过长AW解耦、HelloWorld；iDMA后端未改，不预设重跑所有后端组合 | 若1D仍仅合成完成而没搬数据、2D退化或生成一致性不符，停止；触发共享LLC旧循环则记录并停，不降低在途数/改LLC求通过 |

P1/P2官方PR给出原因与触发描述，没有新增专用回归文件；P4a/P4b也没有配套新回归文件。维护者合并或第三方报告只能支持候选选择，不能代替上述实际验证。P3的后续#29提供0/0反例与独立复测线索，仍需在当前CPU/Ara集成中检查传播。P5的公开小用例来自Cheshire #203；未访问其nonfree CI，也不把私有CI声明当本工程证据。

**P5的生成来源范围已核实。** R中为iDMA `src/frontend/reg/tpl/idma_reg.sv.tpl`、`target/rtl/idma_reg64_2d_top.sv`和活动`target/rtl/idma_generated.sv`。若采用官方通用模板的完整reps hunk，同时保持现有`idma_reg32_3d_top.sv`及汇总内3D派生两行一致；3D未实例化，不能宣称动态验证。F已有映射只有`provenance/generation/idma/src/frontend/reg/tpl/idma_reg.sv.tpl`及`src/cheshire_soc/idma/target/rtl/idma_generated.sv`，**不新增独立_top文件**。另改`sw/include/dif/dma.h`删1D清reps行，保留四类32位指针和CONF接口；不用#66的protocol字段、hjson、寄存器包/头、新生成工具或清单改动。模板与当前派生文件按选定hunk同步，不默认全量再生成。

如选择C1，最小允许文件为`commit_stage.sv`与`ariane_pkg.sv`；保留crt0 Clean及WT断言。测试应在操作数准备、fflags清除后重新设FS=Initial/Clean，分别测fld、FPR算术、F2I改变NX/NV、仅读FPR、显式CSR写、取消指令；逐项观察FS及SD。规范允许保守置Dirty，因此仅读FPR后Dirty不是必然错误；真正修改FPR/fflags后仍Clean才是必查错误，见[官方FS/VS规则](https://docs.riscv.org/reference/isa/v20260120/priv/machine.html)。**F2I/SD失败即报告局部收益及残留，不写回原件，不自行串入#3469/#3638或自定义逻辑。** C2–C8及MMU/Ara其他候选若被选中，以§4各行给定最小范围和触发测试制定该轮具体命令；它们不自动加入P1回归任务。

## 6. 性能候选单列

| 候选 / 精确版本 | 性质及当前关系 | 本工程需要比较什么 | 建议 |
| --- | --- | --- | --- |
| CVA6 RAW/WAW #2881：[dcd5de6016f8643f431d5baa480549585632de31](https://github.com/pulp-platform/cva6/commit/dcd5de6016f8643f431d5baa480549585632de31)；后续#3009：[197f371c72d883ec6452809d82fb4299d8b5a939](https://github.com/pulp-platform/cva6/commit/197f371c72d883ec6452809d82fb4299d8b5a939) | **性能改进**：重写RAW选择、减少不必要WAW停顿；改`issue_read_operands`并新增`raw_checker.sv`，F静态清单需加入。#3009进一步移除rr_arb_tree以改善覆盖，不无依据称必需bug前置 | 相同ELF、输入、时钟/访存延迟/lanes/初态；标量准备及搬运循环，fmatmul标量金值与向量内核分别测`mcycle/instret`，配合WAW短序列issue停顿；同时检查结果、异常及原子/向量交互 | **暂缓**：尚无本工程瓶颈/收益数据，范围大于首批正确性修复；若专门选择性能任务，再定可接受收益与回退条件 |
| AXI id_remap #409：[e11c4f9ff48f2c5dfd15a6dbe31404908df7c34b](https://github.com/pulp-platform/axi/commit/e11c4f9ff48f2c5dfd15a6dbe31404908df7c34b) | 不改变配置的并发改善，当前实际作用点是SerialLink TX双向流量；单向RX或当前默认ELF装载未证明收益 | 同样ID/读写数据流、seed、AR/AW反压与端点延迟，检查数据/ID/ATOP/公平性，再测单位硬件周期完成事务、总周期及读写被无关通道阻塞的周期。先用已有平台可构造流量；若没有TX需求可不做 | 有条件验证；不由官方标题或主机耗时推算提升百分比 |
| Ara load/slide hazard下移 [开放#203](https://github.com/pulp-platform/ara/pull/203)，head `6b229498bd4fdf117ebcd2c3c414b9661a3b7f50` | 性能候选，改9文件/下游hazard；未合并，IPC/frequency检查不能视为已证明 | 固定向量复制/slide/依赖链及fmatmul，正确性后比较目标周期和停顿；不能只读PR宣传值 | 暂缓；不与正确性补丁打包 |
| CVFPU低精度、MXDOTP/PACE、新FMA流水线；CVA6 HPD/WB、超标量、新BHT等 | **新功能/架构或配置变化**，会改变操作/延迟/接口或支持范围；不是保行为维护 | 需要独立软件/ISA与数值范围、硬件参数、实现结果评估；本轮没有产品需求映射 | 不纳入本轮优先实施列表 |
| Cheshire MEMH/Verilator、原子PR中“10×仿真速度”等 | 工具/主机执行开销或修复错误等待后的观察；不能直接作为CPU/SoC硬件性能数据 | 若以后选择，只能分别记录主机耗时与目标周期，说明固定环境和原因 | 不作为本工程硬件加速依据 |

任何改变cache类型、LLC/总线拓扑、在途数、lane/VLEN或其他硬件参数的方案，均单列为架构/配置任务。本轮没有获得频率、面积或功耗数据；仿真周期减少不能推导这些实现指标。若正确性需要增加等待（例如P2），不得为了保留旧周期数撤掉必要等待。

## 7. 阶段 B/C 及授权边界

### A：本轮交付并停止

已完成实际版本/差异/配置核对、官方分支与候选diff/讨论检查、本文及现有索引/交接。只读访问现有产物的README/记录和ELF布局；没有执行ELF或仿真。没有恢复已清理工作区、生成RTL、升级工具或依赖。保护本地FPGA/RTL/sw、R/F及`.bender`、历史归档、TTY及其他工程、`/opt`和EDA工具。

### B：参考环境的隔离候选验证——另行授权

1. **先冻结本次实际输入。** 重新检查R/F变化，仅针对已选候选记录当前源、来源SHA、现有本地差异及配置。使用R现有成功编译清单和真实源码；不能从纯`e040`或官方最新分支重建一个遗漏FS/DMA/断言修正的“基线”。
2. **副本只携带当前候选需要的输入。** 对SoC候选，包含既有有效编译清单引用的源/include、原生成物、通用技术单元、TB/VIP/DPI、所需外设模型、当前配置、既有编译/运行入口、选定测试及必要软件/链接输入、来源许可。保持参考相对路径或在已有导出脚本中明确重定位；不把可写候选硬链接到原件。只有候选需要单元测试时再加入其现有单元平台。**不复制整个`.git`、整个`_e01`、历史simv/FSDB/trace、全部未使用依赖或整个验收归档。** 候选文件必须落在隔离目录，不能只换输出而仍编译原件。
3. **复用已有入口，不新增框架。** R成功静态编译脚本的历史位置为 `_e01/dma_vector_check/pr80_204_20261021/production_build/`，另有已使用的结果判定方法；实施前核实它们的现存位置和实际输入，若已归档只读取所需成员。局部调整候选源/输出引用即可，不预设重新Bender导出。若旧`run.py`隐式读取原输出绑定，先在该候选副本明确绑定当前输入，不能读旧缓存冒充新结果。**R当前start默认PRELMODE0；P4及拟保持F装载条件的候选须显式选BOOTMODE0/PRELMODE1**，不能依赖R默认。stub勿用。
4. **一次一个修复或确实不可拆组。** P1/P2/P3/P5各自独立；P4a→P4b保留中间测试；P5先RTL同ELF、再HAL重建对照；Ara #432的两个提交、MMU三个配套提交按组，不顺带迁相邻工具/架构变化。保留修改前文件及官方原始patch、局部适配差异；先旧后新使用同一测试输入与条件、不同新输出。若继续第二个候选，明确它是以上一已接受候选为基准，还是重新取原基准，不能混淆累计变化。
5. **证明范围。** 尽可能先复现旧行为，再验证修复和受影响既有用例；若当前配置无法复现，写明只有静态适用性/单元证明/回归通过中的哪一种证据。不能写伪造的“前失败后通过”。普通运行串行、无波形、每例默认600秒；超时先判断推进、异常或停滞；只在解释已出现失败需要时按原调试约定处理。
6. **结果必须按实际判据。** 保留目标、simv和入口三层结果、完成标记、断言、实际源/ELF/配置/命令/日志。F的现行解析语义是0正常、1目标失败、2断言/仿真错误、3其他simv错误、4未完成、124超时；R候选也须沿现有已验判据，不能仅看simv=0。原SPI padding仅“两读两写”已定位事件允许单列功能接受，仍返回2；不能放行其他告警。
7. **失败及停止。** 出现新增功能错误、未解释trace/协议变化、适配需要越过已选文件/接口/参数/依赖范围，保留失败输入和输出并停止；**已明确授权并列明的P4中间对照失败按§4的分步规则处理**，不当作最终通过。恢复只针对本轮候选改动；不用reset hard、整包覆盖或清理。**隔离副本通过不表示R原件已更新。** 是否写回R由阶段B授权明确；建议默认不写回。阶段B报告后停止，等用户决定是否采纳及授权C。

### C：同步独立正式工程并复验——另行授权

1. 只同步B已接受的hunk及必要前置项。按来源映射：依赖源→`src/cheshire_soc/<组件>/`，VIP→`src/tb/src/`，配置→当前合并版`src/config/cheshire_pkg.sv`，HAL按实际文件→`sw/include/dif/`或`sw/lib/dif/`；ROM仅在专门授权时同步`provenance/generation/bootrom/`源资料与`src/cheshire_soc/cheshire_top/bootrom/`活动生成SV。核对R验证后F是否又有改动，保留集中配置、共同wrapper、Bash入口及Make，不整包覆盖。
2. 先保存将改文件及相关来源/patch记录，作为可恢复输入；检查静态分组/include、重复定义、生成模板/生成物及许可证。P1–P5不应需要新增源或改变静态分组，P5需同步现有生成资料；RAW/WAW优化若另选才添加`raw_checker`。没有依据就不改清单。修改后更新现有来源清单/差异记录，不新增依赖管理机制。
3. 用F现行compile/start与Make，在**显式新BUILD_DIR/RUN_DIR/软件输出**重建受影响部分并运行已选定向和受影响回归。RTL候选可先复用同ELF做纯硬件对照；改软件才重建相关软件。不调用Bender，不在线下载/解析/更新依赖；不引入R绝对路径、旧`.bender`活动路径或旧缓存。正常联网及VCS既有许可通信沿用，无额外工程禁网要求。
4. 正式工程通过才记“已同步、正式复验通过”；R通过不能替代F。失败保留报告与日志，按本轮文件备份恢复到修改前的**实际版本**，不影响其他后续改动。若授权只允许报告不允许恢复原件，则停止等待处理，不扩大为全量升级。
5. 更新本文候选状态、现有E01交接及必要共享状态：官方SHA、实际版本/适配差异、运行证据、恢复方法及未关闭项。阶段C结束停止。上述通用模型仿真不代表ASIC/物理实现/流片验收。

### 保留的限制

DMA共享LLC的读挡写、写挡读、Bloom行锁循环保持；用户暂停扩展排查的决定不变。选了某个iDMA/LLC/原子修复也不自动重开该任务。原FS Dirty原因、libgcc特定128-bit除法在DRAM高地址的重定位限制、未解释旧warning、ROM padding限定事件逐项保留；只有对应实际新证据才改结论。历史测试路径按 `~/CheshireAra_validation_archive_20261022/validation.tar.gz` 内原目录名前缀定位，按需读取单个成员，不能恢复整个旧工作区。

## 8. 阶段A时待决定事项（本次P1–P5授权前的记录）

1. **选择首个阶段B候选。** 建议P1；若当前更关注浮点结果，选P2或P3；若要先完善DMA现有API，选P5。日常加载入口可另选P4a/P4b分步评估，明确P4a只是中间对照且可能失败。也可以保持现状，不安排更新。
2. **阶段B的写回边界。** 建议只允许隔离候选副本及新输出，验证后报告；如希望通过后写回R原件，需要在该次授权中明确。无论是否写回R，F均等待阶段C另行授权。

不需要用户现在决定整套依赖升级、换cache、改拓扑/参数或引入新工具。C1等条件候选及性能任务只有被明确选中时再实施。**本轮在阶段A交付后停止。**

## 附录：完整锁定版本与补充范围

本表逐项锁SHA与本轮实际依赖HEAD相符；F路径通常为`src/cheshire_soc/<组件>/`，配置、TB、软件和生成资料以现有manifest为准。`无`仅指当前依赖相对锁定HEAD无跟踪差异，不表示该组件无缺陷。

| 组件 / 官方源 | 锁定版本 | 完整SHA | 当前依赖差异 |
| --- | --- | --- | --- |
| [apb](https://github.com/pulp-platform/apb) | 0.2.4 | `77ddf073f194d44b9119949d2421be59789e69ae` | 无 |
| [apb_uart](https://github.com/pulp-platform/apb_uart.git) | 0.2.1 | `6c7dde3d749ac8274377745c105da8c8b8cd27c6` | 无 |
| [ara](https://github.com/pulp-platform/ara.git) | 固定提交 | `2895ba907e9eb14b3464609dc791a969d159a7c3` | 无 |
| [axi](https://github.com/pulp-platform/axi.git) | 0.39.6 | `39f5f2d51c5e524f6fc5cf8b6e901f7dcc5622d7` | 无 |
| [axi_llc](https://github.com/pulp-platform/axi_llc.git) | 0.2.1 | `559bcbd09a5a884dbe31e2d72fd95d024e357f39` | 无 |
| [axi_riscv_atomics](https://github.com/pulp-platform/axi_riscv_atomics.git) | 0.8.2 | `0ac3a78fe342c5a5b9b10bff49d58897f773059e` | 无 |
| [axi_rt](https://github.com/pulp-platform/axi_rt.git) | 0.0.0-alpha.9 | `641ea950e24722af747033f2ab85f0e48ea8d7f8` | HJSON、生成RTL及头4文件；功能关闭 |
| [axi_stream](https://github.com/pulp-platform/axi_stream.git) | 0.1.1 | `54891ff40455ca94a37641b9da4604647878cc07` | 无 |
| [axi_vga](https://github.com/pulp-platform/axi_vga.git) | 0.1.3 | `3718b9930f94a9eaad8ee50b4bccc71df0403084` | 无 |
| [clic](https://github.com/pulp-platform/clic.git) | 2.0.0 | `8ed76ffc779a435d0ed034f3068e4c3334fe2ecf` | 无 |
| [clint](https://github.com/pulp-platform/clint.git) | 0.2.0 | `d5390a805c20f9226758a152ba1645f61da73349` | HJSON及生成RTL4文件 |
| [common_cells](https://github.com/pulp-platform/common_cells.git) | 1.33.0 | `13f28aa0021fc22c0d01a12d618fda58d2c93239` | 无 |
| [common_verification](https://github.com/pulp-platform/common_verification.git) | 0.2.3 | `9c07fa860593b2caabd9b5681740c25fac04b878` | 无 |
| [cva6](https://github.com/pulp-platform/cva6.git) | 固定提交 | `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c` | 两份WT读断言 |
| [dram_rtl_sim](https://github.com/pulp-platform/dram_rtl_sim.git) | 0.1.1 | `2cac4a9e12a60537567276b539ab6c919c87b5dc` | 无 |
| [fpnew](https://github.com/pulp-platform/cvfpu.git) | 0.2.3 | `e5aa6a01b5bbe1675c3aa8872e1203413ded83d1` | 无 |
| [fpu_div_sqrt_mvp](https://github.com/pulp-platform/fpu_div_sqrt_mvp.git) | 1.0.4 | `86e1f558b3c95e91577c41b2fc452c86b04e85ac` | 无 |
| [idma](https://github.com/pulp-platform/iDMA.git) | 0.6.3 | `c12caf59bb482fe44b27361f6924ad346b2d22fe` | #80/#204，共36文件 |
| [irq_router](https://github.com/pulp-platform/irq_router.git) | 0.0.1-beta.1 | `d1d31350b24f3965b3a51e1bc96c71eb34e94db3` | 无 |
| [obi](https://github.com/pulp-platform/obi.git) | 0.1.5 | `5321106817e177d6c16ecc4daa922b96b1bc946b` | 无 |
| [opentitan_peripherals](https://github.com/pulp-platform/opentitan_peripherals.git) | 0.4.0 | `cd3153de2783abd3d03d0595e6c4b32413c62f14` | PLIC配置/生成RTL及头7文件 |
| [register_interface](https://github.com/pulp-platform/register_interface.git) | 0.4.4 | `ae616e5a1ec2b41e72d200e5ab09c65e94aebd3d` | 无 |
| [riscv-dbg](https://github.com/pulp-platform/riscv-dbg.git) | 0.8.1 | `358f90110220adf7a083f8b65d157e836d706236` | 无 |
| [serial_link](https://github.com/pulp-platform/serial_link.git) | 1.1.1 | `5a25f5a71074f1ebb6de7b5280f2b16924bcc666` | 单通道HJSON NumBits16→8及生成RTL3文件 |
| [tech_cells_generic](https://github.com/pulp-platform/tech_cells_generic.git) | 0.2.13 | `7968dd6e6180df2c644636bc6d2908a49f2190cf` | 无 |
| [unbent](https://github.com/pulp-platform/unbent.git) | 0.1.6 | `e9c9d5cfb635f2d4668c816ce9235798cfecb297` | 无 |

其他基础IP按版本及实际消费者登记；本轮未逐提交审查apb、axi_stream、axi_vga、clic、irq_router、obi、unbent等所有功能。Clic/AXI-RT/IRQ router及DRAMSys未启用；其他目录存在或通过编译不构成其全部功能验收。重点调查深度已在§3–4逐项说明，不作“全部上游缺陷已排除”的结论。

复查入口：

- [E01现行提取计划](server_reference_extraction_plan.md)，包括配置合并、Bash入口和历史搬迁结果。
- [E01主题交接](../../../handoffs/E01_fixed_vector_extraction.md)。
- [参考测试与限制](../reports/reference_rebuild_check.md)：§3启动/FS，§5 WT断言，§8 #80/#204，§9–10 LLC限制，§12剩余验收。
- 服务器现有`provenance/{reference,source_manifest,regression_inputs}.json`、`patches/`、当前README/docs及编译入口；旧路径以验收归档成员为准。
