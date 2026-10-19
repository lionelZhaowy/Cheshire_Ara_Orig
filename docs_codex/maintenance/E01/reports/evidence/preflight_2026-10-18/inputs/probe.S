// SPDX-License-Identifier: Apache-2.0
// E01 standalone toolchain probe; not Cheshire startup or a runtime acceptance test.
.section .text._start,"ax",@progbits
.globl _start
_start:
    .option push
    .option norelax
    la gp, __global_pointer$
    .option pop
    la sp, __stack_top
    li t0, 0x2000
#ifdef __riscv_vector
    ori t0, t0, 0x200
#endif
    csrs mstatus, t0
    csrw fcsr, zero
#ifdef __riscv_vector
    csrw vstart, zero
#endif
    call scalar_isa_probe
#ifdef __riscv_vector
    call vector_isa_probe
#endif
    call probe_main
    la t0, probe_status
    sw a0, 0(t0)
1:  wfi
    j 1b

.section .text,"ax",@progbits
.globl scalar_isa_probe
scalar_isa_probe:
    csrr t0, misa
    fence.i
    la t0, atomic_word
    li t1, 3
    amoadd.d.aqrl t2, t1, (t0)
    amoswap.w.aqrl t2, t1, (t0)
    lr.d.aq t2, (t0)
    sc.d.rl t3, t1, (t0)
    fcvt.d.l ft0, t1
    fadd.d ft1, ft0, ft0
    fcvt.s.w ft2, t1
    fadd.s ft3, ft2, ft2
    ret

#ifdef __riscv_vector
.globl vector_isa_probe
vector_isa_probe:
    li a0, 4
    vsetvli t0, a0, e32, m1, ta, ma
    la a1, vector_int_input
    la a2, vector_int_output
    vle32.v v1, (a1)
    vadd.vv v2, v1, v1
    vse32.v v2, (a2)
    vsetivli t0, 4, e32, m1, tu, mu
    vsetvli t0, a0, e64, m1, ta, ma
    la a1, vector_fp_input
    la a2, vector_fp_output
    vle64.v v8, (a1)
    vle64.v v10, (a1)
    vfmacc.vv v8, v10, v10
    vse64.v v8, (a2)
    ret
#endif

.section .data,"aw",@progbits
.balign 16
atomic_word: .dword 7
#ifdef __riscv_vector
vector_int_input: .word 1, 2, 3, 4
vector_int_output: .word 0, 0, 0, 0
.balign 16
vector_fp_input: .double 1.0, 2.0, 3.0, 4.0
vector_fp_output: .double 0.0, 0.0, 0.0, 0.0
#endif
.section .note.GNU-stack,"",@progbits
