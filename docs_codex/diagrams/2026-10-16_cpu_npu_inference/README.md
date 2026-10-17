# CPU＋NPU 推理体系图稿

2026-10-16，L01。[正式专题](../../engineering/CPU_NPU_Inference_Systems_Survey.md) · [四页原生 PPTX](export/diagrams.pptx)

四图均为依据公开资料重新组织的中文示意图，使用 `industrial-svg-pptx` 风格和 `svg-pptx-diagrams-native` 导出后端；未截取或嵌入第三方整图。一个主题对应一个正式版本，根目录 SVG 是母版，PNG 与 PPTX 从同一母版生成。`evidence/` 中的中间产物只记录检查过程。

| 图 | 母版与阅读版 | 依据与省略 |
|---|---|---|
| 模型部署全链路 | [SVG](deployment-chain.svg) / [PNG](deployment-chain.png) | NVDLA、Ethos-U、ExecuTorch、Deeploy 的职责归纳；不表示统一厂商 ABI 或固定 SoC 拓扑 |
| 三种调用方式 | [SVG](invocation-paths.svg) / [PNG](invocation-paths.png) | NVDLA headless Linux、Ethos-U Cortex-M、Gemmini RoCC；省略 CPU 普通访存 |
| Deeploy / Siracusa | [SVG](deeploy-siracusa.svg) / [PNG](deeploy-siracusa.png) | Deeploy 论文 Fig. 1、Fig. 5、§V 和 Siracusa 论文；互连归并表达职责，省略端口、宽度与容量 |
| LLM 阶段与分工 | [SVG](llm-phases.svg) / [PNG](llm-phases.png) | 上部通用自回归关系；下部 llm.npu v2 §3 的特有机制，不表示本工程存在 GPU |

全部连接连续绘制。紫色为调用/控制，蓝灰为张量/结果，绿色为局部存储或 KV 数据，棕色为编译产物。图 4 虚线区域表示论文特有机制。箭头是逻辑关系，不承诺同时执行；来源与条件详见正文。

## 复现

从仓库根执行，输出到新的空目录，避免覆盖已经审阅的图稿：

```sh
python3 docs_codex/diagrams/2026-10-16_cpu_npu_inference/build_figures.py --out-dir /tmp/inference-svg-new
python3 docs_codex/diagrams/2026-10-16_cpu_npu_inference/render.py --source-dir /tmp/inference-svg-new --out-dir /tmp/inference-png-new
```

生成脚本只用 Python 标准库。渲染器使用已安装 Chrome 和仓库 `docs_codex/learning/scripts/preview_structure_site.py` 中的 CDP 传输类；不运行该旧脚本的主程序、不更改旧图。Chrome 需要本地调试套接字；本环境在沙箱外经自动审批运行。生成的 PNG 为 2400×1350。

PPTX 使用已安装 skill 的原生导出器。将 `native_skill_root` 指向 `svg-pptx-diagrams-native` 实际目录后执行：

```sh
python3 "$native_skill_root/scripts/run.py" \
  --input /tmp/inference-svg-new/deployment-chain.svg \
          /tmp/inference-svg-new/invocation-paths.svg \
          /tmp/inference-svg-new/deeploy-siracusa.svg \
          /tmp/inference-svg-new/llm-phases.svg \
  --out-dir /tmp/inference-pptx-new --aspect source \
  --font 'Microsoft YaHei' \
  --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc
```

SVG/PNG 使用文泉驿正黑；PPTX 指定 Microsoft YaHei，未嵌入字体。PPT 中的文字、矩形与箭头为原生对象，折线保持整条对象；移动模块不保证箭头自动跟随。**结构检查通过，Office 显示与编辑未验证。** 不把结构检查或 PNG 检查表述为 Office 实测。

```sh
python3 docs_codex/diagrams/2026-10-16_cpu_npu_inference/validate.py --out-file /tmp/inference-validation-new.json
```

## 本次检查记录

- [输入快照](evidence/input.json)：分支、HEAD、原始工作区状态及 288 个已有文件/相关源码哈希；[索引修改前快照](evidence/engineering_readme_before.md)用于逐字核对。
- [主来源](evidence/sources.json)、[补充来源](evidence/sources-extra.json)：公开 URL、获取日期、提交与内容哈希。初次 Deeploy API 限流和两个路径错误被保留，改由可访问的作者仓库、论文和官方文档补足；失败页面未作为技术依据。
- `evidence/render-01/`：Chrome 被沙箱套接字限制阻止；`render-02/`发现三处线/文字交叉，调整后 `render-03/`通过。`export-01.log`记录 SVG ID 重名，随后修正。
- `evidence/render-04/`：Chrome 端口文件创建与写入之间的等待竞争导致失败，渲染器已修正；[render-05](evidence/render-05/browser.json)是最终母版的通过记录。
- [视觉检查](evidence/visual-review.json)：作者逐张查看四张实际 PNG，检查文字、遮挡、箭头方向和图文边界；最终 PNG 与已查看的 `render-03` 逐字节一致，后续只修正 SVG 标识命名。
- [导出记录](export/export_report.json)：保存后重读四页 PPTX，共 156 个文字对象、46 条原生箭头、1 个原生虚线框；无整图图片替代。
- [最终验收](evidence/validation.json)：正文覆盖、相对链接、图稿可复现性、连线端点、PPTX XML 和已有文件保护；[外链检查](evidence/external-links.json)保留实际 HTTP 结果。

本次只验收文档和图稿，没有安装模型 SDK、运行目标模型、修改 RTL/sw、升级依赖或验证硬件性能。文件整体搬迁时须保留仓库相对目录关系；官方外链需要网络。
