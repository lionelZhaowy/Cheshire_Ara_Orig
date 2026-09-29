// SPDX-License-Identifier: Apache-2.0
// L01: one hart, PLIC mode, exclusive peripherals and uncached SPM buffers.
// Built independently; target execution has NOT been validated.
#include <stdint.h>
#include "util.h"
#include "dif/uart.h"
#include "dif/clint.h"
#include "dif/dma.h"
#include "regs/clint.h"
#include "gpio_regs.h"
#include "rv_plic_regs.h"
#include "printf.h"
#ifndef ADV_STAGE
#define ADV_STAGE 3
#endif
#ifndef INJECT_ERROR
#define INJECT_ERROR 0
#endif
#ifndef OMIT_GPIO_TRIGGER
#define OMIT_GPIO_TRIGGER 0
#endif
#ifndef DMA_INTERFACE_VALIDATED
#define DMA_INTERFACE_VALIDATED 0
#endif
// Keep the proposed DMA path inspectable in disassembly, but block launch until
// the 64-bit Regbus / 32-bit generated-register lane issue is validated separately.
volatile uint32_t adv_allow_dma=DMA_INTERFACE_VALIDATED;
#define GPIO_SOURCE 20u // Derived from packed cheshire_int_intr_t; single default map.
#define N 137u
#define LIMIT 10000000UL
volatile uint64_t adv_timer_count, adv_gpio_count, adv_bad_irq;
volatile uint64_t adv_mcause, adv_mepc, adv_mtval;
volatile uint64_t adv_submitted_id, adv_last_done, adv_last_status;

static uint64_t ticks(void) {
    uint32_t h,l,h2;
    do {
        h=*reg32(&__base_clint, CLINT_MTIME_HIGH_REG_OFFSET);
        l=*reg32(&__base_clint, CLINT_MTIME_LOW_REG_OFFSET);
        h2=*reg32(&__base_clint, CLINT_MTIME_HIGH_REG_OFFSET);
    } while (h!=h2);
    return ((uint64_t)h<<32)|l;
}
static void compare(uint64_t v) {
    // Avoid a transient low comparison while a split 64-bit value changes.
    *reg32(&__base_clint, CLINT_MTIMECMP_LOW0_REG_OFFSET)=UINT32_MAX;
    *reg32(&__base_clint, CLINT_MTIMECMP_HIGH0_REG_OFFSET)=(uint32_t)(v>>32);
    *reg32(&__base_clint, CLINT_MTIMECMP_LOW0_REG_OFFSET)=(uint32_t)v;
    fence();
}
#if ADV_STAGE == 3
static void dma_pair(unsigned low, uint64_t v) {
    *reg32(&__base_dma,low)=(uint32_t)v;
    *reg32(&__base_dma,low+4)=(uint32_t)(v>>32);
}
static uint32_t dma_submit(uintptr_t dst, uintptr_t src, uint32_t bytes) {
    dma_pair(IDMA_REG64_2D_SRC_ADDR_LOW_REG_OFFSET,src);
    dma_pair(IDMA_REG64_2D_DST_ADDR_LOW_REG_OFFSET,dst);
    dma_pair(IDMA_REG64_2D_LENGTH_LOW_REG_OFFSET,bytes);
    dma_pair(IDMA_REG64_2D_REPS_2_LOW_REG_OFFSET,0);
    *reg32(&__base_dma,IDMA_REG64_2D_CONF_REG_OFFSET)=0;
    fence();
    // Exactly one 32-bit read with a side effect, after all parameters are stable.
    return *reg32(&__base_dma,IDMA_REG64_2D_NEXT_ID_0_REG_OFFSET);
}
#endif
void trap_vector(void) {
    // Ordinary C function: original crt0 wrapper saves integer callers and mret's.
    // Do not add floating point, vector code, printf or nesting here.
    uint64_t cause,epc,tval;
    asm volatile("csrr %0, mcause":"=r"(cause));
    asm volatile("csrr %0, mepc":"=r"(epc));
    asm volatile("csrr %0, mtval":"=r"(tval));
    adv_mcause=cause; adv_mepc=epc; adv_mtval=tval;
    if (cause==((1UL<<63)|7)) {
        ++adv_timer_count;
        compare(ticks()+8); // Event count, not a precise fixed-rate scheduler.
    } else if (cause==((1UL<<63)|11)) {
        uint32_t id=*reg32(&__base_plic, RV_PLIC_CC0_REG_OFFSET);
        if (id==GPIO_SOURCE) {
            *reg32(&__base_gpio, GPIO_INTR_STATE_REG_OFFSET)=1; // W1C, clear device first.
            fence();
            ++adv_gpio_count;
        } else if (id) {
            ++adv_bad_irq;
            asm volatile("csrc mie, %0"::"r"(1UL<<11):"memory");
        }
        if (id) *reg32(&__base_plic, RV_PLIC_CC0_REG_OFFSET)=id;
        fence();
    } else {
        // Publish a failing completion for the VIP and stop; don't re-execute a bad instruction.
        ++adv_bad_irq;
        asm volatile("csrw mie, zero");
        *reg32(&__base_regs, CHESHIRE_SCRATCH_2_REG_OFFSET)=(31u<<1)|1u;
        fence();
        for (;;) asm volatile("wfi");
    }
}
static void stop_irqs(void) {
    asm volatile("csrci mstatus, 8":::"memory");
    asm volatile("csrw mie, zero":::"memory");
    *reg32(&__base_gpio, GPIO_INTR_ENABLE_REG_OFFSET)=0;
    *reg32(&__base_plic, RV_PLIC_IE0_0_REG_OFFSET)=0;
    compare(UINT64_MAX);
}
int main(void) {
    // This is an application owning the test system, not an OS-compatible driver.
    asm volatile("csrci mstatus, 8":::"memory");
    asm volatile("csrw mie, zero":::"memory");
    if (*reg32(&__base_regs, CHESHIRE_NUM_INT_HARTS_REG_OFFSET)!=1 ||
        !chs_hw_feature_present(CHESHIRE_HW_FEATURES_UART_BIT) ||
        !chs_hw_feature_present(CHESHIRE_HW_FEATURES_GPIO_BIT) ||
        chs_hw_feature_present(CHESHIRE_HW_FEATURES_CLIC_BIT) ||
        chs_hw_feature_present(CHESHIRE_HW_FEATURES_IRQ_ROUTER_BIT)) return 10;
    uint32_t rtc=*reg32(&__base_regs, CHESHIRE_RTC_FREQ_REG_OFFSET);
    if (rtc<2500) return 11;
    uart_init(&__base_uart, clint_get_core_freq(rtc,2500), __BOOT_BAUDRATE);
    printf("ADV stage=%u begin\r\n", (unsigned)ADV_STAGE);
    stop_irqs();
    *reg32(&__base_gpio, GPIO_INTR_STATE_REG_OFFSET)=UINT32_MAX;
    *reg32(&__base_gpio, GPIO_INTR_ENABLE_REG_OFFSET)=1;
    *reg32(&__base_plic, GPIO_SOURCE*4)=1; // Source priority 1.
    *reg32(&__base_plic, RV_PLIC_THRESHOLD0_REG_OFFSET)=0;
    *reg32(&__base_plic, RV_PLIC_IE0_0_REG_OFFSET)=1u<<GPIO_SOURCE;
    *reg32(&__base_plic, RV_PLIC_IE0_1_REG_OFFSET)=0;
    compare(ticks()+8);
    uint64_t enables=(1UL<<11) | (ADV_STAGE>=2 ? 1UL<<7 : 0);
    fence();
    asm volatile("csrw mie, %0"::"r"(enables):"memory");
    asm volatile("csrsi mstatus, 8":::"memory");
    if (!OMIT_GPIO_TRIGGER) *reg32(&__base_gpio, GPIO_INTR_TEST_REG_OFFSET)=1;
    unsigned errors=0;
    int done=1;
#if ADV_STAGE == 3
    if (!adv_allow_dma) {
        stop_irqs();
        printf("ADV BLOCKED DMA register lane mapping requires separate validation; rc=16\r\n");
        uart_write_flush(&__base_uart);
        return 16;
    }
    if (!chs_hw_feature_present(CHESHIRE_HW_FEATURES_DMA_BIT) ||
        *reg32(&__base_regs, CHESHIRE_LLC_SIZE_REG_OFFSET)!=131072) {
        stop_irqs(); return 12;
    }
    // Physical SPM [0x10010000,0x10011000) must be exclusive, never cached.
    volatile uint32_t *src=(volatile uint32_t *)0x14010000UL;
    volatile uint32_t *dst=(volatile uint32_t *)0x14010800UL;
    for (unsigned i=0;i<N;++i) { src[i]=3*i+1; dst[i]=0xdeadbeef; }
    src[N]=0x1234abcd; dst[N]=0xabcd1234;
    fence();
    adv_submitted_id=dma_submit((uintptr_t)dst,(uintptr_t)src,N*4);
    if (!adv_submitted_id) {
        stop_irqs();
        printf("ADV FAIL zero DMA ID QUARANTINED\r\n");
        uart_write_flush(&__base_uart);
        return 13;
    }
    done=0;
#endif
    uint64_t start=get_mcycle();
    while (!done || !adv_gpio_count || (ADV_STAGE>=2 && adv_timer_count<2)) {
#if ADV_STAGE == 3
        adv_last_done=*reg32(&__base_dma,IDMA_REG64_2D_DONE_ID_0_REG_OFFSET);
        done=adv_last_done==adv_submitted_id;
#endif
        if (adv_bad_irq || get_mcycle()-start>LIMIT) {
#if ADV_STAGE == 3
            adv_last_status=*reg32(&__base_dma,IDMA_REG64_2D_STATUS_0_REG_OFFSET);
#endif
            stop_irqs();
            printf("ADV FAIL timeout/badirq id=%lu done=%lu status=%lu gpio=%lu timer=%lu QUARANTINED\r\n",
                   adv_submitted_id,adv_last_done,adv_last_status,adv_gpio_count,adv_timer_count);
            uart_write_flush(&__base_uart);
            // No abort register: buffer is deliberately NOT reused until test-system reset.
            return 14;
        }
    }
    stop_irqs();
    fence();
    errors+=adv_bad_irq!=0;
#if ADV_STAGE == 3
    if (INJECT_ERROR) dst[5]^=1;
    for (unsigned i=0;i<N;++i) errors+=dst[i]!=3*i+1;
    errors+=src[N]!=0x1234abcd || dst[N]!=0xabcd1234;
#endif
    printf("ADV stage=%u gpio=%lu timer=%lu errors=%u\r\n", (unsigned)ADV_STAGE,
           adv_gpio_count,adv_timer_count,errors);
    uart_write_flush(&__base_uart);
    return errors ? 1 : 0;
}
