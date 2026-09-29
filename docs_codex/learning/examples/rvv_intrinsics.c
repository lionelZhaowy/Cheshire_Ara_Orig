// SPDX-License-Identifier: Apache-2.0
// Names checked against the actual GCC 15.2 toolchain; compile evidence is not execution.
#include <stdint.h>
#include <stddef.h>
#include <riscv_vector.h>
void learn_vadd(const uint32_t *a, const uint32_t *b, uint32_t *c, unsigned long n) {
    while (n) {
        size_t vl = __riscv_vsetvl_e32m1(n);
        vuint32m1_t va = __riscv_vle32_v_u32m1(a, vl);
        vuint32m1_t vb = __riscv_vle32_v_u32m1(b, vl);
        __riscv_vse32_v_u32m1(c, __riscv_vadd_vv_u32m1(va, vb, vl), vl);
        a += vl; b += vl; c += vl; n -= vl;
    }
}
uint32_t learn_sum(const uint32_t *a, unsigned long n) {
    uint32_t sum = 0;
    while (n) {
        size_t vl = __riscv_vsetvl_e32m1(n);
        vuint32m1_t v = __riscv_vle32_v_u32m1(a, vl);
        vuint32m1_t zero = __riscv_vmv_v_x_u32m1(0, 1);
        vuint32m1_t partial = __riscv_vredsum_vs_u32m1_u32m1(v, zero, vl);
        sum += __riscv_vmv_x_s_u32m1_u32(partial);
        a += vl; n -= vl;
    }
    return sum;
}
