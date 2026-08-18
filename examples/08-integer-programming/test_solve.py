from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import highspy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "examples" / "common"))

import solve as solve_module  # noqa: E402
from solve import solve  # noqa: E402
from sudoku import boards_are_distinct, load_board, validate_solution  # noqa: E402


class IntegerProgrammingSudokuTest(unittest.TestCase):
    def test_nonfinal_status_is_unknown(self) -> None:
        fake_model = Mock()
        fake_model.getModelStatus.return_value = highspy.HighsModelStatus.kTimeLimit
        fake_model.modelStatusToString.return_value = "Time limit reached"
        board = load_board(ROOT / "fixtures" / "shidoku-4x4.sdk")
        with patch.object(solve_module, "build_model", return_value=(fake_model, {})):
            result = solve(board)
        self.assertEqual(result.status, "unknown")
        self.assertFalse(result.search_complete)

    def test_standard_board_is_unique(self) -> None:
        board = load_board(ROOT / "fixtures" / "standard-9x9.sdk")
        result = solve(board, limit=2)
        self.assertEqual(result.status, "solved")
        self.assertEqual(len(result.solutions), 1)
        self.assertTrue(result.search_complete)
        self.assertTrue(validate_solution(result.solutions[0], board)[0])

    def test_shidoku_board(self) -> None:
        board = load_board(ROOT / "fixtures" / "shidoku-4x4.sdk")
        result = solve(board)
        self.assertEqual(result.status, "solved")
        self.assertEqual(len(result.solutions), 1)
        self.assertTrue(validate_solution(result.solutions[0], board)[0])

    def test_unsatisfiable_board(self) -> None:
        board = load_board(ROOT / "fixtures" / "unsat-9x9.sdk")
        result = solve(board)
        self.assertEqual(result.status, "unsat")
        self.assertEqual(result.solutions, ())
        self.assertTrue(result.search_complete)

    def test_two_distinct_solutions(self) -> None:
        board = load_board(ROOT / "fixtures" / "multiple-9x9.sdk")
        result = solve(board, limit=2)
        self.assertEqual(result.status, "solved")
        self.assertEqual(len(result.solutions), 2)
        self.assertTrue(boards_are_distinct(result.solutions))
        for solution in result.solutions:
            self.assertTrue(validate_solution(solution, board)[0])


if __name__ == "__main__":
    unittest.main()
