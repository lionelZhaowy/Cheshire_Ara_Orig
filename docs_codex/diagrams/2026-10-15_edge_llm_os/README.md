# 边缘大模型推理：OS 选择与软硬件协作图

2026-10-15，L01；输入 `mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`。配套[正式 Markdown 专题](../../engineering/Edge_LLM_OS_Selection.md)。每图一个正式版本；无 OS 移植、RTL 改动或目标运行。

| 图 | SVG 母版 | PNG 阅读版 |
|---|---|---|
| 裸机、RTOS 与 Embedded Linux 软件栈 | [software-stacks.svg](software-stacks.svg) | [software-stacks.png](software-stacks.png) |
| 一次推理任务的软硬件协作 | [inference-flow.svg](inference-flow.svg) | [inference-flow.png](inference-flow.png) |

[两页原生可编辑 PPTX](export/diagrams.pptx) · [导出报告](export/export_report.json) · [验证结果](evidence/validation-final.json) · [作者视觉检查](evidence/visual_review.json)

## 图意与风格

软件栈图采用 `svg-pptx-diagrams-native`：浅色分层、协调框线，左侧为服务/设备请求，右侧为 RVV 指令执行。中间框表示职责而非每次调用必须穿过的精确函数栈；Linux 内核负责上下文管理，用户态向量指令无需逐条经 NPU 驱动提交。三列是替代环境，不代表三个实例。

推理协作图采用 `industrial-svg-pptx`，复用同一原生导出后端：薄深色边框、功能分区、连续正交走线。紫色是控制/状态，蓝灰是主存访问，绿色是 GB 数据访问。双向箭头合并表达双向能力，不代表同时进行。任务控制是待实现的协调职责，不预设独立控制器 IP；GB 为独立 SRAM，图不引入 CPU 直接访问 GB，也不冻结当前缓存一致性候选方案。

两图均为 2400×1350。SVG 与 PNG 保留中文 text，字体为本机文泉驿正黑；PPTX 指定 Microsoft YaHei，并用本机字体测量。PPTX 不嵌入字体，目标机器需具备对应字体或自行替换。

文字、模块及完整箭头均为原生 PPTX 对象，未用整图图片替代。连接器尚未绑定模块端口，移动模块不保证连线自动跟随。**结构检查通过，Office 显示与编辑未验证。**

## 再生成

在仓库根执行；输出必须为新目录，避免覆盖证据。先修改生成脚本，再生成 SVG，不独立修改 PNG 或规范化导出 SVG。

```sh
python3 docs_codex/diagrams/2026-10-15_edge_llm_os/build_figures.py --out-dir /tmp/edge-llm-source-new
python3 docs_codex/diagrams/2026-10-15_edge_llm_os/render.py --source-dir /tmp/edge-llm-source-new --out-dir /tmp/edge-llm-render-new
```

`render.py` 改编自仓库 L01 缓存一致性图的渲染器，只复用已跟踪 `learning/scripts/preview_structure_site.py` 中的 CDP 通信类，不执行其测试入口。需要已安装的 `google-chrome`；仅打开本地 SVG。若环境限制本地套接字，按环境审批机制运行，不绕过策略。

PPTX 使用已安装 `svg-pptx-diagrams-native/scripts/run.py`，按软件栈、推理协作顺序传入 SVG，参数为 `--aspect source --font 'Microsoft YaHei' --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`。通过当前技能目录解析导出器路径，不自动安装或修改技能依赖。导出到新的空目录后再检查。

验证可单独运行，输出同样不得覆盖：

```sh
python3 docs_codex/diagrams/2026-10-15_edge_llm_os/validate.py --out-file /tmp/edge-llm-validation-new.json
```

正文和图片含仓库相对链接，整体保留目录关系即可离线阅读本地内容；官方外链仍需网络。

## 检查证据

- [输入快照](evidence/input.json)：HEAD、原始 Git 状态、92 个既有文件及源码的哈希；工程索引修改前内容另存为 [快照](evidence/engineering_readme_before.md)。该快照用于恢复与逐字对照，不作为导航文档维护。
- `evidence/source-01/`：本次两张 SVG 的生成输入；根目录母版与其一致。
- `evidence/render-01/`：首次 Chrome 被沙箱套接字限制阻止，原始失败日志保留。
- [render-02](evidence/render-02/browser.json)：经环境审批的本机渲染通过，两图均无文字越界、框内溢出、文字相互重叠或文字/连线交叉；逐张查看实际 PNG。
- `export/`：两页、119 个文本对象、28 个原生箭头对象、8 个原生虚线对象，保存后重读并核对 XML。
- [首次验证](evidence/validation.json)：产物检查通过，输入全一致检查失败；检测到独立 GB 图稿的 `build_figures.py` 在本轮期间改变，本任务未写该路径。
- [最终验证](evidence/validation-final.json)：文档/图稿检查通过，状态为 `pass_with_external_changes`；输入全一致仍如实记为 false。[外部变化记录](evidence/external_change.json)保留输入与结束哈希，未覆盖或回滚该脚本。验证器仅识别已记录的这个变化，其他差异仍报失败。

以上只验收文档和图稿；OS、模型推理、总线一致性、DDR/GB/NPU 实现与性能均未在本次运行验证。
