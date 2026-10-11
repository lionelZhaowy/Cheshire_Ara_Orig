# L01 / 元数据 BIST、main 返回与初始化图

> 记录日期：2026-10-08。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-08；任务 L01。
- 用户授权：解释 tag/valid/dirty BIST 的目的、main 完成后的 CPU 状态；指定科研图 SVG 与可编辑 PPTX skill，生成软硬件对应图及程序执行流程图。
- 输入：`mp/ara-pulp-v2`，HEAD `278434024`；已有两份同日源码答疑交接未跟踪，保留。
- 状态：答疑及图/PPTX交付完成；Office 实际验证受执行策略限制未完成。
- 负责路径：新 `docs_codex/diagrams/2026-10-08_boot_initialization/` 和本交接。未修改 RTL/sw、依赖、公共教材或共享状态，未提交 Git。

## 源码结果

- `axi_llc_tag_store.sv:300` 将 tag、valid、dirty 读出值与图样作 XNOR 比较；313 行将三部分结果合并。自测既检查图样读写，又在末尾清零元数据；Valid=0 避免未知 SRAM 数据被视为有效缓存行，Dirty=0 避免把无效启动状态作为待回写数据处理。Tag 错误可能造成错误命中/回写归属。
- 依据 tag_pattern_gen 的实际读写序列解释，不宣称能覆盖所有物理故障或制造测试。数据 SRAM 不在该 tag BIST 内，ROM 只等待 DONE，错误结果需另看 BIST_OUT。
- 当前裸机 main 正常返回先进入应用 CRT0 的_exit，恢复栈上保存的 sp/gp/ra，写 scratch2，再 ret。CPU 不因 C 函数 return 自动断电/停钟/复位/换权限。仿真环境可在观察到完成后停止整个仿真，不能说成 CPU 关机。
- 图2明确标记 boot_next_stage 返回链的 ret 自循环为源码推导；也明确排除 JTAG 直接 PC、UART invoke、OS 用户进程退出契约。前轮已详查该问题，没有新增动态验证。

## Skill 与产物

- 阅读 `/home/zhaowenyao/.codex/skills/svg-pptx-diagrams/SKILL.md` 和 `references/svg-profile.md`，使用 `scripts/run.py`；另阅读实际 Office 验证脚本，未改 skill。
- 最终使用图目录的 `export_final/`：两份 `.editable.svg`、两份 PNG、`diagrams.pptx`、`export_report.json`；根目录两份 SVG 为最终母版，README 导航和技术边界齐备。
- 两页 16:9 PPTX 有 85/83 个原生对象，50/47 个文本对象，最小文字 10.71 pt（来源/边界脚注）；正文使用更大字号。逐项文字和对象数重读一致，ZIP 完整、无 ppt/media/。
- `export/` 为中间版，保留；最终母版图1减小两个标题/设备行宽，图2调整退出现场措辞与观察者标题，避免跨框。最终两张预览人工检查完成。

## 实际命令及结果

- 导出：`python3 /home/zhaowenyao/.codex/skills/svg-pptx-diagrams/scripts/run.py --input <两份母版SVG> --out-dir docs_codex/diagrams/2026-10-08_boot_initialization/export_final --aspect 16:9`，退出 0。脚本使用 skill 可用隔离环境，无安装或工程依赖修改。
- 渲染：Chrome headless，1600×900，独立 mktemp profile、file:// 输入；沙箱内两次退出133，按权限流程重试后均退出0。最后再渲染修订版到新的 export_final/，退出0。
- Office：通过 `powershell.exe -NoProfile -File <skill verify_powerpoint.ps1> -Presentation <本轮新PPTX> -OutDirectory <本轮输出>` 尝试只读打开/文字编辑探针/导出。脚本在进入前即被签名策略拦截，退出1（UnauthorizedAccess）；没有打开或修改任何用户文稿，没有改全局执行策略。最终PPTX同样未在Office实测。
- 独立 ZIP 检查输出 integrity=None，media=[]，恰有 slide1.xml/slide2.xml。未把浏览器图当 Office 预览。
- 最终母版 SHA-256：图1 `fcd54ee815cc89d21dd0982ff1a994f1672b6d490276a2b23e53810182c76a06`；图2 `0cf010da0dcecfec3ad40e4c0b368b00ca90f4792776a62f9bd3b54bce5b1633`。
- `git diff --stat -- hw sw target` 无输出；未重新编译 ELF/ROM、未运行 RTL/板测。

## 下一步

1. 用户可以打开 export_final/diagrams.pptx 编辑各对象；需要 Office 外观验收时，在允许执行的本地环境运行现有只读验证脚本。
2. S01/V01 根据既有交接决定是否需要可返回载荷，另行授权修复和目标验证；P01分别处理 tag/data SRAM 工艺与制造测试覆盖。
3. 本轮图片没有改变产品架构或关闭技术缺口，暂不改共享状态/任务表。
