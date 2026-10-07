# L01 / 结构化 SVG 与原生可编辑 PowerPoint

## 基本信息

- 日期：2026-10-06；任务 L01。
- 用户授权：修复 SVG 转 Office Shape 后文字丢失及矩形变形问题；保持文字为 text、各图形独立；补充授权直接生成 PPTX，并按已阅读的 DDR Datasheet 修正过时内容。
- 输入：`mp/ara-pulp-v2`，HEAD `5ddec4fb4`。既有未跟踪目录为本对话此前生成的 diagrams/ 和 AXI RT 答疑交接，原样保护。
- 状态：结构化 SVG 和原生 PPTX 交付完成；SVG 的 Office Convert to Shape 流程未实测，不声称所有 Office 版本会保留 SVG 文字。
- 修改边界：diagram 专题目录与本交接；无 RTL/sw/config/filelist 修改，无 Git 提交。

## 交付

最终用户文件均在 `docs_codex/diagrams/2026-10-06_axi_crossbar_ara/ppt_editable_final/`：

- `crossbar_ara_ppt.svg`：保持原图所有 64 个 text；30 个独立直角矩形、37 条独立曲线、14 条直线、16 个独立箭头三角形。无 CSS/marker/defs/use/image、文字轮廓、合并全图路径。
- `ddr_qos_proposal_ppt.svg`：36 个 text；15 个矩形、10 条线、10 个箭头。
- `cheshire_ara_ddr_editable.pptx`：2 页，分别 161 / 71 个独立原生对象；文字为文本框，曲线为独立 DrawingML cubicBezier 自由曲线。无内嵌位图或 SVG 图片。
- `powerpoint-slide-1.png`、`powerpoint-slide-2.png`：实际 PowerPoint 导出预览。
- `export_report.json`：来源哈希、SVG 元素计数和生成检查；`office_verification.json`：实际 Office 打开、文字读取/编辑探针、导出结果。
- `native_slide_1.pptx`、`native_slide_2.pptx` 是同目录的单页原生版本。

SVG 全部采用逐元素呈现属性、Microsoft YaHei、直角 rect、独立 line/path/polygon；不依赖样式继承、透明度或 marker。灰色连接矩阵预混合颜色，保持视觉淡化。PPTX 显式清除主题阴影，调整一处字体替换后的标题间距。SVG 保留 text 不等于 PowerPoint 转换器一定生成可编辑文本，原生 PPTX 是已实测的可编辑交付。

## 技术内容适配

- `crossbar_ara.svg` 当前仿真配置事实未过时，原文件和原 PNG 保持不变；兼容导出只调整呈现。
- `ddr_qos_proposal.svg` 与 PNG 已更新：LLC 外存出口 → S0，ISP → S1，NPU → S2；控制器内含端口 Arbiter 和 Controller Core/FR-FCFS 命令调度，不再必画控制器外部共享 DDR Crossbar。
- 原 DDR 图保存为 `ddr_qos_proposal_before_datasheet.svg`，可恢复。
- 依据用户提供的 INNOSILICON Combo Controller Datasheet V2.1（2024-09）：p8 多端口；p10 仲裁特性；p13 QoS；p17–18 架构及调度；p14 独立 urgent 接口不支持。图仅保留授权范围内的接口摘要与页码，未复制供应商架构原图或 PDF。
- 图明确标注建议尚未实现；没有声称带宽保底/最长等待保证已存在。采购 IP 的具体配置规则仍需 User Guide/Register Table。
- 受控资料在用户指定 D 盘路径，本轮未修改该文件，未上传。

## 验证证据

- `export_ppt_editable.py` 使用 python-pptx 1.0.2 / Pillow 12.3.0，依赖仅安装在 `/tmp/cheshire-ppt-export.EKRJVt`，未更改工程依赖。
- 命令：`PYTHONPATH=/tmp/cheshire-ppt-export.EKRJVt PYTHONDONTWRITEBYTECODE=1 python3 docs_codex/diagrams/2026-10-06_axi_crossbar_ara/export_ppt_editable.py --out-dir <新空目录>`。默认拒绝已有输出；`--svg-only` 可只生成结构化 SVG。
- 命令退出 0；SVG 逐项文字与源相同；PPTX 保存后重新读取，100 个非空文本对象逐项相同。ZIP 完整性通过，无 ppt/media/。
- `verify_powerpoint.ps1` 用本机 Microsoft PowerPoint 16.0 只读打开最终 PPTX，不使用 ActivePresentation，不调用应用 Quit；只关闭本轮测试文档。每页一个文本对象的首字符修改、读回、恢复探针通过，未保存测试修改。
- PowerPoint 读取 2 页、161/71 对象、64/36 文本，全部文本内容与 SVG 逐项相同；2 页 1680×1160 PNG 导出成功。人工查看最终预览：文字、矩形、箭头、曲线完整，标题无碰撞，主题阴影已去除。
- 浏览器渲染新版 DDR SVG 和其结构化导出成功，更新了根目录对应 PNG。首次原生生成遇到 Connector 无 fill 属性，已在导出器区分处理，最终生成和 Office 验证通过。
- 中间试制输出在 `ppt_editable/`、`ppt_editable_v2/`，最终请使用 `ppt_editable_final/`，未把中间预览当最终结果。
- 未执行 SVG → Office Shape 自动转换；不能把原生 PPTX 的通过当作该流程通过。
- 未 RTL 编译/仿真/板测或实施 DDR 集成。

## 下一步

1. 用户直接打开最终 PPTX，选中原生对象复制到自己的演示文稿；SVG 继续保留为可编辑源格式。
2. 若继续试 SVG Convert to Shape，使用最终目录的新 SVG；如特定版本仍丢失文字，优先采用已验证的原生 PPTX，不将文字转 path。
3. 后续 DDR/互连评估仍需受控 User Guide/Register Table；本次仅改图，不冻结架构或仲裁参数。无需改变共享任务状态。
