# 安装与切换

目录名为 `svg-pptx-diagrams-native`，与旧 `svg-pptx-diagrams` 和 `publication-figures` 并存；调用 `$svg-pptx-diagrams-native` 选择本版，调用 `$svg-pptx-diagrams` 选择旧版。不修改其他 skill 的发现/调用策略。

仅复制本目录源文件；目标平台单独创建虚拟环境，不复制 .venv/__pycache__ 或覆盖用户已有环境。Linux/WSL：

```sh
python3 -m venv ~/.codex/skills/svg-pptx-diagrams-native/.venv
~/.codex/skills/svg-pptx-diagrams-native/.venv/bin/python -m pip install -r ~/.codex/skills/svg-pptx-diagrams-native/requirements.txt
python3 ~/.codex/skills/svg-pptx-diagrams-native/scripts/run.py --input figure.svg --out-dir export-new
```

Windows 将代码复制到用户选定的新技能目录，用 `python -m venv .venv`，再 `.venv\Scripts\python.exe -m pip install -r requirements.txt`。`scripts/run.py` 会等待导出完成并传回退出码。本版不自带自动覆盖旧技能的安装器。

回归：用安装依赖的 Python 执行 `-m unittest discover -s scripts -p "test_*.py"`。预览：导出 assets/native_example.svg，在浏览器查看 SVG；可用 verify_powerpoint.ps1 验证 Office（须环境允许，不绕过执行策略）。PPT 字体应在目标电脑安装，程序化读写测试不是 Office UI 实测。
