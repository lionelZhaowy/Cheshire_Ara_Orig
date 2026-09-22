# L01 交接：配置参数参考手册

## 基本信息

- 日期：2026-09-20；任务 ID：L01 / 配置学习文档。
- 用户授权范围：阅读协作/状态文档，详细整理 CVA6、Cheshire、Ara 与其他模块配置参数和常用配置 Markdown 文档。
- 状态：文档完成；硬件功能验证未执行。
- 输入 HEAD：`379ae4544bc62e05a2736b11b33a3244181bba38`。
- 开始时已有变更：`docs_codex/00_README.md`、`01_Cheshire_Ara_Quick_Start.md` 已修改；根 AGENTS、02、共享状态/任务/模板、handoffs 等已存在但未跟踪。保留原内容；未覆盖或清理。
- 负责路径：新建 `docs_codex/configuration/*.md` 和本记录；串行给 PROJECT_STATE、AGENT_TASKS、handoffs/README 增加文档导航与状态。无 RTL/软件/构建脚本修改，无自动子 Agent。

## 本轮结果

新增六篇中文文档：

| 文件 | 内容 |
| --- | --- |
| [README](../configuration/README.md) | 分层概念、阅读导航、向量取值快照 |
| [CVA6](../configuration/CVA6.md) | 全部 88 个 cva6_user_cfg_t 字段、profile 原值/SoC 覆盖关系、派生值 |
| [CHESHIRE](../configuration/CHESHIRE.md) | 全部 113 个 cheshire_cfg_t 字段、原始默认值、消费者、地址图、容量/ID 公式 |
| [ARA](../configuration/ARA.md) | 顶层参数、实例固定设置、包常量、lane/VLEN 示例、软件关系 |
| [PERIPHERALS](../configuration/PERIPHERALS.md) | DMA、LLC/SPM、外设/中断/RT、DDR wrapper、时钟和 VIP |
| [RECIPES](../configuration/RECIPES.md) | 配置矩阵、常用修改示例、仿真入口、最小验证矩阵与配置记录模板 |

证据等级：本地源码确认与静态计算；容量变化、裁切与扩展为明确标注的实施建议。不是最新上游通用手册，不穷举第三方 IP 所有内部实现参数。

新增/澄清的源码事实：

1. CVA6 user VLEN=64 是虚拟地址容器；Ara VLEN=2048 是向量寄存器容量。
2. SoC 默认把向量 profile 的 PMP 项数 8 覆盖为 0；CLIC 和总线字段也受覆盖。
3. `SlinkMaxClkDiv` 配置字段为 10 位，原始默认赋值 1024 截为 0；SoC/VIP 实际使用包级常量 1024，单改 Cfg 字段不生效。
4. `gen_cva6_cfg()` 的 SPM 可执行长度为 `2*SizeSpm`，实际高地址非缓存别名却相隔 0x04000000；默认执行规则没有覆盖该别名。未动态验证或修复。
5. `cheshire_idma_wrap.sv` 1D 分支 `.busy_i(idma_busy)` 与实际声明 `busy` 不一致；软件驱动又固定使用 2D 布局。1D 切换不可列为已验收组合。
6. DMA 驱动 decouple 两个表达式均移到 AW 位号，当前宏值为 0；VGA 错误单元容量用 CoreMaxTxns=8，而 VGA 读上限=24。这些为待核查消费者关系，未断言已有故障。
7. 内部中断 packed struct 为 58 位（6 个 bus-error、32 GPIO、20 个其他标量位），PLIC 58 个源已满；默认 NumExtPlicIntrs/NumExtClicIntrs 为 0。新增外部 PLIC 中断需同步生成包。
8. 当前 AXI RT 生成包为 6 managers / 2 regions；Ara TB 发起者数为 7，组合启用需要联动核对。

以上定义/消费者都在章节内链接到源码。既有仿真标量 profile+decoder stub/真实实现并存的问题再次通过当前脚本确认，未修复。

## 改动与接口

- 没有改变硬件配置/profile/宏/地址/中断/位宽，没有迁移或裁切。
- 无构建产物、无依赖下载、无 Git 提交。
- 文档采用仓库相对链接；连同当前源码快照一起搬迁可查阅。只复制文档不包含被链接的依赖源码。
- E01/V01/S01/M01 可把文档作为输入，但具体配置以其实际提取与测试为准。

## 验证证据

工作目录为仓库根。执行了 `git status --short`、`git rev-parse HEAD`，定向用 `rg`、`sed`、`cat` 阅读配置定义、profile、实例、生成包和软件入口；有少数预估路径不存在，随后用 rg 定位到实际源码路径，不影响最终引用。

参数表生成过程在 `/tmp` 用 Python 辅助抽取字段和原始默认表达式，中文释义由对照消费者编写。该临时生成器不是项目构建入口，也不作为后续唯一维护源；最终文档包含人工复核修订。字段覆盖、链接、代码块和 diff 空白检查以最终文档为准。

可在仓库根复现以下只读检查（Python 3）：

```sh
python - <<'PY'
from pathlib import Path
import re
base = Path('docs_codex/configuration')
for p in base.glob('*.md'):
    s = p.read_text()
    assert sum(line.startswith('```') for line in s.splitlines()) % 2 == 0, p
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', s):
        if '://' not in target and not target.startswith('#'):
            assert (p.parent / target.split('#')[0]).exists(), (p, target)
c = Path('hw/cheshire_pkg.sv').read_text()
c = c.split('// Externally controllable parameters')[1].split('} cheshire_cfg_t;')[0]
v = Path('.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/include/config_pkg.sv').read_text()
v = v.split('typedef struct packed {', 1)[1].split('} cva6_user_cfg_t;')[0]
for source, name, count in [(c, 'CHESHIRE.md', 113), (v, 'CVA6.md', 88)]:
    fields = re.findall(r'\b(\w+)\s*;', re.sub(r'//[^\n]*', '', source))
    rows = re.findall(r'^\| `(\w+)` \|', (base / name).read_text(), re.M)
    assert len(fields) == len(rows) == count and set(fields) == set(rows), name
print('PASS: six chapter links/fences; Cheshire 113/113; CVA6 88/88')
PY

git diff --check
```

最终检查结果：上述字段覆盖/本地链接/代码块检查与 `git diff --check` 均通过，退出码 0；新增文档另检查行尾空白通过。链接检查只确认相对路径存在，未使用 Markdown 渲染器验证页面内锚点。首次链接检查在交接文件尚未创建时提示缺失，创建后最终复查通过。

**未编译/未仿真/未综合/未板测。** 用户本轮要求文档，不执行大型构建；文档内示例函数与 Tcl 片段均未执行，不能作为功能通过证据。

## 决策与下一步

- 保留 02 文档的 1 核、2 lanes、VLEN 2048 提取建议；未冻结最终产品外设/性能/工艺配置。
- 下一位最小步骤：先从配置 README/RECIPES 选定工作入口；E01 固定源码/参数并修正独立清单；V01 按修改项执行对应最小回归。
- 若修改 Serial Link 分频、非缓存 SPM 取指、DMA 1D、VGA 错误追踪或增加中断，先复核本记录对应消费者关系，再按授权实施与验证。
- 已同步共享状态和任务导航；E01 等实施任务状态保持原样。
