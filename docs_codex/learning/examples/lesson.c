// SPDX-License-Identifier: Apache-2.0
// L01 teaching example. Only this directory is written by its build script.
#include <stdint.h>
#include "util.h"
#include "dif/uart.h"
#include "dif/clint.h"
#include "regs/clint.h"
#include "printf.h"
#if LESSON_STAGE == 4
#include "dif/dma.h"
#endif
#ifndef LESSON_STAGE
#define LESSON_STAGE 1
#endif
#ifndef INJECT_ERROR
#define INJECT_ERROR 0
#endif
#define N 137u

// Explicitly inspect these in the ELF: seed in .misc, result in .bss.
volatile uint32_t seed = 1;
volatile uint32_t result[N];

#if LESSON_STAGE == 3
// Robust split 64-bit counter read. Original driver has no rollover retry.
static uint64_t ticks(void) {
    uint32_t hi, lo, again;
    do {
        hi = *reg32(&__base_clint, CLINT_MTIME_HIGH_REG_OFFSET);
        lo = *reg32(&__base_clint, CLINT_MTIME_LOW_REG_OFFSET);
        again = *reg32(&__base_clint, CLINT_MTIME_HIGH_REG_OFFSET);
    } while (hi != again);
    return ((uint64_t)hi << 32) | lo;
}

#endif

#if LESSON_STAGE == 5
extern void learn_vadd(const uint32_t *, const uint32_t *, uint32_t *, unsigned long);
#endif

int main(void) {
    uint32_t rtc = *reg32(&__base_regs, CHESHIRE_RTC_FREQ_REG_OFFSET);
    if (rtc < 2500) return 10;
    uint64_t hz = clint_get_core_freq(rtc, 2500);
    uart_init(&__base_uart, hz, __BOOT_BAUDRATE);
    printf("LEARN stage=%u Hello Cheshire!\r\n", (unsigned)LESSON_STAGE);
    unsigned errors = 0;
    uint32_t sum = 0;
#if LESSON_STAGE >= 1
    for (unsigned i = 0; i < N; ++i) result[i] = 3 * i + seed;
    if (INJECT_ERROR) result[5] ^= 1u;
    for (unsigned i = 0; i < N; ++i) {
        errors += result[i] != 3 * i + 1u;
        sum += result[i];
    }
#endif
#if LESSON_STAGE == 2
    // scratch0..5 belong to boot/exit protocols. Single-owner scratch6 exercise.
    volatile uint32_t *s = reg32(&__base_regs, CHESHIRE_SCRATCH_6_REG_OFFSET);
    uint32_t saved = *s;
    *s = 0x12345678;
    fence();
    errors += *s != 0x12345678;
    *s = saved;
    fence();
#endif
#if LESSON_STAGE == 3
    uint64_t start = ticks(), cycles = get_mcycle();
    while (ticks() - start < 8) {
        if (get_mcycle() - cycles > 10000000UL) return 11;
    }
    printf("timer ticks>=8\r\n");
#endif
#if LESSON_STAGE >= 4
    // Single hart; Boot ROM has configured all 128 KiB as SPM.
    // Reserve physical SPM [0x10010000,0x10011000) exclusively for this lab.
    // Access ONLY its uncached alias, never the cached address.
    // Application fits in low 64 KiB; inherited stack must stay above 0x10011000.
    if (*reg32(&__base_regs, CHESHIRE_LLC_SIZE_REG_OFFSET) != 131072) return 12;
    volatile uint32_t *a = (volatile uint32_t *)0x14010000UL;
    volatile uint32_t *b = (volatile uint32_t *)0x14010400UL;
    volatile uint32_t *c = (volatile uint32_t *)0x14010800UL;
    for (unsigned i = 0; i < N; ++i) { a[i] = i; b[i] = 2*i+1; c[i] = 0xdeadbeef; }
    fence();
#if LESSON_STAGE == 4
    if (!chs_hw_feature_present(CHESHIRE_HW_FEATURES_DMA_BIT)) return 13;
    uint64_t id = sys_dma_memcpy((uintptr_t)c, (uintptr_t)a, N * sizeof(*a));
    uint64_t begin = get_mcycle();
    while (*sys_dma_done_ptr() != id) {
        if (get_mcycle() - begin > 10000000UL) return 14;
    }
    fence();
    for (unsigned i = 0; i < N; ++i) errors += c[i] != i;
    printf("DMA copied=%u\r\n", N * (unsigned)sizeof(*a));
#else
    // All C and CRT objects use scalar ISA. The only vector code is rvv_add.S.
    asm volatile("csrs mstatus, %0" :: "r"(3UL << 9) : "memory");
    learn_vadd((const uint32_t *)a, (const uint32_t *)b, (uint32_t *)c, N);
    fence();
    for (unsigned i = 0; i < N; ++i) errors += c[i] != 3*i+1;
    printf("RVV checked=%u\r\n", N);
#endif
#endif
    printf("LEARN sum=%u errors=%u\r\n", sum, errors);
    uart_write_flush(&__base_uart);
    return errors ? 1 : 0;
}
