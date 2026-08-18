from __future__ import annotations

import importlib.util
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOLVER = ROOT / "examples" / "02-prolog" / "solve.pl"
COMMON = ROOT / "examples" / "common" / "sudoku.py"
SWIPL = shutil.which("swipl")

spec = importlib.util.spec_from_file_location("sudoku_common", COMMON)
assert spec and spec.loader
sudoku_common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sudoku_common)


def run_solver(fixture: str, limit: int = 2) -> str:
    result = subprocess.run(
        [
            SWIPL or "swipl",
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
    return result.stdout


def expected_output(name: str) -> str:
    return (ROOT / "outputs" / f"02-prolog-{name}.txt").read_text(encoding="utf-8")


def parse_solutions(output: str) -> list[tuple[int, ...]]:
    lines = output.splitlines()
    solutions: list[tuple[int, ...]] = []
    for index, line in enumerate(lines):
        if line.startswith("solution "):
            solutions.append(
                sudoku_common.parse_board("\n".join(lines[index + 1 : index + 10]))
            )
    return solutions


@unittest.skipUnless(SWIPL, "SWI-Prolog (swipl) binary not found")
class PrologSudokuTests(unittest.TestCase):
    def assert_valid_solutions(self, fixture: str, solutions: list[tuple[int, ...]]) -> None:
        givens = sudoku_common.load_board(ROOT / "fixtures" / fixture)
        for solution in solutions:
            valid, errors = sudoku_common.validate_solution(solution, givens)
            self.assertTrue(valid, errors)

    def test_standard_board_has_one_valid_solution(self) -> None:
        output = run_solver("standard-9x9.sdk", 2)
        solutions = parse_solutions(output)
        self.assertIn("status: solved", output)
        self.assertEqual(output, expected_output("standard"))
        self.assertEqual(len(solutions), 1)
        self.assert_valid_solutions("standard-9x9.sdk", solutions)

    def test_unsat_board_has_no_solution(self) -> None:
        output = run_solver("unsat-9x9.sdk", 2)
        self.assertIn("status: unsat", output)
        self.assertEqual(output, expected_output("unsat"))
        self.assertEqual(parse_solutions(output), [])

    def test_multiple_board_returns_two_distinct_solutions(self) -> None:
        output = run_solver("multiple-9x9.sdk", 2)
        solutions = parse_solutions(output)
        self.assertEqual(output, expected_output("multiple"))
        self.assertEqual(len(solutions), 2)
        self.assertTrue(sudoku_common.boards_are_distinct(solutions))
        self.assert_valid_solutions("multiple-9x9.sdk", solutions)


if __name__ == "__main__":
    unittest.main()
