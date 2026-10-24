// SPDX-License-Identifier: Apache-2.0
// Fixed-reference SPM test. Keep all buffers within the linked SPM.
#include <stdint.h>
#include "dif/dma.h"
#include "printf.h"

enum { Bytes = 8192, Words = Bytes / 8, GuardWords = 8, Jobs = 3 };
static uint64_t src_storage[Words + 2 * GuardWords] __attribute__((aligned(64)));
static uint64_t dst_storage[Words + 2 * GuardWords] __attribute__((aligned(64)));
volatile uint64_t submitted_ids[Jobs], completed_ids[Jobs];
volatile unsigned pending_polls[Jobs];

// A named symbol lets disassembly identify the single DONE_ID load.
__attribute__((noinline)) uint64_t read_done_once(void) {
    return *sys_dma_done_ptr();
}

static unsigned byte_errors(uint64_t a, uint64_t b) {
    uint64_t diff = a ^ b;
    unsigned n = 0;
    if (diff) for (unsigned k = 0; k < 8; ++k) n += ((diff >> (8 * k)) & 255) != 0;
    return n;
}

int main(void) {
    volatile uint64_t *src_all = (volatile uint64_t *)((uintptr_t)src_storage + 0x04000000);
    volatile uint64_t *dst_all = (volatile uint64_t *)((uintptr_t)dst_storage + 0x04000000);
    volatile uint64_t *src = src_all + GuardWords;
    volatile uint64_t *dst = dst_all + GuardWords;
    const uint64_t guard = UINT64_C(0xa55ac33cf00f9669);
    unsigned errors = 0;
    for (unsigned job = 0; job < Jobs; ++job) {
        for (unsigned i = 0; i < Words + 2 * GuardWords; ++i) {
            src_all[i] = guard;
            dst_all[i] = guard;
        }
        for (unsigned i = 0; i < Words; ++i) {
            src[i] = UINT64_C(0x0706050403020100) ^
                     (UINT64_C(0x0101010101010101) * (i + 17 * job));
            dst[i] = ~src[i];
        }
        asm volatile("fence iorw,iorw" ::: "memory");
        uint64_t id = sys_dma_2d_memcpy((uintptr_t)dst, (uintptr_t)src, 256, 256, 256, 32, DMA_CONF_DECOUPLE_AW);
        uint64_t done = read_done_once();
        unsigned polls = 0;
        while (done != id && polls < 100000) {
            ++polls;
            done = read_done_once();
        }
        submitted_ids[job] = id;
        completed_ids[job] = done;
        pending_polls[job] = polls;
        errors += id != 2 + job;
        errors += done != id;
        errors += polls == 0;
        if (done != id) return 90; // Avoid inspecting or reusing a live DMA buffer.
        asm volatile("fence iorw,iorw" ::: "memory");
        for (unsigned i = 0; i < Words; ++i) errors += byte_errors(dst[i], src[i]);
        for (unsigned i = 0; i < GuardWords; ++i) {
            errors += src_all[i] != guard;
            errors += dst_all[i] != guard;
            errors += src[Words + i] != guard;
            errors += dst[Words + i] != guard;
        }
        printf("DMA_LONG job=%u id=%u done=%u pending=%u errors=%u\n",
               job, (unsigned)id, (unsigned)done, polls, errors);
    }
    return errors;
}
