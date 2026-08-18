"""Generate or verify the outputs included by the Prolog article."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOLVER = Path(__file__).with_name("solve.pl")


def run_solver(fixture: str, limit: int) -> str:
    try:
        completed = subprocess.run(
            [
                "swipl",
                "-q",
                "-s",
                str(SOLVER),
                "--",
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
            "error: SWI-Prolog executable 'swipl' was not found; "
            "install SWI-Prolog and ensure swipl is on PATH"
        ) from None
    return completed.stdout


def generated_outputs() -> dict[str, str]:
    return {
        "02-prolog-standard.txt": run_solver("standard-9x9.sdk", 2),
        "02-prolog-unsat.txt": run_solver("unsat-9x9.sdk", 2),
        "02-prolog-multiple.txt": run_solver("multiple-9x9.sdk", 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if shutil.which("swipl") is None:
        raise SystemExit(
            "error: SWI-Prolog executable 'swipl' was not found; "
            "install SWI-Prolog and ensure swipl is on PATH"
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
