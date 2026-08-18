from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "01-backtracking"
COMMON = ROOT / "examples" / "common"
sys.path[:0] = [str(EXAMPLE), str(COMMON)]

from solve import solve_naive, solve_propagating  # noqa: E402
from sudoku import Board, boards_are_distinct, load_board, validate_solution  # noqa: E402


class BacktrackingTests(unittest.TestCase):
    def fixture(self, name: str) -> Board:
        return load_board(ROOT / "fixtures" / name)

    def assert_valid_solutions(self, result, givens) -> None:
        for solution in result.solutions:
            valid, errors = validate_solution(solution, givens)
            self.assertTrue(valid, errors)
        self.assertTrue(boards_are_distinct(result.solutions))

    def test_both_methods_solve_standard_puzzle(self) -> None:
        givens = self.fixture("standard-9x9.sdk")
        for solver in (solve_naive, solve_propagating):
            with self.subTest(solver=solver.__name__):
                result = solver(givens, limit=1)
                self.assertEqual(result.status, "solved")
                self.assertEqual(len(result.solutions), 1)
                self.assert_valid_solutions(result, givens)

    def test_propagating_solver_proves_standard_puzzle_unique(self) -> None:
        givens = self.fixture("standard-9x9.sdk")
        result = solve_propagating(givens, limit=2)
        self.assertEqual(len(result.solutions), 1)
        self.assertTrue(result.exhausted)
        self.assert_valid_solutions(result, givens)

    def test_both_methods_report_unsat(self) -> None:
        givens = self.fixture("unsat-9x9.sdk")
        for solver in (solve_naive, solve_propagating):
            with self.subTest(solver=solver.__name__):
                result = solver(givens, limit=2)
                self.assertEqual(result.status, "unsat")
                self.assertTrue(result.exhausted)

    def test_both_methods_find_two_distinct_solutions(self) -> None:
        givens = self.fixture("multiple-9x9.sdk")
        for solver in (solve_naive, solve_propagating):
            with self.subTest(solver=solver.__name__):
                result = solver(givens, limit=2)
                self.assertEqual(len(result.solutions), 2)
                self.assertFalse(result.exhausted)
                self.assert_valid_solutions(result, givens)

    def test_shidoku_fixture_is_supported(self) -> None:
        givens = self.fixture("shidoku-4x4.sdk")
        result = solve_propagating(givens, limit=2)
        self.assertGreaterEqual(len(result.solutions), 1)
        self.assert_valid_solutions(result, givens)


if __name__ == "__main__":
    unittest.main()
