define noundef i32 @_ZN8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy(ptr noalias writeonly captures(none) %retptr, ptr noalias readnone captures(none) %excinfo, ptr readnone captures(none) %arg.buffer.0, ptr readnone captures(none) %arg.buffer.1, i64 %arg.buffer.2, i64 %arg.buffer.3, ptr %arg.buffer.4, i64 %arg.buffer.5.0, i64 %arg.buffer.6.0, i64 %arg.slot, i64 %arg.iters, i64 %arg.thread_seed) local_unnamed_addr #0 {
B0.endif:
  %0 = freeze i64 %arg.iters
  %.23 = or i64 %arg.thread_seed, 1
  %.10872.not = icmp slt i64 %0, 1
  br i1 %.10872.not, label %B170, label %B76.lr.ph

B76.lr.ph:                                        ; preds = %B0.endif
  %const = bitcast i64 6364136223846793005 to i64
  %xtraiter = and i64 %0, 7
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  br i1 %lcmp.mod.not, label %B76.prol.loopexit, label %B76.prol.preheader

B76.prol.preheader:                               ; preds = %B76.lr.ph
  br label %B76.prol

B76.prol:                                         ; preds = %B76.prol.preheader, %B76.prol
  %prol.iter = phi i64 [ %prol.iter.next, %B76.prol ], [ 0, %B76.prol.preheader ]
  %sunkaddr = mul i64 %arg.slot, 8
  %sunkaddr1 = getelementptr i8, ptr %arg.buffer.4, i64 %sunkaddr
  %counter.load.prol = load volatile i64, ptr %sunkaddr1, align 8
  %.155.prol = mul i64 %counter.load.prol, %const
  %.157.prol = add i64 %.155.prol, %.23
  store volatile i64 %.157.prol, ptr %sunkaddr1, align 8
  %prol.iter.next = add i64 %prol.iter, 1
  %prol.iter.cmp.not = icmp eq i64 %xtraiter, %prol.iter.next
  br i1 %prol.iter.cmp.not, label %B76.prol.loopexit.loopexit, label %B76.prol, !llvm.loop !0

B76.prol.loopexit.loopexit:                       ; preds = %B76.prol
  %1 = sub i64 %0, %prol.iter.next
  br label %B76.prol.loopexit

B76.prol.loopexit:                                ; preds = %B76.prol.loopexit.loopexit, %B76.lr.ph
  %.1077074.unr = phi i64 [ %0, %B76.lr.ph ], [ %1, %B76.prol.loopexit.loopexit ]
  %2 = icmp ult i64 %0, 8
  br i1 %2, label %B170, label %B76.preheader

B76.preheader:                                    ; preds = %B76.prol.loopexit
  %3 = add i64 %.1077074.unr, 8
  br label %B76

B76:                                              ; preds = %B76.preheader, %B76
  %lsr.iv = phi i64 [ %3, %B76.preheader ], [ %lsr.iv.next, %B76 ]
  %sunkaddr2 = mul i64 %arg.slot, 8
  %sunkaddr3 = getelementptr i8, ptr %arg.buffer.4, i64 %sunkaddr2
  %counter.load = load volatile i64, ptr %sunkaddr3, align 8
  %.155 = mul i64 %counter.load, %const
  %.157 = add i64 %.155, %.23
  store volatile i64 %.157, ptr %sunkaddr3, align 8
  %counter.load.1 = load volatile i64, ptr %sunkaddr3, align 8
  %.155.1 = mul i64 %counter.load.1, %const
  %.157.1 = add i64 %.155.1, %.23
  store volatile i64 %.157.1, ptr %sunkaddr3, align 8
  %counter.load.2 = load volatile i64, ptr %sunkaddr3, align 8
  %.155.2 = mul i64 %counter.load.2, %const
  %.157.2 = add i64 %.155.2, %.23
  store volatile i64 %.157.2, ptr %sunkaddr3, align 8
  %counter.load.3 = load volatile i64, ptr %sunkaddr3, align 8
  %.155.3 = mul i64 %counter.load.3, %const
  %.157.3 = add i64 %.155.3, %.23
  store volatile i64 %.157.3, ptr %sunkaddr3, align 8
  %counter.load.4 = load volatile i64, ptr %sunkaddr3, align 8
  %.155.4 = mul i64 %counter.load.4, %const
  %.157.4 = add i64 %.155.4, %.23
  store volatile i64 %.157.4, ptr %sunkaddr3, align 8
  %counter.load.5 = load volatile i64, ptr %sunkaddr3, align 8
  %.155.5 = mul i64 %counter.load.5, %const
  %.157.5 = add i64 %.155.5, %.23
  store volatile i64 %.157.5, ptr %sunkaddr3, align 8
  %counter.load.6 = load volatile i64, ptr %sunkaddr3, align 8
  %.155.6 = mul i64 %counter.load.6, %const
  %.157.6 = add i64 %.155.6, %.23
  store volatile i64 %.157.6, ptr %sunkaddr3, align 8
  %counter.load.7 = load volatile i64, ptr %sunkaddr3, align 8
  %.155.7 = mul i64 %counter.load.7, %const
  %.157.7 = add i64 %.155.7, %.23
  store volatile i64 %.157.7, ptr %sunkaddr3, align 8
  %lsr.iv.next = add i64 %lsr.iv, -8
  %.108.7 = icmp sgt i64 %lsr.iv.next, 8
  br i1 %.108.7, label %B76, label %B170

B170:                                             ; preds = %B76, %B76.prol.loopexit, %B0.endif
  store ptr null, ptr %retptr, align 8
  ret i32 0
}