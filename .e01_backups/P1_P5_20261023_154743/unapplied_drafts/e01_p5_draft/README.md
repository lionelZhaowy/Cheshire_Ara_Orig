# P5 local review drafts

2026-10-23. Nothing here has been applied, compiled or simulated. The reviewing agent only read the server. Drafts are for the coordinating agent to review and use inside the authorized isolated candidate.

- `01_reps_rtl.patch`: only the reps hunk from iDMA #66, SHA `92799c5fabcf2cd1f224f970bbb040b290d08fd5`, adapted to the current reference template, existing independent 2D/3D derived modules, and compiled `idma_generated.sv`. No protocols, register map, generator/tool/dependency changes. Three-dimensional updates only maintain template/derived-source consistency; current SoC does not instantiate that profile.
- `02_hal_cleanup.patch`: only the 1D zero-reps write removal from Cheshire #203, SHA `bca9aadb7588de7046460daf91b39fe863a7a9d1`. Current 32-bit control pointers and per-call CONF behavior remain intact.
- `draft_hashes.json`: actual reference before-hashes and expected after-hashes of these draft hunks. Recheck candidate inputs before any application; do not assume old draft hashes remain current.
- `p5_dma_1d.spm.c`: source draft based on the public official 18-byte 1D and currently accepted small overlapping 2D example. It uses the current 8-argument 2D HAL, SPM uncached alias, guards, submitted/completed IDs, and the bounded polling convention from the existing checked DMA test.
- `missing_13_paths.txt`: exact independent files absent from the isolated candidate at the read-only check. Their compiled representations are already in the unchanged aggregate; they do not need to be added to compilation.
- `existing_idma_full.diff`: the complete current 36-file reference iDMA diff, saved only locally; unlike a hash, this preserves the local change contents. The coordinating agent should keep an equivalent record in the existing backup/provenance area if it is not already archived there.

## Suggested sequence

1. Build the default `P5_SEQUENCE=0` source once using the OLD HAL and existing candidate software recipe/flags. Keep the ELF and hash. Run old RTL, then reps-only RTL with the identical ELF, in separate outputs. Data and guards must be checked even if DONE increments: old ND-zero rejection can produce a completion without a real copy. Reuse the existing SoC completion/error classification. This draft is not itself evidence of failure or success.
2. Re-run the existing small 2D software on the reps-only RTL. Current R `sw/tests/dma_2d.spm.c` is the original `_e01/dma_vector_check/src/dma_original.c` with the necessary final `DMA_CONF_DECOUPLE_NONE` argument added. Old `_e01` originals/checkers still have seven arguments and cannot be rebuilt unchanged against today's eight-argument HAL.
3. Apply the separate HAL cleanup, rebuild with `-DP5_SEQUENCE=1`, and run the 2D -> 1D -> 2D sequence. It checks that the reps register retains 4 through the cleaned-up 1D call while data still shows exactly one 1D copy. Compare this against the step-1 result rather than attributing the RTL repair to the HAL cleanup.
4. In the existing TB observation, distinguish one accepted ND-to-backend transfer from the number of physical AXI bursts/beats. The C test can prove data/ID/guards, but cannot independently prove the internal handshake count. Do not add a new regression framework for that observation.

The 10,000-poll bound is inherited from the existing checked example; if reached, report incomplete transfer and inspect progress/exception/wait evidence rather than labeling it a deadlock. Do not vary LLC/in-flight settings or reopen the previously paused long-transfer investigation.

## Input completeness findings

At candidate HEAD `26637be97e731a98ae0fd220b61f814f6a703409`, the 23 copied files from the 36-file iDMA local diff all matched R exactly. The four P5 RTL/template files, current DMA HAL/wrapper, FS crt0 and both WT assertion files matched R. No Git index entry had mode 160000.

The external `protection_before.json` contains full `reference_diff` text, but its `components.idma` contains only HEAD and diff SHA256; it does not archive the full iDMA diff. The candidate also did not contain the historical `backport.patch`, `deployment.json` or `input_hashes.json`. Keep the complete iDMA diff plus the existing source/official-adaptation record in the already established provenance/backup area. No need to copy or compile all unused derived variants merely to preserve their patch provenance.

Software reconstruction: avoid R root Makefile (Bender inclusion) and directly invoking original `sw/sw.mk` (header generation and in-source object/archive outputs). The existing F software Makefile supplies the validated explicit 23-source GCC/ar recipe; map those sources back to the copied R inputs and retain separate new outputs. Preserve scalar library `rv64gc_zifencei`, crt0/tests `rv64gcv_zifencei`, lp64d/O2/LTO, and plugin lookup alongside `gcc -print-prog-name=lto-wrapper`. Do not reuse the old `libcheshire.a` as a substitute for rebuilding the selected inputs. The parent agent has already adapted this recipe; no additional build wrapper is proposed.
