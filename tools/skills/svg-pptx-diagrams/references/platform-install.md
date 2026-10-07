# Windows / Linux 同步

只同步 SKILL.md、agents/、scripts/、references/、assets/ 和 requirements.txt，不同步 .venv、__pycache__、输出产物或凭据。目标平台单独创建 Python 虚拟环境。

个人安装根目录可沿用 `.codex/skills/svg-pptx-diagrams`；当前 Codex 官方技能发现目录为 `.agents/skills`，Linux 可建立指向安装根的 symlink，Windows 可用 Junction。自定义 CODEX_HOME 时先核对实际路径。不要改动已有 Codex 配置、会话或其他技能；同名工具存在时先核对差异并保留备份。

Windows PowerShell（安装目录已经包含源文件）：

```powershell
$diagramSkill = Join-Path $env:USERPROFILE '.codex\skills\svg-pptx-diagrams'
python -m venv (Join-Path $diagramSkill '.venv')
& (Join-Path $diagramSkill '.venv\Scripts\python.exe') -m pip install -r (Join-Path $diagramSkill 'requirements.txt')
python (Join-Path $diagramSkill 'scripts\run.py') --input (Join-Path $diagramSkill 'assets\example.svg') --out-dir C:\work\svg-pptx-example-new
```

Linux（安装目录已经包含源文件）：

```sh
python3 -m venv ~/.codex/skills/svg-pptx-diagrams/.venv
~/.codex/skills/svg-pptx-diagrams/.venv/bin/python -m pip install -r ~/.codex/skills/svg-pptx-diagrams/requirements.txt
python3 ~/.codex/skills/svg-pptx-diagrams/scripts/run.py --input ~/.codex/skills/svg-pptx-diagrams/assets/example.svg --out-dir /tmp/svg-pptx-example-new
```

环境/输出已存在时先检查，不删除或重建用户的现有环境。Python 建议 3.10 及以上；字体不嵌入 PPTX，服务器可生成结构但不代表完成 Office 渲染验证。

安装验证：运行 scripts/test_svg_to_pptx.py、导出 assets/example.svg；有 PowerPoint 的 Windows 再运行 verify_powerpoint.ps1，检查文字可编辑性和预览。没有 PowerPoint 的服务器只报告结构检查结果。

自带安装器：Windows 使用 `install_windows.ps1 -SourceDir <源包目录>`；同名安装存在时先检查，显式 `-UpdateExisting` 会备份技能源码文件后更新，保留 .venv。Linux 缺少 pip/ensurepip 时，可准备目标 Python/平台对应的二进制 wheelhouse（含 pip）并运行 `python3 scripts/install_linux_offline.py --wheelhouse <目录>`；它仅在该技能内创建无 pip 的 venv 并离线引导依赖，不改系统 Python，默认拒绝已有目标。
