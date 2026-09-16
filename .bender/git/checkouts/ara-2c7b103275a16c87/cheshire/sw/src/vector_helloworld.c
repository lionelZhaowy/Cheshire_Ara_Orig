// Copyright 2024 ETH Zurich and University of Bologna.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0
//
// Matteo Perotti <mperotti@ethz.ch>
//
// Simple vector memcpy for Hello World!

#include "regs/cheshire.h"
#include "dif/clint.h"
#include "dif/uart.h"
#include "params.h"
#include "util.h"

#include "cheshire_util.h"
#include "vector_util.h"

unsigned char buf[64];

#pragma GCC push_options
#pragma GCC optimize ("O0")

int main(void) {
    cheshire_start();
    enable_rvv();
    // __asm__ volatile("csrs mstatus, %0" :: "r"(0x600));

    const unsigned char str[] = "Hello Vector World!\r\n";
    vuint8m1_t str_v;

    // Copy the hello world string to buf
    str_v = __riscv_vle8_v_u8m1(str, sizeof(str));
    // __riscv_vse8_v_u8m1(buf, str_v, sizeof(str));
    // 提取向量长度
    size_t vl = sizeof(str);
    
    // 使用内联汇编手动执行 vsetvli 和 vse8.v 指令
    __asm__ volatile (
        "vsetvli zero, %2, e8, m1, ta, ma \n\t"
        "vse8.v %1, (%0)"
        : 
        : "r" (buf), "vr" (str_v), "r" (vl)
        : "memory"
    );

    // Print buf
    printf("%s", str_v);

    cheshire_end();

    return 0;
}
