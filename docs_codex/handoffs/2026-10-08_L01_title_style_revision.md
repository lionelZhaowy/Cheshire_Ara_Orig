# L01 / 全站标题规范修正

## 基本信息

- 日期：2026-10-08；用户在系统教材实施收尾追加标题修正授权，主管继续协调三个子Agent。
- 目标：恢复2026-09-23既定标题规范；只改正式标题、副标题及必要引用，不改技术正文与课程结构。
- 状态：标题实施、全量审阅及文档发布检查完成。
- 输入：mp/ara-pulp-v2，459f9d6f5748e39063f7bb67e959c2f27859915d；当前已有未提交教材、图稿和证据保留。
- 所有权：子Agent仅各自content标题；主管持有pages、首页、引用、生成、维护、共享状态与最终验收。

## 本轮结果

- 完整审阅664个标题/副标题/正式入口源字段；修改319处，其余345项保留；变化按源字段计，不重复算生成传播。
- 全量对照见../L01_Title_Style_Revision_2026-10-08.md，完整清单见../reviews/L01_title_style_20261008/inventory.json。
- 九篇42章、文件名/slug/ID/篇章顺序/迁移映射不变。51页非标题内容在显式引用归一化后字节一致，自测/代码/技术表格/图保持。
- 新结论等级为文档检查；没有重新审计技术实现或产生目标运行证据。

## 改动与接口

- content/*.html正式标题、pages.json标题/副标题、首页导航与一处UART小节引用，生成learning/*.html。
- README重申正式标题规范；build_registers仅修一处标题输出，check_structure保留原索引数据哈希检查，仅归一化批准标题。
- 独立证据learning/evidence/title-style-20261008/与reviews/L01_title_style_20261008/；历史系统实施证据不覆盖。
- 配置、地址、IRQ、位宽、工程接口变化：无。未Git提交/推送。

## 验证证据

- 仓库根；Python3.13.5，Chrome151.0.7922.108；版本如上。
- check_titles.py退出0：664项、319变化，51页非标题保护；3080输入文件中2971不变，109项授权变化；ID/href/src及页面结构不变。
- 生成、全站链接、临时生成一致性、桌面/手机浏览器实际结果均通过，命令与具体日志见下方。
- 未目标编译、未仿真、未综合、未板测；未Office实测/真人试读。标题检查不能关闭S01-B01、iDMA或Ara缺口。

## 决策与下一步

- 已确认：正式标题陈述技术主题，递进讲解由正文承担，自测允许提问。
- 后续扩写先按当前README检查全量正式标题，再按语义决定是否修改；不依据关键词机械替换。
- 最少输入：当前README、pages.json、本记录与对照表；技术任务另读对应实现交接。
- 工程任务仍依赖其原输入和授权，不因标题修正启动。

## 实际发布命令与结果

~~~sh
python3 docs_codex/learning/scripts/build_registers.py
python3 docs_codex/learning/scripts/build_site.py
python3 docs_codex/learning/scripts/check_site.py
python3 docs_codex/learning/scripts/check_structure.py --check-generated --out-dir docs_codex/learning/evidence/title-style-20261008/release-generated
python3 docs_codex/learning/scripts/preview_structure_site.py --out-dir docs_codex/learning/evidence/title-style-20261008/release-browser
python3 docs_codex/reviews/L01_title_style_20261008/check_titles.py --out-dir docs_codex/reviews/L01_title_style_20261008/final-protection
git diff --check
~~~

以上退出码均为0。证据目录若已存在，不可覆写，重验时为--out-dir选择新路径。浏览器及WaveDrom临时生成使用经允许的主机离线Chrome；无生产目标运行。

结果：71 HTML/5068本地链接、143重生成产物一致、37结构母版及manifest不变、373迁移；51页桌面1440×1100/手机390×844、12无脚本页、199跨页书签通过。429寄存器项及代码/图/自测保持。71个被测HTML哈希和既有证据在浏览器检查期间不变。主管查看异常、PAD、SRAM、测量四张新截图，标题和目录无可见遮挡。

日志：[生成](../learning/evidence/title-style-20261008/release-generated/checks.txt)、[浏览器](../learning/evidence/title-style-20261008/release-browser/browser.txt)、[保护](../reviews/L01_title_style_20261008/final-protection/check-result.json)。没有将网页检查扩大为工程技术验证。
