# L01 / DDR–GB 缓存一致性审查与图稿

## 修改记录

| 日期 | 角色 / 输入 | 内容 |
|---|---|---|
| 2026-10-15 | L01 文档作者；`mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8` | 按用户确认计划新增一致性条件审查、三类架构比较及三张可编辑图；只交付文档与图稿 |

## 结果与范围

- 正式技术内容：[DDR–GB 缓存一致性](../engineering/Cache_Coherence_Architecture.md)。状态：文档与图稿完成；硬件方案未选型、未实现、未验证。
- 用户选择“先比较，暂不选型”。逐行 I/O 一致性是不分配 LLC 行的长期优先评估建议；缓存直接供数、协议选型及接口改造不是用户已确认决策。
- 本轮改动：上述正式文档、`engineering/README.md` 入口、[新图稿目录](../diagrams/2026-10-15_cache_coherence/README.md)、本交接。
- 保留 `IP_DDR_Interface_Contract.md` 的用户需求及现有建议。未改 RTL、sw、地址、位宽、CSR、IRQ、启动、filelist 或依赖；未提交 Git。共享状态与任务状态没有工程进展变化，不改写。
- 输入已有 `L01_software_hardware_interfaces.md` 未提交修改与 `2026-10-14_software_stack_industrial/` 未跟踪目录，未覆盖；[input.json](../diagrams/2026-10-15_cache_coherence/evidence/input.json)保存这些文件、现行契约/共享文档及源码哈希。

## 证据与检查

工作目录为仓库根。源码检查覆盖 WT profile、写缓冲、Ara 失效/pending、LLC way 维护和原子适配前提；外部规范采用 Arm IHI 0022H D3.1/D6.7/D11。依赖上游 HEAD 仅作来源标识，实际输入由主仓库版本及文件哈希约束。

下列命令结果均为本轮实际执行；输出目录相对图稿目录：

| 命令 / 检查 | 结果 |
|---|---|
| `build_figures.py --out-dir evidence/source-01` | 退出 0，3 张 SVG、29 条连续箭头 |
| `render.py --source-dir evidence/source-01 --out-dir evidence/render-01` | 退出 1；Chrome socket 被沙箱拒绝，原始日志保留 |
| 同输入渲染到 `evidence/render-02` | 经环境审批在沙箱外运行，退出 0；首次预览通过 |
| `build_figures.py --out-dir evidence/source-02`，再渲染到 `evidence/render-03` | 各退出 0；最终三图无文字越界、框内溢出、文本重叠或连线穿字；逐张人工查看 PNG |
| 原生后端 `run.py --input system.svg read-to-gb.svg write-to-ddr.svg --out-dir export --aspect source --font 'Microsoft YaHei' --font-file /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc` | 退出 0；3 页、119 文本、29 原生箭头；保存重读检查通过 |
| `validate.py --out-file evidence/validation.json`，`git diff --check` | 结果见[验证报告](../diagrams/2026-10-15_cache_coherence/evidence/validation.json)；检查正文/图稿链接、SVG/PPTX一致性、原生对象、输入保护与空白错误 |

字体、重现命令和完整产物导航见[图稿说明](../diagrams/2026-10-15_cache_coherence/README.md)。PNG 的布局检查不是 Office 检查；Office 显示与编辑未实测。未编译、未展开、未仿真、未板测，也没有运行新硬件一致性协议。

## 未关闭项与下一步

- M01/I01 评审共享粒度、是否允许缓存直接供数、GB/搬运器实际接口、共享原子域与成本；本轮没有冻结接口编码或配置。
- 现有 L1D 外部失效不能未经并发重审直接拓展；LLC 的逐行探测、数据响应和完整确认服务仍是新增工作。
- 将正文验收场景交 V01/S01；重点验证旧回填/脏行不能覆盖新写、部分字节不丢失、完成与超时恢复可追溯。已有 Ara B 错误处理等生产缺口不因本次文档交付关闭。
- 最小下一步：用户/M01 先选需要的共享能力及是否允许缓存供数，再形成实现规格；无需为阅读本文重跑历史实验。
