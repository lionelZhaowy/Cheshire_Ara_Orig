# M01 / DDR interface feasibility (static review)

- Date: 2026-09-22. Scope: user requested comparison with the two available vendor documents; no full DDR IP received.
- Input: mp/ara-pulp-v2, ae2b69fe0640e57c89dfc6bcc9404bfd5008e1a5; clean worktree before review.
- Status: feasibility review completed; implementation and compatibility validation pending.

## Findings and evidence

- Correct integration boundary is cheshire_soc axi_llc_mst_req_o / axi_llc_mst_rsp_i, after atomic adaptation and LLC (hw/cheshire_soc.sv:446-546).
- Current DefaultCfg: AXI data64 / addr48 / user2. LLC output ID derives from master ID plus source bits plus LLC bit; Default and Ara profiles yield6, FPGA with both Ara and USB disabled yields5 (hw/cheshire_pkg.sv:311-324,538-610; hw/include/cheshire/typedef.svh:19-40).
- Existing target/xilinx/src/dram_wrapper_xilinx.sv is MIG-specific: width/ID conversion, CDC and low-address slicing are not a ready vendor wrapper.
- Default external window is [0x80000000,0x100000000). Actual installed capacity and vendor base-address semantics must drive mapping. Full-width range validation must precede narrowing; do not silently alias invalid addresses.
- Atomic adapter consumes AMO and LRSC before LLC. Downstream ATOP/LOCK are cleared by dependency modules. New downstream DMA/NPU/ISP bypass traffic needs separate cache and reservation ownership rules.
- LLC whole-line transfers are INCR,8 beats with current NumBlocks8 (axi_llc src/eviction_refill/axi_llc_ax_master.sv:135-137). This does not bound every possible pass-through transaction.
- Reg/APB control, independent reset sequencing and interrupt hookup still needed. Existing reg_to_apb expects PSLVERR and drives PSTRB; endpoint semantics must be confirmed.
- Boot ROM establishes LLC SPM after LLC BIST (hw/bootrom/cheshire_bootrom.S:59-78), giving a basis for pre-DDR initialization. DDR Controller core reset must not be confused with CPU reset. LLC SRAM BIST is not external SDRAM BIST.

## Changes and validation

- Only this independent handoff added in WSL; no RTL, configuration, scripts, shared state or task-table edits. Not committed.
- Detailed Chinese analysis updated in the controlled Windows workspace DDR_PHY/DDR3控制器IP接口梳理与CVA6集成指南.md section19.5; companion HTML updated. Vendor originals remain in that directory and were not copied here.
- Read-only inspection used git status --short, git rev-parse HEAD, git branch --show-current, sed/nl/grep on the paths above and Bender.local. Successful source reads and source-derived arithmetic; one compound grep command exited1 for no match, followed by direct source-location checks.
- No compile, simulation, CDC/STA run, hardware test, or DDR initialization executed.

## Next steps / coordinator input

1. Obtain final AXI4 parameter manifest, top-level ports, matched Controller/PHY revisions and register/init/training/BIST manuals.
2. Freeze the ASIC memory map and wrapper contract; review all burst, ID, attribute, error and clock-domain cases before implementation.
3. Validate wrapper and startup with model-based AXI tests before hardware bring-up.
- C00 may record M01 static feasibility review complete, implementation pending. This is not authorization to implement the proposed topology.
