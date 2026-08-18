from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "examples" / "common"))

from small_projection import project_diagonal, project_x_axis  # noqa: E402
from solve import project_concur, project_divide, solve  # noqa: E402
from sudoku import load_board, validate_solution  # noqa: E402


class SmallProjectionTest(unittest.TestCase):
    def test_two_line_projections(self) -> None:
        point = np.array([2.0, 1.0])
        np.testing.assert_array_equal(project_x_axis(point), np.array([2.0, 0.0]))
        np.testing.assert_array_equal(project_diagonal(point), np.array([1.5, 1.5]))


class SudokuProjectionTest(unittest.TestCase):
    def test_divide_satisfies_every_local_constraint(self) -> None:
        givens = load_board(HERE / "boards" / "unique-4x4.sdk")
        values = np.random.default_rng(7).normal(size=(4, 4, 4, 4))
        divided = project_divide(values, givens)

        np.testing.assert_array_equal(divided[0].sum(axis=2), np.ones((4, 4)))
        np.testing.assert_array_equal(divided[1].sum(axis=1), np.ones((4, 4)))
        np.testing.assert_array_equal(divided[2].sum(axis=0), np.ones((4, 4)))
        for top in (0, 2):
            for left in (0, 2):
                block = divided[3, top : top + 2, left : left + 2]
                np.testing.assert_array_equal(block.sum(axis=(0, 1)), np.ones(4))
        self.assertEqual(divided[0, 0, 0, 0], 1.0)
        self.assertEqual(divided[0, 0, 3, 3], 1.0)

    def test_concur_makes_replicas_equal(self) -> None:
        values = np.random.default_rng(11).normal(size=(4, 4, 4, 4))
        concurred = project_concur(values)
        for replica in range(1, 4):
            np.testing.assert_array_equal(concurred[0], concurred[replica])

    def test_unique_problem_returns_valid_solution(self) -> None:
        givens = load_board(HERE / "boards" / "unique-4x4.sdk")
        result = solve(
            givens,
            seed=0,
            max_iterations=2_000,
            tolerance=1e-8,
            beta=0.5,
        )
        self.assertEqual(result.status, "solved")
        self.assertIsNotNone(result.solution)
        valid, errors = validate_solution(result.solution, givens)
        self.assertTrue(valid, errors)

    def test_known_unsat_problem_remains_unknown(self) -> None:
        givens = load_board(HERE / "boards" / "unsat-4x4.sdk")
        result = solve(
            givens,
            seed=0,
            max_iterations=200,
            tolerance=1e-8,
            beta=0.5,
        )
        self.assertEqual(result.status, "unknown")
        self.assertIsNone(result.solution)

    def test_multiple_problem_returns_one_valid_solution(self) -> None:
        givens = load_board(ROOT / "fixtures" / "shidoku-4x4.sdk")
        result = solve(
            givens,
            seed=2,
            max_iterations=2_000,
            tolerance=1e-8,
            beta=0.5,
        )
        self.assertEqual(result.status, "solved")
        self.assertIsNotNone(result.solution)
        valid, errors = validate_solution(result.solution, givens)
        self.assertTrue(valid, errors)


if __name__ == "__main__":
    unittest.main()
