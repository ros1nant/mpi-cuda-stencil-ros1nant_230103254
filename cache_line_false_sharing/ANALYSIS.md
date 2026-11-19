# Cache Line and False Sharing Mechanics: Analysis

**Student:** Ainabek Aisultan

**Student ID:** 230103254

**GitHub handle:** ros1nant

**Instructor:** Sufyan bin Uzayr

**Recorded run (UTC):** 2026-11-19T07:34:18.080614+00:00

## Method and reproducibility

This report was generated from cache_lab_manifest.json and its LLVM evidence.
The host CPU is **13th Gen Intel(R) Core(TM) i7-13650HX**, with **14 physical cores**
and **20 logical CPUs**, running Windows-11-10.0.26300-SP0.
Four workers were pinned to logical CPUs **[0, 2, 4, 6]**, on
four distinct physical cores identified by GetLogicalProcessorInformation.
The cache-line size is 64 bytes (64-byte fallback).

The seed input is `ros1nant::AMD64::13th Gen Intel(R) Core(TM) i7-13650HX::20`. Taking the first 16 hexadecimal digits
of its SHA-256 digest gives **INSTANCE_SEED = 11063486948304444235**.
Per-thread seeds are derived from this seed and remain identical across layouts.
Versions: NumPy 2.2.3, Numba 0.66.0, llvmlite 0.48.0.

Every measured run performs **60,000,000 updates per thread**, with **4 threads**
and **240,000,000 total updates**. There are **3 repetitions per layout**.
The identical uint64 recurrence is:

```text
x0 = 0
x_next = (x * 6364136223846793005 + (thread_seed | 1)) modulo 2**64
```

The buffers are 128-byte aligned, also satisfying 64-byte alignment. Relative
cache-line mappings are [0, 0, 0, 0] for stride 1, [0, 0, 1, 1] for stride 4,
[0, 1, 2, 3] for stride 8, and [0, 2, 4, 6] for stride 16. Distinct words are
owned by distinct threads, so there is no same-variable data race.

JIT compilation and warmup precede timing. time.perf_counter_ns() measures start
barrier release through the last kernel return; worker creation, compilation,
parity checks, and file writing are excluded. Barrier release and Python dispatch
overhead remain included. Layout order rotates between repetitions. The reported
timer resolution is 1e-07 seconds, so nanosecond units
do not imply 1 ns accuracy. Primary results use medians.

## Q1. MESI protocol state transitions

Consider Core 0 and Core 1 holding clean shared copies of the same line after
reads: **(Shared, Shared)**. buffer[0] and buffer[1] are different words in that
line under stride 1.

1. Core 0's store requires exclusive ownership. A Shared-line ownership upgrade
   invalidates Core 1's copy. After acknowledgments the stable states become
   **(Modified, Invalid)**. An upgrade need not fetch already cached data again.
2. Core 1's following read-modify-write finds its line Invalid. It needs an
   ownership request (RFO / read-exclusive, possibly following a shared read).
   Core 0 supplies or writes back the dirty data and loses ownership. A direct
   transfer leaves **(Invalid, Modified)**.
3. Core 0's next ownership request reverses the states to **(Modified, Invalid)**.
   Four writers extend this ownership competition to four cores.

Starting instead from **(Invalid, Invalid)** with no other sharers, Core 0's
ordinary first read can obtain **(Exclusive, Invalid)**, followed by a silent
Exclusive-to-Modified transition on its store. Exclusive is not a required
intermediate state in the Shared-line trace. Actual processors have transient
states and may use an interconnect rather than a literal shared bus.

Core 1 can enqueue a store before ownership arrives, but its store-buffer entry
cannot drain into a writable coherent line until ownership and invalidation
acknowledgments complete. Dependency or buffer exhaustion can then stall progress.
Not every store creates an RFO: stores while the line remains Modified proceed
locally, and store buffering can batch ownership intervals.

The measured stride-1 median was **137,933,000 ns**, versus **127,706,900 ns** for
stride 8. Timing is consistent with a layout effect but does not directly observe
individual MESI transactions.

## Q2. Quantitative slowdown and coherency overhead

| Layout | Median elapsed (ns) | Aggregate ns/update: time / 240,000,000 | Wall ns/thread iteration: time / 60,000,000 |
| --- | ---: | ---: | ---: |
| A: stride 1 (8 B) | 137,933,000 | 0.574720833 | 2.298883333 |
| B: stride 4 (32 B) | 138,060,800 | 0.575253333 | 2.301013333 |
| C: stride 8 (64 B) | 127,706,900 | 0.532112083 | 2.128448333 |
| D: stride 16 (128 B) | 127,770,900 | 0.532378750 | 2.129515000 |
| Register-private | 56,198,800 | 0.234161667 | 0.936646667 |

Aggregate ns/update is reciprocal throughput across four workers; it is not the
latency of a single load or store. All raw wall-clock samples are:

| Layout | Repetition | Elapsed (ns) |
| --- | ---: | ---: |
| A: stride 1 (8 B) | 1 | 139,052,800 |
| A: stride 1 (8 B) | 2 | 137,933,000 |
| A: stride 1 (8 B) | 3 | 134,114,000 |
| B: stride 4 (32 B) | 1 | 163,694,800 |
| B: stride 4 (32 B) | 2 | 138,060,800 |
| B: stride 4 (32 B) | 3 | 132,359,600 |
| C: stride 8 (64 B) | 1 | 130,620,100 |
| C: stride 8 (64 B) | 2 | 127,706,900 |
| C: stride 8 (64 B) | 3 | 124,458,200 |
| D: stride 16 (128 B) | 1 | 132,317,400 |
| D: stride 16 (128 B) | 2 | 127,770,900 |
| D: stride 16 (128 B) | 3 | 123,486,800 |
| Register-private | 1 | 56,198,800 |
| Register-private | 2 | 59,055,200 |
| Register-private | 3 | 54,860,100 |

```text
stride-1 / stride-8 = 137933000 / 127706900 = 1.080074765x
relative difference = 8.007476%
wall-time difference = 10,226,100 ns
aggregate difference per update = 0.042608750 ns
stride-8 / private = 2.272413290x
stride-1 / private = 2.454376250x
stride-8 minus private = 71,508,100 ns
```

The padded-versus-private difference includes repeated load/store operations,
store forwarding, arithmetic dependencies, and compiler effects. It is not an
isolated hardware latency. Likewise the contiguous-versus-padded difference is
not a direct RFO service-time measurement. CPU frequency, scheduling, buffering,
and sample spread affect the results. No theoretical slowdown was substituted.

### Context switches and concurrency

Python's resource module is unavailable on this Windows host. Voluntary and involuntary counts are null in the manifest; only psutil's total is available. They are not fabricated zeros. Windows totals sum live-thread counters, so all four workers stay alive for both snapshots.
Counter source: psutil Windows total; resource unavailable. The counter window runs from before the start
barrier through the completion barrier while all workers are alive. It includes
synchronization and other process activity and is broader than the kernel window.

| Layout | Repetition | Voluntary | Involuntary | Total |
| --- | ---: | ---: | ---: | ---: |
| A: stride 1 (8 B) | 1 | unavailable | unavailable | 109 |
| A: stride 1 (8 B) | 2 | unavailable | unavailable | 419 |
| A: stride 1 (8 B) | 3 | unavailable | unavailable | 85 |
| B: stride 4 (32 B) | 1 | unavailable | unavailable | 227 |
| B: stride 4 (32 B) | 2 | unavailable | unavailable | 104 |
| B: stride 4 (32 B) | 3 | unavailable | unavailable | 69 |
| C: stride 8 (64 B) | 1 | unavailable | unavailable | 104 |
| C: stride 8 (64 B) | 2 | unavailable | unavailable | 134 |
| C: stride 8 (64 B) | 3 | unavailable | unavailable | 48 |
| D: stride 16 (128 B) | 1 | unavailable | unavailable | 84 |
| D: stride 16 (128 B) | 2 | unavailable | unavailable | 85 |
| D: stride 16 (128 B) | 3 | unavailable | unavailable | 61 |
| Register-private | 1 | unavailable | unavailable | 63 |
| Register-private | 2 | unavailable | unavailable | 267 |
| Register-private | 3 | unavailable | unavailable | 37 |

The minimum four-kernel overlap across all runs is **53,276,200 ns**.
Summed thread CPU-time / wall-time ratios range from **3.054465** to
**4.272231**. Overlapping wall intervals support concurrent scheduling;
CPU time above one wall-time unit additionally supports parallel execution.
Thread CPU accounting can be coarse, particularly on Windows, and occasionally
produce values slightly above four. These are diagnostics, not precise utilization.

## Q3. L2 spatial prefetcher and 128-byte pairing

Stride 8 measured **127,706,900 ns** and stride 16 measured **127,770,900 ns**.
The stride-8 / stride-16 ratio is **0.999499103x**. At the median, stride 16 is
**64,000 ns slower** than stride 8.
The median difference is smaller than the observed sample range; these measurements do not establish a repeatable prefetcher benefit.

Intel documents spatial prefetchers that fetch the partner 64-byte line in the
same 128-byte-aligned region. With a 128-byte-aligned base, stride-8 workers use
lines 0/1 and 2/3, which form such pairs. Stride 16 writes lines 0, 2, 4, and 6,
leaving their potential companions unused.

This pairing does not make coherence operate at 128-byte granularity. A neighbor
prefetch can introduce a copy of another worker's line into a peer cache, adding
a sharer, downgrading ownership, or requiring an extra invalidation later.
Such secondary interference depends on the CPU, cache state, enabled prefetchers,
and access pattern. 64-byte spacing removes direct same-line sharing; 128-byte
spacing addresses this adjacent-line mechanism rather than all cache effects.

Prefetcher controls and hardware events were not measured here. The observed
difference cannot establish that mechanism on this host. See Intel's
[Optimization Reference Manual, Volume 2](https://cdrdv2-public.intel.com/821614/356477-Software-Optimization-Manual_V2.pdf).

## Q4. Compiler register promotion versus volatile memory stores

A loop-carried arithmetic dependency does not itself prevent register promotion:
an optimizer can keep buffer[slot] in a register and sink its final store. The
strided kernel uses Numba intrinsics to emit volatile uint64 memory accesses
inside every iteration, preserving the actual per-iteration traffic. The native
optimized IR contains these exact lines:

```llvm
%counter.load.prol = load volatile i64, ptr %sunkaddr1, align 8
store volatile i64 %.157.prol, ptr %sunkaddr1, align 8
%counter.load = load volatile i64, ptr %sunkaddr3, align 8
store volatile i64 %.157, ptr %sunkaddr3, align 8
```

The audit finds **9 static volatile i64 load sites**
and **9 static volatile i64 store sites**, in
cyclic blocks **B76.prol, B76**. LLVM may unroll the
loop, duplicating static sites while retaining exactly one load/store pair per
executed source iteration. The control-flow audit checks actual backedges, and
the full LLVM module passes LLVM's verifier.

Under [LLVM's volatile rules](https://llvm.org/docs/LangRef.html#volatile-memory-accesses),
the optimizer must preserve the dynamic number and relative order of volatile
operations. Volatile is not an atomic RMW or cross-thread synchronization. Threads
write separate words, so locks and atomic operations are unnecessary here.

The private native function has register accumulator phi nodes, no volatile
accesses, and one i64 shared-counter store after its loop. Its `store ptr null`
writes Numba's return slot, not a counter. The strided native body has no Python
C-API or GIL-management calls; nopython signatures and objectmode=False are audited.
Python-related code in a full LLVM module belongs to its entry wrapper.

Generated assembly is included. A real memory instruction can still use the
store buffer or store forwarding; volatility does not force every store to RAM
or cause a distinct RFO. The padded memory median was **127,706,900 ns** versus
**56,198,800 ns** for the register baseline.

## Q5. CPython GIL masking versus nogil=True execution

This run reports a GIL-enabled CPython interpreter.
With ordinary GIL-enabled Python bytecode threads, only one CPU-bound Python
thread executes bytecode at a time. Four Python loops therefore do not generate
four continuously simultaneous native counter-store streams. GIL handoff and
scheduling add overhead and often slow a fixed amount of CPU work as thread count
increases. With fixed work per thread, more threads also mean more total work;
that effect must be distinguished from lock overhead.

Ownership can still transfer when Python threads take turns, and the GIL itself
can contend. What is masked is sustained simultaneous counter-store competition,
not literally every possible coherence event. Interpreter and object overhead
also obscure the desired hardware comparison.

The two lab kernels use @njit(nogil=True), releasing the GIL during nopython
machine-code execution. Affinity places workers on separate physical cores, and
the barriers synchronize them. Native LLVM evidence, overlapping kernel intervals,
and recorded CPU time support multicore execution. The native stride-1 versus
stride-8 comparison is **137,933,000 ns versus 127,706,900 ns** with identical work.
No pure-Python control timing was measured or invented.

See the [Numba compilation documentation](https://numba.readthedocs.io/en/stable/user/jit.html#nogil)
and [Python threading documentation](https://docs.python.org/3/library/threading.html#gil-and-performance-considerations).
Optional free-threaded Python builds change the conventional GIL premise.

## Exact parity and verification

An independent affine-exponentiation oracle computes expected uint64 states in
O(log n), rather than reusing the timed loop. Before benchmarking, both kernels
are checked for 0, 1, 2, 3, 31, and 1,024 iterations with seeds 0, 1, maximum
uint64, and the instance seed. Unassigned buffer elements must remain zero.

Final values, identical across all four layouts, the private baseline, and every
repetition:

| Thread | Final uint64 counter |
| --- | ---: |
| 0 | 11728436330833416448 |
| 1 | 14589801440730549504 |
| 2 | 278312573438284032 |
| 3 | 11708582284052155648 |

The manifest records **verification_passed: true** for the required workload,
affinity, four-kernel overlap, parity, untouched slots, and LLVM audit. This does
not assert availability of unsupported OS counters, identify individual RFO
events, prove a prefetcher mechanism, or indicate a Git push occurred.
