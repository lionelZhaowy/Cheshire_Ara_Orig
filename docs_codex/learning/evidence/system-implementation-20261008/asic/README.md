# L01-ASIC / P01 文档实施证据

2026-10-08，输入 HEAD `459f9d6f5748e39063f7bb67e959c2f27859915d`。

- `input.json`：开始时分支/HEAD/git状态，4个负责正文和21个定向生产/依赖来源SHA-256。
- `clocks-before.html`、`reset-before.html`、`power-before.html`、`future-before.html`：本子任务修改前正文；不覆盖历史证据。
- `page-manifest.json`：十个负责页及全部ID；用于主管导航集成和旧链接保护。
- `checks.txt`：第一轮定向检查，检查正文链接、旧ID保护、源码哈希、VRF尺寸复算及差异空白；不是目标验证。
- `final-checks.txt`：P01手册/报告完成后的检查结果。
- `additional-sources.json`：P01扩展定向读取的来源哈希与版本边界，不冒充开始前保护快照。

在线官方资料及用途记于 `docs_codex/L01_ASIC_Implementation_2026-10-08.md` 第3节；不抓取完整受版权资料到仓库。生成页面和浏览器检查由主管串行执行、写入本轮其他新目录。本子任务没有运行目标构建、仿真、综合、板测、CDC/RDC/STA/DFT或首硅测试。
