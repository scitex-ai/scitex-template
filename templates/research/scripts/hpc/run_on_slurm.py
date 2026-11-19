#!/usr/bin/env python3
# File: scripts/hpc/run_on_slurm.py
# stx-allow-file: STX-S001  (reason: job orchestration, not an analysis step;
#   the analysis step it dispatches runs under @scitex_session.session remotely)

"""Run the compute-heavy step on a Slurm cluster through scitex-hpc (`make hpc`).

1. sync the project to <REMOTE_BASE>/<project> (scitex_hpc.sync; never _out/)
2. create/refresh the remote venv from requirements.txt on the login node
3. run CONFIG.HPC.STEP with srun (scitex_hpc.srun, blocking)
4. pull the step's <script>_out/ back and re-create the data/ links

PROVENANCE GAP (known, reported upstream): the remote run cannot reach this
project's clew store, so it runs with SCITEX_CLEW_CAPTURE=0 and its outputs
come back WITHOUT a recorded run. `make verify` then reports them as having
no lineage (exit 13 under --strict) -- the honest answer -- until clew can
import a remote run. Re-run `make train` locally to restore full lineage.
"""

import argparse
import shlex
import subprocess
from pathlib import Path

import scitex_hpc
import scitex_io as sio

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_hpc_config():
    return sio.load(str(PROJECT_ROOT / "config" / "HPC.yaml"))


def run(cmd):
    print("+", " ".join(shlex.quote(c) for c in cmd), flush=True)
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", required=True)
    parser.add_argument("--account", required=True)
    parser.add_argument("--partition", required=True)
    args = parser.parse_args()

    cfg = load_hpc_config()
    project = PROJECT_ROOT.name
    remote_root = f"{cfg['REMOTE_BASE']}/{project}"
    venv = cfg["REMOTE_VENV"]
    step = cfg["STEP"]
    out_dir = str(Path(step).with_suffix("")) + "_out"

    job = scitex_hpc.JobConfig(
        project=project,
        command=(f"cd {remote_root} && SCITEX_CLEW_CAPTURE=0 {venv}/bin/python {step}"),
        host=args.host,
        partition=args.partition,
        account=args.account,
        cpus=cfg["CPUS"],
        mem=cfg["MEM"],
        time=cfg["TIME"],
        job_name=cfg["JOB_NAME"],
        remote_base=cfg["REMOTE_BASE"],
    )

    scitex_hpc.sync(job, local_path=str(PROJECT_ROOT))
    # data/mnist/*.npy are symlinks into 01_fetch_mnist_out/, which sync skips:
    # send the resolved arrays the step reads.
    run(
        [
            "rsync",
            "-azL",
            f"{PROJECT_ROOT}/data/mnist/",
            f"{args.host}:{remote_root}/data/mnist/",
        ]
    )
    setup_env = (
        f"bash -lc 'uv venv --allow-existing --python 3.12 {venv} && "
        f"uv pip install -q --python {venv}/bin/python -r {remote_root}/requirements.txt'"
    )
    run(["ssh", args.host, setup_env])

    code = scitex_hpc.srun(job)
    if code != 0:
        raise SystemExit(f"remote step failed with exit code {code}")

    run(
        [
            "rsync",
            "-az",
            f"{args.host}:{remote_root}/{out_dir}/",
            f"{PROJECT_ROOT}/{out_dir}/",
        ]
    )
    print(
        "\nPulled the remote outputs. They have NO recorded run in this project's "
        "clew store (see the docstring): `make verify` will say so. Run "
        "`make train` locally to restore full lineage."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# EOF
