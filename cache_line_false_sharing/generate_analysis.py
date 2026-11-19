"""Write an English Q1-Q5 report using only the current recorded evidence."""
import argparse
import json
from pathlib import Path

LAYOUTS = ("stride_1", "stride_4", "stride_8", "stride_16", "private")
LABELS = ("A: stride 1 (8 B)", "B: stride 4 (32 B)", "C: stride 8 (64 B)",
          "D: stride 16 (128 B)", "Register-private")


def write_analysis(root):
    root = Path(root)
    manifest = json.loads((root / "cache_lab_manifest.json").read_text(encoding="utf-8"))
    if not manifest["verification_passed"] or not manifest["full_specification_workload"]:
        raise ValueError("A verified full benchmark is required before generating the report.")
    ctx, summary, runs = manifest["context"], manifest["summary"], manifest["runs"]
    iterations = manifest["iterations_per_thread"]
    updates = iterations * manifest["num_threads"]
    repeats = manifest["repetitions"]
    times = {key: summary[key]["median_elapsed_ns"] for key in LAYOUTS}
    t1, t4, t8, t16, tp = (times[key] for key in LAYOUTS)
    ratio = t1 / t8
    ratio16 = t8 / t16
    table = []
    raw = []
    switches = []
    for key, label in zip(LAYOUTS, LABELS):
        table.append(f"| {label} | {times[key]:,} | {times[key] / updates:.9f} | "
                     f"{times[key] / iterations:.9f} |")
        samples = sorted((run for run in runs if run["layout"] == key),
                         key=lambda run: run["repetition"])
        for run in samples:
            raw.append(f"| {label} | {run['repetition'] + 1} | {run['elapsed_ns']:,} |")
            cs = run["context_switches"]
            def counter(value):
                return "unavailable" if value is None else str(value)
            switches.append(f"| {label} | {run['repetition'] + 1} | "
                            f"{counter(cs['voluntary'])} | {counter(cs['involuntary'])} | "
                            f"{counter(cs['total'])} |")
    table = "\n".join(table)
    raw = "\n".join(raw)
    switches = "\n".join(switches)
    finals = "\n".join(f"| {i} | {value} |" for i, value in enumerate(runs[0]["final_values"]))
    audit = manifest["llvm_audit"]
    ir_lines = "\n".join(audit["volatile_ir_lines"][:4])
    overlap = min(run["all_four_kernel_intervals_overlap_ns"] for run in runs)
    cpu_ratios = [run["cpu_time_to_wall_ratio"] for run in runs]
    paired_difference = t16 - t8
    comparison = ("slower" if paired_difference > 0 else "faster" if paired_difference < 0
                  else "equal")
    window_range8 = summary["stride_8"]["max_elapsed_ns"] - summary["stride_8"]["min_elapsed_ns"]
    window_range16 = summary["stride_16"]["max_elapsed_ns"] - summary["stride_16"]["min_elapsed_ns"]
    small_difference = abs(paired_difference) < max(window_range8, window_range16)
    significance = ("The median difference is smaller than the observed sample range; "
                    "these measurements do not establish a repeatable prefetcher benefit."
                    if small_difference else
                    "A median difference alone does not identify its cause; prefetcher controls "
                    "and hardware events were not measured.")
    switch_source = runs[0]["context_switches"]["source"]
    context_note = (
        "Python's resource module is unavailable on this Windows host. Voluntary and "
        "involuntary counts are null in the manifest; only psutil's total is available. "
        "They are not fabricated zeros. Windows totals sum live-thread counters, so "
        "all four workers stay alive for both snapshots."
        if "resource unavailable" in switch_source else
        "Voluntary and involuntary process context switches were collected with "
        "resource.getrusage(resource.RUSAGE_SELF).")
    gil_note = ("This run reports a GIL-enabled CPython interpreter."
                if ctx["gil_enabled"] else
                "This run reports a free-threaded interpreter; the conventional "
                "CPython GIL comparison below describes a GIL-enabled build.")
    report = f"""# Cache Line and False Sharing Mechanics: Analysis

**Student:** {ctx['student_name']}

**Student ID:** {ctx['student_id']}

**GitHub handle:** {ctx['git_username']}

**Instructor:** Sufyan bin Uzayr

**Recorded run (UTC):** {manifest['created_at_utc']}

## Method and reproducibility

This report was generated from cache_lab_manifest.json and its LLVM evidence.
The host CPU is **{ctx['cpu_model']}**, with **{ctx['physical_cores']} physical cores**
and **{ctx['logical_cores']} logical CPUs**, running {ctx['os']}.
Four workers were pinned to logical CPUs **{ctx['selected_logical_cpus']}**, on
four distinct physical cores identified by {ctx['topology_source']}.
The cache-line size is {ctx['cache_line_bytes']} bytes ({ctx['cache_line_source']}).

The seed input is `{ctx['seed_input']}`. Taking the first 16 hexadecimal digits
of its SHA-256 digest gives **INSTANCE_SEED = {ctx['instance_seed']}**.
Per-thread seeds are derived from this seed and remain identical across layouts.
Versions: NumPy {ctx['numpy']}, Numba {ctx['numba']}, llvmlite {ctx['llvmlite']}.

Every measured run performs **{iterations:,} updates per thread**, with **4 threads**
and **{updates:,} total updates**. There are **{repeats} repetitions per layout**.
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
timer resolution is {ctx['timer']['resolution']} seconds, so nanosecond units
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

The measured stride-1 median was **{t1:,} ns**, versus **{t8:,} ns** for
stride 8. Timing is consistent with a layout effect but does not directly observe
individual MESI transactions.

## Q2. Quantitative slowdown and coherency overhead

| Layout | Median elapsed (ns) | Aggregate ns/update: time / {updates:,} | Wall ns/thread iteration: time / {iterations:,} |
| --- | ---: | ---: | ---: |
{table}

Aggregate ns/update is reciprocal throughput across four workers; it is not the
latency of a single load or store. All raw wall-clock samples are:

| Layout | Repetition | Elapsed (ns) |
| --- | ---: | ---: |
{raw}

```text
stride-1 / stride-8 = {t1} / {t8} = {ratio:.9f}x
relative difference = {(ratio - 1) * 100:.6f}%
wall-time difference = {t1 - t8:,} ns
aggregate difference per update = {(t1 - t8) / updates:.9f} ns
stride-8 / private = {t8 / tp:.9f}x
stride-1 / private = {t1 / tp:.9f}x
stride-8 minus private = {t8 - tp:,} ns
```

The padded-versus-private difference includes repeated load/store operations,
store forwarding, arithmetic dependencies, and compiler effects. It is not an
isolated hardware latency. Likewise the contiguous-versus-padded difference is
not a direct RFO service-time measurement. CPU frequency, scheduling, buffering,
and sample spread affect the results. No theoretical slowdown was substituted.

### Context switches and concurrency

{context_note}
Counter source: {switch_source}. The counter window runs from before the start
barrier through the completion barrier while all workers are alive. It includes
synchronization and other process activity and is broader than the kernel window.

| Layout | Repetition | Voluntary | Involuntary | Total |
| --- | ---: | ---: | ---: | ---: |
{switches}

The minimum four-kernel overlap across all runs is **{overlap:,} ns**.
Summed thread CPU-time / wall-time ratios range from **{min(cpu_ratios):.6f}** to
**{max(cpu_ratios):.6f}**. Overlapping wall intervals support concurrent scheduling;
CPU time above one wall-time unit additionally supports parallel execution.
Thread CPU accounting can be coarse, particularly on Windows, and occasionally
produce values slightly above four. These are diagnostics, not precise utilization.

## Q3. L2 spatial prefetcher and 128-byte pairing

Stride 8 measured **{t8:,} ns** and stride 16 measured **{t16:,} ns**.
The stride-8 / stride-16 ratio is **{ratio16:.9f}x**. At the median, stride 16 is
**{abs(paired_difference):,} ns {comparison}** than stride 8.
{significance}

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
{ir_lines}
```

The audit finds **{audit['volatile_i64_load_sites']} static volatile i64 load sites**
and **{audit['volatile_i64_store_sites']} static volatile i64 store sites**, in
cyclic blocks **{', '.join(audit['volatile_loop_blocks'])}**. LLVM may unroll the
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
or cause a distinct RFO. The padded memory median was **{t8:,} ns** versus
**{tp:,} ns** for the register baseline.

## Q5. CPython GIL masking versus nogil=True execution

{gil_note}
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
stride-8 comparison is **{t1:,} ns versus {t8:,} ns** with identical work.
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
{finals}

The manifest records **verification_passed: true** for the required workload,
affinity, four-kernel overlap, parity, untouched slots, and LLVM audit. This does
not assert availability of unsupported OS counters, identify individual RFO
events, prove a prefetcher mechanism, or indicate a Git push occurred.
"""
    (root / "ANALYSIS.md").write_text(report, encoding="utf-8")
    print(f"Generated current analysis: {root / 'ANALYSIS.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path(__file__).resolve().parent)
    write_analysis(parser.parse_args().directory)
