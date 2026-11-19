"""Verify the current full-run artifacts without executing the benchmark."""
import hashlib
import json
from pathlib import Path
import re
import statistics

from llvmlite import binding
from false_sharing_lab import expected_counter


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "cache_lab_manifest.json").read_text(encoding="utf-8"))
    assert manifest["verification_passed"] is True
    assert manifest["full_specification_workload"] is True
    assert manifest["num_threads"] == 4
    assert manifest["iterations_per_thread"] == 60_000_000
    assert manifest["repetitions"] >= 1
    ctx = manifest["context"]
    assert ctx["student_name"] == "Ainabek Aisultan"
    assert ctx["student_id"] == "230103254"
    assert ctx["seed_input"] == f"{ctx['git_username']}::{ctx['cpu_signature']}"
    assert int(hashlib.sha256(ctx["seed_input"].encode()).hexdigest()[:16], 16) == ctx["instance_seed"]
    selected = ctx["selected_logical_cpus"]
    assert len(set(selected)) == 4
    group_ids = [next(i for i, group in enumerate(ctx["physical_core_logical_cpu_groups"])
                      if cpu in group) for cpu in selected]
    assert len(set(group_ids)) == 4
    for name, expected in manifest["artifact_sha256"].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
    expected_layouts = {"stride_1", "stride_4", "stride_8", "stride_16", "private"}
    runs = manifest["runs"]
    assert {run["layout"] for run in runs} == expected_layouts
    expected_values = runs[0]["final_values"]
    for run in runs:
        assert run["iterations_per_thread"] == 60_000_000
        assert run["total_updates"] == 240_000_000
        assert run["buffer_address"] % 128 == 0
        assert run["elapsed_ns"] > 0
        assert run["all_four_kernel_intervals_overlap_ns"] > 0
        assert run["parity_passed"] and run["untouched_slots_passed"]
        assert run["final_values"] == run["expected_values"] == expected_values
        assert len(run["workers"]) == 4
        for index, (worker, value) in enumerate(zip(run["workers"], run["final_values"])):
            seed = int(hashlib.sha256(
                f"{ctx['instance_seed']}::thread::{index}".encode()).hexdigest()[:16], 16)
            assert worker["seed"] == seed
            assert value == expected_counter(60_000_000, seed)
            assert worker["affinity_applied"]
            assert worker["logical_cpu"] == selected[index]
        for key in ("total", "voluntary", "involuntary"):
            value = run["context_switches"][key]
            assert value is None or value >= 0
        mapping = {"stride_1": [0, 0, 0, 0], "stride_4": [0, 0, 1, 1],
                   "stride_8": [0, 1, 2, 3], "stride_16": [0, 2, 4, 6],
                   "private": [0, 1, 2, 3]}
        assert run["relative_cache_lines"] == mapping[run["layout"]]
    for key in expected_layouts:
        samples = [run for run in runs if run["layout"] == key]
        assert len(samples) == manifest["repetitions"]
        assert sorted(run["repetition"] for run in samples) == list(range(manifest["repetitions"]))
        median = statistics.median(run["elapsed_ns"] for run in samples)
        assert manifest["summary"][key]["median_elapsed_ns"] == median
        assert manifest["summary"][key]["aggregate_ns_per_update"] == median / 240_000_000
    for name in ("worker_strided.ll", "worker_private.ll"):
        module = binding.parse_assembly((root / name).read_text(encoding="utf-8"))
        module.verify()
    native = (root / "worker_strided_native.ll").read_text(encoding="utf-8")
    private = (root / "worker_private_native.ll").read_text(encoding="utf-8")
    audit = manifest["llvm_audit"]
    assert audit["passed"] and audit["volatile_loop_blocks"]
    assert native.count("load volatile i64") == audit["volatile_i64_load_sites"] > 0
    assert native.count("store volatile i64") == audit["volatile_i64_store_sites"] > 0
    assert len(re.findall(r"^\s+store i64 ", private, re.MULTILINE)) == 1
    assert "volatile" not in private
    analysis = (root / "ANALYSIS.md").read_text(encoding="utf-8")
    for index in range(1, 6):
        assert f"## Q{index}." in analysis
    assert manifest["created_at_utc"] in analysis
    assert str(ctx["instance_seed"]) in analysis
    for key in expected_layouts:
        assert f"{manifest['summary'][key]['median_elapsed_ns']:,}" in analysis
    for value in expected_values:
        assert str(value) in analysis
    print("PASS: workload, identity, physical-core pinning, hashes, exact parity, LLVM, and current Q1-Q5.")
    if any(run["context_switches"]["voluntary"] is None for run in runs):
        print("Platform limitation recorded: separate context-switch categories are unavailable.")


if __name__ == "__main__":
    main()
