# 重建工程版本管理与个人 GitHub 托管

2026-10-23。目标：`lionelZhaowy/CheshireAraPULP`，私有仓库。

## 当前版本与边界

- 官方历史保留，基底为`e040b7bbc7851a37faff3c4657ff8d656cc6e20a`；个人分支为`main`，实际重建基线标签为`rebuild-baseline-20261023`。
- 基线保存已有FS启动设置、DMA wrapper/HAL/CONF、iDMA #80/#204、WT读断言及实际生成文件。它们此前只是工作区修改；本次一并保存，不冒称每项已有独立历史提交。
- `.bender/git/checkouts/`中26个依赖的实际文件由根Git直接跟踪；保留服务器原嵌套Git元数据，上传不包含这些`.git`。日常提交从工程根目录进行，根仓库才是个人版本的权威记录；嵌套Git仍保留上游来源历史。
- printf当前源码直接保存，原子模块Git元数据留在本机；未启用的`sw/deps/cva6-sdk`及依赖中的其他未初始化子模块没有拉取，版本记录见`provenance/rebuild_sources.json`。本基线不声称支持所有可选Linux/FPGA/验证配置。
- 保存必要静态编译脚本、软件源、测试入口及命令记录；不上传simv、ELF、波形、日志、EDA安装、虚拟环境或凭据。构建产物与既有验收归档留原位置。
- `target/sim/models/24FC1025.v`的头部有限定使用条款，未明确授予再分发权限，因此不上传；服务器原件不动，哈希与获取配方位置已记录。GitHub克隆不能单靠仓库完成仿真，还须按授权取得该模型及现有工具环境。`s25fs512s.v`按其原GPL-2.0声明保留版权头。
- P1–P5仅在隔离候选`5e0f973c090ee26ba18ce520bc61beebe584e929`验证，尚未同步到本工程。`~/CheshireAra`正式工程未修改。

本次只配置版本管理；没有编译、仿真或重新生成RTL。原构建脚本含参考工程绝对路径，换目录使用前需核对路径；现有`run.py`仍依赖同目录`inputs.json`，二者一并保存。不要调用Bender update、删除`.bender`或直接运行上游`make all`来恢复本基线。

## GitHub准备与用户操作

根仓库保留`origin`指向官方只读来源，另用`personal`指向`git@github.com:lionelZhaowy/CheshireAraPULP.git`；普通推送默认目标设为`personal`。提交身份只设置在本仓库，邮箱使用GitHub noreply地址。

服务器专用SSH密钥：`~/.ssh/cheshirearapulp_github_ed25519`；公钥为同名`.pub`。私钥只留服务器，不放Git仓库、不复制到聊天。连接配置只在本仓库`.git/config`中生效；没有更改全局Git/SSH配置。GitHub主机公钥按官方Ed25519指纹固定。

用户需要操作：

1. 在 <https://github.com/new> 创建`lionelZhaowy/CheshireAraPULP`，选**Private**；不要勾选初始化README、许可证或.gitignore。
2. 新仓库 **Settings → Actions → General → Disable actions → Save**。先停用继承的官方CI，避免初次上传触发依赖下载或不适用的构建。
3. **Settings → Deploy keys → Add deploy key**，标题可用`CheshireAraPULP server 243`。在服务器执行下面命令，复制整行公钥，勾选 **Allow write access** 后保存：

```bash
cat ~/.ssh/cheshirearapulp_github_ed25519.pub
```

该密钥只授权此仓库。GitHub可能要求用户登录/二次验证；无需向Agent提供密码或token。完成后告知Agent，由Agent核对仓库私有状态和SSH权限，再上传基线并比对云端SHA。连接器缺少新建仓库/添加deploy key功能，因此这两项需用户在网页完成。

待用户完成设置后，预定执行以下命令；**本次尚未推送**：

```bash
cd ~/CheshireAraPULP
git push -u personal main
git push personal refs/tags/rebuild-baseline-20261023
```

## 云端基线上传后的修复提交

顺序为基线上传并核对 → P1 → P2 → P3 → P4 → P5 → 累计回归。使用已验证候选的固定提交和最小文件差异，不整包覆盖；测试入口适配单独提交。官方回移与本地修复分别提交并注明来源，P4的#191/#192中间版本不能标记为通过；最终组通过后再打参考工程通过标签。

每组同步前检查原文件无后续改动；在本工程新输出目录构建、复用适用定向用例及回归，默认600秒、串行、无波形、不用stub。已有候选结果不能代替本工程复验。原ROM padding限定告警、FS/libgcc和共享LLC限制保留；不扩展为全量更新。正式工程同步仍不在本次范围。

## 日常提交与恢复

```bash
cd ~/CheshireAraPULP
git status --short
git diff -- path/to/changed_file
git add -u -- path/to/changed_file
git commit -m "fix: describe the specific change"
```

已跟踪依赖文件也使用上面命令；新增文件需明确`git add -f -- 具体路径`并检查`git diff --cached`，不要对整个`.bender`运行批量添加。忽略规则只阻止新缓存/产物进入，不会取消现有文件跟踪。不要在依赖子目录代替根仓库提交个人修复。

工程外备份：`~/CheshireAra_maintenance/github_rebuild_20261023/`。`before/`保存原根Git配置/索引/HEAD、官方bundle、各依赖原差异及实际文件归档；`rebuild-baseline.bundle`保存个人基线。恢复检查会从bundle克隆到独立新目录并比较源码哈希，不构建。

后续修复回退使用逆序`git revert <本次修复提交>`，先保存失败日志并检查并发变化。不要`reset --hard`或覆盖整个工程。需要只查看基线时，在新目录从bundle克隆并选择`rebuild-baseline-20261023`，不要切换/覆盖正在使用的工作区。

官方操作参考：[上传现有代码](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)、[Deploy keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys)、[GitHub SSH指纹](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints)。
