# Parallel Computing Laboratory Submissions

**Student:** Ainabek Aisultan  
**Student ID:** 230103254  
**GitHub:** ros1nant

## Cache Line and False Sharing Mechanics

Open [cache_line_false_sharing_lab.ipynb](cache_line_false_sharing_lab.ipynb)
in Jupyter, or use the Colab link below. Run every cell from top to bottom.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ros1nant/mpi-cuda-stencil-ros1nant_230103254/blob/main/cache_line_false_sharing_lab.ipynb)

**The benchmark requires at least four available physical CPU cores.** The notebook
checks this before running. Some hosted notebook runtimes provide fewer cores;
use a local Jupyter runtime or a machine with four available physical cores if
that check fails. A GPU is not required for this CPU experiment.

For a terminal run:

```sh
git clone https://github.com/ros1nant/mpi-cuda-stencil-ros1nant_230103254.git
cd mpi-cuda-stencil-ros1nant_230103254/cache_line_false_sharing
python -m pip install -r requirements.txt
python run_lab.py
```

The runner performs the full benchmark, regenerates the English Q1-Q5 report
from the new measurements, and verifies the resulting evidence. See the
[lab instructions](cache_line_false_sharing/README.md) and
[current analysis](cache_line_false_sharing/ANALYSIS.md).

The included measurements are from the previously completed Windows host run.
Running the notebook replaces them with measurements from your runtime. It does
not automatically commit or push generated files.

This existing repository is used at the student's request. The specification's
suggested separate repository name is `cache-line-false-sharing-ros1nant`.

## MPI and CUDA Stencil Laboratory

The earlier lab remains available in
[mpi_cuda_stencil_lab.ipynb](mpi_cuda_stencil_lab.ipynb), with its solver in
[distributed_cuda_solver.py](distributed_cuda_solver.py) and recorded telemetry
in [submission_manifest.json](submission_manifest.json).
