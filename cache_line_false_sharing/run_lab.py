"""Run the complete experiment and refresh all analytical deliverables."""
import argparse
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--git-username", default="ros1nant")
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    root = Path(__file__).resolve().parent
    commands = [
        ["false_sharing_lab.py", "--repeats", str(args.repeats),
         "--git-username", args.git_username],
        ["generate_analysis.py"],
        ["verify_submission.py"],
    ]
    for command in commands:
        subprocess.run([sys.executable, *command], cwd=root, check=True)
    print("Full workload, current Q1-Q5 analysis, and evidence verification completed.")
    print(f"Submission directory: {root}")


if __name__ == "__main__":
    main()
