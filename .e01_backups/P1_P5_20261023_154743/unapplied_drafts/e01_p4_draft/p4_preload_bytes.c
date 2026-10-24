// Copyright 2023 ETH Zurich and University of Bologna.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0
// E01 P4 local draft. HelloWorld UART initialization reused; NOT built or run.
// The payload is emitted as PROGBITS by assembler; main only reads it.
#include <stdint.h>
#include "regs/cheshire.h"
#include "dif/clint.h"
#include "dif/uart.h"
#include "params.h"
#include "util.h"

#ifndef P4_CASE
#define P4_CASE 1
#endif
#if P4_CASE == 1
#define P4_A_ADDR 0x10000000
#define P4_A_LEN 1024
#elif P4_CASE == 2
#define P4_A_ADDR 0x10000000
#define P4_A_LEN 2048
#elif P4_CASE == 3
#define P4_A_ADDR 0x10000000
#define P4_A_LEN 1031
#elif P4_CASE == 4
#define P4_A_ADDR 0x10000001
#define P4_A_LEN 1024
#elif P4_CASE == 5
#define P4_A_ADDR 0x10000ff8
#define P4_A_LEN 16
#elif P4_CASE == 6
#define P4_A_ADDR 0x10002000
#define P4_A_LEN 13
#define P4_B_ADDR 0x1000200d
#define P4_B_LEN 9
#else
#error P4_CASE must be 1 through 6
#endif

#define STR_(x) #x
#define STR(x) STR_(x)

// Expose absolute addresses/lengths to the linker, so the case is selected once.
// Every payload byte is nonzero and position-dependent: 1+((37*i+seed)%251).
// These assembly directives create the actual loadable file bytes, not a runtime
// fill or a DPI substitute. KEEP in the local linker preserves their sections.
__asm__(
  ".global __p4_a_addr,__p4_a_len\n"
  ".set __p4_a_addr," STR(P4_A_ADDR) "\n"
  ".set __p4_a_len," STR(P4_A_LEN) "\n"
  ".section .p4_a,\"a\",@progbits\n"
  ".balign 1\n"
  ".global p4_a,p4_a_end\n"
  "p4_a:\n"
  ".set .Lp4_i,0\n"
  ".rept " STR(P4_A_LEN) "\n"
  ".byte 1+((37*.Lp4_i+17)%251)\n"
  ".set .Lp4_i,.Lp4_i+1\n"
  ".endr\n"
  "p4_a_end:\n"
  ".previous\n"
);
extern const uint8_t p4_a[],p4_a_end[];
#if P4_CASE == 6
__asm__(
  ".global __p4_b_addr,__p4_b_len\n"
  ".set __p4_b_addr," STR(P4_B_ADDR) "\n"
  ".set __p4_b_len," STR(P4_B_LEN) "\n"
  ".section .p4_b,\"a\",@progbits\n"
  ".balign 1\n"
  ".global p4_b,p4_b_end\n"
  "p4_b:\n"
  ".set .Lp4_j,0\n"
  ".rept " STR(P4_B_LEN) "\n"
  ".byte 1+((37*.Lp4_j+101)%251)\n"
  ".set .Lp4_j,.Lp4_j+1\n"
  ".endr\n"
  "p4_b_end:\n"
  ".previous\n"
);
extern const uint8_t p4_b[],p4_b_end[];
#endif

static unsigned checks,failures;
static unsigned first_group,first_offset,first_got,first_want;
static void check(unsigned group,unsigned offset,unsigned got,unsigned want) {
  ++checks;
  if(got!=want) {
    if(failures==0) {
      first_group=group; first_offset=offset; first_got=got; first_want=want;
    }
    ++failures;
  }
}

static void check_payload(unsigned group,uintptr_t addr,unsigned len,unsigned seed) {
  // Current SPM cached-address -> uncached-address alias; no DRAM aliasing.
  volatile const uint8_t *p=(volatile const uint8_t *)(addr+0x04000000UL);
  for(unsigned i=0;i<len;++i)check(group,i,p[i],1+(37*i+seed)%251);
}

static void check_final_padding(uintptr_t end) {
  // Only the final segment's explicit whole-beat zero padding is checked.
  // Padding after A in case 6 is part of B and is checked as B's real bytes.
  uintptr_t beat_end=(end+7)&~(uintptr_t)7;
  for(uintptr_t a=end;a<beat_end;++a) {
    volatile const uint8_t *p=(volatile const uint8_t *)(a+0x04000000UL);
    check(3,(unsigned)(a-end),*p,0);
  }
}

int main(void) {
  uint32_t rtc_freq=*reg32(&__base_regs,CHESHIRE_RTC_FREQ_REG_OFFSET);
  uint64_t reset_freq=clint_get_core_freq(rtc_freq,2500);
  uart_init(&__base_uart,reset_freq,__BOOT_BAUDRATE);
  uintptr_t sp;
  asm volatile("mv %0,sp\n fence":"=r"(sp)::"memory");
  check(0,0,(unsigned)(uintptr_t)p4_a,P4_A_ADDR);
  check(0,1,(unsigned)((uintptr_t)p4_a_end-(uintptr_t)p4_a),P4_A_LEN);
  // Current Boot ROM inherits a stack near the 128 KiB SPM top. The linker
  // reserves everything from 0x1000c000 upward; do not change stack setup here.
  check(0,2,sp>=0x1000c000UL && sp<0x10020000UL,1);
#if P4_CASE == 6
  check(0,3,(unsigned)(uintptr_t)p4_b,P4_B_ADDR);
  check(0,4,(unsigned)((uintptr_t)p4_b_end-(uintptr_t)p4_b),P4_B_LEN);
#endif
  if(failures)goto done;
  check_payload(1,P4_A_ADDR,P4_A_LEN,17);
#if P4_CASE == 6
  check_payload(2,P4_B_ADDR,P4_B_LEN,101);
  check_final_padding((uintptr_t)P4_B_ADDR+P4_B_LEN);
#else
  check_final_padding((uintptr_t)P4_A_ADDR+P4_A_LEN);
#endif
done:
  if(failures)
    printf("P4_FAIL g=%u i=%u v=%x e=%x\r\n",
           first_group,first_offset,first_got,first_want);
  printf("P4_DONE case=%u c=%u e=%u\r\n",(unsigned)P4_CASE,checks,failures);
  uart_write_flush(&__base_uart);
  return failures?44:0;
}
