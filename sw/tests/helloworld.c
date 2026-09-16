// Copyright 2023 ETH Zurich and University of Bologna.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0
//
// Nicole Narr <narrn@student.ethz.ch>
// Christopher Reinwardt <creinwar@student.ethz.ch>
// Paul Scheffler <paulsc@iis.ee.ethz.ch>

#include "regs/cheshire.h"
#include "dif/clint.h"
#include "dif/uart.h"
#include "params.h"
#include "util.h"
#include "printf.h"  // 依然需要包含头文件，以获取 printf 宏和函数声明

// int main(void) {
//     // 开启 RISC-V 向量单元 (Vector Unit)
//     // 将 mstatus 寄存器的 VS 位段 (bits [10:9]) 置为 11
//     asm volatile("csrs mstatus, %0" :: "r"(3 << 9));

//     char str[] = "Hello World!\r\n";
//     uint32_t rtc_freq = *reg32(&__base_regs, CHESHIRE_RTC_FREQ_REG_OFFSET);
//     uint64_t reset_freq = clint_get_core_freq(rtc_freq, 2500);
//     uart_init(&__base_uart, reset_freq, __BOOT_BAUDRATE);
//     uart_write_str(&__base_uart, str, sizeof(str));
//     uart_write_flush(&__base_uart);
//     return 0;
// }

int main(void) {
    // 开启 RISC-V 向量单元 (Vector Unit)
    // 将 mstatus 寄存器的 VS 位段 (bits [10:9]) 置为 11
    asm volatile("csrs mstatus, %0" :: "r"(3 << 9));
    // 获取时钟并初始化 UART
    uint32_t rtc_freq = *reg32(&__base_regs, CHESHIRE_RTC_FREQ_REG_OFFSET);
    uint64_t reset_freq = clint_get_core_freq(rtc_freq, 2500);
    uart_init(&__base_uart, reset_freq, __BOOT_BAUDRATE);

    // 直接愉快地使用 printf 打印格式化字符串
    int test_num = 1024;
    printf("Hello Cheshire SoC!\r\n");
    printf("This is a formatted string. Decimal: %d, Hex: 0x%X\r\n", test_num, test_num);
    
    // 确保数据全部发送完毕
    uart_write_flush(&__base_uart);
    return 0;
}