# DDR–GB 一致性图稿

2026-10-15，L01。正文见[缓存一致性审查与架构比较](../../../engineering/Cache_Coherence_Architecture.md)。图示为未实施的候选职责和逻辑过程，不是冻结的 RTL 拓扑。

| 图 | SVG 母版 | PNG 预览 |
|---|---|---|
| 系统与一致性边界 | [system.svg](system.svg) | [system.png](system.png) |
| DDR 地址数据搬入 GB | [read-to-gb.svg](read-to-gb.svg) | [read-to-gb.png](read-to-gb.png) |
| GB 数据写入 DDR | [write-to-ddr.svg](write-to-ddr.svg) | [write-to-ddr.png](write-to-ddr.png) |

[三页原生可编辑 PPTX](export/diagrams.pptx) · [导出报告](export/export_report.json) · [检查结果](evidence/validation.json)

采用 `industrial-svg-pptx` 与 `svg-pptx-diagrams-native` 后端：1920×1080、连续正交连线；跨线跳线表示无连接。系统图合并画出请求/返回，过程图的箭头不表示逐周期握手。GB 支路、设备代理与一致性协调均保留候选状态。

SVG/PNG 使用本机文泉驿正黑；PPTX 指定 Microsoft YaHei，以本机字体做尺寸测量。文字、模块和箭头为独立原生对象；移动模块不保证连线自动跟随。已查看三张最终 PNG，PPTX 已保存重读并检查 XML；**没有实际运行 Office 显示/编辑验证**。

## 再生成

在仓库根运行，所有输出目录必须是新目录。先改 `build_figures.py`，不独立编辑生成文件。不得覆盖本次 evidence；检查后才能另行发布新版本。

```sh
python3 docs_codex/diagrams/2026-10-15_cache_coherence/build_figures.py --out-dir /tmp/coherence-source-new
python3 docs_codex/diagrams/2026-10-15_cache_coherence/render.py --source-dir /tmp/coherence-source-new --out-dir /tmp/coherence-render-new
```

PPTX 使用已安装技能目录中的 `svg-pptx-diagrams-native/scripts/run.py`，三个 SVG 按系统、读、写顺序传入；参数为 `--aspect source --font 'Microsoft YaHei' --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`。技能根目录随环境解析，不随仓库安装或修改依赖。原始 SVG 无字体描边，PNG 由本地 Chrome 渲染。

## 本次证据

- [输入快照](evidence/input.json)：主仓库 HEAD、依赖来源 HEAD、源文件与 30 个既有文件哈希。
- `source-01` / `render-02`：首次成功渲染。`render-01` 因沙箱 socket 限制失败，日志保留；随后经环境审批在沙箱外渲染本地 SVG。
- [source-02](evidence/source-02/layout.json) / [render-03](evidence/render-03/browser.json)：正式输入与最终预览；修正部分写过程的 clean/失效顺序，并改用已安装无衬线字体。根目录三组 SVG/PNG 与此批次一致。
- 原生导出共 3 页、119 个文本对象、29 个箭头对象；没有整图图片。历史草稿只作证据，非额外候选版。

检查命令：`python3 docs_codex/diagrams/2026-10-15_cache_coherence/validate.py --out-file /tmp/coherence-validation-new.json`。硬件并发、错误恢复与性能用例仅列入正文验收要求，本次未执行。
