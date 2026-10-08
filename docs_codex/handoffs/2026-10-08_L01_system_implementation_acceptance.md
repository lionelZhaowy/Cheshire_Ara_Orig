# L01 / 系统教材实施与主管集成验收

## 基本信息

- 日期：2026-10-08；任务L01-S/OS/ASIC/O，追加M01-D/P01文档。
- 用户授权多个子Agent实施教材，由主管协调验收；生产RTL/sw/依赖/配置/地址/工程脚本只读。
- 状态：系统正文及网页检查完成；随后用户指出正式标题风格违例，按新要求继续独立标题修正。不能以本记录替代标题修正后的最终交接。
- 分支mp/ara-pulp-v2，HEAD 459f9d6f5748e39063f7bb67e959c2f27859915d；此前未提交教材、报告与用户PPTX均作输入保留。
- 分工：software负责软件7+2页，os负责OS4+1页及M01手册，asic负责旧4+新6页及P01手册，主管负责其余衔接、测量/系统诊断、目录/生成/验收/共享索引。

## 本轮结果

- 九篇42章、51主页面，新增12章与3个诊断页；软件全链、异常/上下文、RTOS/Linux、ASIC真实消费者与测量落入HTML，外设/Ara独立复审5项修正。
- M01_IP_DDR_Interface_Contract.md、P01_ASIC_Adaptation_and_Evidence.md已交付；原03平台文件和02提取规格职责保持。
- 详细覆盖与前后对照见../L01_System_Textbook_Implementation_2026-10-08.md；17页独立审读见../L01_System_Independent_Review_2026-10-08.md。
- 新结论为源码确认/文档检查/方案建议，未新增目标执行。S01-B01、iDMA、Ara运行与错误处理缺口仍开放。
- 遗漏：本轮若干标题采用口语/提问/教学指令，违反2026-09-23既定规范；用户新附件已明确要求标题专项修正，技术正文及课程顺序不得随之改写。

## 改动与接口

- content、pages、生成页面及必要维护脚本和入口；图稿、示例、历史证据不改。旧路线图生成器绑定旧目录输入以保持逐字节复现。
- 记录：learning/evidence/system-implementation-20261008/；可随docs_codex搬迁，相对路径保留。
- 配置/profile/地址/IRQ/位宽变化：无；未提交Git。
- L01正文不授权E01提取、S01修复/OS移植、M01旁路、P01宏适配或V01大型验证。

## 验证证据

仓库根目录；Python3.13.5、Chrome151.0.7922.108；代码版本如上。

~~~sh
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/check_site.py
python3 docs_codex/learning/scripts/check_structure.py --check-generated --out-dir docs_codex/learning/evidence/system-implementation-20261008/release-generated-final
python3 docs_codex/learning/scripts/preview_structure_site.py --out-dir docs_codex/learning/evidence/system-implementation-20261008/release-browser
python3 docs_codex/reviews/L01_system_acceptance_20261008/check_protection.py
git diff --check
~~~

- 成功检查退出0：71 HTML、5068本地链接、143临时生成产物、37结构SVG和manifest一致；373迁移、51页桌面/手机、12无脚本页、199跨页书签。
- 保护检查：2824输入文件中2744不变，80个授权文档变化；383旧正文ID保留，77定向源哈希不变。旧站728文件与原图/PPTX保护通过。
- Chrome沙箱无法启动的首次失败与旧路线图输入漂移的重试失败各保存在独立目录；主机离线运行及固定历史输入后通过。没有覆盖失败日志。
- 未运行软件目标构建、RTL编译/仿真、综合、板测、OS移植、性能或工艺签核；未真人试读、未Office实测。以上网页结果是标题修正前的版本快照，标题修改后须另写新证据。

## 决策与下一步

1. 按用户最新附件完成全站正式标题专项修正：技术主题优先，正文递进/自测提问各自保留。
2. 保留语义ID、slug、页面顺序和技术内容；从源更新标题/副标题及必要引用，重新生成并验收新版本。
3. 后续工程由供应商/I01/P01提供接口和工艺资料，用户/S01提供OS与工作负载，E01/V01另行建立工程证据；文档交付不关闭这些缺口。

最少阅读：本记录、主管报告、最新标题专项交接、learning/README/pages.json，以及对应作者报告。共享状态由主管串行汇总。
