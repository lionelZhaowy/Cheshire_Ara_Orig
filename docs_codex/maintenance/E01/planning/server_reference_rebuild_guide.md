# Cheshire + Ara：服务器同版本重建速查

<a id="cross-project-sync-rules"></a>

## 两工程目录与代码同步规范（2026-10-25 用户确认）

正式工程F为 `/home/zhaowy24/CheshireAra`，采用集中配置、wrapper、静态编译入口和独立软件构建；参考工程R为 `/home/zhaowy24/CheshireAraPULP`，保留官方目录组织及本地修复，供来源对照、补丁复现与参考验证。**保留两套布局，不为同步方便把R重构成F，也不把F恢复成R的布局。同步对象是本次授权的代码修改及必要配套，不是整个目录树。** R包含本地修改，不等同于未经修改的官方代码。

### 常见路径映射

下表是定位规则，执行时仍须核对当前文件、调用关系和来源记录；不表示表内整组文件都获准同步。

| R中的位置 | F中的位置 | 同步注意事项 |
| --- | --- | --- |
| `.bender/git/checkouts/<组件>-<固定后缀>/…` | `src/cheshire_soc/<组件>/…` | 对已提取文件按组件内相对路径定位；后缀从现场确认，不能整包复制依赖或把`.bender`视为缓存清理。 |
| `hw/…` | `src/cheshire_soc/cheshire_top/…` | `cheshire_pkg.sv`是集中配置例外，见下项。 |
| `hw/cheshire_pkg.sv`、CVA6所选配置包 | `src/config/cheshire_pkg.sv`及对应CPU配置包 | 保留F有效配置、类型及参数派生；不能直接用R文件覆盖。 |
| `target/sim/src/…`、`target/sim/models/…` | `src/tb/src/…`、`src/tb/models/…` | fixture/VIP可能含F wrapper、配置引用及层级适配，须比较修改内容后合并。 |
| `_e01/…`中的已采用独立TB、探针及job输入 | `src/tb/regressions/{slink_rx,llc,idma}/…` | 来源分散，按现有清单逐项定位；历史实验、日志和产物不整体搬入。 |
| `sw/tests/`或`_e01/…`中的维护用例 | `sw/tests/regressions/…` | 维护测试沿用F分组；日常测试仍在`sw/tests/`，Ara可选测试仍在`sw/tests/ara/rv64uv/`。 |
| `sw/link/p4_single.ld`、`sw/link/p4_multi.ld` | `sw/link/regressions/`下同名文件 | 修改路径引用时保留链接地址及布局；不是一般链接脚本的整体搬迁规则。 |
| R的Makefile、VCS脚本及测试入口 | `sw/Makefile`、`sim/scripts/` | 合并必要规则或选项，不复制R整份入口；保留F静态清单及统一compile/start选择独立TB的组织。 |

### 每次同步须遵守的边界

1. **确定实际输入。** 检查本地及R的HEAD、`git status --short`，核对F现有差异和相关文件的内容、哈希、权限。修复可能尚未提交，HEAD不能代替已验证工作区版本；当前R文件也不能仅凭路径认定与历史验收版本相同。
2. **先备份再合并。** 保存受改文件及新增文件原先不存在的事实，记录可恢复位置；写入前再比较，避免覆盖并发修改。保留F的`src/config/`、`src/top/`、wrapper、静态入口、既有TB层级及已接受修复，除非本次授权明确要求改动。
3. **复用现有软件组织。** F日常`all`、维护`regressions`及可选Ara构建组分别保留；维护用例加入已有`regressions`，不因同步引入重复分组或新的运行框架。ELF名称、编译期宏和运行参数分别核对；不要将R的默认目标集合覆盖到F，也不要因新增ELF就新增TARGET。
4. **维护当前来源，保留历史。** 复用F `provenance/source_manifest.json`中的源路径、目标路径和维护记录，更新相关最终文件哈希，保留原来源信息。按现有用途更新相关patch或输入记录，不另建一份平行映射表；`provenance/history/`、原始来源清单及旧验证快照不重写为本次状态。
5. **在目标工程验证。** 获得运行授权后，从F自身入口在新输出目录重新构建受影响的软件与仿真器，串行执行对应测试和相关回归；普通运行无波形，每例默认600秒。检查目标结果、仿真器/入口判定及断言，R的通过结果不能代替F验证。同步文档中的ELF/TARGET及构建组说明，并区分本次运行、历史结果和未测范围。
6. **不扩大同步范围。** 不调用Bender、升级依赖、重生成原Boot ROM、搬入参考工程的工具环境或历史产物；不修改参考工程来消除路径差异，不清理旧验收归档。同步授权不自动包含Git提交、推送、综合或板测。

本规范由根`AGENTS.md`导航，后续对话引用本节并列出本次文件即可，无须每次重述全部目录差异。它不代替具体任务授权。2026-10-25制定本规范时P6仍仅在R完成，F尚未同步；修复与测试清单见[当前P6报告](../reports/official_pr_failure_fixes_review.md#p6-fix-20261025)。

<a id="llvm-default-20261026"></a>

## LLVM默认软件链当前状态（2026-10-26）

已先在R完成LLVM适配验证，再同步并独立验证F；目标裸机软件现默认Ara配套LLVM20.1.0/newlib/compiler-rt，输出`sw/build/llvm_p7`，不依赖目标GCC/libgcc。R38/F49新ELF、40/51主记录分别36/47正常PASS，SPI原限定告警/保留LLC未完成/两个预期负例分别报告；旧工具及产物保留，宿主g++仍用于VCS。随后R八文件LLVM修改已提交并推送[`6f2b2a3b`](https://github.com/lionelZhaowy/CheshireAraPULP/commit/6f2b2a3be50eeb15eb93c0ada2164029a102c94c)，远端main读回一致；原两处诊断修改保留，其他工作区内容见[发布记录12.4](llvm_toolchain_migration_plan.md#llvm-github-push-20261026)。

日常正式工程请读服务器`docs/README.md`及`docs/CONFIGURATION_AND_DEVELOPMENT.md`；本页的官方重建步骤及下方GCC默认描述属于历史，不代替当前入口。精确修改、实际运行、两地备份和回退见[LLVM迁移第12节](llvm_toolchain_migration_plan.md#llvm-resume-20261026)。没有调用Bender、重生Boot ROM、修改RTL或实施综合。

<a id="p7-reference-formal-sync-20261026"></a>

## P7当前同步结果（2026-10-26）

R四文件提交[`4e30feec`](https://github.com/lionelZhaowy/CheshireAraPULP/commit/4e30feec288f0157f2ae6c0fb9ea736314de902e)已在personal/main读回；此前先完成F独立重建和17次串行PASS，68组/13416项0错。F维护组31、日常7/Ara11，布局及静态入口保持。输入/逐项结果/两地备份与恢复见[报告13.6](../reports/official_pr_failure_fixes_review.md#p7-reference-formal-sync-20261026)；正式工程日常操作仍以服务器docs/README.md为准。该P7发布阶段默认GCC13.2；当前LLVM默认迁移已完成，见上节。下方P6为历史发布记录。

<a id="p6-reference-formal-sync-20261025"></a>

## 2026-10-25 P6已上云并完成F独立验证

R P6六文件已提交并正常推送[个人仓库`cb20a03c`](https://github.com/lionelZhaowy/CheshireAraPULP/commit/cb20a03c063d208d17eef024a1f6491152d509e8)，远端main读回一致；R两处原诊断修改保留，未混入提交。F随后按本页同步规范合入3RTL、两份regressions C及必要Make规则；自身新目录重建后11次仿真全部PASS，P6五项508组/38452项0错，P2三项及vector/RVV/fmatmul回归通过。

两工程继续保留各自目录和构建组织：R沿用原p6-regressions；F五项加入既有regressions，构建组为日常7/维护29/可选Ara11，运行使用F原TARGET=soc。F自身的路径、编译宏、运行设置和结果已更新到其两份docs指南及README；没有复制R的整份Makefile或实验观察器。

完整映射、运行目录、双份前后源码和恢复检查见[当前同步结果](../reports/official_pr_failure_fixes_review.md#p6-reference-formal-sync-20261025)。F未初始化Git或提交/推送，未综合、板测；下面“P6仅R、未提交、F未同步”保留同步前历史，不代表当前状态。

<a id="p6-fix-20261025"></a>

## 2026-10-25 P6仅参考工程R已修复

R `~/CheshireAraPULP` 已写入P6：#475/#480相关局部＋本地MASKU数据归属、compress结束修复。生产路径8次仿真全部PASS；5个P6软件目标共508组/38452项0错。另有候选8 PASS及旧版预期停滞反例，详见[当前修改表、测试和备份](../reports/official_pr_failure_fixes_review.md#p6-fix-20261025)。默认`all`不扩展，软件显式入口为：

```bash
cd /home/zhaowy24/CheshireAraPULP
make -C sw OUT="$PWD/sw/build/p6_fix_20261025/accepted" p6-regressions
```

R HEAD仍为 `5986ba021e1a0d30dbdb5ecb2cfa230a2c35947c`，P6是**未提交工作区修改，未推送**，不能仅从该历史提交取得P6。前后源码及恢复说明已在服务器工程外和本地双份保存。正式工程F仍为已接受P1–P5及其后续整理状态，**本轮未同步P6**；下面“两工程同步”指P1–P5历史结果。未综合或板测。

<a id="reference-formal-sync-20261024"></a>

## 2026-10-24 两工程同步与复验完成

R `~/CheshireAraPULP` 已分项合入P1–P5、完成48次验证并推送GitHub `5986ba02` / `reference-p1-p5-pass-20261024`。随后F `~/CheshireAra` 按映射同步，从自身入口重建31ELF和四种仿真目标，41次测试完成：38 PASS、1次原ROM/SPI限定告警接受、2项负例判定正确；39项共同用例与R一致。

两工程均有服务器目录外及本地备份：R恢复4390文件匹配；F修改前17文件、修改后27文件均实际恢复并核对。F的配置/wrapper/静态入口保持，无Bender调用或依赖升级。详细版本、比较范围、输出与回退命令统一见[本轮结果](official_upstream_maintenance_assessment.md#reference-formal-sync-20261024)。WSL连接中断后已按用户指示通过Windows OpenSSH完成剩余执行。本轮完成停止；下方为历史托管记录。

<a id="github-cloud-baseline-20261023"></a>

## 2026-10-23 云端基线同步成功

用户完成仓库/公钥设置后要求尝试云端同步。已通过服务器专用SSH密钥，将重建基线原子推送至[个人仓库](https://github.com/lionelZhaowy/CheshireAraPULP)，没有强制推送。推送前远端为空，R工作区干净；dry-run及实际push均返回0。

| 引用 | 云端实际值 |
| --- | --- |
| `refs/heads/main` | `424e4d2cd9f7e129bbda7e595504a48952b150e9` |
| `refs/tags/rebuild-baseline-20261023`（附注标签对象） | `99e48aebfd30a9cd5da9d8bed7852ee1bbc59726` |
| 标签解引用后的提交 | `424e4d2cd9f7e129bbda7e595504a48952b150e9`，与服务器基线一致 |

已通过`git ls-remote`重新读取并比对以上三个引用；本地main跟踪`personal/main`，R源码/HEAD不变，工作区仍干净。未合入P1–P5、未构建/仿真、未修改C或正式工程F。本次只完成修复前基线上云；后续仍按已授权的P1→P5分项同步到R并复验。

用户已选择私有仓库且截图显示锁图标；本轮匿名GitHub API返回404，授权SSH可访问。GitHub连接器仍返回404，不能读取新仓库的Actions管理设置，因此**没有声称独立验证Actions已关闭**，本次沿用用户完成前述网页设置的说明。SSH推送不依赖连接器权限。

证据：服务器`~/CheshireAra_maintenance/github_rebuild_20261023/cloud_sync_20261023.json`及本地`.e01_backups/github_rebuild_20261023/cloud_sync_20261023.json`保存前置检查、dry-run、实际push和云端引用；原双份bundle与恢复记录继续保留。

下方为首次配置准备记录，其中“待授权/未push”描述当时状态，现已由本节更新。

<a id="github-personal-baseline-20261023"></a>

## 2026-10-23 当前版本管理与 GitHub 待授权步骤

用户已选择新建 **`lionelZhaowy/CheshireAraPULP` 私有仓库**，顺序为先上传重建基线，再将隔离副本中验证过的P1–P5分项同步、提交和复验。这授权后续写回重建工程R，不包含正式工程F。

**已完成服务器配置，尚未上传GitHub，也未合入P1–P5。** 重建工程原有官方Git历史，但进入本轮时处于`e040b7bbc…`的detached HEAD，本地修正未提交，根仓库忽略整个`.bender`。本次保留官方历史，新建个人`main`分支并保存实际基线：

| 项目 | 当前实际状态 |
| --- | --- |
| 工程 | `/home/zhaowy24/CheshireAraPULP` |
| 基线提交 | `424e4d2cd9f7e129bbda7e595504a48952b150e9` |
| 基线标签 | `rebuild-baseline-20261023` |
| 官方来源remote | `origin = https://github.com/pulp-platform/cheshire.git`，保留 |
| 个人托管remote | `personal = git@github.com:lionelZhaowy/CheshireAraPULP.git`，默认推送目标 |
| 保存内容 | 4,358个普通文件/符号链接，另保留1个未初始化可选cva6-sdk gitlink；包括26个依赖、printf、已有修正、必要构建/测试输入 |
| 依赖管理 | 根Git直接保存依赖实际文件；服务器原嵌套Git元数据保留，不上传、不更新依赖。printf改为根Git跟踪源码，原子模块元数据仍在本机 |
| 备份 | 服务器`~/CheshireAra_maintenance/github_rebuild_20261023/`；本地`.e01_backups/github_rebuild_20261023/`保存累计bundle及摘要 |
| 恢复核对 | 从bundle克隆到服务器新目录，4,358文件内容和模式匹配；其余4,353个原输入不变、27个依赖/printf的HEAD和原差异不变；本地bundle SHA256匹配并验证完整 |
| 构建/测试 | 本轮未构建、仿真或综合；只进行版本保存和文件恢复检查 |

本轮只改R的Git配置/索引和三份既有说明/管理文件（`.gitignore`、`.gitmodules`、`README.md`），新增`docs/rebuild_versioning.md`及`provenance/rebuild_sources.json`。RTL、软件功能源、原输出、隔离候选C和正式工程F未改。

**外部模型例外：**`target/sim/models/24FC1025.v`头部有限定使用条款，未明确授予再分发权限，因此不纳入上传；原件及服务器恢复备份保留，仓库记录路径/哈希/官方获取配方。克隆后运行仿真仍需该授权模型及现有EDA/软件工具。未初始化的可选子模块没有拉取，不能称所有上游配置完整可用。

### 用户现在需要做的操作

1. 打开[新建仓库](https://github.com/new)，Owner选`lionelZhaowy`，名称填`CheshireAraPULP`，选择 **Private**；不要初始化README、许可证或.gitignore。
2. 新仓库 **Settings → Actions → General → Disable actions → Save**，避免上传时触发继承的官方CI及依赖下载。
3. **Settings → Deploy keys → Add deploy key**，标题填`CheshireAraPULP server 243`，粘贴下面公钥，勾选 **Allow write access** 后保存：

```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINJTDZjc3u4V4BrOnstCQ5aSftgPlpjjaYNDY7HZeMD6 CheshireAraPULP-server-243
```

密钥指纹为`SHA256:ksfV3avv37FkBJECBNWN6YvJPqUSs2km+roKgrh3+us`。私钥只在服务器`~/.ssh/cheshirearapulp_github_ed25519`，不复制到仓库或聊天；Git/SSH配置仅影响本仓库。GitHub主机Ed25519指纹按官方文档核对。实际SSH连接已到GitHub，但返回`Permission denied (publickey)`，符合公钥尚未授权的状态。

GitHub连接器可查询账号/仓库，但没有新建仓库或添加deploy key的工具；服务器也没有已授权的GitHub写入身份，因此需用户本人登录网页完成以上步骤，不需要提供密码或token。[官方上传说明](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)、[Deploy keys操作](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys)。

用户完成后，Agent先核对仓库为私有、空仓库、Actions关闭及SSH写入权限，再执行`git push -u personal main`和推送基线标签，读取云端SHA确认。**当前未创建远端仓库、未push，不把本地基线提交说成云端备份完成。**

### 基线上云后的同步顺序

按P1→P2→P3→P4→P5顺序，每个独立官方修复、本地修复分别提交，必要的测试入口适配另提交。来源和三处自行修改见[代码审查摘要](../reports/official_pr_failure_fixes_review.md)。仅同步固定SHA及已经验证的局部差异，保留R后续修改；P4中间失败版本不作为通过标签。

每组在R新输出目录构建及复验，串行、无stub、默认600秒、普通运行无波形；最后累计回归。C已通过不能代替R复验。失败先保存结果、范围内定位修复，不扩展FS/共享LLC排查或依赖升级。正式工程F同步不在本次范围。

回退先保存失败代码/日志，核对并发修改，再按本轮提交逆序`git revert`；不使用`reset --hard`。基线bundle已实际恢复检查，旧原件快照、原HEAD/index/config和依赖diff在服务器`before/`保留。日常从R根目录使用`git add -u -- 具体文件`提交已跟踪依赖修改；新增文件明确添加并检查暂存差异，不批量添加整个`.bender`。

---

**以下为2026-10-18从零重建的历史操作记录，不应在已保存个人基线的工程上重新执行初始化、detached checkout、Bender或生成步骤。**

更新：2026-10-18。五步重建后，用户已修正启动代码FS设置，并完成官方32×32 fmatmul向量测试；Agent只读核对 `Passed.`、`[SLINK] SUCCESS` 和退出0，见[Q07](#q07)。**第5步本身仅构建软件；单个测试通过不等于完整RVV/提取验收。** 其余版本、工具和warning见[核查报告](../reports/reference_rebuild_check.md)。每步经用户确认后实施；遇到失败先定位。命令在服务器 Bash 中执行，保护已有 `_e01/preflight`、TTY 和本地 FPGA 工程。

阅读方式：先按步骤1—5操作；遇到问题时点击步骤旁的 **⚠ 排障链接**。后半部分的[排障索引](#troubleshooting)集中保存报错原文、原因、解决方案和验证状态。

原则：沿用官方目录、Makefile 和仿真脚本，只为已确认的版本、环境差异和实际缺陷做必要调整。记录命令、日志、退出码仍按[详细方案](server_reference_extraction_plan.md)执行，不为此另建通用执行框架。

## 1. 获取同一版本

目标目录已有探针证据，不能直接 `git clone … .`；检查仅有 `_e01` 后，用以下命令在原目录获取官方源码。若已有工程文件，先检查，不重复初始化。

```bash
ssh zhaowy24@172.16.0.243
bash
export CHS_ROOT="$HOME/CheshireAraPULP"
cd "$CHS_ROOT"
ls -la
git init
git remote add origin https://github.com/pulp-platform/cheshire.git
git fetch origin e040b7bbc7851a37faff3c4657ff8d656cc6e20a
git checkout --detach e040b7bbc7851a37faff3c4657ff8d656cc6e20a
bender checkout
export ARA_ROOT="$(bender path ara)"
```

`fetch/checkout` 固定 Cheshire；`bender checkout` 恢复其锁定依赖。应核对 Ara=`2895ba907…`、CVA6=`99eac9a64…`，以及其余依赖与锁文件一致；不运行依赖更新。必要的 `printf` 子模块及就绪标记由官方 Makefile 管理，不再手动维护。

## 2. 准备工具环境

```bash
export PATH="/opt/riscv/bin:/opt/rh/gcc-toolset-13/root/usr/bin:/eda/synopsys/vcs/W-2024.09-SP1/bin:$PATH"
export CHS_SW_GCC_BINROOT=/opt/riscv/bin
export CXX=/opt/rh/gcc-toolset-13/root/usr/bin/g++
export CXX_PATH="$CXX"
/usr/bin/python3.9 -m venv .venv
source .venv/bin/activate
# 现有环境核查为pip26.0.1；新建环境若仍是pip20.2.4，使用Q01的参数。
python -m pip install -r requirements.txt
python -m pip check
```

分别指定 RISC-V 软件编译器和本机 DPI 编译器；虚拟环境承载旧版生成脚本的 Python 包。若已有适配环境，直接使用，不重复安装。旧版采用 Python ≥3.9/`requirements.txt`，不要套用最新网页的 uv 配方。包多数未锁版本，首次解析后记录版本；遇到不兼容先说明，不自动升级工具。

⚠ 排障：[Q01：pip 显示安装成功但依赖冲突](#q01)。

## 3. 生成硬件和向量仿真清单

⚠ 排障：[Q02：GitHub超时](#q02) · [Q03：下载证书错误](#q03) · [Q04：E31模型缺失](#q04) · [Q05：W28头文件警告](#q05)。

先生成外围寄存器等必要文件；保持原 Boot ROM，不主动重编它。

```bash
cd "$CHS_ROOT"
make -j2 hw-all
```

再准备 SPI Flash、EEPROM 模型。此版本 EEPROM 官方下载规则的 `wget -o` 用法有误，因此限定使用以下下载命令；已有有效模型时跳过，保留来源和许可证。任何下载失败先排障，不继续生成清单。

```bash
mkdir -p target/sim/models
curl -fL https://freemodelfoundry.com/fmf_vlog_models/flash/s25fs512s.v \
  -o target/sim/models/s25fs512s.v
curl -fL https://ww1.microchip.com/downloads/en/DeviceDoc/24xx1025_Verilog_Model.zip \
  -o _e01/eeprom.zip
unzip -p _e01/eeprom.zip 24FC1025.v > target/sim/models/24FC1025.v
```

确认两文件非空且内容为 Verilog 模型，而非错误网页，然后生成向量清单：

```bash
ls -lh target/sim/models/{s25fs512s,24FC1025}.v
head -n 8 target/sim/models/{s25fs512s,24FC1025}.v
```

```bash
make -C "$ARA_ROOT/cheshire" update_vsim_src \
  BACKREF_CHS_ROOT="$CHS_ROOT" ARA_CONFIGURATION=2_lanes \
  VLOGAN_ARGS='-full64 -kdb -nc -assert svaext +v2k -timescale=1ns/1ps'
```

Ara 官方入口依次生成 Questa、VCS 脚本，自动选择向量 CPU、Ara decoder 和 2 lanes/VLEN=2048。`-full64` 是服务器 VCS 所需调整。此后不要再用默认标量参数重新生成清单。

## 4. 小程序编译与首次仿真

```bash
cd "$CHS_ROOT"
make -j2 sw/tests/helloworld.spm.elf
cd "$CHS_ROOT/target/sim/vcs"
export SELCFG=3 BOOTMODE=0 PRELMODE=1
export BINARY="$CHS_ROOT/sw/tests/helloworld.spm.elf"
unset USE_DRAMSYS
timeout 1800 bash -e -o pipefail ./compile.cheshire_soc.sh
timeout 1800 bash -e -o pipefail ./start.cheshire_soc.sh
```

官方脚本完成 RTL 编译、DPI 联编、展开和运行。`SELCFG=3` 选择此版本的 Ara SoC；CPU profile 已由上一步单独选择。`pipefail` 防止日志管道掩盖错误，`timeout` 限制运行时间。检查目标返回值和 SUCCESS/error 信息，不能只看命令退出码。

此步验证向量配置硬件上的标量程序，**尚不构成 RVV 验收**。已完成的工具链检查无需重复，见[第1步结果](../reports/toolchain_preflight.md)；实际 VCS 许可和联编由执行结果判断，出现问题时再缩小为必要探针。

## 5. 后续向量验证

⚠ 排障：[Q06：EEW/PRINTF空宏导致软件编译失败](#q06) · [Q07：fmatmul非法浮点指令与仿真超时](#q07)。

官方整套向量软件的构建入口如下，必须显式传入测试参数；已核对18个Ara源对应的54个ELF及配套dump/镜像齐全。该目标会构建整套软件，不运行向量程序；后续小规模验收应另选必要测试，不必反复执行全套构建。

```bash
make -C "$ARA_ROOT/cheshire/sw" \
  CHS_ROOT="$CHS_ROOT" eew=64 printf=1 chs-sw-all
```

`eew=64` 选择测试元素宽度，`printf=1` 启用测试打印；它们不改变 Ara 的硬件 VLEN。已有 `vector_helloworld.c` 打印参数及 VS 初始化问题仍需在实际选用该程序时处理，编译完成不等于向量测试通过。

复位启动、访存/原子测试和独立提取按[验收方案](server_reference_extraction_plan.md#6-v01-验收用例和证据)分步实施。`~/CheshireAra` 待参考向量工程验证通过后再建立。

---
## 官方依据

- github.io：[入门](https://pulp-platform.github.io/cheshire/gs/)、[仿真](https://pulp-platform.github.io/cheshire/tg/sim/)、[软件与启动](https://pulp-platform.github.io/cheshire/um/sw/)。
- 固定版本：[入门说明](https://github.com/pulp-platform/cheshire/blob/e040b7bbc7851a37faff3c4657ff8d656cc6e20a/docs/gs.md)、[Cheshire 构建规则](https://github.com/pulp-platform/cheshire/blob/e040b7bbc7851a37faff3c4657ff8d656cc6e20a/cheshire.mk)、[Ara 集成入口](https://github.com/pulp-platform/ara/blob/2895ba907e9eb14b3464609dc791a969d159a7c3/cheshire/Makefile)、[Ara 软件入口](https://github.com/pulp-platform/ara/blob/2895ba907e9eb14b3464609dc791a969d159a7c3/cheshire/sw/Makefile)。

网页用于理解流程，具体命令以固定提交为准。

<a id="troubleshooting"></a>

---
## 排障索引：遇到问题再查

以下记录均始于2026-10-18。状态区分用户反馈、Agent只读核查与实际运行证据，不把排障完成写成完整工程验收通过。

| 编号 | 阶段／报错关键词 | 当前处理结论 |
| --- | --- | --- |
| [Q01](#q01) | 步骤2：`tclint` / `incompatible` | 用户确认已解决 |
| [Q02](#q02) | 步骤3：`curl 7` / `expected flush` | 代理连接实测通过 |
| [Q03](#q03) | 步骤3：`curl (60)` / `local issuer certificate` | 用户日志显示单次跳过校验后下载完成 |
| [Q04](#q04) | 步骤3：`error[E31]` / `s25fs512s.v doesn't exist` | 用户日志显示补齐模型后消失 |
| [Q05](#q05) | 步骤3：`warning[W28]` / `.svh` | 已核查，可暂时忽略、不修改 |
| [Q06](#q06) | 步骤5：`-DEEW= -DPRINTF=` / `no left operand` | 已核对预期软件产物齐全，向量运行待验收 |
| [Q07](#q07) | 运行fmatmul：退出124、`Illegal Instruction`、无UART输出 | FS显式设置修正后，单个矩阵测试已通过；正常计算超时另行区分 |

<a id="q01"></a>

### Q01：pip 20.2.4依赖冲突

**现象：**安装最后显示 `Successfully installed`，但同时报告 `tclint 0.4.2` 的三个依赖不兼容：

```text
tclint 0.4.2 requires importlib-metadata==6.8.0, but you'll have importlib-metadata 8.7.1 which is incompatible.
tclint 0.4.2 requires pathspec==0.11.2, but you'll have pathspec 1.1.1 which is incompatible.
tclint 0.4.2 requires tomli~=2.0.1; python_version < "3.11", but you'll have tomli 2.5.0 which is incompatible.
```

| 依赖 | tclint 要求 | 当时安装版本 |
| --- | --- | --- |
| importlib-metadata | `==6.8.0` | `8.7.1` |
| pathspec | `==0.11.2` | `1.1.1` |
| tomli（Python <3.11） | `~=2.0.1`，即 `>=2.0.1,<2.1.0` | `2.5.0` |

**原因：**pip 20.2.4 默认使用旧解析器，可能安装不满足其他包约束的版本；安装完成不等于依赖一致。参见[pip 官方说明](https://pip.pypa.io/en/stable/user_guide/#changes-to-the-pip-dependency-resolver-in-20-3-2020)。

**解决：**保留当前虚拟环境与 pip 版本，启用其自带的新解析器重新安装，再检查依赖。步骤2已同步采用此命令，避免再次按旧写法触发冲突。

```bash
cd ~/CheshireAraPULP
source .venv/bin/activate
python -m pip install --use-feature=2020-resolver -r requirements.txt
python -m pip check
```

`pip check` 预期输出 `No broken requirements found.`。用户于2026-10-18确认问题已解决；未提供修复后的完整输出和版本列表，本轮未远程复测。该结论仅涉及 Python 依赖冲突，不代表硬件生成或仿真通过。此参数针对旧版 pip，采用默认新解析器的新版无需照加。

**后续核查（同日）：**Agent已在服务器执行`pip check`，退出0并输出上述成功信息；现有pip为26.0.1，tclint0.4.2、importlib-metadata6.8.0、pathspec0.11.2、tomli2.0.2。本轮未升级任何工具；该实测替代此前“未远程复测”的状态，旧版修复命令保留用于对应历史报错。

<a id="q02"></a>

### Q02：printf子模块下载超时

**报错（2026-10-18，`make -j2 hw-all`）：**

```text
Info Checked out 26 dependencies in 65ms
Cloning into '/home/zhaowy24/CheshireAraPULP/sw/deps/printf'...
error: RPC failed; curl 7 Failed to connect to github.com port 443: Connection timed out
fatal: expected flush after ref listing
fatal: clone of 'https://github.com/mpaland/printf' into submodule path '/home/zhaowy24/CheshireAraPULP/sw/deps/printf' failed
Failed to clone 'sw/deps/printf'. Retry scheduled
```

**原因：**当前终端未设置代理，无法连接 GitHub；启动 Mihomo 不会自动更新其他终端的环境。这是 printf 子模块获取失败，不是26项 Bender 依赖或 RTL 编译失败。

**解决：**已在服务器确认 HTTP 代理为 `127.0.0.1:17890`（`19090` 是管理端口）。原命令仍卡住时先按 Ctrl+C，在原终端设置代理并检查连接：

```bash
export http_proxy="http://127.0.0.1:17890"
export https_proxy="$http_proxy"
export HTTP_PROXY="$http_proxy"
export HTTPS_PROXY="$https_proxy"
timeout 30 git ls-remote https://github.com/mpaland/printf.git HEAD
```

**验证结果：**Agent已通过该代理执行上述 Git 查询，返回 HEAD、退出码0。连接成功后重试下面的构建；连接验证本身不证明构建成功。无需清理依赖或重建虚拟环境。

```bash
cd "$CHS_ROOT"
make -j2 hw-all
```

`hw-all` 生成外围寄存器等必要文件。保持原 Boot ROM，不主动重编它。

<a id="q03"></a>

### Q03：Flash模型下载证书校验失败

**已遇报错（Flash 下载）：**

```text
curl: (60) SSL certificate problem: unable to get local issuer certificate
curl failed to verify the legitimacy of the server and therefore could not
establish a secure connection to it.
ls: cannot access 'target/sim/models/s25fs512s.v': No such file or directory
```

**原因：**curl 未能建立受信任的 TLS 证书链，Flash 模型没有下载成功。仅凭日志不能确定是本机 CA、站点证书链还是代理链路造成；EEPROM 下载成功，不需要重下。

**解决：**先尝试当前虚拟环境已有的 CA 集合：

```bash
cd "$CHS_ROOT"
curl --cacert "$(python -m certifi)" -fL \
  https://freemodelfoundry.com/fmf_vlog_models/flash/s25fs512s.v \
  -o target/sim/models/s25fs512s.v
```

本次用户执行后仍报 curl (60)。固定版官方 Makefile 对该站点使用 `wget --no-check-certificate`；沿其处理方式，仅对这一次模型下载跳过证书校验：

```bash
curl -k -fL \
  https://freemodelfoundry.com/fmf_vlog_models/flash/s25fs512s.v \
  -o target/sim/models/s25fs512s.v
```

`-k` 放弃本次服务器身份校验，不设置为全局默认。**用户日志结果：**下载约371 KiB，文件列表显示372K，文件头为 Free Model Foundry 的 `s25fs512s.v` 及许可证说明；这确认文件已获取，不等于验证了模型行为或来源真实性。

<a id="q04"></a>

### Q04：E31缺少仿真模型

**报错原文：**

```text
error[E31]: File /home/zhaowy24/CheshireAraPULP/target/sim/models/s25fs512s.v doesn't exist.
make[1]: *** [cheshire.mk:151: /home/zhaowy24/CheshireAraPULP/target/sim/vsim/compile.cheshire_soc.tcl] Error 1
make[1]: *** Deleting file '/home/zhaowy24/CheshireAraPULP/target/sim/vsim/compile.cheshire_soc.tcl'
make: *** [Makefile:61: update_vsim_src] Error 2
```

**原因：**Bender生成清单时就检查文件是否存在。原文先生成清单、后下载模型的顺序有误；之后 Flash 下载又因上述证书错误失败，所以 E31 再次出现。`Deleting file` 是 make 移除生成失败的脚本，不是删除源码。

**解决：**按[步骤3](#3-生成硬件和向量仿真清单)补齐模型（证书错误见[Q03](#q03)），再重试 `update_vsim_src`；无需重跑已成功的 `hw-all` 或清理依赖。正确顺序是 **硬件生成→模型准备→清单生成→编译仿真**。

**验证结果：**用户后续日志中 E31 已消失，Questa、VCS清单生成均走完，剩下[Q05](#q05)中的 W28 警告。

<a id="q05"></a>

### Q05：W28两个.svh文件类型未知

**警告原文（Questa、VCS清单生成时各出现一次）：**

```text
warning[W28]: Files with unknown type:
  - /home/zhaowy24/CheshireAraPULP/.bender/git/checkouts/cva6-20c9d7cbe0dd6995/common/local/util/instr_trace_item.svh
  - /home/zhaowy24/CheshireAraPULP/.bender/git/checkouts/cva6-20c9d7cbe0dd6995/common/local/util/ex_trace_item.svh
 ├─› help: Known file extensions are: .sv, .v, .vp (Verilog) and .vhd, .vhdl (VHDL).
 ╰─› help: To indicate a file type for unknown file extensions, use `sv:`, `v:`, or `vhd:` when listing the file.
```

**原因：**CVA6的 `Bender.yml` 将两个头文件也列入源文件列表，而 Bender 不将 `.svh` 自动作为独立编译文件。这是文件分类警告，不是文件缺失或 SystemVerilog 语法错误。

**核查依据（Agent已在服务器只读确认）：**两个文件均存在；`instr_tracer.sv` 已包含：

```systemverilog
`include "ex_trace_item.svh"
`include "instr_trace_item.svh"
```

生成的VCS脚本同时包含 tracer 源码及对应的头文件搜索路径（摘录，非连续命令）：

```text
"+incdir+$ROOT/.bender/git/checkouts/cva6-20c9d7cbe0dd6995/common/local/util"
"$ROOT/.bender/git/checkouts/cva6-20c9d7cbe0dd6995/common/local/util/instr_tracer.sv"
```

**处理结论：低严重度，可暂时忽略，不修改。** 两份 `.svh` 在脚本中只作为注释列出，其内容由 tracer 的 include 引入，不需要单独编译。不要仅为消除警告添加 `sv:`，以免重复定义或改变作用域；不需要升级Bender。此结论仅适用于这两项已核查警告；后续实际编译若报 include 缺失或类型未定义，再检查对应路径和编译作用域。

用户日志显示 Questa、VCS 清单生成已走完，可进入第4步；这不是 RTL 编译或仿真通过的证据。

<a id="q06"></a>

### Q06：EEW、PRINTF空宏导致向量软件编译失败

**触发命令（旧写法，缺参数，不再沿用）：**

```bash
make -C "$ARA_ROOT/cheshire/sw" CHS_ROOT="$CHS_ROOT" chs-sw-all
```

**具体报错（用户日志关键摘录）：**编译命令包含 `-DEEW= -DPRINTF=`，随后出现：

```text
rvv_test.h:17:13: error: operator '==' has no left operand
   17 | #if (PRINTF == 1)
rvv_test.h:30:9: error: operator '==' has no left operand
   30 | #if EEW == 64
rvv_test.h:59:2: error: #error "ERROR: No EEW was defined. Please specify one in [8,16,32,64]."
error: unknown type name '_DTYPE'
warning: implicit declaration of function '_VSETVLI'; did you mean 'VSETVLI'?
error: expected expression before '/' token
  199 | #define ELMMAX VLMAX / (EEW / 8)
make: *** [Makefile:40: chs-sw-all] Error 2
```

**原因：**官方 `cheshire/sw/Makefile` 使用 `-DEEW=$(eew) -DPRINTF=$(printf)`，但未提供两个Make变量的默认值。未传参数时，宏已定义但替换内容为空，`#if (PRINTF == 1)` 变为 `#if ( == 1)`；`#ifndef` 默认值也不会生效。EEW相关类型和指令宏未选择，进一步引发 `_DTYPE`、`_VSETVLI`、`_VST` 等连锁错误，不应逐条修改调用处。

本地旧工程曾加入 `eew ?= 64`、`printf ?= 1`；本次官方重建未自动带入这项本地修改。此前速查列出的入口未补齐参数，现已纠正。

**解决：**只补命令参数，保留官方源码，不升级编译器、不清理依赖：

```bash
make -C "$ARA_ROOT/cheshire/sw" \
  CHS_ROOT="$CHS_ROOT" \
  eew=64 printf=1 \
  chs-sw-all
```

参数名为小写：`eew=64`指定这批测试的64位元素宽度，`printf=1`启用打印，不修改硬件VLEN。当前失败对象未成功生成，可直接重试；这不代表后续改变编译选项时已有对象会自动重编。

**验证标准与状态：**新编译行应出现 `-DEEW=64 -DPRINTF=1`，不再有上述空宏错误。方案尚未收到修复后日志；即使该错误消失，整套软件仍可能遇到其他问题，不能据此声称全部编译或RVV运行通过。

**后续核查（同日）：**用户报告完成第5步；服务器上18个Ara源对应SPM/DRAM/ROM的54个ELF、54个dump及36个ROM/GPT memh均存在，抽查ELF确有RVV指令。该产物检查支持软件构建完成；原构建控制台日志/退出码未留存于所查目录，不能补造。现有`simulate.log`运行的仍是标量HelloWorld，向量运行尚待验收，见[核查报告](../reports/reference_rebuild_check.md)。

**同一日志的其他warning：**

| 原始关键词 | 判断与处理 |
| --- | --- |
| `implicit declaration of function '_VSETVLI'` / `'_VST'` | 优先修复EEW，属于宏选择失败的连锁现象；修复后仍出现再定位 |
| `comparison of integer expressions of different signedness` | 独立的有符号/无符号比较警告；非本次阻塞，选用该测试时核对取值范围 |
| `'return' with a value, in function returning void` | `get_unit_stride_bursts_wrap` 的独立源码警告；非本次阻塞，不靠关闭警告解决 |
| `this 'if' clause does not guard...` | `ret_cnt++`的缩进与实际控制范围不一致；正式采用测试前核对意图，不为消警告随意加括号 |

<a id="q07"></a>

### Q07：fmatmul启动后超时——FS被关闭导致非法浮点指令

**适用版本与位置：**Cheshire `e040b7bbc…`、Ara `2895ba907…`、CVA6 `99eac9a64…`；向量CPU profile、Ara 2 lanes/VLEN2048。服务器应用启动代码为 `/home/zhaowy24/CheshireAraPULP/sw/lib/crt0.S`，不是Boot ROM源文件。本次由用户备份为 `crt0.S.backup` 后修改服务器源码；本地FPGA工程、RTL及依赖版本未改。

**现象：**ELF加载完成，但无UART打印，最终退出124：

```text
[SLINK] Preload complete
[SLINK] Wrote launch signal and entry point 0x0000000010000000
simulator exit status: 124
```

124只代表外部timeout到期，不能据此判断原因。首次运行的 `trace_hart_0.log` 显示：

```text
Exception @2811345000, PC: 00000000100012e0, Cause: Illegal Instruction,
                tval: 000000000000ac22
```

对应实际ELF的 `c.fsdsp fs0,24(sp)`，是编译器生成的main入口浮点寄存器保存指令；随后进入 `0x1000018c <trap_vector>` 的 `j trap_vector` 死循环。尚未执行printf或RVV计算，延长超时无效。插入诊断指令后异常PC会移动，应以当次ELF反汇编为准。

**原因及确认方法：**原启动代码先开启浮点并清零浮点寄存器，之后以如下操作“设置Clean”：

```asm
    // Set FS state to "Clean"
    csrrc x0, mstatus, t1    // t1 = 0x2000，只清FS低位
```

它依赖此前FS已经为Dirty(11)，清位后才是Clean(10)。本次在该指令前后加入 `csrr t2,mstatus`、`csrr t3,mstatus` 并重编运行，实测：

| 读数 | mstatus | `(mstatus >> 13) & 3` |
| --- | --- | --- |
| t2：清位前 | `0x0000000a00002000` | 1，Initial |
| t3：清位后 | `0x0000000a00000000` | 0，Off |

因此FS实际被关闭，下一条浮点保存指令触发异常。此前HelloWorld不充分使用应用浮点路径，不能排除此问题；标量浮点与Ara向量也不是同一执行路径。

**修复：**保留已有备份，将上述设置Clean的位置改为显式设置FS。前后两次CSR读回用于诊断，本次成功版本仍保留：

```asm
    csrr t2, mstatus

    // Explicitly set FS to Clean (10).
    li t1, 0x6000
    csrc mstatus, t1
    li t1, 0x4000
    csrs mstatus, t1

    csrr t3, mstatus
```

这里清除FS两位，再置Clean；其他mstatus位保持。必须在 `call main` 前生效，在main第一条C语句中开启浮点可能已经晚于入口保存指令。此为本次兼容修正，不是已合入上游的修复；不需要改CPU profile、RTL或升级工具链。

**重新编译：**在已完成重建的服务器环境中执行。保留原失败ELF后，恢复官方整套构建结束时移除的单个C源，沿用官方Ara参数，只构建该测试；已有头文件来自此前第5步。`cp -n`不覆盖已有文件。

```bash
cd ~/CheshireAraPULP
export CHS_ROOT="$PWD"
export ARA_ROOT="$CHS_ROOT/.bender/git/checkouts/ara-2c7b103275a16c87"
# 在首次重编前保存旧输入；后续已有备份时不要覆盖
cp -n sw/tests/fmatmul.spm.elf _e01/rvv_fmatmul_01/fmatmul.spm.elf
cp -n "$ARA_ROOT/cheshire/sw/src/fmatmul.c" sw/tests/fmatmul.c
VECTOR_FLAGS="$(sed -n 's/^CHS_SW_FLAGS[[:space:]]*?=[[:space:]]*//p' sw/sw.mk \
  | sed 's/rv64gc/rv64gcv/')"
VECTOR_FLAGS+=" -DCHESHIRE -DNR_LANES=2 -DVLEN=2048 -DARA_NR_LANES=2 -DEEW=64 -DPRINTF=1"
make -j1 sw/tests/fmatmul.spm.elf sw/tests/fmatmul.spm.dump \
  CHS_SW_GCC_BINROOT=/opt/riscv/bin CHS_SW_FLAGS="$VECTOR_FLAGS"
```

依赖链为 `crt0.S → crt0.o → libcheshire.a → fmatmul.spm.elf`；`.backup`不会参与源码匹配。此单测试命令复用官方根Make规则，不是Ara另有一个官方单测试目标。

**重跑与超时判断：**复用原simv，在新的输出目录运行，保留ELF/simv哈希、simulate.log、trace及退出码；完整运行命令见[上手指南 §5.2](../../../software/SERVER_SIMULATION_GUIDE.md#52-运行一次现有fmatmul)。参数保持 `+BOOTMODE=0 +PRELMODE=1 +BINARY="$CHS_ROOT/sw/tests/fmatmul.spm.elf"`。本次运行顺序如下，旧目录均保留：

| 目录（均在 `_e01/` 下） | 结果与处理 |
| --- | --- |
| `rvv_fmatmul_01` | 原版，600秒超时；非法浮点指令后trap循环，不能靠延长超时修复 |
| `rvv_fmatmul_02` | 仅增加CSR读回，180秒超时；确认FS从Initial变Off |
| `rvv_fmatmul_03` | 显式FS修正，读回FS=2；180秒超时时标量乘加完成24,413/32,768次，未检出异常，循环持续推进 |
| `rvv_fmatmul_04` | 与03相同ELF/simv，限时600秒；完成向量计算与比较，退出0 |

03打印到 `Calculating fmatmul on scalar core...` 时的超时与01/02不同：程序确实在计算金值，诊断限时不足。此时根据trace确认有效进展后才增加预算，无需再次修改或编译。每次重跑都从复位开始，不接着旧进度继续。

**验证结果（2026-10-18，用户执行、Agent SSH只读复核）：**

```text
[UART] Calculating fmatmul on scalar core...
[UART] Calculating fmatmul on vector core...
[UART] The execution took 19883 cycles.
[UART] The performance is 3.296082 FLOP/cycle (82.402054% utilization).
[UART] Verifying result...
[UART] Passed.
[SLINK] SUCCESS
Time: 26019135000 ps
CPU Time: 402.720 seconds; Data structure size: 517.3Mb
simulator exit status: 0
```

运行证据为 `~/CheshireAraPULP/_e01/rvv_fmatmul_04/`；输入哈希见该目录 `inputs.sha256`，详细证据及历史判断保留在[核查报告第6节](../reports/reference_rebuild_check.md)。软件打印的周期数属于内核测量，VCS CPU Time是主机仿真开销，两者不能混用；性能打印仅保留原始观察，不作为已校准的性能验收。

**结论边界：**FS启动兼容修正已通过本次32×32 fmatmul运行验证；“为何清零浮点寄存器后FS仍为Initial”仍需独立检查，不能据此宣称CVA6 Dirty状态跟踪正确。不同VL/尾部、访存原子、SPI自主启动和独立提取验收仍未完成。
