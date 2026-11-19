"""Four-rank anisotropic reaction-diffusion reference solver for Google Colab."""
import hashlib
import json
import math
import re
import subprocess
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from mpi4py import MPI
from numba import cuda, float64

TILE_DIM = 16
SHARED_DIM = TILE_DIM + 2
GLOBAL_NX = GLOBAL_NY = 512
NY = NX = 256
STEPS = 400
LAMBDA_DAMP = 0.15
UP, DOWN, LEFT, RIGHT = range(4)
OPPOSITE = (DOWN, UP, RIGHT, LEFT)
MANIFEST_PATH = Path("submission_manifest.json")


def get_gpu_uuid():
    output = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=uuid", "--format=csv,noheader"],
        text=True,
    )
    return output.splitlines()[0].strip()


def derive_student_seed(github_user, gpu_uuid):
    digest = hashlib.sha256(f"{github_user.strip()}::{gpu_uuid}".encode("utf-8"))
    return int(digest.hexdigest()[:16], 16)


def init_distributed_context(github_user):
    world = MPI.COMM_WORLD
    if world.Get_size() != 4:
        raise RuntimeError(f"Expected 4 MPI ranks, got {world.Get_size()}")
    cart = world.Create_cart(dims=(2, 2), periods=(False, False), reorder=False)
    rank = cart.Get_rank()
    coords = cart.Get_coords(rank)
    neighbors = (*cart.Shift(0, 1), *cart.Shift(1, 1))
    cuda.select_device(0)
    gpu_uuid = cart.bcast(get_gpu_uuid() if rank == 0 else None, root=0)
    seed = derive_student_seed(github_user, gpu_uuid)
    return cart, coords, neighbors, gpu_uuid, seed


def initialize_subdomains(coords, neighbors, seed):
    row_rank, col_rank = coords
    dx = 1.0 / (GLOBAL_NX + 1)
    dy = 1.0 / (GLOBAL_NY + 1)
    x = (col_rank * NX + np.arange(NX + 2, dtype=np.float64))[None, :] * dx
    y = (row_rank * NY + np.arange(NY + 2, dtype=np.float64))[:, None] * dy
    kappa = 0.16 + 0.08 * np.sin(2.0 * np.pi * x) * np.cos(2.0 * np.pi * y)

    rng = np.random.default_rng(seed)
    initial = np.zeros((NY + 2, NX + 2), dtype=np.float64)
    for _ in range(3):
        center_x, center_y = rng.uniform(0.37, 0.63, size=2)
        amplitude = rng.uniform(0.65, 1.0)
        radius = 0.15
        initial += amplitude * np.exp(
            -((x - center_x) ** 2 + (y - center_y) ** 2) / (2.0 * radius**2)
        )
    source = 0.005 * np.exp(-((x - 0.50) ** 2 + (y - 0.55) ** 2) / (2.0 * 0.07**2))

    if neighbors[UP] == MPI.PROC_NULL:
        initial[0, :] = 0.0
    if neighbors[DOWN] == MPI.PROC_NULL:
        initial[-1, :] = 0.0
    if neighbors[LEFT] == MPI.PROC_NULL:
        initial[:, 0] = 0.0
    if neighbors[RIGHT] == MPI.PROC_NULL:
        initial[:, -1] = 0.0
    return initial, kappa, source, dx, dy


@cuda.jit
def pack_halos_kernel(u, up, down, left, right):
    lane = cuda.grid(1)
    ny, nx = u.shape[0] - 2, u.shape[1] - 2
    if lane < nx:
        up[lane] = u[1, lane + 1]
        down[lane] = u[ny, lane + 1]
    if lane < ny:
        left[lane] = u[lane + 1, 1]
        right[lane] = u[lane + 1, nx]


@cuda.jit
def unpack_halos_kernel(u, up, down, left, right):
    lane = cuda.grid(1)
    ny, nx = u.shape[0] - 2, u.shape[1] - 2
    if lane < nx:
        u[0, lane + 1] = up[lane]
        u[ny + 1, lane + 1] = down[lane]
    if lane < ny:
        u[lane + 1, 0] = left[lane]
        u[lane + 1, nx + 1] = right[lane]


@dataclass
class HaloBuffers:
    send_host: tuple
    recv_host: tuple
    send_device: tuple
    recv_device: tuple


def allocate_halos():
    lengths = (NX, NX, NY, NY)
    send_host = tuple(cuda.pinned_array(n, dtype=np.float64) for n in lengths)
    recv_host = tuple(cuda.pinned_array(n, dtype=np.float64) for n in lengths)
    for buffer in recv_host:
        # A receive from MPI.PROC_NULL leaves its buffer unchanged.
        buffer.fill(0.0)
    send_device = tuple(cuda.device_array(n, dtype=np.float64) for n in lengths)
    recv_device = tuple(cuda.device_array(n, dtype=np.float64) for n in lengths)
    return HaloBuffers(send_host, recv_host, send_device, recv_device)


def exchange_halos_async(cart, neighbors, u, buffers, stream_boundary, start, end):
    """Stage outgoing halos and post receives before sends. Return pending requests."""
    blocks = (max(NX, NY) + 127) // 128
    start.record(stream_boundary)
    pack_halos_kernel[blocks, 128, stream_boundary](u, *buffers.send_device)
    for device, host, neighbor in zip(buffers.send_device, buffers.send_host, neighbors):
        if neighbor != MPI.PROC_NULL:
            device.copy_to_host(host, stream=stream_boundary)
    end.record(stream_boundary)
    stream_boundary.synchronize()

    requests = [
        cart.Irecv(buffers.recv_host[d], source=neighbor, tag=OPPOSITE[d])
        for d, neighbor in enumerate(neighbors)
    ]
    requests.extend(
        cart.Isend(buffers.send_host[d], dest=neighbor, tag=d)
        for d, neighbor in enumerate(neighbors)
    )
    return requests


def receive_halos(u, buffers, stream_boundary):
    for device, host in zip(buffers.recv_device, buffers.recv_host):
        device.copy_to_device(host, stream=stream_boundary)
    blocks = (max(NX, NY) + 127) // 128
    unpack_halos_kernel[blocks, 128, stream_boundary](u, *buffers.recv_device)


@cuda.jit
def tiled_stencil_kernel(u, out, kappa, source, dt, inv_dx2, inv_dy2,
                         r_start, r_end, c_start, c_end):
    """Update a box with exclusive end indices."""
    smem = cuda.shared.array((SHARED_DIM, SHARED_DIM), dtype=float64)
    tx, ty = cuda.threadIdx.x, cuda.threadIdx.y
    sx, sy = tx + 1, ty + 1
    r = r_start + cuda.blockIdx.y * TILE_DIM + ty
    c = c_start + cuda.blockIdx.x * TILE_DIM + tx
    active = r < r_end and c < c_end

    if active:
        smem[sy, sx] = u[r, c]
        if tx == 0:
            smem[sy, sx - 1] = u[r, c - 1]
        if tx == TILE_DIM - 1 or c == c_end - 1:
            smem[sy, sx + 1] = u[r, c + 1]
        if ty == 0:
            smem[sy - 1, sx] = u[r - 1, c]
        if ty == TILE_DIM - 1 or r == r_end - 1:
            smem[sy + 1, sx] = u[r + 1, c]

    cuda.syncthreads()

    if active:
        center = smem[sy, sx]
        k_center = kappa[r, c]
        k_east = 0.5 * (k_center + kappa[r, c + 1])
        k_west = 0.5 * (k_center + kappa[r, c - 1])
        k_south = 0.5 * (k_center + kappa[r + 1, c])
        k_north = 0.5 * (k_center + kappa[r - 1, c])
        flux_x = (k_east * (smem[sy, sx + 1] - center)
                  - k_west * (center - smem[sy, sx - 1])) * inv_dx2
        flux_y = (k_south * (smem[sy + 1, sx] - center)
                  - k_north * (center - smem[sy - 1, sx])) * inv_dy2
        damping = LAMBDA_DAMP * center * center * center
        out[r, c] = center + dt * (flux_x + flux_y - damping + source[r, c])


def launch_box(stencil_args, box, stream):
    r_start, r_end, c_start, c_end = box
    blocks = (
        (c_end - c_start + TILE_DIM - 1) // TILE_DIM,
        (r_end - r_start + TILE_DIM - 1) // TILE_DIM,
    )
    tiled_stencil_kernel[blocks, (TILE_DIM, TILE_DIM), stream](*stencil_args, *box)


@dataclass
class StepEvents:
    pack_start: object
    pack_end: object
    interior_start: object
    interior_end: object
    ring_start: object
    ring_end: object


def launch_interior(stencil_args, stream_interior, events):
    events.interior_start.record(stream_interior)
    launch_box(stencil_args, (2, NY, 2, NX), stream_interior)
    events.interior_end.record(stream_interior)


def finish_boundary(stencil_args, buffers, stream_boundary, events):
    events.ring_start.record(stream_boundary)
    receive_halos(stencil_args[0], buffers, stream_boundary)
    boxes = (
        (1, 2, 1, NX + 1),
        (NY, NY + 1, 1, NX + 1),
        (2, NY, 1, 2),
        (2, NY, NX, NX + 1),
    )
    for box in boxes:
        launch_box(stencil_args, box, stream_boundary)
    events.ring_end.record(stream_boundary)


def step_overlapped(cart, neighbors, stencil_args, buffers, stream_boundary,
                    stream_interior, events):
    pending = exchange_halos_async(
        cart, neighbors, stencil_args[0], buffers, stream_boundary,
        events.pack_start, events.pack_end,
    )
    launch_interior(stencil_args, stream_interior, events)
    MPI.Request.Waitall(pending)
    finish_boundary(stencil_args, buffers, stream_boundary, events)
    # Complete both writers before swapping the current and next fields.
    stream_boundary.synchronize()
    stream_interior.synchronize()


def step_serialized(cart, neighbors, stencil_args, buffers, stream_boundary,
                    stream_interior, events):
    pending = exchange_halos_async(
        cart, neighbors, stencil_args[0], buffers, stream_boundary,
        events.pack_start, events.pack_end,
    )
    MPI.Request.Waitall(pending)
    finish_boundary(stencil_args, buffers, stream_boundary, events)
    stream_boundary.synchronize()
    launch_interior(stencil_args, stream_interior, events)
    stream_interior.synchronize()


def record_diagnostics(cart, current, previous, step, dx, dy):
    owned = current.copy_to_host()[1:-1, 1:-1]
    residual_sq = 0.0
    if previous is not None:
        old_owned = previous.copy_to_host()[1:-1, 1:-1]
        diff = owned - old_owned
        residual_sq = np.sum(diff * diff, dtype=np.float64)
    local = np.array([np.sum(owned, dtype=np.float64) * dx * dy, residual_sq])
    total = np.empty_like(local)
    cart.Allreduce(local, total, op=MPI.SUM)
    entry = {"step": step, "energy": float(total[0]), "l2_residual": math.sqrt(total[1])}
    if cart.Get_rank() == 0:
        print(f"step={step:3d}  energy={entry['energy']:.16e}  "
              f"L2 residual={entry['l2_residual']:.16e}", flush=True)
    return entry


def benchmark_mode(cart, neighbors, initial, material_args, buffers,
                   stream_boundary, stream_interior, dx, dy, step_function):
    current = cuda.to_device(initial)
    next_field = cuda.to_device(initial)
    events = StepEvents(*(cuda.event(timing=True) for _ in range(6)))
    if cart.Get_rank() == 0:
        print(f"\nMode {step_function.__name__}", flush=True)
    history = [record_diagnostics(cart, current, None, 0, dx, dy)]
    interior_ms = 0.0
    boundary_ms = 0.0
    cart.Barrier()
    started = MPI.Wtime()
    for step in range(1, STEPS + 1):
        stencil_args = (current, next_field, *material_args)
        step_function(cart, neighbors, stencil_args, buffers,
                      stream_boundary, stream_interior, events)
        interior_ms += cuda.event_elapsed_time(events.interior_start, events.interior_end)
        boundary_ms += cuda.event_elapsed_time(events.pack_start, events.pack_end)
        boundary_ms += cuda.event_elapsed_time(events.ring_start, events.ring_end)
        previous, current, next_field = current, next_field, current
        if step % 100 == 0:
            history.append(record_diagnostics(cart, current, previous, step, dx, dy))
    wall_ms = (MPI.Wtime() - started) * 1000.0
    maxima = np.empty(3, dtype=np.float64)
    cart.Allreduce(np.array([wall_ms, interior_ms, boundary_ms]),
                   maxima, op=MPI.MAX)
    timings = {
        "wall_ms": float(maxima[0]),
        "interior_cuda_ms": float(maxima[1]),
        "boundary_cuda_ms": float(maxima[2]),
    }
    return current.copy_to_host()[1:-1, 1:-1].copy(), history, timings


def audit_ptx():
    assembly = tiled_stencil_kernel.inspect_asm()
    if len(assembly) != 1:
        raise RuntimeError(f"Expected one stencil specialization, found {len(assembly)}")
    ptx = next(iter(assembly.values()))
    counts = {}
    for mnemonic in ("st.shared.f64", "ld.shared.f64", "bar.sync"):
        pattern = rf"(?m)^\s*(?:@!?%\w+\s+)?{re.escape(mnemonic)}(?=\s)"
        counts[mnemonic] = len(re.findall(pattern, ptx))
    return counts, all(counts.values())


def run_solver(github_user):
    cart, coords, neighbors, gpu_uuid, seed = init_distributed_context(github_user)
    rank = cart.Get_rank()
    if rank == 0:
        MANIFEST_PATH.unlink(missing_ok=True)
        print(f"GITHUB_USERNAME={github_user}  GPU_UUID={gpu_uuid}  INSTANCE_SEED={seed}", flush=True)
        print(f"mpi_ranks={cart.Get_size()}  cart_dims=2x2  MPI.PROC_NULL={MPI.PROC_NULL}", flush=True)

    initial, kappa, source, dx, dy = initialize_subdomains(coords, neighbors, seed)
    # Include physical edge values because they participate in face conductivities.
    kappa_max = cart.allreduce(float(kappa.max()), op=MPI.MAX)
    dt_max = dx * dx / (4.0 * kappa_max)
    dt = 0.8 * dt_max
    print(f"rank={rank}  coords={tuple(coords)}  neighbors (U,D,L,R)={neighbors}  "
          f"local_shape={initial.shape}", flush=True)
    if rank == 0:
        packed = NY * initial.itemsize
        bounding = ((NY - 1) * initial.shape[1] + 1) * initial.itemsize
        print(f"column stride={initial.strides[0]} B  packed={packed} B  "
              f"bounding={bounding} B  extra={bounding - packed} B per column", flush=True)
        print(f"kappa_max={kappa_max:.16e}  dx={dx:.16e}  "
              f"dt_max={dt_max:.16e}  dt={dt:.16e}", flush=True)
        print("Wall time includes 400 steps with event collection and diagnostics. "
              "CUDA event times sum per-stream intervals.", flush=True)

    material_args = (cuda.to_device(kappa), cuda.to_device(source),
                     dt, 1.0 / dx**2, 1.0 / dy**2)
    buffers = allocate_halos()
    stream_boundary = cuda.stream()
    stream_interior = cuda.stream()

    # Compile all kernels and initialize both streams before the timed modes.
    warm_args = (cuda.to_device(initial), cuda.to_device(initial), *material_args)
    warm_events = StepEvents(*(cuda.event(timing=True) for _ in range(6)))
    step_overlapped(cart, neighbors, warm_args, buffers, stream_boundary,
                    stream_interior, warm_events)
    del warm_args, warm_events

    mode_args = (cart, neighbors, initial, material_args, buffers,
                 stream_boundary, stream_interior, dx, dy)
    serial, serial_history, serial_times = benchmark_mode(*mode_args, step_serialized)
    overlap, overlap_history, overlap_times = benchmark_mode(*mode_args, step_overlapped)
    finite = cart.allreduce(bool(np.isfinite(serial).all() and np.isfinite(overlap).all()),
                            op=MPI.LAND)
    local_max = float(np.max(np.abs(serial - overlap))) if finite else math.inf
    parity_max_diff = cart.allreduce(local_max, op=MPI.MAX)

    if rank == 0:
        ptx_counts, ptx_passed = audit_ptx()
        speedup = serial_times["wall_ms"] / overlap_times["wall_ms"]
        print(f"PTX counts: {ptx_counts}  ptx_audit_passed={ptx_passed}", flush=True)
        print(f"serialized_ms={serial_times['wall_ms']:.3f}  "
              f"overlapped_ms={overlap_times['wall_ms']:.3f}  speedup={speedup:.5f}x", flush=True)
        print(f"CUDA events (max rank, ms): serialized={serial_times}  "
              f"overlapped={overlap_times}", flush=True)
        print(f"parity_max_diff={parity_max_diff:.16e}", flush=True)
        if not ptx_passed or not parity_max_diff < 1e-12:
            raise RuntimeError("Verification failed: see the PTX counts and parity above.")

        manifest = {
            "github_username": github_user,
            "gpu_uuid": gpu_uuid,
            "instance_seed": seed,
            "mpi_ranks": cart.Get_size(),
            "cart_dims": [2, 2],
            "steps": STEPS,
            "kappa_max": kappa_max,
            "dx": dx,
            "dy": dy,
            "dt": dt,
            "dt_max": dt_max,
            "ptx_instruction_counts": ptx_counts,
            "ptx_audit_passed": ptx_passed,
            "parity_max_diff": parity_max_diff,
            "serialized_ms": serial_times["wall_ms"],
            "overlapped_ms": overlap_times["wall_ms"],
            "cuda_event_timings_ms": {
                mode: {key: value for key, value in timings.items() if key != "wall_ms"}
                for mode, timings in (("serialized", serial_times), ("overlapped", overlap_times))
            },
            "energy_and_residual": {"serialized": serial_history, "overlapped": overlap_history},
        }
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n",
                                 encoding="utf-8")
        print(f"Wrote {MANIFEST_PATH}", flush=True)
    cart.Barrier()
    cart.Free()


if __name__ == "__main__":
    try:
        if (len(sys.argv) != 2 or not sys.argv[1].strip()
                or sys.argv[1] == "REPLACE_WITH_YOUR_GITHUB_USERNAME"):
            raise SystemExit("Usage: distributed_cuda_solver.py YOUR_GITHUB_USERNAME")
        run_solver(sys.argv[1].strip())
    except Exception:
        traceback.print_exc()
        MPI.COMM_WORLD.Abort(1)
