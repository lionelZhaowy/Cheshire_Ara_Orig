/* SPDX-License-Identifier: Apache-2.0 */
/* Standalone compiler probe only. The actual Cheshire link scripts stay unchanged. */
OUTPUT_ARCH(riscv)
ENTRY(_start)
PHDRS { text PT_LOAD FLAGS(5); data PT_LOAD FLAGS(6); }
SECTIONS {
  . = PROBE_BASE;
  .text : { *(.text._start) *(.text .text.*) } :text
  .rodata : ALIGN(16) { *(.rodata .rodata.* .srodata .srodata.*) } :text
  . = ALIGN(0x1000);
  .data : { *(.data .data.* .sdata .sdata.*) } :data
  __global_pointer$ = ADDR(.data) + 0x800;
  .bss (NOLOAD) : ALIGN(16) { *(.bss .bss.* .sbss .sbss.* COMMON) } :data
  __image_end = .;
  __stack_top = PROBE_BASE + 0x10000;
  ASSERT(__image_end < __stack_top - 0x1000, "probe exceeds reserved memory")
  .riscv.attributes 0 : { *(.riscv.attributes) }
  /DISCARD/ : { *(.comment) *(.note.GNU-stack) }
}
