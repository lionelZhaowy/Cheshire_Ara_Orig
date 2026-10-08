# L01 标题审阅与保护检查

完整报告：[标题规范修正](../../L01_Title_Style_Revision_2026-10-08.md)。664项全量源字段含504个H2/H3、49入口标签及111篇/页面标题副标题。最终319变化及45个引用同步以inventory.json/check-result.json为准。

software/os-vector/asic.json是三个子Agent的标题清单，root.json及root-references.json记录主管修改；coordinator-retained.json保留主管撤回不必要改名的决定。初次检查后新增安全输出参数，final-protection再次验证通过；原记录未覆盖。历史技术检查及标题前正文未修改。

可重复命令（输出目录必须不存在）：

~~~sh
python3 docs_codex/reviews/L01_title_style_20261008/check_titles.py --out-dir /tmp/l01-title-recheck-new
~~~

命令从固定快照检查标题范围、其余字节、ID/链接/结构/历史文件保护；人工语义审读见总报告，关键词只有辅助定位作用。
