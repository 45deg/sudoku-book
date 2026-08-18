"""Generate or verify the outputs included by the constraint-programming article."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOLVER = Path(__file__).with_name("solve.py")


def run_solver(fixture: str, limit: int) -> str:
    try:
        completed = subprocess.run(
            [
                sys.executable,
                str(SOLVER),
                str(ROOT / "fixtures" / fixture),
                "--limit",
                str(limit),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise SystemExit(
            "error: Python executable used to launch MiniZinc was not found"
        ) from None
    return completed.stdout


def generated_outputs() -> dict[str, str]:
    return {
        "04-constraint-programming-standard.txt": run_solver("standard-9x9.sdk", 2),
        "04-constraint-programming-unsat.txt": run_solver("unsat-9x9.sdk", 1),
        "04-constraint-programming-multiple.txt": run_solver("multiple-9x9.sdk", 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if shutil.which("minizinc") is None:
        raise SystemExit(
            "error: MiniZinc executable 'minizinc' was not found; "
            "install MiniZinc and ensure minizinc is on PATH"
        )

    output_dir = ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)
    stale: list[str] = []
    for name, expected in generated_outputs().items():
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
