#include "dif/dma.h"
uint64_t probe_next(void) { return *sys_dma_nextid_ptr(); }
uint64_t probe_done(void) { return *sys_dma_done_ptr(); }
