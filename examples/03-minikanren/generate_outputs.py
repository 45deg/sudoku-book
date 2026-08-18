"""Generate or verify the outputs included by the miniKanren article."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from relation_demo import append_examples, choice_example
from solve import ROOT, describe_result, solve

COMMON = ROOT / "examples" / "common"
sys.path.insert(0, str(COMMON))

from sudoku import load_board  # noqa: E402


def append_output() -> str:
    joined, splits = append_examples()
    lines = [f"join: {joined[0]}", "splits:"]
    lines.extend(f"  {left} + {right}" for left, right in splits)
    return "\n".join(lines) + "\n"


def generated_outputs() -> dict[str, str]:
    example = ROOT / "examples" / "03-minikanren"
    unique = load_board(example / "puzzles" / "unique-4x4.sdk")
    unsat = load_board(example / "puzzles" / "unsat-4x4.sdk")
    multiple = load_board(ROOT / "fixtures" / "shidoku-4x4.sdk")
    return {
        "03-minikanren-appendo.txt": append_output(),
        "03-minikanren-choice.txt": f"choices: {choice_example()}\n",
        "03-minikanren-unique.txt": describe_result(solve(unique, 2), unique, 2) + "\n",
        "03-minikanren-unsat.txt": describe_result(solve(unsat, 2), unsat, 2) + "\n",
        "03-minikanren-multiple.txt": describe_result(solve(multiple, 2), multiple, 2) + "\n",
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
