"""Generate or verify outputs included by the exact-cover article."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def run(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return completed.stdout


def generated_outputs() -> dict[str, str]:
    return {
        "05-exact-cover-toy.txt": run([sys.executable, str(HERE / "toy.py")]),
        "05-exact-cover-standard.txt": run(
            [sys.executable, str(HERE / "solve.py"), str(ROOT / "fixtures/standard-9x9.sdk"), "--limit", "2"]
        ),
        "05-exact-cover-unsat.txt": run(
            [sys.executable, str(HERE / "solve.py"), str(ROOT / "fixtures/unsat-9x9.sdk"), "--limit", "2"]
        ),
        "05-exact-cover-multiple.txt": run(
            [sys.executable, str(HERE / "solve.py"), str(ROOT / "fixtures/multiple-9x9.sdk"), "--limit", "2"]
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

