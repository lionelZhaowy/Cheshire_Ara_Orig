// SPDX-License-Identifier: Apache-2.0
// L01 continuous example: scalar runtime first, optional explicit RVV later.
#include <stdint.h>
#include "util.h"
#include "dif/uart.h"
#include "dif/clint.h"
#include "printf.h"
#ifndef JOURNEY_RVV
#define JOURNEY_RVV 0
#endif
#ifndef INJECT_ERROR
#define INJECT_ERROR 0
#endif
#ifndef JOURNEY_DEPTH
#define JOURNEY_DEPTH 0
#endif
#define N 137u
volatile uint32_t seed = 1;
volatile uint32_t result[N];
const char greeting[] = "Hello Cheshire!";
__attribute__((noinline)) uint32_t make_value(unsigned i) {
    uint32_t temporary = 3u * i + seed;
    return temporary;
}
#if JOURNEY_RVV
extern void learn_vadd(const uint32_t *, const uint32_t *, uint32_t *, unsigned long);
#if JOURNEY_DEPTH
extern uint32_t learn_sum(const uint32_t *, unsigned long);
// Independent input formulas include wraparound and alternating high bits.
static uint32_t input_a(unsigned i) { return (i & 1u) ? 13u*i+1u : 0u-5u*i-7u; }
static uint32_t input_b(unsigned i) { return 31u-i; }
static unsigned depth_cases(volatile uint32_t *a, volatile uint32_t *b,
                            volatile uint32_t *c) {
    static const unsigned lengths[] = {0, 1, 63, 64, 65, 137};
    unsigned errors = 0;
    const uint32_t sentinel = 0x51a7beef;
    for (unsigned k = 0; k < sizeof(lengths)/sizeof(lengths[0]); ++k) {
        unsigned n = lengths[k]; uint32_t expected_sum = 0;
        for (unsigned i = 0; i < n; ++i) {
            a[i] = input_a(i); b[i] = input_b(i); c[i] = 0xdeadbeef;
            expected_sum += input_a(i) + input_b(i);
        }
        a[n] = b[n] = c[n] = sentinel;
        fence();
        learn_vadd((const uint32_t *)a, (const uint32_t *)b, (uint32_t *)c, n);
        fence();
        uint32_t reduced = learn_sum((const uint32_t *)c, n);
        for (unsigned i = 0; i < n; ++i) {
            errors += c[i] != input_a(i)+input_b(i);
            errors += a[i] != input_a(i) || b[i] != input_b(i);
        }
        errors += reduced != expected_sum;
        errors += a[n] != sentinel || b[n] != sentinel || c[n] != sentinel;
    }
    printf("RVV_DEPTH cases=6 errors=%u\r\n", errors);
    return errors;
}
#endif
#endif
int main(void) {
    // Inspect initialized data and BSS before overwriting either one.
    unsigned errors = seed != 1;
    for (unsigned i = 0; i < N; ++i) errors += result[i] != 0;
    uint32_t rtc = *reg32(&__base_regs, CHESHIRE_RTC_FREQ_REG_OFFSET);
    if (rtc < 2500) return 10;
    uint64_t hz = clint_get_core_freq(rtc, 2500);
    uart_init(&__base_uart, hz, __BOOT_BAUDRATE);
    printf("LEARN stage=%u %s\r\n", JOURNEY_RVV ? 5u : 1u, greeting);
    printf("INIT seed=%u zeroed=137 errors=%u\r\n", seed, errors);
#if JOURNEY_RVV
    // Exclusive buffers occupy physical [0x10010000,0x10011000).
    // Only use the uncached alias. Full-SPM boot, one hart, no concurrent DMA.
    if (*reg32(&__base_regs, CHESHIRE_LLC_SIZE_REG_OFFSET) != 131072) return 12;
    volatile uint32_t *a = (volatile uint32_t *)0x14010000UL;
    volatile uint32_t *b = (volatile uint32_t *)0x14010400UL;
    volatile uint32_t *c = (volatile uint32_t *)0x14010800UL;
    const uint32_t guard = 0x51a7beef;
    a[N] = b[N] = c[N] = guard;
    for (unsigned i = 0; i < N; ++i) {
        a[i] = i; b[i] = 2u*i + seed; c[i] = 0xdeadbeef;
    }
    fence();
    asm volatile("csrs mstatus, %0" :: "r"(3UL << 9) : "memory");
    learn_vadd((const uint32_t *)a, (const uint32_t *)b, (uint32_t *)c, N);
    fence();
    errors += a[N] != guard; errors += b[N] != guard; errors += c[N] != guard;
    for (unsigned i = 0; i < N; ++i) {
        errors += a[i] != i || b[i] != 2u*i+1;
        result[i] = c[i];
    }
    printf("RVV checked=%u\r\n", N);
#if JOURNEY_DEPTH
    uint32_t reduced = learn_sum((const uint32_t *)c, N);
    errors += reduced != 28085u;
    printf("RVV_REDUCE n=137 sum=%u\r\n", reduced);
    errors += depth_cases(a, b, c);
#endif
#else
    for (unsigned i = 0; i < N; ++i) result[i] = make_value(i);
#endif
    if (INJECT_ERROR) result[5] ^= 1u;
    uint32_t sum = 0;
    for (unsigned i = 0; i < N; ++i) {
        errors += result[i] != 3u*i+1u;
        sum += result[i];
    }
    printf("LEARN sum=%u errors=%u\r\n", sum, errors);
    uart_write_flush(&__base_uart);
    return errors ? 1 : 0;
}
