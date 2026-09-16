# 随主仓库保存的依赖源码

2026-09-16 起，`.bender/git/checkouts/` 不再只是可删除的下载缓存：其中的源码以主仓库普通文件保存，包含本地 CVA6/Ara 集成修改。重新克隆 GitHub 主仓库即可得到这些文件，不依赖各子仓库的隐藏 `.git` 目录。

## 复现入口

根目录 `Bender.local` **有意纳入版本管理**，把 26 个硬件依赖固定到仓库内相对路径。这里的用法与通常只在个人机器使用 `Bender.local` 不同；不要删除它或改成绝对路径。根 `Bender.lock` 已通过 `bender --local update` 转为相对路径依赖；原 Git 版本锁保存在 `UPSTREAM.lock`，`SNAPSHOT.tsv` 补充已展开仓库的实际 HEAD 和原先未初始化的子模块信息。本地工作区修改以主仓库提交中的文件内容为准，不只看上游 HEAD。

必须保留这套配置与新锁文件的配对：验证时发现，只增加路径 overrides 而沿用旧 Git 锁文件，Bender 仍可能尝试初始化 Git 依赖；没有子仓库 `.git` 的源码快照会失败。当前配对已在无依赖 Git 元数据的临时副本中检查过。

```sh
git clone --recurse-submodules git@github.com:lionelZhaowy/Cheshire_Ara_Orig.git
cd Cheshire_Ara_Orig
bender --local path cva6 ara
bender --local script flist -t rtl -t cva6 -t cv64a6_imafdcv_sv39 -t exclude_first_pass_decoder
```

硬件依赖路径应指向这次克隆目录内的 `.bender/git/checkouts/`。根仓库 `sw/deps/printf` 与 `sw/deps/cva6-sdk` 仍为原来的 Git 子模块，不属于本次 `.bender` 快照范围；首次递归克隆这些子模块需要网络。

硬件 source list 可离线解析，不等于整套工程无需外部环境：Python 包、交叉编译器、EDA 工具、仿真外设模型以及 Linux 构建下载仍需单独准备。沿用 `docs_codex/01_Cheshire_Ara_Quick_Start.md` 的向量配置步骤，不要仅依赖原 README 的默认标量命令。

## 保存与排除范围

- 保存 26 个顶层硬件依赖，以及本机已经初始化的嵌套依赖源码；保留许可证、版权说明、脚本、测试、配置、相关数据文件与源码修改。
- 依赖被展开为普通目录，不是只上传 mode 160000 的 gitlink。原本存在的嵌套 `.gitmodules` 用于记录来源，不代表主仓库会再把这些目录作为子模块初始化。
- 保留当前工作树中额外的 RTL、头文件、C/汇编等源码；不保留构建完成标记，以便新环境正确执行必要生成步骤。
- 排除 Git 对象库/元数据、嵌套 Bender 缓存、Buildroot `dl/output`、安装目录、ELF/库/FPGA/仿真产物、日志和备份。
- 排除 SDK 示例 rootfs 中的 SSH host keys，以及 U-Boot 示例 `board/broadcom/bcmns3/fit/keys/dev.key`。这些演示密钥不能作为部署凭据；需要相应功能时应自行生成。
- 三个大型可选 benchmark 输入未保存：`_canneal/input/2500000.nets`、`_spmv/input/poisson3Db.mtx`、`_spmv/input/venkat25.mtx`，位于 Ara 的 `cheshire/sw/riscv-vectorized-benchmark-suite/`。它们不是硬件源码；运行对应大规模软件 benchmark 时需另行获取。
- Ara 的 `apps/rvv-bench`、`toolchain/newlib`、`toolchain/riscv-gnu-toolchain`、`toolchain/riscv-llvm` 在原工作区未初始化，本次未额外下载。所需版本见 `SNAPSHOT.tsv`。因此这不是“全部可选工具链及 Linux 环境的离线镜像”。

## 后续维护

不要执行 `bender clean`，也不要删除 `.bender/`。根 Makefile 的 `clean-deps` 已加入拒绝删除此源码快照的保护；直接手工删除或调用其他清理工具不受这个保护约束。

不要盲目运行依赖内部的 `git submodule update` 或删除其源目录。当前机器保留的嵌套 `.git` 属于原工作区元数据，并未上传；新克隆目录中的普通文件才代表主仓库保存形式。后续更改依赖源文件，应在主仓库审核并提交。新增文件若命中上游依赖自带 `.gitignore`，先确认确为源码，再对该具体文件使用 `git add -f`，不要强制加入整个目录。

更新依赖时应同时审核 `Bender.local`、锁文件、来源清单和本地补丁，完成回归后提交；不要把“更新到上游最新提交”当作恢复当前快照。

各依赖保留自己的许可证，根项目的硬件/软件许可证概述不会覆盖第三方 Linux、U-Boot、Buildroot 等源码的原许可证。

本次在另一个绝对路径、无依赖 `.git` 元数据的副本中，验证了 `bender --local checkout`、路径解析及文件列表：向量 RTL 的 608 个文件、VCU118 FPGA 配置的 605 个文件均存在。本次不包含新的 VCS/Questa/Vivado 编译或板级运行结果。
