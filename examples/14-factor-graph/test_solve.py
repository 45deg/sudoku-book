from __future__ import annotations

import sys
import unittest
from itertools import permutations
from math import prod
from pathlib import Path
from random import Random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "examples" / "common"))

from solve import all_different_message, solve  # noqa: E402
from sudoku import load_board, validate_solution  # noqa: E402


class FactorMessageTest(unittest.TestCase):
    def test_subset_messages_match_enumeration(self) -> None:
        rng = Random(11)
        for side in (3, 4, 5):
            incoming = tuple(
                tuple(rng.choice((0.0, 0.2, 0.5, 1.0)) for _ in range(side))
                for _ in range(side)
            )
            for target in range(side):
                for method in ("sum-product", "max-product"):
                    expected = [0.0] * side
                    for assignment in permutations(range(side)):
                        weight = prod(incoming[p][assignment[p]] for p in range(side) if p != target)
                        digit = assignment[target]
                        if method == "sum-product":
                            expected[digit] += weight
                        else:
                            expected[digit] = max(expected[digit], weight)
                    actual = all_different_message(incoming, target, method)
                    total = sum(expected)
                    if total == 0:
                        self.assertIsNone(actual)
                    else:
                        self.assertIsNotNone(actual)
                        for left, right in zip(actual, expected):
                            self.assertAlmostEqual(left, right / total)

    def test_nine_digit_message_excludes_target_input(self) -> None:
        incoming = tuple(tuple(float(d == p) for d in range(9)) for p in range(9))
        for target in range(9):
            messages = list(incoming)
            messages[target] = (0.0,) * 9
            for method in ("sum-product", "max-product"):
                self.assertEqual(all_different_message(messages, target, method), incoming[target])

    def test_impossible_factor_has_no_message(self) -> None:
        for method in ("sum-product", "max-product"):
            self.assertIsNone(all_different_message(((1.0, 0.0, 0.0),) * 3, 0, method))

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
    def test_sum_product_iteration_budget_is_unknown(self) -> None:
        board = load_board(ROOT / "fixtures" / "standard-9x9.sdk")
        result = solve(board, "sum-product", max_iterations=200)
        self.assertEqual(result.status, "unknown")
        self.assertFalse(result.converged)
        self.assertIsNone(result.solution)

    def test_unique_board_max_product(self) -> None:
        board = load_board(ROOT / "fixtures" / "standard-9x9.sdk")
        result = solve(board, "max-product")
        self.assertEqual(result.status, "solved")
        self.assertTrue(result.converged)
        self.assertIsNotNone(result.solution)
        assert result.solution is not None
        valid, errors = validate_solution(result.solution, board)
        self.assertTrue(valid, errors)

    def test_multiple_board_ties_are_unknown(self) -> None:
        board = load_board(ROOT / "fixtures" / "multiple-9x9.sdk")
        result = solve(board, "sum-product")
        self.assertEqual(result.status, "unknown")
        self.assertTrue(result.converged)
        self.assertGreater(result.ties, 0)

    def test_unsatisfiable_board_is_not_reported_as_unsat(self) -> None:
        board = load_board(ROOT / "fixtures" / "unsat-9x9.sdk")
        result = solve(board, "sum-product")
        self.assertEqual(result.status, "unknown")
        self.assertFalse(result.converged)

    def test_iteration_limit_is_unknown(self) -> None:
        board = load_board(ROOT / "fixtures" / "standard-9x9.sdk")
        result = solve(board, "sum-product", max_iterations=1)
        self.assertEqual(result.status, "unknown")
        self.assertFalse(result.converged)



if __name__ == "__main__":
    unittest.main()
