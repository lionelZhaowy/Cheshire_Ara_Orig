// SPDX-License-Identifier: Apache-2.0
// Compile-only check of official config API and preserved MMIO widths.
#include "dif/dma.h"
uint64_t check_submit(uint64_t d, uint64_t s) {
    return sys_dma_2d_memcpy(d, s, 256, 256, 256, 32, DMA_CONF_DECOUPLE_AW);
}
uint64_t check_done(void) { return *sys_dma_done_ptr(); }
void check_all_signatures(uint64_t d, uint64_t s, uint64_t conf) {
    (void)sys_dma_memcpy(d, s, 8, conf);
    sys_dma_blk_memcpy(d, s, 8, conf);
    sys_dma_2d_blk_memcpy(d, s, 8, 8, 8, 2, conf);
}
