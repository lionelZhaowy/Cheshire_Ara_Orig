# 2026-10-08 L01证据目录

本目录始于外设任务，包含随后用户增加的Ara/RVV优化及全书审查。输入HEAD为459f9d6f5748e39063f7bb67e959c2f27859915d。全部为本轮新文件，历史证据不回写。

- input.json：开始时工作区与哈希；用户已有diagrams.pptx修改在其中。
- before-content/：34份修改前正文快照，仅供本轮审查定位，不作为新网站入口。
- before-checks.txt / before-browser.txt：修改前结构/浏览器结果。
- sources.json：58个定向来源路径的当前哈希；记录来源，不代表58文件逐行全审计。
- protection-and-task-checks.txt：资产、旧锚点及手算任务核对。
- generated-check/：沙箱内临时生成失败，原因是Chrome无法提供DevToolsActivePort；保留失败日志。
- generated-final/、browser/、browser-final/：修订中间检查，保留当时被测输入哈希。
- **release-generated/**：最终正文生成一致性及结构/链接检查。
- **release-browser/**：最终桌面/手机浏览器、导航/迁移/交互及被测HTML哈希。
- release-protection.txt：收尾保护与数值推导核对。
- documentation-final.txt：交接/索引收尾后的Markdown链接及diff检查。

浏览器结果只证明本地页面可读、图文/导航可用；不证明目标程序执行。实际人工查看了I2C桌面、SPI手机、Ara内部图、RVV手机、诊断入口等截图；脚本自动遍历36主页面两种尺寸，并检查7个无脚本页、199条跨页旧书签。

本轮未构建软件、未运行生产RTL仿真/综合/板测、未测性能或ASIC签核。未进行真人试读。已知Platform ROM、iDMA和Ara验证缺口继续开放。完整命令与退出码见docs_codex/handoffs/2026-10-08_L01_teaching_review_peripherals_ara.md。
