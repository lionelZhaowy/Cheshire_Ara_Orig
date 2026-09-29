// SPDX-License-Identifier: Apache-2.0
// Read-only experiments for the EXISTING VIP models prefilled with 0x9a.
// Not a board test: a real device may contain other data. Never programs/erases.
#include <stdint.h>
#include "util.h"
#include "dif/uart.h"
#include "dif/clint.h"
#include "printf.h"
#if ADV_STAGE == 4
#include "hal/i2c_24fc1025.h"
#else
#include "hal/spi_s25fs512s.h"
#endif
static uint8_t data[16];
int main(void) {
    uint32_t rtc=*reg32(&__base_regs, CHESHIRE_RTC_FREQ_REG_OFFSET);
    if (rtc<2500) return 10;
    uint64_t hz=clint_get_core_freq(rtc,2500);
    uart_init(&__base_uart,hz,__BOOT_BAUDRATE);
    int rc;
#if ADV_STAGE == 4
    if (!chs_hw_feature_present(CHESHIRE_HW_FEATURES_I2C_BIT)) return 11;
    dif_i2c_t dev;
    rc=i2c_24fc1025_init(&dev,hz);
    // Aligned addr=0, len=16 avoids the known short-unaligned HAL edge case.
    if (!rc) rc=i2c_24fc1025_read(&dev,data,0,sizeof(data));
#else
    if (!chs_hw_feature_present(CHESHIRE_HW_FEATURES_SPI_HOST_BIT)) return 11;
    spi_s25fs512s_t dev={.spi_freq=1000000,.csid=1}; // VIP flash is CS1.
    rc=spi_s25fs512s_init(&dev,hz);
    if (!rc) rc=spi_s25fs512s_single_read(&dev,data,0,sizeof(data));
#endif
    if (rc) { printf("STORAGE rc=%d\r\n",rc); uart_write_flush(&__base_uart); return 12; }
    unsigned errors=0;
    for (unsigned i=0;i<sizeof(data);++i) errors+=data[i]!=0x9a;
    printf("STORAGE stage=%u bytes=16 errors=%u\r\n",(unsigned)ADV_STAGE,errors);
    uart_write_flush(&__base_uart);
    return errors ? 1 : 0;
}
