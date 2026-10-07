# 结构化 SVG 导出子集

支持 rect（含等半径圆角）、circle、ellipse、line、polyline、polygon、单连续轮廓的 path，以及单行 text。支持无 transform 的 g 分组与呈现属性继承；导出时每个图形/文本成为独立对象。

路径支持绝对/相对 M、L、H、V、C、Q、Z；二次曲线精确转换为三次 Bézier。暂不支持 A/S/T 和复合轮廓。可用独立曲线/图形改写；不能把所有文字或全图改为路径来绕过限制。

使用显式 x/y/width/height、fill、stroke、stroke-width、font-family、font-size、font-weight、font-style、text-anchor。颜色用 #RGB/#RRGGBB 或 none；不使用渐变/滤镜/裁剪/蒙版。字号及坐标使用数字或 px。圆角矩形 rx 与 ry 必须相同（仅 rx 时沿用同半径）；不同横纵半径暂不支持。

text 保留实际字符串；多行文本拆成各自有绝对 x/y 的多个 text。text-anchor 可为 start/middle/end。支持 normal/bold 或数值字重（600 及以上映射为粗体）。不嵌入字体，跨系统须确认字体可用；CJK 优先目标 Windows 已安装的 Microsoft YaHei，英文出版按期刊选择字体。PPTX 文本框基线需要实际渲染检查，不承诺所有字体像素级一致。

箭头头部用独立 polygon，例如 line + triangle；不使用 marker/defs/use。导出器拒绝 CSS class/style、tspan/textPath、transform、外部图片、透明度、dash、非默认 linecap/join 等尚未支持的特性，错误会定位元素。这些是当前实现边界，不是 SVG 或 PowerPoint 的固有限制。

依赖可安装在隔离环境，例如：

```sh
python3 -m venv /tmp/svg-pptx-env
/tmp/svg-pptx-env/bin/python -m pip install -r requirements.txt
/tmp/svg-pptx-env/bin/python scripts/svg_to_pptx.py --input figure.svg --out-dir output-new
```

若同名环境/输出已存在，先检查或使用新的目录，不删除它们。不要将临时依赖目录硬编码进 skill 脚本。

Windows 实测：

```powershell
powershell.exe -NoProfile -File scripts/verify_powerpoint.ps1 -Presentation C:\work\output-new\diagrams.pptx -OutDirectory C:\work\output-new
```

WSL 调用时使用 wslpath -w 解析路径。执行策略或沙箱限制由环境批准处理，脚本不改全局执行策略。
