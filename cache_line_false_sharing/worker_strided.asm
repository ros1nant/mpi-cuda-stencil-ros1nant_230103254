	.file	"<string>"
	.section	.ltext,"axl",@progbits
	.globl	_ZN8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy
	.p2align	4
	.type	_ZN8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy,@function
_ZN8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy:
	pushq	%rsi
	pushq	%rdi
	movq	104(%rsp), %r11
	testq	%r11, %r11
	jle	.LBB0_9
	movq	96(%rsp), %rax
	movq	72(%rsp), %rdx
	movq	112(%rsp), %r8
	orq	$1, %r8
	movabsq	$6364136223846793005, %r9
	movq	%r11, %r10
	andq	$7, %r10
	je	.LBB0_2
	xorl	%esi, %esi
	.p2align	4
.LBB0_4:
	movq	(%rdx,%rax,8), %rdi
	imulq	%r9, %rdi
	addq	%r8, %rdi
	movq	%rdi, (%rdx,%rax,8)
	incq	%rsi
	cmpq	%rsi, %r10
	jne	.LBB0_4
	movq	%r11, %r10
	subq	%rsi, %r10
	cmpq	$8, %r11
	jae	.LBB0_7
	jmp	.LBB0_9
.LBB0_2:
	movq	%r11, %r10
	cmpq	$8, %r11
	jb	.LBB0_9
.LBB0_7:
	addq	$8, %r10
	.p2align	4
.LBB0_8:
	movq	(%rdx,%rax,8), %r11
	imulq	%r9, %r11
	addq	%r8, %r11
	movq	%r11, (%rdx,%rax,8)
	movq	(%rdx,%rax,8), %r11
	imulq	%r9, %r11
	addq	%r8, %r11
	movq	%r11, (%rdx,%rax,8)
	movq	(%rdx,%rax,8), %r11
	imulq	%r9, %r11
	addq	%r8, %r11
	movq	%r11, (%rdx,%rax,8)
	movq	(%rdx,%rax,8), %r11
	imulq	%r9, %r11
	addq	%r8, %r11
	movq	%r11, (%rdx,%rax,8)
	movq	(%rdx,%rax,8), %r11
	imulq	%r9, %r11
	addq	%r8, %r11
	movq	%r11, (%rdx,%rax,8)
	movq	(%rdx,%rax,8), %r11
	imulq	%r9, %r11
	addq	%r8, %r11
	movq	%r11, (%rdx,%rax,8)
	movq	(%rdx,%rax,8), %r11
	imulq	%r9, %r11
	addq	%r8, %r11
	movq	%r11, (%rdx,%rax,8)
	movq	(%rdx,%rax,8), %r11
	imulq	%r9, %r11
	addq	%r8, %r11
	movq	%r11, (%rdx,%rax,8)
	addq	$-8, %r10
	cmpq	$8, %r10
	jg	.LBB0_8
.LBB0_9:
	movq	$0, (%rcx)
	xorl	%eax, %eax
	popq	%rdi
	popq	%rsi
	retq
.Lfunc_end0:
	.size	_ZN8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy, .Lfunc_end0-_ZN8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy

	.globl	_ZN7cpython8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy
	.p2align	4
	.type	_ZN7cpython8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy,@function
_ZN7cpython8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy:
	.cfi_startproc
	pushq	%r15
	.cfi_def_cfa_offset 16
	pushq	%r14
	.cfi_def_cfa_offset 24
	pushq	%r13
	.cfi_def_cfa_offset 32
	pushq	%r12
	.cfi_def_cfa_offset 40
	pushq	%rsi
	.cfi_def_cfa_offset 48
	pushq	%rdi
	.cfi_def_cfa_offset 56
	pushq	%rbp
	.cfi_def_cfa_offset 64
	pushq	%rbx
	.cfi_def_cfa_offset 72
	subq	$200, %rsp
	.cfi_def_cfa_offset 272
	.cfi_offset %rbx, -72
	.cfi_offset %rbp, -64
	.cfi_offset %rdi, -56
	.cfi_offset %rsi, -48
	.cfi_offset %r12, -40
	.cfi_offset %r13, -32
	.cfi_offset %r14, -24
	.cfi_offset %r15, -16
	movq	%rdx, %rcx
	leaq	104(%rsp), %rax
	movq	%rax, 56(%rsp)
	leaq	112(%rsp), %rax
	movq	%rax, 48(%rsp)
	leaq	120(%rsp), %rax
	movq	%rax, 40(%rsp)
	leaq	128(%rsp), %rax
	movq	%rax, 32(%rsp)
	movabsq	$.const.worker_strided_accumulate, %rdx
	movabsq	$PyArg_UnpackTuple, %rax
	movl	$4, %r8d
	movl	$4, %r9d
	callq	*%rax
	testl	%eax, %eax
	je	.LBB1_1
	movabsq	$_ZN08NumbaEnv8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy, %rax
	cmpq	$0, (%rax)
	je	.LBB1_4
	movq	128(%rsp), %rcx
	vxorps	%xmm0, %xmm0, %xmm0
	vmovups	%ymm0, 144(%rsp)
	vmovups	%ymm0, 168(%rsp)
	movabsq	$NRT_adapt_ndarray_from_python, %rax
	leaq	144(%rsp), %rdx
	vzeroupper
	callq	*%rax
	testl	%eax, %eax
	jne	.LBB1_8
	cmpq	$8, 168(%rsp)
	jne	.LBB1_8
	movq	144(%rsp), %r12
	movq	176(%rsp), %rdi
	movq	120(%rsp), %rcx
	movabsq	$PyNumber_Long, %r15
	callq	*%r15
	movabsq	$PyLong_AsLongLong, %rsi
	movabsq	$Py_DecRef, %r13
	testq	%rax, %rax
	movq	%rdi, 96(%rsp)
	je	.LBB1_10
	movq	%rax, %rbx
	movq	%rax, %rcx
	callq	*%rsi
	movq	%rax, %rdi
	movq	%rbx, %rcx
	callq	*%r13
	movabsq	$PyErr_Occurred, %rbp
	callq	*%rbp
	testq	%rax, %rax
	jne	.LBB1_11
.LBB1_14:
	movq	112(%rsp), %rcx
	callq	*%r15
	testq	%rax, %rax
	je	.LBB1_15
	movq	%rax, %r14
	movq	%rax, %rcx
	callq	*%rsi
	movq	%rax, %rbx
	movq	%r14, %rcx
	callq	*%r13
	callq	*%rbp
	testq	%rax, %rax
	jne	.LBB1_11
.LBB1_18:
	movq	104(%rsp), %rcx
	callq	*%r15
	testq	%rax, %rax
	je	.LBB1_19
	movq	%rax, %r15
	movabsq	$PyLong_AsUnsignedLongLong, %rax
	movq	%r15, %rcx
	callq	*%rax
	movq	%rax, %r14
	movq	%r15, %rcx
	callq	*%r13
	callq	*%rbp
	testq	%rax, %rax
	jne	.LBB1_11
.LBB1_22:
	movabsq	$PyEval_SaveThread, %rax
	callq	*%rax
	movq	%rax, %r15
	movq	%r14, 88(%rsp)
	movq	%rbx, 80(%rsp)
	movq	%rdi, 72(%rsp)
	movq	96(%rsp), %rax
	movq	%rax, 48(%rsp)
	movabsq	$_ZN8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy, %rax
	leaq	136(%rsp), %rcx
	callq	*%rax
	movabsq	$PyEval_RestoreThread, %rax
	movq	%r15, %rcx
	callq	*%rax
	movabsq	$NRT_decref, %rax
	movq	%r12, %rcx
	callq	*%rax
	movabsq	$_Py_NoneStruct, %rsi
	movabsq	$Py_IncRef, %rax
	movq	%rsi, %rcx
	callq	*%rax
.LBB1_2:
	movq	%rsi, %rax
	addq	$200, %rsp
	popq	%rbx
	popq	%rbp
	popq	%rdi
	popq	%rsi
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	retq
.LBB1_4:
	movabsq	$PyExc_RuntimeError, %rcx
	movabsq	$".const.missing Environment: _ZN08NumbaEnv8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy", %rdx
	jmp	.LBB1_5
.LBB1_8:
	movabsq	$PyExc_TypeError, %rcx
	movabsq	$".const.can't unbox array from PyObject into native value.  The object maybe of a different type", %rdx
.LBB1_5:
	movabsq	$PyErr_SetString, %rax
	callq	*%rax
	jmp	.LBB1_1
.LBB1_10:
	xorl	%edi, %edi
	movabsq	$PyErr_Occurred, %rbp
	callq	*%rbp
	testq	%rax, %rax
	je	.LBB1_14
	jmp	.LBB1_11
.LBB1_15:
	xorl	%ebx, %ebx
	callq	*%rbp
	testq	%rax, %rax
	je	.LBB1_18
	jmp	.LBB1_11
.LBB1_19:
	xorl	%r14d, %r14d
	callq	*%rbp
	testq	%rax, %rax
	je	.LBB1_22
.LBB1_11:
	movabsq	$NRT_decref, %rax
	movq	%r12, %rcx
	callq	*%rax
.LBB1_1:
	xorl	%esi, %esi
	jmp	.LBB1_2
.Lfunc_end1:
	.size	_ZN7cpython8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy, .Lfunc_end1-_ZN7cpython8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy
	.cfi_endproc

	.globl	cfunc._ZN8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy
	.p2align	4
	.type	cfunc._ZN8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy,@function
cfunc._ZN8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy:
	subq	$104, %rsp
	movq	144(%rsp), %rax
	vmovups	168(%rsp), %xmm0
	movq	184(%rsp), %rcx
	movq	$0, 96(%rsp)
	movq	%rcx, 88(%rsp)
	vmovups	%xmm0, 72(%rsp)
	movq	%rax, 48(%rsp)
	movabsq	$_ZN8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy, %rax
	leaq	96(%rsp), %rcx
	callq	*%rax
	movq	96(%rsp), %rax
	addq	$104, %rsp
	retq
.Lfunc_end2:
	.size	cfunc._ZN8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy, .Lfunc_end2-cfunc._ZN8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy

	.weak	NRT_decref
	.p2align	4
	.type	NRT_decref,@function
NRT_decref:
	.cfi_startproc
	testq	%rcx, %rcx
	je	.LBB3_2
	#MEMBARRIER
	lock		decq	(%rcx)
	je	.LBB3_3
.LBB3_2:
	retq
.LBB3_3:
	#MEMBARRIER
	movabsq	$NRT_MemInfo_call_dtor, %rax
	rex64 jmpq	*%rax
.Lfunc_end3:
	.size	NRT_decref, .Lfunc_end3-NRT_decref
	.cfi_endproc

	.type	.const.worker_strided_accumulate,@object
	.section	.lrodata,"al",@progbits
	.p2align	4, 0x0
.const.worker_strided_accumulate:
	.asciz	"worker_strided_accumulate"
	.size	.const.worker_strided_accumulate, 26

	.type	_ZN08NumbaEnv8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy,@object
	.comm	_ZN08NumbaEnv8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy,8,8
	.type	".const.missing Environment: _ZN08NumbaEnv8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy",@object
	.p2align	4, 0x0
".const.missing Environment: _ZN08NumbaEnv8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy":
	.asciz	"missing Environment: _ZN08NumbaEnv8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy"
	.size	".const.missing Environment: _ZN08NumbaEnv8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy", 153

	.type	".const.can't unbox array from PyObject into native value.  The object maybe of a different type",@object
	.p2align	4, 0x0
".const.can't unbox array from PyObject into native value.  The object maybe of a different type":
	.asciz	"can't unbox array from PyObject into native value.  The object maybe of a different type"
	.size	".const.can't unbox array from PyObject into native value.  The object maybe of a different type", 89

	.section	".note.GNU-stack","",@progbits
