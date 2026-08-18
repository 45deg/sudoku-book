"""Generate or verify the outputs included by the SAT article."""

from __future__ import annotations

import argparse
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

from proposition_demo import main as proposition_main
from solve import ROOT, describe_result, solve

COMMON = ROOT / "examples" / "common"
sys.path.insert(0, str(COMMON))

from sudoku import load_board  # noqa: E402


def proposition_output() -> str:
    output = io.StringIO()
    with redirect_stdout(output):
        proposition_main()
    return output.getvalue()


def generated_outputs() -> dict[str, str]:
    standard = load_board(ROOT / "fixtures" / "standard-9x9.sdk")
    unsat = load_board(ROOT / "fixtures" / "unsat-9x9.sdk")
    multiple = load_board(ROOT / "fixtures" / "multiple-9x9.sdk")
    return {
        "06-sat-proposition.txt": proposition_output(),
        "06-sat-standard.txt": describe_result(solve(standard, 2), standard) + "\n",
        "06-sat-unsat.txt": describe_result(solve(unsat, 2), unsat) + "\n",
        "06-sat-multiple.txt": describe_result(solve(multiple, 2), multiple) + "\n",
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
