# SVG 与原生对象约定

支持 rect（等半径圆角）、circle、ellipse、line、polyline、polygon、单连续 path 和单行 text。路径为 M/L/H/V/C/Q/Z（绝对或相对），Q 转换为三次曲线。无 transform 的 g 支持属性继承，导出时展开。text 可编辑，多行拆成独立 text。新图保持对象语义，而非把所有东西拆成最小线段。

使用显式坐标/呈现属性；数字或 px 坐标、#RGB/#RRGGBB/none 颜色，stroke-linecap 默认 butt、stroke-linejoin 默认 miter。基础限制沿用原版：不支持 CSS style/class、transform、image、tspan、复合子路径、A/S/T、透明度、滤镜、裁剪、蒙版、use 等。遇到不支持内容报错，不悄悄栅格化。

## 完整虚线框

```xml
<rect id="optional-domain" x="40" y="40" width="400" height="220" rx="16"
      fill="#F3F7FD" stroke="#7896B5" stroke-width="2" stroke-dasharray="10 6"/>
```

这是一个 PPT 圆角矩形对象。每个虚线段不是独立形状。支持任意正数 dash/gap 数组（单位为 SVG 坐标单位）；奇数长度数组按 SVG 规则重复一遍。使用 `none` 为实线。暂不支持零/负数、百分比、dashoffset 或圆端点点线；不能默默丢弃不支持的视觉效果。dash 值按线宽换算成 DrawingML custom dash 百分比。

## 完整箭头

原生端点只支持下列明确的实心三角 marker 子集；不是任意 SVG marker 转换器。

```xml
<defs>
  <marker id="arrow-blue" markerUnits="strokeWidth"
          markerWidth="3" markerHeight="3" viewBox="0 0 3 3"
          refX="3" refY="1.5" orient="auto-start-reverse">
    <polygon points="0,0 3,1.5 0,3" fill="#3575A6"/>
  </marker>
</defs>
<line id="request" x1="80" y1="120" x2="360" y2="120"
      stroke="#3575A6" stroke-width="3" marker-end="url(#arrow-blue)"/>
```

defs 必须位于根层，内含上述 marker；polygon 只是 SVG 的复用端点定义，不导出为单独 PPT 形状。marker 填充必须为显式六位颜色且与线色相同。结束端支持 orient=auto 或 auto-start-reverse；起始端必须 auto-start-reverse，避免箭头方向被无意反转。名字可自定；同色可复用同一 marker。只接受本地 `url(#id)`。

双向箭头：在同一线对象上同时设置 marker-start 与 marker-end。反向箭头：交换起终点坐标，仍用 marker-end。折线和曲线：

```xml
<polyline id="config" points="80,250 200,250 200,330 360,330" fill="none"
          stroke="#3575A6" stroke-width="3" stroke-dasharray="8 5"
          marker-end="url(#arrow-blue)"/>
<path id="feedback" d="M 360 420 C 360 520 80 520 80 420" fill="none"
      stroke="#3575A6" stroke-width="3" marker-end="url(#arrow-blue)"/>
```

path 必须开放、fill=none、正线宽且可见，起终段不能退化为零长度/零切向。闭合路径箭头、marker-mid、自定义图像 marker、不同大小/不同填充色的箭头暂不支持，明确报错。若用户要求其他箭头外观，需扩展并验证后端，不能拿独立三角形冒充一个原生箭头。

直线使用 `p:cxnSp`；折线/曲线使用一个带 `a:custGeom` 的 `p:sp`。端点写到同一对象的 `a:ln/a:headEnd`（起点）与 `a:tailEnd`（终点），type=triangle、w/len=med。这保证对象结构完整，不表示已绑定其他模块或已在 Office UI 验证。

## 字体和画布

text 使用实际字符串；字体支持 normal/bold、数值字重以及 normal/italic，锚点 start/middle/end。多行独立 text。PPT 不嵌入字体，中文通常选目标 Windows 已有的 Microsoft YaHei；`--font-file` 用于测量，不会把字体打包。服务端字形回退与 Office 需分别查看。

画布按内容组织。概念图无需论文尺寸阈值。PPT 默认 14 in 编辑宽度可由 --slide-width-in 改动；过大/过小会受 PowerPoint 格式范围限制，而非学术规范。

实现依据：[Microsoft DrawingML HeadEnd](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.drawing.headend)、[TailEnd](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.drawing.tailend)、[CustomDash](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.drawing.customdash)。SVG marker 与 PPT 原生端点的具体尺寸轮廓仍有渲染差别，最终以目标应用预览为准。
