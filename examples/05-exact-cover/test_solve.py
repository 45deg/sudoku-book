from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "examples" / "common"))

from exact_cover import solve_exact_cover  # noqa: E402
from solve import build_sudoku_model, solve  # noqa: E402
from sudoku import boards_are_distinct, load_board, validate_solution  # noqa: E402
from toy import COLUMNS, ROWS  # noqa: E402


class ExactCoverTest(unittest.TestCase):
    def test_toy_problem_has_two_exact_covers(self) -> None:
        result = solve_exact_cover(ROWS, limit=10, required_columns=COLUMNS)
        actual = {frozenset(solution) for solution in result.solutions}
        self.assertEqual(actual, {frozenset(("r1", "r2")), frozenset(("r3", "r4"))})
        self.assertTrue(result.exhausted)

    def test_empty_sudoku_matrix_dimensions(self) -> None:
        model = build_sudoku_model((0,) * 81)
        self.assertEqual(len(model.rows), 729)
        self.assertEqual(len(model.columns), 324)
        self.assertTrue(all(len(covered) == 4 for covered in model.rows.values()))

    def assert_valid_solutions(self, fixture: str, solutions: tuple[tuple[int, ...], ...]) -> None:
        givens = load_board(ROOT / "fixtures" / fixture)
        for solution in solutions:
            valid, errors = validate_solution(solution, givens)
            self.assertTrue(valid, errors)

    def test_standard_board_has_one_solution(self) -> None:
        givens = load_board(ROOT / "fixtures" / "standard-9x9.sdk")
        result = solve(givens, limit=2)
        self.assertEqual(len(result.solutions), 1)
        self.assertTrue(result.exhausted)
        self.assert_valid_solutions("standard-9x9.sdk", result.solutions)

    def test_unsatisfiable_board_has_no_solution(self) -> None:
        givens = load_board(ROOT / "fixtures" / "unsat-9x9.sdk")
        result = solve(givens, limit=2)
        self.assertEqual(result.status, "unsat")
        self.assertEqual(result.solutions, ())
        self.assertTrue(result.exhausted)

    def test_multiple_board_returns_two_solutions(self) -> None:
        givens = load_board(ROOT / "fixtures" / "multiple-9x9.sdk")
        result = solve(givens, limit=2)
        self.assertEqual(len(result.solutions), 2)
        self.assertTrue(boards_are_distinct(result.solutions))
        self.assert_valid_solutions("multiple-9x9.sdk", result.solutions)


if __name__ == "__main__":
    unittest.main()
