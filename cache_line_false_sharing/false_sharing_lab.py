"""Cache-line false-sharing lab: Ainabek Aisultan, student ID 230103254.

Run: python false_sharing_lab.py
The default is the complete 4 x 60,000,000-update experiment, repeated 3 times.
Every worker owns a different uint64 element. Volatile LLVM accesses retain the
memory traffic without introducing atomic operations, locks, or shared counters.
"""

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import statistics
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone

import llvmlite
from llvmlite import binding, ir
import numba
from numba import njit, types, uint64
from numba.extending import intrinsic
import numpy as np
import psutil

try:
    import resource
except ImportError:
    resource = None

GIT_USERNAME = "ros1nant"
STUDENT_NAME = "Ainabek Aisultan"
STUDENT_ID = "230103254"
NUM_THREADS = 4
ITERATIONS_PER_THREAD = 60_000_000
STRIDES = (1, 4, 8, 16)
MASK64 = (1 << 64) - 1
MULTIPLIER = 6364136223846793005
INSTANCE_SEED = None


def detect_cache_line_size():
    """Use the specification's sysfs -> sysctl -> 64-byte fallback."""
    path = Path("/sys/devices/system/cpu/cpu0/cache/index0/coherency_line_size")
    if path.exists():
        return int(path.read_text(encoding="utf-8").strip())
    if sys.platform == "darwin":
        try:
            return int(subprocess.check_output(
                ["sysctl", "-n", "hw.cachelinesize"], text=True).strip())
        except (OSError, subprocess.SubprocessError, ValueError):
            pass
    return 64


def windows_core_topology():
    """Read physical-core masks (one processor group, at most 64 CPUs)."""
    from ctypes import wintypes

    class Cache(ctypes.Structure):
        _fields_ = [("level", ctypes.c_ubyte), ("associativity", ctypes.c_ubyte),
                    ("line_size", ctypes.c_ushort), ("size", wintypes.DWORD),
                    ("kind", wintypes.DWORD)]

    class InfoUnion(ctypes.Union):
        _fields_ = [("cache", Cache), ("reserved", ctypes.c_ulonglong * 2)]

    class Info(ctypes.Structure):
        _fields_ = [("mask", ctypes.c_size_t), ("relationship", wintypes.DWORD),
                    ("info", InfoUnion)]

    api = ctypes.WinDLL("kernel32", use_last_error=True)
    fn = api.GetLogicalProcessorInformation
    fn.argtypes = [ctypes.POINTER(Info), ctypes.POINTER(wintypes.DWORD)]
    fn.restype = wintypes.BOOL
    length = wintypes.DWORD(0)
    fn(None, ctypes.byref(length))
    if not length.value:
        raise ctypes.WinError(ctypes.get_last_error())
    entries = (Info * (length.value // ctypes.sizeof(Info)))()
    if not fn(entries, ctypes.byref(length)):
        raise ctypes.WinError(ctypes.get_last_error())
    cores = []
    l1_lines = []
    for item in entries:
        cpus = [i for i in range(64) if item.mask & (1 << i)]
        if item.relationship == 0:  # RelationProcessorCore
            cores.append(cpus)
        elif item.relationship == 2 and item.info.cache.level == 1:
            if item.info.cache.kind in (0, 2):  # Unified or Data
                l1_lines.append(int(item.info.cache.line_size))
    return cores, sorted(set(l1_lines))


def init_system_context(git_user):
    """Task 1: bind identity, CPU model, seed, and physical-core selection."""
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", git_user):
        raise ValueError("Provide a real GitHub handle using --git-username.")
    logical_cores = os.cpu_count() or 1
    if logical_cores < NUM_THREADS:
        raise RuntimeError("At least four logical CPUs are required.")
    cpu_model = platform.processor()
    if sys.platform.startswith("linux"):
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu_model = line.split(":", 1)[1].strip()
                break
    elif sys.platform == "win32":
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
            cpu_model = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
    cpu_sig = f"{platform.machine()}::{cpu_model}::{logical_cores}"
    seed_input = f"{git_user}::{cpu_sig}"
    seed = int(hashlib.sha256(seed_input.encode()).hexdigest()[:16], 16)
    try:
        allowed = psutil.Process().cpu_affinity()
    except (AttributeError, NotImplementedError):
        allowed = list(range(logical_cores))
    core_groups, extra_line_sizes = [], []
    topology_source = "unavailable"
    if sys.platform == "win32":
        if logical_cores > 64:
            raise RuntimeError("This Windows affinity implementation supports one CPU group.")
        core_groups, extra_line_sizes = windows_core_topology()
        topology_source = "GetLogicalProcessorInformation"
    elif sys.platform.startswith("linux"):
        groups = {}
        for cpu in allowed:
            base = Path(f"/sys/devices/system/cpu/cpu{cpu}/topology")
            key = ((base / "physical_package_id").read_text().strip(),
                   (base / "core_id").read_text().strip())
            groups.setdefault(key, []).append(cpu)
        core_groups = list(groups.values())
        topology_source = "Linux sysfs physical_package_id/core_id"
    selected = [next(cpu for cpu in group if cpu in allowed)
                for group in core_groups if any(cpu in allowed for cpu in group)][:4]
    if len(selected) < 4:
        raise RuntimeError("Cannot identify four distinct available physical cores.")
    line_size = detect_cache_line_size()
    if line_size != 64 or (extra_line_sizes and extra_line_sizes != [64]):
        raise RuntimeError("The required stride layouts assume 64-byte data cache lines.")
    return {
        "student_name": STUDENT_NAME, "student_id": STUDENT_ID,
        "git_username": git_user, "instance_seed": seed,
        "seed_input": seed_input, "seed_algorithm": "SHA-256 first 16 hex digits",
        "cpu_model": cpu_model, "cpu_signature": cpu_sig,
        "logical_cores": logical_cores, "physical_cores": len(core_groups),
        "physical_core_logical_cpu_groups": core_groups,
        "allowed_logical_cpus": allowed, "selected_logical_cpus": selected,
        "topology_source": topology_source, "cache_line_bytes": line_size,
        "cache_line_source": ("sysfs" if sys.platform.startswith("linux") else
                              "sysctl" if sys.platform == "darwin" else "64-byte fallback"),
        "windows_reported_l1_data_line_bytes": extra_line_sizes,
        "os": platform.platform(), "python": sys.version,
        "numpy": np.__version__, "numba": numba.__version__,
        "llvmlite": llvmlite.__version__, "psutil": psutil.__version__,
        "gil_enabled": bool(sys._is_gil_enabled()) if hasattr(sys, "_is_gil_enabled") else True,
        "timer": time.get_clock_info("perf_counter")._asdict()
        if hasattr(time.get_clock_info("perf_counter"), "_asdict") else
        vars(time.get_clock_info("perf_counter")),
    }


class _VolatileLoad(ir.instructions.LoadInstr):
    def descr(self, buf):
        text = []
        super().descr(text)
        buf.append("".join(text).replace("load ", "load volatile ", 1))


class _VolatileStore(ir.instructions.StoreInstr):
    def descr(self, buf):
        text = []
        super().descr(text)
        buf.append("".join(text).replace("store ", "store volatile ", 1))


@intrinsic
def volatile_load_u64(typingctx, buffer, slot):
    """Emit a native volatile read of buffer[slot], preventing loop promotion."""
    if not isinstance(buffer, types.Array) or buffer.dtype != types.uint64:
        raise TypeError("Expected a uint64 NumPy array.")
    signature = types.uint64(buffer, slot)

    def codegen(context, builder, sig, args):
        array = context.make_array(sig.args[0])(context, builder, value=args[0])
        ptr = builder.gep(array.data, [args[1]])
        load = _VolatileLoad(builder.block, ptr, name="counter.load")
        load.align = 8
        builder._insert(load)
        return load
    return signature, codegen


@intrinsic
def volatile_store_u64(typingctx, buffer, slot, value):
    """Emit a native volatile write to buffer[slot]; no synchronization added."""
    if not isinstance(buffer, types.Array) or buffer.dtype != types.uint64 or value != types.uint64:
        raise TypeError("Expected uint64 array and uint64 value.")
    signature = types.void(buffer, slot, value)

    def codegen(context, builder, sig, args):
        array = context.make_array(sig.args[0])(context, builder, value=args[0])
        ptr = builder.gep(array.data, [args[1]])
        store = _VolatileStore(builder.block, args[2], ptr)
        store.align = 8
        builder._insert(store)
        return context.get_dummy_value()
    return signature, codegen


@njit(nogil=True)
def worker_strided_accumulate(buffer, slot, iters, thread_seed):
    """Task 2: each iteration reads and writes the actual buffer[slot]."""
    increment = uint64(thread_seed) | uint64(1)
    for _ in range(iters):
        value = volatile_load_u64(buffer, slot)
        value = value * uint64(MULTIPLIER) + increment
        volatile_store_u64(buffer, slot, value)


@njit(nogil=True)
def worker_private_accumulate(buffer, slot, iters, thread_seed):
    """Task 4: identical uint64 recurrence, a register loop, one final store."""
    increment = uint64(thread_seed) | uint64(1)
    accumulator = buffer[slot]
    for _ in range(iters):
        accumulator = accumulator * uint64(MULTIPLIER) + increment
    buffer[slot] = accumulator


def expected_counter(iters, seed):
    """Independent O(log n) affine-exponentiation oracle modulo 2**64."""
    acc_mul, acc_add = 1, 0
    mul, add = MULTIPLIER, seed | 1
    while iters:
        if iters & 1:
            acc_mul = (mul * acc_mul) & MASK64
            acc_add = (mul * acc_add + add) & MASK64
        mul, add = (mul * mul) & MASK64, (mul * add + add) & MASK64
        iters >>= 1
    return acc_add


def aligned_buffer(elements):
    # Align to 128 bytes as well as 64 to make sector pairs unambiguous.
    owner = np.zeros(elements * 8 + 127, dtype=np.uint8)
    offset = (-owner.ctypes.data) % 128
    array = owner[offset:offset + elements * 8].view(np.uint64)
    assert array.ctypes.data % 128 == 0
    return array


def pin_current_thread(cpu):
    """Return a restoration function; Windows pins a thread, never the process."""
    if sys.platform == "win32":
        api = ctypes.WinDLL("kernel32", use_last_error=True)
        api.GetCurrentThread.restype = ctypes.c_void_p
        api.SetThreadAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        api.SetThreadAffinityMask.restype = ctypes.c_size_t
        handle = api.GetCurrentThread()
        previous = api.SetThreadAffinityMask(handle, 1 << cpu)
        if not previous:
            raise ctypes.WinError(ctypes.get_last_error())
        return lambda: api.SetThreadAffinityMask(handle, previous)
    if hasattr(os, "sched_setaffinity"):
        previous = os.sched_getaffinity(0)
        os.sched_setaffinity(0, {cpu})
        assert os.sched_getaffinity(0) == {cpu}
        return lambda: os.sched_setaffinity(0, previous)
    raise RuntimeError("Per-thread affinity is unavailable on this OS.")


def context_switch_snapshot():
    if resource is not None:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        return {"source": "resource.getrusage(RUSAGE_SELF)",
                "voluntary": int(usage.ru_nvcsw), "involuntary": int(usage.ru_nivcsw),
                "total": int(usage.ru_nvcsw + usage.ru_nivcsw)}
    count = psutil.Process().num_ctx_switches()
    # Windows exposes a total count only. Do not mislabel it as voluntary.
    return {"source": "psutil Windows total; resource unavailable",
            "voluntary": None, "involuntary": None,
            "total": int(count.voluntary + count.involuntary)}


def run_stride_benchmark(context, stride, iters, private=False, repetition=0):
    """Task 3: four pinned workers, a synchronized start, exact telemetry."""
    buffer = aligned_buffer(NUM_THREADS * 16)
    seed = context["instance_seed"]
    seeds = [int(hashlib.sha256(f"{seed}::thread::{i}".encode()).hexdigest()[:16], 16)
             for i in range(NUM_THREADS)]
    expected = [expected_counter(iters, value) for value in seeds]
    records = [None] * NUM_THREADS
    errors = []
    timing = {}
    kernel = worker_private_accumulate if private else worker_strided_accumulate
    gate = threading.Barrier(NUM_THREADS + 1,
                             action=lambda: timing.update(start_ns=time.perf_counter_ns()))
    finished = threading.Barrier(NUM_THREADS + 1)
    release = threading.Event()

    def worker(index):
        restore = None
        try:
            cpu = context["selected_logical_cpus"][index]
            restore = pin_current_thread(cpu)
            gate.wait(timeout=30)
            start = time.perf_counter_ns()
            cpu_start = time.thread_time_ns()
            kernel(buffer, index * stride, iters, np.uint64(seeds[index]))
            cpu_end = time.thread_time_ns()
            end = time.perf_counter_ns()
            records[index] = {"thread": index, "native_thread_id": threading.get_native_id(),
                              "logical_cpu": cpu, "affinity_mask": 1 << cpu,
                              "affinity_applied": True, "seed": seeds[index],
                              "kernel_start_ns": start, "kernel_end_ns": end,
                              "thread_cpu_ns": cpu_end - cpu_start}
            # Keep the same threads alive until both counter snapshots are read.
            # Windows psutil totals sum live threads and otherwise can decrease.
            finished.wait(timeout=60)
            if not release.wait(timeout=60):
                raise RuntimeError("Telemetry collection timed out.")
        except BaseException as exc:
            errors.append(repr(exc))
            gate.abort()
            finished.abort()
            release.set()
        finally:
            if restore is not None:
                restore()

    workers = [threading.Thread(target=worker, args=(i,), name=f"cache-worker-{i}")
               for i in range(NUM_THREADS)]
    for thread in workers:
        thread.start()
    before = context_switch_snapshot()
    try:
        gate.wait(timeout=30)
        finished.wait(timeout=60)
    except threading.BrokenBarrierError:
        release.set()
        for thread in workers:
            thread.join()
        raise RuntimeError(f"Worker setup failed: {errors}")
    after = context_switch_snapshot()
    release.set()
    for thread in workers:
        thread.join()
    if errors:
        raise RuntimeError(f"Worker execution failed: {errors}")
    elapsed = max(r["kernel_end_ns"] for r in records) - timing["start_ns"]
    values = [int(buffer[i * stride]) for i in range(NUM_THREADS)]
    assert values == expected, (values, expected)
    unused = np.ones(buffer.size, dtype=bool)
    unused[[i * stride for i in range(NUM_THREADS)]] = False
    assert not np.any(buffer[unused]), "A worker modified an unassigned element."
    overlap = min(r["kernel_end_ns"] for r in records) - max(r["kernel_start_ns"] for r in records)
    address = int(buffer.ctypes.data)
    switches = {key: (after[key] - before[key] if before[key] is not None else None)
                for key in ("voluntary", "involuntary", "total")}
    switches["source"] = before["source"]
    assert all(value is None or value >= 0 for key, value in switches.items() if key != "source")
    return {
        "layout": "private" if private else f"stride_{stride}",
        "repetition": repetition, "stride_elements": stride, "spacing_bytes": stride * 8,
        "iterations_per_thread": iters, "total_updates": iters * NUM_THREADS,
        "elapsed_ns": elapsed, "aggregate_ns_per_update": elapsed / (iters * NUM_THREADS),
        "elapsed_ns_per_thread_iteration": elapsed / iters,
        "context_switches": switches, "buffer_address": address,
        "alignment_bytes": 128, "slot_indices": [i * stride for i in range(NUM_THREADS)],
        "slot_addresses": [address + 8 * i * stride for i in range(NUM_THREADS)],
        "cache_line_indices": [(address + 8 * i * stride) // 64 for i in range(NUM_THREADS)],
        "relative_cache_lines": [(8 * i * stride) // 64 for i in range(NUM_THREADS)],
        "final_values": values, "expected_values": expected, "parity_passed": True,
        "untouched_slots_passed": True, "workers": records,
        "all_four_kernel_intervals_overlap_ns": max(0, overlap),
        "sum_thread_cpu_ns": sum(r["thread_cpu_ns"] for r in records),
        "cpu_time_to_wall_ratio": sum(r["thread_cpu_ns"] for r in records) / elapsed,
    }


def audit_llvm_and_parity(runs, output):
    """Task 5: exact parity plus evidence from optimized, executable LLVM IR."""
    signature = worker_strided_accumulate.signatures[0]
    strided_ir = worker_strided_accumulate.inspect_llvm(signature)
    private_ir = worker_private_accumulate.inspect_llvm(worker_private_accumulate.signatures[0])
    # Find the native function independently of its module name (CLI or import).
    def extract(module, name):
        lines = module.splitlines()
        start = next(i for i, line in enumerate(lines) if line.startswith("define ")
                     and name in line and "cpython" not in line and "cfunc" not in line)
        end = next(i for i in range(start + 1, len(lines)) if lines[i] == "}")
        return "\n".join(lines[start:end + 1])
    native = extract(strided_ir, "worker_strided_accumulate")
    private_native = extract(private_ir, "worker_private_accumulate")
    # Full module is parsed because the native function uses module-level metadata.
    parsed = binding.parse_assembly(strided_ir)
    parsed.verify()
    name = re.search(r"@([^ (]+)\(", native).group(1)
    function = parsed.get_function(name)
    blocks = {block.name: block for block in function.blocks}
    edges = {name: re.findall(r"label %([\w.]+)", str(list(block.instructions)[-1]))
             for name, block in blocks.items()}
    loop_blocks = []
    for name, block in blocks.items():
        if "load volatile i64" not in str(block) or "store volatile i64" not in str(block):
            continue
        stack, seen = list(edges[name]), set()
        while stack:
            target = stack.pop()
            if target == name:
                loop_blocks.append(name)
                break
            if target not in seen:
                seen.add(target)
                stack.extend(edges.get(target, []))
    assert loop_blocks, "Volatile i64 load/store missing from a loop."
    assert worker_strided_accumulate.nopython_signatures
    assert all(not item.objectmode for item in worker_strided_accumulate.overloads.values())
    assert not re.search(r"\b(?:call|invoke)\b.*@(?:Py\w*|numba_gil\w*)", native)
    assert "atomicrmw" not in native and "cmpxchg" not in native
    assert "volatile" not in private_native
    assert len(re.findall(r"^\s+store i64 ", private_native, re.MULTILINE)) == 1
    assert all(r["parity_passed"] and r["untouched_slots_passed"] for r in runs)
    assert all(r["final_values"] == runs[0]["final_values"] for r in runs)
    expected_layouts = {"stride_1", "stride_4", "stride_8", "stride_16", "private"}
    assert {r["layout"] for r in runs} == expected_layouts
    for name, contents in (("worker_strided.ll", strided_ir),
                           ("worker_private.ll", private_ir),
                           ("worker_strided_native.ll", native),
                           ("worker_private_native.ll", private_native),
                           ("worker_strided.asm", worker_strided_accumulate.inspect_asm(signature)),
                           ("worker_private.asm", worker_private_accumulate.inspect_asm(
                               worker_private_accumulate.signatures[0]))):
        (output / name).write_text(contents, encoding="utf-8")
    memory_lines = [line.strip() for line in native.splitlines()
                    if "load volatile i64" in line or "store volatile i64" in line]
    return {"passed": True, "nopython": True, "nogil": True,
            "signature": str(signature), "volatile_loop_blocks": loop_blocks,
            "volatile_i64_load_sites": native.count("load volatile i64"),
            "volatile_i64_store_sites": native.count("store volatile i64"),
            "volatile_ir_lines": memory_lines,
            "no_python_api_calls_in_native_kernel": True,
            "no_atomic_rmw": True, "private_no_volatile_accesses": True,
            "private_i64_store_sites": 1,
            "llvm_module_verifier_passed": True,
            "exact_state_parity_all_layouts_and_repetitions": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--git-username", default=GIT_USERNAME)
    parser.add_argument("--iterations", type=int, default=ITERATIONS_PER_THREAD)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    if args.iterations <= 0 or args.repeats <= 0:
        parser.error("Iterations and repeats must be positive.")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    context = init_system_context(args.git_username)
    global INSTANCE_SEED
    INSTANCE_SEED = context["instance_seed"]
    print(json.dumps(context, indent=2), flush=True)
    # Compile each exact signature and fault in pages before any measured region.
    warmup = aligned_buffer(64)
    worker_strided_accumulate(warmup, 0, 1024, np.uint64(INSTANCE_SEED))
    worker_private_accumulate(warmup, 0, 1024, np.uint64(INSTANCE_SEED))
    for count in (0, 1, 2, 3, 31, 1024):
        for seed in (0, 1, MASK64, INSTANCE_SEED):
            probe = aligned_buffer(1)
            worker_strided_accumulate(probe, 0, count, np.uint64(seed))
            assert int(probe[0]) == expected_counter(count, seed)
            probe[0] = 0
            worker_private_accumulate(probe, 0, count, np.uint64(seed))
            assert int(probe[0]) == expected_counter(count, seed)
    runs = []
    # Rotate the fixed order to reduce a systematic position/thermal bias.
    layouts = [(stride, False) for stride in STRIDES] + [(8, True)]
    for repetition in range(args.repeats):
        order = layouts[repetition % 5:] + layouts[:repetition % 5]
        for stride, private in order:
            result = run_stride_benchmark(context, stride, args.iterations, private, repetition)
            runs.append(result)
            print(f"repeat={repetition + 1} {result['layout']}: {result['elapsed_ns']} ns; "
                  f"CPU/wall={result['cpu_time_to_wall_ratio']:.3f}; parity=PASS", flush=True)
    audit = audit_llvm_and_parity(runs, output)
    summary = {}
    for name in ("stride_1", "stride_4", "stride_8", "stride_16", "private"):
        samples = [r for r in runs if r["layout"] == name]
        median = statistics.median(r["elapsed_ns"] for r in samples)
        representative = next(r for r in samples if r["elapsed_ns"] == median) if len(samples) % 2 else None
        summary[name] = {"median_elapsed_ns": median,
                         "min_elapsed_ns": min(r["elapsed_ns"] for r in samples),
                         "max_elapsed_ns": max(r["elapsed_ns"] for r in samples),
                         "aggregate_ns_per_update": median / (args.iterations * NUM_THREADS),
                         "elapsed_ns_per_thread_iteration": median / args.iterations,
                         "representative_repetition": representative["repetition"] if representative else None}
    summary["slowdown_stride1_over_stride8"] = (
        summary["stride_1"]["median_elapsed_ns"] / summary["stride_8"]["median_elapsed_ns"])
    summary["ratio_stride8_over_stride16"] = (
        summary["stride_8"]["median_elapsed_ns"] / summary["stride_16"]["median_elapsed_ns"])
    full = args.iterations == ITERATIONS_PER_THREAD
    manifest = {
        "schema_version": 1, "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "context": context, "num_threads": NUM_THREADS,
        "iterations_per_thread": args.iterations, "repetitions": args.repeats,
        "full_specification_workload": full,
        "recurrence": "x_next = (x * 6364136223846793005 + (thread_seed | 1)) mod 2**64; x0=0",
        "measurement_window": "barrier release through last worker kernel return; JIT and thread creation excluded",
        "context_switch_window": "before start barrier through completion barrier; all worker threads kept alive for both snapshots; process-wide",
        "runs": runs, "summary": summary, "llvm_audit": audit,
        "limitations": (["resource is unavailable on Windows: voluntary and involuntary counts are null; total uses psutil."]
                        if resource is None else []) +
                       ["No hardware performance counters or prefetcher-control experiment; timings do not identify individual RFO events."],
        "verification_passed": bool(full and audit["passed"] and all(
            r["all_four_kernel_intervals_overlap_ns"] > 0
            and all(w["affinity_applied"] for w in r["workers"]) for r in runs)),
    }
    evidence = ["false_sharing_lab.py", "requirements.txt", "worker_strided.ll", "worker_private.ll",
                "worker_strided_native.ll", "worker_private_native.ll", "worker_strided.asm", "worker_private.asm"]
    manifest["artifact_sha256"] = {}
    for name in evidence:
        path = Path(__file__).resolve() if name == "false_sharing_lab.py" else output / name
        if path.exists():
            manifest["artifact_sha256"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
    path = output / "cache_lab_manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Manifest: {path}; verification_passed={manifest['verification_passed']}", flush=True)
    if full and not manifest["verification_passed"]:
        raise RuntimeError("The full verification did not pass; inspect the manifest.")


if __name__ == "__main__":
    main()
