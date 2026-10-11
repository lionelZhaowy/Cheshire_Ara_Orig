# M01 / Mixed AXI ports and technology comparison

> 记录日期：2026-10-09。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。
Date: 2026-10-09. Analysis only, HEAD 278434024. No RTL, Word, shared-state or build changes.
User prefers existing vendor mixed-width capability. Keep CPU exposed port64 and NPU port256; vendor internal adaptation preferred, subject to generated configuration confirmation. Details stay in Windows controlled DDR guide section19.8.
CPU64 at533.25MHz gives4.266GB/s per direction only if whole source path runs at that rate. Current CPU/crossbar/LLC share clk_i. Equal clock numbers alone do not prove synchronous timing.
Cheshire original Neo is TSMC65nm:200MHz implementation target, up to325MHz silicon report. GF22FDX Ariane is a different result:902MHz signoff and up to1.7GHz silicon. No validated conversion factor to SMIC55LL; inverse-node arithmetic is not an Fmax prediction. DDR rates do not scale with CPU process dimensions.
Read official papers https://arxiv.org/pdf/2305.04760 and https://arxiv.org/pdf/1904.05442; local SoC clock connections and VCU118 existing XCI. No compilation/simulation/STA/board test. Existing untracked files preserved. Not committed.
Next: obtain vendor parameter manifest, then evaluate CPU/uncore and DDR/NPU domains with actual55LL cells/macros and timing constraints. C00 need not merge a frozen frequency decision: none made.
