"""Run a recorded exploratory batch with one networkless Docker container per trial.

This is an execution wrapper, not a replacement for scripts/run_trials.py. The task
multiset and shuffle match that script's default order for the same n and seed.
Each trial gets a fresh /runs mount so labagent cannot inspect prior workspaces.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = ["T1_disk_cleanup", "T2_config_fix", "T3_log_pressure"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True)
    ap.add_argument("--arm", choices=["A_panel", "B_gate"], required=True)
    ap.add_argument("--stratum", choices=["S", "E"], required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--bridge-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    order = [TASKS[i % len(TASKS)] for i in range(args.n)]
    random.Random(args.seed).shuffle(order)
    schedule = {"phase": args.phase, "arm": args.arm, "stratum": args.stratum,
                "model": args.model, "seed": args.seed, "tasks": order,
                "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "isolation": "one networkless Docker container and fresh /runs mount per trial"}
    (out / "schedule.json").write_text(json.dumps(schedule, indent=2) + "\n")
    for index, task in enumerate(order):
        trial_dir = out / f"trial_{index:02d}"
        trial_dir.mkdir(mode=0o755)
        q = shlex.quote
        cmd = [
            "docker", "run", "--rm", "--network", "none", "--cap-drop", "ALL",
            "--cap-add", "CHOWN", "--cap-add", "DAC_OVERRIDE", "--cap-add", "FOWNER",
            "--cap-add", "SETUID", "--cap-add", "SETGID",
            "--security-opt", "no-new-privileges:true",
            "-e", "APPROVAL_GATE_BRIDGE_DIR=/bridge",
            "-v", f"{args.bridge_dir.resolve()}:/bridge",
            "-v", f"{trial_dir}:/runs",
            "-v", f"{ROOT}:/root/source:ro",
            "docker-verify", "sh", "-c",
            "chmod 700 /lab; cp -a /root/source /root/lab; "
            "python3 /root/lab/infra/bridge_container.py & sleep 1; "
            "python3 /root/lab/scripts/run_trials.py "
            f"--phase {q(args.phase)} --arm {q(args.arm)} --backend openai_compat "
            f"--model {q(args.model)} --base-url http://127.0.0.1:8000 "
            f"--stratum {q(args.stratum)} --task {q(task)} --n 1 --seed {args.seed} "
            "--mode enforced --out /runs/trial.jsonl --runs-dir /runs",
        ]
        with (trial_dir / "container.log").open("w") as log:
            result = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
        (trial_dir / "container_exit.txt").write_text(str(result.returncode) + "\n")
        print(f"trial={index} task={task} container_exit={result.returncode}", flush=True)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
