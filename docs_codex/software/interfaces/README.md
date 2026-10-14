# Cheshire 软硬件接口专题

阅读：[HTML 入口](index.html) · [Markdown 入口](markdown/index.md)。顺序为总览→基础软件/BSP→构建启动→指令/CSR→内存/MMIO→异常中断→五条案例→集成修改→实践验证。

本专题是 L01 现有软件参考体系下的连续阅读专题，不改变主教材九篇42章的顺序。与[RTL模块指南](../../rtl_modules/README.md)互补，生产源码保持只读。初版基线为2026-10-13、`mp/ara-pulp-v2` / `c4162204cfee0c48b81158b4296860a678d92bec`；基础软件扩充基线为同日`bf1b4198dfd74cc78291c152b8b682d523e785c5`，当前共9对页面。

## 维护方式

沿用主教材的 **HTML 正文单一来源 → HTML/Markdown 两种阅读输出**。章节清单是`scripts/pages.json`；修改 `content/*.html`，不要单独编辑生成的 `markdown/*.md`。`scripts/build.py`复用现有课程的标题/目录函数及Markdown导出器，并引用主教材CSS/JS，不改写原51页课程。

在仓库根运行：

```sh
python3 docs_codex/software/interfaces/scripts/build.py
python3 docs_codex/software/interfaces/scripts/check.py
# 需要落盘时另加 --out 新报告路径，禁止覆盖历史报告
python3 docs_codex/software/interfaces/scripts/preview.py --out-dir /tmp/cheshire-interface-preview-new
```

浏览器证据输出必须使用不存在的新目录。`check.py`检查本专题源链接、页面锚点/图片、双格式内容、源码身份和本轮证据；不声称全仓旧文档链接均正常。默认校验批次为`evidence/complete-stack-20261013/`，可用`--evidence-dir`选择另一批次；该批次的`checks.json`指定浏览器、图稿及授权修改。默认只打印结果，`--out`只接受新报告文件。新批次需重新核对源码并建立独立清单，不覆盖历史哈希或旧结果。浏览器脚本按当前章节清单和页面引用的SVG自动检查页数、图片与画布。

## 图稿和验证

[初版四张图及可编辑PPTX](../../diagrams/2026-10-13_software_hardware_interfaces/README.md)。图源按本次日期独立保存，旧图未重绘或移动。

[实践页](labs.html#evidence)区分本轮静态检查、独立软件编译、文档浏览器检查及未执行的目标运行。[L01主题交接](../../handoffs/L01_software_hardware_interfaces.md)供后续S01/V01/M01协调；不是功能修复授权。

完整仓库内可离线打开本专题；复制时需保留相对路径所指的主教材CSS/JS、图稿和源码。第三方短代码片段来自相应源文件，原版权/许可证继续保留；本专题没有改动或重新许可这些文件。

本次新增[基础软件与BSP（Markdown）](markdown/foundation-software.md)与[软件栈图](../../diagrams/2026-10-13_foundation_software/README.md)。本次只进行源码/工具查询及图文检查，未重新构建或运行目标程序；初版编译证据保留原输入身份。

新增[全组件软件栈与39类源码索引](foundation-software.html#complete-stack)，保留原UART/Flash调用链图；[SVG/PNG/原生PPTX](../../diagrams/2026-10-13_complete_software_stack/README.md)。当前验证独立保存于[complete-stack批次](evidence/complete-stack-20261013/validation.json)，旧foundation批次只对应修改前页面。
