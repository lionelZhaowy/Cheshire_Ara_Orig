# 导出能力与限制

后端由 svg-pptx-diagrams 的 2026-10-10 快照独立演进，旧文件 SHA-256：`a90319fc1d553ff326fc092e48e5aff9f66062c7e4890e105046996b21dfe438`。旧 skill 不需安装；此目录包含完整实现。

支持显式属性的 SVG rect、circle、ellipse、line、polyline、polygon、单一子路径 M/L/H/V/C/Q/Z、独立 text；g 可继承基础样式但不支持 transform。颜色用 #RGB/#RRGGBB/none。文字不使用 tspan；换行拆成独立 text。箭头为独立三角形。虚线支持一个正数 dash/gap 对（原生 DrawingML custom dash）。不支持 CSS、marker、透明度、滤镜、clip/mask、image、复合路径、弧线命令与复杂排版，遇到即报错，不偷偷栅格化。

坐标取自 viewBox；最终宽度由 --width-mm 明确指定，等比确定高度。字体有效大小为 `font_size × width_mm × 72 / 25.4 / viewBox_width`；报告同时记最小线宽。--min-font-pt 是用户可改的工作阈值。图源中的裸坐标单位不代表最终 pt。默认 source 比例；固定比例只在明确需要时使用。

文本字体名和 --font-file 应匹配。SVG/PDF 渲染由 CairoSVG/fontconfig，PPT 字体需目标电脑安装；字体文件不被嵌入 PPT。PDF 报告检查字体是否嵌入、尺寸、无整图图片，但不能保证每个语言字形都正确；须查看中文/符号实物。PDF 内搜索文字也不能代替字形检查。

--render 依赖 CairoSVG 与系统 Cairo，生成 PDF、300 dpi PNG、灰度 PNG；PyMuPDF 检查 PDF。PNG 是预览衍生品。PPT 保留独立对象，但移动模块不会自动重连箭头；不支持语义分组或双向同步。Office 只读验证可用 verify_powerpoint.ps1；遵守环境执行策略，不能绕过签名策略来宣称通过。

依赖安装：在本 skill 下 `python3 -m venv .venv`，然后 `.venv/bin/python -m pip install -r requirements.txt`（Windows 使用 Scripts/python.exe）。不要复制跨系统虚拟环境或修改任务工程依赖。
