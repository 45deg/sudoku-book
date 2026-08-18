"""Generate or verify outputs included by the integer-programming article."""

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
    return {
        "08-integer-programming-small-example.txt": run_script("small_example.py"),
        "08-integer-programming-standard.txt": run_script(
            "solve.py", str(ROOT / "fixtures" / "standard-9x9.sdk"), "--limit", "2"
        ),
        "08-integer-programming-unsat.txt": run_script(
            "solve.py", str(ROOT / "fixtures" / "unsat-9x9.sdk"), "--limit", "1"
        ),
        "08-integer-programming-multiple.txt": run_script(
            "solve.py", str(ROOT / "fixtures" / "multiple-9x9.sdk"), "--limit", "2"
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
