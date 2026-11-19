; ModuleID = 'worker_private_accumulate'
source_filename = "<string>"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc"

@.const.worker_private_accumulate = internal constant [26 x i8] c"worker_private_accumulate\00"
@_ZN08NumbaEnv8__main__25worker_private_accumulateB2v2B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy = common local_unnamed_addr global ptr null
@".const.missing Environment: _ZN08NumbaEnv8__main__25worker_private_accumulateB2v2B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy" = internal constant [153 x i8] c"missing Environment: _ZN08NumbaEnv8__main__25worker_private_accumulateB2v2B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy\00"
@PyExc_TypeError = external global i8
@".const.can't unbox array from PyObject into native value.  The object maybe of a different type" = internal constant [89 x i8] c"can't unbox array from PyObject into native value.  The object maybe of a different type\00"
@_Py_NoneStruct = external global i8
@PyExc_RuntimeError = external global i8

; Function Attrs: nofree norecurse nosync nounwind memory(argmem: readwrite)
define noundef i32 @_ZN8__main__25worker_private_accumulateB2v2B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy(ptr noalias writeonly captures(none) %retptr, ptr noalias readnone captures(none) %excinfo, ptr readnone captures(none) %arg.buffer.0, ptr readnone captures(none) %arg.buffer.1, i64 %arg.buffer.2, i64 %arg.buffer.3, ptr captures(none) %arg.buffer.4, i64 %arg.buffer.5.0, i64 %arg.buffer.6.0, i64 %arg.slot, i64 %arg.iters, i64 %arg.thread_seed) local_unnamed_addr #0 {
B0.endif:
  %.23 = or i64 %arg.thread_seed, 1
  %.41 = icmp slt i64 %arg.slot, 0
  %.42 = select i1 %.41, i64 %arg.buffer.5.0, i64 0
  %0 = getelementptr i64, ptr %arg.buffer.4, i64 %arg.slot
  %.56 = getelementptr i64, ptr %0, i64 %.42
  %.57 = load i64, ptr %.56, align 8
  %.14279.not = icmp slt i64 %arg.iters, 1
  br i1 %.14279.not, label %B132, label %B84.preheader

B84.preheader:                                    ; preds = %B0.endif
  %const = bitcast i64 6364136223846793005 to i64
  %xtraiter = and i64 %arg.iters, 7
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  br i1 %lcmp.mod.not, label %B84.prol.loopexit, label %B84.prol.preheader

B84.prol.preheader:                               ; preds = %B84.preheader
  br label %B84.prol

B84.prol:                                         ; preds = %B84.prol.preheader, %B84.prol
  %accumulator.2.082.prol = phi i64 [ %.183.prol, %B84.prol ], [ %.57, %B84.prol.preheader ]
  %prol.iter = phi i64 [ %prol.iter.next, %B84.prol ], [ 0, %B84.prol.preheader ]
  %.181.prol = mul i64 %accumulator.2.082.prol, %const
  %.183.prol = add i64 %.181.prol, %.23
  %prol.iter.next = add i64 %prol.iter, 1
  %prol.iter.cmp.not = icmp eq i64 %xtraiter, %prol.iter.next
  br i1 %prol.iter.cmp.not, label %B84.prol.loopexit.loopexit, label %B84.prol, !llvm.loop !0

B84.prol.loopexit.loopexit:                       ; preds = %B84.prol
  %1 = sub i64 %arg.iters, %prol.iter.next
  br label %B84.prol.loopexit

B84.prol.loopexit:                                ; preds = %B84.prol.loopexit.loopexit, %B84.preheader
  %accumulator.2.082.unr = phi i64 [ %.57, %B84.preheader ], [ %.183.prol, %B84.prol.loopexit.loopexit ]
  %.14181.unr = phi i64 [ %arg.iters, %B84.preheader ], [ %1, %B84.prol.loopexit.loopexit ]
  %.183.lcssa.unr = phi i64 [ poison, %B84.preheader ], [ %.183.prol, %B84.prol.loopexit.loopexit ]
  %2 = icmp ult i64 %arg.iters, 8
  br i1 %2, label %B132, label %B84.preheader1

B84.preheader1:                                   ; preds = %B84.prol.loopexit
  %3 = add i64 %.14181.unr, 8
  br label %B84

B84:                                              ; preds = %B84.preheader1, %B84
  %lsr.iv = phi i64 [ %3, %B84.preheader1 ], [ %lsr.iv.next, %B84 ]
  %accumulator.2.082 = phi i64 [ %.183.7, %B84 ], [ %accumulator.2.082.unr, %B84.preheader1 ]
  %.181 = mul i64 %accumulator.2.082, %const
  %.183 = add i64 %.181, %.23
  %.181.1 = mul i64 %.183, %const
  %.183.1 = add i64 %.181.1, %.23
  %.181.2 = mul i64 %.183.1, %const
  %.183.2 = add i64 %.181.2, %.23
  %.181.3 = mul i64 %.183.2, %const
  %.183.3 = add i64 %.181.3, %.23
  %.181.4 = mul i64 %.183.3, %const
  %.183.4 = add i64 %.181.4, %.23
  %.181.5 = mul i64 %.183.4, %const
  %.183.5 = add i64 %.181.5, %.23
  %.181.6 = mul i64 %.183.5, %const
  %.183.6 = add i64 %.181.6, %.23
  %.181.7 = mul i64 %.183.6, %const
  %.183.7 = add i64 %.181.7, %.23
  %lsr.iv.next = add i64 %lsr.iv, -8
  %.142.7 = icmp sgt i64 %lsr.iv.next, 8
  br i1 %.142.7, label %B84, label %B132

B132:                                             ; preds = %B84, %B84.prol.loopexit, %B0.endif
  %accumulator.2.0.lcssa = phi i64 [ %.57, %B0.endif ], [ %.183.lcssa.unr, %B84.prol.loopexit ], [ %.183.7, %B84 ]
  %sunkaddr = mul i64 %.42, 8
  %sunkaddr2 = getelementptr inbounds i8, ptr %0, i64 %sunkaddr
  store i64 %accumulator.2.0.lcssa, ptr %sunkaddr2, align 8
  store ptr null, ptr %retptr, align 8
  ret i32 0
}

define noundef ptr @_ZN7cpython8__main__25worker_private_accumulateB2v2B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy(ptr readnone captures(none) %py_closure, ptr %py_args, ptr readnone captures(none) %py_kws) local_unnamed_addr {
entry:
  %.5 = alloca ptr, align 8
  %.6 = alloca ptr, align 8
  %.7 = alloca ptr, align 8
  %.8 = alloca ptr, align 8
  %.9 = call i32 (ptr, ptr, i64, i64, ...) @PyArg_UnpackTuple(ptr %py_args, ptr nonnull @.const.worker_private_accumulate, i64 4, i64 4, ptr nonnull %.5, ptr nonnull %.6, ptr nonnull %.7, ptr nonnull %.8)
  %.10 = icmp eq i32 %.9, 0
  %.24 = alloca { ptr, ptr, i64, i64, ptr, [1 x i64], [1 x i64] }, align 8
  %.95 = alloca ptr, align 8
  br i1 %.10, label %common.ret, label %entry.endif, !prof !2

common.ret:                                       ; preds = %entry.endif.endif.endif.thread, %arg0.err, %entry, %entry.endif.endif.endif.e...endif.endif, %entry.endif.if
  %common.ret.op = phi ptr [ null, %arg0.err ], [ null, %entry ], [ null, %entry.endif.if ], [ null, %entry.endif.endif.endif.thread ], [ @_Py_NoneStruct, %entry.endif.endif.endif.e...endif.endif ]
  ret ptr %common.ret.op

entry.endif:                                      ; preds = %entry
  %.14 = load ptr, ptr @_ZN08NumbaEnv8__main__25worker_private_accumulateB2v2B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy, align 8
  %.19 = icmp eq ptr %.14, null
  br i1 %.19, label %entry.endif.if, label %entry.endif.endif, !prof !2

entry.endif.if:                                   ; preds = %entry.endif
  call void @PyErr_SetString(ptr nonnull @PyExc_RuntimeError, ptr nonnull @".const.missing Environment: _ZN08NumbaEnv8__main__25worker_private_accumulateB2v2B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy")
  br label %common.ret

entry.endif.endif:                                ; preds = %entry.endif
  %.23 = load ptr, ptr %.5, align 8
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 8 dereferenceable(56) %.24, i8 0, i64 56, i1 false)
  %.28 = call i32 @NRT_adapt_ndarray_from_python(ptr %.23, ptr nonnull %.24)
  %sunkaddr = getelementptr inbounds i8, ptr %.24, i64 24
  %.32 = load i64, ptr %sunkaddr, align 8
  %.33 = icmp ne i64 %.32, 8
  %.34 = icmp ne i32 %.28, 0
  %.35 = or i1 %.34, %.33
  br i1 %.35, label %entry.endif.endif.endif.thread, label %entry.endif.endif.endif.endif, !prof !2

entry.endif.endif.endif.thread:                   ; preds = %entry.endif.endif
  call void @PyErr_SetString(ptr nonnull @PyExc_TypeError, ptr nonnull @".const.can't unbox array from PyObject into native value.  The object maybe of a different type")
  br label %common.ret

entry.endif.endif.endif.endif:                    ; preds = %entry.endif.endif
  %.39.fca.0.load = load ptr, ptr %.24, align 8
  %sunkaddr1 = getelementptr inbounds i8, ptr %.24, i64 32
  %.39.fca.4.load = load ptr, ptr %sunkaddr1, align 8
  %sunkaddr2 = getelementptr inbounds i8, ptr %.24, i64 40
  %.39.fca.5.0.load = load i64, ptr %sunkaddr2, align 8
  %.46 = load ptr, ptr %.6, align 8
  %.49 = call ptr @PyNumber_Long(ptr %.46)
  %.50.not = icmp eq ptr %.49, null
  br i1 %.50.not, label %entry.endif.endif.endif.endif.endif, label %entry.endif.endif.endif.endif.if, !prof !2

arg0.err:                                         ; preds = %entry.endif.endif.endif.e...endif, %entry.endif.endif.endif.endif.endif.endif.endif, %entry.endif.endif.endif.endif.endif
  call void @NRT_decref(ptr %.39.fca.0.load)
  br label %common.ret

entry.endif.endif.endif.endif.if:                 ; preds = %entry.endif.endif.endif.endif
  %.52 = call i64 @PyLong_AsLongLong(ptr nonnull %.49)
  call void @Py_DecRef(ptr nonnull %.49)
  br label %entry.endif.endif.endif.endif.endif

entry.endif.endif.endif.endif.endif:              ; preds = %entry.endif.endif.endif.endif.if, %entry.endif.endif.endif.endif
  %.47.0 = phi i64 [ %.52, %entry.endif.endif.endif.endif.if ], [ 0, %entry.endif.endif.endif.endif ]
  %.57 = call ptr @PyErr_Occurred()
  %.58.not = icmp eq ptr %.57, null
  br i1 %.58.not, label %entry.endif.endif.endif.endif.endif.endif, label %arg0.err, !prof !3

entry.endif.endif.endif.endif.endif.endif:        ; preds = %entry.endif.endif.endif.endif.endif
  %.62 = load ptr, ptr %.7, align 8
  %.65 = call ptr @PyNumber_Long(ptr %.62)
  %.66.not = icmp eq ptr %.65, null
  br i1 %.66.not, label %entry.endif.endif.endif.endif.endif.endif.endif, label %entry.endif.endif.endif.endif.endif.endif.if, !prof !2

entry.endif.endif.endif.endif.endif.endif.if:     ; preds = %entry.endif.endif.endif.endif.endif.endif
  %.68 = call i64 @PyLong_AsLongLong(ptr nonnull %.65)
  call void @Py_DecRef(ptr nonnull %.65)
  br label %entry.endif.endif.endif.endif.endif.endif.endif

entry.endif.endif.endif.endif.endif.endif.endif:  ; preds = %entry.endif.endif.endif.endif.endif.endif.if, %entry.endif.endif.endif.endif.endif.endif
  %.63.0 = phi i64 [ %.68, %entry.endif.endif.endif.endif.endif.endif.if ], [ 0, %entry.endif.endif.endif.endif.endif.endif ]
  %.73 = call ptr @PyErr_Occurred()
  %.74.not = icmp eq ptr %.73, null
  br i1 %.74.not, label %entry.endif.endif.endif.endif.endif.endif.endif.endif, label %arg0.err, !prof !3

entry.endif.endif.endif.endif.endif.endif.endif.endif: ; preds = %entry.endif.endif.endif.endif.endif.endif.endif
  %.78 = load ptr, ptr %.8, align 8
  %.81 = call ptr @PyNumber_Long(ptr %.78)
  %.82.not = icmp eq ptr %.81, null
  br i1 %.82.not, label %entry.endif.endif.endif.e...endif, label %entry.endif.endif.endif.e...if, !prof !2

entry.endif.endif.endif.e...if:                   ; preds = %entry.endif.endif.endif.endif.endif.endif.endif.endif
  %.84 = call i64 @PyLong_AsUnsignedLongLong(ptr nonnull %.81)
  call void @Py_DecRef(ptr nonnull %.81)
  br label %entry.endif.endif.endif.e...endif

entry.endif.endif.endif.e...endif:                ; preds = %entry.endif.endif.endif.e...if, %entry.endif.endif.endif.endif.endif.endif.endif.endif
  %.79.0 = phi i64 [ %.84, %entry.endif.endif.endif.e...if ], [ 0, %entry.endif.endif.endif.endif.endif.endif.endif.endif ]
  %.89 = call ptr @PyErr_Occurred()
  %.90.not = icmp eq ptr %.89, null
  br i1 %.90.not, label %entry.endif.endif.endif.e...endif.endif, label %arg0.err, !prof !3

entry.endif.endif.endif.e...endif.endif:          ; preds = %entry.endif.endif.endif.e...endif
  %.94 = call ptr @PyEval_SaveThread()
  %.101 = call i32 @_ZN8__main__25worker_private_accumulateB2v2B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy(ptr nonnull %.95, ptr nonnull poison, ptr poison, ptr poison, i64 poison, i64 poison, ptr %.39.fca.4.load, i64 %.39.fca.5.0.load, i64 poison, i64 %.47.0, i64 %.63.0, i64 %.79.0) #3
  call void @PyEval_RestoreThread(ptr %.94)
  call void @NRT_decref(ptr %.39.fca.0.load)
  call void @Py_IncRef(ptr nonnull @_Py_NoneStruct)
  br label %common.ret
}

declare i32 @PyArg_UnpackTuple(ptr, ptr, i64, i64, ...) local_unnamed_addr

declare void @PyErr_SetString(ptr, ptr) local_unnamed_addr

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr writeonly captures(none), i8, i64, i1 immarg) #1

declare i32 @NRT_adapt_ndarray_from_python(ptr captures(none), ptr captures(none)) local_unnamed_addr

declare ptr @PyNumber_Long(ptr) local_unnamed_addr

declare i64 @PyLong_AsLongLong(ptr) local_unnamed_addr

declare void @Py_DecRef(ptr) local_unnamed_addr

declare ptr @PyErr_Occurred() local_unnamed_addr

declare i64 @PyLong_AsUnsignedLongLong(ptr) local_unnamed_addr

declare ptr @PyEval_SaveThread() local_unnamed_addr

declare void @PyEval_RestoreThread(ptr) local_unnamed_addr

declare void @Py_IncRef(ptr) local_unnamed_addr

; Function Attrs: nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none, target_mem0: none, target_mem1: none)
define ptr @cfunc._ZN8__main__25worker_private_accumulateB2v2B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy({ ptr, ptr, i64, i64, ptr, [1 x i64], [1 x i64] } %.1, i64 %.2, i64 %.3, i64 %.4) local_unnamed_addr #2 {
entry:
  %.6 = alloca ptr, align 8
  store ptr null, ptr %.6, align 8
  %extracted.data = extractvalue { ptr, ptr, i64, i64, ptr, [1 x i64], [1 x i64] } %.1, 4
  %extracted.shape = extractvalue { ptr, ptr, i64, i64, ptr, [1 x i64], [1 x i64] } %.1, 5
  %.10 = extractvalue [1 x i64] %extracted.shape, 0
  %.12 = call i32 @_ZN8__main__25worker_private_accumulateB2v2B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy(ptr nonnull %.6, ptr nonnull poison, ptr poison, ptr poison, i64 poison, i64 poison, ptr %extracted.data, i64 %.10, i64 poison, i64 %.2, i64 %.3, i64 %.4) #3
  %.22 = load ptr, ptr %.6, align 8
  ret ptr %.22
}

; Function Attrs: noinline
define linkonce_odr void @NRT_decref(ptr %.1) local_unnamed_addr #3 {
.3:
  %.4 = icmp eq ptr %.1, null
  br i1 %.4, label %common.ret1, label %.3.endif, !prof !2

common.ret1:                                      ; preds = %.3, %.3.endif
  ret void

.3.endif:                                         ; preds = %.3
  fence release
  %0 = tail call i8 @llvm.x86.atomic.sub.cc.i64(ptr nonnull %.1, i64 1, i32 4)
  %1 = trunc i8 %0 to i1
  br i1 %1, label %.3.endif.if, label %common.ret1, !prof !2

.3.endif.if:                                      ; preds = %.3.endif
  fence acquire
  tail call void @NRT_MemInfo_call_dtor(ptr nonnull %.1)
  ret void
}

; Function Attrs: nounwind
declare i8 @llvm.x86.atomic.sub.cc.i64(ptr, i64, i32 immarg) #4

declare void @NRT_MemInfo_call_dtor(ptr) local_unnamed_addr

attributes #0 = { nofree norecurse nosync nounwind memory(argmem: readwrite) }
attributes #1 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #2 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none, target_mem0: none, target_mem1: none) }
attributes #3 = { noinline }
attributes #4 = { nounwind }

!0 = distinct !{!0, !1}
!1 = !{!"llvm.loop.unroll.disable"}
!2 = !{!"branch_weights", i32 1, i32 99}
!3 = !{!"branch_weights", i32 99, i32 1}
