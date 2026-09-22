	.file	"dma_access_audit.c"
	.option nopic
	.attribute arch, "rv64i2p1_m2p0_a2p1_f2p2_d2p2_c2p0_zicsr2p0_zifencei2p0_zmmul1p0_zaamo1p0_zalrsc1p0_zca1p0_zcd1p0"
	.attribute unaligned_access, 0
	.attribute stack_align, 16
	.text
	.align	1
	.globl	sys_dma_src_ptr
	.type	sys_dma_src_ptr, @function
sys_dma_src_ptr:
	lla	a0,__base_dma+216
	ret
	.size	sys_dma_src_ptr, .-sys_dma_src_ptr
	.align	1
	.globl	sys_dma_dst_ptr
	.type	sys_dma_dst_ptr, @function
sys_dma_dst_ptr:
	lla	a0,__base_dma+208
	ret
	.size	sys_dma_dst_ptr, .-sys_dma_dst_ptr
	.align	1
	.globl	sys_dma_num_bytes_ptr
	.type	sys_dma_num_bytes_ptr, @function
sys_dma_num_bytes_ptr:
	lla	a0,__base_dma+224
	ret
	.size	sys_dma_num_bytes_ptr, .-sys_dma_num_bytes_ptr
	.align	1
	.globl	sys_dma_conf_ptr
	.type	sys_dma_conf_ptr, @function
sys_dma_conf_ptr:
	lla	a0,__base_dma
	ret
	.size	sys_dma_conf_ptr, .-sys_dma_conf_ptr
	.align	1
	.globl	sys_dma_status_ptr
	.type	sys_dma_status_ptr, @function
sys_dma_status_ptr:
	lla	a0,__base_dma+4
	ret
	.size	sys_dma_status_ptr, .-sys_dma_status_ptr
	.align	1
	.globl	sys_dma_nextid_ptr
	.type	sys_dma_nextid_ptr, @function
sys_dma_nextid_ptr:
	lla	a0,__base_dma+68
	ret
	.size	sys_dma_nextid_ptr, .-sys_dma_nextid_ptr
	.align	1
	.globl	sys_dma_done_ptr
	.type	sys_dma_done_ptr, @function
sys_dma_done_ptr:
	lla	a0,__base_dma+132
	ret
	.size	sys_dma_done_ptr, .-sys_dma_done_ptr
	.align	1
	.globl	sys_dma_src_stride_ptr
	.type	sys_dma_src_stride_ptr, @function
sys_dma_src_stride_ptr:
	lla	a0,__base_dma+240
	ret
	.size	sys_dma_src_stride_ptr, .-sys_dma_src_stride_ptr
	.align	1
	.globl	sys_dma_dst_stride_ptr
	.type	sys_dma_dst_stride_ptr, @function
sys_dma_dst_stride_ptr:
	lla	a0,__base_dma+232
	ret
	.size	sys_dma_dst_stride_ptr, .-sys_dma_dst_stride_ptr
	.align	1
	.globl	sys_dma_num_reps_ptr
	.type	sys_dma_num_reps_ptr, @function
sys_dma_num_reps_ptr:
	lla	a0,__base_dma+248
	ret
	.size	sys_dma_num_reps_ptr, .-sys_dma_num_reps_ptr
	.align	1
	.globl	sys_dma_memcpy
	.type	sys_dma_memcpy, @function
sys_dma_memcpy:
	sd	a1,__base_dma+216,a5
	sd	a0,__base_dma+208,a5
	sd	a2,__base_dma+224,a5
	lla	a5,__base_dma
	sd	zero,248(a5)
	sd	zero,0(a5)
	lw	a4,68(a5)
	lw	a0,72(a5)
	slli	a4,a4,32
	srli	a4,a4,32
	slli	a0,a0,32
	or	a0,a0,a4
	ret
	.size	sys_dma_memcpy, .-sys_dma_memcpy
	.align	1
	.globl	sys_dma_blk_memcpy
	.type	sys_dma_blk_memcpy, @function
sys_dma_blk_memcpy:
	addi	sp,sp,-16
	sd	a1,__base_dma+216,a5
	sd	a0,__base_dma+208,a5
	sd	a2,__base_dma+224,a5
	sd	zero,__base_dma+248,a5
	sd	zero,__base_dma,a5
	lwu	a4,__base_dma+68
	lwu	a5,__base_dma+72
	slli	a5,a5,32
	or	a5,a5,a4
	sd	a5,8(sp)
	j	.L18
.L19:
 #APP
# 125 "/home/zhaowenyao/RISC_CVA6_prj/cheshire_ara/sw/include/dif/dma.h" 1
	nop
# 0 "" 2
 #NO_APP
.L18:
	lwu	a3,__base_dma+132
	lwu	a5,__base_dma+136
	ld	a4,8(sp)
	slli	a5,a5,32
	or	a5,a5,a3
	bne	a5,a4,.L19
	addi	sp,sp,16
	jr	ra
	.size	sys_dma_blk_memcpy, .-sys_dma_blk_memcpy
	.align	1
	.globl	sys_dma_2d_memcpy
	.type	sys_dma_2d_memcpy, @function
sys_dma_2d_memcpy:
	sd	a1,__base_dma+216,a6
	sd	a0,__base_dma+208,a1
	sd	a2,__base_dma+224,a1
	li	a1,1024
	lla	a2,__base_dma
	sd	a1,0(a2)
	sd	a4,240(a2)
	sd	a3,232(a2)
	sd	a5,248(a2)
	lw	a5,68(a2)
	lw	a0,72(a2)
	slli	a5,a5,32
	srli	a5,a5,32
	slli	a0,a0,32
	or	a0,a0,a5
	ret
	.size	sys_dma_2d_memcpy, .-sys_dma_2d_memcpy
	.align	1
	.globl	sys_dma_2d_blk_memcpy
	.type	sys_dma_2d_blk_memcpy, @function
sys_dma_2d_blk_memcpy:
	addi	sp,sp,-16
	sd	a1,__base_dma+216,a6
	sd	a0,__base_dma+208,a1
	sd	a2,__base_dma+224,a1
	li	a2,1024
	sd	a2,__base_dma,a1
	sd	a4,__base_dma+240,a2
	sd	a3,__base_dma+232,a4
	sd	a5,__base_dma+248,a4
	lwu	a4,__base_dma+68
	lwu	a5,__base_dma+72
	slli	a5,a5,32
	or	a5,a5,a4
	sd	a5,8(sp)
	j	.L26
.L27:
 #APP
# 125 "/home/zhaowenyao/RISC_CVA6_prj/cheshire_ara/sw/include/dif/dma.h" 1
	nop
# 0 "" 2
 #NO_APP
.L26:
	lwu	a3,__base_dma+132
	lwu	a5,__base_dma+136
	ld	a4,8(sp)
	slli	a5,a5,32
	or	a5,a5,a3
	bne	a5,a4,.L27
	addi	sp,sp,16
	jr	ra
	.size	sys_dma_2d_blk_memcpy, .-sys_dma_2d_blk_memcpy
	.align	1
	.globl	legacy_next
	.type	legacy_next, @function
legacy_next:
	lwu	a0,__base_dma+68
	lwu	a5,__base_dma+72
	slli	a5,a5,32
	or	a0,a5,a0
	ret
	.size	legacy_next, .-legacy_next
	.align	1
	.globl	single_next
	.type	single_next, @function
single_next:
	lw	a0,__base_dma+68
	ret
	.size	single_next, .-single_next
	.ident	"GCC: (g5115c7e44) 15.2.0"
	.section	.note.GNU-stack,"",@progbits
