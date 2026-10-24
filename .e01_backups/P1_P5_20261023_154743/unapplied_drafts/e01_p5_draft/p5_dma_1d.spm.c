// Copyright 2024 ETH Zurich and University of Bologna.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0
//
// Based on Cheshire #203 dma_1d.spm.c (Alessandro Ottaviano) and the
// current dma_2d.spm.c (Paul Scheffler). Local P5 verification draft.
// Execute from SPM only. Not compiled or run by the reviewing agent.

#include <stdint.h>
#include "util.h"
#include "dif/dma.h"
#include "printf.h"

#ifndef P5_SEQUENCE
#define P5_SEQUENCE 0
#endif

static int run_copy(unsigned stage, int two_d) {
    volatile char src_cached[] = "This is a DMA test";
    const char gold_1d[] = "This is a DMA test!";
    const char gold_2d[] = "This ishis is is is as is a DMA test!";
    volatile unsigned char dst_cached[96] __attribute__((aligned(64)));
    volatile char *src = (volatile char *)((uintptr_t)src_cached + 0x04000000);
    volatile unsigned char *area =
        (volatile unsigned char *)((uintptr_t)dst_cached + 0x04000000);
    volatile unsigned char *dst = area + 8;
    const char *gold = two_d ? gold_2d : gold_1d;
    unsigned gold_bytes = two_d ? sizeof(gold_2d) : sizeof(gold_1d);

    for (unsigned i = 0; i < sizeof(src_cached); ++i) src[i] = src_cached[i];
    for (unsigned i = 0; i < sizeof(dst_cached); ++i) area[i] = 0xa5;
    dst[gold_bytes - 2] = '!';
    dst[gold_bytes - 1] = '\0';
    asm volatile("fence rw,rw" ::: "memory");

    uint64_t submitted = two_d
        ? sys_dma_2d_memcpy((uintptr_t)dst, (uintptr_t)src,
                            sizeof(src_cached) - 4, 7, 1, 4,
                            DMA_CONF_DECOUPLE_NONE)
        : sys_dma_memcpy((uintptr_t)dst, (uintptr_t)src,
                         sizeof(src_cached) - 1, DMA_CONF_DECOUPLE_NONE);
    uint64_t completed = *sys_dma_done_ptr();
    unsigned polls = 0;
    while (completed != submitted && polls++ < 10000)
        completed = *sys_dma_done_ptr();
    asm volatile("fence rw,rw" ::: "memory");

    unsigned errors = 0;
    for (unsigned i = 0; i < gold_bytes; ++i)
        errors += dst[i] != (unsigned char)gold[i];
    for (unsigned i = 0; i < 8; ++i) errors += area[i] != 0xa5;
    for (unsigned i = 8 + gold_bytes; i < sizeof(dst_cached); ++i)
        errors += area[i] != 0xa5;
    printf("P5 stage=%u two_d=%u submit=%lu done=%lu data_errors=%u polls=%u\n",
           stage, (unsigned)two_d, (unsigned long)submitted,
           (unsigned long)completed, errors, polls);
    if (!submitted) return 0x40;
    if (completed != submitted) return 0x42;
    return errors ? 0x41 : 0;
}

int main(void) {
    CHECK_ASSERT(-1, chs_hw_feature_present(CHESHIRE_HW_FEATURES_DMA_BIT));
#if P5_SEQUENCE
    // Use only after the separate HAL cleanup step. The preceding 2D request
    // must leave nonzero stride/reps state which 1D mode correctly overrides.
    int rc = run_copy(0, 1);
    if (rc) return rc;
    if (*sys_dma_num_reps_ptr() != 4) return 0x60;
    rc = run_copy(1, 0);
    if (rc) return rc;
    // The cleaned-up 1D HAL must no longer overwrite the reps register.
    if (*sys_dma_num_reps_ptr() != 4) return 0x61;
    return run_copy(2, 1);
#else
    // Compile once with the OLD HAL. Run the identical ELF against old RTL
    // and then against the reps-only RTL patch, preserving both results.
    return run_copy(0, 0);
#endif
}
