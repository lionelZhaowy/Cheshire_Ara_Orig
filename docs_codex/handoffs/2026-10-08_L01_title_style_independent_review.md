# L01 / 标题规范修正独立复审

## 基本信息

- 日期：2026-10-08。
- 授权：审查标题修正成果并提供意见；教材和生产工程只读。
- 状态：复审完成；建议接受本轮修正，以下为非阻断润色建议。
- 输入 HEAD：`459f9d6f5748e39063f7bb67e959c2f27859915d`；工作区含系统教材、标题修订、图稿及证据等大量既有未提交修改，均保留。
- 本轮仓库内仅新增本交接；不更新并行修改中的共享状态和任务索引。

## 审查结论

依据 2026-09-23 编排约定，正式标题采用陈述性、名词性技术主题。已核对当前标题清单与元数据，定向对照异常、启动、Ara、SRAM、跨域、制造测试等正文，未发现需要阻断验收的标题问题。用户指出的三处标题已经修正。候选方案、示例、适用范围和验证缺口等限定得到保留。

正文引导语、自测问句以及“主动让出”等技术用语不属于标题违规，不建议继续机械清理。已有正式陈述句（如“约束描述外部条件和合法捕获关系”）也无须强制改为名词短语。

## 非阻断建议

1. 标题对象可以更明确：
   - `content/accelerators.html#control-registers`：“寄存器与软件”可改为“IP 控制寄存器与软件接口”。
   - `content/stream-io.html#vga-registers`：“参数和关键寄存器”可改为“VGA 参数与关键寄存器”。
   - `content/vector.html#implementation`：“状态、循环和编程入口”可改为“RVV 运行状态、分块循环与编程入口”。
   这些标题本身已符合形式规范；建议只提高目录的独立可读性，不扩写正文或增加技术结论。
2. 术语显示可统一：`content/sharing.html#cpu-ara-mechanism` 的“当前 CPU/Ara：WT、pending 与失效通知”可考虑改为“CPU/Ara 写直达、在途访存与缓存失效协作”；`content/traps.html#local-handler` 的“本地 trap handler 的适用范围”可改为“本地异常与中断处理入口的适用范围”。源码标识及准确英文术语保留在正文。
3. 中英文间距可作小范围排版收尾：`pages.json` 中“CVA6与RISC-V程序使用模型”“RTOS任务、调度与同步”“嵌入式Linux启动与用户程序”“Scan、MBIST与制造测试”等，与现有带空格的标题不一致。统一显示间距并同步首页/生成导航即可，不改 slug/ID/顺序。

以上建议均非技术错误，不应据此重写全站或强迫全部合规标题换一种措辞。

## 本轮验证

复核输入快照的 51 个 before-content 文件，其 SHA-256 与 input.json 记录一致。检查发布生成报告和浏览器报告：两者各自记录的 212 项输入及 71 个 HTML 与当前文件哈希全部一致。没有用旧截图代表发生漂移的新页面。

独立重跑以下命令，均退出 0；新输出根目录为 `/tmp/l01-title-independent-qwntdzh1`，未覆盖作者证据：

```sh
python3 docs_codex/reviews/L01_title_style_20261008/check_titles.py --out-dir /tmp/l01-title-independent-qwntdzh1/protection
python3 docs_codex/learning/scripts/check_structure.py --out-dir /tmp/l01-title-independent-qwntdzh1/structure
```

- 664 项标题/副标题/入口字段，319 处变化；51 页非标题内容在列明的引用归一化后保持一致。
- 3080 个输入文件中 2971 个未变，其余变化通过原范围保护检查；ID、href/src、slug、顺序保持。
- 九篇42章、51主页面；71 HTML、5068本地链接/资源、373迁移检查通过；本轮Markdown链接检查为933项。
- 本轮未请求 `--check-generated`，未重跑Chrome；143产物生成一致性及51页桌面/手机结果引用作者发布检查，并已核对其输入及HTML无漂移。
- 人工查看作者保存的 `preview-traps.png` 和 `preview-mobile-traps.png`，所看范围标题、目录无明显遮挡。不声称人工查看全部页面截图。
- `check_titles.py` 内执行的 `git diff --check` 返回0。

没有运行目标软件构建、RTL仿真、综合或板测；本次不重新审计教材全部技术结论。

## 下一步

可以接受本轮标题修正。若采纳上述润色，只改相关标题/元数据及可见引用，保留语义锚点，用新目录进行受影响范围检查即可。无须扩大为另一轮课程重构。
