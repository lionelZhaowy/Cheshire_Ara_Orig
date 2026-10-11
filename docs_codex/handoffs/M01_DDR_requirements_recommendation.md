# M01 / DDR requirements recommendation

> 记录日期：2026-10-09。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

Date: 2026-10-09. Scope: user requested advice for revising vendor DDR requirements. No implementation authorized in this turn.
Input HEAD short: 278434024. Existing untracked L01 documents/diagrams were preserved. No changes to shared state, task table, RTL or build scripts. This handoff is not committed.

## New evidence and proposal

User relayed supplier confirmation: PHY and Controller width follow system requirements; a 64-bit implementation may connect eight x8 or four x16 devices. Configuration interface supports APB4. User says NPU compute/SRAM are undecided, workloads are very small LLMs and small detection/tracking/segmentation models.

Recommend evaluating one physical x64 DDR3/3L channel with independent Cheshire64 and NPU256 AXI4 ingress ports. This is a project integration proposal based on the new IP requirements, not current Cheshire functionality or a frozen procurement decision. Capacity candidate2 GiB, with support for4 GiB organization requested; actual population selected before PCB freeze from weights/KV/workspace/OS budget. Two channels are an upgrade alternative pending traffic estimates and cost/physical review.

Current hw/cheshire_pkg.sv still has AddrWidth48, AxiDataWidth64 and LLC external range [0x80000000,0x100000000). Increasing to contiguous4 GiB overlaps the default SerialLink range [0x100000000,0x200000000) if enabled. Local32-bit Controller addressing requires explicit full-width decode/base translation. Do not truncate address bits.

hw/cheshire_soc.sv still places atomic adaptation before LLC. NPU bypass follows the project requirement but needs full cache visibility/ownership and atomic restrictions. Multiple AXI ports do not create coherent memory or multiply physical DDR bandwidth. Preserve current official Platform ROM hook direction for boot configuration.

## Deliverable / evidence

Detailed proposed values, source page references, capacity/bandwidth arithmetic, interface limits and validation requirements were appended to section19.6 of the controlled Windows DDR_PHY/DDR3控制器IP接口梳理与CVA6集成指南.md. Vendor originals remain in that Windows directory; no restricted vendor source files copied here. Original DOCX unchanged.

Read-only checks: git rev-parse --short HEAD; git status --short; reads of AGENTS.md, PROJECT_STATE.md, AGENT_TASKS.md, ASIC extraction handoff and relevant package/SoC source. Successful extraction of vendor PDF feature/clock/reset pages and all original DOCX tables. Arithmetic/Markdown checks only. No compile, simulation, STA, CDC/RDC or board test.

## Next steps

1. Obtain supplier-approved final parameter manifest, paired PHY/DFI details and physical constraints.
2. Estimate representative model external traffic and resident memory before selecting capacity and channel count.
3. Coordinate final address/cache/ID/clock contract with C00/M01 before any RTL changes; validate with AXI BFMs and actual vendor models.

C00 can record the two new supplier statements as user-relayed evidence and all proposed widths/ports/capacity as pending decisions; do not mark DDR integration complete.
