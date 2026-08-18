from __future__ import annotations

import sys
import unittest
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "06-sat"
COMMON = ROOT / "examples" / "common"
sys.path[:0] = [str(EXAMPLE), str(COMMON)]

from proposition_demo import exactly_one_of_two  # noqa: E402
from solve import (  # noqa: E402
    BASE_CLAUSES,
    VARIABLES,
    candidate_var,
    exactly_one,
    solve,
    sudoku_cnf,
)
from sudoku import Board, boards_are_distinct, load_board, validate_solution  # noqa: E402


def satisfies(clauses: list[list[int]], values: tuple[bool, ...]) -> bool:
    return all(
        any(values[abs(literal) - 1] == (literal > 0) for literal in clause)
        for clause in clauses
    )


class SatTests(unittest.TestCase):
    def fixture(self, name: str) -> Board:
        return load_board(ROOT / "fixtures" / name)

    def assert_valid_solutions(self, result, givens) -> None:
        for solution in result.solutions:
            valid, errors = validate_solution(solution, givens)
            self.assertTrue(valid, errors)
        self.assertTrue(boards_are_distinct(result.solutions))

    def test_small_formula_has_exactly_two_models(self) -> None:
        self.assertEqual(exactly_one_of_two(), ((False, True), (True, False)))

    def test_exactly_one_encoding(self) -> None:
        clauses = exactly_one([1, 2, 3])
        models = [
            values
            for values in product((False, True), repeat=3)
            if satisfies(clauses, values)
        ]
        self.assertEqual(models, [(False, False, True), (False, True, False), (True, False, False)])

    def test_base_encoding_size_and_variable_range(self) -> None:
        empty = (0,) * 81
        clauses = sudoku_cnf(empty)
        self.assertEqual(VARIABLES, 729)
        self.assertEqual(len(clauses), BASE_CLAUSES)
        self.assertEqual(BASE_CLAUSES, 11_988)
        self.assertEqual(max(abs(literal) for clause in clauses for literal in clause), 729)
        self.assertEqual(candidate_var(0, 0, 1), 1)
        self.assertEqual(candidate_var(8, 8, 9), 729)

    def test_standard_puzzle_is_unique(self) -> None:
        givens = self.fixture("standard-9x9.sdk")
        result = solve(givens, limit=2)
        self.assertEqual(result.status, "solved")
        self.assertEqual(len(result.solutions), 1)
        self.assertTrue(result.exhausted)
        self.assert_valid_solutions(result, givens)

    def test_unsatisfiable_puzzle(self) -> None:
        givens = self.fixture("unsat-9x9.sdk")
        result = solve(givens, limit=2)
        self.assertEqual(result.status, "unsat")
        self.assertEqual(result.solutions, ())
        self.assertTrue(result.exhausted)

    def test_multiple_puzzle_returns_two_distinct_solutions(self) -> None:
        givens = self.fixture("multiple-9x9.sdk")
        result = solve(givens, limit=2)
        self.assertEqual(result.status, "solved")
        self.assertEqual(len(result.solutions), 2)
        self.assertTrue(result.exhausted)
        self.assert_valid_solutions(result, givens)

    def test_rejects_4x4_board(self) -> None:
        givens = self.fixture("shidoku-4x4.sdk")
        with self.assertRaisesRegex(ValueError, "9x9"):
            solve(givens)


if __name__ == "__main__":
    unittest.main()
