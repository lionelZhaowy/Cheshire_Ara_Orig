# L01 / 现用教材插图重绘、旧图归档与可编辑 PPTX

## 基本信息

- 日期：2026-10-07；L01 教材修改者。独立评审由用户另开的对话负责，本记录不宣布独立评审通过。
- 用户授权：以详细 AXI Crossbar 参考图为标准，参考科研 SVG / 可编辑 PPTX skill，重绘教材所有图像并归档替换旧图。
- 输入 HEAD：`f01487c2f3c3e990b515bff813227b97049976a3`，分支 `mp/ara-pulp-v2`。开始时已有20个已修改文档/脚本，以及未跟踪的 R1/R2 修正、独立评审和证据；均保留。完整输入见 [input.json](../learning/evidence/figures-20261007/input.json)。
- 范围：当前七篇/30章正文实际引用的43张 SVG（含6张教学时序），25个正文页引用；图集、维护脚本、证据与必要索引。不重写未被当前正文引用的历史资产，不改生产实现。
- 使用 `svg-pptx-diagrams` skill；未启动子 Agent、未提交或推送 Git。
- 状态：43张重绘及替换完成，SVG/网页与PPTX结构检查通过；Office实际渲染未完成，待独立评审。

## 本轮结果

- [新版插图目录](../learning/assets/figures-20261007/)包含43张结构化SVG母版和清单；[新旧图对照](../learning/figures/20261007/index.html)逐图关联教材章节；[PPTX](../learning/figures/20261007/editable/diagrams.pptx)每图一页，共43页、3090个原生对象、1293个文本对象。
- [归档目录](../learning/figure_archive/20261007/)保存43张旧图、4个旧生成器和6个原始波形JSON。旧 `assets/*.svg` 也原样保留，使既有引用与875项历史保护检查仍有效；不是将历史记录回填成新检查。
- Crossbar 重绘为逐输入 DEMUX / 全连接矩阵 / 逐目标 MUX，保留 M1 下游 Reg 二级译码、M2 LLC/SPM 与外存分支，以及 W 和 ID 归属说明。图上明确 `DefaultCfg + Ara=1`、单核、无外部扩展；端口数7×5、来源前缀3位、目标侧ID共5位均按这一条件静态推导。Ara关闭的AXI RT案例仍使用原6来源/DMA=2，不受图中编号替代。
- 系统图分职责层次与三个具体请求；Ara图展开控制协议、lane分布和地址/数据平面；存储图区分地址窗口、物理ways、缓存副本及所有权；时钟、电源图区分实际域与未来域；DDR图区分AXI、调度、PHY、器件及读返回。
- 软件图解释产物和内存段，启动图保留主机/目标两条时间线及首次栈访问前提。新首页路线图改为由当前 `pages.json` 读取七篇/30章编号，消除旧图沿用16章的过期标签。
- 6张时序图直接消费未改动的原 `assets/waves/*.json`；重新绘制独立波形段、总线块、时间栅格、背压底色及VALID/READY同高区间标记。仍为教学示意，不是实测波形。
- 统一1800×1125画布，文本保留SVG `text`，线、箭头、曲线与形状独立；没有整图栅格化、文字转轮廓、外部CDN或新网站框架。

## 源码与内容边界

- Crossbar依据：`hw/cheshire_pkg.sv::gen_axi_in/gen_axi_out/gen_reg_out/DefaultCfg`，`hw/cheshire_soc.sv::AxiSlvIdWidth/i_axi_xbar/gen_llc`，本地 `axi/doc/axi_xbar.md` 官方设计说明。确认连接矩阵为全连接、编号按配置生成、同一M2目标具有多个地址规则。
- 其他图沿现有正文及旧图的源码依据重排，定向来源哈希见 [sources.json](../learning/evidence/figures-20261007/sources.json)。图内标注源码、教学/未来属性；未用在线新版本替换本地依赖事实。
- 未修改硬件配置、profile、地址图、中断、位宽、RTL、原sw、filelist、依赖或旧FPGA工程。`.bender/` 未清理或重拉。
- S01-B01、iDMA控制位宽/HAL、Ara B错误处理、Router测试入口等未关闭；未冻结PLL、DDR、NPU或电源域方案。
- R1/R2原修正保留。多数正文变化只是图片路径；首页图注与证据页/维护页按新产物更新。

## 改动与维护接口

- `scripts/build_research_figures.py` 为43张图的布局母版，`figure_primitives.py` 为显式SVG原语；`assets/figures-20261007/manifest.json` 记录每张图的哈希、来源、状态与旧/新路径。
- `scripts/preview_research_figures.py` 使用本地Chrome实际渲染，检查画布、所属框边界与文字间重叠；所有输出要求新目录。
- `scripts/build_figure_gallery.py` 生成新旧对照页。页面位于 `figures/20261007/`；与整个learning目录一起搬迁可离线查看。
- `check_site.py` 递归检查新版SVG XML；`check_structure.py --check-generated` 在临时副本另生成43张图及清单；旧生成器仍只维护旧资产。
- `preview_structure_site.py` 保留已有检查，新增43组新旧对照、86张资源加载、链接和桌面/手机布局检查；SVG边界检查指向新版图。
- [FIGURES.md](../learning/FIGURES.md)说明生成、导出与验证边界；README、证据页与共享L01索引同步。

## 验证证据

工作目录为仓库根。源目录与输出目录均不覆盖旧证据；完整证据在 [figures-20261007](../learning/evidence/figures-20261007/)。

```bash
python3 docs_codex/learning/scripts/build_research_figures.py --out-dir <新的SVG目录>
python3 docs_codex/learning/scripts/preview_research_figures.py --input-dir <SVG目录> --out-dir <新的预览目录>
python3 docs_codex/learning/scripts/build_figure_gallery.py --out-dir <新的对照页目录>
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/preview_structure_site.py --out-dir <新的网页检查目录>
python3 docs_codex/learning/scripts/check_structure.py --check-generated --out-dir <新的结构检查目录>
git diff --check
```

- [最终SVG报告](../learning/evidence/figures-20261007/svg-browser-final/report.json)：43张实际渲染；文字画布越界、所属框越界、文字间重叠均为0，检查前后母版哈希一致。
- 人工看过43张初稿的分组总览，针对连线与布局修正后，又查看最终Crossbar、未来时钟域、JTAG启动与向量load原尺寸截图。初稿存在的Crossbar说明挤压、UART标题重叠已修；别名误连、常开控制穿越域框、JTAG段装载/resume关系也经定向调整。不声称逐页在Office人工审读。
- [网页浏览器报告](../learning/evidence/figures-20261007/site-browser/browser.txt)：34主页面桌面/手机、7页无脚本、199跨页旧书签、交互检查通过；对照页43组/86张图片、链接及两种尺寸无页面溢出；当前43张SVG边界检查通过。
- [PPTX导出报告](../learning/figures/20261007/editable/export_report.json)：43页原生对象，逐项重读文本与源一致、对象数一致、无整图图片；最小文本字号约9.72 pt（少数窄时序块），一般正文约12–14 pt。字体为本地 WenQuanYi Zen Hei，未嵌入。
- 尝试Office实测：检测到PowerPoint注册；首次沙箱内调用受WSL socket限制，获准沙箱外执行同一只读验证后，被Windows的未签名脚本执行策略阻止。日志分别保存在 `powerpoint/run.txt`、`powerpoint-final/run.txt`。未修改执行策略，未打开文稿，未完成PowerPoint编辑探针或预览导出；不能声明Office显示已验证。
- 初次SVG预览在沙箱启动Chrome失败；使用获准的本地Chrome检查后成功。所有失败与草稿报告保留原身份。
- 最终 `structure-final/checks.txt` 退出0：54 HTML、2837项本地链接/资源、114 SVG XML、654项Markdown链接/锚点；七篇/30章、373项迁移、875项历史保护、728个备份通过。临时副本的43张新版图及清单、旧生成器的126个产物均与工作区一致。`git diff --check`通过。最终保护快照见 `protection-final.json`，旧源码、旧证据、旧图和独立评审原件保持保护。
- **未执行**软件构建、生产RTL编译/仿真、综合、板测、性能测试或ASIC实施。

## 决策与下一步

1. 独立评审从新旧对照页进入，优先核对Crossbar编号/方向、同一M2的多个窗口、W/ID状态，以及控制/数据/事件分离是否准确。
2. 检查当前/教学/未来状态标记、R1栈前提和6份波形序列未被视觉重绘改变；图中的7×5不能泛化成所有配置。
3. 对需要修改的图给出文件名、对象/连线及预期语义；后续只改对应母版并重新生成受影响产物，不重新实施已完成的正文评审修正。
4. 用户在目标Office环境打开PPTX后可检查字体回退与原生对象编辑；当前仅结构验证通过，Office实际显示仍待确认。

最少继续输入：本交接、FIGURES.md、新旧对照页、对应SVG母版定义及sources.json。共享状态只记录教材进展，不提高生产验证等级。
