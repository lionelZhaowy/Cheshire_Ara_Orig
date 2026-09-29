# L01 / 机制复审定向收尾

## 基本信息

- 日期：2026-09-29；任务 L01；用户授权落实机制复审 M1–M3。
- 输入 HEAD：`69fabdd227e225bf9f5f0b9ec5fe9d056999fea6`，加既有未提交教材与审查成果；未覆盖他人改动，未提交 Git。
- 状态：三项教材及报告修订完成。七篇/30章框架不变。

## 本轮结果与范围

1. M1：Boot 总表和 SD/NOR 小节改为 mtime 绝对阈值，补充 `spin_until` 与 `spin_ticks` 区别。依据 `hw/bootrom/cheshire_bootrom.c` 的两个调用及 `sw/lib/dif/clint.c` 的实现；代码注释意图、实际行为与器件要求分开。源码哈希见本轮 protection.json。未修改生产代码，也未推断板上启动失败。
2. M2：clocks 现有 PLL 小节新增影响范围表，区分独立 C1 与共享 M/N/参考源调整；明确多域排空、控制器有效时钟、锁定/恢复和相关派生时钟条件。属于现有简化公式及候选架构的条件说明，未冻结 ASIC 参数。
3. M3：report_run.py 在 inputs 之外新增 tested_html，记录全部根目录主页面和兼容 HTML 的 SHA-256；preview_structure_site.py 在结束时核对文件集合和哈希。旧报告不回填。README 同步说明。

修改内容源 `learning/content/boot.html`、`clocks.html`，用 build_site.py 同步生成网页；其他范围为上述检查脚本、维护说明、交接与状态索引。无 RTL、软件、接口、地址、IRQ、位宽或依赖变化。

## 验证证据

从仓库根执行，以下命令退出码均为 0：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs_codex/learning/scripts/build_site.py
PYTHONDONTWRITEBYTECODE=1 python3 docs_codex/learning/scripts/check_structure.py --out-dir docs_codex/learning/evidence/closeout-20260929/checks
PYTHONDONTWRITEBYTECODE=1 python3 docs_codex/learning/scripts/preview_structure_site.py --out-dir docs_codex/learning/evidence/closeout-20260929/browser
```

这些输出目录已经存在，复跑请换新目录或使用默认临时目录，不能覆盖。

- [只读结构报告](../learning/evidence/closeout-20260929/checks/checks.txt)：54 HTML、2711 项本地链接/资源，七篇/30章、373迁移及历史保护通过；Markdown 链接计数是写入本交接前的快照。
- [浏览器报告](../learning/evidence/closeout-20260929/browser/browser.txt)：34 主页面桌面/手机、7 页无脚本、199 条跨页旧书签和主要交互通过；54 HTML 在测试期间字节及文件集合不变。
- [输入与被测页面版本](../learning/evidence/closeout-20260929/browser/run.json)：实际运行时间、Chrome 版本（browser.txt）、源文件与 HTML 哈希。HEAD 单独不能标识当前未提交网页。
- [历史保护与源码哈希](../learning/evidence/closeout-20260929/protection.json)：本轮开始前的 evidence 和旧站备份按 input.json 逐项比对，全部保持。
- 未重跑生成一致性比较；本轮仅使用明确的 build_site.py 更新教材 HTML，以及不含生成分支的只读检查。上一审查的自动审批拒绝见原审查记录，未将旧比较结果记为本轮实测。
- 未构建软件、未运行 RTL 仿真/板测/ASIC 实现。

## 下一步

教材可按团队试读反馈继续收尾。若 S01 要判断启动代码是否应改为相对等待，需核对器件要求、计时起点和实际启动时序，再单独实施及验证；本轮不授权底层修复。最少续读本交接、Boot 小节和 CLINT 实现。
