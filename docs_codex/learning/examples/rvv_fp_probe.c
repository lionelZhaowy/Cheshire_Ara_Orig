// SPDX-License-Identifier: Apache-2.0
// Compile-only support probe. No claim that this has executed on the SoC.
#include <riscv_vector.h>
#include <stddef.h>
void fp_add(const float *a, const float *b, float *c, size_t n) {
    while (n) {
        size_t vl = __riscv_vsetvl_e32m1(n);
        vfloat32m1_t va = __riscv_vle32_v_f32m1(a, vl);
        vfloat32m1_t vb = __riscv_vle32_v_f32m1(b, vl);
        __riscv_vse32_v_f32m1(c, __riscv_vfadd_vv_f32m1(va, vb, vl), vl);
        a += vl; b += vl; c += vl; n -= vl;
    }
}
