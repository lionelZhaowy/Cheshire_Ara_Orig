# RTL 模块图 C：原生 SVG/PPTX 连续走线试绘

2026-10-13 · L01 · 输入 `c4162204cfee0c48b81158b4296860a678d92bec`，分支 `mp/ara-pulp-v2`。范围为图稿、生成脚本和文档导航。

[打开 A/C 对比](index.html) · [C 原生 PPTX（24 页）](C/editable/diagrams.pptx) · [模块指南](../../rtl_modules/README.md)

## 本次表达方式

采用 [svg-pptx-diagrams-native skill](../../../../../.codex/skills/svg-pptx-diagrams-native/SKILL.md)：协调配色、柔和边框、彩色模块标题带、浅色主体。保留 A 的模块布局、全部文字、213 条连续连线、方向和现有/规划边界；颜色只辅助区分，不增加协议或时钟域含义。这是同一结构的视觉试绘，并未重新拆分 RTL。

此前 A/B 已使用该 skill 的导出后端；本次的区别是使用其绘图约定设计 C 外观，不把更换导出工具冒称为新的拓扑设计。所有箭头都由单个带 marker 的 polyline 表达；PPT 中保留整条路径和原生箭头属性。E 编号仅辅助查共用信号表。

用户已否定 B 的离散模块/配对端口表达。B 文件留作历史档案，活动页面不再展示，旧默认脚本不再生成 B。**用户比较 C 后已确认“还是用 A”；当前文档及后续补图、修订沿用 A，C 仅保留试绘记录。**这一轮不创建或修改 skill。

## 图源和复现

- [build_native_c.py](build_native_c.py)：读取已核对 A SVG，校验实现文件哈希，确定性生成 C 的 SVG/PNG/PDF 和 A/C 比较页；不改 A。
- [connections.json](connections.json)：与 A 共用的模块/连线/信号说明清单。
- [render_manifest.json](render_manifest.json)：输入 A、输出 C、PNG 哈希及模块标题样式清单。
- [verify_native_c.py](verify_native_c.py)：检查拓扑、方向、文字/位置、规划边界、正文修改范围、源码哈希、链接、PDF 字体和原生 PPT。
- [visual_review.json](visual_review.json)：本轮实际查看全部 24 张 PNG 的覆盖与哈希。
- [validation.json](validation.json)：当前检查结果；原 A/B 检查记录仍作为当时快照保留。

从仓库根执行；使用已安装环境，不安装或升级工程依赖：

```sh
/home/zhaowenyao/.codex/skills/publication-figures/.venv/bin/python docs_codex/diagrams/2026-10-13_rtl_modules_native_c/build_native_c.py
python3 /home/zhaowenyao/.codex/skills/svg-pptx-diagrams-native/scripts/run.py --input docs_codex/diagrams/2026-10-13_rtl_modules_native_c/C/*.svg --out-dir /tmp/rtl-native-c-export-new --aspect source
/home/zhaowenyao/.codex/skills/publication-figures/.venv/bin/python docs_codex/diagrams/2026-10-13_rtl_modules_native_c/verify_native_c.py
```

首次交付的导出目标为本目录 `C/editable/`；上面复现命令使用新的空目录，避免覆盖用户已编辑的 PPT。验证脚本检查交付的 `C/editable/`。重新修改图源后，需要复看 PNG 并更新视觉记录、导出到新目录，不能只刷新哈希冒充检查。

## 已检查内容与边界

24 张图已逐张渲染并查看，检查文字、色带、虚线规划边界、箭头端点及连线追踪；未发现本次改样式引入的遮挡或裁切。复用布局不消除复杂模块固有的长回线，连接表仍承担完整信号解释。每条线的位置、方向与 A 自动比对，全部文字和字号/位置保留，只有页脚版本标记从 A 改为 C。

PNG 使用本机 WenQuanYi Zen Hei；PDF 保留矢量文字并检查字体嵌入。PPT 为原生对象，字体不嵌入，连线未绑定模块端口；移动模块后不保证自动跟随。**Office 显示/编辑未实测，浏览器交互未做端到端测试。**这轮未重新进行 RTL 技术审查、编译、仿真或板测；技术依据沿用 A 已核对清单并校验源码哈希。

修改前正文、导航和脚本保存在 [本轮备份](evidence/before_c_style.tar.gz)。正文仅迁移比较入口和替换废弃 B 的查线说明，技术段落及 A 图片保持原样。
