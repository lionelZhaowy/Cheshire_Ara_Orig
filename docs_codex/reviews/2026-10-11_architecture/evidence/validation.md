# 本轮执行与未执行检查

日期2026-10-11，任务M01/I01/S01/P01-AR，仓库根执行，HEAD `2784340240915fe4338ec54bfd613723b127d62e`。本页记录实际检查，不把建议测试写成通过。

| 实际检查 | 命令/方式 | 结果与证据边界 |
|---|---|---|
| 输入状态 | `git status --short`、`git branch --show-current`、`git rev-parse HEAD` | 分支mp/ara-pulp-v2；[初始状态](initial_git_status.txt)，[533个既有文件保护哈希](initial_worktree.json) |
| 关键源码 | 定向`rg --files`、`rg -n`、`nl -ba`/`sed`，对照构建入口及模块消费者 | [32个关键文件哈希及工具路径](source_snapshot.json)；报告附录有模块/函数/行号。未调用Bender checkout/clean或大型构建 |
| 原始ROM指令 | 从生成SV正则抽取2048×32-bit字，小端写/tmp，再用RISC-V objdump反汇编 | 8192 B、索引完整；objdump退出0；[指令证据](bootrom_disassembly.txt)，不是重生成或运行ROM |
| 官方修复 | `git show 9b4c222df72f74f90ab9f36d80ba7b527f92e62b`；`git merge-base --is-ancestor 9b4c222df72f74f90ab9f36d80ba7b527f92e62b HEAD` | 修复对象可读，ancestor检查退出1（预期：未包含）；未应用修复 |
| 外购IP资料 | 受控目录遵循其AGENTS；Word OOXML只读；PDF通过Python标准库解压独立页面内容，核对p9/p13/p18 | 原件未写、未上传；接口摘要、文件身份/hash在报告附录。不是实际RTL接口验收 |
| 工具可见性 | `vsim -version`及`shutil.which` | Questa Sim-64 2024.1退出0；vcs/vlogan当前PATH未找到。宿主WSL2不等于目标CentOS；未测VCS2018 |
| 计算公式 | `PYTHONDONTWRITEBYTECODE=1 python3 docs_codex/reviews/2026-10-11_architecture/scripts/test_budget.py` | 11项全部通过，含单位、读写通道/DDR合计、KV/FIFO、非法输入/来源、换帧率/尺寸；[实际日志](../results/self_check.json) |
| 可复算/覆盖保护 | 相同JSON输入生成到/tmp新目录并逐字比较；对已有结果目录再次生成 | 确定性一致；第二次退出1并保持原字节；同上日志 |
| SVG/PPTX | `draw_architecture.py`；技能`scripts/run.py`转换两张SVG，使用已安装环境，无安装依赖 | [导出报告](../figures/editable_final/export_report.json)含文本、原生箭头/虚线对象和重读结构检查；Office实际显示/编辑未验证 |
| 图片 | Chrome headless只打开本地SVG并截PNG；逐张视觉查看 | 两张PNG可查看；沙箱socket限制通过受审查的本地渲染权限解决。未上传图或源码 |
| 报告HTML | 已安装Python Markdown，`tools/render_report.py`；本地Chrome桌面/手机首屏查看 | 离线单HTML、同目录图片和源链接，无网站部署或新前端框架；截图不等于逐页人工技术签核 |
| 产物与保护 | `tools/check_artifacts.py`；对本轮新增文本检查空白/围栏，检查生产路径无tracked diff | 产物检查与工作区保护结果分列于[artifact_checks.json](artifact_checks.json)。初次保护检查退出1，发现其他教程/旧图并行变化（[保留原记录](initial_protection_observation.json)）；这些文件均未被本轮覆盖/回滚。最终检查如实保留该观察，不将其包装为全部文件未变 |

复算命令（输出目录必须是新的）：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs_codex/reviews/2026-10-11_architecture/scripts/test_budget.py
PYTHONDONTWRITEBYTECODE=1 python3 docs_codex/reviews/2026-10-11_architecture/scripts/budget.py --input docs_codex/reviews/2026-10-11_architecture/inputs/budget_inputs.json --output-dir /tmp/cheshire-review-budget-new
python3 docs_codex/reviews/2026-10-11_architecture/tools/render_report.py
python3 docs_codex/reviews/2026-10-11_architecture/tools/check_artifacts.py
```

ROM抽取命令（仅生成/tmp分析输入，不改源码）：

```python
from pathlib import Path
import re, struct
s = Path('hw/bootrom/cheshire_bootrom.sv').read_text()
words = re.findall(r"(\d+):\s+data_o\s*=\s*32'h([0-9a-fA-F]{8})", s)
assert len(words) == 2048 and [int(i) for i, _ in words] == list(range(2048))
Path('/tmp/architecture_review_bootrom.bin').write_bytes(
    b''.join(struct.pack('<I', int(word, 16)) for _, word in words))
```

```sh
riscv64-unknown-elf-objdump -D -b binary -m riscv:rv64 --adjust-vma=0x02000000 --start-address=0x020000a4 --stop-address=0x02000164 /tmp/architecture_review_bootrom.bin
```

过程中的非产品检查失败：初始少数文件路径/大小写/glob猜测失败后用`rg --files`定位；初版SVG marker少`viewBox`被技能校验拒绝，修正后转换通过；初次Chrome缺用户数据目录/沙箱socket权限，改/tmp用户目录及受审查的只读本地渲染后成功。它们不属于RTL测试失败，亦未伪记为第一次成功。

**未执行：** 报告V01–V13的目标动态用例、RTL compile/elaborate、SoC仿真、Linux启动/驱动、DDR训练/PHY仿真、板测、综合、CDC/RDC工具分析、DFT/MBIST插入、STA/布局/流片签核。未修改生产RTL/sw/配置/filelist/供应商资料，未提交或推送。
