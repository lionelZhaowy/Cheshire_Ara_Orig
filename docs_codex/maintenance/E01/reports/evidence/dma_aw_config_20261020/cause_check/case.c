// SPDX-License-Identifier: Apache-2.0
// Reference-only SPM layout checks; absolute buffers avoid code/stack regions.
#include <stdint.h>
#include "dif/dma.h"
#ifndef CASE
#define CASE 0
#endif
volatile uint64_t case_ids[2], case_done[2];
volatile unsigned case_polls[2], case_errors, cpu_visits;
#ifndef TEST_SRC
#define TEST_SRC 0x14008043
#endif
#ifndef TEST_DST
#define TEST_DST 0x14010045
#endif
#ifndef TEST_BYTES
#define TEST_BYTES 123
#endif
#ifndef TEST_SS
#define TEST_SS 139
#endif
#ifndef TEST_DS
#define TEST_DS 149
#endif
#ifndef TEST_ROWS
#define TEST_ROWS 16
#endif
int main(void) {
    uintptr_t sa=0x14008040, da=0x1400a040;
    unsigned rows=32, bytes=128, ss=128, ds=128;
    if (CASE==0) { uintptr_t t=sa;sa=da;da=t; } // reversed within bank 2
    if (CASE==1 || CASE==3) {sa=0x1400c040;da=0x14010040;} // banks 3 -> 4, crosses 4 KiB
    if (CASE==2) {sa=TEST_SRC;da=TEST_DST;rows=TEST_ROWS;bytes=TEST_BYTES;ss=TEST_SS;ds=TEST_DS;}
    volatile uint64_t *sr=(volatile uint64_t *)((sa & ~63UL)-64), *dr=(volatile uint64_t *)((da & ~63UL)-64);
    volatile unsigned char *s=(volatile unsigned char *)sa, *d=(volatile unsigned char *)da;
    const unsigned span=CASE==2?2560:4224; // includes guard bytes on both sides
    unsigned errors=0;
    for(unsigned job=0;job<2;job++) {
        uint64_t fill=UINT64_C(0x17395b7d9fb1d3f5) ^ (UINT64_C(0x0101010101010101)*(job+CASE));
        for(unsigned i=0;i<span/8;i++){sr[i]=fill ^ (UINT64_C(0x0101010101010101)*i);dr[i]=UINT64_C(0xa5a5a5a5a5a5a5a5);}
        // CPU traffic uses a separate region; validate each prior value before updating.
        volatile uint64_t *cpu=(volatile uint64_t *)0x14016000;
        for(unsigned i=0;i<32;i++)cpu[i]=i;
        asm volatile("fence iorw,iorw" ::: "memory");
        uint64_t id=sys_dma_2d_memcpy(da,sa,bytes,ds,ss,rows,DMA_CONF_DECOUPLE_AW);
        uint64_t done=*sys_dma_done_ptr();unsigned polls=0,visits=0;
        while(done!=id && polls<100000) {
            if(CASE==3) {for(unsigned i=0;i<32;i++){errors+=cpu[i]!=(uint64_t)(i+visits);cpu[i]=i+visits+1;}visits++;}
            polls++;done=*sys_dma_done_ptr();
        }
        case_ids[job]=id;case_done[job]=done;case_polls[job]=polls;cpu_visits+=visits;
        if(done!=id)return 90;
        errors+=id!=2+job;errors+=polls==0;
        asm volatile("fence iorw,iorw" ::: "memory");
        // Compare every destination byte, including inter-row gaps and both guards.
        unsigned off=da-(uintptr_t)dr;
        for(unsigned i=0;i<span;i++) {
            unsigned j=i>=off?i-off:~0U;
            unsigned row=j/ds, col=j%ds;
            unsigned char expected=(row<rows && col<bytes)?s[row*ss+col]:0xa5;
            errors+=((volatile unsigned char *)dr)[i]!=expected;
        }
        // DMA must not alter source, including its guards.
        for(unsigned i=0;i<span/8;i++)errors+=sr[i]!=(fill ^ (UINT64_C(0x0101010101010101)*i));
    }
    if(CASE==3)errors+=cpu_visits==0;
    case_errors=errors;return errors!=0;
}
