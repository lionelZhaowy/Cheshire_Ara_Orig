# M01 / DDR2133 and SoC bandwidth compatibility review

Date: 2026-10-09. Status: analysis complete; implementation and timing unverified.
User requested renewed compatibility analysis of higher DDR speed versus AXI width/clock. Input HEAD 278434024. Existing untracked documents preserved. No RTL, shared state, build or Word changes.

## Results

- Current Cheshire bus and LLC external port use Cfg.AxiDataWidth=64; bus/LLC use clk_i. gen_cva6_cfg forwards this width to CVA6. RV64 ISA alone does not require a 64-bit external bus.
- A terminal width converter or faster receiving clock cannot raise sustained throughput beyond the unchanged upstream path. At 333.3 MHz, 64-bit carries at most 2.6664 GB/s per direction before overhead.
- get_llc_size multiplies width. Keeping 8 ways, 256 lines, 8 blocks while changing 64 to 256 gives 512 KiB instead of 128 KiB and 256-byte instead of 64-byte lines. Review macro/SPM/software consequences before widening.
- AraDataWideWidth=32*NrLanes; Ara is converted to Cfg.AxiDataWidth. DDR-only widening does not remove this bottleneck.
- Proposed performance topology preserves CPU/Ara/LLC64 and gives NPU an independent wide DMA/memory path. Higher memory clocks do not force CPU clocks when crossings are supported and verified. High-frequency single-port versus lower-frequency multiport remains a proposal, not a frozen decision.
- Vendor-specific source analysis and exact candidate parameters remain in the controlled Windows DDR_PHY guide section19.7; no vendor source copied here. Both existing Word requirements versions remain unchanged.

## Evidence and checks

Read hw/cheshire_pkg.sv (get_llc_size, gen_cva6_cfg, defaults), hw/include/cheshire/typedef.svh, hw/cheshire_soc.sv (LLC, AraDataWideWidth, converter), target/xilinx/src/dram_wrapper_xilinx.sv (width conversion and CDC). Official PULP AXI module roles checked at https://github.com/pulp-platform/axi; local dependencies not upgraded.
Commands: git rev-parse --short HEAD; git status --short; targeted sed/grep reads. WSL rg unavailable, used grep. Analysis and arithmetic only; no compilation, simulation, STA, CDC/RDC or board test.

## Next steps

1. Obtain paired vendor clock/width/physical implementation commitments and constraints.
2. Estimate NPU model traffic and select native DMA/SRAM bandwidth and clock domains; retain ownership/cache/atomic rules for bypass.
3. Validate end-to-end traffic, QoS and timing before freezing interfaces. No C00 shared-state change required until a configuration is selected.
