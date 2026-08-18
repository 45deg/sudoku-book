from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "examples" / "common"))

from solve import all_different_message, solve  # noqa: E402
from sudoku import load_board, validate_solution  # noqa: E402


class FactorMessageTest(unittest.TestCase):
    def test_sum_and_max_product_differ(self) -> None:
        incoming = (
            (1 / 3, 1 / 3, 1 / 3),
            (0.6, 0.3, 0.1),
            (0.2, 0.3, 0.5),
        )
        summed = all_different_message(incoming, 0, "sum-product")
        maximized = all_different_message(incoming, 0, "max-product")
        self.assertIsNotNone(summed)
        self.assertIsNotNone(maximized)
        self.assertNotEqual(summed, maximized)
        self.assertAlmostEqual(sum(summed or ()), 1.0)
        self.assertAlmostEqual(sum(maximized or ()), 1.0)


class FactorGraphSudokuTest(unittest.TestCase):
    def test_unique_board_sum_product(self) -> None:
        board = load_board(HERE / "boards" / "unique-4x4.sdk")
        result = solve(board, "sum-product")
        self.assertEqual(result.status, "solved")
        self.assertTrue(result.converged)
        self.assertIsNotNone(result.solution)
        assert result.solution is not None
        valid, errors = validate_solution(result.solution, board)
        self.assertTrue(valid, errors)

    def test_unique_board_max_product(self) -> None:
        board = load_board(HERE / "boards" / "unique-4x4.sdk")
        result = solve(board, "max-product")
        self.assertEqual(result.status, "solved")
        self.assertTrue(result.converged)
        self.assertIsNotNone(result.solution)
        assert result.solution is not None
        valid, errors = validate_solution(result.solution, board)
        self.assertTrue(valid, errors)

    def test_multiple_board_ties_are_unknown(self) -> None:
        board = load_board(ROOT / "fixtures" / "shidoku-4x4.sdk")
        result = solve(board, "sum-product")
        self.assertEqual(result.status, "unknown")
        self.assertTrue(result.converged)
        self.assertGreater(result.ties, 0)

    def test_unsatisfiable_board_is_not_reported_as_unsat(self) -> None:
        board = load_board(HERE / "boards" / "unsat-4x4.sdk")
        result = solve(board, "sum-product")
        self.assertEqual(result.status, "unknown")
        self.assertFalse(result.converged)

    def test_iteration_limit_is_unknown(self) -> None:
        board = load_board(HERE / "boards" / "unique-4x4.sdk")
        result = solve(board, "sum-product", max_iterations=1)
        self.assertEqual(result.status, "unknown")
        self.assertFalse(result.converged)

    def test_nine_by_nine_is_rejected_explicitly(self) -> None:
        board = load_board(ROOT / "fixtures" / "standard-9x9.sdk")
        with self.assertRaisesRegex(ValueError, "4×4"):
            solve(board)


if __name__ == "__main__":
    unittest.main()
