"""Generate or verify the outputs included by the backtracking article."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "01-backtracking"
COMMON = ROOT / "examples" / "common"
sys.path[:0] = [str(EXAMPLE), str(COMMON)]

from solve import describe_result, solve_naive, solve_propagating  # noqa: E402
from sudoku import load_board  # noqa: E402


def generated_outputs() -> dict[str, str]:
    standard = load_board(ROOT / "fixtures" / "standard-9x9.sdk")
    unsat = load_board(ROOT / "fixtures" / "unsat-9x9.sdk")
    multiple = load_board(ROOT / "fixtures" / "multiple-9x9.sdk")

    standard_text = "\n\n".join(
        [
            describe_result("naive", solve_naive(standard, limit=1), standard, 1),
            describe_result("propagate", solve_propagating(standard, limit=1), standard, 1),
        ]
    )
    return {
        "01-backtracking-standard.txt": standard_text + "\n",
        "01-backtracking-unsat.txt": describe_result(
            "propagate", solve_propagating(unsat, limit=2), unsat, 2
        )
        + "\n",
        "01-backtracking-multiple.txt": describe_result(
            "propagate", solve_propagating(multiple, limit=2), multiple, 2
        )
        + "\n",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    output_dir = ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)
    stale = []
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
