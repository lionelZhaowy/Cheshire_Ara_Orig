# L01 / LLC 多路组相联与 SPM 转换图

> 记录日期：2026-10-10。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-10；任务 L01；用户指定 svg-pptx-diagrams skill 绘制 LLC Cache/SPM 结构图。
- 输入：`mp/ara-pulp-v2`，HEAD `278434024`；原有 M01 文档修改、其他图目录与交接保留。本轮未启动子Agent。
- 状态：源码核对、图稿和原生PPTX交付完成；Office实测未完成。
- 负责：新 `docs_codex/diagrams/2026-10-10_llc_cache_spm/` 和本交接。未改RTL/sw、配置、地址图、依赖、共享状态或教材；未提交Git。

## 结果与来源

- 图稿基于当前DefaultCfg：AXI Addr48/Data64、8way、256组、每行8块，数据容量128KiB，per-way16KiB。
- 核对Tag/Valid命中、独立tag/data SRAM、固定SPM槽、用途位图、未设SPM槽的SLVERR、commit后的隔离/在途等待/刷新、全SPM的DDR旁路，以及CPU L1缓存属性边界。
- 左图全Cache、右图0x00/0x0F/0xFF用途组合、下方配置转换流程。混合位图与组42/Way6命中为例子，非产品冻结或运行事实。
- 后续动态转换必须保护代码/栈/数据，不把独立配置提交误描述为数据复制或缓存一致性保证。COMMIT在FSM接受请求时清除，不能只据其清零证明所有刷新已完成；图中使用按寄存器契约确认完成的措辞。
- 最少源码：cheshire_pkg、cheshire_soc、bootrom.S；本地 axi_llc_top/config/burst_cutter/hit_miss、tag_store、data_way。官方补充：[AXI LLC文档](https://github.com/pulp-platform/axi_llc/blob/master/doc/axi_llc.md)。

## Skill 与产物

- 主Agent完整读取本次skill文件及SVG子集说明，并读取其PowerPoint验证脚本；使用scripts/run.py，不改skill或工程依赖。
- [最终入口](../diagrams/2026-10-10_llc_cache_spm/README.md)：source_final母版、export_final可编辑SVG/PNG/PPTX/报告。中间母版及export/原样保留。
- 297个独立原生PPT对象，177个文本对象，3:2页面与母版同布局，最小文字10.2pt。无文字轮廓、无整图图片或SVG内嵌。
- 生成器refuse覆盖目标；第一次行1与选中行相邻过紧，修正row0/1间距，补全SPM时DDR旁路说明后生成新的source_final/export_final目录。

## 验证命令与结果

- `python3 <图目录>/build_figure.py --output <图目录>/source_final/llc_cache_spm.svg`：退出0。
- `python3 /home/zhaowenyao/.codex/skills/svg-pptx-diagrams/scripts/run.py --input <最终SVG> --out-dir <图目录>/export_final --font 'Microsoft YaHei' --font-file /mnt/c/Windows/Fonts/msyh.ttc`：退出0；文字/对象重新读取一致，ZIP完整无media。
- Chrome headless使用独立mktemp profile，本地file://离线渲染1680×1120 PNG；按本会话已确认的沙箱启动限制取得执行权限，初版及最终版均退出0。最终预览人工查看，无矩阵行遮挡或跨框标题。
- PowerPoint脚本尝试只读打开初版PPTX，被Windows签名策略拦截，退出1 UnauthorizedAccess；没有进入文稿读取/编辑/导出，未改执行策略。最终PPTX也未Office实测，不冒称通过。
- 独立ZIP检查输出integrity=None、media=[]，一页slide1.xml。静态算术断言验证容量及0x10008AAB→(2,42,5,3)字段，非RTL仿真。
- 最终SVG SHA-256 `ec0e60d9eb312f1119e7678bdb029c7cde040cf217d169e8df39efe364232733`。
- `git diff --stat -- hw sw target` 无输出；未重新构建软件、运行RTL或板测。

## 后续

1. 用户使用export_final SVG或原生PPTX编辑；需要Office外观验收时，在允许执行验证脚本的环境完成，只读打开本次文稿。
2. 真正实施Cache/SPM转换由S01/V01验证栈与数据迁移、刷新完成及并发/错误分支，不能把本轮图稿当动态验收。
3. 未新增实现或冻结选择，不修改共享状态/任务表；与已有LLC/BIST/启动缺口记录互相补充。
