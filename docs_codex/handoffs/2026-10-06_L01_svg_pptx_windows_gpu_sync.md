# L01 / SVG-PPTX skill 同步到 Windows 和 GPU 服务器

## 基本信息

- 日期：2026-10-06；用户授权同步工具到 Windows Codex 和 GPU 账户 `zhaowenyao24@172.16.0.246`。
- 输入：HEAD `5ddec4fb4`；本对话已有未跟踪工具、图片和交接均保留。
- 状态：Windows/GPU 部署、平台原生依赖安装及脚本验证完成；WSL 也同步了兼容性修复。
- 无生产 RTL/sw/config/filelist 修改，无系统 Python/Codex/SSH 配置修改，无 Git 提交。

## 安装位置

| 环境 | 安装根目录 | Codex 发现入口 |
| --- | --- | --- |
| WSL | `/home/zhaowenyao/.codex/skills/svg-pptx-diagrams` | `/home/zhaowenyao/.agents/skills/svg-pptx-diagrams` symlink |
| Windows | `C:\Users\ZhaoWenyao\.codex\skills\svg-pptx-diagrams` | `C:\Users\ZhaoWenyao\.agents\skills\svg-pptx-diagrams` Junction |
| GPU | `/home/zhaowenyao24/.codex/skills/svg-pptx-diagrams` | `/home/zhaowenyao24/.agents/skills/svg-pptx-diagrams` symlink |

Windows 独立 Python 3.14.6 环境位于技能 `.venv\Scripts\python.exe`；GPU 用 Python 3.12.3 创建 `.venv/bin/python`；未复制 WSL 的 .venv。

## 修复与同步内容

- Windows 原来没有安装该 skill，也没有 python-pptx/Pillow；WSL 用户安装不会自动出现在 Windows 用户目录。
- scripts/run.py 改用等待子进程的 subprocess.call 并返回其退出码。首次 Windows 导出后立即 Office 打开失败，稍后单独打开成功；修复后新增等待/错误码行为测试及完整安装验证通过。没有把首次失败写成通过。
- svg_to_pptx.py 在原生 Windows 从 WINDIR/Fonts 查找微软雅黑；WSL 沿用 /mnt/c/Windows/Fonts。GPU 字体未复制或嵌入，只验证结构生成。
- 新增 install_windows.ps1：目标存在时默认拒绝；显式更新先备份技能源码，保留 .venv 和验证产物，检查 Junction 目标。Windows 旧源码备份位于该用户 `.codex/skill-backups/`。
- 新增 install_linux_offline.py：支持系统 Python 无 pip/ensurepip 的场景，在技能内建立 --without-pip venv，用提供的 pip wheel 离线引导并安装要求。拒绝已有目标，不用 apt/sudo、不改系统 Python。
- 新增 references/platform-install.md；更新 SKILL.md 的平台调用方式与同步边界；补充启动器等待/退出码测试。
- 按 whitelist 仅同步 SKILL.md、requirements、agents/scripts/references/assets。12 个源码文件在仓库源包、WSL、Windows 和 GPU 上逐项 SHA-256 一致。
- WSL 更新前源码备份：`/home/zhaowenyao/.codex/skill-backups/svg-pptx-diagrams-20261006-cross-platform-before/`；原 .venv 保留。

## 执行与验证

- skill-creator quick_validate.py：源包通过。
- Windows、GPU、更新后的 WSL 各运行 4 项行为测试，退出 0；覆盖启动器同步等待及错误码、SVG/PPTX 文字/对象/圆角、路径、拒绝不支持特性与已有输出保护。
- Windows 调用原生 python + scripts/run.py，实际生成示例 SVG/PPTX，PowerPoint 16.0 只读打开成功：19 个原生对象、8 个文本、编辑字符探针通过、PNG 导出成功。报告：Windows 安装根 installation_report.json；预览在 `validation-windows-20261006-131018/`。
- GPU 通过 Windows 已配置 SSH 密钥登录。WSL 默认身份验证失败；默认 WSL 密钥交换检查停滞，换兼容的 curve25519 检查后确认认证失败。没有修改 SSH 配置或凭据；使用 Windows 现有配置继续任务，仍严格校验主机密钥。停滞的本轮本地 SSH 检查进程经定位后已结束。
- GPU 为 x86_64 / Ubuntu glibc 2.39、Python 3.12.3，缺 pip/ensurepip。按目标 Python/ABI/platform 下载二进制 wheels 后离线安装，只在该 skill .venv 内安装 pip 26.2.1、python-pptx 1.0.2、Pillow 12.3.0 等。
- GPU 原生导出示例：19 个对象、8 个文本，重新读回及 ZIP/无整图图片检查通过。产物在服务器安装根 `validation-linux/`。未做 GPU 上的 Office 渲染或 UI skill 列表实测。
- 传输内容仅 skill 与离线依赖；未上传工程源码、供应商 PDF、字体、配置或凭据。
- 持久比对证据：[platform_sync.json](../diagrams/2026-10-06_svg_pptx_skill_validation/platform_sync.json)，包含各端源码哈希与安装报告摘要。
- 临时包：本机 `/tmp/svg-pptx-diagrams-source-20261006.tar.gz`、`/tmp/svg-pptx-gpu-wheels-20261006.tar.gz`；服务器暂存 `/tmp/svg-pptx-sync.3TzfHU/`。未执行清理或删除用户资料。

## 调用

各端 Codex 刷新技能列表/重新打开对话后：`$svg-pptx-diagrams 根据需求绘制结构化 SVG 并生成可编辑 PPTX。`

Windows PowerShell：

```powershell
python "$env:USERPROFILE\.codex\skills\svg-pptx-diagrams\scripts\run.py" --input figure.svg --out-dir figures-export-new
```

GPU Linux：

```sh
python3 ~/.codex/skills/svg-pptx-diagrams/scripts/run.py --input figure.svg --out-dir figures-export-new
```

输出目录应为空或新建。以后更新源包需先检查各端差异并保留备份；虚拟环境按目标平台维护，不参与源文件同步。本次是工具部署，不更改 SoC 实现状态或共享任务表。
