"""Generate or verify outputs included by the model-checking article."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from solve import find_nuxmv

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def run_script(name: str, nuxmv: str, *arguments: str) -> str:
    completed = subprocess.run(
        [sys.executable, str(HERE / name), *arguments, "--nuxmv", nuxmv],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def generated_outputs(nuxmv: str) -> dict[str, str]:
    return {
        "11-model-checking-small-example.txt": run_script("small_example.py", nuxmv),
        "11-model-checking-standard.txt": run_script(
            "solve.py",
            nuxmv,
            str(ROOT / "fixtures" / "standard-9x9.sdk"),
            "--limit",
            "2",
        ),
        "11-model-checking-unsat.txt": run_script(
            "solve.py",
            nuxmv,
            str(ROOT / "fixtures" / "unsat-9x9.sdk"),
            "--limit",
            "2",
        ),
        "11-model-checking-multiple.txt": run_script(
            "solve.py",
            nuxmv,
            str(ROOT / "fixtures" / "multiple-9x9.sdk"),
            "--limit",
            "2",
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--nuxmv")
    args = parser.parse_args()
    nuxmv = find_nuxmv(args.nuxmv)

    output_dir = ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)
    stale: list[str] = []
    for name, expected in generated_outputs(nuxmv).items():
        path = output_dir / name
        if args.check:
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != expected:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(expected, encoding="utf-8")
    if stale:
        raise SystemExit("stale generated outputs: " + ", ".join(stale))


if __name__ == "__main__":
    main()
