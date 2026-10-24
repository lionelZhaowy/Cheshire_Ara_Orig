/* Copyright 2022 ETH Zurich and University of Bologna. */
/* Licensed under the Apache License, Version 2.0, see LICENSE for details. */
/* SPDX-License-Identifier: Apache-2.0 */
/* E01 test-only adaptation of sw/link/spm.ld. NOT linked or validated yet. */
INCLUDE common.ldh

PHDRS {
  data_a PT_LOAD FLAGS(4);
  data_b PT_LOAD FLAGS(4);
  app PT_LOAD FLAGS(7);
}

SECTIONS {
  .p4_a __p4_a_addr : { KEEP(*(.p4_a)) } > spm :data_a
  .p4_b __p4_b_addr : { KEEP(*(.p4_b)) } > spm :data_b
  ASSERT(SIZEOF(.p4_a)==__p4_a_len && SIZEOF(.p4_b)==__p4_b_len,
         "P4 multi payload length mismatch")
  ASSERT(ADDR(.p4_a)==0x10002000 && SIZEOF(.p4_a)==13 &&
         ADDR(.p4_b)==0x1000200d && SIZEOF(.p4_b)==9,
         "P4 multi requires case 6 adjacent non-overlapping sections")

  .text 0x10004000 : {
    *(.text._start)
    *(.text)
    *(.text.*)
  } > spm :app
  .misc : ALIGN(16) {
    *(.rodata) *(.rodata.*)
    *(.data) *(.data.*)
    *(.srodata) *(.srodata.*)
    *(.sdata) *(.sdata.*)
  } > spm :app
  .bss : ALIGN(16) {
    __bss_start = .;
    *(.bss) *(.bss.*) *(.sbss) *(.sbss.*)
    __bss_end = .;
  } > spm :app
  .bulk : ALIGN(16) { *(.bulk) *(.bulk.*) } > spm :app
  .p4_app_tail : {
    BYTE(0x5d)
    . = ALIGN(8);
    BYTE(0xa6)
  } > spm :app
  ASSERT(.<=0x1000c000,"P4 app encroaches reserved stack area")
  ASSERT((. & 7)==1,"P4 app length must not be an exact beat multiple")
}
