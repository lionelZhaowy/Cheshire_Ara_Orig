// SPDX-License-Identifier: Apache-2.0
// Compile to assembly ONLY. Comparing access widths does not validate RTL lanes.
#include "util.h"
#include "dif/dma.h"
uint64_t legacy_next(void) { return *sys_dma_nextid_ptr(); }
uint32_t single_next(void) { return *reg32(&__base_dma,IDMA_REG64_2D_NEXT_ID_0_REG_OFFSET); }
