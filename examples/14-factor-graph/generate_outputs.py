"""Generate or verify outputs included by the factor-graph article."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def run_script(name: str, *arguments: str) -> str:
    completed = subprocess.run(
        [sys.executable, str(HERE / name), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def generated_outputs() -> dict[str, str]:
    unique = HERE / "boards" / "unique-4x4.sdk"
    unsat = HERE / "boards" / "unsat-4x4.sdk"
    multiple = ROOT / "fixtures" / "shidoku-4x4.sdk"
    return {
        "14-factor-graph-message.txt": run_script("message_example.py"),
        "14-factor-graph-unique-sum.txt": run_script(
            "solve.py", str(unique), "--method", "sum-product"
        ),
        "14-factor-graph-unique-max.txt": run_script(
            "solve.py", str(unique), "--method", "max-product"
        ),
        "14-factor-graph-multiple.txt": run_script(
            "solve.py", str(multiple), "--method", "sum-product"
        ),
        "14-factor-graph-unsat.txt": run_script(
            "solve.py", str(unsat), "--method", "sum-product"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

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
