# E01 / 243 服务器向量参考工程与固定工程实施方案

<a id="provenance-organization-plan-20261025"></a>

## 2026-10-25 第3轮：来源资料与历史记录整理（已完成）

### 2026-10-25 实施结果

用户明确“开始实施”后，已在正式`~/CheshireAra`完成归类。输入为本地HEAD `ca8395677691ba8d9d226ce4b5b5b49192b90f1c`、第2轮及ELF/TARGET文档完成后的1048份实际工程输入；参考工程及本地FPGA源码未改。

| 实际操作 | 结果 |
| --- | --- |
| 8份`2b_*` → `provenance/history/2b/` | 文件名、内容、权限保持 |
| 22份`2c_*` → `provenance/history/2c/` | 成功/失败日志和旧清单均保留，历史路径/哈希不改写 |
| 5份`2d_*` → `provenance/history/2d/` | 文件名、内容、权限保持 |
| 根`README.md`、`docs/README.md` | 更新当前2D导航，说明来源用途、阶段快照和旧新位置映射；保留ELF/TARGET、Ara及特殊测试说明 |
| `provenance/source_manifest.json` | 仅更新上述两份说明的当前哈希和维护记录；其余984条完全不变 |

provenance文件总数仍为217，顶层43→8；没有新建artifacts、独立索引/管理脚本或兼容符号链接。35份移动文件合计2,670,724字节，逐文件内容/权限与备份一致，所有移动前位置已空出。其他1010份输入哈希/权限保持；生成资料、补丁、原清单、LICENSES、RTL/TB/软件/Make/compile/start/check_result保持。没有移动、删除或清理sw/build、sim/work及外部验收归档。

**本轮检查：**986条活动来源哈希全匹配；被移动的35份文件不在活动destination中，JSON文件解析通过；两份说明25个本地链接目标存在，新provenance-history锚点有效，12段Bash片段语法检查通过。确认活动入口不引用被移动文件，source_manifest仍在原路径；仅将清单复制到备份中的临时检查文件并比较哈希一致，未调用编译入口。历史JSON内部路径保留原文，指南提供阶段目录映射；旧仿真产物仍按原外部归档索引定位。

**没有构建、仿真、生成RTL、更新依赖、Git提交或GitHub推送。** 前两轮结果仍为之前实测，本轮交付是目录、引用及恢复能力检查，不是新的功能验证。

**备份和回退：**服务器`~/CheshireAra_maintenance/provenance_history_20261025/`，本地`.e01_backups/provenance_history_20261025/`。`before.tar`与`after.tar`各38文件（35历史记录＋3修改文件），两地均实际展开并校验逐成员内容/权限；证据归档8成员（含7项校验索引）已核对。`moves.json`、`result.json`记录全部准确路径及改后哈希；完整差异在证据中的`changes.patch`。

恢复步骤见[rollback.md](../../../../.e01_backups/provenance_history_20261025/rollback.md)：先检查当前38文件无后续变化、旧位置未重新占用，再恢复旧位置与导航；发现指南/清单并发修改必须只逆向本轮导航和两条文档记录、人工保留其他维护内容，不整包覆盖。保留空history目录和全部输出，工作工程未执行回退。本轮备份不撤销此前Ara迁移、特殊测试整理或ELF/TARGET文档。

| 归档 | SHA256（两地一致） |
| --- | --- |
| `before.tar` | `0244d7228fc77078140e5374989eafe8c5ba9043c21b6e61c246ff34262a22e5` |
| `after.tar` | `5f9e3c606bceb658fa559d946f926f324c862fb949f7a48268a8eee220f65267` |
| `evidence.tar.gz` | `4ca968b7cc6845ccb9fb09ec442319833105c154038118b43f68f1bda587cba2` |

[详细检查结果](../../../../.e01_backups/provenance_history_20261025/result.json)。本轮完成后停止，不追加其他整理。

### 原规划（已获授权并实施，保留历史）

本轮只规划。已通过Windows SSH只读核对正式`~/CheshireAra`的provenance目录、实际compile/start/check_result与软件Make入口、现有指南及来源清单；本地HEAD `ca8395677691ba8d9d226ce4b5b5b49192b90f1c`，第1/2轮和后续ELF/TARGET文档修改均作为现状保留。未写服务器、移动文件、构建、仿真或清理产物。

### 定位与取舍

`provenance`意为来源及追溯资料，不是Codex专属目录。当前共217文件、约5.24MB，其中顶层43文件，`generation/`129文件、`original_manifests/`37文件、`patches/`8文件。活动`source_manifest.json`有986条，当前文件哈希全部匹配，其中155条指向provenance内的来源材料。

- 编译入口直接复制`provenance/source_manifest.json`到BUILD_DIR，结果解析器记录该编译快照的哈希；因此保留活动路径和格式，不整目录改名。
- 源码版本、原依赖锁/清单、许可证和差异记录必须随工程保存；即使最初由助手收集，也不是可以当缓存删除的内容。
- `generation/`含真实模板、HJSON、生成器及原配方，当前不参与日常构建。保留原层级，不能混成普通日志，也不据目录存在宣称可以直接重新生成当前RTL。
- 测试源码已在第2轮归类，继续留`sw/tests/regressions/`、`sw/link/regressions/`和`src/tb/regressions/`。ELF、日志、波形仍留`sw/build/`及`sim/work/`。**不新建工程根artifacts或Codex专属管理目录，不将这些内容合并到provenance。**

### 最小目录调整

仅移动顶层的35份2B/2C/2D历史文件，合计2,670,724字节；全部保留原文件名、字节及权限，不压缩、不去重、不删失败日志。下列glob是本轮查得的明确集合，实施前先冻结文件清单，不把后来新增的同名匹配文件自动纳入。

| 当前内容 | 数量 | 拟位置/处理 |
| --- | --- | --- |
| `provenance/2b_*` | 8 | `provenance/history/2b/`：RTL提取/编译与比较记录 |
| `provenance/2c_*` | 22 | `provenance/history/2c/`：软件提取、旧Make/README、旧清单和构建/比较日志 |
| `provenance/2d_*` | 5 | `provenance/history/2d/`：搬迁复制及验证快照 |
| `source_manifest.json` | 1 | 原位保留，当前来源入口 |
| `reference.json`、`group_selection.json`、`excluded_inputs.json`、`regression_inputs.json`、`generation_inputs.json` | 5 | 原位保留，来源/选取依据；在现有指南标明阶段快照属性 |
| `p1_p5_sync_20261024.json`、`cleanup_20261022.json` | 2 | 原位保留，既有指南直接引用的修补及外部证据定位记录 |
| `original_manifests/`、`patches/`、`generation/` | 174文件 | 整体原位保留，不另拆内部历史文件或重生成差异 |

整理后provenance顶层由43个文件降至8个，增加一个`history/`入口。不新增独立索引JSON、README或管理脚本；现有`docs/README.md`已承担目录/证据导航，直接在其中解释各类资料即可。

`reference.json`记录早期参考基底和当时状态，不能把其HEAD当成当前参考工程HEAD；`regression_inputs.json`、`generation_inputs.json`同样不能不经核对当当前哈希表。当前文件映射与哈希以`source_manifest.json`为入口，结合后续维护记录/实际文件核实；`patches/`不预设为覆盖所有后续修改的完整累计补丁。本轮只说明含义，不改造版本管理或修订历史事实。

### 引用、历史真实性与修改范围

- 修改服务器根`README.md`和`docs/README.md`中当前导航，尤其把`provenance/2d_summary.json`改为`provenance/history/2d/2d_summary.json`；说明35文件旧新位置对应规则。
- 历史JSON、旧README、日志、命令中的路径和哈希保留原样。指南明确：顶层`provenance/2b_* / 2c_* / 2d_*`旧记录分别到`history/2b / 2c / 2d`下找同名文件；原工作区/仿真产物路径另按原验证归档索引查找，不能一律套用这个映射。历史内容不伪改为新路径，不用兼容符号链接增加实体。
- 35个候选均不在当前986条来源destination中；因此不需虚构35条活动源码记录。只更新上述两份指南已有条目的当前哈希与维护说明，保留其他来源条目、原source/source_sha256及后续ELF/TARGET维护记录。`docs/CONFIGURATION_AND_DEVELOPMENT.md`现有引用均为保留路径，本轮预计不修改。
- 本地仅在既有计划、交接和任务表记录进展；活跃导航如有失效链接才最小调整，历史报告/备份中的旧路径不批量替换。
- `~/CheshireAra_validation_archive_20261022/`、`~/CheshireAra_maintenance/`、本地`.e01_backups/`及现有sw/build、sim/work均不搬动或清理。参考`~/CheshireAraPULP`、GitHub、本地FPGA、.vscode、工具与许可证保持。

### 获准后的实施与验证

1. **备份及并发核对：**重新读实际目录/受影响说明和来源清单；保存35文件准确路径、哈希、权限，备份拟改的3文件（根README、docs/README、活动清单）。工程外备份再复制本地并实际解包核对。确认新位置无占用、没有其他对话正在编辑同一说明/清单；发现冲突先保留，不覆盖。
2. **执行最小移动：**逐文件移动35项，只改当前导航、补目录用途与历史定位规则。对写入的说明/清单做写前哈希检查，确保未覆盖并发修改。无批量清理、无重生成RTL、无依赖或工具升级。
3. **检查即可，不为归档运行仿真：**逐一比较35文件内容/权限和旧新映射；解析归档前后JSON确认合法，核对当前文档链接/锚点及旧路径定位规则；核对986条来源哈希，其他源码、Make、compile/start/check_result、TB、配置及既有产物不变。检查当前入口不读取被移动文件、活动清单仍在原位置；必要时将清单复制到临时检查目录并比较哈希，不调用RTL编译入口。
4. **验收界限：**交付“35项移动、导航/清单检查通过、两地恢复核对通过”，不写成新功能验证或重新仿真通过。第1/2轮结果仍是此前实测结果。本轮不需要构建、仿真或扩大测试范围；若发现某个候选被活动入口读取，则先留在原位并调整计划说明，不顺手改构建脚本。
5. **恢复：**记录旧新位置和改后哈希。需要回退时先确认旧位置未被重新占用、新位置及3个修改文件没有后续变化，再按备份恢复；若指南或来源清单有后续编辑，只逆向本轮导航/对应条目并保留其他记录，不整文件覆盖。输出、历史证据及失败记录始终保留。

**待用户同意：仅将35份2B/2C/2D文件移入provenance/history，其他来源材料原位保留，不新建artifacts目录。** 本轮交付规划后停止。

<a id="special-tests-organization-plan-20261025"></a>

## 2026-10-25 第2轮：特殊测试与链接脚本整理（已完成）

### 2026-10-25 实施结果

用户明确“好的，开始实施”后，已在服务器正式`~/CheshireAra`完成本节方案。输入为本地HEAD `ca8395677691ba8d9d226ce4b5b5b49192b90f1c`、Ara首批迁移及TB/Tcl排版后的1048份实际输入；参考工程`~/CheshireAraPULP`及本地FPGA源未修改，无Git提交/推送。

- **9文件移动：**7个P1–P5 C文件移到`sw/tests/regressions/`，2个P4 ld移到`sw/link/regressions/`，原名、内容与权限全部保持。各文件明细见下方原规划表。
- **5文件修改：**`sw/Makefile`拆分日常/维护构建集合并改源路径；`docs/README.md`增加使用说明；根`README.md`及`docs/CONFIGURATION_AND_DEVELOPMENT.md`修正默认数量/P4路径；`provenance/source_manifest.json`更新当前destination和变更记录。后两份说明是在实施检查时发现的必要同步，已纳入完整备份。没有改测试算法、golden、RTL、TB、仿真入口、静态清单或配置。
- **默认7项：**`helloworld`、`helloworld.rom`、`vector_fixed`、`fmatmul.spm`、`rvv_test_vstart_csrs.spm`、`rvv_bounds.spm`、`memory_atomic.spm`。新OUT实际默认只生成7个ELF；`make -C sw regressions`显式增加其余24项，原ELF名称保留；`ara-tests`仍独立，不混入all。全部`.d`依赖仍读入，不删除旧输出。
- **来源保护：**986条当前来源哈希全匹配，原source/source_sha256保留；整理时1034份不涉及输入内容/权限不变，9个移动文件内容/权限匹配，另5文件为上列修改。既有P1–P5报告和旧命令路径是历史快照，未伪改；另一轮TB/Tcl排版与Ara测试均保留，未开展provenance目录整理。

**软件与运行验证：**先从未移动的当前源码在`sw/build/special_tests_20261025_before/`重新构建原31项及ara-vadd；整理后在`sw/build/special_tests_20261025/`依次执行all、regressions、ara-vadd，分别观察7/31/32个ELF。32项逐一比较入口、每个PT_LOAD的地址、filesz/memsz、权限、对齐和内容哈希，全部相同；6个P4 ELF均包含在比较内。移动后的C依赖路径正确，无参考工程依赖。三份使用说明的Bash片段语法检查通过。

运行复用已核对soc源码一致的`sim/work/ara_tests_20261025/soc`，没有重新编译RTL；现有start仍逐次展开，独立运行目录为`sim/work/special_tests_20261025/runs/`。串行、无波形、每项600秒，以下7项均目标0/simv0/入口0、PASS、无未解释错误：

| 用例 | 实际结果 |
| --- | --- |
| hello | PASS；Hello World! |
| vector | PASS；Hello Vector World!；VECTOR_COPY errors=0 bytes=22 |
| ara_vadd | PASS；ARA_DONE cases=7 checks=25 vsets=27 errors=0 |
| p2 | PASS；P2_DONE c=835 e=0 repeat=8 |
| p4_4 | PASS；P4_DONE case=4 c=1034 e=0 |
| p4_5 | PASS；P4_DONE case=5 c=19 e=0 |
| p4_6 | PASS；P4_DONE case=6 c=29 e=0 |


P4三项的完整`[P4_*]`观察记录与前次P1–P5验收一致；均missing=0、bad=0、errors=0、launch=1。P2两lane各136次输入/输出相等、无非计算结果错配，标量early/store_without_addrack均0。P4 case1/2/3及其余未运行目标只证明本轮可装载内容/布局保持，**不写成重新仿真通过**。既有FS/libgcc、ROM padding限定告警、共享LLC限制不变。

**备份及恢复：**服务器`~/CheshireAra_maintenance/special_tests_20261025/`；本地`.e01_backups/special_tests_20261025/`。完整回退输入是`rollback_before.tar`（14文件），`after.tar`保存14个最终文件；初始`before.tar`仅12文件，不含后续发现需同步更新的两份说明，不能单独完整回退。两个完整归档在服务器和本地实际恢复到独立目录，逐文件内容/权限核对通过。收尾时另一轮ELF/TARGET文档整理已更新两份指南及其来源条目；用户确认已结束并要求保留。当前三文件另外保存为`concurrent_docs.tar`，与本轮`after.tar`区别记录，没有覆盖后续修改；源码/Makefile仍与本轮验证版本一致。恢复步骤见[rollback.md](../../../../.e01_backups/special_tests_20261025/rollback.md)：旧版本整套恢复命令在当前后续文档哈希处会主动停止，不能绕过。仅回退本轮时，9个源文件、Make和根README可按本轮版本恢复，两份指南需保留新增ELF/TARGET内容并人工调整回退后的路径/构建集合；来源清单只逆向本轮映射及相关哈希，保留后续维护记录。明确授权连后续文档一起撤回时才按相反顺序使用两轮备份。未在工作工程执行回退，不清理输出。

源码差异、映射、基准/新ELF、命令及7项结果保存在两地证据中；完整hart轨迹保留服务器运行目录。归档信息如下：

| 文件 | SHA256 |
| --- | --- |
| `before.tar` | `2720c25f5770f03a1b8031ca20d9cb24357dfbd4d9e461b98d2b82c61529c8fe` |
| `rollback_before.tar` | `b96704419f54e88d929b5c85d07d6685944e2d4b7acbd3d4bce1f86e73f00943` |
| `after.tar` | `6df6a0cb829f5b897b83e0543e3656b9c2b021072ffc6001f22360bd5ad6b02a` |
| `concurrent_docs.tar` | `e21d75fdd5c52bc968622915c035b5145388f47f4643622e141c52cf44a630be` |
| `evidence.tar.gz` | `f127e35ba0ba65663c2d4aaf675f3151bcc2703a165f8ffb4ffbb084f945db0a` |

证据归档242个成员（241项索引），两地归档与逐成员哈希/权限检查通过；[逐项验收](../../../../.e01_backups/special_tests_20261025/acceptance.json)。


本轮完成后停止。第3轮provenance整体整理尚未规划/实施，不自动继续。

### 原规划（已获授权并实施，保留历史）

用户要求在Ara首批迁移完成后进行第2步规划。本轮经Windows SSH只读检查正式`~/CheshireAra`的实际软件清单、Makefile、链接脚本、仿真入口及相关来源记录；本地HEAD为`ca8395677691ba8d9d226ce4b5b5b49192b90f1c`。**没有移动服务器文件、修改构建入口、构建或仿真。** 第3轮provenance整体整理仍不开始；本节方案需用户同意后实施。

### 整理目标与目录

特殊测试仍是工程的可维护回归源码，后续改RTL时可用来检查旧bug是否重现；不当作一次性产物删除，也不放入含义不明确的Codex artifacts目录。复用已有`sw/tests/regressions/`；生成的ELF、日志和波形仍放`sw/build/`、`sim/work/`，历史证据不搬动。

| 当前位置 | 拟调整 | 用途/边界 |
| --- | --- | --- |
| `sw/tests/p1_vstu_wrap.c` | 移入`sw/tests/regressions/`，原名不变 | 存储队列绕回复现 |
| `sw/tests/p2_vmfpu_order.c`、`p2_vcpop_boundaries.c`、`p2_scalar_overlap.c` | 同上 | 浮点次序、mask边界、共享标量返回 |
| `sw/tests/p3_div_flags.c` | 同上 | 除法/异常标志及mask矩阵，两目标共用一个源 |
| `sw/tests/p4_preload_bytes.c` | 同上 | 六类ELF预加载边界 |
| `sw/tests/p5_dma_1d.spm.c` | 同上 | 一维与二维交替DMA，两目标共用一个源 |
| `sw/link/p4_single.ld`、`p4_multi.ld` | 移入`sw/link/regressions/`，原名不变 | 只用于P4；普通link目录顶层保留3种官方ld及公共ldh |
| 已有`sw/tests/regressions/`其他源 | 保留原位置/内容 | 不趁机重命名或重新分类整个测试库；`vector_fixed.c`虽在此目录，仍作为日常示例构建 |
| `src/tb/regressions/`及soc TB内P1–P5监视逻辑 | 保持 | 已隔离且按目标/开关使用；不移动刚排版的TB/Tcl，不修改compile/start/filelist |
| `sw/tests/ara/rv64uv/`、公共头 | 保持 | 首批Ara测试继续显式`ara-*`/`ara-tests`构建 |

总计只移动**7个C文件、2个ld文件**。源码、golden、链接布局、权限、ELF文件名和运行参数保持。无需新增README、独立Makefile、脚本或参数框架；在现有`sw/Makefile`及`docs/README.md`完成入口说明。

### 默认构建与显式回归

只搬目录不会解决当前默认生成31个ELF的问题。建议同时调整现有Make目标集合：

- `make -C sw`默认构建7个日常ELF：`helloworld.elf`、`helloworld.rom.elf`、`vector_fixed.elf`、`fmatmul.spm.elf`、`rvv_test_vstart_csrs.spm.elf`、`rvv_bounds.spm.elf`、`memory_atomic.spm.elf`；保留对应库/map/dump和SPI镜像生成。
- 新增一个显式`regressions`目标，构建其余24个既有ELF及dump：P1–P5共14个、RVV负例1个、DMA/LLC/SLINK维护目标9个。它**只构建，不自动运行**，其中有预期失败和已知限制，不能定义为“一键全通过”。
- 保留现有逐个输出目标，如`make -C sw OUT="$PWD/sw/build/check" "$PWD/sw/build/check/p2_vmfpu_order.elf"`；执行命令仍使用原start入口。`make -C sw all regressions`可重建原31项集合；Ara11项仍另用`ara-tests`。
- 复用现有split/direct规则及ELFS依赖收集，只明确日常/回归目标集合；不能为了从all排除而漏掉回归`.d`依赖。P4规则的链接脚本参数改为`regressions/p4_single`或`regressions/p4_multi`，现有`-L sw/link`继续解析`common.ldh`，不复制公共链接文件。
- 不删除旧输出；旧目录里的特殊ELF不会因默认集合缩减自动消失。验收使用新OUT，避免把旧产物误认成本轮默认生成。

这是有意改变默认构建集合，**不是已经实施的状态**。DMA维护测试仍可显式构建；今后需要日常DMA例程时另讨论，不借本轮把历史排查程序改写成用户示例。

### 特殊ld的额外用途

普通链接选择仍为：`spm.ld`在SPM运行，`dram.ld`在DRAM运行并设置对应栈，`rom.ld`规定ROM镜像装载地址与SPM运行地址。`common.ldh`为公共定义，不是第四种启动模式。

P4脚本不表示新存储器配置，而是**强制生成普通布局不保证出现的ELF可装载段**：

| P4用例 | 强制布局 | 检查目的 |
| --- | --- | --- |
| 1/2 | 1024/2048字节段 | 循环边界、避免多发空突发 |
| 3 | 1031字节段 | 非整拍尾字节不丢失 |
| 4 | 从`0x10000001`起的1024字节段 | 非拍对齐装载 |
| 5 | 从`0x10000ff8`起的16字节段 | 4 KiB边界处分割事务 |
| 6 | `0x10002000`起13字节，紧接9字节第二段 | 不用前段padding覆盖后段真实数据 |

脚本还固定应用段、保留栈区域并检查段长度。它们对预加载器维护有价值，日常更换ELF不需要选择；不能用spm.ld替换它们后仍宣称P4边界覆盖保持。

### 实施、验证与回退（待授权）

1. **先备份。**重新核对现场及并发修改；将9个待移动文件、Makefile、docs和需要更新的活动来源记录备份到工程外并复制本地，保存哈希/权限/旧新路径。先确认新位置不存在冲突，不覆盖已有文件。保护另一轮已排版TB/Tcl及Ara迁移结果。
2. **只改路径和集合。**移动9文件，调整Make路径/默认集合，在现有docs说明日常与显式回归。同步`provenance/source_manifest.json`的当前destination及Make/docs哈希，保留参考source/source_sha256；检查相关patch/活动路径引用，只有失效引用才最小修正。`regression_inputs.json`、P1–P5同步报告、旧命令/日志作为历史快照保留，不伪改历史路径。不得开展第3轮provenance搬迁/合并。
3. **静态及软件验证。**逐文件比较移动前后内容/权限；核对默认目标7个、回归24个、Ara11个不进入all，全部依赖仍可追踪；从新OUT重建原31项以及`ara-vadd`。对照迁移前匹配版本的可装载字节、入口、PT_LOAD地址/长度/标志，特别检查全部6个P4 ELF；调试路径变化可使完整ELF哈希不同，不能仅据此判功能改变。若基准ELF无法匹配当前源/参数，先从未移动版本重建对照，不借用不明旧产物。
4. **代表性串行复验。**先复用已确认源码一致的soc编译产物、用新RUN_DIR运行HelloWorld、vector_fixed、ara-vadd、P2次序、P4 case4/5/6，共7次；分别确认普通入口、未移动示例、Ara显式入口、移动C文件及特殊ld路径可用。保留P2/P4原配套监视参数和多层结果判据；P4其余case先由完整PT_LOAD/可装载字节一致性覆盖，不把未重跑项写成重新动态验证。普通运行无波形，每例600秒；失败先定位路径/构建差异，不改RTL。无新差异或失败不扩展成全工程重测。
5. **可回退交付。**保留旧新映射、前后哈希、构建/运行记录和两地备份；实际解包检查可恢复。回退前确认涉及文件无后续修改，再按映射恢复旧位置及本轮入口记录，移除仅本轮新增且未变的目标文件；有并发变化停止覆盖、人工合并。保留输出和失败证据，不reset、不清理依赖。正式工程无Git的现状不在本轮改变。

完成后只报告本轮目录/默认集合变更和实际验证；参考`~/CheshireAraPULP`、本地FPGA工程及GitHub均不修改。**本轮规划后停止；用户同意上述9文件移动及默认31→7、其余24显式构建后才实施。**

<a id="ara-tests-migration-plan-20261025"></a>

## 2026-10-25 Ara 官方 C 测试首批迁移（已完成）

### 2026-10-25 实施结果

用户“开始实施”后，已直接迁入服务器正式工程 **`~/CheshireAra`**，不是只保存在候选副本。输入为本地HEAD `ca8395677691ba8d9d226ce4b5b5b49192b90f1c`、正式工程实际1033份输入，以及Ara `2895ba907e9eb14b3464609dc791a969d159a7c3` 锁定源码；参考工程HEAD保持`5986ba021e1a0d30dbdb5ecb2cfa230a2c35947c`。本轮不修改参考工程、不提交/推送GitHub。

**实际文件：**新增下面11个C及4个头，共15个；修改`sw/Makefile`、`docs/README.md`、`provenance/source_manifest.json`共3个旧文件。Make只增加显式`ara-*`/`ara-tests`目标，原内容前缀和默认`all/ELFS`保持；使用现有`spm.ld/common.ldh`、启动、库、工具链和compile/start/check_result入口，没有新增ld或运行框架，没有改生产RTL、TB、配置、FS或cache。

| 正式工程位置 | 文件 |
| --- | --- |
| `sw/tests/ara/rv64uv/` | `vadd.c vl.c vs.c vmul.c vredsum.c vslideup.c vcpop.c vls.c vss.c vluxei.c vsuxei.c` |
| `sw/deps/ara/rv64uv/` | `vector_macros.h dataset.h rvv_debug_macros.h float_conversion.h` |

**测试适配及原因：**完整差异在备份目录`patches/`，上游原文件在`upstream/`，`migration.json`逐项记录原始/适配后SHA。

- 公共宏适配Cheshire UART、VS启用、成功/失败计数和返回码；各main只增加case执行计数。保留全部原数值输入及golden，逐文件数值token比对一致，没有删除case。成功输出缩减为最终统计，错误详情保留，避免串口打印占据大量仿真时间。
- 修正VSET未声明固定临时寄存器破坏的问题，检查实际VL；VLOAD按所提供数组元素数装载并恢复原VL，避免mask小数组被当前VL越界读取；VCMP按期望元素数真正读回寄存器，避免短VL时比较旧结果缓冲区。补实际fence及memory clobber，未改地址别名、关闭cache或删比较。
- vcpop使用标准`vcpop.m`助记符，把被写标量从input改为early-clobber output。只对这些测试关闭自动向量化/SLP和源文件LTO，防止检查代码使用被测寄存器；链接仍使用原库的LTO设置。未使用的`check_vtype_vl`漏增失败计数分支一并修正，但不宣称已动态覆盖该分支。
- 保留上游ta/ma和尾部/mask的期望值；这部分结果属于**当前Ara实现回归**，不能解释成所有RVV实现都必须保留agnostic元素。SHL-0.51和头内许可文字保留，复用现有`LICENSES/ara/LICENSE`。

**运行与判据：**新软件目录`sw/build/ara_tests_20261025/`，新硬件/运行目录`sim/work/ara_tests_20261025/`。使用现有入口新编译soc，各次串行、无波形、600秒。每次保留`command.json`、ELF哈希、`simulate.log`、`result.json`及hart轨迹；不是仅以simv=0判定。

| 用例/组 | 实测结果 |
| --- | --- |
| HelloWorld、vector_fixed | 各PASS，向量复制errors=0 |
| vadd | PASS；`ARA_DONE cases=7 checks=25 vsets=27 errors=0` |
| vl | PASS；`ARA_DONE cases=4 checks=4 vsets=4 errors=0` |
| vs | PASS；`ARA_DONE cases=4 checks=4 vsets=4 errors=0` |
| vmul | PASS；`ARA_DONE cases=4 checks=16 vsets=16 errors=0` |
| vredsum | PASS；`ARA_DONE cases=5 checks=20 vsets=20 errors=0` |
| vslideup | PASS；`ARA_DONE cases=5 checks=20 vsets=20 errors=0` |
| vcpop | PASS；`ARA_DONE cases=2 checks=8 vsets=14 errors=0` |
| vls | PASS；`ARA_DONE cases=14 checks=14 vsets=14 errors=0` |
| vss | PASS；`ARA_DONE cases=6 checks=6 vsets=6 errors=0` |
| vluxei | PASS；`ARA_DONE cases=6 checks=22 vsets=26 errors=0` |
| vsuxei | PASS；`ARA_DONE cases=2 checks=8 vsets=8 errors=0` |
| 故意错误的vadd负例 | TARGET_FAIL；errors=1、target=1、simv=0、入口1（符合预期） |
| rvv_bounds | PASS；5976项、0错误 |
| P2浮点次序 | PASS；835项、0错误，repeat=8 |
| P3 mask/异常矩阵 | PASS；753项、0错误 |
| fmatmul | PASS；数值匹配，19883周期，与此前结果一致 |


11个新用例共59个case函数、147组结果比较（不是147个向量元素）；每项`ARA_DONE`数量符合预期且errors=0。负例只在输出目录的临时C副本改错一个golden，正式源不变；确实得到errors=1、target=1、simv=0、入口1/TARGET_FAIL。18次验收运行为17 PASS及1预期负例。

另保留1次早期verbose vadd诊断运行：轨迹确认在UART输出推进，因逐比较打印耗时主动结束，未将其计为通过或死锁；随后使用精简成功输出及上述宏适配重建再测。软件首轮链接曾因整体禁LTO与既有LTO库不兼容报undefined reference；改为测试对象单独禁LTO、链接保持既有设置后通过，未更换工具链或修改库。旧失败源、命令及日志保留。

**容量/范围检查：**11个ELF均在现有64KiB链接区内，最少剩余31468字节；最大单函数静态栈帧1248字节。ROM实际传入栈顶`0x1001fff8`，11项轨迹中ELF执行区的SP与BSS均无重叠（`observed_stack.json`）；这是已执行路径观察，不是全路径栈证明。既有4项回归重建后的可装载字节与前次P1–P5版本一致。编译依赖无参考工程或`.bender`路径；986条来源哈希全部对应实际文件。保留原有RWX链接、MMIO链接符号数组边界、mmio.c符号比较以及上游vcpop常量截断告警，未通过屏蔽告警改变判据。

**并发修改保护：**本轮发现另一对话已经排版两工程的slink_rx TB及LLC Tcl，并更新正式来源清单/差异patch。经用户确认后，以最新清单追加15项并更新本轮Make/docs记录，原969项保持。1033份初始输入中1027份哈希/权限不变，另6份为本轮3份与另一轮3份（共享清单在本轮3份中）；另一轮的3份文件与其完成后快照一致。参考工程仅保留那两份排版文件未提交状态，没有将它们纳入本轮提交或回退。

**备份及恢复：**服务器`~/CheshireAra_maintenance/ara_tests_20261025/`，本地`.e01_backups/ara_tests_20261025/`。`before.tar`保留最初快照；**实际回退用`rollback_before.tar`，不能用最初来源清单覆盖后来排版记录**。`after.tar`保存最终18个文件；两个归档已实际恢复到独立目录，逐成员内容/权限核对通过，本地副本也校验。恢复步骤在两地`rollback.md`：先检查18文件仍与`source_validation.json`匹配，再恢复3旧文件、仅移除15新增源文件；发现后续变化即停止并人工合并，保留全部输出与日志，不使用reset或整目录覆盖。工作工程没有执行回退。

首批迁移完成。未扩展到第二批浮点/全部ISA、异常/MMU、ASIC/工艺验收；FS/libgcc、ROM限定告警及共享LLC原有限制不变。特殊测试/ld归档及provenance整理仍为另外两轮，未实施。

归档SHA256（两地一致）：

| 文件 | SHA256 |
| --- | --- |
| `before.tar` | `90ac8aff27b981f8c2d11b7759a9d5adeab431d53250904d98331d1c7f800097` |
| `rollback_before.tar` | `bcce328dd73bb0f68d1640482ffb7b3ab1d64ca8d52e993e211e1f763f8e4c09` |
| `after.tar` | `5a4430e0fd976f9e89ac2a9faf0bcf6d38d3faa7d8869f8df34811099bb0691c` |
| `evidence.tar.gz` | `500f3903d1937b8435f6713c34d28db89fa1b4e1b2f4ae8f4fc9b0d462f54ad9` |

证据归档含252个成员（含251项逐文件索引）；本地逐成员哈希/权限核对通过。详见[本地恢复步骤](../../../../.e01_backups/ara_tests_20261025/rollback.md)、[逐项结果](../../../../.e01_backups/ara_tests_20261025/acceptance.json)。

### 实施前规划（历史）

**以下为原规划快照：**本轮只处理用户三个议题中的第1项：选取适合正式工程的Ara测试并规划迁移/初步验证。第2项特殊测试/链接脚本归档、第3项provenance整理另轮讨论，不在此移动文件。本轮服务器仅只读；没有复制源码、构建、仿真、修改参数或升级工具。

### 输入与首批范围

2026-10-25通过Windows OpenSSH读取服务器当前实际文件。参考R为`~/CheshireAraPULP`，正式F为`~/CheshireAra`；此前P1–P5已同步，不回退到纯上游。当前Ara来源HEAD为`2895ba907e9eb14b3464609dc791a969d159a7c3`，`apps/riscv-tests`路径无本地修改；`vadd.c`在该仓库中为普通跟踪文件，不需要初始化SDK或下载子模块。正式配置仍为2 lanes、VLEN=2048，软件当前GCC入口、lp64d和Cheshire启动保持。

源码根记作A：`~/CheshireAraPULP/.bender/git/checkouts/ara-2c7b103275a16c87`。官方版本定位：[rv64uv C测试](https://github.com/pulp-platform/ara/tree/2895ba907e9eb14b3464609dc791a969d159a7c3/apps/riscv-tests/isa/rv64uv)、[公共宏](https://github.com/pulp-platform/ara/tree/2895ba907e9eb14b3464609dc791a969d159a7c3/apps/riscv-tests/isa/macros/vector)。本轮证据为服务器该锁定版本源码/Makefile的只读检查，不是对最新分支或远程PR状态的调查。

建议首批11个C文件，先运行前三个，再逐项扩展。每个文件单独生成ELF；全部为待迁移、待验证，不把静态适用判断写为已通过。

| 顺序 | 官方文件（A/apps/riscv-tests/isa/rv64uv/） | 初步检查目的 |
| --- | --- | --- |
| 1 | `vadd.c` | 整数vv/vx/vi加法、多SEW和mask；先验证公共宏/结果检查能正常工作 |
| 2–3 | `vl.c`、`vs.c` | 8/16/32/64位单位步长载入/存储，元素对齐但相对数据拍偏移的地址；与当前WT D-cache、Ara共享内存配合 |
| 4 | `vmul.c` | 整数乘法及mask，不依赖大型应用输入 |
| 5 | `vredsum.c` | 整数归约，检查多lane数据汇聚 |
| 6 | `vslideup.c` | slide数据重排及mask，与逐元素运算区别 |
| 7 | `vcpop.c` | mask计数及标量返回；与已有P2边界/并发测试互补 |
| 8–9 | `vls.c`、`vss.c` | 步长访存；逐项保留上游实际case，不宣称覆盖所有步长/边界 |
| 10–11 | `vluxei.c`、`vsuxei.c` | 索引访存及源文件已有mask场景，检查实际内存结果 |

选择依据：这些测试带确定输入/期望结果，通常比大型应用易定位失败；前三项成功后才能证明迁移适配基本可用。`vl.c/vs.c`中的`AXI_DWIDTH=128`实际用于数组字节对齐，不据变量名修改工程AXI位宽；当前测试也不能被描述为全部总线宽度组合验收。

第二批候选为`vfadd.c`、`vfmul.c`、`vfmacc.c`，不自动包含在首批11项实施中。这些源文件混有FP16/FP32/FP64段落，需单独核对当前启用精度、标量NaN-boxing、舍入和异常判据；首批继续用已有P2/P3 FP32/FP64与fmatmul回归。不能悄悄删掉FP16后宣称完整官方用例通过。`vsetvl/vsetvli/vsetivli`、分段/整寄存器/异常访存留下一批，先解决公共判据与实际VL适配。FFT/卷积/softmax等应用暂缓，避免首批引入数据生成及大容量链接问题。Cheshire适配目录内多项`mmu_stub`/寄存器stub测试不迁入；已有非stub CSR和修正后的vector_fixed不重复复制。原vector_helloworld有将向量变量作为`%s`参数的旧错误，继续使用已修正并做数据比较的正式用例。

### 拟迁入和修改的文件

- 11个C文件：从上述rv64uv路径复制到拟定`F/sw/tests/ara/rv64uv/`，保留原文件名、版权、测试case和期望常量。独立子目录用于隔离官方测试集合，不搬动现有p*.c；目录归档议题仍留第2轮。
- 公共头4个：`vector_macros.h`、`dataset.h`、`rvv_debug_macros.h`、`float_conversion.h`，从A的`apps/riscv-tests/isa/macros/vector/`迁到拟定`F/sw/deps/ara/rv64uv/`。即使首批不运行浮点，vector_macros仍包含float_conversion。首批不需要`long_array.h`或`float_macros.h`；实际预处理依赖如有额外项，先列明再最小复制。
- 复用正式工程已有`encoding.h`、printf、UART/CLINT、`cheshire_util.h`、crt0和软件库；比较官方宏所需常量与现有encoding定义，不覆盖共用头。工具链版本不升级。
- 首选已有`sw/link/spm.ld`和`common.ldh`，不新增ld。SPM链接区域当前为64KiB，需检查各ELF的text/data/bss、所有测试栈数组和ROM继承栈实际余量，不能只看链接是否成功。dataset中存在1024元素公共数组；按实际链接存活数据核对，不为塞进内存直接减小数据/删除case。放不下时该项暂缓并报告，不默默改地址图或切换dram.ld。
- 只在现有`sw/Makefile`增加显式目标，例如`ara-vadd`及可选集合`ara-tests`。与当前`ELFS/all`分开，默认`make all`保持原集合；现有direct_test宏会追加到ELFS，不能直接无区分套用。复用现有构建机制，不另造自动运行器。
- 在现有`docs/README.md`补一小节构建/运行方法和覆盖范围；在既有`provenance/source_manifest.json`等适用清单记源SHA、源路径、本地差异与新增目标。核对并保留SHL-0.51及头内NumPy许可文字，缺少许可证正文时按实际来源补入现有LICENSES目录。不新建迁移平台，不整理历史provenance。

### 已发现的适配风险与处理原则

1. **启动不是同一平台。** 官方apps使用自身runtime和链接文件，不能直接调用其Makefile：其中有工具链/Spike与生成链接脚本等路径。正式测试继续用Cheshire crt0；在各main进入/退出处最小添加UART初始化、向量启用、初始化计数及UART flush，保留原main返回失败数。官方非Spike的enable_vec/enable_fp为空，不能假定进入main时VS已就绪；沿现有初始化方式核对，不修改FS硬件或共用crt0。
2. **公共宏不是天然可靠的验收器。** 当前`check_vtype_vl`非法类型失败分支仅printf/return、漏加num_failed；虽然首批不主动选配置测试，公共适配必须记录并修正失败计数，避免以后假通过。审查首批实际展开的比较宏、调用列表、返回码及成功结束标志；不能只grep最后一行PASSED。
3. **标量/向量内存先后关系。** 官方`MEMORY_BARRIER`当前为空，正式平台需要核对现有fence语义并在所需生产/消费边界加编译器memory clobber及实际完成屏障。fence不等于清除WT D-cache旧副本；先按当前SoC一致性路径检查地址和缓存状态，不直接把所有指针改成uncached，也不为测试通过关闭cache。必要的测试端适配必须记录，不能掩盖硬件缺陷。
4. **内联汇编与编译器。** 官方Make使用其LLVM路径，而正式工程使用GCC。VSET等宏写固定t0/t1但未显式声明破坏寄存器，访存汇编也存在缺少memory描述的情况。逐项审查首批实际用到的宏/汇编，在测试局部补准确约束；禁止自动向量化和SLP向量化，避免C检查循环使用被测向量寄存器；保留当前优化级别，必要时仅这些测试禁LTO，并检查反汇编，而不是全工程改编译选项。具体追加差异以实施时编译与检查证据为准。
5. **VL、mask和tail。** 上游多个case以固定元素数比较，VSET采用ta/ma；先检查实际请求VL不被截短、每个case的实际VL与预期匹配。不要将架构允许不确定的masked/tail值当必然错误；若上游检查依赖当前实现保留值，应明确标为实现回归，或单独说明测试契约适配，不能偷偷改golden或跳过失败case。必要时只在这些测试的公共宏中加检查计数/实际VL检查，不新增通用框架。

这些是静态检查发现的迁移风险，**不表示已在正式工程复现硬件缺陷**。源码适配和ISA/硬件修复必须分开报告。

### 实施顺序、验证和回退（另行授权）

1. 重新检查F和输入源码现状，备份将改动的Makefile/说明/来源清单；保存SHA、权限、新增文件清单及上游原文件。备份放工程外，并保留本地副本，不覆盖P1–P5备份，不新增F Git仓库作为隐含前提。
2. 首先只迁入公共依赖和`vadd/vl/vs`。静态检查依赖、汇编约束、case数量和链接容量；构建到新的`sw/build/ara_tests_<日期>/`。复用经源码/配置/编译输入确认匹配的既有soc仿真器；不能确认匹配才用现有入口新建硬件输出，不修改RTL/TB。
3. 先跑既有HelloWorld和vector_fixed确认入口，再串行运行这3个新ELF。程序必须进入并完成全部计划case，真实读回数据匹配；UART无FAILED/ERROR、目标0、simv0、入口PASS、无未解释断言，才能标通过。
4. 针对一个明确比较点，在独立临时测试副本中故意改错一个期望值；必须出现失败计数、非零目标返回和入口失败。保留负例证据；正式迁入源仍保留正确golden。若旧宏漏报则先修测试判据，不能将其误报成硬件通过。
5. 上述通过后逐项迁入并运行其余8个C用例；每个ELF独立记录源哈希、软件命令、运行命令、实际case/检查数、输出、simv身份和结果，不能用前3个通过推断全套通过。普通运行无波形，每例默认600秒；失败先保留证据并诊断测试/平台适配，授权内做最小测试修正。需要改生产RTL/架构、工具链或覆盖范围时暂停该项报告，不扩大为P1–P5之外的新修复。
6. 完成后复跑已有`rvv_bounds`、`p2_vmfpu_order`、`p3_mask_matrix`和`fmatmul`，确认原软件入口及关键向量回归保持。若全部一次成功，计划18次运行：2基线＋11新增＋1预期负例＋4回归；失败重试另记，不承诺尚未实测的耗时/通过数。
7. 核查正式工程不依赖R路径、Bender、网络下载或上游runtime；默认all集合未改变。交付逐项状态（通过/失败/未执行/不适用）、实际覆盖、完整差异与恢复命令。回退先确认没有后续并发修改，再恢复本轮修改的旧文件和仅本轮新增文件；保留所有日志和失败源，不执行reset/批量清理。

初步通过只代表这些官方case在当前2-lane/VLEN2048平台适配后通过。尚未覆盖所有指令、LMUL、tail/mask策略、异常恢复、地址翻译、全部浮点格式或工艺实现；fmatmul回归也不能替代ISA覆盖。后续按缺口再扩充，不一次迁入整个apps。

**原待授权事项已被用户“开始实施”取代；实施限首批11项，不开始第2/3轮目录整理。**


2026-10-24 P1–P5同步完成：R先完成48次验证并推送GitHub `5986ba02`，F随后按映射同步并独立完成41次测试，39项共同用例与R一致。前后源码、两地备份及恢复核对齐备，集中配置/wrapper/静态入口与既有限制保持。见[结果与回退](official_upstream_maintenance_assessment.md#reference-formal-sync-20261024)。本轮完成停止，下方“未写回/待授权”为历史。

2026-10-23 P3–P5修复与累计回归完成：按用户要求对范围内失败继续定位修复，隔离C的P3 SIMD异常标志、P4相邻段覆盖及P5 RTL/HAL均验证通过。累计7次新运行为6 PASS及SPI原padding限定告警接受，同版本3项DMA回归通过；最终`p1-p5-pass=5e0f973…`及双份源码/证据已校验，R/F保护核对保持。详见[实测、版本与恢复](official_upstream_maintenance_assessment.md#p3-p5-repair-20261023)。阶段B完成并停止，未写回R/F，阶段C仍需单独授权；下方为历史记录。

2026-10-23 P2定位与局部修复已完成：隔离C中分别修复mask尾位计数和共享标量返回条件，原835项、补充124/483项及五项回归全部通过。`p2-pass`=`7ac2e12…`及两地源码/证据备份已保存并校验，R/F保护核对不变。详见[原因、逐步结果及恢复命令](official_upstream_maintenance_assessment.md#p2-repair-20261023)。本轮停止，P3–P5及全组累计回归未继续，正式同步仍需阶段C授权；下方停止记录为历史。

2026-10-23 P1–P5维护阶段B历史停止记录：隔离候选中P1定向及向量/RVV回归通过；P2官方修改后仍31项检查不符，未标通过，P3–P5及累计回归未执行。双份Git备份与首次恢复校验完成，R/F保持，未授权正式同步。完整版本、结果与回退见[阶段B实测记录](official_upstream_maintenance_assessment.md#p1-p5-stage-b-stop-20261023)；下条“等待B授权”为历史阶段A状态。

2026-10-23 官方后续维护阶段A完成：只读核对两工程实际源码/配置、26依赖及962条活动来源记录，调查官方diff与后续问题；候选分类、最小回移、参考副本验证→正式工程同步的分阶段计划见[官方后续维护评估](official_upstream_maintenance_assessment.md)。优先候选为Ara #481/#482、MVP #18及iDMA一维提交修复；FS/SLINK候选的残留风险单列。**本轮未修改服务器、升级依赖、构建或测试；交付后停止，等待选择候选及阶段B授权。** 既有版本、配置合并和限制保持。

2026-10-22 最新配置入口：独立固定配置包已合入 `cheshire_pkg.sv`，只有 `DefaultCfg.Ara` 默认0→1、有效值保持1；改动、恢复关联项和14次前后对照见[第7.12节](#config-entry-merge-defaults-20261022)。下方原配置包结构及验收记录为合并前事实，不再作为当前活动入口。

**2026-10-22 compile/start入口简化已完成：**按用户新要求恢复Bash启动、输出复用WARNING和可读脚本，软件仍单独Make；10次串行仿真分类符合预期，静态/依赖/范围检查通过。原run.py及强制新目录规则被本次决定替代。见[第7.11节](#entry-scripts-result-20261022)；以下保留此前阶段快照。

**2026-10-22 独立工程用户文档阶段B已完成：**用户明确“开始实施”后，在服务器`~/CheshireAra/docs/`写入两份指南，仅调整根README导航和现有来源清单；最终文件的命令语法、链接、配置/判据及修改范围检查通过，未构建或仿真。入口和交付结果见[第7.10节](#user-documentation-result-20261022)。本阶段交付后停止，不主动优化流程或脚本。下条为阶段A记录。

**2026-10-22 独立工程用户文档：阶段A规划与只读核查完成。** 建议两份用户文档，准确路径、章节依据、现有流程限制及阶段B检查见[第7.9节](#user-documentation-plan-20261022)。本轮仅更新本地既有计划和交接；未创建服务器`docs/`、写服务器文件、构建或运行仿真，等待用户明确同意撰写。

**2026-10-22 验证后清理已完成：**正式工作区保留 `~/CheshireAra`；搬迁副本和旧输出已移除，必要证据压缩到 `~/CheshireAra_validation_archive_20261022/`。下文2B–2D路径是验收时位置，现按归档内同名目录前缀定位；见[第7.8节](#post-validation-cleanup-20261022)。

**2026-10-22 步骤2D完成，独立提取及搬迁验证结束。** 在 `~/CheshireAra_relocated_2d_20261022` 从新输出重建四种硬件、软件和镜像，31项对照保持基准分类；实际构建/运行不调用Bender、不下载依赖、不读取旧工程源码或缓存。保留`run.py`、ROM限定告警和三项LLC失败；服务器正常联网及VCS既有许可通信无需另行确认。结果见[第7.7节](#step2d-result-20261022)，工程仍在 `~/CheshireAra`。本阶段完成后停止；以下是此前阶段记录。

**2026-10-22 步骤2C历史记录：当时完成软件重建。** 新工程内已从源码重建23单元库、17个ELF和SPI raw/memh；19次串行新软件对照完成：13项正常PASS、SPI限定告警功能接受、2项故意负例判定正确、3项LLC已知失败保持。硬件/原ROM及参考工程保持；结果见[第7.6节](#step2c-result-20261022)。**停止等待2D授权**；搬迁及实际文件访问验证尚未执行。

**2026-10-21 步骤2B历史记录：当时完成硬件提取。** 已在服务器 `~/CheshireAra` 提取硬件及最小仿真配套，用集中配置/共同wrapper和静态分组清单从新输出目录构建，未调用Bender。31次串行对照中25项正常通过，SPI按原限定告警接受功能结果，2项故意失败/超时判定正确，3项LLC旧失败保持；具体范围与证据见[第7.5节](#step2b-result-20261021)。参考工程及原产物保护检查通过。软件仍复用参考ELF/镜像，**停止等待2C授权**；2D搬迁独立性验证尚未执行。

**2026-10-21 步骤2A历史记录：规划与只读核查完成，当时未开始提取。** 步骤 1 的现有结果及已声明限制已被用户接受为提取对照基准；不要求先修完所有历史问题。当前阶段表见[第 7 节](#step2-plan)，取代下方旧阶段编号及“全部无缺陷后才可规划”的门槛。下一步为用户明确授权 **2B**，不是重新获取参考工程。

2A轮由本地 Agent 经 WSL SSH 只读检查；用户补充允许本地子 Agent 后，分别核查 RTL/配置、软件/启动、仿真/验收，主 Agent 统一写文档。未委派服务器 Agent，未创建目标工程、复制源码、运行 Bender、构建、仿真或修改服务器文件。旧日志、ROM 限定告警和 DMA 共享 LLC 失败记录保持。

2026-10-20 历史进展：用户已授权本地 Agent 执行服务器 DMA/向量 HelloWorld 疑点测试，现已完成，见[控制接口测试](../reports/reference_rebuild_check.md#dma-vector-tests-20261020)。向量修正副本 22 字节比较通过；DMA 原小用例数据通过，但确认控制寄存器返回位置及 64 位写入问题，且目标失败未传播为主机非零退出。原 RTL/驱动、参数及旧产物未改，修复未实施，提取未开始。E01 暂不交给服务器 Agent。

2026-10-20 测试前决定与记录：第 1 步“梳理现有测试”已完成，结果见[第 6.1 节](#existing-test-inventory)，与历史“第 1 步工具链检查”不同。**stub 测试标记“勿用”，不纳入后续测试，不再安排去除 stub 后复用。** 当时将 DMA 截位解释保留为待验证假设并准备[第 6.3 节](#dma-vector-reference-check)；该准备任务现已执行，以页首实际结果替代此前“尚未复现”的状态。

2026-10-20 协作口径同步：用户已确认 Cheshire SoC 由本地统筹、服务器按明确任务自主实施，详见[根约定](../../../../AGENTS.md#local-server-collaboration)及[最小任务格式](../../../AGENT_TASKS.md#server-task-brief)。任务可含完整小闭环，不逐条命令请示；具体修改范围和运行权限仍须由任务说明确定。此前“把部分参考验收移至提取对照阶段”的建议尚未获接受，第 6—7 节验收要求与先参考验收、后提取的顺序不因此改变。本次只同步文档，不授权复跑、提取、配置修改或清理。

分步命令与简要解释见[同版本重建速查](server_reference_rebuild_guide.md)；实际执行结果及未关闭项见 [E01 最新交接](../../../handoffs/E01_fixed_vector_extraction.md)。下文第 2–3 节和历史阶段中的“尚未编译、等待第 2 步”等是当时快照；现行基准查[报告第 12 节](../reports/reference_rebuild_check.md#remaining-acceptance-20261021)及其引用章节；2B实际提取结果见[第7.5节](#step2b-result-20261021)。

**2026-10-19 用户确认的配置管理更新：**固定 CVA6＋Ara 功能组合，在 `src/config/` 集中维护参数，每次构建选择一个有效配置；先保持 2 lanes/VLEN 2048 及原 Cache/LLC 基线完成提取对照，再逐步开放参数，以应用验证和面积、时序、功耗评估确定产品配置。原“长期只用一个固定参数配置”的限制被替代，具体候选值和支持组合尚未验收。本次只同步文档，未改参数、提取工程或执行试验。规范见 [02 第 3.3 节](../../../02_Cheshire_Ara_ASIC_Extraction_Handoff.md#parameter-policy)，评估方法见[资源指南 Q7/Q8](../../../engineering/Fixed_Vector_SoC_Resource_Guide.md#q7)。

2026-10-18 用户补充“如无必要、勿增实体”：优先直接使用官方入口，不为记录或预防假设故障新增通用框架。下文原先要求的独立 SV/DPI 前置探针改为按需诊断，先由参考工程实际构建检验许可和联编；既定日志、超时及功能验收要求保留。

更新：2026-10-18。输入：`mp/ara-pulp-v2` / `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`。本轮完成只读调查和方案，**未复制工程、未编译、未展开、未仿真**。

同日实施增量：用户已确认并完成第1步，见[实际报告](../reports/toolchain_preflight.md)。工具链最小编译/链接已执行，发现并保留libgcc特定高地址重定位限制；未执行VCS或目标程序。下文只读调查表保留为阶段0快照，不能替代实际报告。第2步等待确认。

同日用户调整来源：明确不复制本地官方工程，希望从 GitHub 官方仓库重建，并要求先分析两种方案。**原第2步“复制本地快照”已被替代，不能继续照旧执行。** 目前仅完成来源方案比较（第8节）；官方具体提交、依赖组合及环境配方尚未冻结，未授权直接采用最新主线或重建/升级工具链。第4节原复制流程保留为旧方案依据，不再是待执行动作。

同日进一步澄清（当前有效）：用户明确重建当初克隆的 **`mp/ara-pulp-v2` 同版本**，不重新选新版官方工程。按本地Git历史定位，原始上游基准为 `e040b7bbc7851a37faff3c4657ff8d656cc6e20a`，配套依赖沿该提交锁文件；服务器负责重新获取、搭建环境和构建。本地后加修改逐项对照，不自动回放。上段“版本待选”由本澄清取代；剩余工作是核对该历史提交的官方可获取性和服务器环境，不再评选最新主线。此澄清未启动第2步下载/构建。

历史人工把关要求为“先规划，每一步报告后等待确认”，曾取代原提示词前半段的连续实施授权。2026-10-19 用户进一步确认以明确任务为授权单位：任务内自主实施常规细节，完成或遇到越界时回报，不逐条命令请示。参数探索仍限于已确认的具体试验范围；超出范围、改变架构、触及受保护对象或无法消解的冲突须反馈。此澄清不改变验收顺序，本文更新本身不构成工程任务授权。

## 1. 输入、目标与保护范围

| 对象 | 2026-10-21 步骤 2A 实际核查 |
| --- | --- |
| 本地输入 | `/home/zhaowenyao/RISC_CVA6_prj/cheshire_ara`，HEAD=`c9abbb48946fe3a7244bfb3159919b7c9731cb59`；已有多份文档修改及未跟踪图稿/证据，保留原内容 |
| 参考工程 | `zhaowy24@172.16.0.243:/home/zhaowy24/CheshireAraPULP`，HEAD=`e040b7bbc7851a37faff3c4657ff8d656cc6e20a`，已重建且有实际源码修正、生成文件和测试产物 |
| 固定工程 | `/home/zhaowy24/CheshireAra` 存在且为空；2B 前再查，不覆盖后续出现的未知文件，不再嵌套 `cheshire_ara_asic/` |
| 只读参考 | `/home/zhaowy24/Desktop/mycheshire_24`；不在其目录内构建、修改或清理 |
| 首次提取边界 | 保留地址、中断、外设、LLC/SPM、原子路径和既有 Boot ROM；不实施 v1 产品新增 IP、外设裁切、真实 DDR/工艺宏 |

参考工程及 `.bender`、全部旧产物、本地 FPGA/RTL/sw、TTY 和 `/opt` 均受保护。步骤 2 的新源码与输出只写获授权的新工程位置，不再向参考工程追加提取产物。目标出现未知内容时先核对归属，不覆盖、删除或改名消除冲突。

服务器实际来源记录是根 `Bender.lock`/`Bender.yml`、各依赖 Git HEAD/diff 和既有修正记录；**没有**本地快照机制的 `Bender.local`、`.bender/SNAPSHOT.tsv`、`.bender/UPSTREAM.lock`。26 个依赖 HEAD 均与服务器锁文件相符，锁文件不能替代当前磁盘内容。主要记录值：

| 组件 | 上游来源记录 |
| --- | --- |
| Ara | `2895ba907e9eb14b3464609dc791a969d159a7c3` |
| CVA6 | `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c` |
| AXI | `39f5f2d51c5e524f6fc5cf8b6e901f7dcc5622d7` |
| LLC | `559bcbd09a5a884dbe31e2d72fd95d024e357f39` |
| 原子适配器 | `0ac3a78fe342c5a5b9b10bff49d58897f773059e` |
| iDMA | `c12caf59bb482fe44b27361f6924ad346b2d22fe`，另保留实际 #80/#204 回移 |
| 根软件 printf 子模块 | 服务器实际展开为 `0dd4b64bc778bf55229428cefccba4c0a81f384b` |

根 `sw/deps/cva6-sdk` 未初始化，本次裸机提取不迁 Linux SDK 或无关 benchmark。必须保留服务器 FS、DMA wrapper/HAL、CVA6 两份 WT 读断言、iDMA 36 文件回移，以及 axi_rt、clint、OpenTitan PLIC、serial_link 的实际生成差异；不能以 `git archive` 固定提交替代它们。现有根 diff 与最近验收的 `root_after.diff` 一致；339 项保护输入、26 项最终验收输入、15 项测试产物及 iDMA 36 项部署哈希均与当前文件匹配。

已验证构建位于 `_e01/dma_vector_check/pr80_204_20261021/production_build/`：`build_commands.json` 记录编译/展开均返回 0；`compile.cheshire_soc.sh` 有 **66 组、716 个不重复源文件、18 个 include 目录**，路径均存在，`compile.log` 的解析顺序与之完全一致。唯一向量 profile、Ara 真实 decoder、`ARA/NR_LANES=2/VLEN=2048` 及各组宏/include 已核对。`AN.DB/make.vlogan` 少记没有数据库单元的 deprecated `sram.sv`，不能据此删源；以分组脚本和完整编译日志为依据。716 是筛选输入上界，不是最终精简文件数。

参考 simv SHA256=`e16fc6a78f7f37ec27c7324b8732e643876249f2636cd05190e4280b15e00dfd`；与 `_e01/remaining_acceptance_20261021/` 的实际绑定一致。本轮只核查记录和文件，没有重跑。原六项 SoC DMA/HAL 回归实际使用补丁副本 `rtl_build/simv`（`e31ce939…`）；正式路径版本另有 HelloWorld、第 9/12 节结果，二者不能混记。

## 2. 服务器和 TTY 的实际情况

只读 SSH 成功；系统为 x86_64、EL8 内核。`/home` 约 36 TiB 可用，64 个逻辑 CPU；容量只是本次查询快照，不据此占满机器。`vcs -full64 -ID` 本轮退出 0，返回 `VCS W-2024.09-SP1_Full64`。未测试许可证 checkout 或实际编译。

TTY 目录为：

```text
mycheshire_24/
  src/filelist.f
  src/cheshire_soc/<component>/
  src/tb/{src,models}/
  sim/{scripts,work,log}/
  sw/tests/
```

实际检查所得：

- `src/filelist.f` 为 308 个不重复源码条目、12 个 include 目录，从 `sim/work` 解析均存在；这只是路径检查。
- 第 177 行为 `cv64a6_imafdchsclic_sv39_wb_config_pkg.sv`，无 Ara 源码/宏；TB 默认 `SelectedCfg=0`。
- TTY 的配置 3 是 **vCLIC**；本地当前源码的配置 3 才是 **Ara**。不能把两者的 SELCFG 数字互用。
- `compile.sh`、`sim.sh`、`verdi.sh` 写死 `/home/dell/Desktop/test/mycheshire_24`，与本次登录位置不同。前者含 `-full64`、本机 C++/DPI、`-j4`、`-fgp` 和较重调试选项；后者固定旧 ELF 和 Serial Link preload，管道没有可靠失败传播。
- TTY TB 强制调用 FSDB dump；不把 Verdi/FSDB 作为首轮批处理必需项。其 TB/SoC 源与本地有差别，不能整套复制后视为当前源码参考。
- `sw/` 检查到测试源码和已有 ELF/dump，没有完整启动、链接、运行库构建目录；已有 `simv`、日志、波形、ELF 均不作为本轮验证证据。

借鉴的是目录约定与 VCS/DPI 流程。新脚本须自行定位根目录，显式设置输出、编译组、工具路径、超时、退出码与结果判据；不直接复用 TTY 的绝对路径、标量清单和现成 TB。

## 3. 工具链结论及待执行检查

| 类别 | 已只读核实 | 当前结论 |
| --- | --- | --- |
| RISC-V 编译器 | `/opt/riscv/bin/riscv64-unknown-elf-gcc`，13.2.0 (`gc891d8dc23e`)，triple `riscv64-unknown-elf` | 首选待测候选；尚未实际编译 |
| ISA/ABI 默认 | `-Q --help=target`：`rv64imafdc_zicsr_zifencei`、`lp64d`，默认 code model 为 medlow | 工程显式指定 ISA/ABI；软件按当前入口使用 medany |
| 汇编器/链接器 | GNU as/ld 2.43.1；已查询 GCC 实际选择的工具路径 | 指令与重定位能力待最小测试 |
| 运行库/multilib | `-print-multi-lib` 仅 `.;`；libc.a、libgcc.a、newlib.h、riscv_vector.h 存在 | 一个 multilib 不直接说明 RVV 缺失；须实链两组 ISA 并核查实际库 |
| 服务器本机 C/C++ | PATH 为 `/opt/rh/gcc-toolset-13/root/usr/bin/{gcc,g++}` 13.3.1，triple `x86_64-redhat-linux`；`/usr/bin/gcc` 为 8.5.0 | 与 RISC-V 工具链分开；DPI 编译、VCS 联编和动态库兼容待验证 |
| 其他工具 | make 4.2.1、默认 Python 3.6.8、另有 `/usr/bin/python3.9` 3.9.25、python3.11 3.11.13、python3.12 3.12.14；rsync 3.1.3、Bender 0.32.1、timeout 可用，rg 不在远端 PATH | 官方 `docs/gs.md` 要求 Python >=3.9；必要生成步骤显式选现有 python3.9 并检查 requirements，不能沿用默认 python3。Python 包尚未验证，不升级系统 |

当前本地根软件 ISA 为 `rv64gc_zifencei`，Ara Cheshire 软件入口改为 `rv64gcv_zifencei`，ABI 均为 `lp64d`。ISA 与调用约定分别明确指定；其含义参见 [GCC 13.2 官方选项](https://gcc.gnu.org/onlinedocs/gcc-13.2.0/gcc/RISC-V-Options.html)。现有标量运行库是否可用于本次向量软件，最终以实际链接输入、反汇编和目标运行确认。

Ara README 声明 RVV 1.0，实际 dispatcher 含 vma/vta 和 vsetivli；同目录旧 DEPENDENCIES.md 仍提 0.9，存在文档冲突。采用当前 README、实际 RTL 和 Cheshire 集成入口的 1.0 路线，不据旧说明安装 0.9 工具链。Ara 独立 apps 的 LLVM 建议不等同于本轮必须构建全部 apps/LLVM。

下一步的最小探针：

1. 分别以 `-march=rv64gc_zifencei`、`-march=rv64gcv_zifencei`，`-mabi=lp64d -mcmodel=medany` 查询库选择，编译 `.S`/C、链接并生成 map、`readelf` 和 `objdump`。标量覆盖基本整数、浮点及原子指令；向量覆盖 vsetvli/vsetivli、整数 load/add/store 和一个简单浮点向量操作。用明确的运算引用检查 libc/libgcc 的实际解析，不能只看库文件存在。
2. 区分裸指令探针与完整启动/运行库：探针通过后，在参考源码到位时，用现行 crt0、common.ldh、spm/rom/dram 链接布局及必要 libcheshire 源重建小程序；不运行 Linux 或整套 benchmark。
   `common.ldh` 会丢弃最终 ELF 的 `.riscv.attributes`；ISA 属性同时检查中间 `.o`，最终 ELF 检查实际指令。软件 SPM 链接窗口为 64 KiB，硬件 LLC/SPM 为 128 KiB，两者不混同。
3. 服务器本机 C++ 编译简单程序以及复制的 `elfloader.cpp`，使用实际 VCS `svdpi.h`；后续小型 SV/DPI 运行才验证 VCS 联编与许可。不能用交叉编译器生成宿主 DPI。
4. 保存每条命令、版本、输入 SHA256、退出码、输出和失败日志。不适配时先报告具体汇编、ABI、重定位、runtime 或 intrinsic 缺项；不覆盖 `/opt`，不自动安装新工具。

## 4. 参考工程重建与固定配置

当前本地 [官方仿真说明](../../../../docs/tg/sim.md) 明列 VCS >=2024.09。Ara `cheshire/Makefile:29,60–62` 提供向量 targets/defines，并调用根 VCS 清单生成；根 `cheshire.mk:158–160` 使用 `bender script vcs`。官方 VCS start 已有 `-full64` 和 ELF DPI。这是存在官方入口的源码证据，尚非本组合运行证据。

原本地快照复制方案（历史，已被第 8 节同版本 GitHub 重建方向替代；以下 1—6 条不作为当前执行步骤）：

1. 在本地建立输入清单，复制当前磁盘的必要官方目录、26 项硬件依赖快照、已展开的必要软件子模块、include、现有生成 RTL/头文件、模型及许可证。保留来源结构；传输前后 SHA256 比对。不使用 `git archive HEAD` 丢失实际子模块或工作树内容，也不复制旧构建输出来充当新验证。
2. 参考根保留 `Makefile`、`cheshire.mk`、`hw/`、`sw/`、`target/`、`.bender/` 和 Bender 来源文件。版本元数据、纳入/排除清单及差异放 `_e01/provenance/`；不复制凭据、Git 对象库、FPGA/EDA 缓存、旧 ELF/库/波形。可选 Linux/benchmark 大数据排除项逐项记录，不声称复制了完整 SDK。
3. 在新参考目录内用 Bender 本地模式受控导出一次正确向量清单；同时归档 VCS 分组清单和结构化信息。不更新依赖、不下载。若必要路径缺失，停止该导出并报告，按 02 规格有限回退，不修整个旧管理系统。
4. 采用官方支持的 `sim/test` 目标及 Ara targets：`rtl cva6 cv64a6_imafdcv_sv39 exclude_first_pass_decoder`，宏 `ARA NR_LANES=2 VLEN=2048`。实际命令按已安装 Bender 的帮助和官方 recipe 确认，明确 `vlogan`/`vcs` 均使用 64 位模式。
5. 不直接跑 `make all`/`ara-chs-all`。根 make 在 `.chs_deps` 缺失时可能触发 checkout/submodule，模型规则可能下载；这些入口先限定依赖/生成步骤。归档原入口；仅在新目录补必要的离线构建包装和最小兼容修改。
6. 本地现成 `compile.cheshire_soc.sh` 含旧绝对路径、标量 profile、两份 decoder，不能直接运行。官方 start 的参数传递须经实际展开核验，管道退出状态由受控包装保证；把本次适配与官方原件区别记录。首次保留已生成的 ROM/寄存器 RTL；如确需重生成，先验证解释器与对应包，不因主机存在 Python 就认定官方生成器可运行。

当前参考来源为服务器 `~/CheshireAraPULP` 的官方历史版本重建及已记录的必要修正，提取目标为 `~/CheshireAra`。本地副本用于差异审查，不直接回放到参考工程；重建入口及实测状态分别查重建速查和最新交接。后续提取仍遵守保护、离线独立和来源记录要求。

首次提取对照的基线值保持，后续参数试验不覆盖这份基线记录：

| 项目 | 参考 / 固定工程共同基线 |
| --- | --- |
| CPU | `cv64a6_imafdcv_sv39`，RVV=1，WT D-cache |
| SoC/Ara | 当前 `gen_cheshire_ara_cfg()`：Ara=1、2 lanes、VLEN=2048 |
| decoder | Ara 真实 `cva6_accel_first_pass_decoder`；排除 CVA6 同名 stub |
| LLC/SPM | 8 ways × 256 lines × 8 blocks × 8 bytes = 128 KiB，保留原子适配和 Boot ROM 初始化 |
| 其余 | 完整 DefaultCfg 实际快照；48-bit 地址、64-bit AXI、RTC=32768、PlatformRom=0，地址/IRQ/外设不重排 |
| 验证模型 | `UseDramSys=0`，沿现有 AXI memory model；不是 DDR Controller/PHY 验证 |

CPU profile 的 `VLEN=64` 是另一字段，保持原值；不能按 Ara VLEN 修改。参考 TB 的 `SelectedCfg=3` 只选 SoC，仍须独立选择 CPU profile。展开时打印/断言 CPU RVV、SoC Ara、lane/VLEN、LLC容量与派生位宽，证明实际选中了目标组合。

提取工程在 `src/config/` 集中保存唯一向量 CPU profile 副本、完整 SoC 配置包及参数说明；每次构建导出一个确定配置。沿用 `gen_cva6_cfg()`、`build_config()`、`CHESHIRE_TYPEDEF_ALL` 等配置和类型派生；仿真 fixture 与后续综合共同使用该配置和 wrapper，TB 不再用 `SELCFG` 或私有字段改写硬件配置，不重写底层参数化 IP。

保持可复现基线和各候选的有效配置快照，编译输出按配置隔离、测试输出按运行隔离，避免复用另一配置的 `simv`。首次对照完成后，先开放 L1 容量和 LLC 行数，再按瓶颈评估预测器/TLB/队列/VLEN；lane、Cache 路数/行长、总线宽度或 Cache 类型单独评估。候选值不等于支持列表，分别记录静态约束、定向测试和完整候选回归状态。宏按实际消费者核查，不能仅修改 `NR_LANES/VLEN` 就认定当前 Cheshire 的 `Cfg.AraNrLanes/AraVLEN` 已改变。

## 5. 当前最小目录与配置（步骤 2A 更新）

```text
~/CheshireAra/
  README.md
  src/
    config/
      cheshire_pkg.sv                 # 原包的提取副本，保留类型、默认值、地址及派生函数
      cv64a6_imafdcv_sv39_config_pkg.sv # 唯一向量 profile，CPU VLEN=64 保持
      cheshire_ara_asic_cfg_pkg.sv     # 唯一有效 SoC 配置和类型出口
      README.md                       # 基线实际值、覆盖关系及支持范围
    top/cheshire_ara_asic_soc.sv
    cheshire_soc/cheshire_top/        # Cheshire 源码/include/现有生成 ROM
    cheshire_soc/<component>/        # 必要组件及通用技术单元，保留相对 include 结构
    tb/                              # 所选 TB、VIP、DPI、模型及回归输入
  sim/scripts/                       # 静态分组编译入口、既有运行判定的最小适配
  sim/reference_inputs/              # 2B 指定参考 ELF/镜像，明确仅作对照输入
  sim/work/                          # 实施时生成，构建和每例运行分别用新目录
  sw/                                # 2C 已迁启动/链接/库/头/测试及 Make 入口
  provenance/                        # 来源清单、原清单/锁文件、差异和生成资料
  LICENSES/
```

此示意不是必须创建的空目录清单；不建尚未使用的 `tech/asic`、`constraints`、`synth.f` 或综合流程。当前通用技术单元仍在原组件目录，来源清单注明用途。未来综合复用同一 SoC wrapper/配置，但工艺映射与综合验收另行授权。

配置只做来源集中：将服务器 `cheshire_pkg.sv` 的提取副本放入 `src/config/` 且保持实现，参考原件不移动；固定包在冻结的 `DefaultCfg` 上设置 `Ara=1`，2 lanes/2048 已是该包实际值，不再手抄另一套输入。继续经 `gen_cva6_cfg()`、`build_config()`、`CHESHIRE_TYPEDEF_ALL` 派生；例如 CPU profile 的 PMP=8 实际被 SoC 配置覆盖为 0，说明文档记录最终消费者和有效值。fixture/VIP 使用同一有效配置，fixture 改接共同 wrapper，不再用 TB 私有 `SelectedCfg` 改写硬件；参考值 3 留在对照记录，`UseDramSys=0` 保持。

**清单只维护一份。** 优先将现有 `compile.cheshire_soc.sh` 改路径并筛选为新工程的静态分组清单/编译入口，继续显式逐组调用 `vlogan`，复用已验证的 VCS 展开命令；不为 66 组另造 66 个配置文件，也不维护一份重复扁平 `filelist.f`。保留顺序、语言选项、各组宏和 include 作用域，禁止递归通配符。数值宏在 2B 按保留源码的实际消费者处理：无消费者的冗余宏可去除，有消费者则引用唯一配置输入，不能另留一套可独立修改的 lane/VLEN。此处调整清单表达方式，不改变静态、离线、可追溯要求。

保留功能 RTL 的参数化实现及必要 package/include/生成文件/技术单元分支；只排除与所选 SoC/回归无关的独立测试、其他 profile、stub、FPGA 包装和旧产物，不按一次展开的活跃模块裁切硬件。`idma_generated.sv` 按原编译单元保留，不与组成文件重复编译。来源清单记录原/新路径、组件版本、原/新 SHA256、用途/分组、许可证及改动原因；以后超出已声明支持范围时另查依赖与验证，不恢复日常 Bender 管理。

## 6. V01 验收用例和证据

第 6.1 节保留 2026-10-20 测试梳理快照，其中“待修/尚缺”不代表当前仍未执行。后续实际结果以[报告第 8–12 节](../reports/reference_rebuild_check.md#dma-pr80-204-20261021)为准；本次选用项及限定告警处理见[第 7.3 节](#step2-tests)。stub 继续勿用。

<a id="existing-test-inventory"></a>

### 6.1 第 1 步：梳理现有测试（2026-10-20 已完成）

**输入与检查范围。** 提取来源仍是服务器重建参考工程 `~/CheshireAraPULP`，不是本地修改版。本次用本地 Git 中的 Cheshire `e040b7bbc7851a37faff3c4657ff8d656cc6e20a`、Ara `2895ba907e9eb14b3464609dc791a969d159a7c3` 原始文件检查测试内容；配套 CVA6 为 `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c`。工作区 HEAD 为 `c9abbb48946fe3a7244bfb3159919b7c9731cb59`；本地 Ara 有修改，因而通过 `git show <提交>:<文件>` 读取原版，未将本地修正当成服务器输入。本轮未核查服务器当前文件，执行测试前仍须核对实际输入与已保留的 FS 修正。

沿该版本官方软件入口，共有 **25 个 C/汇编测试入口**：Cheshire `sw/tests/` 下 7 个，Ara `cheshire/sw/src/` 及其 `tests/` 下 18 个；5 个 `.body` 是被包含的测试正文，不重复计数。Ara Makefile 将这 18 个入口复制到 Cheshire 软件目录构建；“构建全部”并不筛选硬件适用性，也不等于执行全部。这里不把 Ara 独立平台的 `apps/`、CVA6 独立验证环境或 SDK 自动纳入 SoC 验收。本地另加的 `fmatmul_test_4x4.c`、`mnist_mlp_cpu.dram.c` 不属于上述固定参考版本，首次不自动带入。

**配置依据。** `target/sim/src/tb_cheshire_pkg.sv` 的配置 3 在 `DefaultCfg` 上开启 Ara、2 lanes、VLEN=2048；`hw/cheshire_pkg.sv` 保持 DMA/二维 DMA 开启、AXI-RT/CLIC 关闭。CPU 仍须选择 `cv64a6_imafdcv_sv39`，不能由配置 3 推断。`hw/cheshire_soc.sv` 使用 `OSSupport=1` 的 Ara 与 CVA6 实际请求/响应连接；寄存器描述与头文件没有下述 MMU stub 控制寄存器。相关本地硬件配置、SoC、寄存器文件相对 Cheshire 固定提交无差异。

下表“纳入”仅表示功能和测试目的适用，**不表示本轮已编译或通过**。后续运行共用判据：程序完成所列检查且目标返回 0，TB 报成功，无超时或未解释的错误；主机退出状态另行记录，不能只看打印字符串。`PRINTF`、`EEW`、链接模式属于实际测试输入，沿现有入口明确选择。

2026-10-20 用户明确停用 stub 测试后，25 个入口按 **4 个纳入计划、1 个待修正、15 个勿用、5 个配置不适用**维护。原“4/8/13”是初次梳理分类，由本次决定取代。`rvv_test_exceptions.c` 原版也执行 stub 初始化写入，随该组停用；不访问 stub 的 `rvv_test_vstart_csrs.c` 保留。

**可纳入测试计划：4 个。**

| 入口 | 检查内容与通过判据 | 限制/待处理事项 |
| --- | --- | --- |
| `helloworld.c` | 标量启动、CLINT 计时和 UART；输出 `Hello World!` 并返回 0 | 来自 Cheshire；不能单凭输出证明所有 ROM 初始化细节或 SPI 自主启动 |
| `dma_2d.spm.c` | SPM 非缓存别名上的二维 DMA 拷贝；逐字节匹配原用例金值（含结尾保护字符），错误计数为 0 | 保留测试。2026-10-20 原版 38 字节比较通过；诊断确认 CPU ID 读成 0、64 位配置写丢高半部，控制路径尚待修复，不能据原版通过关闭 DMA 问题。详见第 6.3 节 |
| `fmatmul.c` | 默认 32×32 双精度向量矩阵乘法与标量结果比较；执行验证分支并打印 `Passed.`、返回 0 | 来自 Ara；保留已确认 FS 修正。单尺寸、单组输入及现有容差比较，不能代替完整 VL/尾部检查 |
| `rvv_test_vstart_csrs.c` | RVV 开启、CSR 读及状态设置不异常；写只读 `vl/vlenb/vtype` 均触发预期异常，全部断言通过 | 来自 Ara；使用测试自己的 `trap_vector`，不访问 stub 控制寄存器；不等于异常后的向量访存恢复测试 |

**待修正后验证：1 个，来自 Ara。** 本步没有修改软件。

| 入口 | 可复用的检查 | 采用前需处理/确认 |
| --- | --- | --- |
| `vector_helloworld.c` | 向量装载/存储复制字符串 | 原版打印向量临时副本，未比较 `buf`；服务器原版能打印，不是已复现打印崩溃。2026-10-20 测试副本改为打印 `buf` 并比较 22 字节，通过；原件未改，补丁尚未合入 |

**勿用：15 个访问 stub 控制寄存器的原版用例。** 用户已明确不纳入后续测试；保留源文件，不删除，也不再将其中的无故障数据检查列为适配候选。下列结论限于原版用例，停用不等于已证明 RTL 对应功能有错。

来源已经定位到本地保留的 `origin/mp/ara-pulpv1-os-debug`：Cheshire 提交 `5e9e19d052f2591e492721ce74eb336ec27118c0` 增加 stub 寄存器，`553c6d3e15b9bb021f5d8f83ba11dd83d805e78c` 增加并接入 `hw/mmu_stub.sv` / `hw/mmu_req_gen.sv`；这两个提交均不是当前参考 `e040b7bbc…` 的祖先。Ara 后续提交 `53c3aa0cd9bc78b7d026a56fad36ec7b63ae717f`（`Add default defines for no-stub operation`）在缺失寄存器宏时将偏移定义为 0，实际别名到当前 `scratch[0]`，不能产生预期的延迟/故障。这里不需要修改 SoC 来恢复该调试配置。

| 入口 | 原检查目的 | 当前决定及原因 |
| --- | --- | --- |
| `rvv_test_exceptions.c` | 编码、vstart 和非对齐访存异常 | 勿用：原版仍写 stub 初始化寄存器；另含非零 vstart 算术行为的实现前提 |
| `rvv_test_mmu_stub_unit_stride_comprehensive_var_lat.c` | 不同 VL/vstart 的顺序访存 | 勿用：写入不存在的 stub 控制寄存器 |
| `rvv_test_mmu_stub_unit_stride_ld_comprehensive_var_lat.c` | 不同 VL/vstart 的装载结果 | 勿用：同上 |
| `rvv_test_mmu_stub_unit_stride_corner_cases.c` | VL/vstart 边界 | 勿用：同上 |
| `rvv_test_mmu_stub_unit_stride_reshuffle.c` | 不同元素宽度的装载重排 | 勿用：同上 |
| `rvv_test_mmu_stub_unit_stride_st_reshuffle.c` | 不同元素宽度的存储重排 | 勿用：同上 |
| `rvv_test_vstart_unit_stride_mmu_stub_var_lat.c` | 非零 vstart 的顺序访存 | 勿用：同上 |
| `regfile_text_stub_regs.c` | stub 寄存器分别写入并读回 | 勿用：各指针别名到 scratch[0]，不能满足独立寄存器检查 |
| `rvv_test_mmu_stub_idx_ld_comprehensive_page_fault_var_lat_var_ex.c` | 索引装载页故障、地址与部分结果 | 勿用：依赖不存在的 stub 故障注入 |
| `rvv_test_mmu_stub_unit_stride_comprehensive_page_fault_var_lat.c` | 顺序存储页故障与恢复 | 勿用：同上 |
| `rvv_test_mmu_stub_unit_stride_comprehensive_page_fault_var_lat_var_ex.c` | 不同故障位置下的顺序存储 | 勿用：同上 |
| `rvv_test_mmu_stub_unit_stride_ld_comprehensive_page_fault_var_lat.c` | 顺序装载页故障与部分结果 | 勿用：同上 |
| `rvv_test_mmu_stub_unit_stride_ld_comprehensive_page_fault_var_lat_var_ex.c` | 不同故障位置下的顺序装载 | 勿用：同上 |
| `rvv_test_vstart_unit_stride_mmu_stub_page_fault_var_lat.c` | 非零 vstart 的访存页故障 | 勿用：同上 |
| `rvv_test_vstart_unit_stride_mmu_stub_page_fault_var_lat_mmu_req_gen.c` | 上项加 MMU 请求发生器 | 勿用：stub 故障注入及请求发生器均不存在 |

这里排除 MMU stub 用例，**不表示当前 CPU/Ara 没有真实地址翻译或异常功能**。

**当前配置不适用：5 个。** 保留源文件，未关闭或裁切 RTL 功能。

| 入口 | 原检查目的 | 排除依据 |
| --- | --- | --- |
| `axirt_hello.spm.c` | AXI-RT 配置下的基本运行 | 当前 `AxiRt=0` |
| `axirt_budget.spm.c` | DMA 数据与 AXI-RT 预算消耗 | 当前 `AxiRt=0` |
| `axirt_budget_isolate.spm.c` | 超过预算后的隔离状态 | 当前 `AxiRt=0` |
| `clic_basic.spm.S` | CLIC 中断与阈值 | 当前 `Clic=0` |
| `clic_multiple.spm.S` | 不同级别的待处理中断与阈值筛选 | 当前 `Clic=0` |

**与既定验收内容的差距。** 不因筛选测试而删减下一节原要求；本步只指出差距，不新增用例或改动执行顺序。

| 原要求 | 现有测试能提供什么 | 尚缺什么 |
| --- | --- | --- |
| 标量与 ROM/SPI 启动 | HelloWorld 可复用；官方已有 `rom.ld`、`.rom.bin/.memh` 构建规则及 TB SPI 启动路径 | 原 ROM 初始化观测、SPI raw 镜像布局与实际自主启动检查；不是新增一个 HelloWorld 源文件 |
| RVV 结果、VL 与尾部 | fmatmul、非 stub 的 CSR 用例；停用的 stub 用例不计覆盖 | 现有 CSR 辅助代码采用 LMUL=8，不能代替规定 SEW32/64、LMUL=1、运行时 VLMAX 六种长度及完整边界哨兵检查；小型精确浮点结果检查也未由单个 fmatmul 替代 |
| SPM/DDR 模型访存 | DMA 用例覆盖部分 SPM 非缓存路径，其他程序有实际数据访存 | 指定两区域、8/16/32/64 位、字节使能及跨行读回没有现成的完整对应用例；DRAM 链接模式存在也不证明已测试，高地址 libgcc 限制仍须按实际程序处理 |
| AMO、LR/SC | 本次 25 个入口及其 5 个正文中未找到直接对应测试 | 返回旧值、最终值及有界重试的定向检查；不据此扫描或移植整套 ISA 测试库 |
| 失败传播 | 原程序返回值经 crt0 写入结束寄存器，VIP 能报告非零目标退出；TB 使用 `$finish` | 仍需实际负例确认主机入口将失败返回为非零；打印 `FAIL`、目标退出与主机退出不能混同 |

**梳理与后续实测的边界。** 本节最初只完成测试梳理；第 6.3 节现已另获授权并实际执行，结果见页首报告。全工程静态检查、原验收差距仍保留，不自动新增测试替代 stub 用例，也不由本轮疑点测试改变提取和整体验收顺序。

### 6.2 既定功能验收要求（保留）

| 用例 | 验收内容 |
| --- | --- |
| 标量小程序 | 从复位执行原 Boot ROM，观察 LLC BIST 完成、全 SPM 配置与栈建立；载入新编译程序并核对明确结果/退出值 |
| ROM 完整启动 | 另跑 `BOOTMODE=2` SPI raw 小镜像：由原 ROM 读介质、搬到 SPM、交接执行；不修改 CPU PC，不用直接 ELF 加载替代。构造从 flash offset 0 开始的 `.rom.bin`/memh，核对 LMA/VMA 和 raw fallback 读取范围，预留有效填充值 |
| RVV 结果测试 | SEW=32/64、LMUL=1，运行时读取 VLMAX，取 N=0、1、VLMAX−1、VLMAX、VLMAX+3、2×VLMAX+5；strip-mining 每轮使用实际 VL，整数运算逐项对照标量金值，并做小型精确浮点算例 |
| 尾部/越界 | 输入输出前后哨兵、尾轮检查；仅检查有效元素与内存边界，不对 tail-agnostic 寄存器尾部作确定值假设 |
| 基础访存 | SPM 与 `0x80000000` 起的 DDR 模型区，按合法对齐的 8/16/32/64-bit load/store、字节使能、跨 cache-line 数组与确定图样读回 |
| 原子 | AMO add/swap、LR/SC 成功和有界重试，核对返回旧值/最终内存；选当前非缓存可达测试地址或明确维护，保留原子适配通路。无竞争场景不能强制要求 SC 必须失败；首次不扩展成 DMA 竞争验证 |
| 失败传播 | 故意结果不匹配的小负例应被脚本标 FAIL 并非零返回；正常 PASS、目标退出码及 simv 退出码分别记录 |

普通 JTAG preload 当前先等待 ROM 配 LLC，随后 halt/load/改 dpc：可证明部分初始化，不能代替上表 ROM 启动项。官方 TB 支持 SPI 自主启动，SD 分支明确不支持；首轮不恢复 GPT/Linux 全套流程。

历史检查发现原 `crt0.S` 不统一开 VS，HelloWorld 只在 main 中开 VS；最初建议在独立启动副本中补齐初始化。后续用户已直接修改服务器 `crt0.S`，显式设置 FS=Clean，并通过单个 fmatmul，详见 [E01 交接](../../../handoffs/E01_fixed_vector_extraction.md)。提取时保留并溯源该兼容修正，重新核对 VS/FS 在任何可能的向量/浮点指令前已正确初始化及反汇编顺序，不恢复旧 FS 写法；两工程使用相同输入，FS Dirty 状态跟踪原因仍未关闭。

已知启动问题保持显式：默认 PlatformRom=0 不触发其返回缺陷；ROM C 入口栈对齐及载荷返回链仍须观测，首次不顺手修改原 ROM。若阻塞目标用例，先定位实际指令/官方最小修复，再报告需增加的具体修复范围。原软件手册 passive start 位与 C 源存在差异（当前 C 用 scratch[2] 的 bit1，bit0 用于完成）；本方案主验收走已有 SPI 路径，未来补 passive 测试时必须核对实际 ROM，不照旧文字写位。

每条结果绑定源码清单 SHA、配置快照、软件 ELF/image SHA、命令、工具版本、超时和退出值。对照参考/提取的配置、结果与必要初始化行为，不要求时间戳完全相同。先用同一批 ELF/image 隔离硬件差异，再在提取工程内重新构建软件并重跑，验证软件独立性。

参数试验在基线对照及独立性验收后分步进行。每次先检查参数约束与实际展开，再针对变更覆盖新增索引/地址边界、冲突替换、脏行回写/flush、SPM 启动以及向量尾部/mask/跨 lane 等行为；完整候选回归还覆盖适用的并发、背压、原子及异常场景。每层分别记录结果，既有 FS Dirty 等未关闭问题不能由参数改变后的单例成功隐去。

应用对照固定算法、输入和编译选项，尽量复用同一 ELF；明确存储位置、冷热状态、Cache/SPM 分配、测量区间与频率，分别记录目标周期数和端到端时间，不将 VCS 主机耗时当作芯片性能。**当前启动默认全 SPM，测 LLC 缓存收益必须启用 Cache ways 并保护栈/程序数据。** 先单变量比较，再检验候选组合。面积、时序、功耗比较使用一致工艺/宏/约束和测量口径；Pad 围出的空间不免除供电、布线、测试和带宽要求。详细记录字段沿用资源指南，不新增通用试验框架。

<a id="dma-vector-reference-check"></a>

### 6.3 参考工程 DMA 与向量 HelloWorld 验证（已执行，原件未修）

2026-10-20 用户随后授权执行，已完成原版、诊断软件及新构建调试版的实际运行。完整测试项、结果与原因见[控制接口测试](../reports/reference_rebuild_check.md#dma-vector-tests-20261020)；服务器输出为 `~/CheshireAraPULP/_e01/dma_vector_check/`。向量修正副本通过；DMA 控制访问问题及失败退出问题已复现，尚未修复原件。本任务到测试与报告为止，不自动跨入修复或提取。

**以下保留测试前的假设与任务范围，时间用语指当时状态；“尚未复现”已由上述实测结果取代。**

**DMA 待验证的解释。** 用户提出，软件的 64 位访问可能与硬件截取低 32 位配套，在约定条件下正常工作。这个可能性应验证，不能仅凭宽度不同断言 DMA 有功能故障，也不能先统一改成 32 位访问。当前已知约束是：寄存器规格 `idma_reg64_2d.hjson` 明确 `regwidth=32`；`NEXT_ID_0/1` 位于 0x44/0x48，`DONE_ID_0/1` 位于 0x84/0x88，相邻项是不同通道的 ID，并非同一值的高低半部。当前 `NumStreams=1` 将未用通道读值置零，确实可能掩盖软件额外读取相邻寄存器；但仍须确认有效 ID 的数据位置和提交副作用正确。

已有本地汇编记录 `learning/evidence/advanced-dma-access.s:186` 显示 GCC 15.2.0 将旧驱动 ID 读取拆成 0x44/0x48 两次 32 位读后拼接；这不是服务器 GCC 13.2.0 的本次输出。下一轮必须读取服务器实际 ELF 反汇编，核对最终指令、必要时核对 AXI 地址/访问大小/数据位置、寄存器译码与提交/完成行为。源地址等 64 位字段若只写低半部，在高半部保持零的 SPM 用例中可能正常；单例通过不扩大到非零高地址/多通道支持。本轮没有复现 DMA 故障，也没有确认官方存在上述特殊访问约定。

| 项目 | 准备范围 |
| --- | --- |
| 执行方与时机 | 本地 Agent 操作服务器；用户明确下一轮再决定执行，本轮不 SSH、不构建、不运行，不下发服务器 Agent。下一轮收到该任务开始指令后，在此范围内自主完成常规细节，不逐条命令请示 |
| 输入 | `zhaowy24@172.16.0.243:~/CheshireAraPULP`；先核实本节固定 Cheshire/Ara/CVA6 版本、差异与既有 FS=Clean 修正。保持 `cv64a6_imafdcv_sv39`、Ara 真实 decoder、2 lanes/VLEN=2048、SelectedCfg=3、UseDramSys=0 |
| DMA 顺序 | 先检查原版指定用例的实际反汇编，再运行 `dma_2d.spm`，记录返回值和数据比较。失败或结果可疑时才增加必要的寄存器读写定位；确认提交编号、完成编号和实际拷贝，不预先修改驱动/RTL。`NEXT_ID` 读有提交副作用，打印应保存原读取值，不能为观察而额外读取 |
| 向量 HelloWorld | 在保留原件的测试副本中将打印参数改为 `buf`，增加与原字符串逐字节比较，失败返回非零；在相同硬件配置上构建运行。仅作此最小软件修改，不回放本地优化绕过 |
| 构建与输出 | 沿现有官方软件/仿真入口，先核对可复用的 RTL 构建；不无条件从头重建参考工程。仅构建指定软件用例，所有本轮测试副本、ELF、日志和退出状态在服务器 `_e01/dma_vector_check/` 独立保存；先核实目录，已有内容不得覆盖。官方入口若写固定路径，先确定必要输出重定向/最小副本用法，再运行 |
| 运行限制 | 单个仿真默认 10 分钟墙钟超时，串行运行；普通测试不导出波形，实际定位需要时才采集有限信号。stub 用例全部勿用，不调用会收集整目录测试的全量目标 |
| 保护范围 | 不改参考 RTL/驱动原件，不升级依赖或修改参数，不写提取目标 `~/CheshireAra`，保护 `.bender`、旧结果、TTY `/home/zhaowy24/Desktop/mycheshire_24` 和 `/opt`；若定位后需要修复功能性 RTL，另报最小范围 |
| 结果要求 | 分别报告实际输入、ELF/构建、命令、目标与主机退出状态、日志位置；DMA 核对数据/保护字符及必要的提交完成过程，向量 HelloWorld 核对逐字节结果。失败或超时如实保留，源码疑点不写成已复现故障；结果更新既有 E01 交接，日志和波形留服务器。本任务结束后不自动提取或扩大回归 |

<a id="step2-plan"></a>

## 7. 当前步骤 2：分阶段计划（2026-10-21）

### 7.1 阶段、验收与停止点

以下 **2A、2B、2C、2D均已完成**；2D结果见[第7.7节](#step2d-result-20261022)。每阶段报告后停止，用户明确授权下一阶段后才继续；阶段内常规路径、构建副本及测试适配自行处理，不逐条请示。

| 阶段 | 输入与修改范围 | 必要产物 | 验证与通过条件 | 停止点 |
| --- | --- | --- | --- | --- |
| **2A 规划（已完成）** | 本地文档及服务器实际源码/差异、成功清单、工具入口、测试记录、目标目录；服务器只读 | 本计划、E01 交接与必要共享状态；协作约定补充 | 明确真实来源、保留规则、分阶段依赖及测试判据；不产生提取/运行结论 | 交付计划后停止，等待 2B 授权 |
| **2B RTL 与最小仿真配套（已完成）** | 从服务器磁盘提取功能 RTL、包/include、原生成物、通用技术单元；加入集中配置/共同 wrapper，最小适配 fixture/VIP 层次；同时迁入所需 TB/DPI/模型和构建/运行入口 | 第 5 节的硬件/仿真部分、唯一有序静态分组清单、来源/许可记录；新输出构建的 simv；指定参考 ELF/SPI 镜像副本 | 路径/重复定义/宏/分组及完整有效配置正确；从源编译展开；用**同一批参考 ELF/镜像**跑第 7.3 节所选硬件对照，成功项与参考一致，限定告警/已知失败单列，无新增未解释差异 | 报告硬件提取结果后停止；此时软件尚未独立，等待 2C |
| **2C 软件与镜像（已完成）** | 迁入启动、链接、23 单元库及头/HAL、选定测试与镜像规则；保持 FS 修正及 VS/FS 顺序、地址/启动语义；原生成 Boot ROM 不重生成 | 新工程内的明确软件源列表/Make 入口、新编译 `libcheshire.a`、ELF、SPI raw/memh、map/dump/构建结果 | 空软件输出重建，链接记录不得指向旧库或旧脚本；核对启动反汇编，重跑第 7.3 节软件相关测试；48 KiB 搬运与**本次重建镜像**一致。未改输入的纯后端测试不因软件重建重复运行 | 报告软件独立结果后停止，等待 2D |
| **2D 入口收敛与搬迁验证（已完成）** | 整理 2B/2C 实际使用的入口，去掉临时旧路径/重复入口；复制必要工程文件到另一经检查的新位置，使用全新输出 | 可搬迁工程、实际构建/运行记录及外部工具边界；已知限制摘要 | 搬迁位置从源重建 RTL、DPI、软件和镜像，运行已选回归；按第 7.4 节检查实际文件读取与子进程，无 Bender、依赖下载、旧工程资源或缓存参与 | 报告独立性结果后停止；参数开放、功能改动和工艺适配另行授权 |

### 7.2 各类输入从哪里取

下列路径均相对服务器 `~/CheshireAraPULP`，不以本地同名文件替代。

| 类别 | 实际来源与保留依据 |
| --- | --- |
| 功能 RTL、配置、技术单元 | `hw/` 与锁定 `.bender/git/checkouts/<组件>/` 的实际文件；依据生产构建分组脚本筛选，并保留当前配置/声明支持范围所需分支。`tc_sram/tc_sram_impl/tc_clk` 等取已验证通用实现，不用 `-t asic` 排空技术单元 |
| 包、include、生成物 | 现有 18 个 include 作用域及实际间接引用；`hw/bootrom/cheshire_bootrom.sv`、Cheshire/各组件寄存器 RTL/头和 iDMA 汇总 RTL；保存相应 hjson/yml/模板/生成器及本地差异，首次构建直接使用现有生成物，不触发重生成 |
| SoC TB、VIP、DPI、模型 | `target/sim/src/{tb_cheshire_soc,fixture_cheshire_soc,vip_cheshire_soc}.sv`、`elfloader.cpp`，其使用的 AXI/Serial Link/debug/UART 等验证依赖；`target/sim/models/{s25fs512s,24FC1025}.v`。`tb_cheshire_pkg.sv` 只作参考配置来源，新活动清单不再选入其四组配置数组；无其他消费者时不迁该包。保持 AXI RAM 模型路径，UseDramSys=0，不迁 DRAMSys/SystemC 运行资源 |
| 构建和运行 | `_e01/dma_vector_check/pr80_204_20261021/production_build/` 内的 `compile.cheshire_soc.sh`、`build_commands.json` 与官方 VCS 入口提供编译/展开选项；`_e01/remaining_acceptance_20261021/run.py` 提供已有结果判定。只改内部路径/输出与层次引用；现有 `E01_SIMV` 写法仍会读取旧 `inputs.json` 默认表达式，必须移除此依赖。保留目标/仿真器/入口三种退出状态、未完成非零和拒绝覆盖 |
| 软件库、链接、测试 | 原 `sw/lib` 8 单元，printf、LLC `axi_llc_reg32.c`、AXI-RT `axirt.c`、OpenTitan base/dif/autogen 12 单元，共 **23 单元**及相应头；原 `sw/include`（含 DMA HAL 与生成寄存器头）、`sw/link/{common.ldh,spm.ld,rom.ld,dram.ld}`；Ara `cheshire/sw` 的所选测试/辅助头及第 7.3 节现有测试副本。沿实际 `*.build.json` 的 GCC13.2、ISA/ABI、O2/LTO/medany 和定向测试禁自动向量化选项，明确列源，不引入 SDK |
| ROM 与镜像生成资料 | ROM 本体保留原生成 SV；同时保存 `hw/bootrom/cheshire_bootrom.{S,c,ld}`、`util/gen_bootrom.py`、`cheshire.mk:134–144` 的配方/来源。2C 重建的是 HelloWorld 载荷及 raw：LMA=0、VMA=`0x10000000`、offset0，填 `0x9a` 至49152 B并生成memh。服务器 GPT recipe 实际启用，与旧本地描述不同；本次不调用 GPT/sgdisk，原 ROM 的 GPT/raw 逻辑及 `gpt.c` 保持 |
| 来源和许可证 | 根锁文件/原分组清单、组件 HEAD/diff、既有修正 patch/deployment/hash 记录及各 LICENSE/版权头。两外设模型分别保留 GPLv2、Young Engineering/Microchip 使用提示；仅按现有内部仿真用途纳入，不把它们当作可任意再分发的工程自有源码 |

已有分组脚本、日志和锁定源码足以开始 2B，**不安排 Bender 导出为必做步骤**。只有实施时发现具体条件选择/编译组信息确实无法从现有材料确定，才说明缺项并提出一次性离线解析；不能升级、联网解析或再建包管理机制。

新增固定配置包和共同 wrapper 用于消除 TB 私有硬件选择；运行适配沿用已验证 `run.py`，用于识别 simv=0 的目标失败；软件 Make 入口用于脱离根 Make 的依赖获取和旧路径。除此不新增通用配置生成、自动归档、调度或审计框架。未实例化不等于可删除，目录名含 test 也不等于其中的包/接口都无用。

<a id="step2-tests"></a>

### 7.3 复用的对比测试

记 `$R=_e01/remaining_acceptance_20261021`，`$D=_e01/dma_vector_check`，`$P=$D/pr80_204_20261021`。以对应报告、实际命令/输入哈希和日志为基准，不另造替代测试。

| 选择 | 来源与对比内容 | 阶段 |
| --- | --- | --- |
| 标量 HelloWorld、原 ROM/SPI | `$D/aw_config_20261020/helloworld.elf`；`$R/spi_raw.memh`、`spi_copy_check.json`及启动日志。核对 BIST/全SPM、ROM自行搬运49152 B及交接、目标完成；SPI不能由直接加载ELF替代 | 2B同产物；2C新软件/镜像；2D搬迁重跑 |
| 非 stub CSR、RVV、访存原子 | `$R` 的 CSR、`rvv_bounds`、`memory_atomic`；分别核对3次预期CSR异常，SEW32/64、m1的规定六种N/实际VL/保护区/精确浮点5976项，以及SPM/DDR模型访存、AMO/LRSC572项。另保留已验证32×32 `sw/tests/fmatmul.spm.elf` 与其源码，检查 FS/FP 应用结果 | 2B/2C/2D；2C保持现有VS在首条向量指令前、FS显式Clean的顺序 |
| 运行入口四种判定 | `$R/run.py`、`rvv_negative.spm.elf`、CSR的1秒故意限时及SPI真实断言日志。正常0，目标失败1，断言2，超时124，缺完成标志非零；目标失败41/simv0不能误判成功 | 2B适配即验；2C使用新ELF；2D重复 |
| DMA wrapper/HAL 六项回归 | `$D/aw_config_20261020/{dma_original,dma_checked,dma_reg_lanes,dma_long_aw_api,helloworld,vector_fixed}.elf`。覆盖短搬运、编号、上下半部访问、AW解耦长搬运和22 B向量复制；HelloWorld只计一次 | 2B/2C/2D；保留原成功结果和构建绑定 |
| iDMA #80/#204 后端定向回归 | `$P/jobs/`、既有 `tb_idma_backend_rw_axi.sv` 及 `backend_tests.py` 的参数/判据：#115四种AW/RW、mixed_modes、pr80_asymmetric，各理想/反压内存，共12项；数据/完成/事务数及通道稳定性。迁入 `idma_intf/idma_test/axi_sim_mem` 等实际所需依赖 | 2B和2D；不重跑旧版/仅#80版本，不另查same_dst |
| 既知 LLC 限制对照 | `$P/llc_recheck/{default_long,unaligned16,dense32}/` 的原命令及只读采样，分别代表读挡写、写挡读、Bloom行锁等待。仅适配wrapper层次，确认限制未被配置变化掩盖；仍记录为失败/停滞，不能计作功能通过 | 2B/2C/2D各保留这3项，不扩展参数扫描或修复 |
| Serial Link RX 经 LLC 写 DDR | `$D/slink_llc_rx_20261021/final/` 的64KiB、CPU并发192KiB、非对齐间断8193B三项；因fixture/wrapper搬迁涉及该通路，核对数据、保护区及完成 | 2B迁必要TB/监视器，2C重建CPU软件，2D重跑；不新增TX/GB/eMMC验证 |

ROM 限定豁免只针对已定位的 **两条读、两条写 padding 含 X 事件**。保留原日志及入口返回2；对照时确认同一访问和无新增错误后，单列“功能接受、已知告警”，不改成无断言PASS、不把其他返回2自动放行。`spi_boot/result.json` 初版只列写事件，读事件还须结合原日志和最终断言核查记录。

完整14项LLC复查、same_dst原平台失败/修正副本通过、独立端点/DDR旁路诊断等保留原记录及索引，不默认重跑或纳入当前SoC新拓扑。FS Dirty原因、libgcc高地址重定位和未逐条解释的旧warning仍是限制，不因提取完成消失。普通用例串行、无波形、每例默认主机600秒；故意1秒测试限时出口除外。超时先区分程序推进、异常和停滞，只有等待关系证据支持才称死锁。

### 7.4 独立性及用户决定

**2026-10-22 用户决定：**保留现有 `sim/scripts/run.py` 运行入口；后续根据用户实际使用习惯和反馈再改进优化。2D沿用该入口，不预设改名为 `start` 或新增重复包装脚本。该决定最初只更新文档；随后用户明确授权2D，实施结果见第7.7节。

每次用现有日志/结果记录实际源码修正、有效CPU/SoC配置、ELF/镜像、simv、命令和退出状态；比较目标结果、完成标志、异常/断言、必要内存/总线行为，不要求 simv 哈希相等。2B保留参考二进制只为隔离硬件变化，2C必须重编库和应用，2D不能复制旧编译库/缓存充当重建。

2D 选择一个不存在的新位置，复制工程必要文件后从新输出构建；结合显式清单、include/链接记录、符号链接真实路径和服务器现有 `strace` 的文件/子进程/网络记录，检查实际未调用 Bender/下载程序、未读取参考工程/旧 `.bender`/TTY/旧缓存。源码、DPI、模型、镜像和运行资源必须在搬迁目录内；编译器、EDA和系统运行库为列明的外部工具。**2026-10-22用户澄清：服务器可以正常联网；VCS直接使用现有许可证及必要通信，无需另行确认。限制的是工程构建不依赖在线下载源码、解析或更新依赖，不调用Bender、不擅自升级依赖。**此前“用户的联网限制”“严格离线冲突须批准例外”的表述缺乏依据，现予纠正。实际访问检查区分许可/工具通信与下载工程依赖，不要求零网络调用。不改名、删除或限制访问受保护参考工程来证明独立性。

**当前没有需要新增的配置或架构选择。** 2D已沿现有工具和许可环境完成，不以许可通信设置额外确认条件。通用仿真不代表SRAM宏、DDR PHY、ASIC综合或流片验收；新IP、参数开放和产品DDR拓扑均不混入本任务。

<a id="step2b-result-20261021"></a>

### 7.5 步骤 2B 实施结果（2026-10-21）

用户于同日明确“开始实施2B”。本地 Agent 经 WSL SSH 在 `~/CheshireAra` 实施；本地子 Agent 分别核查配置/端口、补入限定生成来源/许可证、独立比较运行结果，未启动服务器 Agent。初查目标为空后才写入；参考基底仍为 `e040b7bbc…` 加实际磁盘修正，没有从纯提交导出或用本地 RTL 替代。

**提取范围。** 保留成功清单的48个原编译组、624个原设计文件，排除92个未选独立测试/专用支持及旧TB配置数组。功能RTL及参数化实现、17个仍有消费者的原include作用域，另加1个后端回归include路径（移除的`axi_llc/test`只服务已排除的独立TB）、原生成ROM/寄存器/iDMA RTL、技术仿真单元、TB/VIP/DPI/模型均来自服务器实际文件。新增固定配置包及68端口共同wrapper后，SoC构建编译626个设计文件，顺序与选择后的原清单一致且无重复。CPU profile及`cheshire_pkg`逐字保留；仅原Ara启用项进入固定包。实际运行配置仍为2 lanes/VLEN2048、CPU VLEN64/WT、LLC128KiB、DMA在途16、UseDramSys0；不把SelectedCfg当CPU配置证明。

活动有序清单直接位于 `sim/scripts/compile.cheshire_soc.sh`，没有另建重复filelist或配置生成框架；`sim/scripts/run.py`沿既有判定最小适配工程路径和选定测试完成标记。原生成器/hjson/模板/recipe仅存 `provenance/generation/`，首次构建未调用；全部来源、版本、实际差异及许可在 `provenance/`、`LICENSES/`。原FS/HAL修正由本阶段相同ELF输入与来源记录保留，软件源/库重建仍待2C。

**构建与对照。** 从新输出目录构建SoC、iDMA ideal/throttle、SerialRX四种simv；实际命令及退出状态在 `provenance/2b_builds.json`。首个后端目录 `sim/work/idma_ideal` 的simv构建返回0但KDB缺少新增top，补上新增vlogan的`-kdb`后在 `idma_ideal_02` 重建成功；旧输出保留且未用于回归。SoC的257条编译告警与参考逐项一致，无新增告警。普通测试串行、无波形、600秒上限，只有故意超时用例为1秒。

| 对照项 | 本次实际结果与限定条件 |
| --- | --- |
| HelloWorld、32×32 fmatmul | 均目标/仿真器/入口0。HelloWorld两份CPU trace与正式参考逐字相同；fmatmul同ELF、19883目标周期、Passed及完成时刻与历史绑定摘要一致，旧完整trace已被后来运行覆盖，不声明该项完整trace相同 |
| 非stub CSR、RVV、访存原子 | CSR三次预期Illegal Instruction/mcause2；RVV5976项、FP32/64零错，18组实际VL与参考一致；SPM/DDR访存原子572项零错，16条AMO/LRSC及各访问宽度计数一致 |
| DMA wrapper/HAL | 六项（含HelloWorld）全部通过；同ELF、完成/结果/时刻一致，各两份CPU trace均与参考逐字相同，无新增异常 |
| iDMA #80/#204后端 | 六job×ideal/throttle共12项通过，seed1；remaining=0，AR/AW/B及反压计数逐项一致，无数据或通道稳定性错误 |
| SerialRX经LLC写DDR | 64KiB、CPU并发192KiB、非对齐间断8193B均通过，分别32/96/5突发；DDR模型数据和保护区、CPU并发及写回条件符合原TB检查，无新增总线错误。不扩称多在途反压或同缓冲区缓存交接已验证 |
| 原ROM/SPI | ROM自主搬运49152 B全覆盖、零差异，BIST/全SPM/栈/交接一致，HelloWorld完成；目标0、simv0、入口2。仅原字节6/7的两读两写padding事件，全部错误标记标准化后与参考一致，按限定条件接受功能结果 |
| 入口判定 | 正常0；故意目标不匹配为目标41/simv0/入口1；SPI断言入口2；故意1秒超时124；缺少完成标志的LLC采样入口4，均实际运行验证 |
| LLC既有限制 | default_long、unaligned16、dense32分别复现读返回等待、写读循环、Bloom行锁等待，入口均INCOMPLETE/4；采样和已知失败记录保留，不计功能通过、不扩展修复 |

本次原始输出统一在 `sim/work/`；每例 `result.json` 绑定实际simv、ELF/镜像、构建时来源清单、命令、目标/仿真器/入口状态。`provenance/2b_run_commands.json`、`2b_build_comparison.json`、`2b_trace_comparison.json`、`2b_soc_comparison.json`保存定向比较，最终摘要为 `sim/work/2b_summary.json`。初次HelloWorld仍保留加入入口自身哈希字段前的原记录，未回写旧结果。新simv哈希天然不同，不作为比较失败。

**保护检查与停止点。** 31次运行分类为25项正常PASS、1项SPI限定告警功能接受、2项故意失败/超时判定符合预期、3项LLC既知失败保持。339项生产输入、26项最终输入、15项参考测试产物、根HEAD/status/diff及26组件HEAD/diff均保持；所有提取源与来源记录、4种构建的实际解析输入及每例产物绑定无不符，见`provenance/2b_final_check.json`。构建/运行未调用Bender、下载依赖或使用旧编译缓存；未改参考工程、本地FPGA/RTL/sw、TTY工程或外部工具。2B报告后停止；下一步仅在用户明确授权2C后迁入软件源码、重建库/ELF/SPI镜像。2D搬迁和实际文件访问验证尚未执行，本轮路径检查不能替代它；未进行SRAM宏、DDR PHY、ASIC综合或流片验收。

<a id="step2c-result-20261022"></a>

### 7.6 步骤 2C 实施结果（2026-10-21～22）

用户明确授权“开始2C”，并于次日要求继续。本地 Agent 经 WSL SSH 实施，本地子 Agent 按不重叠目录迁入软件、独立检查构建和结果；未委派服务器 Agent。次日 WSL 原生 SSH 超时，改由 WSL 调用既有 Windows SSH 通道；先确认前五项测试已完成且无遗留仿真进程，再从未运行的 DMA 项继续，没有重复或覆盖前五项输出。

**软件与构建。** 在服务器 `~/CheshireAra/sw/` 迁入服务器实际启动、四份链接文件、HAL/生成寄存器头、库依赖及所选测试，共90份来源文件；新增一份 `sw/Makefile`，解决原根 Make 会访问 Bender/旧目录的问题。23个库单元与归档顺序保持，22个C单元沿原标量ISA，crt0及测试沿原向量ISA，GCC13.2、lp64d、O2/LTO/medany保持；RVV/访存金值测试的禁自动向量化选项保持。软件 `NR_LANES` 直接读取 `src/config/cheshire_pkg.sv` 的 `AraNrLanes`，`ARA_NR_LANES` 由同一值派生，不新增硬件配置入口或保留无消费者的 VLEN 软件宏。

原 `crt0.S`、DMA HAL及地址/启动语义逐字保留；FS Initial→清FP寄存器→显式FS Clean→main，以及各测试首条向量指令前启用VS的顺序保持。唯一测试源码适配是旧 `dma_long_2d.c` 的6参数调用追加 `DMA_CONF_DECOUPLE_NONE`，与现行7参数HAL对应；该项可加载内容及1,893条指令仍与参考一致。相同辅助头共用一份，原符号链接按源内容保存为工程内普通文件；版权、printf MIT及已有组件许可保留。未带入Linux SDK、无关测试或旧对象/库。

实际构建命令为 `make -C sw -j1 OUT="$PWD/sw/build/2c_02" all`（在工程根执行）。首次 `2c_01` 因GCC的 `-print-file-name=liblto_plugin.so` 仅返回裸名，ar未正确索引LTO符号而链接失败；改从现有 `lto-wrapper` 同目录定位插件，在新目录 `2c_02` 重建成功，失败输出和Make旧版均保留。成功构建从源码得到新 `libcheshire.a`、17个ELF及map/dump、HelloWorld ROM载荷与raw/memh；没有链接参考库或执行参考脚本。原生成Boot ROM及RTL/simv保持，未重新生成或编译。

17个新ELF的入口、ALLOC节/地址/BSS大小、全部PT_LOAD内容及归一化反汇编与参考一致；整个ELF的debug路径不同不要求哈希相等。新HelloWorld载荷847 B，LMA=0/VMA=`0x10000000`，按原规则填 `0x9a` 至49152 B；raw及memh与参考逐字相同，未调用GPT/sgdisk。40份编译依赖文件、17份map确认81个实际项目源/头及项目链接输入位于新工程；外部仅为既有工具链头/库和本次GCC临时LTO对象。24条软件告警（11条RWX、13条源码告警）保留，CSR告警与原日志逐项一致，相关源码未改。实际构建输入检查见 `provenance/2c_build_review.json`，机器码和镜像对照见 `2c_elf_comparison.json`。这不替代2D搬迁后的实际文件访问验证。

| 新软件对照 | 实际结果与判据 |
| --- | --- |
| HelloWorld、fmatmul、非stub CSR | 目标/仿真器/入口均0；fmatmul为32×32，19883目标周期、Passed；CSR恰三次预期Illegal Instruction/mcause2 |
| RVV与访存原子 | RVV5976项、FP32/64零错，18组实际VL保持；SPM/DDR模型572项零错，16条AMO/LRSC保持 |
| DMA/HAL及Serial RX | DMA六项含HelloWorld全部通过；RX 64KiB、CPU并发192KiB、非对齐间断8193B通过，数据/保护区与原条件一致 |
| SPI自主启动 | 原ROM自主搬运新49152 B镜像并执行HelloWorld，目标0/simv0/入口2；仅原padding字节6/7两读两写事件，按既有限定豁免接受功能结果 |
| 负例与旧失败 | 目标不匹配41/0/1，故意1秒超时124；LLC三项保留原等待/循环采样与INCOMPLETE/4，不计功能通过、不扩大排查 |

共19次串行运行：13项正常PASS、1项SPI限定告警功能接受、2项故意负例判定正确、3项LLC已知失败保持。新输出为 `sim/work/runs_2c/`；未变的12项纯iDMA后端测试不重复。每例结果绑定simv/ELF/镜像及硬件构建清单，`provenance/2c_run_commands.json` 另绑定本次软件来源快照、新库及构建记录；原2B结果保持。完成摘要为 `sim/work/2c_summary.json`，独立比较保存在 `provenance/2c_*comparison.json`。

**保护与停止点。** 最终保护检查见 `provenance/2c_final_check.json`：参考源码/版本/差异和原测试产物、2B硬件/配置/生成ROM、编译运行入口及simv未变；未改本地FPGA/RTL/sw、TTY工程或外部工具。2C完成后停止，等待用户明确授权2D；尚未执行搬迁后的RTL/软件重新构建与实际文件访问验证。ROM限定告警、DMA共享LLC限制、FS Dirty原因和libgcc高地址限制继续保留，不宣称工艺或产品验收完成。

<a id="step2d-progress-20261022"></a>
<a id="step2d-result-20261022"></a>

### 7.7 步骤2D实施结果（2026-10-22）

**授权与约束纠正。** 用户已授权2D并确认保留`run.py`。主Agent曾将“不依赖在线下载源码或解析、更新依赖”扩大为全面禁网而暂停EDA；用户明确纠正后，已取消这一无依据的暂停条件，直接沿服务器现有VCS及许可证服务继续。本轮不调用Bender、不下载或升级依赖，不改RTL/配置/启动语义。所有操作仍由本地Agent经WSL SSH执行，本地子Agent只读独立评审，主Agent统一修改文档与运行，未委派服务器Agent。

**入口和搬迁。** 检查目标不存在后，将明确源码、许可证及必要来源/生成资料复制至服务器 `~/CheshireAra_relocated_2d_20261022`：987份文件、活动清单960项，约14.6 MB；省略18份历史参考ELF/镜像，不复制旧`sim/work/`、`sw/build/`或缓存。保留原目标`~/CheshireAra`和参考工程，未改名或限制其访问。`compile.cheshire_soc.sh`、`run.py`和`sw/Makefile`已从自身位置派生根目录，实际不需要修改或新增包装；两处README统一为“编译硬件→重建软件→运行新ELF/镜像”，来源清单仅相应更新README哈希。原参考二进制及历史产物仍保留在原工程，不作为搬迁构建输入。

**从源码重新构建。** 在搬迁根执行 `make -C sw -j1 OUT="$PWD/sw/build/2d_01" all`，重建23单元库、17个ELF和SPI raw/memh；四个硬件target分别用 `bash sim/scripts/compile.cheshire_soc.sh sim/work/<target> <target>` 从新输出构建，target为`soc`、`idma_ideal`、`idma_throttle`、`slink_rx`，全部返回0。673份`src`文件及三个活动入口保持；实际分组、文件顺序、宏、include、top和参数与2B相同。DPI从新目录编译；四种构建未读取其他目标的输出。SoC/SerialRX各257条、后端各3条既有告警逐项保持。软件17个ELF的入口、ALLOC/BSS、PT_LOAD内容及指令与2C一致；847 B载荷及49152 B raw逐字相同，由raw生成的memh也逐字相同，24条软件告警保持。原生成Boot ROM未重生成。

**串行运行对照。** 用新simv、新软件/镜像及工程内job/probe执行31项既定对照，普通每例600秒、无波形。结果：

| 分类 | 结果及基准关系 |
| --- | --- |
| 25项正常PASS | 包括HelloWorld、非stub CSR、RVV5976项、访存原子572项、32×32 fmatmul、DMA/HAL、Serial RX三项及iDMA后端12项；目标结果、完成标志、异常和必要访存/总线行为与2B/2C一致 |
| 原ROM/SPI功能接受 | 自主搬运本次49152 B新镜像并执行HelloWorld；仅原padding两读两写事件，保留目标0/simv0/入口2，不扩展豁免 |
| 两项故意负例 | 目标41/simv0/入口1及故意1秒限时124；失败识别正常 |
| 三项LLC已知失败 | 原default_long、unaligned16、dense32采样行为保持，仍INCOMPLETE/4，不计功能通过、不扩展修复 |

实际结果在新工程 `sim/work/runs_2d/`，命令及软件/硬件输入绑定在 `provenance/2d_run_commands02.json`。首次临时批命令重复替换ELF路径，被未修改的`run.py`工程目录检查拒绝；没有启动simv或生成测试结果，不计入31项。该次`2d_run_plan.json`、`2d_run_commands.json`及入口日志/trace保留；修正的是临时命令准备脚本，随后校验所有路径再运行。

**实际访问和保护。** 软件、四种硬件构建和31次运行均保留`strace`文件/子进程/网络记录，网络载荷以raw指针形式记录；加上单独保留的入口拒绝，共37份trace、4,075,541条事件，解析无缺口。工程输入和运行资源均来自搬迁目录；没有读取原`~/CheshireAra`、参考工程、旧`.bender`或TTY工程，没有Bender/下载依赖工具执行或旧编译缓存参与。编译器/EDA安装及系统文件为显式外部工具；临时编译文件结合本次创建/输出记录识别。VCS及其线程另有工程外用户配置/工具数据路径打开，摘要如实单列；Agent评审未打开这些文件的内容，也不推断工具访问用途，不宣称所有进程仅访问新目录或完全无网络。实际跟踪未见`/opt`、`/eda`写打开或成功路径修改；这不等于对整个安装目录做前后哈希审计。

独立结果比较在 `provenance/2d_runtime_comparison.json`（36份CPU trace逐字相同，12项后端事务/停顿计数及完成时刻一致），完整访问评审在 `provenance/2d_access_review.json`。最终保护与绑定检查在 `provenance/2d_final_check.json`；原源码/软件、参考版本及差异、旧构建/运行产物保持，源码树仅README及对应清单记录变更。摘要 `provenance/2d_summary.json` 分别保存在原工程和搬迁工程，指向本次构建、运行、独立比较及实际访问证据。两处README提供当前入口；详细原始记录保留在搬迁验证目录。

**停止点。** 2D完成，本次独立提取、软件重建和搬迁验证结束。ROM限定告警、DMA共享LLC失败、FS Dirty原因和libgcc高地址限制继续保留；不扩大为SRAM宏、DDR PHY、ASIC综合或流片验收。后续参数开放、使用习惯优化及功能/工艺改造另行授权。

<a id="post-validation-cleanup-20261022"></a>

### 7.8 验证后清理（2026-10-22）

用户先要求规划，随后明确“好的，开始实施吧”，授权按已说明范围清理验证产物。执行前核查两个工程目录、来源清单及运行进程；没有构建/仿真进程，未清理参考工程、`.bender`、TTY、外部工具或本地已有修改/未跟踪文件。

| 对象 | 实际处理 |
| --- | --- |
| `~/CheshireAra` | 保留源码、集中配置、许可证、来源/生成资料、README及原compile/run.py/Make入口；移除`sim/work/`、`sw/build/`和18份旧`sim/reference_inputs/` |
| `~/CheshireAra_relocated_2d_20261022` | 完成归档及逐文件校验后删除；不再保留第二个工作工程 |
| `~/CheshireAra_validation_archive_20261022/validation.tar.gz` | 保留2033份文件，包括完整运行/失败日志、CPU trace、原始strace、软件输入、构建日志、源清单/比较记录及搬迁源码快照；约202 MiB，仅作证据归档 |
| 可重建缓存 | 九个硬件构建中的`csrc`、`AN.DB`、`work.lib++`、`simv.daidir`未归档，共1477个缓存文件随旧输出删除 |

归档SHA256为`8d1f4535961177338f2b991adf3c639841bfb4eaafac05fc3a81737ff923ff1a`；`index.json`记录每个归档成员的SHA256及清理范围。归档先完整重读、逐文件校验，再复查原文件未变化后删除；正式工程1018份保留文件哈希保持，只有README和活动来源清单按清理状态更新。活动清单移出18份已归档参考二进制后为960项，没有修改RTL、软件、配置或入口。未重新构建/仿真，不产生新的功能验收结论。

两个工程清理前共占3,925,499,904字节；清理后正式工程及归档共约232,239,104字节（统计时未计随后写入的两个小型清理摘要），净释放约3.44 GiB。清理结果保存在正式工程`provenance/cleanup_20261022.json`及归档目录`cleanup_result.json`。

历史JSON和本节之前的测试路径保留当时事实；归档内以`CheshireAra/`、`CheshireAra_relocated_2d_20261022/`为前缀，可用`tar -tzf validation.tar.gz`列出，或用`tar -xOzf`读取指定记录。不要把历史路径失效解释为测试证据丢失。ROM限定告警、LLC失败及首次失败记录均保留。下一次使用正式工程须按README重新编译硬件和软件；当前工作区不保留现成simv/ELF。

<a id="user-documentation-plan-20261022"></a>

### 7.9 独立工程用户文档规划（2026-10-22，阶段A）

**范围与实际检查。** 用户本轮只授权规划和只读核查，明确同意后才在服务器写文档。本地HEAD为`c9abbb48946fe3a7244bfb3159919b7c9731cb59`，既有文档修改及未跟踪图稿/证据保持。主Agent经WSL SSH读取`/home/zhaowy24/CheshireAra`实际入口、配置、共同wrapper、必要启动/链接规则及来源/验收摘要；原生SSH响应不稳定时沿既有Windows SSH通道读取，未委派服务器Agent。本地子Agent只读检查文档范围与判据，主Agent统一本节及交接。服务器工程无`.git`，来源版本由`provenance/reference.json`等记录；未扫描全部RTL、读取受限工具配置、解包归档、构建或运行仿真。

#### 7.9.1 最少文档与阅读顺序

建议只新增两份正文，根README加导航，保留现有`src/config/README.md`作为配置源码旁的简要说明，不另建目录说明、脚本手册或重复配置表文件。

| 拟写文件（相对`~/CheshireAra`） | 用途与章节 |
| --- | --- |
| `docs/README.md` | 用户入口。先给最短上手，再解释目录/固定基线/外部工具、产物和日志、退出状态与已知限制，最后给按需查阅链接。目录示意说明哪些是源码、哪些在构建/运行时产生，不要求创建空目录 |
| `docs/CONFIGURATION_AND_DEVELOPMENT.md` | 按需查阅。分开讲硬件配置、编译选项、运行参数、软件构建选项；按CPU/Ara、总线/LLC/SPM、启动/地址/中断/外设分组列维护字段、当前值、消费者/派生关系及修改后重建/测试范围。再分别讲修改已有RTL、配置、软件库/测试、源码/include清单、TB/模型；调试放在最后 |

阅读顺序：根README导航→`docs/README.md`的上手与结果检查→需要修改时查第二份。首次不要求通读配置表、历史实施资料或参考工程教程。

最短操作顺序沿现有README：在`~/CheshireAra`执行`bash sim/scripts/compile.cheshire_soc.sh sim/work/soc_01 soc`；再执行`make -C sw -j1 OUT="$PWD/sw/build/software_01" all`，从源生成库、17个ELF和SPI镜像；使用`E01_SIMV="$PWD/sim/work/soc_01/simv" python3.9 sim/scripts/run.py sim/work/runs/hello_01 elf "$PWD/sw/build/software_01/helloworld.elf"`运行新ELF。运行后立即查看入口退出值、该运行目录的`result.json`与`simulate.log`。原ROM/SPI自主启动另列为可选步骤，使用同一新simv、`spi`模式和本次`spi_raw.memh`，另选新运行目录。这些是拟写命令，本轮未执行。

编译、运行和结果检查分别说明。普通运行串行、默认600秒、无波形；首次沿`all`，不新增简化入口。需要重建硬件或软件时各自换尚不存在的输出目录；仅重复运行时可复用已有新simv/ELF，但必须换新运行目录，不要求无关重编。首次沿现有生成Boot ROM，不列重新生成/修复ROM为上手步骤。

#### 7.9.2 章节的实际依据

以下均为本轮读取的服务器文件，不能用本地同名源码替换。

| 内容 | 实际依据 |
| --- | --- |
| 编译入口、工具和有序清单 | `sim/scripts/compile.cheshire_soc.sh:1–14`及各`vlogan`分组、末尾target/`vcs`段。有序源码、语言/宏/include作用域直接维护在此脚本，无另一个活动`filelist.f`；target为`soc`、`idma_ideal`、`idma_throttle`、`slink_rx`。`build.log`、`elaborate.log`及清单快照在新构建目录 |
| 运行、输出与判定 | `sim/scripts/run.py:1–42`、`src/tb/src/tb_cheshire_soc.sv`及VIP完成标记。mode为`elf/spi/job/slink`；`elf`实际使用`BOOTMODE=0/PRELMODE=1`的Serial Link装载，不能写成JTAG默认。`E01_SIMV`、`E01_TIMEOUT`及附加参数按现有实现解释；simv、运行输出与输入均须位于工程内，simv旁须保留`source_manifest.json` |
| CPU/SoC/Ara配置 | `src/config/{cv64a6_imafdcv_sv39_config_pkg,cheshire_pkg,cheshire_ara_asic_cfg_pkg}.sv`，共同wrapper`src/top/cheshire_ara_asic_soc.sv`，`src/cheshire_soc/cheshire_top/cheshire_soc.sv`的CVA6/Ara消费者。固定包只覆盖`DefaultCfg.Ara=1`，经`gen_cva6_cfg()`、`build_config()`和`CHESHIRE_TYPEDEF_ALL`派生；CPU PMP由profile的8覆盖为SoC的0。CPU profile VLEN64是CVA6虚拟地址位宽字段，定义见`cva6/core/include/config_pkg.sv:59–60`；Ara VLEN2048是向量寄存器长度，沿Ara实例参数和dispatcher的`VLENB=VLEN/8`消费，两者不能统一数值 |
| TB/DPI/模型与当前支持边界 | `src/tb/src/{tb_cheshire_soc,fixture_cheshire_soc,vip_cheshire_soc}.sv`、`elfloader.cpp`、`src/tb/models/`。fixture读取同一Cfg，输出`E01_CFG/E01_SOC_CFG/E01_CPU_CFG`，并在`:171`检查当前固定组合；UseDramSys=0使用AXI RAM模型。profile/WT/真实decoder、2 lanes/2048、LLC128KiB、AXI48/64、DMA在途16沿现值说明；SelectedCfg只作历史对应，不能证明CPU profile |
| 软件、启动与镜像 | `sw/Makefile:8–33,35–122`、`sw/lib/crt0.S`、`sw/link/{common.ldh,spm.ld,dram.ld,rom.ld}`、`sw/include/{params.h,dif/dma.h}`与选定测试。库/测试列表、ISA/ABI/LTO/链接方式及新输出边界均在Make；lane读取`cheshire_pkg.AraNrLanes`，地址/容量并不自动同步。区分硬件生成Boot ROM与新HelloWorld ROM载荷/raw/memh，说明49152 B镜像、LMA0/VMA0x10000000及offset0 |
| 修改后选哪些现有测试 | `sw/Makefile`所列测试、`src/tb/regressions/{idma/jobs,llc/probe.tcl,slink_rx/}`及`provenance/2{b,c}_run_commands.json`、`2d_summary.json`。CPU/Ara用CSR/RVV/访存原子/fmatmul；启动/链接用HelloWorld及SPI；DMA/HAL/LLC按实际改动选择成功回归、后端job和三项已知失败对照；互连/Serial RX按需选三项RX。表中写明每组检查内容，不能把修改源码默认扩成整套回归或新增测试 |
| 许可、来源和历史证据 | `LICENSES/`、`provenance/{source_manifest,reference,generation_inputs,2d_summary,cleanup_20261022}.json`及`provenance/generation/README.txt`；现有活动清单含documentation条目。历史原始输出按归档`index.json`及原目录前缀定位，不成为日常命令的输入；生成资料不参与日常构建 |

#### 7.9.3 已发现的文档差异与流程限制

- **干净工作区已确认。** 根下只有`README.md`、`LICENSES/`、`provenance/`、`src/`、`sim/`、`sw/`；`docs/`、`sim/work/`、`sw/build/`、`sim/reference_inputs/`均不存在。旧2D摘要及根README个别历史句子仍指向清理前位置，须结合最新清理说明读取；新文档给可用归档位置，不回写旧摘要或恢复产物。
- **软件当前不提供复用输出的增量构建。** Make在解析时拒绝已存在的OUT，且OUT须位于`sw/build/`内；硬件编译及运行也拒绝已有输出目录。影响是改软件后要换新目录重建，文档按现状说明，不删除保护或顺手优化Make。
- **参数化不等于支持配置。** Make只接受`AraNrLanes=2`；fixture明确限制Ara开启、2 lanes/2048、CPU RVV/VLEN64和UseDramSys0。其他组合未验收，不提供可放心切换的候选配方，也不以写文档为由移除这些检查。
- **软硬件只有部分联动。** lane由Make自动读取，但`common.ldh`的地址/存储空间和`params.h`常量仍是人工维护。文档提醒改地址/容量/启动时检查对应位置和影响，不能声称已有统一自动生成。原LLC/SPM、地址、中断、外设与启动语义保持，不把后续产品DDR/GB方案写成现状。
- **参考指南适用范围不同。** 本地`SERVER_SIMULATION_GUIDE.md`的Bender、`update_vsim_src`、`start.cheshire_soc.sh`、参考工程路径/旧ELF以及“独立提取未验收”等旧状态不能复制。当前独立入口无已交付的波形采集Tcl，普通编译也没有参考指南中的显式PLI配置；缺少独立工程FSDB/GUI全流程实测依据。按需调试先说明已有日志、CPU trace、map/dump及LLC只读UCLI probe，波形能力标明未确认，不新增采集入口、不为此改脚本或默认启动验证。

结果说明必须对应当前run.py：正常0、目标失败1、断言/仿真错误2、其他simv非零3、未完成4、墙钟超时124；同时查看`target_rc/simv_host_rc/entry_host_rc`、完成标志和错误内容。运行前参数/路径拒绝没有本次有效result，不能套用仿真结果表。simv0不证明目标成功。原ROM仅已定位字节6/7的两读两写padding事件按既定范围接受功能结果，保留入口2；其余错误不豁免。default_long/unaligned16/dense32仍是三项已知失败，不写成全部通过或通用无死锁；stub勿用，FS Dirty原因及libgcc特定高地址限制保持。模型仿真不能代表SRAM宏、DDR PHY、ASIC综合或流片验收。

#### 7.9.4 阶段B准确写入范围、验证与停止点

用户明确同意本方案后，服务器拟写范围仅为：

1. 新增`/home/zhaowy24/CheshireAra/docs/README.md`。
2. 新增`/home/zhaowy24/CheshireAra/docs/CONFIGURATION_AND_DEVELOPMENT.md`。
3. 修改`/home/zhaowy24/CheshireAra/README.md`，仅作上述用户文档的必要导航调整。
4. 更新`/home/zhaowy24/CheshireAra/provenance/source_manifest.json`：按现有documentation记录方式登记两份新正文并更新根README当前哈希，保留原来源/版本/差异字段及其他条目；不新建文档管理机制，不改历史验收摘要。

本地仅按需更新本节与同主题handoff的交付状态。写入前重查目标、并行变化及对应来源条目；出现未知已有内容先读取，不覆盖。范围不包括`src/config/README.md`或任何脚本、RTL、软件、配置、参考工程、工具、归档和已清理目录。

阶段B逐条静态对照命令参数、当前源码/消费者、路径/相对链接、输出拒绝覆盖、结果判据及适用测试；检查代码块命令语法、文档间一致性、来源条目与最终文件哈希，并核对仅约定文件变化。**本轮未发现必须实跑的文档验证命令，阶段B不预设编译、仿真或整套回归。** 2B–2D结果明确标为复用历史验证，本轮及阶段B静态检查不冒充新运行。若写作发现确须实跑才能回答的具体问题，先说明命令、必要性及影响，未获该范围授权不执行。

**阶段A交付后停止，等待用户明确同意撰写。** 阶段B交付入口和简短阅读建议后停止；用户使用前不主动优化流程或入口。

<a id="user-documentation-result-20261022"></a>

### 7.10 独立工程用户文档交付（2026-10-22，阶段B）

用户审核阶段A后明确“开始实施”。执行前再次检查本地HEAD/status及服务器目标；输入仍为本地`c9abbb489`和服务器清理后的实际工程，未用本地不同版本源码替代。服务器`docs/`和旧输出均不存在；先在本地`/tmp/e01-user-docs-20261022-h4f9ofkf/`暂存指定源码快照、既有文件哈希和草稿，写入前再次确认正式工程文件未发生并行变化。本地子Agent分别撰写第二份指南、只读复核命令/配置/判据；主Agent统一修改与服务器写入，未委派服务器Agent。

| 服务器实际交付路径 | 用途及变更 |
| --- | --- |
| `/home/zhaowy24/CheshireAra/docs/README.md` | 新增196行用户入口：干净工作区硬件/软件重建、新ELF及可选原ROM/SPI运行、目录/工具、产物、结果与限制 |
| `/home/zhaowy24/CheshireAra/docs/CONFIGURATION_AND_DEVELOPMENT.md` | 新增265行配置/修改指南：有效配置和消费者、四类选项分层、五类修改的重建/测试范围、现有定向命令及按需调试 |
| `/home/zhaowy24/CheshireAra/README.md` | 仅增加上述两份文档的导航，原正文逐字保留 |
| `/home/zhaowy24/CheshireAra/provenance/source_manifest.json` | 原960条记录只更新根README当前哈希，另追加两条documentation记录，共962条；原来源/版本/源哈希和其他记录保持 |

**实际检查与结果。** 文档按当前compile/run.py/Make、配置/SoC/fixture/VIP、启动/链接及已有验收记录逐项核对；检查了17个Make ELF目标与示例输入、当前静态分组清单、输出拒绝覆盖、有效配置与手工地址/容量对应关系。首次最终检查脚本误用服务器默认`python3`，因不支持`Path.is_relative_to`退出；随后直接用工程既有`python3.9`重读最终文件检查通过，没有修改/安装工具。最终11段Bash代码块经`bash -n`解析、36个相对链接及显式锚点检查通过；只解析命令，没有执行这些构建/运行命令。最终文件与草稿逐字一致，962条来源记录的当前哈希均匹配。

服务器实际差异仅为新增两份指南、修改根README和来源清单，没有删除文件；其他1019份既有文件哈希保持。旧`sim/work/`、`sw/build/`、`sim/reference_inputs/`仍不存在，未恢复搬迁工程、读取/解包整个验收归档或修改参考工程/外部工具。未改脚本、RTL、软件、配置或工作流程。临时快照、写入结果和最终静态检查记录保存在上述本地`/tmp/`目录，不作为工程运行依赖，也未在服务器新增报告或管理入口。

**证据边界与停止点。** 两份正文区分本轮静态检查与历史2B–2D验证，保留三层状态及0/1/2/3/4/124、原ROM两读两写限定接受/入口2、三项LLC失败、stub勿用和模型/工艺边界；没有将波形全流程、其他参数组合或产品新拓扑写成已验收。**本轮没有编译硬件/软件或运行仿真。** 交付后先读`docs/README.md`第1节上手，再按需查第二份；本阶段完成并停止，不主动优化入口或流程。

<a id="entry-scripts-result-20261022"></a>

### 7.11 compile/start 入口简化实施结果（2026-10-22）

**用户决定与授权：**用户明确要求恢复简洁的compile/start、允许覆盖旧输出并打印WARNING、改善脚本注释和排版；讨论中选择“软件单独Make”和“Python仅用于内部结果解析”，随后明确要求实施完整计划。本条替代此前保留run.py和每次新目录的要求；未扩大RTL、参数、依赖、启动协议或LLC修复范围。

**输入及修改：**本地HEAD仍为`c9abbb48946fe3a7244bfb3159919b7c9731cb59`，服务器正式工程`/home/zhaowy24/CheshireAra`。写入前未发现构建/仿真并行任务，待改入口与文档已备份，源码按当时1023份非输出文件哈希比较。主Agent通过WSL的Windows SSH实施，未委派服务器Agent。

- `sim/scripts/compile.cheshire_soc.sh`默认`TARGET=soc`、`BUILD_DIR=sim/work/$TARGET`，仅执行vlogan；全部分组成功后保存原来源快照。编译失败撤下旧快照，start不会使用该失败构建。51条完整vlogan命令逐条相同，包括源顺序、宏和include。
- 新`sim/scripts/start.cheshire_soc.sh`沿固定版本官方“vcs展开→simv运行”分工，保留原展开参数及四个top。默认经Serial Link装载`sw/build/default/helloworld.elf`；参数集中在开头，可环境覆盖；普通运行600秒、串行、无波形。直接Bash启动，tee实时显示和保存日志，分别捕获simv/tee状态。
- 原`run.py`迁为`check_result.py`并移除旧启动入口；仅处理日志、原三层分类和JSON。保留原字段、退出0/1/2/3/4/124，`entry_sha256`对应start，新增`parser_sha256`。Python按函数、docstring、独立import、四空格和空行整理；Bash补充参数/阶段说明、数组和路径引用。
- Make默认复用`sw/build/default`并读取已有`.d`依赖，加入Makefile、lane输入和现有链接脚本依赖；直接编译/链接用例明确依赖目标。重新生成静态库，避免已移除的源码成员残留；ISA/ABI/编译选项和23单元/17ELF目标保持。命令行换工具链或选项时用`make -B`，不新增配置缓存。
- 复用目录打印WARNING，无需确认或新目录名。仅处理当前运行目录已知result/log/hart0 trace，不递归清空目录；输入缺失、展开失败或编译失败不启动旧结果。BUILD_DIR/RUN_DIR限于工程sim/work下，固定输出拒绝符号链接，其他历史目录和未知文件不清理。
- 更新服务器根README、原两份docs及现有来源清单。新增start、迁移解析器是本次需要；没有新增包装器、配置文件、调度器或自动归档机制。临时验证脚本只在`/tmp`，不是工程入口。

**实际验证：**默认`make -C sw`、`./sim/scripts/compile.cheshire_soc.sh`、`./sim/scripts/start.cheshire_soc.sh`实际完成，且在同一默认目录重复Make/compile/start。四种top均完成编译、展开和代表用例。10次串行仿真如下，非PASS分类按原规则保留：

| 用例 | 次数 | 目标 / simv / 入口 | 结果 |
| --- | --- | --- | --- |
| 默认HelloWorld（初次、重复、最终） | 3 | 0 / 0 / 0 | PASS；最终默认目录保留PASS |
| `BINARY=sw/build/default/vector_fixed.elf` | 1 | 0 / 0 / 0 | PASS |
| `BINARY=sw/build/default/rvv_negative.spm.elf` | 1 | 41 / 0 / 1 | 正确识别TARGET_FAIL，不能只看simv0 |
| `SIM_TIMEOUT=1`、CSR ELF | 1 | null / 124 / 124 | 正确识别TIMEOUT，约1.073秒 |
| `BOOTMODE=2`默认SPI镜像 | 1 | 0 / 0 / 2 | 452.634秒完成；ASSERTION_OR_SIM_ERROR保持 |
| `TARGET=idma_ideal`、默认issue115_aw0_rw0 job | 1 | 0 / 0 / 0 | PASS |
| `TARGET=idma_throttle`、同job | 1 | 0 / 0 / 0 | PASS |
| `TARGET=slink_rx`、slink_cpu0、CASE0 | 1 | 0 / 0 / 0 | PASS，64KiB代表用例 |

SPI日志核对4条实际失败断言：读byte6/7均为`xxxx0000000f0f0f`，写为`gen_invalid_write_assertion[6/7]`；目标完成，无新增READ_META_INVALID。仅接受既定padding事件，不豁免其他返回2。本次未重新逐字比对全部49152字节搬运，不把历史完整比较冒充本次检查。

软件依赖检查使用`make -n -W <绝对输入路径>`：头文件触发18次编译及后续链接，spm.ld触发14次链接且无编译，Makefile/lane输入各触发35次编译和后续链接；没有为了测试修改生产头文件或RTL。实际无改动重复Make保持52个对象/ELF时间戳；最终库规则重建后17个ELF和两份SPI镜像哈希保持，23个库成员与对应对象逐字一致，当前所测输入匹配result记录。一次额外“静态库整文件哈希保持”检查未通过；该工具生成的ar头含非零构建时间，故归档字节不作为稳定判据，转以成员内容及最终ELF/镜像核对，未擅改AR标志。首次失败和检查说明保留。

临时模拟VCS/simv检查覆盖所有结果分类（含137→124）、四目标、参数含空格的转发、重复覆盖、未知文件保留、输入缺失、非法参数、展开/编译失败后停止、tee写日志失败；这些是入口逻辑检查，不冒充硬件仿真。最终Bash/Python语法、12段文档Bash、36个相对链接/锚点通过；963条来源哈希全部匹配。原VCS命令除变量名和所属脚本外保持。

**范围与证据：**最终非输出差异为六份既有文件修改（compile、Make、根README、两份docs、来源清单），新增start/check_result、删除已备份run.py；其余1016份原文件哈希保持，RTL/配置/软件源未改。参考工程、TTY、工具和旧验收归档未写入。本轮新产物保留，不恢复搬迁副本、不运行Bender。

- 正式工程本次检查输出：`~/CheshireAra/sim/work/entry_checks_20261022/`，含逐次日志/JSON、`summary.json`、`static_checks.json`、`mock_checks.log`、依赖预演、`make_final_check.json`和`final_checks.json`。这是本次手动保存的检查结果，不是新增自动归档流程。
- 服务器修改前备份及中间检查：`/tmp/e01-entry-20261022-zm5iis9_/`；本地草稿、检查脚本及原共享文档备份：`/tmp/e01-entry-20261022-txxkykpx/`。旧2B–2D归档保持不变。
- **实施完成并停止。** 未重跑全部回归，未再次排查三项LLC旧失败，未改变ROM限定告警、FS Dirty、高地址libgcc和ASIC/PHY/宏验证边界。后续按实际使用问题处理。

<a id="config-entry-merge-defaults-20261022"></a>

### 7.12 配置入口合并与默认值变更（2026-10-22）

**范围与输入。** 用户明确授权实施：取消独立配置包，将必要定义合入已有 `cheshire_pkg.sv`，保持当前有效硬件行为。由本地 Agent 经 WSL SSH 修改 `/home/zhaowy24/CheshireAra`，本地子 Agent 只读审查；未委派服务器 Agent。本地输入 HEAD 为 `c9abbb48946fe3a7244bfb3159919b7c9731cb59`，既有未提交修改保留；正式工程没有 `.git`，以修改前备份、来源哈希和现有补丁记录实际差异。本节取代此前“单独固定配置包”的活动组织方式，历史验收记载保持原貌。

**默认值备忘（本次只有这一项改变）：**下表路径相对服务器正式工程根目录。

| 文件/字段 | 原始默认值 | 修改前有效值及来源 | 修改后值及位置 | 原因 | 恢复时需处理的关联项 |
| --- | --- | --- | --- | --- | --- |
| `src/config/cheshire_pkg.sv` 的 `DefaultCfg.Ara` | 上游及合并前默认0 | 1；旧 `src/config/cheshire_ara_asic_cfg_pkg.sv::fixed_cfg()` 从 DefaultCfg 复制后令 `ret.Ara=1` | 1；直接在 `cheshire_pkg::DefaultCfg` 维护，`Cfg=DefaultCfg` | 合并配置入口，保持已启用 Ara 的有效基线 | 若恢复上游默认0但仍启用 Ara，须同时恢复明确的集成覆盖及其消费者/编译关系，不能只改这一行；真正关闭 Ara 还涉及 fixture 基线检查、软件和测试，是另一个功能变更任务 |

**保持项。** CPU profile `cv64a6_imafdcv_sv39`/WT、真实 decoder、Ara 2 lanes/VLEN=2048、CPU profile VLEN=64、UseDramSys=0 保持；LLC/SPM、DMA、地址、中断、外设、原生成 Boot ROM 及初始化语义保持。它们不是本次默认值修改项。

**定义迁移与实际文件。** `cheshire_pkg.sv` 加入现有 typedef 头文件，在 DefaultCfg 后提供原 `Cfg`、`CpuUserCfg=gen_cva6_cfg(Cfg)`、`CpuCfg=build_config_pkg::build_config(CpuUserCfg)` 及 `CHESHIRE_TYPEDEF_ALL(, Cfg)`。wrapper 和 fixture 仅删除旧包 import；compile 仅删除旧包路径并调整对应注释，随后删除 `src/config/cheshire_ara_asic_cfg_pkg.sv`。没有新增配置层或参数。更新服务器根 README、两份 docs、`src/config/README.md`、现有 `provenance/source_manifest.json` 和 `provenance/patches/extraction_adaptations.patch`；来源清单将旧包原记录保存在 `cheshire_pkg` 的 `merged_from`，上游 source/revision/hash 保留。start、check_result、Make、CPU profile 和其他 RTL/软件源未改。

**依赖与静态检查。** build_config_pkg 已在原组27，早于组65的 cheshire_pkg；原 include 路径足够，无需重排。宏内包限定引用指向先行定义，不引入依赖环；SoC 参数 Cfg 和 SoC/VIP 本地类型仍按局部声明解析。正式源码无其他 DefaultCfg 直接消费者，Make 只解析未改的 AraNrLanes。51条完整 vlogan 命令除旧配置文件一项外逐条一致；逐项检查 DefaultCfg 初始化条目，只改变 Ara。活动源码/脚本无旧包引用，Bash 语法及文档链接检查结果见本次验证输出。

**实际验证。** 在新输出分别重建修改前后 `soc`、`slink_rx`，复用同一组正式工程 ELF/镜像；未重建软件或调用参考库。临时 probe 比较完整有效 SoC、CPU User、最终 CPU 配置和30项接口类型位宽；仅 DefaultCfg.Ara 的0→1符合预期。选择以下用例验证启动、CSR/向量、SPM/DDR访存、DMA与共享 fixture/接口，不重跑全部历史诊断：

| 用例 | 修改前：目标 / simv / 入口 | 修改后：目标 / simv / 入口 | 结果 |
| --- | --- | --- | --- |
| HelloWorld | 0 / 0 / 0 | 0 / 0 / 0 | PASS |
| 非 stub CSR（vstart/CSRs） | 0 / 0 / 0 | 0 / 0 / 0 | PASS |
| RVV 边界/浮点，5976项 | 0 / 0 / 0 | 0 / 0 / 0 | PASS |
| SPM/DDR 访存原子，572项 | 0 / 0 / 0 | 0 / 0 / 0 | PASS |
| 既有 dma_checked 小规模搬运 | 0 / 0 / 0 | 0 / 0 / 0 | PASS |
| 原 ROM/SPI 启动 | 0 / 0 / 2 | 0 / 0 / 2 | 限定 padding 两读两写告警保持；功能结果按原限定范围接受 |
| Serial RX CASE0，64 KiB | 0 / 0 / 0 | 0 / 0 / 0 | PASS |

共14次串行用例仿真，12次 PASS、2次 SPI 限定告警；每例600秒上限，无波形。14对 CPU trace 经实际字节比较一致，SHA-256也一致，目标输出、三行有效配置及输入绑定一致。两种目标的编译/展开告警类别、数量和完整告警块一致；SoC 的 KDB-OPTIONS 来自本次临时 probe 未加 -kdb，两侧辅助命令相同，仅影响调试信息，不作为新增硬件告警。SPI 的目标/仿真器均0、入口仍2，完整错误列表一致；恰为read byte6/7的 `xxxx0000000f0f0f` 及write byte6/7四条既定断言，无新增 READ_META_INVALID。此次未另外重做49152字节镜像搬运逐字检查，不把历史该项检查写成本次执行。未运行独立iDMA后端：它不消费本次迁移的配置/类型；SoC小规模DMA及Serial RX用于覆盖相关集成通路。

**证据与保护。** 本次构建/运行/对照结果在 `~/CheshireAra/sim/work/cfg_merge_20261022/`；`comparison.json`、`final_checks.json` 与各 `before_*`/`after_*` 目录保留实际命令、结果、输入绑定、日志和 trace。服务器修改前备份 `/tmp/e01-cfg-20261022-5difdhgr/before/`；本地快照/草稿/共享文档备份 `/tmp/e01-cfg-20261022-joge44so/`。初次临时 probe 使用了错误的 AXI 通道类型名，修正为宏实际的 `*_chan_t` 后继续，原失败日志保留；此失败来自验证辅助代码，未修改生产 IP。实际差异仅上述10份修改和旧包删除，其余1013份非输出文件哈希不变；5份原soc关键产物及18份ELF/镜像哈希保持，现有输出未覆盖。962条活动来源哈希、37个相对链接/锚点及12段文档Bash语法检查通过。参考工程、.bender、历史验收归档、TTY工程和外部工具未写入；本地仅更新本计划、E01交接、PROJECT_STATE和AGENT_TASKS，没有同步本地RTL。

**停止点。** 本次仅调整配置组织；没有开放新组合、关闭 Ara 或修复 DMA/LLC。原 SPI 限定告警、LLC 旧失败、FS Dirty 和高地址 libgcc 限制保持。未执行 ASIC 综合、宏/PHY 或板级验收。完成后停止，不自动调整其他参数或工作流程。

### 历史：2026-10-18 的分步确认与交付

以下保留原计划及当时的编号，不是当前待执行步骤；现行步骤2只采用上方2A–2D表。旧“参考验收全部无缺陷”的文字不覆盖2026-10-21用户接受基准及保留限制的决定。

| 步骤 | 动作与写入范围 | 通过后交付 |
| --- | --- | --- |
| 0（本轮） | 只读本地/服务器；只新增本地 E01 方案、证据摘要和主题交接 | 当前事实、目录映射、实施/验收方案；无工程运行结论 |
| 1（已执行） | 仅在 `~/CheshireAraPULP/_e01/preflight/` 新建最小工具链探针；复制必要小输入；实际编译/链接/反汇编 RISC-V 标量/RVV 和本机 C++/ELF loader | [结果](../reports/toolchain_preflight.md)：SPM与DPI源编译通过，libgcc特定高地址链接失败未关闭；不编译完整SoC，不写提取目录 |
| 2（同版本方向已确认，执行待确认） | 从GitHub官方仓库重新获取当初 `mp/ara-pulp-v2` 的历史提交 `e040b7bbc…` 及其锁定依赖，在 `~/CheshireAraPULP` 搭建环境并重建；先核实官方可获取性。原本地快照只用于差异审查，不作复制源；保留preflight证据 | 官方历史提交与依赖锁、差异分类、服务器环境和必要补丁；具体执行子步骤重新报告，尚不称参考验收通过 |
| 3 | 优先用参考工程官方入口进行 VCS 编译、展开及许可/联编检查；出现错误时按需增加最小探针；依次运行标量、ROM启动、RVV、访存/原子 | 参考向量基线的实际 PASS/FAIL、日志及缺口；失败先定位，不带病称对照基线 |
| 4 | 在 `~/CheshireAra` 提取集中配置/类型/共同 wrapper、静态清单、软件和来源记录；保持原基线重建并运行相同测试 | 独立工程与参考结果对照、可复制命令、配置支持状态和已知限制 |
| 5 | 复制提取工程源码到预先检查不存在的独立验收路径，使用全新输出重新构建 RTL 和软件并重跑 | 搬迁验证与依赖审计；最终交接和最小下一步 |
| 6（基线独立验收后，另行分步确认） | 按开放范围选择参数试验，独立构建并进行定向/候选回归和应用比较；工艺资料具备后评估面积、时序和功耗 | 有效配置及输入快照、分层验证状态、性能/物理实现证据和未关闭项；不预定最终参数 |

拟用最终入口为 `bash sim/scripts/compile.sh`、`bash sim/scripts/run_tests.sh` 与 `make -C sw`；这些是待实现接口，**目前不能当已可执行命令**。每步执行前交付实际脚本/参数，日志按步骤与测试分目录，不覆盖失败证据。

资源上限建议：单个 VCS 构建，编译并发最多 2，测试串行；探针单条 60 秒、全量编译/展开各 30 分钟、单个仿真默认 10 分钟硬超时，SPI 启动如需更长先报实际进展再调整。使用后台作业/短轮询保持可报告，避免长阻塞等待。默认不启用 FGP/全量 FSDB，首错定位后才加必要波形。

独立性审计覆盖所有执行中的清单、脚本、软件依赖、include、符号链接及构建实际输入；原路径允许出现在 provenance 的来源记录中，不允许参与执行。搬迁位置从空输出重新构建，记录实际访问/编译输入；不重命名、移走或限制访问原工程/TTY 以做验证。

历史阶段 1 的下一步曾为表中第 2 步，不能据此重新下载或覆盖现有参考工程；当前实际进度和最小下一步以页首 E01 交接为准，仍按用户逐步确认执行。第 1 步工具链检查仅覆盖所测用例，不等于运行库全部适配；通用模型仿真通过不等于 ASIC 工艺、真实 DDR 或流片验收。

## 8. 官方重新获取与本地快照复现的比较（来源调整）

用户担心WSL时期工具链/环境报错后存在绕过，因此选择官方GitHub来源。源代码来源、主机环境、交叉工具链/运行库是三个独立对象：复制源码不等于复制WSL安装环境；从GitHub获取源码也不自动修复服务器 `/opt/riscv` 的S01-T01。

| 维度 | 原方案：本地实际快照 | 新方向：官方固定版本重建 |
| --- | --- | --- |
| 首先证明什么 | 当前本地实现能在服务器重新构建和运行 | 明确的官方原始版本组合能在可记录的环境中构建和运行 |
| 本地修改 | 随源码带入，逐项归档后验证 | 默认不带入；只作问题定位参考，确有需要才形成新的最小补丁 |
| 版本控制 | 当前磁盘内容＋主仓库HEAD＋依赖SHA | 官方仓库URL＋主工程提交＋依赖锁/子模块提交＋后续补丁 |
| 环境问题 | 在服务器重新搭建，仍可暴露问题 | 同样需要独立准备/验证，clone本身不包含已验证工具环境 |
| 成本/风险 | 通常迁移较快，但继承历史源码绕过 | 下载/版本配套/生成步骤较多，旧错误可能重新出现；问题来源更容易区分 |
| 与现有FPGA的关系 | 源码连续性较强，但没有重新板测保证 | 有意建立新来源基线；旧HelloWorld不能转移成新基线证据 |
| 后续提取 | 从实测本地快照参考提取 | 从实测官方重建参考提取；两者最终都需静态清单和离线独立验收 |

本轮定向差异证据：

- 本地首次保存提交 `4175f440144fba38a2c7d3b7411e26b51d4c5e56` 的父提交是 `e040b7bbc7851a37faff3c4657ff8d656cc6e20a`；本地历史 `origin/mp/ara-pulp-v2` 也指向后者。它是待核实的官方来源候选，不宣称当前远端分支仍在该位置。
- 该候选的 `Bender.lock` 指向 Ara `2895ba907e9eb14b3464609dc791a969d159a7c3`、CVA6 `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c`，与本地快照记录吻合。可以先评估同版本官方重建，避免同时引入全套升级。
- `git diff e040b7bbc HEAD -- sw/sw.mk` 确认关闭 GPT 镜像规则及其测试构建项；根HelloWorld有VS/printf改动。不能把所有本地差异统称工具链错误或硬件修复。
- Ara子仓库实际HEAD为上述提交，`git diff`确认8个受跟踪文件修改：板卡默认VCU128→VCU118、`eew/printf`默认参数、C函数/类型和打印相关修改、`vector_helloworld.c`加入O0并将一处向量store intrinsic替换为内联汇编。原始报错日志未找到，本轮不推断每项修改的必要性和正确性。
- 本轮查看的CVA6子仓库没有工作树差异；根hw/TB源相对该父提交也未显示差异。此有限检查不代表已审计所有26项依赖或全部生成文件。

“从官方获取固定版本”和“直接取最新main”必须分开：最新版本可能更换CPU集成、参数和构建配方，属于另一个版本迁移决策。当前在线 [Getting Started](https://pulp-platform.github.io/cheshire/gs/) 已要求Python>=3.11并使用pyproject.toml/uv.lock；本地版本为Python>=3.9和requirements.txt。不能拿最新文档套用旧提交，或把旧固定CPU profile默认认为最新主线仍支持。

建议把下一步拆成可审查的小步骤：先确认官方Ara集成提交及配套锁文件，列出本地差异处理表和该版本所需环境；随后按确认的组合从官方获取，默认不回放本地改动，只执行当前裸机向量/VCS任务需要的官方步骤。必要修改以原始错误、原因、补丁和验证逐项记录。默认不重建LLVM/Spike/Linux整套工具链，也不因为本地曾绕过可选目标而强迫当前任务完成它们。

后续用户已澄清上述版本选择：就是当初克隆的 `mp/ara-pulp-v2`。据此，`e040b7bbc…` 从比较时的候选成为本地历史定位的重建基准；获取时核验完整SHA和配套锁文件，不能只checkout可能已经移动的分支名。Ara/CVA6沿原组合，既定CPU profile、2 lanes/VLEN=2048和首次提取范围保持。与本地源码的预期差异主要来自本地后来加入的修改、生成物及环境，但仍须逐项核对，不能事先声称完全相同。

第1步工具链证据保留：若新版本继续使用同一服务器安装及相同ISA/ABI，相关检查仍有参考价值；若更换工具链，必须针对新安装重跑，不能沿用旧通过结论。独立提取工程日常无Bender/无联网要求不变，官方参考初次获取需要联网与受控依赖解析并不冲突。
