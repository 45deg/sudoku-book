from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

COMMANDS = {
    "13-iterative-projection-small.txt": [str(HERE / "small_projection.py")],
    "13-iterative-projection-unique.txt": [
        str(HERE / "solve.py"),
        str(HERE / "boards" / "unique-4x4.sdk"),
        "--seed",
        "0",
        "--max-iterations",
        "2000",
    ],
    "13-iterative-projection-unknown.txt": [
        str(HERE / "solve.py"),
        str(HERE / "boards" / "unsat-4x4.sdk"),
        "--seed",
        "0",
        "--max-iterations",
        "2000",
    ],
    "13-iterative-projection-multiple.txt": [
        str(HERE / "solve.py"),
        str(ROOT / "fixtures" / "shidoku-4x4.sdk"),
        "--seed",
        "2",
        "--max-iterations",
        "2000",
    ],
}


def generated_outputs() -> dict[str, str]:
    generated = {}
    for filename, arguments in COMMANDS.items():
        completed = subprocess.run(
            [sys.executable, *arguments],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        generated[filename] = completed.stdout
    return generated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    stale = []
    for filename, expected in generated_outputs().items():
        path = ROOT / "outputs" / filename
        if args.check:
            current = path.read_text() if path.exists() else ""
            if current != expected:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(expected)
    if stale:
        raise SystemExit("stale generated outputs: " + ", ".join(stale))


if __name__ == "__main__":
    main()
