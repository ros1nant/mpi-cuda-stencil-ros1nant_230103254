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